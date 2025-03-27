import pytest
import os

@pytest.fixture(autouse=True)
def setup_test_environment():
    """Set up the test environment."""
    # Create uploads directory if it doesn't exist
    os.makedirs('uploads', exist_ok=True)
    
    # Set environment variables for testing
    os.environ['FLASK_ENV'] = 'testing'
    
    yield
    
    # Clean up after tests if needed
