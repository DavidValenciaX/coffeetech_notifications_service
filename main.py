from fastapi import FastAPI
from endpoints import notifications
import logging

app = FastAPI()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Incluir las rutas de notificaciones
app.include_router(notifications.router, prefix="/notification", tags=["Notificaciones"])

@app.get("/")
def read_root():
    """
    Ruta raíz que retorna un mensaje de bienvenida.

    Returns:
        dict: Un diccionario con un mensaje de bienvenida.
    """
    return {"message": "Welcome to the FastAPI application CoffeeTech!"}