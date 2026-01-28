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
from ml.auto_selection import TaskType

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

logger = logging.getLogger(__name__)


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
        content_type: str = 'blog_post'
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

        # Add platform context if available
        if PROMPTING_SYSTEM_AVAILABLE and PLATFORM_CONTEXT:
            prompt_parts.append(f"\n\n{PLATFORM_CONTEXT}")

        # Add temporal awareness
        prompt_parts.append(f"""

## TEMPORAL AWARENESS (Session 523)
- Current Date: {today}
- Current Year: {year}
- CRITICAL: All content must be current and relevant to {month_year}
- DO NOT reference outdated years like {year-2} or {year-1} unless discussing historical context
- Use phrases like "in {year}" and "this {month_year}" to ensure freshness""")

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

        # Add spider intelligence summary
        if spider_context:
            trends = spider_context.get('trends', [])
            if trends:
                trend_text = ", ".join(trends[:5]) if isinstance(trends[0], str) else ", ".join([t.get('title', str(t)) for t in trends[:5]])
                prompt_parts.append(f"""

## REAL-TIME INTELLIGENCE (Session 523)
Current trending topics from spider network:
{trend_text}

Consider these trends when crafting the content to maximize relevance and engagement.""")

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

        # Session 858: Extract user context for personalization
        user_context = context.get('user', {})
        self._user_context = user_context  # Store for use in prompt building

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
                        flagship_injection = generate_flagship_injection(
                            topic=topic or task[:50],
                            audience=target_audience,
                            cta_type=cta_type
                        )
                        prompt = prompt + "\n\n" + flagship_injection
                        logger.info(f"📝 Session 854: Added flagship template injection ({len(flagship_injection)} chars)")
                    except Exception as e:
                        logger.warning(f"Could not add flagship injection: {e}")

                # Session 523: Generate content via GPT with intelligent prompting
                generated_content = self._generate_content(
                    prompt,
                    content_type,
                    scifi_context=scifi_context,
                    spider_context=spider_context
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
                        }
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

        except Exception as e:
            logger.warning(f"Failed to create content memory: {e}")

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
        keywords: List[str]
    ) -> str:
        """
        Build the GPT prompt for content generation.

        Session 523: Added source citation requirements.
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
- CITE YOUR SOURCES! Attribute specific claims to their sources
- Write in a natural, engaging style appropriate for {target_audience}
- Ensure the content is ready to publish with minimal editing
- Include practical examples and actionable insights where appropriate
- Make it compelling, valuable, and credible to the reader

Generate the {content_config['name']} now:"""

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
- Sign Off: Warm, personal closing"""
        }

        return instructions.get(content_type, f"Follow standard {content_type} format.")

    def _generate_content(
        self,
        prompt: str,
        content_type: str,
        scifi_context: Dict[str, Any] = None,
        spider_context: Dict[str, Any] = None
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
            intelligent_system_prompt = self._build_intelligent_system_prompt(
                scifi_context=scifi_context or {},
                spider_context=spider_context or {},
                content_type=content_type
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
        if tool_name == 'delegate_to_specialist':
            return self._handle_delegate_to_specialist(
                specialist_agent=arguments.get('specialist_agent', ''),
                task=arguments.get('task', ''),
                context=arguments.get('context', ''),
                delegation_context=getattr(self, '_current_delegation_context', {})
            )

        # This agent doesn't have other sub-tools
        return {
            'success': False,
            'error': f'ContentWriterAgent does not support tool: {tool_name}'
        }

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
