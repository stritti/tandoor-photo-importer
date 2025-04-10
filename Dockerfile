# Version: 0.2.0
# Build-Stage für das Frontend
FROM node:lts-alpine AS frontend-build
WORKDIR /app/frontend
# Copy only package files first for better caching
COPY frontend/package*.json ./
RUN npm ci
# Then copy the rest of the frontend code
COPY frontend/ ./
RUN npm run build

# Build-Stage für Python dependencies
FROM python:3.13-slim AS python-deps
WORKDIR /app
# Install build dependencies for Python packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*
# Install Python dependencies into a virtual environment
COPY backend/requirements.txt .
RUN python -m venv /opt/venv && \
    /opt/venv/bin/pip install --no-cache-dir --upgrade pip && \
    /opt/venv/bin/pip install --no-cache-dir -r requirements.txt

# Final stage with minimal image
FROM python:3.13-slim
LABEL version="0.2.0"
WORKDIR /app

# Install only runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy Python virtual environment from the build stage
COPY --from=python-deps /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy backend code
COPY backend/ ./backend/

# Copy frontend build
COPY --from=frontend-build /app/frontend/dist ./dist/frontend

# Create uploads directory with proper permissions
RUN mkdir -p uploads && chmod 755 uploads

# Copy .env file if it exists (using a safer approach)
COPY backend/.env /app/backend/.env 2>/dev/null || touch /app/backend/.env

WORKDIR /app/backend

# Environment variables
ENV FLASK_APP=app.py
ENV FLASK_ENV=production
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Port configuration
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:5000/api/health || exit 1

# Create non-root user for security
RUN groupadd -r appuser && useradd -r -g appuser appuser
RUN chown -R appuser:appuser /app
USER appuser

# Start application
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "--threads", "4", "--chdir", "/app/backend", "app:app"]
