from unittest.mock import patch, MagicMock
import pytest
from datetime import datetime, timezone

# Patch sqlalchemy.create_engine before other project imports
_patch_create_engine = patch('sqlalchemy.create_engine', return_value=MagicMock())
_patch_create_engine.start()

from use_cases.get_notifications_use_case import GetNotificationsUseCase
from domain.services.notification_service import NotificationService
from domain.schemas import NotificationResponse # For checking response structure

class FaultyType:
    """Helper class to simulate an attribute access error."""
    @property
    def name(self):
        raise AttributeError("Simulated error")

@pytest.fixture
def mock_notification_type():
    mock_type = MagicMock() 
    mock_type.name = "TestType"
    return mock_type

@pytest.fixture
def mock_notification_state():
    mock_state = MagicMock() 
    mock_state.name = "TestState"
    return mock_state

@pytest.fixture
def mock_notification_service():
    """Create a mock notification service for testing"""
    return MagicMock(spec=NotificationService)

# Test for invalid session token
@patch('domain.services.notification_service.verify_session_token')
@patch('use_cases.get_notifications_use_case.session_token_invalid_response')
def test_get_notifications_invalid_token(mock_session_token_invalid_response, mock_verify_session_token, mock_notification_service):
    mock_notification_service.authenticate_user.return_value = None
    expected_response = {"status": "error", "message": "Token inválido"}
    mock_session_token_invalid_response.return_value = expected_response

    use_case = GetNotificationsUseCase(mock_notification_service)
    result = use_case.execute("invalid_token")

    mock_notification_service.authenticate_user.assert_called_once_with("invalid_token")
    mock_session_token_invalid_response.assert_called_once()
    assert result == expected_response

# Test for valid token, user has notifications
@patch('use_cases.get_notifications_use_case.create_response')
def test_get_notifications_valid_token_with_notifications(mock_create_response, mock_notification_service, mock_notification_type, mock_notification_state):
    mock_user = {'user_id': 1, 'name': 'Test User'}
    mock_notification_service.authenticate_user.return_value = mock_user

    mock_notif1_date = datetime.now(timezone.utc)
    mock_notification_response = NotificationResponse(
        notification_id=1,
        message="Test message 1",
        notification_date=mock_notif1_date, 
        invitation_id=101,
        notification_type="TestType",
        notification_state="TestState"
    )
    
    mock_notification_service.get_user_notifications.return_value = [mock_notification_response]
    
    expected_data = [mock_notification_response.model_dump()]
    
    # Consistent with the prompt's example for this test case for create_response call
    expected_message = "Notificaciones obtenidas exitosamente."
    expected_response_dict = {"status": "success", "message": expected_message, "data": expected_data}
    # Set the return value for the mock_create_response
    mock_create_response.return_value = expected_response_dict

    use_case = GetNotificationsUseCase(mock_notification_service)
    result = use_case.execute("valid_token")

    mock_notification_service.authenticate_user.assert_called_once_with("valid_token")
    mock_notification_service.get_user_notifications.assert_called_once_with(1)
    mock_create_response.assert_called_once_with(
        "success", 
        expected_message, 
        data=expected_data
    )
    assert result == expected_response_dict

# Test for valid token, user has no notifications
@patch('use_cases.get_notifications_use_case.create_response')
def test_get_notifications_valid_token_no_notifications(mock_create_response, mock_notification_service):
    mock_user = {'user_id': 1, 'name': 'Test User'}
    mock_notification_service.authenticate_user.return_value = mock_user
    mock_notification_service.get_user_notifications.return_value = []
    
    # Consistent with the prompt's example for this test case
    expected_message = "No hay notificaciones para este usuario."
    # The prompt's example for the final assert had "No hay notificaciones", I'm using the one from create_response call.
    expected_response_dict = {"status": "success", "message": expected_message, "data": []}
    mock_create_response.return_value = expected_response_dict

    use_case = GetNotificationsUseCase(mock_notification_service)
    result = use_case.execute("valid_token")

    mock_notification_service.authenticate_user.assert_called_once_with("valid_token")
    mock_notification_service.get_user_notifications.assert_called_once_with(1)
    mock_create_response.assert_called_once_with(
        "success", 
        expected_message, 
        data=[]
    )
    assert result == expected_response_dict

# Test for valid token, serialization error
@patch('use_cases.get_notifications_use_case.create_response')
def test_get_notifications_serialization_error(mock_create_response, mock_notification_service):
    mock_user = {'user_id': 1, 'name': 'Test User'}
    mock_notification_service.authenticate_user.return_value = mock_user

    # Simulate an exception being raised by the service
    mock_notification_service.get_user_notifications.side_effect = Exception("Simulated error")
    
    # As per prompt's example for assert_called_once_with for this test case
    expected_message = "Simulated error"
    expected_response_dict = {"status": "error", "message": expected_message, "data":[]}
    mock_create_response.return_value = expected_response_dict

    use_case = GetNotificationsUseCase(mock_notification_service)
    result = use_case.execute("valid_token")

    mock_notification_service.authenticate_user.assert_called_once_with("valid_token")
    mock_notification_service.get_user_notifications.assert_called_once_with(1)
    mock_create_response.assert_called_once_with(
        "error", 
        expected_message, 
        data=[]
    )
    assert result == expected_response_dict



def teardown_module(module):
    _patch_create_engine.stop()
