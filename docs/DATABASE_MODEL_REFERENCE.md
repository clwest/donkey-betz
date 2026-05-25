# Database Model Reference

**Created:** Session 737 (January 9, 2026)
**Purpose:** Complete reference for all database models
**Last Updated:** Session 1012 (March 4, 2026 — body contains Session 1012 additions; header bumped Session 1142 to match)

---

## Summary

| Metric | Value |
|--------|-------|
| **Total Models** | 386+ |
| **Active Models** (have data) | 250+ |
| **Empty Models** (0 records) | ~136 |
| **Session 856-969b Models** | 30+ (diagnostic pipeline, signals, deliberation, initiatives, telemetry) |

---

## Critical Models - Know These!

These are the most important models and where confusion commonly occurs:

### Agent Execution Tracking

| Purpose | Model | Import | Records |
|---------|-------|--------|---------|
| Agent registry | `Agent` | `core.models_unified_system` | 80 |
| Execution records | `AgentExecution` | `core.models_unified_system` | 94 |
| Execution memories | `AgentMemory` | `core.models_unified_system` | 1,076 |
| Learning outcomes | `CoordinatorOutcome` | `core.models_unified_system` | 3,963 |

### Spider Data

| Purpose | Model | Import | Records |
|---------|-------|--------|---------|
| Raw spider data | `SpiderData` | `core.models` | 11,314 |
| Spider intelligence events | `AgentLearning` | `core.models_unified_system` | 45,414 |
| Execution logs | `SpiderExecutionLog` | `core.models_unified_system` | 22,056 |
| Deduplication hashes | `SpiderItemHash` | `core.models_unified_system` | 63,657 |

### User Interactions

| Purpose | Model | Import | Records |
|---------|-------|--------|---------|
| PA chat history | `ConversationMemory` | `core.models` | 617 |
| Chat messages | `ConversationMessage` | `core.models` | 19,177 |
| User context | `UserMemoryContext` | `core.models_unified_system` | 682 |

---

## Common Mistakes to Avoid

### Mistake 1: Wrong memory table
```python
# WRONG - User chat history (may be empty if PA not used)
from core.models import ConversationMemory
ConversationMemory.objects.count()  # 617, but 0 recent

# CORRECT - Agent execution memories (actively updated)
from core.models_unified_system import AgentMemory
AgentMemory.objects.count()  # 1,076 and growing
```

### Mistake 2: Wrong learning table
```python
# WRONG - Spider intelligence events (not agent learning!)
from core.models_unified_system import AgentLearning
AgentLearning.objects.filter(learning_type='agent_execution').count()  # 0

# CORRECT - Agent execution outcomes
from core.models_unified_system import CoordinatorOutcome
CoordinatorOutcome.objects.count()  # 3,963
```

### Mistake 3: Confusing similar model names
```python
# AgentSolution (45,414) - Same as AgentLearning, spider data
# AgentMemory (1,076) - Agent execution memories
# ConversationMemory (617) - User chat history
# UserMemoryContext (682) - User context tracking
```

---

## AgentMemory Model Fields (Session 768)

The `AgentMemory` model stores agent execution memories with embeddings for semantic retrieval. Session 768 added **Memory Safety Classification** to prevent test content from polluting learning.

### Core Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | UUID | Primary key |
| `agent` | FK(Agent) | Which agent owns this memory |
| `title` | CharField(200) | Brief title/summary |
| `content` | TextField | Detailed memory content |
| `context` | TextField | Context in which memory was formed |
| `memory_type` | CharField | success, failure, preference, technique, insight, interaction, feedback |
| `valence` | CharField | positive, negative, neutral |
| `importance_score` | Float(0-1) | How important is this memory |
| `memory_outcome` | CharField | success, failure, partial, unknown |

### Session 768: Safety Classification Fields

| Field | Type | Description |
|-------|------|-------------|
| `safety_class` | CharField | **test_only** (never embed), **exploratory** (review), **candidate** (default), **approved** (embed) |
| `poison_risk_score` | Float(0-1) | Risk of polluting embeddings (0=safe, 1=dangerous) |
| `poison_risk_factors` | JSONField | List of detected risks: `too_short`, `self_promotional`, `test_pattern`, `lacks_context`, `highly_abstract` |

### Embedding & Metadata

