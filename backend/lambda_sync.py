"""
Lambda sync handler that directly imports from the app package.

This file is a self-contained handler that imports the sync handler
from app.lambda_sync for AWS Lambda execution via EventBridge.
"""

from app.lambda_sync import handler

__all__ = ['handler']
