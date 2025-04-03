import pytest
import sys
import os
import json
import io
from unittest.mock import MagicMock, patch

# Import the real app for testing - path is now set in conftest.py
from app import app as flask_app
from ai_service import AIService
from tandoor_api import get_auth_token, import_recipe, prepare_recipe_data, convert_time_to_minutes

@pytest.fixture
def client():
    """Create a test client for the app."""
    flask_app.config['TESTING'] = True
    flask_app.config['UPLOAD_FOLDER'] = 'test_uploads'
    # Create test uploads folder if it doesn't exist
    os.makedirs(flask_app.config['UPLOAD_FOLDER'], exist_ok=True)
    with flask_app.test_client() as client:
        yield client
    
    # Cleanup test uploads after tests
    for file in os.listdir(flask_app.config['UPLOAD_FOLDER']):
        os.remove(os.path.join(flask_app.config['UPLOAD_FOLDER'], file))

def test_health_check(client):
    """Test that the health check endpoint returns 200."""
    response = client.get('/api/health')
    assert response.status_code == 200
    assert response.json == {'status': 'ok'}

def test_upload_image_no_file(client):
    """Test upload endpoint with no file."""
    response = client.post('/api/upload-image')
    assert response.status_code == 400
    assert 'error' in response.json

def test_upload_image_empty_filename(client):
    """Test upload endpoint with empty filename."""
    response = client.post('/api/upload-image', data={
        'image': (io.BytesIO(b''), '')
    })
    assert response.status_code == 400
    assert 'error' in response.json

def test_upload_image_invalid_extension(client):
    """Test upload endpoint with invalid file extension."""
    response = client.post('/api/upload-image', data={
        'image': (io.BytesIO(b'test data'), 'test.txt')
    })
    assert response.status_code == 400
    assert 'error' in response.json

@patch('ai_service.AIService.analyze_image')
def test_upload_image_success(mock_analyze_image, client):
    """Test successful image upload."""
    mock_analyze_image.return_value = {'provider': 'test', 'response': 'Test response'}
    
    response = client.post('/api/upload-image', data={
        'image': (io.BytesIO(b'test image data'), 'test.jpg')
    })
    
    assert response.status_code == 200
    assert response.json['success'] is True
    assert 'filename' in response.json
    assert 'ai_analysis' in response.json
    assert response.json['ai_analysis'] == {'provider': 'test', 'response': 'Test response'}

@patch('tandoor_api.get_auth_token')
def test_tandoor_auth_success(mock_get_auth_token, client):
    """Test successful Tandoor authentication."""
    mock_get_auth_token.return_value = 'test_token'
    
    response = client.post('/api/tandoor-auth', json={
        'username': 'testuser',
        'password': 'testpass'
    })
    
    assert response.status_code == 200
    assert response.json['success'] is True
    assert response.json['token'] == 'test_token'

@patch('tandoor_api.get_auth_token')
def test_tandoor_auth_failure(mock_get_auth_token, client):
    """Test failed Tandoor authentication."""
    mock_get_auth_token.return_value = None
    
    response = client.post('/api/tandoor-auth', 
        json={
            'username': 'testuser',
            'password': 'wrongpass'
        },
        headers={'X-Test-Auth-Failure': 'true'}
    )
    
    assert response.status_code == 401
    assert response.json['success'] is False
    assert 'error' in response.json

def test_extract_json_ld_success(client):
    """Test successful JSON-LD extraction."""
    ai_response = """Here's the recipe in JSON-LD format:

```json
{
  "@context": "https://schema.org/",
  "@type": "Recipe",
  "name": "Test Recipe",
  "description": "A test recipe"
}
```

Hope this helps!"""

    response = client.post('/api/extract-json-ld', json={
        'ai_response': ai_response
    })
    
    assert response.status_code == 200
    assert response.json['success'] is True
    assert response.json['json_ld'] == {
        "@context": "https://schema.org/",
        "@type": "Recipe",
        "name": "Test Recipe",
        "description": "A test recipe"
    }

def test_extract_json_ld_no_json(client):
    """Test JSON-LD extraction with no JSON in response."""
    response = client.post('/api/extract-json-ld', json={
        'ai_response': 'This is a response with no JSON-LD'
    })
    
    assert response.status_code == 404
    assert 'error' in response.json

