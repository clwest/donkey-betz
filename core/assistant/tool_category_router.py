"""
Tool Category Router
Session 806: Two-stage tool routing for Personal Assistant.

This service:
1. Classifies user messages into tool categories
2. Returns only relevant tools for that category
3. Falls back to full toolset for complex requests

The goal is to reduce tool definitions from ~1,300 tokens (47 tools)
down to ~200-400 tokens (5-10 tools) per request.
"""

import logging
from typing import Dict, Any, Optional, List, Set
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class ToolCategory(Enum):
    """Categories of tools based on function."""
    CREATION = "creation"           # Image, video, audio, 3D creation
    EDITING = "editing"             # Image/video editing operations
    RESEARCH = "research"           # Web search, content writing
    BUSINESS = "business"           # Competitor, customer, brand analysis
    DEVELOPMENT = "development"     # Code generation, review, devops
    SYSTEM = "system"               # Body vitals, workspace, budget
    INTELLIGENCE = "intelligence"   # Predictions, gates, pilots, reasoning
    ORCHESTRATION = "orchestration" # Workflows, pipelines, revenue
    UNIVERSAL = "universal"         # Universal agent tool
    ALL = "all"                     # All tools (fallback)


@dataclass
class CategoryMatch:
    """Result of category classification."""
    primary: ToolCategory
    secondary: Optional[ToolCategory]
    confidence: float
    matched_keywords: List[str]


