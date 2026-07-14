---
title: "SESSION 2782 — substrate fix (frontend detection in recycle-all) + C1 observability (AgentExecution.celery_task_id)"
session: 2782
status: closed
date: 2026-07-14
close_prs: [3176, 3177]
close_pr_merge_shas: [1f4c22f89, b2595ee7b]
arc: substrate_plus_observability
predecessor: SESSION_2781_N17_SESSION_NUMBER_PILL_SEARCH_CHIP.md
---

## §1. What shipped

**Two engineering ships in one session** (~1h), triggered by Chris eyeball-verifying prior UI ships (last-mile-UI rule paying off in real time).

**PR #3176 · `1f4c22f89` — substrate fix: `make recycle-all` frontend detection**

- Extends `recycle-all` to `grep`-detect `frontend/(src/|package(-lock)?\.json|vite\.config|tsconfig|index\.html)` in `git diff --name-only HEAD~1..HEAD` and, when matched, invoke `make frontend-build` + `collectstatic` before the `restart` step. Backend-only diff → no npm churn.
- Narrative paragraph appended to Playbook §7.4.4 naming the *served-artifact freshness* anti-pattern class. Explicitly marked non-rule; codification deferred pending an independent third trigger.
- Pin refresh: `tools/pa_local.sh` → `pa-29d72ab149344edd`.
- Zoom-out ledger row 23: `close_ceremony_served_artifact_freshness` (`same_pr_actionable`, mitigated same-PR).

**PR #3177 · `b2595ee7b` — C1 observability: `AgentExecution.celery_task_id`**

- Nullable indexed `celery_task_id` CharField on `AgentExecution`.
- `pre_save` signal receiver auto-populates from `celery.current_task.request.id` on create. Never overwrites; swallows any failure; bypassed by `bulk_create` (no such sites exist today).
- Migration `0384_s2782_agentexecution_celery_task_id.py` — hand-written after Django autogen bundled 38 unrelated model-drift operations.
- Enables cross-referencing SLO breaches (e.g., "Agent wall-clock timeout rate") back to `CeleryTaskEvent` for root-cause diagnosis of the false-positive-timeout hypothesis.

**Files touched (5):** `Makefile`, `docs/ENGINEERING_PLAYBOOK.md`, `tools/pa_local.sh`, `core/models_unified_system.py`, `core/migrations/0384_s2782_agentexecution_celery_task_id.py`.

---

## §2. Novel-precedent moment

**Last-mile UI rule paid off in real time and cascaded into a substrate fix.** The session opened with the routine eyeball-verify candidate for S2780 (N22 v3) + S2781 (N17) UI ships. Chris hit a blank page — bundle dated Jul 11 vs sources dated Jul 13. Root cause: `make recycle-all` per PLAYBOOK-7.4.4 refreshes Celery processes but never touched `frontend/dist/` or bounced Daphne. **Two consecutive UI ships (S2780 + S2781) had shipped invisible to the browser** without anyone noticing until Chris looked.

