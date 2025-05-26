from fastapi import FastAPI
from endpoints.external import notifications_external
from endpoints.internal import notifications_internal
from utils.logger import setup_logger

app = FastAPI()

# Setup logging for the entire application
logger = setup_logger()
logger.info("Starting CoffeeTech Notification Service")

# Incluir las rutas de notificaciones externas (clientes móvil/web)
app.include_router(notifications_external.router, prefix="/notification", tags=["Notificaciones"])

# Incluir las rutas de notificaciones internas (microservicios)
app.include_router(notifications_internal.router)

@app.get("/", include_in_schema=False)
def read_root():
    """
    Ruta raíz que retorna un mensaje de bienvenida.

    Returns:
        dict: Un diccionario con un mensaje de bienvenida.
    """
    logger.info("Root endpoint accessed")
    return {"message": "Welcome to the FastAPI application CoffeeTech Notification Service!"}