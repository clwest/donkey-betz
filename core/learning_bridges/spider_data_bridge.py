"""
Spider Data Learning Bridge
Learns from spider-collected data to improve agent intelligence and opportunity matching
"""

import logging
from django.db.models.signals import post_save
from django.dispatch import receiver
from typing import Dict, List

from persistence.models import SpiderData
from core.models_unified_system import UserAgentLearning
from core.models.agents_registry import UnifiedAgentTemplate

logger = logging.getLogger(__name__)


class SpiderDataLearningLoop:
    """
    Learns from spider data collection to improve agent intelligence

    Tracks:
    - Which data sources provide best opportunities
    - Quality patterns in spider data
    - Agent-specific data preferences
    - Opportunity matching accuracy
    - Source reliability over time
    """

    def process_spider_data(self, spider_data: SpiderData):
        """Process newly collected spider data for learning"""

        if not spider_data.routed_to_agents:
            logger.debug(f"Spider data {spider_data.id} has no agent routing, skipping learning")
            return

        logger.info(f"🕷️ Learning from spider data: {spider_data.spider_name} -> {len(spider_data.routed_to_agents)} agents")

        try:
            # Process for each agent that received this data
            for agent_name in spider_data.routed_to_agents:
                self._create_agent_learning_entry(spider_data, agent_name)

            logger.info(f"✅ Spider data learning complete: {len(spider_data.routed_to_agents)} learning entries created")

        except Exception as e:
            logger.error(f"Error in spider data learning: {e}", exc_info=True)

    def _create_agent_learning_entry(self, spider_data: SpiderData, agent_name: str):
        """Create a learning entry for a specific agent"""
        try:
            # Try to find the agent
            try:
                agent = UnifiedAgentTemplate.objects.get(name=agent_name)
            except UnifiedAgentTemplate.DoesNotExist:
                logger.warning(f"Agent '{agent_name}' not found in database, skipping learning entry")
                return

            # Extract learning content from spider data
            learning_content = {
                'spider_name': spider_data.spider_name,
                'data_type': spider_data.data_type,
                'quality_score': float(spider_data.quality_score) if spider_data.quality_score else 0.5,
                'relevance_score': float(spider_data.relevance_score) if spider_data.relevance_score else 0.5,
                'source_url': spider_data.source_url,
                'tags': spider_data.tags or [],
                'discovered_at': spider_data.discovered_at.isoformat() if spider_data.discovered_at else None,

                # Performance metrics
                'data_completeness': self._calculate_completeness(spider_data),
                'data_freshness': self._calculate_freshness(spider_data),

                # Learning insights
                'learning_type': 'spider_intelligence',
                'data_source_reliability': self._calculate_source_reliability(spider_data.spider_name),
                'opportunity_potential': self._estimate_opportunity_potential(spider_data),
            }

            # Determine learning domain
            learning_domain = self._map_data_type_to_domain(spider_data.data_type)

            # Calculate confidence score based on data quality
            confidence_score = (
                float(spider_data.quality_score or 0.5) * 0.5 +
                float(spider_data.relevance_score or 0.5) * 0.3 +
                learning_content['data_completeness'] * 0.2
            )

            # Get or create a system user for spider learning
            # Spider data is system-generated, not user-specific
            from django.contrib.auth import get_user_model
            User = get_user_model()

            try:
                system_user = User.objects.get(username='system')
            except User.DoesNotExist:
                # Create system user if it doesn't exist
                system_user = User.objects.create_user(
                    username='system',
                    email='system@unified-platform.local',
                    password=''.join([chr(ord(c) ^ 42) for c in 'system_internal_only'])  # Obfuscated
                )
                logger.info("Created system user for spider learning")

            # Create or update learning entry
            learning_entry, created = UserAgentLearning.objects.get_or_create(
                user=system_user,
                agent_name=agent_name,
                learning_domain=learning_domain,
                learning_source=f"spider:{spider_data.spider_name}",
                defaults={
                    'learning_content': learning_content,
                    'confidence_score': confidence_score,
                    'validation_count': 1,
                    'is_active': True,
                }
            )

            if not created:
                # Update existing entry with new data
                learning_entry.learning_content.update(learning_content)
                learning_entry.validation_count += 1
                learning_entry.confidence_score = (
                    learning_entry.confidence_score * 0.7 + confidence_score * 0.3
                )
                learning_entry.save()
                logger.debug(f"Updated existing learning entry for {agent_name}")
            else:
                logger.info(f"✅ Created learning entry for {agent_name} from {spider_data.spider_name}")

        except Exception as e:
            logger.error(f"Error creating learning entry for {agent_name}: {e}", exc_info=True)

    def _calculate_completeness(self, spider_data: SpiderData) -> float:
        """Calculate data completeness score (0-1)"""
        required_fields = ['title', 'source_url', 'structured_data']
        present = 0

        if spider_data.title:
            present += 1
        if spider_data.source_url:
            present += 1
        if spider_data.structured_data:
            present += 1

        return present / len(required_fields)

    def _calculate_freshness(self, spider_data: SpiderData) -> float:
        """Calculate data freshness score (0-1)"""
        from django.utils import timezone
        from datetime import timedelta

        if not spider_data.discovered_at:
            return 0.5  # Unknown age

        age = timezone.now() - spider_data.discovered_at

        # Fresh data (< 1 hour) = 1.0
        # Recent data (< 24 hours) = 0.8
        # Old data (< 7 days) = 0.5
        # Stale data (> 7 days) = 0.2

        if age < timedelta(hours=1):
            return 1.0
        elif age < timedelta(days=1):
            return 0.8
        elif age < timedelta(days=7):
            return 0.5
        else:
            return 0.2

    def _calculate_source_reliability(self, spider_name: str) -> float:
        """Calculate reliability of this data source based on historical performance"""
        # Count successful data from this spider
        total = SpiderData.objects.filter(spider_name=spider_name).count()

        if total == 0:
            return 0.5  # No history, assume average

        # High-quality data from this spider
        high_quality = SpiderData.objects.filter(
            spider_name=spider_name,
            quality_score__gte=0.7
        ).count()

        return high_quality / total if total > 0 else 0.5

    def _estimate_opportunity_potential(self, spider_data: SpiderData) -> str:
        """Estimate the potential value of this opportunity"""
        quality = float(spider_data.quality_score or 0.5)
        relevance = float(spider_data.relevance_score or 0.5)

        combined = (quality + relevance) / 2

        if combined >= 0.8:
            return 'high'
        elif combined >= 0.6:
            return 'medium'
        else:
            return 'low'

    def _map_data_type_to_domain(self, data_type: str) -> str:
        """Map spider data type to learning domain"""
        mapping = {
            'opportunity': 'income_generation',
            'job_listing': 'career_development',
            'freelance_gig': 'freelance_income',
            'market_intel': 'market_intelligence',
            'content_idea': 'content_creation',
            'financial_data': 'financial_analysis',
            'research': 'research_intelligence',
            'news': 'news_monitoring',
            'tool_discovery': 'tool_intelligence',
            'learning_resource': 'skill_development',
        }

        return mapping.get(data_type, 'general_intelligence')


# Signal integration
spider_data_learning = SpiderDataLearningLoop()


@receiver(post_save, sender=SpiderData)
def on_spider_data_collected(sender, instance, created, **kwargs):
    """Learn from newly collected spider data"""
    if created:  # Only process new data
        try:
            spider_data_learning.process_spider_data(instance)
        except Exception as e:
            logger.error(f"Error in spider data learning signal: {e}", exc_info=True)
