#!/bin/bash

# Create workspace directory if it doesn't exist
mkdir -p /workspace

# Copy the index.html to the workspace directory
if [ -f /app/workspace/index.html ]; then
    cp /app/workspace/index.html /workspace/
else
    # Create a simple index.html if one doesn't exist
    cat > /workspace/index.html << EOF
<!DOCTYPE html>
<html>
<head>
    <title>Browser Automation Sandbox</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        h1 { color: #2c3e50; }
        .status { padding: 10px; background-color: #e8f5e9; border-left: 5px solid #4caf50; margin: 10px 0; }
        .links a { display: inline-block; margin: 5px; padding: 8px 15px; text-decoration: none; background-color: #3498db; color: white; border-radius: 4px; }
    </style>
</head>
<body>
    <h1>Browser Automation Sandbox</h1>
    <div class="status">
        <p>All services are running. This environment provides browser automation capabilities with VNC access.</p>
    </div>
    <div class="links">
        <a href="/vnc/" target="_blank">Open noVNC</a>
        <a href="/health" target="_blank">Service Health</a>
    </div>
</body>
</html>
EOF
fi

# Create a symbolic link for noVNC
if [ ! -L "/workspace/vnc" ]; then
    ln -s /opt/novnc /workspace/vnc
fi

# Create a direct noVNC shortcut
cat > /workspace/novnc.html << EOF
<!DOCTYPE html>
<html>
<head>
  <title>Redirecting to noVNC</title>
  <meta http-equiv="refresh" content="0; URL=/vnc/vnc.html?autoconnect=true&resize=scale&quality=9">
</head>
<body>
  <p>Redirecting to noVNC...</p>
  <p>If you are not redirected, <a href="/vnc/vnc.html?autoconnect=true&resize=scale&quality=9">click here</a>.</p>
</body>
</html>
EOF

# Create a simple startup complete flag
touch /workspace/.startup_complete
