#!/bin/bash
# Automated Python backend setup for SST dev mode
# This script is idempotent - safe to run multiple times

set -e  # Exit on error

BACKEND_DIR="backend"
VENV_DIR="$BACKEND_DIR/venv"

echo "🔍 Checking Python backend setup..."

# Check if venv exists
if [ ! -d "$VENV_DIR" ]; then
  echo "📦 Python venv not found. Setting up backend..."

  # Check Python version
  if ! command -v python3 &> /dev/null; then
    echo "❌ Error: python3 not found. Please install Python 3.11+"
    exit 1
  fi

  PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
  echo "✓ Found Python $PYTHON_VERSION"

  # Create virtual environment
  echo "→ Creating virtual environment..."
  cd "$BACKEND_DIR"
  python3 -m venv venv

  # Activate and install dependencies
  echo "→ Installing dependencies..."
  . venv/bin/activate
  pip install --quiet --upgrade pip
  pip install --quiet -e .

  cd ..
  echo "✅ Backend setup complete!"
else
  echo "✅ Backend venv exists - skipping setup"
fi

echo ""
