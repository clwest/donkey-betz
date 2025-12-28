"""
AI Content Creation Agents Registry
====================================

Session 219: Defines specialized agents for AI Content Creation platform.
Session 266: Updated to use central prompt registry.

These agents receive intelligence from the 70 spiders and provide:
- Trend analysis and recommendations
- Style suggestions and inspiration
- Content ideas and opportunities
- Workflow optimization

Each agent is designed to receive specific spider data categories
and transform them into actionable intelligence for users.

NOTE: Agent prompts are now defined in core/prompts/registry.py
"""

import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum

logger = logging.getLogger(__name__)

# Session 266: Import from central registry
try:
    from core.prompts import get_agent_prompt
    REGISTRY_AVAILABLE = True
except ImportError:
    REGISTRY_AVAILABLE = False
    logger.warning("Prompt registry not available, using legacy prompts")


class AgentCapability(Enum):
    """Capabilities that agents can have"""
    IMAGE_GENERATION = "image_generation"
    VIDEO_GENERATION = "video_generation"
    AUDIO_GENERATION = "audio_generation"
    STYLE_ANALYSIS = "style_analysis"
    TREND_DETECTION = "trend_detection"
    PROMPT_ENGINEERING = "prompt_engineering"
    CONTENT_STRATEGY = "content_strategy"
    MARKET_ANALYSIS = "market_analysis"
    DESIGN_SYSTEM = "design_system"
    TEMPLATE_CURATION = "template_curation"
    OPPORTUNITY_SCANNING = "opportunity_scanning"
    RESEARCH = "research"


@dataclass
class AIContentAgent:
    """Definition of an AI Content Creation agent"""
    name: str
    description: str
    capabilities: List[AgentCapability]
    data_interests: List[str]  # Spider categories this agent is interested in
    prompt_template: str = ""  # Session 266: Now optional, pulls from registry
    is_active: bool = True
    priority: int = 5  # 1-10, higher = more important
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def get_prompt(self) -> str:
        """Session 266: Get prompt from registry, fallback to template."""
        if REGISTRY_AVAILABLE:
            # Try to get from central registry first
            registry_prompt = get_agent_prompt(self.name, include_platform_context=True)
            if registry_prompt and len(registry_prompt) > 100:
                return registry_prompt
        # Fallback to legacy prompt_template
        return self.prompt_template

    def get_context_prompt(self, intelligence_data: List[Dict]) -> str:
        """Generate context-enhanced prompt with spider intelligence"""
        base_prompt = self.get_prompt()

        if not intelligence_data:
            return base_prompt

        # Format intelligence into context
        intel_summary = self._format_intelligence(intelligence_data)

        return f"""{base_prompt}

## Current Intelligence ({len(intelligence_data)} items):
{intel_summary}
"""

    def _format_intelligence(self, data: List[Dict]) -> str:
        """Format intelligence data for prompt injection"""
        lines = []
        for item in data[:10]:  # Limit to 10 most recent
            source = item.get('spider_name', 'unknown')
            title = item.get('data', {}).get('title', item.get('title', 'No title'))
            timestamp = item.get('timestamp', '')
            lines.append(f"- [{source}] {title}")

        return "\n".join(lines) if lines else "No recent intelligence available."


# Agent Registry
AI_CONTENT_AGENTS: Dict[str, AIContentAgent] = {}


def register_agent(agent: AIContentAgent) -> None:
    """Register an agent in the registry"""
    AI_CONTENT_AGENTS[agent.name] = agent
    logger.info(f"Registered AI Content Agent: {agent.name}")


def get_agent(name: str) -> Optional[AIContentAgent]:
    """Get an agent by name"""
    return AI_CONTENT_AGENTS.get(name)


def get_all_agents() -> Dict[str, AIContentAgent]:
    """Get all registered agents"""
    return AI_CONTENT_AGENTS