| Field | Type | Description |
|-------|------|-------------|
| `embedding` | VectorField(1536) | pgvector embedding for semantic search |
| `tags` | JSONField | List of tags for grouping |
| `source_type` | CharField | What triggered: task, conversation, dream, hive_mind |
| `source_id` | CharField | ID of source event |
| `access_count` | PositiveInt | How many times retrieved |
| `last_accessed_at` | DateTime | When last retrieved |

### Usage Examples

```python
from core.models_unified_system import AgentMemory

# Get only approved memories (safe for learning)
approved = AgentMemory.objects.filter(safety_class='approved')

# Exclude test memories from retrieval
learnable = AgentMemory.objects.exclude(safety_class='test_only')

# Find high-risk memories needing review
risky = AgentMemory.objects.filter(poison_risk_score__gte=0.5)

# Create test memory (won't generate embedding)
memory = AgentMemory.create_memory(
    agent=agent,
    title="Health check response",
    content="Agent says hello",
    safety_class='test_only'
)
```

---

## All Models by Category

### Agent Models (33 models, 109,198 records)

**Note:** `AgentSolution` and `AgentLearning` are a **1:1 parent-child pair** (created together):
- `AgentSolution`: Stores the actual spider-collected content/solution
- `AgentLearning`: Tracks knowledge transfer (which agent learned from which solution)
- Every `AgentLearning` has a `solution` FK pointing to an `AgentSolution`

| Model | Records | Purpose |
|-------|---------|---------|
| `AgentSolution` | 45,414 | Spider-collected solutions/content (parent) |
| `AgentLearning` | 45,414 | Knowledge transfer tracking (child of AgentSolution) |
| `AgentDream` | 7,542 | Agent dream/imagination logs |
| `AgentKnowledgeSource` | 3,915 | Knowledge sources for agents |
| `AgentConversation` | 3,672 | Agent conversation logs |
| `AgentMemory` | 1,076 | **Agent execution memories** |
| `AgentDecisionSummary` | 604 | Decision summaries |
| `AgentRelationship` | 552 | Inter-agent relationships |
| `UserAgentLearning` | 285 | Per-user agent preferences |
| `AgentLearningConnection` | 160 | Learning connections |
| `AgentExecution` | 94 | **Execution records** |
| `Agent` | 80 | **Agent registry** |
| `AgentMood` | 80 | Agent mood states |
| `AgentLLMConfig` | 75 | LLM configs per agent |
| `AgentSpiderConnection` | 57 | Agent-spider mappings |
| `AgentEvolution` | 56 | Evolution/XP tracking |
| `AgentPrediction` | 50 | Agent predictions |
| `AgentCategory` | 25 | Agent categories |
| `AgentPersonality` | 20 | Personality configs |
| `AgentRole` | 8 | Role definitions |
| `AgentPerformanceMetric` | 8 | Performance metrics |
| `AgentAccuracyMetrics` | 4 | Accuracy tracking |
| `AgentSession` | 3 | Session tracking |
| `AgentChannel` | 2 | Agent channels |
| `AgentTeam` | 1 | Team definitions |
| `AgentAbility` | 1 | Ability definitions |
| `AgentLearningSession` | 0 | Learning sessions |
| `AgentCollaboration` | 0 | Collaboration records |
| `AgentAssignment` | 0 | Assignment records |
| `InterAgentMessage` | 0 | Inter-agent messages |
| `AgentTeamMembership` | 0 | Team memberships |
| `AgentMessage` | 0 | Agent messages |
| `AgentQueryPerformance` | 0 | Query performance |

### Spider Models (7 models, 97,072 records)

| Model | Records | Purpose |
|-------|---------|---------|
| `SpiderItemHash` | 63,657 | Deduplication hashes |
| `SpiderExecutionLog` | 22,056 | Execution logs |
| `SpiderData` | 11,314 | **Raw collected data** |
| `TrackSpiderMapping` | 23 | Track-spider mappings |
| `SpiderCategory` | 15 | Spider categories |
| `ProjectSpiderPriority` | 7 | Priority settings |
| `SpiderAnalytics` | 0 | Analytics (unused) |

### Memory Models (8 models, 1,573 records)

| Model | Records | Purpose |
|-------|---------|---------|
| `UserMemoryContext` | 682 | User context |
| `ConversationMemory` | 617 | **PA chat history** |
| `MemoryClusterMembership` | 219 | Cluster memberships |
| `MemoryPalaceRoom` | 45 | Memory palace rooms |
| `MemoryCluster` | 6 | Memory clusters |
| `ClusterEvolution` | 2 | Cluster evolution |
| `MemoryConnection` | 1 | Memory connections |
| `LegalMemory` | 1 | Legal memories |

