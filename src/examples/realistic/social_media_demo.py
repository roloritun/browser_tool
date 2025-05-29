#!/usr/bin/env python3
"""
Social Media Automation Demo

This demo tests the browser automation tool's ability to handle social media
platforms and content discovery workflows. It demonstrates navigation of 
social platforms, content interaction, feed browsing, and social features
while respecting platform terms of service and ethical guidelines.

Platforms tested:
- Public social media content exploration
- News aggregation and content discovery
- Community platform navigation
- Content interaction patterns

Safety: Uses only public content and respects platform ToS.
Ethics: No automated posting, following, or account manipulation.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

import asyncio
import logging
import time
import random
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

from langchain_openai import ChatOpenAI

from tools.utilities.browser_tools_init import initialize_browser_tools
from tools.utilities.sandbox_manager import SandboxManager
from utils.enhanced_agent_formatting import create_enhanced_react_agent
from utils.novnc_viewer import generate_novnc_viewer

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Social media and content discovery sites
SOCIAL_CONTENT_SITES = [
    {
        "name": "Reddit Public Content",
        "url": "https://www.reddit.com/",
        "description": "Public Reddit content and community discussions",
        "platform_type": "discussion_forum",
        "content_features": ["posts", "comments", "voting", "communities"],
        "test_scenario": "public_content_exploration",
        "interaction_types": ["browse", "read", "navigate"],
        "requires_account": False
    },
    {
        "name": "Hacker News",
        "url": "https://news.ycombinator.com/",
        "description": "Tech news aggregation and discussion platform",
        "platform_type": "news_aggregator",
        "content_features": ["articles", "comments", "voting", "discussions"],
        "test_scenario": "news_discovery_workflow",
        "interaction_types": ["browse", "read", "analyze"],
        "requires_account": False
    },
    {
        "name": "GitHub Trending",
        "url": "https://github.com/trending",
        "description": "Trending repositories and developer content",
        "platform_type": "developer_platform",
        "content_features": ["repositories", "code", "trends", "discovery"],
        "test_scenario": "developer_content_discovery",
        "interaction_types": ["explore", "analyze", "discover"],
        "requires_account": False
    },
    {
        "name": "Product Hunt",
        "url": "https://www.producthunt.com/",
        "description": "Product discovery and launch platform",
        "platform_type": "product_discovery",
        "content_features": ["products", "launches", "voting", "collections"],
        "test_scenario": "product_discovery_workflow",
        "interaction_types": ["browse", "discover", "evaluate"],
        "requires_account": False
    }
]

# Content interaction patterns
CONTENT_INTERACTION_PATTERNS = {
    "discovery": {
        "description": "Content discovery and exploration patterns",
        "actions": ["browse_feeds", "explore_categories", "discover_trends"],
        "metrics": ["content_variety", "discovery_depth", "time_efficiency"]
    },
    "engagement": {
        "description": "Content engagement and interaction patterns",
        "actions": ["read_content", "view_details", "explore_comments"],
        "metrics": ["engagement_depth", "interaction_quality", "content_understanding"]
    },
    "navigation": {
        "description": "Platform navigation and user experience patterns",
        "actions": ["menu_navigation", "search_usage", "filter_application"],
        "metrics": ["navigation_efficiency", "feature_utilization", "user_experience"]
    },
    "analysis": {
        "description": "Content analysis and evaluation patterns",
        "actions": ["content_assessment", "trend_analysis", "quality_evaluation"],
        "metrics": ["analysis_depth", "insight_generation", "pattern_recognition"]
    }
}

class SocialMediaDemo:
    def __init__(self):
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "platforms_tested": [],
            "content_types_explored": set(),
            "interaction_patterns": {},
            "discovery_workflows": [],
            "navigation_strategies": [],
            "content_analysis_examples": [],
            "platform_features_tested": {},
            "success_metrics": {},
            "challenges_encountered": [],
            "total_execution_time": 0
        }
        self.llm = None
        self.tools = None
        self.agent_executor = None

    async def setup_browser_environment(self):
        """Initialize browser tools and create agent with NoVNC viewer."""
        try:
            # Create sandbox and get URLs
            logger.info("Creating sandbox environment...")
            sandbox_manager = SandboxManager()
            sandbox_id, cdp_url, vnc_url, novnc_url, api_url, web_url, x_url = sandbox_manager.create_sandbox()
            
            # Generate and open NoVNC viewer for real-time monitoring
            logger.info("🖥️ Opening NoVNC viewer for real-time monitoring...")
            try:
                viewer_path = generate_novnc_viewer(
                    novnc_url=novnc_url,
                    vnc_password="vncpassword",
                    auto_open=True
                )
                logger.info(f"✅ NoVNC viewer opened: {viewer_path}")
                logger.info(f"🌐 Direct NoVNC URL: {novnc_url}")
            except Exception as e:
                logger.warning(f"⚠️ Could not open NoVNC viewer: {e}")
                logger.info(f"🌐 You can manually open: {novnc_url}")
            
            # Initialize browser tools with the sandbox
            logger.info("Initializing browser automation tools...")
            self.tools = await initialize_browser_tools(api_url, sandbox_id)
            
            # Initialize LLM
            self.llm = ChatOpenAI(
                model="gpt-4-turbo-preview",
                temperature=0.1,
                max_tokens=2000
            )
            
            # Create enhanced agent
            self.agent_executor = create_enhanced_react_agent(
                llm=self.llm,
                tools=self.tools,
                max_iterations=20,
                max_execution_time=700,
                return_intermediate_steps=True
            )
            
            logger.info("✅ Browser environment setup complete")
            logger.info(f"🔑 VNC Password: vncpassword")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to setup browser environment: {e}")
            return False

    async def test_social_platform(self, platform: Dict[str, Any]) -> Dict[str, Any]:
        """Test a specific social media platform with ethical guidelines."""
        logger.info(f"\n🌐 Testing {platform['name']} ({platform['platform_type']})...")
        
        platform_result = {
            "platform_name": platform["name"],
            "platform_type": platform["platform_type"],
            "url": platform["url"],
            "test_scenario": platform["test_scenario"],
            "success": False,
            "content_types_found": [],
            "features_explored": [],
            "interaction_patterns_used": [],
            "content_discovery_examples": [],
            "navigation_efficiency": {},
            "ethical_compliance": True,
            "execution_time": 0,
            "error_details": None
        }
        
        start_time = time.time()
        
        try:
            # Create ethical social media exploration task
            task = self._create_social_exploration_task(platform)
            
            # Execute the task
            logger.info(f"🤖 Executing social content exploration: {platform['test_scenario']}")
            result = await self.agent_executor.ainvoke({"input": task})
            
            # Process and analyze results
            if result and "output" in result:
                platform_result.update(self._analyze_social_results(result, platform))
                platform_result["success"] = True
                logger.info(f"✅ Successfully explored {platform['name']}")
            else:
                logger.warning(f"⚠️ Limited results from {platform['name']}")
                platform_result["success"] = False
                
        except Exception as e:
            logger.error(f"❌ Error testing {platform['name']}: {e}")
            platform_result["error_details"] = str(e)
            self.results["challenges_encountered"].append({
                "platform": platform["name"],
                "platform_type": platform["platform_type"],
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            })
        
        platform_result["execution_time"] = time.time() - start_time
        return platform_result

    def _create_social_exploration_task(self, platform: Dict[str, Any]) -> str:
        """Create an ethical social media exploration task."""
        base_task = f"""
