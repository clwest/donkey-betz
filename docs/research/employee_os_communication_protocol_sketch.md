---
title: "Employee OS Comms Protocol Sketch — Platform Auditor → Chief of Staff (research only)"
status: draft
session: 1268
date: 2026-06-30
mission_type: design_research
authority: |
  Design research only. No runtime code changes. No models.
  Reuse existing primitives or surface the gap. messaging_tool
  send_message stays OFF. v0 is one-way unless evidence supports
  two-way.
companion_docs:
  - docs/research/employee_os_communication_substrate_audit.md
  - docs/EMPLOYEE_OS_PRIMITIVES.md
  - docs/handoffs/SESSION_1267_EMPLOYEE_4_BUG_TRIAGE_SHIP.md
verifier_loop: |
  Doc grounded in direct file reads of jobs.py:388-966 (Platform
  Auditor + Chief of Staff JobContracts), comms.py (post_shift_report
  full source), comms_docs_manager.py (wrapper pattern),
  models_messaging.py:1-170 (MessageThread/Participant/DirectMessage),
  models_human_interface.py:1-180 (HumanAttentionItem). All
  primitives cited by file:line. Independent review by Rigby
  complete (S1268 PA conversation pa-01e90a1d36f54880): two
  SIGN-WITH-EDITS (cadence freshness in §7.4; L3 helper-side
  dedupe safety belt in §7.1), two clarifications (no HAI creation
  authority on Auditor; helper re-export idea), and confirmation
  on threading/authority/terminal-gate/contract semantics. Edits
  are folded into §7, §8, §10, §11, §12.
owner: claude (synthesis) + rigby (independent review, S1268)
---

# Comms Protocol Sketch — Platform Auditor → Chief of Staff

> **What this is.** A reuse-first design sketch for the *first*
> inter-employee write path in the Donkey Betz Employee OS. The
> S1268 substrate audit named Platform Auditor → Chief of Staff as
> the lowest-risk candidate; this doc gives that protocol a concrete
> shape grounded in existing primitives.
>
> **What this is not.** An implementation PR. A model. A schema
> change. An enablement of `messaging_tool.send_message`. A two-way
> dialog between AI employees. Authority enforcement (vs. warn-mode
> observation). A bridge across fleet apps. **None of that lands in
> v0.**

---

## 1. Executive Summary

The Platform Auditor runs **weekly** (proposed Monday 06:30 local,
per `jobs.py:461`) and produces a 6-section audit Deliverable. The
Chief of Staff runs **daily** at 07:00 America/Denver and synthesizes
1-3 Decision Cards from four lane pulls (`jobs.py:715-718`,
`jobs.py:732`). The cadences don't align: the Auditor's findings are
fresh on Monday brief, stale by Friday.

The protocol's job is to give the Auditor a **bounded, one-way,
fire-and-forget channel** to flag *significant* findings (not the
routine report — that's the existing Deliverable + shift-report DM
path) so a downstream employee (Chief of Staff) has structured input
when synthesizing tomorrow's brief.

**Reuse-only shape.** `MessageThread` + `DirectMessage` +
`ThreadParticipant` (`core/models_messaging.py:21-141`) carry the
notice. A new thin wrapper helper — call it
`post_inter_employee_notice()` for sketch purposes — would mirror
`post_docs_manager_shift_report()` (`comms_docs_manager.py:105-122`)
but key threads on `(source_employee, target_employee, topic)`
instead of `(employee, job)`. **No new model. No new tool. No new
schema.**

**v0 is strictly one-way.** Chief of Staff *consumes* the message
as inbox context (visible to Chris in `/inbox`). Programmatic
consumption from inside the `morning_brief` workflow is a follow-up
PR, not part of this protocol sketch.

**Authority handling.** S1264 warn-mode (per Rigby S1268 review:
"observational telemetry that *never blocks any mission*") already
covers cross-employee actions. The protocol does not require
enforcement to flip on. The new authority surface that *would*
need to land before any *consumer*-side reaction is the
`recommend_*` family on the Auditor — already declared as
`AuthorityLevel.RECOMMEND` for `recommend_remediations`
(`jobs.py:497`).

**HumanAttentionItem stays out of v0.** Findings that warrant
Chris's decision are already routed via the Auditor's existing
escalation Deliverable flip to `attention-required` status
(`jobs.py:605-607`). The inter-employee DM is for findings that
are *too low-severity* to demand a decision but *too significant*
to bury in the routine weekly report.

---

## 2. Candidate Use Case

### 2.1 The Auditor's existing output (today)

Per `jobs.py:415-656` and `jobs.py:520-571`, every weekly audit
produces:

- One `OpsRun(domain='mission', run_kind='platform_audit')` row.
- One audit `Deliverable` (always, not just on escalation,
  `jobs.py:569-571`).
- `summary` JSON with `findings_count` + `issues_found_count` +
  6 evidence keys (`docs_audited`, `integrations_audited_count`,
  `env_vars_checked_count`, `models_counted`, `report_deliverable_id`,
  `report_chars`).
- One `OpsRunEvent` per step (`step_start` / `step_pass` /
  `step_fail`) + `verdict_issued:certified` event.
- One shift-report DM via `post_shift_report()` into the
  `(platform_auditor, platform_audit)` thread.
- Routine "Top Risks" + "Green Checks" sections in the
  Deliverable (`jobs.py:451-452`).

