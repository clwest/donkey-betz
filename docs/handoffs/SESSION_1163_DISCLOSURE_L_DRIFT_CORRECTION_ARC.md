---
originating_session: 1163
provenance_confidence: HIGH
provenance_note: Hand-authored Session 1163 handoff. Four PRs merged in one session covering the full corpus-walk → drift-discovery → C-style honest interim → B-style correct fix arc on Disclosure L. Session started with an apparent quick-PR list (the four self-tuning follow-on items the Session 1162 narrative §6 surfaced) and turned into a substantive drift correction when mid-recon discovered the patent's as-built §5 Component 4 mechanism was aspirational rather than built. Captured one new feedback memory + one new dogfood-loop lineage example. Session ran ~3 hours from open to close including parallel Rigby review at every step.
---

# Session 1163 — Disclosure L drift correction arc (C-style + B-style)

**Date:** 2026-05-26 (rolled into 2026-05-27 during the late B-style cycle verification)
**Branch state at session close:** All work merged. Main is clean. Four PRs landed.

---

## TL;DR

Session 1163 turned a planned cleanup PR (Disclosure L path-move addendum) into a four-PR arc closing a substantive mechanism drift between Patent Disclosure L §5 Component 4 (`FinalAppliedOverrides.objects.create(...)` with per-cycle history) and as-built code (single-row `SystemConfiguration` overwrite, no history). The corpus walk surfaced the drift; the C-style honest interim PR documented it; the B-style correct fix PR closed it. Rigby ratified at every step; Chris green-lit each merge.

The four PRs:

| PR | Theme | SHA | Merge |
|----|------|-----|-------|
| **#2283** | Disclosure L §13 — path-move addendum (PolicyOptimizer/PolicyArbitrator/ExperimentEngine class definitions moved `core.py` → `governance.py` + `experiment.py` per commit `fe94c928` 2026-03-09) | `9bf87f4e` | morning |
| **#2284** | `latest_overrides_snapshot` C-style honest interim PA tool + Disclosure L §14 mechanism drift addendum + narrative §6.4 correction + nit-fix commit (row_updated_at freshness field) | `dad9ec84` | afternoon |
| **#2285** | Narrative §6.4 tool-name drift fix — `ops_tool` → `autopilot_tool` (caught by Rigby's post-merge smoke test of #2284) | `b99bfa0c` | afternoon |
| **#2286** | B-style `FinalAppliedOverrides` per-cycle table + idempotent backfill + time-travel `at` arg + 90-day Celery beat retention + Disclosure L §14.7 "B-style shipped" + narrative §6.4 lineage table | `636ed6c7` | late afternoon |

End-to-end verification post-merge:
- 2 autopilot cycles ran (cycle_ids `b1e83041-...` @ 22:05:55 + `8b6af738-...` @ 22:07:24).
- `latest_overrides_snapshot at='2026-05-27T22:05:56+00:00'` correctly returned the older row.
- `latest_overrides_snapshot` (no `at`) correctly returned the newer row.
- 14 knobs populated in each snapshot (real data: `backlog_governor_level`, `desk_allocation:*`, `goal_allocation:*`).

---

## What shipped

### PR #2283 — Disclosure L §13 path-move addendum

**Surface:** `docs/patents/DISCLOSURE_L_SELF_TUNING_EXPERIMENTATION.md` §13.1–§13.5.

**Why:** Disclosure L (drafted 2026-03-16) cited `core/services/ops_autopilot/core.py` line ranges for `PolicyOptimizer` (1224-1328) + `ExperimentEngine` (1693-1746) + `PolicyArbitrator` (2643-2706). Commit `fe94c928` (2026-03-09, *7 days before* the disclosure) had already split `ops_autopilot.py` into the package, moving class definitions to `governance.py` + `experiment.py`. The disclosure cited pre-refactor paths from day one.

**What:** Appended §13 (5 subsections) with current canonical class locations (verified at HEAD `1b10f361`) + cycle wrapper current line spans + frozen-artifact convention preservation + future drift policy ("append §13.6+, never edit §5 inline"). Frontmatter `maps_to_narratives` updated to point at the operator-facing narrative.

**Rigby ratified the tone-softening** (Option A wording over the original "7 days post-refactor" framing, which read as implicit blame).

### PR #2284 — `latest_overrides_snapshot` C-style tool + §14 + narrative §6.4

