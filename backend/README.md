# Tandoor Photo Importer Backend

This is the backend service for the Tandoor Photo Importer application. It provides API endpoints for image upload, AI analysis, and Tandoor recipe import functionality.

## Setup

1. Copy `.env.example` to `.env` and configure your environment variables
2. Install dependencies: `pip install -r requirements.txt`
3. Run the application: `flask run`

## Testing

The backend uses pytest for testing. To run the tests:

```bash
# Run all tests
pytest

# Run tests with verbose output
pytest -v

# Run a specific test file
pytest test_app.py

# Run a specific test function
pytest test_app.py::test_health_check

# Run tests with coverage report
pytest --cov=.
```

Make sure you have pytest installed: `pip install pytest pytest-cov`

## API Endpoints

- `GET /api/health`: Health check endpoint
- `POST /api/upload-image`: Upload and optionally analyze an image
- `POST /api/tandoor-auth`: Authenticate with Tandoor
- `POST /api/extract-json-ld`: Extract JSON-LD from AI response
- `POST /api/import-to-tandoor`: Import a recipe to Tandoor
