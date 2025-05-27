from dataclasses import dataclass
from datetime import datetime
from typing import Optional
import pytz


@dataclass
class Notification:
    """
    Notification entity representing a notification in the domain layer.
    This entity encapsulates the business logic and rules for notifications.
    """
    
    # Core attributes
    notification_id: Optional[int]
    message: Optional[str]
    notification_date: datetime
    invitation_id: int
    notification_type_id: int
    notification_state_id: int
    user_id: int
    
    # Optional attributes for relationships
    notification_type_name: Optional[str] = None
    notification_state_name: Optional[str] = None
    
    def __post_init__(self):
        """Validate the notification after initialization"""
        self._validate()
    
    def _validate(self):
        """Validate notification business rules"""
        if self.user_id <= 0:
            raise ValueError("User ID must be a positive integer")
        
        if self.invitation_id <= 0:
            raise ValueError("Invitation ID must be a positive integer")
        
        if self.notification_type_id <= 0:
            raise ValueError("Notification type ID must be a positive integer")
        
        if self.notification_state_id <= 0:
            raise ValueError("Notification state ID must be a positive integer")
        
        if self.message is not None and len(self.message.strip()) == 0:
            raise ValueError("Message cannot be empty if provided")
    
    @classmethod
    def create_new(
        cls,
        message: Optional[str],
        user_id: int,
        notification_type_id: int,
        invitation_id: int,
        notification_state_id: int,
        timezone: str = "America/Bogota"
    ) -> "Notification":
        """
        Factory method to create a new notification with current timestamp
        
        Args:
            message: The notification message
            user_id: ID of the user receiving the notification
            notification_type_id: ID of the notification type
            invitation_id: ID of the related invitation
            notification_state_id: ID of the notification state
            timezone: Timezone for the notification date (default: America/Bogota)
        
        Returns:
            A new Notification instance
        """
        tz = pytz.timezone(timezone)
        current_time = datetime.now(tz)
        
        return cls(
            notification_id=None,  # Will be set by the database
            message=message,
            notification_date=current_time,
            invitation_id=invitation_id,
            notification_type_id=notification_type_id,
            notification_state_id=notification_state_id,
            user_id=user_id
        )
    
    def update_state(self, new_state_id: int) -> None:
        """
        Update the notification state
        
        Args:
            new_state_id: The new state ID
        """
        if new_state_id <= 0:
            raise ValueError("State ID must be a positive integer")
        
        self.notification_state_id = new_state_id
    
    def is_pending(self) -> bool:
        """
        Check if the notification is in pending state
        State ID 1 = 'Pendiente'
        """
        return self.notification_state_id == 1
    
    def is_responded(self) -> bool:
        """
        Check if the notification has been responded to
        State ID 2 = 'Respondida'
        """
        return self.notification_state_id == 2
    
    def is_scheduled(self) -> bool:
        """
        Check if the notification is scheduled
        State ID 3 = 'Programada'
        """
        return self.notification_state_id == 3
    
    def is_inactive(self) -> bool:
        """
        Check if the notification is inactive
        State ID 4 = 'Inactiva'
        """
        return self.notification_state_id == 4
    
    def is_accepted(self) -> bool:
        """
        Check if the notification has been accepted
        State ID 5 = 'Aceptada'
        """
        return self.notification_state_id == 5
    
    def is_rejected(self) -> bool:
        """
        Check if the notification has been rejected
        State ID 6 = 'Rechazada'
        """
        return self.notification_state_id == 6
    
    def mark_as_responded(self) -> None:
        """Mark the notification as responded"""
        self.update_state(2)  # 2 = 'Respondida'
    
    def mark_as_scheduled(self) -> None:
        """Mark the notification as scheduled"""
        self.update_state(3)  # 3 = 'Programada'
    
    def mark_as_inactive(self) -> None:
        """Mark the notification as inactive"""
        self.update_state(4)  # 4 = 'Inactiva'
    
    def mark_as_accepted(self) -> None:
        """Mark the notification as accepted"""
        self.update_state(5)  # 5 = 'Aceptada'
    
    def mark_as_rejected(self) -> None:
        """Mark the notification as rejected"""
        self.update_state(6)  # 6 = 'Rechazada'
    
    def is_invitation_notification(self) -> bool:
        """
        Check if this is an invitation notification
        This method assumes you have a specific type ID for invitations
        """
        # You should adjust this based on your actual notification type IDs
        return self.notification_type_name == "Invitation" if self.notification_type_name else False
    
    def get_formatted_date(self, format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
        """
        Get formatted notification date
        
        Args:
            format_str: The format string for the date
        
        Returns:
            Formatted date string
        """
        return self.notification_date.strftime(format_str)
    
    def to_dict(self) -> dict:
        """
        Convert the notification to a dictionary representation
        
        Returns:
            Dictionary representation of the notification
        """
        return {
            "notification_id": self.notification_id,
            "message": self.message,
            "notification_date": self.notification_date.isoformat(),
            "invitation_id": self.invitation_id,
            "notification_type_id": self.notification_type_id,
            "notification_state_id": self.notification_state_id,
            "user_id": self.user_id,
            "notification_type_name": self.notification_type_name,
            "notification_state_name": self.notification_state_name
        }
    
    def __str__(self) -> str:
        """String representation of the notification"""
        return f"Notification(id={self.notification_id}, user_id={self.user_id}, message='{self.message}')"
    
    def __repr__(self) -> str:
        """Detailed string representation of the notification"""
        return (f"Notification(notification_id={self.notification_id}, "
                f"message='{self.message}', user_id={self.user_id}, "
                f"invitation_id={self.invitation_id}, "
                f"notification_type_id={self.notification_type_id}, "
                f"notification_state_id={self.notification_state_id}, "
                f"notification_date={self.notification_date})") 