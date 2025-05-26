from abc import ABC, abstractmethod
from typing import List
from models.models import Notifications


class NotificationRepositoryInterface(ABC):
    """Interface for notification repository operations"""
    
    @abstractmethod
    def get_notifications_by_user_id(self, user_id: int) -> List[Notifications]:
        """Get all notifications for a specific user"""
        pass 