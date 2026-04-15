"""
Living Project Service
Session 335: The Brain of the Living Project System

This service connects the autonomous agent ecosystem to user projects.
It watches for relevant data and surfaces insights automatically.

The key insight: Projects SUBSCRIBE to the learning ecosystem.
When something relevant happens (spider data, agent conversation, decision),
the project gets notified.

Flow:
1. Spider collects data → check if relevant to any project → create insight
2. Agents have conversation → check if relevant to any project → create insight
3. Decision becomes canonical → check if relevant to any project → create insight
"""

import logging
import re
from typing import List, Dict, Set

from django.core.exceptions import ObjectDoesNotExist

logger = logging.getLogger(__name__)


class LivingProjectService:
    """
    Service for managing living projects and their insights.

    Responsibilities:
    1. Match incoming data to relevant projects
    2. Score relevance and confidence
    3. Create insights for projects
    4. Learn from user feedback
    """

    def __init__(self):
        self.keyword_cache = {}  # Cache project keywords for performance

    # =========================================================================
    # TOPIC MATCHING
    # =========================================================================

    def get_project_topics(self, project) -> Set[str]:
        """
        Extract all topics/keywords a project cares about.

        Sources:
        - project.tags
        - project.metadata.get('research_articles') titles
        - project.metadata.get('company_info')
        - LivingProjectConfig watch_* fields
        """
        topics = set()

        # From tags
        if project.tags:
            for tag in project.tags:
                topics.add(tag.lower().strip())

        # From category
        if project.category:
            topics.add(project.category.lower().strip())

        # From project name (extract keywords)
        name_words = re.findall(r'\b\w{3,}\b', project.project_name.lower())
        topics.update(name_words)

        # From metadata
        if project.metadata:
            # Company info
            company_info = project.metadata.get('company_info', {})
            if company_info.get('name'):
                topics.add(company_info['name'].lower())
            if company_info.get('target_market'):
                topics.add(company_info['target_market'].lower())

            # Research context
            if project.metadata.get('research_type'):
                topics.add(project.metadata['research_type'].lower())

        # From living config if exists.
        # Session 1103c: was 'except Exception: pass # No config yet'
        # which silently dropped project topic/keyword/competitor
        # context whenever the living_config relation raised for any
        # reason — including DB hiccups or schema drift, not just the
        # intended "config doesn't exist yet" case. Project agents
        # would then run with empty watch lists and look like they
        # were deliberately tracking nothing.
        try:
            config = project.living_config
            topics.update([t.lower() for t in config.watch_topics])
            topics.update([k.lower() for k in config.watch_keywords])
            topics.update([c.lower() for c in config.watch_competitors])
        except (AttributeError, ObjectDoesNotExist):
            pass  # Genuine "no config yet" — silent skip is correct
        except Exception as e:
            logger.warning(
                "living_project_service: living_config lookup failed "
                "for project %s (%s: %s) — watch topics/keywords/"
                "competitors will be empty for this project",
                getattr(project, 'id', '<unknown>'),
                type(e).__name__, e,
            )

        # Filter out common words
        stop_words = {'the', 'and', 'for', 'with', 'this', 'that', 'from', 'project'}
        topics = topics - stop_words

        return topics

    def calculate_relevance(
        self,
        content: str,
        project_topics: Set[str],
        title: str = ""
    ) -> tuple[float, List[str]]:
        """
        Calculate how relevant content is to a project's topics.

        Returns:
            (relevance_score, matched_topics)
        """
        content_lower = content.lower()
        title_lower = title.lower()

        matched = []

        for topic in project_topics:
            # Check if topic appears in content or title
            if topic in content_lower or topic in title_lower:
                matched.append(topic)

        if not matched:
            return 0.0, []

        # Score based on matches
        # More matches = higher relevance, but with diminishing returns
        score = min(1.0, len(matched) * 0.2 + 0.3)  # Base 0.3, +0.2 per match, max 1.0

        # Boost for title matches
        title_matches = sum(1 for t in matched if t in title_lower)
        if title_matches > 0:
            score = min(1.0, score + 0.2)

        return score, matched

    # =========================================================================
    # SPIDER DATA → INSIGHTS
    # =========================================================================

    def process_spider_data(self, spider_data) -> List[Dict]:
        """
        Process new spider data and create insights for matching projects.

        Called when spider data is collected (from Celery task or signal).

        Returns list of created insights.
        """
        from core.models_unified_system import ProjectInsight
        from core.models_partnership import PartnershipProject

        created_insights = []

        # Get active living projects
        active_projects = PartnershipProject.objects.filter(
            living_config__is_active=True
        ).select_related('living_config')

        # Also check projects without config (default active)
        projects_without_config = PartnershipProject.objects.filter(
            living_config__isnull=True,
            status__in=['planning', 'in_progress']
        )

        all_projects = list(active_projects) + list(projects_without_config)

        # Extract content from spider data
        title = ""
        content = ""

        raw_data = spider_data.raw_data or {}
        if isinstance(raw_data, dict):
            title = raw_data.get('title', '') or raw_data.get('name', '')
            content = raw_data.get('content', '') or raw_data.get('description', '') or raw_data.get('summary', '')

            # Also check items array
            items = raw_data.get('items', [])
            if items and isinstance(items, list):
                for item in items[:5]:  # First 5 items
                    if isinstance(item, dict):
                        content += " " + (item.get('title', '') or '')
                        content += " " + (item.get('content', '') or '')

        full_text = f"{title} {content}"

        if len(full_text.strip()) < 20:
            return []  # Not enough content to match

        # Check each project
        for project in all_projects:
            topics = self.get_project_topics(project)
            if not topics:
                continue

            relevance, matched = self.calculate_relevance(full_text, topics, title)

            # Check threshold.
            # Session 1083 (Rigby audit): was `except Exception: pass`, which
            # silently reverted to the 0.6 default whenever project.living_config
            # was missing, the related table hit an error, or the attribute
            # resolved to an unexpected type. Since this threshold gates whether
            # spider data becomes a ProjectInsight at all, a bad fallback here
            # means some projects silently lose their insight feed while
            # the service logs zero warnings. Narrow to the expected
            # "config simply not present" case and log anything else.
            min_relevance = 0.6
            try:
                min_relevance = project.living_config.min_relevance_score
            except (AttributeError, ObjectDoesNotExist):
                pass  # No living_config configured — use default
            except Exception as e:
                logger.warning(
                    "living_project_service: failed to read min_relevance_score "
                    "for project %s (%s: %s) — falling back to 0.6",
                    getattr(project, 'id', 'unknown'),
                    type(e).__name__, e,
                )

            if relevance >= min_relevance:
                # Create insight
                insight = ProjectInsight.objects.create(
                    project=project,
                    insight_type='spider_data',
                    title=title[:300] if title else f"New data from {spider_data.spider_name}",
                    summary=content[:500] if content else "New relevant data collected",
                    details={
                        'spider_name': spider_data.spider_name,
                        'source_url': spider_data.source_url,
                        'data_type': spider_data.data_type,
                        'raw_data': raw_data,
                    },
                    source_type='spider',
                    source_id=spider_data.id,
                    source_name=spider_data.spider_name,
                    relevance_score=relevance,
                    confidence_score=0.7,  # Spider data is fairly reliable
                    matched_topics=matched,
                )

                created_insights.append({
                    'project': project.project_name,
                    'insight_id': str(insight.id),
                    'relevance': relevance,
                    'matched_topics': matched,
                })

                logger.info(
                    f"📡 [LIVING PROJECT] Created insight for '{project.project_name}' "
                    f"from spider '{spider_data.spider_name}' (relevance: {relevance:.2f})"
                )

        return created_insights

    # =========================================================================
    # AGENT CONVERSATIONS → INSIGHTS
    # =========================================================================

    def process_agent_conversation(self, conversation) -> List[Dict]:
        """
        Process agent conversation and create insights for matching projects.

        Called when a conversation concludes.
        """
        from core.models_unified_system import ProjectInsight
        from core.models_partnership import PartnershipProject

        created_insights = []

        # Skip if conversation already linked to a project
        if conversation.project_id:
            return []

        # Get conversation content
        topic = getattr(conversation, 'topic', '') or ''
        conclusion = getattr(conversation, 'conclusion', '') or ''
        insights_generated = getattr(conversation, 'insights_generated', []) or []

        full_text = f"{topic} {conclusion} {' '.join(str(i) for i in insights_generated)}"

        if len(full_text.strip()) < 30:
            return []

        # Get active projects
        active_projects = PartnershipProject.objects.filter(
            status__in=['planning', 'in_progress']
        )

        for project in active_projects:
            topics = self.get_project_topics(project)
            if not topics:
                continue

            relevance, matched = self.calculate_relevance(full_text, topics, topic)

            if relevance >= 0.5:  # Slightly lower threshold for agent insights
                # Get participants
                participants = []
                try:
                    participants = list(conversation.participants.values_list('name', flat=True))
                except Exception:
                    pass

                insight = ProjectInsight.objects.create(
                    project=project,
                    insight_type='agent_insight',
                    title=f"Agent Discussion: {topic[:100]}..." if topic else "Agent Insight",
                    summary=conclusion[:500] if conclusion else topic[:500],
                    details={
                        'topic': topic,
                        'conclusion': conclusion,
                        'insights': insights_generated,
                        'participants': participants,
                        'conversation_type': getattr(conversation, 'conversation_type', 'unknown'),
                    },
                    source_type='agent_conversation',
                    source_id=conversation.id,
                    source_name=f"Conversation: {', '.join(participants[:3])}",
                    relevance_score=relevance,
                    confidence_score=0.6,
                    matched_topics=matched,
                )

                created_insights.append({
                    'project': project.project_name,
                    'insight_id': str(insight.id),
                    'relevance': relevance,
                })

                logger.info(
                    f"💬 [LIVING PROJECT] Created insight for '{project.project_name}' "
                    f"from agent conversation (relevance: {relevance:.2f})"
                )

        return created_insights

    # =========================================================================
    # CANONICAL DECISIONS → INSIGHTS
    # =========================================================================

    def process_canonical_decision(self, decision) -> List[Dict]:
        """
        Process canonical decision and notify relevant projects.

        When a decision becomes canonical, all projects that could benefit
        should be notified.
        """
        from core.models_unified_system import ProjectInsight
        from core.models_partnership import PartnershipProject

        created_insights = []

        # Get decision content
        topic = decision.topic or ''
        stance = decision.recommended_stance or ''
        rationale = decision.rationale or ''
        impact_area = decision.impact_area or ''

        full_text = f"{topic} {stance} {rationale} {impact_area}"

        # Get active projects
        active_projects = PartnershipProject.objects.filter(
            status__in=['planning', 'in_progress']
        )

        for project in active_projects:
            topics = self.get_project_topics(project)
            if not topics:
                continue

            relevance, matched = self.calculate_relevance(full_text, topics, topic)

            # Also check impact area match
            if impact_area.lower() in topics:
                relevance = min(1.0, relevance + 0.3)
                matched.append(impact_area.lower())

            if relevance >= 0.5:
                insight = ProjectInsight.objects.create(
                    project=project,
                    insight_type='decision',
                    title=f"Policy: {stance[:100]}..." if stance else f"Decision: {topic[:100]}",
                    summary=stance[:500] if stance else topic[:500],
                    details={
                        'topic': topic,
                        'recommended_stance': stance,
                        'rationale': rationale,
                        'decision_type': decision.decision_type,
                        'impact_area': impact_area,
                    },
                    source_type='agent_decision',
                    source_id=decision.id,
                    source_name=f"Canonical {decision.decision_type}",
                    relevance_score=relevance,
                    confidence_score=0.9,  # Canonical decisions are high confidence
                    matched_topics=list(set(matched)),
                )

                created_insights.append({
                    'project': project.project_name,
                    'insight_id': str(insight.id),
                    'relevance': relevance,
                })

                logger.info(
                    f"🏛️ [LIVING PROJECT] Created insight for '{project.project_name}' "
                    f"from canonical decision (relevance: {relevance:.2f})"
                )

        return created_insights

    # =========================================================================
    # PROJECT SETUP
    # =========================================================================

    def activate_living_project(self, project) -> 'LivingProjectConfig':
        """
        Activate a project as a living project.

        Creates the config and extracts initial topics from project content.
        """
        from core.models_unified_system import LivingProjectConfig

        # Get or create config
        config, created = LivingProjectConfig.objects.get_or_create(
            project=project,
            defaults={
                'is_active': True,
                'watch_topics': list(self.get_project_topics(project)),
            }
        )

        if not created:
            # Update topics if config already exists
            current_topics = set(config.watch_topics or [])
            new_topics = self.get_project_topics(project)
            config.watch_topics = list(current_topics | new_topics)
            config.is_active = True
            config.save()

        logger.info(f"🟢 [LIVING PROJECT] Activated: {project.project_name}")

        return config

    def get_project_feed(
        self,
        project,
        limit: int = 20,
        status_filter: str = None,
        type_filter: str = None
    ) -> List[Dict]:
        """
        Get the insight feed for a project.

        Returns insights formatted for display.
        """
        from core.models_unified_system import ProjectInsight

        queryset = ProjectInsight.objects.filter(project=project)

        if status_filter:
            queryset = queryset.filter(status=status_filter)

        if type_filter:
            queryset = queryset.filter(insight_type=type_filter)

        insights = queryset.order_by('-is_pinned', '-created_at')[:limit]

        return [
            {
                'id': str(insight.id),
                'type': insight.insight_type,
                'title': insight.title,
                'summary': insight.summary,
                'source': insight.source_name,
                'relevance': insight.relevance_score,
                'status': insight.status,
                'is_pinned': insight.is_pinned,
                'matched_topics': insight.matched_topics,
                'created_at': insight.created_at.isoformat(),
                'user_rating': insight.user_rating,
            }
            for insight in insights
        ]

    def get_project_stats(self, project) -> Dict:
        """Get stats for a living project."""
        from core.models_unified_system import ProjectInsight
        from django.db.models import Count, Avg

        insights = ProjectInsight.objects.filter(project=project)

        stats = insights.aggregate(
            total=Count('id'),
            avg_relevance=Avg('relevance_score'),
            avg_rating=Avg('user_rating'),
        )

        by_type = dict(
            insights.values('insight_type')
            .annotate(count=Count('id'))
            .values_list('insight_type', 'count')
        )

        by_status = dict(
            insights.values('status')
            .annotate(count=Count('id'))
            .values_list('status', 'count')
        )

        return {
            'total_insights': stats['total'] or 0,
            'new_insights': by_status.get('new', 0),
            'acted_on': by_status.get('acted_on', 0),
            'avg_relevance': round(stats['avg_relevance'] or 0, 2),
            'avg_rating': round(stats['avg_rating'] or 0, 1),
            'by_type': by_type,
            'by_status': by_status,
        }


# Singleton instance
_living_project_service = None


def get_living_project_service() -> LivingProjectService:
    """Get singleton living project service."""
    global _living_project_service
    if _living_project_service is None:
        _living_project_service = LivingProjectService()
    return _living_project_service
