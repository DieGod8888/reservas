from fastapi import FastAPI

# Importa los modelos para que create_all registre sus tablas.
from app import models  # noqa: F401
from app.database import Base, engine
from app.routers import reservations, rooms

app = FastAPI(title="API de reservas de salas", version="1.0.0")
app.include_router(rooms.router)
app.include_router(reservations.router)

Base.metadata.create_all(bind=engine)


@app.get("/health", summary="Comprueba que la API está funcionando")
def health():
    return {"status": "ok"}