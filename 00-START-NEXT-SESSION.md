# Next Session — Start Here

---

## READ THIS FIRST — SESSION 2795 CLOSED — PA tools validation-coverage gap map

**Refreshed 2026-07-15 (SESSION 2795 CLOSED — engineering-first session #9 in row per `feedback_engineering_bias_over_audit`. NOT on the pre-planned S2795 open menu — surfaced by Chris mid-session: "Rigby has noted a few times that she doesn't have certain tools to call from the chat UI. I know at one point we had started you and Rigby testing/verifing all the tools she has and things like curl/HTTP tools she might need but I don't know if we ever actually finished it." Investigated: S2728→S2732 tool validation campaign shipped 57 patches + 270 tests across 18 tools, but 18/113 pairs = ~7% per-tool coverage. Right-sized ship: gap map that surfaces the shopping list without pre-committing to another 5-session sweep. Rigby T1 tool-grounded SIGN (6+ repo_tool calls) discovered pre-existing `build_pa_tool_audit` command + `PA_TOOL_AUDIT.md` (84KB stale from 2026-05-12) + `test_pa_tool_schema_drift.py` CI guard, and upgraded ship shape from B (new command) to (c) fold gap map into build_pa_tool_audit + preserve BC. 5 folds classified + persisted BEFORE Chris D-verdict: 60 `same_pr_actionable` (F1 doc_exists!=validated 3-state distinction — adopted), 61 `same_pr_mitigatable` (F2 "cross_cutting" too generous rename — adopted), 62 `same_pr_actionable` (F3 shopping-list coupling risk — adopted via triage slices + NOT-burn-down framing), 63 `future_trigger` (F4 telemetry-backed complaints — deferred to ToolCallRecord surface), 64 `same_pr_mitigatable` (F5 schema quality lint — adopted). Full 17-suite regression: 318 tests OK (295 prior + 23 new). Post-merge dogfood: Rigby found `docs/audits/PA_TOOLS_GAP_MAP_S2795.md` via `repo_tool.search`. Rigby SIGN response non-truncated (sample size 6 — pattern strongly holds). THIRTY-FIFTH close-cycle post-PLAYBOOK-7.4.4.)**

**S2795 ship:**

**PR #3203 · `5ec09d625`** — 6 files, +1756 / -321. New pure-logic module `core/services/pa_tools_gap_map.py` (431 lines) + extended `build_pa_tool_audit` with 4 optional flags (`--include-validation-xref`, `--emit-gap-json`, `--gap-only`, `--output PATH`) preserving BC on default. 23-test contract suite locks 14 contracts. First artifact at `docs/audits/PA_TOOLS_GAP_MAP_S2795.md`.

**Handoff:** `docs/handoffs/SESSION_2795_PA_TOOLS_GAP_MAP.md`
**Post-merge:** `make recycle-all` per PLAYBOOK-7.4.4 completed (thirty-fifth cycle, sha=`5ec09d625e85`).
**Ledger state at close:** `logs/zoom_out_classifications.jsonl` — **64 rows** (26 same_pr_actionable / 22 same_pr_mitigatable / 16 future_trigger).

---

## SESSION-OPEN INFRA STORY (S2795)

Engineering-first session #9 in row. **Critical process moment:** Chris did NOT pick from the S2795 candidate menu I wrote at S2794 close. He surfaced a NEW candidate mid-session ("Rigby doesn't have certain tools…"). Candidate menus are useful priors, not gates.

Rigby's tool-grounded read reshaped ship scope BEFORE code was written — she found `build_pa_tool_audit` (existing) + `PA_TOOL_AUDIT.md` (2 months stale) + `test_pa_tool_schema_drift.py` CI guard. Without her read I might have built a parallel command duplicating 60% of the introspection. Direct payoff of `feedback_cycle_1a_verify_before_build`.

Fresh headline counts locked in the PR body (via `build_pa_tool_audit --check` at HEAD `a2b3e484b`): **158 tool names / 114 schemas / 157 handlers / 113 pairs / 44 handler-only agents by design / 1 meta-tool.**

**Gap map first emit:** **105 UNTESTED · 8 validated_doc_exists_unknown · 44 agent_via_run_agent · 1 meta_no_handler.** Schema lints: 23 tools with actions_not_mentioned_in_description; 14 with no_required; 1 with no_properties.

Top 5 triage slices (grouped by handler file, ~2-6 sessions each at 4/session S2728→S2732 pace):
- `td_handlers_agents` — 23 untested (~6 sessions)
- `td_handlers_core` — 22 untested (~6 sessions)
- `td_handlers_content` — 12 untested (~3 sessions)
- `td_handlers_gateway` — 11 untested (~3 sessions)
- `td_handlers_ops` — 8 untested (~2 sessions)

Sum of top-5 triage: ~20 sessions. Total untested: 105 = ~27 sessions if you validate all. **The gap map is a decision aid, not a burn-down.**

---

## THE PIVOTS — WHY THIS SHIP MATTERS

**First mid-session Chris pivot to a candidate not on the S2795 open menu.** Signal: menus are priors, not gates.

**First tool-grounded pre-existing-substrate discovery that reshaped ship scope BEFORE code was written.** Rigby's read prevented duplicate work; ship shifted from "build new command" to "extend existing command behind flags". Direct payoff of `feedback_cycle_1a_verify_before_build`.

**First BC-preserving extension of a DOC-AUTOGEN artifact.** `docs/PA_TOOL_AUDIT.md` downstream readers protected; additive columns only under `--include-validation-xref`.

**First rendered "triage slices" section as explicit anti-burn-down device.** F3 mitigation encoded in framing: "NOT a burn-down queue. Chris picks."

**Rigby SIGN response non-truncation sample size 6.** S2790→S2795 all clean. Trend claim strongly holds.

**Zoom-out ask (PLAYBOOK-6.10.7) load-bearing for fifth consecutive session.** All 5 S2795 folds surfaced by the zoom-out ask.

---

## S2796 CANDIDATES (Chris selects at open)

### First — freshness/regression sanity

**Post-cascade freshness check:** wrapper pin retired (S2795 close); freshness should be FRESH · SHA-match at S2795 close SHA `5ec09d625` (or cascade PR merge SHA).
**Ledger baseline:** 64 rows expected (26/22/16). Any drift = investigate.
**Regression 17-suite:** 318 tests OK at S2795 close.
**Gap map:** `docs/audits/PA_TOOLS_GAP_MAP_S2795.md` (first emit; regenerate anytime via `python manage.py build_pa_tool_audit --gap-only --output <path>`).

### Net-new engineering (⭐ recommended per `feedback_engineering_bias_over_audit`)

- **⭐ Pick a triage slice from the S2795 gap map** — the ship deliberately produced 5 slices ranked by handler file. Options ordered by session cost:
  - `td_handlers_ops` (8 untested, ~2 sessions) — cheapest, ops observability tools
  - `td_handlers_gateway` (11 untested, ~3 sessions) — gateway/meta tools
  - `td_handlers_content` (12 untested, ~3 sessions) — content pipeline
  - `td_handlers_core` (22 untested, ~6 sessions) — foundational
  - `td_handlers_agents` (23 untested, ~6 sessions) — agent dispatch
- **Cheap pre-work: add "Covered actions" sections to the 8 existing per-tool validation docs** — this upgrades them from `validated_doc_exists_unknown` to `validated_full` / `validated_partial` in the gap map with ~zero risk. Cheapest gap-map upgrade possible.
- **Cheap pre-work: fix the 23 tools flagged `actions_not_mentioned_in_description`** — edit schema description text to name the action verbs. Zero-code, description-only PR.
- **Open I-0303 (Async Tenant-Boundary Enforcement)** — the ONLY unopened RUR-C1 child arc. RUR-C1 parent closes only when I-0303 lands + all-3 pass umbrella. Multi-session arc.
- **Wire the tenant boundary health umbrella into a Celery beat schedule** — S2794 shipped runner + CLI; only the periodic invocation is missing. Small (~1 PR).
- **Wire the tenant boundary health umbrella into a CI GitHub Action** — same substrate, different trigger.
- **Playbook amendment PR — codify future-trigger-encoded-as-test pattern** (third-instance trigger fired at S2793 F3; still standing).
- **Continue Workspace-tab extension pattern** per `feedback_workspace_over_command_center_for_new_ui`.
- **Next PUBLIC_PATHS prefix ship** (64 remaining across ~13 prefixes per S2789 audit doc).
- **Decorator order codebase migration** — row 45 `same_pr_mitigatable` (S2790).
- **N24 anti-rubber-stamp SIGN codification** — 5 F-BLOCKING-equivalent triggers.
- **AudioAgent completion-flip verification** — awaiting next timeout.
- **Model drift arc** — 38+ auto-migrations queued.
- **Frontend raw-fetch consolidation** — 30 files with fetch(); deferrable.

**Still gated by S2774 ops-surface pause:** N9, N20, Candidate 1 (S2761 smoke), 30+ `core/urls.py` lambda-`__import__` sites.

**Still owed:** P0.5 cost-threshold, P0.75 CI billing, `SESSION_819_SYSTEM_AUDIT_*` cleanup (17 untracked files from webhook cron — grew from 15 during S2795).

### Deferred (waiting on triggers, not calendar)

- **N10** — partial-recycle UI badge (gated on real partial-recycle event)
- **First real N11 PARTIAL_RECYCLE tile fire** (watching)
- **Q3 #5** (health_summary / ops_tool.overview overlap)
- **N22 v3 timestamp-based windows** — trigger: session-int windows prove insufficient
- **Second non-Rigby consumer of `zoom_out_tool`** — still awaited
- **Second consumer of `pa_tools_gap_map` service** — trigger for factor-out abstraction test
- **N17 smart-command-box creep** — row 21 `future_trigger`
- **First autonomous Rigby invocation of `tenant_boundary_health` endpoint** — S2794 dogfood was prompted
- **First autonomous Rigby invocation of `build_pa_tool_audit`** — S2795 dogfood was prompted
- **F4 (telemetry-backed complaints, S2795 row 63) future_trigger** — fires when a `tool_call_error_rate` query surface exists (ToolCallRecord model already exists)
- **First graceful-degradation clause activation on PLAYBOOK-6.10.8** — pending
- **Third served-artifact-freshness trigger** — PLAYBOOK-7.4.4 amendment candidate
- **S2794 Row 57 autonomy creep trigger** — fires if any sibling PR wires status→flag auto-flip on tenant boundary health
- **Third instance of future_trigger-encoded-as-test pattern — still standing** (S2791/S2792/S2793). S2795 F4 was future_trigger but not encoded-as-test (deferred with no locked contract). Playbook amendment candidate.

### Post-S2795 owed

- **I-0303 scoping open** — RUR-C1 parent-close direct blocker
- **Add "Covered actions" sections to 8 existing per-tool validation docs** — cheapest gap-map upgrade
- **Fix 23 tools with actions_not_mentioned_in_description schema lints** — description-only PR
- **Wire tenant boundary health umbrella to Celery beat + CI Action** — S2794 follow-up
- **Playbook amendment PR — future-trigger-encoded-as-test codification** (candidate)
- **64 remaining PUBLIC_PATHS candidates** across ~13 prefixes
- **Decorator order codebase migration** (S2790 row 45)
- **PLAYBOOK-6.10.11+ per-prefix authZ sweep codification** (S2790 row 47)
- **N24 anti-rubber-stamp SIGN codification** — 5 triggers
- **AudioAgent completion-flip verification**
- **Ledger split drift audit** — now 26/22/16
- **`SESSION_819_SYSTEM_AUDIT_*` untracked file cleanup** (17 files)

---

## SESSION PIN — S2795 RETIRED (fresh mint required at S2796 open)

**Pin history (S2795):**

- `pa-dd870b3158784a9d` (label `s2795-pa-tool-gap-map`) minted S2795 T1 open; **retired at S2795 close (`force=true`, twenty-sixth consecutive per S2770+ pattern)**

**Wrapper `tools/pa_local.sh` still points at `pa-dd870b3158784a9d` (retired)** — intended failure mode forces S2796 first-action fresh mint.

**S2796 open sequence:**

```
context-kit orient

# Read this file end-to-end
# Read S2795 handoff §2 (novel-precedent moments) + §3 (T1 SIGN cycle) + §6 (open items)

# Freshness check. Should be FRESH · SHA-match at S2795 close SHA (5ec09d625 or cascade PR SHA) — THIRTY-FIFTH close-cycle after PLAYBOOK-7.4.4.
bash tools/pa_local.sh "S2796 open — freshness check: ops_tool.version verdict + head_commit_sha; ops_tool.recent_recycles limit=5"

# Ledger check: confirm 64-row baseline survived close cascade
DJANGO_LOG_LEVEL=WARNING python manage.py zoom_out_streak_report --as-json 2>/dev/null | python -c "
import json, sys
d = sys.stdin.read()
r = json.loads(d[d.find('{'):])
assert r['total_rows']==64, r
print('OK — 64 rows, counts:', r['counts_by_classification'])
"

# Regression 17-suite (S2794 16-suite + S2795 gap map)
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
  core.tests.test_platform_authz_sweep_2788 \
  core.tests.test_pilot_gates_authz_sweep_2789 \
  core.tests.test_time_travel_authz_sweep_2790 \
  core.tests.test_zoom_out_aggregations_2791 \
  core.tests.test_zoom_out_tool_aggregations_2792 \
  core.tests.test_zoom_out_time_window_2793 \
  core.tests.test_tenant_boundary_health_2794 \
  core.tests.test_pa_tools_gap_map_2795 \
  --noinput

# Optional — regenerate gap map to see fresh counts
DJANGO_LOG_LEVEL=WARNING python manage.py build_pa_tool_audit --gap-only --check 2>/dev/null | head -40

# Mint fresh pin scoped to selected S2796 candidate.
python manage.py session_lifecycle open --label <candidate-scoped-label>
python manage.py session_lifecycle history --limit 5

grep '^python tools/pa_chat.py' tools/pa_local.sh
```

**Anti-rubber-stamp check on S2796 first Rigby SIGN:** verify `tool_runs` non-empty. **PLAYBOOK-6.10.7 + 6.10.8 + 6.10.9 constitutional at v0.8.0** — every joint SIGN routing MUST include ≥1 zoom-out ask; folds MUST be classified + persisted BEFORE D-verdict; folds asserting concrete code-state facts MUST admit stable-state-pointer + file+line evidence + (i)/(ii)/(iii) outcome inline before classify+persist.

---

## Twin-pointer card

📁 **Repo `/` + `/docs/` — S2795 artifacts:**

- **Ship logic:** `core/services/pa_tools_gap_map.py`
- **Ship command:** `python manage.py build_pa_tool_audit --gap-only --output <path>` (or `--include-validation-xref` for extended audit)
- **Ship artifact:** `docs/audits/PA_TOOLS_GAP_MAP_S2795.md`
- **Ship refresh:** `docs/PA_TOOL_AUDIT.md` (fresh at close)
- **Ship tests:** `core/tests/test_pa_tools_gap_map_2795.py`
- **Handoff:** `docs/handoffs/SESSION_2795_PA_TOOLS_GAP_MAP.md`
- **Predecessors:** S2794 (tenant boundary health), S2733 (tool validation campaign retrospective), S2732 (validation campaign close), S2728→S2731 (campaign body)

🖥️ **Workspace UI — `/workspaces` surface:**

- **No Workspace tab this ship** — deliberately CLI + markdown-only
- **Live surfaces at close:**
  - `logs/zoom_out_classifications.jsonl` — **64 rows** (26/22/16)
  - `logs/recycle_events.jsonl` — +1 event (post-#3203, sha=`5ec09d625e85`)
  - `docs/audits/PA_TOOLS_GAP_MAP_S2795.md` — first emit

---

## Current repository state

| Field | Value |
|---|---|
| Branch | `main` |
| HEAD | `5ec09d625` (S2795 ship) — cascade PR advances this at close |
| Playbook version | v0.8.0 (unchanged) |
| Playbook rule count | 205 (unchanged) |
| RUR-C1 state | Substrate: gap-map surface built. RUR-C1 parent-close blocker unchanged (I-0303 not opened). |
| RUR-C1 child arcs | I-0301 CLOSED (S2742) · I-0302 CLOSED (S2751) · **I-0303 NOT YET OPENED** |
| Session pin | `pa-dd870b3158784a9d` (retired at S2795 close, force=true, twenty-sixth consecutive) |
| Wrapper default pin | `tools/pa_local.sh` — `pa-dd870b3158784a9d` (retired; forces fresh mint at S2796 open) |
| Live infra state | S2755→S2794 substrate + S2795 PA tools gap map |
| Postgres :5432 | pg15 (July DB) — brew launchd `started` |
| Postgres pg16 | Parked (April fossil) |
| Freshness log | `logs/session_freshness.jsonl` — grew by 1 at S2795 open |
| Recycle log | `logs/recycle_events.jsonl` — +1 event (post-#3203, sha=`5ec09d625e85`) |
| Zoom-out ledger | `logs/zoom_out_classifications.jsonl` — **64 rows** (26 actionable / 22 mitigatable / 16 future_trigger) |
| PA tool audit | `docs/PA_TOOL_AUDIT.md` — regenerated at close (158/114/157/113) |
| PA tools gap map | `docs/audits/PA_TOOLS_GAP_MAP_S2795.md` — first emit (105 untested / 8 doc_exists_unknown / 44 agents / 1 meta) |
| Next move | Chris selects at S2796 open |

---

## Recommended session-open protocol (S2796)

1. `context-kit orient`
2. Read this file end-to-end
3. Read S2795 handoff §2 (novel-precedent moments) + §3 (T1 SIGN cycle) + §6 (open items)
4. **Freshness + regression 17-suite + ledger verify** — see S2796 open sequence above
5. **Watch for** ledger 64-row baseline surviving cascade merge; freshness FRESH · SHA-match
6. If `staleness_verdict != FRESH` → escalate
7. **Check `brew services list | grep postgres` FIRST** if freshness fails oddly
8. Verify runtime state: `git log --oneline -5`; confirm wrapper at retired pin
9. Present candidate menu — engineering leans first per `feedback_engineering_bias_over_audit`; Workspace-tab leans preferred per `feedback_workspace_over_command_center_for_new_ui`
10. **Anti-rubber-stamp check on first SIGN** — verify `tool_runs` non-empty
11. Chris directs S2796 P0 selection (candidate menu is a prior, not a gate — Chris may pivot to something new)
12. Mint fresh pin with candidate-scoped label
13. Route work through Rigby joint agreement before coding
14. **PLAYBOOK-6.10.9 constitutional at v0.8.0:** any zoom-out fold asserting concrete code-state facts MUST admit stable-state-pointer + file+line evidence + (i)/(ii)/(iii) outcome inline before classify+persist

---

## Reference documents

Ordered by frequency of use at S2796:

1. [`CLAUDE.md`](CLAUDE.md) — repo bootstrap + Rigby collaboration protocol (anchor at v0.8.0)
2. [`docs/ENGINEERING_PLAYBOOK.md`](docs/ENGINEERING_PLAYBOOK.md) — v0.8.0 (205 rules)
3. [`docs/handoffs/SESSION_2795_PA_TOOLS_GAP_MAP.md`](docs/handoffs/SESSION_2795_PA_TOOLS_GAP_MAP.md) — **S2795 handoff (current)**
4. [`docs/audits/PA_TOOLS_GAP_MAP_S2795.md`](docs/audits/PA_TOOLS_GAP_MAP_S2795.md) — **S2795 gap map artifact (headline + triage slices + per-tool coverage table)**
5. [`docs/PA_TOOL_AUDIT.md`](docs/PA_TOOL_AUDIT.md) — fresh runtime-derived PA tool audit (regen at S2795 close)
6. [`docs/handoffs/SESSION_2794_TENANT_BOUNDARY_HEALTH.md`](docs/handoffs/SESSION_2794_TENANT_BOUNDARY_HEALTH.md) — S2794 predecessor
7. [`docs/handoffs/SESSION_2733_CAMPAIGN_RETROSPECTIVE.md`](docs/handoffs/SESSION_2733_CAMPAIGN_RETROSPECTIVE.md) — S2728→S2732 validation campaign retrospective (methodology reference for triage slice execution)
8. [`docs/research/tools/validation/`](docs/research/tools/validation/) — 18 existing validation docs (10 substrate + 8 per-tool without Covered actions checklist)
9. [`logs/zoom_out_classifications.jsonl`](logs/zoom_out_classifications.jsonl) — 64 rows at S2795 close (rows 60/61/62/63/64 are S2795 F1-F5 folds)
