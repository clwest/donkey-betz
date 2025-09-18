"""
Unified Storage System
Persistent storage across all platform components
"""

import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from django.core.cache import cache
from django.db import models
from django.utils import timezone

logger = logging.getLogger(__name__)


class ComponentState(models.Model):
    """Store component state persistently"""
    component_name = models.CharField(max_length=100)
    user_id = models.CharField(max_length=100, default='default_user')
    state_data = models.JSONField()
    version = models.IntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['component_name', 'user_id']

    def __str__(self):
        return f"{self.component_name} - {self.user_id}"


class UserProfile(models.Model):
    """Unified user profile across all components"""
    user_id = models.CharField(max_length=100, unique=True)
    profile_data = models.JSONField()
    completeness_score = models.FloatField(default=0.0)
    last_activity = models.DateTimeField(auto_now=True)
    sync_version = models.IntegerField(default=1)

    def __str__(self):
        return f"Profile - {self.user_id}"


class ActionHistory(models.Model):
    """Track all user actions across platform"""
    user_id = models.CharField(max_length=100)
    component = models.CharField(max_length=100)
    action_type = models.CharField(max_length=100)
    action_data = models.JSONField()
    result = models.JSONField(null=True, blank=True)
    success = models.BooleanField(default=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.action_type} - {self.component} - {self.user_id}"


class ComponentDataSync(models.Model):
    """Track data synchronization between components"""
    source_component = models.CharField(max_length=100)
    target_component = models.CharField(max_length=100)
    data_type = models.CharField(max_length=100)
    sync_data = models.JSONField()
    sync_status = models.CharField(max_length=50, default='pending')
    sync_timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.source_component} -> {self.target_component} ({self.data_type})"


