# SESSION 2946 — A6 SignalCluster promotion diversity denominator (5 → 3)

**Closed:** 2026-07-24
**Body commit:** `7be5ee9af` (u-d-b PR #3531, merged `main`)
**Docs cascade:** filled at close

---

## What shipped

**PR #3531** — S2946 A6: `_calculate_strength` diversity_factor denominator from `source_count / 5` to `source_count / 3` in `signal_aggregation_service.py:855`. Aligns with `MIN_CLUSTER_SIZE = 3` already used elsewhere in the file. **Unlocks ~10× SignalCluster promotion rate** (9 active / 870 total = 1.03% → projected ~80–100 active).

Chris picked A6 (SignalCluster promotion audit) as engineering-first first-action from the S2945 deferred queue after plain-English framing of the 5 candidates.

**A6 was framed as "audit" but shipped as a fix.** The audit surfaced a 1-line root cause; Claude+Rigby T1 SIGN converged on Option 1 (denominator /3) over Option 2 (per-pattern floors) on simplicity + reversibility grounds.

## Root cause (raw-ORM verified at HEAD 62ca81bea)

- 838/870 (96%) of SignalClusters decayed or archived without ever becoming actionable.
- **No decayed cluster ever hit ≥4 sources** — max `source_count` across all 527 decayed rows = 3.
- Decayed source distribution: 1 source: 205 / 2 sources: 177 / 3 sources: 145.
- Per-pattern-type decayed avg strength: `demand_spike` 0.347, `trend_emergence` 0.374, `skill_demand` 0.362, `opportunity_window` 0.406. All below 0.5 bar.
- Per-pattern-type decayed avg confidence: 0.449–0.562. **Confidence was not the blocker** (322/527 decayed had conf ≥ 0.5). Strength was.

Naturally-narrow signal types (skill_demand from job spiders like RemoteOK/WeWorkRemotely/GitHub Jobs/Adzuna) cap at ~3 sources structurally. Old `diversity_factor = min(1, source_count/5)` capped at 0.6 for these, so strength never cleared 0.5 bar, cluster decayed at the 48h TTL (`tasks_misc.py:4547`).

## Retrospective lift

153 of 527 historical decayed rows would have promoted under new formula:
- 145 with 3 sources (target cohort — the "you're right below the bar" clusters)
- 8 with 2 sources
- 0 with 1 source (confidence floor holds — single-source noise stays unpromoted)

## Files shipped

- **MODIFIED** `core/services/signal_aggregation_service.py:855` — 1-LOC change + 6-line rationale comment.
- **NEW** `core/tests/test_s2946_diversity_denominator.py` — 7 regression tests.
- **NEW** `docs/research/platform/S2946_A6_diversity_denominator.md` — validation doc.

## Twin mirrors (per `feedback_twin_deliverable_at_every_ratification`)

- Content: `3374ffce-3925-4bcc-a527-e2a9a38f052a` (Architecture & Research, `deliverable_type='initiative_phase_doc'`, `category='initiative_phase_doc'`; diagnostic cleared via ORM per known bug).
- Ratification: `a01ea4f1-5536-49a7-beea-a1a99c2e2107` (Architecture & Research, `deliverable_type='ratification_record'`, `category='governance'`; diagnostic cleared via ORM per known bug).

## Rigby SIGN cycle

**Verdict:** AGREE ship. Non-blocking. Precision guardrail intact (confidence floor unchanged; `source_count < 2 → 0.3` hard floor).

**Zoom-out fold** (per `feedback_zoom_out_ask_per_rigby_sign`): 4 downstream breakpoint categories at 10× active-cluster count:

a) **Agent dispatch / orchestration loops** that iterate all active clusters — Celery load spike risk.
b) **Curated snapshots / newsletter / summarizers** without rank + cap — quality dilution.
c) **UI/API endpoints** without pagination/window filters — payload bloat.
d) **Human attention surfaces** (dashboards, notifications) treating active as "review-worthy" — overwhelm.

Rigby's fix pattern: rank + cap + paginate — not "don't ship the change." Reactive follow-ups if any bite.

## Test coverage

- 7 new tests in `test_s2946_diversity_denominator.py` (all pass)
- 17 adjacent tests (`test_s2862_huggingface_signal_extraction`, `test_s2872_ledger_22b_raw_data_dict_sweep`) — pass, no regression
- 36 downstream signal-dispatch tests (`test_signal_dispatch_service`, `test_s2934_signal_dispatch_harness`) — pass, no regression

## Post-merge live-dispatch (per PLAYBOOK-7.4.4)

- Recycled after PR #3531 merge (`make recycle-all` — clean; workers matched HEAD `7be5ee9af`).
- Live-verified via Rigby prose-only check: `SignalCluster.status='active'` count = 9 (baseline, as expected — going-forward only), workers loaded post-merge = yes, no unexpected activity in 15 min.

## Governance

Same-PR fold: none this session. No new record-only zoom-out candidates.

## Rigby Tool Gap Ledger

No new formal entries. Two known bugs re-hit and re-worked-around via ORM as expected:
- `deliverable_tool.create` marks new deliverables with `diagnostic_status='diagnostic'` and empty `deliverable_type` (per `feedback_pa_deliverables_tool_flags_ratifications_as_diagnostic`).

## Deferred queue additions

- **Rank + cap + paginate follow-ups on Rigby's 4 zoom-out breakpoint categories** — reactive, only ship if a specific consumer bites at post-lift active-count levels. Watch signal_dispatch fire rate, curator snapshot sizes, UI endpoint response times, dashboard density over 24–48h.
- **Option 2 revisit — per-pattern-type diversity floors** — if /3 across the board proves too noisy for `opportunity_window` (natively hits 5+ sources on mega-topics), introduce `PER_PATTERN_DIVERSITY_FLOOR` dict mirroring `PER_PATTERN_MIN_CLUSTER_SIZE`. Watch precision on Iran/Trump/Anthropic-style mega-topics.

## Limitations

- Historical decayed rows are not retroactively promoted. Lift is going-forward only — new spider signals must hit the aggregator with the new /3 semantics.
- No live post-ship monitoring dashboard for Rigby's 4 downstream breakpoints — reactive if any bite.
- Pre-existing pyright drift on `signal_aggregation_service.py` (module-wide) and the new test file. Matches "bundled dev-env drift slate" deferred item; not S2946-introduced.

---

## S2947 first-action

Chris directs. Deferred queue carries forward from S2945 with S2946 additions above; the two obvious next candidates in the same neighborhood are:

- **A8** — "Manual dispatch" button on Signal Dispatches tab (~30 min UI). Now more useful with more active clusters flowing.
- **A9** — 4th signal-dispatch rule (`demand_spike` 250 clusters or `skill_demand` 131 clusters). Directly amplified by S2946 lift.

Or Chris picks something entirely different.
