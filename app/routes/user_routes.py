"""
Endpoints del recurso 'users' para device_systems.

<<<<<<< HEAD
Almacenamiento: lista en memoria (esta actividad -EV07- no usa base de
datos todavía; SQLAlchemy se agrega en una actividad posterior).
"""

from typing import Optional
from fastapi import APIRouter, HTTPException, Query, status

from app.schemas.user_schema import UserCreate, UserResponse, RoleType

router = APIRouter(prefix="/users", tags=["Users"])

# "Base de datos" en memoria, con un par de usuarios de ejemplo
_fake_db: list[dict] = [
    {
        "id": 1,
        "name": "Ana Pérez",
        "email": "ana@sena.edu.co",
        "role": "admin",
        "is_active": True,
    },
    {
        "id": 2,
        "name": "Carlos Gómez",
        "email": "carlos@sena.edu.co",
        "role": "user",
        "is_active": False,
    },
]
_next_id = 3

=======
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

>>>>>>> feature/ev08

@router.get(
    "",
    response_model=list[UserResponse],
    summary="Listar usuarios",
    description="Lista todos los usuarios. Permite filtrar por rol y por estado activo.",
<<<<<<< HEAD
=======
    response_description="Lista de usuarios que cumplen los filtros aplicados.",
>>>>>>> feature/ev08
)
def list_users(
    role: Optional[RoleType] = Query(None, description="Filtrar por rol: admin, support o user."),
    is_active: Optional[bool] = Query(None, description="Filtrar por estado activo/inactivo."),
):
<<<<<<< HEAD
    result = _fake_db
    if role is not None:
        result = [u for u in result if u["role"] == role]
    if is_active is not None:
        result = [u for u in result if u["is_active"] == is_active]
    return result
=======
    return user_service.list_users(role=role, is_active=is_active)
>>>>>>> feature/ev08


@router.get(
    "/{user_id}",
    response_model=UserResponse,
    summary="Consultar usuario por ID",
<<<<<<< HEAD
)
def get_user(user_id: int):
    for user in _fake_db:
        if user["id"] == user_id:
            return user
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")
=======
    response_description="Datos del usuario solicitado.",
)
def get_user(user: dict = Depends(get_user_or_404)):
    return user
>>>>>>> feature/ev08


@router.post(
    "",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar un nuevo usuario",
<<<<<<< HEAD
)
def create_user(user: UserCreate):
    global _next_id

    if any(u["email"] == user.email for u in _fake_db):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El correo ya está registrado",
        )

    new_user = {"id": _next_id, **user.model_dump()}
    _fake_db.append(new_user)
    _next_id += 1
    return new_user
=======
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
>>>>>>> feature/ev08
