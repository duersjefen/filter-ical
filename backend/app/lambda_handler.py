"""
Lambda handler for FastAPI application using Mangum adapter.

This file wraps the FastAPI app for AWS Lambda execution via API Gateway.
Uses relative imports since it's inside the app package.
"""

from mangum import Mangum
from .main import app

# Create Lambda handler using Mangum
handler = Mangum(app, lifespan="auto")
