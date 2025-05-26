from typing import List, Dict, Any
import logging
from domain.repositories.notification_repository import NotificationRepositoryInterface
from domain.schemas import NotificationResponse
from adapters.http.user_service_adapter import verify_session_token

logger = logging.getLogger(__name__)


class SerializationError(Exception):
    """Custom exception for serialization errors."""
    pass


class NotificationService:
    """Service for handling notification business logic"""
    
    def __init__(self, notification_repository: NotificationRepositoryInterface):
        self.notification_repository = notification_repository
    
    def authenticate_user(self, session_token: str) -> Dict[str, Any] | None:
        """Authenticate user using session token"""
        user = verify_session_token(session_token)
        if user:
            logger.info(f"Usuario autenticado: {user['user_id']} - {user['name']}")
        else:
            logger.warning(f"Sesión inválida para el token: {session_token}")
        return user
    
    def get_user_notifications(self, user_id: int) -> List[NotificationResponse]:
        """Get and serialize notifications for a user"""
        notifications = self.notification_repository.get_notifications_by_user_id(user_id)
        logger.info(f"Notificaciones obtenidas: {len(notifications)}")
        
        if not notifications:
            logger.info("No hay notificaciones para este usuario.")
            return []
        
        try:
            notification_responses = [
                NotificationResponse(
                    notification_id=notification.notification_id,
                    message=notification.message,
                    notification_date=notification.notification_date,
                    invitation_id=notification.invitation_id,
                    notification_type=notification.notification_type.name if notification.notification_type else None,
                    notification_state=notification.state.name if notification.state else None
                )
                for notification in notifications
            ]
            logger.info(f"Notificaciones serializadas correctamente: {len(notification_responses)}")
            return notification_responses
        except Exception as e:
            logger.error(f"Error de serialización: {e}")
            raise SerializationError(f"Error de serialización: {str(e)}") 