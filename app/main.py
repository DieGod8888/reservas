from fastapi import FastAPI

app = FastAPI(title="API de reservas de salas", version="1.0.0")


@app.get("/health", summary="Comprueba que la API está funcionando")
def health():
    return {"status": "ok"}
