"""
Persona Advisor Service
=======================

Session 812: Enables Persona Agents to provide advisory input during content production.

Persona Agents (139 database records) don't have Python code - they participate via
LLM conversations enriched with spider data from their domain.

This service:
1. Loads persona agent from database
2. Fetches relevant spider context for their domain
3. Generates LLM response from their perspective
4. Returns structured advice for use in content production

Usage:
    from core.services.persona_advisor_service import PersonaAdvisorService
from core.services.openai_client_factory import get_openai_client  # Session 1084 round 51

    advisor = PersonaAdvisorService()
    result = advisor.get_advice(
        persona_name='Content Strategy Planner',
        topic='AI trends for 2026',
        advice_type='content_strategy',
        context={'content_type': 'blog_post', 'tone': 'professional'}
    )
"""

import json
import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field

from django.utils import timezone

logger = logging.getLogger(__name__)


# Persona agents relevant to each content production phase
CONTENT_PRODUCTION_ADVISORS = {
    'blog_post': {
        'planning': ['Content Strategy Planner', 'SEO Content Optimizer', 'Blog Post Generator'],
        'creation': ['Content Writer Pro', 'Copywriting Specialist'],
        'optimization': ['Digital Marketing Strategist', 'Social Media Creator'],
        'review': ['Trend Analysis Expert', 'Audience Engagement Specialist'],
    },
    'podcast': {
        'planning': ['Content Strategy Planner', 'Audio Content Creator'],
        'creation': ['Podcast Script Writer', 'Storytelling Expert'],
        'optimization': ['Digital Marketing Strategist', 'Social Media Creator'],
        'review': ['Audience Engagement Specialist'],
    },
    'video': {
        'planning': ['Content Strategy Planner', 'Video Content Strategist'],
        'creation': ['Video Script Writer', 'Storytelling Expert'],
        'optimization': ['YouTube Optimization Expert', 'Social Media Creator'],
        'review': ['Trend Analysis Expert'],
    },
    'newsletter': {
        'planning': ['Content Strategy Planner', 'Email Campaign Manager'],
        'creation': ['Copywriting Specialist', 'Content Writer Pro'],
        'optimization': ['Conversion Rate Optimizer'],
        'review': ['Audience Engagement Specialist'],
    },
    'social_campaign': {
        'planning': ['Digital Marketing Strategist', 'Social Media Creator'],
        'creation': ['Copywriting Specialist', 'Brand Voice Developer'],
        'optimization': ['Growth Hacker Pro', 'Conversion Rate Optimizer'],
        'review': ['Trend Analysis Expert', 'Audience Engagement Specialist'],
    },
}


# Advice type prompts
ADVICE_PROMPTS = {
    'content_strategy': """
You are {persona_name}, a specialist in {domain}.

A content team is creating a {content_type} about: {topic}

Based on your expertise and the real-world data available to you, provide strategic advice:

1. **Key Angles**: What 2-3 angles would resonate most with the target audience?
2. **Unique Hook**: What's a compelling hook that differentiates this content?
3. **Must-Include Points**: What 3-5 points absolutely must be covered?
4. **Potential Pitfalls**: What should the content team avoid?
5. **Success Metrics**: How should they measure if this content succeeds?

{spider_context}

Provide your expert advice in a structured format.
""",

    'seo_optimization': """
You are {persona_name}, a specialist in {domain}.

Review this content topic for SEO optimization: {topic}
Content type: {content_type}

Based on your expertise and current trends, provide SEO guidance:

1. **Primary Keywords**: 3-5 keywords to target
2. **Long-tail Opportunities**: 2-3 long-tail keyword phrases
3. **Title Suggestions**: 2-3 SEO-optimized title options
4. **Meta Description**: A compelling 150-160 character meta description
5. **Content Structure**: Recommended H2 headers for SEO

{spider_context}

Provide actionable SEO recommendations.
""",

    'marketing_angle': """
You are {persona_name}, a specialist in {domain}.

A content piece is being created about: {topic}
Content type: {content_type}

Provide marketing guidance to maximize reach and engagement:

1. **Target Audience Segments**: Who are the 2-3 key audiences?
2. **Platform Strategy**: Which platforms and why?
3. **Timing**: Best time/day to publish based on your expertise
4. **Promotion Hooks**: 2-3 hooks for social promotion
5. **Call-to-Action**: What should readers do after consuming this?

{spider_context}

Provide strategic marketing recommendations.
""",

    'quality_review': """
You are {persona_name}, a specialist in {domain}.

Review this content plan for quality and relevance:
Topic: {topic}
Content type: {content_type}
{existing_content}

Based on your expertise and current market trends:

1. **Relevance Score**: 1-10, how relevant is this topic right now?
2. **Completeness**: What's missing that should be included?
3. **Differentiation**: How does this stand out from existing content?
4. **Improvement Suggestions**: Top 3 ways to improve
5. **Go/No-Go**: Should this content proceed as planned?

{spider_context}

Provide your expert quality assessment.
""",

    'trend_analysis': """
You are {persona_name}, a specialist in {domain}.

Analyze current trends related to: {topic}
For content type: {content_type}

Based on the real-world data and your expertise:

1. **Trending Now**: What aspects of this topic are trending?
2. **Emerging Themes**: What related themes are gaining traction?
3. **Declining Interest**: What angles should be avoided (oversaturated)?
4. **Opportunity Windows**: What timing opportunities exist?
5. **Competitor Activity**: What are others doing in this space?

{spider_context}

Provide actionable trend insights.
""",
}


