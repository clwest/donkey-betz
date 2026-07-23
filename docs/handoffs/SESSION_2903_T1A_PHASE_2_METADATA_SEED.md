# Session 2903 — T1a Phase 2 Metadata Seed (Row 161 Substrate Arc Thread 2/3)

**Date:** 2026-07-22
**Session:** S2903
**Branch/PR:** `s2903-t1a-phase-2-metadata-seed` → **PR #3431** (merged as `6237df49c`)
**Predecessor:** [SESSION_2902_T1A_AUTO_HARNESS_SCAFFOLD.md](SESSION_2902_T1A_AUTO_HARNESS_SCAFFOLD.md)
**Playbook:** v0.9.0 — unchanged
**Recycle cycle:** post-merge `make recycle-all` clean (sha=`6237df49c1c6`)

---

## §1 — Ship summary

Third consecutive substrate-arc thread executed in a single session. T1a
Phase 2 harden closes T1a fully (Phase 1 shipped S2902, Phase 2 shipped
this session). T1a total actual: **1.5 sessions** vs ≤2 hard cap.

**PR shipped:** [#3431](https://github.com/clwest/donkey-betz-platform/pull/3431) merged at `6237df49c` — 119 files changed (+1,289 / −688):

- `core/services/tool_action_metadata.py` — 4 TOOL_DEFAULTS + 8 new TOOL_ACTION_METADATA records (up from 0 defaults + 2 records at Phase 1)
- `core/tests/test_tool_action_metadata_seed.py` — new file, 12 regression tests across 5 classes
- `docs/audits/pa_tools/harness_output/*.json` — 116 per-tool artifacts + `summary.json` refreshed

**Harness dispatch delta:**

| Metric | Phase 1 (S2902) | Phase 2 (S2903) | Δ |
|---|---|---|---|
| Tools in-class | 116 | 116 | 0 |
| READ_ONLY dispatched | 2 | 39 | +37 |
| skipped_metadata_missing | 567 | 525 | −42 |
| Exceptions | 0 | 0 | 0 |
| error_captured | 0 | 0 | 0 |
| Parity mismatches | 8 | 8 | 0 (Phase 0 backlog) |

**Twin workspace mirror** (Donkey Betz workspace `b4503364-2573-4401-9e28-61a739e0ce50`):
- Content mirror: `a9cbb5cd-af20-4660-8fd8-1ab1f79696cb` (`initiative_phase_doc` / `engineering`, status `completed`, diagnostic flag cleared post-create)
- Ratification envelope: `c5579bda-aa8c-414e-8deb-cfd16fe79541` (`ratification_record` / `governance`, status `completed`, no diagnostic flag)

Both written by Rigby via `deliverable_tool.create` per feedback rule
`feedback_rigby_writes_workspace_deliverables`. Content mirror caught the
known bug per `feedback_pa_deliverables_tool_flags_ratifications_as_diagnostic`
(applies to content mirror this session, same as S2902 — pattern is
"missing initiative_id" not "ratification-specific"). Cleared via ORM
post-create.

---

## §2 — Metadata seed content

Authored per each tool's validation-doc evidence.

### TOOL_DEFAULTS (all READ_ONLY)

| Tool | Evidence source |
|---|---|
| `ops_tool` | `ops_tool_validation.md` §5 — "all actions read-only except focus_mode_update" |
| `kb_tool` | `td_handlers_ops.py:7548` handler trace — all 5 actions are ORM/pgvector queries |
| `agent_introspection_tool` | Read-only introspection surface (list, stats, details, capabilities, tools) |
| `repo_tool` | `repo_tool_validation.md` line 3 — "read-only codebase introspection" |

### TOOL_ACTION_METADATA (per-action records)

**Override on defaulted tool** (1 record):

- `(ops_tool, focus_mode_update)` → `WRITE_GATED` — the one mutating action in ops_tool per validation doc §5; overrides the READ_ONLY tool default

**Mixed-safety fan-out — session_tool** (7 records; NO tool default because safety splits per action):

| Action | Safety | Applicability | Notes |
|---|---|---|---|
| `health_check` | READ_ONLY | always | default action per handler |
| `list_recent` | READ_ONLY | always | F-S-3 mitigation shipped S2728 |
| `whoami` | READ_ONLY | always | provenance surface |
| `create_fresh` | MUTATION | always | creates ChatConversation row |
| `retire` | MUTATION | conditional | F-S-6 mitigation shipped S2728 |
| `set_active` | MUTATION | conditional | writes session_active=True |
| `seed` | MUTATION | conditional | writes ChatMessage with [SYSTEM SEED] marker |

Total: **4 TOOL_DEFAULTS + 10 TOOL_ACTION_METADATA records** (2 Phase 1 + 8 Phase 2).

---

## §3 — Rigby joint SIGN cycle (Q1-Q4)

Pre-commit SIGN routed with mandatory zoom-out ask per
`feedback_zoom_out_ask_per_rigby_sign`. Rigby returned tool-grounded verdicts
(multiple `repo_tool.search` + `repo_tool.read_file` calls on
`tool_dispatcher.py`, `td_handlers_ops.py`, and the metadata module — non-empty
`tool_runs` per `feedback_verify_rigby_tool_runs_before_trusting_sign`).

| # | Question | Verdict | Resolution |
|---|---|---|---|
| Q1 | Do the 12 authored (tool, action) safety classifications match your belief? | AGREE-WITH-EDITS | Softened `ops_tool.focus_mode_update` note — auth enforcement location not verified at seed time |
| Q2 | TOOL_DEFAULTS vs per-action shape (session_tool no-default invariant)? | AGREE | session_tool mixed fan-out is the correct invariant |
| Q3 | Test coverage — any missing regression guard? | AGREE-WITH-EDITS | Added `MutationVerbDefaultLeakTests` — heuristic guard against future mutating-verb action landing on a READ_ONLY-defaulted tool and getting silently classified as READ_ONLY |
| Q4 | Zoom-out pushback | AGREE-WITH-EDITS | Same-PR: Q1 fix. Future triggers: FT-1 defaulted-tool action-set change lint; FT-2 harness `soft_error` outcome for `ok=True` + `error_code` responses |

Both same-PR edits (Q1 note softening + Q3 mutation-verb guard) applied
inline before commit. Follow-up SIGN cycle Rigby returned AGREE across all
four verdicts.

---

## §4 — Same-PR mitigations

### Mitigation 1 — `ops_tool.focus_mode_update` note softening (Q1)

**Concern:** initial note read `"gate: staff-only"` but handler at
`td_handlers_ops.py:317-328` shows no in-handler auth check — `set_config()`
called directly on non-empty `config_updates` payload.

**Fix:** note updated to `"writes Focus Mode config; revisit: auth-boundary
at harness-dispatch"`. Applicability moved from `gated` → `conditional`.
Full inline comment cites `td_handlers_ops.py:317` and states auth
enforcement location NOT verified at seed time; revisit if/when WRITE_GATED
harness dispatch is added.

### Mitigation 2 — `MutationVerbDefaultLeakTests` regression guard (Q3)

**Failure mode being guarded:** future author adds `ops_tool.delete_recycles`
(or similar) to schema; no `TOOL_ACTION_METADATA` entry authored;
`resolve_safety` falls through to `TOOL_DEFAULTS['ops_tool']` (READ_ONLY) and
the harness dispatches a write action as if it were a read.

**Guard shape:** for every `TOOL_DEFAULTS[tool]` with `default_safety_class ==
'READ_ONLY'`, iterate the tool's schema action enum. Any action whose name
matches a mutation-verb prefix
(`create_/delete_/update_/set_/seed/retire/save_/unsave/add_/remove_/write_/append/archive_/kill_/freeze_/unfreeze_/approve_/reject_/apply_/reset_/clear_/link_/unlink_/normalize/bulk_`)
MUST have an explicit `TOOL_ACTION_METADATA` override. Test fails with the
offending `(tool, action)` list if any leak.

Test currently green — no leaks with Phase 2 seed. Heuristic, not
AST-level; catches obvious naming-signal regressions.

---

## §5 — Future triggers recorded (not acted this PR)

Both gated behind substrate-arc-scoped SIGN when they fire.

**FT-1 — "defaulted tool action-set changed" review/lint**
- Trigger: a new schema action lands on a `TOOL_DEFAULTS` tool without an
  accompanying `TOOL_ACTION_METADATA` entry OR an updated tool default
- Placement: could live as a check in the harness `--check` flag or as a
  separate pre-commit hook
- Rationale: Rigby Q4 concern about silent coupling between the metadata
  registry and schema evolution

**FT-2 — Harness `soft_error` outcome value**
- Trigger: any handler returns `ToolResult.ok=True` with `error_code` or
  `error` keys in the response `dict`
- Observed at S2903 Phase 2: `session_tool.whoami` and `session_tool.health_check`
  exhibit this at `user_id=None` dispatch (harness default)
- Change: bump `HARNESS_VERSION` to `'v2'` (per frozen v1 contract in
  `pa_tool_validate_harness.py` module docstring) — adds a new stable
  `expected_outcome` value distinct from `success` (result.ok=True + no
  error keys) and `error_captured` (result.ok=False)

---

## §6 — Zoom-out fold captured (per PLAYBOOK-6.10.7)

**Fold — harness timestamp churn** (`future_trigger`, NOT MITIGATED)
- **Concern:** 110 of 116 per-tool JSONs diff on every `--all-in-class` run
  even when their content is unchanged. Only `run_metadata.generated_at` and
  `run_metadata.git_sha` change. This inflates PR diffs and makes
  content-vs-timestamp changes hard to distinguish.
- **Trigger to act:** if the harness becomes CI-invoked (parity gate in a
  workflow) or if a session's PR needs to isolate content-change signal.
- **Candidate fix shape:** compare content excluding `generated_at` before
  writing; if unchanged, preserve prior timestamp. `run_metadata.generated_at`
  becomes "when this shape was last observed to have changed" — matches the
  stable-filename design intent.
- **Not mitigated inline** because it needs harness code change (v1
  behavior stable; contract not violated).

---

## §7 — Test coverage state

| Test file | Class count | Test count | Guards |
|---|---|---|---|
| `test_pa_tool_validate_harness_in_class.py` | 2 | 8 | Fold A/D filter invariants (unchanged from S2902) |
| `test_tool_action_metadata_seed.py` | 5 | 12 | Phase 2 seed shape + Q3 mutation-verb leak guard |
| **Total** | **7** | **20** | |

All 20 pass at HEAD `6237df49c`.

---

## §8 — Substrate arc status

- T1c ✓ shipped S2901 (PR #3427 at `e92bd807c`)
- T1a Phase 1 ✓ shipped S2902 (PR #3429 at `bfc3dc61c`)
- **T1a Phase 2 ✓ shipped S2903 (PR #3431 at `6237df49c`) — this session**
- T1b ← queued for S2904 or later

**Arc close estimate updated:**
- T1c: 1 session
- T1a: 1.5 sessions (Phase 1 + Phase 2)
- T1b: ~1-2 sessions remaining
- **Total substrate arc: ~3-4 sessions actual** vs ~4-5 initial estimate

Post-substrate sweep pace target unchanged: **~10-15 sessions** for
remaining ~76 tools (vs ~50 at current-shape pace).

---

## §9 — Post-merge sanity check

Fresh HEAD `6237df49c` post-recycle:

```
python manage.py pa_tool_validate_harness --all-in-class --summary-only
→ 116 tool(s), 39 READ_ONLY dispatched, 525 skipped for missing metadata

python manage.py pa_tool_validate_harness --check-doc-schema-parity
→ 8 mismatches unchanged from Phase 1 (Phase 0 doc-fix backlog)

python manage.py test core.tests.test_tool_action_metadata_seed core.tests.test_pa_tool_validate_harness_in_class
→ Ran 20 tests. OK.
```

Harness runnable + tests green + parity gate stable from freshly-recycled state.

---

## §10 — Next session (S2904) first action

**Recommend T1b template extraction** — T1a is fully done; T1a v1 output
schema is frozen (`pa_tool_validate_harness.py` module docstring); Phase 2
now produces real harness output to canonicalize a template shape around.

Concrete T1b work per parent §3:
- Canonicalize per-tool validation-doc section structure
- Add ratchet-and-warn gap-map lint
- Ratchet fires on new-doc-authoring OR when a tool's covered-actions set changes

Alternative Step 1 candidate — **Phase 0 heading fixes for the 8
close_with_short_note tools** (agent_introspection_tool / autopilot_tool /
deliverable_tool / kb_tool / ops_tool / repo_tool / search_docs /
session_tool). Doc-only, would clear all parity mismatches. Defensible if
Chris judges the parity gate should be clean before T1b template work
begins.

---

## §11 — D6 moratorium status

**D6 moratorium still in force.** No strategic discovery arcs opened. No
opportunity portfolio expansions. No layer-boundary design work. S2903 was
pure engineering substrate execution on the pre-ratified Row 161 arc plan.

---

## §12 — Rigby Tool Gap Ledger

No new entries this session. FT-1 + FT-2 recorded in §5 above (substrate-arc
scope, not tool-surface-gap scope).

---

## §13 — PRs shipped this session

- u-d-b PR [#3431](https://github.com/clwest/donkey-betz-platform/pull/3431) — S2903 T1a Phase 2 metadata seed, merged at `6237df49c`
- u-d-b PR `<TBD>` — S2903 close cascade (handoff + 00-START refresh + wrapper pin bump)
