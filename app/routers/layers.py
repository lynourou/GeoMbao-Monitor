import json

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.services.layer_catalog import get_layer, serialize_catalog


router = APIRouter(prefix="/api", tags=["Couches SIG"])
TRANSPARENT_PNG = bytes.fromhex(
    "89504e470d0a1a0a0000000d49484452000000010000000108060000001f15c489"
    "0000000d49444154789c6360000000020001e221bc330000000049454e44ae426082"
)


@router.get("/layers")
def layer_catalog(database: Session = Depends(get_db)) -> dict:
    return {"groups": ["Référence", "Occupation du sol", "Indices", "Relief"],
            "layers": serialize_catalog(database)}


@router.get("/layer/{layer_name}")
def vector_layer(
    layer_name: str,
    bbox: str | None = Query(default=None, description="west,south,east,north in EPSG:4326"),
    limit: int = Query(default=10_000, ge=1, le=50_000),
    database: Session = Depends(get_db),
) -> dict:
    definition = get_layer(layer_name, "vector")
    if not definition:
        raise HTTPException(status_code=404, detail="Couche vectorielle inconnue")

    params: dict[str, object] = {"limit": limit}
    where = ""
    if bbox:
        try:
            west, south, east, north = (float(value) for value in bbox.split(","))
        except (ValueError, TypeError):
            raise HTTPException(status_code=422, detail="bbox doit contenir west,south,east,north") from None
        params.update(west=west, south=south, east=east, north=north)
        where = (
            f'WHERE ST_Intersects("{definition.geometry_column}", '
            f'ST_Transform(ST_MakeEnvelope(:west, :south, :east, :north, 4326), '
            f'ST_SRID("{definition.geometry_column}")))'
        )

    sql = text(f'''
        SELECT jsonb_build_object(
            'type', 'FeatureCollection',
            'features', COALESCE(jsonb_agg(feature), '[]'::jsonb)
        )
        FROM (
            SELECT jsonb_build_object(
                'type', 'Feature',
                'id', source.id,
                'geometry', ST_AsGeoJSON(ST_Transform(source."{definition.geometry_column}", 4326))::jsonb,
                'properties', to_jsonb(source) - '{definition.geometry_column}'
            ) AS feature
            FROM "{definition.table}" AS source
            {where}
            LIMIT :limit
        ) AS features
    ''')
    try:
        return database.execute(sql, params).scalar_one()
    except SQLAlchemyError as exc:
        raise HTTPException(status_code=503, detail="La couche n’est pas disponible") from exc


@router.get("/raster/{layer_name}/{z}/{x}/{y}.png", response_class=Response)
def raster_tile(
    layer_name: str,
    z: int,
    x: int,
    y: int,
    database: Session = Depends(get_db),
) -> Response:
    definition = get_layer(layer_name, "raster")
    if not definition:
        raise HTTPException(status_code=404, detail="Couche raster inconnue")
    if not 0 <= z <= 22 or x < 0 or y < 0:
        raise HTTPException(status_code=422, detail="Coordonnées de tuile invalides")

    sql = text(f'''
        WITH tile AS (SELECT ST_TileEnvelope(:z, :x, :y) AS geom),
        source AS (
            SELECT ST_Clip(ST_Transform(r."{definition.raster_column}", 3857), tile.geom) AS rast
            FROM "{definition.table}" AS r, tile
            WHERE ST_Intersects(ST_Transform(ST_ConvexHull(r."{definition.raster_column}"), 3857), tile.geom)
        ), merged AS (SELECT ST_Union(rast) AS rast FROM source)
        SELECT ST_AsPNG(ST_ColorMap(rast, 1, :colormap, 'INTERPOLATE'))
        FROM merged WHERE rast IS NOT NULL
    ''')
    try:
        image = database.execute(sql, {"z": z, "x": x, "y": y, "colormap": definition.colormap}).scalar()
    except SQLAlchemyError as exc:
        raise HTTPException(status_code=503, detail="Le raster n’est pas disponible") from exc
    return Response(content=bytes(image) if image else TRANSPARENT_PNG, media_type="image/png",
                    headers={"Cache-Control": "public, max-age=3600"})
