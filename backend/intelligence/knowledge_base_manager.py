"""
Agent Knowledge Base Manager
Manages persistent knowledge bases for all 152+ agents
"""

import asyncio
import json
import logging
from typing import Dict, List, Any, Optional, Set
from datetime import datetime, timezone, timedelta
from collections import defaultdict, Counter
from dataclasses import dataclass, asdict

# Import models
try:
    from .models import (
        AgentLearningEvent,
        AgentKnowledgeBase,
        LearningDocument,
        LearningEmbedding
    )
except ImportError:
    AgentLearningEvent = None
    AgentKnowledgeBase = None
    LearningDocument = None
    LearningEmbedding = None

logger = logging.getLogger(__name__)


@dataclass
class KnowledgeItem:
    """Represents a piece of knowledge in an agent's knowledge base"""
    item_id: str
    content: str
    source_type: str  # 'learning_event', 'document', 'insight'
    source_id: str
    confidence: float
    quality_score: float
    created_at: datetime
    tags: List[str]
    metadata: Dict[str, Any]


@dataclass
class KnowledgeDomain:
    """Represents a domain of knowledge (financial, social, etc.)"""
    domain_name: str
    item_count: int
    avg_confidence: float
    avg_quality: float
    recent_activity: int
    top_tags: List[str]
    knowledge_items: List[KnowledgeItem]


