# Browser Automation Tool with Enhanced AI Agent Integration

A production-ready browser automation system using Python and LangChain with enhanced AI agent capabilities, human intervention support, and robust error handling.

## 🚀 Key Features

- **🤖 Enhanced LangChain Agent Integration** - Zero formatting errors with automatic correction
- **💼 Professional Business Automation** - Market research, lead generation, competitive analysis
- **🧠 Intelligent Task Parsing** - Natural language to browser automation translation
- **🛡️ Human Intervention Support** - Seamless handoff for CAPTCHAs and complex scenarios (in development)
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