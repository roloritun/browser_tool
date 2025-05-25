# Browser Automation Tool

A browser automation tool using Python and LangChain for executing natural language browser automation tasks, with enhanced human intervention capabilities.

## Features

- Natural language task parsing
- Browser automation with retry and fallback mechanisms
- VNC and noVNC viewer support
- Comprehensive error handling
- Sandboxed execution environment
- CAPTCHA detection and handling
- Human intervention for sensitive inputs and complex scenarios
- Timeout mechanisms to prevent hanging
- Integration with Azure OpenAI for intelligent automation
- FastAPI backend for browser control

## Installation

```bash
pip install -r requirements.txt
```

## Setup

1. Create a `.env` file with the following variables:
   ```
   # Azure OpenAI Credentials
   AZURE_OPENAI_API_KEY=your_api_key_here
   AZURE_OPENAI_ENDPOINT=https://your-resource-name.openai.azure.com/
   AZURE_OPENAI_DEPLOYMENT_NAME=your_deployment_name
   AZURE_OPENAI_API_VERSION=2023-05-15

   # Daytona Sandbox API Key
   DAYTONA_API_KEY=your_daytona_api_key
   DAYTONA_API_URL=https://app.daytona.io/api
   ```

## Usage

### Running the Demo

```bash
# Create a new sandbox and run the demo
python src/demo.py

# Use an existing browser API (set BROWSER_API_URL in .env first)
python src/api_demo.py
```

This will:
1. Create a Daytona sandbox with Chrome browser (or use existing API)
2. Initialize the LangChain agent with browser tools
3. Execute a simple task (navigating to example.com and extracting content)

### Using in Your Own Projects

You can integrate the browser tools into your own LangChain projects:

```python
from src.tools.utilities.browser_tools_init import get_browser_tools
from langchain_openai import AzureChatOpenAI
from langchain.agents import AgentExecutor, create_react_agent
from langchain.prompts import PromptTemplate
import os

# Option 1: Create a new sandbox automatically
browser_tools = get_browser_tools()

# Option 2: Use an existing API URL
api_url = "https://your-browser-api-url"
browser_tools = get_browser_tools(api_url=api_url)

# Create language model
llm = AzureChatOpenAI(
    azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
    temperature=0.2
)

# Create agent
prompt = PromptTemplate.from_template("Your prompt template here {tools} {input}")
agent = create_react_agent(llm, browser_tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=browser_tools, verbose=True)

# Execute task
result = agent_executor.invoke({"input": "Your task here"})
```

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
pytest tests/test_browser_api_integration.py -v
```

### Using the Helper Script

For convenience, you can use the helper script:

```bash
# Run the mock tests
python run_tests.py --test-file tests/test_browser_api_mock.py -v

# Run all tests
python run_tests.py -v

# Run human intervention tests
python run_tests.py --human-tests
```

## Human Intervention Features

The enhanced browser tool now includes robust human intervention capabilities for handling complex scenarios:

### CAPTCHA Detection and Handling

The tool can automatically detect common CAPTCHA types and request human assistance:

```python
# Detect if a CAPTCHA is present
captcha_result = browser_api.detect_captcha(screenshot=True)
if captcha_result.get("captcha_detected"):
    # Wait for human to solve it
    browser_api.wait_for_human_input(reason="CAPTCHA detected")
```

### Handling Sensitive Inputs

For passwords, 2FA codes, and other sensitive information:

```python
# Securely handle password input
browser_api.handle_sensitive_input(
    selector="input[type='password']",
    field_type="password",
    reason="Please enter your password"
)
```

## Available Browser Tools

The toolkit includes the following browser automation capabilities:

- **Navigation**: Navigate to URLs, go back, refresh
- **Interaction**: Click elements, input text, send keyboard keys
- **Content extraction**: Extract content based on goals
- **Scrolling**: Scroll up/down, scroll to text
- **Tab management**: Open, close, and switch between tabs
- **Form manipulation**: Select dropdown options, fill out forms
- **PDF generation**: Save and generate PDFs of pages
- **Cookie management**: Get, set, and clear cookies
- **Dialog handling**: Accept or dismiss dialogs
- **Frame handling**: Switch between frames
- **Network control**: Set network conditions

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

### Periodic CAPTCHA Checking

The enhanced `_run` method now periodically checks for CAPTCHAs during execution and falls back to human intervention when automated recovery fails.

## Test Report

See the [TEST_REPORT.md](TEST_REPORT.md) file for a comprehensive overview of the testing approach and results.
