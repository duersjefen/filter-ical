"""
Lambda handler for FastAPI application using Mangum adapter.

This file wraps the FastAPI app for AWS Lambda execution via API Gateway.
"""

from mangum import Mangum
from app.main import app

# Create Lambda handler using Mangum
# Mangum automatically converts API Gateway events to ASGI format
handler = Mangum(app, lifespan="off")  # Disable lifespan for Lambda (managed separately)
