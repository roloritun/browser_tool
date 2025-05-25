#!/bin/bash
# This file should be placed in the workspace directory to redirect to noVNC
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

# Create a file indicating successful setup
touch /workspace/.novnc_ready
