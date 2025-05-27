from typing import List, Optional
from sqlalchemy.orm import Session, joinedload
from datetime import datetime
import pytz
from models.models import Notifications, NotificationStates, NotificationTypes
from domain.repositories.notification_repository import NotificationRepositoryInterface


class NotificationRepository(NotificationRepositoryInterface):
    """Repository for handling notification data persistence"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_notifications_by_user_id(self, user_id: int) -> List[Notifications]:
        """Get all notifications for a specific user"""
        return (self.db.query(Notifications)
                .options(joinedload(Notifications.notification_type), joinedload(Notifications.state))
                .filter(Notifications.user_id == user_id)
                .all())
    
    def get_all_notification_states(self) -> List[NotificationStates]:
        """Get all notification states"""
        return self.db.query(NotificationStates).all()
    
    def get_all_notification_types(self) -> List[NotificationTypes]:
        """Get all notification types"""
        return self.db.query(NotificationTypes).all()
    
    def get_all_notifications(self) -> List[Notifications]:
        """Get all notifications"""
        return (self.db.query(Notifications)
                .options(joinedload(Notifications.notification_type), joinedload(Notifications.state))
                .all())
    
    def get_notification_by_invitation(self, invitation_id: int) -> Optional[Notifications]:
        """Get notification by invitation ID"""
        notification_type = self.db.query(NotificationTypes).filter(
            NotificationTypes.name == "Invitation"
        ).first()
        
        if not notification_type:
            return None
            
        return self.db.query(Notifications).filter(
            Notifications.notification_type_id == notification_type.notification_type_id,
            Notifications.invitation_id == invitation_id
        ).first()
    
    def delete_notifications_by_invitation(self, invitation_id: int) -> int:
        """Delete notifications by invitation ID and return count of deleted notifications"""
        invitation_notification_type = self.db.query(NotificationTypes).filter(
            NotificationTypes.name == "Invitation" 
        ).first()

        if not invitation_notification_type:
            return 0

        notifications_to_delete = self.db.query(Notifications).filter(
            Notifications.invitation_id == invitation_id,
            Notifications.notification_type_id == invitation_notification_type.notification_type_id
        ).all()

        if not notifications_to_delete:
            return 0

        deleted_count = 0
        for notif in notifications_to_delete:
            self.db.delete(notif)
            deleted_count += 1
        
        self.db.commit()
        return deleted_count
    
    def update_notification_state(self, notification_id: int, notification_state_id: int) -> Optional[Notifications]:
        """Update notification state and return the updated notification"""
        notification = self.db.query(Notifications).filter(
            Notifications.notification_id == notification_id
        ).first()
        
        if not notification:
            return None
            
        notification.notification_state_id = notification_state_id
        self.db.commit()
        return notification
    
    def create_notification(self, message: str, user_id: int, notification_type_id: int, 
                          invitation_id: int, notification_state_id: int) -> Notifications:
        """Create a new notification"""
        bogota_tz = pytz.timezone("America/Bogota")
        new_notification = Notifications(
            message=message,
            notification_date=datetime.now(bogota_tz),
            invitation_id=invitation_id,
            notification_type_id=notification_type_id,
            notification_state_id=notification_state_id,
            user_id=user_id
        )
        self.db.add(new_notification)
        self.db.commit()
        
        # Refresh to get the relationships loaded
        self.db.refresh(new_notification)
        return (self.db.query(Notifications)
                .options(joinedload(Notifications.notification_type), joinedload(Notifications.state))
                .filter(Notifications.notification_id == new_notification.notification_id)
                .first())
    
    def get_notification_by_id(self, notification_id: int) -> Optional[Notifications]:
        """Get notification by ID"""
        return (self.db.query(Notifications)
                .options(joinedload(Notifications.notification_type), joinedload(Notifications.state))
                .filter(Notifications.notification_id == notification_id)
                .first()) 