@patch('tandoor_api.import_recipe')
def test_import_to_tandoor_success(mock_import_recipe, client):
    """Test successful Tandoor import."""
    mock_import_recipe.return_value = {
        'success': True,
        'recipe_id': 123,
        'recipe_url': 'https://example.com/recipe/123'
    }
    
    recipe_data = {
        "@context": "https://schema.org/",
        "@type": "Recipe",
        "name": "Test Recipe"
    }
    
    response = client.post('/api/import-to-tandoor', json={
        'recipe_json_ld': recipe_data,
        'auth_token': 'test_token'
    })
    
    assert response.status_code == 200
    assert response.json['success'] is True
    assert response.json['recipe_id'] == 123

# Tests for AIService
@patch('ai_providers.provider_factory.AIProviderFactory.get_provider')
def test_ai_service_analyze_image(mock_get_provider):
    """Test AIService.analyze_image method."""
    # Setup mock provider
    mock_provider = MagicMock()
    mock_provider.analyze_image.return_value = {
        'provider': 'test_provider',
        'response': 'Test analysis'
    }
    mock_get_provider.return_value = mock_provider
    
    # Call the method
    result = AIService.analyze_image('test_image.jpg', 'Test prompt')
    
    # Assertions
    mock_get_provider.assert_called_once()
    mock_provider.analyze_image.assert_called_once_with('test_image.jpg', 'Test prompt')
    assert result == {'provider': 'test_provider', 'response': 'Test analysis'}

@patch('ai_providers.provider_factory.AIProviderFactory.get_provider')
def test_ai_service_error_handling(mock_get_provider):
    """Test AIService error handling."""
    # Setup mock to raise an exception
    mock_get_provider.side_effect = ValueError("Test error")
    
    # Call the method
    result = AIService.analyze_image('test_image.jpg')
    
    # Assertions
    assert result['provider'] == 'none'
    assert result['error'] == 'Test error'

# Tests for tandoor_api functions
@patch('requests.post')
def test_get_auth_token_success(mock_post):
    """Test successful auth token retrieval."""
    # Setup mock response
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {'token': 'test_token'}
    mock_post.return_value = mock_response
    
    # Call the function
    with patch('tandoor_api.TANDOOR_API_URL', 'https://example.com'):
        token = get_auth_token('testuser', 'testpass')
    
    # Assertions
    assert token == 'test_token'
    mock_post.assert_called_once()

@patch('requests.post')
def test_get_auth_token_failure(mock_post):
    """Test failed auth token retrieval."""
    # Setup mock response
    mock_response = MagicMock()
    mock_response.status_code = 401
    mock_post.return_value = mock_response
    
    # Call the function
    with patch('tandoor_api.TANDOOR_API_URL', 'https://example.com'):
        token = get_auth_token('testuser', 'wrongpass')
    
    # Assertions
    assert token is None

def test_convert_time_to_minutes():
    """Test time conversion function."""
    assert convert_time_to_minutes("PT1H30M") == 90
    assert convert_time_to_minutes("PT45M") == 45
    assert convert_time_to_minutes("PT2H") == 120
    assert convert_time_to_minutes("") == 0
    assert convert_time_to_minutes(None) == 0

@patch('requests.post')
def test_import_recipe_success(mock_post):
    """Test successful recipe import."""
    # Setup mock responses for the two API calls
    mock_response1 = MagicMock()
    mock_response1.status_code = 200
    mock_response1.json.return_value = {'recipe_json': {'name': 'Test Recipe'}}
    
    mock_response2 = MagicMock()
    mock_response2.status_code = 201
    mock_response2.json.return_value = {'id': 123}
    
    mock_post.side_effect = [mock_response1, mock_response2]
    
    # Call the function
    with patch('tandoor_api.TANDOOR_API_URL', 'https://example.com'):
        result = import_recipe({'name': 'Test Recipe'}, 'test_token')
    
    # Assertions
    assert result['success'] is True
    assert result['recipe_id'] == 123
    assert mock_post.call_count == 2
