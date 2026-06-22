# Session 1201 — Platform Connectivity Reality Map recon (16 rows, 4 child Initiatives, completion roadmap)

**Status:** Closed clean. **0 PRs merged** (recon-only session — fix work scheduled in 6-8 session arc per roadmap). **1 parent Initiative + 4 child Initiatives + 15 deliverables created**; all DBZ-bound + bidirectionally linked.
**Date:** 2026-06-22
**Active conversation:** `pa-1ccc494ea00b4e77` (continued from Session 1200; titled "Session 1200 — Watch Tracking + Phase 2 Gate (Plan C)"; can stay on this thread for Session 1202 or spin fresh).
**Prior session:** [`SESSION_1200_DAY0_INFERENCE_WATCH_INSTRUMENTATION.md`](./SESSION_1200_DAY0_INFERENCE_WATCH_INSTRUMENTATION.md).
**Next session entry point:** Connectivity Completion Roadmap Phase A (`docs/specs/CONNECTIVITY_COMPLETION_ROADMAP.md`).

## TL;DR

Chris's open question — "are agents + tools + learning + spiders + body systems actually wired together end-to-end, or are pieces dry?" — drove a 16-row drift map across the platform. Investigation surfaced **4 distinct fix arcs** worth filing as child Initiatives:

1. **Producer Reroute Completion** — Session 1199 fix was applied to 1 callsite but 3 others still leak (agent_router fallback, SKIN layer helper, activate_workspace exclusion). Confirmed live: every Initiative spawned today produced an auto-research deliverable in System Autonomous Workspace, NOT DBZ.
2. **Initiative-Management Tool Surface Gaps** — `work_tool` has no `initiative_update` or `initiative_link` actions. Rigby could not patch `target_workspace_id` or write bidirectional `related_initiatives` per `INITIATIVES_FIRST_BACKBONE.md` §6.4. Required ORM bypass on every Initiative spawn this session.
3. **Docs ↔ Runtime Alignment Layer** — `context-kit orient` shows narrative anchors but not live Initiative/Deliverable state; handoffs are hand-written at close, drift compounds each session. Structural fixes: close-session manifest + orient enhancement.
4. **Diagnostic Telemetry Tool Surface Gaps** — 6 of 8 Phase 2 audit rows hit the same wall: no PA tool exposes per-advisor invocations, per-bridge writes, schema↔handler diff, per-provider calls, etc. The audit can't grade itself without ORM.

**Net:** Reality Map Initiative `0ecd1bc2-…` (investigation, ACTIVE, DBZ, spawned_from Spine 1) holds the 16 row classifications. 4 child Initiatives (each `kind=project` except Docs↔Runtime which is `recurring_artifact`) hold the fix scope. The Connectivity Completion Roadmap (`docs/specs/CONNECTIVITY_COMPLETION_ROADMAP.md`) sequences all 5 phases in dependency order. Estimated 6-8 sessions to full close.

## Session Manifest *(new pattern per Docs↔Runtime Alignment Initiative)*

### Initiatives created / touched

| ID | Name | Kind | Status | Workspace | Notes |
|---|---|---|---|---|---|
| `0ecd1bc2-9931-4464-8efa-495a28b58779` | Platform Connectivity Reality Map | investigation | ACTIVE | DBZ | Parent of all 4 children; spawned_from Spine 1 |
| `05931145-89d2-4923-946e-676e0db44e91` | Producer Reroute Completion — Patch 3 Bypass Callsites | project | ACTIVE | DBZ | spawned_from Reality Map |
| `f4cfe31e-366b-4d5e-802c-041ba66c7afb` | Initiative-Management Tool Surface Gaps | project | ACTIVE | DBZ | spawned_from Reality Map |
| `1859dd51-ce3b-4689-bd4b-42d9de5793d8` | Docs ↔ Runtime Alignment Layer | recurring_artifact | ACTIVE | DBZ | spawned_from Reality Map |
| `50b7adf2-ec1c-4ef0-8245-ec026cff114f` | Diagnostic Telemetry Tool Surface Gaps | project | ACTIVE | DBZ | spawned_from Reality Map |
| `6941372d-b13c-4631-91c8-749fa65c55a0` | Spine 1 — Initiatives-First Wiring + No-Orphan Output | project | ACTIVE | DBZ | TOUCHED — added `spawns` link to Reality Map |

### Deliverables created / touched

