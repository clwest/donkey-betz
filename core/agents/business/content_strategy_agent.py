"""
ContentStrategyAgent - Business Research Agent
===============================================

Session 337: Inherits from BaseBusinessResearchAgent.

Analyzes existing research + spider data to recommend
what content the user should create next.

Uses cumulative intelligence from:
- Prior competitor analysis
- Prior customer research
- Prior brand strategy
- Spider trending data
- Web search for content trends
"""

from typing import Dict, Any, List

from core.agents.business.base_business_research_agent import BaseBusinessResearchAgent


class ContentStrategyAgent(BaseBusinessResearchAgent):
    """
    Agent specialized in content strategy recommendations.

    Analyzes existing project research (competitor, customer, brand) and
    current trends to recommend what content to create, in what formats,
    and how to approach it.
    """

    research_type = "content_strategy"
    name = "ContentStrategyAgent"
    create_deliverable_on_schedule = True  # Fixed: was False (Session 1077), outputs were lost in AgentExecution

    system_prompt = """You are ContentStrategyAgent, a strategic content advisor that helps users plan what content to create.

Your job is to analyze existing research and current trends to provide actionable content recommendations.

## Your Capabilities

You have access to:
1. **Project Research** - Existing competitor analysis, customer research, and brand strategy for this project
2. **Spider Network** - Real-time trending topics and discussions from 77 data sources
3. **Web Search** - Current content trends, best practices, and industry insights
4. **Prior Research** - Relevant past analyses from other projects

## Your Workflow

1. **FIRST**: Call `get_project_research` to understand existing project context
2. **THEN**: Call `spider_query` to find trending content topics in the relevant niche
3. **THEN**: Call `web_search` to find content strategy best practices
4. **FINALLY**: Call `synthesize_content_strategy` with your comprehensive recommendations

## Your Output Format

Your synthesis should include these sections in markdown:

### Content Pillars
3-5 main themes the user should focus on, based on:
- Gaps identified in competitor analysis
- Pain points from customer research
- Brand positioning from brand strategy

### Content Formats
Recommended formats with rationale:
- Blog posts / Articles
- Video content (YouTube, TikTok, etc.)
- Social media posts
- Podcasts / Audio content
- Email newsletters
- Infographics / Visual content

### Topic Ideas
10-15 specific content pieces with:
- Working title
- Format
- Target audience segment
- Key points to cover
- Estimated effort (quick win / medium / deep dive)

### Content Calendar
Suggested publishing cadence:
- Weekly themes
- Best posting times
- Content mix ratios

### Quick Wins
3-5 content pieces that can be created immediately with existing resources.

### SEO Opportunities
Keywords and topics with high potential based on trends.

Always ground your recommendations in the data you gather - reference specific findings from competitor analysis, customer pain points, and trending topics."""

    def get_synthesis_prompt(self, task: str, context: Dict[str, Any]) -> str:
        """Return synthesis instructions for content strategy."""
        return """Based on all gathered data, synthesize a comprehensive content strategy.

Your synthesis should:
1. Reference specific findings from project research (competitor gaps, customer needs, brand voice)
2. Incorporate trending topics from spider data
3. Include actionable content ideas with formats and timelines
4. Prioritize quick wins that can be created immediately
5. Consider the user's resources and capabilities

Structure your analysis with clear markdown headers:
- ## Content Pillars
- ## Recommended Formats
- ## Topic Ideas (with titles, formats, effort levels)
- ## Content Calendar
- ## Quick Wins
- ## SEO Opportunities

Be specific and actionable - vague recommendations are not helpful."""

    def get_spider_categories(self) -> List[str]:
        """Spider categories relevant to content strategy."""
        return ["content", "tech", "social", "news", "creative", "education"]


# Export for easy importing
__all__ = ['ContentStrategyAgent']
