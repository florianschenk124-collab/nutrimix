# ════════════════════════════════════════════════════════════════
# NutrientMixer – Production Dockerfile
# Stage 1: Build React frontend
# Stage 2: Run Python API + serve static files
# ════════════════════════════════════════════════════════════════

# ── Stage 1: Frontend Build ───────────────────────────────────
FROM node:20-slim AS frontend-build

WORKDIR /app/frontend
COPY frontend/package.json frontend/package-lock.json* ./
RUN npm ci --no-audit 2>/dev/null || npm install --no-audit
COPY frontend/ ./
RUN npm run build


# ── Stage 2: Python API ───────────────────────────────────────
FROM python:3.12-slim

WORKDIR /app

# Python deps
COPY requirements-web.txt ./
RUN pip install --no-cache-dir -r requirements-web.txt

# App-Code
COPY chemistry/ ./chemistry/
COPY database/ ./database/
COPY ui/__init__.py ui/locales.py ./ui/
COPY api/ ./api/
COPY server.py ./

# Gebautes Frontend als static/ einbinden
COPY --from=frontend-build /app/frontend/dist ./static/

# user_data Verzeichnis für Runtime-Daten
RUN mkdir -p user_data

# Port (Railway setzt $PORT automatisch)
ENV PORT=8000
EXPOSE 8000

# Start
CMD uvicorn api.main:app --host 0.0.0.0 --port ${PORT}
