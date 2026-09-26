"""
device_systems - API REST para la gestión de usuarios (EV07).
"""

from fastapi import FastAPI, Request

from app.routes.user_routes import router as user_router

APP_NAME = "device_systems"
API_VERSION = "1.0"

app = FastAPI(
    title="device_systems API",
    description="API REST para la gestión de usuarios del sistema device_systems.",
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