@dataclass
class AdvisoryResult:
    """Result from a persona agent advisory consultation."""
    persona_name: str
    advice_type: str
    topic: str
    advice: str
    structured_advice: Optional[Dict[str, Any]] = None
    spider_data_used: int = 0
    execution_time_ms: int = 0
    success: bool = True
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            'persona_name': self.persona_name,
            'advice_type': self.advice_type,
            'topic': self.topic,
            'advice': self.advice,
            'structured_advice': self.structured_advice,
            'spider_data_used': self.spider_data_used,
            'execution_time_ms': self.execution_time_ms,
            'success': self.success,
            'error': self.error,
        }


class PersonaAdvisorService:
    """
    Service for getting advisory input from Persona Agents.

    Persona Agents provide domain expertise via LLM conversations
    enriched with real-time spider data from their specialty area.
    """

    def __init__(self):
        self._context_builder = None
        self._Agent = None

    @property
    def context_builder(self):
        """Lazy-load persona context builder."""
        if self._context_builder is None:
            from core.services.persona_agent_context import get_persona_context_builder
            self._context_builder = get_persona_context_builder()
        return self._context_builder

    @property
    def Agent(self):
        """Lazy-load Agent model."""
        if self._Agent is None:
            from core.models_unified_system import Agent
            self._Agent = Agent
        return self._Agent

    def get_advice(
        self,
        persona_name: str,
        topic: str,
        advice_type: str = 'content_strategy',
        context: Optional[Dict[str, Any]] = None
    ) -> AdvisoryResult:
        """
        Get advice from a persona agent on a topic.

        Args:
            persona_name: Name of the persona agent (e.g., 'Content Strategy Planner')
            topic: Topic to get advice about
            advice_type: Type of advice (content_strategy, seo_optimization, marketing_angle, etc.)
            context: Additional context (content_type, tone, existing_content, etc.)

        Returns:
            AdvisoryResult with the advice
        """
        import time
        start_time = time.time()
        context = context or {}

        # Find the persona agent
        agent = self.Agent.objects.filter(name=persona_name).first()
        if not agent:
            # Try fuzzy match
            agent = self.Agent.objects.filter(name__icontains=persona_name.split()[0]).first()

        if not agent:
            return AdvisoryResult(
                persona_name=persona_name,
                advice_type=advice_type,
                topic=topic,
                advice='',
                success=False,
                error=f"Persona agent not found: {persona_name}"
            )

        # Check if this is actually a persona agent (not a core agent)
        if not self.context_builder.is_persona_agent(agent):
            logger.warning(f"{persona_name} is a core agent, not a persona agent")
            # Still proceed - they can still provide advice

        # Get spider context for this agent's domain
        spider_context = self.context_builder.build_context_for_agent(
            agent=agent,
            topic=topic,
            hours=72,  # Last 3 days
            limit=5
        )

        spider_data_count = len(self.context_builder.get_spider_data_for_agent(agent, hours=72, limit=10))

        # Get the domain description
        mapping = self.context_builder.get_mapping_for_agent(agent)
        domain = mapping.get('description', agent.specialization or 'your domain') if mapping else 'your domain'

        # Build the prompt
        prompt_template = ADVICE_PROMPTS.get(advice_type, ADVICE_PROMPTS['content_strategy'])
        prompt = prompt_template.format(
            persona_name=persona_name,
            domain=domain,
            topic=topic,
            content_type=context.get('content_type', 'content'),
            spider_context=spider_context or "No recent data available.",
            existing_content=context.get('existing_content', ''),
        )

        # Generate advice via LLM
        try:
            advice_text = self._generate_advice(prompt, agent)
            structured = self._parse_structured_advice(advice_text)

            execution_time = int((time.time() - start_time) * 1000)

            return AdvisoryResult(
                persona_name=persona_name,
                advice_type=advice_type,
                topic=topic,
                advice=advice_text,
                structured_advice=structured,
                spider_data_used=spider_data_count,
                execution_time_ms=execution_time,
                success=True
            )

        except Exception as e:
            logger.error(f"Error getting advice from {persona_name}: {e}")
            return AdvisoryResult(
                persona_name=persona_name,
                advice_type=advice_type,
                topic=topic,
                advice='',
                success=False,
                error=str(e),
                execution_time_ms=int((time.time() - start_time) * 1000)
            )

    def _generate_advice(self, prompt: str, agent) -> str:
        """Generate advice via LLM."""
        try:
            import os

            # Session 1084 round 51: custom 60s timeout dropped — factory enforces 90s read centrally
            client = get_openai_client(api_key=os.getenv('OPENAI_API_KEY'))

            system_prompt = f"""You are {agent.name}, a specialized AI advisor.

Your role: {agent.description or 'Domain expert providing strategic guidance'}
Your specialization: {agent.specialization or 'General expertise'}

Provide thoughtful, actionable advice based on your expertise and any real-world data provided.
Be specific and practical. Format your response with clear sections using **bold headers**.
"""

            response = client.chat.completions.create(
                model="gpt-5-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                max_completion_tokens=1500,
                timeout=60.0
            )

            return response.choices[0].message.content

        except Exception as e:
            logger.error(f"LLM generation error: {e}")
            raise

    def _parse_structured_advice(self, advice_text: str) -> Optional[Dict[str, Any]]:
        """Attempt to parse structured sections from advice text."""
        if not advice_text:
            return None

        structured = {}
        current_section = None
        current_content = []

        for line in advice_text.split('\n'):
            line = line.strip()
            if not line:
                continue

            # Check for bold headers like **Key Angles**:
            if line.startswith('**') and '**' in line[2:]:
                # Save previous section
                if current_section and current_content:
                    structured[current_section] = '\n'.join(current_content).strip()

                # Extract new section name
                end_bold = line.index('**', 2)
                current_section = line[2:end_bold].lower().replace(' ', '_').replace(':', '')
                current_content = []

                # Check if there's content on the same line
                rest = line[end_bold+2:].strip().lstrip(':').strip()
                if rest:
                    current_content.append(rest)
            elif current_section:
                current_content.append(line)

        # Save last section
        if current_section and current_content:
            structured[current_section] = '\n'.join(current_content).strip()

        return structured if structured else None

    def get_advisors_for_content_type(
        self,
        content_type: str,
        phase: str = 'planning'
    ) -> List[str]:
        """
        Get recommended persona advisors for a content type and phase.

        Args:
            content_type: Type of content (blog_post, podcast, etc.)
            phase: Production phase (planning, creation, optimization, review)

        Returns:
            List of persona agent names
        """
        advisors = CONTENT_PRODUCTION_ADVISORS.get(content_type, {})
        return advisors.get(phase, [])

    def get_multiple_advice(
        self,
        persona_names: List[str],
        topic: str,
        advice_type: str = 'content_strategy',
        context: Optional[Dict[str, Any]] = None
    ) -> List[AdvisoryResult]:
        """
        Get advice from multiple persona agents.

        Args:
            persona_names: List of persona agent names
            topic: Topic to get advice about
            advice_type: Type of advice
            context: Additional context

        Returns:
            List of AdvisoryResults
        """
        results = []
        for name in persona_names:
            result = self.get_advice(
                persona_name=name,
                topic=topic,
                advice_type=advice_type,
                context=context
            )
            results.append(result)

        return results

    def get_planning_advice(
        self,
        content_type: str,
        topic: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Convenience method to get planning advice for content production.

        Args:
            content_type: Type of content
            topic: Topic for the content
            context: Additional context

        Returns:
            Dict with combined planning advice
        """
        advisors = self.get_advisors_for_content_type(content_type, 'planning')
        if not advisors:
            return {'success': False, 'error': f'No advisors defined for {content_type}'}

        # Get advice from first available advisor
        for advisor_name in advisors:
            result = self.get_advice(
                persona_name=advisor_name,
                topic=topic,
                advice_type='content_strategy',
                context={'content_type': content_type, **(context or {})}
            )
            if result.success:
                return {
                    'success': True,
                    'advisor': advisor_name,
                    'advice': result.advice,
                    'structured': result.structured_advice,
                    'spider_data_used': result.spider_data_used,
                }

        return {'success': False, 'error': 'No advisors available'}


# Singleton instance
_advisor_service = None


def get_persona_advisor_service() -> PersonaAdvisorService:
    """Get or create the PersonaAdvisorService singleton."""
    global _advisor_service
    if _advisor_service is None:
        _advisor_service = PersonaAdvisorService()
    return _advisor_service


def get_advice(
    persona_name: str,
    topic: str,
    advice_type: str = 'content_strategy',
    context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Convenience function to get advice from a persona agent.

    Returns:
        Dict with advice results
    """
    service = get_persona_advisor_service()
    result = service.get_advice(
        persona_name=persona_name,
        topic=topic,
        advice_type=advice_type,
        context=context
    )
    return result.to_dict()


__all__ = [
    'PersonaAdvisorService',
    'get_persona_advisor_service',
    'get_advice',
    'AdvisoryResult',
    'CONTENT_PRODUCTION_ADVISORS',
    'ADVICE_PROMPTS',
]
