"""
Learning Companion Service - Session 266

This service manages the Learning Companion functionality:
1. Charter persistence - Save and load the user's learning companion charter
2. Track-based context - Load relevant spider categories for active tracks
3. Progress tracking - Remember covered trends and actions

Integrates with:
- Memory Palace (AgentMemory) for semantic storage
- Spider Network for track-specific data
- Context Aggregator for enriched prompts
"""

import logging
from typing import Dict, Any, List, Optional

from django.utils import timezone
from django.core.cache import cache

logger = logging.getLogger(__name__)


class LearningCompanionService:
    """
    Service for managing Learning Companion state and context.

    Provides:
    - Charter management
    - Track-based spider filtering
    - Progress tracking
    - Context injection for prompts
    """

    # Cache keys
    CACHE_PREFIX = "learning_companion"
    CACHE_TTL = 3600  # 1 hour

    def __init__(self, user=None):
        self.user = user
        self._companion = None

    @property
    def companion(self):
        """Lazy load the LearningCompanion model."""
        if self._companion is None and self.user:
            try:
                from core.models_unified_system import LearningCompanion
                self._companion, created = LearningCompanion.objects.get_or_create(
                    user=self.user
                )
                if created:
                    logger.info(f"📚 Created new Learning Companion for {self.user.username}")
            except Exception as e:
                logger.warning(f"Could not load Learning Companion: {e}")
        return self._companion

    # =========================================================================
    # CHARTER MANAGEMENT
    # =========================================================================

    def set_charter(self, charter_text: str) -> bool:
        """
        Set the user's Learning Companion charter.

        Also creates an AgentMemory entry for semantic retrieval.
        """
        if not self.companion:
            return False

        try:
            # Save to the companion model
            self.companion.set_charter(charter_text)

            # Also save as an AgentMemory for semantic search
            self._save_charter_to_memory(charter_text)

            # Clear cache
            cache.delete(f"{self.CACHE_PREFIX}:{self.user.id}:charter")

            logger.info(f"📜 Learning Companion charter set for {self.user.username}")
            return True
        except Exception as e:
            logger.error(f"Failed to set charter: {e}")
            return False

    def get_charter(self) -> Optional[str]:
        """Get the user's Learning Companion charter."""
        if not self.companion:
            return None
        return self.companion.charter or None

    def _save_charter_to_memory(self, charter_text: str) -> None:
        """Save charter to AgentMemory for semantic retrieval."""
        try:
            from core.models_unified_system import AgentMemory, Agent

            # Get or create a "LearningCompanion" agent
            learning_agent, _ = Agent.objects.get_or_create(
                name="LearningCompanion",
                defaults={
                    'description': "Personal learning companion that curates knowledge",
                    'agent_type': 'support',
                    'is_active': True,
                }
            )

            # Create/update the charter memory
            AgentMemory.objects.update_or_create(
                agent=learning_agent,
                source_type='charter',
                source_id=str(self.user.id),
                defaults={
                    'title': f"Learning Charter for {self.user.username}",
                    'content': charter_text,
                    'context': f"User's personal charter defining their ideal learning companion",
                    'memory_type': 'preference',
                    'valence': 'positive',
                    'importance_score': 0.9,
                }
            )
            logger.info(f"📝 Charter saved to Memory Palace")
        except Exception as e:
            logger.warning(f"Could not save charter to memory: {e}")

    # =========================================================================
    # TRACK MANAGEMENT
    # =========================================================================

    def set_active_track(self, track: str) -> bool:
        """Set the user's active learning track."""
        if not self.companion:
            return False

        try:
            self.companion.active_track = track
            self.companion.save(update_fields=['active_track', 'updated_at'])

            # Clear relevant caches
            cache.delete(f"{self.CACHE_PREFIX}:{self.user.id}:track_spiders")

            logger.info(f"📚 Active track set to '{track}' for {self.user.username}")
            return True
        except Exception as e:
            logger.error(f"Failed to set track: {e}")
            return False

    def get_active_track(self) -> str:
        """Get the user's active learning track."""
        if not self.companion:
            return 'tech_trends'
        return self.companion.active_track

    def get_spiders_for_current_track(self) -> List[str]:
        """
        Get spider categories relevant to the current track.

        Returns a list of spider category names, ordered by relevance.
        """
        cache_key = f"{self.CACHE_PREFIX}:{self.user.id}:track_spiders"
        cached = cache.get(cache_key)
        if cached:
            return cached

        track = self.get_active_track()

        try:
            from core.models_unified_system import TrackSpiderMapping
            spiders = TrackSpiderMapping.get_spiders_for_track(track)

            if not spiders:
                # Seed defaults if none exist
                TrackSpiderMapping.seed_default_mappings()
                spiders = TrackSpiderMapping.get_spiders_for_track(track)

            cache.set(cache_key, spiders, self.CACHE_TTL)
            return spiders
        except Exception as e:
            logger.warning(f"Could not get track spiders: {e}")
            return []

    def get_track_context_for_prompt(self) -> Dict[str, Any]:
        """
        Get track-specific context to inject into prompts.

        Returns a dict with track info and relevant spider categories.
        """
        track = self.get_active_track()
        spiders = self.get_spiders_for_current_track()
        charter = self.get_charter()

        track_labels = {
            'tech_trends': 'Tech Trends → Shippable Experiments',
            'ai_design': 'AI + Design for Branding',
            'agentic_ai': 'Agentic AI Systems',
            'creative_ops': 'Creative Operations',
            'custom': 'Custom Track',
        }

        return {
            'track': track,
            'track_label': track_labels.get(track, track),
            'relevant_spiders': spiders,
            'charter': charter,
            'has_charter': bool(charter),
        }

    # =========================================================================
    # PROGRESS TRACKING
    # =========================================================================

    def record_topic_covered(
        self,
        topic: str,
        trend_category: str = '',
        content_summary: str = '',
        action_suggested: str = '',
        spider_categories: List[str] = None,
        project_id: str = None
    ) -> Optional[str]:
        """
        Record that a topic was covered in a learning session.

        Returns the progress entry ID.
        """
        if not self.companion:
            return None

        try:
            from core.models_unified_system import LearningProgress

            progress = LearningProgress.objects.create(
                companion=self.companion,
                topic=topic,
                trend_category=trend_category,
                content_summary=content_summary,
                action_suggested=action_suggested,
                spider_categories_used=spider_categories or [],
                related_project_id=project_id,
                status='introduced',
            )

            # Update companion state
            self.companion.current_topic = topic
            self.companion.start_session()

            logger.info(f"📊 Recorded progress: {topic}")
            return str(progress.id)
        except Exception as e:
            logger.error(f"Failed to record progress: {e}")
            return None

    def get_covered_topics(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recently covered topics."""
        if not self.companion:
            return []

        try:
            from core.models_unified_system import LearningProgress

            entries = LearningProgress.objects.filter(
                companion=self.companion
            ).order_by('-started_at')[:limit]

            return [
                {
                    'topic': e.topic,
                    'status': e.status,
                    'trend_category': e.trend_category,
                    'action_completed': e.action_completed,
                    'started_at': e.started_at.isoformat(),
                }
                for e in entries
            ]
        except Exception as e:
            logger.warning(f"Could not get covered topics: {e}")
            return []

    def get_uncompleted_actions(self) -> List[Dict[str, Any]]:
        """Get suggested actions that haven't been completed."""
        if not self.companion:
            return []

        try:
            from core.models_unified_system import LearningProgress

            entries = LearningProgress.objects.filter(
                companion=self.companion,
                action_suggested__isnull=False,
                action_completed=False
            ).exclude(action_suggested='').order_by('-started_at')[:5]

            return [
                {
                    'topic': e.topic,
                    'action': e.action_suggested,
                    'started_at': e.started_at.isoformat(),
                }
                for e in entries
            ]
        except Exception as e:
            logger.warning(f"Could not get uncompleted actions: {e}")
            return []

    def mark_action_completed(self, topic: str, result: str = '') -> bool:
        """Mark an action as completed."""
        if not self.companion:
            return False

        try:
            from core.models_unified_system import LearningProgress

            progress = LearningProgress.objects.filter(
                companion=self.companion,
                topic=topic,
                action_completed=False
            ).order_by('-started_at').first()

            if progress:
                progress.action_completed = True
                progress.action_result = result
                progress.completed_at = timezone.now()
                progress.save()

                logger.info(f"✅ Action completed: {topic}")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to mark action completed: {e}")
            return False

    def get_learning_summary(self) -> Dict[str, Any]:
        """Get a summary of learning progress."""
        if not self.companion:
            return {}

        try:
            from core.models_unified_system import LearningProgress

            total = LearningProgress.objects.filter(companion=self.companion).count()
            completed = LearningProgress.objects.filter(
                companion=self.companion,
                action_completed=True
            ).count()

            by_status = {}
            for status_code, status_label in LearningProgress.STATUS_CHOICES:
                count = LearningProgress.objects.filter(
                    companion=self.companion,
                    status=status_code
                ).count()
                by_status[status_code] = count

            return {
                'total_topics': total,
                'actions_completed': completed,
                'completion_rate': (completed / total * 100) if total > 0 else 0,
                'by_status': by_status,
                'active_track': self.get_active_track(),
                'has_charter': bool(self.get_charter()),
                'total_sessions': self.companion.total_sessions,
            }
        except Exception as e:
            logger.warning(f"Could not get learning summary: {e}")
            return {}

    # =========================================================================
    # CONTEXT FOR PROMPTS
    # =========================================================================

    def get_learning_context_for_prompt(self) -> str:
        """
        Build a context section for injection into GPT prompts.

        This provides the LLM with:
        - The user's charter
        - Active track
        - Recently covered topics
        - Pending actions
        """
        parts = []

        # Charter
        charter = self.get_charter()
        if charter:
            parts.append(f"📜 LEARNING COMPANION CHARTER:\n\"{charter}\"")

        # Active track
        track_context = self.get_track_context_for_prompt()
        parts.append(f"\n📚 ACTIVE LEARNING TRACK: {track_context['track_label']}")

        if track_context['relevant_spiders']:
            spiders = ', '.join(track_context['relevant_spiders'][:5])
            parts.append(f"🕷️ Relevant data sources: {spiders}")

        # Recent topics
        recent = self.get_covered_topics(limit=5)
        if recent:
            topic_list = ', '.join([t['topic'] for t in recent])
            parts.append(f"\n📊 RECENTLY COVERED: {topic_list}")

        # Pending actions
        pending = self.get_uncompleted_actions()
        if pending:
            parts.append("\n⏳ PENDING ACTIONS:")
            for p in pending[:3]:
                parts.append(f"  - {p['action']} (from: {p['topic']})")

        if parts:
            return "\n--- LEARNING COMPANION CONTEXT ---\n" + "\n".join(parts) + "\n--- END LEARNING COMPANION ---\n"

        return ""


# Singleton accessor
_learning_companion_service = {}

def get_learning_companion_service(user=None) -> LearningCompanionService:
    """Get the Learning Companion service for a user."""
    if user is None:
        return LearningCompanionService()

    user_id = user.id if hasattr(user, 'id') else user
    if user_id not in _learning_companion_service:
        _learning_companion_service[user_id] = LearningCompanionService(user)
    return _learning_companion_service[user_id]
