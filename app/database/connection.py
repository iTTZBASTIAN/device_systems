"""
Configuración de la conexión a la base de datos.

Usa SQLite para desarrollo. El engine, la sesión y la Base declarativa
se definen aquí y se reutilizan en todo el proyecto.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = "sqlite:///./device_systems.db"

# check_same_thread=False es necesario solo para SQLite, ya que FastAPI
# puede acceder a la conexión desde distintos hilos.
engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
