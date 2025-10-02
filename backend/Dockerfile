# Backend Dockerfile for Python + FastAPI
FROM python:3.11-slim AS base

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create backward compatibility symlink for platform deploy.sh
# Platform script uses: cd /app/backend && alembic upgrade head
# This symlink makes /app/backend resolve to /app
RUN ln -s /app /app/backend

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app/ ./app/

# Copy OpenAPI specification and domains configuration
COPY openapi.yaml ./
COPY domains/ ./domains/

# Copy Alembic migration files
COPY alembic/ ./alembic/
COPY alembic.ini ./

# Test stage
FROM base AS test
COPY tests/ ./tests/
RUN python3 -m pytest tests/ -m unit -v

# Production stage
FROM base AS production

# Create directories for data persistence
RUN mkdir -p /app/data

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:3000/health || exit 1

# Expose port
EXPOSE 3000

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "3000"]