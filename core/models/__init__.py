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
    PAToolInsight,
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

# Import pipeline feedback model (Session 861 - Feedback Processing)
from ..models_pipeline_feedback import (
    PipelineStageFeedback,
)

# Import research result model (Session 862 - Content Flow Unification)
from ..models_research import (
    ResearchResult,
)

# Import synthetic user models (Session 862 - Test Personas)
from ..models_synthetic_users import (
    SyntheticUserProfile,
    SyntheticUserTestRun,
)

# Import ConceptForge models (Session 863 - Autonomous Think Tank Pipeline)
from ..models_conceptforge import (
    ConceptForgeRun,
    ConceptForgeStageRun,
    ConceptForgeArtifact,
)

# Import ATS optimization models (Session 866 - Resume ATS Keyword Optimization)
from ..models_ats_optimization import (
    PersonaResumeTemplate,
    ATSKeywordMapping,
    ResumeOptimizationLog,
    ResumeRewriteOrder,
)

# Import signal intelligence models (Session 900 - Signal Provenance)
from ..models_signal_intelligence import (
    SignalCluster,
    AutoTopic,
    TopicSuggestion,
)

# Import audio cache model (Session 926 - Universal Agent Voice System)
from ..models_audio_cache import AudioCache

# Import user feedback model (Session 948 - PA Feedback Queue)
from ..models_user_feedback import UserFeedback

# Import deliberation models (Session 962 - Phase 1 Persistence Layer)
from ..models_deliberation import (
    DeliberationSession,
    DeliberationTurn,
    ContractRecord,
    DocVersion,
)

# Import executor models (Session 1074 - Three-Way Collaboration Executor)
# Session 1075: Added Repo registry for multi-repo architecture
from .executor import ExecutionRun, Repo

# Import Celery telemetry models (Session 983 - Celery Observability)
from ..models_celery_telemetry import CeleryTaskEvent

# Import code artifact models (Session 1012 - Patch-First Workflow)
from ..models_code_artifacts import CodeArtifact

# Import tenant model (Session 1039 - Multi-Tenant Customer Access)
from ..models_tenant import Tenant

# Import mobile models (Session 1073 - Mobile Push Notifications)
from ..models_mobile import MobilePushToken

from ..models_cockpit_audit import CockpitAuditLog

# Import cockpit agent state (Session P12 - Agent Fleet Management)
from ..models_cockpit_agent_state import CockpitAgentState

# Import cockpit autopilot (Session P14 - Autopilot)
from ..models_cockpit_autopilot import CockpitAutopilotPolicy, CockpitAutopilotEvent

# Import cockpit incidents (Session P17 - Incident Commander)
from ..models_cockpit_incidents import CockpitIncident, CockpitIncidentEvent

# Import competitor comparison (Session G1)
from ..models_competitor_comparison import CompetitorComparison

# Import workflow run model
from ..models_workflow_run import WorkflowRun

# Import ops runs (Context Packet #9 - Ops Observability)
from ..models_ops_runs import OpsRun, OpsRunEvent

# Import AutopilotAction + RemediationPlaybook (Session 1086/1087)
# Other diagnostic pipeline models already tracked via earlier migrations
from ..models_diagnostic_pipeline import AutopilotAction, RemediationPlaybook

# Import ImpactEvent (Session 1089 - Autonomy #8 Impact Tracking)
from ..models_impact_events import ImpactEvent

# Import PolicyExperiment (Session 1090 - Autonomy #11 Experiment Engine)
from ..models_policy_experiment import PolicyExperiment

# Import DecisionLedgerEntry (Session 1090 - Autonomy #12 Decision Ledger)
from ..models_decision_ledger import DecisionLedgerEntry

# Import impact credit model (Autonomy #17 - Multi-Touch Attribution)
from ..models_impact_credit import ImpactCredit

# Import learning journey models (Session 773 - Learning Journeys)
from ..models_learning_journey import (
    LearningJourneyTemplate,
    LearningJourney,
    LearningJourneyStep,
    LearningAchievement,
    UserLearningAchievement,
    UserLearningStreak,
)

