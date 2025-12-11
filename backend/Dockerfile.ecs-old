# Multi-stage build for Python backend
# Stage 1: Build dependencies
FROM python:3.13-slim AS builder

WORKDIR /app

# Install build dependencies only
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy only requirements first (cache layer)
COPY requirements.txt .

# Install Python dependencies to user site
RUN pip install --no-cache-dir --user -r requirements.txt

# Stage 2: Test stage (includes test dependencies)
FROM python:3.13-slim AS test

WORKDIR /app

# Copy Python packages from builder
COPY --from=builder /root/.local /root/.local

# Add local Python packages to PATH
ENV PATH=/root/.local/bin:$PATH

# Copy application code
COPY app/ ./app/
COPY openapi.yaml ./
COPY domains/ ./domains/
COPY alembic/ ./alembic/
COPY alembic.ini ./

# Copy tests and run
COPY tests/ ./tests/
RUN python3 -m pytest tests/ -m unit -v

# Stage 3: Production runtime
FROM python:3.13-slim AS production

WORKDIR /app

# Install only runtime dependencies (curl for health checks)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create user first
RUN useradd -m -u 1000 appuser

# Copy Python packages from builder to appuser's home
COPY --from=builder --chown=appuser:appuser /root/.local /home/appuser/.local

# Add local Python packages to PATH
ENV PATH=/home/appuser/.local/bin:$PATH

# Create backward compatibility symlink for platform deploy.sh
# Platform script uses: cd /app/backend && alembic upgrade head
# This symlink makes /app/backend resolve to /app
RUN ln -s /app /app/backend

# Copy application code
COPY --chown=appuser:appuser app/ ./app/
COPY --chown=appuser:appuser openapi.yaml ./
COPY --chown=appuser:appuser domains/ ./domains/
COPY --chown=appuser:appuser alembic/ ./alembic/
COPY --chown=appuser:appuser alembic.ini ./

# Create directories for data persistence
RUN mkdir -p /app/data && chown -R appuser:appuser /app/data

# Switch to non-root user
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:3000/health || exit 1

# Expose port
EXPOSE 3000

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "3000"]