def get_agents_by_capability(capability: AgentCapability) -> List[AIContentAgent]:
    """Get agents with a specific capability"""
    return [
        agent for agent in AI_CONTENT_AGENTS.values()
        if capability in agent.capabilities
    ]


def get_agents_for_spider_category(category: str) -> List[AIContentAgent]:
    """Get agents interested in a spider category"""
    return [
        agent for agent in AI_CONTENT_AGENTS.values()
        if category in agent.data_interests
    ]


# =============================================================================
# Register Default AI Content Creation Agents
# =============================================================================

# Image Generation Agent
register_agent(AIContentAgent(
    name="image_generation_agent",
    description="Analyzes trends and suggests optimal prompts for image generation",
    capabilities=[
        AgentCapability.IMAGE_GENERATION,
        AgentCapability.STYLE_ANALYSIS,
        AgentCapability.PROMPT_ENGINEERING
    ],
    data_interests=["creative_assets", "ai_creative", "design"],
    prompt_template="""You are an expert image generation assistant.
Your role is to help users create stunning images using AI tools like Stability AI.
You analyze current trends from creative marketplaces and AI art communities
to suggest optimal prompts, styles, and parameters.""",
    priority=10
))

# Video Generation Agent
register_agent(AIContentAgent(
    name="video_generation_agent",
    description="Helps create compelling video content with AI",
    capabilities=[
        AgentCapability.VIDEO_GENERATION,
        AgentCapability.STYLE_ANALYSIS,
        AgentCapability.CONTENT_STRATEGY
    ],
    data_interests=["ai_creative", "content_creation"],
    prompt_template="""You are an expert video creation assistant.
Your role is to help users create engaging videos using AI tools like Runway ML.
You understand current video trends and can suggest optimal approaches
for different content types and platforms.""",
    priority=9
))

# Style Discovery Agent
register_agent(AIContentAgent(
    name="style_discovery_agent",
    description="Discovers and tracks trending visual styles",
    capabilities=[
        AgentCapability.STYLE_ANALYSIS,
        AgentCapability.TREND_DETECTION
    ],
    data_interests=["creative_assets", "ai_creative", "design"],
    prompt_template="""You are a visual style analyst and trend forecaster.
Your role is to identify emerging design trends, popular styles, and
aesthetic movements from creative communities. You help users stay
ahead of visual trends and adopt styles that resonate with audiences.""",
    priority=8
))

# Prompt Engineering Agent
register_agent(AIContentAgent(
    name="prompt_engineering_agent",
    description="Optimizes prompts for AI image and video generation",
    capabilities=[
        AgentCapability.PROMPT_ENGINEERING,
        AgentCapability.IMAGE_GENERATION,
        AgentCapability.VIDEO_GENERATION
    ],
    data_interests=["ai_creative"],
    prompt_template="""You are an expert prompt engineer for AI generation tools.
Your role is to craft optimal prompts that produce the best results
from tools like Stable Diffusion, DALL-E, and Midjourney. You understand
the nuances of different models and can adapt prompts for each.""",
    priority=9
))

# Model Recommender Agent
register_agent(AIContentAgent(
    name="model_recommender_agent",
    description="Recommends optimal AI models for specific tasks",
    capabilities=[
        AgentCapability.IMAGE_GENERATION,
        AgentCapability.VIDEO_GENERATION,
        AgentCapability.RESEARCH
    ],
    data_interests=["ai_creative", "tech", "innovation"],
    prompt_template="""You are an AI model specialist who tracks the latest
developments in generative AI. Your role is to recommend the best models,
LoRAs, and checkpoints for specific creative tasks based on quality,
speed, and suitability for the user's goals.""",
    priority=7
))

