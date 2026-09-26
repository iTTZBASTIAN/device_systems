"""
device_systems - API REST para usuarios, dispositivos y préstamos.

EV07: GET y POST.
EV08: + PUT, PATCH, DELETE, manejo de errores, Dependency Injection
y documentación Swagger/OpenAPI mejorada.
EV09: persistencia real con SQLAlchemy y SQLite.
EV10: migraciones Alembic, relaciones entre modelos y consultas con joins.
"""

from fastapi import FastAPI, Request

from app.routes.device_routes import router as device_router
from app.routes.loan_routes import router as loan_router
from app.routes.user_routes import router as user_router

APP_NAME = "device_systems"
API_VERSION = "4.0.0"

app = FastAPI(
    title="device_systems API",
    description="API REST para gestionar usuarios, dispositivos tecnológicos y préstamos con SQLAlchemy, SQLite y migraciones Alembic.",
    version=API_VERSION,
    openapi_tags=[
        {"name": "Users", "description": "Gestión de usuarios y consulta de sus préstamos."},
        {"name": "Devices", "description": "Inventario, disponibilidad e historial de dispositivos."},
        {"name": "Loans", "description": "Préstamos, devoluciones, filtros y consultas relacionadas."},
    ],
)


@app.middleware("http")
async def add_custom_headers(request: Request, call_next):
    """Agrega cabeceras personalizadas a toda respuesta de la API."""
    response = await call_next(request)
    response.headers["X-App-Name"] = APP_NAME
    response.headers["X-API-Version"] = API_VERSION
    return response


app.include_router(user_router)
app.include_router(device_router)
app.include_router(loan_router)


@app.get("/", tags=["Root"], summary="Healthcheck")
def root():
    return {"app": APP_NAME, "version": API_VERSION, "status": "ok"}