The fix (PR #3176) closes that gap forward. Then the same session, opening the ops console UI now that it renders, surfaced a live SLO breach (Agent wall-clock timeout rate = 7.14%) which drove PR #3177 (C1 observability). One eyeball verification → one substrate fix + one observability substrate. This is the tightest last-mile → substrate feedback loop observed so far.

**First substrate fix triggered by a `feedback_last_mile_ui` payoff, not a joint SIGN cycle or a memory-rule trigger.**

---

## §3. SIGN cycle for PR #3176 (substrate fix)

| Slot | Verdict | Notes |
|---|---|---|
| Design (A/B/C options: extend recycle-all vs separate target vs wait-for-third) | AGREE on A | Joint recommendation with Rigby |
| V5 zoom-out (mandatory per 6.10.7) | 1 fold classified + persisted | See §4 |

**Anti-rubber-stamp gate PASS** — Rigby returned **5 tool_runs** verifying the framing: `repo_tool.search` ×2, `search_docs` ×1, `zoom_out_tool.list` ×2 (the latter dogfooding the S2780 N22 v3 read surface for the second consecutive session).

Chris D-verdict: "Approved."

**PR #3177 (C1 observability) shipped without a joint SIGN cycle** — after B/C/D investigation reached a clear diagnosis, Chris D-verdict "Proceed with C1" authorized direct execution. Different mode than PR #3176 (SIGN was for the substrate design question; C1 was execution of a decided path).

---

## §4. V5 zoom-out fold (per PLAYBOOK-6.10.7 + 6.10.8)

| # | Fold | Classification | Mitigation |
|---|---|---|---|
| Row 23 | Close-ceremony substrate gap class: `make recycle-all` refreshes processes but can miss *served artifacts* (frontend build outputs + Django staticfiles manifest). When frontend/src changes, failing to run `npm run build` + `collectstatic` + bounce Daphne can ship a blank/old UI even though backend code is updated. Generalizes into a "served-artifact freshness" checklist/automation: static assets, WhiteNoise manifest, Beat schedule reload, template caching layers. | `same_pr_actionable` | Mitigated same-PR via git-diff detection in `recycle-all` |

Ledger state at close: **23 rows** (12 same_pr_actionable + 8 same_pr_mitigatable + 3 future_trigger).

---

## §5. Verification

- **Regression 6-suite:** 82/82 PASS (skipping `test_session_freshness_2775` known env-drift on this machine — see §7 forward-carry).
- **Signal semantics tested** (5 scenarios):
  - no-celery context → field NULL
  - in-celery context → auto-populated
  - update on existing row → not overwritten
  - explicit `celery_task_id` on create → not overwritten
  - broken celery import → save works, no exception
- **Migration 0384** applied cleanly. Field present on model, all 1728 pre-existing rows NULL (signal is forward-only).
- **`make recycle-all` post-merge for both PRs** — both clean, self-test of the new logic (backend-only diff → npm build correctly skipped both times).
- **Chris eyeball verify** — N22 v3 SIGN Ledger tab + N17 pill both render after PR #3176 + manual `npm run build` + `collectstatic` + daphne bounce at S2782 mid-session.

---

## §6. Ledger state at close

- **23 rows total** (22 baseline from S2781 + 1 substrate fold from S2782 SIGN)
- Counts: 12 same_pr_actionable / 8 same_pr_mitigatable / 3 future_trigger

---

## §7. Open items rolled forward to S2783

**From S2781 close still open (unchanged unless noted):**
- P0.5 cost-threshold, P0.75 CI billing
- S2758 D1/D2/D4/D5
- S2761 smoke test (ops-surface, gated)
- N13 handoff-date-format normalizer
- HMAC signing of `x-acting-user-id`
- 30+ lambda-`__import__` sites in `core/urls.py`
- N15 v2 / N21 v2 candidates (deferred)
- First observed partial-recycle event (N10/N11 trigger)
- Rigby S2774 forward-carry ops-surface pause (still held; both S2782 ships were backend/infra, unaffected)
- Postgres cleanup follow-ups (S2774 carryover)
- Chris eyeball verification of prior UI ships — **NOW CLOSED for N22 v3 + N17** (via S2782 opening)
- Wire GovernanceTab into WorkspacePageNew (dead-code cleanup, ~50 LOC)
- N17 smart-command-box creep (row 21 `future_trigger`)
- Second non-Rigby consumer of `zoom_out_tool`
- Autonomous Rigby consultation of `zoom_out_tool.list`
- N24 anti-rubber-stamp SIGN codification — Playbook MINOR, 2 triggers observed
- I-0302 three-PR pattern amendment → PLAYBOOK-6.10.9 slot
- First graceful-degradation clause activation on PLAYBOOK-6.10.8

**New from S2782:**
- **AudioAgent completion-flip verification** — C1 linkage is live. Next AudioAgent (or any agent) timeout in the wild will land with a `celery_task_id` populated. One-query join to `CeleryTaskEvent` verifies whether the underlying task actually succeeded (proving/disproving the false-positive-timeout hypothesis). If confirmed false-positive, follow-up PR patches the completion-flip leak — likely in AudioAgent, possibly in the parent `AiSeriesWorkflowAgent` at `core/agents/ai_series_workflow_agent.py:1310`.
- **`test_session_freshness_2775` environmental drift** — S2782 saw 91/92 (one fail) on the 7-suite regression when workers weren't running locally at test time. The test asserts `staleness_error` key is set on `UNKNOWN` verdict; when no daphne/celery running, verdict is `UNKNOWN` without that key. Not a code regression, but worth flagging for either (a) test-side guard that skips when workers aren't up, or (b) computation-side always-populate `staleness_error` even on cold-start UNKNOWN.
- **Ledger split drift** observed at S2782 open (S2781 §6 declared 12/8/2, actual was 11/8/3). Either the S2781 handoff §6 miscount or a post-close reclassification. Non-blocking; not investigated. Current split is 12/8/3.
- **Model drift bomb** in `makemigrations core` — the Django autogen produced 38 unrelated operations (haidispatchlog, narrative, narrativeshift, etc.) on a fresh migration invocation. Hand-writing was correct for this PR; but the drift signals accumulated model-vs-DB divergence that will trip up any future migration author. Candidate for a housekeeping arc: run `makemigrations` in an isolated branch, review the 38 ops, decide which are legitimate vs abandoned.

---

## §8. Session pin

- Pin history: `pa-29d72ab149344edd` (label `s2782-eyeball-verify-shipped-ui`)
- Minted S2782 open (candidate scoped to eyeball-verify, which scope-crept in-session)
- Retired at S2782 close (`force=true`, per S2770+ pattern — thirteenth consecutive)
- Wrapper `tools/pa_local.sh` will retain the retired pointer — intended failure mode forces fresh mint at S2783 open

---

## §9. Meta-observation

**Scope-creep-that-worked pattern.** S2782 opened as a routine "eyeball verify shipped UI" candidate. That surfaced a substrate defect (frontend staleness), which cascaded into a substrate fix (PR #3176), which revealed the ops console (now rendering), which surfaced a live SLO breach, which drove an observability substrate fix (PR #3177). Three distinct problems, one causal chain, ~1h total. Every scope expansion was authorized by Chris in single-turn (approvals: "Approved", "Let's go with D", "Proceed with C1") — no ambiguous drift.

**Two-in-a-row cadence.** S2781 was a deliberate palate-cleanser between substrate arcs. S2782 was the opposite: eyeball-triggered substrate work that fell out of a nominally-small last-mile check. Cadence is not converging on any single rhythm; the arc-vs-cleanser split is opportunistic, driven by what Chris walks into at open.

**Last-mile-UI rule now has a concrete "why-we-write-it-this-way" example.** `feedback_last_mile_ui.md` said: "Chris watches backend work live and trusts it's done — but if he can't SEE and USE it in the browser, it's not done." S2782 open proved the case: TWO shipped UI features (N22 v3, N17) had passed CI, code review, SIGN cycles, and merge — and had been INVISIBLE for 2 sessions. The rule is not paranoia; it's load-bearing.

**S2771-rule streak now spans 12 sessions (S2771–S2782)** with 3 F-BLOCKING DISAGREEs, 1 constitutional codification (v0.7.0), and 12 in-wild joint SIGN cycles. Row 23 is the first substrate-scoped fold classified `same_pr_actionable` that was mitigated in the SAME session but in a DIFFERENT PR from the trigger (the trigger being Chris's eyeball at session open, not a coding activity). Small but distinct precedent.

**Anti-rubber-stamp gate held again** — second consecutive session with Rigby using `zoom_out_tool.list` inside her T1 verification (dogfooding the S2780 N22 v3 substrate). The "truer signal" — autonomous consultation without user direction — remains unobserved.
