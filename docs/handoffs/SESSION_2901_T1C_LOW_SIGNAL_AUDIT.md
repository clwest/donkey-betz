# Session 2901 — T1c Low-Signal Audit (Row 161 Substrate Arc Thread 1/3)

**Date:** 2026-07-22
**Session:** S2901
**Branch/PR:** `s2901-t1c-low-signal-audit` → **PR #3427** (merged as `e92bd807c`)
**Predecessor:** [SESSION_2900_ROW_161_SUBSTRATE_ARC_OPENED.md](SESSION_2900_ROW_161_SUBSTRATE_ARC_OPENED.md)
**Playbook:** v0.9.0 — unchanged
**Recycle cycle:** post-merge `make recycle-all` clean (sha=`e92bd807cf52`)

---

## §1 — Ship summary

First thread of the Row 161 substrate arc executed per S2900 Chris D-verdict Option A ratification. Locked sequencing: T1c first (fast pass, carves in-class boundary) → T1a (auto-harness build) → T1b (family-doc template).

T1c ship shape: doc-only edit populating the triage table + Action Metadata Map location decision + T1a MVP surface input. Fast-pass posture held (~5 min per tool, most triaged in under 2).

**PR shipped:** [#3427](https://github.com/clwest/donkey-betz-platform/pull/3427) merged at `e92bd807c` — `docs/audits/pa_tools/substrate/T1c_low_signal_audit.md` (+112 lines net).

**Twin workspace mirror** (Donkey Betz workspace `b4503364-2573-4401-9e28-61a739e0ce50`):
- Content mirror: `c9c0d8e2-41c3-4be5-8a44-8d55e78f6ca1` (`initiative_phase_doc` / `engineering`, status `completed`, diagnostic_status `cleared`)
- Ratification envelope: `40373e35-d063-4033-920e-e7d02b82aa7b` (`ratification_record` / `governance`, status `completed`, no diagnostic flags)

Rigby wrote both via `deliverable_tool.create` per feedback rule `feedback_rigby_writes_workspace_deliverables`.

---

## §2 — Triage results (54 unique rows)

### Bucket totals

| Bucket | Count | Notes |
|---|---|---|
| `close_with_short_note` | 8 | 7 doc-unknown tools + `autopilot_tool` (Slice 1.5b already queued) |
| `promote_to_sweep` | 2 | `ops_tool` (18/20 unverified), `workspace_tool` (false-positive validated_partial) |
| `defer_indefinitely` | 0 | — |
| `out_of_class_agent` | 44 | all agent-via-run_agent tools |
| **Total** | **54** | — |

### Count reconciliation (author correction to parent §1)

Parent §1 said "14 low-signal tools (7 doc-unknown + 3 partial + 4 doc-only ops)". Fast-pass established: the 4 doc-only ops tools (`agent_introspection_tool`, `kb_tool`, `search_docs`, `ops_tool`) are **not a separate bucket** — they already reside in the doc-unknown / partial groups per PA_TOOLS_GAP_MAP.md HEAD `7891ee9c`. Unique Group A = **10 tools**, not 14. (Whether "14" was a double-count or phrasing choice is not provable from the gap map itself — Rigby SIGN correction.)

### Group B rationale

All 44 `agent_via_run_agent` tools bucket as `out_of_class_agent` because `run_agent` is intercepted at `core/services/unified_pa_entrypoint.py:2236` BEFORE the dispatcher (`if tool_name == 'run_agent': actual_tool_name = arguments.pop('agent_name', tool_name)`). These 44 handlers have **no PA schema** — the LLM cannot invoke them directly. Their validation surface is BaseAgent-level, not PA-tool-invariant. Explicitly removed from PA tools sweep + harness surface.

Agent-substrate validation as a peer arc: flagged as follow-on; not opened; not queued. Requires Chris directive.

---

## §3 — Action Metadata Map location decision

**Candidate A confirmed** (per parent §4 default + Rigby S2900 SIGN lean).

**Exact location:** `core/services/tool_action_metadata.py` — one module registering a `TOOL_ACTION_METADATA` dict keyed by `(tool_name, action)` tuples. Minimum viable field set for T1a MVP:

- `safety_class`: `Literal['READ_ONLY', 'WRITE_GATED', 'MUTATION', 'IRREVERSIBLE']`
- `applicability`: `Literal['always', 'conditional', 'gated']`
- `notes`: free-form string

File to be created at T1a. T1c is design-decision only (Rigby verified file does not yet exist).

---

## §4 — T1a MVP surface (post-T1c inputs)

- **In-class tools for harness:** 96 (94 untested + 2 T1c-promoted: `ops_tool` + `workspace_tool`)
- **Out-of-harness explicit:** 45 (44 `agent_via_run_agent` + 1 `run_agent` meta)
- **Close_with_short_note tools (8):** remain in-class; harness re-verifies against existing validation reports
- **Harness action-count target:** ~300-450 actions across 96 tools; refined at T1a Phase 1 scaffold

---

## §5 — Rigby SIGN cycle

**Two-turn cycle.** First turn: Rigby ran 4 tool calls (`search_docs` + `repo_tool.search/read_file/tree`) and returned MODIFY on 4 of 5 claims, flagging "not tool-verified yet." Second turn (after tighter directive): Rigby ran 6 verification tool calls with file+line evidence and returned 4 AGREE + 1 MODIFY (Claim 1 wording only) + composite MODIFY on the same rewording.

**Verified per PLAYBOOK-6.10.9 evidence admission rule:** every AGREE carries a file+line pointer:
- Claim 2 (`run_agent` interception): `core/services/unified_pa_entrypoint.py:2236-2237`
- Claim 3 (`ops_tool` 18/20 unverified): `docs/research/tools/validation/ops_tool_validation.md:25-26, 147`
- Claim 4 (`workspace_tool` false positive): `docs/research/tools/validation/workspace_retrieval_validation.md:5-7` + search returned 0 matches for `workspace_tool`
- Claim 5 (`tool_action_metadata.py` does not exist): `file_not_found` error on read attempt

**Not rubber-stamped.** Rigby's first-turn honesty ("MODIFY: not tool-verified") + Fold B (schema↔doc parity gap) prevented shipping the T1c doc with unverified claims.

---

## §6 — Zoom-out folds (per PLAYBOOK-6.10.7 zoom-out ask rule)

Four folds captured. All classified + landed per PLAYBOOK-6.10.8 fold classification SIGN discipline.

| Fold | Concern | Classification | Landing |
|---|---|---|---|
| A | `run_agent` rewrite (`actual_tool_name` after arg pop) may confuse harness telemetry into treating agent tools as directly invoked | `future_trigger` | T1a Phase 1 — add exclusion filter + regression test |
| B | `close_with_short_note` tools may have schema drift; heading-fix alone would misclassify as `validated_full` while real coverage gaps persist | `future_trigger` | T1a Phase 0 — add `pa_tool_validate_harness --check-doc-schema-parity` gate; auto-escalate mismatches to sweep |
| C | Gap-map regeneration mid-T1a-scaffold could flap the 96 in-class count | `same_pr_mitigatable` | Mitigated at §7.0 by pinning HEAD `7891ee9c` |
| D | `validated (full)` is a doc-status label; may mask low runtime coverage (e.g., `ops_tool` case) | `future_trigger` | T1a §2 anti-goals — harness verifies all in-class regardless of doc-status |

None of Folds A/B/D require substrate-arc-scoped SIGN or expand T1c scope; they carry forward as T1a scope inputs. Fold C closed inline.

---

## §7 — Follow-on carry (to T1a)

- **Doc heading fix pass** (T1a Phase 0, doc-only): 8 tools need `## Covered actions` heading added so the classifier re-categorizes them from `doc-unknown` / `partial` to `validated_full`. Bundling into T1a Phase 0 scaffold PR is Rigby's preference at T1a open.
- **`ops_tool` + `workspace_tool` sweep slots:** promote into standard sweep queue after T1a harness ships; both benefit from harness auto-execution.
- **Agent-substrate validation as peer arc:** flagged §2; requires Chris directive; not opened.
- **Fold A/B/D T1a Phase requirements:** carried forward as scope-inputs (not scope-expansion).

---

## §8 — Ledger + arc state

**Ledger status (unchanged from S2900):**
- Row 161 → OPENED as substrate arc; T1c (thread 1/3) shipped this session.
- Row A `mitigated` (PR #3419 S2897).
- Row B `mitigated` (PR #3421 S2898).
- Row C `mitigated` (PR #3417 S2896).
- Row #29 `mitigated` (PR #3423 S2899).
- Deferred rows 27/28/30 unchanged.

**Arc progress (Row 161):**
- Thread 1/3 (T1c) — **shipped this session (PR #3427)**
- Thread 2/3 (T1a auto-harness) — S2902 first action; MVP-strict; ≤2 sessions
- Thread 3/3 (T1b family-doc template) — after T1a; 1-2 sessions

**Substrate-arc estimate:** ~4-5 sessions total (T1c already done → ~3-4 remaining). Post-substrate sweep pace target: **~10-15 sessions** for remaining ~76 tools (vs ~50 at current-shape pace).

---

## §9 — What's next (S2902 first action)

**T1a auto-harness — scaffold phase.**

Sequencing locked per S2900 Chris D-verdict Option A ratification. Do NOT open before T1c completes — this session completed T1c, so T1a is unblocked.

**T1a MVP boundaries** (parent §5 + T1a §2 anti-goals):
- Django mgmt command `pa_tool_validate_harness`
- In-process dispatch (not HTTP)
- READ_ONLY auto-executes only; per-action safety classifier via `TOOL_ACTION_METADATA`
- Action Metadata Map micro-thread (create `core/services/tool_action_metadata.py`)
- Session cap: ≤2 (scaffold + harden)

**T1c-inherited scope inputs:**
- 96 in-class tools for harness (94 untested + 2 T1c-promoted)
- Fold A: exclude `run_agent`-rewritten calls from harness surface (regression test at Phase 1)
- Fold B: `--check-doc-schema-parity` gate at Phase 0 doc-heading-fix pass
- Fold D: harness verifies all in-class regardless of doc-status (anti-goal in T1a §2)

**Anti-scope-creep watchlist** (from parent + T1a doc): async / pagination / golden-files / multi-auth / rate-limit / orchestration. If any surface, defer as substrate-follow-on rows.

**What's forbidden at S2902** (D6 moratorium still in force):
- No strategic discovery arcs. No opportunity portfolio expansions. No layer-boundary design arcs.
- No T1b before T1a completes.
- No scope changes during T1a execution without substrate-arc-scoped SIGN.

---

## §10 — Session close mechanics

- ✅ T1c doc updated (§7 triage + §8 metadata + §9 T1a input + §10 follow-on + §11 folds)
- ✅ PR #3427 shipped + merged at `e92bd807c`
- ✅ `make recycle-all` post-merge (PLAYBOOK-7.4.4 discipline, recycle_events.jsonl updated)
- ✅ Twin workspace mirror written by Rigby (content mirror `c9c0d8e2` + ratification envelope `40373e35`)
- ✅ Session handoff (this doc)
- ✅ 00-START-NEXT-SESSION.md refresh (T1a as S2902 first action)
- ✅ session_lifecycle close (fresh S2902 pin + wrapper rewrite)
- ✅ Close cascade PR + post-merge recycle + wrapper pin commit

---

## §11 — References

- **Parent arc scoping:** `docs/audits/pa_tools/substrate/S2900_substrate_arc_scoping.md`
- **T1c doc (this session):** `docs/audits/pa_tools/substrate/T1c_low_signal_audit.md`
- **T1a design (next session):** `docs/audits/pa_tools/substrate/T1a_auto_harness.md`
- **T1b design (deferred):** `docs/audits/pa_tools/substrate/T1b_family_doc_templates.md`
- **Gap map (pinned):** `docs/audits/PA_TOOLS_GAP_MAP.md` HEAD `7891ee9c` at triage
- **S2900 handoff (predecessor):** `docs/handoffs/SESSION_2900_ROW_161_SUBSTRATE_ARC_OPENED.md`
- **Rigby Tool Gap Ledger:** deliverable `5c84e75a-0ce5-4f93-9da5-f6db4e53e7f0` (Donkey Betz workspace)
