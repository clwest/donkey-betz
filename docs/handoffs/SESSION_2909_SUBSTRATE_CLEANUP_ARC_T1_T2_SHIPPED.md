# Session 2909 — S2909 substrate cleanup arc T1 + T2 shipped (arc closed)

**Date:** 2026-07-23
**Merged PRs:**
- T1: [#3443](https://github.com/clwest/donkey-betz-platform/pull/3443) at `dbea312541c7`
- T2: [#3444](https://github.com/clwest/donkey-betz-platform/pull/3444) at `589b0792df90`
- Close cascade: `<TBD>` at close

**Ship shape:** engineering — harness classifier fix (v1→v2 bump) + external-bridge preflight probes + arc scoping doc + backfill artifacts. NOT a doc-only session.

**Session outcome:** S2909 substrate cleanup arc opened + shipped T1 + shipped T2 + arc closed (T3 declared unnecessary via joint Claude+Rigby SIGN AGREE + Chris D-verdict). Fold B systemic-drift trigger crushed from 87.5% × 2 + 75% pre-fix → **13.3% post-T2** on sweep-covered 15 tools. Below the 50% Fold B floor that opened the arc.

---

## What shipped

### T1 — Harness soft_error classifier (PR #3443)

**File touched (1):** `core/management/commands/pa_tool_validate_harness.py`
- `HARNESS_VERSION 'v1' → 'v2'`
- `_run_single_action`: transport-success + inline error envelope (`ok:false` or `error_code` present in response dict) reclassifies to new stable `expected_outcome='soft_error'`
- Distinct label `inline_error_nested_code=` for nested-dict error codes (avoids collision with top-level)
- Summary rollup: per-tool `soft_error_count` + terminal output `[N soft_error]`
- Module docstring: Migration notes block documents Fold Q4 mitigation (per-tool validation docs are hand-authored, NOT auto-regenerated)

**Tests (new):** `core/tests/test_pa_tool_validate_harness_soft_error.py` — 8 tests, all pass.

### T2 — Bridge availability precheck (PR #3444)

**Files touched (2):**
- `core/services/tool_action_metadata.py` — `ToolActionMetadata` dataclass gains `bridge: Optional[str] = None` field. 7 external_bridge READ_ONLY entries wired (`obs_tool.health/status/last` → `bridge='obs'`; `davinci_tool.health/status/result/jobs` → `bridge='resolve_node'`). New helper `resolve_bridge(tool, action)`.
- `core/management/commands/pa_tool_validate_harness.py` — new stable `expected_outcome='skipped_bridge_unreachable'`. New `_probe_bridge(bridge_name)` method (cached per-run; probes via same client the tool uses per Rigby Q4 fold #1 critical catch). `_run_single_action` short-circuits dispatch when bridge unreachable. Summary rollup gains `skipped_bridge_unreachable_count`.

**Tests (new):** `core/tests/test_pa_tool_validate_harness_bridge_precheck.py` — 9 tests, all pass.

### Arc scoping doc (both T1 and T2 contributed)

`docs/audits/pa_tools/substrate/S2909_substrate_cleanup_arc_scoping.md` — arc-level shape + Rigby T0 SIGN folds + §6a future-trigger notes (FT-1 through FT-5).

### Backfill artifacts (both T1 and T2)

- `docs/audits/pa_tools/harness_output/*.json` — 117 files regenerated at v2 (twice — once at T1 ship, once at T2 ship)
- `docs/audits/PA_TOOLS_GAP_MAP.md` — autogen
- `docs/INDEX.md` — autogen

---

## Backfill evidence — the whole arc

Sweep-covered 15 tools (Fold B measurement scope):

| Stage | Dispatched | soft_error | bridge_unreachable | Drift % |
|---|---:|---:|---:|---:|
| Pre-fix (Fold B) | 37 | (classifier bug: showed 0) | (bug: 0) | 87.5% × 2 + 75% |
| Post-T1 (v2 classifier) | 37 | 9 | — | 24.3% |
| **Post-T2 (bridge preflight)** | **30** | **4** | **7** | **13.3%** |

Full 116-tool run at close: 69 READ_ONLY dispatched, 12 soft_error, 7 skipped_bridge_unreachable, 480 skipped for missing metadata.

**Post-T2 residual soft_errors (4):** all `orm_inspect_tool` (`describe_model / get / filter / count_by`), all with the same cause — `minimal_safe_args_v1` payload `{action: <name>}` doesn't include the required `model` param. **This is FT-5 territory** — input-synthesis substrate concern, distinct from S2909's output-classification scope. Candidate arc, deferred.

---

## Joint Claude+Rigby SIGN — three grounded cycles

**T0 arc-scope SIGN (before any code):** Rigby AGREE Q1 (coexist semantics) / AGREE Q2 (cached once-per-bridge) / AGREE Q3 (all-15-tools backfill scope) / Q4 zoom-out named DOC-AUTOGEN coupling risk (per-tool validation docs are hand-authored, NOT auto-regen'd) — folded as §4 Fold Q4 mitigation + T1 docstring migration note.

**T1 post-implementation SIGN:** Rigby SHIP-READY with 5 grounded tool_runs. Flagged stale docstring line (`Backfill scope: all 15` after --all-in-class actually ran) — polished before commit. Q4 zoom-out named FT-1 (artifact_sha256 cache-invalidation), FT-2 (error_code false-positive constraint), FT-3 (soft_error_count metric-temptation).

**T2 shape SIGN:** Rigby AGREE Q1 (metadata schema) / **REVISE Q2 (5s resolve_node / 3s obs — matched ResolveNodeClient internal timeout)** / AGREE Q3 (notes format) / Q4 zoom-out **caught a critical bug: `RESOLVE_NODE_URL` port 5001 vs `DAVINCI_BRIDGE_URL` port 9090 env sprawl — my first draft would have re-derived URLs and false-positive-skipped healthy tools**. Fold: probe via SAME client tool uses (`_obs_bridge_request` + `ResolveNodeClient.health_check()`), never re-derive. Also FT-4 (bridge-metadata consistency lint) + Q4 fold #3 (reachable = network-only semantics).

**T2 post-implementation SIGN:** Rigby SHIP-READY with 3 grounded tool_runs. Q3 verdict AGREE — T3 unnecessary given T1+T2 evidence. Q4 zoom-out named FT-5 (`minimal_safe_args_v2` substrate arc candidate — orm_inspect_tool residual drift is input-synthesis concern, distinct from S2909 scope).

**Total zoom-out asks: 3 (mandatory per session). Total substantive folds: 8 (Q4 folds + FT-1..FT-5 + stale-docstring polish + critical bug catch). Zero rubber-stamp SIGNs across all three cycles.**

---

## Post-merge live-dispatch verification (per PLAYBOOK-7.4.4)

Workers recycled via `make recycle-all` after each merge. Post-T2 recycle at `589b0792df90`.

- `obs_tool.json` post-recycle → `health/status/last` all `expected_outcome='skipped_bridge_unreachable'`, `status_code=null`, `notes='bridge=obs; OBS_ENABLED env not set'` ✓
- `davinci_tool.json` post-recycle → `health/status/result/jobs` all `expected_outcome='skipped_bridge_unreachable'`, `notes` includes `'bridge=resolve_node; resolve_node bridge offline: HTTPConnectionPool(host='localhost', port=5001): Max retries exceeded with url: /health'` ✓ (**the exact env-var Rigby's Q4 fold caught — proves the probe uses ResolveNodeClient's URL, not the settings.py-derived DAVINCI_BRIDGE_URL**)

---

## Workspace mirrors written (Rigby per `feedback_rigby_writes_workspace_deliverables`)

All 6 deliverables in Donkey Betz workspace `b4503364-2573-4401-9e28-61a739e0ce50`:

| # | Type | Title | UUID |
|---|---|---|---|
| 1 | content mirror | S2907 batch 3 handoff | `47c1f2a7-969e-40ba-aa12-12d70d0ed56a` |
| 2 | ratification | S2907 batch 3 sweep close | `45e819d0-84e9-4bf0-b9ff-42b7767eccf1` |
| 3 | content mirror | S2908 batch 4 handoff | `381ee899-f399-4878-b6f7-d1315083a339` |
| 4 | ratification | S2908 batch 4 sweep close | `4010ebeb-1d0d-4974-8774-d19c62fdffb7` |
| 5 | content mirror | S2909 arc scoping doc | `8795f629-737d-4709-8782-3f3e7ee5d3d7` |
| 6 | ratification | S2909 T1 ship close | `84dadc95-e68c-47a1-bb3a-74f7a160ed29` |
| 7 | ratification | S2909 T2 ship close | `cb91603b-cb83-4b25-8f80-1c5ae901e9ec` |

**Known Rigby tool-surface gap** (Ledger entry #31 appended): content-mirror `deliverable_tool.create` auto-flags `diagnostic_status='diagnostic'` (`missing_initiative_id`). Cleared 3 rows via ORM this session (S2907 content mirror `381ee899`, S2909 arc scoping `8795f629`). T2 ratification envelope was cleared via `deliverable_tool.update` (Rigby found a path that touches the diagnostic_* fields). Substrate fix candidate deferred.

---

## Rigby Tool Gap Ledger entries added this session

- **Entry #31:** Content-mirror auto-flagged as diagnostic — 2 instances this session — substrate fix candidate.
- **Entry #32:** FT-5 (`minimal_safe_args_v2`) tracking — new substrate arc candidate.

Ledger deliverable UUID unchanged: `5c84e75a-0ce5-4f93-9da5-f6db4e53e7f0` (Donkey Betz workspace).

---

## Arc-level future-trigger notes (recorded in `S2909_substrate_cleanup_arc_scoping.md` §6a)

- **FT-1** — `artifact_sha256` cache-invalidation ripple at v2 flip (no downstream watcher identified today; operational-ripple)
- **FT-2** — `error_code` false-positive constraint (tools must not emit `error_code` on success; enforcement TBD if false-positive observed)
- **FT-3** — `soft_error_count` new-gate-temptation (any CI/merge gate proposal ratifies separately, likely under Testing Discipline chapter candidacy — Ledger row 154)
- **FT-4** — bridge-metadata consistency lint (`external_bridge` in notes → `bridge` field required)
- **FT-5** — `minimal_safe_args_v2` substrate arc candidate (post-T2 residual drift is input-synthesis concern, distinct from S2909 scope)

---

## Arc close criteria satisfied

Per `S2909_substrate_cleanup_arc_scoping.md` §6:

1. **T1 shipped** ✓ — `soft_error` classifier + HARNESS_VERSION `v2` + backfill + docstring migration note. PR #3443 merged. Live-dispatch verified.
2. **T2 shipped** ✓ — bridge preflight + `skipped_bridge_unreachable` + backfill. PR #3444 merged. Live-dispatch verified.
3. **T3 D-verdict recorded** ✓ — Chris ratified Option A (close arc without T3) 2026-07-23 after joint Claude+Rigby AGREE that T1+T2 evidence answers the arc's primary question decisively.

**Total sessions: 1 (same as T1a in the earlier substrate arc). Beat the ≤3-session estimate.**

---

## Closed-by-arc references

- S2907 substrate finding "T1a harness `status_code`-only misclassification of inline `{ok:false}` envelopes as success" → **CLOSED-BY-ARC-T1** at `dbea312541c7`
- S2908 substrate finding "Bridge-unreachable-during-harness detection gap" → **CLOSED-BY-ARC-T2** at `589b0792df90`
- T1a FT-2 "harness `soft_error` outcome value substrate-arc-scope" → **SHIPPED** at `dbea312541c7`

---

## What's next (S2910 open)

**First action:** resume Slice 2 sweep. Harness now trustworthy — future batches measure real drift against a fixed classifier. Batch 5 = pick 3-5 more tools from `td_handlers_agents` untested slice (currently 10 tools remaining).

**Session posture:** back to sweep-batch pace (S2905-S2908 shape). No substrate work pending in-arc.

**Ledger status update in 00-START:** S2905/S2906/S2907/S2908 substrate findings all now have their post-arc dispositions recorded. S2909 arc closes. Ledger rows 154-162 all unchanged except FT-1..FT-5 added to deferred queue.
