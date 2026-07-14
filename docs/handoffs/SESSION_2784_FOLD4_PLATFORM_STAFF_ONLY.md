---
title: "SESSION 2784 — Fold 4 mitigation: staff-only gate on 12 platform mutation endpoints"
session: 2784
status: closed
date: 2026-07-14
close_prs: [3181]
close_pr_merge_shas: [814c2452d]
arc: fold4_platform_mutation_staff_gate
predecessor: SESSION_2783_WIRE_GOVERNANCE_TAB.md
---

## §1. What shipped

**Same-PR mitigation of the S2783 Fold 4 discovery.** All 12 mutation POST endpoints in `core/views_platform_command.py` now use the `@login_required @_platform_staff_only` decorator stack matching the S2772 N16 Rigby-ratified contract + the `_governance_staff_only` pattern at `core/views_governance.py:26-28`.

**PR #3181 · `814c2452d` — Fold 4 mitigation**

- `core/views_platform_command.py`:
  - Added imports: `from django.contrib.auth.decorators import login_required, user_passes_test`
  - Added module-level gate: `_platform_staff_only = user_passes_test(lambda u: u.is_authenticated and u.is_staff)`
  - Removed 12 inline `if not request.user.is_authenticated: return JsonResponse({...}, status=401)` blocks (redundant after decorators)
  - Removed 2 leading `# Verify authentication` comments (obsolete)
  - Added `@login_required @_platform_staff_only` decorator pair to the 12 mutation view functions
- New file `core/tests/test_platform_auth_regression_2784.py`:
  - Mirrors `test_governance_auth_regression_2780.py` shape
  - 28 tests: 12 anon-blocked + 12 non-staff-blocked + 2 staff-reachable (`emergency_halt`, `skin_lock`) + 2 route-inventory guards
- `tools/pa_local.sh`: pin refresh to `pa-f2bd82d8c76f4e32` (retired at close).

**Files touched (3):** `core/views_platform_command.py`, `core/tests/test_platform_auth_regression_2784.py`, `tools/pa_local.sh`.

**Session-in-session shape.** S2784 opened directly off the S2783 close's ⭐ candidate list ("Fold 4 same-PR mitigation") without a gap session — Chris authorized "Let's do fold 4 auth mitigation" seconds after S2783 close.

---

## §2. The 12 endpoints gated

| Endpoint | View |
|---|---|
| `POST /api/platform/decision-summary/<id>/create-initiative/` | `create_initiative_from_decision_view` |
| `POST /api/platform/emergency-halt/` | `emergency_halt_view` ⚡ GovernanceTab |
| `POST /api/platform/skin-lock/` | `skin_lock_toggle_view` ⚡ GovernanceTab |
| `POST /api/platform/canon/promote/` | `canon_promote_view` |
| `POST /api/platform/audits/run/` | `audit_run_view` |
| `POST /api/platform/triggers/<rule>/toggle/` | `trigger_toggle_view` |
| `POST /api/platform/triggers/run-now/` | `trigger_run_now_view` |
| `POST /api/platform/actions/run-spiders/` | `action_run_spiders_view` |
| `POST /api/platform/actions/run-remediation/` | `action_run_remediation_view` ⚡ GovernanceTab |
| `POST /api/platform/actions/agent-health-check/` | `action_agent_health_check_view` |
| `POST /api/platform/actions/agent-category-rotation/` | `action_agent_category_rotation_view` |
| `POST /api/platform/actions/run-self-audit/` | `action_run_self_audit_view` ⚡ GovernanceTab |

Only 4 of 12 (⚡) are reachable via the newly-wired GovernanceTab. The other 8 are called by adjacent surfaces (PlatformCommandCenter, direct API scripts). The **broader scope was the correct closure** — leaving 8 sites vulnerable while patching 4 would have been half-measure security.

---

## §3. Novel-precedent moment — Fold 4 framing correction

S2783 Fold 4 was recorded as "**no auth gating**" — but the actual gap was "**no staff-only gating**." Every one of the 12 mutation endpoints already had an inline `if not request.user.is_authenticated` check. The vulnerability was that any *authenticated non-staff* user could trigger any of them.

