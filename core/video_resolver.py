"""
Unified video resolver — locate any video by UUID, sequential number, or URL.

All videos (generated + uploaded) live in content.VideoHistory.
There is no separate MediaAsset model for videos.
"""

import logging
from dataclasses import dataclass
from typing import Optional

from django.contrib.auth import get_user_model

User = get_user_model()
logger = logging.getLogger(__name__)


@dataclass
class ResolvedVideo:
    source: str  # "video_history"
    id: str
    sequential_number: Optional[int]
    title: str
    url: str
    thumbnail_url: str
    duration: Optional[int]
    width: Optional[int]
    height: Optional[int]
    video_type: str
    source_type: str
    status: str
    created_at: str
    original_filename: str
    file_size_bytes: Optional[int]

    def to_dict(self):
        return {
            'source': self.source,
            'id': self.id,
            'sequential_number': self.sequential_number,
            'title': self.title,
            'url': self.url,
            'thumbnail_url': self.thumbnail_url,
            'duration': self.duration,
            'width': self.width,
            'height': self.height,
            'resolution': f"{self.width}x{self.height}" if self.width else None,
            'video_type': self.video_type,
            'source_type': self.source_type,
            'status': self.status,
            'created_at': self.created_at,
            'original_filename': self.original_filename,
            'file_size_bytes': self.file_size_bytes,
        }


def _video_to_resolved(video) -> ResolvedVideo:
    return ResolvedVideo(
        source='video_history',
        id=str(video.id),
        sequential_number=video.get_sequential_number(),
        title=(video.prompt or video.original_filename or '')[:200],
        url=video.video_url or '',
        thumbnail_url=video.thumbnail_url or '',
        duration=video.duration,
        width=video.video_width,
        height=video.video_height,
        video_type=video.video_type or '',
        source_type=getattr(video, 'source_type', ''),
        status=video.status or '',
        created_at=video.created_at.isoformat() if video.created_at else '',
        original_filename=video.original_filename or '',
        file_size_bytes=video.file_size_bytes,
    )


def resolve_video(ref: dict, user=None) -> Optional[ResolvedVideo]:
    """
    Resolve a video reference to a normalized ResolvedVideo.

    ref supports:
      - {"id": "uuid"}                    — lookup by VideoHistory UUID
      - {"sequential_number": 42}          — lookup by user-scoped sequential number
      - {"url": "https://...mp4"}          — lookup by video_url
      - {"id": "uuid", "source": "video_history"} — explicit source (future-proof)

    user: required for sequential_number lookup (scoped per user).
    """
    from content.models import VideoHistory

    qs = VideoHistory.objects.all()
    if user:
        qs = qs.filter(user=user)

    # By UUID
    video_id = ref.get('id')
    if video_id:
        video = qs.filter(id=video_id).first()
        if video:
            return _video_to_resolved(video)
        return None

    # By sequential number
    seq = ref.get('sequential_number')
    if seq is not None:
        if not user:
            logger.warning("sequential_number lookup requires a user")
            return None
        # Sequential number is computed: count of earlier videos + 1
        # So video #N is the Nth video by created_at ascending
        try:
            video = qs.order_by('created_at')[int(seq) - 1]
            return _video_to_resolved(video)
        except (IndexError, ValueError):
            return None

    # By URL
    url = ref.get('url')
    if url:
        video = qs.filter(video_url=url).first()
        if video:
            return _video_to_resolved(video)
        return None

    return None
