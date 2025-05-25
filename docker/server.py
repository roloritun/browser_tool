from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from starlette.middleware.base import BaseHTTPMiddleware
import uvicorn
import os

# Ensure we're serving from the /workspace directory
workspace_dir = "/workspace"

class WorkspaceDirMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Check if workspace directory exists and recreate if deleted
        if not os.path.exists(workspace_dir):
            print(f"Workspace directory {workspace_dir} not found, recreating...")
            os.makedirs(workspace_dir, exist_ok=True)
        return await call_next(request)

app = FastAPI()
app.add_middleware(WorkspaceDirMiddleware)

# Add health check endpoint
@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "timestamp": os.popen("date").read().strip(),
        "services": {
            "http": True,
            "vnc": os.system("pgrep x11vnc > /dev/null") == 0,
            "novnc": os.system("pgrep novnc_proxy > /dev/null") == 0,
            "xvfb": os.system("pgrep Xvfb > /dev/null") == 0
        }
    }

# Initial directory creation
os.makedirs(workspace_dir, exist_ok=True)
app.mount('/', StaticFiles(directory=workspace_dir, html=True), name='site')

# This is needed for the import string approach with uvicorn
if __name__ == '__main__':
    print(f"Starting server with auto-reload, serving files from: {workspace_dir}")
    # Don't use reload directly in the run call
    port = int(os.environ.get("HTTP_PORT", 8080))
    uvicorn.run("server:app", host="0.0.0.0", port=port, reload=True) 