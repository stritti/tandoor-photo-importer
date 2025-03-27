import pytest
import sys
import os
from unittest.mock import MagicMock, patch

# Add the parent directory to sys.path to ensure imports work correctly
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Mock the dependencies before importing app
@pytest.fixture(autouse=True, scope="session")
def mock_dependencies(monkeypatch):
    """Mock all external dependencies."""
    # Create mock modules
    mock_ai_service = MagicMock()
    mock_ai_providers = MagicMock()
    mock_provider_factory = MagicMock()
    mock_tandoor_api = MagicMock()
    
    # Add the mocks to sys.modules
    monkeypatch.setitem(sys.modules, 'ai_service', mock_ai_service)
    monkeypatch.setitem(sys.modules, 'ai_providers', mock_ai_providers)
    monkeypatch.setitem(sys.modules, 'ai_providers.provider_factory', mock_provider_factory)
    monkeypatch.setitem(sys.modules, 'tandoor_api', mock_tandoor_api)

# Import app after mocking dependencies
with patch.dict('sys.modules'):
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
