#!/bin/bash

# Modify the novnc_proxy script to ensure it's properly configured
cat > /Users/rahmanoloritun/browser_tool_daytona/src/sandbox/docker/novnc_proxy_fixed << EOF
#!/usr/bin/env python3

'''
Wrapper script for websockify. Adds a check if the websockify module
is available to run.
'''

import errno
import os
import subprocess
import sys

if __name__ == '__main__':
    # Check to make sure the WebSockets/websockify is available
    here = os.path.dirname(__file__)
    if not os.path.exists(os.path.join(here, 'websockify')):
        sys.stderr.write('Could not find Python websockify module\n')
        sys.exit(errno.ENOENT)
        
    # Run websockify directly with all command line arguments
    argv = [sys.executable, os.path.join(here, 'websockify', 'websocketproxy.py')]
    argv.extend(sys.argv[1:])
    
    try:
        proc = subprocess.Popen(argv, stdout=sys.stdout, stderr=sys.stderr)
        ret = proc.wait()
        sys.exit(ret)
    except KeyboardInterrupt:
        sys.exit(1)
EOF

chmod +x /Users/rahmanoloritun/browser_tool_daytona/src/sandbox/docker/novnc_proxy_fixed
