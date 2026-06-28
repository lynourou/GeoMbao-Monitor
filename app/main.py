from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy import text

from app.database.database import engine
from app.routers import dashboard
from app.routers.foret import router as foret_router
from app.routers.layers import router as layers_router


app = FastAPI(
    title="Plateforme SIG — Forêt Classée de Mbao",
    description="API réutilisable pour la consultation des données SIG et des indicateurs.",
    version="1.1.0",
)
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

app.include_router(layers_router)
app.include_router(foret_router)
app.include_router(dashboard.router)


@app.get("/", response_class=HTMLResponse, include_in_schema=False)
def map_view(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")


@app.get("/map", response_class=HTMLResponse, include_in_schema=False)
def map_alias(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")


@app.get("/api/health", tags=["Système"])
def health_check() -> dict:
    with engine.connect() as connection:
        database = connection.execute(text("SELECT current_database()")) .scalar_one()
    return {"status": "ok", "database": database}
