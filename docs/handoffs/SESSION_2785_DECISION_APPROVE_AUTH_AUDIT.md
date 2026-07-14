---
title: "SESSION 2785 — decision-approve auth audit: staff-only gate /api/human/* + /api/boardroom/* (C-lite)"
session: 2785
status: closed
date: 2026-07-14
close_prs: [3183]
close_pr_merge_shas: [130955ec]
arc: fold4_decision_approve_audit
predecessor: SESSION_2784_FOLD4_PLATFORM_STAFF_ONLY.md
---

## §1. What shipped

**Continuation of the S2783 → S2784 → S2785 authZ arc.** S2784 gated the 12 `/api/platform/*` mutation endpoints; S2785 closes the two remaining gaps surfaced by Chris's S2784 eyeball question about the DecisionDetailModal Approve/Dismiss buttons.

**PR #3183 · `130955ec` — decision-approve authZ (C-lite)**

- `core/views_human_interface.py`:
  - Added `user_passes_test` import
  - Added module-level `_human_staff_only` gate mirroring `_platform_staff_only` (S2784) + `_governance_staff_only` (S2780)
  - Swapped 15 `@method_decorator([csrf_exempt, login_required], name='dispatch')` → `@method_decorator([csrf_exempt, login_required, _human_staff_only], name='dispatch')`
- `core/views_agent_learning.py`:
  - Extracted `_require_boardroom_staff(request)` helper — preserves S887 Token auth codepath (session OR Token → is_staff), returns `JsonResponse | None`
  - Replaced 4 inline auth blocks on `promote_decision`, `reject_decision`, `bulk_promote_decisions`, `bulk_reject_decisions` with `err = _require_boardroom_staff(request); if err: return err`
- `core/tests/test_decision_approve_auth_regression_2785.py` (new 358 lines):
  - 15 anon-blocked + 15 non-staff-blocked `/api/human/*` tests
  - 4 anon-blocked + 4 non-staff-blocked `/api/boardroom/*` tests
  - 4 staff-reachable smoke tests
  - 3 route-inventory guard tests
  - **45 tests total**
- `tools/pa_local.sh`: pin refresh to `pa-ad6b2c423b514728` (retired at close).

**Not touched:** `views_diagnostics.py` (`cockpit_approve_decision` already `@superuser_required`, tighter than staff — no change needed).

**Files touched (4):** `core/views_human_interface.py`, `core/views_agent_learning.py`, `core/tests/test_decision_approve_auth_regression_2785.py`, `tools/pa_local.sh`.

---

## §2. Novel-precedent moments (two)

**(a) Fold-authoring drift RECURRED — 2nd trigger.** Investigation began with a claim that boardroom endpoints were "completely ungated." Rigby's tool_read of `views_agent_learning.py:2105-2195` revealed inline authN with S887 Token auth fallback. Original characterization would have justified the wrong scope of fix. Same phenomenon as S2784 Fold 31. **Two triggers observed → Playbook amendment candidate:** codify fold-authoring hygiene rule (check both decorator AND inline code state before recording a fold's characterization).

