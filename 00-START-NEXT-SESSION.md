# Next Session — Start Here

---

## READ THIS FIRST — SESSION 2787 CLOSED — CSRF EXEMPTION CROSS-FILE CLEANUP SHIPPED (31 mutation endpoints, 3 files)

**Refreshed 2026-07-14 (SESSION 2787 CLOSED — engineering-first candidate shipped per `feedback_engineering_bias_over_audit`. PR #3187 (`39b69d820`) removes @csrf_exempt from the 31 mutation endpoints S2784+S2785 gated staff-only (12 platform + 15 human + 4 boardroom) and adds a frontend axios CSRF interceptor to `frontend/src/lib/api.ts`. Session-cookie browser callers now must send X-CSRFToken; Token/Bearer/X-API-Key callers unaffected — `DisableCSRFForAuthEndpoints` middleware at `core/middleware.py:31-45` pre-CSRF short-circuit was already in place, so no new middleware needed to preserve S887 codepath. Scope refined from initial ~1-3h estimate to ~1-2h after two evidence flips (middleware pre-existed; single axios interceptor covers cockpitApi.ts via shared import). Joint SIGN with Rigby in 3 turns (T1 tool-grounded F-BLOCKING → T2 truncation recovery → T3 blockers cleared with PLAYBOOK-6.10.9 evidence admission → AGREE with one micro-edit). Chris D-verdict single-yes. 3 folds persisted pre-D-verdict per PLAYBOOK-6.10.8 (rows 37 Fold A same_pr_actionable → adopted unsafe-methods scope framing, row 38 Fold B same_pr_mitigatable → single-interceptor coupling documented, row 39 Fold C future_trigger → 2 unaudited csrf_exempt mutation endpoints at views_platform_command.py:2630/2696 lacking staff-only gate). **First in-wild application of PLAYBOOK-6.10.9** — exercised 3 times cleanly (T3 middleware evidence + mid-implementation mapping correction + Fold C surfacing). Regression 9-suite: 158 tests OK (155 existing + 3 new × 31 endpoint subtests = 93 CSRF assertions). Post-merge `make recycle-all` clean — TWENTY-FOURTH close-cycle post-PLAYBOOK-7.4.4 codification.)**

**S2787 ship:**

**PR #3187 · `39b69d820`** — `core/views_platform_command.py` (removed 12 @csrf_exempt), `core/views_human_interface.py` (removed csrf_exempt from 15 method_decorator lists + unused import), `core/views_agent_learning.py` (removed 4 @csrf_exempt on boardroom mutations + updated stale docstrings), `frontend/src/lib/api.ts` (+22/-1 CSRF interceptor), `core/tests/test_csrf_enforcement_2787.py` (new 179-line regression), `tools/pa_local.sh` (+2/-1 pin refresh)

**Handoff:** `docs/handoffs/SESSION_2787_CSRF_EXEMPT_CROSS_FILE_CLEANUP.md`
**Post-merge:** `make recycle-all` per PLAYBOOK-7.4.4 completed (twenty-fourth cycle, sha=39b69d820247).
**Ledger state at close:** `logs/zoom_out_classifications.jsonl` — 39 rows (16 same_pr_actionable / 15 same_pr_mitigatable / 8 future_trigger).

---

## SESSION-OPEN INFRA STORY (S2787)

Engineering-first session per `feedback_engineering_bias_over_audit`. Chris selected CSRF cleanup at S2787 open — one of the S2787-CANDIDATES net-new engineering leans (net-new decorator removal + new frontend interceptor + new regression file; not audit-of-what-exists).

Author-side scope proposal claimed "31 mutation endpoints across 3 files" per S2786 handoff. PLAYBOOK-6.10.9 evidence admission surfaced the actual csrf_exempt footprint is ≥45 sites across those 3 files (14 standalone + 15 standalone + 16 method_decorator variant); the "31" figure is a SUBSET (only the S2784+S2785-audited mutation endpoints). Boundary defined as intersection of {audited mutation endpoints} ∩ {unsafe HTTP methods}.

Rigby T1 tool-grounded SIGN caught F-BLOCKING on S887 Token-auth codepath survival + raised 2 zoom-out folds (Fold A: scope by unsafe HTTP methods; Fold B: single-interceptor coupling risk). T2 recovered a truncated verdict tail (pa_chat.py cut Rigby's ~40KB message body at "**However:** yo..." mid-Fold-A). T3 cleared B1 (middleware evidence flip — `DisableCSRFForAuthEndpoints` already pre-CSRF-short-circuits Token requests) + B2 (only 2 raw fetch calls to /api/platform/*, both GETs; cockpitApi.ts:1 imports the same axios instance). Rigby T3 AGREE with one micro-edit adopted. Chris D-verdict single-yes.

Mid-implementation correction: T3 written mapping had views_agent_learning.py ↔ views_human_interface.py counts swapped (15 boardroom vs 4 human, actual is 15 human CBVs vs 4 boardroom function views). Admitted per PLAYBOOK-6.10.9 before writing code; actual scope unchanged.

Fold C surfaced pre-implementation while reading views_platform_command.py:2642/2708 (post-cleanup renumbered to 2630/2696) — 2 unaudited csrf_exempt POST/DELETE endpoints (cleanup_stale_executions_view + delete_failed_executions_view) lacking @login_required + _platform_staff_only. Persisted as future_trigger; S2788+ authZ-audit-sweep candidate.

---

## THE PIVOTS — WHY THIS SHIP MATTERS

**First engineering ship after 3-consecutive-constitutional-MINOR streak (v0.6.0/S2766 + v0.7.0/S2778 + v0.8.0/S2786).** Signals that the constitutional substrate stays out of the way of net-new engineering work — the SIGN discipline adds a few minutes of pre-code verification and catches real F-BLOCKING (as it did here), but doesn't slow the actual work.

**First in-wild application of PLAYBOOK-6.10.9 succeeded 3× in one session.** The rule exercised on middleware finding, mid-implementation mapping correction, and Fold C surfacing. Every constraint the rule was designed to catch was caught cleanly. No back-and-forth loops from imprecise assertions.

**Anti-rubber-stamp discipline hit a 4th F-BLOCKING trigger on the S2771 streak.** Now S2778/S2780/S2786/S2787 all show F-BLOCKING catches on tool-grounded SIGN turns. N24 memory rule promotion window firmly open — codification candidate for a future Playbook amendment.

**Scope evidence flips saved time.** Chris estimated ~1-3h; middleware + frontend verification found the scope was smaller than the initial architecture guess (~1-2h realized). PLAYBOOK-6.10.9 evidence admission is the mechanism that made the flips visible.

---

## S2788 CANDIDATES (Chris selects at open)

### First — freshness/regression sanity

**Post-cascade freshness check:** wrapper pin retired (S2787 close); freshness should be FRESH · SHA-match at S2787 close SHA `39b69d820` (or the cascade PR merge SHA).
**Ledger baseline:** 39 rows expected (16/15/8). Any drift = investigate.
**Regression 9-suite:** unchanged (158 tests OK at S2787 close).

### Net-new engineering (⭐ recommended per `feedback_engineering_bias_over_audit`)

- **Auth-gate consolidation trigger evaluation** — 3 sentinel modules currently (`_platform_staff_only`, `_governance_staff_only`, `_human_staff_only`, `_require_boardroom_staff`). If Fold C follow-up (below) surfaces a 4th, trigger consolidation into `core/auth_gates.py`.
- **Fold C follow-up — authZ-audit sweep for unaudited mutation endpoints in views_platform_command.py** — 2 known sites (cleanup_stale_executions_view + delete_failed_executions_view) currently missing @login_required + _platform_staff_only. Similar sites likely exist across other `core/views_*.py` files. Non-trivial (~1-2h backend + regression tests + eyeball). Trigger 4th auth-gate sentinel if consolidation candidate.
- **CSRF interceptor E2E eyeball (Chris)** — open GovernanceTab under session auth, confirm Approve/Dismiss + platform command actions still function post-cleanup. Minimal effort; verifies the frontend interceptor + backend enforcement work end-to-end.
- **Frontend raw-fetch consolidation (mid-term)** — 30 files with raw `fetch()` calls (not going through api.ts axios). Most are read-only GETs (safe), but any that become mutations later will silently bypass the new CSRF interceptor. Trigger: first observed regression from a raw-fetch mutation site.
- **AudioAgent completion-flip verification** — C1 linkage live; awaiting next timeout for one-query verification.
- **Model drift arc** — 38 unrelated auto-migrations queued.
- **Something entirely new** — new spider / UI page / agent capability / pipeline / dashboard.

**Still gated by S2774 ops-surface pause:** N9, N20, Candidate 1 (S2761 smoke), 30+ `core/urls.py` lambda-`__import__` sites.

**Still owed:** P0.5 cost-threshold, P0.75 CI billing, memory rule promotion audit (**N24 anti-rubber-stamp SIGN now at 4 F-BLOCKING triggers** — S2778 + S2780 + S2786 + S2787 — promotion candidate).

### Deferred (waiting on triggers, not calendar)

- **N10** — partial-recycle UI badge (gated on real partial-recycle event)
- **First real N11 PARTIAL_RECYCLE tile fire** (watching)
- **Q3 #5** (health_summary / ops_tool.overview overlap)
- **N22 v2 time-window filters** — trigger: ~50+ rows temporal spread (currently 39)
- **N22 v4+ candidates** — Django model, JSONL rotation, auto-hook
- **Second non-Rigby consumer of `zoom_out_tool`** — trigger for factor-out abstraction test
- **N17 smart-command-box creep** — row 21 `future_trigger`
- **Autonomous Rigby consultation of `zoom_out_tool.list`** — Rigby's dogfooding so far was under prompts, not autonomous
- **First graceful-degradation clause activation on PLAYBOOK-6.10.8** — pending
- **Third served-artifact-freshness trigger** — PLAYBOOK-7.4.4 amendment candidate
- **S2783 Fold 1 same-PR mitigation** — GovernanceTab subtitle
- **S2784 Fold 29 automation identity trigger** — pre-prod → non-staff automation deploy
- **4th auth-gate sentinel** — trigger for consolidation into `core/auth_gates.py`
- **Fold-authoring evidence-admission helper (§6.12 note)** — 3+ SIGN cycles delayed >5min by manual verify OR one SIGN blocked
- **Second amendment with ledger-enumerable two-trigger corpus** — corroborate the amendment shape for codification
- **Rigby SIGN response truncation** — observed 2× (S2786 T2 partial, S2787 T1 more severe); if 3rd trigger, consider (a) proactive 2-turn splits for large SIGN packets or (b) pa_chat.py truncation-detection warning

### Post-S2787 owed

- **I-0302 three-PR pattern amendment** → PLAYBOOK-6.10.10 slot when opened (re-slotted forward again from 6.10.9 in v0.8.0 provenance)
- **Fold C follow-up** — 2 unaudited csrf_exempt mutations + likely more across `core/views_*.py` (see net-new)
- **N24 anti-rubber-stamp SIGN codification** — 4 F-BLOCKING triggers now, promotion candidate
- **AudioAgent completion-flip verification**
- **`test_session_freshness_2775` env drift**
- **Ledger split drift audit** — now 16/15/8 (was 15/14/7 at S2786 close)

---

## SESSION PIN — S2787 RETIRED (fresh mint required at S2788 open)

**Pin history (S2787):**

- `pa-0a74be099bf6428a` (label `s2787-csrf-exempt-cross-file-cleanup`) minted S2787 open; **retired at S2787 close (`force=true`, eighteenth consecutive per S2770+ pattern)**

**Wrapper `tools/pa_local.sh` still points at `pa-0a74be099bf6428a` (retired)** — intended failure mode forces S2788 first-action fresh mint.

**S2788 open sequence:**

```
context-kit orient

# Read this file end-to-end
# Read S2787 handoff §2 (three novel-precedent moments) + §3 (T1..T3 SIGN cycle) + §6 (open items)

# Freshness check. Should be FRESH · SHA-match at S2787 close SHA (39b69d820 or cascade PR SHA) — TWENTY-FOURTH close-cycle after PLAYBOOK-7.4.4.
bash tools/pa_local.sh "S2788 open — freshness check: ops_tool.version verdict + head_commit_sha; ops_tool.recent_recycles limit=5"

# Verify Sign Ledger tab shows 39 rows
# http://localhost:8000/workspace?tab=system&sub=sign-ledger

# Ledger check: confirm 39-row baseline survived close cascade
DJANGO_LOG_LEVEL=WARNING python manage.py zoom_out_streak_report --as-json 2>/dev/null | python -c "
import json, sys
d = sys.stdin.read()
r = json.loads(d[d.find('{'):])
assert r['total_rows']==39, r
print('OK — 39 rows, counts:', r['counts_by_classification'])
"

# Regression 9-suite (unchanged from S2787)
python manage.py test \
  core.tests.test_ops_auth_regression_2772 \
  core.tests.test_ops_query_param_allowlist_2773 \
  core.tests.test_pa_wrapper_ownership_2776 \
  core.tests.test_zoom_out_classifications_2777 \
  core.tests.test_zoom_out_tool_2780 \
  core.tests.test_governance_auth_regression_2780 \
  core.tests.test_platform_auth_regression_2784 \
  core.tests.test_decision_approve_auth_regression_2785 \
  core.tests.test_csrf_enforcement_2787 \
  --noinput

# Mint fresh pin scoped to selected S2788 candidate.
python manage.py session_lifecycle open --label <candidate-scoped-label>
python manage.py session_lifecycle history --limit 5

grep '^python tools/pa_chat.py' tools/pa_local.sh
```

**Anti-rubber-stamp check on S2788 first Rigby SIGN:** verify `tool_runs` non-empty. **PLAYBOOK-6.10.7 + 6.10.8 + 6.10.9 constitutional at v0.8.0** — every joint SIGN routing MUST include ≥1 zoom-out ask; folds MUST be classified + persisted BEFORE D-verdict; folds asserting concrete code-state facts MUST admit stable-state-pointer + file+line evidence + (i)/(ii)/(iii) outcome inline before classify+persist.

---

## OPEN RUNTIME ITEMS (from S2787 close)

1. **CSRF interceptor E2E eyeball** — Chris to confirm GovernanceTab Approve/Dismiss + platform commands function under session auth
2. **Fold C follow-up** — 2 unaudited csrf_exempt mutations at views_platform_command.py:2630/2696 lacking staff-only gate; likely more sites across `core/views_*.py`
3. **N24 anti-rubber-stamp SIGN codification** — 4 F-BLOCKING triggers now (S2778/S2780/S2786/S2787), memory rule promotion candidate
4. **Rigby SIGN response truncation pattern** — 2 observations (S2786 T2 partial + S2787 T1 severe); 3rd trigger promotes to substrate fix
5. **Auth-gate consolidation** — 4 sentinel modules now (add `_require_boardroom_staff`); wait for 5th before promoting to `core/auth_gates.py`
6. **AudioAgent completion-flip verification** (C1 linkage live, 0 rows populated)
7. **`test_session_freshness_2775` env drift**
8. **Model drift arc** (38 unrelated auto-migrations queued)
9. **Ledger split drift audit** (16/15/8 now)
10. **S2761 smoke test** (ops-surface, gated)
11. **S2758 D2 canonical decision** (needs joint SIGN)
12. **S2758 D4 HIGH-RISK wiring extension** (REPORT-ONLY)
13. **N13 handoff-date-format normalizer** (hygiene)
14. **P0.5 cost-threshold advance-to-freeze**
15. **P0.75 CI billing**
16. **RUR-C2 open eligible**
17. **S2758 D1 process_pa_chat_task payload strip**
18. **S2758 D5 local shim retirement**
19. **HMAC signing of `x-acting-user-id`**
20. **First observed partial-recycle event** — N10/N11 trigger
21. **Rigby S2774 forward-carry: ops-surface PR pause** — held
22. **30+ other lambda-`__import__` sites**
23. **Rigby S2773 forward-carry #5 (health_summary overlap)**
24. **N15 v2 / N21 v2 candidates** — deferred
25. **`session_lifecycle` refactor trigger** — still armed
26. **`/api/pa/*` future-endpoint audit trigger** — sharp 5-point test
27. **N22 v4+ candidates** — Django model, JSONL rotation, auto-hook
28. **N22 v2 time-window filters** — deferred until ~50+ rows temporal spread
29. **N17 smart-command-box creep** — row 21 `future_trigger`
30. **Second non-Rigby consumer of `zoom_out_tool`** — abstraction quality test
31. **Autonomous Rigby consultation of `zoom_out_tool.list`** — truer substrate-payoff signal
32. **I-0302 three-PR pattern amendment → PLAYBOOK-6.10.10** (re-slotted forward again)
33. **First graceful-degradation clause activation on PLAYBOOK-6.10.8** — pending
34. **Third served-artifact-freshness trigger** — PLAYBOOK-7.4.4 amendment candidate
35. **S2783 Fold 1 same-PR mitigation deferred** (GovernanceTab subtitle)
36. **S2784 Fold 29 automation identity trigger** — pre-prod → non-staff automation deploy
37. **5th auth-gate sentinel trigger** — consolidation into `core/auth_gates.py`
38. **Postgres cleanup follow-ups (S2774 carryover)**
39. **Second amendment with ledger-enumerable two-trigger corpus** — codify the amendment shape
40. **Frontend raw-fetch consolidation trigger** — first regression from a raw-fetch mutation site

---

## Twin-pointer card

📁 **Repo `/` + `/docs/` — S2787 artifacts:**

- **Ship code:** `core/views_platform_command.py` (removed 12 @csrf_exempt), `core/views_human_interface.py` (removed csrf_exempt from 15 method_decorator lists + unused import), `core/views_agent_learning.py` (removed 4 @csrf_exempt on boardroom mutations + updated stale docstrings), `frontend/src/lib/api.ts` (+22/-1 CSRF interceptor), `core/tests/test_csrf_enforcement_2787.py` (new 179-line regression), `tools/pa_local.sh` (+2/-1 pin refresh)
- **Handoff:** `docs/handoffs/SESSION_2787_CSRF_EXEMPT_CROSS_FILE_CLEANUP.md`
- **Predecessors:** S2786 handoff (Playbook v0.8.0), S2785 handoff (decision-approve authZ), S2784 handoff (platform mutations)

🖥️ **Workspace UI — `/workspaces` surface:**

- **System / Sign Ledger sub-tab** (`?tab=system&sub=sign-ledger`) — 39 rows now, including S2787 Folds A/B/C
- **Live surfaces:**
  - `logs/zoom_out_classifications.jsonl` — 39 rows at S2787 close
  - `logs/session_freshness.jsonl` — grew by 1 at S2787 open
  - `logs/recycle_events.jsonl` — +1 new event from S2787 close (`sha=39b69d820247`)

---

## Current repository state

| Field | Value |
|---|---|
| Branch | `main` |
| HEAD | `39b69d820` (S2787 ship) — cascade PR advances this at close |
| Playbook version | v0.8.0 (unchanged) |
| Playbook rule count | 205 (unchanged) |
| RUR-C1 state | S2755→S2786 CLOSED · **S2787 ENGINEERING SHIPPED** · RUR-C1 parent OPEN |
| Session pin | `pa-0a74be099bf6428a` (retired at S2787 close, force=true, eighteenth consecutive) |
| Wrapper default pin | `tools/pa_local.sh` — `pa-0a74be099bf6428a` (retired; forces fresh mint at S2788 open) |
| Live infra state | S2755→S2786 substrate + PLAYBOOK-6.10.9 first-in-wild proven at S2787 |
| Postgres :5432 | pg15 (July DB) — brew launchd `started` |
| Postgres pg16 | Parked (April fossil) |
| Freshness log | `logs/session_freshness.jsonl` — grew by 1 at S2787 open |
| Recycle log | `logs/recycle_events.jsonl` — +1 event (post-#3187, sha=39b69d820247) |
| Zoom-out ledger | `logs/zoom_out_classifications.jsonl` — **39 rows** (16 actionable / 15 mitigatable / 8 future_trigger) |
| Next move | Chris selects at S2788 open |

---

## Recommended session-open protocol (S2788)

1. `context-kit orient`
2. Read this file end-to-end
3. Read S2787 handoff §2 (three novel-precedent moments) + §3 (T1..T3 SIGN cycle) + §6 (open items)
4. **Freshness + regression 9-suite + ledger + Playbook verify** — see S2788 open sequence above
5. **Watch for** ledger 39-row baseline surviving cascade merge; freshness FRESH · SHA-match
6. If `staleness_verdict != FRESH` → escalate
7. **Check `brew services list | grep postgres` FIRST** if freshness fails oddly
8. Verify runtime state: `git log --oneline -5`; confirm wrapper at retired pin
9. Present candidate menu — engineering leans first per `feedback_engineering_bias_over_audit` (Fold C follow-up + auth-gate consolidation trigger + something entirely new)
10. **Anti-rubber-stamp check on first SIGN** — verify `tool_runs` non-empty
11. Chris directs S2788 P0 selection
12. Mint fresh pin with candidate-scoped label
13. Route work through Rigby joint agreement before coding
14. **PLAYBOOK-6.10.9 constitutional at v0.8.0:** any zoom-out fold asserting concrete code-state facts MUST admit stable-state-pointer + file+line evidence + (i)/(ii)/(iii) outcome inline before classify+persist

---

## Reference documents

Ordered by frequency of use at S2788:

1. [`CLAUDE.md`](CLAUDE.md) — repo bootstrap + Rigby collaboration protocol (anchor at v0.8.0)
2. [`docs/ENGINEERING_PLAYBOOK.md`](docs/ENGINEERING_PLAYBOOK.md) — v0.8.0 (205 rules)
3. [`docs/handoffs/SESSION_2787_CSRF_EXEMPT_CROSS_FILE_CLEANUP.md`](docs/handoffs/SESSION_2787_CSRF_EXEMPT_CROSS_FILE_CLEANUP.md) — **S2787 handoff (current)**
4. [`docs/handoffs/SESSION_2786_PLAYBOOK_V0_8_0_RATIFIED.md`](docs/handoffs/SESSION_2786_PLAYBOOK_V0_8_0_RATIFIED.md) — S2786 predecessor
5. [`docs/research/implementation/RATIFICATION_2026-07-14_PLAYBOOK_V0_8_0.md`](docs/research/implementation/RATIFICATION_2026-07-14_PLAYBOOK_V0_8_0.md) — v0.8.0 ratification envelope
6. [`docs/handoffs/SESSION_2785_DECISION_APPROVE_AUTH_AUDIT.md`](docs/handoffs/SESSION_2785_DECISION_APPROVE_AUTH_AUDIT.md) — S2785 handoff (2nd fold trigger)
7. [`docs/handoffs/SESSION_2784_FOLD4_PLATFORM_STAFF_ONLY.md`](docs/handoffs/SESSION_2784_FOLD4_PLATFORM_STAFF_ONLY.md) — S2784 handoff (1st fold trigger)
8. [`logs/zoom_out_classifications.jsonl`](logs/zoom_out_classifications.jsonl) — 39 rows at S2787 close (rows 37/38/39 are S2787 Folds A/B/C)
