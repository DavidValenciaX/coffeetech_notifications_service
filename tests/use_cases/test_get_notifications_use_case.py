from unittest.mock import patch, MagicMock, PropertyMock
import pytest
from datetime import datetime

# Patch sqlalchemy.create_engine before other project imports
_patch_create_engine = patch('sqlalchemy.create_engine', return_value=MagicMock())
_patch_create_engine.start()

from use_cases.get_notifications_use_case import get_notifications
from models.models import Notifications # This is the actual SQLAlchemy model
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

# Test for invalid session token
@patch('use_cases.get_notifications_use_case.verify_session_token')
@patch('use_cases.get_notifications_use_case.session_token_invalid_response')
def test_get_notifications_invalid_token(mock_session_token_invalid_response, mock_verify_session_token, mock_db_session):
    mock_verify_session_token.return_value = None
    expected_response = {"status": "error", "message": "Token inválido"}
    mock_session_token_invalid_response.return_value = expected_response

    result = get_notifications("invalid_token", mock_db_session)

    mock_verify_session_token.assert_called_once_with("invalid_token")
    mock_session_token_invalid_response.assert_called_once()
    assert result == expected_response

# Test for valid token, user has notifications
@patch('use_cases.get_notifications_use_case.verify_session_token')
@patch('use_cases.get_notifications_use_case.create_response')
def test_get_notifications_valid_token_with_notifications(mock_create_response, mock_verify_session_token, mock_db_session, mock_notification_type, mock_notification_state):
    mock_user = {'user_id': 1, 'name': 'Test User'}
    mock_verify_session_token.return_value = mock_user

    mock_notif1_date = datetime.utcnow()
    mock_notif1 = MagicMock(spec=Notifications)
    mock_notif1.notification_id = 1
    mock_notif1.message = "Test message 1"
    mock_notif1.notification_date = mock_notif1_date 
    mock_notif1.invitation_id = 101
    mock_notif1.notification_type = mock_notification_type 
    mock_notif1.state = mock_notification_state 
    
    mock_db_session.query.return_value.filter.return_value.all.return_value = [mock_notif1]
    
    expected_data = [
        NotificationResponse(
            notification_id=1,
            message="Test message 1",
            notification_date=mock_notif1_date.isoformat(), 
            invitation_id=101,
            notification_type="TestType",
            notification_state="TestState"
        ).model_dump()
    ]
    
    # Consistent with the prompt's example for this test case for create_response call
    expected_message = "Notificaciones obtenidas exitosamente."
    expected_response_dict = {"status": "success", "message": expected_message, "data": expected_data}
    # Set the return value for the mock_create_response
    mock_create_response.return_value = expected_response_dict


    result = get_notifications("valid_token", mock_db_session)

    mock_verify_session_token.assert_called_once_with("valid_token")
    mock_db_session.query.assert_called_once_with(Notifications)
    mock_create_response.assert_called_once_with(
        "success", 
        expected_message, 
        data=expected_data
    )
    assert result == expected_response_dict

# Test for valid token, user has no notifications
@patch('use_cases.get_notifications_use_case.verify_session_token')
@patch('use_cases.get_notifications_use_case.create_response')
def test_get_notifications_valid_token_no_notifications(mock_create_response, mock_verify_session_token, mock_db_session):
    mock_user = {'user_id': 1, 'name': 'Test User'}
    mock_verify_session_token.return_value = mock_user

    mock_db_session.query.return_value.filter.return_value.all.return_value = []
    
    # Consistent with the prompt's example for this test case
    expected_message = "No hay notificaciones para este usuario."
    # The prompt's example for the final assert had "No hay notificaciones", I'm using the one from create_response call.
    expected_response_dict = {"status": "success", "message": expected_message, "data": []}
    mock_create_response.return_value = expected_response_dict


    result = get_notifications("valid_token", mock_db_session)

    mock_verify_session_token.assert_called_once_with("valid_token")
    mock_db_session.query.assert_called_once_with(Notifications)
    mock_create_response.assert_called_once_with(
        "success", 
        expected_message, 
        data=[]
    )
    assert result == expected_response_dict

# Test for valid token, serialization error
@patch('use_cases.get_notifications_use_case.verify_session_token')
@patch('use_cases.get_notifications_use_case.create_response')
def test_get_notifications_serialization_error(mock_create_response, mock_verify_session_token, mock_db_session, mock_notification_state):
    mock_user = {'user_id': 1, 'name': 'Test User'}
    mock_verify_session_token.return_value = mock_user

    mock_notif_broken_date = datetime.utcnow()
    mock_notif_broken = MagicMock(spec=Notifications) 
    mock_notif_broken.notification_id = 1
    mock_notif_broken.message = "Test message broken"
    mock_notif_broken.notification_date = mock_notif_broken_date 
    mock_notif_broken.invitation_id = 101
    
    mock_notif_broken.notification_type = FaultyType() # This will raise AttributeError("Simulated error") on .name access
    mock_notif_broken.state = mock_notification_state 

    mock_db_session.query.return_value.filter.return_value.all.return_value = [mock_notif_broken]
    
    # As per prompt's example for assert_called_once_with for this test case
    # This implies the use case formats the message as "Error de serialización: {exception_message}"
    expected_message = "Error de serialización: Simulated error"
    expected_response_dict = {"status": "error", "message": expected_message, "data":[]}
    mock_create_response.return_value = expected_response_dict


    result = get_notifications("valid_token", mock_db_session)

    mock_verify_session_token.assert_called_once_with("valid_token")
    mock_db_session.query.assert_called_once_with(Notifications)
    mock_create_response.assert_called_once_with(
        "error", 
        expected_message, 
        data=[]
    )
    assert result == expected_response_dict

def teardown_module(module):
    _patch_create_engine.stop()
