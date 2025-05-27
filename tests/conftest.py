import pytest
from unittest.mock import MagicMock

@pytest.fixture
def mock_db_session():
    session = MagicMock()
    return session
