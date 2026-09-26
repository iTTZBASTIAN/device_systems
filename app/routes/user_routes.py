"""
Endpoints del recurso 'users' para device_systems.

Las rutas son "delgadas": reciben la petición, validan con los
schemas y las dependencias, y delegan la lógica al servicio.
"""

from typing import Optional

from fastapi import APIRouter, Depends, Query, status

from app.schemas.user_schema import (
    UserCreate,
    UserUpdate,
    UserPatch,
    UserResponse,
    RoleType,
)
from app.dependencies.user_dependencies import get_user_or_404
from app.services import user_service

router = APIRouter(prefix="/users", tags=["Users"])


@router.get(
    "",
    response_model=list[UserResponse],
    summary="Listar usuarios",
    description="Lista todos los usuarios. Permite filtrar por rol y por estado activo.",
    response_description="Lista de usuarios que cumplen los filtros aplicados.",
)
def list_users(
    role: Optional[RoleType] = Query(None, description="Filtrar por rol: admin, support o user."),
    is_active: Optional[bool] = Query(None, description="Filtrar por estado activo/inactivo."),
):
    return user_service.list_users(role=role, is_active=is_active)


@router.get(
    "/{user_id}",
    response_model=UserResponse,
    summary="Consultar usuario por ID",
    response_description="Datos del usuario solicitado.",
)
def get_user(user: dict = Depends(get_user_or_404)):
    return user


@router.post(
    "",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar un nuevo usuario",
    response_description="Usuario creado, incluyendo su ID asignado.",
)
def create_user(data: UserCreate):
    return user_service.create_user(data)


@router.put(
    "/{user_id}",
    response_model=UserResponse,
    summary="Actualizar usuario (reemplazo completo)",
    description="Reemplaza todos los campos del usuario. Requiere enviar el objeto completo.",
    response_description="Usuario con los datos actualizados.",
)
def update_user(
    data: UserUpdate,
    user: dict = Depends(get_user_or_404),
):
    return user_service.replace_user(user, data)


@router.patch(
    "/{user_id}",
    response_model=UserResponse,
    summary="Actualizar usuario (parcial)",
    description="Actualiza solo los campos enviados. Si no se envía ningún campo, responde 400.",
    response_description="Usuario con los campos modificados.",
)
def patch_user(
    data: UserPatch,
    user: dict = Depends(get_user_or_404),
):
    return user_service.patch_user(user, data)


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar usuario",
    description="Elimina un usuario existente. No retorna contenido.",
)
def delete_user(user: dict = Depends(get_user_or_404)):
    user_service.delete_user(user)
    return None