Investigation caught this before code shipped (the joint SIGN T1 tool_runs surfaced the discrepancy). Recorded as **Fold 4 of this session** (`same_pr_mitigatable`, process fix): standardize fold language to distinguish **authN present vs authZ missing**, so folds don't overstate findings and drive more work than needed.

**First observed fold-authoring drift.** Prior sessions haven't produced this class of discrepancy at this scale. Watch for repetition — 2nd trigger = candidate for a Playbook note (fold-authoring hygiene rule).

---

## §4. SIGN cycle

| Slot | Verdict | Notes |
|---|---|---|
| Design (A: 4 endpoints / B: all 12 / C: alternate) | **B** AGREE | Joint recommendation with Rigby (2-turn resolution — T1 with initial 4-endpoint scope, T2 with corrected 12-endpoint scope after Claude discovered the wider pattern via `grep -B 3`) |
| V5 zoom-out (PLAYBOOK-6.10.7) | 4 folds classified + persisted | See §5 |
| Anti-rubber-stamp gate | **PASS** — T1 returned tool_runs (repo_tool.read_file × 3, repo_tool.search, zoom_out_tool.list, session_tool.whoami, search_docs) | T2 was scope refinement, no re-verification needed |

Chris D-verdict "Let's do B — comprehensive fix" after Claude+Rigby joint agreement (per `feedback_claude_rigby_agree_first_chris_yes_no`).

---

## §5. V5 zoom-out folds (per PLAYBOOK-6.10.7 + 6.10.8)

Ledger state at close: **31 rows** (13 same_pr_actionable + 12 same_pr_mitigatable + 6 future_trigger).

| # | Concern | Classification | Notes |
|---|---|---|---|
| 28 | AuthZ boundary should be the mutation surface (`views_platform_command.py`), not the UI-caller surface (GovernanceTab). | same_pr_actionable | Option B directly implements this. |
| 29 | Potential legitimate non-staff automation/service-account usage would break under Option B. | future_trigger | Trigger: introduction of an automation identity that isn't `is_staff`. Mitigation is NOT to keep endpoints open — it's to make automation identities staff, or introduce explicit permission classes. |
| 30 | CSRF exemption remains on all 12 endpoints. Staff-only shrinks blast radius but doesn't fix the CSRF exposure. | same_pr_mitigatable | Deferred as follow-up substrate concern; mixing CSRF refactor into authZ PR would violate single-concern. |
| 31 | **Fold-authoring discipline drift** — Fold 4 was originally recorded as "no auth gating" when the actual finding was "no staff-only gating." | same_pr_mitigatable | Process fix: standardize fold language to distinguish authN present vs authZ missing. Watch for 2nd trigger. |

---

## §6. Verification

- **Syntax:** `python -c "import ast; ast.parse(open('core/views_platform_command.py').read())"` — OK
- **0 remaining inline auth sites** in `core/views_platform_command.py`
- **12 `@_platform_staff_only` decorator injections** with correct stacking order (`@csrf_exempt @require_POST @login_required @_platform_staff_only def <view>`) matching `views_governance.py` pattern
- **`test_platform_auth_regression_2784`:** 28 tests OK (0.336s)
- **3-suite auth sweep:** `test_ops_auth_regression_2772` + `test_governance_auth_regression_2780` + `test_platform_auth_regression_2784` — **48 tests OK** (0.826s), no cross-file regressions
- **Live curl on Daphne:** anon POST returns 401 on `emergency-halt`, `skin-lock`, `run-remediation`
- **Chris eyeball verified:** GovernanceTab renders + operates as before (Chris is staff+superuser; new gate is transparent to him)
- **Post-merge `make recycle-all`:** clean recycle at sha=`814c2452d154`, surviving=none. Backend-only diff, no frontend rebuild triggered (S2782 detection working correctly). **Twenty-first close-cycle post-PLAYBOOK-7.4.4 codification.**

---

## §7. Ledger state at close

- **31 rows total** (27 baseline from S2783 + 4 new folds from S2784 SIGN)
- Counts: 13 same_pr_actionable / 12 same_pr_mitigatable / 6 future_trigger

---

## §8. Open items rolled forward to S2785