# Product Idea Agent
register_agent(AIContentAgent(
    name="product_idea_agent",
    description="Generates digital product ideas from market intelligence",
    capabilities=[
        AgentCapability.MARKET_ANALYSIS,
        AgentCapability.TREND_DETECTION,
        AgentCapability.CONTENT_STRATEGY
    ],
    data_interests=["digital_products", "creative_assets"],
    prompt_template="""You are a digital product strategist who identifies
profitable opportunities in marketplaces like Etsy, Gumroad, and Creative Market.
Your role is to suggest product ideas based on trending demands,
gaps in the market, and successful product patterns.""",
    priority=8
))

# Content Strategy Agent
register_agent(AIContentAgent(
    name="content_strategy_agent",
    description="Develops content strategies based on current trends",
    capabilities=[
        AgentCapability.CONTENT_STRATEGY,
        AgentCapability.TREND_DETECTION,
        AgentCapability.MARKET_ANALYSIS
    ],
    data_interests=["content_creation", "digital_products", "news", "tech"],
    prompt_template="""You are a content strategist who helps creators
build effective content plans. Your role is to analyze current trends,
identify content opportunities, and suggest topics that will resonate
with target audiences based on real-time market intelligence.""",
    priority=8
))

# Design Assistant Agent
register_agent(AIContentAgent(
    name="design_assistant_agent",
    description="Provides design guidance and inspiration",
    capabilities=[
        AgentCapability.DESIGN_SYSTEM,
        AgentCapability.STYLE_ANALYSIS,
        AgentCapability.TEMPLATE_CURATION
    ],
    data_interests=["design", "creative_assets", "content_creation"],
    prompt_template="""You are a design assistant who helps users create
professional visual content. Your role is to provide design guidance,
suggest color palettes, typography, and layouts based on current
design trends and best practices.""",
    priority=7
))

# Trend Analysis Agent
register_agent(AIContentAgent(
    name="trend_analysis_agent",
    description="Analyzes cross-platform trends for content creation",
    capabilities=[
        AgentCapability.TREND_DETECTION,
        AgentCapability.MARKET_ANALYSIS,
        AgentCapability.RESEARCH
    ],
    data_interests=["tech", "innovation", "news", "design", "digital_products"],
    prompt_template="""You are a trend analyst who monitors multiple platforms
and data sources to identify emerging opportunities. Your role is to
synthesize information from tech news, social media, marketplaces,
and creative communities into actionable insights.""",
    priority=9
))

# Research Agent
register_agent(AIContentAgent(
    name="research_agent",
    description="Conducts research and synthesizes information",
    capabilities=[
        AgentCapability.RESEARCH,
        AgentCapability.TREND_DETECTION
    ],
    data_interests=["tech", "innovation", "education", "legal"],
    prompt_template="""You are a research specialist who gathers and
synthesizes information from multiple sources. Your role is to
provide comprehensive research on topics, technologies, and
market opportunities.""",
    priority=6
))

# Template Curator Agent
register_agent(AIContentAgent(
    name="template_curator_agent",
    description="Curates and recommends templates for various use cases",
    capabilities=[
        AgentCapability.TEMPLATE_CURATION,
        AgentCapability.DESIGN_SYSTEM
    ],
    data_interests=["creative_assets", "content_creation", "digital_products"],
    prompt_template="""You are a template specialist who understands
the best templates for different use cases. Your role is to
recommend templates for presentations, social media, documents,
and other content based on the user's needs and current trends.""",
    priority=6
))

# Opportunity Scanner Agent
register_agent(AIContentAgent(
    name="opportunity_scanner_agent",
    description="Scans for freelance and business opportunities",
    capabilities=[
        AgentCapability.OPPORTUNITY_SCANNING,
        AgentCapability.MARKET_ANALYSIS
    ],
    data_interests=["freelance", "remote_work", "digital_products"],
    prompt_template="""You are an opportunity scout who identifies
relevant freelance gigs, remote jobs, and business opportunities.
Your role is to match opportunities with user skills and
highlight the most promising prospects.""",
    priority=7
))