### Learning Models (12 models, 8,249 records)

| Model | Records | Purpose |
|-------|---------|---------|
| `PredictionOutcome` | 4,124 | Prediction outcomes |
| `CoordinatorOutcome` | 3,963 | **Agent execution outcomes** |
| `OpportunityOutcome` | 150 | Opportunity outcomes |
| `ExperimentLearning` | 4 | Experiment learning |
| `LearningCompanion` | 3 | Learning companions |
| `DecisionTypeSuccessPattern` | 3 | Success patterns |
| `LearningInsight` | 1 | Learning insights |
| `LearningPattern` | 1 | Learning patterns |
| `ErrorPattern` | 0 | Error patterns |
| `SuccessPattern` | 0 | Success patterns |
| `ErrorInstance` | 0 | Error instances |
| `LearningProgress` | 0 | Learning progress |

### Body System Models (30 models, 251 records)

| Model | Records | Purpose |
|-------|---------|---------|
| `DigestivePulse` | 101 | Digestive system pulse |
| `CirculationPulse` | 19 | Circulatory system pulse |
| `RoutePattern` | 19 | Spine route patterns |
| `ThreatPattern` | 14 | Immune threat patterns |
| `MuscularPulse` | 12 | Muscular system pulse |
| `MuscleGroup` | 10 | Muscle groups |
| `MuscleStatus` | 10 | Muscle status |
| `MythologyQuarantine` | 9 | Quarantined content |
| `FlowRoute` | 9 | Flow routes |
| `FlowStatus` | 9 | Flow status |
| `IngestionRoute` | 8 | Ingestion routes |
| `RespiratoryStatus` | 7 | Respiratory status |
| `ComponentStatus` | 6 | Component status |
| `Budget` | 6 | LUNGS budgets |
| `BreathCycle` | 6 | Breath cycles |
| `HeartBeat` | 3 | Heartbeat records |
| `SpineStatus` | 2 | Spine status |
| `ImmuneStatus` | 1 | Immune status |
| `WorkspaceOperation` | 6 | SKIN operations |
| `ProjectWorkspace` | 2 | Workspaces |
| *+ 10 more empty* | 0 | Various body systems |

### Content Models (22 models, 204 records)

| Model | Records | Purpose |
|-------|---------|---------|
| `ChannelEpisode` | 88 | Channel episodes |
| `SeriesEpisode` | 49 | Series episodes |
| `ContentProvenance` | 23 | Content provenance |
| `ContentDebate` | 22 | Content debates |
| `DiscordServerChannel` | 7 | Discord channels |
| `ChannelMembership` | 5 | Channel memberships |
| `PodcastDebate` | 4 | Podcast debates |
| `ContentChannel` | 3 | Content channels |
| `PodcastEpisode` | 3 | Podcast episodes |
| *+ 13 more empty* | 0 | Various content types |

### User Models (16 models, 66 records)

| Model | Records | Purpose |
|-------|---------|---------|
| `UserEmbedding` | 30 | User embeddings |
| `UserProfile` | 10 | User profiles |
| `UserStatistics` | 10 | User statistics |
| `ExtendedUserProfile` | 10 | Extended profiles |
| `EnhancedUserProfile` | 3 | Enhanced profiles |
| `UserCertification` | 1 | Certifications |
| `UserPreferenceProfile` | 1 | Preferences |
| `VoiceProfile` | 1 | Voice profiles |
| *+ 8 more empty* | 0 | Various user data |

### Opportunity Models (9 models, 1,657 records)

| Model | Records | Purpose |
|-------|---------|---------|
| `Opportunity` | 1,498 | **Opportunity records** |
| `OpportunityTask` | 150 | Opportunity tasks |
| `SavedOpportunity` | 5 | Saved opportunities |
| `OpportunityScore` | 3 | Opportunity scores |
| `OpportunityDigest` | 1 | Opportunity digests |
| *+ 4 more empty* | 0 | Various opportunity data |

### LLM Models (3 models, 32 records)

| Model | Records | Purpose |
|-------|---------|---------|
| `LLMModel` | 16 | LLM model configs |
| `LLMCallLog` | 10 | LLM call logs |
| `LLMProvider` | 6 | LLM providers |

### Pilot/Experiment Models (7 models, 370 records)

