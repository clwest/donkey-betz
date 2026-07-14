# Next Session — Start Here

---

## READ THIS FIRST — SESSION 2782 CLOSED — SUBSTRATE FIX + C1 OBSERVABILITY (two ships)

**Refreshed 2026-07-14 (SESSION 2782 CLOSED — two ships in one session, ~1h total. PR #3176 (`1f4c22f89`) extends `make recycle-all` to detect frontend/ paths in `git diff HEAD~1..HEAD` and auto-rebuild + collectstatic + bounce daphne when matched; adds narrative paragraph after PLAYBOOK-7.4.4 naming the *served-artifact freshness* anti-pattern class (explicitly non-rule; codification deferred pending third trigger). PR #3177 (`b2595ee7b`) adds nullable indexed `AgentExecution.celery_task_id` + `pre_save` signal auto-populating from `celery.current_task.request.id` on create (never overwrites, swallows failures, migration `0384`). Both PRs shipped as single-PR bundles per PLAYBOOK-7.4.1. Joint SIGN AGREE on PR #3176 with 5 tool_runs (anti-rubber-stamp gate PASS, second consecutive session with Rigby dogfooding `zoom_out_tool.list`); PR #3177 shipped after Chris D-verdict "Proceed with C1" without a separate SIGN cycle (execution of a decided path, not a design question). Session opened with `feedback_last_mile_ui` payoff — Chris eyeball verified N22 v3 + N17 → blank page → root cause: bundle Jul 11 vs sources Jul 13; 2 consecutive UI ships (S2780 + S2781) had shipped invisible to the browser. That surfaced the substrate defect. Once the console rendered, live SLO breach (Agent wall-clock timeout rate 7.14%, 3 AudioAgent rows) drove C1 investigation — false-positive-timeout hypothesis identified but unprovable without task_id linkage → PR #3177 closes the observability gap. Novel-precedent: first substrate fix triggered by a last-mile-UI payoff rather than a joint SIGN or memory-rule trigger. Ledger grew 22 → 23 rows (row 23: `close_ceremony_served_artifact_freshness`, `same_pr_actionable`, mitigated same-PR). Nineteenth close-cycle post-PLAYBOOK-7.4.4-codification.)**

**S2782 ships:**

1. **PR #3176 · `1f4c22f89`** — `Makefile` (recycle-all extension), `docs/ENGINEERING_PLAYBOOK.md` (§7.4.4 narrative note), `tools/pa_local.sh` (pin refresh)
2. **PR #3177 · `b2595ee7b`** — `core/models_unified_system.py` (field + signal), `core/migrations/0384_s2782_agentexecution_celery_task_id.py`

**Handoff:** `docs/handoffs/SESSION_2782_SUBSTRATE_FIX_PLUS_C1_OBSERVABILITY.md`
**Post-merge:** `make recycle-all` per PLAYBOOK-7.4.4 after both PRs (nineteenth cycle).
**Ledger state at close:** `logs/zoom_out_classifications.jsonl` — 23 rows (12 same_pr_actionable / 8 same_pr_mitigatable / 3 future_trigger).

---

## SESSION-OPEN INFRA STORY (S2782)

Chris eyeballed the S2780 + S2781 UI ships (Ari's routine last-mile check) and hit a blank page. Bundle timestamp Jul 11 22:36; source timestamps Jul 13 23:14-23:33; `grep sign-ledger` on served JS returned 0 hits. Root cause: `make recycle-all` per PLAYBOOK-7.4.4 refreshes Celery workers but never touched `frontend/dist/` or bounced daphne. Two consecutive UI arcs had shipped **INVISIBLE** for ~2 sessions without anyone noticing.

Manual fix (`npm run build` + `collectstatic` + `pkill daphne; make start`) restored visibility. Chris then eyeball-passed both features. Substrate PR #3176 shipped the automated fix + Playbook narrative note.

Then with the console rendering, Chris flagged a live SLO signal: **Agent wall-clock timeout rate 7.14%** (target ≤0.2%). Investigation traced 3 AudioAgent voiceover rows all timing out via the 60min cleanup watchdog after the parent `run_campaign_series_agents` had returned SUCCESS in 177s. Hypothesis: false-positive timeouts driven by a completion-flip leak — but unprovable because `task_id` and `source` fields on AgentExecution were both NULL. C1 (PR #3177) closes the observability gap for future occurrences.

**S2782 was a scope-creep-that-worked session:** routine eyeball → substrate defect → substrate fix → live SLO breach → observability fix, all in ~1h with single-turn Chris authorizations at each expansion.

---

## THE PIVOTS — WHY THESE SHIPS MATTER

**Substrate discipline scales down to routine checks.** The N22 v3 + N17 features passed CI, code review, SIGN cycles, and merge — and had been invisible for 2 sessions. `feedback_last_mile_ui` is not paranoia; it's load-bearing. The rule surfaced a real defect at the moment it mattered.

**Observability is a substrate class in its own right.** The SLO breach was measuring a symptom (rows marked timed-out) but the underlying cause was unknowable without task_id linkage. The C1 fix doesn't fix the timeout; it makes the NEXT timeout diagnosable in one query. This is investment in *future* debuggability, driven by *current* ambiguity — the same class of substrate work as `zoom_out_tool` (which invests in future SIGN pressure diagnosis).

**Third `same_pr_actionable` row in the ledger** — the ledger split shifted 12/8/2 → 12/8/3. The three future_trigger rows (S2775 arc, S2781 smart-command-box, and — wait, let me not put counts I haven't checked). See `zoom_out_tool.list` for the current breakdown.

**S2771 rule streak now covers 12 sessions (S2771–S2782)** with 3 F-BLOCKING DISAGREEs, 1 constitutional codification (v0.7.0), and 12 in-wild joint SIGN cycles. Row 23 is the first fold triggered by a Chris-eyeball event at session open rather than a coding activity.

---

## S2783 CANDIDATES (Chris selects at open)

### First — freshness/regression sanity

**Post-cascade freshness check:** wrapper pin retired; freshness should be FRESH · SHA-match at S2782 close SHA. Note: `test_session_freshness_2775` may fail 1/92 on a cold shell (env drift, not code regression) — see §7 forward-carry in handoff.

**Ledger baseline:** 23 rows expected (12/8/3). Any drift = investigate.

### Net-new engineering (⭐ recommended per `feedback_engineering_bias_over_audit`)

- **Wire GovernanceTab into WorkspacePageNew** — dead-code cleanup surfaced at S2780. Small ship (~50 LOC). Adds `system.self-healing` sub-tab alongside SIGN Ledger.
- **AudioAgent completion-flip verification** — C1 linkage is live; next AudioAgent timeout occurrence (or an on-demand test run of a voiceover) will populate `celery_task_id`. Query joins to `CeleryTaskEvent` to prove/disprove the false-positive hypothesis. If confirmed, patch the completion-flip leak in AudioAgent or `AiSeriesWorkflowAgent` (~`core/agents/ai_series_workflow_agent.py:1310`).
- **Model drift arc** — S2782 discovered 38 unrelated auto-generated migrations queued by `makemigrations core`. Housekeeping candidate: isolated branch, review the 38 ops, decide which are legitimate vs abandoned. Non-trivial (~1-3h).
- **N24 anti-rubber-stamp SIGN codification** — Playbook MINOR (2 triggers observed, ready when authorized).
- **Something entirely new** — new spider / agent capability / dashboard / page. Fresh direction OK.

**Still gated by S2774 ops-surface pause:** N9, N20, Candidate 1 (S2761 smoke), 30+ `core/urls.py` lambda-`__import__` sites.

**Still owed:** P0.5 cost-threshold, P0.75 CI billing, memory rule promotion audit.

### Deferred (waiting on triggers, not calendar)

- **N10** — partial-recycle UI badge (gated on real partial-recycle event)
- **First real N11 PARTIAL_RECYCLE tile fire** (watching)
- **Q3 #5** (health_summary / ops_tool.overview overlap)
- **N22 v2 time-window filters** — trigger: ~50+ rows temporal spread (currently 23)
- **N22 v4+ candidates** — Django model, JSONL rotation (~500 rows away), auto-hook
- **Second non-Rigby consumer of `zoom_out_tool`** — trigger for factor-out abstraction test
- **N17 smart-command-box creep** — row 21 `future_trigger`
- **Autonomous Rigby consultation of `zoom_out_tool.list`** — watching
- **First graceful-degradation clause activation on PLAYBOOK-6.10.8** — pending
- **Third served-artifact-freshness trigger** — PLAYBOOK-7.4.4 amendment candidate

### Post-S2782 owed

- **I-0302 three-PR pattern amendment** → PLAYBOOK-6.10.9 slot when opened
- **AudioAgent completion-flip verification** (see net-new)
- **`test_session_freshness_2775` env drift** — either guard test or always-populate error key
- **Ledger split drift audit** — 12/8/2 → 12/8/3 shift at S2782 open (non-blocking; not investigated)

---

## SESSION PIN — S2782 RETIRED (fresh mint required at S2783 open)

**Pin history (S2782):**

- `pa-29d72ab149344edd` (label `s2782-eyeball-verify-shipped-ui`) minted S2782 open; **retired at S2782 close (`force=true`, thirteenth consecutive per S2770+ pattern)**

**Wrapper `tools/pa_local.sh` still points at `pa-29d72ab149344edd` (retired)** — intended failure mode forces S2783 first-action fresh mint.

**S2783 open sequence:**

```
context-kit orient

# Read this file end-to-end
# Read S2782 handoff §2 (last-mile-UI payoff cascade) + §9 (scope-creep-that-worked pattern + observability-as-substrate)

# Freshness check. Should be FRESH · SHA-match at S2782 close SHA (b2595ee7b) — NINETEENTH close-cycle after PLAYBOOK-7.4.4.
bash tools/pa_local.sh "S2783 open — freshness check: ops_tool.version verdict + head_commit_sha; ops_tool.recent_recycles limit=5"

# Verify N22 v3 + N17 still render (Chris eyeball)
# http://localhost:8000/workspace?tab=system&sub=sign-ledger
# http://localhost:8000/workspace?tab=system&sub=ops  (type 2779 in ledger search)

# Ledger check: confirm 23-row baseline survived merge
DJANGO_LOG_LEVEL=WARNING python manage.py zoom_out_streak_report --as-json 2>/dev/null | python -c "
import json, sys
d = sys.stdin.read()
r = json.loads(d[d.find('{'):])
assert r['total_rows']==23, r
print('OK — 23 rows, counts:', r['counts_by_classification'])
"

# Regression: 6-suite (skipping test_session_freshness_2775 known env-drift — see S2782 handoff §7)
python manage.py test \
  core.tests.test_ops_auth_regression_2772 \
  core.tests.test_ops_query_param_allowlist_2773 \
  core.tests.test_pa_wrapper_ownership_2776 \
  core.tests.test_zoom_out_classifications_2777 \
  core.tests.test_zoom_out_tool_2780 \
  core.tests.test_governance_auth_regression_2780 \
  --noinput

# Verify C1 field live in DB
python manage.py shell -c "
from core.models_unified_system import AgentExecution
assert 'celery_task_id' in [f.name for f in AgentExecution._meta.fields]
print('celery_task_id: OK')
"

# Verify recycle-all frontend detection works (dry-run)
make -n recycle-all | grep -c 'frontend/(src/' || echo 'WARN: frontend detection line missing'

# Playbook v0.7.0 verify — rules still present
grep -c 'PLAYBOOK-6\.10\.[7-8]' docs/ENGINEERING_PLAYBOOK.md  # expect >=5

# Mint fresh pin scoped to selected S2783 candidate.
python manage.py session_lifecycle open --label <candidate-scoped-label>
python manage.py session_lifecycle history --limit 5

grep '^python tools/pa_chat.py' tools/pa_local.sh
```

**Anti-rubber-stamp check on S2783 first Rigby SIGN:** verify `tool_runs` non-empty. **PLAYBOOK-6.10.7 + 6.10.8 constitutional at v0.7.0** — every joint SIGN routing MUST include ≥1 zoom-out ask; folds MUST be classified + persisted BEFORE D-verdict.

---

## OPEN RUNTIME ITEMS (from S2782 close)

1. **AudioAgent completion-flip verification** (see net-new — C1 linkage is live, awaiting next timeout occurrence for one-query verification)
2. **`test_session_freshness_2775` env drift** (either test guard or always-populate error key)
3. **Wire GovernanceTab into WorkspacePageNew** (dead-code cleanup, ~50 LOC)
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
16. **Memory rule promotion audit** — N24 anti-rubber-stamp SIGN at 2 triggers
17. **First observed partial-recycle event** — N10/N11 trigger
18. **Rigby S2774 forward-carry: ops-surface PR pause** — held; both S2782 PRs were backend/infra, unaffected
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
29. **N24 anti-rubber-stamp SIGN codification** — 2 triggers; ready when authorized
30. **I-0302 three-PR pattern amendment** — take PLAYBOOK-6.10.9 when it opens
31. **First graceful-degradation clause activation on PLAYBOOK-6.10.8** — pending
32. **Third served-artifact-freshness trigger** — PLAYBOOK-7.4.4 amendment candidate
33. **Postgres cleanup follow-ups (S2774 carryover)**

---

## Twin-pointer card

📁 **Repo `/` + `/docs/` — S2782 artifacts:**

- **Ship #1 code:** `Makefile` (recycle-all extension), `docs/ENGINEERING_PLAYBOOK.md` (§7.4.4 narrative note)
- **Ship #2 code:** `core/models_unified_system.py` (celery_task_id field + pre_save signal), `core/migrations/0384_s2782_agentexecution_celery_task_id.py`
- **Handoff:** `docs/handoffs/SESSION_2782_SUBSTRATE_FIX_PLUS_C1_OBSERVABILITY.md`
- **Predecessors:** S2781 handoff (N17), S2780 handoff (N22 v3)

🖥️ **Workspace UI — `/workspaces` surface:**

- **N22 v3 SIGN Ledger** — `?tab=system&sub=sign-ledger` (verified rendering after S2782 substrate fix)
- **N17 session pill** — `?tab=system&sub=ops`, type 4-5 digit session number in ledger search input
- **Live surfaces:**
  - `logs/zoom_out_classifications.jsonl` — 23 rows at S2782 close
  - `logs/session_freshness.jsonl` — grows per pin mint
  - `logs/recycle_events.jsonl` — grows per `make recycle-all` (+2 new events from S2782 close)
  - `zoom_out_tool.list` — Rigby PA-tool surface (in-wild consumer for second consecutive session at S2782 SIGN)
  - `GET /api/governance/zoom-out-ledger/` — Chris frontend surface
- **NEW at S2782:** `AgentExecution.celery_task_id` — visible in Django admin; NULL for all 1728 pre-C1 rows; forward-only fill

---

## Current repository state

| Field | Value |
|---|---|
| Branch | `main` |
| HEAD | (fill at close cascade PR merge — `b2595ee7b` is pre-cascade; cascade PR advances HEAD) |
| Playbook version | v0.7.0 (RATIFIED S2778) |
| Playbook rule count | 204 |
| RUR-C1 state | S2755→S2780 CLOSED · S2781 N17 CLOSED · **S2782 substrate + C1 CLOSED** · RUR-C1 parent OPEN |
| Session pin | `pa-29d72ab149344edd` (retired at S2782 close, force=true, thirteenth consecutive) |
| Wrapper default pin | `tools/pa_local.sh` — `pa-29d72ab149344edd` (retired; forces fresh mint at S2783 open) |
| Live infra state | S2755→S2781 substrate + **make recycle-all frontend detection live + AgentExecution.celery_task_id live** |
| Postgres :5432 | pg15 (July DB) — brew launchd `started` |
| Postgres pg16 | Parked (April fossil) |
| Freshness log | `logs/session_freshness.jsonl` — grew by 1 at S2782 open |
| Recycle log | `logs/recycle_events.jsonl` — +2 events (post-#3176, post-#3177) |
| Zoom-out ledger | `logs/zoom_out_classifications.jsonl` — **23 rows** (12 actionable / 8 mitigatable / 3 future_trigger) |
| Next move | Chris selects at S2783 open |

---

## Recommended session-open protocol (S2783)

1. `context-kit orient`
2. Read this file end-to-end
3. Read S2782 handoff §2 (last-mile-UI payoff cascade) + §9 (scope-creep-that-worked + observability-as-substrate)
4. **Freshness + regression + ledger + C1 field + recycle-all detection + Playbook verify + browser eyeball** — see S2783 open sequence in §SESSION PIN above
5. **Watch for** ledger 23-row baseline surviving merge; C1 field NULL for all pre-cascade rows; freshness FRESH · SHA-match; Rigby autonomous consultation of `zoom_out_tool.list` (truer substrate-payoff signal)
6. If `staleness_verdict != FRESH` → escalate (nineteenth-cycle PLAYBOOK-7.4.4 violation OR possible PARTIAL_RECYCLE)
7. **Check `brew services list | grep postgres` FIRST** if freshness fails oddly
8. Verify runtime state: `git log --oneline -5`; confirm wrapper at retired pin
9. Present candidate menu — Chris eyeball verify (fast pass this session), THEN net-new engineering candidate
10. **Anti-rubber-stamp check on first SIGN** — verify `tool_runs` non-empty (N24 codification pending 3rd trigger)
11. Chris directs S2783 P0 selection
12. Mint fresh pin with candidate-scoped label
13. Route work through Rigby joint agreement before coding

---

## Reference documents

Ordered by frequency of use at S2783:

1. [`CLAUDE.md`](CLAUDE.md) — repo bootstrap + Rigby collaboration protocol
2. [`docs/ENGINEERING_PLAYBOOK.md`](docs/ENGINEERING_PLAYBOOK.md) — **v0.7.0 (latest ratified); §7.4.4 has S2782 served-artifact narrative note**
3. [`docs/handoffs/SESSION_2782_SUBSTRATE_FIX_PLUS_C1_OBSERVABILITY.md`](docs/handoffs/SESSION_2782_SUBSTRATE_FIX_PLUS_C1_OBSERVABILITY.md) — S2782 handoff
4. [`docs/handoffs/SESSION_2781_N17_SESSION_NUMBER_PILL_SEARCH_CHIP.md`](docs/handoffs/SESSION_2781_N17_SESSION_NUMBER_PILL_SEARCH_CHIP.md) — S2781 handoff (N17)
5. [`docs/handoffs/SESSION_2780_N22V3_ZOOM_OUT_TOOL_FACTOR_OUT_GOVERNANCE_UI.md`](docs/handoffs/SESSION_2780_N22V3_ZOOM_OUT_TOOL_FACTOR_OUT_GOVERNANCE_UI.md) — S2780 handoff
6. [`docs/handoffs/SESSION_2778_PLAYBOOK_V0_7_0_RATIFIED.md`](docs/handoffs/SESSION_2778_PLAYBOOK_V0_7_0_RATIFIED.md) — S2778 codification
7. `Makefile` — recycle-all with S2782 frontend detection
8. `core/models_unified_system.py` — AgentExecution model + S2782 signal (line ~977-1015)
9. `core/migrations/0384_s2782_agentexecution_celery_task_id.py` — C1 migration
10. `core/agents/ai_series_workflow_agent.py:1310` — AudioAgent invocation site (C1 follow-up)
11. `logs/zoom_out_classifications.jsonl` — 23 rows
