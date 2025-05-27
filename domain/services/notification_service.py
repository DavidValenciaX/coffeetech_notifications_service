from typing import List, Dict, Any, Optional
import logging
from datetime import datetime
import pytz
from domain.repositories.notification_repository import NotificationRepositoryInterface
from domain.entities import Notification, NotificationMapper
from domain.schemas import (
    NotificationResponse, 
    NotificationStateResponse, 
    NotificationTypeResponse,
    NotificationDetailResponse,
    NotificationByInvitationResponse,
    DeleteNotificationsResponse,
    SendNotificationRequest,
    SendNotificationResponse
)
from adapters.http.user_service_adapter import verify_session_token, get_user_devices_by_user_id
from utils.send_fcm_notification import send_fcm_notification
from firebase_admin._messaging_utils import SenderIdMismatchError

logger = logging.getLogger(__name__)


class SerializationError(Exception):
    """Custom exception for serialization errors."""
    pass


class NotificationNotFoundError(Exception):
    """Custom exception for notification not found errors."""
    pass


class NotificationService:
    """Enhanced notification service that uses domain entities while maintaining all existing functionality"""
    
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
        """Get and serialize notifications for a user using entities"""
        notification_models = self.notification_repository.get_notifications_by_user_id(user_id)
        logger.info(f"Notificaciones obtenidas: {len(notification_models)}")
        
        if not notification_models:
            logger.info("No hay notificaciones para este usuario.")
            return []
        
        try:
            # Convert models to entities
            notification_entities = [
                NotificationMapper.to_entity(model) 
                for model in notification_models
            ]
            
            # Convert entities to response DTOs
            notification_responses = [
                NotificationResponse(
                    notification_id=entity.notification_id,
                    message=entity.message,
                    notification_date=entity.notification_date,
                    invitation_id=entity.invitation_id,
                    notification_type=entity.notification_type_name,
                    notification_state=entity.notification_state_name
                )
                for entity in notification_entities
            ]
            
            logger.info(f"Notificaciones serializadas correctamente: {len(notification_responses)}")
            return notification_responses
        except Exception as e:
            logger.error(f"Error de serialización: {e}")
            raise SerializationError(f"Error de serialización: {str(e)}")
    
    def get_all_notification_states(self) -> List[NotificationStateResponse]:
        """Get all notification states"""
        states = self.notification_repository.get_all_notification_states()
        return [
            NotificationStateResponse(
                notification_state_id=state.notification_state_id,
                name=state.name
            )
            for state in states
        ]
    
    def get_all_notification_types(self) -> List[NotificationTypeResponse]:
        """Get all notification types"""
        types = self.notification_repository.get_all_notification_types()
        return [
            NotificationTypeResponse(
                notification_type_id=type_.notification_type_id,
                name=type_.name
            )
            for type_ in types
        ]
    
    def get_all_notifications(self) -> List[NotificationDetailResponse]:
        """Get all notifications using entities"""
        notification_models = self.notification_repository.get_all_notifications()
        
        # Convert to entities and then to response DTOs
        notification_entities = [
            NotificationMapper.to_entity(model) 
            for model in notification_models
        ]
        
        return [
            NotificationDetailResponse(
                notification_id=entity.notification_id,
                message=entity.message,
                notification_date=entity.notification_date,
                invitation_id=entity.invitation_id,
                notification_type_id=entity.notification_type_id,
                notification_state_id=entity.notification_state_id,
                user_id=entity.user_id
            )
            for entity in notification_entities
        ]
    
    def get_notification_by_invitation(self, invitation_id: int) -> NotificationByInvitationResponse:
        """Get notification by invitation ID"""
        notification_model = self.notification_repository.get_notification_by_invitation(invitation_id)
        return NotificationByInvitationResponse(
            notification_id=notification_model.notification_id if notification_model else None
        )
    
    def delete_notifications_by_invitation(self, invitation_id: int) -> DeleteNotificationsResponse:
        """Delete notifications by invitation ID"""
        try:
            deleted_count = self.notification_repository.delete_notifications_by_invitation(invitation_id)
            logger.info(f"{deleted_count} notificaciones de tipo 'Invitation' eliminadas para invitation_id {invitation_id}.")
            return DeleteNotificationsResponse(deleted_count=deleted_count)
        except Exception as e:
            logger.error(f"Error eliminando notificaciones por invitation_id {invitation_id}: {str(e)}")
            raise
    
    def update_notification_state(self, notification_id: int, notification_state_id: int) -> None:
        """Update notification state using entity validation"""
        # Get current notification
        current_model = self.notification_repository.get_notification_by_id(notification_id)
        if not current_model:
            raise NotificationNotFoundError("Notificación no encontrada")
        
        # Convert to entity and validate state change
        notification_entity = NotificationMapper.to_entity(current_model)
        
        try:
            # Use entity validation for state update
            notification_entity.update_state(notification_state_id)
        except ValueError as e:
            logger.error(f"Invalid state update: {e}")
            raise ValueError(f"Estado inválido: {str(e)}")
        
        # Update in repository
        updated_model = self.notification_repository.update_notification_state(notification_id, notification_state_id)
        if not updated_model:
            raise NotificationNotFoundError("Error actualizando notificación")
            
        logger.info(f"Estado de notificación {notification_id} actualizado a {notification_state_id}")
    
    def _send_fcm_to_token(self, token: str, title: str, body: str, fcm_errors: list, invalid_tokens: list) -> bool:
        """Send FCM to a specific token and handle errors. Returns True if successful."""
        try:
            response = send_fcm_notification(token, title, body)
            if isinstance(response, dict) and response.get("success"):
                return True
            elif isinstance(response, dict) and response.get("should_delete_token"):
                invalid_tokens.append(token)
                fcm_errors.append({
                    "token": token,
                    "error_type": response.get("error_type"),
                    "error_message": response.get("error_message")
                })
        except SenderIdMismatchError:
            invalid_tokens.append(token)
            fcm_errors.append({
                "token": token,
                "error_type": "sender_id_mismatch",
                "error_message": "Token pertenece a un proyecto FCM diferente"
            })
        except Exception as e:
            fcm_errors.append({
                "token": token,
                "error_type": "unknown",
                "error_message": str(e)
            })
            logger.error(f"Error enviando FCM: {str(e)}")
        return False
    
    def _send_fcm_to_devices(self, request: SendNotificationRequest, user_devices: list, fcm_errors: list, invalid_tokens: list) -> int:
        """Send FCM to all user devices. Returns the number of successful sends."""
        sent_count = 0
        if not (request.fcm_title and request.fcm_body):
            return sent_count
            
        for device in user_devices:
            if self._send_fcm_to_token(device["fcm_token"], request.fcm_title, request.fcm_body, fcm_errors, invalid_tokens):
                sent_count += 1
        return sent_count
    
    def send_notification(self, request: SendNotificationRequest) -> SendNotificationResponse:
        """Send a notification using entity-based approach with FCM support"""
        try:
            # Step 1: Create notification entity with validation
            notification_entity = Notification.create_new(
                message=request.message,
                user_id=request.user_id,
                notification_type_id=request.notification_type_id,
                invitation_id=request.invitation_id,
                notification_state_id=request.notification_state_id
            )
            
            # Step 2: Apply business rules
            if notification_entity.is_invitation_notification():
                logger.info("Processing invitation notification")
            
            # Step 3: Save notification to database
            saved_model = self.notification_repository.create_notification(
                message=notification_entity.message,
                user_id=notification_entity.user_id,
                notification_type_id=notification_entity.notification_type_id,
                invitation_id=notification_entity.invitation_id,
                notification_state_id=notification_entity.notification_state_id
            )
            
            # Convert back to entity with ID
            saved_entity = NotificationMapper.to_entity(saved_model)
            
            # Step 4: Handle FCM notifications
            user_devices = get_user_devices_by_user_id(request.user_id)
            
            if not user_devices:
                logger.info(f"Usuario {request.user_id} no tiene dispositivos registrados para notificaciones FCM")
                return SendNotificationResponse(
                    notification_id=saved_entity.notification_id,
                    devices_notified=0
                )
            
            fcm_errors = []
            invalid_tokens = []
            
            # Send to all user devices
            sent_count = self._send_fcm_to_devices(request, user_devices, fcm_errors, invalid_tokens)
            
            # If a specific additional token was provided
            if request.fcm_token and request.fcm_title and request.fcm_body:
                if self._send_fcm_to_token(request.fcm_token, request.fcm_title, request.fcm_body, fcm_errors, invalid_tokens):
                    sent_count += 1
            
            # Step 5: FCM notification sent successfully
            # Note: We do NOT change the notification state here
            # Notifications remain in their original state until user responds
            if sent_count > 0:
                logger.info(f"FCM notification sent successfully to {sent_count} devices for notification {saved_entity.notification_id}")
            else:
                logger.info(f"No FCM notifications sent for notification {saved_entity.notification_id}")

            # Log invalid tokens
            if invalid_tokens:
                logger.warning(f"Tokens FCM inválidos detectados: {invalid_tokens}")

            return SendNotificationResponse(
                notification_id=saved_entity.notification_id,
                devices_notified=sent_count,
                invalid_tokens=invalid_tokens if invalid_tokens else None,
                fcm_errors=fcm_errors if fcm_errors else None
            )
            
        except ValueError as e:
            # Handle entity validation errors
            logger.error(f"Error de validación de entidad: {e}")
            raise ValueError(f"Datos de notificación inválidos: {str(e)}")
        except Exception as e:
            logger.error(f"Error enviando notificación: {str(e)}")
            raise
    
    # Additional entity-based methods
    
    def get_notification_entity_by_id(self, notification_id: int) -> Optional[Notification]:
        """Get a notification as a domain entity"""
        model = self.notification_repository.get_notification_by_id(notification_id)
        if model:
            return NotificationMapper.to_entity(model)
        return None
    
    def get_user_notifications_as_entities(self, user_id: int) -> List[Notification]:
        """Get user notifications as domain entities"""
        models = self.notification_repository.get_notifications_by_user_id(user_id)
        return [NotificationMapper.to_entity(model) for model in models]
    
    def process_notification_workflow(self, notification_entity: Notification) -> Notification:
        """Process a complete notification workflow using entity business logic"""
        try:
            # Apply business rules based on entity state
            if notification_entity.is_pending():
                logger.info(f"Processing pending notification {notification_entity.notification_id}")
                
                # Apply specific business logic based on type
                if notification_entity.is_invitation_notification():
                    logger.info("Applying invitation-specific business rules")
                    # Add invitation-specific logic here
                
                # Apply business logic but don't automatically change state
                # State changes should be explicit based on user actions
                logger.info("Invitation notification processed, state remains pending until user responds")
                
                logger.info(f"Notification {notification_entity.notification_id} workflow completed")
            
            return notification_entity
            
        except Exception as e:
            logger.error(f"Error in notification workflow: {e}")
            raise 