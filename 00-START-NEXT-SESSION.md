# Next Session — Start Here

---

## READ THIS FIRST — SESSION 2783 CLOSED — WIRE GOVERNANCETAB (dead-code cleanup)

**Refreshed 2026-07-14 (SESSION 2783 CLOSED — one net-new engineering ship, small, ~1h. PR #3179 (`515d9c136`) wires the dead-code `GovernanceTab` (~500 LOC self-healing surface: Emergency Controls + Self-Healing progress + Run Remediation / Run Audit buttons + Pending Decisions) into `WorkspacePageNew.tsx` as a new `system.self-healing` sub-tab alongside SIGN Ledger. Actual diff +7 lines. Chris eyeball verified renders correctly (most metrics 0, 1 critical decision pending). Joint SIGN AGREE Option A with 6 tool_runs (anti-rubber-stamp gate PASS, THIRD consecutive session with Rigby dogfooding `zoom_out_tool.list`). 4 zoom-out folds classified + persisted BEFORE D-verdict per PLAYBOOK-6.10.8 — including a **novel Fold 4** (governance mutation endpoints have no auth gating, pre-existing, non-blocking under single-user pre-prod, but a hard pre-prod→prod gate) discovered during Fold 2 mitigation audit rather than in Rigby's returned folds. Ledger grew 23 → 27 rows. Post-merge `make recycle-all` per PLAYBOOK-7.4.4 (twentieth close-cycle post-codification) — **S2782 frontend detection triggered as designed** (auto-rebuild + collectstatic in-recycle, no manual dance). First engineering ship WITH frontend/ changes to land cleanly post-merge on the new substrate. Session opened clean off S2782 close's ⭐ recommended net-new candidate list — no substrate defects surfaced, no rework required. Novel: Fold 4 discovery (Claude verifying independently) closed the Fold 2 mitigation loop with a real answer rather than an assumption.)**

**S2783 ship:**

**PR #3179 · `515d9c136`** — `frontend/src/pages/WorkspacePageNew.tsx` (+6 lines), `tools/pa_local.sh` (+1/-1 pin refresh)

**Handoff:** `docs/handoffs/SESSION_2783_WIRE_GOVERNANCE_TAB.md`
**Post-merge:** `make recycle-all` per PLAYBOOK-7.4.4 completed (twentieth cycle).
**Ledger state at close:** `logs/zoom_out_classifications.jsonl` — 27 rows (12 same_pr_actionable / 10 same_pr_mitigatable / 5 future_trigger).

---

## SESSION-OPEN INFRA STORY (S2783)

Clean run. S2783 open sequence found:
- Freshness FRESH · SHA-match (HEAD=`698f4fca3`)
- Ledger 23-row baseline held from S2782 close
- C1 field (`AgentExecution.celery_task_id`) live on model, 1728 rows NULL (forward-only as designed, no populated rows yet — no in-wild timeout since S2782)
- `make recycle-all` frontend detection wired (verified via `make -n`)
- Playbook v0.7.0 rules 6.10.7 + 6.10.8 present (5 refs)
- Postgres pg15 started (donkeyking), pg16 parked — clean, no port-collision drift

Chris selected candidate #1 (wire GovernanceTab) from the S2782 ⭐ recommended list. No substrate defects surfaced through the entire close cycle.

---

## THE PIVOTS — WHY THIS SHIP MATTERS

**Small ships still count.** S2783 was a +7-line ship that dispatched a dead-code observation from S2780. Nothing dramatic — just a clean close on a paper cut. The S2771 rule streak (S2771–S2783 = 13 sessions) now has its first "boring completion" — no F-BLOCKING DISAGREE, no substrate defect, no scope creep. That's a healthy signal.

**Fold 4 is the substantive find.** Rigby's Fold 2 asked me to verify auth gating; she explicitly noted she did not verify it herself. When I checked `core/views_platform_command.py`, I found `@csrf_exempt @require_POST` with **no `@login_required` or DRF `permission_classes`** on 4 mutation endpoints (`emergency_halt_view`, `skin_lock_toggle_view`, `action_run_remediation_view`, `action_run_self_audit_view`). Pre-existing — wiring the tab didn't create this; the tab has been dead code, but the endpoints have been callable via direct API all along. Non-blocking under `project_single_user_pre_prod_operating_context`, but a **hard pre-prod → prod gate**. Recorded as fold 27 for tracking.

**The S2782 substrate paid off silently.** Post-merge `make recycle-all` detected `frontend/src/pages/WorkspacePageNew.tsx` in `HEAD~1..HEAD`, auto-rebuilt the frontend bundle + ran collectstatic + bounced daphne. No manual dance, no blank-page moment. First "with-frontend" ship on the new substrate — worked as designed.

**Third consecutive Rigby zoom_out_tool dogfooding session** (S2781, S2782, S2783). "Second non-Rigby consumer" trigger still outstanding.

---

## S2784 CANDIDATES (Chris selects at open)

### First — freshness/regression sanity

**Post-cascade freshness check:** wrapper pin retired; freshness should be FRESH · SHA-match at S2783 close SHA.
**Ledger baseline:** 27 rows expected (12/10/5). Any drift = investigate.

### Net-new engineering (⭐ recommended per `feedback_engineering_bias_over_audit`)

- **AudioAgent completion-flip verification** — C1 linkage is live but 0 rows populated yet. On-demand voiceover test run → join to `CeleryTaskEvent` → prove/disprove false-positive-timeout hypothesis. Could unblock a fix in `core/agents/ai_series_workflow_agent.py:1310`.
- **Fold 4 same-PR mitigation opportunity** — add `@login_required` + staff-only DRF `permission_classes` to the 4 governance mutation endpoints in `core/views_platform_command.py`. Small ship (~20 LOC). Closes a pre-prod → prod gate now instead of later. Nice fit with S2783's Fold 4 discovery.
- **Model drift arc** — S2782 discovered 38 unrelated auto-generated migrations queued by `makemigrations core`. Housekeeping candidate: isolated branch, review the 38 ops, decide which are legitimate vs abandoned. Non-trivial (~1-3h).
- **N24 anti-rubber-stamp SIGN codification** — Playbook MINOR (2+ triggers observed, ready when authorized).
- **Something entirely new** — new spider / UI page / agent capability / pipeline / dashboard / command. Fresh direction OK.

**Still gated by S2774 ops-surface pause:** N9, N20, Candidate 1 (S2761 smoke), 30+ `core/urls.py` lambda-`__import__` sites.

**Still owed:** P0.5 cost-threshold, P0.75 CI billing, memory rule promotion audit.

### Deferred (waiting on triggers, not calendar)

- **N10** — partial-recycle UI badge (gated on real partial-recycle event)
- **First real N11 PARTIAL_RECYCLE tile fire** (watching)
- **Q3 #5** (health_summary / ops_tool.overview overlap)
- **N22 v2 time-window filters** — trigger: ~50+ rows temporal spread (currently 27)
- **N22 v4+ candidates** — Django model, JSONL rotation (~500 rows away), auto-hook
- **Second non-Rigby consumer of `zoom_out_tool`** — trigger for factor-out abstraction test
- **N17 smart-command-box creep** — row 21 `future_trigger`
- **Autonomous Rigby consultation of `zoom_out_tool.list`** — watching (dogfooding streak S2781–S2783 doesn't count; Rigby uses it under my SIGN prompts, not autonomously)
- **First graceful-degradation clause activation on PLAYBOOK-6.10.8** — pending
- **Third served-artifact-freshness trigger** — PLAYBOOK-7.4.4 amendment candidate
- **S2783 Fold 1 same-PR mitigation** — Rigby's proposed subtitle deferred; track for follow-up if Chris hits label confusion between "Governance" and "Self-Healing"

### Post-S2783 owed

- **I-0302 three-PR pattern amendment** → PLAYBOOK-6.10.9 slot when opened
- **AudioAgent completion-flip verification** (see net-new)
- **`test_session_freshness_2775` env drift** — either guard test or always-populate error key
- **Ledger split drift audit** — 12/8/2 → 12/8/3 shift at S2782 open (non-blocking; not investigated)
- **Fold 4 auth gating gap** — pre-prod → prod gate; also a same-PR mitigation opportunity (see net-new)

---

## SESSION PIN — S2783 RETIRED (fresh mint required at S2784 open)

**Pin history (S2783):**

- `pa-56b6840c5296488f` (label `s2783-wire-governance-tab`) minted S2783 open; **retired at S2783 close (`force=true`, fourteenth consecutive per S2770+ pattern)**

**Wrapper `tools/pa_local.sh` still points at `pa-56b6840c5296488f` (retired)** — intended failure mode forces S2784 first-action fresh mint.

**S2784 open sequence:**

```
context-kit orient

# Read this file end-to-end
# Read S2783 handoff §2 (session shape — first S2783 candidate cleanly off queue) + §4 (Fold 4 novel find)

# Freshness check. Should be FRESH · SHA-match at S2783 close SHA (515d9c136) — TWENTIETH close-cycle after PLAYBOOK-7.4.4.
bash tools/pa_local.sh "S2784 open — freshness check: ops_tool.version verdict + head_commit_sha; ops_tool.recent_recycles limit=5"

# Verify Self-Healing tab still renders (Chris eyeball)
# http://localhost:8000/workspace?tab=system&sub=self-healing

# Ledger check: confirm 27-row baseline survived close cascade
DJANGO_LOG_LEVEL=WARNING python manage.py zoom_out_streak_report --as-json 2>/dev/null | python -c "
import json, sys
d = sys.stdin.read()
r = json.loads(d[d.find('{'):])
assert r['total_rows']==27, r
print('OK — 27 rows, counts:', r['counts_by_classification'])
"

# Regression: 6-suite (skipping test_session_freshness_2775 known env-drift)
python manage.py test \
  core.tests.test_ops_auth_regression_2772 \
  core.tests.test_ops_query_param_allowlist_2773 \
  core.tests.test_pa_wrapper_ownership_2776 \
  core.tests.test_zoom_out_classifications_2777 \
  core.tests.test_zoom_out_tool_2780 \
  core.tests.test_governance_auth_regression_2780 \
  --noinput

# Playbook v0.7.0 verify — rules still present
grep -c 'PLAYBOOK-6\.10\.[7-8]' docs/ENGINEERING_PLAYBOOK.md  # expect >=5

# Mint fresh pin scoped to selected S2784 candidate.
python manage.py session_lifecycle open --label <candidate-scoped-label>
python manage.py session_lifecycle history --limit 5

grep '^python tools/pa_chat.py' tools/pa_local.sh
```

**Anti-rubber-stamp check on S2784 first Rigby SIGN:** verify `tool_runs` non-empty. **PLAYBOOK-6.10.7 + 6.10.8 constitutional at v0.7.0** — every joint SIGN routing MUST include ≥1 zoom-out ask; folds MUST be classified + persisted BEFORE D-verdict.

---

## OPEN RUNTIME ITEMS (from S2783 close)

1. **AudioAgent completion-flip verification** (C1 linkage live, awaiting next timeout occurrence for one-query verification)
2. **Fold 4 auth gating gap on governance mutation endpoints** (pre-existing; pre-prod → prod gate; also a same-PR mitigation opportunity, ~20 LOC)
3. **`test_session_freshness_2775` env drift** (either test guard or always-populate error key)
4. **Model drift arc** (38 unrelated auto-migrations queued — housekeeping candidate)
5. **Ledger split drift audit** (12/8/2 → 12/8/3 shift at S2782 open)
6. **S2761 smoke test** (ops-surface, gated)
7. **S2758 D2 canonical decision** (needs joint SIGN)
8. **S2758 D4 HIGH-RISK wiring extension** (REPORT-ONLY)
9. **N13 handoff-date-format normalizer** (hygiene)
10. **P0.5 cost-threshold advance-to-freeze**
11. **P0.75 CI billing**
12. **RUR-C2 open eligible**
13. **S2758 D1 process_pa_chat_task payload strip**
14. **S2758 D5 local shim retirement**
15. **HMAC signing of `x-acting-user-id`**
16. **Memory rule promotion audit** — N24 anti-rubber-stamp SIGN at 2+ triggers
17. **First observed partial-recycle event** — N10/N11 trigger
18. **Rigby S2774 forward-carry: ops-surface PR pause** — held; S2783 was frontend-only, unaffected
19. **30+ other lambda-`__import__` sites**
20. **Rigby S2773 forward-carry #5 (health_summary overlap)**
21. **N15 v2 / N21 v2 candidates** — deferred
22. **`session_lifecycle` refactor trigger** — still armed
23. **`/api/pa/*` future-endpoint audit trigger** — sharp 5-point test
24. **N22 v4+ candidates** — Django model, JSONL rotation, auto-hook
25. **N22 v2 time-window filters** — deferred until ~50+ rows temporal spread
26. **N17 smart-command-box creep** — row 21 `future_trigger`
27. **Second non-Rigby consumer of `zoom_out_tool`** — abstraction quality test
28. **Autonomous Rigby consultation of `zoom_out_tool.list`** — truer substrate-payoff signal
29. **N24 anti-rubber-stamp SIGN codification** — 2+ triggers; ready when authorized
30. **I-0302 three-PR pattern amendment** — take PLAYBOOK-6.10.9 when it opens
31. **First graceful-degradation clause activation on PLAYBOOK-6.10.8** — pending
32. **Third served-artifact-freshness trigger** — PLAYBOOK-7.4.4 amendment candidate
33. **S2783 Fold 1 same-PR mitigation deferred** (subtitle for GovernanceTab if label confusion appears)
34. **Postgres cleanup follow-ups (S2774 carryover)**

---

## Twin-pointer card

📁 **Repo `/` + `/docs/` — S2783 artifacts:**

- **Ship code:** `frontend/src/pages/WorkspacePageNew.tsx` (+6 lines), `tools/pa_local.sh` (+1/-1)
- **Handoff:** `docs/handoffs/SESSION_2783_WIRE_GOVERNANCE_TAB.md`
- **Predecessors:** S2782 handoff (substrate + C1), S2781 handoff (N17), S2780 handoff (N22 v3)

🖥️ **Workspace UI — `/workspaces` surface:**

- **NEW at S2783: Self-Healing tab** — `?tab=system&sub=self-healing` (Emergency Controls + Self-Healing progress + Run Remediation/Audit buttons + Pending Decisions)
- **Adjacent surfaces preserved:** SIGN Ledger `?sub=sign-ledger`, Governance `?sub=boardroom`
- **Live surfaces:**
  - `logs/zoom_out_classifications.jsonl` — 27 rows at S2783 close
  - `logs/session_freshness.jsonl` — grows per pin mint
  - `logs/recycle_events.jsonl` — +1 new event from S2783 close (`sha=515d9c136`)
  - `zoom_out_tool.list` — Rigby PA-tool surface (in-wild consumer for third consecutive session at S2783 SIGN)
  - `GET /api/governance/zoom-out-ledger/` — Chris frontend surface

---

## Current repository state

| Field | Value |
|---|---|
| Branch | `main` |
| HEAD | `515d9c136` (S2783 ship) — cascade PR advances this at close |
| Playbook version | v0.7.0 (RATIFIED S2778) |
| Playbook rule count | 204 |
| RUR-C1 state | S2755→S2782 CLOSED · **S2783 dead-code cleanup CLOSED** · RUR-C1 parent OPEN |
| Session pin | `pa-56b6840c5296488f` (retired at S2783 close, force=true, fourteenth consecutive) |
| Wrapper default pin | `tools/pa_local.sh` — `pa-56b6840c5296488f` (retired; forces fresh mint at S2784 open) |
| Live infra state | S2755→S2782 substrate + **GovernanceTab surface live at `?tab=system&sub=self-healing`** |
| Postgres :5432 | pg15 (July DB) — brew launchd `started` |
| Postgres pg16 | Parked (April fossil) |
| Freshness log | `logs/session_freshness.jsonl` — grew by 1 at S2783 open |
| Recycle log | `logs/recycle_events.jsonl` — +1 event (post-#3179) |
| Zoom-out ledger | `logs/zoom_out_classifications.jsonl` — **27 rows** (12 actionable / 10 mitigatable / 5 future_trigger) |
| Next move | Chris selects at S2784 open |

---

## Recommended session-open protocol (S2784)

1. `context-kit orient`
2. Read this file end-to-end
3. Read S2783 handoff §2 (session shape) + §4 (Fold 4 novel find)
4. **Freshness + regression + ledger + eyeball verify + Playbook verify** — see S2784 open sequence in §SESSION PIN above
5. **Watch for** ledger 27-row baseline surviving cascade merge; freshness FRESH · SHA-match; Rigby autonomous consultation of `zoom_out_tool.list` (truer substrate-payoff signal)
6. If `staleness_verdict != FRESH` → escalate (twentieth-cycle PLAYBOOK-7.4.4 violation OR possible PARTIAL_RECYCLE)
7. **Check `brew services list | grep postgres` FIRST** if freshness fails oddly
8. Verify runtime state: `git log --oneline -5`; confirm wrapper at retired pin
9. Present candidate menu — Fold 4 same-PR mitigation is a strong small-ship candidate given S2783's discovery
10. **Anti-rubber-stamp check on first SIGN** — verify `tool_runs` non-empty (N24 codification pending)
11. Chris directs S2784 P0 selection
12. Mint fresh pin with candidate-scoped label
13. Route work through Rigby joint agreement before coding

---

## Reference documents

Ordered by frequency of use at S2784:

1. [`CLAUDE.md`](CLAUDE.md) — repo bootstrap + Rigby collaboration protocol
2. [`docs/ENGINEERING_PLAYBOOK.md`](docs/ENGINEERING_PLAYBOOK.md) — v0.7.0 (latest ratified)
3. [`docs/handoffs/SESSION_2783_WIRE_GOVERNANCE_TAB.md`](docs/handoffs/SESSION_2783_WIRE_GOVERNANCE_TAB.md) — **S2783 handoff (current)**
4. [`docs/handoffs/SESSION_2782_SUBSTRATE_FIX_PLUS_C1_OBSERVABILITY.md`](docs/handoffs/SESSION_2782_SUBSTRATE_FIX_PLUS_C1_OBSERVABILITY.md) — S2782 handoff
5. [`docs/handoffs/SESSION_2781_N17_SESSION_NUMBER_PILL_SEARCH_CHIP.md`](docs/handoffs/SESSION_2781_N17_SESSION_NUMBER_PILL_SEARCH_CHIP.md) — S2781 handoff (N17)
6. [`docs/handoffs/SESSION_2780_N22V3_ZOOM_OUT_TOOL_FACTOR_OUT_GOVERNANCE_UI.md`](docs/handoffs/SESSION_2780_N22V3_ZOOM_OUT_TOOL_FACTOR_OUT_GOVERNANCE_UI.md) — S2780 handoff
7. `Makefile` — recycle-all with S2782 frontend detection (paid off at S2783)
8. `frontend/src/pages/WorkspacePageNew.tsx` — S2783 ship site
9. `frontend/src/pages/workspace/tabs/GovernanceTab.tsx` — the newly-wired surface (~500 LOC)
10. `core/views_platform_command.py` — governance mutation endpoints (Fold 4 audit target: `emergency_halt_view` line ~919, `skin_lock_toggle_view` line ~1172, `action_run_remediation_view` line ~2040, `action_run_self_audit_view` line ~2250)
11. `logs/zoom_out_classifications.jsonl` — 27 rows
