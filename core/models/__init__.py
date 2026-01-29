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

# Import conversation artifacts (Session 555)
from ..models_conversation_artifacts import *

# Import bankroll tracking (Session 558)
from ..models_bankroll import *

# Import document registry (Session 622)
from ..models_document_registry import *

# Import pilot readiness models (Session 590)
from ..models_pilot_readiness import *

# Import implementation pipeline models (Session 690)
from ..models_implementation_pipeline import *

# Import LLM routing models (Session 697)
from ..models_llm_routing import *

# Import human interface layer models (Session 686)
from ..models_human_interface import *

# Import orchestration layer models (Session 764)
from ..models_orchestration import *

# Import deliverables models (Session 819 - Deliverables Marketplace)
from ..models_deliverables import (
    DeliverableType,
    ContentFormat,
    Deliverable,
    DeliverableExport,
    DeliverableCollection,
)

# Import audit tracking models (Session 819 - Audit Tracking System)
from ..models_audit_tracking import (
    AuditReport,
    AuditFinding,
    AuditRemediationTask,
    AuditVerificationRun,
)

# Import tool call recording models (Session 861 - Tool Call Audit Trail)
from ..models_tool_calls import (
    ToolCallRecord,
    ToolCallAggregate,
)

# Import learning data backup models (Session 861 - Learning Data Persistence)
from ..models_learning_backup import (
    AgentInteractionRecord,
    LearnedPreferenceRecord,
    LearningProgressSnapshot,
    AgentImprovementRecord,
)

# Import decision recording models (Session 861 - Decision Trace Persistence)
from ..models_decision_records import (
    DecisionRecord,
    DecisionAggregate,
)

# Import spider aggregation models (Session 861 - Spider Aggregation Caching)
from ..models_spider_aggregation import (
    SpiderAggregation,
    TrendDataPoint,
)

# Import pipeline feedback model (Session 861 - Feedback Processing)
from ..models_pipeline_feedback import (
    PipelineStageFeedback,
)

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
    'SpiderItemHash',  # Session 616: Spider deduplication
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

    # Conversation Artifacts (Session 555)
    'ExtractedArtifact',
    'ArtifactExtractionLog',
    'ArtifactExecution',
    'WeeklySynthesis',
    'ReviewDocument',
    'SideChat',

    # Document Registry (Session 622)
    'Initiative',
    'InitiativeStage',

    # LLM Routing (Session 697)
    'LLMProvider',
    'LLMModel',
    'AgentLLMConfig',
    'LLMCallLog',

    # Orchestration Layer (Session 764)
    'OrchestrationExecution',
    'OrchestrationStepExecution',
    'OrchestrationApprovalGate',

    # Deliverables Marketplace (Session 819)
    'DeliverableType',
    'ContentFormat',
    'Deliverable',
    'DeliverableExport',
    'DeliverableCollection',

    # Tool Call Recording (Session 861)
    'ToolCallRecord',
    'ToolCallAggregate',

    # Learning Data Backup (Session 861)
    'AgentInteractionRecord',
    'LearnedPreferenceRecord',
    'LearningProgressSnapshot',
    'AgentImprovementRecord',

    # Decision Recording (Session 861)
    'DecisionRecord',
    'DecisionAggregate',

    # Spider Aggregation Caching (Session 861)
    'SpiderAggregation',
    'TrendDataPoint',

    # Pipeline Feedback (Session 861)
    'PipelineStageFeedback',
]