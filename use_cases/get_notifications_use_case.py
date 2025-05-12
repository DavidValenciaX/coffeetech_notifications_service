from fastapi import Depends
from sqlalchemy.orm import Session
from dataBase import get_db_session
from models.models import Notifications
from utils.response import create_response, session_token_invalid_response
from adapters.user_client import verify_session_token
from domain.schemas import NotificationResponse
import logging

logger = logging.getLogger(__name__)

def get_notifications(session_token: str, db: Session = Depends(get_db_session)):
    user = verify_session_token(session_token)
    if not user:
        logger.warning(f"Sesión inválida para el token: {session_token}")
        return session_token_invalid_response()

    logger.info(f"Usuario autenticado: {user['user_id']} - {user['name']}")

    # Consultar directamente las notificaciones del usuario por su user_id
    notifications = db.query(Notifications).filter(Notifications.user_id == user['user_id']).all()
    logger.info(f"Notificaciones obtenidas: {len(notifications)}")

    if not notifications:
        logger.info("No hay notificaciones para este usuario.")
        return create_response("success", "No hay notificaciones para este usuario.", data=[])

    # Serializar las notificaciones
    try:
        notification_responses = [
            NotificationResponse(
                notification_id=notification.notification_id,
                message=notification.message,
                notification_date=notification.notification_date,
                invitation_id=notification.invitation_id,
                notification_type=notification.notification_type.name if notification.notification_type else None,
                notification_state=notification.state.name if notification.state else None
            )
            for notification in notifications
        ]
        logger.info(f"Notificaciones serializadas correctamente: {len(notification_responses)}")
        notification_responses_dict = [n.model_dump() for n in notification_responses]
    except Exception as e:
        logger.error(f"Error de serialización: {e}")
        return create_response("error", f"Error de serialización: {str(e)}", data=[])

    return create_response("success", "Notificaciones obtenidas exitosamente.", data=notification_responses_dict)