| Model | Records | Purpose |
|-------|---------|---------|
| `ReadinessChecklistItem` | 181 | Readiness items |
| `PilotReadinessGate` | 70 | Readiness gates |
| `PilotExecution` | 58 | Pilot executions |
| `Experiment` | 50 | Experiments |
| `PilotImplementation` | 11 | Implementations |
| *+ 2 more empty* | 0 | A/B experiments |

### Other Major Models (selected from 122)

| Model | Records | Purpose |
|-------|---------|---------|
| `ConversationMessage` | 19,177 | Chat messages |
| `ProjectInsight` | 6,919 | Project insights |
| `SideChat` | 6,776 | Side chat records |
| `ExtractedArtifact` | 3,608 | Extracted artifacts |
| `ReviewDocument` | 3,388 | Review documents |
| `KnowledgeTransfer` | 1,589 | Knowledge transfers |
| `MoodHistory` | 733 | Mood history |
| `ChatConversation` | 617 | Chat conversations |
| `SelfBlog` | 549 | Self blog posts |
| `HiveMindSession` | 321 | Hive mind sessions |
| `CostTracking` | 137 | Cost tracking |
| `TrackedConcern` | 97 | Tracked concerns |
| `ThoughtRecord` | 91 | Thought records |
| `SharedKnowledge` | 50 | Shared knowledge |
| `DataProvenance` | 31 | Data provenance |
| `AuditLog` | 31 | Audit logs |
| `Advisor` | 25 | Advisor records |
| `CollaborationSession` | 23 | Collaboration sessions |
| `TimeCapsule` | 7 | Time capsules |

---

## Import Cheat Sheet

```python
# === MOST COMMONLY NEEDED ===

# Agent execution tracking
from core.models_unified_system import (
    Agent,              # Agent registry (80)
    AgentExecution,     # Execution records (94)
    AgentMemory,        # Execution memories (1,076)
    CoordinatorOutcome, # Learning outcomes (3,963)
)

# Spider data
from core.models import SpiderData  # Raw data (11,314)
from core.models_unified_system import (
    AgentLearning,      # Spider intelligence (45,414)
    SpiderExecutionLog, # Execution logs (22,056)
)

# User data
from core.models import ConversationMemory  # PA chat (617)
from core.models_unified_system import (
    ConversationMessage,  # Chat messages (19,177)
    UserMemoryContext,    # User context (682)
)

# Opportunities & Predictions
from core.models_unified_system import (
    Opportunity,        # Opportunities (1,498)
    PredictionOutcome,  # Prediction outcomes (4,124)
)

# Body systems
from core.models_unified_system import (
    ComponentStatus,    # Component health (6)
    Budget,             # LUNGS budgets (6)
    ThreatPattern,      # Immune threats (14)
    MuscleGroup,        # Muscle groups (10)
)

# LLM tracking
from core.models_unified_system import (
    LLMProvider,        # Providers (6)
    LLMModel,           # Models (16)
    AgentLLMConfig,     # Agent configs (75)
    LLMCallLog,         # Call logs (10)
)

# === ADDED SESSIONS 856-969b ===

# Diagnostic pipeline (Session 856)
from core.models_diagnostic_pipeline import (
    FailureSignature,   # Failure grouping by signature
    FailureDetection,   # Raw failure recording
    FailureDiagnosis,   # Root cause analysis
    FailurePrescription,# Fix tracking
)

# Signal intelligence (Session 900)
from core.models_signal_intelligence import (
    SignalCluster,      # Spider signal clusters
    AutoTopic,          # Auto-generated topics
)

# Heart/body health
from core.models_heart import (
    HeartBeat,          # System heartbeats
    ComponentStatus,    # Component health
)

# Initiative pipeline (Session 901-902)
from core.models_document_registry import (
    Initiative,         # Strategic projects (52 active)
    InitiativeActionItem,  # Tracked action items
)

# Celery results (external)
from django_celery_results.models import TaskResult
```

---

## Health Check Query

