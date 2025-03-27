# Build-Stage für das Frontend
FROM node:18-alpine AS frontend-build
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

# Finale Stage
FROM python:3.9-slim
WORKDIR /app

# Python-Abhängigkeiten installieren
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Backend-Code kopieren
COPY backend/ ./backend/

# Frontend-Build kopieren
COPY --from=frontend-build /app/dist/frontend ./dist/frontend

# Umgebungsvariablen
ENV FLASK_APP=backend/app.py
ENV FLASK_ENV=production

# Port freigeben
EXPOSE 5000

# Anwendung starten
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "backend.app:app"]
