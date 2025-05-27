import os
import logging
import firebase_admin
from firebase_admin import credentials, messaging, exceptions
from firebase_admin._messaging_utils import SenderIdMismatchError

logger = logging.getLogger(__name__)

SERVICE_ACCOUNT = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),  # directorio raíz del proyecto
    'serviceAccountKey.json'
)

def _initialize_firebase():
    """
    Initialize Firebase Admin SDK if not already initialized and credentials are available.
    
    This function handles the case where the service account key file doesn't exist
    (e.g., in CI/CD environments or testing) by gracefully logging a warning instead
    of raising an exception. This allows tests to run without requiring actual
    Firebase credentials.
    """
    if not firebase_admin._apps:
        if os.path.exists(SERVICE_ACCOUNT):
            cred = credentials.Certificate(SERVICE_ACCOUNT)
            firebase_admin.initialize_app(cred)
        else:
            logger.warning("Firebase service account key not found at %s. Firebase functionality will be limited.", SERVICE_ACCOUNT)

# Initialize Firebase on module import if credentials are available
_initialize_firebase()

def send_fcm_notification(fcm_token: str, title: str, body: str):
    """
    Envía una notificación utilizando Firebase Cloud Messaging (FCM).

    Args:
        fcm_token (str): El token de registro FCM del dispositivo al que se enviará la notificación.
        title (str): El título de la notificación.
        body (str): El cuerpo del mensaje de la notificación.

    Raises:
        SenderIdMismatchError: Si el token FCM pertenece a un proyecto diferente.
        InvalidArgumentError: Si el token tiene formato incorrecto.
        UnauthenticatedError: Si las credenciales no son válidas.
        Exception: Otros errores al enviar la notificación.
        
    Returns:
        dict: Información sobre el resultado del envío, incluyendo si fue exitoso y cualquier error.
    """
    result = {
        "success": False,
        "token": fcm_token,
        "error_type": None,
        "error_message": None
    }
    
    # Check if Firebase is initialized
    if not firebase_admin._apps:
        logger.error("Firebase Admin SDK not initialized. Cannot send notification.")
        result["error_type"] = "firebase_not_initialized"
        result["error_message"] = "Firebase Admin SDK not initialized. Service account key may be missing."
        return result
    
    # Construir el mensaje
    message = messaging.Message(
        notification=messaging.Notification(title=title, body=body),
        token=fcm_token,
    )
    
    try:
        response = messaging.send(message)
        logger.info("Notificación enviada. ID de mensaje: %s", response)
        result["success"] = True
        result["message_id"] = response
        return result
    except SenderIdMismatchError as e:
        logger.error("Token FCM pertenece a un proyecto diferente: %s", e)
        result["error_type"] = "sender_id_mismatch"
        result["error_message"] = str(e)
        # Este token debe ser eliminado ya que pertenece a otro proyecto
        result["should_delete_token"] = True
        raise SenderIdMismatchError(f"Token FCM pertenece a un proyecto diferente: {e}")
    except exceptions.InvalidArgumentError as e:
        logger.error("Token inválido o formato incorrecto: %s", e)
        result["error_type"] = "invalid_token"
        result["error_message"] = str(e)
        # Este token también debería ser eliminado ya que es inválido
        result["should_delete_token"] = True
        return result
    except exceptions.UnauthenticatedError as e:
        logger.error("Credenciales no válidas / API FCM deshabilitada: %s", e)
        result["error_type"] = "authentication_error"
        result["error_message"] = str(e)
        return result
    except Exception as e:
        logger.exception("Error inesperado enviando notificación: %s", e)
        result["error_type"] = "unknown_error"
        result["error_message"] = str(e)
        return result
