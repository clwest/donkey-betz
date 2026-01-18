"""
Content Idea Pipeline Service

Session 766: Connects Content Production (Dead End #9) to Dreams & Conversations.

Problem: Content production works, but content ideas from Dreams and Conversations
         don't feed into content channels. 1,056 content-related dreams exist
         but none become episodes.

Solution: Pipeline that mines Dreams and Conversations for content ideas,
          matches them to appropriate content channels, and creates episode entries.

Flow:
    1. Scan Dreams for content-related ideas (video, podcast, blog, etc.)
    2. Scan Conversations for content ideas
    3. Match ideas to appropriate content channels based on topic/audience
    4. Create ChannelEpisode entries with source tracking
    5. Trigger content production workflow via Orchestration
"""

import logging
import re
from typing import Dict, List, Optional, Any
from datetime import timedelta
from django.utils import timezone
from django.db.models import Q

logger = logging.getLogger(__name__)


class ContentIdeaPipeline:
    """
    Pipeline for mining content ideas from Dreams and Conversations.

    Transforms system-generated ideas into actionable content production tasks.
    """

    # Content type keywords for matching
    CONTENT_KEYWORDS = {
        'video': ['video', 'youtube', 'tiktok', 'reel', 'shorts', 'clip', 'film', 'visual'],
        'podcast': ['podcast', 'audio', 'episode', 'interview', 'discussion', 'talk'],
        'blog': ['blog', 'article', 'post', 'write', 'written', 'essay', 'guide'],
        'social': ['social', 'tweet', 'thread', 'instagram', 'facebook', 'linkedin'],
        'educational': ['tutorial', 'lesson', 'course', 'teach', 'explain', 'learn', 'education'],
    }

    # Topic matching patterns
    TOPIC_PATTERNS = {
        'ai': r'\b(ai|artificial intelligence|machine learning|ml|deep learning|neural|gpt|llm)\b',
        'tech': r'\b(tech|technology|software|programming|coding|developer)\b',
        'business': r'\b(business|startup|entrepreneur|marketing|sales|revenue)\b',
        'science': r'\b(science|research|experiment|discovery|physics|biology)\b',
        'entertainment': r'\b(entertainment|fun|game|movie|music|creative)\b',
        'kids': r'\b(kid|child|children|young|family|parent)\b',
    }

    def __init__(self):
        self.stats = {
            'dreams_scanned': 0,
            'conversations_scanned': 0,
            'ideas_found': 0,
            'ideas_matched': 0,
            'episodes_created': 0,
            'attention_items_created': 0,
            'errors': [],
        }

    def process_content_ideas(
        self,
        dry_run: bool = False,
        limit: int = 50,
        include_dreams: bool = True,
        include_conversations: bool = True,
        days_lookback: int = 30,
    ) -> Dict[str, Any]:
        """
        Process content ideas from Dreams and Conversations.

        Args:
            dry_run: If True, don't make changes
            limit: Max ideas to process
            include_dreams: Include dreams as source
            include_conversations: Include conversations as source
            days_lookback: How far back to look for ideas

        Returns:
            Processing statistics
        """
        self.stats = {
            'dreams_scanned': 0,
            'conversations_scanned': 0,
            'ideas_found': 0,
            'ideas_matched': 0,
            'episodes_created': 0,
            'attention_items_created': 0,
            'dry_run': dry_run,
            'errors': [],
        }

        try:
            ideas = []

            # Phase 1: Mine dreams for content ideas
            if include_dreams:
                dream_ideas = self._mine_dreams_for_ideas(
                    limit=limit // 2,
                    days_lookback=days_lookback,
                )
                ideas.extend(dream_ideas)

            # Phase 2: Mine conversations for content ideas
            if include_conversations:
                convo_ideas = self._mine_conversations_for_ideas(
                    limit=limit // 2,
                    days_lookback=days_lookback,
                )
                ideas.extend(convo_ideas)

            self.stats['ideas_found'] = len(ideas)

            # Phase 3: Match ideas to channels and create episodes
            for idea in ideas:
                self._process_idea(idea, dry_run=dry_run)

            logger.info(
                f"Content idea pipeline complete: "
                f"{self.stats['ideas_found']} ideas found, "
                f"{self.stats['ideas_matched']} matched, "
                f"{self.stats['episodes_created']} episodes created"
            )

        except Exception as e:
            logger.error(f"Content idea pipeline error: {e}")
            self.stats['errors'].append(str(e))

        return self.stats

    def _mine_dreams_for_ideas(
        self,
        limit: int = 25,
        days_lookback: int = 30,
    ) -> List[Dict[str, Any]]:
        """Mine dreams for content ideas."""
        from core.models_unified_system import AgentDream

        ideas = []
        cutoff = timezone.now() - timedelta(days=days_lookback)

        # Build content query
        content_query = Q()
        for content_type, keywords in self.CONTENT_KEYWORDS.items():
            for keyword in keywords:
                content_query |= Q(title__icontains=keyword)
                content_query |= Q(content__icontains=keyword)

        # Find content-related dreams
        dreams = AgentDream.objects.filter(
            content_query,
            dreamed_at__gte=cutoff,
        ).exclude(
            # Exclude already-processed dreams
            title__startswith='[PROCESSED]'
        ).select_related('agent')[:limit]

        self.stats['dreams_scanned'] = dreams.count()

        for dream in dreams:
            idea = self._extract_idea_from_dream(dream)
            if idea:
                ideas.append(idea)

        logger.info(f"Found {len(ideas)} content ideas from {len(dreams)} dreams")
        return ideas

    def _extract_idea_from_dream(self, dream) -> Optional[Dict[str, Any]]:
        """Extract a content idea from a dream."""
        # Determine content type
        content_type = self._detect_content_type(dream.title + ' ' + dream.content)
        if not content_type:
            return None

        # Determine topic category
        topic = self._detect_topic(dream.title + ' ' + dream.content)

        return {
            'source_type': 'dream',
            'source_id': str(dream.id),
            'title': dream.title,
            'content': dream.content[:500],  # Truncate for processing
            'content_type': content_type,
            'topic': topic,
            'agent': getattr(dream.agent, 'name', 'Unknown') if dream.agent else 'System',
            'created_at': dream.dreamed_at,  # AgentDream uses dreamed_at
            'dream_type': getattr(dream, 'dream_type', 'unknown'),
            'origin': getattr(dream, 'origin', 'unknown'),
        }

    def _mine_conversations_for_ideas(
        self,
        limit: int = 25,
        days_lookback: int = 30,
    ) -> List[Dict[str, Any]]:
        """Mine conversations for content ideas."""
        from core.models import ConversationMemory

        ideas = []
        cutoff = timezone.now() - timedelta(days=days_lookback)

        # Build content query
        content_query = Q()
        for content_type, keywords in self.CONTENT_KEYWORDS.items():
            for keyword in keywords:
                content_query |= Q(message__icontains=keyword)
                content_query |= Q(response__icontains=keyword)

        # Find content-related conversations
        conversations = ConversationMemory.objects.filter(
            content_query,
            created_at__gte=cutoff,
            success=True,  # Only successful conversations
        )[:limit]

        self.stats['conversations_scanned'] = conversations.count()

        for convo in conversations:
            idea = self._extract_idea_from_conversation(convo)
            if idea:
                ideas.append(idea)

        logger.info(f"Found {len(ideas)} content ideas from {len(conversations)} conversations")
        return ideas

    def _extract_idea_from_conversation(self, convo) -> Optional[Dict[str, Any]]:
        """Extract a content idea from a conversation."""
        full_text = (convo.message or '') + ' ' + (convo.response or '')

        # Determine content type
        content_type = self._detect_content_type(full_text)
        if not content_type:
            return None

        # Determine topic category
        topic = self._detect_topic(full_text)

        # Extract a title from the conversation
        title = self._generate_title_from_text(convo.message or '')

        return {
            'source_type': 'conversation',
            'source_id': str(convo.id),
            'title': title,
            'content': full_text[:500],
            'content_type': content_type,
            'topic': topic,
            'agent': convo.agents_used or 'PersonalAssistant',
            'created_at': convo.created_at,
        }

    def _detect_content_type(self, text: str) -> Optional[str]:
        """Detect the type of content from text."""
        text_lower = text.lower()

        for content_type, keywords in self.CONTENT_KEYWORDS.items():
            for keyword in keywords:
                if keyword in text_lower:
                    return content_type

        return None

    def _detect_topic(self, text: str) -> str:
        """Detect the topic category from text."""
        text_lower = text.lower()

        for topic, pattern in self.TOPIC_PATTERNS.items():
            if re.search(pattern, text_lower, re.IGNORECASE):
                return topic

        return 'general'

    def _generate_title_from_text(self, text: str) -> str:
        """Generate a title from conversation text."""
        # Take first sentence or first 50 chars
        text = text.strip()
        if '.' in text[:100]:
            title = text.split('.')[0]
        elif '?' in text[:100]:
            title = text.split('?')[0] + '?'
        else:
            title = text[:50]

        return title[:100] if len(title) > 100 else title

    def _process_idea(self, idea: Dict[str, Any], dry_run: bool = False) -> None:
        """Process a single content idea - match to channel and create episode."""
        from core.models_autonomous_studio import ContentChannel, ChannelEpisode

        # Find matching channel based on topic and content type
        channel = self._find_matching_channel(idea)

        if not channel:
            # Create attention item for unmatched idea
            self._create_idea_attention_item(idea, dry_run=dry_run)
            return

        self.stats['ideas_matched'] += 1

        if dry_run:
            self.stats['episodes_created'] += 1
            return

        try:
            # Check if episode already exists for this source
            existing = ChannelEpisode.objects.filter(
                channel=channel,
                topic__icontains=idea['source_id'][:20],
            ).exists()

            if existing:
                logger.debug(f"Episode already exists for idea {idea['source_id']}")
                return

            # Create episode entry
            episode = ChannelEpisode.objects.create(
                channel=channel,
                title=f"[Idea] {idea['title'][:150]}",
                topic=f"{idea['topic']} | Source: {idea['source_type']}:{idea['source_id'][:20]}",
                description=(
                    f"Content idea from {idea['source_type']}:\n\n"
                    f"{idea['content']}\n\n"
                    f"Content type: {idea['content_type']}\n"
                    f"Agent: {idea['agent']}\n"
                    f"Original created: {idea['created_at']}"
                ),
                script='',  # To be generated during production
            )

            self.stats['episodes_created'] += 1
            logger.info(f"Created episode {episode.id} from {idea['source_type']} idea")

            # Trigger orchestration if available
            self._trigger_content_production(episode, idea)

        except Exception as e:
            self.stats['errors'].append(f"Failed to create episode: {e}")
            logger.error(f"Failed to create episode: {e}")

    def _find_matching_channel(self, idea: Dict[str, Any]):
        """Find a matching content channel for the idea."""
        from core.models_autonomous_studio import ContentChannel

        # Try to match by topic domain
        topic = idea.get('topic', 'general')
        content_type = idea.get('content_type', 'video')

        # Build matching query
        channels = ContentChannel.objects.filter(
            status='active'
        )

        # Try topic match first
        for channel in channels:
            channel_domain = (channel.topic_domain or '').lower()
            if topic in channel_domain or topic == 'general':
                # Also check content type compatibility
                if content_type in ['video', 'educational']:
                    return channel

        # Fall back to any active channel
        return channels.first()

    def _create_idea_attention_item(self, idea: Dict[str, Any], dry_run: bool = False) -> None:
        """Create attention item for an unmatched content idea."""
        from core.models_human_interface import HumanAttentionItem
        from django.contrib.auth import get_user_model

        User = get_user_model()

        if dry_run:
            self.stats['attention_items_created'] += 1
            return

        try:
            user = User.objects.filter(is_superuser=True).first()
            if not user:
                user = User.objects.filter(is_staff=True).first()
            if not user:
                return

            # Check if attention item already exists
            existing = HumanAttentionItem.objects.filter(
                source_type='content_idea',
                source_id=idea['source_id'],
                status='pending'
            ).exists()

            if existing:
                return

            HumanAttentionItem.objects.create(
                user=user,
                title=f"[Content Idea] {idea['title'][:80]}",
                summary=(
                    f"New content idea from {idea['source_type']}:\n\n"
                    f"Topic: {idea['topic']}\n"
                    f"Type: {idea['content_type']}\n"
                    f"Content: {idea['content'][:200]}...\n\n"
                    f"No matching channel found. Create a new channel or assign manually."
                ),
                item_type='content_idea',
                urgency='low',
                status='pending',
                source_type='content_idea',
                source_id=idea['source_id'],
                source_agent='ContentIdeaPipeline',
                payload={
                    'idea': idea,
                    'action_options': [
                        {'id': 'create_channel', 'label': 'Create Channel', 'action': 'create_channel', 'style': 'primary'},
                        {'id': 'assign_channel', 'label': 'Assign to Channel', 'action': 'assign', 'style': 'secondary'},
                        {'id': 'dismiss', 'label': 'Dismiss', 'action': 'dismiss', 'style': 'warning'},
                    ],
                }
            )

            self.stats['attention_items_created'] += 1

        except Exception as e:
            self.stats['errors'].append(f"Failed to create attention item: {e}")

    def _trigger_content_production(self, episode, idea: Dict[str, Any]) -> None:
        """Trigger content production workflow for the episode."""
        try:
            from core.services.orchestration_engine import orchestration_engine
            from core.models_unified_system import CustomWorkflow

            # Find or create content production workflow
            workflow = CustomWorkflow.objects.filter(
                name__icontains='content production'
            ).first()

            if not workflow:
                logger.debug("No content production workflow found, skipping orchestration")
                return

            # Create orchestration execution
            orchestration_engine.execute_workflow(
                workflow=workflow,
                context={
                    'episode_id': str(episode.id),
                    'channel_id': str(episode.channel.id),
                    'idea_source': idea['source_type'],
                    'idea_source_id': idea['source_id'],
                    'triggered_by': 'content_idea_pipeline',
                },
                async_mode=True,
            )

            logger.info(f"Triggered content production for episode {episode.id}")

        except ImportError:
            logger.debug("Orchestration engine not available")
        except Exception as e:
            logger.warning(f"Failed to trigger content production: {e}")

    def get_statistics(self) -> Dict[str, Any]:
        """Get current content pipeline statistics."""
        from core.models_unified_system import AgentDream
        from core.models import ConversationMemory
        from core.models_autonomous_studio import ContentChannel, ChannelEpisode
        from django.db.models import Count

        # Count content-related dreams
        content_query = Q()
        for keywords in self.CONTENT_KEYWORDS.values():
            for keyword in keywords:
                content_query |= Q(title__icontains=keyword)
                content_query |= Q(content__icontains=keyword)

        content_dreams = AgentDream.objects.filter(content_query).count()

        # Count content-related conversations
        convo_query = Q()
        for keywords in self.CONTENT_KEYWORDS.values():
            for keyword in keywords:
                convo_query |= Q(message__icontains=keyword)
                convo_query |= Q(response__icontains=keyword)

        content_convos = ConversationMemory.objects.filter(convo_query).count()

        # Channel and episode stats
        channels = ContentChannel.objects.filter(status='active').count()
        episodes = ChannelEpisode.objects.count()
        idea_episodes = ChannelEpisode.objects.filter(title__startswith='[Idea]').count()

        return {
            'sources': {
                'content_related_dreams': content_dreams,
                'content_related_conversations': content_convos,
            },
            'channels': {
                'active': channels,
                'total': ContentChannel.objects.count(),
            },
            'episodes': {
                'total': episodes,
                'from_ideas': idea_episodes,
            },
        }


# Singleton instance
content_idea_pipeline = ContentIdeaPipeline()
