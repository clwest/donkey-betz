# SESSION 2982 — Stage-Doc Guardrails + Enqueue Provenance + Status Consistency (S2981 Follow-up)

**HEAD at close:** `8e775913a` (PR #3619 merged; docs cascade PR TBD)

**Branch shape:**
- `s2982-stage-doc-guardrails-provenance` → main (merged, branch deleted)

**Deliverables (this session):**
- **Spec source:** `2a196415-19cf-4bda-87b5-1c4233a5cd9d` — ENGINEERING SPEC —
  Fix initiative stage doc generator (S2981 follow-up). Received from Chris at
  turn 1; no reframe needed.
- **Rigby Tool Gap Ledger append:** `5c84e75a-0ce5-4f93-9da5-f6db4e53e7f0`
  (workspace `b4503364-…`). Appended 1279 chars capturing Fold D
  (forward_carry: DB uniqueness constraint on `AgentExecution.celery_task_id`)
  post-T1 SIGN.

**Support conversation:** `pa-f9e61e81a2514104` (S2981 pin carried into S2982;
wrapper pin bumps at close).

---

## Three-part summary (Chris-facing)

**What was done.** Shipped bugfix + provenance + status-consistency patch
around `core.tasks.generate_initiative_stage_document` per the S2981-follow-up
spec. The observed Celery failure (Initiative.DoesNotExist from a ResearchAgent
binding directive that injected an unresolvable initiative_id, task_id
`6b836107-…`) is now caught at both enqueue-time and task-body-time. New
service module `core/services/initiative_stage_dispatch.py` exposes
`queue_stage_document_generation` — validates the initiative_id before
`.delay()`, writes a queryable `AgentExecution` provenance row capturing all six
correlation identifiers (task_name, celery_task_id, initiative_id, stage_id,
source_execution_id, trace_id), and returns a typed `{success, reason, error}`
outcome. All 8 existing `.delay()` callsites (integration service, hivemind
pipeline, auto-progression, kickstart view, beat backfill, regen sweep, two
management commands) routed through the helper. Task body now handles
`Initiative.DoesNotExist` / `ValidationError` / `ValueError` / `TypeError`
without retrying, with distinct reason codes (`initiative_not_found` vs
`invalid_initiative_id_format`) so operators can triage caller-bug from
deleted-initiative. `mark_task_outcome` reconciles the queue-provenance row on
every task exit branch — a Celery FAILURE can no longer surface as a completed
AgentExecution. PR #3619 merged as `8e775913a`; 15 regression tests pass;
`make celery-recycle` clean.

**How it improves the platform.** Before: a stale/deleted initiative_id
enqueued from an agent binding directive would fail once loudly (Celery
FAILURE) with no persisted trail linking the failure back to the caller. The
retry-on-Exception in the task's outer except would then mask non-transient
failures by scheduling a retry that could never succeed. Analytics dashboards
had no defense against synthetic system-provenance agents contaminating
top-performer lists. After: every stage-doc enqueue writes a durable
`AgentExecution` row queryable via ORM by celery_task_id, initiative_id, or
trace_id. Missing/malformed initiative_ids are refused BEFORE the broker sees
them. Status consistency is enforced end-to-end. Analytics excludes
`agent_type='system'` at both write layer (learning bridge early-return) and
read layer (three analytics view queries). New `agent_type='system'` namespace
is clean (zero existing agents use it).

**Next session first action.** Wait for Chris. Sensible next-arc candidates
unchanged from S2981 close (see 00-START S2983 seeds). No arc-specific
follow-up from S2982 — the bugfix is self-contained. Forward-carry: Fold D
(DB uniqueness constraint on `AgentExecution.celery_task_id`) logged to
Rigby Tool Gap Ledger `5c84e75a-…`; Fold B (misleading comment about
`deliverable_factory.py:509` at `tasks_initiatives.py:2229` and `:2938`,
actual dedupe at `:909`) is pre-existing S1186 cleanup, not this PR.

---

## Timeline

| Turn | Actor | Phase | Action |
|---|---|---|---|
| 1 | Chris | 0 | Hands over spec Deliverable `2a196415-…` + directive: "implement the spec, deliver a PR with tests" |
| 2 | Claude | 1 | Fetch spec via ORM (`Deliverable` model has `content` not `body_markdown` — first attempt failed; second attempt via `d.content` printed the full 5-AC body) |
| 3 | Claude | 1 | Explore: locate `generate_initiative_stage_document` in `core/tasks.py:11817` → `_impl_generate_initiative_stage_document` in `core/tasks_initiatives.py:2612`. Grep 8 `.delay()` callsites across services + views + management commands |
| 4 | Claude | 2 | Design: new `core/services/initiative_stage_dispatch.py` module with `queue_stage_document_generation` helper + `mark_task_outcome` reconciler. Persist provenance as AgentExecution row (synthetic `InitiativeStageDispatch` agent) — queryable via existing ORM without new tables |
| 5 | Claude | 6 | Implement: helper module written; task body guardrail added (catches `DoesNotExist` + `ValidationError` + `ValueError` + `TypeError`); success + soft-timeout + generic-except branches all call `mark_task_outcome`; all 8 callsites routed through helper |
| 6 | Claude | 6 | Write 15 regression tests: `QueueStageDocumentGenerationValidationTests` (6), `QueueStageDocumentGenerationProvenanceTests` (3), `MarkTaskOutcomeTests` (3), `StageDocumentTaskMissingInitiativeGuardrailTests` (3). Initial run failed on `Initiative.owner_id NOT NULL` — added `_make_owner` UnifiedUser fixture. Second failure: `.delay` patch targeted wrong module namespace — fixed by patching `core.tasks.generate_initiative_stage_document` (the definition site) instead of the dispatch module namespace. 15/15 pass in 0.5s |
| 7 | Claude | 6 | Branch `s2982-stage-doc-guardrails-provenance`; commit; push; open PR #3619 |
| 8 | Chris | 5 | "I forgot to have you orient yourself before you began" — confirmed session brief covered essentials; noted no Rigby SIGN yet |
| 9 | Chris → Claude | 5 | "yes route it to Rigby" — SIGN discipline reasserted |
| 10 | Claude → Rigby | 7 | T1 SIGN routing (§1 spec conformance / §2 callsite completeness / §3 test evidence / §4 zoom-out ask / §5 verdict). Explicit warning: no rubber-stamps, empty tool_runs = re-issue |
| 11 | Rigby → Claude | 7 | T1 turn 1: real tool_runs (deliverable_tool.detail, repo_tool.git_info, repo_tool.search, repo_tool.read_file × 5). AC1/AC2/AC3 SATISFIED with file:line; AC4 PARTIAL; AC5 code-exists-needs-run. Stopped mid-cycle — needed to run tests |
| 12 | Claude → Rigby | 7 | Re-route pushing for §3 + §4 + §5 with tool_runs. Explicit: no stopping mid-cycle |
| 13 | Rigby → Claude | 7 | T1 turn 2: §3 correctly refused (no shell access — didn't fake it). §4 zoom-out substantive: Fold A analytics contamination (verified `views_agent_analytics.py` uses `Agent.objects.all()` with no agent_type gate); Fold B misleading dedupe line comment (pre-existing); Fold C reason taxonomy collapse; Fold D missing DB unique constraint on celery_task_id. §5 provisional AGREE_WITH_REVISIONS pending §3 |
| 14 | Claude | 7 | Ran tests locally: 15/15 pass, exit 0. Applied same-PR folds A + C: gated `on_agent_execution_completed` on `execution_kind='stage_doc_enqueue'` OR `agent_type='system'` (learning bridge write layer); added `_ANALYTICS_EXCLUDED_AGENT_TYPES=('system',)` exclusion to three analytics view queries (read layer). Split exception branches for distinct `initiative_not_found` vs `invalid_initiative_id_format` reason codes. Tests re-verified 15/15 pass |
| 15 | Claude | 7 | Commit `8349579b6` (fold mitigations); push |
| 16 | Claude → Rigby | 7 | Closing SIGN turn with §3 test output pasted + §4 mitigations summarized + explicit fold classifications. Verdict request |
| 17 | Rigby → Claude | 7 | **AGREE** verdict. Fold B + Fold D forward_carry. No same_pr_actionable remaining. No escalation |
| 18 | Chris → Claude | 8 | "log fold D to the Rigby Tool Gap Ledger and merge" |
| 19 | Claude → Rigby | 8 | Ledger append routing — find ledger + append Fold D entry + confirm; do NOT merge |
| 20 | Rigby → Claude | 8 | Ledger `5c84e75a-…` found + appended 1279 chars (total 32588). Merge acknowledged not-attempted |
| 21 | Claude | 8 | `gh pr merge --admin --squash --delete-branch 3619` → merge commit `8e775913a`. `make celery-recycle` clean (5 workers + beat alive) |
| 22 | Chris → Claude | close | "close the session" |

---

## T1 SIGN cycle evidence

**Turn 1 tool_runs (Rigby):**
| # | Tool | Purpose | Result |
|---|---|---|---|
| 1 | `workspace_tool.status` | Confirm active workspace | `b4503364-…` Donkey Betz |
| 2 | `deliverable_tool.detail` | Fetch spec `2a196415-…` | Full 5-AC content read |
| 3 | `repo_tool.git_info` | Confirm branch | `s2982-stage-doc-guardrails-provenance` HEAD `2a04e0101` |
| 4 | `repo_tool.search` | `generate_initiative_stage_document.delay` grep | 1 match only (in the helper) — 8 callsites confirmed routed |
| 5 | `repo_tool.read_file` × 5 | Read new dispatch module + task body + factory + analytics view | Line-level citations for AC1/AC2/AC3 |

**Turn 2 tool_runs (Rigby):** 3 additional searches (agent_type distribution, owner_agent usage sites, deliverable_factory dedupe location at line 909 vs the commented 509).

**Zoom-out folds classified (§4):**
| Fold | Concern | Classification | Applied? |
|---|---|---|---|
| A | `InitiativeStageDispatch` synthetic agent will pollute agent-analytics dashboards (Agent.total_executions aggregated across all agents; no agent_type gate) | same_pr_mitigatable | ✅ Learning bridge early-return + analytics view exclusion |
| B | Misleading comment in `tasks_initiatives.py:2229/:2938` referencing `deliverable_factory.py:509` for dedupe — actual dedupe at `:909` | forward_carry | Pre-existing S1186 cleanup, not this PR |
| C | Single `initiative_not_found` reason code collapses caller-bug (malformed UUID) with race-condition (deleted initiative) | same_pr_mitigatable | ✅ Split into two reason codes; tests updated |
| D | No DB-level uniqueness constraint on `AgentExecution.celery_task_id` (currently just `db_index=True`, not `unique=True`) | forward_carry | ✅ Logged to Rigby Tool Gap Ledger `5c84e75a-…` |

**T1 verdict:** AGREE. Ratified by Chris. Merged via `gh pr merge --admin`.

---

## Files touched (12 total in PR #3619)

**New:**
- `core/services/initiative_stage_dispatch.py` (+352 lines) — dispatch helper
- `core/tests/test_initiative_stage_dispatch.py` (+433 lines) — 15 regression tests

**Modified:**
- `core/tasks_initiatives.py` — task body guardrail + `mark_task_outcome` calls (+109 / -18)
- `core/learning_bridges/agent_execution_bridge.py` — Fold A write-layer gate (+29 / -6)
- `core/views_agent_analytics.py` — Fold A read-layer exclusion (+20 / -6)
- `core/services/initiative_integration_service.py` — routed through helper (+24 / -6)
- `core/services/hivemind_execution_pipeline.py` — routed through helper (+23 / -5)
- `core/services/initiative_auto_progression.py` — routed through helper (+38 / -12)
- `core/views_initiative_kickstart.py` — routed through helper (+21 / -6)
- `core/tasks_misc.py` — beat backfill routed through helper (+25 / -6)
- `core/management/commands/backfill_stage_documents.py` — routed through helper (+24 / -6)
- `core/management/commands/trigger_stage2_generation.py` — routed through helper (+25 / -6)

Net: +1072 / -55 across two commits (`2a04e0101` implementation + `8349579b6`
fold mitigations).

---

## Post-merge verification

- `make celery-recycle`: default worker (solo) + pa worker (solo) + long_running
  worker (2 threads) + broadcast worker (2 threads) + code_jobs worker (solo) +
  beat scheduler — all alive after 8s cooldown. Verified via
  `ps aux | grep celery.*worker`.
- No live-dispatch smoke ran (test plan item deferred — bugfix is defensive;
  first real invocation via any of the 8 upstream callsites will exercise the
  new provenance shape).

Sensible smoke sequence for S2983 if Chris wants to close the loop:
1. Route a `deliverable_tool.create` for a fake initiative through the PA to
   trigger auto-progression, then confirm the queue-provenance row exists via
   `AgentExecution.objects.filter(owner_agent='InitiativeStageDispatch').order_by('-created_at').first()`.
2. Delete an initiative between enqueue and task pickup and confirm
   `mark_task_outcome` transitions the row to `failed` with `error_message`
   populated (may be flaky to time; simpler to unit-test the transition, which
   is already covered).

---

## Wrapper pin note

Active PA conversation pin at S2982 close: `pa-f9e61e81a2514104`.
`session_lifecycle close` at S2982 close retires that pin and mints a fresh
one for S2983; wrapper `tools/pa_local.sh` is rewritten atomically. Commit
the wrapper diff in the S2982 close cascade PR per
`feedback_commit_wrapper_pin_bump_at_close`.

---

## What this session validated about the workflow

- **PLAYBOOK-7.7.1 (spec→ship contract) held** on a real bugfix spec — Phase 1
  (spec grounding via ORM), Phase 2 (design of dispatch module + helper),
  Phase 6 (implement + tests), Phase 7 (T1 SIGN), Phase 8 (ship + close). Not
  every phase produced a formal artifact (Phase 2 was internal reasoning; no
  separate design doc) but the shape held.
- **PLAYBOOK-7.7.2 (SIGN evidence discipline) held twice** — first when
  Rigby's turn 1 stopped mid-cycle and I re-routed rather than accepted the
  partial verdict; second when I ran the tests locally to unblock Rigby's §3
  (she correctly refused to fake it). Zero rubber-stamps.
- **PLAYBOOK-7.7.3 (Chris-facing framing) NOT invoked** — Chris opened with
  a concrete implementation directive, not a decision menu, so Phase 5 was
  degenerate. Framing kicked in at fold-classification time (Chris asked "log
  fold D to the ledger and merge" — a single clear next-step, not a menu).
- **feedback_verify_rigby_tool_runs_before_trusting_sign held** — Rigby's
  turn 1 had 5 real tool_runs but stopped mid-cycle. I checked the raw
  tool_runs before accepting the verdict; the AGREE_WITH_REVISIONS on turn 2
  was backed by 8 total tool_runs across the two turns.
- **feedback_zoom_out_ask_per_rigby_sign held** — Rigby delivered 4 zoom-out
  folds; 2 same_pr_mitigatable applied at §2 revision before final verdict;
  2 forward_carry (one to the Ledger).
- **feedback_local_truth_no_production held** — `make celery-recycle` ran
  post-merge; no production observation window mentioned.
- **feedback_recycle_after_merge held** — recycle ran BEFORE close cascade,
  not after; workers verified alive.

No new feedback candidates from this session. The workflow is behaving as
codified.
