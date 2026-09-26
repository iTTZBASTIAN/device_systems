"""
Endpoints del recurso 'users' para device_systems.

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


@router.get(
    "",
    response_model=list[UserResponse],
    summary="Listar usuarios",
    description="Lista todos los usuarios. Permite filtrar por rol y por estado activo.",
)
def list_users(
    role: Optional[RoleType] = Query(None, description="Filtrar por rol: admin, support o user."),
    is_active: Optional[bool] = Query(None, description="Filtrar por estado activo/inactivo."),
):
    result = _fake_db
    if role is not None:
        result = [u for u in result if u["role"] == role]
    if is_active is not None:
        result = [u for u in result if u["is_active"] == is_active]
    return result


@router.get(
    "/{user_id}",
    response_model=UserResponse,
    summary="Consultar usuario por ID",
)
def get_user(user_id: int):
    for user in _fake_db:
        if user["id"] == user_id:
            return user
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")


@router.post(
    "",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar un nuevo usuario",
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
