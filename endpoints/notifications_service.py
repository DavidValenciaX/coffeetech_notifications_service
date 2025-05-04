from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from dataBase import get_db_session
from models.models import NotificationStates, NotificationTypes, Notifications
from pydantic import BaseModel
from typing import Optional
from utils.response import create_response
from use_cases.register_device_use_case import register_device
import logging

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
    
class RegisterDeviceRequest(BaseModel):
    fcm_token: str
    user_id: Optional[int] = None

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
