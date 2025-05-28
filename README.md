# Browser Automation Tool with Enhanced AI Agent Integration

A production-ready browser automation system using Python and LangChain with enhanced AI agent capabilities, human intervention support, and robust error handling.

## 🚀 Key Features

- **🤖 Enhanced LangChain Agent Integration** - Zero formatting errors with automatic correction
- **💼 Professional Business Automation** - Market research, lead generation, competitive analysis
- **🧠 Intelligent Task Parsing** - Natural language to browser automation translation
- **🛡️ Human Intervention Support** - Seamless handoff for CAPTCHAs and complex scenarios
- **🏗️ Sandboxed Execution** - Isolated browser environments with full cleanup
- **🔧 Enhanced Error Handling** - Robust retry mechanisms and graceful failures
- **📊 Business Intelligence** - Automated reporting and data collection
- **🎯 Production-Ready** - Comprehensive testing and validation completed

## 📋 Prerequisites

- Python 3.11+
- Azure OpenAI API access
- Daytona platform API key

## 🔧 Installation

```bash
# Clone the repository
git clone <repository-url>
cd brower_tool

# Install dependencies
pip install -r requirements.txt

# OR using Poetry
poetry install
```

## ⚙️ Configuration

Create a `.env` file in the root directory:

```env
# Azure OpenAI Configuration
AZURE_OPENAI_API_KEY=your_api_key_here
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT_NAME=your_deployment_name
AZURE_OPENAI_API_VERSION=2023-05-15

# Daytona Platform Configuration
DAYTONA_API_KEY=your_daytona_api_key
DAYTONA_API_URL=https://app.daytona.io/api

# VNC Configuration (optional)
VNC_PASSWORD=vncpassword
```

## 🚀 Quick Start

### Basic Browser Automation

```python
from src.tools.enhanced_browser_tools import get_enhanced_browser_tools
from src.utils.enhanced_agent_formatting import ImprovedReActOutputParser, create_enhanced_business_prompt
from langchain_openai import AzureChatOpenAI
from langchain.agents import create_react_agent, AgentExecutor
import os

# Initialize enhanced browser tools
tools = get_enhanced_browser_tools()

# Create AI model with optimized settings
llm = AzureChatOpenAI(
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
    azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
    temperature=0.1,  # Low temperature for consistent formatting
    max_tokens=3000
)

# Create enhanced agent with zero formatting errors
agent = create_react_agent(
    llm=llm,
    tools=tools,
    prompt=create_enhanced_business_prompt(),
    output_parser=ImprovedReActOutputParser()  # Eliminates "Invalid Format" errors
)

# Execute with enhanced error handling
agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True,
    handle_parsing_errors=True,
    max_iterations=25,
    max_execution_time=3600
)

# Run automation task
result = agent_executor.invoke({
    "input": "Navigate to example.com and extract the main heading"
})
```

### Business Automation Workflow

```bash
# Run comprehensive business automation demo
python src/examples/automation/business_workflow_demo.py
```

This executes a complete business workflow including:

- Market research and trend analysis
- Lead generation and qualification
- Competitive analysis and intelligence
- Human intervention for complex scenarios
- Structured business reporting

## 🎯 Production Status

**Current Status: PRODUCTION READY** ✅

- ✅ Enhanced agent formatting with zero errors
- ✅ Comprehensive business automation workflows  
- ✅ Robust error handling and recovery
- ✅ Human intervention integration
- ✅ Professional business intelligence capabilities
- ✅ Complete testing and validation

## Testing

The project includes both mock-based tests and integration tests.

### Mock-based Tests

These tests don't require external services and are suitable for CI/CD pipelines:

```bash
# Run mock tests
pytest tests/test_browser_api_mock.py -v

# Run basic unit tests
pytest tests/test_browser_api.py -v
```

### Integration Tests

These tests require a Daytona sandbox environment with sufficient quota:

```bash
# Run integration tests
## 🛠️ Available Tools

### Smart Browser Tools
- **`smart_navigate_to`** - Intelligent navigation with retry logic
- **`smart_search_google`** - Google search with result parsing
- **`smart_click_element`** - Smart element clicking with fallbacks
- **`smart_input_text`** - Text input with validation
- **`smart_extract_content`** - Content extraction and parsing
- **`smart_scroll_down`** - Intelligent scrolling
- **`smart_wait`** - Smart waiting with conditions
- **`smart_get_page_content`** - Page content retrieval
- **`smart_request_intervention`** - Human intervention requests

### Human Intervention Features
- **VNC Access** - Remote desktop for manual intervention
- **NoVNC Browser Access** - Web-based intervention interface
- **CAPTCHA Handling** - Automatic human handoff for challenges
- **Complex Form Handling** - Manual assistance for difficult forms

## 🧪 Testing & Validation

### Run Integration Tests

```bash
# Validate business workflow with enhanced formatting
python src/examples/automation/business_workflow_demo.py

# Note: Integration tests and validation scripts are archived in archives/test_files/
```

### Validation Results
- ✅ **Zero formatting errors** in comprehensive testing
- ✅ **Perfect ReAct format** compliance verified
- ✅ **Business automation** workflows operational
- ✅ **Human intervention** integration validated

## 📚 Documentation

- **Human Intervention Guide** - `docs/HUMAN_INTERVENTION_COMPLETE_GUIDE.md`
- **Integration Completion Report** - `ENHANCED_AGENT_FORMATTING_INTEGRATION_COMPLETE.md`

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests to ensure functionality
5. Submit a pull request

---

**Enhanced Browser Automation Tool - Production Ready with AI Agent Integration**
