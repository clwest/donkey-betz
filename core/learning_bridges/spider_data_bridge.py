"""
Spider Data Learning Bridge
Learns from spider-collected data to improve agent intelligence and opportunity matching

Session 400: Fixed to use core.models_unified_system.SpiderData (active model with 6500+ records)
instead of persistence.models.SpiderData (empty model - never populated)
"""

import logging
from django.db.models.signals import post_save
from django.dispatch import receiver
from typing import List

# Session 400: Use the CORRECT SpiderData model (the one that actually has data!)
# Also use Agent from core.models_unified_system (has 31 agents) not UnifiedAgentTemplate (28 agents)
from core.models_unified_system import SpiderData, UserAgentLearning, Agent

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
        """Process newly collected spider data for learning

        Session 400: Updated to use core.models_unified_system.SpiderData which doesn't
        have routed_to_agents field. Instead, we determine agents based on data_type/category.
        """
        # Determine which agents should learn from this data based on category
        target_agents = self._get_target_agents_for_data(spider_data)

        if not target_agents:
            logger.debug(f"Spider data {spider_data.id} has no target agents for category '{spider_data.data_type}'")
            return

        logger.info(f"🕷️ Learning from spider data: {spider_data.spider_name} -> {len(target_agents)} agents")

        try:
            # Process for each agent that should learn from this data
            for agent_name in target_agents:
                self._create_agent_learning_entry(spider_data, agent_name)

            logger.info(f"✅ Spider data learning complete: {len(target_agents)} learning entries created")

        except Exception as e:
            logger.error(f"Error in spider data learning: {e}", exc_info=True)

    def _get_target_agents_for_data(self, spider_data: SpiderData) -> List[str]:
        """Determine which agents should learn from this spider data based on category

        Session 400: Maps data_type/category to relevant agents
        """
        # Map data categories to interested agents
        category_to_agents = {
            'tech': ['ResearchAgent', 'TrendAnalysisAgent', 'ContentStrategyAgent', 'CTOAgent'],
            'news': ['ResearchAgent', 'TrendAnalysisAgent', 'ContentStrategyAgent'],
            'jobs': ['OpportunityScoringAgent', 'ResearchAgent'],
            'freelance': ['OpportunityScoringAgent', 'ResearchAgent'],
            'design': ['CreativeDirectorAgent', 'BrandIdentityAgent', 'ContentStrategyAgent'],
            'creative': ['CreativeDirectorAgent', 'BrandIdentityAgent', 'ImageAgent'],
            'financial': ['OpportunityScoringAgent', 'TrendAnalysisAgent', 'CTOAgent'],
            'community': ['SocialMediaAgent', 'ContentStrategyAgent', 'ResearchAgent'],
            'education': ['ResearchAgent', 'ContentStrategyAgent'],
            'legal': ['ResearchAgent', 'CTOAgent'],
            'health': ['ResearchAgent', 'ContentStrategyAgent'],
            'science': ['ResearchAgent', 'TrendAnalysisAgent'],
            'business': ['OpportunityScoringAgent', 'CTOAgent', 'COOAgent'],
            # Session 436: Added ai_ml category for HuggingFace and AI model data
            'ai_ml': ['ResearchAgent', 'TrendAnalysisAgent', 'ImageAgent', 'VideoAgent', 'CTOAgent'],
        }

        data_type = spider_data.data_type.lower() if spider_data.data_type else 'general'

        # Get agents for this category, default to general research agents
        agents = category_to_agents.get(data_type, ['ResearchAgent', 'TrendAnalysisAgent'])

        return agents

    def _create_agent_learning_entry(self, spider_data: SpiderData, agent_name: str):
        """Create a learning entry for a specific agent

        Session 400: Updated to use fields available in core.models_unified_system.SpiderData
        """
        try:
            # Try to find the agent - Session 400: Use Agent model instead of UnifiedAgentTemplate
            try:
                agent = Agent.objects.get(name=agent_name)
            except Agent.DoesNotExist:
                logger.warning(f"Agent '{agent_name}' not found in database, skipping learning entry")
                return

            # Session 400: Extract learning content using available fields in core SpiderData
            # Core SpiderData has: spider_name, source_url, data_type, raw_data, processed_data,
            # relevance_score, insights, embedding, is_processed, is_actionable, created_at
            raw_data = spider_data.raw_data or {}
            items = raw_data.get('items', [])
            item_count = len(items)

            learning_content = {
                'spider_name': spider_data.spider_name,
                'data_type': spider_data.data_type,
                'relevance_score': float(spider_data.relevance_score) if spider_data.relevance_score else 0.5,
                'source_url': spider_data.source_url,
                'item_count': item_count,
                'created_at': spider_data.created_at.isoformat() if spider_data.created_at else None,

                # Performance metrics
                'data_completeness': self._calculate_completeness(spider_data),
                'data_freshness': self._calculate_freshness(spider_data),

                # Learning insights
                'learning_type': 'spider_intelligence',
                'data_source_reliability': self._calculate_source_reliability(spider_data.spider_name),
                'opportunity_potential': self._estimate_opportunity_potential(spider_data),

                # Sample items from data for context - use modelId for AI/ML data, title for others
                'sample_items': [
                    (item.get('modelId', '') or item.get('title', '') or item.get('name', ''))[:100]
                    for item in items[:3]
                ] if items else [],
            }

            # Determine learning domain
            learning_domain = self._map_data_type_to_domain(spider_data.data_type)

            # Session 400: Calculate confidence score - core SpiderData doesn't have quality_score
            # Use relevance_score, completeness, and item count as proxies
            item_score = min(1.0, item_count / 10) if item_count > 0 else 0.3  # More items = higher confidence
            confidence_score = (
                float(spider_data.relevance_score or 0.5) / 100 * 0.4 +  # relevance_score is 0-100
                learning_content['data_completeness'] * 0.3 +
                item_score * 0.3
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
        """Calculate data completeness score (0-1)

        Session 400: Updated to use fields available in core SpiderData
        """
        score = 0.0

        # Check source_url
        if spider_data.source_url:
            score += 0.25

        # Check raw_data has items
        raw_data = spider_data.raw_data or {}
        items = raw_data.get('items', [])
        if items:
            score += 0.5
            # Bonus for items with titles
            items_with_titles = sum(1 for item in items if item.get('title'))
            if items_with_titles > 0:
                score += 0.25 * min(1.0, items_with_titles / len(items))

        return min(1.0, score)

    def _calculate_freshness(self, spider_data: SpiderData) -> float:
        """Calculate data freshness score (0-1)

        Session 400: Use created_at instead of discovered_at (core SpiderData field)
        """
        from django.utils import timezone
        from datetime import timedelta

        if not spider_data.created_at:
            return 0.5  # Unknown age

        age = timezone.now() - spider_data.created_at

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
        """Calculate reliability from actual crawl execution history.

        Session 1085: Now uses SpiderExecutionLog success rate instead of
        hardcoded relevance_score heuristic. Falls back to relevance if
        no execution logs exist.
        """
        try:
            from core.models_unified_system import SpiderExecutionLog
            from django.db.models import Count, Q

            logs = SpiderExecutionLog.objects.filter(spider_name=spider_name)
            total_runs = logs.count()

            if total_runs < 5:
                # Not enough history — fall back to relevance heuristic
                total = SpiderData.objects.filter(spider_name=spider_name).count()
                if total == 0:
                    return 0.5
                high_relevance = SpiderData.objects.filter(
                    spider_name=spider_name, relevance_score__gte=70
                ).count()
                return high_relevance / total if total > 0 else 0.5

            # Use execution log success rate (items_collected > 0 = success)
            successful = logs.filter(items_collected__gt=0).count()
            return round(successful / total_runs, 3)

        except Exception:
            return 0.5

    def _estimate_opportunity_potential(self, spider_data: SpiderData) -> str:
        """Estimate the potential value of this opportunity

        Session 400: Updated to use relevance_score and item count
        """
        # relevance_score is 0-100 in core SpiderData
        relevance = float(spider_data.relevance_score or 50) / 100

        # Also factor in item count
        raw_data = spider_data.raw_data or {}
        items = raw_data.get('items', [])
        item_score = min(1.0, len(items) / 10) if items else 0.3

        combined = (relevance * 0.6 + item_score * 0.4)

        if combined >= 0.7:
            return 'high'
        elif combined >= 0.5:
            return 'medium'
        else:
            return 'low'

    @staticmethod
    def evaluate_actionability(spider_data: SpiderData) -> bool:
        """Evaluate whether spider data is actionable (can drive user decisions)."""
        if (spider_data.relevance_score or 0) < 50:
            return False
        raw = spider_data.raw_data or {}
        items = raw.get('items', [])
        if not items:
            return False
        if spider_data.data_type == 'training_data':
            return False
        return True

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
            # Session 436: Added AI/ML domain for HuggingFace data
            'ai_ml': 'ai_model_intelligence',
        }

        return mapping.get(data_type, 'general_intelligence')


# Signal integration
spider_data_learning = SpiderDataLearningLoop()


@receiver(post_save, sender=SpiderData)
def on_spider_data_collected(sender, instance, created, **kwargs):
    """Learn from newly collected spider data"""
    if created:  # Only process new data
        # Evaluate actionability (field checks only, no DB queries)
        actionable = SpiderDataLearningLoop.evaluate_actionability(instance)
        if actionable:
            SpiderData.objects.filter(pk=instance.pk).update(is_actionable=True)

        try:
            spider_data_learning.process_spider_data(instance)
        except Exception as e:
            logger.error(f"Error in spider data learning signal: {e}", exc_info=True)
