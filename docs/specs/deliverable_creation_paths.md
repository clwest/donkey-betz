---
title: "Deliverable creation paths — provenance status enumeration"
status: active
last_updated: 2026-06-20
session: 1184
companion_docs:
  - PLATFORM_INVENTORY.md
  - handoffs/SESSION_1184_DELIVERABLE_PROVENANCE_LINKAGE.md
  - handoffs/SESSION_1184_PR_B_BASEAGENT_PROVENANCE_WIRING.md
owner: rigby-and-claude (recon + table from Claude; sequencing input from Rigby Session 1184 PR-B card)
---

# Deliverable creation paths

> **Why this exists.** Session 1184's e4f4e12f deliverable §1 asked for "a
> definitive list of code paths/functions, plus which payloads they
> accept." This is that list, captured per Rigby's Q3 recommendation —
> produce as a side effect of the sweep so the artifact tracks reality
> instead of drifting.
>
> **Scope.** Every production callsite of
> `core.services.deliverable_factory.create_deliverable` (or its
> `_save_to_deliverable` wrapper on `BaseAgent`). Excludes tests, factory
> docstring examples, and the factory's own internal call from
> `deliverable_append_service` fallback.
>
> **Provenance status legend:**
> - ✅ **wired** — passes a real `parent_execution_id` (or
>   `_execution_context['execution_id']` for BaseAgent subclasses post
>   Session 1184 PR-B)
> - 🟡 **synthesized** — PA/user-direct path, factory creates an
>   `AgentExecution` receipt on the fly (Session 1184 PR-A)
> - ⚠️ **WARN** — soft-enforce bucket, `parent_object_id=NULL`, fires the
>   factory's caller-fingerprint WARN. Target for PR-B sweep.

## Coverage summary

| Bucket | Count | Status after Session 1184 |
|---|---:|---|
| BaseAgent-derived agents (via `_save_to_deliverable`) | ~80 | ✅ wired by PR-B (one-line fix in `base_agent.py:4266` + router hoist) |
| PA-direct (deliverable_tool, content_tool, etc.) | 5 | 🟡 synthesized by PR-A (factory creates receipt) |
| Management commands | 5 | ⚠️ WARN — PR-B sweep target |
| Web views | 4 | ⚠️ WARN — PR-B sweep target |
| Tasks (Celery) | 3 | ⚠️ WARN — PR-B sweep target |
| Service-level helpers | 5 | ⚠️ WARN — PR-B sweep target |
| Other tools | 2 | ⚠️ WARN — PR-B sweep target |

## Wired paths (PR-B fix covers them)

The BaseAgent path is the single point that covers all ~80 routable
agents at once. Detail breakout per priority agent only — full list
lives in `core/agent_router.AGENT_MAP`.

| Callsite | Agent / class | Trigger source | Provenance source | Test |
|---|---|---|---|---|
| `core/agents/base_agent.py:4383` (`_save_to_deliverable`) | All `BaseAgent` subclasses | `agent_execution` (auto-tagged by factory when `parent_execution_id` present) | `self._execution_context['execution_id']` set by `core/agent_router.py:1433` before `execute()` / `execute_with_workspace()` | `core/tests/test_base_agent_provenance_wiring.py` covers ContentWriter / BlogWriter / Editor / ContentStrategy / Distribution |

## Synthesized paths (PR-A handles them automatically)

| Callsite | Agent | Trigger source | Provenance source |
|---|---|---|---|
| `core/services/td_handlers_agents.py:1922` (PA `_handle_deliverables` create) | PersonalAssistant or caller-supplied `agent_name` | `pa_tool` | Factory synthesis — `_synthesize_pa_execution_receipt` creates `AgentExecution` row with `status=completed`, `owner_agent=<agent>` |
| `core/tasks_conversations.py:3514` (conversation summary) | `PersonalAssistant` | auto-tagged `user_request` (agent_name match) | Factory synthesis |
| `core/services/td_handlers_core.py:586` (PA research+create) | `PA_IDENTITY` | `user_request` | Factory synthesis |
| `core/services/td_handlers_core.py:2010` (PA memory pin) | `PA_IDENTITY` | `user_request` | Factory synthesis |
| `core/services/td_handlers_newsletter.py:495` (Newsletter config) | `NewsletterTool` | `pa_tool` (when invoked via PA gateway) | Synthesized if `trigger_source=pa_tool` in metadata, else WARN |

## ⚠️ WARN bucket (PR-B sweep targets)

Each row needs a deliberate fix: thread an execution id from caller, or
opt into synthesis explicitly. The WARN log line carries the
caller-fingerprint (`caller=<file>:<line>:<function>`) to make the sweep
fast.

### Management commands

