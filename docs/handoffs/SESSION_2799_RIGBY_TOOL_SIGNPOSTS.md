# Session 2799 — Rigby tool signposts (14 zero-fire tools routed via WHEN→CALL prompt)

**Date:** 2026-07-16
**Session:** S2799
**Branch/PR:** `s2799-rigby-tool-signposts` → **PR #3211** (merged as `a73967b4cc09`)
**Predecessor:** [SESSION_2798_ONBOARDING_ROUTING.md](SESSION_2798_ONBOARDING_ROUTING.md)
**Playbook:** v0.8.0 (205 rules) — unchanged
**Recycle cycle:** thirty-ninth post-PLAYBOOK-7.4.4

---

## §1 — Ship summary

Third consecutive engineering session in a same-day multi-session arc — S2798 closed at ~7:15 AM, then Chris re-scoped "market-shipping priority" from marketing polish to **platform capability audit**. Three parallel Explore agents produced a Platform Capability Snapshot (Thread 1: agents work; Thread 2: Rigby's tools; Thread 3: non-betting use cases). Chris picked sequencing C→B: signpost Rigby's zero-fire tools first, then fix broken agents.

**Ship shape B (joint SIGN, 7 folds persisted BEFORE Chris D-verdict per PLAYBOOK-6.10.8 — S2798 discipline carry-forward correction):**

Adds a **TOOL SIGNPOSTS** section to `_build_function_calling_system_prompt` at `unified_pa_entrypoint.py:2799` with 14 `WHEN → CALL` routing hints. Rigby was defaulting to catch-alls (`intelligence_tool` 1,442 lifetime calls; `web_search` 1,021 calls) because the LLM had no signal telling it when to reach for specific tools.

Ships with a **smoke gate** — new `smoke_pa_tools_for_signpost` mgmt command dispatches each candidate tool with a safe read-only action and verifies coherent response before it earns a signpost. **All 14 non-blocked tools passed** — zero SMOKE_FAIL. Proves the gap was 100% routing-debt, not reliability-debt.

**Signposted tools (Rigby T1 ranking):**

1. `rigby_shift_brief_tool.generate` — "catch me up" / shift summary
2. `employee_tool.status` — AI Employee status / job contract / mission run
3. `zoom_out_tool.list` — zoom-out fold ledger / concern classifications
4. `learning_tool.stats` — "what has the platform learned" / learning stats
5. `learning_patterns_tool.stats` — recurring patterns / aggregates
6. `workflow_run_tool.list` — workflow run status
7. `gates_tool.stats` — feature gates
8. `pilots_tool.stats` — pilot programs / outcomes
9. `revenue_tracker_tool.stats` — earnings / revenue / spend
10. `self_awareness_tool.metrics` — meta capabilities / platform introspection
11. `brainstorm_tool.stats` — past brainstorms
12. `ops_digest_tool.generate` — ops digest / operations rollup
13. `heartbeat_history_tool.recent` — heartbeat history
14. `surgical_moves_status_tool.status` — surgical moves / session status

**Excluded from ship:**
- `mission_verdict` — SMOKE_BLOCKED (all actions write-only; no read variant). Filed as `same_pr_mitigatable` fold; unlocks when a read-only variant is added.
- `calendar_tool` — dead/misnamed (actually manages studio episodes per Thread 2 finding). Rename/kill deferred to its own PR.

**Files changed (3):**

| File | Change | Purpose |
|------|--------|---------|
| `core/services/unified_pa_entrypoint.py` | +22 lines | TOOL SIGNPOSTS section after existing TOOL USAGE block |
| `core/management/commands/smoke_pa_tools_for_signpost.py` | +174 lines (new) | Smoke gate: dispatches each candidate with safe read-only action, tags OK / SMOKE_EMPTY / SMOKE_FAIL / SMOKE_BLOCKED |
| `tools/pa_local.sh` | +1 / -1 | Fresh S2799 pin `pa-f0bb34abfc3c4b25` |

**Verification:**

Smoke command (`python manage.py smoke_pa_tools_for_signpost`): **14 PASS / 0 EMPTY / 0 FAIL / 1 BLOCK**.

Live post-recycle Rigby test: sent `"what's on the zoom-out ledger recently?"` → Rigby fired `zoom_out_tool.list` (per signpost 3). Pre-S2799 she would have defaulted to `intelligence_tool` catch-all. Signpost lift confirmed in a single dispatch.

Regression 17-suite: 318 tests OK at session-start.

---

## §2 — Novel-precedent moments

**First session with intentional context reframe.** Chris explicitly re-scoped "market-shipping priority" mid-session after S2798 close: `"I meant that I wanted to do things like make sure the Agents are working, Rigby has access to all of the tools, that there's a real world use case for the platform other than just betting."` Direct correction to my narrower marketing-polish interpretation of the S2796-persisted signal. Saved as `feedback_user_ready_means_capability_not_polish.md` for future sessions.

**First deployment of the Explore-agent parallel-research pattern for platform audit.** Three parallel Explore agents produced a Platform Capability Snapshot answering three concrete sub-questions (agents work / tools reachable / non-betting use cases) in a single round-trip. Total output ~1500 words per thread; synthesis surfaced the strategic answer (Stock Intelligence as first non-betting revenue play; Rigby routing debt as the tightest capability gap).

**S2798 discipline carry-forward corrected.** PLAYBOOK-6.10.8 requires folds classify+persist BEFORE first D-verdict. S2798 missed this (persisted during close cascade after "ship it"). S2799 corrected: 7 folds written to `logs/zoom_out_classifications.jsonl` (rows 78-84) between T2 SIGN and Chris "ship it." Ledger jumped 77 → 84 pre-D-verdict rather than post. Made the correction explicit in-line.

**Novel — Rigby T1 SIGN caught what Claude missed AND Chris caught what I under-scoped in the same conversation.** Rigby's Thread-2-audit reply flagged `register_view` I'd missed (via head-limit on grep). Chris's mid-session pivot from Shape A to Shape B added the smoke-before-signpost gate. Both interventions upstream of implementation. The joint-SIGN pattern is working as designed — architectural corrections land in the ship shape, not in re-work.

**Smoke gate result surfaced a stronger claim than expected.** Shape B was framed as risk mitigation ("prevent amplifying broken tools"). But when 14/14 passed with zero SMOKE_FAIL, the framing inverted: **the gap between "tools that exist" and "tools that get called" is 100% routing-debt** at the schema-exposed slice. This changes the calibration for Option-B (fix broken agents next session) — the smoke pattern should be reused for the 5 flagged broken agents (CodeReviewAgent 76% fail, WorkflowAgent 69%, AudioAgent 53%, WorkflowOrchestrationAgent 46%, CTOAgent 46%) but they're a DIFFERENT gap (real reliability failures, not routing gaps).

**Bug found via smoke.** `ops_digest_tool` handler logged `FieldError: Cannot resolve keyword 'pattern_hash' into field.` during smoke — the tool still returned ok=True with data (fallback path), but there's a real query bug in `td_handlers_ops.py`. Signposted anyway (returns coherent data); logged as a follow-up.

**First mgmt-command-as-signpost-gate pattern.** `smoke_pa_tools_for_signpost` is a lasting artifact — reusable at any future signpost-expansion pass to re-validate the coverage. Same pattern applies naturally to Option B for broken-agent triage.

---

## §3 — SIGN cycles

### Platform Capability Snapshot (parallel Explore agents)

**Thread 1 (Agents):** 88/83 AGENT_MAP agents active last-30d (97% adoption); 1,803 lifetime executions, 1,722 in 30d; 86.6% completion, 13.4% failure. 5 broken agents identified: CodeReviewAgent (76% fail, tool chaining broken), WorkflowAgent/AudioAgent/WorkflowOrchestrationAgent/CTOAgent (heartbeat/API-wall failures). **Non-betting agent activity is real** — Rigby (163), ResearchAgent (144), ContentWriterAgent (28) are active.

**Thread 2 (Rigby tools):** 157 handlers registered, 114 schemas exposed, **60 zero-fire schemas** (66% of exposed surface). Top-called are untested: `intelligence_tool` (1,442, untested), `web_search` (1,021, untested), `spider_query` (926, untested). Only `ops_tool` (79 calls) is both heavily-used AND `validated_full`. **This is the largest capability gap on the platform.**

**Thread 3 (Non-betting use cases):** 4 candidates ranked by readiness — Stock Intelligence (TIER 1, ~1-2 weeks to first revenue: newsletter + Stripe gate), Content Publishing (TIER 2), Legal Doc Drafter Colorado (TIER 3), Government Monitoring (TIER 4). Stock Intelligence has full citation provenance (defensible vs ChatGPT).

### T1 Rigby SIGN — SIGN-WITH-EDITS (tool_grounded, ~15 tool_runs)

- **Ask 1 (top-15 picks):** Rigby's ranked list of 15 zero-fire tools by expected routing lift. Adopted verbatim.
- **Ask 2 (format):** WHEN → CALL over "X: user asks Y" or example-based. Adopted.
- **Ask 3 (seam):** Hardcoded `prompt_parts` for v1. Dynamic via PAToolLearningEnricher as v2 evolution. Adopted; v2 filed as future_trigger.
- **Ask 4 (calendar_tool rename):** No inline rename. Own PR. Adopted.
- **Ask 5 (zoom-out):** Signpost 12-15 OK if under ~25 lines. Monitoring gap flagged (no per-signpost adoption telemetry). Both concerns adopted.

### T2 Rigby SIGN — AGREE with EDITS (14 tool_runs)

**Chris pivot at T2:** Shape B (smoke-before-signpost) after seeing S2795/S2796 validation gap. Only 4 of ~100 tools `validated_full`; signposting to un-tested tools risks amplifying broken ones.

- **Ask 1 (safe smoke actions):** Rigby named safe read-only action per tool. 14/15 covered. `mission_verdict` flagged SMOKE_BLOCKED (write-only, no read variant).
- **Ask 2 (smoke mechanism):** Mgmt command (option a) — repeatable, artifact-producing. Adopted.
- **Ask 3 (threshold):** (i) no exception + (ii) coherent JSON shape required; (iii) meaningful content optional. Adopted.
- **Ask 4 (SMOKE_FAIL vs SMOKE_EMPTY):** Distinguish these — reliability signal vs data-population signal. Adopted; both eligible for signposts because Rigby will honestly report emptiness.
- **Ask 5 (zoom-out):** 3 folds — smoke-worth-cost (same_pr_actionable), empty-vs-fail distinction (same_pr_mitigatable), SMOKE_FAIL cluster = Option-B trigger (future_trigger).

### Fold ledger — 7 new rows (77 → 84)

| Row | Arc | Classification | Origin |
|-----|-----|----------------|--------|
| 78 | smoke_before_signpost_worth_it | same_pr_actionable | T2 Ask 5 fold 1 |
| 79 | smoke_fail_vs_empty | same_pr_mitigatable | T2 Ask 4 + Ask 5 fold 2 |
| 80 | smoke_fail_cluster_option_b_trigger | future_trigger | T2 Ask 5 fold 3 |
| 81 | mission_verdict_smoke_blocked | same_pr_mitigatable | T2 Ask 1 mission_verdict |
| 82 | no_calendar_rename_this_ship | same_pr_mitigatable | T1 Ask 4 |
| 83 | dynamic_signposts_via_enricher_v2 | future_trigger | T1 Ask 3 |
| 84 | per_signpost_adoption_telemetry | future_trigger | T1 Ask 5 monitoring gap |

**All 7 folds persisted BEFORE Chris D-verdict** (S2798 discipline correction).

---

## §4 — Verification transcript

```bash
# Smoke command (post-classifier-fix)
$ python manage.py smoke_pa_tools_for_signpost
[PASS ] rigby_shift_brief_tool      action=generate  — dict with 7 keys: [ok, summary_text, traffic_light, sections, ...]
[PASS ] employee_tool               action=status    — dict with 15 keys
[PASS ] zoom_out_tool               action=list      — dict with 12 keys: [action, log_exists, log_path, ...]
[PASS ] learning_tool               action=stats     — dict with 2 keys: [stats, totals]
[PASS ] learning_patterns_tool      action=stats     — dict with 4 keys
[PASS ] workflow_run_tool           action=list      — dict with 3 keys: [action, count, runs]
[PASS ] gates_tool                  action=stats     — dict with 4 keys
[PASS ] pilots_tool                 action=stats     — dict with 4 keys
[PASS ] revenue_tracker_tool        action=stats     — dict with 6 keys: [total_revenue, revenue_last_30_days, ...]
[PASS ] self_awareness_tool         action=metrics   — dict with 3 keys
[PASS ] brainstorm_tool             action=stats     — dict with 7 keys
[PASS ] ops_digest_tool             action=generate  — dict with 2 keys (FieldError warning in handler log — investigate)
[PASS ] heartbeat_history_tool      action=recent    — dict with 3 keys
[PASS ] surgical_moves_status_tool  action=status    — dict with 4 keys
[BLOCK] mission_verdict             — write-only; no read variant
PASS=14  EMPTY=0  FAIL=0  BLOCK=1

# Live Rigby test post-recycle
$ bash tools/pa_local.sh "what's on the zoom-out ledger recently?"
[OK] zoom_out_tool (4ms)  → action=list, total_rows=84 ...
```

Signpost routing lift confirmed in a single dispatch.

---

## §5 — Twin-pointer card

📁 **Repo `/` + `/docs/` — S2799 artifacts:**

- **System prompt edit:** `core/services/unified_pa_entrypoint.py:2799` (TOOL SIGNPOSTS section, 22 lines)
- **Smoke gate:** `core/management/commands/smoke_pa_tools_for_signpost.py` (174 lines; reusable for future signpost expansions)
- **Handoff:** `docs/handoffs/SESSION_2799_RIGBY_TOOL_SIGNPOSTS.md`
- **Live test command:** `python manage.py smoke_pa_tools_for_signpost` (or `--as-json` for machine-readable output)

🖥️ **Workspace UI — `/workspaces` surface:**

- **No new Workspace tab** — the ship is a system prompt edit + a mgmt command
- **Live surfaces at close:**
  - `logs/zoom_out_classifications.jsonl` — **84 rows** (35 actionable / 27 mitigatable / 22 future_trigger); rows 78-84 are S2799 folds
  - `logs/recycle_events.jsonl` — +2 events (post-#3211 recycle + post-cascade recycle)
  - Every future Rigby chat that fits one of the 14 signpost intents → tool_run visible in chat + `ToolCallRecord` row

---

## §6 — Open items / owed / deferred

**S2799 owed follow-ups:**

- **Option B (next session's default per Chris sequencing)** — fix the 5 broken agents Thread 1 named:
  - CodeReviewAgent (76% fail — tool chaining broken; `read_file` doesn't flow to review loop)
  - WorkflowAgent + WorkflowOrchestrationAgent + CTOAgent + AudioAgent (heartbeat timeout cluster / TTS API wall)
  - Smoke gate pattern from S2799 reusable for these
- **`ops_digest_tool` handler FieldError** — `Cannot resolve keyword 'pattern_hash' into field. Choices are: category, description, ..., signature_hash`. Handler falls back to a null path; needs 5-line fix at the ORM query site. File: `core/services/td_handlers_ops.py` (grep for `pattern_hash`).
- **`calendar_tool` rename/kill** — dead per Thread 2; misnamed (studio episodes, not calendar). Own follow-up PR.
- **`mission_verdict` read-only variant** — add `list_recent` or `describe` action so it can earn a signpost.

**Standing owed (from S2797/S2798):**

- Onboarding banner in shared authed Layout (S2798 F3 future_trigger)
- Throttle on `POST /api/onboarding/complete/` (S2798 F4 future_trigger)
- Regression test for `complete_onboarding_view`
- Public deployment of LandingPage (hosting + DNS)
- BettingPage first-user trace — **explicitly deferred until Option B done** per Chris sequencing
- Waitlist DB capture (Shape B)
- I-0303 scoping (RUR-C1 parent-close blocker)
- Regression tests for 4 S2796 tools
- 8 remaining per-tool docs need "Covered actions"
- 23 tools schema-lint fix
- Wire tenant boundary health → Celery beat
- `SESSION_819_SYSTEM_AUDIT_*` cleanup (19+ files)

**Deferred (waiting on triggers):**

- **NEW: S2799 F80** — SMOKE_FAIL cluster ≥4/14 = Option-B trigger. Didn't fire this ship (0 SMOKE_FAIL); trigger stays armed for future signpost expansions.
- **NEW: S2799 F83** — Dynamic signposts via PAToolLearningEnricher (v2). Fires when Chris wants to iterate signposts without a PR.
- **NEW: S2799 F84** — Per-signpost adoption telemetry. Fires 7 days post-ship if any signposted tool has zero invocations (measures actual routing lift).
- All S2797/S2798 triggers unchanged.

---

## §7 — Chris directive queue captured this session

**Explicit sequencing given at S2799 open (mid-conversation):**

1. **C first** — this ship (Rigby tool signposts). **DONE.**
2. **B next** — fix the 5 broken agents (CodeReviewAgent + heartbeat cluster).
3. **Then BettingPage** — first-user trace + top-1 fix.

**Reframe captured to memory:** `feedback_user_ready_means_capability_not_polish.md` — "user-ready" means platform capability (agents work, Rigby toolkitted, non-betting use cases exist), not marketing polish (LandingPage, onboarding UI). Applies to future candidate menus.

---

## §8 — Discipline observations

- **PLAYBOOK-6.10.8 fold persistence timing corrected.** S2798 persisted after D-verdict; S2799 persisted 7 rows before "ship it." Consistent going forward.
- **Verify-before-build extended.** Before writing prompt copy, I read `_build_function_calling_system_prompt` end-to-end, checked ToolDispatcher.execute signature, confirmed ToolResult field names. Bug caught: I initially wrote the smoke classifier against `.data` (wrong attribute); ToolResult uses `.result`. Cost: one re-run. Would have shipped a broken smoke command otherwise.
- **Live-verify-before-close matters.** Signpost routing lift was verified in a single Rigby dispatch to `zoom_out_tool.list` before close. Cheap; catches silent prompt-cache failures.
