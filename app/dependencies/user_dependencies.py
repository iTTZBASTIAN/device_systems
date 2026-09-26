"""
Dependencias reutilizables para las rutas del recurso 'users',
pensadas para usarse con Depends().
"""

from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.dependencies.database_dependency import get_db
from app.services import user_service


def get_user_or_404(user_id: int, db: Session = Depends(get_db)):
    """
    Busca un usuario por su ID en la base de datos. Si no existe,
    corta la petición con 404. Se usa como Depends() en las rutas que
    operan sobre un usuario existente (GET por ID, PUT, PATCH, DELETE).
    """
    user = user_service.get_user_by_id(db, user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado",
        )
    return user
