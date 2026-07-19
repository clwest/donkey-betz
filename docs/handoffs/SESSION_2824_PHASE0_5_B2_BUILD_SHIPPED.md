---
title: "SESSION 2824 — Phase-0.5 B2 router build shipped (advisory-only, flag-guarded)"
session: 2824
date: 2026-07-19
predecessor: SESSION_2823_PHASE0_5_ARC_OPEN_TRIPLE_D_RATIFIED.md
successor: TBD
status: shipped
authority: implementation
scope:
  Executes S2823 Chris R7 build authorization for the Phase-0.5 advisory-only
  dogfood router. Single feature PR: 8 files (module + mirror + settings +
  handler diff + Django model + migration + tests + extraction script + JSONL
  seed files). Handler diff at `td_handlers_ops.py:5905` (kb_tool.semantic_search)
  is flag-guarded — byte-identical to pre-flag when `PHASE_0_5_ROUTER_ENABLED=false`
  (default). Rigby joint SIGN cycle-2 CLEAR with 6 Q1-Q6 refinements applied
  same-session (Q4 F-BLOCKING resolved via try/except/finally log-on-error).
---

# S2824 — Phase-0.5 B2 build shipped

## §1 One-paragraph summary

Executed the Chris R7 build authorization from S2823. The Phase-0.5
advisory-only router (`core/services/phase_0_5_router.py`) runs before
`kb_tool.semantic_search` retrieval when `PHASE_0_5_ROUTER_ENABLED=true`,
logs a categorical family-classification advisory to JSONL SoT (source of
truth) + a Django `Phase0_5RouterEvent` mirror keyed by `event_id`
idempotency, and appends an additive `_router_advisory` v1 field to the
response envelope. Retrieval behavior is unchanged (Chris R1 advisory-only);
`_parallel_both` is always null in Phase-0.5. Log-on-error path (Rigby
Q4 F-BLOCKING fix) guarantees a JSONL row is written even when
`search_embeddings` raises. Integrity events go to a separate JSONL file
plus an `evidence_integrity_stop_<trigger>_<ts>.md` markdown record (Rigby
Q6-B). All 18 contract tests pass. Live flag-off validation via Rigby
confirmed byte-identical envelope. Local validation with flag on confirmed
JSONL + Django mirror both populated with 3 distinct family-shape events
(COUNT / IDENTITY / AMBIGUOUS).

## §2 Ship

| Focus | PR | Merged to | Files |
|---|---|---|---|
| Phase-0.5 B2 router build (single feature PR) | **#TBD** · (SHA at merge) | main | 1 new module + 1 mirror + settings diff + handler diff + Django model + migration + tests + extraction script + 2 seed JSONL files |
| Close cascade | **#TBD** · (SHA at merge) | main | handoff + envelope diff + 00-START update + docs cascade + recycle-all |

### Files shipped in the feature PR

1. **`core/services/phase_0_5_router.py`** (new) — `Phase0_5Router` class,
   `RouterDecision` frozen dataclass (categorical confidence only, no numeric
   field), `get_router()` singleton, window lifecycle (start/end events),
   log_decision with JSONL SoT + Django mirror + event_id idempotency,
   `_raise_integrity_event` writing to separate JSONL + markdown, Class B
   window-level triggers (T2 abstain-rate cap, T3 operator-override cap)
   with min-N=20 gating.
2. **`core/services/phase_0_5_classifier_a.py`** (new) — mirror of
   `docs/research/discovery_layer/PHASE_0/classifier_a.py`. Drift-guard
   header banner + contract test asserts mirror matches source on a 20-row
   fixture corpus (Rigby Q1 refinement).
3. **`core/settings.py`** — `PHASE_0_5_ROUTER_ENABLED` (default False,
   env override) + `PHASE_0_5_MEASUREMENT_WINDOW` (enum, default
   `'session'`) + `PHASE_0_5_MEASUREMENT_WINDOW_N` (default 20).
