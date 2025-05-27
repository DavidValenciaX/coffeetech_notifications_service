import pytest
from unittest.mock import Mock, MagicMock, patch
from datetime import datetime
import pytz
from domain.services.notification_service import NotificationService, SerializationError, NotificationNotFoundError
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
from models.models import Notifications, NotificationStates, NotificationTypes


class TestNotificationService:
    """Test cases for the NotificationService with entities"""
    
    @pytest.fixture
    def mock_repository(self):
        """Create a mock repository"""
        return Mock()
    
    @pytest.fixture
    def notification_service(self, mock_repository):
        """Create a notification service with mock repository"""
        return NotificationService(mock_repository)
    
    @pytest.fixture
    def sample_notification_model(self):
        """Create a sample notification model"""
        model = Mock(spec=Notifications)
        model.notification_id = 1
        model.message = "Test notification"
        model.notification_date = datetime.now(pytz.timezone("America/Bogota"))
        model.invitation_id = 123
        model.notification_type_id = 1
        model.notification_state_id = 1
        model.user_id = 456
        
        # Mock relationships
        model.notification_type = Mock()
        model.notification_type.name = "Invitation"
        model.state = Mock()
        model.state.name = "Pending"
        
        return model
    
    @pytest.fixture
    def sample_notification_entity(self):
        """Create a sample notification entity"""
        return Notification.create_new(
            message="Test notification",
            user_id=456,
            notification_type_id=1,
            invitation_id=123,
            notification_state_id=1
        )
    
    def test_authenticate_user_valid_token(self, notification_service):
        """Test user authentication with valid token"""
        with patch('domain.services.notification_service.verify_session_token') as mock_verify:
            mock_verify.return_value = {"user_id": 123, "name": "Test User"}
            
            result = notification_service.authenticate_user("valid_token")
            
            assert result is not None
            assert result["user_id"] == 123
            assert result["name"] == "Test User"
            mock_verify.assert_called_once_with("valid_token")
    
    def test_authenticate_user_invalid_token(self, notification_service):
        """Test user authentication with invalid token"""
        with patch('domain.services.notification_service.verify_session_token') as mock_verify:
            mock_verify.return_value = None
            
            result = notification_service.authenticate_user("invalid_token")
            
            assert result is None
            mock_verify.assert_called_once_with("invalid_token")
    
    def test_get_user_notifications_success(self, notification_service, mock_repository, sample_notification_model):
        """Test getting user notifications successfully"""
        mock_repository.get_notifications_by_user_id.return_value = [sample_notification_model]
        
        result = notification_service.get_user_notifications(456)
        
        assert len(result) == 1
        assert isinstance(result[0], NotificationResponse)
        assert result[0].notification_id == 1
        assert result[0].message == "Test notification"
        assert result[0].notification_type == "Invitation"
        assert result[0].notification_state == "Pending"
        mock_repository.get_notifications_by_user_id.assert_called_once_with(456)
    
    def test_get_user_notifications_empty(self, notification_service, mock_repository):
        """Test getting user notifications when none exist"""
        mock_repository.get_notifications_by_user_id.return_value = []
        
        result = notification_service.get_user_notifications(456)
        
        assert result == []
        mock_repository.get_notifications_by_user_id.assert_called_once_with(456)
    
    def test_get_user_notifications_serialization_error(self, notification_service, mock_repository):
        """Test handling serialization errors"""
        # Create a model that will cause serialization issues
        bad_model = Mock()
        bad_model.notification_id = 1
        bad_model.message = "Test"
        bad_model.notification_date = "invalid_date"  # This will cause issues
        
        mock_repository.get_notifications_by_user_id.return_value = [bad_model]
        
        with pytest.raises(SerializationError):
            notification_service.get_user_notifications(456)
    
    def test_get_all_notification_states(self, notification_service, mock_repository):
        """Test getting all notification states"""
        mock_state = Mock(spec=NotificationStates)
        mock_state.notification_state_id = 1
        mock_state.name = "Pending"
        
        mock_repository.get_all_notification_states.return_value = [mock_state]
        
        result = notification_service.get_all_notification_states()
        
        assert len(result) == 1
        assert isinstance(result[0], NotificationStateResponse)
        assert result[0].notification_state_id == 1
        assert result[0].name == "Pending"
    
    def test_get_all_notification_types(self, notification_service, mock_repository):
        """Test getting all notification types"""
        mock_type = Mock(spec=NotificationTypes)
        mock_type.notification_type_id = 1
        mock_type.name = "Invitation"
        
        mock_repository.get_all_notification_types.return_value = [mock_type]
        
        result = notification_service.get_all_notification_types()
        
        assert len(result) == 1
        assert isinstance(result[0], NotificationTypeResponse)
        assert result[0].notification_type_id == 1
        assert result[0].name == "Invitation"
    
    def test_get_all_notifications(self, notification_service, mock_repository, sample_notification_model):
        """Test getting all notifications"""
        mock_repository.get_all_notifications.return_value = [sample_notification_model]
        
        result = notification_service.get_all_notifications()
        
        assert len(result) == 1
        assert isinstance(result[0], NotificationDetailResponse)
        assert result[0].notification_id == 1
        assert result[0].user_id == 456
    
    def test_get_notification_by_invitation_found(self, notification_service, mock_repository, sample_notification_model):
        """Test getting notification by invitation ID when found"""
        mock_repository.get_notification_by_invitation.return_value = sample_notification_model
        
        result = notification_service.get_notification_by_invitation(123)
        
        assert isinstance(result, NotificationByInvitationResponse)
        assert result.notification_id == 1
        mock_repository.get_notification_by_invitation.assert_called_once_with(123)
    
    def test_get_notification_by_invitation_not_found(self, notification_service, mock_repository):
        """Test getting notification by invitation ID when not found"""
        mock_repository.get_notification_by_invitation.return_value = None
        
        result = notification_service.get_notification_by_invitation(123)
        
        assert isinstance(result, NotificationByInvitationResponse)
        assert result.notification_id is None
    
    def test_delete_notifications_by_invitation_success(self, notification_service, mock_repository):
        """Test deleting notifications by invitation ID successfully"""
        mock_repository.delete_notifications_by_invitation.return_value = 2
        
        result = notification_service.delete_notifications_by_invitation(123)
        
        assert isinstance(result, DeleteNotificationsResponse)
        assert result.deleted_count == 2
        mock_repository.delete_notifications_by_invitation.assert_called_once_with(123)
    
    def test_delete_notifications_by_invitation_error(self, notification_service, mock_repository):
        """Test handling errors when deleting notifications"""
        mock_repository.delete_notifications_by_invitation.side_effect = Exception("Database error")
        
        with pytest.raises(Exception):
            notification_service.delete_notifications_by_invitation(123)
    
    def test_update_notification_state_success(self, notification_service, mock_repository, sample_notification_model):
        """Test updating notification state successfully"""
        mock_repository.get_notification_by_id.return_value = sample_notification_model
        mock_repository.update_notification_state.return_value = sample_notification_model
        
        # Should not raise any exception
        notification_service.update_notification_state(1, 2)
        
        mock_repository.get_notification_by_id.assert_called_once_with(1)
        mock_repository.update_notification_state.assert_called_once_with(1, 2)
    
    def test_update_notification_state_not_found(self, notification_service, mock_repository):
        """Test updating notification state when notification not found"""
        mock_repository.get_notification_by_id.return_value = None
        
        with pytest.raises(NotificationNotFoundError):
            notification_service.update_notification_state(1, 2)
    
    def test_update_notification_state_invalid_state(self, notification_service, mock_repository, sample_notification_model):
        """Test updating notification state with invalid state ID"""
        mock_repository.get_notification_by_id.return_value = sample_notification_model
        
        with pytest.raises(ValueError, match="Estado inválido"):
            notification_service.update_notification_state(1, 0)  # Invalid state ID
    
    def test_update_notification_state_update_failed(self, notification_service, mock_repository, sample_notification_model):
        """Test handling update failure"""
        mock_repository.get_notification_by_id.return_value = sample_notification_model
        mock_repository.update_notification_state.return_value = None
        
        with pytest.raises(NotificationNotFoundError, match="Error actualizando notificación"):
            notification_service.update_notification_state(1, 2)
    
    @patch('domain.services.notification_service.get_user_devices_by_user_id')
    @patch('domain.services.notification_service.send_fcm_notification')
    def test_send_notification_success_with_fcm(self, mock_send_fcm, mock_get_devices, notification_service, mock_repository, sample_notification_model):
        """Test sending notification successfully with FCM"""
        # Setup mocks
        mock_repository.create_notification.return_value = sample_notification_model
        mock_get_devices.return_value = [{"fcm_token": "token123"}]
        mock_send_fcm.return_value = {"success": True}
        mock_repository.get_notification_by_id.return_value = sample_notification_model
        mock_repository.update_notification_state.return_value = sample_notification_model
        
        request = SendNotificationRequest(
            message="Test notification",
            user_id=456,
            notification_type_id=1,
            invitation_id=123,
            notification_state_id=1,
            fcm_title="Test Title",
            fcm_body="Test Body"
        )
        
        result = notification_service.send_notification(request)
        
        assert isinstance(result, SendNotificationResponse)
        assert result.notification_id == 1
        assert result.devices_notified == 1
        assert result.invalid_tokens is None
        assert result.fcm_errors is None
        
        mock_repository.create_notification.assert_called_once()
        mock_get_devices.assert_called_once_with(456)
        mock_send_fcm.assert_called_once_with("token123", "Test Title", "Test Body")
    
    @patch('domain.services.notification_service.get_user_devices_by_user_id')
    def test_send_notification_no_devices(self, mock_get_devices, notification_service, mock_repository, sample_notification_model):
        """Test sending notification when user has no devices"""
        mock_repository.create_notification.return_value = sample_notification_model
        mock_get_devices.return_value = []
        
        request = SendNotificationRequest(
            message="Test notification",
            user_id=456,
            notification_type_id=1,
            invitation_id=123,
            notification_state_id=1,
            fcm_title="Test Title",
            fcm_body="Test Body"
        )
        
        result = notification_service.send_notification(request)
        
        assert isinstance(result, SendNotificationResponse)
        assert result.notification_id == 1
        assert result.devices_notified == 0
    
    def test_send_notification_entity_validation_error(self, notification_service, mock_repository):
        """Test sending notification with invalid entity data"""
        request = SendNotificationRequest(
            message="Test notification",
            user_id=0,  # Invalid user ID
            notification_type_id=1,
            invitation_id=123,
            notification_state_id=1
        )
        
        with pytest.raises(ValueError, match="Datos de notificación inválidos"):
            notification_service.send_notification(request)
    
    @patch('domain.services.notification_service.get_user_devices_by_user_id')
    @patch('domain.services.notification_service.send_fcm_notification')
    def test_send_notification_fcm_error(self, mock_send_fcm, mock_get_devices, notification_service, mock_repository, sample_notification_model):
        """Test sending notification with FCM errors"""
        mock_repository.create_notification.return_value = sample_notification_model
        mock_get_devices.return_value = [{"fcm_token": "token123"}]
        mock_send_fcm.return_value = {"should_delete_token": True, "error_type": "invalid_token", "error_message": "Token invalid"}
        
        request = SendNotificationRequest(
            message="Test notification",
            user_id=456,
            notification_type_id=1,
            invitation_id=123,
            notification_state_id=1,
            fcm_title="Test Title",
            fcm_body="Test Body"
        )
        
        result = notification_service.send_notification(request)
        
        assert result.devices_notified == 0
        assert len(result.invalid_tokens) == 1
        assert "token123" in result.invalid_tokens
        assert len(result.fcm_errors) == 1
    
    def test_get_notification_entity_by_id_found(self, notification_service, mock_repository, sample_notification_model):
        """Test getting notification entity by ID when found"""
        mock_repository.get_notification_by_id.return_value = sample_notification_model
        
        result = notification_service.get_notification_entity_by_id(1)
        
        assert isinstance(result, Notification)
        assert result.notification_id == 1
        assert result.message == "Test notification"
        mock_repository.get_notification_by_id.assert_called_once_with(1)
    
    def test_get_notification_entity_by_id_not_found(self, notification_service, mock_repository):
        """Test getting notification entity by ID when not found"""
        mock_repository.get_notification_by_id.return_value = None
        
        result = notification_service.get_notification_entity_by_id(1)
        
        assert result is None
    
    def test_get_user_notifications_as_entities(self, notification_service, mock_repository, sample_notification_model):
        """Test getting user notifications as entities"""
        mock_repository.get_notifications_by_user_id.return_value = [sample_notification_model]
        
        result = notification_service.get_user_notifications_as_entities(456)
        
        assert len(result) == 1
        assert isinstance(result[0], Notification)
        assert result[0].notification_id == 1
        assert result[0].user_id == 456
    
    def test_process_notification_workflow_pending(self, notification_service, mock_repository, sample_notification_entity, sample_notification_model):
        """Test processing notification workflow for pending notification"""
        # Set up entity with ID (simulating saved entity)
        sample_notification_entity.notification_id = 1
        
        mock_repository.get_notification_by_id.return_value = sample_notification_model
        mock_repository.update_notification_state.return_value = sample_notification_model
        
        result = notification_service.process_notification_workflow(sample_notification_entity)
        
        assert isinstance(result, Notification)
        assert result.is_sent()  # Should be marked as sent
        mock_repository.update_notification_state.assert_called_once_with(1, 2)  # Updated to sent state
    
    def test_process_notification_workflow_not_pending(self, notification_service, sample_notification_entity):
        """Test processing notification workflow for non-pending notification"""
        # Set notification to sent state
        sample_notification_entity.notification_state_id = 2
        sample_notification_entity.notification_id = 1
        
        result = notification_service.process_notification_workflow(sample_notification_entity)
        
        assert isinstance(result, Notification)
        assert result.notification_state_id == 2  # Should remain in sent state
    
    def test_process_notification_workflow_error(self, notification_service, mock_repository, sample_notification_entity):
        """Test handling errors in notification workflow"""
        sample_notification_entity.notification_id = 1
        mock_repository.get_notification_by_id.side_effect = Exception("Database error")
        
        with pytest.raises(Exception):
            notification_service.process_notification_workflow(sample_notification_entity)


