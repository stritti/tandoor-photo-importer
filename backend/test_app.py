import pytest
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
