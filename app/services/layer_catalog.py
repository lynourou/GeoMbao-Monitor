from dataclasses import asdict, dataclass
from typing import Literal

from sqlalchemy import text
from sqlalchemy.orm import Session


LayerKind = Literal["vector", "raster"]


@dataclass(frozen=True)
class LayerDefinition:
    slug: str
    label: str
    group: str
    kind: LayerKind
    table: str
    geometry_column: str = "geom"
    raster_column: str = "rast"
    checked: bool = False
    color: str = "#237a45"
    fill_color: str = "#4caf50"
    weight: int = 2
    fill_opacity: float = 0.28
    legend: str = ""
    colormap: str = ""


INDEX_COLORMAP = "-1 132 60 12 220\n0 255 255 204 190\n1 0 104 55 230"
WATER_COLORMAP = "-1 166 97 26 220\n0 245 245 245 180\n1 8 81 156 230"
BSI_COLORMAP = "-1 35 139 69 220\n0 255 255 204 190\n1 140 81 10 230"
LST_COLORMAP = "10 49 54 149 220\n25 255 255 191 210\n50 165 0 38 230"
RELIEF_COLORMAP = "0 25 105 45 220\n25 215 190 120 220\n100 255 255 255 230"


LAYERS = (
    LayerDefinition("foret", "Forêt classée", "Référence", "vector", "foret", checked=True,
                    color="#0b5d2a", fill_color="#36a852", fill_opacity=.25, legend="Périmètre classé"),
    LayerDefinition("commune", "Commune", "Référence", "vector", "commune",
                    color="#5b3f8c", fill_color="#8e75bb", fill_opacity=.08, legend="Limites communales"),
    LayerDefinition("reseau-routier", "Réseau routier", "Référence", "vector", "reseau_transport",
                    color="#cc5938", fill_color="#cc5938", weight=3, fill_opacity=0, legend="Routes"),
    LayerDefinition("plans-eau", "Plans d’eau", "Référence", "vector", "plan_eau",
                    color="#2378b7", fill_color="#5dade2", legend="Plans d’eau"),
    LayerDefinition("observations", "Observations", "Référence", "vector", "observation",
                    color="#9b2d55", fill_color="#e84a7f", legend="Observations de terrain"),
    LayerDefinition("occupation-1985", "1985", "Occupation du sol", "vector", "occupation_sol_1985_ls"),
    LayerDefinition("occupation-2000", "2000", "Occupation du sol", "vector", "occupation_sol_2000_ls"),
    LayerDefinition("occupation-2015", "2015", "Occupation du sol", "vector", "occupation_sol_2015_ls"),
    LayerDefinition("occupation-2025", "2025", "Occupation du sol", "vector", "occupation_sol_2025_s2"),
    LayerDefinition("ndvi", "NDVI", "Indices", "raster", "ndvi_2025", legend="NDVI 2025", colormap=INDEX_COLORMAP),
    LayerDefinition("evi", "EVI", "Indices", "raster", "evi_2025", legend="EVI 2025", colormap=INDEX_COLORMAP),
    LayerDefinition("mndwi", "MNDWI", "Indices", "raster", "mndwi_2025", legend="MNDWI 2025", colormap=WATER_COLORMAP),
    LayerDefinition("bsi", "BSI", "Indices", "raster", "bsi_2025", legend="BSI 2025", colormap=BSI_COLORMAP),
    LayerDefinition("lst", "LST", "Indices", "raster", "lst_2025", legend="Température de surface 2025", colormap=LST_COLORMAP),
    LayerDefinition("mnt-5m", "MNT 5 m", "Relief", "raster", "mnt_5m", legend="Altitude", colormap=RELIEF_COLORMAP),
    LayerDefinition("mnt-50cm", "MNT 50 cm", "Relief", "raster", "mnt_50cm", legend="Altitude", colormap=RELIEF_COLORMAP),
)

LAYER_BY_SLUG = {layer.slug: layer for layer in LAYERS}


def get_layer(slug: str, kind: LayerKind | None = None) -> LayerDefinition | None:
    layer = LAYER_BY_SLUG.get(slug)
    return layer if layer and (kind is None or layer.kind == kind) else None


def serialize_catalog(database: Session) -> list[dict]:
    """Return public layer metadata and whether each backing table exists."""
    table_names = {layer.table for layer in LAYERS}
    available = {
        table: bool(database.execute(text("SELECT to_regclass(:table)"), {"table": f"public.{table}"}).scalar())
        for table in table_names
    }
    return [{**asdict(layer), "available": available[layer.table]} for layer in LAYERS]