class UnifiedStorageManager:
    """Manages persistent storage across all platform components"""

    def __init__(self):
        self.cache_timeout = 3600  # 1 hour
        self.component_keys = {
            'personal_assistant': 'pa_state',
            'income_builder': 'ib_state',
            'revenue_dashboard': 'rd_state',
            'neural_orchestra': 'no_state',
            'decision_command': 'dc_state',
            'job_tracker': 'jt_state'
        }

    # =====================
    # Component State Management
    # =====================

    def save_component_state(self, component: str, user_id: str, state_data: Dict[str, Any]) -> bool:
        """Save component state to persistent storage"""
        try:
            # Update database
            component_state, created = ComponentState.objects.update_or_create(
                component_name=component,
                user_id=user_id,
                defaults={
                    'state_data': state_data,
                    'version': models.F('version') + 1
                }
            )

            # Update cache
            cache_key = f"{self.component_keys.get(component, component)}_{user_id}"
            cache.set(cache_key, state_data, self.cache_timeout)

            # Log action
            self.log_action(
                user_id=user_id,
                component=component,
                action_type='state_save',
                action_data={'keys': list(state_data.keys()), 'size': len(str(state_data))}
            )

            logger.info(f"💾 Saved {component} state for user {user_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to save {component} state: {e}")
            return False

    def load_component_state(self, component: str, user_id: str) -> Optional[Dict[str, Any]]:
        """Load component state from storage"""
        try:
            # Try cache first
            cache_key = f"{self.component_keys.get(component, component)}_{user_id}"
            cached_state = cache.get(cache_key)

            if cached_state:
                logger.info(f"📁 Loaded {component} state from cache for user {user_id}")
                return cached_state

            # Load from database
            try:
                component_state = ComponentState.objects.get(
                    component_name=component,
                    user_id=user_id
                )

                # Restore to cache
                cache.set(cache_key, component_state.state_data, self.cache_timeout)

                logger.info(f"📁 Loaded {component} state from database for user {user_id}")
                return component_state.state_data

            except ComponentState.DoesNotExist:
                logger.info(f"📁 No stored state found for {component} - {user_id}")
                return None

        except Exception as e:
            logger.error(f"Failed to load {component} state: {e}")
            return None

    def sync_component_states(self, user_id: str) -> Dict[str, Any]:
        """Sync all component states for a user"""
        try:
            states = {}

            for component in self.component_keys.keys():
                state = self.load_component_state(component, user_id)
                if state:
                    states[component] = state

            logger.info(f"🔄 Synced {len(states)} component states for user {user_id}")
            return states

        except Exception as e:
            logger.error(f"Failed to sync component states: {e}")
            return {}

    # =====================
    # User Profile Management
    # =====================

    def save_user_profile(self, user_id: str, profile_data: Dict[str, Any]) -> bool:
        """Save unified user profile"""
        try:
            # Calculate completeness score
            completeness = self._calculate_profile_completeness(profile_data)

            # Update database
            user_profile, created = UserProfile.objects.update_or_create(
                user_id=user_id,
                defaults={
                    'profile_data': profile_data,
                    'completeness_score': completeness,
                    'sync_version': models.F('sync_version') + 1
                }
            )

            # Update cache
            cache.set(f"profile_{user_id}", profile_data, self.cache_timeout)

            # Sync to all components
            self._sync_profile_to_components(user_id, profile_data)

            # Log action
            self.log_action(
                user_id=user_id,
                component='unified_storage',
                action_type='profile_save',
                action_data={'completeness': completeness, 'fields': list(profile_data.keys())}
            )

            logger.info(f"👤 Saved user profile for {user_id} (completeness: {completeness:.1%})")
            return True

        except Exception as e:
            logger.error(f"Failed to save user profile: {e}")
            return False

    def load_user_profile(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Load unified user profile"""
        try:
            # Try cache first
            cached_profile = cache.get(f"profile_{user_id}")
            if cached_profile:
                return cached_profile

            # Load from database
            try:
                user_profile = UserProfile.objects.get(user_id=user_id)
                cache.set(f"profile_{user_id}", user_profile.profile_data, self.cache_timeout)
                return user_profile.profile_data

            except UserProfile.DoesNotExist:
                return None

        except Exception as e:
            logger.error(f"Failed to load user profile: {e}")
            return None

    def _calculate_profile_completeness(self, profile_data: Dict[str, Any]) -> float:
        """Calculate profile completeness score"""
        required_fields = [
            'full_name', 'skills', 'experience_level', 'desired_salary_min',
            'desired_salary_max', 'location', 'remote_preference'
        ]

        completed = sum(1 for field in required_fields if profile_data.get(field))
        return completed / len(required_fields)

    def _sync_profile_to_components(self, user_id: str, profile_data: Dict[str, Any]):
        """Sync profile changes to all components"""
        for component in self.component_keys.keys():
            try:
                # Create sync record
                ComponentDataSync.objects.create(
                    source_component='unified_storage',
                    target_component=component,
                    data_type='profile_update',
                    sync_data=profile_data,
                    sync_status='pending'
                )

                logger.debug(f"📤 Queued profile sync to {component}")

            except Exception as e:
                logger.warning(f"Failed to queue profile sync to {component}: {e}")

    # =====================
    # Action Tracking
    # =====================

    def log_action(self, user_id: str, component: str, action_type: str,
                  action_data: Dict[str, Any], result: Dict[str, Any] = None,
                  success: bool = True) -> bool:
        """Log user action"""
        try:
            ActionHistory.objects.create(
                user_id=user_id,
                component=component,
                action_type=action_type,
                action_data=action_data,
                result=result,
                success=success
            )

            # Update cache with recent actions
            cache_key = f"recent_actions_{user_id}"
            recent_actions = cache.get(cache_key, [])

            action_record = {
                'component': component,
                'action_type': action_type,
                'success': success,
                'timestamp': timezone.now().isoformat()
            }

            recent_actions.insert(0, action_record)
            cache.set(cache_key, recent_actions[:50], self.cache_timeout)  # Keep last 50 actions

            return True

        except Exception as e:
            logger.error(f"Failed to log action: {e}")
            return False

    def get_user_actions(self, user_id: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Get user action history"""
        try:
            actions = ActionHistory.objects.filter(user_id=user_id)[:limit]

            return [{
                'component': action.component,
                'action_type': action.action_type,
                'action_data': action.action_data,
                'result': action.result,
                'success': action.success,
                'timestamp': action.timestamp.isoformat()
            } for action in actions]

        except Exception as e:
            logger.error(f"Failed to get user actions: {e}")
            return []

    # =====================
    # Data Synchronization
    # =====================

    def queue_data_sync(self, source: str, target: str, data_type: str, data: Dict[str, Any]) -> bool:
        """Queue data synchronization between components"""
        try:
            ComponentDataSync.objects.create(
                source_component=source,
                target_component=target,
                data_type=data_type,
                sync_data=data,
                sync_status='pending'
            )

            logger.info(f"📤 Queued {data_type} sync: {source} -> {target}")
            return True

        except Exception as e:
            logger.error(f"Failed to queue data sync: {e}")
            return False

    def process_pending_syncs(self) -> int:
        """Process all pending data synchronizations"""
        try:
            pending_syncs = ComponentDataSync.objects.filter(sync_status='pending')
            processed = 0

            for sync in pending_syncs:
                try:
                    # Process the sync (implement specific logic for each data type)
                    self._process_sync(sync)

                    sync.sync_status = 'completed'
                    sync.save()

                    processed += 1

                except Exception as e:
                    logger.error(f"Failed to process sync {sync.id}: {e}")
                    sync.sync_status = 'failed'
                    sync.save()

            logger.info(f"🔄 Processed {processed} data synchronizations")
            return processed

        except Exception as e:
            logger.error(f"Failed to process pending syncs: {e}")
            return 0

    def _process_sync(self, sync: ComponentDataSync):
        """Process a single data synchronization"""
        # This would implement specific sync logic for each data type
        # For now, just update the cache for the target component

        cache_key = f"{self.component_keys.get(sync.target_component, sync.target_component)}_sync"
        cache.set(cache_key, sync.sync_data, self.cache_timeout)

    # =====================
    # Storage Analytics
    # =====================

    def get_storage_metrics(self) -> Dict[str, Any]:
        """Get storage system metrics"""
        try:
            return {
                'total_component_states': ComponentState.objects.count(),
                'total_user_profiles': UserProfile.objects.count(),
                'total_actions': ActionHistory.objects.count(),
                'pending_syncs': ComponentDataSync.objects.filter(sync_status='pending').count(),
                'active_users_today': UserProfile.objects.filter(
                    last_activity__gte=timezone.now() - timedelta(days=1)
                ).count(),
                'cache_status': 'connected' if cache.get('test_key') is None else 'connected'
            }

        except Exception as e:
            logger.error(f"Failed to get storage metrics: {e}")
            return {'error': str(e)}

    def cleanup_old_data(self, days: int = 30) -> Dict[str, int]:
        """Clean up old data"""
        try:
            cutoff_date = timezone.now() - timedelta(days=days)

            # Clean old actions
            old_actions = ActionHistory.objects.filter(timestamp__lt=cutoff_date)
            actions_deleted = old_actions.count()
            old_actions.delete()

            # Clean old syncs
            old_syncs = ComponentDataSync.objects.filter(sync_timestamp__lt=cutoff_date)
            syncs_deleted = old_syncs.count()
            old_syncs.delete()

            logger.info(f"🧹 Cleaned up {actions_deleted} old actions and {syncs_deleted} old syncs")

            return {
                'actions_deleted': actions_deleted,
                'syncs_deleted': syncs_deleted
            }

        except Exception as e:
            logger.error(f"Failed to cleanup old data: {e}")
            return {'error': str(e)}


# Global instance
unified_storage = UnifiedStorageManager()