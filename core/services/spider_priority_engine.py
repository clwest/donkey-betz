"""
Session 326: Spider Priority Engine

This service prioritizes spider data collection based on active projects:
1. Scans active projects for relevant topics
2. Matches topics to spider categories
3. Calculates priority weights for spider scheduling
4. Influences which spiders run more frequently

This closes the loop: Projects → Spider Collection → Relevant Data
"""
import logging
from typing import Any, Dict, List
from uuid import UUID

from django.db import transaction
from django.db.models import Count, Sum
from django.utils import timezone
from datetime import timedelta

logger = logging.getLogger(__name__)


class SpiderPriorityEngine:
    """
    Dynamically prioritizes spider categories based on active project needs.

    Flow:
    1. Projects created with topics/descriptions
    2. Engine extracts keywords and matches to spider categories
    3. ProjectSpiderPriority entries created with weights
    4. Spider scheduler uses weights to prioritize runs
    5. Feedback loop adjusts weights based on usefulness
    """

    # Topic to spider category mappings
    TOPIC_CATEGORY_MAP = {
        # Tech topics
        'ai': ['tech', 'ai_creative', 'hackernews', 'devto'],
        'artificial intelligence': ['tech', 'ai_creative', 'hackernews'],
        'machine learning': ['tech', 'ai_creative', 'hackernews'],
        'startup': ['tech', 'innovation', 'producthunt'],
        'saas': ['tech', 'digital_products', 'producthunt'],
        'software': ['tech', 'digital_products', 'hackernews'],

        # Business topics
        'market': ['news', 'financial', 'innovation'],
        'competitor': ['tech', 'news', 'producthunt'],
        'business': ['news', 'innovation', 'financial'],
        'enterprise': ['tech', 'news', 'financial'],

        # Creative topics
        'design': ['creative_assets', 'design', 'visual_trends'],
        'content': ['content_creation', 'creative_assets'],
        'video': ['content_creation', 'ai_creative'],
        'audio': ['content_creation', 'ai_creative'],
        'podcast': ['content_creation', 'community'],

        # Financial topics
        'crypto': ['financial', 'innovation'],
        'finance': ['financial', 'news'],
        'investment': ['financial', 'innovation'],

        # Jobs/Freelance topics
        'freelance': ['freelance', 'remote_work', 'jobs'],
        'remote': ['remote_work', 'freelance', 'jobs'],
        'job': ['jobs', 'freelance', 'remote_work'],
        'hiring': ['jobs', 'remote_work'],

        # Community topics
        'reddit': ['community', 'social'],
        'community': ['community', 'social'],
        'social': ['social', 'community'],
    }

    # Default base weight for all categories
    DEFAULT_WEIGHT = 1.0

    # Weight multipliers based on recency
    RECENCY_MULTIPLIERS = {
        'very_recent': 2.0,    # Created in last 7 days
        'recent': 1.5,         # Created in last 30 days
        'older': 1.0,          # Older projects
    }

    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.SpiderPriorityEngine")

    def _get_data_value_boosts(self) -> Dict[str, float]:
        """
        Query spider_data_value LearningPatterns and return a
        {data_type: boost_multiplier} dict.

        Boost formula: 1.0 + min(actionable_pct / 100, 1.0) * 0.5
        scaled by avg_relevance / 100.  Types with 0% actionable or
        low relevance return 1.0 (neutral).
        """
        try:
            from core.models_unified_system import LearningPattern

            patterns = LearningPattern.objects.filter(
                pattern_type='spider_data_value',
                is_active=True,
            ).values_list('pattern_data', flat=True)

            boosts: Dict[str, float] = {}
            for data in patterns:
                data_type = data.get('data_type', '')
                actionable_pct = data.get('actionable_pct', 0) or 0
                avg_relevance = data.get('avg_relevance', 0) or 0

                if not data_type or (actionable_pct <= 0 and avg_relevance <= 0):
                    continue

                action_factor = min(actionable_pct / 100, 1.0) * 0.5
                relevance_scale = min(avg_relevance / 100, 1.0)
                boost = 1.0 + action_factor * relevance_scale
                if boost > 1.0:
                    boosts[data_type] = round(boost, 4)

            return boosts
        except Exception as e:
            self.logger.debug(f"Could not load data-value boosts: {e}")
            return {}

    def calculate_priorities(self) -> Dict[str, float]:
        """
        Calculate priority weights for all spider categories based on active projects.

        Returns:
            Dict mapping category slug to priority weight
        """
        from core.models_unified_system import SpiderCategory
        from core.models_partnership import PartnershipProject

        # Get all active projects
        active_projects = PartnershipProject.objects.filter(
            status__in=['active', 'in_progress', 'research']
        )

        # Aggregate priorities across projects
        category_weights: Dict[str, float] = {}
        category_counts: Dict[str, int] = {}

        for project in active_projects:
            project_priorities = self._analyze_project_topics(project)
            recency_mult = self._get_recency_multiplier(project)

            for category_slug, base_weight in project_priorities.items():
                adjusted_weight = base_weight * recency_mult

                if category_slug not in category_weights:
                    category_weights[category_slug] = 0.0
                    category_counts[category_slug] = 0

                category_weights[category_slug] += adjusted_weight
                category_counts[category_slug] += 1

        # Normalize weights
        for slug in category_weights:
            if category_counts[slug] > 0:
                # Average weight per project, with slight boost for popularity
                category_weights[slug] = (
                    category_weights[slug] / category_counts[slug]
                ) * (1 + min(category_counts[slug] * 0.1, 0.5))

        # Ensure all categories have at least default weight
        all_categories = SpiderCategory.objects.all()
        for cat in all_categories:
            if cat.slug not in category_weights:
                category_weights[cat.slug] = self.DEFAULT_WEIGHT

        # Apply data-value boosts from spider_data_value learning patterns
        data_value_boosts = self._get_data_value_boosts()
        for category_slug in category_weights:
            if category_slug in data_value_boosts:
                category_weights[category_slug] *= data_value_boosts[category_slug]

        self.logger.info(f"Calculated priorities for {len(category_weights)} categories")
        return category_weights

    def _analyze_project_topics(self, project) -> Dict[str, float]:
        """
        Analyze a project's content to determine relevant spider categories.

        Returns:
            Dict mapping category slug to weight for this project
        """
        # Combine all project text for analysis
        # PartnershipProject uses project_name and project_type
        text_sources = [
            getattr(project, 'project_name', '') or getattr(project, 'name', '') or '',
            project.description or '',
            getattr(project, 'project_type', '') or '',
        ]

        # Add research queries if available
        if hasattr(project, 'research_results'):
            for research in project.research_results.all()[:5]:
                text_sources.append(research.query or '')

        combined_text = ' '.join(text_sources).lower()

        # Find matching categories
        matched_categories: Dict[str, float] = {}

        for topic, categories in self.TOPIC_CATEGORY_MAP.items():
            if topic in combined_text:
                for cat in categories:
                    if cat not in matched_categories:
                        matched_categories[cat] = 0.0
                    matched_categories[cat] += 1.0

        # Normalize to weights between 1.0 and 3.0
        if matched_categories:
            max_score = max(matched_categories.values())
            for cat in matched_categories:
                matched_categories[cat] = 1.0 + (matched_categories[cat] / max_score) * 2.0

        return matched_categories

    def _get_recency_multiplier(self, project) -> float:
        """Get weight multiplier based on project recency."""
        now = timezone.now()
        age = now - project.created_at

        if age < timedelta(days=7):
            return self.RECENCY_MULTIPLIERS['very_recent']
        elif age < timedelta(days=30):
            return self.RECENCY_MULTIPLIERS['recent']
        else:
            return self.RECENCY_MULTIPLIERS['older']

    def get_priority_for_spider(self, spider_name: str) -> float:
        """
        Get the current priority weight for a specific spider.

        Used by spider scheduler to determine run frequency.

        Args:
            spider_name: Name of the spider (e.g., 'hackernews', 'reddit')

        Returns:
            Priority weight (1.0 = normal, higher = more frequent)
        """
        from ai_core.spiders.spider_registry import SpiderRegistry

        # Get spider's category
        try:
            registry = SpiderRegistry()
            spider_config = registry.get_spider_config(spider_name)
            category = spider_config.get('category', 'general') if spider_config else 'general'
        except Exception:
            category = 'general'

        # Get priority from database
        from core.models_unified_system import ProjectSpiderPriority

        priorities = ProjectSpiderPriority.objects.filter(
            spider_category__slug=category
        ).aggregate(
            avg_weight=Sum('priority_weight') / Count('id')
        )

        return priorities['avg_weight'] or self.DEFAULT_WEIGHT

    def update_project_priorities(self, project) -> Dict[str, Any]:
        """
        Update or create ProjectSpiderPriority entries for a project.

        Called when:
        - New project created
        - Research completed on project
        - User feedback received

        Args:
            project: PartnershipProject instance

        Returns:
            Dict with update statistics
        """
        from core.models_unified_system import (
            SpiderCategory,
            ProjectSpiderPriority,
        )

        # Analyze project topics
        topic_weights = self._analyze_project_topics(project)

        created = 0
        updated = 0

        with transaction.atomic():
            for category_slug, weight in topic_weights.items():
                try:
                    category = SpiderCategory.objects.get(slug=category_slug)
                except SpiderCategory.DoesNotExist:
                    # Create category if it doesn't exist
                    category = SpiderCategory.objects.create(
                        slug=category_slug,
                        name=category_slug.replace('_', ' ').title(),
                        icon=self._get_category_icon(category_slug),
                    )

                # Get keywords that matched
                matched_keywords = self._get_matched_keywords(project, category_slug)

                priority, was_created = ProjectSpiderPriority.objects.update_or_create(
                    project=project,
                    spider_category=category,
                    defaults={
                        'priority_weight': weight,
                        'matched_keywords': matched_keywords,
                        'is_auto_detected': True,
                    }
                )

                if was_created:
                    created += 1
                else:
                    updated += 1

        self.logger.info(
            f"Updated spider priorities for project {project.id}: "
            f"{created} created, {updated} updated"
        )

        return {
            'project_id': str(project.id),
            'categories_matched': len(topic_weights),
            'created': created,
            'updated': updated,
        }

    def _get_matched_keywords(self, project, category_slug: str) -> List[str]:
        """Get the keywords that matched a project to a category."""
        name = getattr(project, 'project_name', '') or getattr(project, 'name', '') or ''
        desc = project.description or ''
        ptype = getattr(project, 'project_type', '') or ''
        text = f"{name} {desc} {ptype}".lower()
        matched = []

        for topic, categories in self.TOPIC_CATEGORY_MAP.items():
            if category_slug in categories and topic in text:
                matched.append(topic)

        return matched[:10]  # Limit to 10 keywords

    def _get_category_icon(self, category_slug: str) -> str:
        """Get an appropriate icon for a spider category."""
        icons = {
            'tech': '💻',
            'ai_creative': '🤖',
            'financial': '💰',
            'news': '📰',
            'innovation': '💡',
            'creative_assets': '🎨',
            'design': '✏️',
            'content_creation': '📝',
            'community': '👥',
            'social': '💬',
            'freelance': '💼',
            'jobs': '👔',
            'remote_work': '🏠',
            'digital_products': '📦',
        }
        return icons.get(category_slug, '🕷️')

    def detect_topics(self, text: str) -> List[str]:
        """
        Detect relevant topics from arbitrary text.

        Useful for:
        - Analyzing user queries
        - Extracting project themes
        - Matching content to spiders

        Args:
            text: Text to analyze

        Returns:
            List of detected topic keywords
        """
        text_lower = text.lower()
        detected = []

        for topic in self.TOPIC_CATEGORY_MAP.keys():
            if topic in text_lower:
                detected.append(topic)

        return detected

    def recalculate_all_priorities(self) -> Dict[str, Any]:
        """
        Recalculate priorities for all active projects.
        Called by Celery Beat every 6 hours.

        Returns:
            Dict with recalculation statistics
        """
        from core.models_partnership import PartnershipProject

        active_projects = PartnershipProject.objects.filter(
            status__in=['active', 'in_progress', 'research']
        )

        total_created = 0
        total_updated = 0
        project_count = 0

        for project in active_projects:
            result = self.update_project_priorities(project)
            total_created += result['created']
            total_updated += result['updated']
            project_count += 1

        self.logger.info(
            f"Recalculated spider priorities for {project_count} projects"
        )

        return {
            'projects_processed': project_count,
            'priorities_created': total_created,
            'priorities_updated': total_updated,
            'timestamp': timezone.now().isoformat(),
        }

    def apply_feedback_to_priorities(
        self,
        project_id: UUID,
        category_slug: str,
        is_useful: bool
    ) -> None:
        """
        Adjust spider priority based on whether data was useful.

        Called when user provides feedback on research that used spider data.

        Args:
            project_id: Project that received the data
            category_slug: Spider category that provided data
            is_useful: Whether the data was marked useful
        """
        from core.models_unified_system import ProjectSpiderPriority

        try:
            priority = ProjectSpiderPriority.objects.get(
                project_id=project_id,
                spider_category__slug=category_slug
            )

            priority.data_used_count += 1
            if is_useful:
                priority.useful_data_count += 1

            # Adjust weight based on effectiveness
            effectiveness = priority.effectiveness_score
            if effectiveness > 0.7:
                priority.priority_weight = min(priority.priority_weight * 1.1, 5.0)
            elif effectiveness < 0.3 and priority.data_used_count > 5:
                priority.priority_weight = max(priority.priority_weight * 0.9, 0.5)

            priority.save()

        except ProjectSpiderPriority.DoesNotExist:
            pass  # Category not linked to this project


# Singleton instance
_engine_instance = None

def get_spider_priority_engine() -> SpiderPriorityEngine:
    """Get the singleton SpiderPriorityEngine instance."""
    global _engine_instance
    if _engine_instance is None:
        _engine_instance = SpiderPriorityEngine()
    return _engine_instance
