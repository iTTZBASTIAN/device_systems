"""
Schemas Pydantic v2 para el recurso 'users' de device_systems.

Roles permitidos: admin, support, user.
"""

from typing import Literal, Optional
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


class UserUpdate(UserBase):
    """
    Actualización completa de un usuario (PUT /users/{id}).
    Requiere todos los campos, ya que reemplaza el recurso por completo.
    """
    pass


class UserPatch(BaseModel):
    """
    Actualización parcial de un usuario (PATCH /users/{id}).
    Todos los campos son opcionales: solo se modifica lo que se envíe.
    """

    name: Optional[str] = Field(None, min_length=3)
    email: Optional[EmailStr] = None
    role: Optional[RoleType] = None
    is_active: Optional[bool] = None

    def has_data(self) -> bool:
        """True si el cliente envió al menos un campo para actualizar."""
        return any(
            value is not None
            for value in self.model_dump(exclude_unset=True).values()
        )


class UserResponse(UserBase):
    """Modelo de salida: lo que la API devuelve al cliente."""

    id: int = Field(..., description="Identificador único del usuario.")

    model_config = ConfigDict(from_attributes=True)
