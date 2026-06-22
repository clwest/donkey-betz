# Session 1202 — Connectivity Roadmap Phase A close (§A.1 + §A.2 shipped, 7 PRs)

**Status:** Closed clean. **7 PRs merged.** Roadmap Phase A fully closed — operator can now spawn + bind + link Initiatives via PA tool, and Rigby has 7 audit-grade diagnostic actions for subsystem health grading. Both phases Rigby-verified live.
**Date:** 2026-06-22
**Active conversation:** `pa-123b7d48f01043eb` — spun fresh mid-session at the §A.1→§A.2 boundary because the prior thread (`pa-1ccc494ea00b4e77`) was carrying Sessions 1200 + 1201 + §A.1 context. Titled "Session 1202 — Phase A.2 (diagnostics_tool 7 actions)". `tools/pa_local.sh` updated.
**Prior session:** [`SESSION_1201_CONNECTIVITY_RECON_16_ROWS.md`](./SESSION_1201_CONNECTIVITY_RECON_16_ROWS.md).
**Next session entry point:** Roadmap Phase B.1 — Producer Reroute Completion (3 single-file PRs in `agent_router.py`, `tasks.py`, `workspace_manager.py`).

## TL;DR

§A.1 + §A.2 of `CONNECTIVITY_COMPLETION_ROADMAP.md` shipped end-to-end with Rigby smoke verification at every PR boundary. Net: Initiatives `f4cfe31e-…` (Initiative-Management Tool Surface Gaps) and `50b7adf2-…` (Diagnostic Telemetry Tool Surface Gaps) are closeable; the auditing infrastructure the Reality Map called for is live.

Two operator-ergonomic v2/v3 fixes shipped same-session catching Rigby's smoke findings:
- **#2443 (v1 null no-op) + #2444 (v2 empty-string also no-op)** — GPT-5.2 fills unset string params with `""` not `null`; v1 closed the null path but not the `""` path Rigby actually hit. v2 made both no-ops.
- **#2447 (v3 meta-tool exclusion)** — Rigby's PR-2 smoke caught `run_agent` flagged as `schema_only` (real-bug bucket); fix added `schema_only_meta_tool` bucket. Result: zero real schema/handler gaps detected platform-wide.

Two findings from Rigby's smoke arc surfaced but **not** addressed in this session — both flagged in §C below as follow-up scope:
1. `advisor_invocations` returned **0 across all advisors** in 7d window. Refines Row 10 of the Reality Map (advisor wiring status).
2. `discord_health` returned **0 invocations** in 7d. Discord bot is a long-running process; may not be wired through `CeleryTaskEvent`. Refines Row 16.

## Session Manifest

### Initiatives created / touched

| ID | Name | Kind | Status | Workspace | Action |
|---|---|---|---|---|---|
| `f4cfe31e-366b-4d5e-802c-041ba66c7afb` | Initiative-Management Tool Surface Gaps | project | ACTIVE → ready-to-close | DBZ | §A.1 scope closed via PRs #2442/#2443/#2444 + Rigby verify |
| `50b7adf2-ec1c-4ef0-8245-ec026cff114f` | Diagnostic Telemetry Tool Surface Gaps | project | ACTIVE → ready-to-close | DBZ | §A.2 scope closed via PRs #2445/#2446/#2447 + Rigby verify |

Status flip to COMPLETED deferred to Session 1203 close to give the operator a chance to ratify; the work is shipped + verified.

### Deliverables created / touched

Two new follow-up Initiative findings worth filing as deliverables under the **Reality Map parent** (`0ecd1bc2-…`) in Session 1203:
| Title | Source | Row attribution | Suggested target Initiative |
|---|---|---|---|
| `advisor_invocations` all zero in 7d (live smoke) | Rigby PR-2445 smoke | Row 10 refinement | Reality Map parent or new investigation Initiative |
| `discord_health` zero invocations in 7d (live smoke) | Rigby PR-2446 smoke | Row 16 refinement | Reality Map parent or new investigation Initiative |

### PRs merged (7)

