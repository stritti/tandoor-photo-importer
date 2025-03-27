import pytest
import sys
import os
from unittest.mock import MagicMock, patch

# Add the parent directory to sys.path to ensure imports work correctly
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Mock the dependencies before importing app
# Use patch instead of monkeypatch to avoid scope issues
mock_ai_service = MagicMock()
mock_ai_providers = MagicMock()
mock_provider_factory = MagicMock()
mock_tandoor_api = MagicMock()

# Apply the mocks to sys.modules
sys.modules['ai_service'] = mock_ai_service
sys.modules['ai_providers'] = mock_ai_providers
sys.modules['ai_providers.provider_factory'] = mock_provider_factory
sys.modules['tandoor_api'] = mock_tandoor_api

# Import app after mocking dependencies
from app import app

@pytest.fixture
def client():
    """Create a test client for the app."""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_health_check(client):
    """Test that the health check endpoint returns 200."""
    response = client.get('/api/health')
    assert response.status_code == 200
    assert response.json == {'status': 'ok'}