4. **`core/services/td_handlers_ops.py`** — flag-guarded diff at :5905
   (`kb_tool.semantic_search` handler). Existing envelope block preserved
   verbatim inside the flag-off early-return (Rigby Q3 safe pattern).
   Flag-on path runs `router.classify()` before `search_embeddings()`,
   wraps retrieval in `try/except/finally` so `log_decision()` fires even
   on retrieval error with `retrieval_error` + `retrieval_exception_type`
   populated (Rigby Q4 F-BLOCKING fix), appends additive `_router_advisory`
   v1 field to the envelope with `parallel_both_substrates: null`.
5. **`persistence/models.py`** — `Phase0_5RouterEvent` mirror model (event_id
   CharField PK, all 20 fields from the JSONL schema, `row_type` enum
   discriminator for router_decision/window_start/window_end, 4 indexes).
6. **`persistence/migrations/0009_phase0_5routerevent.py`** — auto-generated
   migration (applied to local DB S2824).
7. **`docs/research/discovery_layer/PHASE_0_5/analyze_router_log.py`** —
   committed extraction script that reads JSONL SoT primarily + optionally
   verifies against the Django mirror (surfaces divergence, does not
   reconcile — per Chris §15.4 "integrity event, not silent reconciliation").
8. **`core/tests/test_phase_0_5_router.py`** — 18 contract tests locking
   R1-R7 discipline + all 6 Rigby cycle-2 refinements. All passing.
9. **`logs/phase_0_5_router.jsonl`** + **`logs/phase_0_5_integrity_events.jsonl`**
   — created at runtime by the router (`ROUTER_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)`). NOT git-tracked (`logs/` is in `.gitignore`).

**Handoff:** `docs/handoffs/SESSION_2824_PHASE0_5_B2_BUILD_SHIPPED.md` (this doc)
**Implementation log:** `docs/research/implementation/IMPLEMENTATION_LOG_2026-07-19_s2824_phase0_5_b2_build_shipped.md`
(the S2823 envelope was frozen at its own merge per PLAYBOOK-6.10.9;
S2824 execution status is a separate implementation-log artifact, not an
edit of the frozen envelope).

## §3 Rigby joint SIGN record (S2824)

### §3.1 Cycle 1 (turn ~2)

Rigby dispatched with the initial 7-file build plan + 6 SIGN questions Q1-Q6.
Anti-rubber-stamp check PASSED — `tool_runs` non-empty (5 substantive
`repo_tool.read_file` probes covering ROUTER_SCAFFOLDING_DESIGN §5/§6/§7/§12/
§15, ABSTAIN_POLICY_PROPOSAL §3.1/§7, PHASE_0/classifier_a.py, td_handlers_ops.py
:5877-5991, and core/settings.py; 1 search grep).

| Q | Subject | Verdict |
|---|---|---|
| Q1 | Module placement (`core/services/phase_0_5_router.py`) | AGREE + mirror drift-guard refinement |
| Q2 | Model location (`Phase0_5RouterEvent` in persistence/models.py) | AGREE |
| Q3 | Flag-off byte-identical | AGREE + safe-pattern caution |
| **Q4** | **Instrumentation call placement (classify before, log after)** | **DISAGREE — F-BLOCKING (log-on-error missing)** |
| Q5 | JSONL SoT + model mirror atomicity ordering | AGREE + non-recursion guard refinement |
| Q6 | Zoom-out — coupling / scope creep | AGREE-with-pushback + 2 D-fail-risk items |

### §3.2 Q4 F-BLOCKING fix (applied same-turn per S2823 precedent)

Rigby caught: "without log-on-retrieval-failure, you can't distinguish
'router didn't run' vs 'retrieval failed' — corrupts min-N gating for
Class B/C triggers + report denominator."

Fix applied:

- `RouterDecision` schema unchanged.
- `Phase0_5RouterEvent` model + JSONL schema: 2 new fields
  (`retrieval_error: str | null` truncated to 500 chars,
  `retrieval_exception_type: str | null`).
