from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from dataBase import get_db_session
import logging
from use_cases.get_notifications_use_case import GetNotificationsUseCase
from domain.services.notification_service import NotificationService
from adapters.persistence.notification_repository import NotificationRepository

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get(
    "/get-notification",
    response_model=dict,
    responses={
        200: {
            "description": "Respuesta exitosa con notificaciones o sin notificaciones.",
            "content": {
                "application/json": {
                    "examples": {
                        "con_notificaciones": {
                            "summary": "Con notificaciones",
                            "value": {
                                "status": "success",
                                "message": "Notificaciones obtenidas exitosamente.",
                                "data": [
                                    {
                                        "notification_id": 1,
                                        "message": "Tienes una nueva invitación",
                                        "notification_date": "2024-06-01T12:34:56.789Z",
                                        "invitation_id": 123,
                                        "notification_type": "Invitation",
                                        "notification_state": "Pendiente"
                                    }
                                ]
                            }
                        },
                        "sin_notificaciones": {
                            "summary": "Sin notificaciones",
                            "value": {
                                "status": "success",
                                "message": "No hay notificaciones para este usuario.",
                                "data": []
                            }
                        },
                        "token_invalido": {
                            "summary": "Token inválido",
                            "value": {
                                "status": "error",
                                "message": "Token de sesión inválido.",
                                "data": []
                            }
                        }
                    }
                }
            }
        }
    }
)
def get_notifications_endpoint(session_token: str, db: Session = Depends(get_db_session)):
    """
    Endpoint para obtener las notificaciones de un usuario autenticado.

    Parámetros:
    - session_token: Token de sesión del usuario.
    - db: Sesión de la base de datos (inyectada automáticamente).

    Retorna:
    - Respuesta con las notificaciones del usuario.
    """
    # Create dependencies: Repository -> Service -> Use Case
    notification_repository = NotificationRepository(db)
    notification_service = NotificationService(notification_repository)
    use_case = GetNotificationsUseCase(notification_service)
    
    return use_case.execute(session_token)