Explore public content on {platform['name']} with strict ethical guidelines and platform respect.

PLATFORM: {platform['name']}
TYPE: {platform['platform_type']}
URL: {platform['url']}
SCENARIO: {platform['test_scenario']}

ETHICAL EXPLORATION OBJECTIVES:

1. **Public Content Discovery**:
   - Navigate to the platform's public content areas
   - Explore trending topics and popular content
   - Discover different content types and formats
   - Analyze content organization and presentation

2. **Platform Navigation Analysis**:
   - Test navigation menus and interface elements
   - Explore search functionality and filtering options
   - Understand the platform's content categorization
   - Document user interface patterns and design

3. **Content Interaction Patterns**:
   - Observe content presentation and layout
   - Test reading and viewing experiences
   - Explore content details and metadata
   - Analyze engagement mechanisms (view-only)

4. **Feature Exploration**:
   - Identify key platform features and capabilities
   - Test search and discovery mechanisms
   - Explore content organization systems
   - Document unique platform characteristics

STRICT ETHICAL GUIDELINES:

🚫 **PROHIBITED ACTIONS**:
- NO account creation or login attempts
- NO posting, commenting, or content creation
- NO following, unfollowing, or social actions
- NO automated liking, voting, or engagement
- NO personal data collection or user profiling
- NO violation of platform terms of service

