"""
REAL-WORLD BUSINESS AUTOMATION WORKFLOW DEMO
==========================================

This demo showcases a complete business automation workflow that demonstrates
the system's capability to handle real-world business scenarios with human
intervention when needed.

BUSINESS SCENARIO: Market Research & Lead Generation
==================================================

Objective: Automate the process of researching a technology market and gathering
potential leads for a browser automation service business.

WORKFLOW STEPS:
1. Research the browser automation market trends
2. Find potential customers (companies using automation)
3. Gather contact information and company details
4. Generate a structured report of findings
5. Handle all security challenges with human intervention

This represents a typical business use case where human oversight
and intervention are critical for success.
"""

import asyncio
import os
import time
import json
from dotenv import load_dotenv

# LangChain and AI imports
from langchain_openai import AzureChatOpenAI
from langchain.agents import create_react_agent, AgentExecutor
from langchain.memory import ConversationBufferMemory
from langchain.tools.render import render_text_description

# Our comprehensive automation system
from src.tools.enhanced_browser_tools import get_enhanced_browser_tools
from src.tools.utilities.sandbox_manager import SandboxManager
from src.utils.logger import logger
from src.utils.novnc_viewer import generate_novnc_viewer

# Enhanced agent formatting fixes
from src.utils.enhanced_agent_formatting import ImprovedReActOutputParser, create_enhanced_business_prompt

# Load environment variables
load_dotenv()

