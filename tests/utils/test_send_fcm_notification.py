import pytest
import os
import logging
from unittest.mock import Mock, patch, MagicMock
from firebase_admin import messaging, exceptions
from firebase_admin._messaging_utils import SenderIdMismatchError

from utils.send_fcm_notification import send_fcm_notification


class TestSendFCMNotification:
    """Test suite for the send_fcm_notification function."""

    @pytest.fixture
    def mock_firebase_app(self):
        """Mock Firebase app initialization."""
        with patch('utils.send_fcm_notification.firebase_admin._apps', [Mock()]):
            yield

    @pytest.fixture
    def sample_notification_data(self):
        """Sample notification data for testing."""
        return {
            "fcm_token": "test_fcm_token_123",
            "title": "Test Notification",
            "body": "This is a test notification body"
        }

    def test_successful_notification_send(self, mock_firebase_app, sample_notification_data):
        """Test successful FCM notification sending."""
        mock_message_id = "projects/test-project/messages/test-message-id"
        
        with patch('utils.send_fcm_notification.messaging.send') as mock_send:
            mock_send.return_value = mock_message_id
            
            result = send_fcm_notification(
                sample_notification_data["fcm_token"],
                sample_notification_data["title"],
                sample_notification_data["body"]
            )
            
            # Verify the result
            assert result["success"] is True
            assert result["token"] == sample_notification_data["fcm_token"]
            assert result["message_id"] == mock_message_id
            assert result["error_type"] is None
            assert result["error_message"] is None
            
            # Verify messaging.send was called with correct parameters
            mock_send.assert_called_once()
            call_args = mock_send.call_args[0][0]  # Get the message argument
            assert call_args.token == sample_notification_data["fcm_token"]
            assert call_args.notification.title == sample_notification_data["title"]
            assert call_args.notification.body == sample_notification_data["body"]

    def test_sender_id_mismatch_error(self, mock_firebase_app, sample_notification_data):
        """Test handling of SenderIdMismatchError."""
        error_message = "Token belongs to different project"
        
        with patch('utils.send_fcm_notification.messaging.send') as mock_send:
            mock_send.side_effect = SenderIdMismatchError(error_message)
            
            with pytest.raises(SenderIdMismatchError) as exc_info:
                send_fcm_notification(
                    sample_notification_data["fcm_token"],
                    sample_notification_data["title"],
                    sample_notification_data["body"]
                )
            
            # Verify the exception message
            assert "Token FCM pertenece a un proyecto diferente" in str(exc_info.value)

    def test_invalid_argument_error(self, mock_firebase_app, sample_notification_data):
        """Test handling of InvalidArgumentError."""
        error_message = "Invalid token format"
        
        with patch('utils.send_fcm_notification.messaging.send') as mock_send:
            mock_send.side_effect = exceptions.InvalidArgumentError(error_message)
            
            result = send_fcm_notification(
                sample_notification_data["fcm_token"],
                sample_notification_data["title"],
                sample_notification_data["body"]
            )
            
            # Verify the result
            assert result["success"] is False
            assert result["token"] == sample_notification_data["fcm_token"]
            assert result["error_type"] == "invalid_token"
            assert result["error_message"] == error_message
            assert result["should_delete_token"] is True

    def test_unauthenticated_error(self, mock_firebase_app, sample_notification_data):
        """Test handling of UnauthenticatedError."""
        error_message = "Invalid credentials"
        
        with patch('utils.send_fcm_notification.messaging.send') as mock_send:
            mock_send.side_effect = exceptions.UnauthenticatedError(error_message)
            
            result = send_fcm_notification(
                sample_notification_data["fcm_token"],
                sample_notification_data["title"],
                sample_notification_data["body"]
            )
            
            # Verify the result
            assert result["success"] is False
            assert result["token"] == sample_notification_data["fcm_token"]
            assert result["error_type"] == "authentication_error"
            assert result["error_message"] == error_message
            assert "should_delete_token" not in result

    def test_generic_exception(self, mock_firebase_app, sample_notification_data):
        """Test handling of generic exceptions."""
        error_message = "Unexpected error occurred"
        
        with patch('utils.send_fcm_notification.messaging.send') as mock_send:
            mock_send.side_effect = Exception(error_message)
            
            result = send_fcm_notification(
                sample_notification_data["fcm_token"],
                sample_notification_data["title"],
                sample_notification_data["body"]
            )
            
            # Verify the result
            assert result["success"] is False
            assert result["token"] == sample_notification_data["fcm_token"]
            assert result["error_type"] == "unknown_error"
            assert result["error_message"] == error_message
            assert "should_delete_token" not in result

    def test_message_construction(self, mock_firebase_app, sample_notification_data):
        """Test that the FCM message is constructed correctly."""
        with patch('utils.send_fcm_notification.messaging.send') as mock_send, \
             patch('utils.send_fcm_notification.messaging.Message') as mock_message_class, \
             patch('utils.send_fcm_notification.messaging.Notification') as mock_notification_class:
            
            mock_send.return_value = "test-message-id"
            mock_message_instance = Mock()
            mock_notification_instance = Mock()
            mock_message_class.return_value = mock_message_instance
            mock_notification_class.return_value = mock_notification_instance
            
            send_fcm_notification(
                sample_notification_data["fcm_token"],
                sample_notification_data["title"],
                sample_notification_data["body"]
            )
            
            # Verify Notification was created with correct parameters
            mock_notification_class.assert_called_once_with(
                title=sample_notification_data["title"],
                body=sample_notification_data["body"]
            )
            
            # Verify Message was created with correct parameters
            mock_message_class.assert_called_once_with(
                notification=mock_notification_instance,
                token=sample_notification_data["fcm_token"]
            )
            
            # Verify send was called with the message
            mock_send.assert_called_once_with(mock_message_instance)

    @pytest.mark.parametrize("fcm_token,title,body", [
        ("token123", "Title", "Body"),
        ("another_token", "Another Title", "Another Body"),
        ("special-token_456", "Special Title!", "Body with special chars: @#$%"),
    ])
    def test_different_input_parameters(self, mock_firebase_app, fcm_token, title, body):
        """Test the function with different input parameters."""
        with patch('utils.send_fcm_notification.messaging.send') as mock_send:
            mock_send.return_value = "test-message-id"
            
            result = send_fcm_notification(fcm_token, title, body)
            
            assert result["success"] is True
            assert result["token"] == fcm_token
            assert result["message_id"] == "test-message-id"

    def test_logging_on_success(self, mock_firebase_app, sample_notification_data, caplog):
        """Test that success is logged correctly."""
        mock_message_id = "test-message-id"
        
        with caplog.at_level(logging.INFO):
            with patch('utils.send_fcm_notification.messaging.send') as mock_send:
                mock_send.return_value = mock_message_id
                
                send_fcm_notification(
                    sample_notification_data["fcm_token"],
                    sample_notification_data["title"],
                    sample_notification_data["body"]
                )
                
                # Check that success was logged
                assert "Notificación enviada" in caplog.text
                assert mock_message_id in caplog.text

    def test_logging_on_sender_id_mismatch(self, mock_firebase_app, sample_notification_data, caplog):
        """Test that SenderIdMismatchError is logged correctly."""
        error_message = "Token belongs to different project"
        
        with caplog.at_level(logging.ERROR):
            with patch('utils.send_fcm_notification.messaging.send') as mock_send:
                mock_send.side_effect = SenderIdMismatchError(error_message)
                
                with pytest.raises(SenderIdMismatchError):
                    send_fcm_notification(
                        sample_notification_data["fcm_token"],
                        sample_notification_data["title"],
                        sample_notification_data["body"]
                    )
                
                # Check that error was logged
                assert "Token FCM pertenece a un proyecto diferente" in caplog.text

    def test_logging_on_invalid_argument(self, mock_firebase_app, sample_notification_data, caplog):
        """Test that InvalidArgumentError is logged correctly."""
        error_message = "Invalid token format"
        
        with caplog.at_level(logging.ERROR):
            with patch('utils.send_fcm_notification.messaging.send') as mock_send:
                mock_send.side_effect = exceptions.InvalidArgumentError(error_message)
                
                send_fcm_notification(
                    sample_notification_data["fcm_token"],
                    sample_notification_data["title"],
                    sample_notification_data["body"]
                )
                
                # Check that error was logged
                assert "Token inválido o formato incorrecto" in caplog.text

    def test_logging_on_unauthenticated_error(self, mock_firebase_app, sample_notification_data, caplog):
        """Test that UnauthenticatedError is logged correctly."""
        error_message = "Invalid credentials"
        
        with caplog.at_level(logging.ERROR):
            with patch('utils.send_fcm_notification.messaging.send') as mock_send:
                mock_send.side_effect = exceptions.UnauthenticatedError(error_message)
                
                send_fcm_notification(
                    sample_notification_data["fcm_token"],
                    sample_notification_data["title"],
                    sample_notification_data["body"]
                )
                
                # Check that error was logged
                assert "Credenciales no válidas / API FCM deshabilitada" in caplog.text

    def test_logging_on_generic_exception(self, mock_firebase_app, sample_notification_data, caplog):
        """Test that generic exceptions are logged correctly."""
        error_message = "Unexpected error"
        
        with caplog.at_level(logging.ERROR):
            with patch('utils.send_fcm_notification.messaging.send') as mock_send:
                mock_send.side_effect = Exception(error_message)
                
                send_fcm_notification(
                    sample_notification_data["fcm_token"],
                    sample_notification_data["title"],
                    sample_notification_data["body"]
                )
                
                # Check that error was logged
                assert "Error inesperado enviando notificación" in caplog.text


