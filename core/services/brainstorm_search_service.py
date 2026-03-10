"""
Session 943: Brainstorm Search Service

Enables PA and Boardroom to search through past Discussion/Panel conversations
for relevant ideas, proposals, and insights WITHOUT creating pending action items.

The value of brainstorming is in searchable reference, not review queues.

Usage:
    from core.services.brainstorm_search_service import brainstorm_search_service

    # Search for ideas on a topic
    results = brainstorm_search_service.search("competitor pricing strategy")

    # Get recent brainstorming summaries
    summaries = brainstorm_search_service.get_recent_summaries(days=7)
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import timedelta

from django.db.models import Q, Count
from django.utils import timezone

logger = logging.getLogger(__name__)


class BrainstormSearchService:
    """
    Search and retrieve insights from automated brainstorming conversations
    (Discussion: and Panel: topics).

    These conversations contain valuable ideas that shouldn't clutter
    the pending review queue, but should be searchable on demand.
    """

    # Conversation prefixes that indicate brainstorming
    BRAINSTORM_PREFIXES = ['Discussion:', 'Panel:']

    def search(
        self,
        query: str,
        days_back: int = 30,
        limit: int = 10,
        conversation_type: Optional[str] = None  # 'discussion', 'panel', or None for both
    ) -> Dict[str, Any]:
        """
        Search brainstorming conversations for relevant content.

        Args:
            query: Search terms (searches topic, messages)
            days_back: How far back to search (default 30 days)
            limit: Max results to return
            conversation_type: Filter to 'discussion' or 'panel' only

        Returns:
            Dict with matching conversations and extracted insights
        """
        from core.models import AgentConversation, ConversationMessage

        cutoff = timezone.now() - timedelta(days=days_back)

        # Build base query for brainstorming conversations
        base_query = Q(started_at__gte=cutoff)

        # Filter by conversation type
        if conversation_type == 'discussion':
            base_query &= Q(topic__startswith='Discussion:')
        elif conversation_type == 'panel':
            base_query &= Q(topic__startswith='Panel:')
        else:
            # Both types
            base_query &= (
                Q(topic__startswith='Discussion:') |
                Q(topic__startswith='Panel:')
            )

        # Search in topic
        topic_matches = AgentConversation.objects.filter(
            base_query & Q(topic__icontains=query)
        ).order_by('-started_at')[:limit]

        # Search in message content
        message_matches = ConversationMessage.objects.filter(
            conversation__in=AgentConversation.objects.filter(base_query),
            content__icontains=query
        ).select_related('conversation', 'agent').order_by('-created_at')[:limit * 2]

        # Dedupe conversations from message matches
        conv_ids_from_messages = set()
        message_results = []
        for msg in message_matches:
            if msg.conversation_id not in conv_ids_from_messages:
                conv_ids_from_messages.add(msg.conversation_id)
                message_results.append({
                    'conversation_id': str(msg.conversation_id),
                    'topic': msg.conversation.topic,
                    'matching_message': msg.content[:500],
                    'agent': msg.agent.name if msg.agent else 'Unknown',
                    'date': msg.created_at.isoformat(),
                })

        # Format topic matches
        topic_results = []
        for conv in topic_matches:
            topic_results.append({
                'conversation_id': str(conv.id),
                'topic': conv.topic,
                'date': conv.started_at.isoformat(),
                'status': conv.status,
                'message_count': conv.messages.count(),
            })

        return {
            'query': query,
            'days_searched': days_back,
            'topic_matches': topic_results,
            'content_matches': message_results[:limit],
            'total_found': len(topic_results) + len(message_results),
        }

    def get_conversation_insights(
        self,
        conversation_id: str,
        include_full_content: bool = False
    ) -> Dict[str, Any]:
        """
        Get detailed insights from a specific brainstorming conversation.

        Args:
            conversation_id: UUID of the conversation
            include_full_content: Whether to include all message content

        Returns:
            Dict with conversation details and key insights
        """
        from core.models import AgentConversation

        try:
            conv = AgentConversation.objects.get(id=conversation_id)
        except AgentConversation.DoesNotExist:
            return {'error': f'Conversation {conversation_id} not found'}

        messages = conv.messages.all().order_by('sequence_number')

        # Extract participants
        participants = set()
        for msg in messages:
            if msg.agent:
                participants.add(msg.agent.name)

        # Get conclusion/summary (usually last few messages)
        conclusion_messages = messages.order_by('-sequence_number')[:3]
        conclusion = "\n".join([
            f"{m.agent.name if m.agent else 'Unknown'}: {m.content[:300]}"
            for m in conclusion_messages
        ])

        result = {
            'conversation_id': str(conv.id),
            'topic': conv.topic,
            'type': 'Discussion' if conv.topic.startswith('Discussion:') else 'Panel',
            'date': conv.started_at.isoformat(),
            'status': conv.status,
            'participants': list(participants),
            'message_count': messages.count(),
            'conclusion_preview': conclusion,
        }

        if include_full_content:
            result['messages'] = [
                {
                    'agent': m.agent.name if m.agent else 'Unknown',
                    'content': m.content,
                    'sequence': m.sequence_number,
                }
                for m in messages
            ]

        return result

    def get_recent_summaries(
        self,
        days: int = 7,
        limit: int = 20
    ) -> Dict[str, Any]:
        """
        Get summaries of recent brainstorming conversations.

        Args:
            days: How many days back to look
            limit: Max conversations to summarize

        Returns:
            Dict with conversation summaries grouped by type
        """
        from core.models import AgentConversation

        cutoff = timezone.now() - timedelta(days=days)

        discussions = AgentConversation.objects.filter(
            started_at__gte=cutoff,
            topic__startswith='Discussion:'
        ).order_by('-started_at')[:limit]

        panels = AgentConversation.objects.filter(
            started_at__gte=cutoff,
            topic__startswith='Panel:'
        ).order_by('-started_at')[:limit]

        def summarize(conv):
            # Get first message as context
            first_msg = conv.messages.order_by('sequence_number').first()
            return {
                'id': str(conv.id),
                'topic': conv.topic.replace('Discussion:', '').replace('Panel:', '').strip()[:100],
                'date': conv.started_at.strftime('%Y-%m-%d %H:%M'),
                'participants': list(
                    conv.messages.exclude(agent__isnull=True)
                    .values_list('agent__name', flat=True).distinct()
                ),
                'messages': conv.messages.count(),
                'preview': first_msg.content[:200] if first_msg else '',
            }

        return {
            'period_days': days,
            'discussions': [summarize(c) for c in discussions],
            'panels': [summarize(c) for c in panels],
            'total_discussions': discussions.count(),
            'total_panels': panels.count(),
        }

    def get_ideas_by_category(
        self,
        category: str,
        days_back: int = 30,
        limit: int = 10
    ) -> Dict[str, Any]:
        """
        Get brainstorming ideas filtered by category/domain.

        Categories: competitor, customer, pricing, content, product, technical, marketing

        Args:
            category: Category to filter by
            days_back: How far back to search
            limit: Max results

        Returns:
            Dict with categorized ideas
        """
        # Category keywords mapping
        category_keywords = {
            'competitor': ['competitor', 'competitive', 'rival', 'market share', 'positioning'],
            'customer': ['customer', 'user', 'persona', 'behavior', 'segment', 'audience'],
            'pricing': ['pricing', 'price', 'revenue', 'monetization', 'subscription', 'tier'],
            'content': ['content', 'blog', 'video', 'podcast', 'article', 'media'],
            'product': ['product', 'feature', 'roadmap', 'mvp', 'prototype', 'launch'],
            'technical': ['technical', 'architecture', 'pipeline', 'api', 'integration', 'data'],
            'marketing': ['marketing', 'campaign', 'brand', 'acquisition', 'growth', 'channel'],
        }

        keywords = category_keywords.get(category.lower(), [category])

        # Search for each keyword and combine results
        all_results = []
        for keyword in keywords:
            results = self.search(keyword, days_back=days_back, limit=limit)
            all_results.extend(results.get('topic_matches', []))
            all_results.extend(results.get('content_matches', []))

        # Dedupe by conversation_id
        seen = set()
        unique_results = []
        for r in all_results:
            conv_id = r.get('conversation_id')
            if conv_id and conv_id not in seen:
                seen.add(conv_id)
                unique_results.append(r)

        return {
            'category': category,
            'keywords_used': keywords,
            'results': unique_results[:limit],
            'total_found': len(unique_results),
        }

    def list_conversations(
        self,
        days_back: int = 30,
        offset: int = 0,
        limit: int = 50,
        conversation_type: Optional[str] = None,
        status: Optional[str] = None,
        include_transcript: bool = False,
    ) -> Dict[str, Any]:
        """
        Paginated listing of all brainstorm conversations.

        Args:
            days_back: How far back to search
            offset: Pagination offset
            limit: Page size (capped at 200 by caller)
            conversation_type: 'discussion', 'panel', or None for both
            status: Filter by conversation status
            include_transcript: Include full message list per conversation

        Returns:
            Dict with conversations list and pagination metadata
        """
        from core.models import AgentConversation

        cutoff = timezone.now() - timedelta(days=days_back)

        qs = AgentConversation.objects.filter(started_at__gte=cutoff).filter(
            Q(topic__startswith='Discussion:') | Q(topic__startswith='Panel:')
        )

        if conversation_type == 'discussion':
            qs = qs.filter(topic__startswith='Discussion:')
        elif conversation_type == 'panel':
            qs = qs.filter(topic__startswith='Panel:')

        if status:
            qs = qs.filter(status=status)

        total_count = qs.count()
        conversations = qs.order_by('-started_at').annotate(
            msg_count=Count('messages')
        )[offset:offset + limit]

        results = []
        for conv in conversations:
            conv_type = 'Discussion' if conv.topic.startswith('Discussion:') else 'Panel'
            # Extract participant names
            participants = list(
                conv.messages.exclude(agent__isnull=True)
                .values_list('agent__name', flat=True)
                .distinct()
            )
            entry = {
                'id': str(conv.id),
                'topic': conv.topic,
                'type': conv_type,
                'started_at': conv.started_at.isoformat(),
                'status': conv.status,
                'message_count': conv.msg_count,
                'quality_score': getattr(conv, 'quality_score', None),
                'conclusion': (conv.conclusion or '')[:300],
                'participants': participants,
            }
            if include_transcript:
                entry['messages'] = list(
                    conv.messages.order_by('sequence_number').values(
                        'agent__name', 'content', 'sequence_number', 'message_type'
                    )
                )
            results.append(entry)

        return {
            'conversations': results,
            'total_count': total_count,
            'offset': offset,
            'limit': limit,
            'has_more': (offset + limit) < total_count,
        }

    def get_stats(self, days: int = 30) -> Dict[str, Any]:
        """
        Get statistics about brainstorming activity.

        Args:
            days: Period to analyze

        Returns:
            Dict with brainstorming statistics
        """
        from core.models import AgentConversation
        from django.db.models import Count
        from django.db.models.functions import TruncDate

        cutoff = timezone.now() - timedelta(days=days)

        # Count by type
        discussions = AgentConversation.objects.filter(
            started_at__gte=cutoff,
            topic__startswith='Discussion:'
        ).count()

        panels = AgentConversation.objects.filter(
            started_at__gte=cutoff,
            topic__startswith='Panel:'
        ).count()

        # Count by day
        by_day = AgentConversation.objects.filter(
            started_at__gte=cutoff
        ).filter(
            Q(topic__startswith='Discussion:') | Q(topic__startswith='Panel:')
        ).annotate(
            day=TruncDate('started_at')
        ).values('day').annotate(count=Count('id')).order_by('-day')[:7]

        # Top topics (extract topic without prefix)
        all_convs = AgentConversation.objects.filter(
            started_at__gte=cutoff
        ).filter(
            Q(topic__startswith='Discussion:') | Q(topic__startswith='Panel:')
        ).values_list('topic', flat=True)

        # Simple keyword extraction from topics
        topic_words = {}
        for topic in all_convs:
            clean = topic.replace('Discussion:', '').replace('Panel:', '').strip().lower()
            for word in clean.split()[:5]:  # First 5 words
                if len(word) > 4:  # Skip short words
                    topic_words[word] = topic_words.get(word, 0) + 1

        top_keywords = sorted(topic_words.items(), key=lambda x: -x[1])[:10]

        return {
            'period_days': days,
            'total_discussions': discussions,
            'total_panels': panels,
            'total_brainstorming': discussions + panels,
            'daily_breakdown': [
                {'date': item['day'].isoformat(), 'count': item['count']}
                for item in by_day
            ],
            'top_keywords': [{'word': w, 'count': c} for w, c in top_keywords],
        }


# Singleton instance
brainstorm_search_service = BrainstormSearchService()
