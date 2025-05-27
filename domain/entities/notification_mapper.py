from typing import Optional
from models.models import Notifications as NotificationModel
from .notification import Notification


class NotificationMapper:
    """
    Mapper class to convert between domain entities and database models
    """
    
    @staticmethod
    def to_entity(model: NotificationModel) -> Notification:
        """
        Convert SQLAlchemy model to domain entity
        
        Args:
            model: SQLAlchemy Notifications model instance
            
        Returns:
            Notification domain entity
        """
        notification_type_name = None
        notification_state_name = None
        
        # Extract relationship data if available
        if hasattr(model, 'notification_type') and model.notification_type:
            notification_type_name = model.notification_type.name
            
        if hasattr(model, 'state') and model.state:
            notification_state_name = model.state.name
        
        return Notification(
            notification_id=model.notification_id,
            message=model.message,
            notification_date=model.notification_date,
            invitation_id=model.invitation_id,
            notification_type_id=model.notification_type_id,
            notification_state_id=model.notification_state_id,
            user_id=model.user_id,
            notification_type_name=notification_type_name,
            notification_state_name=notification_state_name
        )
    
    @staticmethod
    def to_model(entity: Notification) -> NotificationModel:
        """
        Convert domain entity to SQLAlchemy model
        
        Args:
            entity: Notification domain entity
            
        Returns:
            SQLAlchemy Notifications model instance
        """
        model = NotificationModel(
            message=entity.message,
            notification_date=entity.notification_date,
            invitation_id=entity.invitation_id,
            notification_type_id=entity.notification_type_id,
            notification_state_id=entity.notification_state_id,
            user_id=entity.user_id
        )
        
        # Set ID if it exists (for updates)
        if entity.notification_id is not None:
            model.notification_id = entity.notification_id
            
        return model
    
    @staticmethod
    def update_model_from_entity(model: NotificationModel, entity: Notification) -> NotificationModel:
        """
        Update an existing SQLAlchemy model with data from domain entity
        
        Args:
            model: Existing SQLAlchemy model instance
            entity: Notification domain entity with updated data
            
        Returns:
            Updated SQLAlchemy model instance
        """
        model.message = entity.message
        model.notification_date = entity.notification_date
        model.invitation_id = entity.invitation_id
        model.notification_type_id = entity.notification_type_id
        model.notification_state_id = entity.notification_state_id
        model.user_id = entity.user_id
        
        return model 