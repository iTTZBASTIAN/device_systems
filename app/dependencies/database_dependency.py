"""
Dependencia de base de datos: entrega una sesión por petición y la
cierra automáticamente al finalizar, usando Depends().
"""

from app.database.connection import SessionLocal


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
