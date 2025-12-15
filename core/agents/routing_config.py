"""
Unified Routing Configuration - Single Source of Truth
=======================================================

Session 454: Created to consolidate agent definitions from multiple locations.

PREVIOUSLY, agent keywords/capabilities were defined in:
- core/agents/personal_assistant_agent.py (INTENT_KEYWORDS)
- core/services/semantic_routing.py (AGENT_CAPABILITIES)
- core/prompts/tool_descriptions.py (tool descriptions)

NOW, all routing-related definitions live here and are imported by those modules.

Usage:
    from core.agents.routing_config import (
        AGENT_ROUTING_CONFIG,
        get_intent_keywords,
        get_semantic_capabilities,
        get_priority_keywords
    )
"""

from typing import Dict, List, Any

# =============================================================================
# UNIFIED AGENT ROUTING CONFIGURATION
# =============================================================================
# Each agent has:
#   - description: What the agent does (used for semantic routing)
#   - examples: Example queries this agent handles (used for semantic embeddings)
#   - keywords: Keywords for fallback matching (used by PersonalAssistant)
#   - category: Agent category for organization
#   - priority: Higher = checked first in keyword matching (default 0)

AGENT_ROUTING_CONFIG: Dict[str, Dict[str, Any]] = {
    # =========================================================================
    # CREATION AGENTS
    # =========================================================================
    "ImageAgent": {
        "description": "Generate images, logos, banners, illustrations, graphics, icons, avatars, and visual content from text descriptions",
        "examples": [
            "create a logo for my tech startup",
            "generate a cyberpunk city illustration",
            "make a banner for my YouTube channel",
            "design an icon for my app",
            "create a watercolor portrait",
        ],
        "keywords": [
            "logo", "banner", "image", "picture", "illustration", "icon", "graphic",
            "thumbnail", "avatar", "portrait", "landscape", "poster", "flyer"
        ],
        "category": "creation",
        "priority": 0,
    },
    "VideoAgent": {
        "description": "Create videos, animations, motion graphics, and animate still images into video content",
        "examples": [
            "create a video showing a sunset over mountains",
            "animate this logo into a video",
            "make a motion graphic for my intro",
            "generate a promotional video",
        ],
        "keywords": [
            "video", "animate", "animation", "motion", "clip", "movie"
        ],
        "category": "creation",
        "priority": 0,
    },
    "AudioAgent": {
        "description": "Generate audio content including text-to-speech, voiceovers, narration, and sound effects",
        "examples": [
            "create a voiceover for my video",
            "generate text-to-speech narration",
            "make an audio introduction",
            "create sound effects for my game",
        ],
        "keywords": [
            "audio", "voice", "speech", "voiceover", "narration", "sound", "tts"
        ],
        "category": "creation",
        "priority": 10,  # Higher priority for specific audio keywords
    },
    "ThreeDAgent": {
        "description": "Create 3D models, convert images to 3D objects for printing or rendering",
        "examples": [
            "convert this image to a 3D model",
            "create a 3D object from this logo",
            "make a 3D printable version",
            "generate a 3D mesh",
        ],
        "keywords": [
            "3d", "three-dimensional", "model", "mesh", "sculpture"
        ],
        "category": "creation",
        "priority": 10,  # Higher priority - specific domain
    },

    # =========================================================================
    # EDITING AGENTS
    # =========================================================================
    "ImageEditingAgent": {
        "description": "Edit existing images - upscale, remove background, recolor, create variations, search and replace objects",
        "examples": [
            "upscale image 5 to 4x resolution",
            "remove the background from this image",
            "make the logo blue instead of red",
            "create 3 variations of this design",
        ],
        "keywords": [
            "upscale", "enlarge", "remove background", "transparent", "recolor",
            "variations", "edit image", "modify image", "change color"
        ],
        "category": "editing",
        "priority": 20,  # Higher priority for compound keywords
    },
    "VideoEditingAgent": {
        "description": "Edit existing videos - trim, add effects, slow motion, add text overlays, concatenate clips",
        "examples": [
            "trim this video to 30 seconds",
            "add slow motion effect",
            "add text overlay to the video",
            "combine these video clips",
        ],
        "keywords": [
            "trim", "cut", "edit video", "add text to video", "effects", "slow motion",
            "speed up", "concatenate", "merge videos"
        ],
        "category": "editing",
        "priority": 20,  # Higher priority for compound keywords
    },

    # =========================================================================
    # RESEARCH AGENTS
    # =========================================================================
    "ResearchAgent": {
        "description": "Search the web and spider network for trending topics, news, and general information",
        "examples": [
            "what's trending in design right now",
            "find the latest AI news",
            "search for web development trends",
            "what's hot in cybersecurity",
        ],
        "keywords": [
            "search", "find", "trending", "what is", "insights", "hot in", "hot right now", "whats hot"
        ],
        "category": "research",
        "priority": 0,
    },
    "CompetitorAnalysisAgent": {
        "description": "Research business markets, analyze competitors, create SWOT analysis, evaluate startup ideas and business landscapes",
        "examples": [
            "research the AI writing assistant market for my startup idea",
            "analyze competitors in the coffee subscription space",
            "do a SWOT analysis for project management tools",
            "who are the main competitors in ed-tech",
            "research the competitive landscape for my business idea",
        ],
        "keywords": [
            "market", "competition", "competitors", "competitor", "startup", "business idea",
            "swot", "analyze market", "research market", "competitive", "landscape",
            "who are the competitors", "market analysis", "industry analysis", "for my startup"
        ],
        "category": "research",
        "priority": 5,
    },
    "CustomerResearchAgent": {
        "description": "Build customer personas, research pain points, analyze customer sentiment and needs from forums and social media",
        "examples": [
            "build customer personas for fitness apps",
            "what are the pain points for project management users",
            "research customer needs for food delivery",
            "who are the target customers for online education",
        ],
        "keywords": [
            "customer", "customers", "personas", "persona", "pain points", "customer needs",
            "who buys", "target audience", "user research", "customer research", "sentiment"
        ],
        "category": "research",
        "priority": 5,
    },

    # =========================================================================
    # STRATEGY AGENTS
    # =========================================================================
    "BrandIdentityAgent": {
        "description": "Develop brand identity including colors, typography, style guidelines, and visual consistency",
        "examples": [
            "help me develop my brand colors",
            "what typography should my brand use",
            "create brand guidelines for consistency",
        ],
        "keywords": [
            "brand identity", "brand colors", "brand style", "color palette", "brand guidelines",
            "visual identity", "brand consistency", "brand voice", "brand look"
        ],
        "category": "strategy",
        "priority": 5,
    },
    "ContentStrategyAgent": {
        "description": "Develop content strategy, recommend what to create, plan content calendars based on trends",
        "examples": [
            "what content should I create for my tech blog",
            "develop a content strategy for my YouTube channel",
            "recommend topics for my newsletter",
        ],
        "keywords": [
            "content strategy", "content plan", "content calendar", "what to post",
            "content ideas", "content pillars", "editorial calendar"
        ],
        "category": "strategy",
        "priority": 5,
    },
    "SEOOptimizerAgent": {
        "description": "Optimize content for search engines with keywords, hashtags, meta descriptions",
        "examples": [
            "what keywords should I target",
            "help me with SEO for my blog post",
            "suggest hashtags for my post",
        ],
        "keywords": [
            "seo", "keywords", "hashtags", "meta description", "search optimization",
            "meta tags", "keyword research", "ranking"
        ],
        "category": "strategy",
        "priority": 5,
    },
    "SocialMediaAgent": {
        "description": "Develop social media strategies, optimize content for different platforms",
        "examples": [
            "what should I post on Instagram",
            "help me with my TikTok strategy",
            "optimize this for LinkedIn",
        ],
        "keywords": [
            "social media", "social strategy", "instagram", "tiktok", "linkedin",
            "twitter", "platform strategy", "social posts", "engagement"
        ],
        "category": "strategy",
        "priority": 5,
    },

    # =========================================================================
    # EXECUTIVE AGENTS
    # =========================================================================
    "CTOAgent": {
        "description": "Provide technical planning, architecture guidance, and technology stack recommendations",
        "examples": [
            "what tech stack should I use",
            "help me design the system architecture",
            "evaluate technical trade-offs",
        ],
        "keywords": [
            "technical", "architecture", "tech stack", "infrastructure", "cto",
            "technical planning", "system design", "scalability"
        ],
        "category": "executive",
        "priority": 5,
    },
    "COOAgent": {
        "description": "Provide operations planning, process optimization, and risk analysis",
        "examples": [
            "help me optimize my operations",
            "what are the operational risks",
            "improve my workflows",
        ],
        "keywords": [
            "operations", "coo", "operational", "processes", "efficiency",
            "risk analysis", "operational planning", "workflows"
        ],
        "category": "executive",
        "priority": 5,
    },
    "CreativeDirectorAgent": {
        "description": "Provide creative direction, art direction, and design guidance",
        "examples": [
            "help me with creative direction",
            "what visual style should I use",
            "guide my design decisions",
        ],
        "keywords": [
            "creative direction", "creative brief", "art direction", "creative guidance",
            "visual direction", "design direction", "creative strategy"
        ],
        "category": "executive",
        "priority": 5,
    },

    # =========================================================================
    # ANALYSIS AGENTS
    # =========================================================================
    "TrendAnalysisAgent": {
        "description": "Analyze market trends, emerging patterns, and industry movements",
        "examples": [
            "analyze current AI trends",
            "what trends are emerging in fintech",
            "give me a trend report",
        ],
        "keywords": [
            "trends", "trend analysis", "market trends", "emerging trends",
            "what's trending", "industry trends", "trend report"
        ],
        "category": "analysis",
        "priority": 5,
    },
    "OpportunityScoringAgent": {
        "description": "Score and evaluate business opportunities for viability and potential",
        "examples": [
            "score this business opportunity",
            "evaluate the viability of this idea",
            "rate this opportunity",
        ],
        "keywords": [
            "opportunity score", "score opportunity", "rate opportunity", "evaluate opportunity",
            "opportunity assessment", "viability score", "business viability"
        ],
        "category": "analysis",
        "priority": 5,
    },

    # =========================================================================
    # TRAINING AGENTS
    # =========================================================================
    "CharacterTrainingAgent": {
        "description": "Train custom character models using FLUX LoRA for consistent character generation",
        "examples": [
            "train a model on my character",
            "create a LoRA for my mascot",
            "fine-tune on these reference images",
        ],
        "keywords": [
            "train character", "lora training", "train model", "character training",
            "fine tune", "custom model", "train on images"
        ],
        "category": "training",
        "priority": 10,
    },
    "TrainedCreationAgent": {
        "description": "Generate images using previously trained LoRA models for consistent characters",
        "examples": [
            "use my trained character model",
            "generate with my custom LoRA",
            "create image with my trained model",
        ],
        "keywords": [
            "use trained model", "use lora", "trained character", "my character",
            "custom character", "generate with lora"
        ],
        "category": "training",
        "priority": 10,
    },

    # =========================================================================
    # LEGAL AGENT
    # =========================================================================
    "LegalDocDrafterAgent": {
        "description": "Provide general legal information for Colorado family law, help with motion templates and court procedures (NOT legal advice)",
        "examples": [
            "help me understand custody procedures",
            "what forms do I need for divorce",
            "explain parenting time modifications",
        ],
        "keywords": [
            "legal", "law", "lawyer", "attorney", "court", "judge", "lawsuit",
            "divorce", "custody", "child support", "parenting time", "visitation",
            "motion", "file motion", "declaration", "subpoena", "served",
            "pro se", "self-represented", "family law", "family court",
            "jdf", "colorado court", "colorado divorce", "colorado custody",
            "modification", "enforce", "order", "decree", "separation",
            "parental responsibilities", "parenting plan", "child custody",
            "denied", "denied motion", "motion denied", "rejected", "dismissal",
            "rewrite motion", "fix motion", "correct motion", "refile",
            "magistrate", "ruling", "contempt", "affidavit",
        ],
        "category": "legal",
        "priority": 30,  # High priority - legal terms should always route here
    },

    # =========================================================================
    # ORCHESTRATION AGENT
    # =========================================================================
    "WorkflowAgent": {
        "description": "Execute multi-step workflows that combine research and creation, like research-and-create logo packages or brand identity kits",
        "examples": [
            "research and create 3 logos for my AI startup",
            "create a complete brand identity package",
            "make a YouTube thumbnail package with research",
            "research trending styles and create banners",
        ],
        "keywords": [
            "research and create", "brand identity", "package", "complete", "full",
            "end to end", "workflow", "step by step"
        ],
        "category": "orchestration",
        "priority": 25,  # High priority for multi-step workflows
    },
}


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def get_intent_keywords() -> Dict[str, List[str]]:
    """
    Get keywords for all agents.
    
    Used by PersonalAssistantAgent for keyword-based routing.

    Returns:
        Dict mapping agent name to list of keywords
    """
    return {
        name: info["keywords"]
        for name, info in AGENT_ROUTING_CONFIG.items()
    }


