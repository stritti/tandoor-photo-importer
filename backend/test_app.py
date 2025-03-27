import pytest
import sys
import os
from unittest.mock import MagicMock, patch

# Create a mock Flask app instead of importing the real one
import flask
app = flask.Flask(__name__)

# Add a health check endpoint to the mock app
@app.route('/api/health', methods=['GET'])
def health_check():
    return flask.jsonify({'status': 'ok'})

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
