# Dockerfile (API Service)

# ═══════════════════════════════════════════════════════════════
# BASE IMAGE
# ═══════════════════════════════════════════════════════════════
FROM python:3.12-slim as base

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# ═══════════════════════════════════════════════════════════════
# DEPENDENCIES
# ═══════════════════════════════════════════════════════════════
FROM base as dependencies

COPY services/api/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ═══════════════════════════════════════════════════════════════
# PRODUCTION
# ═══════════════════════════════════════════════════════════════
FROM dependencies as production

COPY services/api/app ./app

# Create non-root user
RUN adduser --disabled-password --gecos '' appuser
USER appuser

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