| ID | Title | Initiative | Tags |
|---|---|---|---|
| `23edb2a4-38fe-4909-b592-844f9f0148cd` | Row 5 — Deliverables → Learning | Reality Map | `connectivity-reality-map` |
| `3c185661-c708-4723-9bff-a2feb60dc2bc` | Row 6 — Body Systems / Coordinator | Reality Map | `connectivity-reality-map` |
| `8da895f0-e8c8-485c-b0c8-a3fd5d32823e` | Recon: Producer reroute bypass leak sites | Producer Reroute Completion | `producer-reroute`, `connectivity-reality-map-child` |
| `22bd184a-53dd-40b2-9fd4-6efc12b05e9b` | Recon: work_tool initiative-management surface gaps | Initiative-Management Tool Surface Gaps | `work-tool-surface`, `connectivity-reality-map-child` |
| `00c286cd-df2d-4951-a58e-b14f1354769f` | Docs ↔ Runtime Alignment — Session 1201 Baseline Reconciliation | Docs ↔ Runtime Alignment | `docs-runtime-alignment` |
| `621ad9dc-fa0d-4eb0-9258-38a877cca22c` | Diagnostic Telemetry Tool Surface Gaps — Initial Inventory | Diagnostic Telemetry Tool Surface Gaps | `diagnostic-tool-surface`, `connectivity-reality-map-child` |
| `44faf5ae-592f-42b5-a1c2-1bdb2aae7edf` | Row 9 — Initiative auto-research evidence mismatch | Reality Map | `connectivity-reality-map` |
| `d3bb67ae-28a7-49c7-ae8a-37a973bacdcd` | Row 10 — Advisor invocation reality | Reality Map | `connectivity-reality-map` (Claude-lane append shipped) |
| `a00d8953-5b28-4a3d-9b5f-961b8480b569` | Row 11 — PA Tool schema ↔ handler gap | Reality Map | `connectivity-reality-map` (Claude-lane append shipped) |
| `2e1c6423-cd85-4fd2-8183-5c646d3eccc4` | Row 12 — 6 LLM Provider usage reality | Reality Map | `connectivity-reality-map` |
| `0b4a7cdc-ee00-4cf6-baf1-f51fea695d2c` | Row 13 — 8 Learning Bridges writer audit | Reality Map | `connectivity-reality-map` |
| (Rows 14-16 deliverables not separately captured during truncated tool output — see Rigby's `pa-1ccc494ea00b4e77` thread for UUIDs) | | | |
| `d3f2fc09-b45c-4fea-80da-3f3f98797cf7` | Connectivity Completion Roadmap — sequenced fix plan (pointer to `docs/specs/CONNECTIVITY_COMPLETION_ROADMAP.md`) | Reality Map | `connectivity-reality-map`, `completion-roadmap`, `session-1201-close` |

## Behavioral invariants — what's now true post-session

- Reality Map Initiative `0ecd1bc2-…` exists in DBZ workspace as `kind=investigation`, ACTIVE, with 4 `spawns` links to children + 1 `spawned_from` link to Spine 1 (`6941372d-…`). Spine 1 has reciprocal `spawns` → Reality Map.
- All 4 child Initiatives are DBZ-bound + bidirectionally linked to Reality Map per `INITIATIVES_FIRST_BACKBONE.md` §6.4 (spawns / spawned_from + idempotent + bidirectional).
- 15 deliverables tagged `connectivity-reality-map` (rows) + `connectivity-reality-map-child` (child Initiative recon) exist + are bound to their parent Initiative.
- `[INITIATIVE-DIAGNOSTIC-CLEARED]` signal fired on all 4 children when their `target_workspace_id` flipped from NULL to DBZ.
- Reality Map row classifications:
  - **Wire-exists + flowing:** Rows 11 (false drift identified), 12 (partial confirmation — OpenAI only), 15
  - **Wire-exists + dry:** Rows 5 (data scarcity + threshold gating), 6 (no autonomic tick scheduled)
  - **Wire-exists + broken:** Row 9 (auto-research evidence mismatch — multi-week)
  - **Wire-exists + narrative drift:** Row 10 (25 advisors with real names vs claimed "30 functional")
  - **Wire-exists + telemetry blocked:** Rows 13, 14, 16
  - **Rows 1-4, 7-8** carried forward to Sessions 1202+ per Reality Map cadence

## Rollback / disable levers

- **All 4 child Initiatives are independently revertible.** Each holds fix scope only — no production code shipped. Set `status=ARCHIVED` on any child to defer that fix arc.
- **Reality Map → Spine 1 linkage:** `Initiative.related_initiatives` is JSONField — direct ORM removal of the `(spine_1, spawns, reality_map)` and `(reality_map, spawned_from, spine_1)` entries reverts.
- **Connectivity Completion Roadmap doc:** `docs/specs/CONNECTIVITY_COMPLETION_ROADMAP.md` is purely advisory; `git rm` reverts cleanly.
- **No production behavior changed this session.** Only ORM patches (workspace binding + `related_initiatives` JSON writes on Initiatives created during the session).

## Open items into Session 1202

| Priority | Item | Where it's defined |
|---|---|---|
| **P1 (daily, active 2026-06-23)** | Daily watch appends — inference accuracy + default-only-projects | Session 1200 handoff §"Day-0 protocol artifacts"; runbook `cb9d8ae1-…`; append target `9ba58690-…` |
| **P1 (Reality Map roadmap)** | Phase A.1 — ship `work_tool` `initiative_update` + `initiative_link` | `docs/specs/CONNECTIVITY_COMPLETION_ROADMAP.md` §Phase A.1 |
| **P1 (Reality Map roadmap)** | Phase A.2 — ship 7 `diagnostics_tool` actions | `docs/specs/CONNECTIVITY_COMPLETION_ROADMAP.md` §Phase A.2 |
| P2 | Phase B.1 — Producer Reroute Completion (3 PRs) | Roadmap §Phase B.1; Initiative `05931145-…` |
| P2 | Phase B.2 — Row 9 auto-research evidence supplier fix | Roadmap §Phase B.2 |
| P2 | Phase B.3 — backfill 31 NULL-workspace Initiatives | Roadmap §Phase B.3 |
| P3 | Phase C — structural fixes (close-session manifest + orient enhancement) | Roadmap §Phase C; Initiative `1859dd51-…` |
| **P1 (time-gated 2026-06-29)** | Plan C Phase 2 hard-reject flip | Session 1200 handoff |
| **P1 (time-gated 2026-06-29)** | Session 1196 7-day watch | Session 1200 handoff |
| **P1 (time-gated 2026-06-30)** | Day-8 inference watch decision | Session 1200 handoff |

## Decision points for Chris (when ready)

1. **Row 10 advisors:** Option A (correct docs to data — 25 real-person names) or Option B (migrate data to functional)? → roadmap §D.7
2. **Row 6 body coordinator:** Enable autonomous tick now, or audit response logic first? → roadmap §D.6
3. **Phase ordering:** Strict A → B → C → D → E, or interleave? → roadmap §"Decision points"
4. **Spine Initiatives:** Address opportunistically (when Phase E becomes possible) or actively plan? → roadmap §Phase E

## Mechanism findings worth keeping

These shipped as memory updates (see `MEMORY.md` additions Session 1201):

1. **Gateway pattern false drift** — schema↔handler counts compare different layers; `run_agent` is a meta-tool special-cased in `core/services/unified_pa_entrypoint.py:1687`. The "108 vs 173" framing in PLATFORM_INVENTORY creates phantom drift signal.
2. **Producer Reroute Session 1199 fix was partial.** `_ensure_system_workspace` honors `DEFAULT_PRODUCER_WORKSPACE_ID` but `agent_router.py:1083` + `tasks.py:7748` + `workspace_manager.py:1906` don't. Most Initiatives spawned WITHOUT explicit workspace_id leak to System Autonomous via the router fallback.
3. **31 of 46 Initiatives have NULL `target_workspace_id`.** Spawn-without-workspace is the Initiative-side equivalent of the producer reroute leak. One-shot backfill needed in addition to forward-fix.
4. **Initiative pipeline Stage 1 auto-research is broken since at least 2026-06-14.** Every spawn produces an Initiative whose Stage 1 BLOCKS on irrelevant SEC/Kaggle evidence. Spine 1/2/3 are all stuck here. Fix is upstream of the Reality Map row work.
5. **Tool-surface gaps are 2-class:** (A) initiative-management (`f4cfe31e-…`), (B) diagnostic-telemetry (`50b7adf2-…`). Most audit work this session hit one or both.

## Memory rules touched / added during Session 1201

- Added: `feedback_no_eod_framing.md` — don't propose "defer to tomorrow" mid-morning when a multi-session arc is active
- Touched: `feedback_corpus_walks_surface_mechanism_drift.md` — the session ran in this mode; recon arc honestly surfaced 4 mechanism drifts and routed each through Rigby

## Notes for Session 1202 open

1. **Standard FIRST THING checks** still apply (disk, swap, worker freshness, gh PR list, Rigby `platform_config_tool overview` to confirm local).
2. **Daily inference watch starts 2026-06-23 (Day 1)** — append A/B/C/D to `9ba58690-…` per runbook `cb9d8ae1-…`. Independent of the Reality Map work.
3. **Reality Map Initiative `0ecd1bc2-…` is the new investigation anchor.** All 4 child Initiatives + 15 deliverables are linked. The Connectivity Completion Roadmap (`docs/specs/CONNECTIVITY_COMPLETION_ROADMAP.md`) is the sequenced plan to close them.
4. **Recommend Session 1202 Phase A.1 (Initiative-Management tools)** as the FIRST THING after the daily watch — it unblocks Rigby from needing Claude ORM bypass on every Initiative spawn.
