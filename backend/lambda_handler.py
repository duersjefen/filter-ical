"""
Lambda handler for FastAPI application using Mangum adapter.

This file is a self-contained handler that directly imports the FastAPI app
and wraps it with Mangum for AWS Lambda execution via API Gateway.

The lifespan is enabled to run startup logic (database seeding, domain setup).
APScheduler is automatically disabled via IS_LAMBDA environment variable.
"""

from mangum import Mangum
from .app.main import app

# Create Lambda handler using Mangum
# Mangum automatically converts API Gateway events to ASGI format
# Lifespan is enabled for startup tasks (APScheduler disabled via IS_LAMBDA env var)
handler = Mangum(app, lifespan="auto")
