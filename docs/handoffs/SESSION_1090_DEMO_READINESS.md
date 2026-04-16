# Session 1090 — Demo Readiness + Agent Self-Audit

**Date:** April 16, 2026
**PRs:** #1946–#1961 (12 PRs merged)
**PA Conversations:** `pa-bf5a64f29816`, `pa-697ab48e2ffc`

## Summary

Session 1090 focused on demo readiness for the "A Platform That Knows Itself" video. Fixed agent reliability issues, built Demo Autonomy Mode, corrected agent-to-role assignments, and ran a full dry run where 5 agents produced real operational artifacts from live platform data. The agents identified 14 real issues that became the fix list for Session 1091.

---

## PRs Shipped (12)

| PR | Title | Impact |
|----|-------|--------|
| #1946 | ContentWriter error propagation + AISeriesWorkflow timeout caps | Real errors visible, zombie executions eliminated |
| #1947 | Demo Autonomy Mode + EditorAgent brief fallback | 15-agent allowlist, 30/hr cap, brief defaults |
| #1948 | Demo mode banner + runbook + API endpoint | UI banner, `/api/system/demo-status/`, demo playbook |
| #1949 | PA payload context promotion for agent dispatch | workspace_id, content_type, tone flow through to agents |
| #1950 | EditorAgent gathers workspace deliverables | Auto-fetches workspace content for editing |
| #1951 | MetricsActionTrigger governor gate + Redis cooldown | Stopped hourly SystemIntelligence spam |
| #1952 | EditorAgent workspace fallback to active workspace | Prefers active non-system workspace |
| #1953 | Demo runbook — ContentWriter for synthesis, Editor for QA | Correct agent role assignments |
| #1954 | ContentWriter workspace research injection | Workspace deliverables as research context |
| #1955 | Always prefer active workspace over System Autonomous | Fixed workspace resolution for all agents |
| #1956 | Exclude blog outputs from workspace content gather | Prevented news contamination of research |
| #1957 | Demo runbook v2 — correct agent roles | SystemIntelligenceAgent for status synthesis |
| #1958 | PlatformAuditAgent prose output + synthesis instruction | Told GPT to synthesize, not echo JSON |
| #1959 | PlatformAuditAgent empty synthesis fallback | Fallback formatter for gpt-5-mini |
| #1960 | PlatformAuditAgent proper markdown formatter | Structured sections from tool results |
| #1961 | PlatformAuditAgent switch to gpt-5.2 | Reliable function calling (gpt-5-mini simulated tools) |

Note: PRs #1958-1961 were iterative fixes to PlatformAuditAgent output quality.

---

## Key Architecture Decisions

### Demo Autonomy Mode
- `DEMO_MODE=true` env var gates all agent execution to 15-agent allowlist
- 30/hr execution cap via Redis counter
- Defense-in-depth: checked in both `should_dispatch()` and `_impl_execute_agent_task()`
- Allowlist: PlatformAuditAgent, SystemIntelligenceAgent, ResearchAgent, TrendAnalysisAgent, CompetitorAnalysisAgent, OpportunityScoringAgent, ContentWriterAgent, EditorAgent, ContentStrategyAgent, SEOOptimizerAgent, ImageAgent, CTOAgent, COOAgent, ContentAuditAgent, PromptEngineeringAgent

### Agent Role Corrections
- **ContentWriterAgent**: Blog posts/newsletters from research (WRITER)
- **EditorAgent**: Reviews/polishes existing drafts against quality rubric (QA GATE)
- **SystemIntelligenceAgent**: Live platform status synthesis from attention items (STATUS)
- **PlatformAuditAgent**: Integration health, env config, DB counts (AUDITOR)
- **CTOAgent**: Technical analysis via PlatformContextService (EXECUTIVE)
- **COOAgent**: Operations analysis via PlatformContextService (EXECUTIVE)
- **TechnicalDocumentAgent**: Formal internal docs (DOCUMENTER) — needs investigation, LLM call failed

### Workspace Content Injection
- `_handle_agent_tool` in tool_dispatcher.py now:
  - Promotes payload fields into context (`_CONTEXT_PROMOTE_KEYS`)
  - Gathers workspace deliverables for EditorAgent (`context['content']`)
  - Injects workspace deliverables as research for ContentWriterAgent (`context['research']`)
  - Always prefers active non-system workspace over PA-injected System Autonomous Workspace
  - Excludes prior blog_post outputs from workspace gather

### MetricsActionTrigger Fixes
- Governor gate added before agent dispatch (`trigger_source='schedule'`)
- Cooldown persisted to Redis (was in-memory, reset on worker recycle)
- Disabled 6 conversation beat tasks that were consuming worker threads

---

## Dry Run Results (all passed)

| Agent | Time | Words | Content |
|-------|------|-------|---------|
| PlatformAuditAgent | 20s | 596 | Prose audit: integrations, config, DB, risks/greens |
| CTOAgent | 32s | 686 | "9.5% failure rate" — real telemetry analysis |
| COOAgent | 35s | 687 | Ops execution analysis + 24-hour timeline |
| SystemIntelligenceAgent | 61s | 674 | Live platform status brief with 7 recommendations |
| ContentWriterAgent | 173s | 1,218 | "Why Our AI Platform Audits Itself" — publishable |

---

## Real Issues Found by Agents (Fix List for Session 1091)

### P0 — Fix Before Demo
1. Agent timeout rate 1.9% vs 0.2% SLO
2. DEBUG=True on production
3. PlatformAuditAgent model/schema mismatch in audit queries

### P1 — Fix This Week
4. 87 pending action items, all unowned
5. 155 ACTIVE / 83 TRIAGE / 11 COMPLETED initiatives (WIP sprawl)
6. 315 stale suggestions >7 days
7. 130 gates active 74 days
8. AudioAgent blocked (ElevenLabs quota)
9. OpportunityPipelineAgent circuit breaker tripped
10. 1 unapplied migration (content.0046)

### P2 — Next Sprint
11. 3 missing API keys (DeepSeek, Replicate, TheOdds)
12. Feature flags unset
13. No standardized failure taxonomy
14. ResearchAgent volume amplifying dependency instability

Full fix list saved as deliverable in demo-testing workspace.

---

## Demo Readiness

- **Runbook**: `docs/playbooks/DEMO_HAPPY_PATH.md` — "A Platform That Knows Itself"
- **Workspace**: demo-testing (active, 9 deliverables including fix list)
- **Narrative**: Platform self-audits → multi-role analysis → governed decision → published content
- **All agents proven working on real data**
- **Demo mode toggleable via `DEMO_MODE=true`**

---

## Next Session Priorities

1. Work through the fix list (P0 first)
2. Run clean end-to-end demo with all fixes applied
3. Record the video
