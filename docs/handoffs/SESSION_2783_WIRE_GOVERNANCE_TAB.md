---
title: "SESSION 2783 — wire GovernanceTab into WorkspacePageNew as system.self-healing sub-tab"
session: 2783
status: closed
date: 2026-07-14
close_prs: [3179]
close_pr_merge_shas: [515d9c136]
arc: workspace_ui_dead_code_cleanup
predecessor: SESSION_2782_SUBSTRATE_FIX_PLUS_C1_OBSERVABILITY.md
---

## §1. What shipped

**One net-new engineering ship** — surfaces the dead-code `GovernanceTab` (~500 LOC self-healing UI) as a new `system.self-healing` sub-tab in `WorkspacePageNew`. Small ship (+7 LOC actual diff), first S2783 candidate off the S2782 close list.

**PR #3179 · `515d9c136` — wire GovernanceTab as system.self-healing sub-tab**

- `frontend/src/pages/WorkspacePageNew.tsx` (+6 lines): `Wrench` icon import, `GovernanceTab` barrel import, sub-tab entry `{ id: 'self-healing', label: 'Self-Healing', icon: Wrench }` inserted after `sign-ledger`, render block `{activePrimary === 'system' && activeSub === 'self-healing' && <GovernanceTab />}` inserted after the SIGN Ledger render block.
- `tools/pa_local.sh` (+1/-1): pin refresh to `pa-56b6840c5296488f`.
- **Not changed:** `GovernanceTab.tsx` itself (fully-featured surface preserved as-is: Emergency Controls + Self-Healing System card + Progress-by-Agent table + Run Remediation / Run Audit buttons + Pending Decisions modal); `boardroom` sub-tab (still renders `BoardroomTab`); legacy tab mapping.

**Files touched (2):** `frontend/src/pages/WorkspacePageNew.tsx`, `tools/pa_local.sh`.

---

## §2. Session shape — first S2783 candidate cleanly off the queue

S2782 close listed "Wire GovernanceTab into WorkspacePageNew" as a ⭐ recommended net-new engineering candidate — small ~50 LOC ceiling, dead-code cleanup surfaced at S2780. Chris selected it at open.

The ship followed the standard shape without any deviation:
- Freshness/regression sanity → PASS (23-row ledger baseline, C1 field live, recycle-all detection wired, Playbook rules present)
- Mint fresh pin `pa-56b6840c5296488f` scoped to `s2783-wire-governance-tab`
- Joint SIGN with Rigby → **AGREE Option A** with 6 tool_runs (anti-rubber-stamp gate PASS)
- 4 zoom-out folds classified + persisted (PLAYBOOK-6.10.8) BEFORE D-verdict
- Ship code (+7 lines) → frontend build → collectstatic → daphne bounce
- Chris eyeball verify at `?tab=system&sub=self-healing` → **PASS** (renders correctly; most metrics 0; 1 critical decision pending)
- PR #3179 opened + merged with `--admin` flag (CI billing still broken per memory rule)
- `make recycle-all` post-merge → **twentieth close-cycle post-PLAYBOOK-7.4.4 codification** (rebuilt frontend automatically via S2782 detection)

---

## §3. SIGN cycle

| Slot | Verdict | Notes |
|---|---|---|
| Design (A: new sub-tab / B: reuse boardroom / C: alternate) | **A** AGREE | Joint recommendation with Rigby |
| V5 zoom-out (PLAYBOOK-6.10.7) | 4 folds classified + persisted | See §4 |
| Anti-rubber-stamp gate | **PASS** — 6 tool_runs | `repo_tool.search` × 2, `repo_tool.read_file` × 2, `search_docs`, `zoom_out_tool.list` |

Chris D-verdict at candidate selection ("Let's do #1"). No separate cycle needed for the design AGREE — folds persisted before code shipped, meeting the PLAYBOOK-6.10.8 pre-D-verdict discipline via the natural session ordering.

Rigby's tool-grounded verification independently confirmed:
- 0 `<GovernanceTab` render sites in `frontend/src` (dead code)
- `boardroom` sub-tab still renders `BoardroomTab` (not GovernanceTab)
- S2780 handoff §8 explicitly noted the dead-code cleanup target
- No prior future_trigger folds warning against this shape

---

## §4. V5 zoom-out folds (per PLAYBOOK-6.10.7 + 6.10.8)

