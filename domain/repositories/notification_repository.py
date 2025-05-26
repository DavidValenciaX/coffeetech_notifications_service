from abc import ABC, abstractmethod
from typing import List, Optional
from models.models import Notifications, NotificationStates, NotificationTypes


class NotificationRepositoryInterface(ABC):
    """Interface for notification repository operations"""
    
    @abstractmethod
    def get_notifications_by_user_id(self, user_id: int) -> List[Notifications]:
        """Get all notifications for a specific user"""
        pass
    
    @abstractmethod
    def get_all_notification_states(self) -> List[NotificationStates]:
        """Get all notification states"""
        pass
    
    @abstractmethod
    def get_all_notification_types(self) -> List[NotificationTypes]:
        """Get all notification types"""
        pass
    
    @abstractmethod
    def get_all_notifications(self) -> List[Notifications]:
        """Get all notifications"""
        pass
    
    @abstractmethod
    def get_notification_by_invitation(self, invitation_id: int) -> Optional[Notifications]:
        """Get notification by invitation ID"""
        pass
    
    @abstractmethod
    def delete_notifications_by_invitation(self, invitation_id: int) -> int:
        """Delete notifications by invitation ID and return count of deleted notifications"""
        pass
    
    @abstractmethod
    def update_notification_state(self, notification_id: int, notification_state_id: int) -> Optional[Notifications]:
        """Update notification state and return the updated notification"""
        pass
    
    @abstractmethod
    def create_notification(self, message: str, user_id: int, notification_type_id: int, 
                          invitation_id: int, notification_state_id: int) -> Notifications:
        """Create a new notification"""
        pass
    
    @abstractmethod
    def get_notification_by_id(self, notification_id: int) -> Optional[Notifications]:
        """Get notification by ID"""
        pass 