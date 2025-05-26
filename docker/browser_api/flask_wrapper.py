"""
Flask wrapper for browser automation API.
This module provides a Flask-compatible wrapper around the browser automation functionality.
"""

import asyncio
import logging
from flask import Blueprint, request, jsonify
from browser_api.core.browser_automation import BrowserAutomation
from browser_api.actions.navigation import NavigationActions
from browser_api.actions.interaction import InteractionActions
from browser_api.actions.content import ContentActions

logger = logging.getLogger(__name__)

class BrowserAutomationAPI:
    """Flask wrapper for browser automation functionality"""
    
    def __init__(self):
        self.browser_automation = BrowserAutomation()
        self.loop = None
        self._sessions = {}
        
    def get_blueprint(self):
        """Get Flask blueprint with all browser automation routes"""
        bp = Blueprint('browser_api', __name__)
        
        @bp.route('/sessions', methods=['POST'])
        def create_session():
            """Create new browser session"""
            try:
                # Run async function in sync context
                result = self._run_async(self._create_session())
                return jsonify(result)
            except Exception as e:
                logger.error(f"Error creating session: {e}")
                return jsonify({"error": str(e)}), 500
        
        @bp.route('/sessions', methods=['GET'])
        def list_sessions():
            """List active sessions"""
            return jsonify({
                "sessions": list(self._sessions.keys()),
                "count": len(self._sessions)
            })
        
        @bp.route('/sessions/<session_id>', methods=['DELETE'])
        def close_session(session_id):
            """Close session"""
            if session_id in self._sessions:
                del self._sessions[session_id]
                return jsonify({"message": f"Session {session_id} closed"})
            return jsonify({"error": "Session not found"}), 404
        
        @bp.route('/navigate', methods=['POST'])
        def navigate():
            """Navigate to URL"""
            try:
                data = request.get_json()
                url = data.get('url')
                if not url:
                    return jsonify({"error": "URL is required"}), 400
                
                action = {"url": url}
                result = self._run_async(NavigationActions.navigate_to(self.browser_automation, action))
                return jsonify(result)
            except Exception as e:
                logger.error(f"Error navigating: {e}")
                return jsonify({"error": str(e)}), 500
        
        @bp.route('/click', methods=['POST'])
        def click():
            """Click elements"""
            try:
                data = request.get_json()
                selector = data.get('selector')
                if not selector:
                    return jsonify({"error": "Selector is required"}), 400
                
                action = {"selector": selector}
                result = self._run_async(InteractionActions.click_element(self.browser_automation, action))
                return jsonify(result)
            except Exception as e:
                logger.error(f"Error clicking: {e}")
                return jsonify({"error": str(e)}), 500
        
        @bp.route('/type', methods=['POST'])
        def type_text():
            """Type text into elements"""
            try:
                data = request.get_json()
                selector = data.get('selector')
                text = data.get('text')
                if not selector or not text:
                    return jsonify({"error": "Selector and text are required"}), 400
                
                action = {"selector": selector, "text": text}
                result = self._run_async(InteractionActions.input_text(self.browser_automation, action))
                return jsonify(result)
            except Exception as e:
                logger.error(f"Error typing: {e}")
                return jsonify({"error": str(e)}), 500
        
        @bp.route('/screenshot', methods=['GET'])
        def screenshot():
            """Take screenshots"""
            try:
                result = self._run_async(self._take_screenshot())
                return jsonify(result)
            except Exception as e:
                logger.error(f"Error taking screenshot: {e}")
                return jsonify({"error": str(e)}), 500
        
        @bp.route('/content', methods=['GET'])
        def content():
            """Extract page content"""
            try:
                action = {"type": "text"}
                result = self._run_async(ContentActions.extract_content(self.browser_automation, action))
                return jsonify(result)
            except Exception as e:
                logger.error(f"Error extracting content: {e}")
                return jsonify({"error": str(e)}), 500
        
        return bp
    
    def _run_async(self, coro):
        """Run async function in sync context"""
        try:
            # Try to get existing event loop
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # If loop is running, we need to use a different approach
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(asyncio.run, coro)
                    return future.result()
            else:
                return loop.run_until_complete(coro)
        except RuntimeError:
            # No event loop in current thread
            return asyncio.run(coro)
    
    async def _create_session(self):
        """Create new browser session"""
        if not self.browser_automation.browser:
            await self.browser_automation.startup()
        
        session_id = f"session_{len(self._sessions) + 1}"
        self._sessions[session_id] = True
        
        return {
            "session_id": session_id,
            "status": "created",
            "browser_ready": self.browser_automation.browser is not None
        }
    
    async def _take_screenshot(self):
        """Take screenshot"""
        if not self.browser_automation.browser:
            await self.browser_automation.startup()
        
        if self.browser_automation.pages:
            page = self.browser_automation.pages[self.browser_automation.current_page_index]
            screenshot_path = f"/app/screenshots/screenshot_{len(self._sessions)}.png"
            await page.screenshot(path=screenshot_path)
            return {
                "screenshot_path": screenshot_path,
                "status": "success"
            }
        else:
            return {
                "error": "No active page",
                "status": "error"
            }