# tandoor-photo-importer

Extension for Tandoor receipe app to import hand written receipes by shooting a photo of them.

## Development Setup

### Prerequisites
- Docker and Docker Compose installed
- Node.js and npm (for local frontend development without Docker)
- Python 3.9+ (for local backend development without Docker)

### Running with Docker Compose (Recommended)
The easiest way to start both frontend and backend services is using Docker Compose:

```bash
# Start both services
docker-compose up

# Frontend will be available at: http://localhost:8080
# Backend API will be available at: http://localhost:5000
```

### Running Frontend Locally
If you want to run just the frontend locally:

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start development server
npm start
```

The frontend will be available at http://localhost:8080 and will proxy API requests to the backend.

### Running Backend Locally
To run just the backend locally:

```bash
# Navigate to backend directory
cd backend

# Create and activate a virtual environment (optional but recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start the Flask server
flask run
```

The backend API will be available at http://localhost:5000.

### Running Backend Tests
The backend uses pytest for testing:

```bash
# Navigate to backend directory
cd backend

# Run all tests
pytest

# Run tests with verbose output
pytest -v

# Run tests with coverage report
pytest --cov=.
```

Make sure you have pytest and pytest-cov installed:
```bash
pip install pytest pytest-cov
```

