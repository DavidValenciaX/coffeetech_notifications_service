from typing import List
from sqlalchemy.orm import Session
from models.models import Notifications
from domain.repositories.notification_repository import NotificationRepositoryInterface


class NotificationRepository(NotificationRepositoryInterface):
    """Repository for handling notification data persistence"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_notifications_by_user_id(self, user_id: int) -> List[Notifications]:
        """Get all notifications for a specific user"""
        return self.db.query(Notifications).filter(Notifications.user_id == user_id).all() 