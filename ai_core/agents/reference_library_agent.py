"""
ReferenceLibraryAgent - Curated Reference Image Management

Philosophy: Save references → Match style → Consistent results

This agent manages a library of reference images for style matching using
image-to-image generation. Much faster than training, perfect for quick consistency.

Session 90 - The Perfect Workflow: Reference-Based Consistency
"""

import uuid
from typing import Dict, List, Optional
from datetime import datetime

from django.contrib.auth.models import User
from django.utils import timezone

from content.models import ImageHistory
from ai_core.agents.agent_memory_interface import AgentMemoryInterface


class ReferenceImage:
    """In-memory representation of a reference image."""

    def __init__(
        self,
        reference_id: str,
        user_id: int,
        name: str,
        image_url: str,
        tags: List[str],
        notes: str = "",
        source_image_id: Optional[int] = None,
        created_at: datetime = None
    ):
        self.reference_id = reference_id
        self.user_id = user_id
        self.name = name
        self.image_url = image_url
        self.tags = tags
        self.notes = notes
        self.source_image_id = source_image_id
        self.created_at = created_at or timezone.now()

    def to_dict(self) -> Dict:
        return {
            'reference_id': self.reference_id,
            'user_id': self.user_id,
            'name': self.name,
            'image_url': self.image_url,
            'tags': self.tags,
            'notes': self.notes,
            'source_image_id': self.source_image_id,
            'created_at': self.created_at.isoformat()
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'ReferenceImage':
        data['created_at'] = datetime.fromisoformat(data['created_at'])
        return cls(**data)


class ReferenceLibraryAgent:
    """
    Manages reference images for style matching.

    Use cases:
    - Save approved image as reference
    - Generate "like this reference"
    - Organize references by tags (logo, video-style, color-palette)
    - Quick consistency without training

    Faster than brand training, perfect for:
    - Quick projects
    - Testing styles
    - Multiple concurrent brands
    """

    def __init__(self, user: User, session_id: Optional[str] = None):
        self.user = user
        self.session_id = session_id or f"reference_lib_{user.id}_{uuid.uuid4().hex[:8]}"

        self.memory = AgentMemoryInterface(
            agent_name="ReferenceLibraryAgent",
            user_id=user.id,
            agent_id=self.session_id,
            redis_db=3
        )

        self.memory.log_agent_action(
            action="agent_initialized",
            details={"user_id": user.id}
        )

    def add_reference(
        self,
        name: str,
        image_id: int,
        tags: List[str],
        notes: str = ""
    ) -> Dict:
        """
        Add image to reference library.

        Args:
            name: User-friendly name
            image_id: ImageHistory ID
            tags: Tags for organization
            notes: Optional notes

        Returns:
            Dict with reference info
        """
        try:
            image = ImageHistory.objects.get(id=image_id, user=self.user)

            reference_id = f"ref_{uuid.uuid4().hex[:12]}"

            reference = ReferenceImage(
                reference_id=reference_id,
                user_id=self.user.id,
                name=name,
                image_url=image.image_url,
                tags=tags,
                notes=notes,
                source_image_id=image_id
            )

            # Store in Redis
            ref_key = f"reference_library:user_{self.user.id}:refs:{reference_id}"
            self.memory.redis.set(ref_key, str(reference.to_dict()))

            # Add to library list
            list_key = f"reference_library:user_{self.user.id}:ref_list"
            self.memory.redis.sadd(list_key, reference_id)

            # Add to tag indexes
            for tag in tags:
                tag_key = f"reference_library:user_{self.user.id}:tag:{tag}"
                self.memory.redis.sadd(tag_key, reference_id)

            self.memory.log_agent_action(
                action="reference_added",
                details={
                    'reference_id': reference_id,
                    'name': name,
                    'tags': tags
                }
            )

            return {
                'success': True,
                'reference_id': reference_id,
                'name': name,
                'message': f'✅ Reference "{name}" added to library!'
            }

        except ImageHistory.DoesNotExist:
            return {'success': False, 'error': 'Image not found'}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def get_reference(self, reference_id: str) -> Optional[ReferenceImage]:
        """Get reference by ID."""
        try:
            ref_key = f"reference_library:user_{self.user.id}:refs:{reference_id}"
            ref_data = self.memory.redis.get(ref_key)

            if ref_data:
                import ast
                ref_dict = ast.literal_eval(ref_data.decode('utf-8'))
                return ReferenceImage.from_dict(ref_dict)

            return None

        except Exception as e:
            self.memory.log_agent_action(
                action="get_reference_error",
                details={'reference_id': reference_id, 'error': str(e)}
            )
            return None

    def list_references(self, tags: List[str] = None) -> List[Dict]:
        """
        List references with optional tag filter.

        Args:
            tags: Optional tags to filter by

        Returns:
            List of reference dictionaries
        """
        try:
            if tags:
                # Get intersection of all tag sets
                tag_keys = [f"reference_library:user_{self.user.id}:tag:{tag}" for tag in tags]
                reference_ids = self.memory.redis.sinter(*tag_keys) if tag_keys else set()
            else:
                # Get all references
                list_key = f"reference_library:user_{self.user.id}:ref_list"
                reference_ids = self.memory.redis.smembers(list_key)

            references = []
            for ref_id_bytes in reference_ids:
                ref_id = ref_id_bytes.decode('utf-8')
                ref = self.get_reference(ref_id)
                if ref:
                    references.append(ref.to_dict())

            # Sort by created_at (newest first)
            references.sort(key=lambda r: r['created_at'], reverse=True)

            return references

        except Exception as e:
            self.memory.log_agent_action(
                action="list_references_error",
                details={'error': str(e)}
            )
            return []

    def delete_reference(self, reference_id: str) -> Dict:
        """Delete a reference."""
        try:
            # Get reference to get tags before deleting
            ref = self.get_reference(reference_id)

            if not ref:
                return {'success': False, 'error': 'Reference not found'}

            # Remove from Redis
            ref_key = f"reference_library:user_{self.user.id}:refs:{reference_id}"
            self.memory.redis.delete(ref_key)

            # Remove from list
            list_key = f"reference_library:user_{self.user.id}:ref_list"
            self.memory.redis.srem(list_key, reference_id)

            # Remove from tag indexes
            for tag in ref.tags:
                tag_key = f"reference_library:user_{self.user.id}:tag:{tag}"
                self.memory.redis.srem(tag_key, reference_id)

            self.memory.log_agent_action(
                action="reference_deleted",
                details={'reference_id': reference_id}
            )

            return {
                'success': True,
                'message': f'Reference {reference_id} deleted'
            }

        except Exception as e:
            return {'success': False, 'error': str(e)}

    def get_state_summary(self) -> Dict:
        """Get agent state summary."""
        references = self.list_references()

        # Get unique tags
        all_tags = set()
        for ref in references:
            all_tags.update(ref['tags'])

        return {
            'agent_name': 'ReferenceLibraryAgent',
            'session_id': self.session_id,
            'user_id': self.user.id,
            'total_references': len(references),
            'unique_tags': sorted(list(all_tags))
        }
