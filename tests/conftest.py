import pytest
from unittest.mock import MagicMock

@pytest.fixture
def mock_db_session():
    session = MagicMock()
    # Add any specific mock configurations needed globally, for example:
    # session.query.return_value.filter.return_value.first.return_value = None
    # session.commit = MagicMock()
    # session.add = MagicMock()
    # session.delete = MagicMock()
    # session.rollback = MagicMock()
    return session