**From S2783 close still open (unchanged unless noted):**
- AudioAgent completion-flip verification (C1 linkage live; 0 rows populated)
- `test_session_freshness_2775` env drift
- Model drift arc (38 unrelated auto-migrations queued)
- Ledger split drift audit (12/8/2 → 12/8/3 shift at S2782 open)
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
- Postgres cleanup follow-ups (S2774 carryover)

**New from S2784:**
- **CSRF exemption on 12 platform mutation endpoints** (Fold 30, `same_pr_mitigatable`, deferred). Staff-only shrinks blast radius but CSRF is a real remaining exposure vector — future substrate PR candidate.
- **Non-staff automation/service-account gap** (Fold 29, `future_trigger`). Watch for: any deployment introduces a non-staff automation identity. Mitigation NOT to open endpoints — to make automation is_staff or add explicit permission_classes.
- **Fold-authoring discipline drift** (Fold 31, `same_pr_mitigatable`). One trigger observed; watch for second before promoting to a workflow rule.
- **DecisionApprove endpoint auth posture unaudited** (from Chris's approve-button question during eyeball verify). The decision-approve endpoint lives outside `views_platform_command.py`; wasn't touched by this PR. Same authN-only pattern likely applies. Follow-up candidate: audit all pending-decision approve/dismiss endpoints for staff-only gating consistency.

---

## §9. Session pin

- Pin history: `pa-f2bd82d8c76f4e32` (label `s2784-fold4-auth-mitigation`) minted at S2784 open.
- **Retired at S2784 close with `force=true`** (fifteenth consecutive per S2770+ pattern).

---

## §10. What worked

1. **Same-session dispatch of prior-session fold.** S2783 Fold 4 discovered → S2784 opened seconds later → mitigation shipped in ~1h. Tight fold→mitigation loop.
2. **Fold framing corrected before ship.** Original "no auth gating" claim would have justified a smaller/wrong patch. Discovery of the actual "no staff-only gating" pattern via `grep -B 3` reframed the work correctly.
3. **Scope expansion 4→12 handled cleanly.** T2 SIGN turn addressed the scope question; Rigby's zoom-out on PLAYBOOK-7.4.1 kept the whole-file-fix within single-concern discipline.
4. **Regression test file gives future drift a fail-loud contract.** The route inventory guard fails if anyone adds a new mutation endpoint without an accompanying anon/non-staff test.
5. **`test_platform_auth_regression_2784` added to next open sequence.** The regression 6-suite becomes a **7-suite** at S2785 open (see §11).

---

## §11. What to codify (candidates)

Nothing urgent. Fold 31 (fold-authoring discipline drift) is one observed trigger; wait for a second before proposing a Playbook amendment.

**Suggestion for docs/ENGINEERING_PLAYBOOK.md §7 (author-side sequencing):** consider adding a fold-hygiene note: when recording a fold that names a specific gap, verify the gap's actual character (e.g., authN present vs authZ absent) before recording, so downstream mitigation work isn't scoped against a mis-framing. Not urgent — one trigger.

---

## §12. Twin-pointer card

📁 **Repo `/` + `/docs/` — S2784 artifacts:**
- **Ship code:** `core/views_platform_command.py` (module gate + decorators on 12 views), `core/tests/test_platform_auth_regression_2784.py` (new 236-line regression file), `tools/pa_local.sh` (+1/-1)
- **Handoff:** `docs/handoffs/SESSION_2784_FOLD4_PLATFORM_STAFF_ONLY.md`
- **Predecessors:** S2783 handoff (wire GovernanceTab), S2782 handoff (substrate + C1), S2781 handoff (N17)

🖥️ **Workspace UI — `/workspaces` surface:**
- **Self-Healing tab** (`?tab=system&sub=self-healing`) — unchanged UI surface, but now gated: anon → 401, non-staff → 401/302, staff (Chris) → 200 as before
- **Live surfaces:**
  - `logs/zoom_out_classifications.jsonl` — **31 rows** at S2784 close
  - `logs/session_freshness.jsonl` — grew by 1 at S2784 open
  - `logs/recycle_events.jsonl` — +1 event from S2784 close (`sha=814c2452d154`)