class TestNotificationServiceIntegration:
    """Integration tests for NotificationService with real entities"""
    
    @pytest.fixture
    def mock_repository(self):
        """Create a mock repository for integration tests"""
        return Mock()
    
    @pytest.fixture
    def notification_service(self, mock_repository):
        """Create a notification service with mock repository"""
        return NotificationService(mock_repository)
    
    def test_entity_validation_integration(self, notification_service):
        """Test that entity validation is properly integrated"""
        request = SendNotificationRequest(
            message="",  # Empty message should be caught by entity validation
            user_id=123,
            notification_type_id=1,
            invitation_id=456,
            notification_state_id=1
        )
        
        with pytest.raises(ValueError, match="Datos de notificación inválidos"):
            notification_service.send_notification(request)
    
    def test_entity_business_logic_integration(self, notification_service, mock_repository):
        """Test that entity business logic is properly integrated"""
        # Create a mock model that represents an invitation notification
        mock_model = Mock()
        mock_model.notification_id = 1
        mock_model.message = "Invitation notification"
        mock_model.notification_date = datetime.now(pytz.timezone("America/Bogota"))
        mock_model.invitation_id = 123
        mock_model.notification_type_id = 1
        mock_model.notification_state_id = 1
        mock_model.user_id = 456
        mock_model.notification_type = Mock()
        mock_model.notification_type.name = "Invitation"
        mock_model.state = Mock()
        mock_model.state.name = "Pending"
        
        mock_repository.get_notification_by_id.return_value = mock_model
        
        entity = notification_service.get_notification_entity_by_id(1)
        
        # Test entity business logic
        assert entity.is_pending()
        assert entity.is_invitation_notification()
        
        # Test state transitions
        entity.mark_as_sent()
        assert entity.is_sent()
        assert not entity.is_pending()


if __name__ == "__main__":
    pytest.main([__file__]) 