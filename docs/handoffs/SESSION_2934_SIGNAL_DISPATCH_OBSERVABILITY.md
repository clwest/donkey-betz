# SESSION 2934 — Signal-dispatch observability + third rule + on-demand harness

**Date:** 2026-07-24
**Merge SHA:** `242d6116c`
**PR:** [#3503](https://github.com/clwest/donkey-betz-platform/pull/3503)
**Shape:** Net-new engineering — 975-line insert-only diff (1 endpoint + 1 mgmt command + 1 tab component + 2 test files + 13 new tests + 1 rule). ~90 min end-to-end.
**Ratification:** Chris "Approved, ship it" after joint Claude+Rigby AGREE on bundled A4+A5+A7.

---

## What shipped

Three additions to the S2933 A3 reactive-orchestration pipeline, bundled into one PR because Rigby's zoom-out (0.58% active-cluster rate ⇒ "dead dashboard" risk for A4 alone) argued for shipping the harness in the same slice.

### A4 — Signal Dispatches Workspace tab

- **Endpoint:** `GET /api/v1/agents/signal-dispatches/`
  (`core/views_signal_dispatch.py`) — read-only over `SignalDispatch`.
  Filters: `pattern_type`, `outcome`, `rule_key`. Pagination:
  `limit` (default 25, max 200) + `offset` + `total_count` +
  `has_more` (same shape as `/unified-executions/` from S2930).
- **URL registration:** `core/urls.py` — one line added next to the
  S2930 agent-runs route.
- **API client:** `agentsApi.signalDispatches` in
  `frontend/src/lib/api.ts`.
- **Tab component:** `SignalDispatchesTab` in
  `frontend/src/pages/workspace/tabs/SignalDispatchesTab.tsx` —
  clones the AgentRunsTab (S2930) shape. 25/page table with
  columns: When / Pattern / Agent / Outcome / Cluster / Scan Run /
  Duration. Manual dispatches visually badged (Zap icon + amber)
  so they never blend with reactive-pipeline analytics. Row click
  opens a detail panel with cluster metadata, agent execution UUID,
  input payload JSON, and error summary.
- **Mount:** New `system → signal-dispatches` sub-tab in
  `frontend/src/pages/WorkspacePageNew.tsx`.

### A5 — Third dispatch rule

Added to `SIGNAL_DISPATCH_RULES` in
`core/services/signal_dispatch_service.py`:

| Rule key | pattern_type | Agent | min_strength | min_confidence | max_per_day |
|---|---|---|---|---|---|
| `opportunity_window__opportunity_scoring` | `opportunity_window` | `OpportunityScoringAgent` | 0.5 | 0.5 | 10 |

**Verification chain before commit** (mirrors S2933 method):
- `agent_introspection_tool` — OpportunityScoringAgent: 33 total executions, 96 effectiveness, 2/2 recent 7d success.
- ORM — 117 opportunity_window clusters exist (1 active + others rotating through detecting/decayed/archived).
- `AGENT_MAP` — `'OpportunityScoringAgent' in AgentRouter.AGENT_MAP` = True.

### A7 — `python manage.py dispatch_signal --cluster-id X`

On-demand harness for the pipeline. Companion to S2933's
`resend_signal_dispatch` (which re-fires a specific prior
dispatch); this synthesizes a **new** dispatch for any cluster.

**Rigby SIGN safety envelope (all enforced):**
- `--cluster-id` required (no batch mode).
- Idempotent guard: an in-flight/succeeded prior dispatch for
  `(cluster, rule_key)` within the default 5-min window blocks
  re-dispatch unless `--force`. Configurable via
  `--guard-window-minutes`.
- Manual dispatches labeled `scan_run_id='manual'` so they never
  contaminate reactive-pipeline analytics. Frontend badges them.
- No background scanning — one cluster per invocation.
- Rule auto-pick from `cluster.pattern_type`; errors if 0 or 2+
  match; explicit `--rule-key` accepted.
- `--sync` executes inline; default enqueues to Celery long_running.

## Post-merge live evidence

Verified after `make recycle-all` at 16:19 UTC.

**Reactive path (unexpected bonus, better than manual harness):**

Beat scheduler picked up the new A5 rule and fired
`scan-signal-dispatch-rules` at 16:20:00 UTC — **90 seconds after
merge**. Scanner found the active opportunity_window cluster
`62bdb598-dc89-43af-a0e8-1e368e94ee60` ("Chatgpt, Openai
opportunity window"), enqueued dispatch, OpportunityScoringAgent
executed successfully (`execution_id=37c66dd7-d1e5-49c6-b04c-2fea5efc442e`).
Row created with `scan_run_id=b6d3b2b747fc44e8` (real scanner run,
not manual). **A5 rule ships fires reactively for real, not just
theoretically.**

**Idempotent guard path:**

Called `dispatch_signal --sync` (no `--force`) against the same
cluster at 16:21:20. Correctly errored with:
> `CommandError: Idempotent guard: dispatch 798587a9-... exists within 5min window (outcome=succeeded). Pass --force to override.`

**Manual `--force` path + labeling:**

Called `dispatch_signal --sync --force` against the same cluster
at 16:21:32. New row `3f189266-2511-4132-b691-d6a4c18b19bb` created
with `scan_run_id='manual'` (Rigby SIGN safety condition
satisfied). Sync path executed OpportunityScoringAgent inline.

**A4 endpoint path:**

`GET /api/v1/agents/signal-dispatches/` returned HTTP 200 with the
correct row count (Rigby verified via her tool surface).

## Test coverage

- **`core/tests/test_s2934_signal_dispatch_harness.py` — 13 new tests:**
  - 9 for `dispatch_signal`: auto-pick / explicit rule / idempotent
    guard block / --force bypass / --sync inline / configurable
    guard window / missing cluster / no-matching-rule / mismatched
    rule.
  - 5 for the list endpoint: envelope shape / pattern_type filter /
    outcome filter / pagination / limit cap.
- **`core/tests/test_signal_dispatch_service.py` — 2 new tests:**
  opportunity_window rule shape + anti-regression on registry size
  (=3).
- **All 36 tests pass. Django check clean.**

## Governance

None this session. D6 moratorium unchanged. Zero new forbidden-entry candidates.

## Rigby Tool Gap Ledger

**One LOW observation (S2934 A7 verification):** Rigby has no
`terminal_tool` in her PA surface, so she couldn't run the
`dispatch_signal` mgmt command herself for post-merge verification —
I ran it locally and routed the result back for cross-check. Same
class as the S2933 `orm_inspect_tool` allowlist gap. Not opening
as a formal Ledger entry yet; will promote if a third
tool-surface gap of the "operator-critical CLI unreachable from PA"
shape surfaces.

## Zoom-out fold (Rigby, deferred)

**CLI-only control plane for the harness.** `dispatch_signal` is
great for determinism, but requiring shell access makes verification
and demos fragile. Follow-up arc candidate: expose an authenticated
"Manual dispatch" button in the Signal Dispatches tab that calls
the same service method with the same idempotency/force guardrails.

Recorded here as future-arc candidate. Not opening this session per
Chris's engineering-bias-over-audit directive — the current bundle
already ships all three ratified slices.

## Files touched (10)

**New (4):**
- `core/views_signal_dispatch.py` — endpoint (78 lines)
- `core/management/commands/dispatch_signal.py` — A7 harness (157 lines)
- `core/tests/test_s2934_signal_dispatch_harness.py` — 13 new tests (~250 lines)
- `frontend/src/pages/workspace/tabs/SignalDispatchesTab.tsx` — tab component (436 lines)

**Modified (6):**
- `core/services/signal_dispatch_service.py` — third rule (+13 lines)
- `core/tests/test_signal_dispatch_service.py` — 2 new tests (+15 lines)
- `core/urls.py` — endpoint route + import (+2 lines)
- `frontend/src/lib/api.ts` — signalDispatches API client (+8 lines)
- `frontend/src/pages/WorkspacePageNew.tsx` — subtab + import + mount (+5 lines)
- `frontend/src/pages/workspace/tabs/index.ts` — export (+3 lines)

**Total: 975-line insert-only diff.**

---

## What's next

No governance blocking. Clean surface for S2935. Candidate leans
carried forward:

- **S2934 zoom-out follow-on:** Expose in-tab "Manual dispatch"
  button so operators don't need shell access to fire test
  dispatches. ~30 min.
- **A6 (deferred from S2934 open):** upstream promotion audit —
  only 5/862 SignalClusters currently active (~0.58%). Investigate
  whether `SignalAggregationService` is under-promoting or whether
  the rarity is a natural signal-quality floor.
- **A5 continuation:** additional (pattern_type → agent) rules.
  Remaining candidates observed at S2934 open: `demand_spike` (250
  clusters, 8 detecting), `skill_demand` (131 clusters),
  `sentiment_shift` (15 clusters).
- **Slice 5-hardening** — 3-4 executable invariants deferred at S2928 fork A.
- **Slice 6 sweep continuation** — `td_handlers_content.py` (6 tools).
- **Docs restructuring arc** — unblocked at S2800, still queued.
