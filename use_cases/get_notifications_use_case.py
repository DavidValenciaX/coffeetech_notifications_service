from fastapi import Depends
from sqlalchemy.orm import Session
from dataBase import get_db_session
from models.models import Notifications, UserDevices, NotificationDevices, NotificationTypes
from utils.response import create_response, session_token_invalid_response
from adapters.user_client import verify_session_token
from adapters.invitation_client import get_invitation_details
from domain.schemas import NotificationResponse
import logging

logger = logging.getLogger(__name__)

def get_notifications(session_token: str, db: Session = Depends(get_db_session)):
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

    # Filtrar notificaciones tipo invitación para asegurar que son para este usuario específico
    filtered_notifications = []
    invitation_type = db.query(NotificationTypes).filter(NotificationTypes.name == "Invitation").first()
    
    for notification in notifications:
        # Para notificaciones tipo invitación, verificar si el usuario es el invitado
        if invitation_type and notification.notification_type_id == invitation_type.notification_type_id:
            # Obtener detalles de la invitación para verificar el invited_user_id
            if notification.invitation_id:
                invitation = get_invitation_details(notification.invitation_id)
                if invitation and invitation.get("invited_user_id") == user["user_id"]:
                    filtered_notifications.append(notification)
        else:
            # Para otros tipos de notificaciones, incluirlas sin filtro adicional
            filtered_notifications.append(notification)

    logger.info(f"Notificaciones filtradas: {len(filtered_notifications)}")

    if not filtered_notifications:
        logger.info("No hay notificaciones para este usuario después del filtrado.")
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
            for notification in filtered_notifications
        ]
        logger.info(f"Notificaciones serializadas correctamente: {len(notification_responses)}")
        notification_responses_dict = [n.model_dump() for n in notification_responses]
    except Exception as e:
        logger.error(f"Error de serialización: {e}")
        return create_response("error", f"Error de serialización: {str(e)}", data=[])

    return create_response("success", "Notificaciones obtenidas exitosamente.", data=notification_responses_dict)