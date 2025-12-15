"""
Root-level Lambda handler wrapper.

This file works around SST's uv workspace module path resolution by providing
a simple entrypoint that imports from the backend package structure.
"""

import sys
import os

# Ensure backend is in Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.app.main import app
from mangum import Mangum

handler = Mangum(app, lifespan="auto")
