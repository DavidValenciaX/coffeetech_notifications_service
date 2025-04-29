from fastapi import Depends
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime
from dataBase import get_db_session
from pydantic import BaseModel
from models.models import Notifications, UserDevices, NotificationDevices
import logging
from utils.response import create_response, session_token_invalid_response
from use_cases.verify_session_token_use_case import verify_session_token

logger = logging.getLogger(__name__)

USER_SERVICE_BASE_URL = "http://localhost:8000/user-service"

class NotificationResponse(BaseModel):
    notification_id: int
    message: Optional[str]
    notification_date: datetime
    entity_type: Optional[str]
    entity_id: Optional[int]
    notification_type: Optional[str]
    notification_state: Optional[str]

    class Config:
        # Pydantic v2: permite poblar desde atributos ORM
        from_attributes = True
        # formatea datetimes a ISO 8601
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

def get_notifications_use_case(session_token: str, db: Session = Depends(get_db_session)):
    user = verify_session_token(session_token)
    if not user:
        logger.warning(f"Sesión inválida para el token: {session_token}")
        return session_token_invalid_response()

    logger.info(f"Usuario autenticado: {user['user_id']} - {user['name']}")

    # Obtener los dispositivos del usuario
    user_devices = db.query(UserDevices).filter(UserDevices.user_id == user['user_id']).all()
    user_device_ids = [ud.user_device_id for ud in user_devices]
    logger.info(f"Dispositivos del usuario: {user_device_ids}")

    if not user_device_ids:
        logger.info("El usuario no tiene dispositivos registrados.")
        return create_response("success", "No hay notificaciones para este usuario.", data=[])

    # Obtener los notification_ids asociados a los dispositivos del usuario
    notification_device_rows = db.query(NotificationDevices).filter(
        NotificationDevices.user_device_id.in_(user_device_ids)
    ).all()
    notification_ids = list({nd.notification_id for nd in notification_device_rows})
    logger.info(f"IDs de notificaciones asociadas a los dispositivos: {notification_ids}")

    if not notification_ids:
        logger.info("No hay notificaciones para los dispositivos de este usuario.")
        return create_response("success", "No hay notificaciones para este usuario.", data=[])

    # Consultar las notificaciones usando los notification_ids
    notifications = db.query(Notifications).filter(Notifications.notification_id.in_(notification_ids)).all()
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
                entity_type=notification.entity_type,
                entity_id=notification.entity_id,
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