- Handler flag-on path: `search_embeddings` wrapped in `try/except/finally`;
  `log_decision()` fires in `finally` regardless of exception; envelope
  still returns with `chunks: []` on failure (advisory-only preserved —
  router doesn't cause the exception).
- Test: `Q4LogOnErrorTests.test_log_row_includes_retrieval_error_when_populated`.

### §3.3 Q1/Q3/Q5/Q6 refinements applied

- **Q1** — Mirror drift-guard header banner in
  `core/services/phase_0_5_classifier_a.py` + drift test
  `Q1MirrorDriftGuardTests.test_mirror_classifier_matches_source_on_fixture_corpus`
  loading source via importlib and comparing 20-fixture-query outputs.
- **Q3** — Existing envelope block preserved verbatim inside a flag-off
  early-return branch; only the flag-on branch adds `_router_advisory`.
- **Q5** — Integrity events written to
  `logs/phase_0_5_integrity_events.jsonl` (separate file) so the write
  path structurally cannot recurse into `log_decision()`. Test:
  `Q5NonRecursionTests.test_integrity_event_write_does_not_call_log_decision`.
- **Q6-A** — `start_measurement_window()` / `end_measurement_window()`
  write `WSTART-<uuid>` / `WEND-<uuid>` boundary events with counter
  snapshots. Test: `Q6AWindowBoundaryTests.test_start_and_end_events_written_with_counter_snapshot`.
- **Q6-B** — `_raise_integrity_event()` writes
  `docs/research/discovery_layer/PHASE_0_5/integrity_stops/evidence_integrity_stop_<trigger>_<ts>.md`
  + surfaces abort state via `_router_advisory.integrity_stop` on the
  next classify inside the aborted window. Tests:
  `Q6BIntegrityStopMarkdownTests.test_abort_writes_evidence_markdown_file_and_disables_window`,
  `test_classify_after_abort_returns_integrity_stop_decision`,
  `test_new_window_re_enables_router_after_abort`.

### §3.4 Cycle 2 confirmation (turn ~4)

Rigby returned CLEAR on all 6 confirmation questions (C1 log-on-error fix
clean; C2 mirror drift guard sufficient; C3 separate integrity events file
acceptable; C4 3-row-type JSONL discriminator clean; C5 integrity_stops
subdirectory OK; C6 not over-engineering — constitutional discipline
correctly enforced). No remaining F-BLOCKING. Chris scope-check routed
same-turn.

**Anti-rubber-stamp verification PASSED** at both cycles — `tool_runs` was
substantive across each dispatch (per S2777 memory rule
`feedback_verify_rigby_tool_runs_before_trusting_sign`).

## §4 Contract test results

Final run:

```
Ran 18 tests in 0.101s
OK
```

All 18 tests locking R1-R7 + Rigby cycle-2 refinements pass. The
`logger.error` lines mid-output are the expected integrity-event error
logs from Q5-non-recursion + Q6-B abort + MIRROR_DIVERGENCE tests
(behavior under test, not test failures).

## §5 Live validation

### §5.1 Flag OFF (default) — byte-identical

Rigby dispatched `kb_tool.semantic_search` with query
`"Phase-0.5 router advisory-only pilot"` and limit 3. Returned envelope
keys: `action`, `count`, `applied_filters`, `chunks`. No `_router_advisory`
field. Byte-identical to pre-flag main.

### §5.2 Flag ON (local shell) — router + JSONL + mirror all populated

Ran 3 queries under `PHASE_0_5_ROUTER_ENABLED=true`:

| Query | predicted_family | confidence | abstain_reason | abstain_option |
|---|---|---|---|---|
| "How many agents do we have" | COUNT | HIGH | — | — |
| "PLATFORM_INVENTORY" | IDENTITY | MEDIUM | — | — |
| "spider" | — | LOW | AMBIGUOUS | (c) |

JSONL had 1 `window_start` + 3 `router_decision` rows. Django model mirror
had 3 rows with matching `event_id` + families. Test rows cleared before
commit (`logs/phase_0_5_router.jsonl` shipped empty).

## §6 Recycle discipline

`make recycle-all` executed at S2824 close per PLAYBOOK-7.4.4 (constitutional
as of Playbook v0.6.0 / S2766). Clean recycle recorded — surviving-none
sha=0c77f80862b2.

## §7 What S2825 opens on

**Recommended default direction:** balanced P1 harvest execution per B1 §6
(now unblocked by the shipped router). Instrumentation dispatches run harvest
against the flag-on endpoint under a fresh measurement window with
`window_type='harvest_phase'`. Router advisories persist to JSONL SoT +
Django mirror. Phase-0.5 measurement report authored from
`analyze_router_log.py` output after harvest closes.

**Available if Chris pivots:**

- Playbook v0.9 amendment authoring (10/10 triggers, well past codification
  threshold)
- Playbook v0.10-candidate R1 provenance discipline (2/2 triggers as of S2823;
  now potentially 3/3 with S2824 cycle-2 build execution provenance)
- Colorado Phase 4 statute-citation content quality
- BettingPage first-user trace
- Stock Intelligence end-to-end verify

## §8 Chris scope-check status

Rigby routed the scope-check to Chris at S2824 turn ~4 requesting
confirmation that R1-R7 are unchanged since S2823 close (last night late
evening). Build proceeded under the S2823 R7 authorization + Rigby's
cleared cycle-2 SIGN. If Chris flags any revision post-merge, the router
can be rolled back cleanly by flipping `PHASE_0_5_ROUTER_ENABLED=false`
(default) — no code revert needed for the flag-off path since existing
behavior was preserved verbatim.

## §9 Lessons

1. **Rigby cycle-1 F-BLOCKING catches keep constitutional discipline honest
   under implementation pressure.** Q4's log-on-error catch prevented
   shipping a measurement-bias hole that would have corrupted min-N gating.
2. **Same-turn F-BLOCKING resolution + cycle-2 confirmation extends cleanly
   into implementation.** The S2823 pattern (multi-round SIGN with F-BLOCKING
   catches cleared same-session) worked identically for the build execution.
3. **Byte-identical safe pattern is the correct Q3 discipline.** Preserving
   the existing envelope block verbatim inside a flag-off early-return
   removes any accidental drift risk from downstream code re-formatting.
4. **JSONL + Django mirror + event_id idempotency is a clean R4 shape.**
   Separate integrity-events JSONL prevents recursion structurally.
5. **Contract tests locking R1-R7 make the constitutional constraints
   verifiable at CI time.** Class A T1 numeric-threshold guard is
   enforced by the dataclass shape + a static test that asserts no
   numeric field ever appears in `RouterDecision`.

## §10 Twin-pointer card

📁 **Repo — S2824 artifacts:**

- **Feature module:** `core/services/phase_0_5_router.py`
- **Classifier mirror:** `core/services/phase_0_5_classifier_a.py`
- **Handler diff:** `core/services/td_handlers_ops.py:5905+`
- **Settings:** `core/settings.py` (bottom-of-file additions)
- **Model:** `persistence/models.py` — `Phase0_5RouterEvent`
- **Migration:** `persistence/migrations/0009_phase0_5routerevent.py`
- **Tests:** `core/tests/test_phase_0_5_router.py` (18 tests OK)
- **Extraction:** `docs/research/discovery_layer/PHASE_0_5/analyze_router_log.py`
- **Seed logs:** `logs/phase_0_5_router.jsonl` + `logs/phase_0_5_integrity_events.jsonl` (empty)
- **Integrity-stop dir:** `docs/research/discovery_layer/PHASE_0_5/integrity_stops/` (populated at runtime)
- **Handoff:** `docs/handoffs/SESSION_2824_PHASE0_5_B2_BUILD_SHIPPED.md` (this doc)
- **Envelope diff appended to:** `docs/research/implementation/RATIFICATION_2026-07-18_s2823_phase0_5_constitutional_package_b1_b2_b3.md` §8

🖥️ **Workspace UI — S2824 has NO new twin-pointer workspace deliverable this
session** — implementation execution sessions preserve the envelope in
`docs/research/implementation/` as authoritative; workspace mirror deferred
per S2823 pattern. Group 2700 arc's workspace deliverable
(`37d6ca76-89c3-4966-8f4c-decc52ce8169`) remains the /docs/ restructuring
arc anchor.
