# Phase-0 Corpus — Label Schema v0 (Field Dictionary)

**Frozen at:** 2026-07-18 (S2822 Phase-0 execution, Step 1.5 checkpoint per Rigby SIGN Q5 pushback #3)
**Source of truth:** `docs/research/implementation/RATIFICATION_2026-07-18_s2822_phase0_methodology_ratified_r1_r6.md` §5 step 2
**Precedent:** S2821 §7.3 label schema (four Rigby refinements — strict/loose target, answer_mode, has_literal_identifier, COUNT elevated)

> Any schema change after v0 freeze requires an amendment note in the ratification envelope AND versioning to v1 (do not silently mutate v0 rows midstream).

---

## Purpose

This dictionary is the single-page ground truth for the field set applied to every row in `corpus.json`. Authors reference this file — not the envelope — when labeling rows. Envelope §5 step 2 is authoritative; this file is a working restatement optimized for authoring speed.

---

## Row structure — all fields (v0)

Every row is a JSON object with the fields below. Missing-required-field = row invalid.

### Core identity + text (2 fields — required always)

| Field | Type | Required | Description |
|---|---|:---:|---|
| `query_id` | string | ✅ | Unique short label. Prefix convention: `Q`/`C`/`P`/`I`/`S`/`K`/`A` + integer. Prefix hints intended_family but does not authoritatively bind it (e.g., `Q1`, `P3`, `A2`). |
| `query_text` | string | ✅ | Exact query text as harvested/authored. NO paraphrase. If harvested from a real source, preserve original casing/punctuation. Small variations flip retrieval — do not normalize. |

### Family + relationship (3 fields — required if applicable)

| Field | Type | Required | Description |
|---|---|:---:|---|
| `intended_family` | enum | ✅ | Primary family from working taxonomy: `COUNT` / `PROCEDURAL` / `DISCOVERY` / `IDENTITY` / `SELF-REFERENCE` / `CONCEPTUAL`. Taxonomy is WORKING, not constitutional (per S2821 §7.1 + R6). |
| `secondary_family` | enum | optional | Set only if query is genuinely ambiguous (maps to 2 families with roughly equal plausibility). Same enum as intended_family. |
| `expected_behavior` | enum | ✅ | One of: `return-target` (specific doc/pointer expected) · `return-any-of-list` (any of loose target set is OK) · `abstain` (deterministic non-answer expected) · `return-none` (no result expected). |

### Answer mode (1 field — required)

| Field | Type | Required | Description |
|---|---|:---:|---|
| `answer_mode` | enum | ✅ | Encodes IS-ness/aboutness: `IS_DOC` (this doc IS the answer — e.g., "2701_docs_inventory_topology_audit" → return the file itself) · `ABOUT_TOPIC` (returned docs should discuss the topic — e.g., "explain Colorado JDF form selection") · `POINTER_DOC` (returned doc should be a pointer/nav to the answer — e.g., "00-START-NEXT-SESSION" → return CLAUDE.md#6 pointer chunk, not 00-START itself). |

### Truth labels — targets (2 fields — required per §5 step 2 discipline)

| Field | Type | Required | Description |
|---|---|:---:|---|
| `known_correct_target_strict` | list[string] OR null | conditional | Must-hit target(s) — document paths, filenames, or content stems. MAY be null ONLY when `expected_behavior` is not `return-target` OR `return-any-of-list` (e.g., COUNT/PROCEDURAL asks judgeable without a specific canonical target). For DOC/POINTER asks, manual labeling required — do NOT substitute `observed_live_result_target` for truth. |
| `known_correct_target_loose` | list[string] OR null | conditional | Acceptable alternative(s) beyond strict. Same NULL rules as strict. When strict is [X], loose may be [X, Y, Z] where Y/Z are second-best correct answers. |

### Derived + auxiliary (2 fields)

| Field | Type | Required | Description |
|---|---|:---:|---|
| `has_literal_identifier` | bool | ✅ (derived) | True if query contains a literal filename/path/stem (e.g., "2701_docs_inventory_topology_audit" or "CLAUDE.md" or "00-START-NEXT-SESSION"). Cheap classifier feature for IS_DOC prediction. Derived at label time; not authored. |
| `label_rationale` | string | ✅ | One-sentence explanation of intended_family + target-set choice. Keeps labeling reviewable + argueable. |

### Consequence + safety (2 fields)

| Field | Type | Required | Description |
|---|---|:---:|---|
| `misroute_consequence` | enum | ✅ | `HIGH` / `MEDIUM` / `LOW`. Per S2821 §7.6 + Rigby COUNT-elevation: COUNT/IDENTITY/SELF-REFERENCE default HIGH; PROCEDURAL default MEDIUM; DISCOVERY/CONCEPTUAL default LOW. Author may override with rationale. |
| `safety_level` | enum | optional | For PROCEDURAL-destructive rows only: `destructive` / `irreversible` / `safe`. Empty for non-PROCEDURAL. |

### R1 provenance extension (5 fields — required for R1 compliance)

| Field | Type | Required | Description |
|---|---|:---:|---|
| `provenance_tier` | enum | ✅ | `P1` (real operational query harvested from actual platform work) · `P2` (observed failure case from prior sessions) · `P3` (synthetic — must have gap_filled). Per Chris R1 hierarchy. |
| `provenance_source` | string | ✅ | Harvest source label. Controlled vocab: `handoff_grep` (grep of docs/handoffs/) · `handoff_rg` · `rigby_conversation_search` · `zoom_out_ledger` · `s2818_baseline` · `s2819_baseline` · `s2820_baseline` · `s2821_baseline` · `synthetic_gap` · other with justification in label_rationale. |
| `provenance_pointer` | string | ✅ | Pointer to source: URL, doc path, conversation id, session number, or ledger row ts. Enables audit of where the query came from. |
| `origin_session` | int | optional | Session number when query was first observed/failed (P2) or authored (P3). Empty for P1 harvests without a specific originating session. |
| `gap_filled` | string | conditional | REQUIRED if `provenance_tier=P3`. Free-text description of which coverage gap this synthetic row fills (e.g., "CONCEPTUAL family had 0 rows after P1+P2 harvest — this row exemplifies typical conceptual ask"). EMPTY if tier=P1 or P2. |

### Baseline observation (1 field — separate from truth per Rigby Q4)

| Field | Type | Required | Description |
|---|---|:---:|---|
| `observed_live_result_target` | list[string] OR null | optional | What live retrieval returned when the query was harvested/probed. Explicitly NOT truth — used only for post-hoc baseline analysis (how much did the routing decision change vs current behavior?). Do NOT reference this field during classifier evaluation scoring — it is baseline observation, not ground truth. |

---

## Total field count

**16 fields** — 2 identity/text, 3 family/relationship, 1 answer_mode, 2 truth targets, 2 derived/aux, 2 consequence/safety, 5 R1 provenance, 1 baseline observation.

## Validation rules

1. Every row MUST have all fields required in the table above. NULL is permitted only where explicitly allowed.
2. `provenance_tier=P3` → `gap_filled` MUST be non-empty.
3. `intended_family=PROCEDURAL` + destructive intent → `safety_level` MUST be set.
4. `expected_behavior=return-target` OR `return-any-of-list` → `known_correct_target_strict` MUST be non-null (labor cost: manual labeling per Rigby Q4 discipline) UNLESS `secondary_family` is set (indicating AMBIGUOUS ground-truth — no single canonical target recoverable without context; correct classifier outcome is AMBIGUOUS or CONTEXT_NEEDED, and `known_correct_target_loose` documents the candidate targets IF the classifier attempts an answer).
5. `known_correct_target_loose` (when set) MUST be a superset of `known_correct_target_strict` (loose ⊇ strict).
6. `secondary_family` (when set) MUST NOT equal `intended_family`.
7. `has_literal_identifier` derivation rule: True if query contains any of `.md`, `.py`, `.json`, or matches regex `\b[A-Z_0-9]{4,}\b` (uppercase-heavy tokens likely to be filenames/stems), OR contains any path-like `/` character.

## Enum values (canonical set)

- **intended_family / secondary_family:** `COUNT` · `PROCEDURAL` · `DISCOVERY` · `IDENTITY` · `SELF-REFERENCE` · `CONCEPTUAL`
- **expected_behavior:** `return-target` · `return-any-of-list` · `abstain` · `return-none`
- **answer_mode:** `IS_DOC` · `ABOUT_TOPIC` · `POINTER_DOC`
- **misroute_consequence:** `HIGH` · `MEDIUM` · `LOW`
- **safety_level:** `destructive` · `irreversible` · `safe` · (empty)
- **provenance_tier:** `P1` · `P2` · `P3`
- **provenance_source:** `handoff_grep` · `handoff_rg` · `rigby_conversation_search` · `zoom_out_ledger` · `s2818_baseline` · `s2819_baseline` · `s2820_baseline` · `s2821_baseline` · `synthetic_gap` · other-with-justification

---

## Change log

- **v0** (2026-07-18 S2822 Phase-0 Step 1.5 freeze): initial publication. 16 fields total. R1 provenance extension applied per Rigby SIGN Q3 (flat over nested). Truth-vs-observation separation per Rigby SIGN Q4. `has_literal_identifier` derivation rule specified.