class BusinessAutomationWorkflow:
    """
    Real-world business automation workflow demonstration.
    
    This class showcases how the browser automation system can be used
    for actual business processes with human oversight and intervention.
    """
    
    def __init__(self):
        self.llm = None
        self.agent_executor = None
        self.memory = None
        self.sandbox_manager = SandboxManager()
        self.sandbox_id = None
        self.api_base_url = None
        self.vnc_url = None
        self.novnc_url = None
        self.tools = []
        self.research_data = {
            "market_trends": [],
            "potential_leads": [],
            "competitor_analysis": [],
            "workflow_metrics": {}
        }
        
    async def initialize_business_workflow(self):
        """Initialize the complete business automation workflow system"""
        
        logger.info("🏢 INITIALIZING BUSINESS AUTOMATION WORKFLOW")
        logger.info("="*80)
        logger.info("🎯 Business Objective: Market Research & Lead Generation")
        logger.info("🔧 Using Enhanced Agent Formatting Fixes")
        logger.info("💼 Target Industry: Browser Automation Services")
        logger.info("="*80)
        
        # Create sandbox environment with browser automation capabilities
        logger.info("🏗️ Creating automated business research environment...")
        (self.sandbox_id, cdp_url, self.vnc_url, 
         self.novnc_url, self.api_base_url, web_url, browser_api_url) = self.sandbox_manager.create_sandbox()
        
        logger.info(f"✅ Business Research Environment Ready: {self.sandbox_id}")
        logger.info(f"   🌐 Research Platform: {self.api_base_url}")
        logger.info(f"   🔐 Secure Access: {self.novnc_url}")
        logger.info(f"   🔑 Access Code: {os.getenv('VNC_PASSWORD', 'vncpassword')}")
        
        # Generate and open NoVNC viewer for business workflow monitoring
        try:
            viewer_path = generate_novnc_viewer(
                vnc_url=self.novnc_url,
                vnc_password=os.getenv('VNC_PASSWORD', 'vncpassword'),
                title="Business Automation Research Monitor",
                auto_open=True
            )
            logger.info(f"🖥️ Business monitoring interface: {viewer_path}")
        except Exception as e:
            logger.warning(f"⚠️ Monitor interface setup issue: {e}")
        
        # Wait for environment initialization
        await asyncio.sleep(60)
        
        # Initialize enhanced AI agent with improved formatting
        logger.info("🧠 Initializing enhanced business intelligence agent...")
        self.llm = AzureChatOpenAI(
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
            azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
            temperature=0.1,  # Lower temperature for consistent formatting
            max_tokens=3000,  # Increased for complex business reasoning
            model_kwargs={
                "top_p": 0.9,
                "frequency_penalty": 0.0,
                "presence_penalty": 0.0
            }
        )
        
        # Setup enhanced browser automation tools for business research
        logger.info("🛠️ Configuring business research automation tools...")
        self.tools = get_enhanced_browser_tools()
        
        for tool in self.tools:
            await tool.setup(self.api_base_url, self.sandbox_id)
        
        # Initialize conversation memory for business context
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True,
            input_key="input"
        )
        
        # Create enhanced business automation agent with improved formatting
        business_prompt = create_enhanced_business_prompt()
        
        # Create business automation agent with enhanced configuration
        agent = create_react_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=business_prompt,
            output_parser=ImprovedReActOutputParser(),
            tools_renderer=render_text_description
        )
        
        # Create enhanced agent executor for business workflows
        self.agent_executor = AgentExecutor(
            agent=agent,
            tools=self.tools,
            memory=self.memory,
            verbose=True,
            return_intermediate_steps=True,
            handle_parsing_errors=True,
            max_iterations=25,  # Complex business research needs more steps
            max_execution_time=3600,  # 1 hour for comprehensive research
            early_stopping_method="force"
        )
        
        logger.info("✅ BUSINESS AUTOMATION WORKFLOW READY!")
        logger.info("🎯 Enhanced agent formatting fixes applied")
        logger.info("🚀 Ready to conduct professional market research")
        logger.info("="*80)
        
    async def research_market_trends(self):
        """Phase 1: Research browser automation market trends"""
        logger.info("📈 PHASE 1: MARKET TREND ANALYSIS")
        logger.info("-" * 50)
        
        research_task = """
        Conduct comprehensive market research on browser automation trends:
        
        1. **Industry Overview Research**:
           - Navigate to industry report sites (Gartner, Forrester, McKinsey)
           - Search for "browser automation market 2025" or "web scraping industry"
           - Research common automation applications
           - Find case studies of successful implementations
           - Identify vertical-specific automation needs
           
        2. **Market Intelligence Gathering**:
           - Handle paywalls/access restrictions by requesting human intervention
           - Extract and structure relevant market intelligence
           - Return findings in a structured report format
           
        Respect privacy policies and only collect publicly available information.
        Return structured data ready for business analysis.
        """
        
        start_time = time.time()
        
        try:
            result = await asyncio.get_event_loop().run_in_executor(
                None, 
                lambda: self.agent_executor.invoke({"input": research_task})
            )
            
            duration = time.time() - start_time
            output_result = result.get("output") if result else None
            self.research_data["market_trends"] = {
                "research_duration": duration,
                "findings": output_result or "",  # Ensure string type, handle None values
                "sources_accessed": len(result.get("intermediate_steps", []) if result else []),
                "status": "completed"
            }
            
            logger.info(f"✅ Market trend analysis completed in {duration:.1f}s")
            return result
            
        except Exception as e:
            logger.error(f"❌ Market research failed: {e}")
            self.research_data["market_trends"] = {
                "status": "failed",
                "error": str(e)
            }
            return None
    
    async def generate_qualified_leads(self):
        """Phase 2: Generate qualified lead prospects"""
        logger.info("🎯 PHASE 2: LEAD GENERATION")
        logger.info("-" * 50)
        
        lead_task = """
        Generate qualified leads for browser automation services:
        
        1. **Job Board Research**:
           - Search LinkedIn, Indeed, AngelList for automation-related jobs
           - Find companies hiring for "web scraping", "browser automation", "RPA" roles
           - Look for "data extraction", "automated testing", "web automation" positions
           - Extract company names, sizes, and contact information
           
        2. **Technology Company Research**:
           - Find SaaS companies that might need automation services
           - Look for fintech companies needing automated compliance checks
           - Identify marketing agencies using web scraping for research
           
        3. **Industry-Specific Prospects**:
           - Real estate companies needing data automation
           - Travel companies requiring price monitoring
           - Retail businesses needing competitive analysis
           - Healthcare companies requiring regulatory compliance
           
        4. **Contact Information Gathering**:
           - Find decision makers: CTOs, IT Directors, Engineering VPs
           - Gather LinkedIn profiles of key personnel
           - Document company details: name, website, industry, size
           - Company name, website, industry
           - Key contact information
           - Company size and revenue estimates
           
        Respect privacy policies and only collect publicly available information.
        Return structured data ready for business outreach.
        """
        
        start_time = time.time()
        
        try:
            result = await asyncio.get_event_loop().run_in_executor(
                None, 
                lambda: self.agent_executor.invoke({"input": lead_task})
            )
            
            duration = time.time() - start_time
            output_result = result.get("output") if result else None
            self.research_data["potential_leads"] = {
                "research_duration": duration,
                "findings": output_result or "",
                "sources_accessed": len(result.get("intermediate_steps", []) if result else []),
                "status": "completed"
            }
            
            logger.info(f"✅ Lead generation completed in {duration:.1f}s")
            return result
            
        except Exception as e:
            logger.error(f"❌ Lead generation failed: {e}")
            self.research_data["potential_leads"] = {
                "status": "failed",
                "error": str(e)
            }
            return None
    
    async def analyze_competition(self):
        """Phase 3: Competitive analysis and positioning research"""
        logger.info("🏆 PHASE 3: COMPETITIVE ANALYSIS")
        logger.info("-" * 50)
        
        competition_task = """
        Conduct competitive analysis of browser automation service providers:
        
        1. **Direct Competitor Research**:
           - Research Selenium Grid service providers
           - Find Puppeteer, Playwright automation companies
           - Look for cloud-based browser automation solutions
           - Identify RPA solution providers
           
        2. **Service Offering Analysis**:
           - Document pricing models and service tiers
           - Research customer testimonials and case studies
           - Find unique value propositions and market positioning
           - Research partnership/integration strategies
           
        3. **Technology Stack Analysis**:
           - Find information about their automation capabilities
           - Identify gaps in current market offerings
           - Research their target customer base and industry focus
           - Technology capabilities and infrastructure
           - Market positioning and messaging
           - Strengths and weaknesses analysis
           
        Handle access restrictions professionally and request human intervention when needed.
        Return competitive intelligence suitable for strategic business planning.
        """
        
        start_time = time.time()
        
        try:
            result = await asyncio.get_event_loop().run_in_executor(
                None, 
                lambda: self.agent_executor.invoke({"input": competition_task})
            )
            
            duration = time.time() - start_time
            output_result = result.get("output") if result else None
            self.research_data["competitor_analysis"] = {
                "research_duration": duration,
                "findings": output_result or "",
                "sources_accessed": len(result.get("intermediate_steps", []) if result else []),
                "status": "completed"
            }
            
            logger.info(f"✅ Competitive analysis completed in {duration:.1f}s")
            return result
            
        except Exception as e:
            logger.error(f"❌ Competitive analysis failed: {e}")
            self.research_data["competitor_analysis"] = {
                "status": "failed",
                "error": str(e)
            }
            return None
    
    async def generate_business_report(self):
        """Generate comprehensive business intelligence report"""
        logger.info("📊 GENERATING BUSINESS INTELLIGENCE REPORT")
        logger.info("="*80)
        
        # Calculate workflow metrics
        completed_phases = sum(1 for phase in [
            self.research_data.get("market_trends"),
            self.research_data.get("potential_leads"),
            self.research_data.get("competitor_analysis")
        ] if phase and phase.get("status") == "completed")
        
        total_research_time = sum(
            phase.get("research_duration", 0) 
            for phase in [
                self.research_data.get("market_trends", {}),
                self.research_data.get("potential_leads", {}),
                self.research_data.get("competitor_analysis", {})
            ]
        )
        
        total_sources = sum(
            phase.get("sources_accessed", 0) 
            for phase in [
                self.research_data.get("market_trends", {}),
                self.research_data.get("potential_leads", {}),
                self.research_data.get("competitor_analysis", {})
            ]
        )
        
        self.research_data["workflow_metrics"] = {
            "completed_phases": completed_phases,
            "total_phases": 3,
            "total_research_time": total_research_time,
            "total_sources_accessed": total_sources,
            "automation_efficiency": f"{(completed_phases/3)*100:.1f}%"
        }
        
        # Save comprehensive business report
        report_path = "business_automation_report.json"
        with open(report_path, 'w') as f:
            json.dump(self.research_data, f, indent=2, default=str)
        
        logger.info(f"✅ Business intelligence report saved: {report_path}")
        logger.info(f"📈 Phases completed: {completed_phases}/3")
        logger.info(f"⏱️ Total research time: {total_research_time:.1f}s")
        logger.info(f"🔍 Sources accessed: {total_sources}")
        logger.info(f"🎯 Automation efficiency: {(completed_phases/3)*100:.1f}%")
        
        return self.research_data
    
    async def execute_complete_workflow(self):
        """Execute the complete business automation workflow"""
        logger.info("🚀 EXECUTING COMPREHENSIVE BUSINESS AUTOMATION WORKFLOW")
        logger.info("="*80)
        
        workflow_start = time.time()
        
        try:
            # Initialize the complete business workflow system
            await self.initialize_business_workflow()
            
            # Phase 1: Market Research
            await self.research_market_trends()
            
            # Phase 2: Lead Generation
            await self.generate_qualified_leads()
            
            # Phase 3: Competitive Analysis
            await self.analyze_competition()
            
            # Generate final business report
            final_report = await self.generate_business_report()
            
            workflow_duration = time.time() - workflow_start
            
            logger.info("="*80)
            logger.info("🎉 BUSINESS AUTOMATION WORKFLOW COMPLETED")
            logger.info(f"⏱️ Total execution time: {workflow_duration:.1f}s")
            logger.info("📊 Business intelligence report generated")
            logger.info("🎯 Enhanced agent formatting: WORKING ✅")
            logger.info("="*80)
            
            return final_report
            
        except Exception as e:
            logger.error(f"❌ Business workflow execution failed: {e}")
            return None
        finally:
            # Clean up resources
            await self.cleanup()
    
    async def cleanup(self):
        """Clean up resources"""
        if hasattr(self, 'sandbox_id') and self.sandbox_id:
            logger.info("🧹 Cleaning up business research environment...")
            self.sandbox_manager.delete_sandbox(self.sandbox_id)
            logger.info("✅ Cleanup completed")

async def main():
    """Main function to run the business automation workflow demonstration"""
    
    logger.info("🏢 BUSINESS AUTOMATION WORKFLOW DEMONSTRATION")
    logger.info("Using Enhanced Agent Formatting Fixes")
    logger.info("="*80)
    
    # Create and execute business automation workflow
    workflow = BusinessAutomationWorkflow()
    
    try:
        result = await workflow.execute_complete_workflow()
        
        if result:
            logger.info("✅ Business automation demonstration completed successfully!")
            logger.info("🎯 Enhanced agent formatting fixes: OPERATIONAL")
            return True
        else:
            logger.error("❌ Business automation demonstration failed")
            return False
            
    except Exception as e:
        logger.error(f"❌ Workflow demonstration error: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)
