import pytest
import os
import sys

@pytest.fixture(scope="session", autouse=True)
def setup_path():
    """Add the backend directory to the Python path for all tests."""
    # Add the parent directory to sys.path to allow imports from the backend package
    backend_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir = os.path.dirname(backend_dir)
    
    if backend_dir not in sys.path:
        sys.path.insert(0, backend_dir)
    
    if root_dir not in sys.path:
        sys.path.insert(0, root_dir)
        
    print(f"Python path: {sys.path}")

@pytest.fixture(autouse=True)
def setup_test_environment():
    """Set up the test environment."""
    # Create uploads directory if it doesn't exist
    os.makedirs('uploads', exist_ok=True)
    
    # Set environment variables for testing
    os.environ['FLASK_ENV'] = 'testing'
    
    yield
    
    # Clean up after tests if needed
