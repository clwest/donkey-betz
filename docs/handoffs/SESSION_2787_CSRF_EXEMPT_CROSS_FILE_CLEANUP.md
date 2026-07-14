# Session 2787 — CSRF Exemption Cross-File Cleanup

**Ship SHA:** `39b69d820` · **PR:** [#3187](https://github.com/clwest/donkey-betz-platform/pull/3187) · **Date:** 2026-07-14

---

## §1 What shipped

Removed `@csrf_exempt` from the 31 mutation endpoints S2784+S2785 gated staff-only, added a frontend CSRF interceptor, and locked in a regression test suite that guards both the CSRF pass path and the S887 Token-auth preservation.

**Backend (3 files, 31 endpoints):**

- `core/views_platform_command.py` — 12 mutation endpoints (from S2784 audit):
  `create_initiative_from_decision_view`, `emergency_halt_view`, `skin_lock_toggle_view`, `canon_promote_view`, `audit_run_view`, `trigger_toggle_view`, `trigger_run_now_view`, `action_run_spiders_view`, `action_run_remediation_view`, `action_agent_health_check_view`, `action_agent_category_rotation_view`, `action_run_self_audit_view`.
  2 out-of-scope csrf_exempt sites (lines 2630/2696 after removal — pre-cleanup 2642/2708) left untouched — recorded as Fold C `future_trigger`.
- `core/views_human_interface.py` — 15 `/api/human/*` CBVs (from S2785 audit): all 15 `@method_decorator([csrf_exempt, login_required, _human_staff_only], name='dispatch')` stacks stripped of `csrf_exempt`. Unused `csrf_exempt` import removed.
- `core/views_agent_learning.py` — 4 `/api/boardroom/*` mutation function views: `promote_decision`, `reject_decision`, `bulk_promote_decisions`, `bulk_reject_decisions`. Docstring mentions of "@csrf_exempt for API calls" updated to reflect the new posture. `csrf_exempt` import kept (still used by 9 out-of-scope endpoints elsewhere in the file).

**Frontend (1 file):**

- `frontend/src/lib/api.ts` — added axios request interceptor reading `csrftoken` cookie and setting `X-CSRFToken` header on POST/PUT/PATCH/DELETE. Inline comment documents shared coverage of `cockpitApi.ts` via axios-instance import.

**Tests (1 new file):**

- `core/tests/test_csrf_enforcement_2787.py` — 3 test classes × 31 endpoint subtests = 93 assertions:
  - `SessionAuthCsrfEnforcementTest` — session POST without X-CSRFToken → 403
  - `SessionAuthCsrfPassTest` — session POST with valid X-CSRFToken → not 403
  - `TokenAuthS887PreservationTest` — Token-authed POST without CSRF → not 403 (S887 regression guard)

---

## §2 Novel-precedent moments

### 2.1 First in-wild application of PLAYBOOK-6.10.9 (fold-authoring evidence admission)

Triggered three times during S2787:

1. **T3 SIGN routing:** middleware finding at `core/middleware.py:31-45` admitted with stable-state-pointer (HEAD `421f0f6fb`) + file+line + (i)/(ii)/(iii) verified-state outcome inline before Rigby lock-in.
2. **Mid-implementation correction:** T3 file-endpoint mapping had `views_agent_learning.py ↔ views_human_interface.py` counts swapped (15 vs 4 assignments reversed). Admitted with correction narrative pre-code so Chris's yes/no was still on the substance. Actual code-change scope unchanged.
3. **Fold C surfacing:** the 2 out-of-scope csrf_exempt sites at `views_platform_command.py:2642/2708` admitted with file+line evidence before persisting the future_trigger row.

**Signal:** the rule works. All three admissions caught a would-be code-state assertion drift before it reached ratification. Every constraint the rule was designed to catch was actually caught.

### 2.2 Rigby SIGN response truncation surfaced (T1→T2 recovery pattern)

Rigby's T1 message body was ~40KB with tool_runs and got truncated by `pa_chat.py`'s message-capture path at the "**However:** yo..." mark — clean cut mid-Fold-A rationale. T2 was a compact re-request for just the tail (Folds A/B remainder + F-BLOCKING content + zoom-out answers + blocker verdicts). Rigby responded cleanly.

**Rule-of-thumb:** when routing large SIGN packets to Rigby, expect truncation on responses > ~30 lines of markdown after tool_runs. Follow-up compact re-requests are cheap; token cost of full re-verification is much higher.

### 2.3 Fold-C-before-D-verdict pattern

Chris said "yes proceed" between T3 AGREE and Fold C discovery. Rather than treat the D-verdict as sealed, I persisted Fold C as `future_trigger` (informational; not gating this PR) and updated the plan accordingly. This preserves PLAYBOOK-6.10.8's "persist BEFORE D-verdict" spirit even when a fold surfaces post-verdict — the persistence happens BEFORE the code lands, and future_trigger classification means no scope creep on the ratified plan.

---

## §3 T1..T3 SIGN cycle summary

| Turn | Author | Content | Tool_runs | Outcome |
|---|---|---|---|---|
| T1 | Claude → Rigby | Scope proposal + PLAYBOOK-6.10.9 evidence admission for the 31-vs-45 csrf_exempt count discrepancy + 3 blockers + 3 zoom-out asks | Rigby: 10 (git_info, 4×repo_tool.read_file, 3×repo_tool.search, plus verification) | Rigby CONDITIONAL AGREE with 2 folds + 1 F-BLOCKING DISAGREE (pending verification); message truncated mid-Fold-A |
| T2 | Claude → Rigby | Compact re-request for truncated tail (Folds A/B, F-BLOCKING content, zoom-out answers, blocker verdicts) | None (Rigby ran no new tools; text-only recovery) | Rigby full CONDITIONAL AGREE tail: Fold A pushback on decorator-count boundary → adopt unsafe-methods framing; Fold B shared-factory suggestion; F-BLOCKING is S887 Token-auth survival needs verification |
| T3 | Claude → Rigby | Blockers cleared with PLAYBOOK-6.10.9 evidence admission (B1: DisableCSRFForAuthEndpoints middleware pre-CSRF; B2: single-axios coverage of cockpitApi.ts + no orphan fetch sites); refined scope | Rigby: 9 (zoom_out_tool.list ×2, 4×repo_tool.read_file, 3×repo_tool.search) | Rigby AGREE with one micro-edit to B2 phrasing (adopted) |

**Anti-rubber-stamp check:** all 3 SIGN routings returned non-empty tool_runs. Rigby's T1 F-BLOCKING was a real, tool-grounded pushback (verified by her subsequent tool_runs against middleware/settings). Anti-rubber-stamp discipline confirmed to correlate with F-BLOCKING catches (now 4 triggers on the S2771 streak: S2778/S2780/S2786/S2787 — a promotion signal for the N24 memory rule).

---

## §4 Ledger delta

- **At S2787 open:** 36 rows (15 same_pr_actionable / 14 same_pr_mitigatable / 7 future_trigger)
- **After T3 fold persistence (pre-D-verdict):** 38 rows (16/15/7)
  - Row 37 (S2787, Fold A, `same_pr_actionable`): "Scope-by-decorator-count risks conflating unsafe-method mutations with GET-decorated sites…"
  - Row 38 (S2787, Fold B, `same_pr_mitigatable`): "Single-axios-interceptor coupling risk… therefore single api.ts interceptor is sufficient for THIS state…"
- **After Fold C pre-implementation:** 39 rows (16/15/8)
  - Row 39 (S2787, Fold C, `future_trigger`): "views_platform_command.py lines 2642+2708 are csrf_exempt unsafe-method mutations lacking @login_required + _platform_staff_only decorator stack…"

---

## §5 Twin-pointer card

📁 **Repo `/` + `/docs/` — S2787 artifacts:**

- **Ship code:** `core/views_platform_command.py`, `core/views_human_interface.py`, `core/views_agent_learning.py`, `frontend/src/lib/api.ts`, `core/tests/test_csrf_enforcement_2787.py`, `tools/pa_local.sh` (+2/-1 pin refresh)
- **Handoff:** `docs/handoffs/SESSION_2787_CSRF_EXEMPT_CROSS_FILE_CLEANUP.md` (this file)
- **Predecessors:** S2786 (Playbook v0.8.0), S2785 (decision-approve authZ), S2784 (platform mutations)

🖥️ **Workspace UI — `/workspaces` surface:**

- **System / Sign Ledger sub-tab** (`?tab=system&sub=sign-ledger`) — 39 rows now, including S2787 Folds A/B/C
- **Live surfaces:**
  - `logs/zoom_out_classifications.jsonl` — 39 rows at S2787 close
  - `logs/session_freshness.jsonl` — grew by 1 at S2787 open
  - `logs/recycle_events.jsonl` — +1 new event from S2787 close (`sha=39b69d820`)

---

## §6 Open items forward-carry

1. **First in-wild follow-up on PLAYBOOK-6.10.9** — S2787 exercised the rule 3 times cleanly. No amendments needed yet.
2. **Fold C follow-up** — 2 unaudited csrf_exempt POST/DELETE mutations at `views_platform_command.py:2630/2696` lack `@login_required + _platform_staff_only`. Not gating; deferred for a S2788+ authZ-audit sweep of unaudited mutation endpoints in the same file family.
3. **N24 anti-rubber-stamp SIGN promotion** — now 4 F-BLOCKING triggers on the S2771 streak (S2778 V1 slot, S2780 V3 canonical home, S2786 D4 "at HEAD", S2787 T1 S887 Token-auth survival). Memory rule promotion window firmly open — codification candidate for a future Playbook amendment.
4. **CSRF interceptor E2E eyeball** — Chris to open GovernanceTab and confirm Approve/Dismiss still function under session auth (proves frontend interceptor + backend enforcement working end-to-end). Fold Chris's finding into S2788 open if any regression surfaces.
5. **Rigby SIGN response truncation pattern** — observed twice now (S2786 T2 partial, S2787 T1 more severe). If it recurs a third time, consider (a) breaking large SIGN packets into 2 turns from the start, or (b) instrumenting `pa_chat.py` to detect and warn on truncation.
6. All prior S2786 open runtime items forward-carry unchanged unless S2787 changed them (none did).

---

## §7 Rebindings post-merge

- **Ledger:** 39 rows (16 actionable / 15 mitigatable / 8 future_trigger)
- **Rule count:** 205 (unchanged; no Playbook amendment this session)
- **Playbook version:** v0.8.0 (unchanged)
- **Session pin:** `pa-0a74be099bf6428a` (S2787) — retire at close per S2770+ pattern with `force=true`
- **Wrapper default pin:** to be updated with fresh mint at S2788 open (forcing function preserved)
