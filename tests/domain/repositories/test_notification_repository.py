import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime
import pytz
from adapters.persistence.notification_repository import NotificationRepository
from models.models import Notifications, NotificationStates, NotificationTypes


class TestNotificationRepository:
    """Test suite for NotificationRepository"""
    
    @pytest.fixture
    def mock_db_session(self):
        """Create a mock database session"""
        return MagicMock()
    
    @pytest.fixture
    def notification_repository(self, mock_db_session):
        """Create a NotificationRepository instance with mocked database"""
        return NotificationRepository(mock_db_session)
    
    @pytest.fixture
    def sample_notification(self):
        """Create a sample notification object"""
        notification = MagicMock(spec=Notifications)
        notification.notification_id = 1
        notification.message = "Test notification"
        notification.user_id = 123
        notification.invitation_id = 456
        notification.notification_type_id = 1
        notification.notification_state_id = 1
        notification.notification_date = datetime.now(pytz.timezone("America/Bogota"))
        return notification
    
    @pytest.fixture
    def sample_notification_state(self):
        """Create a sample notification state object"""
        state = MagicMock(spec=NotificationStates)
        state.notification_state_id = 1
        state.name = "Unread"
        return state
    
    @pytest.fixture
    def sample_notification_type(self):
        """Create a sample notification type object"""
        type_obj = MagicMock(spec=NotificationTypes)
        type_obj.notification_type_id = 1
        type_obj.name = "Invitation"
        return type_obj

    def test_get_notifications_by_user_id_success(self, notification_repository, mock_db_session, sample_notification):
        """Test successful retrieval of notifications by user ID"""
        # Arrange
        user_id = 123
        expected_notifications = [sample_notification]
        mock_db_session.query.return_value.filter.return_value.all.return_value = expected_notifications
        
        # Act
        result = notification_repository.get_notifications_by_user_id(user_id)
        
        # Assert
        assert result == expected_notifications
        mock_db_session.query.assert_called_once_with(Notifications)
        mock_db_session.query.return_value.filter.assert_called_once()
        mock_db_session.query.return_value.filter.return_value.all.assert_called_once()

    def test_get_notifications_by_user_id_empty_result(self, notification_repository, mock_db_session):
        """Test retrieval of notifications by user ID when no notifications exist"""
        # Arrange
        user_id = 999
        mock_db_session.query.return_value.filter.return_value.all.return_value = []
        
        # Act
        result = notification_repository.get_notifications_by_user_id(user_id)
        
        # Assert
        assert result == []
        mock_db_session.query.assert_called_once_with(Notifications)

    def test_get_all_notification_states_success(self, notification_repository, mock_db_session, sample_notification_state):
        """Test successful retrieval of all notification states"""
        # Arrange
        expected_states = [sample_notification_state]
        mock_db_session.query.return_value.all.return_value = expected_states
        
        # Act
        result = notification_repository.get_all_notification_states()
        
        # Assert
        assert result == expected_states
        mock_db_session.query.assert_called_once_with(NotificationStates)
        mock_db_session.query.return_value.all.assert_called_once()

    def test_get_all_notification_states_empty_result(self, notification_repository, mock_db_session):
        """Test retrieval of all notification states when none exist"""
        # Arrange
        mock_db_session.query.return_value.all.return_value = []
        
        # Act
        result = notification_repository.get_all_notification_states()
        
        # Assert
        assert result == []
        mock_db_session.query.assert_called_once_with(NotificationStates)

    def test_get_all_notification_types_success(self, notification_repository, mock_db_session, sample_notification_type):
        """Test successful retrieval of all notification types"""
        # Arrange
        expected_types = [sample_notification_type]
        mock_db_session.query.return_value.all.return_value = expected_types
        
        # Act
        result = notification_repository.get_all_notification_types()
        
        # Assert
        assert result == expected_types
        mock_db_session.query.assert_called_once_with(NotificationTypes)
        mock_db_session.query.return_value.all.assert_called_once()

    def test_get_all_notification_types_empty_result(self, notification_repository, mock_db_session):
        """Test retrieval of all notification types when none exist"""
        # Arrange
        mock_db_session.query.return_value.all.return_value = []
        
        # Act
        result = notification_repository.get_all_notification_types()
        
        # Assert
        assert result == []
        mock_db_session.query.assert_called_once_with(NotificationTypes)

    def test_get_all_notifications_success(self, notification_repository, mock_db_session, sample_notification):
        """Test successful retrieval of all notifications"""
        # Arrange
        expected_notifications = [sample_notification]
        mock_db_session.query.return_value.all.return_value = expected_notifications
        
        # Act
        result = notification_repository.get_all_notifications()
        
        # Assert
        assert result == expected_notifications
        mock_db_session.query.assert_called_once_with(Notifications)
        mock_db_session.query.return_value.all.assert_called_once()

    def test_get_all_notifications_empty_result(self, notification_repository, mock_db_session):
        """Test retrieval of all notifications when none exist"""
        # Arrange
        mock_db_session.query.return_value.all.return_value = []
        
        # Act
        result = notification_repository.get_all_notifications()
        
        # Assert
        assert result == []
        mock_db_session.query.assert_called_once_with(Notifications)

    def test_get_notification_by_invitation_success(self, notification_repository, mock_db_session, 
                                                   sample_notification, sample_notification_type):
        """Test successful retrieval of notification by invitation ID"""
        # Arrange
        invitation_id = 456
        mock_query = MagicMock()
        mock_db_session.query.return_value = mock_query
        
        # Mock the first query for notification type
        mock_query.filter.return_value.first.side_effect = [sample_notification_type, sample_notification]
        
        # Act
        result = notification_repository.get_notification_by_invitation(invitation_id)
        
        # Assert
        assert result == sample_notification
        assert mock_db_session.query.call_count == 2  # Called twice: for type and notification

    def test_get_notification_by_invitation_no_type_found(self, notification_repository, mock_db_session):
        """Test retrieval of notification by invitation ID when notification type doesn't exist"""
        # Arrange
        invitation_id = 456
        mock_query = MagicMock()
        mock_db_session.query.return_value = mock_query
        mock_query.filter.return_value.first.return_value = None
        
        # Act
        result = notification_repository.get_notification_by_invitation(invitation_id)
        
        # Assert
        assert result is None
        mock_db_session.query.assert_called_once_with(NotificationTypes)

    def test_get_notification_by_invitation_no_notification_found(self, notification_repository, mock_db_session, 
                                                                 sample_notification_type):
        """Test retrieval of notification by invitation ID when notification doesn't exist"""
        # Arrange
        invitation_id = 456
        mock_query = MagicMock()
        mock_db_session.query.return_value = mock_query
        mock_query.filter.return_value.first.side_effect = [sample_notification_type, None]
        
        # Act
        result = notification_repository.get_notification_by_invitation(invitation_id)
        
        # Assert
        assert result is None
        assert mock_db_session.query.call_count == 2

    def test_delete_notifications_by_invitation_success(self, notification_repository, mock_db_session, 
                                                       sample_notification_type):
        """Test successful deletion of notifications by invitation ID"""
        # Arrange
        invitation_id = 456
        mock_notifications = [MagicMock(), MagicMock()]  # Two notifications to delete
        
        mock_query = MagicMock()
        mock_db_session.query.return_value = mock_query
        mock_query.filter.return_value.first.return_value = sample_notification_type
        mock_query.filter.return_value.all.return_value = mock_notifications
        
        # Act
        result = notification_repository.delete_notifications_by_invitation(invitation_id)
        
        # Assert
        assert result == 2
        assert mock_db_session.delete.call_count == 2
        mock_db_session.commit.assert_called_once()

    def test_delete_notifications_by_invitation_no_type_found(self, notification_repository, mock_db_session):
        """Test deletion when invitation notification type doesn't exist"""
        # Arrange
        invitation_id = 456
        mock_query = MagicMock()
        mock_db_session.query.return_value = mock_query
        mock_query.filter.return_value.first.return_value = None
        
        # Act
        result = notification_repository.delete_notifications_by_invitation(invitation_id)
        
        # Assert
        assert result == 0
        mock_db_session.delete.assert_not_called()
        mock_db_session.commit.assert_not_called()

    def test_delete_notifications_by_invitation_no_notifications_found(self, notification_repository, mock_db_session, 
                                                                      sample_notification_type):
        """Test deletion when no notifications exist for the invitation"""
        # Arrange
        invitation_id = 456
        mock_query = MagicMock()
        mock_db_session.query.return_value = mock_query
        mock_query.filter.return_value.first.return_value = sample_notification_type
        mock_query.filter.return_value.all.return_value = []
        
        # Act
        result = notification_repository.delete_notifications_by_invitation(invitation_id)
        
        # Assert
        assert result == 0
        mock_db_session.delete.assert_not_called()
        mock_db_session.commit.assert_not_called()

    def test_update_notification_state_success(self, notification_repository, mock_db_session, sample_notification):
        """Test successful update of notification state"""
        # Arrange
        notification_id = 1
        new_state_id = 2
        mock_query = MagicMock()
        mock_db_session.query.return_value = mock_query
        mock_query.filter.return_value.first.return_value = sample_notification
        
        # Act
        result = notification_repository.update_notification_state(notification_id, new_state_id)
        
        # Assert
        assert result == sample_notification
        assert sample_notification.notification_state_id == new_state_id
        mock_db_session.commit.assert_called_once()

    def test_update_notification_state_notification_not_found(self, notification_repository, mock_db_session):
        """Test update of notification state when notification doesn't exist"""
        # Arrange
        notification_id = 999
        new_state_id = 2
        mock_query = MagicMock()
        mock_db_session.query.return_value = mock_query
        mock_query.filter.return_value.first.return_value = None
        
        # Act
        result = notification_repository.update_notification_state(notification_id, new_state_id)
        
        # Assert
        assert result is None
        mock_db_session.commit.assert_not_called()

    @patch('adapters.persistence.notification_repository.datetime')
    @patch('adapters.persistence.notification_repository.pytz')
    def test_create_notification_success(self, mock_pytz, mock_datetime, notification_repository, mock_db_session):
        """Test successful creation of a new notification"""
        # Arrange
        message = "Test notification"
        user_id = 123
        notification_type_id = 1
        invitation_id = 456
        notification_state_id = 1
        
        mock_timezone = MagicMock()
        mock_pytz.timezone.return_value = mock_timezone
        mock_now = datetime(2023, 1, 1, 12, 0, 0)
        mock_datetime.now.return_value = mock_now
        
        # Act
        result = notification_repository.create_notification(
            message, user_id, notification_type_id, invitation_id, notification_state_id
        )
        
        # Assert
        mock_db_session.add.assert_called_once()
        mock_db_session.commit.assert_called_once()
        mock_pytz.timezone.assert_called_once_with("America/Bogota")
        mock_datetime.now.assert_called_once_with(mock_timezone)
        
        # Verify the notification object was created with correct parameters
        added_notification = mock_db_session.add.call_args[0][0]
        assert added_notification.message == message
        assert added_notification.user_id == user_id
        assert added_notification.notification_type_id == notification_type_id
        assert added_notification.invitation_id == invitation_id
        assert added_notification.notification_state_id == notification_state_id
        assert added_notification.notification_date == mock_now
        
        # Verify the returned notification is the same as the one added
        assert result == added_notification

    def test_get_notification_by_id_success(self, notification_repository, mock_db_session, sample_notification):
        """Test successful retrieval of notification by ID"""
        # Arrange
        notification_id = 1
        mock_query = MagicMock()
        mock_db_session.query.return_value = mock_query
        mock_query.filter.return_value.first.return_value = sample_notification
        
        # Act
        result = notification_repository.get_notification_by_id(notification_id)
        
        # Assert
        assert result == sample_notification
        mock_db_session.query.assert_called_once_with(Notifications)
        mock_query.filter.assert_called_once()
        mock_query.filter.return_value.first.assert_called_once()

    def test_get_notification_by_id_not_found(self, notification_repository, mock_db_session):
        """Test retrieval of notification by ID when notification doesn't exist"""
        # Arrange
        notification_id = 999
        mock_query = MagicMock()
        mock_db_session.query.return_value = mock_query
        mock_query.filter.return_value.first.return_value = None
        
        # Act
        result = notification_repository.get_notification_by_id(notification_id)
        
        # Assert
        assert result is None
        mock_db_session.query.assert_called_once_with(Notifications)

    def test_repository_initialization(self, mock_db_session):
        """Test that the repository is properly initialized with a database session"""
        # Act
        repository = NotificationRepository(mock_db_session)
        
        # Assert
        assert repository.db == mock_db_session

    def test_delete_notifications_by_invitation_database_error(self, notification_repository, mock_db_session, 
                                                              sample_notification_type):
        """Test deletion when database error occurs during commit"""
        # Arrange
        invitation_id = 456
        mock_notifications = [MagicMock()]
        
        mock_query = MagicMock()
        mock_db_session.query.return_value = mock_query
        mock_query.filter.return_value.first.return_value = sample_notification_type
        mock_query.filter.return_value.all.return_value = mock_notifications
        mock_db_session.commit.side_effect = Exception("Database error")
        
        # Act & Assert
        with pytest.raises(Exception, match="Database error"):
            notification_repository.delete_notifications_by_invitation(invitation_id)

    def test_update_notification_state_database_error(self, notification_repository, mock_db_session, sample_notification):
        """Test update notification state when database error occurs during commit"""
        # Arrange
        notification_id = 1
        new_state_id = 2
        mock_query = MagicMock()
        mock_db_session.query.return_value = mock_query
        mock_query.filter.return_value.first.return_value = sample_notification
        mock_db_session.commit.side_effect = Exception("Database error")
        
        # Act & Assert
        with pytest.raises(Exception, match="Database error"):
            notification_repository.update_notification_state(notification_id, new_state_id)

    def test_create_notification_database_error(self, notification_repository, mock_db_session):
        """Test create notification when database error occurs during commit"""
        # Arrange
        message = "Test notification"
        user_id = 123
        notification_type_id = 1
        invitation_id = 456
        notification_state_id = 1
        mock_db_session.commit.side_effect = Exception("Database error")
        
        # Act & Assert
        with pytest.raises(Exception, match="Database error"):
            notification_repository.create_notification(
                message, user_id, notification_type_id, invitation_id, notification_state_id
            ) 