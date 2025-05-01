from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from dataBase import get_db_session
import logging
from use_cases.get_notifications_use_case import get_notifications

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/get-notification")
def get_notifications_endpoint(session_token: str, db: Session = Depends(get_db_session)):
    """
    Endpoint para obtener las notificaciones de un usuario autenticado.

    Parámetros:
    - session_token: Token de sesión del usuario.
    - db: Sesión de la base de datos (inyectada automáticamente).

    Retorna:
    - Respuesta con las notificaciones del usuario.
    """
    # Verificar el session_token y obtener el usuario autenticado
    return get_notifications(session_token, db)
