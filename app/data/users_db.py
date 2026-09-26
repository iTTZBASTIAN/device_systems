"""
Simulación de base de datos en memoria para el recurso 'users'.

En EV09 esto se reemplaza por persistencia real con SQLAlchemy.
"""

users_db: list[dict] = [
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

# Contador simple para asignar IDs nuevos
_counter = {"next_id": 3}


def get_next_id() -> int:
    new_id = _counter["next_id"]
    _counter["next_id"] += 1
    return new_id
