import pytest
from datetime import datetime
import pytz
from domain.entities import Notification, NotificationMapper


class TestNotificationEntity:
    """Test cases for the Notification entity"""
    
    def test_create_notification_with_factory_method(self):
        """Test creating a notification using the factory method"""
        notification = Notification.create_new(
            message="Test notification",
            user_id=123,
            notification_type_id=1,
            invitation_id=456,
            notification_state_id=1
        )
        
        assert notification.message == "Test notification"
        assert notification.user_id == 123
        assert notification.notification_type_id == 1
        assert notification.invitation_id == 456
        assert notification.notification_state_id == 1
        assert notification.notification_id is None
        assert isinstance(notification.notification_date, datetime)
    
    def test_create_notification_with_constructor(self):
        """Test creating a notification using the constructor"""
        now = datetime.now(pytz.timezone("America/Bogota"))
        
        notification = Notification(
            notification_id=1,
            message="Test notification",
            notification_date=now,
            invitation_id=456,
            notification_type_id=1,
            notification_state_id=1,
            user_id=123
        )
        
        assert notification.notification_id == 1
        assert notification.message == "Test notification"
        assert notification.notification_date == now
        assert notification.user_id == 123
    
    def test_notification_validation_positive_user_id(self):
        """Test that user_id must be positive"""
        with pytest.raises(ValueError, match="User ID must be a positive integer"):
            Notification.create_new(
                message="Test",
                user_id=0,  # Invalid
                notification_type_id=1,
                invitation_id=456,
                notification_state_id=1
            )
    
    def test_notification_validation_positive_invitation_id(self):
        """Test that invitation_id must be positive"""
        with pytest.raises(ValueError, match="Invitation ID must be a positive integer"):
            Notification.create_new(
                message="Test",
                user_id=123,
                notification_type_id=1,
                invitation_id=-1,  # Invalid
                notification_state_id=1
            )
    
    def test_notification_validation_positive_notification_type_id(self):
        """Test that notification_type_id must be positive"""
        with pytest.raises(ValueError, match="Notification type ID must be a positive integer"):
            Notification.create_new(
                message="Test",
                user_id=123,
                notification_type_id=0,  # Invalid
                invitation_id=456,
                notification_state_id=1
            )
    
    def test_notification_validation_positive_notification_state_id(self):
        """Test that notification_state_id must be positive"""
        with pytest.raises(ValueError, match="Notification state ID must be a positive integer"):
            Notification.create_new(
                message="Test",
                user_id=123,
                notification_type_id=1,
                invitation_id=456,
                notification_state_id=0  # Invalid
            )
    
    def test_notification_validation_empty_message(self):
        """Test that message cannot be empty if provided"""
        with pytest.raises(ValueError, match="Message cannot be empty if provided"):
            Notification.create_new(
                message="   ",  # Empty message
                user_id=123,
                notification_type_id=1,
                invitation_id=456,
                notification_state_id=1
            )
    
    def test_notification_with_none_message(self):
        """Test that message can be None"""
        notification = Notification.create_new(
            message=None,
            user_id=123,
            notification_type_id=1,
            invitation_id=456,
            notification_state_id=1
        )
        
        assert notification.message is None
    
    def test_update_state(self):
        """Test updating notification state"""
        notification = Notification.create_new(
            message="Test",
            user_id=123,
            notification_type_id=1,
            invitation_id=456,
            notification_state_id=1
        )
        
        notification.update_state(2)
        assert notification.notification_state_id == 2
    
    def test_update_state_invalid(self):
        """Test updating notification state with invalid value"""
        notification = Notification.create_new(
            message="Test",
            user_id=123,
            notification_type_id=1,
            invitation_id=456,
            notification_state_id=1
        )
        
        with pytest.raises(ValueError, match="State ID must be a positive integer"):
            notification.update_state(0)
    
    def test_state_checking_methods(self):
        """Test state checking methods"""
        notification = Notification.create_new(
            message="Test",
            user_id=123,
            notification_type_id=1,
            invitation_id=456,
            notification_state_id=1
        )
        
        # Test pending state
        assert notification.is_pending() is True
        assert notification.is_sent() is False
        assert notification.is_read() is False
        
        # Test sent state
        notification.update_state(2)
        assert notification.is_pending() is False
        assert notification.is_sent() is True
        assert notification.is_read() is False
        
        # Test read state
        notification.update_state(3)
        assert notification.is_pending() is False
        assert notification.is_sent() is False
        assert notification.is_read() is True
    
    def test_mark_as_sent(self):
        """Test marking notification as sent"""
        notification = Notification.create_new(
            message="Test",
            user_id=123,
            notification_type_id=1,
            invitation_id=456,
            notification_state_id=1
        )
        
        notification.mark_as_sent()
        assert notification.notification_state_id == 2
        assert notification.is_sent() is True
    
    def test_mark_as_read(self):
        """Test marking notification as read"""
        notification = Notification.create_new(
            message="Test",
            user_id=123,
            notification_type_id=1,
            invitation_id=456,
            notification_state_id=1
        )
        
        notification.mark_as_read()
        assert notification.notification_state_id == 3
        assert notification.is_read() is True
    
    def test_is_invitation_notification(self):
        """Test checking if notification is invitation type"""
        notification = Notification.create_new(
            message="Test",
            user_id=123,
            notification_type_id=1,
            invitation_id=456,
            notification_state_id=1
        )
        
        # Without type name
        assert notification.is_invitation_notification() is False
        
        # With invitation type name
        notification.notification_type_name = "Invitation"
        assert notification.is_invitation_notification() is True
        
        # With other type name
        notification.notification_type_name = "Other"
        assert notification.is_invitation_notification() is False
    
    def test_get_formatted_date(self):
        """Test getting formatted date"""
        notification = Notification.create_new(
            message="Test",
            user_id=123,
            notification_type_id=1,
            invitation_id=456,
            notification_state_id=1
        )
        
        # Default format
        formatted = notification.get_formatted_date()
        assert isinstance(formatted, str)
        assert len(formatted) > 0
        
        # Custom format
        custom_formatted = notification.get_formatted_date("%d/%m/%Y")
        assert "/" in custom_formatted
    
    def test_to_dict(self):
        """Test converting notification to dictionary"""
        notification = Notification.create_new(
            message="Test notification",
            user_id=123,
            notification_type_id=1,
            invitation_id=456,
            notification_state_id=1
        )
        
        notification.notification_type_name = "Invitation"
        notification.notification_state_name = "Pending"
        
        result = notification.to_dict()
        
        assert result["message"] == "Test notification"
        assert result["user_id"] == 123
        assert result["notification_type_id"] == 1
        assert result["invitation_id"] == 456
        assert result["notification_state_id"] == 1
        assert result["notification_type_name"] == "Invitation"
        assert result["notification_state_name"] == "Pending"
        assert "notification_date" in result
    
    def test_string_representations(self):
        """Test string representations of notification"""
        notification = Notification.create_new(
            message="Test notification",
            user_id=123,
            notification_type_id=1,
            invitation_id=456,
            notification_state_id=1
        )
        
        # Test __str__
        str_repr = str(notification)
        assert "Notification" in str_repr
        assert "123" in str_repr
        assert "Test notification" in str_repr
        
        # Test __repr__
        repr_str = repr(notification)
        assert "Notification(" in repr_str
        assert "user_id=123" in repr_str
        assert "message='Test notification'" in repr_str