**(b) Third arc-session in a row.** S2783 wired GovernanceTab → discovered dead code + surfaced authZ concern → S2784 gated 12 platform mutations → surfaced during eyeball that Approve buttons hit a different (unaudited) surface → S2785 audits + gates the /human/* + /boardroom/* decision surface. Each session's eyeball-verify or close-cycle finding drove the next session's P0. **Longest same-arc-continuation streak observed** — 3 sessions of continuous authZ work, no gap sessions, no scope drift.

---

## §3. The C-lite scope decision

**Options presented to Chris:**
- A: AttentionDecideView only (1 endpoint) — closes exact Chris question; leaves 19 similar endpoints inconsistent
- B: All 15 `/api/human/*` views (1 file) — parallels S2784 shape
- C: B + 4 boardroom endpoints (2 files) with **decorator** gating
- **C-lite: B + 4 boardroom endpoints with inline helper** (preserves S887 Token auth codepath)

**Chris D-verdict: C-lite** — "go with your suggestions."

C would have broken the Token auth codepath. The `@login_required` decorator redirects unauthenticated users to `/accounts/login/` (302) BEFORE the view executes. Token auth callers would receive a redirect instead of their expected 200/400/500. Extracting the inline helper preserves the exact same authN flow (session first, then Token fallback) with an added is_staff gate.

**Design principle established:** when adding staff-only gating to endpoints with non-standard authN (e.g., Token auth fallback, custom middleware), extract an inline helper rather than layering decorators. Decorator gating requires DRF-style permission_classes which is a bigger refactor.

---

## §4. SIGN cycle

| Slot | Verdict | Notes |
|---|---|---|
| Design (A/B/C/C-lite) | **C-lite** AGREE | Joint recommendation with Rigby; Chris D-verdict |
| V5 zoom-out (PLAYBOOK-6.10.7) | 3 folds classified + persisted | See §5 |
| Anti-rubber-stamp gate | **PASS** — 6+ tool_runs | repo_tool.read_file × 4, repo_tool.search × 3, search_docs, zoom_out_tool.list |

Rigby's SIGN response text got truncated at the persist step (long tool_run outputs consumed the response window), but tool_runs verified the state independently. Folds persisted BEFORE Chris D-verdict per PLAYBOOK-6.10.8. Anti-rubber-stamp gate PASS on grounded verification.

---

## §5. V5 zoom-out folds (per PLAYBOOK-6.10.7 + 6.10.8)

Ledger state at close: **34 rows** (15 same_pr_actionable + 13 same_pr_mitigatable + 6 future_trigger).

| # | Concern | Classification | Notes |
|---|---|---|---|
| 32 | **Fold-authoring discipline drift RECURRED** (2nd trigger of S2784 Fold 31). Initial audit claimed boardroom endpoints were "completely ungated" — Rigby tool_read revealed inline authN + Token auth. Original framing would have justified wrong scope. | same_pr_mitigatable | **2 triggers observed → Playbook amendment candidate.** Consider: "when recording a fold that names a specific gap, verify the gap's actual character (decorator AND inline code state) before recording." |
| 33 | Auth posture inconsistency across decision-approve surface — 3 different patterns (@superuser_required / @method_decorator([csrf_exempt, login_required]) / inline authN with Token fallback). No consistent standard. | same_pr_actionable | C-lite consolidates 19 non-superuser endpoints to S2772 N16 contract. |
| 34 | Token auth codepath preservation on boardroom endpoints — inline helper (`_require_boardroom_staff`) rather than decorator gating that would redirect Token requests. Design principle: for endpoints with non-standard authN, extract inline helper; don't layer decorators. | same_pr_actionable | Encoded in the ship. |

---

## §6. Verification

- **Syntax:** `python -c "import ast; ast.parse(...)"` — both files clean
- **New test file:** `test_decision_approve_auth_regression_2785` — 45 tests OK (0.508s)
- **Full 4-suite auth sweep:** `test_ops_auth_regression_2772` + `test_governance_auth_regression_2780` + `test_platform_auth_regression_2784` + `test_decision_approve_auth_regression_2785` — **93 tests OK** (1.582s), no cross-file regressions
- **Live curl on Daphne** — 4 endpoints returned 401 for anon:
  - `POST /api/human/attention/*/decide/`
  - `GET /api/human/attention/`
  - `POST /api/boardroom/decisions/bulk-promote/`
  - `POST /api/boardroom/decisions/*/promote/`
- **Chris E2E verified:** opened DecisionDetailModal from Self-Healing tab, **approved one decision + dismissed one — both functional** under new gate (Chris is staff+superuser)
- **Post-merge `make recycle-all`:** clean recycle at sha=`130955ec07ea`, surviving=none. Backend-only diff, no frontend rebuild triggered. **Twenty-second close-cycle post-PLAYBOOK-7.4.4 codification.**

---

## §7. Ledger state at close

- **34 rows total** (31 baseline from S2784 + 3 new folds from S2785 SIGN)
- Counts: 15 same_pr_actionable / 13 same_pr_mitigatable / 6 future_trigger

---

## §8. Open items rolled forward to S2786

**From S2784 close still open (unchanged unless noted):**
- AudioAgent completion-flip verification (C1 linkage live; 0 rows populated)
- `test_session_freshness_2775` env drift
- Model drift arc (38 unrelated auto-migrations queued)
- Ledger split drift audit
- CSRF exemption follow-up on the 12 S2784 platform mutation endpoints (`same_pr_mitigatable`, deferred)
- P0.5 cost-threshold, P0.75 CI billing
- S2758 D1/D2/D4/D5
- S2761 smoke test (ops-surface, gated)
- N13 handoff-date-format normalizer
- HMAC signing of `x-acting-user-id`
- 30+ lambda-`__import__` sites in `core/urls.py`
- Rigby S2774 forward-carry ops-surface pause
- N15 v2 / N21 v2 candidates
- First observed partial-recycle event (N10/N11 trigger)
- N24 anti-rubber-stamp SIGN codification — Playbook MINOR, 2+ triggers observed
- I-0302 three-PR pattern amendment → PLAYBOOK-6.10.9 slot
- First graceful-degradation clause activation on PLAYBOOK-6.10.8
- Second non-Rigby consumer of `zoom_out_tool`
- Autonomous Rigby consultation of `zoom_out_tool.list`
- N22 v4+ candidates
- Third served-artifact-freshness trigger — PLAYBOOK-7.4.4 amendment candidate
- S2783 Fold 1 same-PR mitigation deferred (GovernanceTab subtitle)
- S2784 Fold 29 automation identity trigger — pre-prod → non-staff automation deploy
- Postgres cleanup follow-ups (S2774 carryover)

**New from S2785:**
- **Fold-authoring hygiene Playbook amendment** — 2 triggers observed (S2784 Fold 31 + S2785 Fold 32). Ready for codification. Suggested rule text: "When recording a fold that names a specific code gap, verify the gap's actual character (check BOTH decorator/method_decorator AND inline runtime auth blocks) before recording the fold characterization. Overstating a gap can drive wrong-scoped mitigation work."
- **CSRF exemption cleanup follow-up expanded scope** — S2784 flagged CSRF exemption on 12 platform endpoints; S2785 now adds 15 /human/* CBVs + 4 boardroom mutations = 31 total endpoints with `@csrf_exempt`. Cross-file substrate PR candidate.
- **DRF permission_classes migration candidate** — 3 files (`views_governance.py`, `views_platform_command.py`, `views_human_interface.py`) now each define their own `_*_staff_only = user_passes_test(...)` sentinel. Consolidation candidate: single shared `core/auth_gates.py` module with `staff_only` gate + optional DRF permission class for future endpoints. Non-urgent (~3 sentinels is not painful yet); watch for 4th before promoting.
- **Auth-gate helper module candidate** (`core/views_agent_learning.py:_require_boardroom_staff` + future) — similar consolidation opportunity if any other endpoint file needs inline helper style due to non-standard authN. Currently a single site.

---

## §9. Session pin

- Pin history: `pa-ad6b2c423b514728` (label `s2785-decision-approve-audit`) minted at S2785 open.
- **Retired at S2785 close with `force=true`** (sixteenth consecutive per S2770+ pattern).

---

## §10. What worked

1. **Investigation caught fold-mischaracterization before ship.** Original claim "boardroom completely ungated" would have justified the wrong scope; Rigby's tool_read caught the actual state. Fold-authoring drift is now a 2-trigger pattern.
2. **C-lite design decision preserved a real feature.** Naive decorator gating would have broken the S887 Token auth codepath. The inline helper pattern is now precedent for endpoints with non-standard authN.
3. **Full 4-suite auth regression sweep clean.** 93 tests OK across ops + governance + platform + decision-approve surfaces. Cross-file substrate integrity holds.
4. **3-session same-arc continuation** without scope drift or gap sessions. S2783 → S2784 → S2785 all served the same authZ objective, each guided by the prior session's discovered gap.

---

## §11. What to codify (candidates)

**Fold-authoring hygiene rule** — 2 triggers observed. Suggested Playbook §6 rule:

> **PLAYBOOK-6.10.X (proposed):** When recording a zoom-out fold that names a specific code gap (e.g., "no auth gating", "no error handling"), the fold-authoring turn MUST verify the gap's actual character before persistence. For auth gaps specifically, check BOTH decorator/method_decorator AND inline runtime auth blocks in the target file. Overstating a gap drives wrong-scoped mitigation work.

Ready for author-side sequencing at next Playbook MINOR release. Not blocking S2786.

---

## §12. Twin-pointer card

📁 **Repo `/` + `/docs/` — S2785 artifacts:**
- **Ship code:** `core/views_human_interface.py` (15 CBV decorator swaps + module gate), `core/views_agent_learning.py` (4 boardroom endpoints + helper extraction), `core/tests/test_decision_approve_auth_regression_2785.py` (new 358 lines), `tools/pa_local.sh` (+1/-1)
- **Handoff:** `docs/handoffs/SESSION_2785_DECISION_APPROVE_AUTH_AUDIT.md`
- **Predecessors:** S2784 handoff (platform mutations), S2783 handoff (wire GovernanceTab), S2782 handoff (substrate + C1)

🖥️ **Workspace UI — `/workspaces` surface:**
- **Self-Healing tab** (`?tab=system&sub=self-healing`) — unchanged UI, but now DecisionDetailModal calls also gated: anon → 401, non-staff → 401/302, staff (Chris) → operational as before
- **Live surfaces:**
  - `logs/zoom_out_classifications.jsonl` — **34 rows** at S2785 close
  - `logs/session_freshness.jsonl` — grew by 1 at S2785 open
  - `logs/recycle_events.jsonl` — +1 new event from S2785 close (`sha=130955ec07ea`)
