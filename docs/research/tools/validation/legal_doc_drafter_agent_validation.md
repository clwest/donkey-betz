# `legal_doc_drafter_agent` — Validation Report (S2910)

**Tool:** `legal_doc_drafter_agent`
**Schema:** `core/services/pa_tool_schemas.py:1461`
**Handler:** `core/services/td_handlers_agents.py:295` (`_handle_legal_agent`)
**Register site:** `core/services/tool_dispatcher.py` (via `AgentHandlersMixin`)
**Session:** S2910 (Path B systematic sweep — Slice 2 batch 5 of `td_handlers_agents`)
**HEAD at validation:** `e642c7aa8` (2026-07-23)
**Ship shape:** Doc-only (S2796 shape). Regression tests deferred.
**Category upgrade target:** `untested` → `validated_partial` (actionless — no schema `action` enum; single-verb async dispatch surface. MUTATION-class end-to-end path is not exercised at doc-only sweep — see §5a).
**Rigby SIGN:** S2910 T0 SIGN AGREE-with-edits (batch 5 composition); S2910 T1 SIGN pending — see §Related.
**Template variant:** sweep
**Template version:** v1

---

## 1. Purpose / when-to-use

Async dispatch of the platform's Legal Document Drafter agent (Session 1035; hardened S2803 Phase 3.0). Answers "draft a legal document for me" — contracts, NDAs, terms of service, cease-and-desist letters, etc. The tool queues a Celery task on the `legal` queue via the shared `dispatch_legal_draft` helper; the actual drafting happens asynchronously, and progress is checked via `task_breakdown_tool`.

Distinct from the Web UI path (`POST /api/legal/draft/`) only in transport — S2803 Phase 3.0 unified both surfaces through `dispatch_legal_draft`, so both callers share the same `disclaimer_acknowledged` gate + `LegalDocumentDispatchLog` audit row.

Because legal drafting is domain-sensitive (mistaken advice can create real liability), the tool enforces an explicit disclaimer acknowledgement: callers MUST set `disclaimer_acknowledged=True` in payload root OR in the `context` nested dict. Absence → `error_code='disclaimer_required'` error envelope. This is the gate; Rigby / PA should confirm the user understands "this is not legal advice" before setting the flag.

## Covered actions

**This tool is actionless by schema design** — `schema_action_count=0` per T1a harness artifact (`docs/audits/pa_tools/harness_output/legal_doc_drafter_agent.json`), no `action` enum declared at `pa_tool_schemas.py:1467-1475`. The dispatch surface is a single implicit `draft_legal_document` call parameterized by `task` (description) + optional `document_type` + optional `context`.

Therefore `## Covered actions` is intentionally empty. S2910 batch 5 validates actionless-shape via `TOOL_DEFAULTS` seed (`MUTATION` — dispatches Celery job that generates a legal-document artifact + writes `LegalDocumentDispatchLog` audit row). Same pattern as `web_fetch_tool` for shape (actionless via TOOL_DEFAULTS), but with a MUTATION classification because of the persistent side effects.

## 3. Schema notes

- **Required (declared):** `task` (string; the legal document task description).
- **Optional (declared):**
  - `document_type` (string; type of legal document, e.g. `nda`, `contract`, `letter`).
  - `context` (object; additional context passed through to the agent).
- **Handler-side load-bearing implicit fields:**
  - `query` (fallback alias for `task` at handler line 311 — `task_description = payload.get('task') or payload.get('query', '')`).
  - `disclaimer_acknowledged` (bool; payload root OR `payload.context` — line 314-317). **Load-bearing gate — see §5a.**
  - `conversation_id` (string; payload root OR `payload.context` — line 318-322 → passed to `dispatch_legal_draft` as `client_session_pin`).
  - `context` dict passed through to `dispatch_legal_draft` (line 348).
- **User scoping:** requires an authenticated user (line 331-332). Anonymous dispatch returns `{success: false, error: 'Authenticated user required for legal drafting.'}` at line 333.

## 4. Golden-path examples

**"Draft an NDA for a contractor engagement" (disclaimer acknowledged):**

```
legal_doc_drafter_agent  task="Draft a mutual NDA for a 3-month contractor engagement covering deliverable IP and confidentiality."  document_type="nda"  disclaimer_acknowledged=true
```

**"Draft a cease-and-desist letter" (with context):**

```
legal_doc_drafter_agent  task="Draft a cease-and-desist for trademark infringement by <competitor>."  document_type="letter"  context={"prior_correspondence": "..."}  disclaimer_acknowledged=true
```

**Successful dispatch response (async):**

```json
{
  "agent": "LegalDocDrafterAgent",
  "action": "draft_legal_document",
  "mode": "async",
  "task": "<task_description>",
  "task_id": "<celery.task.id>",
  "dispatch_log_id": "<LegalDocumentDispatchLog.uuid>",
  "message": "Legal document drafting has been queued. This typically takes 1-3 minutes. Use task_breakdown_tool to check progress."
}
```

**Progress polling:** the caller uses `task_breakdown_tool` (or `agent_control_tool` / `execution_history_tool`) with the returned `task_id` to poll completion.

## 5. Failure / empty-state / pagination notes

- **No authenticated user** — returns `{agent, action, success: false, error: 'Authenticated user required for legal drafting.'}` at line 333.
- **`disclaimer_acknowledged` missing / falsy** — `dispatch_legal_draft` raises `DisclaimerRequired`; handler returns `{agent, action, success: false, error_code: 'disclaimer_required', error: <exc str>, message: '<usage guidance>'}` at line 350-362. The `message` field explicitly says: *"Legal drafting requires explicit disclaimer acknowledgement. Include `disclaimer_acknowledged=true` in the tool call payload after confirming the user understands this is not legal advice."*
- **`dispatch_legal_draft` returns `success: false`** — handler passes through the returned dict wrapped with `{agent, action}` at line 364-369.
- **Empty `task`** — the handler does NOT explicitly reject; it passes `task_description = ''` through to `dispatch_legal_draft`. The dispatch helper is the last-line-of-defense for empty-task rejection (out of scope this ship — deferred to `dispatch_legal_draft` audit).
- **Async progress fetch** — success response includes `task_id` + `dispatch_log_id`; the caller polls via `task_breakdown_tool`. This tool does NOT block on completion.

