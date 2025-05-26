from typing import Dict, Any
import logging
from sqlalchemy.orm import Session
from domain.services.notification_service import NotificationService
from adapters.persistence.notification_repository import NotificationRepository
from utils.response import create_response, session_token_invalid_response

logger = logging.getLogger(__name__)


class GetNotificationsUseCase:
    """Use case for getting user notifications"""
    
    def __init__(self, db: Session):
        self.notification_repository = NotificationRepository(db)
        self.notification_service = NotificationService(self.notification_repository)
    
    def execute(self, session_token: str) -> Dict[str, Any]:
        """Execute the get notifications use case"""
        # Authenticate user
        user = self.notification_service.authenticate_user(session_token)
        if not user:
            return session_token_invalid_response()
        
        try:
            # Get user notifications
            notification_responses = self.notification_service.get_user_notifications(user['user_id'])
            
            if not notification_responses:
                return create_response("success", "No hay notificaciones para este usuario.", data=[])
            
            # Convert to dict format for response
            notification_responses_dict = [n.model_dump() for n in notification_responses]
            return create_response("success", "Notificaciones obtenidas exitosamente.", data=notification_responses_dict)
            
        except Exception as e:
            return create_response("error", str(e), data=[])