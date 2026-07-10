# Session 2744 — Cost Thresholds Management Command

**Session:** 2744
**Date:** 2026-07-10
**Session type:** Direct EOS campaign — §17 Cost Protection ops surface
**System Owner directive:** "ship the manage.py command as a session arc" → "approved" (scope) → "approve — open the PR" → "merge it"
**PA conversation pin (arc):** `pa-571748d9b6b940ea` (title: `session-2744-cost-thresholds-manage-command-arc`)
**Preceding arc:** SESSION_2743 (Cat 3 startup config log — revealed $246/mo prod spend as byproduct)
**Merge commit:** `20747b6e` (PR #3070, squash-merged 2026-07-10)

---

## §1 Delivery ledger

| # | PR | Purpose |
|---|---|---|
| 1 | #3070 (`feat/session-2744-cost-thresholds-manage-command`) | cost_thresholds management command — 3 files, +396/-1 LOC |

**Ledger totals for S2744:** 1 PR · 1 feat · 25 new tests · 25/25 pass · zero regressions · zero governance side effect · closes the S2735→S2743 observation-period gate loop as CLI-executable.

---

## §2 Arc shape

1. **Chris directive at open** — "route the PLAYBOOK PATCH..." (no, that was S2742). "ship the manage.py command as a session arc" — followed the "small session arc" option from the S2743 close recommendation.
2. **Pin lifecycle** — retired S2743 Cat 3 arc pin `pa-0963d4aa1f5b484f`; minted `pa-571748d9b6b940ea`; rotated `tools/pa_local.sh` line 532
3. **PLAYBOOK-6.10.6 verify-before-build** (30 seconds):
   - HEAD verified: `72c9fd7068b015c8938d79434dfeb646a439d3e5`
   - `Glob core/management/commands/cost_*.py` returned no files
   - `Grep cost_threshold OR cost_protection_enforce_mode` returned no hits in commands directory
   - Outcome: (i) proceed to Cat A
4. **Cat A independent read** — mapped SystemConfiguration model (JSONField value + set_config classmethod); proposed 5-flag mutually-exclusive command surface (show/set/unset/set-mode/unset-mode); drafted validation rules + output format; 9-question scope SIGN dispatch
5. **Cat A scope SIGN** — Rigby 0.88 PICK with 8 refinements confirmed
6. **Chris D-verdict** — "approved" (single word; ratifies all 8 refinements)
7. **Implementation** — 2 new files:
   - `core/management/commands/cost_thresholds.py` (+189 LOC): argparse group + 5 handlers + `_parse_threshold_value` guardrail + `_mode_row_present` disambiguation helper
   - `core/tests/test_cost_thresholds_command.py` (+207 LOC): 25 tests across 7 classes
8. **Cat B implementation SIGN** — Rigby 0.93 APPROVE zero F-BLOCKING (**highest Cat B confidence in the arc streak**)
9. **Chris ratification** — "approve — open the PR"
10. **PR #3070 opened + squash-merged as `20747b6e`**
11. **Post-merge cascade:**
    - Docs cascade: build_docs_index + build_rag_corpus + sync + embed + provenance
    - No `make celery-recycle` needed (management command not touched by beat scheduler)
    - This handoff authored
    - 00-START refreshed for S2745

---

## §3 What shipped

### §3.1 Command surface (`core/management/commands/cost_thresholds.py`)

**5 flags via argparse.add_mutually_exclusive_group():**

| Flag | Behavior |
|---|---|
| (none / --show) | Print `[COST_MONITOR] configuration:` block with deterministic mode → hour → day → month order |
| `--set WINDOW VALUE` | Write threshold via `SystemConfiguration.set_config(category='performance')`; VALUE parsed as Decimal + validated `is_finite()` + `> 0` |
| `--unset WINDOW` | Delete row via `.filter(...).delete()` (clean default restoration; no is_active=False tombstoning) |
| `--set-mode MODE` | MODE ∈ {monitor,freeze}; case-insensitive |
| `--unset-mode` | Delete row; reverts to default 'monitor' |

**Value validation guardrails:**
- Non-Decimal → `CommandError("invalid VALUE 'x': expected Decimal-parseable string")`
- Non-finite (`inf`, `nan`) → `CommandError("must be finite")`
- Zero or negative → `CommandError("must be > 0 (got 0). Zero or negative would fire on every cost; use --unset to remove a threshold.")`
- Invalid window → `CommandError("invalid WINDOW 'year'; must be one of ('hour', 'day', 'month')")`
- Invalid mode → `CommandError("invalid MODE 'paranoid'; must be one of ('monitor', 'freeze')")`

**Output format matches S2743 startup log for grep parity:**
```
[COST_MONITOR] configuration:
  enforce_mode: monitor (default; unset row)
  hour: unset
  day: unset
  month: $500.00
```

The `(default; unset row)` suffix distinguishes explicit-monitor from absent-row via `_mode_row_present()` helper. Rigby: "good ops-clarity, not over-engineering."

### §3.2 Test coverage (`core/tests/test_cost_thresholds_command.py`)

**25 tests across 7 classes:**

| Class | Tests | Focus |
|---|---|---|
| `ShowTests` | 5 | Default block format + deterministic ordering + suffix behavior + default-no-flag = --show |
| `SetTests` | 8 | Roundtrip all 3 windows + invalid window + non-Decimal + zero (footgun message) + negative + non-finite |
| `UnsetTests` | 3 | Deletion + absent-noop + invalid window |
| `SetModeTests` | 4 | monitor + freeze + case-insensitive + invalid |
| `UnsetModeTests` | 2 | Deletion + absent-noop |
| `MutualExclusionTests` | 2 | --set + --unset together + --set + --set-mode together |
| `EndToEndTests` | 1 | Full ops cycle: initial state → set 2 thresholds + mode → show mid-state → unset all → initial state matches |

**Test discipline:** real DB writes to SystemConfiguration, no substrate mocking; uses `call_command` + `StringIO` for stdout capture. Suite runtime: 0.181s.

### §3.3 Live invocation verification

Manually verified full cycle at S2744 body-write time:

```
$ python manage.py cost_thresholds
[COST_MONITOR] configuration:
  enforce_mode: monitor (default; unset row)
  hour: unset
  day: unset
  month: unset

$ python manage.py cost_thresholds --set month 500
[COST_MONITOR] set month=$500.00

$ python manage.py cost_thresholds
[COST_MONITOR] configuration:
  enforce_mode: monitor (default; unset row)
  hour: unset
  day: unset
  month: $500.00

$ python manage.py cost_thresholds --unset month
[COST_MONITOR] unset month (deleted 1 row)
```

Ops cycle works end-to-end.

---

## §4 What this unlocks — S2735→S2744 observation gate loop as CLI

Chris now has full CLI control over the enforcement-gate discipline he embedded at S2735 P1:

| Step | CLI verb | Result |
|---|---|---|
| 1. Start observation | `python manage.py cost_thresholds --set month 500` | Threshold row written; `check_cost_thresholds` beat task begins breach detection |
| 2. Wait for data | (passive — 15-min beat cadence + real cost accumulation) | Currently ~$246/mo baseline per S2743 startup log; threshold rarely breaches |
| 3. Arm shadow mode | `python manage.py cost_thresholds --set-mode freeze` | S2739 `would_freeze` shadow log fires on breach; still monitor-only actual behavior |
| 4. Observe counterfactuals | (passive — read celery.log for `would_freeze=True` warnings + HAI payload data) | Baseline observation data accumulates |
| 5. Chris D-verdict | (session dispatch on Cat 1 enforcement flip readiness) | Requires S2735 P1 gate criteria met + explicit approval |

Every step has a durable CLI surface now. No more Django-shell-only workflow. The `[COST_MONITOR]` prefix in output grep-matches the S2743 startup log line, so ops can filter both surfaces with a single pattern.

---

## §5 Rigby SIGN provenance

| Stage | Pin | Confidence | Verdict | Refinements folded |
|---|---|---|---|---|
| Cat A scope + command shape | `pa-571748d9b6b940ea` | 0.88 | PICK | 8: 5-flag mutually-exclusive surface, `cost_thresholds` name (over broader `cost_protection`), DELETE row for --unset (over is_active=False), `[COST_MONITOR]` prefix + deterministic order, `>0` guardrail with footgun message, new test file for isolation, docstring + argparse help documenting 5 key ops, race/DB-down/mutual-exclusion semantics |
| Cat B implementation | `pa-571748d9b6b940ea` | **0.93** (highest in arc streak) | APPROVE (zero F-BLOCKING) | 0 required; 2 informational: category=`performance` acceptable (vs 'system'/'security'); optional integration test for read-path roundtrip "not required for this PR" |

Total Rigby SIGN dispatches: 2 (Cat A + Cat B). Both folded before merge. No REVISE cycles required — **third consecutive Playbook/code arc where scope-to-implementation pipeline required zero corrections** (matches S2742 v0.4.1 PATCH + S2743 Cat 3 first-attempt-pass precedents).

---

## §6 Cross-arc pattern posture

**Zero-F-BLOCKING body SIGN streak now at 3 arcs** (S2742 + S2743 + S2744). All small-to-mid scope. Two of the three (S2743 + S2744) are code arcs with test suites; one (S2742) is a Playbook PATCH.

**Session-arc handshake efficiency:**
- S2739 body SIGN: 1 REVISE cycle (E5 citation, later folded via scope-SIGN feedback pattern)
- S2740 body SIGN: 1 REVISE cycle (E5 memory-file citation → E6 SESSION_2700 §2.1 substitution)
- S2741 body SIGN: PASS with 2 follow-on recs folded (§20/§21 refresh blocks)
- **S2742 body SIGN: PASS zero-F-BLOCKING** ← streak begins
- **S2743 body SIGN: PASS zero-F-BLOCKING**
- **S2744 body SIGN: PASS zero-F-BLOCKING** (0.93 confidence — new high)

**Two-trigger candidates from streak:**
- "Body SIGN pass-on-first-attempt as small-to-mid-scope signal" — 3 instances now; still all small-to-mid. Awaits large-scope arc to establish full scope-independence.
- "Rigby-authored refinement text folded verbatim" — S2742 §6.12 bullet + S2744 refinement recommendations. Pattern where Rigby's scope-SIGN suggested text ships as-is in body-write. Two instances; awaits third.

**Ops-surface pattern candidate:** S2743 shipped a visibility hook (startup log); S2744 shipped an ops verb. This is a natural pairing — visibility hooks reveal state, ops verbs let operators mutate state. Single instance of the "visibility hook + ops verb pair"; awaits second organic occurrence before codification consideration.

---

## §7 What this research taught us about how to do research

*(per feedback_xx99_meta_methodology_section.md discipline — "small-session-arc + ops-surface" edition)*

### §7.1 What worked
- **Reversed Cat A order (S2741 §9.5) is now habitual.** Verify-before-build ran FIRST (30 seconds); Cat A independent read + scope SIGN followed. Ships zero-cost defense against wasted-session arcs.
- **Rigby-authored scope-SIGN refinements shipped verbatim.** All 8 scope-SIGN refinements folded exactly as recommended in the Cat A response — no drift, no reinterpretation. Fastest scope→body pipeline in the streak.
- **Reusing S2743 public helpers.** The command imports `read_thresholds_snapshot()` + `read_enforce_mode()` — both public API surfaces shipped ONE SESSION prior. S2743's public-helper choice (Rigby scope-SIGN Nit 1) directly enabled S2744's clean read path. Cross-arc compounding: small architectural choices in prior sessions unlock clean implementations in later sessions.

### §7.2 What to codify (candidates — do NOT codify yet)
- **"Visibility hook + ops verb pair" arc pattern.** S2743 (startup log) + S2744 (ops command) is the first instance where a visibility hook and an ops verb ship in consecutive sessions on the same substrate. Codification candidate for when a second such pair emerges organically.
- **"Public-helper-first cross-arc unlocking."** S2743 shipped `read_thresholds_snapshot()` because Rigby recommended avoiding leading-underscore imports. S2744 immediately used that helper. This "prior-arc public surface enables next-arc clean implementation" pattern is worth naming if it recurs.

### §7.3 Anti-patterns to avoid
- **Do NOT add admin surface when CLI is sufficient.** Chris asked for the manage.py command, not admin. Adding admin would double the surface area for the same functionality — CLI works over SSH, in cron, and in CI while admin doesn't. Ship the smallest surface that satisfies the ask.
- **Do NOT preemptively broaden command names.** The command is `cost_thresholds` (thresholds dominant, mode secondary) rather than `cost_protection` (broader). Rigby scope-SIGN #2: "If we later add more cost-protection knobs, we can add a sibling command then rather than preemptively broadening now." Naming should track current surface, not aspirational surface.

### §7.4 Suggestions for future ops-surface arcs
- Add a `[SUBSYSTEM]` prefix to command output that matches the subsystem's log prefix. Grep parity across visibility hooks + ops commands + task logs is a durable UX win. S2743 shipped `[COST_MONITOR]` in the startup log; S2744 shipped the same prefix in command output. `grep '[COST_MONITOR]'` now catches both surfaces.
- Reject validation edge cases at the CLI layer, not the service layer. S2744's `_parse_threshold_value` rejects zero at command-parse time; the service layer wouldn't have known zero was a user-input footgun (service just reads Decimal from JSONField). CLI knows user intent; service knows persistence semantics. Layered validation.

---

## §8 Post-merge cascade verification

| Step | Command | Result |
|---|---|---|
| 1. Squash-merge PR #3070 | `gh pr merge 3070 --squash --delete-branch` | Merged as `20747b6e` |
| 2. Docs cascade | `build_docs_index` + `build_rag_corpus` + `sync_docs_index_to_documents --embed` + `build_docs_provenance` | (see cascade output) |
| 3. This handoff | `Write` | authored |
| 4. 00-START refresh | `Write` | S2745 candidate queue authored |

Note: no `make celery-recycle` step — management command not registered with celery beat; no task registry changes.

---

## §9 Governance references

- **Ratified code**: `core/management/commands/cost_thresholds.py` + `core/tests/test_cost_thresholds_command.py` @ merge commit `20747b6e`
- **PR**: #3070 (squash-merged)
- **Rigby SIGN pin (arc)**: `pa-571748d9b6b940ea` (session-2744-cost-thresholds-manage-command-arc)
- **Prior arc handoffs**: SESSION_2743_COST_PROTECTION_CAT3.md (immediately preceding — visibility hook that revealed $246/mo baseline); SESSION_2739_COST_PROTECTION_P2_OBSERVATION.md (`would_freeze` shadow + Cat 3 originally deferred here); S2735 P1 gate discipline embedded in `core/tasks_cost_protection.py:6-10` docstring
- **Chris ratification directives**: 2026-07-10 (multi-step: "ship the manage.py command as a session arc" → "approved" → "approve — open the PR" → "merge it")
- **PLAYBOOK-6.10.6** (v0.4.0) — verify-before-build discipline applied to command substrate (first application to management-command substrate class in the arc streak)
- **S2743 public helpers `read_thresholds_snapshot()` + `read_enforce_mode()`** — reused directly; cross-arc compounding

---

## §10 Wrapper pin state at S2744 close

- `tools/pa_local.sh` line 532: `pa-571748d9b6b940ea` (session-2744-cost-thresholds-manage-command-arc)
- Arc pin held OPEN pending Chris "session close" signal — future S2745 session-open should retire this pin per §16 arc-close discipline and mint fresh S2745 open pin.

---

**Session 2744 CLOSED.** Cost thresholds management command shipped. Full observation-period gate loop is now CLI-executable. 25/25 tests pass; live cycle verified. Zero-F-BLOCKING body SIGN streak now at 3 arcs.
