"""
Endpoints del recurso 'users' para device_systems.

Las rutas son "delgadas": reciben la petición, obtienen la sesión de
base de datos vía Depends(get_db), validan con los schemas y delegan
la lógica al servicio.
"""

from typing import Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.schemas.user_schema import (
    UserCreate,
    UserUpdate,
    UserPatch,
    UserResponse,
    RoleType,
)
from app.dependencies.database_dependency import get_db
from app.dependencies.user_dependencies import get_user_or_404
from app.models.user_model import User
from app.services import user_service

router = APIRouter(prefix="/users", tags=["Users"])


@router.get(
    "",
    response_model=list[UserResponse],
    summary="Listar usuarios",
    description="Lista usuarios almacenados en la base de datos. Permite filtrar por rol y estado, y ordenar por nombre o fecha de creación.",
    response_description="Lista de usuarios que cumplen los filtros aplicados.",
)
def list_users(
    role: Optional[RoleType] = Query(None, description="Filtrar por rol: admin, support o user."),
    is_active: Optional[bool] = Query(None, description="Filtrar por estado activo/inactivo."),
    order_by: Optional[str] = Query(
        None, description="Ordenar por 'name' o 'created_at'.", pattern="^(name|created_at)$"
    ),
    db: Session = Depends(get_db),
):
    return user_service.list_users(db, role=role, is_active=is_active, order_by=order_by)


@router.get(
    "/{user_id}",
    response_model=UserResponse,
    summary="Consultar usuario por ID",
    response_description="Datos del usuario solicitado.",
)
def get_user(user: User = Depends(get_user_or_404)):
    return user


@router.post(
    "",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar un nuevo usuario",
    response_description="Usuario creado en la base de datos, incluyendo su ID y fecha de creación.",
)
def create_user(data: UserCreate, db: Session = Depends(get_db)):
    return user_service.create_user(db, data)


@router.put(
    "/{user_id}",
    response_model=UserResponse,
    summary="Actualizar usuario (reemplazo completo)",
    description="Reemplaza todos los campos del usuario. Requiere enviar el objeto completo.",
    response_description="Usuario con los datos actualizados.",
)
def update_user(
    data: UserUpdate,
    user: User = Depends(get_user_or_404),
    db: Session = Depends(get_db),
):
    return user_service.replace_user(db, user, data)


@router.patch(
    "/{user_id}",
    response_model=UserResponse,
    summary="Actualizar usuario (parcial)",
    description="Actualiza solo los campos enviados. Si no se envía ningún campo, responde 400.",
    response_description="Usuario con los campos modificados.",
)
def patch_user(
    data: UserPatch,
    user: User = Depends(get_user_or_404),
    db: Session = Depends(get_db),
):
    return user_service.patch_user(db, user, data)


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar usuario",
    description="Elimina un usuario existente de la base de datos. No retorna contenido.",
)
def delete_user(user: User = Depends(get_user_or_404), db: Session = Depends(get_db)):
    user_service.delete_user(db, user)
    return None
