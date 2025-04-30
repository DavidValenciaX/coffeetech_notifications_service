import logging
import httpx
from typing import Optional
import os
from dotenv import load_dotenv

load_dotenv(override=True, encoding="utf-8")

logger = logging.getLogger(__name__)

USER_SERVICE_URL = os.getenv("USER_SERVICE_URL", "http://localhost:8000")

def verify_session_token(session_token: str) -> Optional[dict]:
    """
    Verifica el token de sesión haciendo una solicitud al servicio de usuarios.
    Retorna un diccionario con los datos del usuario si es válido, o None si no lo es.
    """
    try:
        with httpx.Client(timeout=5.0) as client:
            response = client.post(f"{USER_SERVICE_URL}/session-token-verification", json={"session_token": session_token})
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "success" and "user" in data.get("data", {}):
                    return data["data"]["user"]
            logger.warning(f"Token inválido o error en la verificación: {response.text}")
    except Exception as e:
        logger.error(f"Error al verificar el token de sesión: {e}")
    return None