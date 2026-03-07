#!/bin/bash
set -e

# Start the FastAPI backend
cd /app
uvicorn backend.app.main:app \
    --host 0.0.0.0 \
    --port 8000 \
    --workers ${SERVER_WORKERS:-2} &

# Wait for backend to be ready
echo "Waiting for backend to start..."
for i in $(seq 1 30); do
    if curl -sf http://localhost:8000/api/health > /dev/null 2>&1; then
        echo "Backend is ready!"
        break
    fi
    sleep 1
done

# Start nginx in foreground
nginx -g "daemon off;"
