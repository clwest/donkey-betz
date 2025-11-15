"""
Data models for Render Node

Session 103 - Resolve Render Node Service
"""

import uuid
from datetime import datetime
from enum import Enum
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field, asdict


class JobStatus(str, Enum):
    """Render job status"""
    QUEUED = "queued"
    RENDERING = "rendering"
    DONE = "done"
    ERROR = "error"
    UPLOADING = "uploading"
    UPLOADED = "uploaded"


@dataclass
class RenderJob:
    """Render job model"""

    job_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timeline_name: Optional[str] = None
    clip_paths: List[str] = field(default_factory=list)
    template: str = "default_mp4"
    webhook_url: Optional[str] = None

    # Status tracking
    status: JobStatus = JobStatus.QUEUED
    progress: float = 0.0

    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    # Results
    output_file: Optional[str] = None
    error_message: Optional[str] = None

    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        data = asdict(self)
        # Convert datetime objects to ISO format
        data['created_at'] = self.created_at.isoformat() if self.created_at else None
        data['started_at'] = self.started_at.isoformat() if self.started_at else None
        data['completed_at'] = self.completed_at.isoformat() if self.completed_at else None
        # Convert enum to string
        data['status'] = self.status.value
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'RenderJob':
        """Create from dictionary"""
        # Convert ISO strings back to datetime
        if 'created_at' in data and isinstance(data['created_at'], str):
            data['created_at'] = datetime.fromisoformat(data['created_at'])
        if 'started_at' in data and isinstance(data['started_at'], str):
            data['started_at'] = datetime.fromisoformat(data['started_at'])
        if 'completed_at' in data and isinstance(data['completed_at'], str):
            data['completed_at'] = datetime.fromisoformat(data['completed_at'])
        # Convert string to enum
        if 'status' in data and isinstance(data['status'], str):
            data['status'] = JobStatus(data['status'])
        return cls(**data)
