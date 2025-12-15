"""
Lambda API handler for FastAPI.

This handler uses Mangum to adapt the FastAPI app for AWS Lambda.
"""

from backend.app.main import app
from mangum import Mangum

handler = Mangum(app, lifespan="auto")
