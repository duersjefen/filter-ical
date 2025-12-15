"""
Lambda sync handler that directly imports from the app package.

This file is a self-contained handler that imports the sync handler
from app.lambda_sync for AWS Lambda execution via EventBridge.
"""

import sys
import os

# Add backend directory to Python path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.lambda_sync import handler

__all__ = ['handler']
