"""
Enhanced Agent Formatting Module
==============================

This module contains the improved ReAct output parser and prompt template
for fixing LangChain agent formatting issues in the business workflow.
"""

from typing import List, Any
from langchain.schema import OutputParserException
from langchain.agents.output_parsers import ReActSingleInputOutputParser
from langchain.prompts import PromptTemplate
from src.utils.logger import logger


class ImprovedReActOutputParser(ReActSingleInputOutputParser):
    """Improved ReAct output parser with better error handling and format validation"""
    
    def parse(self, text: str) -> Any:
        """Parse the LLM output with enhanced error handling"""
        try:
            return super().parse(text)
        except OutputParserException as e:
            # Try to fix common formatting issues
            fixed_text = self._attempt_format_fix(text)
            if fixed_text != text:
                logger.warning(f"Attempting to fix malformed agent output: {e}")
                try:
                    return super().parse(fixed_text)
                except OutputParserException:
                    pass
            
            # If we can't fix it, provide a helpful error
            logger.error(f"Agent output parsing failed: {e}")
            logger.error(f"Raw output: {text}")
            raise OutputParserException(
                f"Could not parse LLM output: `{text}`\n"
                f"Expected format:\n"
                f"Thought: [your reasoning]\n"
                f"Action: [tool name]\n"
                f"Action Input: [tool input]\n"
                f"Observation: [tool output]\n"
                f"... (repeat Thought/Action/Action Input/Observation as needed)\n"
                f"Thought: [final reasoning]\n"
                f"Final Answer: [final response]"
            )
    
    def _attempt_format_fix(self, text: str) -> str:
        """Attempt to fix common formatting issues in agent output"""
        lines = text.strip().split('\n')
        fixed_lines = []
        
        for i, line in enumerate(lines):
            stripped = line.strip()
            
            # Fix missing "Action:" prefix
            if (i > 0 and 
                lines[i-1].strip().startswith('Thought:') and 
                not stripped.startswith(('Action:', 'Final Answer:')) and
                stripped and not stripped.startswith('Observation:')):
                if any(tool_name in stripped for tool_name in self._get_tool_names()):
                    fixed_lines.append(f"Action: {stripped}")
                    continue
            
            # Fix missing "Action Input:" prefix
            if (i > 0 and 
                lines[i-1].strip().startswith('Action:') and 
                not stripped.startswith(('Action Input:', 'Observation:', 'Thought:', 'Final Answer:')) and
                stripped):
                fixed_lines.append(f"Action Input: {stripped}")
                continue
                
            fixed_lines.append(line)
        
        return '\n'.join(fixed_lines)
    
    def _get_tool_names(self) -> List[str]:
        """Get common tool names for format fixing"""
        return [
            'smart_navigate_to', 'smart_search_google', 'smart_click_element',
            'smart_input_text', 'smart_extract_content', 'smart_scroll_down',
            'smart_wait', 'smart_get_page_content', 'smart_request_intervention'
        ]