**Surface:** New PA tool action + Disclosure L §14 + narrative §6.4 rewrite.

**Why:** Recon for the planned `final_overrides_at(time)` tool surfaced a deeper drift than §13. The patent §5 Component 4 mechanism (`FinalAppliedOverrides.objects.create(cycle_id, cycle_ts, knob_count, applied_values)`) and the narrative §6.4 ORM recipe (`filter(cycle_ts__lte=t).order_by('-cycle_ts').first()`) were both invalid as written. Verified: no Django model with that name; snapshots stored as a single overwritten `SystemConfiguration(key='policy_arbitrator_snapshot')` row.

**Decision call (per Rigby + Chris):** C-style honest interim (ship tool against the as-built mechanism, document drift), B-style queued for follow-on. A-style ("ship as-designed, ignore the `t` arg") rejected as building a tool that implicitly lies.

**What shipped:**
- `PolicyArbitrator.get_latest_snapshot()` method reading the single overwritten row with explicit `storage.mechanism: "single-row overwrite per cycle (no per-cycle history)"` block.
- `autopilot_tool action=latest_overrides_snapshot` PA tool action.
- 5 unit tests (no-row null, row-exists parse, corrupt JSON degrade, storage-context honest framing, dispatcher action label).
- Disclosure L §14 addendum (6 subsections) — including §14.3 counsel call on claim §10(g) ("for time-series auditability" arguably not satisfied by single-row overwrite).
- Narrative §6.4 rewrite (original framing preserved as historical context + "Session 1163 correction" subsection).
- Narrative §2 vocabulary entry + §3 Milestone 4 mechanism-drift flag.

