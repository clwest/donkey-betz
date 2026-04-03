"""
Distribution Agent — Engagement Optimization for Any Content
=============================================================

General-purpose agent that optimizes content for maximum engagement
across any channel: newsletters, social media, blog posts, outreach emails.

Capabilities:
- Subject line / headline variants with style tags
- Hook analysis (first impression scoring + rewrites)
- CTA optimization per channel (email, social, web)
- Distribution plan (channels, timing, snippets)
- A/B experiment specs

Usage:
    from core.agents.distribution_agent import DistributionAgent

    agent = DistributionAgent(user=request.user)
    result = agent.execute(
        task="Optimize this newsletter for engagement",
        context={
            'content': 'The full newsletter text...',
            'content_type': 'newsletter',  # or 'blog', 'social', 'outreach'
            'audience': 'CTOs and engineering leaders',
            'goal': 'opens',  # opens, clicks, signups, shares, followers
        },
        scifi_context={},
        spider_context={}
    )

Output (result.data):
    {
        'subject_variants': [...],
        'hook_analysis': {...},
        'cta_variants': [...],
        'distribution_plan': {...},
        'social_snippets': {...},
        'experiment_spec': {...},
    }
"""

import json
import logging
import time
from typing import Dict, Any, Optional, List

from core.agents.base_agent import BaseAgent, AgentResult, OutputCategory, QualityTier

logger = logging.getLogger(__name__)


CONTENT_TYPE_PROMPTS = {
    'newsletter': 'This is an email newsletter. Optimize for open rates, click-throughs, and subscriber retention.',
    'blog': 'This is a blog post. Optimize for SEO clicks, time-on-page, and social shares.',
    'social': 'This is social media content. Optimize for engagement (likes, comments, shares, follows).',
    'outreach': 'This is outreach/cold email. Optimize for reply rates and meeting bookings.',
    'general': 'Optimize this content for maximum reader engagement and action.',
}

GOAL_INSTRUCTIONS = {
    'opens': 'Primary goal: maximize open/click rates. Subject lines are CRITICAL.',
    'clicks': 'Primary goal: maximize click-throughs to links. CTAs must be compelling and clear.',
    'signups': 'Primary goal: drive signups/subscriptions. Include clear value proposition.',
    'shares': 'Primary goal: make this so good people share it. Focus on shareable insights and quotable lines.',
    'followers': 'Primary goal: grow audience. Include follow CTAs and reasons to subscribe.',
    'engagement': 'Primary goal: maximize comments, replies, and discussion. Ask questions, be provocative.',
}


