"""
Content Writer Agent - Session 496 + Session 523 Intelligent Prompting
=======================================================================

Transforms research into written content: blog posts, podcast scripts, video scripts, articles.

This agent takes research context (from spider data, web search, or prior analysis)
and generates professional written content in the requested format.

Session 523: INTEGRATED WITH INTELLIGENT PROMPTING SYSTEM
- Uses DynamicPromptBuilder for context-aware prompts
- Includes Memory Palace context (past interactions)
- Includes agent mood influence
- Includes user preferences
- Uses platform context (capabilities, agents, etc.)
- Dynamic year/date references

Session 886: FEEDBACK LOOP INTEGRATION
- Injects BlogPerformanceContext before each generation
- Shows recent quality scores, strengths, weaknesses
- Includes active learning rules from PipelineLearningInsight
- Agent learns from past content performance

Content Types Supported:
    - blog_post: Title, intro, sections with headers, conclusion, SEO metadata
    - podcast_script: Intro hook, segments with talking points, transitions, outro
    - video_script: Scene descriptions, narration, b-roll suggestions, timing
    - article: Headline, lead paragraph, body sections, call-to-action
    - social_thread: Series of connected posts for Twitter/X, LinkedIn, etc.
    - newsletter: Subject line, preview text, sections, CTA

Usage:
    from core.agents.content_writer_agent import ContentWriterAgent

    agent = ContentWriterAgent(user=request.user)
    result = agent.execute(
        task="Write a blog post about AI startup trends",
        context={
            'content_type': 'blog_post',
            'research': '... research content ...',
            'tone': 'professional',
            'target_audience': 'tech entrepreneurs',
            'word_count': 1500
        },
        scifi_context={},
        spider_context={}
    )
"""

import json
import logging
import time
from datetime import datetime
from typing import Dict, Any, Optional, List

from core.agents.base_agent import BaseAgent, AgentResult, ActionableOutputConfig, OutputCategory, QualityTier
from core.agents.report_schemas import build_provenance, format_disclaimer
from ml.auto_selection import TaskType

# Session 961: Multi-agent content review panel
ENABLE_CONTENT_REVIEW = True

# Session 523: Import Intelligent Prompting System
try:
    from core.prompts.registry import (
        PLATFORM_CONTEXT,
    )
    PROMPTING_SYSTEM_AVAILABLE = True
except ImportError:
    PROMPTING_SYSTEM_AVAILABLE = False
    PLATFORM_CONTEXT = ""

# Session 523: Import Memory Palace for past context
try:
    from core.models_unified_system import ConversationMemory
    MEMORY_AVAILABLE = True
except ImportError:
    MEMORY_AVAILABLE = False
    ConversationMemory = None

# Session 886: Import Blog Performance Context for feedback loop
try:
    from core.services.blog_performance_context import get_blog_performance_context
    PERFORMANCE_CONTEXT_AVAILABLE = True
except ImportError:
    PERFORMANCE_CONTEXT_AVAILABLE = False
    get_blog_performance_context = None

# Session 891: Import Domain Content Context for all topic areas
try:
    from core.services.domain_content_context import get_domain_content_context, detect_content_domain
    DOMAIN_CONTEXT_AVAILABLE = True
except ImportError:
    DOMAIN_CONTEXT_AVAILABLE = False
    get_domain_content_context = None
    detect_content_domain = None

logger = logging.getLogger(__name__)

# Prompt fragments that indicate LLM output leaking into tags
_TAG_BLACKLIST_FRAGMENTS = [
    '##', 'REVIEW', 'Write an article', 'Write a blog',
    'Real-Time Research', 'research data', 'BLOG POST',
    'stage ', '[stage', 'spider data', '\n',
]


def _sanitize_tags(tags: List[str], max_tags: int = 8) -> List[str]:
    """Strip prompt-leaked, oversized, or empty tags."""
    clean = []
    for tag in tags:
        if not isinstance(tag, str) or not tag.strip():
            continue
        tag = tag.strip()
        # Skip oversized tags (real tags are short keywords)
        if len(tag) > 50:
            continue
        # Skip tags containing prompt fragments
        tag_lower = tag.lower()
        if any(frag.lower() in tag_lower for frag in _TAG_BLACKLIST_FRAGMENTS):
            continue
        clean.append(tag)
    return clean[:max_tags]


def analyze_content_with_ml(content_data: dict) -> dict:
    """Analyze content using ML models (Text)."""
    try:
        from core.services.agent_model_router import get_agent_model_router
        router = get_agent_model_router()
        result = router.auto_route(
            data=content_data,
            task_hint=TaskType.TEXT,
            max_models=2
        )
        return {
            'ml_used': True,
            'task_type': result.auto_selection.get('task_type', 'text'),
            'models_used': result.models_used,
            'confidence': round(result.confidence, 2),
            'ml_insights': result.explanation,
            'content_analysis': result.prediction if hasattr(result, 'prediction') else None,
        }
    except Exception as e:
        logger.warning(f"ML content analysis failed: {e}")
        return {'ml_used': False, 'reason': f'ML error: {str(e)}'}


# Content type configurations
CONTENT_TYPES = {
    'blog_post': {
        'name': 'Blog Post',
        'description': 'SEO-optimized blog post with title, intro, sections, and conclusion',
        'default_word_count': 1500,
        'structure': ['title', 'meta_description', 'intro', 'sections', 'conclusion', 'tags']
    },
    'podcast_script': {
        'name': 'Podcast Script',
        'description': 'Conversational podcast script with intro, segments, and outro',
        'default_word_count': 2000,
        'structure': ['title', 'intro_hook', 'segments', 'transitions', 'outro', 'show_notes']
    },
    'video_script': {
        'name': 'Video Script',
        'description': 'Video script with scenes, narration, and visual cues',
        'default_word_count': 1000,
        'structure': ['title', 'hook', 'scenes', 'narration', 'b_roll_suggestions', 'outro']
    },
    'article': {
        'name': 'Article',
        'description': 'Professional article with headline, lead, body, and CTA',
        'default_word_count': 1200,
        'structure': ['headline', 'subheadline', 'lead', 'body_sections', 'conclusion', 'cta']
    },
    'social_thread': {
        'name': 'Social Media Thread',
        'description': 'Series of connected posts for social platforms',
        'default_word_count': 500,
        'structure': ['hook_post', 'thread_posts', 'cta_post', 'hashtags']
    },
    'newsletter': {
        'name': 'Email Newsletter',
        'description': 'Email newsletter with subject, preview, and sections',
        'default_word_count': 800,
        'structure': ['subject_line', 'preview_text', 'greeting', 'sections', 'cta', 'sign_off']
    },
    'internal_document': {
        'name': 'Internal Document',
        'description': 'Internal planning or strategy document (initiative stages, technical specs)',
        'default_word_count': 2000,
        'structure': ['title', 'executive_summary', 'sections', 'key_findings', 'recommendations']
    }
}

# Tone presets
TONE_PRESETS = {
    'professional': 'Clear, authoritative, business-appropriate language',
    'conversational': 'Friendly, approachable, like talking to a colleague',
    'educational': 'Informative, patient, explains concepts clearly',
    'entertaining': 'Engaging, witty, keeps reader hooked',
    'persuasive': 'Compelling, action-oriented, drives decisions',
    'technical': 'Precise, detailed, assumes domain knowledge'
}