### 2.2 The gap the protocol closes

Today's findings live in the audit Deliverable. Chief of Staff's
brief synthesis pulls four lane sources (`jobs.py:759-766`); the
audit Deliverable is **not** one of them. If the auditor flags
an integration that just lost credentials, an env var that flipped
to unset, or a sudden model-row collapse, that finding:

1. Surfaces in the Deliverable (Chris reads on Monday).
2. Surfaces in the shift-report DM (Chris's inbox).
3. Is **invisible to Chief of Staff** until Chris manually
   pastes it into a Lane 4 follow-up — i.e., it never auto-routes
   to "tomorrow's Decision Card."

The protocol creates a structured handoff for cases where the
Auditor's judgment is "Chief of Staff should know about this for
the next morning brief."

### 2.3 What kinds of findings qualify

**In scope for the protocol (Auditor SHOULD notify Chief of
Staff):**

- A previously-green integration just flipped to missing
  credentials (Lane 1 surface — platform readiness).
- A previously-set env var in a critical category (`api_keys`,
  `database`) flipped to unset between audits.
- A database-model count dropped by >X% week-over-week (signal
  of data loss / migration accident).
- A documentation drift count crossed a threshold (Rigby's
  cascade owns this surface; the Auditor flags it as
  cross-employee context if the docs cascade hasn't yet).
- Any "Top Risks" item that is *novel* (didn't appear in the
  prior week's audit).

**Out of scope for the protocol:**

- Routine "Top Risks" repeated week-over-week — already in the
  Deliverable; the morning brief can pick them up by reading
  the latest audit row directly (no DM needed).
- "Green Checks" sections — never noteworthy enough.
- Mission failures from the auditor itself — already covered
  by the existing escalation path (`jobs.py:600-613`).
- Findings that demand a *decision* — those are
  `HumanAttentionItem` shape, not inter-employee DM shape.

---

## 3. Existing Primitives Reused

| Primitive | File:line | Used as |
|---|---|---|
| `MessageThread` | `core/models_messaging.py:21-67` | Thread row; metadata-keyed lookup |
| `ThreadParticipant` | `core/models_messaging.py:69-96` | Per-user read cursor for Chris |
| `DirectMessage` | `core/models_messaging.py:99-141` | The notice itself; `sender_type='system'` |
| `post_shift_report()` | `core/employees/comms.py:228-367` | The shape to mirror — *not directly callable* (its `(employee, job)` keying + terminal-gate don't fit inter-employee semantics; new wrapper instead) |
| `_build_metadata` projection | `core/employees/comms.py:93-120` | Pattern to copy for bounded metadata projection |
| `_get_or_create_thread` | `core/employees/comms.py:159-209` | Pattern to copy with different match keys |
| `_existing_dm_for_mission` | `core/employees/comms.py:215-222` | Dedupe pattern — extend to include `dedupe_key` field |
| `comms_docs_manager.py` | `core/employees/comms_docs_manager.py:1-122` | Wrapper template — copy structure |
| `AIEmployee` dataclass | `core/employees/jobs.py:74-92` | Source + target employee identity |
| `OpsRun(domain='mission')` | `core/models_ops_runs.py:11-89` | Source mission reference |
| `OpsRunEvent` | `core/models_ops_runs.py:91-118` | New event label `inter_employee_notice_emitted` (info event) |
| `evidence_for_mission()` | `core/employees/status.py:347-508` | Postmortem join — extend to surface DM in the existing escalation block |
| `Deliverable` | `core/models_deliverables.py:84-283` | Source mission's existing audit Deliverable (referenced by ID, not modified) |

**Explicitly NOT reused:**

| Primitive | Why not |
|---|---|
| `messaging_tool.send_message` | OFF by design (`td_handlers_core.py:3694-3711`, returns `MESSAGING_SEND_DISABLED`). Free-form LLM outbound is the wrong shape for a structured inter-employee notice. |
| `conversation_orchestrator` | Multi-agent deliberation primitive — wrong shape (per `employee_os_communication_substrate_audit.md` §8). |
| `AgentFollowupSubscription` | Bridges agent terminal → chat banner. Wrong shape for inter-employee DM. |
| New `EmployeeMessage` / `EmployeeNotification` / `InterEmployeeNotice` model | `EMPLOYEE_OS_PRIMITIVES.md` §2 + §4.1 name these as anti-patterns. |
| `HumanAttentionItem` | Reserved for findings that demand a *human decision*. v0 inter-employee DMs are FYI only. |

---

## 4. Proposed Message Shape

### 4.1 Helper signature (sketch)

```python
def post_inter_employee_notice(
    *,
    source_employee: AIEmployee,
    target_employee: AIEmployee,
    topic: str,                       # e.g. "platform_audit_finding"
    source_mission_id: str,           # OpsRun.id from the producing mission
    body: str,                        # bounded markdown
    metadata_extras: Dict[str, Any],  # job-specific bounded keys
    severity: str,                    # "info" / "warning" / "critical"
    recommended_action: str,          # short imperative; <300 chars
    dedupe_key: Optional[str] = None, # finding signature; if absent, falls back to (thread, source_mission_id)
    requires_human_attention: bool = False,  # v0: log only — does NOT spawn HumanAttentionItem
    force_send: bool = False,         # bypass L3 7d helper-side dedupe; emits anyway (Rigby S1268 SIGN edit on §7.1)
) -> Dict[str, Any]:
    ...
```

Return envelope mirrors `post_shift_report()`:

```python
{
  "ok": bool,
  "created": bool,             # False on dedupe hit
  "skipped_reason": Optional[str],  # 'duplicate' / 'duplicate_within_window' / 'no_recipient' / 'authority_prohibited'
  "thread_id": Optional[str],
  "message_id": Optional[str],
  "dedupe_key_used": str,      # the resolved key (caller-supplied or derived)
}
```

### 4.2 Metadata envelope (the full set)

Required base keys (always present, mirrors
`BASE_METADATA_KEYS` at `comms.py:52-59` but with inter-employee
fields):

```python
{
  "source_employee":          source_employee.handle,      # "platform_auditor"
  "target_employee":          target_employee.handle,      # "chief_of_staff"
  "topic":                    topic,                       # "platform_audit_finding"
  "source_mission_id":        source_mission_id,           # UUID of the OpsRun
  "source_ops_run_id":        source_mission_id,           # alias, same value — kept for query symmetry with OpsRunEvent rows
  "source_deliverable_id":    summary.get("report_deliverable_id"),  # FK to audit Deliverable
  "severity":                 severity,                    # 'info' | 'warning' | 'critical'
  "recommended_action":       recommended_action,          # short imperative
  "requires_human_attention": requires_human_attention,    # bool
  "dedupe_key":               <resolved>,                  # see §7
  "emitted_at":               timezone.now().isoformat(),
  "expires_at":               <ISO-8601>,                  # Rigby S1268 SIGN edit: required base key, caller-set freshness boundary (see §7.4)
  "thread_kind":              "inter_employee_notice",     # discriminator
}
```

Caller-supplied `metadata_extras` is projected verbatim (bounded,
JSON-safe — same contract as `post_shift_report`'s
`extra_metadata_keys`, `comms.py:99-106`).

**Auditor-specific extras** (for `topic='platform_audit_finding'`):

```python
{
  "finding_ids":       List[str],     # IDs from the audit Deliverable
  "finding_count":     int,           # length of finding_ids
  "category":          str,           # 'integrations'/'configuration'/'database'/'documentation'
  "delta_from_prior":  Optional[str], # short diff string vs prior audit (e.g., "openai_credentials: configured→missing")
}
```

### 4.3 Body shape (bounded markdown)

The body is **bounded markdown** — not unbounded LLM output. The
wrapper formatter (similar to `comms_docs_manager.format_body()`,
`comms_docs_manager.py:39-99`) constructs from structured inputs:

```
[<SEVERITY>] <ONE_LINE_SUMMARY>

- Source: Platform Auditor mission <mission_id> (audit Deliverable <deliv_id>)
- Category: <category>
- Delta from prior audit: <delta_from_prior>
- Findings flagged: <finding_count> (IDs: <first 3>, ...)
- Recommended action: <recommended_action>

Reference: see audit Deliverable for full Top Risks + remediation detail.
```

Length cap: 1500 chars (well below the
`feedback_deliverable_tool_use_append_for_large_payloads.md`
6kB silent-fail threshold; well above triviality). Enforced
caller-side; helper does not validate.

### 4.4 Severity model

| Severity | Definition | Auditor source signal | Brief consumer behavior (future PR) |
|---|---|---|---|
| `info` | Noteworthy but not actionable this week | Status changes that didn't cross a threshold | Optionally surfaced in Lane 1 brief footer |
| `warning` | Should be on the operator's radar | Threshold crossed; remediation recommended | Considered for Decision Card synthesis |
| `critical` | Demands attention before next audit | Critical category flipped to broken | Promoted to Decision Card; Chris also gets HumanAttentionItem (separate path, not via this protocol) |

`critical` notices in v0 should also fire the Auditor's existing
escalation Deliverable flip to `attention-required` — that's the
Chris-visibility path. The DM is parallel to it, not a
replacement.

---

## 5. Threading / Routing Model

### 5.1 Thread keying

Per `comms.py:178-202`, the existing `post_shift_report` keys
threads on `metadata.employee + metadata.job` with
`thread_kind="employee_shift_report"`. For inter-employee
notices the key set changes:

```python
qs = MessageThread.objects.filter(
    metadata__source_employee=source_employee.handle,
    metadata__target_employee=target_employee.handle,
    metadata__topic=topic,
    metadata__thread_kind="inter_employee_notice",
    is_archived=False,
).order_by("created_at")
```

**Subject is ignored on lookup**, same as the existing pattern —
typos can't fork the thread.

### 5.2 Thread structure

One persistent thread per `(source_employee, target_employee,
topic)` triple. Concretely for the candidate use case:

- Single thread: `(platform_auditor, chief_of_staff,
  platform_audit_finding)` carries all weekly audit notices
  going to the Chief of Staff.
- If a future topic is added (e.g., `platform_audit_security_alert`),
  it gets its own thread on the same employee pair.
- If a future target is added (e.g., Auditor → Bug Triage), it
  gets its own thread.

This is **NOT** a "Chief of Staff inbox thread" or a "Platform
Auditor outbox thread" — it's a topic-specific channel between
two named employees. That keying matches Rigby's S1268 review
guidance (mirrors `post_shift_report` pattern with different key).

### 5.3 Routing decision — answering §2 of the spec

The mission spec asked: "Should the message go to (a) Chief of
Staff shift-report thread, (b) Platform Auditor thread, or (c)
a new topic-specific thread?"

**Answer: (c) — new topic-specific thread**, but in a
*per-employee-pair-per-topic* shape rather than a global inbox
channel. Rationale:

- (a) is wrong: Chief of Staff's shift-report thread carries
  *its own* mission summaries. Mixing inter-employee notices
  with self-shift-reports breaks the existing read-cursor
  semantics.
- (b) is wrong: Platform Auditor's shift-report thread is
  outbound to Chris (per `post_shift_report` semantics, the
  thread's participant is the human who reports-to the
  source). Adding a second AI participant changes the
  semantics from "shift report" to "topic channel."
- (c) is right because: new metadata keys, new
  `thread_kind`, deterministic lookup, doesn't pollute either
  existing shift-report thread.

### 5.4 Participants

In v0, both employees `runs_as_username="chris"` (per
`jobs.py:394` for Platform Auditor; `jobs.py:668` for Chief of
Staff). So `ThreadParticipant` only ever resolves to `chris`.
That's the right shape: Chris sees the inter-employee notice
in `/inbox` alongside the existing shift reports, with a
distinct `thread_kind='inter_employee_notice'` for filtering
in the UX. **No second participant in v0.**

If/when employees get dedicated User rows
(post-`v0 limitation` noted at `jobs.py:391-394`), the
participant set widens to include the target employee's
service account. **Out of scope for this sketch.**

### 5.5 sender_type on the DM row

`DirectMessage.SENDER_TYPE_CHOICES` (`models_messaging.py:119-128`)
has `user`, `rigby`, `system`. For inter-employee notices,
`sender_type='system'` is correct in v0 — same as
`post_shift_report`'s default (`comms.py:236`,
`sender_type: str = "system"`). The discriminator that
identifies *which* employee sent it lives in
`metadata.source_employee`. Adding `'employee'` as a
sender-type choice would be a model change → out of scope.

---

## 6. Evidence and Audit Trail

### 6.1 What proves the communication happened

Three rows, all reusing existing tables:

| Evidence row | What it captures | When written |
|---|---|---|
| `OpsRunEvent(label='inter_employee_notice_emitted', event_type='info')` on the **source** mission's OpsRun | Telemetry that the source employee tried to send; carries target_employee, topic, severity, message_id, dedupe_key in `detail` JSON | At helper-call time, regardless of outcome (sent/duplicate/skipped) |
| `DirectMessage` row + `MessageThread` row | The message itself + the persistent thread it lives in | At helper-call time, only on `created=True` |
| `ThreadParticipant.last_read_at` (existing field, `models_messaging.py:80`) | Whether Chris (the human reader) has actually viewed the thread since the message landed | Updated by `/inbox` view on read |

**Idempotency contract.** Same as `post_shift_report` —
`OpsRunEvent.objects.get_or_create(...)` for the event row
(idempotent on (run, label, detail.dedupe_key));
`DirectMessage` filter on (thread, metadata.dedupe_key)
before insert; same `created: bool` return shape.

### 6.2 Extending `evidence_for_mission()`

Per `core/employees/status.py:347-508`, the
`evidence_for_mission()` join already returns an `escalation`
block with `deliverable`, `deliverable_events`, and `pa_post`
(`evidence_for_mission()` return shape lines 485-508 per
audit doc §5). The natural extension is to add an
`inter_employee_notices` sub-block:

```python
"inter_employee_notices": [
  {
    "thread_id":         str,
    "message_id":        str,
    "target_employee":   str,
    "topic":             str,
    "severity":          str,
    "created_at":        ISO-8601,
    "dedupe_key":        str,
    "consumed_by_brief": Optional[dict],  # see §9.3
  },
  ...
]
```

This is a **read-side extension only** — the helper writes
the rows; the join surfaces them. Mechanical code change;
out of scope for this sketch but part of the v0 PR.

### 6.3 No new audit surface

Per `EMPLOYEE_OS_PRIMITIVES.md` §2 + §4.1, the existing
four audit surfaces (OpsRunEvent, DeliverableEvent,
LLMCallEvent, ToolCallRecord) are already a documented
"don't build a 5th." The protocol does not invent a 5th —
it borrows OpsRunEvent (existing) + DirectMessage metadata
(existing) and lets `evidence_for_mission()` (existing
read surface) join them.

---

## 7. Dedupe / Chatter Prevention

### 7.1 Dedupe layers

Three orthogonal layers, each addressing a different chatter
class:

| Layer | Key | Window | Catches |
|---|---|---|---|
| **L1: Per-(thread, dedupe_key)** | `thread + metadata.dedupe_key` | Forever | Same finding emitted twice (idempotent re-runs of the same audit mission) |
| **L2: Per-(thread, source_mission_id)** | `thread + metadata.source_mission_id` | Forever | Helper called twice for the same source mission (caller bug) — only used when `dedupe_key` is None |
| **L3: Per-(thread, dedupe_key, window)** | Cross-mission | 7 days (matches Auditor's 7-day rolling failure window, `jobs.py:537-541`) | Same finding-signature re-emitted from a fresh mission within 7d (e.g., openai_credentials missing for the second week in a row) |

L1 + L2 are helper-enforced (mirrors
`_existing_dm_for_mission()` at `comms.py:215-222`).

**L3 — Rigby S1268 SIGN-WITH-EDITS.** Original sketch put L3
caller-side only. Per Rigby's review: caller-side-only dedupe
assumes the caller is always correct; an Auditor-runner bug or
a retry storm becomes inbox spam. Updated contract:

- **L3 default = helper-enforced.** Helper queries
  `DirectMessage.objects.filter(thread=thread,
  metadata__dedupe_key=dedupe_key,
  created_at__gte=now - 7d)`. Any hit → skip with
  `skipped_reason='duplicate_within_window'`.
- **`force_send: bool = False` caller override.** Auditor (or
  any caller) can pass `force_send=True` to bypass the L3
  helper check — used for cases where the caller has its own
  judgment that the re-emit is intentional (e.g., severity
  upgrade from `warning` to `critical` on the same finding).
- **Caller-side L3 filter is STILL recommended** as
  defense-in-depth, but no longer the sole guard. Default
  protects the human inbox regardless of caller correctness.

### 7.2 Dedupe key construction (Auditor-specific)

The Auditor builds `dedupe_key` as a stable hash of the
finding-signature it's notifying about. Pattern mirrors
`MissionRunner.make_error_signature` (`mission_runner.py:177-350`):

```python
dedupe_key = hashlib.sha256(
    f"{category}|{finding_signature_normalized}|{delta_direction}".encode()
).hexdigest()[:16]
```

Where:
- `category` is one of `integrations`/`configuration`/`database`/`documentation`
- `finding_signature_normalized` is the auditor's finding label
  normalized (e.g., `openai_credentials_missing` not
  `OpenAI API key not configured (line 47)`)
- `delta_direction` is `improving`/`degrading`/`new`/`resolved`

Identical key on a fresh weekly mission → L3 caller-side
filter skips emission. New key (different finding) → fresh
DM, even if a prior finding for the same category is still
open.

### 7.3 Chatter ceiling per mission

Hard ceiling: **max 3 inter-employee notices per source
mission**, enforced caller-side. The Auditor's job is to
choose the 3 most-significant findings to notify on; the
rest live in the Deliverable. Rationale:

- Chief of Staff's brief surfaces 1-3 Decision Cards
  (`jobs.py:835-839`). More than 3 incoming notices per
  mission would swamp that synthesis.
- Three is the same cap Chief of Staff already uses for its
  own output, so the input shape mirrors the output shape.

### 7.4 Cadence mismatch handling

Auditor runs weekly; Chief of Staff runs daily. If the
Auditor emits a `critical` notice on Monday morning, the
Tuesday-through-Sunday morning briefs will see the same
notice in the thread (until next Monday's audit produces a
new one).

Two design choices:

- **Option A: Notice carries `expires_at` field** (caller-set
  to "next Monday audit + 24h"). The brief consumer filter
  drops expired notices.
- **Option B: Notice has no expiration; brief consumer filter
  matches on `emitted_at >= last_brief_run` to only show
  notices that landed since the prior morning brief.**

Both have prior art on the platform
(`HumanAttentionItem.expires_at` per
`models_human_interface.py:151` for A; standard "since last
run" pattern for B).

**Rigby S1268 SIGN-WITH-EDITS.** Original sketch default-leaned
B (consumer-side filter). Per Rigby's review: without a
protocol-level "freshness" boundary, a daily consumer can
re-surface the same notice repeatedly if the "since last run"
pointer drifts or bugs. **Updated default: A is the primary
safety belt** — notice carries `expires_at` in `metadata`
(caller-set to "next scheduled source mission run + buffer",
e.g., next Monday 07:30 local for the weekly Auditor). B is
fine as a *consumer optimization on top of A*, but not the
sole guard.

This makes the metadata envelope (§4.2) carry `expires_at` as
a *required base key*, not just an extra. Consumers MUST
honor it; helper does not validate beyond storing it.

---

## 8. Authority and Safety

### 8.1 Authority observation under warn-mode

Rigby S1268 review confirmed S1264 warn-mode "never blocks
any mission, single-employee or cross-employee"
(`mission_runner.py:258-275`, per
`employee_os_communication_substrate_audit.md` §5.5). The
inter-employee notice is therefore observable today without
enforcement plumbing.

When the Auditor invokes the helper, MissionRunner's existing
`authority_contract_observed` event (`mission_runner.py:264`,
emitted per-mission) already captures the source employee's
authority shape. The notice itself maps to the existing
`recommend_remediations` authority bucket on the Auditor
(`jobs.py:497`, `AuthorityLevel.RECOMMEND`).

**No new authority entry needed.** The existing `recommend_*`
family is the correct semantic: the Auditor is *recommending*
something to a downstream consumer, not executing on its
behalf.

**Rigby S1268 clarifier (no HAI creation authority).** The
Platform Auditor's `authority` dict (`jobs.py:489-505`) does
**not** grant `create_human_attention_item` or any
equivalent. That's consistent with §4.4 keeping HAI out of
v0: if the Auditor lacks the authority to create one, the
"critical finding needs decision" path must remain the
existing escalation-Deliverable flip to `attention-required`
(`jobs.py:605-607`). The inter-employee DM rides parallel to
that path, not as a substitute. If a future PR wants the
Auditor to create HAIs, it requires an explicit authority
entry in the contract — out of scope for this protocol.

### 8.2 Boundary check (helper-side)

The helper does NOT validate authority — `MissionRunner`
already emits the observation event, and warn-mode never
blocks. But the helper should fail-loud on two structural
violations:

- `source_employee.handle == target_employee.handle` (self-
  notice): raise `ValueError("inter-employee notice cannot
  target same employee")`. Catches caller bugs.
- `target_employee.handle not in known set`: log WARNING +
  return `skipped_reason='no_recipient'`. Mirrors the
  existing helper pattern at `comms.py:291-304`.

### 8.3 messaging_tool.send_message remains OFF

The helper is a **server-side direct ORM helper**, the same
shape as `post_shift_report` and `post_docs_manager_shift_report`.
It is **not** an LLM-callable tool. The LLM-side
`messaging_tool.send_message` stays OFF
(`td_handlers_core.py:3694-3711`, returns
`MESSAGING_SEND_DISABLED` unless
`settings.MESSAGING_TOOL_ALLOW_SEND=True`).

The Auditor's *agent code* (not LLM tool layer) decides
whether to invoke the helper at synthesis time. This keeps
free-form LLM outbound messaging off and confines the
inter-employee channel to deterministic, audited code paths.

### 8.4 What prevents the LLM from spamming the channel

Three locks:

1. **No LLM-callable surface.** Helper is direct ORM, not a
   PA tool. LLM cannot invoke it directly.
2. **Caller-side cap.** Auditor's agent code enforces "max 3
   notices per mission" (§7.3); LLM can recommend findings,
   but only the deterministic post-LLM code decides what
   actually emits.
3. **L3 dedupe.** 7-day cross-mission caller-side filter
   suppresses repeat findings.

If a future variant wants the LLM to decide *which* of the
auditor's findings to escalate (vs. the entire audit
synthesis layer deciding), the L3 dedupe still bounds the
chatter rate regardless of LLM judgment.

---

## 9. Receiving Employee Behavior

### 9.1 What Chief of Staff does in v0 (consumption shape — answering §5 of the spec)

The mission spec asked: "Should Chief of Staff consume this
as (a) inbox context only, (b) morning brief input,
(c) mission evidence, (d) future task trigger?"

**v0 answer: (a) — inbox context only.** Programmatic
consumption requires a code change to the `morning_brief`
workflow (new step, or new lane data pull). That's a
follow-up PR, not part of this protocol sketch.

The DM lands in the `(platform_auditor, chief_of_staff,
platform_audit_finding)` thread; Chris sees it in `/inbox`
(thread_kind filter `inter_employee_notice` separates from
shift reports). The morning brief's existing Lane 1
(platform readiness) and Decision Card synthesis run
unchanged in v0.

### 9.2 What Chief of Staff *should* do in a v0+1 PR

Add a step to `morning_brief` workflow:

- Step 5.5 (between Lane 4 and decision card synthesis):
  `read_inter_employee_notices` — queries the
  `(platform_auditor, chief_of_staff, *)` threads for
  unread DMs since the last brief run.
- Step 6 (`decision_card_synthesis`): receives the unread
  notices as an additional input source. Notices with
  `severity='critical'` are promoted to Decision Card
  candidates; `warning` notices are surfaced in the brief's
  Lane 1 footer; `info` notices are referenced as
  "audit footnote" links to the source Deliverable.

**Why a separate PR:** changing the morning brief workflow
needs its own contract review, test plan, and Rigby
co-sign. This sketch deliberately keeps the consumer side
unchanged so v0 is observable (Chris sees DMs in inbox)
without changing the brief.

### 9.3 Consumption telemetry (when v0+1 lands)

When the morning brief consumes a notice, it records:

```python
# In DM metadata (new key, not a schema change — metadata is open JSON)
"consumed_by_brief": {
    "brief_mission_id":   str,         # UUID of the morning brief OpsRun
    "consumed_at":        ISO-8601,
    "consumed_severity":  str,         # severity at time of consumption (in case caller-side re-classification ever lands)
    "outcome":            str,         # 'promoted_to_decision_card' / 'surfaced_in_lane_1' / 'noted_as_footnote'
}
```

This makes `evidence_for_mission()` on the *brief* mission
naturally surface "what inter-employee inputs shaped this
brief" without joining the source mission. The same key
also lets the *Auditor's* `evidence_for_mission()` show
"was this notice acted on by a downstream employee."

### 9.4 No reply path in v0

Per the spec's required constraint ("Keep v0 one-way unless
evidence supports two-way flow"): the Chief of Staff does
not reply. The thread is one-way; the DM has no response
slot.

If the brief decides to *act* on a notice (promote to
Decision Card), that action surfaces in the brief
Deliverable + the `consumed_by_brief` metadata key — not as
a reply DM. Two-way would conflate "communication" with
"orchestration" and is explicitly out of scope.

### 9.5 No automatic Bug Triage trigger

If the Auditor flags a database-count anomaly and Bug
Triage also runs daily (`jobs.py:1093`, run_kind
`bug_triage_daily`), there is *no* automatic Auditor → Bug
Triage handoff in this protocol. Bug Triage already
*reads* OpsRun rows from the other employees as evidence
(per audit doc §5.2). If Bug Triage needs structured
notices later, it gets its own
`(platform_auditor, bug_triage_specialist, ...)` thread —
not a fan-out from this one.

---

## 10. Explicit Non-Goals

To prevent scope creep before the protocol PR lands, the
following are explicitly **not** part of v0:

1. **No new model.** No `EmployeeMessage`,
   `InterEmployeeNotice`, `EmployeeChannel`,
   `EmployeeNotification` table. `MessageThread.metadata` +
   `DirectMessage.metadata` carry the shape.
2. **No new PA tool.** Helper is direct ORM, not LLM-callable.
   `messaging_tool.send_message` stays OFF.
3. **No new authority entry.** Existing `recommend_*` family
   on the Auditor covers the semantic.
4. **No reply path.** v0 is one-way fire-and-forget.
5. **No `HumanAttentionItem` spawn.** That's reserved for
   findings that demand a human *decision*; protocol is
   FYI between employees.
6. **No automatic Chief of Staff workflow consumption.**
   That's the v0+1 PR. v0 lands the helper + Auditor caller;
   consumer is inbox-only.
7. **No two-way handshake or ack.** Chief of Staff doesn't
   confirm receipt programmatically. Chris's read cursor
   (`ThreadParticipant.last_read_at`) is the only "was it
   seen" signal.
8. **No fan-out.** Auditor → Chief of Staff only. Auditor →
   Bug Triage / Rigby comes later if evidence supports.
9. **No cross-fleet messaging.** v0 lives inside
   `donkey-betz` only. Sibling fleet apps don't see this
   thread or these DMs.
10. **No authority enforcement flip.** Warn-mode stays warn.
    If/when authority enforcement lands, it lands as its
    own design effort, not bundled into this protocol.
11. **No schema change to `DirectMessage.sender_type` enum**
    (e.g., adding `'employee'`). `'system'` is the right
    discriminator for v0; the source employee identity
    lives in `metadata.source_employee`.
12. **No WebSocket "new inter-employee DM" event.** The
    `/ws/system-events/` consumer (per
    `EMPLOYEE_OS_PRIMITIVES.md` row 22) doesn't carry DM-
    arrived events today; v0 doesn't add one.
13. **`force_send` is for callers, not the LLM.** The
    helper's `force_send=True` override (Rigby S1268 SIGN
    edit, §7.1) bypasses the L3 7d helper-side dedupe. It
    is **not** an LLM-callable parameter — only callable
    from deterministic agent code (e.g., the Auditor's
    severity-upgrade path). The helper has no LLM-callable
    surface in any case (per §8.3); naming it here so
    nobody backdoors it.

---

## 11. Open Questions

To resolve with Rigby + Chris before the protocol PR is
scoped:

1. **Cadence-mismatch handling: Option A (expires_at) vs
   Option B (since-last-run filter)?** §7.4 names both with
   prior-art examples. **Rigby S1268 answer:** Option A is
   the primary safety belt (caller-set `expires_at` in
   metadata, now a required base key per §4.2); Option B is
   fine as a consumer-side optimization on top of A but not
   the sole guard. Closed.

2. **Is "max 3 notices per source mission" the right cap?**
   Rationale is brief surfaces 1-3 Decision Cards. Could
   reasonably argue 5 or "no cap; trust the Auditor's
   synthesis." Default-lean: 3 (matches output shape).

3. **Should `critical` notices ALSO spawn a
   `HumanAttentionItem`?** §4.4 keeps them out of v0 on the
   reasoning that the Auditor's existing escalation
   Deliverable flip handles that. But Chief of Staff
   acting on a critical notice means Chris doesn't see it
   in his attention queue until the brief surfaces it.
   Default-lean: NO `HumanAttentionItem` in v0; revisit
   only if evidence shows critical notices land too late.

4. **L3 caller-side dedupe (7 day): is 7 days right, or
   should it match the audit cadence (weekly = 7 days
   anyway)?** Notice that 7d also matches the Auditor's
   own 7-day trust-status-under-review window
   (`jobs.py:537-541`). Default-lean: 7 days.

5. **`thread_kind="inter_employee_notice"` as the
   discriminator — should it be more specific, e.g.,
   `"inter_employee_audit_finding"`?** More specific gives
   sharper inbox filters; less specific scales to other
   topic pairs. Default-lean: keep `inter_employee_notice`
   generic; differentiate via `metadata.topic`.

6. **Should the helper live in `core/employees/comms.py`
   alongside `post_shift_report()` or a new
   `core/employees/comms_inter_employee.py` file?**
   `post_shift_report` lives in `comms.py`; the pattern is
   one file per "comms shape." Inter-employee is a new
   shape. **Rigby S1268 answer:** new file is right —
   `comms.py` already encodes shift-report semantics and the
   sketch explicitly notes those semantics don't fit
   inter-employee, so splitting reduces accidental reuse.
   Optional discoverability nicety: re-export
   `post_inter_employee_notice` from `comms.py` as a thin
   `from .comms_inter_employee import post_inter_employee_notice`
   so callers find it from one well-known module. Default-lean
   for v0: skip the re-export (one source of truth); add only
   if a second caller surfaces and discoverability becomes a
   real friction.

7. **When the Auditor's mission is *itself* failing (post
   escalation), should it still emit inter-employee
   notices about its findings?** Probably not — but the
   helper doesn't currently enforce. Could add a
   "source mission must be `passed` verdict before emit"
   gate in the helper. **Rigby S1268 answer:** enforce.
   Stricter-than-shift-report is appropriate because this
   notice is meant to be a *trusted summary signal*, not a
   streaming debug channel. Emitting mid-run produces
   partial / false positives. Backed by both contracts'
   "silent success" semantic (Auditor `jobs.py:453-456`,
   CoS `jobs.py:738-740`). Closed.

8. **`DirectMessage.sender_type='system'` is reused. Should
   a follow-up PR add `'employee'` as a sender_type
   choice?** Out of scope for this sketch but worth naming
   so the next PR considers it. The UX implication is how
   `/inbox` renders the sender label.

9. **Does the inbox UI need a new filter for
   `thread_kind='inter_employee_notice'` so these don't
   mix with shift reports in Chris's view?** Yes,
   logically — but that's a frontend ticket, not part of
   the protocol PR. Flag for handoff.

10. **Should the protocol have an explicit
    "decommission / archive" path** for when a topic is
    deprecated? Not for v0 — `MessageThread.is_archived`
    handles it manually. Flag if topic churn ever
    materializes.

---

## 12. Recommendation

**v0 protocol scope** (one PR, with Rigby review at the
SIGN-WITH-EDITS line before opening):

1. New file `core/employees/comms_inter_employee.py`
   (~200-250 lines): defines `post_inter_employee_notice()`
   with the contract in §4 — including the `force_send`
   override (Rigby S1268 SIGN edit) and `expires_at`
   required base key (Rigby S1268 SIGN edit).
2. New caller-side hook in `core/tasks_platform_audit.py`
   (or wherever the Auditor synthesis lives): after step 5
   (generate_audit_report), evaluate findings, build
   dedupe keys + `expires_at` (next Monday + buffer), call
   helper for up to 3 notices. Caller-side L3 filter is
   defense-in-depth (helper has the primary L3 guard).
3. New `OpsRunEvent` label
   `inter_employee_notice_emitted` (no model change —
   `OpsRunEvent.label` is a CharField). Tests assert event
   row written on every emit/skip.
4. Extend `evidence_for_mission()` (per §6.2) to surface
   the new `inter_employee_notices` sub-block.
5. Tests:
   - L1 + L2 dedupe (helper-side).
   - **L3 helper-side 7d dedupe** (Rigby SIGN edit) +
     `force_send=True` override path.
   - terminal-gate on source mission (per §11 Q7, Rigby
     confirmed).
   - `expires_at` populated on every emit; consumer-side
     filter (when v0+1 lands) honors it.
   - `evidence_for_mission()` includes new sub-block.
   - thread key resolution (right thread for repeat
     emits; new thread per topic).
   - HAI is **NOT** created (regression guard against §4.4
     drift).

**v0 does NOT include:**

- Chief of Staff workflow consumption (v0+1 PR).
- Inbox UI filter for inter-employee threads (frontend
  ticket).
- `HumanAttentionItem` integration (deferred unless
  evidence demands).
- Fan-out to additional target employees (deferred until
  v0 proves itself).

**Pre-PR gate:**

- Rigby SIGN-WITH-EDITS on this sketch (§11 questions
  answered with explicit defaults).
- Chris sign-off on the use case scope (§2.3).
- Confirm Auditor's authority `recommend_remediations`
  (`jobs.py:497`) is the right semantic bucket.

The independent review from Rigby is pending — see
`verifier_loop` block in the frontmatter and the open PA
chat thread on `pa-01e90a1d36f54880`.

---

## Appendix A — Evidence integrity notes

- Doc grounded in direct file reads (Claude, S1268):
  - `core/employees/jobs.py:388-656` (Platform Auditor
    JobContract — full body, including required_summary_keys,
    evidence_tables, authority, escalation_visibility,
    dedupe_rule)
  - `core/employees/jobs.py:662-966` (Chief of Staff
    JobContract — same depth)
  - `core/employees/comms.py:1-368` (full source of
    `post_shift_report` + constants + helpers)
  - `core/employees/comms_docs_manager.py:1-122` (full
    wrapper pattern)
  - `core/models_messaging.py:1-170`
    (MessageThread / ThreadParticipant / DirectMessage)
  - `core/models_human_interface.py:1-180`
    (HumanAttentionItem — confirmed wrong shape for v0)
- Rigby's S1268 review additions verified by Claude:
  - `core/employees/jobs.py:489-505` (Auditor authority
    dict — confirmed no `create_human_attention_item`
    entry; `recommend_remediations` at line 497 is
    `AuthorityLevel.RECOMMEND`)
  - `core/employees/jobs.py:453-456` (Auditor "silent
    success" + escalation-on-failure responsibility)
  - `core/employees/jobs.py:738-740` (Chief of Staff
    "silent success" + escalation-on-failure
    responsibility)
  - `core/employees/jobs.py:459-465` (Auditor cadence —
    weekly proposed Monday 06:30)
  - `core/employees/jobs.py:714-718` (Chief of Staff
    cadence — weekday daily 07:00 Denver)
- Two SIGN-WITH-EDITS from Rigby's review materially
  changed the protocol (§7.1 L3 → helper-enforced with
  `force_send`; §7.4 cadence default → Option A
  expires_at). Edits are folded into §4.1, §4.2, §7.1,
  §7.4, §11 Q1, §12, and §10 row 13.
- No code changes were made writing this sketch.
- All "should" / "would" language in §4-§9 describes a
  protocol that does not yet exist; all "today" / "is"
  language describes runtime state verified by file read.
