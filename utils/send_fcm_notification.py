import os
import logging
import firebase_admin
from firebase_admin import credentials, messaging, exceptions

logger = logging.getLogger(__name__)

SERVICE_ACCOUNT = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),  # directorio raíz del proyecto
    'serviceAccountKey.json'
)

if not firebase_admin._apps:
    cred = credentials.Certificate(SERVICE_ACCOUNT)
    firebase_admin.initialize_app(cred)

def send_fcm_notification(fcm_token: str, title: str, body: str):
    """
    Envía una notificación utilizando Firebase Cloud Messaging (FCM).

    Args:
        fcm_token (str): El token de registro FCM del dispositivo al que se enviará la notificación.
        title (str): El título de la notificación.
        body (str): El cuerpo del mensaje de la notificación.

    Raises:
        Exception: Si hay un error al enviar la notificación.
    """
    # Construir el mensaje
    message = messaging.Message(
        notification=messaging.Notification(title=title, body=body),
        token=fcm_token,
    )
    try:
        response = messaging.send(message)
        logger.info("Notificación enviada. ID de mensaje: %s", response)
        return response
    except exceptions.InvalidArgumentError as e:
        logger.error("Token inválido o formato incorrecto: %s", e)
    except exceptions.UnauthenticatedError as e:
        logger.error("Credenciales no válidas / API FCM deshabilitada: %s", e)
    except Exception as e:
        logger.exception("Error inesperado enviando notificación: %s", e)
