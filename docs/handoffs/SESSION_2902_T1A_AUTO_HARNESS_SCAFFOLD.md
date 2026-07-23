# Session 2902 — T1a Auto-Harness Scaffold (Row 161 Substrate Arc Thread 2/3)

**Date:** 2026-07-22
**Session:** S2902
**Branch/PR:** `s2902/t1a-auto-harness-scaffold` → **PR #3429** (merged as `bfc3dc61c`)
**Predecessor:** [SESSION_2901_T1C_LOW_SIGNAL_AUDIT.md](SESSION_2901_T1C_LOW_SIGNAL_AUDIT.md)
**Playbook:** v0.9.0 — unchanged
**Recycle cycle:** post-merge `make recycle-all` clean (sha=`bfc3dc61c9c9`)

---

## §1 — Ship summary

Second thread of the Row 161 substrate arc. T1a MVP scaffold shipped in a single session (parent §5 hard cap = ≤2 sessions; Phase 1 landed same-session as design SIGN + Phase 0 investigation).

**PR shipped:** [#3429](https://github.com/clwest/donkey-betz-platform/pull/3429) merged at `bfc3dc61c` — 3 new source files (metadata module + mgmt command + Fold A regression tests) + 116 auto-generated per-tool JSON artifacts + `summary.json` rollup (+9,579 lines net across 120 files).

**Files landed:**
- `core/services/tool_action_metadata.py` (149 lines) — Action Metadata Map per T1c §8 Candidate A
- `core/management/commands/pa_tool_validate_harness.py` (~440 lines including frozen v1 contract block) — the harness mgmt command
- `core/tests/test_pa_tool_validate_harness_in_class.py` (128 lines) — 8 Fold A regression tests
- `docs/audits/pa_tools/harness_output/*.json` (116 per-tool artifacts + `summary.json`)

**Twin workspace mirror** (Donkey Betz workspace `b4503364-2573-4401-9e28-61a739e0ce50`):
- Content mirror: `7535e657-71b3-46ac-9233-087cba947b2c` (`initiative_phase_doc` / `engineering`, status `completed`, no diagnostic flag)
- Ratification envelope: `203dca41-38c7-4e9c-b520-d1c5b2b3e485` (`ratification_record` / `governance`, status `completed`, no diagnostic flag)

Both written by Rigby via `deliverable_tool.create` per feedback rule `feedback_rigby_writes_workspace_deliverables`. **Bug-pattern note:** `feedback_pa_deliverables_tool_flags_ratifications_as_diagnostic` fired this session but on the CONTENT MIRROR (`initiative_phase_doc` / `engineering`) — not the ratification envelope as previously documented. Diagnostic reason was `missing_initiative_id`, same as documented, but the flag applies to any `deliverable_tool.create` call missing an `initiative_id` regardless of `deliverable_type`. Post-create ORM fix cleared the flag on the content mirror; the ratification envelope came out clean. Existing memory feedback may need broadening — flagged for review but not amended this session.

---

## §2 — Four design decisions ratified (Claude+Rigby SIGN → Chris green-light)

Pre-code SIGN routed to Rigby with mandatory zoom-out ask per `feedback_zoom_out_ask_per_rigby_sign`. Rigby returned tool-grounded verdicts (2× `search_docs` + 5× `repo_tool` including 3 `read_file` on the T1a/T1c/parent scoping docs — non-empty tool_runs per `feedback_verify_rigby_tool_runs_before_trusting_sign`).

| # | Decision | Verdict | Rationale |
|---|---|---|---|
| Q1 | Safety enum values | **4** (`READ_ONLY / WRITE_GATED / MUTATION / IRREVERSIBLE`) per T1c §8 — supersedes T1a §3's 3-value list | T1c more recent + locks in-class boundary; IRREVERSIBLE = cannot run safely even with dry_run flag (kill switches, non-recoverable deletes) |
| Q2 | Metadata field set | **3 fields** (`safety_class` / `applicability` / `notes`) per T1c §8 MVP boundary | env/deps encoded via notes convention (`env: external:<name>`, `deps: <handle>`) — parseable at T1b without schema change; `env_required` deferred as future substrate row if pattern surfaces |
| Q3 | Fold B parity mechanism | **Option (a)** — `--check-doc-schema-parity` gate exits non-zero; artifact records mismatches with exact `missing_actions` list; no `PA_TOOLS_GAP_MAP.md` mutation | Preserves DOC-AUTOGEN contract; gap-map regen picks it up naturally; default-mode runs surface without blocking |
| Q4 | Unclassified default | **Option (a)** — skip entirely, `status_code=None`, `reason='metadata_missing'` | Safest MVP; metadata authorship becomes the sweep-pace gate (which is what T1a is designed to enable); full schema action inventory still enumerated so artifact isn't a silent hole |

Rigby also surfaced two zoom-out concerns; both folded into shape at design time:
- **Metadata debt tax** — tool-level defaults + per-action overrides in `TOOL_DEFAULTS`; "top missing metadata" report at end of run (non-blocking); parity check runs independently of metadata. Implemented in the module.
- **Artifact churn** — stable filenames (`<tool_name>.json`, overwrite, no timestamps); `run_metadata` block (`generated_at` + `git_sha`) inside JSON; single `summary.json` rollup with per-tool `artifact_sha256`. Implemented.

---

## §3 — Count reconciliation: 96 vs 116

T1c §9 predicted **96 in-class tools** (94 untested + 2 T1c-promoted). Harness enumerates **116** because Fold D anti-goal ("`validated_full` is a doc-status label, not runtime confidence") means the harness runs across validated tools too.

Delta = ~20 tools currently classified `validated_full` / `validated_partial` / `validated_doc_exists_unknown` that get harness coverage despite already having docs. Both counts are correct in their frame:
- **96** = "how many tools NEED harness coverage" (narrow, T1c's sweep-queue framing)
- **116** = "how many tools CAN run through the harness" (broad, Fold D framing)

Rigby AGREE-with-tweak on this reading at post-scaffold SIGN.

---

## §4 — Fold A / D compliance in code

**In-class filter** (`_compute_in_class`):

```python
return {
    name for name in schema_by_name.keys() & handler_names
    if name != 'run_agent'
}
```

- Fold A: excludes `run_agent` explicitly; the 44 `agent_via_run_agent` handlers excluded implicitly (they have no schema).
- Fold D: filter does not gate on doc-status — validated_full tools get harness coverage same as untested.

**Regression tests** (`test_pa_tool_validate_harness_in_class.py`):

| Test | Guards |
|---|---|
| `test_run_agent_never_in_class` | Fold A: meta-tool excluded |
| `test_no_schema_less_handlers_in_class` | Fold A: 44 agent handlers excluded |
| `test_no_orphan_schemas_in_class` | Symmetry: schema-only tools excluded |
| `test_in_class_intersection_shape` | Filter is exactly `(schema ∩ handler) − {'run_agent'}`, no other subtractions |
| `test_in_class_count_within_baseline_band` | Loose 80–130 band around the current 116 count |
| `test_run_agent_exclusion_reason_names_meta_tool` | Human-readable exclusion message names Fold A |
| `test_schema_less_handler_exclusion_reason` | Reason names run_agent routing |
| `test_unknown_tool_exclusion_reason` | Unknown tools get clean exclusion reason |

All 8 pass.

---

## §5 — Initial `--all-in-class` results

Live sweep produced 116 per-tool artifacts + summary. Headline:

| Metric | Value |
|---|---|
| Tools enumerated | 116 |
| READ_ONLY dispatched | 2 (both `ops_tool` — `version` + `recent_recycles`) |
| Actions skipped for missing metadata | 567 |
| Parity mismatches surfaced | 8 (matches T1c §7.1 close_with_short_note tools) |

Parity mismatches — exactly the 8 tools T1c §7.1 flagged for the `## Covered actions` heading fix:

- `agent_introspection_tool` (no heading)
- `autopilot_tool` (schema drift — 23 new actions post-doc)
- `deliverable_tool` (no heading)
- `kb_tool` (no heading; combined doc with search_docs)
- `ops_tool` (schema drift — 2 new bridge actions post-doc)
- `repo_tool` (no heading)
- `search_docs` (no heading)
- `session_tool` (no heading)

Auto-escalation recommendation emitted per Fold B contract. Fold B `--check-doc-schema-parity` gate exits non-zero on this state.

---

## §6 — Post-scaffold SIGN cycle

Rigby returned tool-grounded verification on shipped code + artifact — **7 `repo_tool` calls** (5× `read_file` including the metadata module, mgmt command, test file, ops_tool.json artifact; 2× `search` for structure verification). Non-empty tool_runs per `feedback_verify_rigby_tool_runs_before_trusting_sign`.

Verdicts:
- **V1** AGREE — Fold A filter shape exact
- **V2** AGREE — Q4a skip semantics; `dispatcher.execute` never called in unclassified branch
- **V3** AGREE — Parity gate: mismatches recorded always, CommandError only on flag
- **V4** AGREE-with-tweak — Artifact contract satisfied by keys present, ordering differs (contract not order-dependent)
- **Count delta 96 vs 116** — AGREE, encoded in module docstring per Fold D
- **Zoom-out concern**: `resolution_source` + skip subtype taxonomy evolved artifact schema beyond T1a §5 minimal spec → **needs frozen v1 contract before T1b consumers bind**

---

## §7 — Zoom-out folds captured (per PLAYBOOK-6.10.7)

**Fold — artifact schema v1 versioning discipline** (`same_pr_mitigatable`, MITIGATED)
- **Concern:** `resolution_source` + skip subtypes (`skipped_metadata_missing`, `skipped_write_gated`, etc.) added fields beyond T1a §5's minimal contract. T1b template extraction will bind to whatever v1 stabilizes at; silent drift breaks T1b consumers.
- **Mitigation applied inline:** v1 stable-fields contract now frozen in `pa_tool_validate_harness.py` module docstring — 8 stable `expected_outcome` values, 9 stable per-action fields. Renaming/removing/type-changing requires MINOR version bump (`'v2'`) + substrate-arc-scoped SIGN.

No `future_trigger` folds this session.

---

## §8 — Post-merge sanity check

Fresh HEAD `bfc3dc61c` post-recycle:

```
python manage.py pa_tool_validate_harness ops_tool --check
→ "expected_outcome": "success"  (ops_tool.version, 49ms)
→ "expected_outcome": "success"  (ops_tool.recent_recycles)
→ "artifact_sha256": "eb930fc1d56242ec"
→ "read_only_dispatched": 2
```

Harness runnable from freshly-recycled state.

---

## §9 — Substrate arc status

- T1c ✓ shipped S2901 (PR #3427 at `e92bd807c`)
- T1a ✓ shipped S2902 (PR #3429 at `bfc3dc61c`) — this session
- T1b ← queued for S2903 or later; depends on T1a stable output schema (now frozen at v1)

Arc close estimate updated: T1a shipped in **1** session (vs ≤2 hard cap). T1b remaining: ~1-2 sessions. Total substrate arc: **~3** sessions actual (T1c 1 + T1a 1 + T1b ~1) vs ~4-5 initial estimate.

---

## §10 — Next session (S2903) first action

**Two candidates:**

1. **T1a Phase 2 harden** — the second session in T1a's ≤2 cap. Concrete work: (a) author metadata for a starter slice (~5-10 tools), (b) surface a real dispatch signal beyond the 2 ops_tool seeds, (c) fold real-run learnings back into the v1 contract if any drift surfaces. Low-risk; extends the freshly-shipped substrate.

2. **T1b template extraction** — MUST come after T1a, per parent §3 sequencing. Now unblocked (v1 contract frozen). Concrete work: canonicalize per-tool validation-doc section structure; add ratchet-and-warn gap-map lint. Ratchet fires on new-doc-authoring OR when a tool's covered-actions set changes.

**Recommend T1a Phase 2 harden** at S2903 open — the harness is minimal seed-only right now; without metadata authoring, the sweep-pace multiplier claim doesn't materialize in practice. Phase 2 adds enough metadata to make Phase 1's value visible before T1b rigidifies the template around T1a's output.

---

## §11 — D6 moratorium status

**D6 moratorium still in force.** No strategic discovery arcs opened. No opportunity portfolio expansions. No layer-boundary design work. S2902 was pure engineering substrate execution on the pre-ratified Row 161 arc plan.

---

## §12 — Rigby Tool Gap Ledger

No new entries this session. `TOOL_ACTION_METADATA` seeding provides substrate that removes future gap-log surface for the seeded actions (ops_tool.version + recent_recycles) — Rigby can now programmatically read their safety classification without asking Claude.
