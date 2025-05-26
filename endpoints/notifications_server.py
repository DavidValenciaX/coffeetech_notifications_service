from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from dataBase import get_db_session
from models.models import NotificationStates, NotificationTypes, Notifications
from utils.response import create_response
from datetime import datetime
from utils.send_fcm_notification import send_fcm_notification
from adapters.user_client import get_user_devices_by_user_id
from firebase_admin._messaging_utils import SenderIdMismatchError
from domain.schemas import (
    UpdateNotificationStateRequest,
    SendNotificationRequest,
)
import logging
import pytz

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/notification-states", include_in_schema=False)
def get_notification_states(db: Session = Depends(get_db_session)):
    """
    Devuelve todos los estados de notificación.
    """
    states = db.query(NotificationStates).all()
    return [{"notification_state_id": s.notification_state_id, "name": s.name} for s in states]

@router.get("/notification-types", include_in_schema=False)
def get_notification_types(db: Session = Depends(get_db_session)):
    """
    Devuelve todos los tipos de notificación.
    """
    types = db.query(NotificationTypes).all()
    return [{"notification_type_id": t.notification_type_id, "name": t.name} for t in types]

@router.get("/notifications", include_in_schema=False)
def get_all_notifications(db: Session = Depends(get_db_session)):
    """
    Devuelve todas las notificaciones.
    """
    notifs = db.query(Notifications).all()
    return [
        {
            "notification_id": n.notification_id,
            "message": n.message,
            "notification_date": n.notification_date,
            "invitation_id": n.invitation_id,
            "notification_type_id": n.notification_type_id,
            "notification_state_id": n.notification_state_id,
            "user_id": n.user_id
        }
        for n in notifs
    ]

@router.get("/notifications/by-invitation/{invitation_id}", include_in_schema=False)
def get_notification_by_invitation(invitation_id: int, db: Session = Depends(get_db_session)):
    """
    Devuelve el notification_id asociado a una invitación.
    """
    
    notification_type_id = db.query(NotificationTypes).filter(
        NotificationTypes.name == "Invitation"
    ).first().notification_type_id
    
    notif = db.query(Notifications).filter(
        Notifications.notification_type_id == notification_type_id,
        Notifications.invitation_id == invitation_id
    ).first()
    if notif:
        return {"notification_id": notif.notification_id}
    else:
        return {"notification_id": None}

@router.delete("/notifications/by-invitation/{invitation_id}", include_in_schema=False)
def delete_notifications_by_invitation(invitation_id: int, db: Session = Depends(get_db_session)):
    """
    Elimina todas las notificaciones de tipo 'Invitation' asociadas a una invitación.
    """
    try:
        invitation_notification_type = db.query(NotificationTypes).filter(
            NotificationTypes.name == "Invitation" 
        ).first()

        if not invitation_notification_type:
            logger.warning("Tipo de notificación 'Invitation' no encontrado en la base de datos. No se pueden eliminar notificaciones específicas.")
            # If the type doesn't exist, no such notifications can be deleted.
            return create_response("success", "Tipo de notificación 'Invitation' no configurado. No se eliminaron notificaciones.", {"deleted_count": 0}, status_code=200)

        notifications_to_delete = db.query(Notifications).filter(
            Notifications.invitation_id == invitation_id,
            Notifications.notification_type_id == invitation_notification_type.notification_type_id
        ).all()

        if not notifications_to_delete:
            logger.info(f"No se encontraron notificaciones de tipo 'Invitation' para eliminar para invitation_id {invitation_id}.")
            return create_response("success", "No se encontraron notificaciones para eliminar.", {"deleted_count": 0}, status_code=200)

        deleted_count = 0
        for notif in notifications_to_delete:
            db.delete(notif)
            deleted_count += 1
        
        db.commit()
        logger.info(f"{deleted_count} notificaciones de tipo 'Invitation' eliminadas para invitation_id {invitation_id}.")
        return create_response("success", f"{deleted_count} notificaciones eliminadas exitosamente.", {"deleted_count": deleted_count}, status_code=200)

    except Exception as e:
        db.rollback()
        logger.error(f"Error eliminando notificaciones por invitation_id {invitation_id}: {str(e)}")
        return create_response("error", f"Error interno del servidor al eliminar notificaciones: {str(e)}", status_code=500)

@router.patch("/notifications/{notification_id}/state", include_in_schema=False)
def update_notification_state(notification_id: int, request: UpdateNotificationStateRequest, db: Session = Depends(get_db_session)):
    """
    Actualiza el estado de una notificación.
    """
    notif = db.query(Notifications).filter(Notifications.notification_id == notification_id).first()
    if not notif:
        return create_response("error", "Notificación no encontrada", status_code=404)
    notif.notification_state_id = request.notification_state_id
    db.commit()
    return create_response("success", "Estado de notificación actualizado")

