"""
Lógica de negocio del recurso 'users'.

Separa las reglas de negocio de las rutas: las rutas solo reciben la
petición HTTP y delegan aquí el trabajo real.
"""

from typing import Optional

from fastapi import HTTPException, status

from app.data.users_db import users_db, get_next_id
from app.schemas.user_schema import UserCreate, UserUpdate, UserPatch


def list_users(role: Optional[str] = None, is_active: Optional[bool] = None) -> list[dict]:
    result = users_db
    if role is not None:
        result = [u for u in result if u["role"] == role]
    if is_active is not None:
        result = [u for u in result if u["is_active"] == is_active]
    return result


def find_user_by_id(user_id: int) -> Optional[dict]:
    return next((u for u in users_db if u["id"] == user_id), None)


def find_user_by_email(email: str, exclude_id: Optional[int] = None) -> Optional[dict]:
    return next(
        (u for u in users_db if u["email"] == email and u["id"] != exclude_id),
        None,
    )


def create_user(data: UserCreate) -> dict:
    if find_user_by_email(data.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El correo ya está registrado",
        )
    new_user = {"id": get_next_id(), **data.model_dump()}
    users_db.append(new_user)
    return new_user


def replace_user(user: dict, data: UserUpdate) -> dict:
    """Actualización completa (PUT): reemplaza todos los campos."""
    if find_user_by_email(data.email, exclude_id=user["id"]):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El correo ya está registrado",
        )
    user.update(data.model_dump())
    return user


def patch_user(user: dict, data: UserPatch) -> dict:
    """Actualización parcial (PATCH): solo cambia los campos enviados."""
    if not data.has_data():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Debe enviar al menos un campo para actualizar",
        )

    updates = data.model_dump(exclude_unset=True)

    if "email" in updates and find_user_by_email(updates["email"], exclude_id=user["id"]):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El correo ya está registrado",
        )

    user.update(updates)
    return user


def delete_user(user: dict) -> None:
    users_db.remove(user)
