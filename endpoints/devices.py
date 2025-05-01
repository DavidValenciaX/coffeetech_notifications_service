from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from dataBase import get_db_session
from utils.response import create_response
from use_cases.register_device_use_case import register_device

router = APIRouter()

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
