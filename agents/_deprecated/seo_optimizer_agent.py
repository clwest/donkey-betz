"""
SEO Content Optimizer Agent
===========================

Session 241: Created as part of agent cleanup - building real, valuable agents.
Session 308: Added learning infrastructure hooks for cross-agent knowledge sharing.

This agent optimizes generated content for discoverability by:
- Adding SEO-friendly descriptions and alt text
- Suggesting hashtags based on trending topics
- Generating metadata for images and videos
- Recommending keywords for content

Example:
    agent = SEOOptimizerAgent(user=request.user)

    # Optimize an image for SEO
    result = agent.optimize_image(image_id='123')
    # Returns: title, description, alt_text, hashtags, keywords

    # Get hashtag suggestions for a topic
    result = agent.get_hashtags(topic='AI logo design')
"""

from __future__ import annotations

import logging
import re
import json
from typing import Dict, Any, List, Optional
from datetime import datetime
from django.utils import timezone
from django.contrib.auth import get_user_model

logger = logging.getLogger(__name__)
User = get_user_model()


class SEOOptimizerLearningMixin:
    """
    Learning infrastructure mixin for SEOOptimizerAgent.
    Session 308: Enables cross-agent knowledge sharing for SEO patterns.
    """

    _learning_loop = None
    _memory_service = None
    _agent_model = None

    @property
    def learning_loop(self):
        """Lazy-load LearningLoopService."""
        if self._learning_loop is None:
            try:
                from core.super_platform.learning_loop import get_learning_loop_service
                self._learning_loop = get_learning_loop_service(None)
            except ImportError:
                logger.debug("LearningLoopService not available")
                return None
        return self._learning_loop

    @property
    def memory_service(self):
        """Lazy-load MemoryEmbeddingService."""
        if self._memory_service is None:
            try:
                from core.services.memory_embedding_service import get_memory_embedding_service
                self._memory_service = get_memory_embedding_service()
            except ImportError:
                logger.debug("MemoryEmbeddingService not available")
                return None
        return self._memory_service

    @property
    def agent_model(self):
        """Lazy-load or create Agent model instance."""
        if self._agent_model is None:
            try:
                from core.models_unified_system import Agent
                self._agent_model, _ = Agent.objects.get_or_create(
                    name='SEOOptimizerAgent',
                    defaults={
                        'agent_type': 'deprecated',
                        'specialization': 'seo_optimization',
                        'description': 'Optimizes content for search engines and social platforms.',
                        'is_active': True,
                    }
                )
            except ImportError:
                logger.debug("Agent model not available")
                return None
        return self._agent_model

    def _record_learning_outcome(
        self,
        result: Dict[str, Any],
        task: str,
        context: Dict[str, Any] = None,
        spider_data_used: bool = False
    ):
        """Record execution outcome for XP and pattern learning."""
        if not self.learning_loop:
            return None

        try:
            outcome_id = self.learning_loop.record_outcome(
                query_type='seo_optimization',
                query_text=task,
                execution_mode='agent',
                agents_used=['SEOOptimizerAgent'],
                response=str(result),
                execution_time_ms=result.get('execution_time_ms', 0),
                success=result.get('success', False),
                spider_data_used=spider_data_used,
                scifi_context_used=False,
                context=context or {}
            )
            return outcome_id
        except Exception as e:
            logger.debug(f"Failed to record learning outcome: {e}")
            return None

    def _create_execution_memory(
        self,
        result: Dict[str, Any],
        task: str,
        memory_type: str = "interaction",
        importance: float = 0.5
    ):
        """Create a memory from the SEO optimization execution."""
        if not self.memory_service or not self.agent_model:
            return None

        try:
            memory = self.memory_service.create_memory(
                agent=self.agent_model,
                title=f"SEO: {task[:50]}...",
                content=str(result),
                memory_type=memory_type,
                valence="positive" if result.get('success') else "negative",
                importance_score=importance,
                source_type='agent_execution',
                tags=['seo', 'optimization', 'success' if result.get('success') else 'failure']
            )
            return memory
        except Exception as e:
            logger.debug(f"Failed to create execution memory: {e}")
            return None

    def _share_knowledge(
        self,
        knowledge_type: str,
        title: str,
        knowledge_value: Dict[str, Any],
        confidence: float = 0.8
    ):
        """Share learned SEO knowledge for cross-agent learning."""
        if not self.agent_model:
            return None

        try:
            from core.models_unified_system import AgentKnowledgeSource

            type_mapping = {
                'hashtags': 'content_idea',
                'keywords': 'content_idea',
                'platform': 'market',
                'seo': 'tool_discovery',
            }
            mapped_type = type_mapping.get(knowledge_type, 'content_idea')

            knowledge, created = AgentKnowledgeSource.objects.update_or_create(
                agent=self.agent_model,
                title=title,
                knowledge_type=mapped_type,
                defaults={
                    'summary': json.dumps(knowledge_value),
                    'confidence_score': confidence,
                    'is_active': True,
                }
            )
            return knowledge
        except Exception as e:
            logger.debug(f"Failed to share knowledge: {e}")
            return None

    def _get_shared_knowledge(
        self,
        knowledge_type: str = None,
        title_contains: str = None,
        from_agents: List[str] = None
    ) -> List[Dict[str, Any]]:
        """Retrieve knowledge from other agents and record the learning transfer."""
        try:
            from core.models_unified_system import AgentKnowledgeSource, AgentLearningConnection, KnowledgeTransfer

            queryset = AgentKnowledgeSource.objects.filter(is_active=True)

            if knowledge_type:
                queryset = queryset.filter(knowledge_type=knowledge_type)

            if title_contains:
                queryset = queryset.filter(title__icontains=title_contains)

            if from_agents:
                queryset = queryset.filter(agent__name__in=from_agents)

            if self.agent_model:
                queryset = queryset.exclude(agent=self.agent_model)

            results = []
            for ks in queryset.order_by('-confidence_score')[:10]:
                results.append({
                    'source_agent': ks.agent.name,
                    'title': ks.title,
                    'type': ks.knowledge_type,
                    'value': json.loads(ks.summary) if ks.summary else {},
                    'confidence': ks.confidence_score,
                })

                # Record the learning connection and transfer (Session 311)
                if self.agent_model and ks.agent:
                    try:
                        connection, created = AgentLearningConnection.objects.get_or_create(
                            teacher_agent=ks.agent,
                            student_agent=self.agent_model,
                            defaults={
                                'learning_type': 'knowledge_sharing',
                                'shareable_knowledge_types': [ks.knowledge_type],
                                'is_active': True,
                            }
                        )
                        connection.total_transfers += 1
                        connection.last_transfer_at = timezone.now()
                        connection.save()

                        KnowledgeTransfer.objects.create(
                            connection=connection,
                            source_knowledge=ks,
                            transfer_summary=f"Retrieved '{ks.title}' for SEO optimization",
                            key_points={'knowledge_type': ks.knowledge_type},
                            was_useful=True,
                            usefulness_score=ks.confidence_score,
                        )
                    except Exception as transfer_error:
                        logger.debug(f"Failed to record transfer: {transfer_error}")

            return results
        except Exception as e:
            logger.debug(f"Failed to get shared knowledge: {e}")
            return []


