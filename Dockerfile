# ---------------------------------------------------------
# Stage 1: Build React Frontend
# ---------------------------------------------------------
FROM node:20-alpine AS frontend-builder
WORKDIR /frontend

COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci

COPY frontend/ ./
RUN npm run build

# ---------------------------------------------------------
# Stage 2: Python Backend Runtime (Hugging Face Spaces)
# ---------------------------------------------------------
FROM python:3.12-slim

WORKDIR /app

# Install curl for container health checks
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Hugging Face Spaces runs as non-root user with UID 1000
RUN useradd -m -u 1000 appuser

COPY backend/requirements.txt .
RUN pip install --no-cache-dir --default-timeout=100 -r requirements.txt

COPY backend/ ./

# Copy compiled React SPA into FastAPI static folder
COPY --from=frontend-builder /frontend/dist/ ./app/static/

# Prepare persistent website cache storage directory with write permissions
RUN mkdir -p /app/app/crawler/cache_storage && \
    chown -R appuser:appuser /app

USER appuser

# Hugging Face Spaces requires port 7860
ENV PORT=7860
EXPOSE 7860

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "7860"]