class ContentWriterAgent(BaseAgent):
    """
    Agent that transforms research into professional written content.

    Takes spider data, web research, or any context and produces
    blog posts, podcast scripts, video scripts, articles, and more.

    Session 523: Now uses Intelligent Prompting System for rich, context-aware content.
    """

    name = "ContentWriterAgent"
    llm_timeout = 180.0  # Session 1074: Long-form content generation needs 3 min

    # Base system prompt - will be enhanced with intelligent context
    system_prompt = """You are ContentWriterAgent, a professional content writer who transforms research into compelling written content.

Your job is to take research data and create polished, ready-to-publish content in various formats.

You excel at:
1. Extracting key insights from research and presenting them engagingly
2. Adapting tone and style for different audiences
3. Creating proper structure for each content type
4. Writing SEO-optimized content with natural keyword usage
5. Crafting compelling hooks, transitions, and calls-to-action

Content Types You Create:
- Blog Posts: SEO-optimized with headers, intro, sections, conclusion
- Podcast Scripts: Conversational with intro, segments, transitions, outro
- Video Scripts: Scene-based with narration and visual cues
- Articles: Professional with headline, lead, body, CTA
- Social Threads: Connected posts with hooks and hashtags
- Newsletters: Email-ready with subject, preview, sections

Always deliver content that's:
- Based on the provided research (don't make up facts)
- Properly structured for the format
- Written in the requested tone
- Approximately the requested word count
- Ready to publish with minimal editing

DELEGATION (Session 744):
If you need something outside your expertise, use the delegate_to_specialist tool:
- Need research/data? Delegate to ResearchAgent
- Need images/graphics? Delegate to ImageAgent
- Need trending topics? Delegate to TrendAnalysisAgent
- Need SEO optimization? Delegate to SEOOptimizerAgent
- Need competitor info? Delegate to CompetitorAnalysisAgent

Always delegate tasks you cannot perform yourself rather than refusing or making up data."""

    tools = []  # Content generation is done via direct GPT call, not sub-tools

    # Session 763: Mission Control configuration
    actionable_config = ActionableOutputConfig(
        enabled=True,
        item_type='review',
        default_urgency='medium',
        min_confidence=0.0,
        actions=[
            {'id': 'publish', 'label': 'Publish', 'style': 'success', 'description': 'Publish content immediately'},
            {'id': 'schedule', 'label': 'Schedule', 'style': 'primary', 'description': 'Schedule for later'},
            {'id': 'edit', 'label': 'Request Edit', 'style': 'warning', 'description': 'Flag for editing'},
            {'id': 'reject', 'label': 'Reject', 'style': 'danger', 'description': 'Do not publish'},
        ],
        payload_fields=['title', 'content_type', 'word_count', 'tone', 'target_audience'],
        max_items_per_hour=5
    )

    def __init__(self, user=None, project_id: str = None):
        """Initialize the content writer agent."""
        super().__init__(user)
        self.project_id = project_id
        self._intelligent_prompt_cache = None

    def _build_intelligent_system_prompt(
        self,
        scifi_context: Dict[str, Any],
        spider_context: Dict[str, Any],
        content_type: str = 'blog_post',
        topic: str = ''  # Session 891: Added for finance context injection
    ) -> str:
        """
        Session 523: Build an intelligent, context-aware system prompt.

        Includes:
        - Platform context (capabilities, agents, etc.)
        - Memory Palace context (past interactions)
        - Agent mood influence
        - User preferences
        - Dynamic year/date references
        """
        now = datetime.now()
        year = now.year
        month_year = now.strftime('%B %Y')
        today = now.strftime('%B %d, %Y')

        prompt_parts = [self.system_prompt]

        # Session 1001B: Dynamic platform summary replaces static PLATFORM_CONTEXT
        # (PLATFORM_CONTEXT listed every spider/agent name, causing fabrication)
        prompt_parts.append(f"\n\n{self._build_dynamic_platform_summary()}")

        # Add temporal awareness
        prompt_parts.append(f"""

## TEMPORAL AWARENESS (Session 523 / Strengthened Session 1006)
- Current Date: {today}
- Current Year: {year}
- CRITICAL: All content must be current and relevant to {month_year}
- DO NOT reference outdated years like {year-2} or {year-1} unless discussing historical context
- Use phrases like "in {year}" and "this {month_year}" to ensure freshness
- Your training data may be outdated. When writing about current events, politics,
  or any time-sensitive topic, ground your claims ONLY in the source data provided.
  Do NOT rely on your training data for who currently holds political office,
  recent legislation, or market conditions. If no source data is provided for a
  claim, state the fact without temporal qualifiers rather than guessing.""")

        # Add agent mood influence from scifi_context
        if scifi_context:
            mood = scifi_context.get('mood', {})
            if mood:
                mood_name = mood.get('name', 'focused')
                mood_influence = mood.get('description', '')
                prompt_parts.append(f"""

## CREATIVE MOOD (Session 523)
Current Mood: **{mood_name.title()}**
{mood_influence}
This influences your writing style - embrace it!""")

            # Add evolution level if available
            evolution = scifi_context.get('evolution', {})
            if evolution:
                level = evolution.get('level', 1)
                title = evolution.get('title', 'Content Writer')
                prompt_parts.append(f"""

## AGENT EVOLUTION
Level: {level} - {title}
Your experience level influences the sophistication of your writing.""")

        # Add Memory Palace context - past successful content
        if MEMORY_AVAILABLE and self.user:
            try:
                recent_memories = ConversationMemory.objects.filter(
                    user=self.user,
                    memory_type__in=['success', 'insight', 'learning']
                ).order_by('-created_at')[:5]

                if recent_memories:
                    memory_text = "\n".join([
                        f"- {m.summary[:100]}..." if len(m.summary) > 100 else f"- {m.summary}"
                        for m in recent_memories
                    ])
                    prompt_parts.append(f"""

## MEMORY PALACE - Past Interactions (Session 523)
I remember our previous work together:
{memory_text}

Use these insights to personalize and improve the content.""")
            except Exception as e:
                logger.debug(f"Could not fetch memories: {e}")

        # Session 858: Use injected user context (from AgentRouter) instead of DB query
        user_context = getattr(self, '_user_context', {})
        if user_context and user_context.get('has_user_context'):
            pref_items = []

            # User's name for personalization
            user_name = user_context.get('name', '')
            if user_name:
                pref_items.append(f"- Writing for: {user_name}")

            # Communication style
            comm_style = user_context.get('communication_style', '')
            if comm_style:
                pref_items.append(f"- Preferred tone: {comm_style}")

            # User's goals (influences content direction)
            goals = user_context.get('goals', [])
            if goals:
                goals_text = ", ".join(goals[:3]) if isinstance(goals, list) else str(goals)
                pref_items.append(f"- User's goals: {goals_text}")

            # Memory summary (past preferences and patterns)
            memory_summary = user_context.get('memory_summary', '')
            if memory_summary:
                pref_items.append(f"- Past patterns: {memory_summary[:200]}...")

            if pref_items:
                prompt_parts.append(f"""

## USER CONTEXT (Session 858)
{chr(10).join(pref_items)}

Tailor the content to match this user's preferences and goals.""")

        # Fallback to DB query if no injected context
        elif self.user:
            try:
                from core.models_unified_system import UserPreferences
                prefs = UserPreferences.objects.filter(user=self.user).first()
                if prefs:
                    pref_items = []
                    if hasattr(prefs, 'preferred_tone') and prefs.preferred_tone:
                        pref_items.append(f"- Preferred tone: {prefs.preferred_tone}")
                    if hasattr(prefs, 'writing_style') and prefs.writing_style:
                        pref_items.append(f"- Writing style: {prefs.writing_style}")
                    if hasattr(prefs, 'industry') and prefs.industry:
                        pref_items.append(f"- Industry focus: {prefs.industry}")

                    if pref_items:
                        prompt_parts.append(f"""

## USER PREFERENCES (Session 523)
{chr(10).join(pref_items)}

Tailor the content to match these preferences.""")
            except Exception as e:
                logger.debug(f"Could not fetch user preferences: {e}")

        # Session 1001B: Inject full spider intelligence (trends, discussions, articles, market data)
        if spider_context:
            spider_intel = self._format_spider_intelligence(spider_context)
            if spider_intel:
                prompt_parts.append(f"\n\n{spider_intel}")

        # Session 886: Add performance context for feedback loop
        # Session 990: Wrapped with timeout to prevent context builders from hanging
        if PERFORMANCE_CONTEXT_AVAILABLE and get_blog_performance_context:
            try:
                from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeoutError
                with ThreadPoolExecutor(max_workers=1) as executor:
                    future = executor.submit(
                        get_blog_performance_context,
                        limit=10,
                        include_learning_rules=True,
                        include_engagement=True
                    )
                    try:
                        performance_context = future.result(timeout=15)
                    except FuturesTimeoutError:
                        logger.warning("Blog performance context timed out after 15s — skipping")
                        performance_context = None
                if performance_context:
                    prompt_parts.append(f"\n\n{performance_context}")
                    logger.info(f"Session 886: Injected performance context ({len(performance_context)} chars)")
            except Exception as e:
                logger.warning(f"Could not inject performance context: {e}")

        # Session 891: Add domain-specific content context (finance, sports, AI, crypto, etc.)
        # Session 990: Wrapped with timeout
        if DOMAIN_CONTEXT_AVAILABLE and get_domain_content_context:
            try:
                from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeoutError
                with ThreadPoolExecutor(max_workers=1) as executor:
                    future = executor.submit(
                        get_domain_content_context,
                        topic=topic or "",
                        max_domains=2
                    )
                    try:
                        domain_context = future.result(timeout=15)
                    except FuturesTimeoutError:
                        logger.warning("Domain content context timed out after 15s — skipping")
                        domain_context = None
                if domain_context and len(domain_context) > 100:  # Skip if only generic
                    prompt_parts.append(f"\n\n{domain_context}")
                    domain, confidence = detect_content_domain(topic or "") if detect_content_domain else ("unknown", 0)
                    logger.info(f"Session 891: Injected {domain} domain context ({len(domain_context)} chars, {confidence:.0%} confidence)")
            except Exception as e:
                logger.warning(f"Could not inject domain context: {e}")

        # Add content-type specific enhancement
        prompt_parts.append(f"""

## CONTENT EXCELLENCE STANDARDS
For this {content_type}, ensure:
- Hook readers in the first sentence
- Use data and specific examples from the research
- Include actionable takeaways
- Write with authority and expertise
- Make it shareable and memorable""")

        return "\n".join(prompt_parts)

    def _build_dynamic_platform_summary(self) -> str:
        """
        Session 1001B: Build a compact platform summary from live DB counts.

        Replaces the static PLATFORM_CONTEXT (~1,400 tokens listing every spider/agent
        name) which caused GPT to fabricate stories about spiders it had no data from.
        """
        try:
            from core.models import Agent
            from core.models_unified_system import SpiderData
            from core.models_heart import HeartBeat
            from django.utils import timezone
            from datetime import timedelta

            now = timezone.now()
            cutoff = now - timedelta(hours=72)

            active_agents = Agent.objects.filter(is_active=True).count()

            spider_qs = SpiderData.objects.filter(created_at__gte=cutoff)
            active_spiders = spider_qs.values('spider_name').distinct().count()
            data_points = spider_qs.count()

            health_line = "unavailable"
            hb = HeartBeat.objects.order_by('-recorded_at').first()
            if hb:
                health_line = f"{hb.overall_status} (score: {hb.health_score})"

            return (
                "## Platform Context (Live)\n"
                f"- Active agents: {active_agents} | Data spiders active (72h): {active_spiders} | Data points collected: {data_points:,}\n"
                f"- System health: {health_line}\n"
                "- Infrastructure: Django + PostgreSQL + Redis + Celery\n\n"
                "This is what you are part of. Do NOT list specific spider or agent names "
                "unless they appear in the research data below.\n"
            )
        except Exception as e:
            logger.debug(f"Dynamic platform summary failed: {e}")
            return "## Platform Context\nAI content platform with multiple agents, spiders, and services.\n"

    def _format_spider_intelligence(self, spider_context: Dict[str, Any]) -> str:
        """
        Session 1001B: Format the rich spider_context dict into citable markdown.

        SpiderContextBuilder returns: relevant_trends, discussions, articles,
        market_data, related_discussions, freshness — all previously ignored.
        """
        sections = []

        # --- relevant_trends ---
        try:
            trends = spider_context.get('relevant_trends', [])
            if trends:
                lines = []
                for t in trends[:7]:
                    if isinstance(t, dict):
                        topic = t.get('topic', t.get('title', str(t)))
                        score = t.get('score', '')
                        sources = ', '.join(t.get('sources', [])) if isinstance(t.get('sources'), list) else ''
                        parts = [f"**{topic}**"]
                        if score:
                            parts.append(f"(score: {score})")
                        if sources:
                            parts.append(f"(sources: {sources})")
                        lines.append(f"- {' '.join(parts)}")
                    else:
                        lines.append(f"- {t}")
                if lines:
                    sections.append("### Trending Topics\n" + "\n".join(lines))
        except Exception as e:
            logger.debug(f"Spider intel trends format error: {e}")

        # --- discussions ---
        try:
            discussions = spider_context.get('discussions', [])
            if discussions:
                lines = []
                for d in discussions[:5]:
                    if isinstance(d, dict):
                        title = d.get('title', d.get('topic', str(d)))
                        source = d.get('source', d.get('spider_name', ''))
                        lines.append(f"- {title}" + (f" -- {source}" if source else ""))
                    else:
                        lines.append(f"- {d}")
                if lines:
                    sections.append("### Discussions\n" + "\n".join(lines))
        except Exception as e:
            logger.debug(f"Spider intel discussions format error: {e}")

        # --- articles ---
        try:
            articles = spider_context.get('articles', [])
            if articles:
                lines = []
                for a in articles[:5]:
                    if isinstance(a, dict):
                        title = a.get('title', a.get('name', str(a)))
                        url = a.get('url', a.get('source', ''))
                        lines.append(f"- {title}" + (f" -- {url}" if url else ""))
                    else:
                        lines.append(f"- {a}")
                if lines:
                    sections.append("### Articles & Projects\n" + "\n".join(lines))
        except Exception as e:
            logger.debug(f"Spider intel articles format error: {e}")

        # --- market_data ---
        try:
            market = spider_context.get('market_data')
            if market and isinstance(market, dict):
                lines = []
                summary = market.get('summary', '')
                if summary:
                    lines.append(summary)
                for key in ('crypto', 'stocks'):
                    items = market.get(key, [])
                    for item in items[:3]:
                        if isinstance(item, dict):
                            name = item.get('name', item.get('symbol', ''))
                            price = item.get('price', '')
                            change = item.get('change', item.get('change_24h', ''))
                            parts = [name]
                            if price:
                                parts.append(str(price))
                            if change:
                                parts.append(f"({change})")
                            lines.append(f"- {' '.join(parts)}")
                if lines:
                    sections.append("### Market Data\n" + "\n".join(lines))
        except Exception as e:
            logger.debug(f"Spider intel market format error: {e}")

        # --- related_discussions ---
        try:
            related = spider_context.get('related_discussions', [])
            if related:
                lines = []
                for r in related[:5]:
                    if isinstance(r, dict):
                        title = r.get('title', r.get('topic', str(r)))
                        source = r.get('source', r.get('spider_name', ''))
                        snippet = str(r.get('snippet', r.get('summary', '')))[:120]
                        line = f"- {title}"
                        if source:
                            line += f" -- {source}"
                        if snippet:
                            line += f": {snippet}"
                        lines.append(line)
                    else:
                        lines.append(f"- {r}")
                if lines:
                    sections.append("### Related Discussions\n" + "\n".join(lines))
        except Exception as e:
            logger.debug(f"Spider intel related format error: {e}")

        # --- freshness ---
        try:
            freshness = spider_context.get('freshness', {})
            if freshness and isinstance(freshness, dict):
                quality = freshness.get('data_quality', '')
                hours = freshness.get('hours_covered', '')
                updated = freshness.get('last_updated', '')
                if quality or hours:
                    parts = []
                    if quality:
                        parts.append(f"Data quality: {quality}")
                    if hours:
                        parts.append(f"covering last {hours}h")
                    if updated:
                        parts.append(f"updated {updated}")
                    sections.append(f"*{', '.join(parts)}*")
        except Exception as e:
            logger.debug(f"Spider intel freshness format error: {e}")

        if not sections:
            return ""

        header = "## Spider Intelligence (Real-Time Data -- cite these specifically)"
        footer = "Reference these data points by name when writing. Do not invent additional spider findings."
        body = "\n\n".join(sections)

        # Soft cap to prevent prompt bloat
        if len(body) > 2000:
            body = body[:2000] + "\n... (truncated)"

        return f"{header}\n\n{body}\n\n{footer}"

    def execute(
        self,
        task: str,
        context: Dict[str, Any],
        scifi_context: Dict[str, Any],
        spider_context: Dict[str, Any]
    ) -> AgentResult:
        """
        Execute content writing based on research.

        Args:
            task: Description of what to write
            context: Must contain:
                - content_type: blog_post, podcast_script, video_script, article, social_thread, newsletter
                - research: The research content to transform
                Optional:
                - tone: professional, conversational, educational, entertaining, persuasive, technical
                - target_audience: Who the content is for
                - word_count: Approximate word count
                - topic: Main topic (extracted from research if not provided)
                - keywords: SEO keywords to include
                Session 858: User context available:
                - user: Full user context dict
                - user_name: User's name
                - user_communication_style: Preferred communication style
                - user_goals: User's goals
            scifi_context: Sci-fi features context
            spider_context: Spider intelligence context

        Returns:
            AgentResult with the generated content
        """
        start_time = time.time()
        scifi_context = scifi_context or {}
        spider_context = spider_context or {}

        # Session 875: Ensure context is a dict (defensive fix for list being passed)
        if not isinstance(context, dict):
            logger.warning(f"ContentWriterAgent received non-dict context (type={type(context).__name__}), using empty dict")
            context = {}

        # Session 858: Extract user context for personalization
        # Session 1102: Guard against stringified context values
        user_context = context.get('user', {})
        if not isinstance(user_context, dict):
            user_context = {}
        self._user_context = user_context  # Store for use in prompt building

        # Session 1103: If pipeline provided research evidence, inject it as highest-priority
        # context so GPT uses it instead of generic spider data
        research_content = context.get('research', '')
        logger.info(
            "📝 [Session 1103] ContentWriterAgent research check: context keys=%s, research_len=%d, content_keys=%s",
            list(context.keys())[:10], len(research_content) if research_content else 0,
            list(context.get('content', {}).keys())[:5] if isinstance(context.get('content'), dict) else type(context.get('content')).__name__,
        )
        if research_content and len(str(research_content)) > 200:
            self._evidence_context_override = str(research_content)
            logger.info("📝 [Session 1103] Evidence-first mode ACTIVE: %d chars injected as primary source", len(str(research_content)))
        else:
            self._evidence_context_override = ''
            logger.info("📝 [Session 1103] Evidence-first mode SKIPPED: research_content=%s", repr(research_content)[:100] if research_content else 'EMPTY')

        # Session 529: Build intelligent prompt with full context
        self._intelligent_context = self._build_intelligent_prompt(task, scifi_context, spider_context)

        with self.time_travel_session("content_writing", task, input_data=context):
            try:
                # Handle simple diagnostic/identification queries
                task_lower = task.lower() if task else ''
                if any(keyword in task_lower for keyword in ['state your name', 'who are you', 'your capability', 'what can you do', 'introduce yourself']):
                    execution_time = int((time.time() - start_time) * 1000)
                    return AgentResult(
                        success=True,
                        message=f"I am {self.name}, a specialist in transforming research into polished content. One capability: I write blog posts, articles, video scripts, podcast scripts, social threads, and newsletters with customizable tone, audience targeting, and SEO optimization.",
                        data={'type': 'self_description', 'capabilities': ['blog_posts', 'articles', 'scripts', 'newsletters', 'seo_optimization']},
                        agent_name=self.name,
                        execution_time_ms=execution_time
                    )

                # Extract parameters
                content_type = context.get('content_type', 'blog_post')
                research = context.get('research', '')

                # Session 858: Use user's preferred communication style as default tone
                default_tone = user_context.get('communication_style', 'professional')
                tone = context.get('tone', default_tone)

                target_audience = context.get('target_audience', 'general audience')
                word_count = context.get('word_count', CONTENT_TYPES.get(content_type, {}).get('default_word_count', 1500))
                topic = context.get('topic', '')
                keywords = context.get('keywords', [])

                # Validate content type
                if content_type not in CONTENT_TYPES:
                    return AgentResult(
                        success=False,
                        error=f"Unknown content type: {content_type}. Available: {list(CONTENT_TYPES.keys())}",
                        agent_name=self.name
                    )

                # Validate we have research
                if not research and not task:
                    return AgentResult(
                        success=False,
                        error="No research or task provided. Need content to transform.",
                        agent_name=self.name
                    )

                self.record_decision(
                    decision_type="content_type_selection",
                    action=f"Writing {content_type} from research",
                    reasoning=f"User requested {content_type}, tone: {tone}, audience: {target_audience}",
                    alternatives=list(CONTENT_TYPES.keys()),
                    confidence=0.95
                )

                logger.info(f"📝 ContentWriterAgent: Creating {content_type}")
                logger.info(f"   Research length: {len(research)} chars")
                logger.info(f"   Tone: {tone}, Audience: {target_audience}")
                logger.info(f"   Target word count: {word_count}")

                # Build the prompt for GPT
                content_config = CONTENT_TYPES[content_type]
                tone_description = TONE_PRESETS.get(tone, tone)

                prompt = self._build_content_prompt(
                    content_type=content_type,
                    content_config=content_config,
                    research=research,
                    task=task,
                    topic=topic,
                    tone=tone,
                    tone_description=tone_description,
                    target_audience=target_audience,
                    word_count=word_count,
                    keywords=keywords
                )

                # Session 854: Add Flagship template injection for distinctive content
                use_flagship = context.get('flagship', True)  # Default to flagship
                cta_type = context.get('cta_type', 'newsletter')

                if use_flagship and content_type in ['blog_post', 'article', 'newsletter']:
                    try:
                        from core.services.content_voice_system import generate_flagship_injection
                        from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeoutError
                        # Session 990: Wrap flagship injection with timeout — it runs
                        # multiple DB queries (agent recoveries, dreams, learnings, decisions)
                        with ThreadPoolExecutor(max_workers=1) as executor:
                            future = executor.submit(
                                generate_flagship_injection,
                                topic=topic or task[:50],
                                audience=target_audience,
                                cta_type=cta_type
                            )
                            try:
                                flagship_injection = future.result(timeout=15)
                            except FuturesTimeoutError:
                                logger.warning("Flagship injection timed out after 15s — skipping")
                                flagship_injection = None
                        if flagship_injection:
                            prompt = prompt + "\n\n" + flagship_injection
                            logger.info(f"Session 854: Added flagship template injection ({len(flagship_injection)} chars)")
                    except Exception as e:
                        logger.warning(f"Could not add flagship injection: {e}")

                # Session 523: Generate content via GPT with intelligent prompting
                # Session 891: Pass topic for finance context injection
                generated_content = self._generate_content(
                    prompt,
                    content_type,
                    scifi_context=scifi_context,
                    spider_context=spider_context,
                    topic=topic
                )

                if not generated_content:
                    return AgentResult(
                        success=False,
                        error="Failed to generate content",
                        agent_name=self.name
                    )

                execution_time = int((time.time() - start_time) * 1000)

                # Session 856: Extract content details for descriptive message
                content_title = (
                    generated_content.get('title') or
                    generated_content.get('headline') or
                    topic or
                    self._extract_topic(research, task) or
                    'Untitled'
                ) if isinstance(generated_content, dict) else 'Content'

                actual_word_count = (
                    len(generated_content.get('full_text', '').split())
                    if isinstance(generated_content, dict) else len(str(generated_content).split())
                )

                # Session 857: Check for truncation and calculate quality tier
                was_truncated = (
                    generated_content.get('_truncated', False)
                    if isinstance(generated_content, dict)
                    else getattr(self, '_last_generation_truncated', False)
                )

                quality_tier, confidence = self._calculate_quality_tier(
                    content_data=generated_content if isinstance(generated_content, dict) else {},
                    content_type=content_type,
                    target_word_count=word_count,
                    was_truncated=was_truncated
                )

                # Session 954: Build provenance to track data sources
                from datetime import timezone
                provenance_sources = []

                # Track research source if provided
                if research:
                    provenance_sources.append({
                        'name': 'ResearchContext',
                        'endpoint': 'input/research',
                        'retrieved_at': datetime.now(timezone.utc).isoformat(),
                        'record_count': len(research.split()) if research else 0,
                    })

                # Track spider data if used
                if spider_context:
                    spider_count = len(spider_context.get('data', [])) if isinstance(spider_context.get('data'), list) else 1
                    provenance_sources.append({
                        'name': 'SpiderNetwork',
                        'endpoint': 'spider/context',
                        'retrieved_at': datetime.now(timezone.utc).isoformat(),
                        'record_count': spider_count,
                    })

                # Track domain context if injected
                if DOMAIN_CONTEXT_AVAILABLE and topic:
                    provenance_sources.append({
                        'name': 'DomainContext',
                        'endpoint': 'domain/content-context',
                        'retrieved_at': datetime.now(timezone.utc).isoformat(),
                        'record_count': 1,
                    })

                provenance = build_provenance(
                    report_type='content_generation',
                    agent_name=self.name,
                    sources=provenance_sources,
                    stale_threshold_hours=72.0,  # Content sources valid for 72h
                )
                provenance.disclaimer = format_disclaimer('market_report')  # Appropriate for content

                # Session 856: Build descriptive message for content review UI
                content_type_display = content_config['name']
                message_parts = [f"{content_type_display}: \"{content_title[:80]}\""]
                message_parts.append(f"{actual_word_count:,} words")
                if tone:
                    message_parts.append(f"{tone} tone")
                if target_audience:
                    message_parts.append(f"for {target_audience}")

                # Session 857: Add quality tier and truncation warning to message
                message_parts.append(f"[{quality_tier.upper()}]")
                if was_truncated:
                    message_parts.append("⚠️ TRUNCATED")

                descriptive_message = " | ".join(message_parts)

                result = AgentResult(
                    success=True,
                    message=descriptive_message,
                    data={
                        'content_type': content_type,
                        'title': content_title,
                        'word_count': actual_word_count,
                        'tone': tone,
                        'target_audience': target_audience,
                        'content': generated_content,
                        'metadata': {
                            'tone': tone,
                            'target_audience': target_audience,
                            'word_count_target': word_count,
                            'actual_word_count': actual_word_count,
                            'topic': topic or self._extract_topic(research, task),
                            # Session 857: Add quality metadata
                            'quality_tier': quality_tier,
                            'confidence': confidence,
                            'truncated': was_truncated,
                        },
                        # Session 954: Add provenance tracking
                        'provenance': provenance.to_dict(),
                        'publishable': provenance.publishable,
                        'validation_status': provenance.validation_status,
                    },
                    agent_name=self.name,
                    execution_time_ms=execution_time,
                    decisions_made=self._tt_decision_count,
                    # Session 857: Set new AgentResult fields
                    quality_tier=quality_tier,
                    output_category=OutputCategory.CONTENT.value,
                    truncated=was_truncated,
                    confidence=confidence,
                )

                self.mark_decision_outcome(
                    success=True,
                    result_summary=f"Created {content_type} successfully"
                )

                # Learning hooks
                self._record_learning_outcome(
                    result, task, context,
                    spider_data_used=bool(spider_context),
                    scifi_context_used=bool(scifi_context)
                )

                # Session 757: Store rich memory with actual content, not just "success"
                self._create_content_memory(
                    content_type=content_type,
                    generated_content=generated_content,
                    task=task,
                    tone=tone,
                    target_audience=target_audience,
                    word_count=result.data['metadata']['actual_word_count'],
                    topic=result.data['metadata']['topic'],
                    execution_time_ms=execution_time
                )

                self._share_knowledge(
                    knowledge_type='technique',
                    title=f"Content created: {content_type}",
                    knowledge_value={
                        'content_type': content_type,
                        'tone': tone,
                        'word_count': word_count,
                        'execution_time_ms': execution_time
                    },
                    confidence=0.85
                )

                # Session 763: Create Mission Control attention item
                self._maybe_create_attention_item(result, task, context)

                # Session 1006: Persist output to Deliverable
                full_text = generated_content.get('full_text', '') if isinstance(generated_content, dict) else str(generated_content)
                self._save_to_deliverable(
                    title=f"{content_type}: {task[:80]}",
                    content=full_text or result.message,
                    deliverable_type='document',
                    category='Content Writing',
                    tags=[content_type, tone],
                    metadata={'task': task[:200], 'content_type': content_type, 'tone': tone, 'word_count': word_count},
                )

                return result

            except Exception as e:
                logger.error(f"ContentWriterAgent error: {e}", exc_info=True)
                return AgentResult(
                    success=False,
                    error=str(e),
                    agent_name=self.name,
                    execution_time_ms=int((time.time() - start_time) * 1000)
                )

    def _create_content_memory(
        self,
        content_type: str,
        generated_content: Dict[str, Any],
        task: str,
        tone: str,
        target_audience: str,
        word_count: int,
        topic: str,
        execution_time_ms: int
    ) -> None:
        """
        Session 757: Create a rich memory with actual content learnings.

        Instead of just storing "Successfully created Blog Post", we store:
        - The actual title/headline created
        - A summary of the content
        - Key sections/topics covered
        - Writing patterns that worked
        - Audience and tone insights
        """
        if not self.memory_service or not self.agent_model:
            return

        try:
            # Extract meaningful content for the memory
            content_title = "Untitled"
            content_summary = ""
            key_sections = []

            if isinstance(generated_content, dict):
                # Get title/headline
                content_title = (
                    generated_content.get('title') or
                    generated_content.get('headline') or
                    generated_content.get('subject_line') or
                    topic or
                    "Untitled"
                )

                # Get sections/structure for learning
                if generated_content.get('sections'):
                    for section in generated_content['sections'][:5]:
                        if isinstance(section, dict):
                            key_sections.append(section.get('header', section.get('title', 'Section')))
                        elif isinstance(section, str):
                            key_sections.append(section[:50])

                # Build content summary from full_text
                full_text = generated_content.get('full_text', '')
                if full_text:
                    # Take first 500 chars as summary
                    content_summary = full_text[:500].strip()
                    if len(full_text) > 500:
                        content_summary += "..."

            # Build rich memory content
            memory_content = f"""Created {CONTENT_TYPES[content_type]['name']}: "{content_title}"

Topic: {topic}
Tone: {tone} | Audience: {target_audience}
Word Count: {word_count} words | Time: {execution_time_ms}ms

"""
            if key_sections:
                memory_content += f"Sections covered:\n"
                for section in key_sections:
                    memory_content += f"  - {section}\n"
                memory_content += "\n"

            if content_summary:
                memory_content += f"Content preview:\n{content_summary}\n\n"

            # Add learning insight
            memory_content += f"""Learning: Successfully created {content_type} for {target_audience} audience using {tone} tone. Structure: {len(key_sections)} sections."""

            # Build memory title
            memory_title = f"Created {content_type}: {content_title[:40]}"
            if len(content_title) > 40:
                memory_title += "..."

            # Create the memory with rich content
            from core.models_unified_system import AgentMemory
            AgentMemory.objects.create(
                agent=self.agent_model,
                title=memory_title,
                content=memory_content,
                context=f"Task: {task}",
                memory_type="success",
                memory_outcome="success",
                importance_score=0.85,
                source_type="agent_execution",
                tags=[self.name, content_type, tone, "content_creation"],
            )

            logger.info(f"📝 Session 757: Created rich memory for {content_type}: {content_title[:30]}...")

            # Session 860: Also save blog_post content to SelfBlog so it's not ephemeral
            if content_type == 'blog_post' and isinstance(generated_content, dict):
                self._save_to_selfblog(
                    generated_content=generated_content,
                    content_title=content_title,
                    topic=topic,
                    tone=tone,
                    target_audience=target_audience,
                    word_count=word_count
                )

        except Exception as e:
            logger.warning(f"Failed to create content memory: {e}")

    def _save_to_selfblog(
        self,
        generated_content: Dict[str, Any],
        content_title: str,
        topic: str,
        tone: str,
        target_audience: str,
        word_count: int
    ) -> None:
        """
        Session 860: Save blog_post content to SelfBlog so it persists.

        Previously, blog content was only stored in the ephemeral AgentResult
        and a summary memory. The actual content was lost after the request.
        This method saves it to SelfBlog for retrieval in the Content Studio.
        """
        try:
            from core.models_unified_system import SelfBlog
            from datetime import timedelta
            from django.utils import timezone

            # Dedup check — skip if same title exists in last 7 days
            if SelfBlog.objects.filter(
                title=content_title,
                created_at__gte=timezone.now() - timedelta(days=7)
            ).exists():
                logger.info(f"Session 860: Skipping duplicate blog title: {content_title[:60]}")
                return

            # Extract structured content
            intro = generated_content.get('intro', '')
            conclusion = generated_content.get('conclusion', '')
            sections = generated_content.get('sections', [])
            meta_description = generated_content.get('meta_description', '')
            keywords = generated_content.get('keywords', [])
            full_text = generated_content.get('full_text', '')

            # Create tags from keywords and topic
            tags = []
            if keywords:
                tags.extend(keywords[:5])
            if topic:
                tags.append(topic)
            if tone:
                tags.append(tone)

            # Session 961: Run through multi-agent review panel
            review_result = None
            if ENABLE_CONTENT_REVIEW:
                try:
                    from core.services.content_review_panel import ContentReviewPanel
                    panel = ContentReviewPanel()
                    review_result = panel.review(
                        content_data=generated_content,
                        topic=topic,
                        tone=tone,
                        target_audience=target_audience,
                    )
                    logger.info(
                        f"Session 961: Review panel decision={review_result.decision} "
                        f"confidence={review_result.confidence:.2f} "
                        f"panel={review_result.panel_composition} "
                        f"time={review_result.execution_time_ms}ms"
                    )
                except Exception as e:
                    logger.warning(f"Session 961: Review panel failed: {e}")

            # Session 961: Map review decision to SelfBlog fields
            if review_result and review_result.decision == 'publish':
                initial_status = 'pending_review'
                content_type_val = 'public'
            elif review_result and review_result.decision == 'kill':
                initial_status = 'draft'
                content_type_val = 'internal'
            else:
                initial_status = 'draft'
                content_type_val = 'public'

            # Build stats snapshot
            stats_snapshot: Dict[str, Any] = {
                'agent_name': self.name,
                'topic': topic,
                'tone': tone,
                'target_audience': target_audience,
                'generated_by': 'ContentWriterAgent',
            }
            if review_result:
                stats_snapshot['review_panel'] = {
                    'decision': review_result.decision,
                    'confidence': review_result.confidence,
                    'panel': review_result.panel_composition,
                    'notes': review_result.review_notes[:500],
                    'spider_data_used': review_result.spider_data_used,
                    'time_ms': review_result.execution_time_ms,
                }

            # Sanitize tags — strip prompt leakage, oversized entries
            clean_tags = _sanitize_tags(tags)

            # Ensure full_text is populated (assemble from sections if needed)
            if not full_text and sections:
                full_text = '\n\n'.join(
                    s.get('content', '') if isinstance(s, dict) else str(s)
                    for s in sections
                )

            # Create the SelfBlog record
            blog = SelfBlog.objects.create(
                title=content_title,
                author='ContentWriterAgent',
                meta_description=meta_description or f"{content_title} - {topic}",
                intro=intro or (full_text[:500] if full_text else ""),
                sections=sections if sections else [{'header': 'Content', 'content': full_text}],
                conclusion=conclusion or "",
                full_text=full_text or "",
                word_count=word_count,
                category='blog',
                status=initial_status,
                content_type=content_type_val,
                tags=clean_tags,
                stats_snapshot=stats_snapshot,
            )

            logger.info(f"Session 860: Saved blog to SelfBlog: {blog.id} - {content_title[:40]}...")

            # Session 961: Auto-run PublishGate for 'publish' decisions
            if review_result and review_result.decision == 'publish':
                try:
                    from core.services.publish_gate import PublishGate
                    gate = PublishGate()
                    gate.evaluate(blog)
                except Exception as e:
                    logger.warning(f"Session 961: PublishGate auto-eval failed: {e}")

        except Exception as e:
            logger.warning(f"Failed to save blog to SelfBlog: {e}")

    def _build_content_prompt(
        self,
        content_type: str,
        content_config: Dict[str, Any],
        research: str,
        task: str,
        topic: str,
        tone: str,
        tone_description: str,
        target_audience: str,
        word_count: int,
        keywords: List[str],
        claims_block: str = '',
    ) -> str:
        """
        Build the GPT prompt for content generation.

        Session 523: Added source citation requirements.
        Phase 4: Optional claims_block appends citation rules for [C-xxxxxxxxxx] markers.
        """
        # Content-type specific instructions
        type_instructions = self._get_type_instructions(content_type, content_config)

        # Session 523: Extract sources from research for citation
        sources_instruction = ""
        if research and ("Source:" in research or "Published:" in research):
            sources_instruction = """

## SOURCE CITATION REQUIREMENTS (Session 523)
The research above includes REAL sources with publication dates. You MUST:
1. Reference specific data, statistics, or quotes from the sources
2. Attribute claims like "According to [Source]..." or "As reported by [Source]..."
3. Include a 'sources' array in your JSON output with all sources used
4. When mentioning numbers or facts, cite where they came from

Example attributions:
- "According to TechCrunch, the AI market is projected to reach $X billion..."
- "A recent MIT Technology Review article notes that..."
- "As reported by Reuters on December 21, 2025..."

This builds credibility and allows readers to verify the information."""

        prompt = f"""Create a {content_config['name']} based on the following research and requirements.

## RESEARCH CONTEXT (Real-Time Data from Spider Network)
{research if research else task}
{sources_instruction}

## REQUIREMENTS
- Content Type: {content_config['name']}
- Topic: {topic if topic else 'Extract from research'}
- Tone: {tone} - {tone_description}
- Target Audience: {target_audience}
- Target Word Count: ~{word_count} words
{f"- Keywords to Include: {', '.join(keywords)}" if keywords else ""}

## STRUCTURE REQUIREMENTS
{type_instructions}

## OUTPUT FORMAT
Return the content as a JSON object with the following structure based on content type.

For {content_type}, include these fields:
{json.dumps(content_config['structure'], indent=2)}

Plus these additional fields:
- 'full_text': Complete content as plain text with source attributions inline
- 'sources': Array of source objects used, each with {{"name": "...", "url": "...", "published": "..."}}

## IMPORTANT
- Base ALL content on the provided research - do not invent facts
- When referencing operational metrics (execution times, success rates, health scores), use ONLY the exact numbers from the Operational Telemetry section
- Do NOT fabricate specific incidents, error messages, or recovery narratives that are not in the provided research
- CITE YOUR SOURCES! Attribute specific claims to their sources
- Write in a natural, engaging style appropriate for {target_audience}
- Ensure the content is ready to publish with minimal editing
- Include practical examples from the provided data where appropriate
- Make it compelling, valuable, and credible to the reader

Generate the {content_config['name']} now:"""

        # Phase 4: Append claims citation block when claims data is provided
        if claims_block:
            prompt += f"""

CLAIMS DATA (cite these using [C-xxxxxxxxxx] inline):
{claims_block}

CITATION RULES:
- MUST cite claim IDs inline as [C-xxxxxxxxxx] when referencing data
- MUST include a 'Sources' section at the end mapping claim IDs to URLs
- Facts without a claim ID must be labeled [SPECULATION]"""

        return prompt

    def _get_type_instructions(self, content_type: str, content_config: Dict[str, Any]) -> str:
        """Get content-type specific writing instructions."""

        instructions = {
            'blog_post': """
- Title: Compelling, SEO-friendly (50-60 chars)
- Meta Description: Engaging summary (150-160 chars)
- Intro: Hook the reader, preview what they'll learn (100-150 words)
- Sections: 3-5 sections with H2 headers, each covering a key point
- Conclusion: Summarize key takeaways, include CTA
- Tags: 5-8 relevant tags for categorization""",

            'podcast_script': """
- Title: Episode title that attracts listeners
- Intro Hook: Attention-grabbing opener (30-60 seconds when spoken)
- Segments: 3-5 segments with talking points and transitions
- Transitions: Smooth bridges between segments
- Outro: Wrap-up, tease next episode, CTA for listeners
- Show Notes: Bullet points of key topics, links, resources""",

            'video_script': """
- Title: Video title optimized for clicks
- Hook: First 5 seconds to grab attention
- Scenes: Numbered scenes with duration, narration, and visual descriptions
- Narration: What to say (formatted for teleprompter)
- B-Roll Suggestions: Visual ideas for each section
- Outro: CTA, subscribe reminder, end screen content""",

            'article': """
- Headline: Powerful, specific headline
- Subheadline: Supporting detail or benefit
- Lead: Opening paragraph that hooks and informs (40-60 words)
- Body Sections: 3-5 sections building the argument/story
- Conclusion: Key takeaway
- CTA: Clear next step for the reader""",

            'social_thread': """
- Hook Post: Attention-grabbing first post (max 280 chars for Twitter)
- Thread Posts: 5-10 connected posts building the story/argument
- CTA Post: Final post with clear action
- Hashtags: 3-5 relevant hashtags""",

            'newsletter': """
- Subject Line: Compelling, personal, curiosity-inducing (40-50 chars)
- Preview Text: First line preview for inbox (90-100 chars)
- Greeting: Personal but professional
- Sections: 2-3 content sections with headers
- CTA: Clear primary call-to-action
- Sign Off: Warm, personal closing""",

            'internal_document': """
- Title: Clear, descriptive title for the document
- Executive Summary: 200-300 word overview of scope and goals
- Sections: 3-5 main content sections with clear H2 headers
- Key Findings: Summary of critical discoveries or decisions
- Recommendations: Prioritized recommendations with rationale
- Action Items (Required): Dedicated section with specific format:
  - Use bullet points: "- AgentName: Task description (Timeline)"
  - Include 3-5 concrete, assignable action items
  - Each item should name a responsible agent or role
  - Include timeline estimates where possible"""
        }

        return instructions.get(content_type, f"Follow standard {content_type} format.")

    def _generate_content(
        self,
        prompt: str,
        content_type: str,
        scifi_context: Dict[str, Any] = None,
        spider_context: Dict[str, Any] = None,
        topic: str = ''  # Session 891: Added for finance context injection
    ) -> Optional[Dict[str, Any]]:
        """
        Generate content using GPT with intelligent prompting.

        Session 523: Now uses _build_intelligent_system_prompt for rich context.
        Session 857: Added truncation detection and tracking.
        """
        try:
            from openai import OpenAI
            import os

            # Session 767: Add timeout to OpenAI client to prevent hanging
            client = OpenAI(
                api_key=os.getenv('OPENAI_API_KEY'),
                timeout=120.0  # 2 minute timeout for API calls
            )

            # Session 523: Build intelligent system prompt with all context
            # Session 891: Added topic parameter for finance context injection
            intelligent_system_prompt = self._build_intelligent_system_prompt(
                scifi_context=scifi_context or {},
                spider_context=spider_context or {},
                content_type=content_type,
                topic=topic
            )

            logger.info(f"📝 Session 523: Using intelligent prompt ({len(intelligent_system_prompt)} chars)")
            logger.debug(f"   Prompt includes: platform_context={PROMPTING_SYSTEM_AVAILABLE}, "
                        f"scifi={bool(scifi_context)}, spider={bool(spider_context)}")

            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": intelligent_system_prompt},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=4000,
                temperature=0.7,
                timeout=120.0  # Session 767: Explicit request timeout
            )

            content_text = response.choices[0].message.content
            finish_reason = response.choices[0].finish_reason

            # Session 857: Detect truncation
            was_truncated = finish_reason == 'length'
            if was_truncated:
                logger.warning(f"⚠️ Session 857: Content truncated at {len(content_text)} chars (finish_reason=length)")
                # Store truncation state for later use in result
                self._last_generation_truncated = True
            else:
                self._last_generation_truncated = False

            # Try to parse as JSON
            try:
                # Find JSON in the response
                if '```json' in content_text:
                    json_start = content_text.find('```json') + 7
                    json_end = content_text.find('```', json_start)
                    content_text = content_text[json_start:json_end].strip()
                elif '```' in content_text:
                    json_start = content_text.find('```') + 3
                    json_end = content_text.find('```', json_start)
                    content_text = content_text[json_start:json_end].strip()

                content_data = json.loads(content_text)

                # Ensure we have full_text
                if 'full_text' not in content_data:
                    content_data['full_text'] = self._extract_full_text(content_data, content_type)

                # Session 857: Add truncation flag to content data
                content_data['_truncated'] = was_truncated

                return content_data

            except json.JSONDecodeError:
                # If not valid JSON, return as plain text
                logger.warning("Could not parse content as JSON, returning as plain text")
                return {
                    'full_text': content_text,
                    'raw_content': content_text,
                    'parse_error': 'Content was not valid JSON',
                    '_truncated': was_truncated
                }

        except Exception as e:
            logger.error(f"GPT content generation error: {e}", exc_info=True)
            return None

    def _extract_full_text(self, content_data: Dict[str, Any], content_type: str) -> str:
        """Extract full text from structured content."""
        parts = []

        if content_type == 'blog_post':
            if content_data.get('title'):
                parts.append(f"# {content_data['title']}\n")
            if content_data.get('intro'):
                parts.append(content_data['intro'] + "\n")
            if content_data.get('sections'):
                for section in content_data['sections']:
                    if isinstance(section, dict):
                        if section.get('header'):
                            parts.append(f"\n## {section['header']}\n")
                        if section.get('content'):
                            parts.append(section['content'] + "\n")
                    else:
                        parts.append(str(section) + "\n")
            if content_data.get('conclusion'):
                parts.append(f"\n## Conclusion\n{content_data['conclusion']}")

        elif content_type == 'podcast_script':
            if content_data.get('title'):
                parts.append(f"# {content_data['title']}\n")
            if content_data.get('intro_hook'):
                parts.append(f"## INTRO\n{content_data['intro_hook']}\n")
            if content_data.get('segments'):
                for i, segment in enumerate(content_data['segments'], 1):
                    if isinstance(segment, dict):
                        parts.append(f"\n## SEGMENT {i}: {segment.get('title', '')}\n")
                        parts.append(segment.get('content', str(segment)) + "\n")
                    else:
                        parts.append(f"\n## SEGMENT {i}\n{segment}\n")
            if content_data.get('outro'):
                parts.append(f"\n## OUTRO\n{content_data['outro']}")

        elif content_type == 'video_script':
            if content_data.get('title'):
                parts.append(f"# {content_data['title']}\n")
            if content_data.get('hook'):
                parts.append(f"## HOOK\n{content_data['hook']}\n")
            if content_data.get('scenes'):
                for i, scene in enumerate(content_data['scenes'], 1):
                    if isinstance(scene, dict):
                        parts.append(f"\n## SCENE {i}\n")
                        if scene.get('narration'):
                            parts.append(f"NARRATION: {scene['narration']}\n")
                        if scene.get('visual'):
                            parts.append(f"VISUAL: {scene['visual']}\n")
                    else:
                        parts.append(f"\n## SCENE {i}\n{scene}\n")
            if content_data.get('outro'):
                parts.append(f"\n## OUTRO\n{content_data['outro']}")

        else:
            # Generic extraction
            for key, value in content_data.items():
                if isinstance(value, str) and len(value) > 20:
                    parts.append(f"{value}\n")
                elif isinstance(value, list):
                    for item in value:
                        if isinstance(item, str):
                            parts.append(f"{item}\n")
                        elif isinstance(item, dict):
                            parts.append(f"{json.dumps(item)}\n")

        return "\n".join(parts).strip()

    def _extract_topic(self, research: str, task: str) -> str:
        """Extract main topic from research or task."""
        text = research or task
        # Simple extraction - first 50 chars or up to first period
        if '.' in text[:100]:
            return text[:text.find('.')].strip()[:50]
        return text[:50].strip()

    def _calculate_quality_tier(
        self,
        content_data: Dict[str, Any],
        content_type: str,
        target_word_count: int,
        was_truncated: bool
    ) -> tuple:
        """
        Session 857: Calculate quality tier and confidence score for content.

        Returns:
            tuple: (quality_tier: str, confidence: float)

        Quality Tiers:
            - GOLD: 80+ points - Ready to publish as-is
            - SILVER: 50-79 points - Publishable with minor edits
            - BRONZE: <50 points - Needs significant review/editing
        """
        score = 0
        max_score = 100

        # 1. Check for required structure fields (up to 30 points)
        content_config = CONTENT_TYPES.get(content_type, {})
        required_fields = content_config.get('structure', [])
        fields_present = sum(1 for f in required_fields if content_data.get(f))
        if required_fields:
            structure_score = (fields_present / len(required_fields)) * 30
            score += structure_score
            logger.debug(f"   Structure score: {structure_score:.1f}/30 ({fields_present}/{len(required_fields)} fields)")

        # 2. Word count meets target (up to 20 points)
        full_text = content_data.get('full_text', '')
        actual_word_count = len(full_text.split()) if full_text else 0
        if target_word_count > 0:
            word_ratio = min(actual_word_count / target_word_count, 1.5)  # Cap at 150%
            if word_ratio >= 0.8:  # Within 80% of target
                score += 20
            elif word_ratio >= 0.5:
                score += 10
            logger.debug(f"   Word count score: {actual_word_count}/{target_word_count} words (ratio: {word_ratio:.2f})")

        # 3. Has sources/citations (15 points) - Session 523 requirement
        sources = content_data.get('sources', [])
        if sources and len(sources) > 0:
            score += 15
            logger.debug(f"   Sources score: 15/15 ({len(sources)} sources)")
        else:
            logger.debug(f"   Sources score: 0/15 (no sources)")

        # 4. Not truncated (15 points)
        if not was_truncated:
            score += 15
            logger.debug(f"   Truncation score: 15/15 (complete)")
        else:
            logger.debug(f"   Truncation score: 0/15 (TRUNCATED)")

        # 5. Has title/headline (10 points)
        has_title = bool(
            content_data.get('title') or
            content_data.get('headline') or
            content_data.get('subject_line')
        )
        if has_title:
            score += 10
            logger.debug(f"   Title score: 10/10")

        # 6. Has conclusion/CTA (10 points)
        has_ending = bool(
            content_data.get('conclusion') or
            content_data.get('cta') or
            content_data.get('outro') or
            content_data.get('sign_off')
        )
        if has_ending:
            score += 10
            logger.debug(f"   Ending score: 10/10")

        # Calculate confidence as normalized score
        confidence = round(score / max_score, 2)

        # Determine tier
        if score >= 80:
            tier = QualityTier.GOLD.value
        elif score >= 50:
            tier = QualityTier.SILVER.value
        else:
            tier = QualityTier.BRONZE.value

        logger.info(f"📊 Session 857: Quality tier = {tier.upper()} (score: {score}/{max_score}, confidence: {confidence})")

        return tier, confidence

    def _execute_tool_call(
        self,
        tool_name: str,
        arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute tool calls. Session 744: Now supports delegation to specialists.
        """
        # Session 744: Handle delegation to specialists first
        return super()._execute_tool_call(tool_name, arguments)

    @classmethod
    def get_supported_content_types(cls) -> Dict[str, Dict[str, Any]]:
        """Return supported content types with their configurations."""
        return CONTENT_TYPES.copy()

    @classmethod
    def get_tone_presets(cls) -> Dict[str, str]:
        """Return available tone presets."""
        return TONE_PRESETS.copy()


# Factory function
def get_content_writer_agent(user=None, project_id: str = None) -> ContentWriterAgent:
    """Create a ContentWriterAgent instance."""
    return ContentWriterAgent(user=user, project_id=project_id)
