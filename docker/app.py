"""
Main Flask application for the browser automation tool.
This provides RESTful API endpoints for browser automation using Playwright.
"""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import logging
from browser_api.flask_wrapper import BrowserAutomationAPI

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)
CORS(app)

# Initialize browser automation API
browser_api = BrowserAutomationAPI()

# Register the browser API blueprint
app.register_blueprint(browser_api.get_blueprint(), url_prefix='/api/browser')

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "browser_automation_flask_api",
        "version": "1.0.0"
    })

@app.route('/')
def index():
    """Root endpoint with API information"""
    return jsonify({
        "service": "Browser Automation Tool",
        "version": "1.0.0",
        "description": "A complete browser automation tool with VNC interface and programmatic control via Playwright",
        "endpoints": {
            "health": "/health",
            "api_base": "/api/browser",
            "vnc_interface": "http://localhost:6080",
            "available_routes": [
                "POST /api/browser/sessions - Create new browser session",
                "GET /api/browser/sessions - List active sessions",
                "DELETE /api/browser/sessions/<session_id> - Close session",
                "POST /api/browser/navigate - Navigate to URL",
                "POST /api/browser/click - Click elements",
                "POST /api/browser/type - Type text into elements",
                "GET /api/browser/screenshot - Take screenshots",
                "GET /api/browser/content - Extract page content"
            ]
        }
    })

@app.route('/workspace')
@app.route('/workspace/<path:filename>')
def serve_workspace(filename=''):
    """Serve files from the workspace directory"""
    workspace_dir = '/workspace'
    if filename:
        return send_from_directory(workspace_dir, filename)
    else:
        # List workspace contents
        try:
            files = os.listdir(workspace_dir)
            return jsonify({"workspace_files": files})
        except Exception as e:
            return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Get port from environment variable or default to 8080
    port = int(os.environ.get('FLASK_PORT', 8080))
    debug = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    
    logger.info(f"Starting Flask application on port {port}")
    app.run(host='0.0.0.0', port=port, debug=debug)
