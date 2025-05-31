#!/bin/bash
# Health check script for Daytona deployment

API_PORT=${API_PORT:-8000}
HEALTH_URL="http://localhost:${API_PORT}/health"

echo "Checking browser API health at ${HEALTH_URL}"

# Check if the API server is responding with timeout
RESPONSE=$(curl -s --max-time 10 "${HEALTH_URL}" 2>/dev/null)
CURL_EXIT_CODE=$?

if [ $CURL_EXIT_CODE -eq 0 ] && [ -n "$RESPONSE" ]; then
    # Check if the response contains success indicator
    if echo "$RESPONSE" | grep -q '"success":true'; then
        echo "✅ Browser API is healthy"
        echo "Response: $RESPONSE"
        exit 0
    else
        echo "⚠️  Browser API responded but status unclear"
        echo "Response: $RESPONSE"
        exit 1
    fi
else
    echo "❌ Browser API is not responding (curl exit code: $CURL_EXIT_CODE)"
    
    # Check if the process is running
    if pgrep -f "browser_api.main" > /dev/null; then
        echo "📊 Browser API process is running but not responding to health checks"
        exit 1
    else
        echo "💀 Browser API process is not running"
        exit 2
    fi
fi
