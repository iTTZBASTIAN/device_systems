# device_systems

API REST con FastAPI, SQLAlchemy, SQLite y Alembic para administrar usuarios, dispositivos tecnológicos y préstamos. La documentación interactiva está disponible en `/docs` y `/redoc`.

## Evolución

- **EV07:** consulta y creación de usuarios en memoria.
- **EV08:** CRUD de usuarios, dependencias y manejo de errores.
- **EV09:** persistencia de usuarios con SQLAlchemy y SQLite.
- **EV10:** migraciones Alembic, relaciones entre modelos, inventario de dispositivos, préstamos, devoluciones y consultas con joins.

## Estructura

```text
device_systems/
├── alembic/
│   ├── versions/
│   └── env.py
├── app/
│   ├── database/connection.py
│   ├── dependencies/
│   ├── models/{user,device,loan}_model.py
│   ├── routes/{user,device,loan}_routes.py
│   ├── schemas/{user,device,loan}_schema.py
│   ├── services/{user,device,loan}_service.py
│   └── main.py
├── tests/
├── alembic.ini
├── pytest.ini
└── requirements.txt
```

## Instalación y ejecución

Desde la raíz del repositorio, en PowerShell:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload
```

En Linux o macOS, activa el entorno con `source .venv/bin/activate`. La URL predeterminada es `sqlite:///./device_systems.db`; se puede sustituir mediante la variable de entorno `DATABASE_URL`. La aplicación no crea tablas al importarse: el esquema se administra con Alembic.

- Swagger UI: <http://127.0.0.1:8000/docs>
- ReDoc: <http://127.0.0.1:8000/redoc>
- Healthcheck: <http://127.0.0.1:8000/>

## Modelo relacional

| Tabla | Campos principales | Relación |
|---|---|---|
| `users` | `id`, `name`, `email`, `role`, `is_active`, `created_at` | Un usuario tiene muchos préstamos. |
| `devices` | `id`, `name`, `serial_number`, `device_type`, `brand`, `is_available`, `created_at` | Un dispositivo aparece en muchos préstamos históricos. |
| `loans` | `id`, `user_id`, `device_id`, `loan_date`, `return_date`, `status` | Cada préstamo referencia un usuario y un dispositivo existentes. |

Las relaciones ORM usan `relationship()` y `back_populates`. Las claves foráneas restringen la eliminación de usuarios o dispositivos con historial, y SQLite tiene activada la comprobación de claves foráneas. Un préstamo `active` o `overdue` impide marcar el equipo disponible; al devolverlo, el servicio actualiza el préstamo y el equipo en la misma sesión.

## Migraciones Alembic

Alembic está configurado para importar la metadata de los tres modelos. La primera revisión establece la línea base de `users`: crea la tabla si no existe y reconoce una tabla de EV09 existente. La siguiente revisión fue generada con autogeneración y crea `devices` y `loans`; también tolera que esas tablas ya existan en una instalación local sin historial Alembic.

```powershell
# Estructura inicial (ya incluida en este repositorio)
alembic init alembic

# Generar una revisión después de modificar modelos
alembic revision --autogenerate -m "descripcion del cambio"

# Aplicar migraciones y consultar el historial/estado
alembic upgrade head
alembic history
alembic current
alembic check
```

Revisiones incluidas:

- `ev10_users`: línea base compatible con EV09 y creación de `users` en bases nuevas.
- `ae2a2c362392`: creación autogenerada de `devices` y `loans`, con sus índices y claves foráneas.

Antes de aplicar migraciones sobre una base con información importante, conserva una copia de seguridad. No edites una revisión que ya se haya aplicado en otros ambientes; crea una nueva.

## Endpoints

### Users

| Método | Ruta | Descripción |
|---|---|---|
| GET | `/users` | Lista usuarios; admite `role`, `is_active` y `order_by`. |
| POST | `/users` | Crea un usuario. |
| GET | `/users/{user_id}` | Consulta un usuario. |
| PUT/PATCH | `/users/{user_id}` | Reemplaza o actualiza parcialmente un usuario. |
| DELETE | `/users/{user_id}` | Elimina si no tiene historial de préstamos. |
| GET | `/users/{user_id}/loans` | Consulta sus préstamos con usuario y dispositivo relacionados. |

### Devices