**Nit-fix commit `4d7e3dab`:** added `row_updated_at` field to the response payload (Rigby's nit — freshness affordance for callers asking "is this stale?"); synced §14.2 line number reference (record_overrides_snapshot drifted 9 lines from `1607` → `1616` after the new method was inserted above).

### PR #2285 — `ops_tool` → `autopilot_tool` tool-name fix

**Surface:** One-line correction to narrative §6.4 + INDEX regen.

**Why:** PR #2284's post-merge smoke test caught a tool-name drift in the narrative. The new action lives on `autopilot_tool` (schema at `pa_tool_schemas.py:2569` + handler in `_handle_autopilot`), but the narrative described it as "`latest_overrides_snapshot` (ops_tool) returns the…". Rigby's `ops_tool action=latest_overrides_snapshot` invocation returned "Unknown ops_tool action"; `autopilot_tool action=latest_overrides_snapshot` worked correctly.

**Self-referential dogfood loop:** Same pattern as Session 1159 #2256 → #2257 (the EDITING_GUARDRAILS-introducing PR violated its own rules). PR #2284 introduced the C-style honest-tool pattern and shipped with a mislabeled tool namespace. The dogfood loop is captured in the commit message as a future-Claude warning.

**Fix:** Single-line edit. The "(ops_tool)" parenthetical now reads "(autopilot_tool — verified via Rigby smoke test 2026-05-26 post-merge; the action lives on the `autopilot_tool` schema at `core/services/pa_tool_schemas.py:2569`, not `ops_tool`)". The "verified via Rigby smoke test" anchor pins the source of truth.

### PR #2286 — B-style `FinalAppliedOverrides` per-cycle table

**Surface:** New Django model + migration + writer change + reader extension + PA tool `at` arg + 90-day retention beat task + narrative §6.4 lineage table + Disclosure L §14.7.

**Why:** Close the mechanism drift §14 documented. Build the per-cycle history mechanism the patent §5 Component 4 originally described.

**What shipped:**

- `core/models_final_applied_overrides.py` — `FinalAppliedOverrides(cycle_id UUID unique, cycle_ts DateTimeField db_index, knob_count IntegerField, applied_values JSONField, created_at auto_now_add)`. `Meta.indexes` adds `fao_cycle_ts_desc` btree on `-cycle_ts`. Default ordering `-cycle_ts`.

- `core/migrations/0354_session_1163_b_final_applied_overrides.py` — hand-written focused migration (rejected the 606-line auto-generated scope-creep that included unrelated `AlterField` ops across multiple subsystems). `CreateModel` + `AddIndex` + idempotent `RunPython` backfill that copies the legacy `SystemConfiguration(key='policy_arbitrator_snapshot')` row into one `FinalAppliedOverrides` row if (a) the new table is empty AND (b) the legacy row exists. Reverse migration is no-op by design.

- `PolicyArbitrator.record_overrides_snapshot()` (governance.py) — now calls `FinalAppliedOverrides.objects.create(cycle_id, cycle_ts=now, knob_count, applied_values=snapshot)` once per cycle. Removed the legacy `SystemConfiguration.update_or_create` write entirely.

- `PolicyArbitrator.get_latest_snapshot(at=None)` — extended signature. Without `at`: `order_by('-cycle_ts').first()`. With `at` (datetime OR ISO 8601 string via `django.utils.dateparse.parse_datetime`): `filter(cycle_ts__lte=at).order_by('-cycle_ts').first()`. Unparseable ISO strings fail loud (`found=False` + explainer note quoting the bad arg). Storage block reads `{model: FinalAppliedOverrides, table: core_final_applied_overrides, mechanism: "append-only per-cycle row (90-day retention)"}`.

- `pa_tool_schemas.py` — `latest_overrides_snapshot` description rewritten to describe the `at` arg + time-travel semantics + 90-day window. New `"at"` parameter in the `autopilot_tool` parameters block.

- `td_handlers_ops.py` — handler passes `payload.get('at')` through to the reader.

- `core/tasks.py` — new `@shared_task purge_finaloverrides_older_than_90d`. Hard-deletes rows where `cycle_ts < now - 90d`. Returns `{deleted: int, retention_days: 90}`.

- `core/celery.py` — beat schedule entry `purge-finaloverrides-90d` (daily 02:40 MST, offset from 02:10 + 02:25 fleet cleanups). Per memory rule "Observation cadence belongs in Celery beat, not OS cron."

- Tests: 11/11 pass in 0.143s. Coverage: latest-only, time-travel between rows, time-travel before first row, ISO string parsing, unparseable-`at` fail-loud, storage context, writer append-only, dispatcher pass-through, retention purge boundary.

- Narrative §6.4 rewritten as a lineage table (Session 1162 framing → Session 1163 discovery → C-style interim → B-style shipped). §2 + §3M4 + provenance note updated.

- Disclosure L §14.7 "B-style storage shipped" subsection records the as-built state + de-escalates the §14.3 counsel call from "amendment-to-match-reality" to "amendment-to-strengthen". Backfill provenance recorded for future patent archeology. §1–§13 + §14.1–§14.6 byte-identical to pre-PR.

---

## Post-merge verification (cross-PR)

After PR #2286 merged + `make restart`:

1. **`autopilot_tool action=latest_overrides_snapshot`** (no `at`) — `found: false` (no autopilot cycle had run yet to write a row).
2. **`autopilot_tool action=latest_overrides_snapshot at='2026-05-26T19:00:00+00:00'`** — `found: false`, `queried_at` echoed correctly.
3. **`autopilot_tool action=latest_overrides_snapshot at='not-a-datetime'`** — `found: false`, fail-loud note ("Could not parse `at` argument…").
4. **`autopilot_tool action=run dry_run=false`** — triggered cycle `2937373c-...` @ 22:05:55.
5. **`autopilot_tool action=latest_overrides_snapshot`** (no `at`, post-cycle) — `found: true`, `cycle_id: b1e83041-...`, `cycle_ts: 2026-05-27T22:05:55.211092+00:00`, `row_created_at: 22:05:55.764502+00:00` (553ms after `cycle_ts` — Django row mtime vs payload capture-time divergence as expected), `knob_count: 14`, knobs populated with real data.
6. **Second cycle triggered.** Two rows now in `core_final_applied_overrides`.
7. **`autopilot_tool action=latest_overrides_snapshot at='2026-05-27T22:05:56+00:00'`** — returned the older row (`b1e83041-...` @ 22:05:55). Correct: `at` is between the two cycles, `cycle_ts__lte` selects the prior row.
8. **`autopilot_tool action=latest_overrides_snapshot`** (no `at`, post-second-cycle) — returned the newer row (`8b6af738-...` @ 22:07:24).

End-to-end time-travel is verified working against real data.

---

## New gotchas captured

### `cycle_id` mismatch between cycle wrapper + arbitrator

The arbitrator's `_policy_policy_arbitrator` wrapper at `core.py:2658` generates its OWN `cycle_id = _uuid.uuid4()` independent of the broader cycle wrapper's tracking ID. So the snapshot's `cycle_id` is the arbitrator's, not the run-cycle's. The run-cycle output from `autopilot_tool action=run` shows one UUID; the resulting `FinalAppliedOverrides` row carries a different one.

This is a minor design wart (the two should arguably share an ID for joinability against `AutopilotAction` records from the same cycle) but not a B-implementation bug. Queued as a future cleanup candidate.

### Corpus walks SURFACE mechanism drift (new feedback memory)

Saved to `feedback_corpus_walks_surface_mechanism_drift.md` + indexed in `MEMORY.md`. Chris's in-session value statement after the FinalAppliedOverrides discovery: *"This is why it's so important for us to go through all of the /docs/ like we have been doing, that's how we surface these issues!!"* Finding drift is intended workflow output, not an interruption. The C-style honest-tool + frozen-artifact-addendum + B-style correct-fix pattern is now a documented playbook for similar discoveries.

### Self-referential dogfood loop — corrective PRs can introduce their own drift

PR #2284 corrected the narrative §6.4 to be honest about `FinalAppliedOverrides` not existing — and in the correction, named the wrong tool namespace (`ops_tool` instead of `autopilot_tool`) for the C-style tool it shipped. Caught immediately by Rigby's post-merge smoke test, fixed in PR #2285. Same lineage as Session 1159 #2256 → #2257 (the `EDITING_GUARDRAILS`-introducing PR violated its own rules).

The 00-START line 78 rule applies: *"if the PR introduces a new rule/process, dogfood the rule on its own diff before opening."* For corrective PRs that introduce new tool surfaces, the dogfood step is: invoke the tool you just shipped against your own docs before merge, not after.

---

## Carryover into Session 1164

### Queued small follow-ons from Session 1163

1. **Legacy `SystemConfiguration(key='policy_arbitrator_snapshot')` row cleanup** — small migration to hard-delete the legacy row after one or more new-model cycles have been observed. Per Rigby's "Pick (b) backfill + (c) cleanup later" recommendation. Local has 2 new-model cycles observed; prod has 0. Queue for after Railway has seen ≥ 1 cycle.

2. **`cycle_id` joinability fix** — make `_policy_policy_arbitrator` accept the run-cycle's `cycle_id` instead of generating its own UUID. Minor cleanup; would make `FinalAppliedOverrides.cycle_id` joinable against `AutopilotAction` records emitted in the same cycle. Single-file edit in `core.py`.

3. **Counsel-side amendment to Disclosure L claim §10(g)** — now optional (de-escalated per §14.7). Not a code change; counsel call.

4. **Opportunistic narrative §4 + §5 cleanup of stale `FinalAppliedOverrides` mentions** — per EDITING_GUARDRAILS rule 4 (migration is opportunistic, not batch). §6.4 lineage table is the canonical correction source; §4 (operational benefits — "Time-travel auditability") and §5 (current state snapshot) still describe `FinalAppliedOverrides` as if it were a snapshot model with the pre-Session-1163 framing. Wait for the next time someone touches those sections.

### Session 1162 carryover items still in queue

5. **STRATEGY correction PR** (#3) — `LLMCallLog.workspace` FK + fleet "scoped workspace bootstrap" both named as implemented in STRATEGY narrative but aren't. Convert "is" → "planned / not yet implemented."

6. **TRIAGE policy PR** (#5) — opt-in archive rule OR review-queue surfacing for stale TRIAGE initiatives.

7. **Threshold tuning** (#7) — fold `pa_acks_health` action thresholds into `_compute_status()`. Gated on 24h+ clean JSONL data. The cadence has been running since Session 1161 (2026-05-26 ~10:47 AM CDT); by 2026-05-27 noon-ish there should be 24h+ of clean data. Becomes actionable as of Session 1164.

8. **Per-module `ops_autopilot` narratives** (#8) — `SELF_TUNING_AND_EXPERIMENTATION.md` §6.3 scoped out the other 7 ops_autopilot files. Each is a future-narrative candidate.

9. **UI spinner proxy** (#9) — confirm `ChatConversation` shape first; implement as `pa_acks_health` field or separate tool action.

### Older queue items (Chris's call)

10. **Old `docs/topics/` sweep** — 7 Feb-March docs deferred from Session 1147 #2221.
11. **`load_all_agents_advisors.py 149→139` cosmetic fix** — queued from Session 1149.

### Deferred infrastructure track

12. **`celery-beat-schedule` CONFLICT detector tuning** — same as Session 1162 carryover.
13. **PeriodicTask drift** (still 81 DB rows vs 79 entries in `core/celery.py` — Session 1163 added 1 beat entry `purge-finaloverrides-90d`).
14-17. **As Session 1162 carryover** — `exists_on_disk` flag, beat-schedule the regens, `build_learning_bridge_audit.py` generator, Redis pooling sweep.

### Chris-call-only carryovers (still parked)

18–20. **Decision Command backend cleanup / DaVinci route removal / Mission refresh PR #2190** — unchanged from Session 1162.

---

## Active issues unchanged from 1162

1. **GitHub Actions billing — still down** (multi-day outage).
2. **`celery-beat-schedule` CONFLICT** — detector signal pending; code-level fix shipped Session 1157 PR #2243.
3. **PA `acks_late=False` observation phase** — fully instrumented per Session 1161 + 1162. JSONL cadence running; Session 1164 entry-check picks up the 24h+ clean-data milestone.

---

## Numbers

- 4 PRs merged (#2283, #2284, #2285, #2286).
- ~1,400 lines of code + docs changed (843 + 269 in #2286 alone).
- 11 unit tests added (all pass in 0.143s).
- 1 new Django model + 1 migration + 1 new `@shared_task` + 1 new beat schedule entry.
- 1 new PA tool action (`latest_overrides_snapshot`) with optional `at` arg.
- 2 cycles run end-to-end to verify time-travel selection.
- 2 disclosure addenda (§13 + §14 + §14.7 added in this session; original §1–§12 byte-identical).
- 1 new feedback memory (`feedback_corpus_walks_surface_mechanism_drift.md`).

---

## Session lessons

- **The corpus walk is the deliverable.** Chris's "this is why we go through all of /docs/" statement is now memory. Drift surfacing is intended output, not a scope-blow obstacle.
- **C-style honest interim ≠ A-style fake.** A C-style PR ships an honest small surface that doesn't lie about capabilities. An A-style PR ships a tool that pretends to support something it doesn't. Always C, never A.
- **Frozen-artifact convention scales.** §13 + §14 + §14.7 added without editing §1–§12. Future patent disclosures with similar drift can follow the same pattern.
- **Self-referential dogfood loops continue.** PR #2284 introduced a tool surface and got the tool name wrong in its own docs. Same family as #2256 → #2257. The 00-START dogfood rule should include "if your PR introduces a tool surface, invoke the tool before merge."
- **Hand-written migrations beat auto-generated when scope matters.** `makemigrations` produced a 606-line migration; the focused hand-written one was 168 lines. The auto-generated version would have bundled unrelated subsystem migrations (Narrative, NarrativeShift, etc.) into the same PR.
- **Idempotent backfills are cheap insurance.** The migration's `if FinalAppliedOverrides.objects.exists(): return` check makes re-running the migration safe and turns the backfill into a one-shot no-op if rows already exist.
- **`session-NNNN` commit subject tag** maintained across all four PRs (`feat(session-1163-ops): ...`, `docs(session-1163): ...`). Streak from 1145-1162 continues.
- **Rigby ratification at every step paid off.** Every PR landed with Rigby's explicit "no further changes requested." The nit-fix commit on #2284 (row_updated_at) was Rigby-suggested. The dogfood loop catch (PR #2285) was Rigby's post-merge smoke test. The B-style design Qs (retention + payload + backfill) were Rigby-formulated. This is the "ACTUALLY collaborate with Rigby" memory rule working as intended.

---

## What to read first in Session 1164

1. `00-START-NEXT-SESSION.md` — the entry-check + queue.
2. This handoff for the Session 1163 arc summary.
3. `docs/narratives/SELF_TUNING_AND_EXPERIMENTATION.md` §6.4 — the canonical lineage of the C→B fix (and the reading path for any operator debugging future autopilot snapshots).
4. `docs/patents/DISCLOSURE_L_SELF_TUNING_EXPERIMENTATION.md` §14.7 — the patent-side ramifications.
5. `feedback_corpus_walks_surface_mechanism_drift.md` — the new memory rule the session validated.