def create_enhanced_business_prompt() -> PromptTemplate:
    """Create an enhanced ReAct prompt template with better formatting instructions"""
    
    template = """You are an expert Business Automation Analyst with comprehensive web research capabilities.

MISSION: Conduct thorough market research and lead generation for browser automation services.

BUSINESS CONTEXT:
- Industry: Browser Automation & Web Scraping Services
- Target: Companies that need automated web interactions
- Goal: Generate qualified leads and market intelligence
- Ethics: Respect robots.txt, privacy policies, and legal boundaries

AVAILABLE TOOLS:
{tools}

TOOL NAMES: {tool_names}

CRITICAL FORMATTING REQUIREMENTS:
You MUST follow this exact format for each step:

Thought: [Your reasoning about what to do next]
Action: [Tool name from the list above]
Action Input: [Input for the tool as a JSON object or string]
Observation: [Result from the tool]

Continue this Thought/Action/Action Input/Observation cycle until you have enough information.

When you have completed the task, end with:
Thought: [Final reasoning]
Final Answer: [Your final response]

EXAMPLE FORMAT:
Thought: I need to research browser automation market trends by searching for industry reports.
Action: smart_search_google
Action Input: "browser automation market trends 2024 industry report"
Observation: [Google search results will appear here]

Thought: I found some search results. Let me navigate to a promising report.
Action: smart_navigate_to
Action Input: https://example.com/automation-report
Observation: [Page content will appear here]

BUSINESS RESEARCH METHODOLOGY:

1. **Market Analysis**:
   - Research browser automation market trends
   - Identify growth opportunities and challenges
   - Analyze pricing models and service offerings
   - Document market size and segmentation

2. **Lead Generation**:
   - Find companies actively hiring for automation roles
   - Identify businesses with web scraping needs
   - Research software companies building automation tools
   - Locate e-commerce companies needing data extraction

3. **Competitive Intelligence**:
   - Research existing automation service providers
   - Analyze their offerings, pricing, and positioning
   - Identify market gaps and opportunities
   - Document competitive advantages

4. **Human Intervention Protocol**:
   - CAPTCHAs → Request human assistance for verification
   - Login walls → Ask human to provide demo credentials
   - Subscription barriers → Get human guidance on approach
   - Legal/ethical concerns → Pause for human review

5. **Data Quality Standards**:
   - Verify accuracy of all collected information
   - Cross-reference data from multiple sources
   - Maintain structured, actionable business intelligence
   - Provide clear source attribution

BUSINESS ETHICS:
- Only collect publicly available information
- Respect website terms of service
- Never attempt unauthorized access
- Maintain professional research standards

CONVERSATION HISTORY:
{chat_history}

CURRENT RESEARCH TASK: {input}

Begin your research following the exact format above.

{agent_scratchpad}"""

    return PromptTemplate(
        template=template,
        input_variables=["tools", "tool_names", "chat_history", "input", "agent_scratchpad"]
    )


def create_enhanced_react_agent(
    llm,
    tools,
    max_iterations: int = 15,
    max_execution_time: int = 600,
    return_intermediate_steps: bool = True,
    handle_parsing_errors: bool = True,
    **kwargs
):
    """
    Create an enhanced ReAct agent with improved error handling and formatting.
    
    Args:
        llm: The language model to use
        tools: List of tools available to the agent
        max_iterations: Maximum number of iterations (default: 15)
        max_execution_time: Maximum execution time in seconds (default: 600)
        return_intermediate_steps: Whether to return intermediate steps (default: True)
        handle_parsing_errors: Whether to handle parsing errors gracefully (default: True)
        **kwargs: Additional arguments passed to the agent
    
    Returns:
        AgentExecutor: Configured agent executor with enhanced error handling
    """
    from langchain.agents import create_react_agent, AgentExecutor
    
    try:
        # Create enhanced prompt
        prompt = create_enhanced_business_prompt()
        
        # Create enhanced output parser
        output_parser = ImprovedReActOutputParser()
        
        # Create the agent with enhanced prompt and parser
        agent = create_react_agent(
            llm=llm,
            tools=tools,
            prompt=prompt,
            output_parser=output_parser if handle_parsing_errors else None,
            **kwargs
        )
        
        # Create agent executor with enhanced configuration
        agent_executor = AgentExecutor(
            agent=agent,
            tools=tools,
            max_iterations=max_iterations,
            max_execution_time=max_execution_time,
            return_intermediate_steps=return_intermediate_steps,
            handle_parsing_errors=handle_parsing_errors,
            verbose=True  # Enable verbose output for better debugging
        )
        
        logger.info(f"✅ Enhanced ReAct agent created with {len(tools)} tools")
        logger.info(f"📊 Configuration: max_iterations={max_iterations}, max_time={max_execution_time}s")
        
        return agent_executor
        
    except Exception as e:
        logger.error(f"❌ Failed to create enhanced ReAct agent: {e}")
        raise RuntimeError(f"Agent creation failed: {e}") from e
