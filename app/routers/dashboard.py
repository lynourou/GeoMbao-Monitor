from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.database.database import get_db


router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])


def _table_exists(database: Session, table: str) -> bool:
    return bool(database.execute(text("SELECT to_regclass(:table)"), {"table": f"public.{table}"}).scalar())


@router.get("")
@router.get("/", include_in_schema=False)
def dashboard(database: Session = Depends(get_db)) -> dict:
    """Aggregate the latest dashboard indicators directly from PostgreSQL/PostGIS."""
    try:
        forest = database.execute(text("""
            SELECT nom, superficie_ha, commune, departement, date_classement,
                   organisme_gestionaire, code
            FROM foret ORDER BY id LIMIT 1
        """)).mappings().first()
        if not forest:
            raise HTTPException(status_code=404, detail="Aucune forêt enregistrée")

        carbon = database.execute(text(
            "SELECT SUM(carbone) FROM occupation_sol_2025_s2 WHERE carbone IS NOT NULL"
        )).scalar() if _table_exists(database, "occupation_sol_2025_s2") else None

        ndvi = database.execute(text(
            "SELECT (ST_SummaryStatsAgg(rast, 1, true)).mean FROM ndvi_2025"
        )).scalar() if _table_exists(database, "ndvi_2025") else None

        temperature = database.execute(text(
            "SELECT AVG(ann) FROM temperature WHERE ann IS NOT NULL"
        )).scalar() if _table_exists(database, "temperature") else None
        precipitation = database.execute(text(
            "SELECT AVG(ann) FROM precipitation WHERE ann IS NOT NULL"
        )).scalar() if _table_exists(database, "precipitation") else None
    except SQLAlchemyError as exc:
        raise HTTPException(status_code=503, detail="Impossible de calculer le tableau de bord") from exc

    return {
        "nom": forest["nom"],
        "superficie_ha": float(forest["superficie_ha"]) if forest["superficie_ha"] is not None else None,
        "commune": forest["commune"],
        "departement": forest["departement"],
        "date_classement": forest["date_classement"].isoformat() if forest["date_classement"] else None,
        "organisme_gestionnaire": forest["organisme_gestionaire"],
        "code": forest["code"],
        "stock_carbone": float(carbon) if carbon is not None else None,
        "ndvi_moyen": float(ndvi) if ndvi is not None else None,
        "temperature_moyenne": float(temperature) if temperature is not None else None,
        "precipitations_moyennes": float(precipitation) if precipitation is not None else None,
    }
