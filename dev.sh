#!/usr/bin/env bash
# Manual development server (workaround for SST dev mode issues)

set -e

echo "🚀 Starting Filter-iCal development servers..."

# Get DATABASE_URL from SST
echo "📊 Getting database connection from SST..."
export DATABASE_URL=$(npx sst shell --stage staging -- bash -c 'echo $DATABASE_URL')

if [ -z "$DATABASE_URL" ]; then
  echo "❌ Error: Could not get DATABASE_URL from SST"
  exit 1
fi

echo "✅ Database URL retrieved"

# Start backend in background
echo "🐍 Starting backend on port 3000..."
cd backend && . venv/bin/activate && DATABASE_URL="$DATABASE_URL" uvicorn app.main:app --reload --host 0.0.0.0 --port 3000 &
BACKEND_PID=$!

# Start frontend in background
echo "⚡ Starting frontend on port 5173..."
cd ../frontend && VITE_API_BASE_URL=http://localhost:3000 npm run dev &
FRONTEND_PID=$!

# Trap to cleanup on exit
trap "echo '🛑 Stopping servers...'; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null" EXIT

echo ""
echo "✅ Development servers started!"
echo "   Frontend: http://localhost:5173"
echo "   Backend:  http://localhost:3000"
echo "   Database: Staging RDS"
echo ""
echo "Press Ctrl+C to stop all servers"

# Wait for both processes
wait