class TestFirebaseInitialization:
    """Test suite for Firebase app initialization."""

    def test_firebase_app_initialization_when_no_apps_exist(self):
        """Test Firebase app initialization when no apps exist."""
        with patch('utils.send_fcm_notification.firebase_admin._apps', []), \
             patch('utils.send_fcm_notification.credentials.Certificate') as mock_cert, \
             patch('utils.send_fcm_notification.firebase_admin.initialize_app') as mock_init, \
             patch('os.path.join') as mock_join, \
             patch('os.path.dirname') as mock_dirname:
            
            mock_dirname.return_value = "/test/path"
            mock_join.return_value = "/test/path/serviceAccountKey.json"
            mock_cert_instance = Mock()
            mock_cert.return_value = mock_cert_instance
            
            # Import the module to trigger initialization
            import importlib
            import utils.send_fcm_notification
            importlib.reload(utils.send_fcm_notification)
            
            # Verify initialization was called
            mock_cert.assert_called_once_with("/test/path/serviceAccountKey.json")
            mock_init.assert_called_once_with(mock_cert_instance)

    def test_firebase_app_not_initialized_when_apps_exist(self):
        """Test Firebase app is not re-initialized when apps already exist."""
        with patch('utils.send_fcm_notification.firebase_admin._apps', [Mock()]), \
             patch('utils.send_fcm_notification.credentials.Certificate') as mock_cert, \
             patch('utils.send_fcm_notification.firebase_admin.initialize_app') as mock_init:
            
            # Import the module
            import importlib
            import utils.send_fcm_notification
            importlib.reload(utils.send_fcm_notification)
            
            # Verify initialization was NOT called
            mock_cert.assert_not_called()
            mock_init.assert_not_called()

    def test_service_account_path_construction(self):
        """Test that the service account path is constructed correctly."""
        with patch('utils.send_fcm_notification.firebase_admin._apps', [Mock()]), \
             patch('utils.send_fcm_notification.os.path.join') as mock_join, \
             patch('utils.send_fcm_notification.os.path.dirname') as mock_dirname:
            
            # Set up the mock to return values for the nested dirname calls
            mock_dirname.side_effect = lambda x: {
                '/test/utils/send_fcm_notification.py': '/test/utils',
                '/test/utils': '/test'
            }.get(x, '/test')
            
            expected_path = "/test/serviceAccountKey.json"
            mock_join.return_value = expected_path
            
            # Import the module to trigger path construction
            import importlib
            import utils.send_fcm_notification
            importlib.reload(utils.send_fcm_notification)
            
            # Verify path construction - dirname should be called twice for double dirname
            assert mock_dirname.call_count >= 2
            mock_join.assert_called_with('/test', "serviceAccountKey.json") 