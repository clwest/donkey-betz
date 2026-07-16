# Next Session — Start Here

---

## READ THIS FIRST — SESSION 2799 CLOSED — 14 Rigby tool signposts shipped (Option C done; Option B next per Chris sequencing)

**Refreshed 2026-07-16 (SESSION 2799 CLOSED — third same-day engineering session after S2798 close. Chris re-scoped "market-shipping priority" mid-day from marketing polish to platform capability audit; three parallel Explore agents produced a Platform Capability Snapshot (agents work / Rigby's tools / non-betting use cases); Chris picked sequencing **C → B → BettingPage**. C shipped this session: 14 WHEN→CALL signposts in Rigby's system prompt, gated on smoke-before-signpost mgmt command. All 14 non-blocked tools passed smoke — 0 SMOKE_FAIL — proving the gap was 100% routing-debt, not reliability-debt. Live post-recycle Rigby test: "what's on the zoom-out ledger?" → routed to `zoom_out_tool.list` (signpost 3) instead of `intelligence_tool` catch-all. **S2798 discipline correction landed**: 7 folds classified + persisted to ledger (77 → 84) BEFORE Chris D-verdict per PLAYBOOK-6.10.8. Novel: first deployment of parallel-Explore-agent Platform Capability Snapshot pattern; first mgmt-command-as-signpost-gate artifact reusable for Option B's broken-agent triage; first captured intentional Chris reframe on "user-ready" definition (saved as `feedback_user_ready_means_capability_not_polish`). Rigby T1 SIGN 15 tool_runs; T2 SIGN 14 tool_runs. THIRTY-NINTH close-cycle post-PLAYBOOK-7.4.4.)**

**S2799 ship:**

**PR #3211 · `a73967b4cc09`** — 3 files, +197 / -1. TOOL SIGNPOSTS section at `unified_pa_entrypoint.py:2799` (14 WHEN→CALL routing hints) + new `smoke_pa_tools_for_signpost` mgmt command (174 lines) + fresh session pin. Rigby's zero-fire specialty tools (rigby_shift_brief_tool, employee_tool, zoom_out_tool, learning_tool, learning_patterns_tool, workflow_run_tool, gates_tool, pilots_tool, revenue_tracker_tool, self_awareness_tool, brainstorm_tool, ops_digest_tool, heartbeat_history_tool, surgical_moves_status_tool) now have routing signals.

**Handoff:** `docs/handoffs/SESSION_2799_RIGBY_TOOL_SIGNPOSTS.md`
**Post-merge:** `make recycle-all` per PLAYBOOK-7.4.4 completed (thirty-ninth cycle).
**Ledger state at close:** `logs/zoom_out_classifications.jsonl` — **84 rows** (35 `same_pr_actionable` / 27 `same_pr_mitigatable` / 22 `future_trigger`); rows 78-84 are S2799 T1/T2 folds.

**Live URL:** `http://localhost:8000/*` — every Rigby chat is the ship surface. Signpost hits visible as `[OK] <tool_name>` in tool_runs; measure adoption via `ToolCallRecord` rows on any of the 14 signposted names post-ship.

---

## SESSION-OPEN INFRA STORY (S2799)

**Third same-day session after S2798.** Chris re-scoped mid-day: `"I meant that I wanted to do things like make sure the Agents are working, Rigby has access to all of the tools, that there's a real world use case for the platform other than just betting."` My S2797→S2798 arc narrowed onto marketing/UI polish; Chris's real bar is platform capability being real. Reframe saved as `feedback_user_ready_means_capability_not_polish.md`.

**Three parallel Explore agents produced a Platform Capability Snapshot.** Answered three questions in one round-trip:
- **Agents:** 88/83 active last-30d (97% adoption); 1,803 lifetime executions; 5 broken agents identified (CodeReviewAgent 76% fail, WorkflowAgent 69%, AudioAgent 53%, WorkflowOrchestrationAgent 46%, CTOAgent 46%)
- **Rigby's tools:** 157 handlers, 114 schemas, **60 zero-fire schemas** (66% of surface). Top-called are untested (intelligence_tool 1,442, web_search 1,021); only ops_tool is both heavily-used AND validated_full
- **Non-betting use cases:** 4 candidates ranked by readiness — Stock Intelligence (TIER 1, ~1-2 weeks to first revenue), Content Publishing (TIER 2), Legal Doc Drafter (TIER 3), Government Monitoring (TIER 4)

**Chris picked sequencing C → B → BettingPage.** C = signpost Rigby's zero-fire tools (widest capability payoff, smallest lift). B = fix the 5 broken agents (reliability floor). BettingPage explicitly deferred.

**Shape B pivoted at T2:** Chris added smoke-before-signpost gate after seeing S2795/S2796 validation gap (only 4 of ~100 tools `validated_full`). New `smoke_pa_tools_for_signpost` mgmt command dispatches each candidate with a safe read-only action, tags OK / SMOKE_EMPTY / SMOKE_FAIL / SMOKE_BLOCKED. Only OK + SMOKE_EMPTY earn signposts.

**All 14 non-blocked tools passed smoke.** Zero SMOKE_FAIL. Inverted the framing — this ship revealed that the routing-vs-reliability gap is 100% routing at the schema-exposed slice. Real reliability failures live at the AGENT layer (Thread 1's 5 broken agents), not the tool layer.

**PLAYBOOK-6.10.8 discipline correction landed.** S2798 persisted folds after D-verdict; S2799 persisted 7 folds (ledger 77 → 84) BEFORE Chris said "ship it." Corrects the carry-forward.

---

## S2800 CANDIDATES — OPTION B IS THE DEFAULT (Chris sequenced)

### First — freshness/regression sanity

**Post-cascade freshness check:** wrapper pin retired (S2799 close); freshness should be FRESH · SHA-match at S2799 close SHA (`a73967b4cc09` or cascade PR SHA).
**Ledger baseline:** 84 rows expected (35/27/22). Any drift = investigate.
**Regression 17-suite:** 318 tests OK at S2798 open; unchanged by S2799 (system prompt edit + mgmt command; no test-covered surface).

### ⭐ OPTION B (default per Chris sequencing) — Fix the 5 broken agents

Per Thread 1 audit + Chris directive:

- **CodeReviewAgent** (76% fail rate; 19/25 recent) — tool chaining broken; `read_file` output doesn't flow to review loop. File: `core/agents/code_review_agent.py:345+`. Fix: add explicit tool-return validation in agent execute loop.
- **WorkflowAgent + WorkflowOrchestrationAgent + CTOAgent** (~46-69% fail — heartbeat timeout cluster). Root cause: 60-min heartbeat watchdog on `AgentExecution.last_heartbeat_at` (`core/models_unified_system.py:961`). Fix: emit heartbeats every 5-10 min during sub-task loops; raise timeout to 6h for orchestration tier.
- **AudioAgent** (52.9% fail) — TTS API payment wall + timeout. Fix: fallback to offline TTS or mock; raise premium API key requirement to config.

**Ship shape suggestion:** reuse the S2799 smoke-gate pattern. New mgmt command `smoke_broken_agents_for_repair` iterates the 5 with a minimal harness dispatch, records structured pass/fail with error signatures. Pick top-2 fixes; ship both in one PR; validate via smoke re-run.

**Also relevant:** SMOKE_FAIL cluster future_trigger fold row 80 IS this arc's justification.

### Option C follow-ups (from S2799)

- **`ops_digest_tool` handler FieldError** — `Cannot resolve keyword 'pattern_hash' into field. Choices are: category, description, ..., signature_hash`. Handler falls back to null path; 5-line fix at ORM query site in `core/services/td_handlers_ops.py`.
- **`calendar_tool` rename/kill** — dead per Thread 2 (actually studio episodes). Own follow-up PR.
- **`mission_verdict` read-only variant** — add `list_recent` or `describe` action so it can earn a signpost.
- **Per-signpost adoption telemetry** — future_trigger fold row 84; fires 7 days post-ship if any signposted tool has zero invocations. Watch: measure lift via ToolCallRecord counts on the 14 signposted names.

### ⭐ Stock Intelligence — first non-betting revenue play (from Thread 3)

Deferred per Chris sequencing (B first), but the strategic candidate. When B is done and if not immediately BettingPage:

- Add newsletter scheduler (send daily brief to Pro subscribers — 3 days work)
- Add Stripe subscription gate on premium briefs / SEC depth (2 days)
- Total: ~1-2 weeks to first non-betting revenue
- Genuinely differentiated vs ChatGPT (citation provenance + multi-agent debate)

### Standing owed (S2797/S2798)

- Onboarding banner in shared authed Layout (S2798 F3 future_trigger)
- Throttle on `POST /api/onboarding/complete/` (S2798 F4 future_trigger)
- Regression test for `complete_onboarding_view`
- Public deployment of LandingPage (hosting + DNS)
- Waitlist DB capture (Shape B)
- I-0303 scoping (RUR-C1 parent-close blocker)
- Regression tests for 4 S2796 tools
- 8 remaining per-tool docs need "Covered actions"
- 23 tools schema-lint fix
- Wire tenant boundary health → Celery beat
- `SESSION_819_SYSTEM_AUDIT_*` cleanup (19+ files)
- Doc-note gap-map classifier h3-truncation bug in S2795 F2 template spec

### Deferred (waiting on triggers)

- **NEW: S2799 F80** — SMOKE_FAIL cluster ≥4/14 = Option-B trigger (already fires at Option B open naturally)
- **NEW: S2799 F83** — Dynamic signposts via PAToolLearningEnricher (v2). Fires when Chris wants to iterate signposts without a PR
- **NEW: S2799 F84** — Per-signpost adoption telemetry. Fires 7d post-S2799 ship if any of the 14 signposted tools has zero invocations
- All S2797/S2798 triggers unchanged
- **N10** — partial-recycle UI badge (real partial-recycle event)
- **N22 v3 timestamp-based windows** — trigger: session-int windows prove insufficient
- **Second non-Rigby consumer of `zoom_out_tool`** — still awaited
- **Second consumer of `pa_tools_gap_map` service**
- **First autonomous Rigby invocation** of tenant_boundary_health / build_pa_tool_audit
- **F4 (telemetry-backed complaints) future_trigger** — fires when `tool_call_error_rate` query surface exists
- **First graceful-degradation clause activation on PLAYBOOK-6.10.8** — pending
- **Third served-artifact-freshness trigger** — PLAYBOOK-7.4.4 amendment candidate
- **Third instance of future_trigger-encoded-as-test pattern** — still standing
- **`status_snapshot_tool` version-source parity trigger**
- **First real prospect email via S2797 mailto CTAs** — first data point on funnel quality

---

## SESSION PIN — S2799 RETIRED (fresh mint required at S2800 open)

**Pin history (S2799):**

- `pa-f0bb34abfc3c4b25` (label `s2799-rigby-tool-signposts`) minted S2799 open; **retired at S2799 close (`force=true`, thirtieth consecutive per S2770+ pattern)**

**Wrapper `tools/pa_local.sh` still points at `pa-f0bb34abfc3c4b25` (retired)** — intended failure mode forces S2800 first-action fresh mint.

**S2800 open sequence:**

```
context-kit orient

# Read this file end-to-end
# Read S2799 handoff §2 (novel-precedent moments) + §3 (Platform Snapshot + T1/T2 SIGN) + §6 (open items) + §7 (Chris directive queue)

# Freshness check. Should be FRESH · SHA-match at S2799 close SHA (or cascade PR SHA).
bash tools/pa_local.sh "S2800 open — freshness check: ops_tool.version verdict + head_commit_sha; ops_tool.recent_recycles limit=5"

# Ledger check: confirm 84-row baseline survived close cascade
DJANGO_LOG_LEVEL=WARNING python manage.py zoom_out_streak_report --as-json 2>/dev/null | python -c "
import json, sys
d = sys.stdin.read()
r = json.loads(d[d.find('{'):])
assert r['total_rows']==84, r
print('OK — 84 rows, counts:', r['counts_by_classification'])
"

# Regression 17-suite (unchanged; S2799 was prompt edit + mgmt command)
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

# Optional: measure S2799 signpost lift — count last-day-invocations on the 14 signposted tools
python manage.py shell <<'PY'
from datetime import timedelta
from django.utils import timezone
from core.models_tool_calls import ToolCallRecord
from django.db.models import Count
SIGNPOSTED = [
    'rigby_shift_brief_tool', 'employee_tool', 'zoom_out_tool', 'learning_tool',
    'learning_patterns_tool', 'workflow_run_tool', 'gates_tool', 'pilots_tool',
    'revenue_tracker_tool', 'self_awareness_tool', 'brainstorm_tool',
    'ops_digest_tool', 'heartbeat_history_tool', 'surgical_moves_status_tool',
]
since = timezone.now() - timedelta(days=1)
counts = dict(ToolCallRecord.objects.filter(
    tool_name__in=SIGNPOSTED, created_at__gte=since
).values_list('tool_name').annotate(c=Count('id')).values_list('tool_name', 'c'))
for t in SIGNPOSTED:
    print(f'  {t}: {counts.get(t, 0)}')
print(f'Total signposted invocations in last 24h: {sum(counts.values())}')
PY

# Mint fresh pin scoped to Option B (or whichever candidate Chris picks).
python manage.py session_lifecycle open --label <candidate-scoped-label>
python manage.py session_lifecycle history --limit 5

grep '^python tools/pa_chat.py' tools/pa_local.sh
```

**Anti-rubber-stamp check on S2800 first Rigby SIGN:** verify `tool_runs` non-empty. **PLAYBOOK-6.10.7 + 6.10.8 + 6.10.9 constitutional at v0.8.0** — zoom-out ask required; folds classify+persist BEFORE D-verdict; concrete code-state claims MUST admit stable-state-pointer + file+line evidence + (i)/(ii)/(iii) outcome inline.

**S2799 lesson to carry:**

1. **Reuse smoke-gate pattern for Option B.** New mgmt command `smoke_broken_agents_for_repair` iterates the 5 broken agents (CodeReviewAgent + heartbeat cluster + AudioAgent) with a minimal harness dispatch, records structured pass/fail with error signatures. Pick top-2 fixes; ship both in one PR; validate via smoke re-run.
2. **Chris sequencing is Option B, then BettingPage, then Stock Intelligence** — don't propose alternative sequences at S2800 open unless Chris signals otherwise.
3. **PLAYBOOK-6.10.8 discipline holds** — persist folds BEFORE first D-verdict. S2799 did it right; carry the pattern.

---

## Twin-pointer card

📁 **Repo `/` + `/docs/` — S2799 artifacts:**

- **System prompt:** `core/services/unified_pa_entrypoint.py:2799` (TOOL SIGNPOSTS section, 22 lines, WHEN→CALL format)
- **Smoke gate:** `core/management/commands/smoke_pa_tools_for_signpost.py` (reusable — Option B should extend this)
- **Handoff:** `docs/handoffs/SESSION_2799_RIGBY_TOOL_SIGNPOSTS.md`
- **Live test:** `python manage.py smoke_pa_tools_for_signpost` (or `--as-json`)
- **Predecessors:** S2798 (onboarding banner), S2797 (public LandingPage), S2796 (market-shipping directive)

🖥️ **Workspace UI — `/workspaces` surface:**

- **No new Workspace tab** — every Rigby chat is now the ship surface
- **Live surfaces at close:**
  - `logs/zoom_out_classifications.jsonl` — **84 rows** (35/27/22); rows 78-84 are S2799
  - `logs/recycle_events.jsonl` — +2 events during S2799 close
  - `http://localhost:8000/welcome` — public LandingPage (unchanged since S2797)
  - `http://localhost:8000/workspace` — first-run banner (unchanged since S2798)
  - Every Rigby dispatch — signpost hits visible as tool_runs

---

## Current repository state

| Field | Value |
|---|---|
| Branch | `main` |
| HEAD | S2799 close cascade — advances at cascade PR merge |
| Playbook version | v0.8.0 (unchanged) |
| Playbook rule count | 205 (unchanged) |
| RUR-C1 state | Unchanged; I-0303 still not opened |
| Session pin | `pa-f0bb34abfc3c4b25` (retired at S2799 close, force=true, thirtieth consecutive) |
| Wrapper default pin | `tools/pa_local.sh` — `pa-f0bb34abfc3c4b25` (retired; forces fresh mint at S2800 open) |
| Postgres :5432 | pg15 (July DB) — brew launchd `started` |
| Freshness log | `logs/session_freshness.jsonl` — grew by 1 at S2799 open |
| Recycle log | `logs/recycle_events.jsonl` — +2 events during S2799 close |
| Zoom-out ledger | `logs/zoom_out_classifications.jsonl` — **84 rows** (35 actionable / 27 mitigatable / 22 future_trigger) |
| PA tool audit | `docs/PA_TOOL_AUDIT.md` — unchanged (S2799 was routing, not schema/handler changes) |
| PA tools gap map | `docs/audits/PA_TOOLS_GAP_MAP_S2796.md` — unchanged; overlay with usage data is a future_trigger fold (row 80) |
| Rigby signposts | 14 tools now routed via `unified_pa_entrypoint.py:2799` TOOL SIGNPOSTS section (WHEN→CALL) |
| Broken agents queue | 5 identified: CodeReviewAgent (76% fail), WorkflowAgent/WorkflowOrchestrationAgent/CTOAgent (heartbeat), AudioAgent (TTS wall) — S2800 Option B default |
| Non-betting revenue play | Stock Intelligence identified as TIER 1 candidate (1-2 weeks to first revenue); deferred behind Option B per Chris sequencing |
| Test user for onboarding demo | `s2798_onboarding_test` / `test-onboard-s2798!` — state re-armed at S2798 close |
| Next move | Chris selects at S2800 open (Option B default) |

---

## Recommended session-open protocol (S2800)

1. `context-kit orient`
2. Read this file end-to-end
3. Read S2799 handoff §2 (novel-precedent moments) + §3 (Platform Snapshot + T1/T2 SIGN cycles) + §7 (Chris directive queue)
4. **Freshness + regression 17-suite + ledger 84 verify** — see S2800 open sequence above
5. **Signpost lift check** — count last-24h invocations on the 14 signposted tools (measurable evidence for future_trigger fold row 84)
6. **Watch for** ledger 84-row baseline surviving cascade merge; freshness FRESH · SHA-match
7. If `staleness_verdict != FRESH` → escalate
8. **Check `brew services list | grep postgres` FIRST** if freshness fails oddly
9. Verify runtime state: `git log --oneline -5`; confirm wrapper at retired pin
10. **Default candidate: Option B** — fix the 5 broken agents. Reuse S2799 smoke-gate pattern. Present the top-2 pick (by failure rate + fix effort) as the recommendation
11. **Anti-rubber-stamp check on first SIGN** — verify `tool_runs` non-empty
12. Chris directs S2800 P0 selection (Option B unless override)
13. Mint fresh pin with candidate-scoped label
14. Route work through Rigby joint agreement before coding
15. **PLAYBOOK-6.10.8 constitutional at v0.8.0 (S2799 discipline held):** fold persistence is the FINAL step of joint SIGN, BEFORE writing the Chris-facing recommendation
16. **PLAYBOOK-6.10.9 constitutional at v0.8.0:** any zoom-out fold asserting concrete code-state facts MUST admit stable-state-pointer + file+line evidence + (i)/(ii)/(iii) outcome inline before classify+persist
17. **BEFORE any user-facing content:** read `docs/PLATFORM_WHAT_IT_IS.md`

---

## Reference documents

Ordered by frequency of use at S2800:

1. [`CLAUDE.md`](CLAUDE.md) — repo bootstrap + Rigby collaboration protocol (anchor at v0.8.0)
2. [`docs/PLATFORM_WHAT_IT_IS.md`](docs/PLATFORM_WHAT_IT_IS.md) — **anchor for user-ready reasoning** (S2799 lesson)
3. [`docs/ENGINEERING_PLAYBOOK.md`](docs/ENGINEERING_PLAYBOOK.md) — v0.8.0 (205 rules)
4. [`docs/handoffs/SESSION_2799_RIGBY_TOOL_SIGNPOSTS.md`](docs/handoffs/SESSION_2799_RIGBY_TOOL_SIGNPOSTS.md) — **S2799 handoff (current)**
5. [`core/services/unified_pa_entrypoint.py`](core/services/unified_pa_entrypoint.py) — TOOL SIGNPOSTS at line 2799
6. [`core/management/commands/smoke_pa_tools_for_signpost.py`](core/management/commands/smoke_pa_tools_for_signpost.py) — smoke gate pattern (reusable)
7. [`docs/handoffs/SESSION_2798_ONBOARDING_ROUTING.md`](docs/handoffs/SESSION_2798_ONBOARDING_ROUTING.md) — S2798 predecessor
8. [`docs/audits/PA_TOOLS_GAP_MAP_S2796.md`](docs/audits/PA_TOOLS_GAP_MAP_S2796.md) — PA tools gap map (usage overlay = future_trigger)
9. [`docs/PA_TOOL_AUDIT.md`](docs/PA_TOOL_AUDIT.md) — runtime PA tool audit
10. [`logs/zoom_out_classifications.jsonl`](logs/zoom_out_classifications.jsonl) — 84 rows at S2799 close (rows 78-84 are S2799)
