# Session 2931 — Rigby Tool Gap Ledger #33 + #34 bundle

**Date:** 2026-07-24
**Merge SHA:** `53fb29c72` (PR #3497)
**Type:** Engineering — Rigby tool-surface fix + test-cost fix (S2931 candidate E per S2930 slate, Chris-selected)

---

## 1. What shipped

Two Rigby Tool Gap Ledger fixes in a single ~45-min bundle:

* **#34** — `on_agent_execution_completed` post_save receiver now short-circuits when `settings.TESTING` is True. `TESTING` hoisted to top-level `settings.py` attribute (auto-detected from `sys.argv` / `pytest` argv0 / `DJANGO_TEST_RUNNER_ACTIVE` env var). Prevents the learning-orchestrator fan-out (`_generate_optimizations` → downstream services → OpenAI) from firing per-row during test-suite fixture setup. `test_agent_runs_list_endpoint.py` alone was measured at ~77 hidden API calls per run.
* **#33** — `AgentExecution` added to `orm_inspect_tool._MODEL_POLICIES` allowlist. Complements the pre-existing `Agent` entry. Removes the 3× Django shell fallback pattern surfaced at S2930 recon. `task` + `error_message` flagged as `expensive_text_fields` (contains/icontains rejected on those columns).

---

## 2. Code changed

* `core/settings.py` — new top-level `TESTING` bool (~line 63); does NOT change the postgres-branch `_running_under_test()` helper (both must stay in sync going forward).
* `core/learning_bridges/agent_execution_bridge.py` — added `from django.conf import settings` import + receiver gate on `getattr(settings, 'TESTING', False)`.
* `core/services/td_handlers_agents.py` — new `AgentExecution` entry in `_MODEL_POLICIES` dict.
* `core/tests/test_s2931_ledger_33_34_bundle.py` — NEW, 8 regression tests:
  * `LearningBridgeTestingGateTests` (3): gate active under test mode, receiver still fires when `TESTING=False`, pre-existing status-gate still enforced.
  * `OrmInspectAgentExecutionTests` (5): list_models includes `AgentExecution`, describe_model returns correct policy, filter by status, count_by status, contains-on-expensive-field rejected.

**Net diff:** 4 files changed, +222/-1.

---

## 3. Post-merge verify (per PLAYBOOK-7.4.4)

* `gh pr merge --admin --squash --delete-branch 3497` — merged at `53fb29c72`.
* `make recycle-all` — clean recycle recorded (`sha=53fb29c725c8, surviving=none`).
* Rigby dispatch — two `orm_inspect_tool` calls succeeded live:
  * `list_models` — 12-model list returned; `AgentExecution` present alongside `Agent`.
  * `count_by AgentExecution field=status` — real live-DB output: **2,327 total executions** (completed 2,028 / failed 259 / cancelled 40). No Django shell required.
* **GATE PASSED.** #33 verified end-to-end via PA tool surface. #34 verified via test suite (S2930 endpoint tests re-ran with zero `learning_orchestrator` chatter in logs).

---

## 4. Governance

No governance decisions this session. D6 moratorium from S2842 unchanged. All S2925/S2926/S2927/S2928/S2929 forbidden entries carry forward. Zero new Fold candidates.

---

## 5. Rigby Tool Gap Ledger — status update

Both entries **RESOLVED** at PR #3497 (merge sha `53fb29c72`) in ledger deliverable `5c84e75a-0ce5-4f93-9da5-f6db4e53e7f0`:

* #33 — RESOLVED via allowlist expansion (chose the ~30 min quick-win over the ~1-2hr dedicated PA tool). Trade-off documented: single-model allowlist gets AgentExecution reachable now; a dedicated `agent_execution_query` tool remains a future option if usage reveals need for richer filter shape.
* #34 — RESOLVED via `settings.TESTING` gate (chose the ~15 min minimal fix over the ~30-min shared decorator or ~1-2hr async Celery task). Extension pattern reusable: any future signal receiver can gate on the same top-level `TESTING` attribute.

No new ledger entries this session.

---

## 6. Sweep progress tracker (unchanged)

* Slice 1 — `td_handlers_ops` (17 tools): UNCHANGED.
* Slice 2 — `td_handlers_agents` (25 tools): CLOSED S2912.
* Slice 3 — `td_handlers_core` (22 tools): CLOSED S2917.
* Slice 4 — `td_handlers_gateway` (17 tools): CLOSED S2924.
* Slice 5 — `tool_dispatcher` (14 tools): CLOSED S2928.

Total remaining tools to close: **15 across 8 handler files** (S2931 shipped no sweep work).

---

## 7. Session shape observations

* Clean iteration: orient → Chris ratifies lean → investigate → 3 edits → 8 tests → PR → merge → recycle → live verify → close. No F-BLOCKING SIGN needed, no zoom-out folds required, no scope drift.
* Pre-existing pyright drift observed in touched files (settings.py, td_handlers_agents.py, agent_execution_bridge.py) — all part of the queued "bundled dev-env drift slate," not introduced by this bundle.
* Wait-for-completion honored (`feedback_wait_for_agent_completions_before_close_cascade`): Rigby's two tool_runs completed synchronously (`orm_inspect_tool` is not async), no in-flight tasks at close-cascade start.
