#!/bin/bash
# Contract Validation Script
# Mirrors the exact contract validation used in GitHub Actions CI/CD
# Provides perfect parity with production contract testing

set -e  # Exit on any error

echo "📋 Contract Validation (GitHub Actions Parity)"
echo "=============================================="
echo ""
echo "🎯 Running the same contract tests as CI/CD pipeline"
echo "💡 This ensures local validation matches production validation"
echo ""

# Navigate to project root
cd "$(dirname "$0")/.."

# Navigate to backend directory
cd backend

echo "🔧 Building test container (same as GitHub Actions)..."
docker build -t test-backend --target test .

echo ""
echo "🧪 Running Unit Tests (mirrors CI/CD)..."
docker run --rm \
  -e ENV=test \
  -e DATABASE_URL=sqlite:///test.db \
  test-backend python3 -m pytest tests/ -m unit -v --tb=short

echo ""
echo "📋 Running Contract Tests (mirrors CI/CD)..."
docker run --rm \
  -e ENV=test \
  -e DATABASE_URL=sqlite:///test.db \
  test-backend python3 -m pytest tests/test_contracts.py -v --tb=short

echo ""
echo "✅ All contract validations passed!"
echo "🎉 Your code is ready for GitHub Actions deployment"
echo ""
echo "📊 Results summary:"
echo "   ✅ Unit tests passed"
echo "   ✅ Contract tests passed"
echo "   ✅ Same validation as GitHub Actions"
echo ""
echo "🚀 Next steps:"
echo "   1. Commit your changes"
echo "   2. Push to trigger GitHub Actions"
echo "   3. Watch deployment succeed in CI/CD"
echo ""