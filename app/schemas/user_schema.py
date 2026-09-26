"""
Schemas Pydantic v2 para el recurso 'users' de device_systems.

Roles permitidos: admin, support, user.
"""

from typing import Literal
from pydantic import BaseModel, EmailStr, Field, ConfigDict


RoleType = Literal["admin", "support", "user"]


class UserBase(BaseModel):
    """Campos comunes para crear/actualizar un usuario."""

    name: str = Field(
        ...,
        min_length=3,
        description="Nombre completo del usuario. Mínimo 3 caracteres.",
        examples=["Ana Pérez"],
    )
    email: EmailStr = Field(
        ...,
        description="Correo electrónico único y con formato válido.",
        examples=["ana@sena.edu.co"],
    )
    role: RoleType = Field(
        ...,
        description="Rol del usuario dentro del sistema.",
        examples=["user"],
    )
    is_active: bool = Field(
        default=True,
        description="Indica si el usuario está activo.",
    )


class UserCreate(UserBase):
    """Datos requeridos para registrar un nuevo usuario (POST /users)."""
    pass


class UserResponse(UserBase):
    """Modelo de salida: lo que la API devuelve al cliente."""

    id: int = Field(..., description="Identificador único del usuario.")

    model_config = ConfigDict(from_attributes=True)