| Método | Ruta | Descripción |
|---|---|---|
| GET | `/devices` | Lista equipos con filtros opcionales. |
| POST | `/devices` | Registra un equipo; `serial_number` debe ser único. |
| GET | `/devices/{device_id}` | Consulta un equipo. |
| PUT/PATCH | `/devices/{device_id}` | Reemplaza o actualiza parcialmente un equipo. |
| DELETE | `/devices/{device_id}` | Elimina si no tiene historial de préstamos. |
| GET | `/devices/{device_id}/loans` | Consulta el historial de préstamos del equipo. |

Filtros de `GET /devices`: `device_type`, `is_available`, `brand` y `search`. Ejemplos: `/devices?device_type=laptop`, `/devices?is_available=true&brand=lenovo` y `/devices?search=thinkpad`.

### Loans

| Método | Ruta | Descripción |
|---|---|---|
| GET | `/loans` | Lista préstamos con datos de usuario y dispositivo. |
| GET | `/loans/details` | Consulta detallada equivalente para explorar joins. |
| POST | `/loans` | Crea un préstamo si existen el usuario y el dispositivo disponible. |
| GET | `/loans/{loan_id}` | Consulta un préstamo. |
| PATCH | `/loans/{loan_id}/return` | Registra la devolución y vuelve a habilitar el equipo. |

Filtros combinables para `GET /loans` y `/loans/details`: `status` (`active`, `returned`, `overdue`), `user_email`, `device_type`, `date_from` y `date_to` (fecha ISO 8601). Ejemplos: `/loans?status=active`, `/loans?user_email=ana@sena.edu.co&device_type=laptop`.

Las consultas relacionadas hacen `join()` entre `loans`, `users` y `devices`, y combinan condiciones con `and_()`, `ilike()` y filtros opcionales.

## Ejemplos

Crear un usuario y un equipo:

```bash
curl -X POST http://127.0.0.1:8000/users -H "Content-Type: application/json" -d '{"name":"Ana Perez","email":"ana@sena.edu.co","role":"user"}'
curl -X POST http://127.0.0.1:8000/devices -H "Content-Type: application/json" -d '{"name":"ThinkPad T14","serial_number":"LEN-2024-001","device_type":"laptop","brand":"Lenovo"}'
```

Con los ID que devuelven las respuestas, crear y consultar un préstamo:

```bash
curl -X POST http://127.0.0.1:8000/loans -H "Content-Type: application/json" -d '{"user_id":1,"device_id":1}'
curl "http://127.0.0.1:8000/loans/details?status=active&device_type=laptop"
curl -X PATCH http://127.0.0.1:8000/loans/1/return
```

La respuesta detallada incluye el estado y la fecha del préstamo, además de `user` (id, nombre y correo) y `device` (id, nombre, serial y tipo).

## Errores y estados HTTP

| Caso | Código |
|---|---:|
| Creación correcta | 201 |
| Consulta, actualización o devolución correcta | 200 |
| Eliminación correcta, sin contenido | 204 |
| Usuario, dispositivo o préstamo inexistente | 404 |
| Correo o serial duplicado | 400 |
| Equipo no disponible, devolución repetida o eliminación con historial | 409 |
| Datos, filtros o rango de fechas inválidos | 422 |

Las respuestas conservan las cabeceras `X-App-Name: device_systems` y `X-API-Version: 4.0.0`.

## Pruebas

Las pruebas usan una base SQLite temporal, separada de la base de desarrollo:

```powershell
pytest -q
```

Cubren creación de usuario/equipo/préstamo, préstamo de un equipo ocupado, joins y filtros, consulta de historiales, devolución y disponibilidad, serial duplicado, referencias inexistentes, filtros inválidos y protección del historial.

## Evidencias de entrega

¡[Alembic evidence](images/alembic-evidence.png)
filtros, joins, devolución y disponibilidad posterior. Las capturas EV09 ya existentes en `images/` corresponden a la actividad anterior; no se presentan como evidencia EV10.

## Reflexión

Alembic permite evolucionar el esquema con cambios revisables y repetibles, sin depender de la creación automática de tablas al iniciar la aplicación. Las relaciones y claves foráneas expresan la integridad del dominio; conservar el historial de préstamos evita perder trazabilidad. Los joins permiten entregar datos útiles al cliente en una consulta y los filtros opcionales hacen que el mismo endpoint sirva para búsquedas concretas sin duplicar rutas.