Ledger state at close: **27 rows** (12 same_pr_actionable + 10 same_pr_mitigatable + 5 future_trigger).

| # | Concern | Classification | Notes |
|---|---|---|---|
| 24 | Label collision — "Governance" (boardroom) sits adjacent to "Self-Healing" (this tab). Users may not know which to click; "Self-Healing" may read as autopilot rather than human-triggered. | same_pr_mitigatable | Rigby proposed 1-line subtitle mitigation ("Manual remediation & audits (staff-only)"); deferred as post-eyeball follow-up if confusion appears. |
| 25 | Mutation-heavy surface discoverability — GovernanceTab exposes Run Remediation + Run Audit buttons directly. Surfacing as a normal sub-tab increases odds of casual clicks triggering runs. | same_pr_mitigatable | Mitigation: verify auth gating (see Fold 4) + rely on GovernanceTab's own confirm patterns. |
| 26 | Polling load spike on mount — GovernanceTab uses 12s `selfHealingProgress` + 30s `remediationStatus` refetchInterval (each tab-persistent). | future_trigger | Trigger: elevated `/api/platform/self-healing-progress/` traffic OR user reports of "System tab feels heavy." |
| 27 | **Material finding — Governance mutation endpoints have no auth gating.** `emergency_halt_view`, `skin_lock_toggle_view`, `action_run_remediation_view`, `action_run_self_audit_view` are all `@csrf_exempt @require_POST` with no `@login_required` or DRF `permission_classes`. Pre-existing (dead tab wasn't the shield). | future_trigger | Non-blocking under single-user pre-prod. **Trigger: pre-prod → multi-user or public prod deploy — must add auth before that.** Discovered during Fold 2 audit; Rigby explicitly noted she did NOT verify auth gating in her SIGN. |

Fold 4 is a **novel find** — it wasn't in Rigby's returned folds because she didn't verify auth gating. Recording it independently satisfies the workflow rule "Claude verifies independently" and closes the Fold 2 mitigation loop with a real answer (rather than an assumption).

---

## §5. Verification

- **Frontend build:** `npm run build` clean — 2287 modules transformed, `dist/assets/index-BYfdgTs5.js` (2.67MB / 617KB gzipped), postbuild manifest wrote `sha=698f4fca3`, 32 routes.
- **collectstatic:** 6 static files copied (fresh bundle), 191 unmodified, 898 post-processed. No manifest errors.
- **Daphne restart:** pre-commit eyeball verify pass via `make restart-daphne` → health OK.
- **Served bundle SHA-match:** `curl /workspace/` returned `/assets/index-BYfdgTs5.js` matching disk.
- **Chris eyeball verify:** `http://localhost:8000/workspace?tab=system&sub=self-healing` — renders GovernanceTab correctly (Emergency Controls + Self-Healing System card; most metrics 0 as expected for idle state; 1 critical decision pending shown correctly).
- **Post-merge `make recycle-all`:** clean recycle recorded (sha=`515d9c136`, surviving=none). S2782 frontend detection auto-triggered the rebuild + collectstatic (bundle timestamp 11:52 confirms in-recycle build). **Twentieth close-cycle post-PLAYBOOK-7.4.4 codification.**

---

## §6. Ledger state at close

- **27 rows total** (23 baseline from S2782 + 4 new folds from S2783 SIGN)
- Counts: 12 same_pr_actionable / 10 same_pr_mitigatable / 5 future_trigger

---

## §7. Open items rolled forward to S2784

**From S2782 close still open (unchanged unless noted):**
- AudioAgent completion-flip verification (C1 linkage live; awaiting next timeout occurrence)
- `test_session_freshness_2775` env drift (either test guard or always-populate error key)
- Model drift arc (38 unrelated auto-migrations queued — housekeeping candidate)
- Ledger split drift audit (12/8/2 → 12/8/3 shift at S2782 open — non-blocking)
- P0.5 cost-threshold, P0.75 CI billing
- S2758 D1/D2/D4/D5
- S2761 smoke test (ops-surface, gated)
- N13 handoff-date-format normalizer
- HMAC signing of `x-acting-user-id`
- 30+ lambda-`__import__` sites in `core/urls.py`
- Rigby S2774 forward-carry ops-surface pause (still held; S2783 was frontend-only, unaffected)
- N15 v2 / N21 v2 candidates (deferred)
- First observed partial-recycle event (N10/N11 trigger)
- N24 anti-rubber-stamp SIGN codification — Playbook MINOR, 2+ triggers observed
- I-0302 three-PR pattern amendment → PLAYBOOK-6.10.9 slot
- First graceful-degradation clause activation on PLAYBOOK-6.10.8
- Second non-Rigby consumer of `zoom_out_tool`
- Autonomous Rigby consultation of `zoom_out_tool.list`
- N22 v4+ candidates (Django model, JSONL rotation, auto-hook)
- Third served-artifact-freshness trigger — PLAYBOOK-7.4.4 amendment candidate
- Postgres cleanup follow-ups (S2774 carryover)

**New from S2783:**
- **Fold 4 — auth gating gap on governance mutation endpoints.** Pre-existing, non-blocking under single-user pre-prod, but a HARD BLOCKER before any multi-user or public deploy. Trigger: pre-prod → prod transition. Follow-up: add `@login_required` + staff-only DRF permission_classes to the 4 mutation views in `core/views_platform_command.py` (`emergency_halt_view`, `skin_lock_toggle_view`, `action_run_remediation_view`, `action_run_self_audit_view`).
- **Fold 1 same-PR mitigation deferred.** Rigby's proposed 1-line subtitle for GovernanceTab ("Manual remediation & audits (staff-only)") was not applied — deferred pending first observed user confusion. Track for a follow-up if Chris reports label ambiguity.

---

## §8. Session pin

- Pin history: `pa-56b6840c5296488f` (label `s2783-wire-governance-tab`) minted at S2783 open.
- **Retired at S2783 close with `force=true`** (fourteenth consecutive per S2770+ pattern).

---

## §9. Substrate signal

**No substrate defects surfaced.** S2782's PLAYBOOK-7.4.4 recycle-all with frontend detection worked as designed — post-merge recycle-all auto-detected the `frontend/src/pages/WorkspacePageNew.tsx` change in `HEAD~1..HEAD` and triggered the `frontend-build` + `collectstatic` step before `restart`. Second consecutive session where the frontend-detection substrate paid off (S2782 was self-test on backend-only diff → npm build correctly skipped; S2783 is the first ship WITH frontend/ changes that landed cleanly post-merge without any manual intervention).

**Rigby dogfooding streak now spans three consecutive sessions** (S2781, S2782, S2783) with `zoom_out_tool.list` used to consult prior folds during her SIGN. Second observed in-wild consumer of `zoom_out_tool` still owed (S2782 forward-carry).

---

## §10. What worked

1. **Small ship completed the S2783 open sequence cleanly** — freshness + regression + eyeball + SIGN + ship + recycle inside ~1h.
2. **Anti-rubber-stamp gate held.** Rigby returned 6 tool_runs verifying every claim in the design directive; no rubber-stamp AGREE.
3. **PLAYBOOK-6.10.8 discipline held.** Folds classified + persisted BEFORE any code touched. Fold 4 (auth gating gap) discovered mid-flight, recorded on the spot rather than deferred.
4. **The S2782 substrate paid off silently.** No blank-page moment, no manual `npm run build` + `collectstatic` + daphne bounce dance. `make recycle-all` did the whole thing.

---

## §11. What to codify (candidates)

None urgent. Fold 4 (auth gating gap) is a pre-prod → prod gate, not a workflow rule — it will manifest naturally when the deployment surface changes.

---

## §12. Twin-pointer card

📁 **Repo `/` + `/docs/` — S2783 artifacts:**
- **Ship code:** `frontend/src/pages/WorkspacePageNew.tsx` (+6 lines), `tools/pa_local.sh` (+1/-1)
- **Handoff:** `docs/handoffs/SESSION_2783_WIRE_GOVERNANCE_TAB.md`
- **Predecessors:** S2782 handoff (substrate + C1), S2781 handoff (N17), S2780 handoff (N22 v3)

🖥️ **Workspace UI — `/workspaces` surface:**
- **NEW: Self-Healing tab** — `?tab=system&sub=self-healing` (Emergency Controls + Self-Healing progress + Pending Decisions)
- **Adjacent surfaces preserved:** SIGN Ledger `?sub=sign-ledger`, Governance `?sub=boardroom`
- **Live surfaces:**
  - `logs/zoom_out_classifications.jsonl` — **27 rows** at S2783 close
  - `logs/session_freshness.jsonl` — grows per pin mint
  - `logs/recycle_events.jsonl` — +1 event from S2783 close (`sha=515d9c136`)
