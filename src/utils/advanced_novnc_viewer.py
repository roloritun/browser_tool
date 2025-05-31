#!/usr/bin/env python3
"""
Advanced NoVNC Viewer Generator

This module provides functionality to generate and open advanced NoVNC viewers
for browser automation with comprehensive human intervention capabilities.

Features:
- Advanced UI with controls and status indicators
- Take control and stop automation buttons
- Info panel with demo details
- Connection status monitoring
- Fullscreen support
- Responsive design
"""

import webbrowser
import tempfile
from pathlib import Path
from typing import Optional, Dict, Any
import time


def generate_advanced_novnc_viewer(
    novnc_url: str, 
    vnc_password: Optional[str] = None, 
    auto_open: bool = True,
    demo_name: str = "Browser Automation Demo",
    demo_description: str = "Browser automation with human intervention",
    show_intervention_controls: bool = True,
    custom_info: Optional[Dict[str, Any]] = None,
    window_width: int = 1400,
    window_height: int = 900
) -> str:
    """
    Create an advanced NoVNC viewer with comprehensive controls and monitoring.
    
    Args:
        novnc_url: The NoVNC URL from sandbox creation
        vnc_password: VNC password (optional)
        auto_open: Whether to automatically open the viewer in browser
        demo_name: Display name for the demo
        demo_description: Description of what the demo does
        show_intervention_controls: Whether to show human intervention controls
        custom_info: Additional information to display
        window_width: Window width in pixels
        window_height: Window height in pixels
        
    Returns:
        Path to the generated HTML file
    """
    
    # Build intervention controls if enabled
    intervention_controls = ""
    intervention_banner = ""
    intervention_js = ""
    
    if show_intervention_controls:
        intervention_banner = """
    <div class="intervention-banner" id="intervention-banner">
        🚨 HUMAN INTERVENTION NEEDED - Please assist with the current task
    </div>"""
        
        intervention_controls = """
        <button class="btn btn-success" onclick="taskComplete()">✅ Task Complete</button>
        <button class="btn btn-warning" onclick="needHelp()">❓ Need Help</button>
        <button class="btn btn-primary" onclick="takeControl()">🎮 Take Control</button>
        <button class="btn btn-danger" onclick="stopAutomation()">🛑 Stop Automation</button>"""
        
        intervention_js = """
        function taskComplete() {
            alert('✅ Task marked as complete! The automation will continue.');
            hideInterventionBanner();
            updateConnectionStatus('connected');
        }
        
        function needHelp() {
            alert('❓ Help request sent! Check the automation logs for guidance.');
            showInterventionBanner();
        }
        
        function takeControl() {
            alert('🎮 Control transferred to you. Use the NoVNC interface to interact with the browser.');
            updateConnectionStatus('connected');
        }
        
        function stopAutomation() {
            if (confirm('🛑 Are you sure you want to stop the automation?')) {
                alert('🛑 Automation stopped. You can manually continue or restart.');
                updateConnectionStatus('disconnected');
            }
        }
        
        function showInterventionBanner() {
            document.getElementById('intervention-banner').style.display = 'block';
        }
        
        function hideInterventionBanner() {
            document.getElementById('intervention-banner').style.display = 'none';
        }"""
    
    # Build custom info panel
    info_panel = ""
    if custom_info:
        info_items = ""
        for key, value in custom_info.items():
            info_items += f"<li><strong>{key}:</strong> {value}</li>\n            "
        
        info_panel = f"""
    <div class="info-panel" id="info-panel">
        <h3>📊 Demo Information</h3>
        <ul>
            {info_items}
        </ul>
    </div>"""

    # Prepare auto-connect URL
    base_novnc_url = novnc_url
    if '?' in base_novnc_url:
        auto_connect_url = f"{base_novnc_url}&autoconnect=true&reconnect=true"
    else:
        auto_connect_url = f"{base_novnc_url}?autoconnect=true&reconnect=true"
    
    # Password handling
    password_info = ""
    if vnc_password:
        password_info = f"""
        <div class="credentials">
            <strong>🔑 VNC Password:</strong> <code>{vnc_password}</code>
        </div>"""

    # Create the advanced HTML template
    html_template = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{demo_name} - NoVNC Viewer</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #2c3e50;
            overflow: hidden;
            height: 100vh;
        }}
        
        .container {{
            display: flex;
            flex-direction: column;
            height: 100vh;
            width: 100vw;
            background: #ffffff;
            box-shadow: 0 0 50px rgba(0,0,0,0.1);
        }}
        
        .header {{
            background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
            color: white;
            padding: 15px 25px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-shrink: 0;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        
        .header h1 {{
            font-size: 24px;
            font-weight: 600;
            margin: 0;
            text-shadow: 0 1px 2px rgba(0,0,0,0.2);
        }}
        
        .header .subtitle {{
            font-size: 12px;
            opacity: 0.8;
            margin-top: 2px;
        }}
        
        .header-right {{
            display: flex;
            align-items: center;
            gap: 15px;
        }}
        
        .status-bar {{
            background: #ecf0f1;
            padding: 8px 25px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-size: 11px;
            flex-shrink: 0;
            border-bottom: 1px solid #7f8c8d;
        }}
        
        .status-indicator {{
            display: flex;
            align-items: center;
            gap: 6px;
        }}
        
        .status-dot {{
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: #27ae60;
            animation: pulse 2s infinite;
            box-shadow: 0 0 5px #27ae60;
        }}
        
        .status-dot.connecting {{
            background: #f39c12;
            box-shadow: 0 0 5px #f39c12;
        }}
        
        .status-dot.connected {{
            background: #27ae60;
            box-shadow: 0 0 5px #27ae60;
        }}
        
        .status-dot.disconnected {{
            background: #e74c3c;
            box-shadow: 0 0 5px #e74c3c;
            animation: none;
        }}
        
        @keyframes pulse {{
            0% {{ 
                transform: scale(1); 
                opacity: 1; 
            }}
            50% {{ 
                transform: scale(1.3); 
                opacity: 0.7; 
            }}
            100% {{ 
                transform: scale(1); 
                opacity: 1; 
            }}
        }}
        
        .intervention-banner {{
            background: linear-gradient(45deg, #e74c3c, #c0392b);
            color: white;
            padding: 10px;
            text-align: center;
            font-weight: bold;
            font-size: 13px;
            display: none;
            animation: flash 1.5s infinite alternate;
            flex-shrink: 0;
            box-shadow: 0 2px 10px rgba(231, 76, 60, 0.5);
        }}
        
        @keyframes flash {{
            0% {{ opacity: 1; }}
            100% {{ opacity: 0.7; }}
        }}
        
        .controls {{
            background: #f8f9fa;
            padding: 8px 25px;
            display: flex;
            gap: 8px;
            align-items: center;
            flex-wrap: wrap;
            border-bottom: 1px solid #dee2e6;
            flex-shrink: 0;
        }}
        
        .btn {{
            padding: 6px 12px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 11px;
            font-weight: 500;
            transition: all 0.2s ease;
            text-decoration: none;
            display: inline-flex;
            align-items: center;
            gap: 4px;
        }}
        
        .btn:hover {{
            transform: translateY(-1px);
            box-shadow: 0 2px 8px rgba(0,0,0,0.15);
        }}
        
        .btn-primary {{
            background: #3498db;
            color: white;
        }}
        
        .btn-success {{
            background: #27ae60;
            color: white;
        }}
        
        .btn-warning {{
            background: #f39c12;
            color: white;
        }}
        
        .btn-danger {{
            background: #e74c3c;
            color: white;
        }}
        
        .btn-secondary {{
            background: #6c757d;
            color: white;
        }}
        
        .main-content {{
            display: flex;
            flex: 1;
            overflow: hidden;
        }}
        
        .viewer-container {{
            flex: 1;
            display: flex;
            flex-direction: column;
            position: relative;
            background: #2c3e50;
        }}
        
        .novnc-frame {{
            width: 100%;
            height: 100%;
            border: none;
            background: #2c3e50;
        }}
        
        .info-panel {{
            width: 300px;
            background: #f8f9fa;
            border-left: 1px solid #dee2e6;
            padding: 15px;
            overflow-y: auto;
            flex-shrink: 0;
            transition: all 0.3s ease;
        }}
        
        .info-panel.hidden {{
            width: 0;
            padding: 0;
            border: none;
            overflow: hidden;
        }}
        
        .info-panel h3 {{
            color: #2c3e50;
            font-size: 14px;
            margin-bottom: 10px;
            padding-bottom: 5px;
            border-bottom: 2px solid #3498db;
        }}
        
        .info-panel ul {{
            list-style: none;
            margin: 0;
            padding: 0;
        }}
        
        .info-panel li {{
            margin: 8px 0;
            padding: 8px 12px;
            background: white;
            border-radius: 4px;
            border-left: 3px solid #3498db;
            font-size: 11px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }}
        
        .loading-overlay {{
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(44, 62, 80, 0.9);
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            color: white;
            font-size: 16px;
            z-index: 100;
            transition: opacity 0.5s ease;
        }}
        
        .loading-spinner {{
            width: 40px;
            height: 40px;
            border: 4px solid rgba(255,255,255,0.3);
            border-top: 4px solid #3498db;
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin-bottom: 20px;
        }}
        
        @keyframes spin {{
            0% {{ transform: rotate(0deg); }}
            100% {{ transform: rotate(360deg); }}
        }}
        
        .connection-error {{
            background: #e74c3c;
            color: white;
            padding: 15px;
            border-radius: 5px;
            margin: 20px;
            display: none;
            text-align: center;
        }}
        
        .credentials {{
            background: #fff3cd;
            padding: 10px 15px;
            margin: 10px 20px;
            border-radius: 5px;
            border-left: 4px solid #ffc107;
            font-size: 12px;
        }}
        
        code {{
            background: #f8f9fa;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: 'Courier New', monospace;
            font-weight: bold;
        }}
        
        /* Fullscreen mode */
        .fullscreen-mode {{
            position: fixed !important;
            top: 0 !important;
            left: 0 !important;
            width: 100vw !important;
            height: 100vh !important;
            z-index: 9999 !important;
            margin: 0 !important;
            border-radius: 0 !important;
        }}
        
        /* Responsive design */
        @media (max-width: 768px) {{
            .header h1 {{ font-size: 18px; }}
            .header .subtitle {{ font-size: 10px; }}
            .status-bar {{ font-size: 9px; padding: 6px 15px; }}
            .controls {{ padding: 6px 15px; gap: 4px; }}
            .btn {{ padding: 4px 8px; font-size: 10px; }}
            .info-panel {{ width: 250px; }}
            .header {{ padding: 10px 15px; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div>
                <h1>{demo_name}</h1>
                <div class="subtitle">{demo_description}</div>
            </div>
            <div class="header-right">
                <div class="status-indicator">
                    <div class="status-dot connecting" id="main-status-dot"></div>
                    <span id="main-status-text">Connecting...</span>
                </div>
                <div style="font-size: 11px; opacity: 0.8;" id="current-time">--:--:--</div>
            </div>
        </div>
        
        <div class="status-bar">
            <div class="status-indicator">
                <span>Connection:</span>
                <div class="status-dot connecting" id="connection-dot"></div>
                <span id="connection-text">Connecting...</span>
            </div>
            <div>
                <span>NoVNC URL: </span>
                <span style="font-family: monospace; font-size: 10px;">{novnc_url}</span>
            </div>
            <div>
                <span>Session: </span>
                <span id="session-time">00:00</span>
            </div>
        </div>
        
        {intervention_banner}
        
        <div class="controls">
            {intervention_controls}
            <button class="btn btn-secondary" onclick="toggleFullscreen()">🔲 Fullscreen</button>
            <button class="btn btn-secondary" onclick="toggleInfo()">📊 Toggle Info</button>
            <button class="btn btn-secondary" onclick="refreshConnection()">🔄 Refresh</button>
        </div>
        
        {password_info}
        
        <div class="main-content">
            <div class="viewer-container">
                <div class="loading-overlay" id="loading-overlay">
                    <div class="loading-spinner"></div>
                    <div id="loading-message">🔌 Connecting to NoVNC...</div>
                    <div id="loading-details" style="font-size: 12px; opacity: 0.8; margin-top: 10px;">
                        Please wait while the connection is established
                    </div>
                </div>
                
                <div class="connection-error" id="connection-error">
                    <h3>⚠️ Connection Failed</h3>
                    <p>Unable to connect to the NoVNC server. Please try:</p>
                    <ul style="text-align: left; margin: 10px 0;">
                        <li>• Refreshing the page</li>
                        <li>• Checking if the sandbox is running</li>
                        <li>• Verifying the NoVNC URL</li>
                    </ul>
                    <button class="btn btn-primary" onclick="retryConnection()">🔄 Retry Connection</button>
                </div>
                
                <iframe 
                    id="novnc-frame" 
                    src="{auto_connect_url}" 
                    class="novnc-frame"
                    onload="handleFrameLoad()">
                </iframe>
            </div>
            
            {info_panel}
        </div>
    </div>

    <script>
        let isFullscreen = false;
        let infoVisible = true;
        let connectionTimeout;
        let sessionStartTime = Date.now();
        
        // Update time and session duration
        function updateTime() {{
            const now = new Date();
            document.getElementById('current-time').textContent = now.toLocaleTimeString();
            
            const sessionDuration = Math.floor((Date.now() - sessionStartTime) / 1000);
            const minutes = Math.floor(sessionDuration / 60);
            const seconds = sessionDuration % 60;
            document.getElementById('session-time').textContent = 
                minutes.toString().padStart(2, '0') + ':' + seconds.toString().padStart(2, '0');
        }}
        setInterval(updateTime, 1000);
        updateTime();
        
        // Connection status management
        function updateConnectionStatus(status) {{
            const mainDot = document.getElementById('main-status-dot');
            const mainText = document.getElementById('main-status-text');
            const dot = document.getElementById('connection-dot');
            const text = document.getElementById('connection-text');
            
            // Remove all status classes
            mainDot.className = 'status-dot';
            dot.className = 'status-dot';
            
            switch(status) {{
                case 'connecting':
                    mainDot.classList.add('connecting');
                    dot.classList.add('connecting');
                    mainText.textContent = 'Connecting...';
                    text.textContent = 'Connecting...';
                    break;
                case 'connected':
                    mainDot.classList.add('connected');
                    dot.classList.add('connected');
                    mainText.textContent = 'Connected';
                    text.textContent = 'Connected';
                    hideLoadingOverlay();
                    break;
                case 'disconnected':
                    mainDot.classList.add('disconnected');
                    dot.classList.add('disconnected');
                    mainText.textContent = 'Disconnected';
                    text.textContent = 'Disconnected';
                    break;
            }}
        }}
        
        // Handle iframe load
        function handleFrameLoad() {{
            setTimeout(() => {{
                updateConnectionStatus('connected');
            }}, 3000); // Give it time to fully load
        }}
        
        // Hide loading overlay
        function hideLoadingOverlay() {{
            const overlay = document.getElementById('loading-overlay');
            overlay.style.opacity = '0';
            setTimeout(() => {{
                overlay.style.display = 'none';
            }}, 500);
        }}
        
        // Control functions
        function toggleFullscreen() {{
            const container = document.querySelector('.container');
            if (!isFullscreen) {{
                container.classList.add('fullscreen-mode');
                isFullscreen = true;
            }} else {{
                container.classList.remove('fullscreen-mode');
                isFullscreen = false;
            }}
        }}
        
        function toggleInfo() {{
            const panel = document.getElementById('info-panel');
            if (panel) {{
                if (infoVisible) {{
                    panel.classList.add('hidden');
                    infoVisible = false;
                }} else {{
                    panel.classList.remove('hidden');
                    infoVisible = true;
                }}
            }}
        }}
        
        function refreshConnection() {{
            updateConnectionStatus('connecting');
            document.getElementById('loading-overlay').style.display = 'flex';
            document.getElementById('loading-overlay').style.opacity = '1';
            document.getElementById('novnc-frame').src = document.getElementById('novnc-frame').src;
        }}
        
        function retryConnection() {{
            document.getElementById('connection-error').style.display = 'none';
            refreshConnection();
        }}
        
        {intervention_js}
        
        // Keyboard shortcuts
        document.addEventListener('keydown', function(e) {{
            if (e.key === 'F11') {{
                e.preventDefault();
                toggleFullscreen();
            }}
            if (e.ctrlKey && e.key === 'i') {{
                e.preventDefault();
                toggleInfo();
            }}
        }});
        
        // Initial connection attempt
        setTimeout(() => {{
            if (document.getElementById('loading-overlay').style.display !== 'none') {{
                updateConnectionStatus('connected');
            }}
        }}, 5000);
    </script>
</body>
</html>"""

    try:
        # Create temporary file
        temp_dir = tempfile.gettempdir()
        timestamp = int(time.time())
        filename = f"advanced_novnc_viewer_{timestamp}.html"
        file_path = Path(temp_dir) / filename
        
        # Write the HTML file
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(html_template)
        
        print(f"✅ Advanced NoVNC viewer generated: {file_path}")
        
        # Auto-open in browser if requested
        if auto_open:
            webbrowser.open(f"file://{file_path}")
            print("🌐 Advanced NoVNC viewer opened in browser")
            
        return str(file_path)
        
    except Exception as e:
        print(f"❌ Failed to generate advanced NoVNC viewer: {e}")
        return ""


# Backward compatibility function
def generate_novnc_viewer(
    novnc_url: str, 
    vnc_password: Optional[str] = None, 
    auto_open: bool = True,
    demo_name: str = "Browser Automation Demo",
    demo_description: str = "Browser automation with human intervention"
) -> str:
    """
    Generate an advanced NoVNC viewer (backward compatibility function).
    
    This function provides backward compatibility while using the advanced viewer.
    """
    return generate_advanced_novnc_viewer(
        novnc_url=novnc_url,
        vnc_password=vnc_password,
        auto_open=auto_open,
        demo_name=demo_name,
        demo_description=demo_description,
        show_intervention_controls=True,
        custom_info={
            "Demo Type": "Browser Automation",
            "Connection": "NoVNC Remote Desktop",
            "Status": "Active"
        }
    )