class AgentKnowledgeBaseManager:
    """Manages persistent knowledge bases for agents"""

    def __init__(self):
        self.knowledge_domains = {
            'financial': ['market', 'price', 'stock', 'crypto', 'trading', 'investment'],
            'social': ['trend', 'engagement', 'viral', 'community', 'influence'],
            'technical': ['innovation', 'technology', 'ai', 'development', 'breakthrough'],
            'news': ['breaking', 'politics', 'world', 'current', 'events'],
            'content': ['creation', 'monetization', 'strategy', 'audience'],
            'freelance': ['opportunity', 'job', 'skill', 'rate', 'client'],
            'general': ['analysis', 'insight', 'pattern', 'recommendation']
        }

        self.stats = {
            'knowledge_bases_updated': 0,
            'knowledge_items_added': 0,
            'domains_processed': 0,
            'consolidation_operations': 0
        }

    async def update_knowledge_base(self, agent_id: str, learning_events: List = None) -> Dict[str, Any]:
        """Update agent's knowledge base with new learning events"""
        if not AgentKnowledgeBase or not AgentLearningEvent:
            return {'error': 'Models not available'}

        try:
            # Get or create knowledge base
            knowledge_base, created = AgentKnowledgeBase.objects.get_or_create(
                agent_id=agent_id,
                defaults={
                    'agent_name': f'Agent_{agent_id}',
                    'agent_specialization': 'general'
                }
            )

            # Get recent learning events if not provided
            if learning_events is None:
                cutoff_time = knowledge_base.last_learning_event or (datetime.now(timezone.utc) - timedelta(days=7))
                learning_events = AgentLearningEvent.objects.filter(
                    agent_id=agent_id,
                    timestamp__gt=cutoff_time,
                    confidence_score__gte=0.5
                ).order_by('-timestamp')

            if not learning_events:
                return {'message': 'No new learning events to process'}

            # Process events and update knowledge domains
            knowledge_updates = await self._process_learning_events(knowledge_base, learning_events)

            # Update knowledge base statistics
            knowledge_base.total_learning_events += len(learning_events)
            knowledge_base.last_learning_event = learning_events[0].timestamp if learning_events else None

            # Calculate learning performance metrics
            if learning_events:
                avg_confidence = sum(e.confidence_score for e in learning_events) / len(learning_events)
                avg_quality = sum(e.quality_score for e in learning_events) / len(learning_events)

                # Update running averages
                total_events = knowledge_base.total_learning_events
                old_weight = max(0, (total_events - len(learning_events)) / total_events) if total_events > 0 else 0
                new_weight = len(learning_events) / total_events if total_events > 0 else 1

                knowledge_base.avg_confidence_score = (
                    knowledge_base.avg_confidence_score * old_weight + avg_confidence * new_weight
                )

                # Update learning accuracy based on confidence trends
                recent_confidence_trend = self._calculate_confidence_trend(learning_events)
                knowledge_base.learning_accuracy = min(1.0, knowledge_base.learning_accuracy + recent_confidence_trend * 0.1)

            knowledge_base.save()
            self.stats['knowledge_bases_updated'] += 1

            return {
                'knowledge_base_id': agent_id,
                'events_processed': len(learning_events),
                'knowledge_updates': knowledge_updates,
                'total_events': knowledge_base.total_learning_events,
                'avg_confidence': knowledge_base.avg_confidence_score,
                'learning_accuracy': knowledge_base.learning_accuracy
            }

        except Exception as e:
            logger.error(f"Error updating knowledge base for {agent_id}: {e}")
            return {'error': str(e)}

    async def _process_learning_events(self, knowledge_base: 'AgentKnowledgeBase', events: List) -> Dict[str, Any]:
        """Process learning events and update knowledge domains"""
        domain_updates = {}

        try:
            # Group events by domain
            events_by_domain = self._categorize_events_by_domain(events)

            for domain, domain_events in events_by_domain.items():
                # Get current domain knowledge
                current_knowledge = getattr(knowledge_base, f'{domain}_knowledge', {})

                # Extract knowledge items from events
                new_knowledge_items = []
                for event in domain_events:
                    knowledge_item = self._extract_knowledge_from_event(event, domain)
                    if knowledge_item:
                        new_knowledge_items.append(knowledge_item)

                # Update domain knowledge
                updated_knowledge = self._merge_knowledge_items(current_knowledge, new_knowledge_items)

                # Save back to knowledge base
                setattr(knowledge_base, f'{domain}_knowledge', updated_knowledge)

                domain_updates[domain] = {
                    'new_items': len(new_knowledge_items),
                    'total_items': len(updated_knowledge.get('items', [])),
                    'avg_confidence': sum(item['confidence'] for item in new_knowledge_items) / len(new_knowledge_items) if new_knowledge_items else 0
                }

                self.stats['domains_processed'] += 1

            # Update primary/secondary domains
            knowledge_base.primary_domains = list(events_by_domain.keys())[:3]
            knowledge_base.secondary_domains = list(events_by_domain.keys())[3:6]

        except Exception as e:
            logger.error(f"Error processing learning events: {e}")

        return domain_updates

    def _categorize_events_by_domain(self, events: List) -> Dict[str, List]:
        """Categorize events by knowledge domain"""
        events_by_domain = defaultdict(list)

        for event in events:
            # Determine domain based on signal type and content
            domain = self._determine_knowledge_domain(event)
            events_by_domain[domain].append(event)

        return dict(events_by_domain)

    def _determine_knowledge_domain(self, event) -> str:
        """Determine which knowledge domain an event belongs to"""
        signal_type = event.signal_type.lower()
        content = json.dumps(event.learned_insights).lower() if event.learned_insights else ""

        # Check against domain keywords
        for domain, keywords in self.knowledge_domains.items():
            if any(keyword in signal_type or keyword in content for keyword in keywords):
                return domain

        # Default domain
        return 'general'

    def _extract_knowledge_from_event(self, event, domain: str) -> Optional[Dict[str, Any]]:
        """Extract structured knowledge from a learning event"""
        try:
            # Create knowledge item from event
            knowledge_item = {
                'item_id': str(event.event_id),
                'content': json.dumps(event.learned_insights) if event.learned_insights else "",
                'source_type': 'learning_event',
                'source_id': str(event.event_id),
                'signal_type': event.signal_type,
                'confidence': event.confidence_score,
                'quality_score': event.quality_score,
                'created_at': event.timestamp.isoformat(),
                'source_api': event.source_api,
                'tags': self._generate_tags_for_event(event, domain),
                'metadata': {
                    'agent_specialization': event.agent_specialization,
                    'processing_time_ms': event.processing_time_ms
                }
            }

            return knowledge_item

        except Exception as e:
            logger.error(f"Error extracting knowledge from event: {e}")
            return None

    def _generate_tags_for_event(self, event, domain: str) -> List[str]:
        """Generate relevant tags for a learning event"""
        tags = [domain, event.signal_type, event.source_api]

        # Add content-based tags
        if event.learned_insights:
            content_str = json.dumps(event.learned_insights).lower()

            # Add domain-specific tags
            domain_keywords = self.knowledge_domains.get(domain, [])
            for keyword in domain_keywords:
                if keyword in content_str:
                    tags.append(keyword)

        # Add quality-based tags
        if event.confidence_score > 0.8:
            tags.append('high_confidence')
        elif event.confidence_score < 0.6:
            tags.append('low_confidence')

        return list(set(tags))  # Remove duplicates

    def _merge_knowledge_items(self, current_knowledge: Dict, new_items: List[Dict]) -> Dict:
        """Merge new knowledge items with existing ones"""
        merged_knowledge = current_knowledge.copy() if current_knowledge else {}

        # Initialize structure if needed
        if 'items' not in merged_knowledge:
            merged_knowledge['items'] = []
        if 'item_index' not in merged_knowledge:
            merged_knowledge['item_index'] = {}
        if 'tags' not in merged_knowledge:
            merged_knowledge['tags'] = []

        existing_items = {item['item_id']: item for item in merged_knowledge['items']}

        # Add new items
        for new_item in new_items:
            item_id = new_item['item_id']

            if item_id not in existing_items:
                merged_knowledge['items'].append(new_item)
                merged_knowledge['item_index'][item_id] = len(merged_knowledge['items']) - 1

                # Update tags
                for tag in new_item['tags']:
                    if tag not in merged_knowledge['tags']:
                        merged_knowledge['tags'].append(tag)

                self.stats['knowledge_items_added'] += 1
            else:
                # Update existing item if new one has higher confidence
                existing_item = existing_items[item_id]
                if new_item['confidence'] > existing_item['confidence']:
                    index = merged_knowledge['item_index'][item_id]
                    merged_knowledge['items'][index] = new_item

        # Update summary statistics
        if merged_knowledge['items']:
            merged_knowledge['summary'] = {
                'total_items': len(merged_knowledge['items']),
                'avg_confidence': sum(item['confidence'] for item in merged_knowledge['items']) / len(merged_knowledge['items']),
                'avg_quality': sum(item['quality_score'] for item in merged_knowledge['items']) / len(merged_knowledge['items']),
                'last_updated': datetime.now(timezone.utc).isoformat(),
                'top_tags': self._get_top_tags(merged_knowledge['items'])
            }

        return merged_knowledge

    def _get_top_tags(self, items: List[Dict], limit: int = 10) -> List[str]:
        """Get the most common tags from knowledge items"""
        tag_counter = Counter()
        for item in items:
            tag_counter.update(item.get('tags', []))

        return [tag for tag, count in tag_counter.most_common(limit)]

    def _calculate_confidence_trend(self, events: List) -> float:
        """Calculate confidence trend from recent events"""
        if len(events) < 2:
            return 0

        # Sort by timestamp
        sorted_events = sorted(events, key=lambda e: e.timestamp)

        # Calculate trend
        first_half = sorted_events[:len(sorted_events)//2]
        second_half = sorted_events[len(sorted_events)//2:]

        avg_first = sum(e.confidence_score for e in first_half) / len(first_half)
        avg_second = sum(e.confidence_score for e in second_half) / len(second_half)

        return avg_second - avg_first

    async def get_agent_knowledge_summary(self, agent_id: str) -> Dict[str, Any]:
        """Get comprehensive knowledge summary for an agent"""
        if not AgentKnowledgeBase:
            return {'error': 'Models not available'}

        try:
            knowledge_base = AgentKnowledgeBase.objects.filter(agent_id=agent_id).first()

            if not knowledge_base:
                return {'message': 'No knowledge base found for agent'}

            summary = {
                'agent_id': agent_id,
                'agent_name': knowledge_base.agent_name,
                'specialization': knowledge_base.agent_specialization,
                'total_learning_events': knowledge_base.total_learning_events,
                'avg_confidence': knowledge_base.avg_confidence_score,
                'learning_accuracy': knowledge_base.learning_accuracy,
                'last_updated': knowledge_base.last_updated.isoformat() if knowledge_base.last_updated else None,
                'primary_domains': knowledge_base.primary_domains,
                'secondary_domains': knowledge_base.secondary_domains,
                'knowledge_domains': {}
            }

            # Get knowledge for each domain
            for domain in ['financial', 'social', 'technical', 'news', 'content', 'freelance', 'general']:
                domain_knowledge = getattr(knowledge_base, f'{domain}_knowledge', {})
                if domain_knowledge:
                    summary['knowledge_domains'][domain] = {
                        'total_items': len(domain_knowledge.get('items', [])),
                        'avg_confidence': domain_knowledge.get('summary', {}).get('avg_confidence', 0),
                        'top_tags': domain_knowledge.get('summary', {}).get('top_tags', [])[:5]
                    }

            return summary

        except Exception as e:
            logger.error(f"Error getting knowledge summary for {agent_id}: {e}")
            return {'error': str(e)}

    async def search_agent_knowledge(self, agent_id: str, query: str, domain: str = None, limit: int = 10) -> List[Dict]:
        """Search through an agent's knowledge base"""
        if not AgentKnowledgeBase:
            return []

        try:
            knowledge_base = AgentKnowledgeBase.objects.filter(agent_id=agent_id).first()

            if not knowledge_base:
                return []

            query_lower = query.lower()
            results = []

            # Search through specified domain or all domains
            domains_to_search = [domain] if domain else ['financial', 'social', 'technical', 'news', 'content', 'freelance', 'general']

            for search_domain in domains_to_search:
                domain_knowledge = getattr(knowledge_base, f'{search_domain}_knowledge', {})
                items = domain_knowledge.get('items', [])

                for item in items:
                    # Simple text search
                    if (query_lower in item.get('content', '').lower() or
                        query_lower in item.get('signal_type', '').lower() or
                        any(query_lower in tag.lower() for tag in item.get('tags', []))):

                        result = {
                            'item_id': item['item_id'],
                            'domain': search_domain,
                            'content_preview': item['content'][:200] + "..." if len(item['content']) > 200 else item['content'],
                            'confidence': item['confidence'],
                            'quality_score': item['quality_score'],
                            'created_at': item['created_at'],
                            'tags': item['tags'][:5],  # Limit tags
                            'signal_type': item.get('signal_type')
                        }
                        results.append(result)

            # Sort by confidence and quality
            results.sort(key=lambda x: x['confidence'] * x['quality_score'], reverse=True)

            return results[:limit]

        except Exception as e:
            logger.error(f"Error searching knowledge for {agent_id}: {e}")
            return []

    async def consolidate_agent_knowledge(self, agent_id: str) -> Dict[str, Any]:
        """Consolidate and optimize agent's knowledge base"""
        if not AgentKnowledgeBase:
            return {'error': 'Models not available'}

        try:
            knowledge_base = AgentKnowledgeBase.objects.filter(agent_id=agent_id).first()

            if not knowledge_base:
                return {'message': 'No knowledge base found'}

            consolidation_results = {
                'duplicates_removed': 0,
                'low_quality_filtered': 0,
                'domains_optimized': 0
            }

            # Consolidate each domain
            for domain in ['financial', 'social', 'technical', 'news', 'content', 'freelance', 'general']:
                domain_knowledge = getattr(knowledge_base, f'{domain}_knowledge', {})

                if domain_knowledge and 'items' in domain_knowledge:
                    original_count = len(domain_knowledge['items'])

                    # Remove duplicates and low-quality items
                    consolidated_items = self._consolidate_domain_knowledge(domain_knowledge['items'])

                    # Update domain knowledge
                    domain_knowledge['items'] = consolidated_items
                    domain_knowledge = self._merge_knowledge_items(domain_knowledge, [])  # Rebuild summary

                    setattr(knowledge_base, f'{domain}_knowledge', domain_knowledge)

                    # Track changes
                    items_removed = original_count - len(consolidated_items)
                    consolidation_results['duplicates_removed'] += items_removed
                    if items_removed > 0:
                        consolidation_results['domains_optimized'] += 1

            knowledge_base.save()
            self.stats['consolidation_operations'] += 1

            return consolidation_results

        except Exception as e:
            logger.error(f"Error consolidating knowledge for {agent_id}: {e}")
            return {'error': str(e)}

    def _consolidate_domain_knowledge(self, items: List[Dict]) -> List[Dict]:
        """Consolidate knowledge items in a domain"""
        # Remove duplicates based on content similarity
        unique_items = []
        seen_content = set()

        for item in items:
            content_hash = hash(item.get('content', ''))

            # Only keep high-quality, unique items
            if (content_hash not in seen_content and
                item.get('confidence', 0) >= 0.5 and
                item.get('quality_score', 0) >= 0.5):

                unique_items.append(item)
                seen_content.add(content_hash)

        # Sort by quality and keep only the best items (limit per domain)
        unique_items.sort(key=lambda x: x['confidence'] * x['quality_score'], reverse=True)

        return unique_items[:100]  # Keep top 100 items per domain

    def get_knowledge_stats(self) -> Dict[str, Any]:
        """Get knowledge management statistics"""
        return self.stats.copy()


# Global instance
knowledge_base_manager = AgentKnowledgeBaseManager()