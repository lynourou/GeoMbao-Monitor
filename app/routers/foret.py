from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.routers.layers import vector_layer


router = APIRouter(prefix="/api/foret", tags=["Forêt"])


@router.get("")
@router.get("/", include_in_schema=False)
def get_foret(database: Session = Depends(get_db)) -> dict:
    """Backward-compatible shortcut for the generic forest layer endpoint."""
    return vector_layer("foret", bbox=None, limit=10_000, database=database)
