"""
Job models package - Career and employment models

This package contains models related to job applications,
resume management, and career tracking.
"""

from .models import JobApplication, ResumeVersion

__all__ = [
    'JobApplication',
    'ResumeVersion',
]