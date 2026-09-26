# device_systems

API REST desarrollada con **FastAPI** para la gestión del recurso **usuarios**, correspondiente a la actividad **GA1-220501096-01-AA1-EV07 — Fundamentos de FastAPI: API REST para Gestión de Usuarios**.

## Descripción

`device_systems` expone un CRUD parcial (GET y POST) sobre el recurso `/users`, aplicando:

- Validación de datos con **Pydantic v2**.
- **Path Parameters** (`/users/{user_id}`).
- **Query Parameters** (`?role=`, `?is_active=`).
- **Response Models** para controlar qué datos se exponen.
- **Cabeceras HTTP personalizadas** (`X-App-Name`, `X-API-Version`) en cada respuesta.
- Control de correos duplicados al crear un usuario.

En esta actividad los usuarios se almacenan en memoria (una lista). La persistencia en base de datos con SQLAlchemy se implementa en la actividad EV09.

## Estructura del proyecto

```
device_systems/
├── app/
│   ├── main.py
│   ├── schemas/
│   │   └── user_schema.py
│   └── routes/
│       └── user_routes.py
├── requirements.txt
└── README.md
```

## Instalación

```bash
python -m venv venv
source venv/bin/activate   # En Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Ejecución

Desde la carpeta raíz del proyecto (`device_systems/`):

```bash
uvicorn app.main:app --reload
```

La API quedará disponible en `http://127.0.0.1:8000`.

Documentación interactiva:

- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`

## Modelo de usuario

| Campo     | Tipo   | Validación                                   |
|-----------|--------|-----------------------------------------------|
| id        | int    | Generado automáticamente                     |
| name      | str    | Obligatorio, mínimo 3 caracteres             |
| email     | str    | Formato de correo válido, único              |
| role      | str    | Uno de: `admin`, `support`, `user`           |
| is_active | bool   | Valor por defecto `true`                     |

## Tabla de endpoints

| Método | Ruta                     | Descripción                              | Código éxito |
|--------|--------------------------|-------------------------------------------|--------------|
| GET    | `/users`                 | Lista todos los usuarios                  | 200 OK       |
| GET    | `/users?role=admin`      | Filtra usuarios por rol                   | 200 OK       |
| GET    | `/users?is_active=true`  | Filtra usuarios activos/inactivos         | 200 OK       |
| GET    | `/users/{user_id}`       | Consulta un usuario por ID                | 200 OK / 404 |
| POST   | `/users`                 | Crea un nuevo usuario                     | 201 Created / 400 |

## Ejemplos de peticiones

### GET /users

```bash
curl http://127.0.0.1:8000/users
```

### GET /users/1

```bash
curl http://127.0.0.1:8000/users/1
```

### GET /users?role=admin

```bash
curl "http://127.0.0.1:8000/users?role=admin"
```

### POST /users

```bash
curl -X POST http://127.0.0.1:8000/users \
  -H "Content-Type: application/json" \
  -d '{
        "name": "Laura Rojas",
        "email": "laura@sena.edu.co",
        "role": "support",
        "is_active": true
      }'
```

Respuesta esperada (201 Created):

```json
{
  "id": 3,
  "name": "Laura Rojas",
  "email": "laura@sena.edu.co",
  "role": "support",
  "is_active": true
}
```

### Intentar crear un correo duplicado

```bash
curl -X POST http://127.0.0.1:8000/users \
  -H "Content-Type: application/json" \
  -d '{"name":"Otro","email":"ana@sena.edu.co","role":"user","is_active":true}'
```

Respuesta esperada (400 Bad Request):

```json
{ "detail": "El correo ya está registrado" }
```

## Cabeceras personalizadas

Toda respuesta de la API incluye:

```
X-App-Name: device_systems
X-API-Version: 1.0
```

Se pueden verificar con:

```bash
curl -i http://127.0.0.1:8000/users
```

## Capturas de Swagger UI

[vista general](images/vista1.png)

[vista general](images/vista2.png)

[GET users](images/Get-users.png)

[GET users](images/Get-users1.png)

[GET users por id](images/get-users-id.png)

[GET users por id](images/get-users-id1.png)

[GET users por id (error)](images/get-users-id-error.png)

[GET users por id (error)](images/get-users-id-error1.png)

[POST users](images/post-users.png)

[POST users](images/post-users1.png)

## Reflexión

Este ejercicio nos permite entender como desarrollar un proyecto con fastAPI, usando Pydantic v2 y uvicorn, entendiendo la conexión y la lógica de JSON
