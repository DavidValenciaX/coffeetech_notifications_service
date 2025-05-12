from typing import Optional, Any, Dict, Union, List
from pydantic import BaseModel
from dotenv import load_dotenv
import logging
import httpx
import os

load_dotenv(override=True, encoding="utf-8")

logger = logging.getLogger(__name__)

USER_SERVICE_URL = os.getenv("USER_SERVICE_URL", "http://localhost:8000")

class UserResponse(BaseModel):
    user_id: int
    name: str
    email: str

def verify_session_token(session_token: str) -> Optional[Union[Dict[str, Any], UserResponse]]:
    """
    Verifica el token de sesión haciendo una solicitud al servicio de usuarios.
    Retorna un diccionario con los datos del usuario si es válido, o None si no lo es.
    """
    try:
        with httpx.Client(timeout=5.0) as client:
            response = client.post(f"{USER_SERVICE_URL}/users-service/session-token-verification", json={"session_token": session_token})
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "success" and "user" in data.get("data", {}):
                    return data["data"]["user"]
            logger.warning(f"Token inválido o error en la verificación: {response.text}")
    except Exception as e:
        logger.error(f"Error al verificar el token de sesión: {e}")
    return None

def get_user_devices_by_user_id(user_id: int) -> List[Dict[str, Any]]:
    """
    Obtiene la lista de dispositivos del usuario desde el servicio de usuarios.
    
    Args:
        user_id (int): ID del usuario
        
    Returns:
        List[Dict[str, Any]]: Lista de dispositivos con user_device_id, user_id y fcm_token
    """
    try:
        with httpx.Client(timeout=5.0) as client:
            response = client.get(f"{USER_SERVICE_URL}/users-service/users/{user_id}/devices")
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "success" and "data" in data:
                    return data["data"]
                else:
                    logger.warning(f"Respuesta inesperada al obtener dispositivos: {response.text}")
            else:
                logger.warning(f"Error al obtener dispositivos del usuario {user_id}: {response.status_code} - {response.text}")
    except Exception as e:
        logger.error(f"Error al conectarse al servicio de usuarios para obtener dispositivos: {e}")
    
    return []