```python
from django.utils import timezone
from datetime import timedelta
from core.models_unified_system import (
    Agent, AgentExecution, AgentMemory, CoordinatorOutcome,
    AgentLearning, SpiderExecutionLog
)
from core.models import SpiderData, ConversationMemory

cutoff = timezone.now() - timedelta(days=7)

print("=== System Health (Last 7 Days) ===")
print(f"Agents registered: {Agent.objects.count()}")
print(f"Agent executions: {AgentExecution.objects.filter(created_at__gte=cutoff).count()}")
print(f"Agent memories: {AgentMemory.objects.filter(created_at__gte=cutoff).count()}")
print(f"Learning outcomes: {CoordinatorOutcome.objects.filter(created_at__gte=cutoff).count()}")
print(f"Spider data: {SpiderData.objects.filter(discovered_at__gte=cutoff).count()}")
print(f"Spider intelligence: {AgentLearning.objects.filter(created_at__gte=cutoff).count()}")
print(f"PA conversations: {ConversationMemory.objects.filter(created_at__gte=cutoff).count()}")
```

---

## Session 861 Models - Data Persistence

These models were added in Session 861 to fix critical data persistence gaps:

### Tool Call Tracking

| Purpose | Model | Import | Description |
|---------|-------|--------|-------------|
| Individual tool calls | `ToolCallRecord` | `core.models_tool_calls` | Records every tool call with latency, success, result |
| Daily aggregates | `ToolCallAggregate` | `core.models_tool_calls` | Daily statistics per agent/tool |

### Decision Recording

| Purpose | Model | Import | Description |
|---------|-------|--------|-------------|
| Agent decisions | `DecisionRecord` | `core.models_decision_records` | Always-on decision tracking with reasoning |
| Daily aggregates | `DecisionAggregate` | `core.models_decision_records` | Daily statistics per agent/decision_type |

### Learning Data Backup

| Purpose | Model | Import | Description |
|---------|-------|--------|-------------|
| Interaction backup | `AgentInteractionRecord` | `core.models_learning_backup` | Backs up Redis interactions to DB |
| Preferences backup | `LearnedPreferenceRecord` | `core.models_learning_backup` | Backs up learned preferences |
| Progress snapshots | `LearningProgressSnapshot` | `core.models_learning_backup` | Periodic learning progress snapshots |
| Improvement backup | `AgentImprovementRecord` | `core.models_learning_backup` | Backs up agent improvement data |

### Spider Aggregation Caching

| Purpose | Model | Import | Description |
|---------|-------|--------|-------------|
| Cached aggregations | `SpiderAggregation` | `core.models_spider_aggregation` | Cached spider data aggregations |
| Time-series data | `TrendDataPoint` | `core.models_spider_aggregation` | Time-series trend data points |

### Usage Example

```python
from core.models_tool_calls import ToolCallRecord
from core.models_decision_records import DecisionRecord
from core.models_spider_aggregation import SpiderAggregation

# Check tool call recording
ToolCallRecord.objects.filter(agent_name='ContentWriterAgent').count()

# Check decision traces
DecisionRecord.objects.filter(decision_type='tool_call').count()

# Check spider aggregation cache
SpiderAggregation.objects.filter(aggregation_type='daily_summary').first()
```

---

## Session 856 Models - Diagnostic Pipeline

Failure analysis system: Detection -> Diagnosis -> Prescription. Import from `core.models_diagnostic_pipeline`.

| Purpose | Model | Key Fields | Description |
|---------|-------|------------|-------------|
| Failure grouping | `FailureSignature` | `signature`, `category`, `status`, `occurrence_count`, `last_seen_at` | Groups failures by stable signature (e.g., OPENAI_429_QUOTA) |
| Raw failure recording | `FailureDetection` | `signature` FK, `source_type`, `error_message`, `detected_at` | Phase 1: What happened |
| Root cause analysis | `FailureDiagnosis` | `signature` 1:1, `root_cause`, `blast_radius`, `evidence_sources` | Phase 2: Why it happened |
| Fix tracking | `FailurePrescription` | `diagnosis` FK, `scope`, `effort`, `priority_score`, `status` | Phase 3: What to do |

**Key:** `FailureSignature.status` choices: active, known_outage, diagnosed, resolved, ignored. `FailureDetection.source_type` choices: experiment, agent_execution, spider, celery_task, api_call, provider.

---

## Session 900 Models - Signal Intelligence

Signal clustering and auto-topic generation for initiative provenance. Import from `core.models_signal_intelligence`.

| Purpose | Model | Key Fields | Description |
|---------|-------|------------|-------------|
| Signal clusters | `SignalCluster` | `detected_at`, `strength`, `confidence`, `novelty`, `status`, `keywords` | Groups spider signals into patterns |
| Auto-generated topics | `AutoTopic` | `signal_cluster` FK, `topic`, `rationale`, `domain` | Why topics are chosen with rationale |

