from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from dataBase import get_db_session
from models.models import NotificationStates, NotificationTypes, Notifications, UserDevices
from pydantic import BaseModel
from typing import Optional
from utils.response import create_response
from use_cases.register_device_use_case import register_device
import logging
from datetime import datetime
import pytz
from use_cases.send_fcm_notification_use_case import send_fcm_notification

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
            "entity_type": n.entity_type,
            "entity_id": n.entity_id,
            "notification_type_id": n.notification_type_id,
            "notification_state_id": n.notification_state_id
        }
        for n in notifs
    ]
    
@router.get("/user-devices/{user_id}", include_in_schema=False)
def get_user_devices(user_id: int, db: Session = Depends(get_db_session)):
    """
    Devuelve todos los dispositivos (fcm_token) asociados a un usuario.
    """
    devices = db.query(UserDevices).filter(UserDevices.user_id == user_id).all()
    return [
        {
            "user_device_id": d.user_device_id,
            "user_id": d.user_id,
            "fcm_token": d.fcm_token
        }
        for d in devices
    ]

@router.get("/notifications/by-invitation/{invitation_id}", include_in_schema=False)
def get_notification_by_invitation(invitation_id: int, db: Session = Depends(get_db_session)):
    """
    Devuelve el notification_id asociado a una invitación (entity_type='invitation', entity_id=invitation_id).
    """
    notif = db.query(Notifications).filter(
        Notifications.entity_type == "invitation",
        Notifications.entity_id == invitation_id
    ).first()
    if notif:
        return {"notification_id": notif.notification_id}
    else:
        return {"notification_id": None}

class RegisterDeviceRequest(BaseModel):
    fcm_token: str
    user_id: Optional[int] = None

class UpdateNotificationStateRequest(BaseModel):
    notification_state_id: int

class SendNotificationRequest(BaseModel):
    message: str
    user_id: int
    notification_type_id: int
    entity_type: str
    entity_id: int
    notification_state_id: int
    fcm_token: Optional[str] = None
    fcm_title: Optional[str] = None
    fcm_body: Optional[str] = None

@router.post("/register-device", include_in_schema=False)
def register_device_endpoint(request: RegisterDeviceRequest, db: Session = Depends(get_db_session)):
    """
    Registra un dispositivo por FCM token (o lo retorna si ya existe).
    """
    device = register_device(db, request.fcm_token, request.user_id)
    if device:
        return create_response("success", "Dispositivo registrado/obtenido", {
            "user_device_id": device.user_device_id,
            "user_id": device.user_id,
            "fcm_token": device.fcm_token
        })
    else:
        return create_response("error", "No se pudo registrar/obtener el dispositivo")

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
    """
    try:
        bogota_tz = pytz.timezone("America/Bogota")
        new_notification = Notifications(
            message=request.message,
            notification_date=datetime.now(bogota_tz),
            entity_type=request.entity_type,
            entity_id=request.entity_id,
            notification_type_id=request.notification_type_id,
            notification_state_id=request.notification_state_id
        )
        db.add(new_notification)
        db.commit()

        if request.fcm_token and request.fcm_title and request.fcm_body:
            send_fcm_notification(request.fcm_token, request.fcm_title, request.fcm_body)

        return create_response("success", "Notificación enviada correctamente", {
            "notification_id": new_notification.notification_id
        })
    except Exception as e:
        db.rollback()
        logger.error(f"Error enviando notificación: {str(e)}")
        return create_response("error", f"Error al enviar la notificación: {str(e)}", status_code=500)
