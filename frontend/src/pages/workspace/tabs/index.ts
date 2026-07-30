// Session 825: Workspace tabs barrel export
// Session 971b: Added SystemTab, DataIntelTab adapters for 9-tab model
// Session 1077: Unified Work tab + Ops Console
// Session 1240: CommandTab/SystemTab/LearningJourneyTab dropped (PlatformPage delete cascade)
export { WorkTab } from './WorkTab'
export { OpsConsoleTab } from './OpsConsoleTab'
export { GovernanceTab } from './GovernanceTab'
export { KnowledgeTab } from './KnowledgeTab'
export { OperationsTab } from './OperationsTab'
export { FilesTab } from './FilesTab'

// Phase 2: Infrastructure Tab (consolidates 6 pages)
export { InfrastructureTab } from './InfrastructureTab'

// Phase 2: Orchestration Tab (consolidates 4 pages)
export { OrchestrationTab } from './OrchestrationTab'

// Phase 3: Content Studio Tab (consolidates 5 pages)
export { ContentStudioTab } from './ContentStudioTab'

// Phase 4: Data Sources Tab (consolidates 3 pages)
export { DataSourcesTab } from './DataSourcesTab'

// Phase 5: AI Consciousness Tab (consolidates 8 pages)
export { AIConsciousnessTab } from './AIConsciousnessTab'

// Phase 6: Intelligence Tab (consolidates 3 pages)
export { IntelligenceTab } from './IntelligenceTab'

// Session 847: Initiative Pipeline Dashboard
export { InitiativesTab } from './InitiativesTab'

// Session 861B: WorkspaceTrigger Autopilot Queue
export { TriggersTab } from './TriggersTab'

// Session 865: ConceptForge Dossier Pipeline
export { ConceptForgeTab } from './ConceptForgeTab'

// Session 866: Career Tab - ATS Resume Optimizer
export { CareerTab } from './CareerTab'

// Session 869: Voice Marketplace Tab
export { VoiceMarketplaceTab } from './VoiceMarketplaceTab'

// Session 927: Boardroom Tab - Decision Hub
export { BoardroomTab } from './BoardroomTab'

// Session 971b: Merged adapter tabs (9-tab model)
export { DataIntelTab } from './DataIntelTab'

// Session 1008: Campaign Orchestrator + ToolCall Analytics
export { CampaignTab } from './CampaignTab'
export { ToolCallAnalyticsTab } from './ToolCallAnalyticsTab'

// Session 1009: Deliverables Library
export { DeliverablesTab } from './DeliverablesTab'

// Session 1035: Workspace split — new workspace-only tabs
export { WorkspaceOverviewTab } from './WorkspaceOverviewTab'
export { GitTab } from './GitTab'

// Stage 3 Evaluation Dashboard — Capitalize Opportunity pilot
export { Stage3EvaluationTab } from './Stage3EvaluationTab'

// Preview System: Workspace Hosted Previews + Magic Links
export { LaunchpadTab } from './LaunchpadTab'

// Session 1078: Home Tab — attention queue + active work + pulse
export { default as HomeTab } from './HomeTab'

// App Integration: Embedded standalone apps in workspace
export { default as AppTab, hasApp } from './AppTab'

// Session 1224: Outreach Inbox — Opportunity → OutreachDraft approval surface
export { OutreachInboxTab } from './OutreachInboxTab'

// S2831: RAG Intent-Gate Diagnostics — canary for S2830 pointer-intent registry
export { RagDiagnosticsTab } from './RagDiagnosticsTab'

// S2930: Agent Runs — persistent view of AgentExecution history
export { AgentRunsTab } from './AgentRunsTab'

// S2934: Signal Dispatches — observability for S2933 A3 auto-dispatch pipeline
export { SignalDispatchesTab } from './SignalDispatchesTab'

// S2978: Theme Signals v1 — Buildable/Investable tab-scoped cards (product-tier UI on SignalCluster)
export { ThemeSignalsTab } from './theme-signals/ThemeSignalsTab'

// S2989 Phase B: Audit Findings — docs/research/ finding registry with mark + send-to-rigby
export { FindingsTab } from './FindingsTab'

// S3047 slice 2: Rigby Tool Gap Ledger — engineering_backlog deliverable dashboard
export { ToolGapLedgerTab } from './ToolGapLedgerTab'