**Key:** `SignalCluster.status` choices: active, processed, expired. Used by `recent_activity_tool` and signal aggregation service.

---

## Session 901-902 Models - Initiative Pipeline

Initiative priority scoring and action item tracking. Import from `core.models_document_registry`.

| Purpose | Model | Key Fields | Description |
|---------|-------|------------|-------------|
| Projects | `Initiative` | `updated_at`, `last_activity_at`, `impact_score`, `urgency`, `confidence`, `revenue_potential`, `status` | Strategic projects from conversations |
| Action items | `InitiativeActionItem` | `initiative` FK, `status`, `priority`, `due_date`, `assigned_agent` | Tracked next steps from conclusions |

**Key:** `Initiative.status` = 'ACTIVE' for live projects. `InitiativeActionItem.priority` choices: critical, high, medium, low. `InitiativeActionItem.status` choices: pending, in_progress, completed, blocked.

---

## Session 1012 Models - Code Artifacts

Patch-first workflow for autonomous code generation. When agents write code on Railway (no writable workspace), outputs are captured as reviewable artifacts.

| Purpose | Model | Import | Description |
|---------|-------|--------|-------------|
| Code capture | `CodeArtifact` | `core.models_code_artifacts` | Captured code output with review status |

**Key fields:** `agent_name`, `kind` (file_create/file_edit/patch), `status` (pending/approved/rejected/applied/stale), `target_path`, `content`, `content_before`, `description`, `reviewed_by`, `reviewed_at`, `review_note`, `trace_id`

**FKs:** `agent_execution` (AgentExecution), `initiative` (Initiative), `reviewed_by` (User) — all nullable

**API:** `/api/code-artifacts/` — list (filterable by status, agent_name, initiative, kind), detail, approve, reject

```python
from core.models_code_artifacts import CodeArtifact

# Pending review
CodeArtifact.objects.filter(status='pending').count()

# By agent
CodeArtifact.objects.filter(agent_name='CodeGeneratorAgent')
```

---

## Session 964 Models - Content Deliberation

Multi-agent content review pipeline. No new migrations — uses existing `SelfBlog.stats_snapshot['deliberation']` JSON field.

| Purpose | Model | Key Fields | Description |
|---------|-------|------------|-------------|
| Blog posts | `SelfBlog` | `quality_score`, `novelty_score`, `structure_score`, `publish_ready`, `gate_notes`, `tone`, `word_count`, `stats_snapshot` | Self-generated blog posts with deliberation data |

**Key:** `stats_snapshot['deliberation']` contains: `claims_pack` (claim IDs, sources), `reviews` (3 reviewer verdicts), `decision` (PUBLISH/REVISE/KILL), `enforcement` details.

---

## Session 969b - PA Telemetry Tool Queries

The 3 PA live telemetry tools query these models (no new models created):

| Tool | Models Queried |
|------|---------------|
| `recent_activity_tool` | `TaskResult` (celery), `SpiderData`, `HiveMindSession`, `SelfBlog`, `Initiative`, `SignalCluster` |
| `system_health_tool` | `HeartBeat`, `ComponentStatus`, `TaskResult`, `ToolCallAggregate`, `SpiderData` |
| `error_summary_tool` | `FailureSignature`, `FailureDetection`, `ToolCallRecord`, `TaskResult` |

**Import patterns:**
```python
# Diagnostic pipeline
from core.models_diagnostic_pipeline import FailureSignature, FailureDetection

# Signal intelligence
from core.models_signal_intelligence import SignalCluster

# Heart/body systems
from core.models_heart import HeartBeat, ComponentStatus

# Celery results (external)
from django_celery_results.models import TaskResult
```

---

## Empty Models (~136 total)

These models exist but have no data yet. They represent features that are:
- Not yet implemented
- Awaiting user interaction
- Reserved for future functionality

Major categories of empty models:
- **A/B Testing** (ABExperiment, ABVariant, etc.)
- **Legal Case Management** (LegalCase, LegalDocument, etc.)
- **Workflow Automation** (CustomWorkflow, WorkflowExecution, etc.)
- **Advanced Analytics** (AnalyticsDashboard, AnalyticsAlert)
- **Betting Features** (Wager, BettingSession)
- **Voice Features** (VoiceTransaction, VoiceReview)

---

*Document created to prevent confusion about database tables.*
*See: docs/audits/SESSION_736_INTEGRATION_REALITY_REPORT.md for the incident that prompted this.*