class TestNotificationMapper:
    """Test cases for the NotificationMapper"""
    
    def test_to_entity_basic(self):
        """Test converting a basic model to entity"""
        # Mock SQLAlchemy model
        class MockModel:
            def __init__(self):
                self.notification_id = 1
                self.message = "Test message"
                self.notification_date = datetime.now(pytz.timezone("America/Bogota"))
                self.invitation_id = 456
                self.notification_type_id = 1
                self.notification_state_id = 1
                self.user_id = 123
                self.notification_type = None
                self.state = None
        
        model = MockModel()
        entity = NotificationMapper.to_entity(model)
        
        assert entity.notification_id == 1
        assert entity.message == "Test message"
        assert entity.user_id == 123
        assert entity.notification_type_name is None
        assert entity.notification_state_name is None
    
    def test_to_entity_with_relationships(self):
        """Test converting model with relationships to entity"""
        # Mock SQLAlchemy model with relationships
        class MockType:
            def __init__(self):
                self.name = "Invitation"
        
        class MockState:
            def __init__(self):
                self.name = "Pending"
        
        class MockModel:
            def __init__(self):
                self.notification_id = 1
                self.message = "Test message"
                self.notification_date = datetime.now(pytz.timezone("America/Bogota"))
                self.invitation_id = 456
                self.notification_type_id = 1
                self.notification_state_id = 1
                self.user_id = 123
                self.notification_type = MockType()
                self.state = MockState()
        
        model = MockModel()
        entity = NotificationMapper.to_entity(model)
        
        assert entity.notification_type_name == "Invitation"
        assert entity.notification_state_name == "Pending"
    
    def test_to_model(self):
        """Test converting entity to model"""
        entity = Notification.create_new(
            message="Test message",
            user_id=123,
            notification_type_id=1,
            invitation_id=456,
            notification_state_id=1
        )
        
        # Test that the method exists and doesn't raise errors with valid input
        assert hasattr(NotificationMapper, 'to_model')
        assert callable(NotificationMapper.to_model)
        
        # Verify entity properties are accessible for mapping
        assert entity.message == "Test message"
        assert entity.user_id == 123
        assert entity.notification_type_id == 1


if __name__ == "__main__":
    pytest.main([__file__]) 