"""
device_systems - API REST para la gestión de usuarios.

EV07: GET y POST.
EV08: + PUT, PATCH, DELETE, manejo de errores, Dependency Injection
y documentación Swagger/OpenAPI mejorada.
EV09: + persistencia real con SQLAlchemy y SQLite (reemplaza el
almacenamiento en memoria de las versiones anteriores).
"""

from fastapi import FastAPI, Request

from app.database.connection import Base, engine
from app.models import user_model  # noqa: F401 - necesario para registrar el modelo en Base
from app.routes.user_routes import router as user_router

APP_NAME = "device_systems"
API_VERSION = "3.0.0"

# Crea las tablas en la base de datos si no existen todavía.
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="device_systems API",
    description="API REST para la gestión de usuarios del sistema device_systems, con persistencia en base de datos vía SQLAlchemy.",
    version=API_VERSION,
)


@app.middleware("http")
async def add_custom_headers(request: Request, call_next):
    """Agrega cabeceras personalizadas a toda respuesta de la API."""
    response = await call_next(request)
    response.headers["X-App-Name"] = APP_NAME
    response.headers["X-API-Version"] = API_VERSION
    return response


app.include_router(user_router)


@app.get("/", tags=["Root"], summary="Healthcheck")
def root():
    return {"app": APP_NAME, "version": API_VERSION, "status": "ok"}
