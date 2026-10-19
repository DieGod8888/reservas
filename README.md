# API de reservas de salas

API REST para gestionar la reserva de salas de reuniones o de estudio. Permite crear salas con su capacidad y reservarlas por horario, sin que dos reservas de la misma sala se crucen. Es un proyecto de portafolio, pensado para ser claro y fácil de explicar.

## Tecnologías

- Python 3.12 y FastAPI
- SQLAlchemy 2 con PyMySQL y MySQL 8
- Pydantic para validar las entradas
- pytest con el TestClient de FastAPI (las pruebas usan SQLite en memoria)
- Ruff como linter y formateador
- Docker y docker compose

## Ejecutar con Docker

Copia el archivo de entorno y levanta todo con un solo comando:

```bash
cp .env.example .env
docker compose up --build
```

En Windows: `Copy-Item .env.example .env`.

El servicio de MySQL tiene healthcheck y la aplicación espera a que la base esté lista. Las tablas se crean solas al arrancar, no hay migraciones. Al terminar:

- API en http://localhost:8000
- Documentación interactiva en http://localhost:8000/docs
- Para detener: `docker compose down`

Las credenciales del `.env` son solo para desarrollo local. El archivo `.env` no se sube al repositorio.

## Ejecutar las pruebas

Con Python 3.12 instalado:

```bash
python -m venv .venv
source .venv/bin/activate   # en Windows: .venv\Scripts\activate
pip install -r requirements.txt
pytest
```

Para revisar y formatear el código:

```bash
ruff check .
ruff format .
```

## Endpoints

| Método | Ruta | Descripción |
| --- | --- | --- |
| GET | `/health` | Comprueba que la API está funcionando |
| GET | `/rooms` | Lista todas las salas |
| POST | `/rooms` | Crea una sala |
| GET | `/rooms/{id}` | Obtiene una sala |
| PUT | `/rooms/{id}` | Actualiza una sala |
| DELETE | `/rooms/{id}` | Elimina una sala |
| GET | `/reservations` | Lista las reservas, con filtro opcional `?room_id=` |
| POST | `/reservations` | Crea una reserva |
| GET | `/reservations/{id}` | Obtiene una reserva |
| PUT | `/reservations/{id}` | Actualiza una reserva |
| DELETE | `/reservations/{id}` | Elimina una reserva |

### Ejemplo: crear una sala

```bash
curl -X POST http://localhost:8000/rooms \
  -H "Content-Type: application/json" \
  -d '{"name": "Sala A", "capacity": 8}'
```

Respuesta `201`:

```json
{"id": 1, "name": "Sala A", "capacity": 8}
```

### Ejemplo: crear una reserva

```bash
curl -X POST http://localhost:8000/reservations \
  -H "Content-Type: application/json" \
  -d '{"room_id": 1, "customer_name": "Ana", "start_time": "2026-10-20T10:00:00", "end_time": "2026-10-20T11:00:00"}'
```

Las fechas van sin zona horaria. Los horarios se tratan como `[inicio, fin)`: una reserva que termina a las 11:00 y otra que empieza a las 11:00 no se consideran cruzadas.

### Errores

- `404`: la sala o la reserva no existe.
- `409`: nombre de sala duplicado, sala con reservas al eliminarla, o horario que se cruza con otra reserva de la misma sala.
- `422`: datos inválidos, por ejemplo que `end_time` no sea posterior a `start_time`.

## Estructura del proyecto

├── app
│   ├── main.py            App, creación de tablas y /health
│   ├── database.py        Engine, sesión y dependencia get_db
│   ├── models.py          Tablas rooms y reservations
│   ├── schemas.py         Modelos de Pydantic y validadores
│   └── routers
│       ├── rooms.py       CRUD de salas
│       └── reservations.py CRUD de reservas con sus reglas
├── tests
│   ├── conftest.py        Cliente de prueba con SQLite en memoria
│   ├── test_rooms.py      Pruebas de los endpoints de salas
│   └── test_reservations.py Pruebas de los endpoints de reservas
├── Dockerfile
├── docker-compose.yml     App y MySQL con healthcheck
├── .env.example           Variables de entorno de ejemplo
├── requirements.txt
└── README.md