**Inline envelope pattern:** returns `{success: false, error_code, error}` at HTTP 200 — same shape as `web_fetch_tool` inline envelope failures. Under the S2909 T1 harness classifier this would classify as `soft_error` — but the tool is actionless so the harness emits 0 rows and this only affects real-caller behavior.

## 5a. Mutation containment

- **Mutating actions:** the entire tool is mutating — dispatches a Celery task on the `legal` queue AND writes a `LegalDocumentDispatchLog` audit row at the boundary of `dispatch_legal_draft`. The Celery task itself generates artifacts + updates state.
- **Safety metadata:** seeded in `TOOL_DEFAULTS` at S2910 with `default_safety_class='MUTATION'`, `applicability='conditional'`. Notes: `deps: dispatch_legal_draft → Celery legal queue + LegalDocumentDispatchLog audit; gate: disclaimer_acknowledged=True; actionless schema`.
- **Multi-layer gate:** authenticated user + explicit disclaimer acknowledgement + non-empty task. Any failure returns the inline `{success: false, error_code}` envelope with actionable guidance in `message`.
- **Audit trail:** every dispatch attempt (successful OR gated-rejected) SHOULD produce a `LegalDocumentDispatchLog` row — this ship does not re-audit the `dispatch_legal_draft` internals but the Session S2803 Phase 3.0 shape put the audit at the shared helper so both PA and Web UI callers hit it.
- **Deferral rationale:** MUTATION-class end-to-end dispatch is not exercised at doc-only sweep (would require an authenticated user + real `dispatch_legal_draft` invocation + Celery task consumption + LLM cost + Legal-queue slot). Deferred to a future MUTATION-coverage batch that pairs with a `dry_run` / seeded-user harness pattern.

## 6. Evidence

### 6.1 T1a harness artifact — this ship

`docs/audits/pa_tools/harness_output/legal_doc_drafter_agent.json` at HEAD `e642c7aa8` (harness run 2026-07-23):

```json
{
  "actions": [],
  "harness_version": "v2",
  "schema_action_count": 0,
  "tool_name": "legal_doc_drafter_agent"
}
```

Expected shape for actionless tools — zero rows.

### 6.2 Handler-trace evidence — this ship

Handler at `td_handlers_agents.py:295-382`:

- Line 311: `task_description = payload.get('task') or payload.get('query', '')` — `task` primary, `query` fallback alias.
- Line 312-322: extract `context`, `disclaimer_acknowledged` (payload root OR nested context), `client_session_pin` (from `conversation_id` — payload root OR nested context).
- Line 324-338: authenticated-user resolution; anonymous → `{success: false, error: 'Authenticated user required for legal drafting.'}`.
- Line 340-349: `dispatch_legal_draft(user, task_description, disclaimer_acknowledged, ip_address=None, user_agent='', client_session_pin, context)`.
- Line 350-362: `DisclaimerRequired` exception → `{success: false, error_code: 'disclaimer_required', error, message}`.
- Line 364-369: `success: false` passthrough with `{agent, action}` wrapping.
- Line 371-382: async success envelope with `task_id` + `dispatch_log_id` + progress-guidance `message`.

### 6.3 Runtime-not-executed — this ship

- **Successful dispatch** — not exercised (would require authenticated user + real `dispatch_legal_draft` invocation + Celery task consumption + LLM cost).
- **`DisclaimerRequired` path** — not exercised at handler level. Trace-only.
- **`dispatch_legal_draft` internals** — S2803 Phase 3.0 shared helper; audited at that ship's scope, not re-audited here.
- **`LegalDocumentDispatchLog` row shape** — not exercised; documented via handler trace only.
- **Async task progress polling via `task_breakdown_tool`** — out of scope.

---

## Related

- **Ledger candidates surfaced this ship:** none new. The tool has been through S1035 initial ship + S1062 async migration + S2803 Phase 3.0 disclaimer-gate unification; behavior is well-specified.
- **Adjacent tools:**
  - `task_breakdown_tool` — polls progress on the returned `task_id`.
  - `agent_control_tool` — pulls agent-execution state (see S2892+ validation doc when it lands).
  - `execution_history_tool` — historical row lookup for completed drafts.
  - `deliverable_tool` — where the generated draft artifact typically lands (workspace deliverable).
- **Substrate context:** part of S2910 batch 5. Uniform-safety MUTATION actionless tool — the most write-heavy of the 4 tools in this batch. Rigby T0 SIGN Q4 named `legal_doc_drafter_agent` alongside `schedule_followup` and `brainstorm_tool.create` as the 3 stateful-dispatch actions in this batch requiring explicit-opt-in gating; the disclaimer gate is the explicit-opt-in mechanism for this tool. Batch 5 peers: `web_fetch_tool`, `schedule_followup`, `brainstorm_tool`.
- **Prior work:** S1035 initial ship, S1062 async migration to Celery, S2803 Phase 3.0 disclaimer-gate + audit-log unification.
- **Related design docs:** S2803 Phase 3.0 shared `dispatch_legal_draft` helper.
- **Metadata seed:** `TOOL_DEFAULTS` entry at `core/services/tool_action_metadata.py` this ship (Pattern A — uniform safety class + actionless).