class DistributionAgent(BaseAgent):
    """
    Engagement optimization agent for any content type.

    Analyzes content and produces engagement-optimized variants:
    subject lines, hooks, CTAs, distribution plans, and social snippets.
    """

    name = "DistributionAgent"
    create_deliverable_on_schedule = False
    description = (
        "Optimizes content for maximum engagement across channels. "
        "Generates subject line variants, hook analysis, CTA optimization, "
        "distribution plans, and social media snippets."
    )

    output_category = OutputCategory.CONTENT
    default_quality_tier = QualityTier.GOLD

    system_prompt = """You are an expert content distribution strategist and engagement optimizer.

You understand the psychology of what makes people click, read, and take action.
You specialize in:
- Subject lines that MUST be opened (curiosity gaps, urgency, specific benefits)
- Opening hooks that keep readers going (the first 2 sentences determine everything)
- CTAs that actually convert (clear, specific, low-friction)
- Channel-specific optimization (email vs social vs web have different rules)
- A/B testing strategy (what to test, how to measure)

You analyze content and produce SPECIFIC, ACTIONABLE optimization recommendations.
Never be generic — every suggestion must reference the actual content you're optimizing.

Output format: Return a JSON object with these sections:
{
    "subject_variants": [
        {"text": "...", "style": "curiosity|urgency|benefit|news|how_to|contrarian", "predicted_strength": "high|medium|low", "char_count": N}
    ],
    "hook_analysis": {
        "current_score": 1-10,
        "issues": ["..."],
        "rewrites": [{"text": "...", "approach": "..."}]
    },
    "cta_variants": [
        {"text": "...", "channel": "email|social|web", "goal": "...", "placement": "..."}
    ],
    "distribution_plan": {
        "primary_channel": "...",
        "cross_post_channels": ["..."],
        "recommended_timing": "...",
        "audience_notes": "..."
    },
    "social_snippets": {
        "twitter": "... (280 chars max)",
        "linkedin": "... (professional tone, 1-2 paragraphs)",
        "thread_hook": "... (first tweet of a thread)"
    },
    "key_recommendations": ["top 3 things to change for maximum impact"]
}

Rules:
- Subject lines: produce exactly 6 variants covering different styles
- Always score the current opening hook honestly (1-10)
- Social snippets must be ready to post (not placeholders)
- Be specific to the actual content — reference real topics/claims from the text
- Think about what would make YOU stop scrolling"""

    tools = [
        {
            'type': 'function',
            'name': 'web_search',
            'description': 'Search for trending formats, competitor subject lines, or engagement benchmarks',
            'parameters': {
                'type': 'object',
                'properties': {
                    'query': {'type': 'string', 'description': 'Search query'},
                },
                'required': ['query'],
            },
        },
    ]

    def execute(self, task: str, context: Dict[str, Any],
                scifi_context: Dict[str, Any] = None,
                spider_context: Dict[str, Any] = None) -> AgentResult:
        """
        Analyze content and produce engagement optimization recommendations.

        Context keys:
            content (str, required): The content to optimize
            content_type (str): newsletter, blog, social, outreach, general
            audience (str): Target audience description
            goal (str): opens, clicks, signups, shares, followers, engagement
            tone (str): Desired tone
            constraints (list): Things to avoid
        """
        start_time = time.time()

        try:
            content = context.get('content', '')
            if not content:
                # Try to get from task description
                content = task if len(task) > 200 else ''

            if not content:
                return AgentResult(
                    success=False,
                    message="No content provided. Include 'content' in context.",
                    error="No content to optimize",
                    agent_name=self.name,
                )

            content_type = context.get('content_type', 'general')
            audience = context.get('audience', 'general readers')
            goal = context.get('goal', 'engagement')
            tone = context.get('tone', '')

            # Build the optimization prompt
            type_prompt = CONTENT_TYPE_PROMPTS.get(content_type, CONTENT_TYPE_PROMPTS['general'])
            goal_prompt = GOAL_INSTRUCTIONS.get(goal, GOAL_INSTRUCTIONS['engagement'])

            # User's distribution hook / angle from the workspace brief
            distribution_hook = context.get('distribution_hook', '')
            if not distribution_hook:
                brief = context.get('workspace_brief', {})
                if isinstance(brief, dict):
                    distribution_hook = brief.get('distribution_hook', '')

            hook_instruction = ''
            if distribution_hook:
                hook_instruction = f"""
IMPORTANT — The content creator specifically wants this angle/hook emphasized:
"{distribution_hook}"
Incorporate this direction into your subject lines, hooks, CTAs, and social snippets.
This is their strategic insight — combine it with your analysis for maximum impact.
"""

            prompt = f"""{type_prompt}
{goal_prompt}

Target audience: {audience}
{f'Tone: {tone}' if tone else ''}
{hook_instruction}

--- CONTENT TO OPTIMIZE ---
{content[:4000]}
--- END CONTENT ---

Analyze this content and produce your full optimization output as JSON.
Include 6 subject line variants, hook analysis with rewrites, CTAs per channel,
distribution plan, ready-to-post social snippets, and your top 3 recommendations."""

            # Call LLM
            from core.llm_enforcer import LLMEnforcer
            enforcer = LLMEnforcer()
            llm_result = enforcer.enforce_real_ai(
                prompt=prompt,
                agent_name=self.name,
                task_type='content',
                max_tokens=3000,
            )

            response_text = llm_result.get('response', '')
            execution_time = time.time() - start_time

            # Try to parse JSON from the response
            optimization_data = self._parse_optimization_output(response_text)

            # Build the deliverable content (human-readable markdown)
            markdown_output = self._format_as_markdown(optimization_data, content_type, audience, goal)

            return AgentResult(
                success=True,
                message=markdown_output,
                data={
                    'optimization': optimization_data,
                    'content_type': content_type,
                    'audience': audience,
                    'goal': goal,
                    'full_text': markdown_output,
                    'subject_variants': optimization_data.get('subject_variants', []),
                    'social_snippets': optimization_data.get('social_snippets', {}),
                },
                agent_name=self.name,
                execution_time_ms=int(execution_time * 1000),
            )

        except Exception as e:
            logger.error(f"DistributionAgent error: {e}")
            return AgentResult(
                success=False,
                message=f"Distribution optimization failed: {str(e)[:200]}",
                error=str(e),
                agent_name=self.name,
                execution_time_ms=int((time.time() - start_time) * 1000),
            )

    def _parse_optimization_output(self, response: str) -> dict:
        """Extract JSON from LLM response, handling markdown code blocks."""
        import re

        # Try to find JSON in code blocks
        json_match = re.search(r'```(?:json)?\s*\n?([\s\S]*?)\n?```', response)
        if json_match:
            try:
                return json.loads(json_match.group(1))
            except json.JSONDecodeError:
                pass

        # Try parsing the whole response as JSON
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            pass

        # Fall back to structured text extraction
        return {
            'raw_analysis': response,
            'subject_variants': [],
            'hook_analysis': {'current_score': 0, 'issues': [], 'rewrites': []},
            'cta_variants': [],
            'distribution_plan': {},
            'social_snippets': {},
            'key_recommendations': [],
        }

    def _format_as_markdown(self, data: dict, content_type: str, audience: str, goal: str) -> str:
        """Format optimization data as readable markdown."""
        parts = [f"# Distribution & Engagement Optimization\n"]
        parts.append(f"**Content type:** {content_type} | **Audience:** {audience} | **Goal:** {goal}\n")

        # Subject lines
        variants = data.get('subject_variants', [])
        if variants:
            parts.append("## Subject Line Variants\n")
            for i, v in enumerate(variants, 1):
                text = v.get('text', v) if isinstance(v, dict) else str(v)
                style = v.get('style', '') if isinstance(v, dict) else ''
                strength = v.get('predicted_strength', '') if isinstance(v, dict) else ''
                parts.append(f"{i}. **{text}**")
                if style or strength:
                    parts.append(f"   _{style}_ | Strength: {strength}")
            parts.append("")

        # Hook analysis
        hook = data.get('hook_analysis', {})
        if hook and hook.get('current_score'):
            parts.append(f"## Hook Analysis\n")
            parts.append(f"**Current score:** {hook.get('current_score')}/10\n")
            for issue in hook.get('issues', []):
                parts.append(f"- {issue}")
            parts.append("\n**Suggested rewrites:**")
            for rw in hook.get('rewrites', []):
                text = rw.get('text', rw) if isinstance(rw, dict) else str(rw)
                parts.append(f"- {text}")
            parts.append("")

        # CTAs
        ctas = data.get('cta_variants', [])
        if ctas:
            parts.append("## CTA Variants\n")
            for cta in ctas:
                text = cta.get('text', cta) if isinstance(cta, dict) else str(cta)
                channel = cta.get('channel', '') if isinstance(cta, dict) else ''
                parts.append(f"- **{text}** ({channel})")
            parts.append("")

        # Social snippets
        social = data.get('social_snippets', {})
        if social:
            parts.append("## Social Media Snippets\n")
            for platform, snippet in social.items():
                parts.append(f"### {platform.title()}\n{snippet}\n")

        # Distribution plan
        plan = data.get('distribution_plan', {})
        if plan:
            parts.append("## Distribution Plan\n")
            for k, v in plan.items():
                parts.append(f"- **{k.replace('_', ' ').title()}:** {v}")
            parts.append("")

        # Key recommendations
        recs = data.get('key_recommendations', [])
        if recs:
            parts.append("## Top Recommendations\n")
            for i, rec in enumerate(recs, 1):
                parts.append(f"{i}. {rec}")

        # Raw analysis fallback
        if data.get('raw_analysis'):
            parts.append(f"\n## Analysis\n\n{data['raw_analysis']}")

        return '\n'.join(parts)