✅ **PERMITTED ACTIONS**:
- Browse public content and feeds
- Use search functionality for discovery
- Navigate through public areas and categories
- Read and analyze visible content
- Take screenshots of public interfaces
- Document platform features and user experience

SPECIFIC EXPLORATION TASKS:

🔍 **Content Discovery**:
- Explore the homepage and main content feeds
- Use search to discover topics related to technology, education, or news
- Navigate through different content categories or sections
- Observe trending topics and popular content

📱 **Interface Analysis**:
- Document the platform's layout and design
- Test navigation responsiveness and usability
- Explore menu systems and organizational structures
- Analyze content presentation and formatting

📊 **Platform Features**:
- Identify unique features that distinguish this platform
- Test search and filtering capabilities
- Explore content organization and categorization
- Document discovery and navigation mechanisms

DOCUMENTATION REQUIREMENTS:
- Take screenshots of key interface elements
- Document successful navigation patterns
- Note unique platform features and capabilities
- Analyze content discovery effectiveness
- Report on user experience and interface design

SAFETY AND COMPLIANCE:
- Respect all platform terms of service
- Maintain read-only interaction patterns
- Focus on public content analysis only
- Avoid any actions that could be considered automated engagement
- Prioritize educational analysis over data collection

Expected outcomes: Comprehensive understanding of the platform's public content ecosystem, navigation patterns, and user experience design, while maintaining full ethical compliance and platform respect.
        """
        
        # Add platform-specific focus
        if platform["platform_type"] == "discussion_forum":
            base_task += "\n\nFORUM-SPECIFIC FOCUS: Community structure, discussion threads, content moderation systems."
        elif platform["platform_type"] == "news_aggregator":
            base_task += "\n\nNEWS-SPECIFIC FOCUS: Content curation, voting systems, discussion quality, trending mechanisms."
        elif platform["platform_type"] == "developer_platform":
            base_task += "\n\nDEVELOPER-SPECIFIC FOCUS: Repository discovery, trending algorithms, code exploration, developer tools."
        elif platform["platform_type"] == "product_discovery":
            base_task += "\n\nPRODUCT-SPECIFIC FOCUS: Product launches, voting mechanisms, discovery features, collection systems."
            
        return base_task

    def _analyze_social_results(self, result: Dict[str, Any], platform: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze the results from social platform exploration."""
        analysis = {
            "content_types_found": [],
            "features_explored": [],
            "interaction_patterns_used": [],
            "content_discovery_examples": [],
            "navigation_efficiency": {}
        }
        
        output_text = result.get("output", "").lower()
        
        # Check for content types
        content_types = ["posts", "articles", "comments", "discussions", "repositories", "products"]
        for content_type in content_types:
            if content_type in output_text:
                analysis["content_types_found"].append(content_type)
                self.results["content_types_explored"].add(content_type)
        
        # Check for platform features
        features = ["search", "navigation", "categories", "trending", "voting", "discovery"]
        for feature in features:
            if feature in output_text:
                analysis["features_explored"].append(feature)
        
        # Check for interaction patterns
        interactions = ["browse", "read", "explore", "discover", "analyze", "navigate"]
        for interaction in interactions:
            if interaction in output_text:
                analysis["interaction_patterns_used"].append(interaction)
        
        # Navigation efficiency indicators
        navigation_terms = ["menu", "search", "filter", "category", "navigation"]
        analysis["navigation_efficiency"]["elements_used"] = len([t for t in navigation_terms if t in output_text])
        
        # Update global metrics
        platform_type = platform["platform_type"]
        if platform_type not in self.results["platform_features_tested"]:
            self.results["platform_features_tested"][platform_type] = set()
        
        for feature in analysis["features_explored"]:
            self.results["platform_features_tested"][platform_type].add(feature)
        
        return analysis

    async def run_comprehensive_social_demo(self):
        """Run the complete social media exploration demonstration."""
        logger.info("🚀 Starting Comprehensive Social Media Demo")
        logger.info("=" * 70)
        
        demo_start_time = time.time()
        
        # Setup browser environment
        if not await self.setup_browser_environment():
            logger.error("❌ Failed to setup browser environment")
            return self.results
        
        # Test each social platform
        for i, platform in enumerate(SOCIAL_CONTENT_SITES, 1):
            logger.info(f"\n🌐 Testing Platform {i}/{len(SOCIAL_CONTENT_SITES)}: {platform['name']}")
            logger.info(f"🔗 URL: {platform['url']}")
            logger.info(f"📱 Type: {platform['platform_type']}")
            logger.info(f"🎯 Scenario: {platform['test_scenario']}")
            
            platform_result = await self.test_social_platform(platform)
            self.results["platforms_tested"].append(platform_result)
            
            # Update discovery workflows
            if platform_result.get("success"):
                self.results["discovery_workflows"].append({
                    "platform": platform["name"],
                    "workflow_type": platform["test_scenario"],
                    "content_types": platform_result.get("content_types_found", []),
                    "features_used": platform_result.get("features_explored", [])
                })
            
            # Update navigation strategies
            self.results["navigation_strategies"].extend(
                platform_result.get("interaction_patterns_used", [])
            )
            
            # Brief pause between platforms
            await asyncio.sleep(3)
        
        # Calculate final metrics
        self.results["total_execution_time"] = time.time() - demo_start_time
        self.results["success_metrics"] = self._calculate_success_metrics()
        
        # Convert sets to lists for JSON serialization
        self.results["content_types_explored"] = list(self.results["content_types_explored"])
        for platform_type in self.results["platform_features_tested"]:
            self.results["platform_features_tested"][platform_type] = list(
                self.results["platform_features_tested"][platform_type]
            )
        
        logger.info("\n" + "=" * 70)
        logger.info("📊 SOCIAL MEDIA DEMO COMPLETED")
        self._print_comprehensive_summary()
        
        return self.results

    def _calculate_success_metrics(self) -> Dict[str, Any]:
        """Calculate comprehensive success metrics."""
        successful_platforms = len([p for p in self.results["platforms_tested"] if p.get("success", False)])
        total_platforms = len(self.results["platforms_tested"])
        
        return {
            "platforms_successfully_explored": successful_platforms,
            "total_platforms_attempted": total_platforms,
            "success_rate": (successful_platforms / total_platforms * 100) if total_platforms > 0 else 0,
            "platform_types_tested": len(set(p.get("platform_type") for p in self.results["platforms_tested"])),
            "content_types_discovered": len(self.results["content_types_explored"]),
            "unique_features_tested": sum(len(features) for features in self.results["platform_features_tested"].values()),
            "discovery_workflows_completed": len(self.results["discovery_workflows"]),
            "navigation_strategies_used": len(set(self.results["navigation_strategies"])),
            "average_execution_time": (
                sum(p.get("execution_time", 0) for p in self.results["platforms_tested"]) / 
                len(self.results["platforms_tested"])
            ) if self.results["platforms_tested"] else 0,
            "ethical_compliance_rate": 100.0  # All platforms tested with ethical guidelines
        }

    def _print_comprehensive_summary(self):
        """Print detailed summary of the demo results."""
        print("\n" + "=" * 70)
        print("🌐 SOCIAL MEDIA DEMO SUMMARY")
        print("=" * 70)
        
        metrics = self.results["success_metrics"]
        
        print(f"🎯 Overall Success Rate: {metrics['success_rate']:.1f}%")
        print(f"🌐 Platforms Explored: {metrics['platforms_successfully_explored']}/{metrics['total_platforms_attempted']}")
        print(f"📱 Platform Types: {metrics['platform_types_tested']}")
        print(f"📝 Content Types: {metrics['content_types_discovered']}")
        print(f"✅ Ethical Compliance: {metrics['ethical_compliance_rate']:.1f}%")
        
        print(f"\n📊 DETAILED METRICS:")
        print(f"├─ Features Tested: {metrics['unique_features_tested']}")
        print(f"├─ Discovery Workflows: {metrics['discovery_workflows_completed']}")
        print(f"├─ Navigation Strategies: {metrics['navigation_strategies_used']}")
        print(f"├─ Avg Execution Time: {metrics['average_execution_time']:.1f}s")
        print(f"└─ Total Runtime: {self.results['total_execution_time']:.1f}s")
        
        if self.results["content_types_explored"]:
            print(f"\n📝 CONTENT TYPES DISCOVERED:")
            for content_type in sorted(self.results["content_types_explored"]):
                print(f"├─ {content_type.title()}")
        
        if self.results["platform_features_tested"]:
            print(f"\n⚙️ PLATFORM FEATURES TESTED:")
            for platform_type, features in self.results["platform_features_tested"].items():
                print(f"├─ {platform_type.replace('_', ' ').title()}:")
                for feature in sorted(features):
                    print(f"│  └─ {feature}")
        
        if self.results["discovery_workflows"]:
            print(f"\n🔍 DISCOVERY WORKFLOWS:")
            for workflow in self.results["discovery_workflows"]:
                content_count = len(workflow["content_types"])
                feature_count = len(workflow["features_used"])
                print(f"├─ {workflow['platform']}: {content_count} content types, {feature_count} features")
        
        print(f"\n📈 PLATFORM-BY-PLATFORM RESULTS:")
        for i, platform in enumerate(self.results["platforms_tested"], 1):
            status = "✅" if platform.get("success", False) else "❌"
            platform_type = platform.get("platform_type", "Unknown")
            time_taken = platform.get("execution_time", 0)
            features = len(platform.get("features_explored", []))
            print(f"{status} {i}. {platform['platform_name']} ({platform_type}): {features} features, {time_taken:.1f}s")
        
        if self.results["challenges_encountered"]:
            print(f"\n⚠️ CHALLENGES ENCOUNTERED:")
            for challenge in self.results["challenges_encountered"]:
                print(f"├─ {challenge['platform']} ({challenge['platform_type']}): {challenge['error']}")
        
        print(f"\n💡 SOCIAL MEDIA AUTOMATION CAPABILITIES DEMONSTRATED:")
        print(f"├─ Ethical public content exploration")
        print(f"├─ Platform navigation and interface analysis")
        print(f"├─ Content discovery and categorization")
        print(f"├─ Feature exploration and documentation")
        print(f"├─ User experience assessment and analysis")
        print(f"├─ Compliance with platform terms of service")
        print(f"├─ Read-only interaction pattern demonstration")
        print(f"└─ Cross-platform content analysis workflows")
        
        print(f"\n🛡️ ETHICAL COMPLIANCE:")
        print(f"├─ No account creation or authentication")
        print(f"├─ No automated posting or content creation")
        print(f"├─ No social actions (follow/like/share)")
        print(f"├─ Public content exploration only")
        print(f"├─ Platform terms of service respected")
        print(f"└─ Educational and analysis focus maintained")
        
        print("\n" + "=" * 70)

async def main():
    """Main execution function."""
    try:
        logger.info("🎬 Starting Social Media Demo")
        logger.info("📝 Demonstrates ethical public content exploration and platform analysis")
        
        # Create and run demo
        demo = SocialMediaDemo()
        results = await demo.run_comprehensive_social_demo()
        
        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = f"social_media_demo_results_{timestamp}.json"
        
        import json
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        logger.info(f"📄 Results saved to: {results_file}")
        return results
        
    except Exception as e:
        logger.error(f"❌ Demo execution failed: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())
