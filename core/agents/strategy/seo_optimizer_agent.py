"""
SEO Optimizer Agent - Clean Architecture
=========================================

Session 280: Phase 2 - Agent Architecture Unification
Session 683: Added ML Integration (Text for keyword optimization)

This agent optimizes content for discoverability by generating hashtags,
keywords, descriptions, and metadata.

Tools Available:
    - generate_hashtags: Generate hashtags for content
    - generate_metadata: Generate SEO metadata for an asset
    - suggest_keywords: Suggest keywords for a topic

Usage:
    from core.agents.strategy import SEOOptimizerAgent

    agent = SEOOptimizerAgent(user=request.user)
    result = agent.execute(
        task="Generate hashtags for my tech logo",
        context={},
        scifi_context={},
        spider_context={}
    )
"""

import logging
import time
import re
from typing import Dict, Any, List

from core.agents.base_agent import BaseAgent, AgentResult
from ml.auto_selection import TaskType

logger = logging.getLogger(__name__)


# =============================================================================
# Session 683: ML Integration Helpers for SEO Optimization
# =============================================================================

def analyze_keywords_with_ml(text_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Analyze text data using ML models for keyword optimization.

    Uses DistilBERT for semantic text analysis to:
    - Extract key topics and themes
    - Identify related keywords
    - Analyze text sentiment and tone

    Args:
        text_data: Dict with 'texts' key containing content to analyze

    Returns:
        Dict with ML analysis results
    """
    try:
        from core.services.agent_model_router import get_agent_model_router
        router = get_agent_model_router()

        result = router.auto_route(
            data=text_data,
            task_hint=TaskType.TEXT,
            max_models=2
        )

        return {
            'ml_used': True,
            'task_type': result.auto_selection.get('task_type', 'text'),
            'models_used': result.models_used,
            'confidence': round(result.confidence, 2),
            'ml_insights': result.explanation,
            'topics': result.prediction.get('topics') if hasattr(result, 'prediction') and result.prediction else None,
            'sentiment': result.prediction.get('sentiment') if hasattr(result, 'prediction') and result.prediction else None,
            'keywords': result.prediction.get('keywords') if hasattr(result, 'prediction') and result.prediction else None,
        }
    except Exception as e:
        logger.warning(f"ML keyword analysis failed: {e}")
        return {'ml_used': False, 'reason': f'ML error: {str(e)}'}


class SEOOptimizerAgent(BaseAgent):
    """
    Agent specialized in SEO optimization and discoverability.

    This agent:
    1. Generates hashtags for social media
    2. Creates SEO metadata (title, description, alt text)
    3. Suggests keywords based on content

    It CANNOT:
    - Generate images, videos, or audio
    - Post to social media
    """

    name = "SEOOptimizerAgent"

    system_prompt = """You are SEOOptimizerAgent, a specialist in SEO and content discoverability.

Your job is to optimize content for search engines and social platforms by generating
hashtags, keywords, and metadata.

When given a task:
1. Analyze the content or topic
2. Generate relevant hashtags for the platform
3. Create SEO-friendly titles, descriptions, and alt text
4. Suggest keywords that improve discoverability

Platform hashtag limits:
- Instagram: 30 max, 11 optimal
- Twitter: 5 max
- LinkedIn: 5 max
- TikTok: 10 max
- YouTube: 15 max

Content categories:
- Design: graphicdesign, creative, art, designinspiration
- Logo: logo, logodesign, branding, brandidentity
- Tech: technology, ai, innovation, digital
- Business: entrepreneur, startup, success
- Social: socialmedia, marketing, contentcreator
- Video: videography, youtube, filmmaker

You CANNOT create content - just optimize for discoverability."""

    tools = [
        {
            "type": "function",
            "function": {
                "name": "generate_hashtags",
                "description": "Generate hashtags for content",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "topic": {
                            "type": "string",
                            "description": "The topic or content description"
                        },
                        "platform": {
                            "type": "string",
                            "description": "Target platform",
                            "enum": ["instagram", "twitter", "linkedin", "tiktok", "youtube", "general"],
                            "default": "general"
                        },
                        "count": {
                            "type": "integer",
                            "description": "Number of hashtags to generate",
                            "default": 10
                        }
                    },
                    "required": ["topic"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "generate_metadata",
                "description": "Generate SEO metadata for content",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "content_description": {
                            "type": "string",
                            "description": "Description of the content"
                        },
                        "content_type": {
                            "type": "string",
                            "description": "Type of content",
                            "enum": ["image", "video", "audio", "article"]
                        }
                    },
                    "required": ["content_description"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "suggest_keywords",
                "description": "Suggest keywords for a topic",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "topic": {
                            "type": "string",
                            "description": "The topic to generate keywords for"
                        },
                        "intent": {
                            "type": "string",
                            "description": "Search intent",
                            "enum": ["informational", "transactional", "navigational", "commercial"]
                        }
                    },
                    "required": ["topic"]
                }
            }
        }
    ]

    # Platform hashtag limits
    PLATFORM_LIMITS = {
        'instagram': 30,
        'twitter': 5,
        'linkedin': 5,
        'tiktok': 10,
        'youtube': 15,
        'general': 10
    }

    # Trending hashtags by category
    TRENDING_HASHTAGS = {
        'design': ['design', 'graphicdesign', 'creative', 'art', 'designinspiration', 'artwork'],
        'logo': ['logo', 'logodesign', 'branding', 'brandidentity', 'logomaker', 'logos'],
        'tech': ['technology', 'tech', 'ai', 'artificialintelligence', 'innovation', 'digital'],
        'business': ['business', 'entrepreneur', 'startup', 'success', 'motivation', 'smallbusiness'],
        'social': ['socialmedia', 'marketing', 'digitalmarketing', 'contentcreator', 'viral'],
        'video': ['video', 'videography', 'filmmaker', 'youtube', 'contentcreation', 'creator'],
        'photography': ['photography', 'photo', 'photooftheday', 'photographer', 'photoshoot'],
        'illustration': ['illustration', 'illustrator', 'digitalart', 'drawing', 'artwork', 'artist']
    }

    def _optimize_with_ml(self, topic: str, content_description: str = None) -> Dict[str, Any]:
        """
        Session 683: Optimize SEO using ML text analysis.

        Uses DistilBERT to analyze text and extract:
        - Semantic topics
        - Related keywords
        - Optimal hashtag categories

        Args:
            topic: Topic or content description
            content_description: Optional detailed description

        Returns:
            Dict with ML analysis results
        """
        text_content = topic
        if content_description:
            text_content = f"{topic} {content_description}"

        if not text_content or len(text_content.strip()) < 10:
            return {'ml_used': False, 'reason': 'Insufficient text for analysis'}

        try:
            text_data = {
                'texts': [text_content],
                'analysis_type': 'seo_optimization'
            }

            ml_result = analyze_keywords_with_ml(text_data)

            if ml_result.get('ml_used'):
                logger.info(
                    f"ML SEO optimization: "
                    f"models={ml_result.get('models_used')}, "
                    f"confidence={ml_result.get('confidence')}"
                )

                # Enhance with ML-suggested keywords
                ml_keywords = ml_result.get('keywords', [])
                if ml_keywords:
                    ml_result['suggested_hashtags'] = [
                        f"#{kw.replace(' ', '').lower()}" for kw in ml_keywords[:5]
                    ]

            return ml_result

        except Exception as e:
            logger.warning(f"ML SEO optimization failed: {e}")
            return {'ml_used': False, 'reason': f'ML error: {str(e)}'}

    def _build_text_for_ml(self, topic: str, platform: str = None) -> Dict[str, Any]:
        """
        Session 683: Build text data for ML keyword analysis.

        Args:
            topic: Topic to analyze
            platform: Optional target platform

        Returns:
            Dict with text data for ML
        """
        context = f"SEO optimization for {platform}" if platform else "General SEO"

        return {
            'texts': [f"{topic} - {context}"],
            'platform': platform,
            'analysis_type': 'keyword_extraction'
        }

    def execute(
        self,
        task: str,
        context: Dict[str, Any],
        scifi_context: Dict[str, Any],
        spider_context: Dict[str, Any]
    ) -> AgentResult:
        """Execute SEO optimization based on the task."""
        start_time = time.time()
        tool_calls_made = []

        # Session 736: Extract spider intelligence for real-time data
        spider_intel = self._extract_spider_intelligence(spider_context)
        if spider_intel['has_data']:
            logger.info(f"🕷️ {self.name} using spider intelligence")

        with self.time_travel_session("seo_optimization", task, input_data=context):
            try:
                if not self._validate_task(task):
                    return AgentResult(
                        success=False,
                        error="Invalid or empty task",
                        agent_name=self.name
                    )

                self.record_decision(
                    decision_type="task_analysis",
                    action="Analyzing SEO request",
                    reasoning=f"Received task: {task[:100]}",
                    alternatives=["ask_for_clarification"],
                    confidence=0.9
                )

                full_prompt = self._build_intelligent_prompt(task, scifi_context, spider_context)
                logger.info(f"SEOOptimizerAgent executing: {task[:50]}...")

                gpt_response = self._call_openai(full_prompt)

                if gpt_response.get('tool_calls'):
                    for tool_call in gpt_response['tool_calls']:
                        tool_name = tool_call['name']
                        arguments = tool_call['arguments']

                        self.record_decision(
                            decision_type="tool_selection",
                            action=f"Calling {tool_name}",
                            reasoning=f"SEO operation: {arguments}",
                            alternatives=[],
                            confidence=0.95
                        )

                        tool_result = self._execute_tool_call(tool_name, arguments)
                        tool_calls_made.append({
                            'tool': tool_name,
                            'arguments': arguments,
                            'result': tool_result
                        })

                        self.mark_decision_outcome(
                            success=tool_result.get('success', False),
                            result_summary=str(tool_result)[:100]
                        )

                    execution_time = int((time.time() - start_time) * 1000)

                    # Session 683: Run ML analysis on SEO content
                    ml_analysis = {'ml_used': False}
                    try:
                        # Extract topic from tool calls or task
                        topic_text = task
                        for tc in tool_calls_made:
                            args = tc.get('arguments', {})
                            if args.get('topic'):
                                topic_text = args.get('topic')
                                break
                            elif args.get('content_description'):
                                topic_text = args.get('content_description')
                                break

                        if topic_text:
                            ml_analysis = self._optimize_with_ml(topic_text)
                            if ml_analysis.get('ml_used'):
                                logger.info(
                                    f"ML SEO analysis complete: "
                                    f"models={ml_analysis.get('models_used')}, "
                                    f"confidence={ml_analysis.get('confidence')}"
                                )
                    except Exception as e:
                        logger.warning(f"ML integration in execute failed: {e}")

                    # Session 1200: Synthesize tool results into real analysis
                    tool_results_list = [tc.get('result', {}) for tc in tool_calls_made]
                    synthesis = self._synthesize_tool_results(tool_calls_made, tool_results_list, task)
                    analysis_msg = synthesis if synthesis else "SEO optimization completed"

                    result = AgentResult(
                        success=True,
                        message=analysis_msg,
                        data={
                            'task': task,
                            'tool_results': tool_calls_made,
                            'content': synthesis,
                            'ml_analysis': ml_analysis,  # Session 683: ML insights
                        },
                        agent_name=self.name,
                        execution_time_ms=execution_time,
                        decisions_made=self._tt_decision_count,
                        tool_calls=tool_calls_made
                    )

                    # Session 380: Learning hooks for collective intelligence
                    self._record_learning_outcome(
                        result=result,
                        task=task,
                        context=context,
                        spider_data_used=bool(spider_context),
                        scifi_context_used=bool(scifi_context)
                    )
                    self._create_execution_memory(
                        result=result,
                        task=task,
                        memory_type="success",
                        importance=0.7
                    )

                    # Session 1006: Persist output to Deliverable
                    self._save_to_deliverable(
                        title=f"SEO Optimization: {task[:80]}",
                        content=result.message,
                        deliverable_type='analysis',
                        category='SEO Strategy',
                        tags=['seo', 'strategy'],
                        metadata={'task': task[:200]},
                    )

                    return result

                else:
                    result = AgentResult(
                        success=True,
                        message=gpt_response.get('content', ''),
                        data={'type': 'conversation'},
                        agent_name=self.name,
                        execution_time_ms=int((time.time() - start_time) * 1000)
                    )

                    # Session 380: Learning hooks for collective intelligence
                    self._record_learning_outcome(
                        result=result,
                        task=task,
                        context=context,
                        spider_data_used=bool(spider_context),
                        scifi_context_used=bool(scifi_context)
                    )
                    self._create_execution_memory(
                        result=result,
                        task=task,
                        memory_type="success",
                        importance=0.6
                    )

                    return result

            except Exception as e:
                logger.error(f"SEOOptimizerAgent error: {e}")
                result = AgentResult(
                    success=False,
                    error=str(e),
                    agent_name=self.name,
                    execution_time_ms=int((time.time() - start_time) * 1000)
                )

                # Session 380: Learning hooks for collective intelligence (failures too)
                self._record_learning_outcome(
                    result=result,
                    task=task,
                    context=context,
                    spider_data_used=bool(spider_context),
                    scifi_context_used=bool(scifi_context)
                )
                self._create_execution_memory(
                    result=result,
                    task=task,
                    memory_type="failure",
                    importance=0.8
                )

                return result

    def _execute_tool_call(
        self,
        tool_name: str,
        arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute an SEO tool call."""
        if tool_name == "generate_hashtags":
            return self._generate_hashtags(
                topic=arguments.get('topic', ''),
                platform=arguments.get('platform', 'general'),
                count=arguments.get('count', 10)
            )

        elif tool_name == "generate_metadata":
            return self._generate_metadata(
                content_description=arguments.get('content_description', ''),
                content_type=arguments.get('content_type', 'image')
            )

        elif tool_name == "suggest_keywords":
            return self._suggest_keywords(
                topic=arguments.get('topic', ''),
                intent=arguments.get('intent', 'informational')
            )

        return super()._execute_tool_call(tool_name, arguments)

    def _generate_hashtags(
        self,
        topic: str,
        platform: str,
        count: int
    ) -> Dict[str, Any]:
        """Generate hashtags for content."""
        logger.info(f"Generating hashtags for: {topic} on {platform}")

        # Detect categories from topic
        topic_lower = topic.lower()
        detected_categories = []

        for category, keywords in [
            ('design', ['design', 'graphic', 'creative', 'art']),
            ('logo', ['logo', 'brand', 'identity']),
            ('tech', ['tech', 'ai', 'software', 'digital', 'app']),
            ('business', ['business', 'startup', 'entrepreneur']),
            ('video', ['video', 'youtube', 'film']),
            ('photography', ['photo', 'photography', 'camera']),
            ('illustration', ['illustration', 'drawing', 'sketch'])
        ]:
            if any(kw in topic_lower for kw in keywords):
                detected_categories.append(category)

        if not detected_categories:
            detected_categories = ['design']

        # Gather hashtags
        hashtags = []
        for category in detected_categories:
            hashtags.extend(self.TRENDING_HASHTAGS.get(category, []))

        # Limit by platform
        limit = min(count, self.PLATFORM_LIMITS.get(platform, 10))
        hashtags = list(dict.fromkeys(hashtags))[:limit]  # Remove duplicates

        # Format with #
        formatted = [f"#{tag}" for tag in hashtags]

        return {
            'success': True,
            'hashtags': formatted,
            'count': len(formatted),
            'platform': platform,
            'categories_detected': detected_categories
        }

    def _generate_metadata(
        self,
        content_description: str,
        content_type: str
    ) -> Dict[str, Any]:
        """Generate SEO metadata."""
        logger.info(f"Generating metadata for: {content_description[:50]}")

        # Extract key terms
        words = re.findall(r'\b\w+\b', content_description.lower())
        keywords = [w for w in words if len(w) > 3][:10]

        # Generate title (first 60 chars)
        title = content_description[:57] + "..." if len(content_description) > 60 else content_description

        # Generate description (first 160 chars)
        description = content_description[:157] + "..." if len(content_description) > 160 else content_description

        # Generate alt text for images
        alt_text = f"{content_type}: {content_description[:100]}" if content_type == 'image' else None

        return {
            'success': True,
            'metadata': {
                'title': title,
                'description': description,
                'alt_text': alt_text,
                'keywords': keywords,
                'content_type': content_type
            }
        }

    def _suggest_keywords(
        self,
        topic: str,
        intent: str
    ) -> Dict[str, Any]:
        """Suggest keywords for a topic."""
        logger.info(f"Suggesting keywords for: {topic}")

        # Extract words and create variations
        base_words = re.findall(r'\b\w+\b', topic.lower())
        keywords = []

        # Add base words
        keywords.extend([w for w in base_words if len(w) > 3])

        # Add common modifiers based on intent
        modifiers = {
            'informational': ['how to', 'what is', 'guide', 'tutorial', 'tips'],
            'transactional': ['buy', 'best', 'cheap', 'discount', 'deal'],
            'navigational': ['official', 'website', 'login', 'app'],
            'commercial': ['review', 'comparison', 'vs', 'alternative', 'top']
        }

        for modifier in modifiers.get(intent, [])[:3]:
            for word in base_words[:2]:
                keywords.append(f"{modifier} {word}")

        return {
            'success': True,
            'keywords': keywords[:15],
            'topic': topic,
            'intent': intent
        }

    def _validate_task(self, task: str) -> bool:
        """Validate the task is appropriate for SEO optimization."""
        return bool(task and task.strip())
