# ============================================================================
# Sentinel XAI — Multi-stage Dockerfile
# Stage 1: Build frontend (React + Vite)
# Stage 2: Production image (Python + FastAPI + built frontend)
# ============================================================================

# ── Stage 1: Frontend build ──────────────────────────────────────────────────
FROM node:20-alpine AS frontend-builder

WORKDIR /app/frontend

# Install dependencies first (layer cache)
COPY frontend/package*.json ./
RUN npm ci --silent

# Copy source and build
COPY frontend/ ./
ARG VITE_API_URL=http://localhost:8000
ENV VITE_API_URL=$VITE_API_URL
RUN npm run build


# ── Stage 2: Production image ────────────────────────────────────────────────
FROM python:3.11-slim AS production

# Metadata
LABEL maintainer="NUST Dept. of Informatics"
LABEL description="Sentinel XAI — Student Mental Health Risk Monitor"
LABEL version="1.0.0"

# Prevent Python from writing .pyc files and enable unbuffered logs
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV ENVIRONMENT=production

WORKDIR /app

# ── System dependencies ───────────────────────────────────────────────────────
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    nginx \
    supervisor \
    && rm -rf /var/lib/apt/lists/*

# ── Python dependencies ───────────────────────────────────────────────────────
COPY backend/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# ── Copy backend source ───────────────────────────────────────────────────────
COPY backend/           ./backend/
COPY generate_real_dataset.py ./
COPY data_preprocessing.py    ./
COPY model_training.py        ./
COPY model_evaluation.py      ./
COPY shap_generation.py       ./

# ── Copy built frontend into nginx html dir ───────────────────────────────────
COPY --from=frontend-builder /app/frontend/dist /usr/share/nginx/html

# ── Create required directories ────────────────────────────────────────────────
RUN mkdir -p \
    backend/data \
    data/raw \
    data/processed \
    models \
    plots \
    reports

# ── Nginx config: serve frontend + proxy /api to FastAPI ─────────────────────
RUN cat > /etc/nginx/sites-available/default << 'NGINX'
server {
    listen 80;
    server_name _;

    # Serve React frontend
    root /usr/share/nginx/html;
    index index.html;

    # Frontend routes — fall back to index.html for SPA routing
    location / {
        try_files $uri $uri/ /index.html;
    }

    # Proxy all API calls to FastAPI
    location /api/ {
        proxy_pass         http://127.0.0.1:8000/;
        proxy_http_version 1.1;
        proxy_set_header   Upgrade $http_upgrade;
        proxy_set_header   Connection "upgrade";
        proxy_set_header   Host $host;
        proxy_set_header   X-Real-IP $remote_addr;
        proxy_set_header   X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_read_timeout 300s;
        proxy_send_timeout 300s;
    }

    # WebSocket proxy
    location /ws {
        proxy_pass         http://127.0.0.1:8000/ws;
        proxy_http_version 1.1;
        proxy_set_header   Upgrade $http_upgrade;
        proxy_set_header   Connection "Upgrade";
        proxy_set_header   Host $host;
    }

    # Health check endpoint
    location /health {
        proxy_pass http://127.0.0.1:8000/health;
    }
}
NGINX

# ── Supervisor config: run nginx + uvicorn together ──────────────────────────
RUN cat > /etc/supervisor/conf.d/sentinel.conf << 'SUPERVISOR'
[supervisord]
nodaemon=true
logfile=/var/log/supervisor/supervisord.log
pidfile=/var/run/supervisord.pid

[program:nginx]
command=/usr/sbin/nginx -g "daemon off;"
autostart=true
autorestart=true
stdout_logfile=/var/log/nginx/access.log
stderr_logfile=/var/log/nginx/error.log

[program:fastapi]
command=uvicorn server:app --host 127.0.0.1 --port 8000 --workers 1 --log-level info
directory=/app/backend
autostart=true
autorestart=true
stdout_logfile=/var/log/supervisor/fastapi.log
stderr_logfile=/var/log/supervisor/fastapi-error.log
environment=PYTHONPATH="/app/backend",SECRET_KEY="%(ENV_SECRET_KEY)s",ENVIRONMENT="%(ENV_ENVIRONMENT)s"
SUPERVISOR

# ── Startup script: generate data + train model on first run ─────────────────
RUN cat > /app/startup.sh << 'STARTUP'
#!/bin/bash
set -e

echo "=============================================="
echo "  Sentinel XAI — Container Startup"
echo "=============================================="

# Generate dataset if not present
if [ ! -f /app/backend/data/students.csv ]; then
    echo "[STARTUP] Generating student dataset..."
    cd /app && python generate_real_dataset.py --n ${NUM_STUDENTS:-1200} --seed ${DATA_SEED:-42}
fi

# Run preprocessing if model not trained
if [ ! -f /app/models/xgboost_model.pkl ]; then
    echo "[STARTUP] Running preprocessing..."
    cd /app && python data_preprocessing.py

    echo "[STARTUP] Training ML model..."
    cd /app && python model_training.py
fi

echo "[STARTUP] Starting services..."
exec /usr/bin/supervisord -c /etc/supervisor/supervisord.conf
STARTUP

RUN chmod +x /app/startup.sh

# ── Expose ports ──────────────────────────────────────────────────────────────
# Port 80:   nginx (serves frontend + proxies API)
# Port 8000: FastAPI directly (optional, for debugging)
EXPOSE 80 8000

# ── Health check ──────────────────────────────────────────────────────────────
HEALTHCHECK --interval=30s --timeout=10s --start-period=120s --retries=3 \
    CMD curl -sf http://localhost/health || exit 1

# ── Entrypoint ────────────────────────────────────────────────────────────────
ENTRYPOINT ["/app/startup.sh"]
