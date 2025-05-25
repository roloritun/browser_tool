#!/bin/bash
# Health check script for Daytona deployment

API_PORT=${API_PORT:-8000}
HEALTH_URL="http://localhost:${API_PORT}/health"

echo "Checking browser API health at ${HEALTH_URL}"

# Check if the API server is responding
if curl -f -s "${HEALTH_URL}" > /dev/null 2>&1; then
    echo "✅ Browser API is healthy"
    exit 0
else
    echo "❌ Browser API is not responding"
    
    # Check if the process is running
    if pgrep -f "browser_api.main" > /dev/null; then
        echo "📊 Browser API process is running but not responding to health checks"
        exit 1
    else
        echo "💀 Browser API process is not running"
        exit 2
    fi
fi
