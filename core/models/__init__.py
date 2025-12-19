"""
Core models package - Domain-driven model architecture

This package organizes models by domain for better maintainability
while preserving backward compatibility.

Domain Structure:
- base/: Foundation models (UnifiedBaseModel, UnifiedUser)
- system/: Platform infrastructure (SystemConfiguration, PlatformMetrics, ErrorPattern, ErrorInstance)
- users/: User management (UserProfile, UserPreferences, UserStatistics, ExtendedUserProfile, EnhancedUserProfile, UserEmbedding)
- jobs/: Career and employment (JobApplication, ResumeVersion)
- conversations/: Chat and memory (ConversationMemory, ChatConversation, UserMemoryContext)
- ai_learning/: Agent learning (AgentLearningSession, AgentCollaboration, LearningInsight)
- projects/: Generated content (GeneratedProject, GeneratedCode)
"""

# Import all models from domain packages for backward compatibility
from .base import *
from .system import *
from .users import *
from .jobs import *
from .conversations import *
from .ai_learning import *
from .projects import *

# Import models from the unified system as well
from ..models_unified_system import *

# Import voice marketplace models (Session 440)
from ..models_voice_marketplace import *

# Import content pipeline models (Session 440)
from ..models_content_pipeline import *

# Import AI series models (Session 445)
from ..models_ai_series import *

# Import autonomous content studio models (Session 466)
from ..models_autonomous_studio import *

# Import podcast studio models (Session 496)
from ..models_podcast_studio import *

# Explicitly define what gets imported with "from core.models import *"
__all__ = [
    # Base models
    'UnifiedBaseModel',
    'UnifiedUser',
    'DiscordLinkCode',

    # System models
    'SystemConfiguration',
    'PlatformMetrics',
    'ErrorPattern',
    'ErrorInstance',

    # User models
    'UserProfile',
    'UserPreferences',
    'UserStatistics',
    'ExtendedUserProfile',
    'EnhancedUserProfile',
    'UserEmbedding',
    'UserPreference',  # Session 309: Key-value preference store

    # Job models
    'JobApplication',
    'ResumeVersion',

    # Conversation models
    'ConversationMemory',
    'ChatConversation',
    'UserMemoryContext',

    # AI Learning models
    'AgentLearningSession',
    'AgentCollaboration',
    'LearningInsight',

    # Project models
    'GeneratedProject',
    'GeneratedCode',

    # Unified system models (imported from models_unified_system.py)
    'AgentCategory',
    'Agent',
    'Advisor',
    'AgentAssignment',
    'AgentExecution',
    'Collaboration',
    'Revenue',
    'Opportunity',
    'Application',
    'AgentSolution',
    'AgentLearning',
    'SpiderData',
    'AdvisorInsight',
    'UserAgentLearning',

    # Spider-Agent Connection models (Session 242)
    'SpiderCategory',
    'AgentSpiderConnection',
    'AgentKnowledgeSource',

    # Agent Learning Network models (Session 243)
    'AgentLearningConnection',
    'KnowledgeTransfer',

    # Agent Conversations (Session 244)
    'AgentConversation',
    'ConversationMessage',

    # Agent Dreams (Session 247)
    'AgentDream',

    # Voice Marketplace (Session 440)
    'VoiceProfile',
    'VoiceTransaction',
    'VoiceReview',
    'VoiceCloneRequest',

    # Content Pipeline (Session 440)
    'ContentPackage',
    'ContentAsset',
    'ContentPurchase',
    'ContentShowroom',
    'ContentGenerationJob',

    # AI Series (Session 445)
    'AISeries',
    'SeriesEpisode',
    'SeriesCharacter',
    'SeriesType',
    'SeriesStatus',
    'EpisodeStatus',

    # Podcast Studio (Session 496)
    'PodcastShow',
    'PodcastEpisode',
    'PodcastDebate',
    'PodcastParticipant',
]