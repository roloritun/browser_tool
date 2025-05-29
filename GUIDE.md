# Browser Automation Tool

A comprehensive browser automation tool with AI agent integration and human intervention capabilities.

## 🚀 Quick Start

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run Examples**:
   ```bash
   python run_all_examples_with_novnc.py
   ```

## 🏗️ Project Structure

```
src/
├── examples/           # Example automation scripts
├── tools/             # Browser automation tools
└── utils/             # Utility functions

docs/                  # Documentation
intervention_status_diagnostic.py  # Status diagnostic tool
```

## 🛠️ Core Features

### Browser Automation
- **Multi-tool Support**: Enhanced browser tools with LangChain integration
- **Content Extraction**: Smart content extraction with configurable strategies
- **Navigation**: Advanced navigation with error handling
- **Element Interaction**: Robust click, type, and form handling

### Human Intervention System
- **Automatic Detection**: Detects CAPTCHAs, anti-bot protection, and authentication needs
- **Visual Interface**: Clear intervention banners with instructions
- **Status Tracking**: Real-time intervention status monitoring
- **NoVNC Integration**: Remote browser access for manual intervention

### AI Agent Integration
- **LangChain Tools**: Native LangChain tool integration
- **Smart Agents**: AI agents that can handle complex automation tasks
- **Error Recovery**: Automatic retry and fallback mechanisms

## 📊 Intervention Status

The intervention system uses these status codes:

- **`unknown`**: Normal state, no intervention needed (this is good!)
- **`pending`**: Intervention requested, waiting for human operator
- **`in_progress`**: Human currently working on the challenge
- **`completed`**: Successfully resolved, automation continues
- **`timeout/failed`**: Intervention unsuccessful

### Understanding "Unknown" Status

The `unknown` status is **normal** and indicates:
- ✅ No active intervention required
- ✅ Browser operating normally
- ✅ System ready for automation
- ✅ Previous interventions completed

## 🔧 Usage Examples

### Basic Browser Automation
```python
from src.tools.browser_tool import BrowserTool

tool = BrowserTool()
result = await tool.navigate("https://example.com")
content = await tool.extract_text()
```

### With Human Intervention
```python
from src.tools.enhanced_browser_tools import EnhancedBrowserTool

tool = EnhancedBrowserTool()
result = await tool.navigate("https://site-with-captcha.com")

# System automatically handles intervention if needed
if "captcha detected" in result:
    intervention_id = await tool.request_human_intervention(
        reason="CAPTCHA challenge detected",
        instructions="Please complete the CAPTCHA"
    )
    # Wait for completion...
```

### Status Checking
```python
# Check intervention status
python intervention_status_diagnostic.py
```

## 🎯 Key Benefits

1. **Seamless Integration**: Works with existing automation scripts
2. **Automatic Detection**: No manual intervention management needed
3. **Visual Feedback**: Clear UI for human operators
4. **Robust Error Handling**: Graceful fallbacks and recovery
5. **AI-Powered**: Smart agents that adapt to different scenarios

## 🚀 Getting Started

Run the comprehensive examples to see all features in action:

```bash
python run_all_examples_with_novnc.py
```

This will:
- Start the browser automation system
- Launch NoVNC viewer for remote access
- Run example automation scripts
- Demonstrate intervention capabilities

## 💡 Tips

- **Monitor Status**: Use the diagnostic tool to understand intervention status
- **NoVNC Access**: Use the NoVNC viewer to see browser actions in real-time
- **Error Recovery**: The system automatically retries failed operations
- **Human Intervention**: Only needed for complex challenges like CAPTCHAs

For detailed examples and advanced usage, see the files in `src/examples/`.
