from fastapi import FastAPI

# Importa los modelos para que create_all registre sus tablas.
from app import models  # noqa: F401
from app.database import Base, engine

app = FastAPI(title="API de reservas de salas", version="1.0.0")

Base.metadata.create_all(bind=engine)


@app.get("/health", summary="Comprueba que la API está funcionando")
def health():
    return {"status": "ok"} 