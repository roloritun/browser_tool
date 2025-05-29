"""
Advanced NoVNC Viewer Utility

This module provides functionality to create and open advanced HTML viewers for NoVNC interfaces
during browser automation demos with comprehensive human intervention capabilities.

Features:
- Advanced UI with controls and status indicators
- Take control and stop automation buttons
- Info panel with demo details
- Connection status monitoring
- Fullscreen support
- Responsive design
"""

import webbrowser
from pathlib import Path
from .advanced_novnc_viewer import generate_advanced_novnc_viewer
from typing import Optional


def generate_novnc_viewer(
    novnc_url: str, 
    vnc_password: Optional[str] = None, 
    auto_open: bool = True,
    demo_name: str = "Browser Automation Demo",
    demo_description: str = "Browser automation with human intervention"
) -> str:
    """
    Generate an advanced NoVNC viewer with comprehensive controls and monitoring.
    
    This function provides an enhanced viewer with:
    - Professional UI with status indicators
    - Human intervention controls (take control, stop, help)
    - Connection monitoring and error handling
    - Fullscreen support and responsive design
    - Session timing and information panel
    
    Args:
        novnc_url: The NoVNC URL from sandbox creation
        vnc_password: VNC password (optional)
        auto_open: Whether to automatically open the viewer in browser
        demo_name: Display name for the demo
        demo_description: Description of what the demo does
        
    Returns:
        Path to the generated HTML file
    """
    return generate_advanced_novnc_viewer(
        novnc_url=novnc_url,
        vnc_password=vnc_password or "vncpassword",
        auto_open=auto_open,
        demo_name=demo_name,
        demo_description=demo_description,
        show_intervention_controls=True,
        custom_info={
            "Demo Type": "Browser Automation",
            "Connection": "NoVNC Remote Desktop",
            "Status": "Active",
            "Features": "Human Intervention Enabled",
            "Keyboard Shortcuts": "F11: Fullscreen, Ctrl+I: Toggle Info"
        },
        window_width=1400,
        window_height=900
    )


def generate_simple_novnc_viewer(
    novnc_url: str, 
    vnc_password: Optional[str] = None, 
    auto_open: bool = True
) -> str:
    """
    Generate a simple HTML viewer for NoVNC interface (legacy function).
    
    Args:
        novnc_url: The NoVNC URL from sandbox creation
        vnc_password: VNC password (default: "vncpassword")
        auto_open: Whether to automatically open the viewer in browser
        
    Returns:
        Path to the generated HTML file
    """
    try:
        # Create a simple HTML template for NoVNC viewing
        html_template = f"""<!DOCTYPE html>
<html>
<head>
    <title>NoVNC Demo Viewer</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background-color: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .header {{
            text-align: center;
            margin-bottom: 20px;
            color: #333;        }}
        .info {{
            background-color: #e8f4fd;
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 20px;
            border-left: 4px solid #1976d2;
        }}
        .viewer-frame {{
            width: 100%;
            height: 80vh;
            border: 1px solid #ddd;
            border-radius: 5px;
        }}
        .credentials {{
            background-color: #fff3cd;
            padding: 10px;
            border-radius: 5px;
            margin-bottom: 15px;
            border-left: 4px solid #ffc107;
        }}
        code {{
            background-color: #f8f9fa;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: monospace;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🖥️ Browser Automation Demo Viewer</h1>
            <p>Watch the automation in real-time through this NoVNC interface</p>
        </div>
        
        <div class="info">
            <h3>📋 Viewing Instructions</h3>
            <ul>
                <li>The browser automation will appear in the frame below</li>
                <li>You can interact with the remote desktop if needed</li>
                <li>The demo will run automatically - no action required</li>
            </ul>
        </div>
        
        <div class="credentials">
            <strong>🔑 VNC Password:</strong> <code>{vnc_password or "vncpassword"}</code>
        </div>
        
        <iframe
            id="novnc-frame" 
            src="{novnc_url}?autoconnect=true" 
            class="viewer-frame"
            frameborder="0">
        </iframe>
        
        <div style="margin-top: 15px; text-align: center; color: #666; font-size: 0.9em;">
            <p>💡 If the connection fails, try refreshing the page or check the VNC URL</p>
        </div>
    </div>
</body>
</html>"""

        # Create output directory and file
        output_dir = Path(__file__).parent.parent / "tools" / "templates"
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / "simple_novnc_viewer.html"
        
        # Write the HTML file
        with open(output_path, "w") as f:
            f.write(html_template)
        
        print(f"✅ Simple NoVNC viewer generated: {output_path}")
        
        # Auto-open in browser if requested
        if auto_open:
            open_viewer_in_browser(str(output_path))
            
        return str(output_path)
        
    except Exception as e:
        print(f"❌ Failed to generate simple NoVNC viewer: {e}")
        return ""


def open_viewer_in_browser(file_path: str) -> None:
    """
    Open the generated HTML file in the default web browser.
    
    Args:
        file_path: Path to the HTML file to open
    """
    try:
        # Get the absolute path of the file
        abs_file_path = str(Path(file_path).resolve())
        
        # Construct the file URL
        file_url = f"file://{abs_file_path}"
        
        # Open the file in the default web browser
        webbrowser.open(file_url)
        
        print(f"🌐 NoVNC viewer opened in browser: {file_url}")
        
    except Exception as e:
        print(f"❌ Failed to open viewer in browser: {e}")


def display_viewer_info(novnc_url: str, vnc_password: str = "secret") -> None:
    """
    Display information about the NoVNC viewer without generating HTML.
    Useful for cases where you just want to show the URL info.
    
    Args:
        novnc_url: The NoVNC URL from sandbox creation
        vnc_password: VNC password (default: "secret")
    """
    print("\n" + "="*60)
    print("🖥️  NoVNC VIEWER INFORMATION")
    print("="*60)
    print(f"📋 NoVNC URL: {novnc_url}")
    print(f"🔑 VNC Password: {vnc_password}")
    print("💡 You can open this URL in your browser to watch the automation")
    print("="*60 + "\n")
