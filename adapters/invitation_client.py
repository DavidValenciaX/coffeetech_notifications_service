from dotenv import load_dotenv
import os
import logging
import httpx

load_dotenv(override=True, encoding="utf-8")

logger = logging.getLogger(__name__)

INVITATIONS_SERVICE_URL = os.getenv("INVITATIONS_SERVICE_URL", "http://localhost:8003")

def get_invitation_details(invitation_id):
    """
    Obtiene los detalles de una invitación del servicio de invitaciones.
    """
    try:
        with httpx.Client() as client:
            resp = client.get(f"{INVITATIONS_SERVICE_URL}/invitations-service/{invitation_id}")
            resp.raise_for_status()
            return resp.json()
    except httpx.RequestError as exc:
        logger.error(f"Request error while getting invitation details for invitation_id={invitation_id}: {exc}")
        return None
    except httpx.HTTPStatusError as exc:
        logger.error(f"HTTP error while getting invitation details for invitation_id={invitation_id}: {exc.response.status_code} - {exc.response.text}")
        return None 