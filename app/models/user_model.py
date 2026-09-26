"""
Modelo SQLAlchemy de la tabla 'users'.

Este es el modelo de BASE DE DATOS (representa la tabla real), y es
distinto de los schemas Pydantic (que representan lo que entra y sale
por la API). Ver README para la explicación de esta diferencia.
"""

from datetime import datetime

from sqlalchemy import Column, Integer, String, Boolean, DateTime

from app.database.connection import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False, index=True)
    role = Column(String, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
