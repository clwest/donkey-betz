"""
MarketingStrategyAgent - Business Research Agent
=================================================

Session 337: Inherits from BaseBusinessResearchAgent.

Analyzes existing research + trends to create comprehensive
marketing strategies for products, services, and content.

Uses cumulative intelligence from:
- Prior competitor analysis (what competitors are doing)
- Prior customer research (who to target, what they need)
- Prior brand strategy (how to position)
- Prior content strategy (what content to promote)
- Spider trending data (current marketing trends)
- Web search (marketing best practices)
"""

import logging
from typing import Dict, Any, List

from core.agents.business.base_business_research_agent import BaseBusinessResearchAgent
from ml.auto_selection import TaskType

logger = logging.getLogger(__name__)


def analyze_marketing_strategy_with_ml(marketing_data: dict) -> dict:
    """Analyze marketing strategy data using ML models (Text + Clustering)."""
    try:
        from core.services.agent_model_router import get_agent_model_router
        router = get_agent_model_router()

        # Use TEXT task type for marketing content analysis
        result = router.auto_route(
            data=marketing_data,
            task_hint=TaskType.TEXT,
            max_models=2
        )

        return {
            'ml_used': True,
            'task_type': result.auto_selection.get('task_type', 'text'),
            'models_used': result.models_used,
            'confidence': round(result.confidence, 2),
            'ml_insights': result.explanation,
            'market_segments': result.prediction if hasattr(result, 'prediction') else None,
        }
    except Exception as e:
        logger.warning(f"ML marketing strategy analysis failed: {e}")
        return {'ml_used': False, 'reason': f'ML error: {str(e)}'}


class MarketingStrategyAgent(BaseBusinessResearchAgent):
    """
    Agent specialized in marketing strategy recommendations.

    Creates comprehensive marketing plans based on existing research,
    including channel strategies, campaign ideas, and budget allocation.
    """

    research_type = "marketing_strategy"
    name = "MarketingStrategyAgent"
    create_deliverable_on_schedule = False  # Session 1077: scheduled outputs go to AgentExecution only

    system_prompt = """You are MarketingStrategyAgent, a strategic marketing advisor that helps users plan how to market their products, services, and content.

Your job is to analyze existing research and current trends to create actionable marketing strategies.

## Your Capabilities

You have access to:
1. **Project Research** - Existing competitor analysis, customer research, brand strategy, and content strategy
2. **Spider Network** - Real-time marketing trends, campaign examples, and industry insights from 77 data sources
3. **Web Search** - Current marketing best practices, platform updates, and case studies
4. **Prior Research** - Relevant past marketing analyses from other projects

## Your Workflow

1. **FIRST**: Call `get_project_research` to understand existing project context (especially customer personas and brand positioning)
2. **THEN**: Call `spider_query` to find current marketing trends and successful campaigns
3. **THEN**: Call `web_search` to find marketing best practices and platform strategies
4. **FINALLY**: Call `synthesize_marketing_strategy` with your comprehensive recommendations

## Your Output Format

Your synthesis should include these sections in markdown:

### Target Audience Summary
Based on customer research:
- Primary audience segments
- Key pain points to address
- Preferred channels
- Decision-making factors

### Channel Strategy
For each relevant channel:
- **Organic Social** (which platforms, posting strategy)
- **Paid Social** (targeting, ad formats, budget allocation)
- **Search Marketing** (SEO priorities, PPC opportunities)
- **Email Marketing** (list building, campaign types)
- **Content Marketing** (distribution strategy)
- **Partnerships/Influencers** (opportunities identified)

### Campaign Ideas
3-5 campaign concepts including:
- Campaign name and theme
- Target audience segment
- Channels to use
- Key messaging
- Call to action
- Success metrics
- Estimated timeline

### Marketing Funnel
- **Awareness**: How to reach new audiences
- **Consideration**: How to nurture interest
- **Conversion**: How to drive action
- **Retention**: How to keep customers engaged

### Budget Recommendations
If applicable:
- Channel allocation percentages
- Priority investments
- Quick wins vs. long-term plays

### Key Metrics
What to track:
- Awareness metrics (reach, impressions)
- Engagement metrics (clicks, shares, comments)
- Conversion metrics (leads, sales, sign-ups)
- ROI tracking approach

### Quick Wins
3-5 marketing actions that can be started immediately with minimal resources.

Always ground your recommendations in the data you gather - reference specific findings from customer research, competitor activities, and current trends."""

    def get_synthesis_prompt(self, task: str, context: Dict[str, Any]) -> str:
        """Return synthesis instructions for marketing strategy."""
        return """Based on all gathered data, synthesize a comprehensive marketing strategy.

Your synthesis should:
1. Build on customer personas and pain points from customer research
2. Position against competitors based on competitor analysis
3. Align with brand voice and positioning from brand strategy
4. Incorporate current marketing trends from spider data
5. Include specific, actionable campaign ideas

Structure your analysis with clear markdown headers:
- ## Target Audience Summary
- ## Channel Strategy (organic social, paid, search, email, etc.)
- ## Campaign Ideas (3-5 specific campaigns with details)
- ## Marketing Funnel (awareness, consideration, conversion, retention)
- ## Budget Recommendations (if applicable)
- ## Key Metrics
- ## Quick Wins

Be specific and actionable - include actual campaign names, specific platforms, and concrete tactics."""

    def get_spider_categories(self) -> List[str]:
        """Spider categories relevant to marketing strategy."""
        return ["social", "tech", "news", "content", "creative", "financial"]


# Export for easy importing
__all__ = ['MarketingStrategyAgent']