# Brand Identity Agent
register_agent(AIContentAgent(
    name="brand_identity_agent",
    description="Helps create cohesive brand identities",
    capabilities=[
        AgentCapability.DESIGN_SYSTEM,
        AgentCapability.STYLE_ANALYSIS,
        AgentCapability.IMAGE_GENERATION
    ],
    data_interests=["creative_assets", "design"],
    prompt_template="""You are a brand identity specialist who helps
create cohesive visual identities. Your role is to guide users
in developing logos, color schemes, typography, and brand
guidelines that communicate their unique value proposition.""",
    priority=7
))

# Innovation Scout Agent
register_agent(AIContentAgent(
    name="innovation_scout_agent",
    description="Identifies emerging technologies and innovations",
    capabilities=[
        AgentCapability.RESEARCH,
        AgentCapability.TREND_DETECTION
    ],
    data_interests=["tech", "innovation"],
    prompt_template="""You are an innovation scout who tracks emerging
technologies and breakthroughs. Your role is to identify new tools,
techniques, and platforms that could benefit content creators
and keep users ahead of the technology curve.""",
    priority=6
))


# =============================================================================
# Agent Intelligence Service
# =============================================================================

class AgentIntelligenceService:
    """Service for managing agent intelligence feeds"""

    def __init__(self):
        self.intelligence_cache: Dict[str, List[Dict]] = {}

    def add_intelligence(self, agent_name: str, data: Dict[str, Any]) -> None:
        """Add intelligence data for an agent"""
        if agent_name not in self.intelligence_cache:
            self.intelligence_cache[agent_name] = []

        self.intelligence_cache[agent_name].insert(0, {
            **data,
            'received_at': datetime.now(timezone.utc).isoformat()
        })

        # Keep only last 100 items per agent
        self.intelligence_cache[agent_name] = self.intelligence_cache[agent_name][:100]

    def get_intelligence(self, agent_name: str, limit: int = 10) -> List[Dict]:
        """Get intelligence data for an agent"""
        return self.intelligence_cache.get(agent_name, [])[:limit]

    def get_all_intelligence(self, limit: int = 50) -> Dict[str, List[Dict]]:
        """Get intelligence for all agents"""
        return {
            name: data[:limit]
            for name, data in self.intelligence_cache.items()
        }

    def get_trending_topics(self, limit: int = 10) -> List[Dict]:
        """Extract trending topics across all agents"""
        all_items = []
        for items in self.intelligence_cache.values():
            all_items.extend(items)

        # Sort by recency and return top items
        sorted_items = sorted(
            all_items,
            key=lambda x: x.get('received_at', ''),
            reverse=True
        )

        return sorted_items[:limit]

    def clear_cache(self, agent_name: Optional[str] = None) -> None:
        """Clear intelligence cache"""
        if agent_name:
            self.intelligence_cache.pop(agent_name, None)
        else:
            self.intelligence_cache.clear()


# Global service instance
agent_intelligence_service = AgentIntelligenceService()


# =============================================================================
# Summary Statistics
# =============================================================================

def get_agent_stats() -> Dict[str, Any]:
    """Get statistics about registered agents"""
    agents = AI_CONTENT_AGENTS.values()

    capability_counts = {}
    for agent in agents:
        for cap in agent.capabilities:
            capability_counts[cap.value] = capability_counts.get(cap.value, 0) + 1

    interest_counts = {}
    for agent in agents:
        for interest in agent.data_interests:
            interest_counts[interest] = interest_counts.get(interest, 0) + 1

    return {
        'total_agents': len(AI_CONTENT_AGENTS),
        'active_agents': sum(1 for a in agents if a.is_active),
        'capability_distribution': capability_counts,
        'interest_distribution': interest_counts,
        'agents_by_priority': sorted(
            [(a.name, a.priority) for a in agents],
            key=lambda x: x[1],
            reverse=True
        )
    }


# Log registration summary on import
logger.info(f"AI Content Agents Registry initialized with {len(AI_CONTENT_AGENTS)} agents")