@router.post("/send-notification", include_in_schema=False)
def send_notification_endpoint(
    request: SendNotificationRequest,
    db: Session = Depends(get_db_session)
):
    """
    Endpoint para enviar una notificación.
    Guarda la notificación en la base de datos y envía una notificación FCM
    a todos los dispositivos del usuario recuperados del servicio de usuarios.
    """
    try:
        bogota_tz = pytz.timezone("America/Bogota")
        # Crear la notificación con user_id
        new_notification = Notifications(
            message=request.message,
            notification_date=datetime.now(bogota_tz),
            invitation_id=request.invitation_id,
            notification_type_id=request.notification_type_id,
            notification_state_id=request.notification_state_id,
            user_id=request.user_id
        )
        db.add(new_notification)
        db.commit()
        
        # Obtener todos los dispositivos del usuario consultando al servicio de usuarios
        user_devices = get_user_devices_by_user_id(request.user_id)
        
        if not user_devices:
            logger.info(f"Usuario {request.user_id} no tiene dispositivos registrados para notificaciones FCM")
            return create_response(
                "success", 
                "Notificación guardada, pero el usuario no tiene dispositivos registrados", 
                {"notification_id": new_notification.notification_id, "devices_notified": 0}
            )
        
        sent_count = 0
        fcm_errors = []
        invalid_tokens = []
        
        # Enviar a todos los dispositivos del usuario
        for device in user_devices:
            try:
                if request.fcm_title and request.fcm_body:
                    response = send_fcm_notification(device["fcm_token"], request.fcm_title, request.fcm_body)
                    if isinstance(response, dict) and response.get("success"):
                        sent_count += 1
                    elif isinstance(response, dict) and response.get("should_delete_token"):
                        # Token inválido que debe ser eliminado
                        invalid_tokens.append(device["fcm_token"])
                        fcm_errors.append({
                            "token": device["fcm_token"],
                            "error_type": response.get("error_type"),
                            "error_message": response.get("error_message")
                        })
            except SenderIdMismatchError:
                # Este error ya está registrado y el token debe ser eliminado
                invalid_tokens.append(device["fcm_token"])
                fcm_errors.append({
                    "token": device["fcm_token"],
                    "error_type": "sender_id_mismatch",
                    "error_message": "Token pertenece a un proyecto FCM diferente"
                })
            except Exception as device_error:
                fcm_errors.append({
                    "token": device["fcm_token"],
                    "error_type": "unknown",
                    "error_message": str(device_error)
                })
                logger.error(f"Error enviando FCM: {str(device_error)}")
        
        # Si se proporcionó un token específico adicional
        if request.fcm_token and request.fcm_title and request.fcm_body:
            try:
                response = send_fcm_notification(request.fcm_token, request.fcm_title, request.fcm_body)
                if isinstance(response, dict) and response.get("success"):
                    sent_count += 1
                elif isinstance(response, dict) and response.get("should_delete_token"):
                    invalid_tokens.append(request.fcm_token)
            except SenderIdMismatchError:
                # Este error ya está registrado y el token debe ser eliminado
                invalid_tokens.append(request.fcm_token)
                fcm_errors.append({
                    "token": request.fcm_token,
                    "error_type": "sender_id_mismatch",
                    "error_message": "Token pertenece a un proyecto FCM diferente"
                })
            except Exception as e:
                fcm_errors.append({
                    "token": request.fcm_token,
                    "error_type": "unknown",
                    "error_message": str(e)
                })
                logger.error(f"Error enviando FCM a token específico: {str(e)}")

        # Registrar y reportar tokens inválidos
        if invalid_tokens:
            # Aquí se podría implementar una llamada al servicio de usuarios
            # para eliminar los tokens inválidos
            logger.warning(f"Tokens FCM inválidos detectados: {invalid_tokens}")
            # TODO: Implementar eliminación de tokens inválidos
            # delete_invalid_tokens(invalid_tokens)

        response_data = {
            "notification_id": new_notification.notification_id,
            "devices_notified": sent_count
        }
        
        if invalid_tokens:
            response_data["invalid_tokens"] = invalid_tokens
            
        if fcm_errors:
            response_data["fcm_errors"] = fcm_errors

        return create_response("success", "Notificación enviada correctamente", response_data)
    except Exception as e:
        db.rollback()
        logger.error(f"Error enviando notificación: {str(e)}")
        return create_response("error", f"Error al enviar la notificación: {str(e)}", status_code=500)