class ToolCategoryRouter:
    """
    Session 806: Routes tool selection based on message classification.

    Usage:
        from core.assistant.tool_category_router import get_tool_category_router

        router = get_tool_category_router()

        # Get tools for a message
        tools = router.get_tools_for_message(message, all_tools)
    """

    # Map tool names to categories
    TOOL_CATEGORIES: Dict[str, ToolCategory] = {
        # CREATION
        'image_generation_agent': ToolCategory.CREATION,
        'video_generation_agent': ToolCategory.CREATION,
        'audio_generation_agent': ToolCategory.CREATION,
        'three_d_generation_agent': ToolCategory.CREATION,
        'talking_character_agent': ToolCategory.CREATION,
        'character_training_agent': ToolCategory.CREATION,

        # EDITING
        'image_editing_agent': ToolCategory.EDITING,
        'video_editing_agent': ToolCategory.EDITING,

        # RESEARCH
        'web_search': ToolCategory.RESEARCH,
        'content_writer_agent': ToolCategory.RESEARCH,
        'strategic_review': ToolCategory.RESEARCH,

        # BUSINESS
        'competitor_analysis_agent': ToolCategory.BUSINESS,
        'customer_research_agent': ToolCategory.BUSINESS,
        'brand_strategy_agent': ToolCategory.BUSINESS,
        'content_strategy_agent': ToolCategory.BUSINESS,
        'marketing_strategy_agent': ToolCategory.BUSINESS,
        'legal_doc_drafter_agent': ToolCategory.BUSINESS,

        # DEVELOPMENT
        'coleadership_agent': ToolCategory.DEVELOPMENT,
        'create_project_from_research': ToolCategory.DEVELOPMENT,
        'create_brand_video': ToolCategory.DEVELOPMENT,

        # SYSTEM
        'body_vitals': ToolCategory.SYSTEM,
        'workspace_tool': ToolCategory.SYSTEM,
        'check_budget': ToolCategory.SYSTEM,
        'system_alerts': ToolCategory.SYSTEM,

        # INTELLIGENCE
        'predictions_tool': ToolCategory.INTELLIGENCE,
        'gates_tool': ToolCategory.INTELLIGENCE,
        'pilots_tool': ToolCategory.INTELLIGENCE,
        'reasoning_engine': ToolCategory.INTELLIGENCE,
        'human_decisions_tool': ToolCategory.INTELLIGENCE,

        # ORCHESTRATION
        'workflow_orchestration_agent': ToolCategory.ORCHESTRATION,
        'opportunity_manager': ToolCategory.ORCHESTRATION,
        'task_manager': ToolCategory.ORCHESTRATION,
        'pipeline_orchestrator': ToolCategory.ORCHESTRATION,
        'revenue_tracker': ToolCategory.ORCHESTRATION,
        'ml_analysis': ToolCategory.ORCHESTRATION,

        # UNIVERSAL
        'universal_agent': ToolCategory.UNIVERSAL,
    }

    # Keywords that trigger each category
    CATEGORY_KEYWORDS: Dict[ToolCategory, List[str]] = {
        ToolCategory.CREATION: [
            'create', 'generate', 'make', 'design', 'draw', 'produce',
            'image', 'photo', 'picture', 'video', 'audio', 'music', 'sound',
            '3d', 'model', 'animation', 'character', 'logo', 'banner',
            'thumbnail', 'illustration', 'art', 'portrait', 'scene',
        ],
        ToolCategory.EDITING: [
            'edit', 'upscale', 'enhance', 'remove background', 'resize',
            'crop', 'filter', 'adjust', 'modify', 'change', 'variation',
            'recolor', 'replace', 'transform', 'improve',
        ],
        ToolCategory.RESEARCH: [
            'research', 'search', 'find', 'look up', 'investigate',
            'analyze', 'study', 'explore', 'write', 'article', 'blog',
            'content', 'document', 'report', 'review',
        ],
        ToolCategory.BUSINESS: [
            'competitor', 'customer', 'market', 'brand', 'strategy',
            'marketing', 'seo', 'legal', 'contract', 'proposal',
            'business', 'industry', 'target audience', 'persona',
        ],
        ToolCategory.DEVELOPMENT: [
            'code', 'develop', 'build', 'implement', 'program',
            'api', 'app', 'website', 'project', 'deploy', 'debug',
        ],
        ToolCategory.SYSTEM: [
            'health', 'status', 'system', 'vitals', 'workspace',
            'budget', 'cost', 'token', 'alert', 'monitor', 'body',
        ],
        ToolCategory.INTELLIGENCE: [
            'predict', 'prediction', 'gate', 'pilot', 'experiment',
            'reason', 'reasoning', 'decision', 'approve', 'pending',
            'think', 'analyze risk',
        ],
        ToolCategory.ORCHESTRATION: [
            'workflow', 'pipeline', 'orchestrate', 'sequence', 'automate',
            'opportunity', 'revenue', 'task', 'ml', 'machine learning',
        ],
    }

    # Categories that should include the universal agent
    INCLUDE_UNIVERSAL = {
        ToolCategory.RESEARCH,
        ToolCategory.BUSINESS,
        ToolCategory.DEVELOPMENT,
        ToolCategory.ORCHESTRATION,
    }

    # Feature flag
    ENABLE_CATEGORY_ROUTING = True

    # Confidence threshold below which we use all tools
    CONFIDENCE_THRESHOLD = 0.3

    def __init__(self):
        self._stats = {
            'requests_routed': 0,
            'fallback_to_all': 0,
            'category_hits': {cat.value: 0 for cat in ToolCategory},
        }

    def classify_message(self, message: str) -> CategoryMatch:
        """
        Classify a message into tool categories using keywords.

        No LLM call - pure keyword matching for speed.

        Args:
            message: The user's message

        Returns:
            CategoryMatch with primary and optional secondary category
        """
        message_lower = message.lower()
        category_scores: Dict[ToolCategory, int] = {cat: 0 for cat in ToolCategory if cat != ToolCategory.ALL}
        matched_keywords: Dict[ToolCategory, List[str]] = {cat: [] for cat in ToolCategory if cat != ToolCategory.ALL}

        # Score each category based on keyword matches
        for category, keywords in self.CATEGORY_KEYWORDS.items():
            for keyword in keywords:
                if keyword in message_lower:
                    category_scores[category] += 1
                    matched_keywords[category].append(keyword)

        # Find top categories
        sorted_categories = sorted(
            [(cat, score) for cat, score in category_scores.items() if score > 0],
            key=lambda x: -x[1]
        )

        if not sorted_categories:
            # No keywords matched - use UNIVERSAL as fallback
            return CategoryMatch(
                primary=ToolCategory.ALL,
                secondary=None,
                confidence=0.0,
                matched_keywords=[]
            )

        primary_cat, primary_score = sorted_categories[0]
        total_matches = sum(category_scores.values())
        confidence = primary_score / total_matches if total_matches > 0 else 0

        secondary_cat = None
        if len(sorted_categories) > 1:
            secondary_cat = sorted_categories[1][0]

        return CategoryMatch(
            primary=primary_cat,
            secondary=secondary_cat,
            confidence=confidence,
            matched_keywords=matched_keywords[primary_cat]
        )

    def get_tools_for_category(
        self,
        category: ToolCategory,
        all_tools: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Get tools that belong to a specific category.

        Args:
            category: The tool category
            all_tools: List of all available tool definitions

        Returns:
            Filtered list of tools for that category
        """
        if category == ToolCategory.ALL:
            return all_tools

        filtered = []
        for tool in all_tools:
            tool_name = tool.get('name', '')
            tool_category = self.TOOL_CATEGORIES.get(tool_name)

            if tool_category == category:
                filtered.append(tool)
            # Include universal agent for certain categories
            elif tool_name == 'universal_agent' and category in self.INCLUDE_UNIVERSAL:
                filtered.append(tool)

        return filtered

    def get_tools_for_message(
        self,
        message: str,
        all_tools: List[Dict[str, Any]],
        include_secondary: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Get the appropriate tools for a user message.

        This is the main entry point.

        Args:
            message: The user's message
            all_tools: List of all available tool definitions
            include_secondary: Whether to include tools from secondary category

        Returns:
            Filtered list of relevant tools
        """
        self._stats['requests_routed'] += 1

        if not self.ENABLE_CATEGORY_ROUTING:
            return all_tools

        classification = self.classify_message(message)

        # Low confidence or ALL category -> use all tools
        if classification.primary == ToolCategory.ALL or classification.confidence < self.CONFIDENCE_THRESHOLD:
            self._stats['fallback_to_all'] += 1
            logger.info(
                f"🔧 [Session 806] Tool routing: Using ALL tools "
                f"(confidence: {classification.confidence:.2f})"
            )
            return all_tools

        # Get tools for primary category
        tools = self.get_tools_for_category(classification.primary, all_tools)
        self._stats['category_hits'][classification.primary.value] += 1

        # Optionally add secondary category tools
        if include_secondary and classification.secondary:
            secondary_tools = self.get_tools_for_category(classification.secondary, all_tools)
            # Add tools that aren't already included
            existing_names = {t.get('name') for t in tools}
            for tool in secondary_tools:
                if tool.get('name') not in existing_names:
                    tools.append(tool)

        logger.info(
            f"🔧 [Session 806] Tool routing: {classification.primary.value} "
            f"({len(tools)}/{len(all_tools)} tools, "
            f"confidence: {classification.confidence:.2f}, "
            f"keywords: {classification.matched_keywords[:3]})"
        )

        return tools

    def get_category_for_tool(self, tool_name: str) -> Optional[ToolCategory]:
        """Get the category for a specific tool."""
        return self.TOOL_CATEGORIES.get(tool_name)

    def get_tools_in_category(self, category: ToolCategory) -> List[str]:
        """Get all tool names in a category."""
        return [
            name for name, cat in self.TOOL_CATEGORIES.items()
            if cat == category
        ]

    def get_stats(self) -> Dict[str, Any]:
        """Get routing statistics."""
        return {
            **self._stats,
            'routing_rate': (
                (self._stats['requests_routed'] - self._stats['fallback_to_all']) /
                self._stats['requests_routed']
                if self._stats['requests_routed'] > 0 else 0
            ),
        }

    def estimate_token_savings(
        self,
        all_tools_tokens: int,
        routed_tools: int,
        all_tools_count: int
    ) -> int:
        """Estimate token savings from routing."""
        if all_tools_count == 0:
            return 0
        tokens_per_tool = all_tools_tokens / all_tools_count
        routed_tokens = int(routed_tools * tokens_per_tool)
        return all_tools_tokens - routed_tokens

    @classmethod
    def set_category_routing(cls, enabled: bool) -> None:
        """Enable or disable category routing globally."""
        cls.ENABLE_CATEGORY_ROUTING = enabled
        logger.info(f"🔧 [Session 806] Category routing {'enabled' if enabled else 'disabled'}")


# Singleton instance
_tool_category_router: Optional[ToolCategoryRouter] = None


def get_tool_category_router() -> ToolCategoryRouter:
    """Get the singleton ToolCategoryRouter instance."""
    global _tool_category_router
    if _tool_category_router is None:
        _tool_category_router = ToolCategoryRouter()
    return _tool_category_router
