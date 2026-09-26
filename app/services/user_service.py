"""
Lógica de negocio del recurso 'users', ahora sobre base de datos real
mediante SQLAlchemy. Las rutas reciben la petición HTTP y delegan aquí
el trabajo de consultar/modificar la base de datos.
"""

from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.user_model import User
from app.models.loan_model import Loan
from app.schemas.user_schema import UserCreate, UserUpdate, UserPatch


def list_users(
    db: Session,
    role: Optional[str] = None,
    is_active: Optional[bool] = None,
    order_by: Optional[str] = None,
) -> list[User]:
    query = db.query(User)

    if role is not None:
        query = query.filter(User.role == role)
    if is_active is not None:
        query = query.filter(User.is_active == is_active)

    if order_by == "name":
        query = query.order_by(User.name)
    elif order_by == "created_at":
        query = query.order_by(User.created_at)

    return query.all()


def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    return db.query(User).filter(User.id == user_id).first()


def get_user_by_email(
    db: Session, email: str, exclude_id: Optional[int] = None
) -> Optional[User]:
    query = db.query(User).filter(User.email == email)
    if exclude_id is not None:
        query = query.filter(User.id != exclude_id)
    return query.first()


def create_user(db: Session, data: UserCreate) -> User:
    if get_user_by_email(db, data.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El correo ya está registrado",
        )
    new_user = User(**data.model_dump())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


def replace_user(db: Session, user: User, data: UserUpdate) -> User:
    """Actualización completa (PUT): reemplaza todos los campos."""
    if get_user_by_email(db, data.email, exclude_id=user.id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El correo ya está registrado",
        )
    for field, value in data.model_dump().items():
        setattr(user, field, value)
    db.commit()
    db.refresh(user)
    return user


def patch_user(db: Session, user: User, data: UserPatch) -> User:
    """Actualización parcial (PATCH): solo cambia los campos enviados."""
    if not data.has_data():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Debe enviar al menos un campo para actualizar",
        )

    updates = data.model_dump(exclude_unset=True)

    if "email" in updates and get_user_by_email(db, updates["email"], exclude_id=user.id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El correo ya está registrado",
        )

    for field, value in updates.items():
        setattr(user, field, value)
    db.commit()
    db.refresh(user)
    return user


def delete_user(db: Session, user: User) -> None:
    if db.query(Loan).filter(Loan.user_id == user.id).first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="No se puede eliminar un usuario con historial de préstamos",
        )
    db.delete(user)
    db.commit()
