"""
VersionControlAgent - Complete Generation History Tracking

Philosophy: Track everything → Learn from history → Never lose perfect results

This agent maintains complete version control for all creative generations,
enabling rollback, comparison, and learning from what worked.

Session 90 - The Perfect Workflow: Version Control System
"""

import uuid
from typing import Dict, List, Optional
from datetime import datetime

from django.contrib.auth.models import User
from django.db import transaction
from django.utils import timezone

from content.models import ImageHistory
from ai_core.agents.agent_memory_interface import AgentMemoryInterface


class GenerationVersion:
    """
    In-memory representation of a generation version.

    Tracks a single generation with all its parameters and relationships.
    """

    def __init__(
        self,
        version_id: str,
        user_id: int,
        image_id: int,
        version_number: int,
        # Generation parameters
        prompt: str,
        model: str,
        style: Optional[str],
        seed: int,
        width: int,
        height: int,
        image_url: str,
        # Relationships
        parent_version_id: Optional[str] = None,
        project_id: Optional[str] = None,
        # User feedback
        rating: Optional[int] = None,  # 1-5 stars
        notes: str = "",
        was_used_for_template: bool = False,
        # Metadata
        created_at: datetime = None
    ):
        self.version_id = version_id
        self.user_id = user_id
        self.image_id = image_id
        self.version_number = version_number
        self.prompt = prompt
        self.model = model
        self.style = style
        self.seed = seed
        self.width = width
        self.height = height
        self.image_url = image_url
        self.parent_version_id = parent_version_id
        self.project_id = project_id
        self.rating = rating
        self.notes = notes
        self.was_used_for_template = was_used_for_template
        self.created_at = created_at or timezone.now()

    def to_dict(self) -> Dict:
        """Convert to dictionary for storage."""
        return {
            'version_id': self.version_id,
            'user_id': self.user_id,
            'image_id': self.image_id,
            'version_number': self.version_number,
            'prompt': self.prompt,
            'model': self.model,
            'style': self.style,
            'seed': self.seed,
            'width': self.width,
            'height': self.height,
            'image_url': self.image_url,
            'parent_version_id': self.parent_version_id,
            'project_id': self.project_id,
            'rating': self.rating,
            'notes': self.notes,
            'was_used_for_template': self.was_used_for_template,
            'created_at': self.created_at.isoformat()
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'GenerationVersion':
        """Create from dictionary."""
        data['created_at'] = datetime.fromisoformat(data['created_at'])
        return cls(**data)


class VersionControlAgent:
    """
    Maintains complete version control for all generations.

    Features:
    - Track every generation with full parameters
    - Build version trees (v1 → v2 → v3)
    - Rate and annotate versions
    - Find "perfect" generations (5-star ratings)
    - Analyze what parameters work best

    This enables:
    - "Show me all 5-star logos I've made"
    - "What settings did I use for that perfect image?"
    - "Generate another like version 7"
    """

    def __init__(self, user: User, session_id: Optional[str] = None):
        """
        Initialize VersionControlAgent.

        Args:
            user: Django user object
            session_id: Optional session identifier
        """
        self.user = user
        self.session_id = session_id or f"version_control_{user.id}_{uuid.uuid4().hex[:8]}"

        # Initialize agent memory interface
        self.memory = AgentMemoryInterface(
            agent_name="VersionControlAgent",
            user_id=user.id,
            agent_id=self.session_id,
            redis_db=3
        )

        # Log initialization
        self.memory.log_agent_action(
            action="agent_initialized",
            details={
                "user_id": user.id,
                "session_id": self.session_id
            }
        )

    def track_generation(
        self,
        image_id: int,
        parent_version_id: Optional[str] = None,
        project_id: Optional[str] = None
    ) -> Dict:
        """
        Track a new generation in version control.

        This should be called for EVERY image generation to maintain
        complete history.

        Args:
            image_id: ID of ImageHistory record to track
            parent_version_id: Optional ID of parent version (for iterations)
            project_id: Optional project this generation belongs to

        Returns:
            Dict with version info
        """
        try:
            # Get the image
            image = ImageHistory.objects.get(id=image_id, user=self.user)

            # Determine version number
            if parent_version_id:
                # This is an iteration - increment parent's version
                parent = self.get_version(parent_version_id)
                version_number = parent.version_number + 1 if parent else 1
            else:
                # This is a new generation - version 1
                version_number = 1

            # Create version ID
            version_id = f"version_{uuid.uuid4().hex[:12]}"

            # Create GenerationVersion
            version = GenerationVersion(
                version_id=version_id,
                user_id=self.user.id,
                image_id=image_id,
                version_number=version_number,
                prompt=image.prompt,
                model=image.model,
                style=image.style,
                seed=image.seed or 0,
                width=image.width,
                height=image.height,
                image_url=image.image_url,
                parent_version_id=parent_version_id,
                project_id=project_id
            )

            # Store in Redis
            version_key = f"version_control:user_{self.user.id}:versions:{version_id}"
            self.memory.redis.set(version_key, str(version.to_dict()))

            # Add to user's version list
            list_key = f"version_control:user_{self.user.id}:version_list"
            self.memory.redis.sadd(list_key, version_id)

            # Add to project's version list if project_id provided
            if project_id:
                project_key = f"version_control:user_{self.user.id}:project_{project_id}:versions"
                self.memory.redis.sadd(project_key, version_id)

            # Log action
            self.memory.log_agent_action(
                action="generation_tracked",
                details={
                    'version_id': version_id,
                    'version_number': version_number,
                    'image_id': image_id,
                    'parent_version_id': parent_version_id,
                    'project_id': project_id
                }
            )

            return {
                'success': True,
                'version_id': version_id,
                'version_number': version_number,
                'message': f'Version {version_number} tracked'
            }

        except ImageHistory.DoesNotExist:
            return {
                'success': False,
                'error': 'Image not found'
            }
        except Exception as e:
            self.memory.log_agent_action(
                action="track_generation_error",
                details={'error': str(e)}
            )
            return {
                'success': False,
                'error': str(e)
            }

    def get_version(self, version_id: str) -> Optional[GenerationVersion]:
        """
        Get a version by ID.

        Args:
            version_id: The version ID

        Returns:
            GenerationVersion object or None
        """
        try:
            version_key = f"version_control:user_{self.user.id}:versions:{version_id}"
            version_data = self.memory.redis.get(version_key)

            if version_data:
                import ast
                version_dict = ast.literal_eval(version_data.decode('utf-8'))
                return GenerationVersion.from_dict(version_dict)

            return None

        except Exception as e:
            self.memory.log_agent_action(
                action="get_version_error",
                details={'version_id': version_id, 'error': str(e)}
            )
            return None

    def rate_version(
        self,
        version_id: str,
        rating: int,
        notes: str = ""
    ) -> Dict:
        """
        Rate a version (1-5 stars) with optional notes.

        This is how we identify "perfect" generations!

        Args:
            version_id: The version to rate
            rating: 1-5 star rating
            notes: Optional notes about why this rating

        Returns:
            Dict with success status
        """
        try:
            version = self.get_version(version_id)

            if not version:
                return {
                    'success': False,
                    'error': f'Version {version_id} not found'
                }

            # Validate rating
            if rating < 1 or rating > 5:
                return {
                    'success': False,
                    'error': 'Rating must be between 1 and 5'
                }

            # Update version
            version.rating = rating
            version.notes = notes

            # Save back to Redis
            version_key = f"version_control:user_{self.user.id}:versions:{version_id}"
            self.memory.redis.set(version_key, str(version.to_dict()))

            # Add to rated versions set
            if rating == 5:
                perfect_key = f"version_control:user_{self.user.id}:perfect_versions"
                self.memory.redis.sadd(perfect_key, version_id)

            self.memory.log_agent_action(
                action="version_rated",
                details={
                    'version_id': version_id,
                    'rating': rating,
                    'is_perfect': rating == 5
                }
            )

            return {
                'success': True,
                'version_id': version_id,
                'rating': rating,
                'message': f'Version rated {rating} stars' + (' - Marked as perfect!' if rating == 5 else '')
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def get_perfect_versions(self) -> List[Dict]:
        """
        Get all 5-star rated versions for this user.

        This returns the user's "best of the best" generations!

        Returns:
            List of 5-star version dictionaries
        """
        try:
            perfect_key = f"version_control:user_{self.user.id}:perfect_versions"
            version_ids = self.memory.redis.smembers(perfect_key)

            versions = []
            for version_id_bytes in version_ids:
                version_id = version_id_bytes.decode('utf-8')
                version = self.get_version(version_id)
                if version:
                    versions.append(version.to_dict())

            # Sort by created_at (newest first)
            versions.sort(key=lambda v: v['created_at'], reverse=True)

            return versions

        except Exception as e:
            self.memory.log_agent_action(
                action="get_perfect_versions_error",
                details={'error': str(e)}
            )
            return []

    def get_version_tree(self, version_id: str) -> Dict:
        """
        Get complete version tree for a version (parent → children).

        Shows the entire evolution of a generation.

        Args:
            version_id: Starting version ID

        Returns:
            Dict with version tree structure
        """
        try:
            version = self.get_version(version_id)

            if not version:
                return {
                    'success': False,
                    'error': f'Version {version_id} not found'
                }

            # Build tree by walking up to root, then down
            tree = {
                'root': None,
                'versions': [],
                'current': version_id
            }

            # Walk up to find root
            current = version
            while current.parent_version_id:
                parent = self.get_version(current.parent_version_id)
                if not parent:
                    break
                current = parent

            tree['root'] = current.version_id

            # Walk down from root collecting all versions
            # (This is simplified - a full tree would need recursive traversal)
            tree['versions'].append(current.to_dict())

            return tree

        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def list_versions(
        self,
        project_id: Optional[str] = None,
        min_rating: Optional[int] = None,
        limit: int = 50
    ) -> List[Dict]:
        """
        List versions with optional filters.

        Args:
            project_id: Optional project filter
            min_rating: Optional minimum rating filter
            limit: Maximum number of versions to return

        Returns:
            List of version dictionaries
        """
        try:
            if project_id:
                # Get versions for specific project
                project_key = f"version_control:user_{self.user.id}:project_{project_id}:versions"
                version_ids = self.memory.redis.smembers(project_key)
            else:
                # Get all versions for user
                list_key = f"version_control:user_{self.user.id}:version_list"
                version_ids = self.memory.redis.smembers(list_key)

            versions = []
            for version_id_bytes in version_ids:
                version_id = version_id_bytes.decode('utf-8')
                version = self.get_version(version_id)

                if version:
                    # Apply rating filter
                    if min_rating and (not version.rating or version.rating < min_rating):
                        continue

                    versions.append(version.to_dict())

            # Sort by created_at (newest first)
            versions.sort(key=lambda v: v['created_at'], reverse=True)

            # Apply limit
            versions = versions[:limit]

            self.memory.log_agent_action(
                action="list_versions",
                details={
                    'count': len(versions),
                    'project_id': project_id,
                    'min_rating': min_rating
                }
            )

            return versions

        except Exception as e:
            self.memory.log_agent_action(
                action="list_versions_error",
                details={'error': str(e)}
            )
            return []

    def mark_used_for_template(self, version_id: str) -> Dict:
        """
        Mark a version as having been used to create a template.

        This creates a link between version control and template management.

        Args:
            version_id: The version that was used

        Returns:
            Dict with success status
        """
        try:
            version = self.get_version(version_id)

            if not version:
                return {
                    'success': False,
                    'error': f'Version {version_id} not found'
                }

            version.was_used_for_template = True

            # Save back to Redis
            version_key = f"version_control:user_{self.user.id}:versions:{version_id}"
            self.memory.redis.set(version_key, str(version.to_dict()))

            return {
                'success': True,
                'message': f'Version {version_id} marked as template source'
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def get_state_summary(self) -> Dict:
        """
        Get current state summary of the agent.

        Returns:
            Dict with agent state
        """
        all_versions = self.list_versions()
        perfect_versions = self.get_perfect_versions()

        return {
            'agent_name': 'VersionControlAgent',
            'session_id': self.session_id,
            'user_id': self.user.id,
            'total_versions': len(all_versions),
            'perfect_versions': len(perfect_versions),
            'has_version_history': len(all_versions) > 0
        }