| Callsite | Agent | Notes for sweep |
|---|---|---|
| `core/management/commands/register_external_repo.py:325` | `REPO_PROFILE_AGENT_NAME` | Script context — likely opt into synthesis with `trigger_source='direct'` |
| `core/management/commands/survey_external_repo.py:277` | `persona["agent_name"]` | Same — opt into synthesis |
| `core/management/commands/draft_repo_verifier_claims.py:277` | `CTOAgent` | Same — opt into synthesis |
| `core/management/commands/refresh_repo_context.py:448` | `SNAPSHOT_AGENT_NAME` | Same — opt into synthesis |
| `core/management/commands/import_patent_disclosures.py:213` | varies (uses `**defaults` spread) | Same — opt into synthesis |

### Web views (HTTP request context)

| Callsite | Agent | Notes for sweep |
|---|---|---|
| `core/views_workspace_templates.py:315` | `User` | User-triggered web action — opt into synthesis with `trigger_source='user_request'` |
| `core/views_diagnostics.py:2389` | `cockpit-operator` | Incident write — opt into synthesis with `trigger_source='direct'` |
| `core/views_diagnostics.py:3338` | `cockpit-autopilot` | Same as above |
| `core/views_demo_pipeline.py:194` | `DemoPipeline` | Demo path — opt into synthesis with `trigger_source='direct'` |

### Celery tasks

| Callsite | Agent | Notes for sweep |
|---|---|---|
| `core/tasks_content.py:244` | `VideoContentPackAgent` | Has Celery task context but no AgentExecution row created. Either (a) thread execution_id from task args, or (b) create an AgentExecution at task start |
| `core/tasks_initiatives.py:2149` | `TechnicalDocumentAgent` | In initiative stage flow — has Initiative + stage_num context. Best to create an AgentExecution per stage and pass its id |
| `core/tasks_initiatives.py:2770` | `InitiativePipeline` | Same pattern as above |

### Service-level helpers

| Callsite | Agent | Notes for sweep |
|---|---|---|
| `core/services/implementation_executor.py:349` | `WorkflowUpdateHandler` | Service-level — opt into synthesis or thread execution from caller |
| `core/services/implementation_executor.py:645` | `ConfigUpdateHandler` | Same |
| `core/services/conversation_initiative_pipeline.py:536` | `ConversationOrchestrator` or `participants[0]` | Has conversation context — should pass conversation-derived execution id |
| `core/services/conversation_deliverable_extractor.py:357` | `ConversationOrchestrator` or `participants[0]` | Same |
| `core/services/workspace_pipeline_runner.py:456` | varies by stage | Has stage/agent context — create AgentExecution per stage |
| `core/services/mission_control_executor.py:241` | `attention_item.source_agent` or `MissionControlExecutor` | Has attention_item context — derive execution id from item |
| `core/services/deliverable_envelope.py:260` | varies (generic helper) | Need to find callers of `deliverable_envelope` and decide per-caller |

### Other tools

| Callsite | Agent | Notes for sweep |
|---|---|---|
| `core/services/td_handlers_core.py:2906` | `competitor_comparison_tool` | Tool-dispatched — trace_id present but no execution. Opt into synthesis with `trigger_source='pa_tool'` |
| `core/services/deliverable_append_service.py:374` | varies (fallback for superseded initiative) | Already accepts `execution_id` parameter — caller responsibility |

## Read surface — the `provenance` block

Every deliverable detail response includes a normalized `provenance`
block (Session 1184 PR-A), regardless of which bucket the deliverable
was created from:

```json
"provenance": {
  "origin_execution_id": "<uuid|null>",
  "trigger_source": "<str>",
  "created_by_agent": "<str>",
  "trace_id": "<uuid|null>",
  "tool_calls": [{"id", "tool_name", "success", "latency_ms", "created_at"}, ...],
  "legacy_no_provenance": true|false,
  "synthesized": true|false
}
```

- `legacy_no_provenance=true` → the deliverable hit the ⚠️ WARN bucket above
- `synthesized=true` → the deliverable used the 🟡 PA-direct factory synthesis
- Both false → the deliverable was ✅ wired with a real execution context

## Future steps

1. **PR-B sweep (Session 1185+):** work through each ⚠️ row above. Pick
   per-callsite: opt into synthesis (`trigger_source` flag in metadata)
   or thread real execution context. Update this table as each callsite
   moves out of the WARN bucket.
2. **PR-C contract flip (Session 1186+):** once WARN volume reaches zero
   after a 24h cooldown, flip the factory contract from
   `logger.warning(...)` to `raise DeliverableProvenanceMissingError(...)`
   for non-PA contexts. The synthesis path stays for PA-direct creates.
3. **Drop legacy `_current_execution_id` attr:** after a release cycle
   with the dict-guard fallback in `base_agent.py:4266`, drop the
   fallback to the legacy attr name. Only `core/tests/test_carryforward_fixes.py`
   references it today.
