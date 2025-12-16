"""
User models package - User management and profile models

This package contains all models related to user management,
profiles, preferences, statistics, and embeddings.
"""

from .models import (
    UserProfile, UserPreferences, UserStatistics,
    ExtendedUserProfile, EnhancedUserProfile, UserEmbedding,
    UserPreference,  # Session 309: Key-value preference store
    UserCertification,  # Session 457: Certificate file uploads
)

__all__ = [
    'UserProfile',
    'UserPreferences',
    'UserStatistics',
    'ExtendedUserProfile',
    'EnhancedUserProfile',
    'UserEmbedding',
    'UserPreference',  # Session 309
    'UserCertification',  # Session 457
]