def get_semantic_capabilities() -> Dict[str, Dict[str, Any]]:
    """
    Get capabilities for semantic routing.

    Used by SemanticRoutingService for embedding-based routing.

    Returns:
        Dict compatible with AGENT_CAPABILITIES in semantic_routing.py
    """
    return {
        name: {
            "description": info["description"],
            "examples": info["examples"],
            "keywords": info["keywords"],
        }
        for name, info in AGENT_ROUTING_CONFIG.items()
    }


def get_agents_by_category(category: str) -> List[str]:
    """Get list of agent names in a category."""
    return [
        name for name, info in AGENT_ROUTING_CONFIG.items()
        if info.get("category") == category
    ]


def get_agent_routing_info(agent_name: str) -> Dict[str, Any]:
    """Get full routing info for a specific agent."""
    return AGENT_ROUTING_CONFIG.get(agent_name, {})


def get_priority_sorted_agents() -> List[tuple]:
    """
    Get agents sorted by priority (highest first).
    
    Used for keyword matching where higher priority agents
    should be checked first.

    Returns:
        List of (agent_name, keywords, priority) tuples
    """
    agents_with_priority = [
        (name, info["keywords"], info.get("priority", 0))
        for name, info in AGENT_ROUTING_CONFIG.items()
    ]
    return sorted(agents_with_priority, key=lambda x: x[2], reverse=True)


# Agent categories for organization
AGENT_CATEGORIES = [
    "creation",
    "editing",
    "research",
    "strategy",
    "executive",
    "analysis",
    "training",
    "legal",
    "orchestration",
]
