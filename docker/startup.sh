#!/bin/bash

# Log function with timestamp
log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1"
}

# Handle errors and cleanup on exit
handle_exit() {
    log "Container is shutting down..."
    pkill -P $$ || true
    exit 0
}

# Set up error handling
trap handle_exit SIGTERM SIGINT

# Configure default environment variables with fallbacks for Daytona compatibility
export RESOLUTION="${RESOLUTION:-1920x1080x24}"
export DISPLAY="${DISPLAY:-:99}"
export VNC_PORT="${VNC_PORT:-5901}"
export NOVNC_PORT="${NOVNC_PORT:-6080}"
export HTTP_PORT="${HTTP_PORT:-8080}"
export RESOLUTION_WIDTH="${RESOLUTION_WIDTH:-1920}"
export RESOLUTION_HEIGHT="${RESOLUTION_HEIGHT:-1080}"

log "Starting container with configuration:"
log "- DISPLAY: $DISPLAY"
log "- RESOLUTION: $RESOLUTION"
log "- VNC_PORT: $VNC_PORT"
log "- NOVNC_PORT: $NOVNC_PORT"
log "- HTTP_PORT: $HTTP_PORT"

# Create required directories with proper permissions for root user
log "Setting up required directories..."
mkdir -p /var/log/supervisor /var/run/supervisor /var/log/vnc /tmp/.X11-unix
chmod 755 /var/log/supervisor /var/run/supervisor /var/log/vnc 2>/dev/null || true
chmod 1777 /tmp/.X11-unix 2>/dev/null || true

# Check if noVNC proxy is executable and fix if needed
log "Verifying noVNC configuration..."
# Fix permissions on websockify files
if [ -d /opt/novnc/utils/websockify ]; then
    find /opt/novnc/utils/websockify -name "*.py" -exec chmod +x {} \; 2>/dev/null || true
    if [ -f /opt/novnc/utils/websockify/run ]; then
        chmod +x /opt/novnc/utils/websockify/run 2>/dev/null || true
        log "Fixed permissions on websockify/run script"
    fi
    log "Fixed permissions on websockify Python files"
else
    log "WARNING: websockify directory not found at /opt/novnc/utils/websockify"
fi

# Initialize workspace
log "Initializing workspace..."
/app/workspace_init.sh

# Set up passwordless VNC
log "Configuring passwordless VNC access..."
mkdir -p /root/.vnc
# Empty password file for passwordless access
touch /root/.vnc/passwd
chmod 600 /root/.vnc/passwd

# Create VNC config with security settings for passwordless access
cat > /root/.vnc/config << EOF
SecurityTypes=None
DotWhenNoCursor=1
EOF

# Set up X11 environment
touch /root/.Xauthority
xauth -f /root/.Xauthority generate $DISPLAY . trusted 2>/dev/null || true

# Check ports availability
check_port() {
    if ! netstat -tuln | grep -q ":$1 "; then
        return 0
    else
        log "WARNING: Port $1 is already in use. Service might not start correctly."
        return 1
    fi
}

log "Checking ports availability..."
for port in $VNC_PORT $NOVNC_PORT $HTTP_PORT; do
    check_port $port
done

# Create a symbolic link for noVNC access
if [ ! -e "/workspace" ]; then
    mkdir -p /workspace
fi

if [ ! -L "/workspace/vnc" ]; then
    ln -sf /opt/novnc /workspace/vnc
fi

# Start supervisord as the main process
log "Starting all services via supervisord..."
exec /usr/bin/supervisord -n -c /etc/supervisor/conf.d/supervisord.conf