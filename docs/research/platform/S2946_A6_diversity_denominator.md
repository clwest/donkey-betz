# S2946 — A6 SignalCluster promotion diversity denominator (5 → 3)

**Session:** 2946
**Ratified:** 2026-07-24 (Chris D-verdict after Rigby AGREE + zoom-out fold)
**Files touched:** `core/services/signal_aggregation_service.py:855`, `core/tests/test_s2946_diversity_denominator.py`
**Scope:** 1-line strength-formula change; 7 regression tests; unlocks ~10× active-cluster promotion rate.

---

## 1. Problem

At S2946 open, only **9 of 870 SignalCluster rows (1.03%)** carried status `active` — the gate downstream signal-dispatch, curator, and dashboard consumers use to decide "is this signal worth acting on." **838 (96%) died decayed or archived without ever being usable.**

Root cause (raw ORM verification, HEAD `62ca81bea`):

- **No decayed cluster ever hit ≥4 sources.** Max `source_count` across all 527 decayed rows = 3.
- Decayed source distribution: **1 source: 205 / 2 sources: 177 / 3 sources: 145.**
- Per-pattern-type decayed avg strength: `demand_spike` 0.347, `trend_emergence` 0.374, `skill_demand` 0.362, `opportunity_window` 0.406. All below the 0.5 promotion bar.
- Per-pattern-type decayed avg confidence: 0.449–0.562. **Confidence was not the blocker** — 322/527 decayed rows already had `confidence ≥ 0.5`. Strength was.

The `_calculate_strength` formula at `signal_aggregation_service.py:855` was:

```python
diversity_factor = min(1.0, source_count / 5)
```

Real signals of user value don't naturally cross 5+ spider sources. Skill-demand signals come from job spiders (RemoteOK, WeWorkRemotely, GitHub Jobs, Adzuna) — a naturally-narrow source pool. They can hit lots of signals but structurally cap at ~3 sources. `diversity_factor` stuck at 0.6, strength never cleared 0.5, cluster decayed at the 48-hour TTL (`tasks_misc.py:4547`).

## 2. Fix

Change one number:

```python
# Normalize source diversity (3 sources = 1.0). S2946 A6: was /5;
# dropped to /3 to match MIN_CLUSTER_SIZE. Only 3-source-max
# signal types (skill_demand from job spiders, single-vertical
# demand_spike) can now clear the strength≥0.5 promotion bar.
# Confidence floor still requires 2+ sources so single-source
# noise stays unpromoted.
diversity_factor = min(1.0, source_count / 3)
```

Rationale:

- 3 already matches `MIN_CLUSTER_SIZE = 3` (`signal_aggregation_service.py:44`). "3 sources is the quality floor" is already Rigby's language elsewhere in the same file.
- Precision guardrail unchanged: `_calculate_confidence` (line 866) still requires 2+ sources for `conf ≥ 0.5` (`source_count < MIN_SOURCES_FOR_CONFIDENCE` returns 0.3 hard floor).
- Single-source noise stays unpromoted end-to-end — confidence gate is independent of strength gate.

## 3. Quantified lift

Retrospective ORM analysis against existing decayed rows (going-forward proxy; existing rows are not retroactively promoted):

- **153 of 527 decayed clusters** would have cleared both `strength ≥ 0.5` and `confidence ≥ 0.5` under the new formula.
- Breakdown by `source_count`: **145 with 3 sources**, 8 with 2 sources, 0 with 1 source (confidence floor holds).
- Projected steady-state active count: **~80–100** (~10× current 9).

## 4. Regression coverage

`core/tests/test_s2946_diversity_denominator.py` — 7 tests, all pass:

1. `test_three_sources_hits_full_diversity_factor` — core S2946 invariant. Locks strength=0.62 for 3-source/6-signal/relevance=50 cluster.
2. `test_two_sources_still_below_bar_at_low_signal_count` — precision guardrail. 2-source thin clusters stay sub-threshold.
3. `test_single_source_diversity_factor_matches_third` — 1-source diversity_factor = 0.333 (still below strength bar).
4. `test_diversity_factor_caps_at_1` — min-clamp preserved for 4+ sources.
5. `test_confidence_floor_still_blocks_single_source` — confidence gate unchanged.
6. `test_promotion_gate_requires_both_strength_and_confidence` — end-to-end: strength lift alone can't promote single-source clusters.
7. `test_three_source_low_relevance_still_promotes` — the target cohort (145 formerly-decayed rows) now cleanly promotes.

Adjacent regression: 17 pre-existing tests in `test_s2862_huggingface_signal_extraction.py` + `test_s2872_ledger_22b_raw_data_dict_sweep.py` still pass. 36 downstream tests in `test_signal_dispatch_service.py` + `test_s2934_signal_dispatch_harness.py` still pass.

## 5. Rigby SIGN cycle

**Verdict:** AGREE ship. Non-blocking. Precision protected by confidence floor.

**Zoom-out fold** (per `feedback_zoom_out_ask_per_rigby_sign`): 4 downstream breakpoint categories at 10× active count:

a) **Agent dispatch / orchestration loops** that iterate all active clusters and spawn agent work per cluster — Celery load spike risk.
b) **Curated snapshots / newsletter / summarizers** that don't rank + cap — quality dilution.
c) **UI/API endpoints** without pagination/window filters — payload bloat.
d) **Human attention surfaces** (dashboards, notifications) treating "active" as "review-worthy" — overwhelm.

Rigby's fix pattern: rank + cap + paginate — not "don't ship the change." Follow-ups are reactive.

## 6. Limitations

- Historical decayed rows are not retroactively promoted. Lift is going-forward only.
- Pre-existing pyright drift on `signal_aggregation_service.py` (module-wide) and the new test file (untyped `_signals` helper + untyped `_calculate_strength` return). Matches the "bundled dev-env drift slate" deferred item in `00-START-NEXT-SESSION.md`; not S2946-introduced.
- No live post-ship monitoring dashboard for the 4 downstream breakpoints — reactive if any bite.