class SEOOptimizerAgent(SEOOptimizerLearningMixin):
    """
    Optimizes content for search engines and social platforms.

    Generates metadata, hashtags, and descriptions to improve discoverability.

    Session 308: Added SEOOptimizerLearningMixin for cross-agent knowledge sharing.
    """

    # Platform-specific hashtag limits
    PLATFORM_HASHTAG_LIMITS = {
        'instagram': 30,
        'twitter': 5,
        'linkedin': 5,
        'tiktok': 10,
        'youtube': 15,
        'general': 10
    }

    # Common trending hashtags by category
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

    # Keywords that indicate content type
    CONTENT_KEYWORDS = {
        'logo': ['logo', 'brand', 'identity', 'mark', 'emblem', 'symbol', 'icon'],
        'thumbnail': ['thumbnail', 'youtube', 'video', 'cover', 'preview'],
        'social': ['post', 'social', 'instagram', 'facebook', 'twitter', 'tiktok'],
        'product': ['product', 'ecommerce', 'shop', 'store', 'merchandise'],
        'illustration': ['illustration', 'art', 'drawing', 'artwork', 'artistic']
    }

    def __init__(self, user: Optional[User] = None, project_id: Optional[str] = None):
        """
        Initialize SEO Optimizer Agent.

        Args:
            user: User context
            project_id: Optional project context
        """
        self.user = user
        self.project_id = project_id
        self.agent_name = 'SEOOptimizerAgent'
        self._spider_service = None

        logger.info(f"🔍 SEOOptimizerAgent initialized for user: {user.username if user else 'system'}")

    @property
    def spider_service(self):
        """Lazy load spider intelligence service."""
        if self._spider_service is None:
            try:
                from core.services.spider_intelligence import SpiderIntelligenceService
                self._spider_service = SpiderIntelligenceService()
            except ImportError:
                logger.warning("SpiderIntelligenceService not available")
        return self._spider_service

    def optimize_image(self, image_id: str) -> Dict[str, Any]:
        """
        Generate SEO metadata for an image.

        Args:
            image_id: Image ID to optimize

        Returns:
            Dict with title, description, alt_text, hashtags, keywords
        """
        logger.info(f"🔍 Optimizing image {image_id} for SEO")

        try:
            from content.models import ImageHistory

            # Get image
            image = ImageHistory.objects.get(id=image_id)
            prompt = image.prompt or ''

            # Analyze the prompt
            content_type = self._detect_content_type(prompt)
            keywords = self._extract_keywords(prompt)
            categories = self._categorize_content(prompt)

            # Generate SEO elements
            title = self._generate_title(prompt, content_type)
            description = self._generate_description(prompt, content_type, keywords)
            alt_text = self._generate_alt_text(prompt)
            hashtags = self.get_hashtags(prompt, platform='general')

            result = {
                'success': True,
                'image_id': str(image_id),
                'seo': {
                    'title': title,
                    'description': description,
                    'alt_text': alt_text,
                    'keywords': keywords,
                    'hashtags': hashtags.get('hashtags', []),
                    'categories': categories,
                    'content_type': content_type
                },
                'message': f"Generated SEO metadata for image"
            }

            # Optionally update the image record
            if hasattr(image, 'metadata') and image.metadata is not None:
                image.metadata['seo'] = result['seo']
                image.save()
                result['saved'] = True

            # Session 308: Learning Infrastructure Hooks
            self._record_learning_outcome(
                result=result,
                task=f"Optimize image: {image_id}",
                context={'content_type': content_type, 'keywords_count': len(keywords)}
            )

            # Create memory for successful SEO optimization
            self._create_execution_memory(
                result=result,
                task=f"Image SEO: {content_type}",
                memory_type="success",
                importance=0.65
            )

            # Share successful SEO patterns
            if keywords:
                self._share_knowledge(
                    knowledge_type='seo',
                    title=f"SEO pattern: {content_type}",
                    knowledge_value={
                        'content_type': content_type,
                        'keywords': keywords[:5],
                        'categories': categories,
                        'hashtag_count': len(hashtags.get('hashtags', [])),
                    },
                    confidence=0.75
                )

            return result

        except Exception as e:
            logger.error(f"❌ SEOOptimizerAgent.optimize_image failed: {e}", exc_info=True)
            # Session 308: Record failure
            self._record_learning_outcome(
                result={'success': False, 'error': str(e)},
                task=f"Optimize image: {image_id} (failed)",
                context={'error': str(e)}
            )
            return {
                'success': False,
                'error': str(e)
            }

    def get_hashtags(
        self,
        topic: str,
        platform: str = 'general',
        include_trending: bool = True
    ) -> Dict[str, Any]:
        """
        Generate hashtag suggestions for a topic.

        Args:
            topic: Topic or prompt to generate hashtags for
            platform: Target platform (instagram, twitter, linkedin, tiktok, youtube)
            include_trending: Whether to include trending hashtags

        Returns:
            Dict with hashtag list and metadata
        """
        logger.info(f"🔍 Generating hashtags for: {topic[:50]}... (platform={platform})")

        try:
            hashtags = set()

            # Get base hashtags from topic keywords
            topic_words = self._extract_keywords(topic)
            for word in topic_words[:5]:
                # Clean word for hashtag use
                clean = re.sub(r'[^a-zA-Z0-9]', '', word.lower())
                if len(clean) >= 3:
                    hashtags.add(clean)

            # Add category-specific hashtags
            categories = self._categorize_content(topic)
            for category in categories:
                if category in self.TRENDING_HASHTAGS:
                    hashtags.update(self.TRENDING_HASHTAGS[category][:3])

            # Add trending hashtags if enabled
            if include_trending:
                trending = self._get_trending_hashtags()
                hashtags.update(trending[:3])

            # Respect platform limits
            limit = self.PLATFORM_HASHTAG_LIMITS.get(platform, 10)
            hashtag_list = list(hashtags)[:limit]

            # Format with # prefix
            formatted = [f"#{tag}" for tag in hashtag_list]

            result = {
                'success': True,
                'hashtags': formatted,
                'hashtags_raw': hashtag_list,
                'count': len(formatted),
                'platform': platform,
                'limit': limit,
                'copy_text': ' '.join(formatted)
            }

            # Session 308: Learning Infrastructure Hooks
            self._record_learning_outcome(
                result=result,
                task=f"Get hashtags: {topic[:30]}",
                context={'platform': platform, 'hashtag_count': len(formatted)},
                spider_data_used=include_trending
            )

            # Share effective hashtag patterns
            if len(formatted) >= 5:
                self._share_knowledge(
                    knowledge_type='hashtags',
                    title=f"Hashtags for: {topic[:30]}",
                    knowledge_value={
                        'topic': topic[:50],
                        'platform': platform,
                        'hashtags': hashtag_list[:10],
                        'categories': categories,
                    },
                    confidence=0.7
                )

            return result

        except Exception as e:
            logger.error(f"❌ SEOOptimizerAgent.get_hashtags failed: {e}", exc_info=True)
            return {
                'success': False,
                'error': str(e)
            }

    def generate_description(
        self,
        content: str,
        content_type: Optional[str] = None,
        max_length: int = 300
    ) -> Dict[str, Any]:
        """
        Generate SEO-optimized description for content.

        Args:
            content: Content prompt or description
            content_type: Type of content (logo, thumbnail, etc.)
            max_length: Maximum description length

        Returns:
            Dict with description and metadata
        """
        logger.info(f"🔍 Generating description for: {content[:50]}...")

        try:
            if not content_type:
                content_type = self._detect_content_type(content)

            keywords = self._extract_keywords(content)
            description = self._generate_description(content, content_type, keywords)

            # Truncate if needed
            if len(description) > max_length:
                description = description[:max_length-3] + '...'

            return {
                'success': True,
                'description': description,
                'content_type': content_type,
                'keywords_used': keywords[:5],
                'character_count': len(description),
                'max_length': max_length
            }

        except Exception as e:
            logger.error(f"❌ SEOOptimizerAgent.generate_description failed: {e}", exc_info=True)
            return {
                'success': False,
                'error': str(e)
            }

    def suggest_keywords(self, topic: str, limit: int = 10) -> Dict[str, Any]:
        """
        Suggest SEO keywords for a topic.

        Args:
            topic: Topic to get keywords for
            limit: Maximum number of keywords

        Returns:
            Dict with keyword suggestions
        """
        logger.info(f"🔍 Suggesting keywords for: {topic}")

        try:
            # Extract from topic
            keywords = self._extract_keywords(topic)

            # Add related keywords from spider data
            if self.spider_service:
                try:
                    related = self.spider_service.get_related_keywords(topic)
                    keywords.extend(related.get('keywords', []))
                except Exception:
                    pass

            # Add category keywords
            categories = self._categorize_content(topic)
            for category in categories:
                if category in self.TRENDING_HASHTAGS:
                    keywords.extend(self.TRENDING_HASHTAGS[category])

            # Deduplicate and limit
            unique_keywords = list(dict.fromkeys(keywords))[:limit]

            return {
                'success': True,
                'keywords': unique_keywords,
                'count': len(unique_keywords),
                'topic': topic,
                'categories': categories
            }

        except Exception as e:
            logger.error(f"❌ SEOOptimizerAgent.suggest_keywords failed: {e}", exc_info=True)
            return {
                'success': False,
                'error': str(e)
            }

    def optimize_for_platform(
        self,
        content: str,
        platform: str
    ) -> Dict[str, Any]:
        """
        Optimize content metadata for a specific platform.

        Args:
            content: Content description
            platform: Target platform

        Returns:
            Platform-specific optimization recommendations
        """
        logger.info(f"🔍 Optimizing for platform: {platform}")

        try:
            platform_tips = {
                'instagram': {
                    'max_hashtags': 30,
                    'ideal_hashtags': '11-15',
                    'caption_limit': 2200,
                    'tips': [
                        'Use a mix of popular and niche hashtags',
                        'Add line breaks for readability',
                        'Include a call-to-action',
                        'First 125 characters are most important'
                    ]
                },
                'twitter': {
                    'max_hashtags': 2,
                    'ideal_hashtags': '1-2',
                    'caption_limit': 280,
                    'tips': [
                        'Keep it concise',
                        'Use 1-2 relevant hashtags max',
                        'Add alt text for images',
                        'Best times: 9am-12pm weekdays'
                    ]
                },
                'linkedin': {
                    'max_hashtags': 5,
                    'ideal_hashtags': '3-5',
                    'caption_limit': 3000,
                    'tips': [
                        'Professional tone',
                        'Hook in first 2 lines',
                        'Use 3-5 relevant hashtags',
                        'Best times: Tuesday-Thursday mornings'
                    ]
                },
                'youtube': {
                    'max_hashtags': 15,
                    'ideal_hashtags': '3-5',
                    'title_limit': 100,
                    'tips': [
                        'Keywords in first 60 characters of title',
                        'Detailed description with keywords',
                        'Use 3-5 hashtags in description',
                        'Add timestamps for longer videos'
                    ]
                },
                'tiktok': {
                    'max_hashtags': 10,
                    'ideal_hashtags': '3-5',
                    'caption_limit': 2200,
                    'tips': [
                        'Trending hashtags are key',
                        'Use 3-5 targeted hashtags',
                        'Short, catchy captions work best',
                        'Participate in trends'
                    ]
                }
            }

            platform_info = platform_tips.get(platform, platform_tips['instagram'])

            # Generate optimized content
            hashtags = self.get_hashtags(content, platform=platform)
            description = self.generate_description(
                content,
                max_length=platform_info.get('caption_limit', 300)
            )

            result = {
                'success': True,
                'platform': platform,
                'optimized': {
                    'hashtags': hashtags.get('hashtags', [])[:platform_info['max_hashtags']],
                    'description': description.get('description', ''),
                    'keywords': self.suggest_keywords(content).get('keywords', [])[:5]
                },
                'platform_guidelines': platform_info,
                'tips': platform_info.get('tips', [])
            }

            # Session 308: Learning Infrastructure Hooks
            self._record_learning_outcome(
                result=result,
                task=f"Optimize for platform: {platform}",
                context={'platform': platform, 'content_preview': content[:50]}
            )

            # Share platform-specific optimization patterns
            self._share_knowledge(
                knowledge_type='platform',
                title=f"Platform optimization: {platform}",
                knowledge_value={
                    'platform': platform,
                    'max_hashtags': platform_info['max_hashtags'],
                    'ideal_hashtags': platform_info.get('ideal_hashtags'),
                    'tips': platform_info.get('tips', [])[:2],
                },
                confidence=0.8
            )

            return result

        except Exception as e:
            logger.error(f"❌ SEOOptimizerAgent.optimize_for_platform failed: {e}", exc_info=True)
            return {
                'success': False,
                'error': str(e)
            }

    # Private helper methods

    def _detect_content_type(self, prompt: str) -> str:
        """Detect content type from prompt."""
        prompt_lower = prompt.lower()

        for content_type, keywords in self.CONTENT_KEYWORDS.items():
            if any(kw in prompt_lower for kw in keywords):
                return content_type

        return 'image'

    def _extract_keywords(self, text: str) -> List[str]:
        """Extract keywords from text."""
        # Remove common words
        stop_words = {'a', 'an', 'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
                      'of', 'with', 'by', 'from', 'is', 'are', 'was', 'were', 'be', 'been',
                      'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would',
                      'could', 'should', 'may', 'might', 'must', 'create', 'make', 'design',
                      'generate', 'style', 'like', 'image', 'picture', 'photo'}

        # Clean and split
        words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
        keywords = [w for w in words if w not in stop_words]

        # Deduplicate while preserving order
        seen = set()
        unique = []
        for kw in keywords:
            if kw not in seen:
                seen.add(kw)
                unique.append(kw)

        return unique

    def _categorize_content(self, text: str) -> List[str]:
        """Categorize content based on text analysis."""
        text_lower = text.lower()
        categories = []

        category_keywords = {
            'design': ['design', 'graphic', 'visual', 'creative', 'artwork'],
            'logo': ['logo', 'brand', 'identity', 'icon', 'mark', 'emblem'],
            'tech': ['tech', 'ai', 'software', 'digital', 'code', 'app', 'startup'],
            'business': ['business', 'company', 'corporate', 'professional', 'enterprise'],
            'social': ['social', 'instagram', 'tiktok', 'youtube', 'content', 'post'],
            'video': ['video', 'thumbnail', 'youtube', 'film', 'movie'],
            'photography': ['photo', 'photography', 'portrait', 'landscape', 'shot'],
            'illustration': ['illustration', 'drawing', 'art', 'artistic', 'cartoon']
        }

        for category, keywords in category_keywords.items():
            if any(kw in text_lower for kw in keywords):
                categories.append(category)

        return categories if categories else ['design']

    def _generate_title(self, prompt: str, content_type: str) -> str:
        """Generate SEO-friendly title."""
        keywords = self._extract_keywords(prompt)[:3]

        type_labels = {
            'logo': 'Logo Design',
            'thumbnail': 'YouTube Thumbnail',
            'social': 'Social Media Graphic',
            'product': 'Product Image',
            'illustration': 'Digital Illustration',
            'image': 'Digital Artwork'
        }

        type_label = type_labels.get(content_type, 'Digital Artwork')

        if keywords:
            title = f"{keywords[0].title()} {type_label}"
            if len(keywords) > 1:
                title += f" - {keywords[1].title()}"
        else:
            title = f"Custom {type_label}"

        return title

    def _generate_description(self, prompt: str, content_type: str, keywords: List[str]) -> str:
        """Generate SEO-friendly description."""
        type_intros = {
            'logo': 'Professional logo design featuring',
            'thumbnail': 'Eye-catching YouTube thumbnail showcasing',
            'social': 'Engaging social media graphic with',
            'product': 'High-quality product photography of',
            'illustration': 'Custom digital illustration depicting',
            'image': 'AI-generated artwork featuring'
        }

        intro = type_intros.get(content_type, 'Digital content featuring')
        keyword_text = ', '.join(keywords[:4]) if keywords else 'unique design elements'

        description = f"{intro} {keyword_text}. "
        description += f"Created with AI-powered creative tools. "
        description += f"Perfect for {content_type} projects and digital content."

        return description

    def _generate_alt_text(self, prompt: str) -> str:
        """Generate accessibility alt text."""
        # Clean and simplify prompt for alt text
        keywords = self._extract_keywords(prompt)[:5]
        if keywords:
            return f"Digital artwork featuring {', '.join(keywords)}"
        return "AI-generated digital artwork"

    def _get_trending_hashtags(self) -> List[str]:
        """Get currently trending hashtags."""
        try:
            if self.spider_service:
                trends = self.spider_service.get_trending_topics(limit=10)
                return [re.sub(r'[^a-zA-Z0-9]', '', t.get('topic', '')).lower()
                        for t in trends.get('topics', [])]
        except Exception:
            pass

        # Fallback trending tags
        return ['ai', 'aiart', 'trending', 'viral', 'creative']


# Convenience function
def get_seo_optimizer_agent(user=None, project_id=None) -> SEOOptimizerAgent:
    """Get SEOOptimizerAgent instance."""
    return SEOOptimizerAgent(user=user, project_id=project_id)


__all__ = [
    'SEOOptimizerAgent',
    'get_seo_optimizer_agent'
]
