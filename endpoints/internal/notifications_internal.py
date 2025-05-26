from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from dataBase import get_db_session
from utils.response import create_response
from domain.schemas import (
    UpdateNotificationStateRequest,
    SendNotificationRequest,
)
from domain.services.notification_service import NotificationService, NotificationNotFoundError
from adapters.persistence.notification_repository import NotificationRepository
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

def get_notification_service(db: Session = Depends(get_db_session)) -> NotificationService:
    """Dependency injection for notification service"""
    repository = NotificationRepository(db)
    return NotificationService(repository)

@router.get("/notification-states", include_in_schema=False)
def get_notification_states(service: NotificationService = Depends(get_notification_service)):
    """
    Devuelve todos los estados de notificación.
    """
    try:
        states = service.get_all_notification_states()
        return [{"notification_state_id": s.notification_state_id, "name": s.name} for s in states]
    except Exception as e:
        logger.error(f"Error obteniendo estados de notificación: {str(e)}")
        return create_response("error", f"Error interno del servidor: {str(e)}", status_code=500)

@router.get("/notification-types", include_in_schema=False)
def get_notification_types(service: NotificationService = Depends(get_notification_service)):
    """
    Devuelve todos los tipos de notificación.
    """
    try:
        types = service.get_all_notification_types()
        return [{"notification_type_id": t.notification_type_id, "name": t.name} for t in types]
    except Exception as e:
        logger.error(f"Error obteniendo tipos de notificación: {str(e)}")
        return create_response("error", f"Error interno del servidor: {str(e)}", status_code=500)

@router.get("/notifications", include_in_schema=False)
def get_all_notifications(service: NotificationService = Depends(get_notification_service)):
    """
    Devuelve todas las notificaciones.
    """
    try:
        notifications = service.get_all_notifications()
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
            for n in notifications
        ]
    except Exception as e:
        logger.error(f"Error obteniendo todas las notificaciones: {str(e)}")
        return create_response("error", f"Error interno del servidor: {str(e)}", status_code=500)

@router.get("/notifications/by-invitation/{invitation_id}", include_in_schema=False)
def get_notification_by_invitation(invitation_id: int, service: NotificationService = Depends(get_notification_service)):
    """
    Devuelve el notification_id asociado a una invitación.
    """
    try:
        result = service.get_notification_by_invitation(invitation_id)
        return {"notification_id": result.notification_id}
    except Exception as e:
        logger.error(f"Error obteniendo notificación por invitation_id {invitation_id}: {str(e)}")
        return create_response("error", f"Error interno del servidor: {str(e)}", status_code=500)

@router.delete("/notifications/by-invitation/{invitation_id}", include_in_schema=False)
def delete_notifications_by_invitation(invitation_id: int, service: NotificationService = Depends(get_notification_service)):
    """
    Elimina todas las notificaciones de tipo 'Invitation' asociadas a una invitación.
    """
    try:
        result = service.delete_notifications_by_invitation(invitation_id)
        
        if result.deleted_count == 0:
            return create_response("success", "No se encontraron notificaciones para eliminar.", {"deleted_count": 0}, status_code=200)
        
        return create_response("success", f"{result.deleted_count} notificaciones eliminadas exitosamente.", {"deleted_count": result.deleted_count}, status_code=200)
        
    except Exception as e:
        logger.error(f"Error eliminando notificaciones por invitation_id {invitation_id}: {str(e)}")
        return create_response("error", f"Error interno del servidor al eliminar notificaciones: {str(e)}", status_code=500)

@router.patch("/notifications/{notification_id}/state", include_in_schema=False)
def update_notification_state(notification_id: int, request: UpdateNotificationStateRequest, service: NotificationService = Depends(get_notification_service)):
    """
    Actualiza el estado de una notificación.
    """
    try:
        service.update_notification_state(notification_id, request.notification_state_id)
        return create_response("success", "Estado de notificación actualizado")
    except NotificationNotFoundError:
        return create_response("error", "Notificación no encontrada", status_code=404)
    except Exception as e:
        logger.error(f"Error actualizando estado de notificación {notification_id}: {str(e)}")
        return create_response("error", f"Error interno del servidor: {str(e)}", status_code=500)



@router.post("/send-notification", include_in_schema=False)
def send_notification_endpoint(
    request: SendNotificationRequest,
    service: NotificationService = Depends(get_notification_service)
):
    """
    Endpoint para enviar una notificación.
    Guarda la notificación en la base de datos y envía una notificación FCM
    a todos los dispositivos del usuario recuperados del servicio de usuarios.
    """
    try:
        result = service.send_notification(request)
        
        if result.devices_notified == 0:
            return create_response(
                "success", 
                "Notificación guardada, pero el usuario no tiene dispositivos registrados", 
                {
                    "notification_id": result.notification_id, 
                    "devices_notified": 0
                }
            )
        
        response_data = {
            "notification_id": result.notification_id,
            "devices_notified": result.devices_notified
        }
        
        if result.invalid_tokens:
            response_data["invalid_tokens"] = result.invalid_tokens
        if result.fcm_errors:
            response_data["fcm_errors"] = result.fcm_errors
            
        return create_response("success", "Notificación enviada correctamente", response_data)
        
    except Exception as e:
        logger.error(f"Error enviando notificación: {str(e)}")
        return create_response("error", f"Error al enviar la notificación: {str(e)}", status_code=500) 