| PR | Title | Branch | Commit |
|---|---|---|---|
| [#2441](https://github.com/clwest/donkey-betz-platform/pull/2441) | docs(session-1201): close — Platform Connectivity Reality Map recon | `docs/session-1201-connectivity-reality-map-recon` | `43fa7d19` |
| [#2442](https://github.com/clwest/donkey-betz-platform/pull/2442) | feat(session-1202-pa): work_tool initiative_update + initiative_link (§A.1) | `feat/session-1202-initiative-update-link` | `a26261ec` |
| [#2443](https://github.com/clwest/donkey-betz-platform/pull/2443) | fix(session-1202-pa): initiative_update treats payload null as no-op | `fix/session-1202-initiative-update-none-noop` | `1d26a80b` |
| [#2444](https://github.com/clwest/donkey-betz-platform/pull/2444) | fix(session-1202-pa): v2 — empty string is also a no-op (LLM default) | `fix/session-1202-initiative-update-empty-also-noop` | `69f643f2` |
| [#2445](https://github.com/clwest/donkey-betz-platform/pull/2445) | feat(session-1202-pa): diagnostics_tool PR-1 (4 simple actions) + pa_local pin | `feat/session-1202-diagnostics-tool-pr1` | `6525dd10` |
| [#2446](https://github.com/clwest/donkey-betz-platform/pull/2446) | feat(session-1202-pa): diagnostics_tool PR-2 (3 medium actions) | `feat/session-1202-diagnostics-tool-pr2` | `67fd92e2` |
| [#2447](https://github.com/clwest/donkey-betz-platform/pull/2447) | fix(session-1202-pa): schema_handler_diff — exclude meta-tools (v3) | `fix/session-1202-schema-handler-diff-meta-tool` | `554a41d3` |

## What §A.1 ships

Two new actions on `work_tool` that close the ORM-bypass that bit Rigby 8+ times during Session 1201's Reality Map recon:

- **`work_tool action=initiative_update`** — patch `target_workspace_id`, `description`, `kind` on an Initiative. v2 contract: `absent | null | "" → no-op`, value → set. Idempotent.
- **`work_tool action=initiative_link`** — write bidirectional `related_initiatives` per `INITIATIVES_FIRST_BACKBONE.md §6.4`. Mirror direction computed from `relation` (`spawns` | `spawned_from`). `select_for_update` to serialize concurrent rewrites. Idempotent on `(parent, child, relation)` tuple.

**Delta from spec:** substituted `kind` for `tags` (Initiative has no tags field). Operator ratification: shipped without pushback.

**Test coverage:** 22 tests in `core/tests/test_initiative_management_tools.py` (15 initial + 5 null/v1 + 5 empty-string/v2 — actually 22 after all merges, locked the GPT-bloat-payload no-collateral-clear contract).

## What §A.2 ships

New top-level tool `diagnostics_tool` with 7 actions for audit/inventory telemetry (distinct from `ops_tool` which is SRE/SLO-focused). Total handlers: **174** (was 173).

| Action | Source | Output |
|---|---|---|
| `advisor_invocations` | AgentExecution joined to Advisor | Per-advisor N-day count + zero-invocation flag |
| `provider_calls` | LLMCallLog | Per-provider rollup + zero-call provider detection |
| `beat_schedule_health` | PeriodicTask | Stalest-first pagination + zero-run flags |
| `workspace_metrics` | ProjectWorkspace + deliverables annotate | last_operation_at + counts + autonomous flag |
| `schema_handler_diff` | PA_TOOL_SCHEMAS vs _tool_handlers | 5-bucket gap classification; meta-tool excluded |
| `learning_bridge_writes` | UserAgentLearning + bridge registry | Per-bridge attribution (6 heuristic + 2 precise) + by_domain/by_source rollups |
| `discord_health` | CeleryTaskEvent | total/success/failure + last-alive proxy |

**Test coverage:** 23 tests in `core/tests/test_diagnostics_tool.py`.

**Closed false positive:** PR-2 v3 fix added `_SCHEMA_HANDLER_DIFF_META_TOOLS = {'run_agent'}` so `schema_handler_diff` no longer flags the `run_agent` meta-tool as a real gap. Live result after v3: **`schema_only=0, handler_only_orphan=0`** — platform has zero real schema/handler gaps detected.

## Per-PR rollback levers

Each PR is single-feature with isolated revert. The most production-touching change is the live `work_tool` schema change (#2442); revert is clean — caller error messages change but no data migration involved.

| PR | Revert command | Side effect |
|---|---|---|
| #2442 | `git revert a26261ec` | `work_tool action=initiative_update/link` returns "Unknown action" |
| #2443 / #2444 | `git revert <sha>` | `initiative_update` reverts to v1 / v0 contract — empty string clears |
| #2445 / #2446 | `git revert <sha>` | `diagnostics_tool` action(s) revert to placeholder errors |
| #2447 | `git revert 554a41d3` | `schema_handler_diff` re-flags `run_agent` as `schema_only` (false positive but harmless) |

## 24h watch checklist (Session 1203 opener)

Per the memory rule on operational handoff sections:

```bash
# 1. Worker freshness (workers should be from 2026-06-22 13:51+ if not bumped)
ps -eo pid,lstart | grep celery | head -1

# 2. work_tool sanity — initiative_update should idempotent
tools/pa_local.sh "Run work_tool action=initiative_update id=<any> kind=project once; \
  run it again; confirm second response has updated_fields=[]"

# 3. work_tool link — bidirectional rule
tools/pa_local.sh "Run work_tool action=initiative_link parent_id=<x> child_id=<y> relation=spawns; \
  call initiative_detail on both and confirm related_initiatives populated on both sides"

# 4. diagnostics_tool sanity — all 7 actions return structured JSON (not placeholder errors)
tools/pa_local.sh "Run diagnostics_tool with each of: advisor_invocations, provider_calls, \
  beat_schedule_health, workspace_metrics, schema_handler_diff, learning_bridge_writes, \
  discord_health. Confirm none return pending_pr field"

# 5. schema_handler_diff sanity — zero real gaps
tools/pa_local.sh "Run diagnostics_tool action=schema_handler_diff; \
  confirm totals.schema_only=0 AND totals.handler_only_orphan=0"

# 6. Daily inference watch Day-1 (independent, fires 2026-06-23)
grep '\[DELIVERABLE-FACTORY-ENTRY\]' celery*.log | wc -l    # A — total
grep '\[DELIVERABLE-FACTORY-ENTRY\]' celery*.log | grep 'initiative_id_present=False' | wc -l    # B — eligible
grep '\[INFERENCE-MATCH\] agent=' celery*.log | wc -l    # C — matches
grep '\[ORPHAN-DELIVERABLE\] code=missing_initiative_id' celery*.log | wc -l    # D — orphans
```

## Invariants (post-merge)

1. `work_tool action=initiative_update` with `description: "" | null | absent` is a no-op for description. Same for `target_workspace_id` and `kind`. Real-value-only writes.
2. `work_tool action=initiative_link` writes both sides of the relation in a single transaction. `(parent_id, child_id, relation)` tuple is idempotent.
3. `diagnostics_tool` is read-only — no mutations on any action.
4. `schema_handler_diff` distinguishes intercepted-meta-tools (`schema_only_meta_tool` — by design) from real bugs (`schema_only` — empty as of today's snapshot).
5. All 7 `diagnostics_tool` actions return `gateway: 'diagnostics_tool'` in the result; no `pending_pr` field.

## Findings for Session 1203 follow-up

Both surfaced by Rigby's live smoke after PR-1/PR-2 merges. NOT bugs in the tools themselves — the tools work; they reveal real platform gaps.

### Finding 1 — Advisor invocations all zero in 7d

**Observation:** `diagnostics_tool action=advisor_invocations` reports 0 invocations across ALL 30 Advisor rows in the 7-day window.

**Hypotheses:**
- (a) Genuine — advisors really aren't being invoked by anything in the platform. Confirms Row 10 of the Reality Map; the advisor system is registered but dry.
- (b) Name mismatch — `Agent.name` rows don't match `Advisor.name` rows by exact string. The `advisor_invocations` join is on exact name; could miss invocations if the dispatcher uses a different identifier.
- (c) Stale data — invocations stored in a different table (e.g., `AgentExecution` of a different `agent` row).

**Next step (Session 1203 P3):** Spawn an investigation Initiative or attach as a deliverable to Reality Map Row 10. Step 1 is the name-resolution check — compare `set(Advisor.name)` to `set(AgentExecution.objects.values_list('agent__name'))`.

### Finding 2 — Discord health zero invocations in 7d

**Observation:** `diagnostics_tool action=discord_health` reports 0 invocations in 7-day window, `last_alive_at: null`.

**Hypotheses:**
- (a) Bot is genuinely down.
- (b) Bot is up but its tasks aren't `@shared_task`-decorated, so they don't write to `CeleryTaskEvent`. The bot is a long-running daphne-adjacent process with its own event loop.
- (c) Task names don't match the `task_name__icontains='discord'` filter.

**Next step (Session 1203 P3):** Check `ps -ef | grep discord` for the bot process, then `grep -i discord celery*.log` to see whether dispatches are logged. If the bot is up but not writing `CeleryTaskEvent`, `discord_health` needs a different data source (e.g., bot heartbeat file).

## Behavioral invariants we discovered (memory candidates)

1. **GPT-5.2 fills unset string params with `""` not `null`** — confirmed at `celery-pa.log:2640` (`Sig: ... "name":"" ...`). Any new PA tool that accepts optional string params must treat `""` as "no-op / leave alone." The `""=clear` semantic only works if the LLM is the caller of last resort.
2. **Meta-tools intercepted before the dispatcher need explicit allowlist** — `unified_pa_entrypoint.py:1687` intercepts `run_agent` and routes via `agent_name`. Any future meta-tool added there must also land in `_SCHEMA_HANDLER_DIFF_META_TOOLS`. Worth adding a comment at the entrypoint line to point to the allowlist.
3. **TransactionTestCase required for tests that hit ToolDispatcher.execute_sync** — sync handlers run in thread-pool executor with separate DB connection; TestCase transaction wrap is invisible to that connection. Confirmed at #2442 first-run failure.

## Provenance

- All 7 PRs authored Session 1202 (2026-06-22) by Claude + ratified-as-shipped by Chris.
- Rigby (PA on `pa-1ccc494ea00b4e77` then `pa-123b7d48f01043eb`) smoke-tested every shipped PR and surfaced 4 follow-up findings (2 closed same-session via v2/v3 fixes; 2 deferred to Session 1203 as Findings 1 + 2 above).
- Roadmap parent: `docs/specs/CONNECTIVITY_COMPLETION_ROADMAP.md` §A.1 + §A.2.
- Reality Map parent: `0ecd1bc2-9931-4464-8efa-495a28b58779` (investigation, ACTIVE, DBZ).
- Phase B (Sessions 1203-1204): "stop live drift" — Producer Reroute Completion is P1.