# Import outreach models (Autonomy #22 - Outreach Sequencing)
from ..models_outreach import OutreachDraft

# Import close pack models (Autonomy #23 - Close-the-Deal Engine)
from ..models_close_pack import ClosePack

# Import engagement models (Autonomy #24 - Engagement Engine)
from ..models_engagement import EngagementEvent

# Import meeting models (Autonomy #25 - Meeting Engine)
from ..models_meeting import Meeting

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
    'PAToolInsight',

    # Learning Data Backup (Session 861)
    'AgentInteractionRecord',
    'LearnedPreferenceRecord',
    'LearningProgressSnapshot',
    'AgentImprovementRecord',

    # Decision Recording (Session 861)
    'DecisionRecord',
    'DecisionAggregate',

    # Pipeline Feedback (Session 861)
    'PipelineStageFeedback',

    # Research Result (Session 862)
    'ResearchResult',

    # Synthetic Users - Test Personas (Session 862)
    'SyntheticUserProfile',
    'SyntheticUserTestRun',

    # ConceptForge - Autonomous Think Tank Pipeline (Session 863)
    'ConceptForgeRun',
    'ConceptForgeStageRun',
    'ConceptForgeArtifact',

    # ATS Optimization - Resume Keyword Optimization (Session 866)
    'PersonaResumeTemplate',
    'ATSKeywordMapping',
    'ResumeOptimizationLog',
    'ResumeRewriteOrder',

    # Signal Intelligence - Signal Provenance (Session 900)
    'SignalCluster',
    'AutoTopic',
    'TopicSuggestion',

    # Audio Cache - Universal Agent Voice System (Session 926)
    'AudioCache',

    # User Feedback - PA Feedback Queue (Session 948)
    'UserFeedback',

    # Deliberation Persistence - Phase 1 (Session 962)
    'DeliberationSession',
    'DeliberationTurn',
    'ContractRecord',
    'DocVersion',

    # Celery Telemetry - Celery Observability (Session 983)
    'CeleryTaskEvent',

    # Learning Journeys (Session 773)
    'LearningJourneyTemplate',
    'LearningJourney',
    'LearningJourneyStep',
    'LearningAchievement',
    'UserLearningAchievement',
    'UserLearningStreak',

    # Desk Intelligence Briefs (Session 1003)
    'SportsBettingBrief',
    'BlockchainAuditBrief',

    # Code Artifacts - Patch-First Workflow (Session 1012)
    'CodeArtifact',

    # Tenant - Multi-Tenant Customer Access (Session 1039)
    'Tenant',

    # Mobile - Push Notifications (Session 1073)
    'MobilePushToken',

    # Executor - Repo Registry (Session 1075)
    'Repo',
    'ExecutionRun',

    # Cockpit Audit Log (P11)
    'CockpitAuditLog',

    # Cockpit Agent State (P12)
    'CockpitAgentState',

    # Cockpit Autopilot (P14)
    'CockpitAutopilotPolicy',
    'CockpitAutopilotEvent',

    # Cockpit Incidents (P17)
    'CockpitIncident',
    'CockpitIncidentEvent',

    # Competitor Comparison (G1)
    'CompetitorComparison',

    # Workflow Run
    'WorkflowRun',

    # Ops Runs (Context Packet #9)
    'OpsRun',
    'OpsRunEvent',

    # Impact Events (Session 1089 - Autonomy #8)
    'ImpactEvent',

    # Policy Experiment (Session 1090 - Autonomy #11)
    'PolicyExperiment',

    # Decision Ledger (Session 1090 - Autonomy #12)
    'DecisionLedgerEntry',

    # Impact Credit (Autonomy #17)
    'ImpactCredit',

    # Outreach Draft (Autonomy #22)
    'OutreachDraft',

    # Close Pack (Autonomy #23)
    'ClosePack',

    # Engagement Event (Autonomy #24)
    'EngagementEvent',

    # Meeting (Autonomy #25)
    'Meeting',

]