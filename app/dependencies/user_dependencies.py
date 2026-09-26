"""
Dependencias reutilizables para las rutas del recurso 'users',
pensadas para usarse con Depends().
"""

from fastapi import HTTPException, status

from app.services.user_service import find_user_by_id


def get_user_or_404(user_id: int) -> dict:
    """
    Busca un usuario por su ID. Si no existe, corta la petición con 404.
    Se usa como Depends() en las rutas que operan sobre un usuario
    existente (GET por ID, PUT, PATCH, DELETE).
    """
    user = find_user_by_id(user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado",
        )
    return user
