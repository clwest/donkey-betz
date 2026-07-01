---
title: Session 1275 — Symbol Mapping Event Schema Design (S1274 commit + S1275 draft)
session: 1275
date: 2026-07-01
status: closed
scope: research + doc (no code changes)
committer: claude
pa_pin: pa-cbcc410b32714f60 (shared with S1268-S1274 arc)
---

# Session 1275 — Symbol Mapping Event Schema Design

## What shipped

**Part 1 (S1274 commit follow-through).** Committed the S1274 doc
`docs/research/symbol_mapping_option_selection_design.md`
(Option E — evidence-only — selected as v0 recommendation) along
with the ARCHITECTURE_INDEX v6 update registering it as §1.10.
Commit hash: `52ec6b54` on branch
`docs/session-1274-symbol-mapping-option-selection`.

**Part 2 (S1275 event schema draft).** Drafted the successor
mission's design-preparation doc:
`docs/research/symbol_mapping_event_schema_design.md` (1283 lines,
18 sections). Registered as ARCHITECTURE_INDEX §1.12 (v8 bump).

## Doc summary

The S1275 doc closes ARCHITECTURE_INDEX §5.2d gap. It takes
S1274's Option E v0 recommendation and pins the concrete event:

- **Canonical event name:** `authority_action_observed`
- **Host surface:** two-surface stream — `OpsRunEvent.data['authority_action_observed']`
  for mission-scoped emissions + `ToolCallRecord.parameters['authority_action_observed']`
  for non-mission tool calls — unified via a new
  `authority_action_observed_stream` DB view (`UNION ALL`)
- **Payload:** 21 fields across 4 tiers (7 required + 5
  semi-required + 6 optional + 3 reserved). Hard cap 1024 bytes
  total; `debug_context` capped at 128B. Reserved-keys policy
  strips unknown keys with invariant warning.
- **First cohort:** 4 v0 emitters (MissionRunner preflight,
  MissionRunner step lifecycle, ToolDispatcher execute,
  employee_tool run_now) + 1 v0 first consumer (Bug Triage step 4)
- **`mapping_confidence` enum:** {DEFINITE (emitter-local
  certainty, *not* canonical truth), DECLARED (coverage-only,
  *never* authoritative — renamed from earlier draft's INFERRED
  per Rigby SIGN), HEURISTIC (reserved, banned in v0), UNKNOWN
  (honest NULL)}
- **Actor roles:** 3 S1271 roles + 1 graph position + 1 identity
  marker — `executor_actor` / `sponsor_actor` / `principal_user_id`
  (roles) + `caller_actor` (graph position, populated only when
  distinct from sponsor) + `employee_handle` (Employee OS identity
  marker)
- **Drift stack (6 patterns):** NULL rate monitor + zero-fire
  audit (forks S1245 `audit_celery_zero_fire.py`) + weighted
  cross-emitter disagreement (emits `suspected_mislabel`, never
  "producer X wrong" without adjudication) + weekly sampled-truthing
  loop (new — reviewer emits `authority_mapping_correction` events;
  `correction_rate` KPI) + invariant validator I1–I7 (payload
  key policy + impossible actor-combo prevention) + schema-signature
  check on tool-schema declarations
- **3 golden flows:** GF-1 Documentation Manager audit run;
  GF-2 PA-invoked `deliverable_tool.list`; GF-3 `employee_tool
  run_now` for Bug Triage (includes consumer read)
- **Rollout:** 5 phases across ~10 weeks P0→exit observation window
- **15 out-of-scope items**, incl. LLM-based action_class inference,
  real-time dashboard, WebSocket/Spider/Fleet producers, enforcement
  (warn-mode only at v0)

## Rigby SIGN fold summary

Rigby returned SIGN-with-edits — 8 must-fixes + bonus #9. All folded:

1. **MF1 (high):** ambient OpsRun rejected → two-surface pattern +
   `authority_action_observed_stream` UNION view
2. **MF2 (medium):** drop required `event_id` → optional
   `idempotency_key` for async emitters
3. **MF3 (medium-high):** kill free-text `notes` → 128B-capped
   `debug_context`; downscope `producer_version` from required
   to canary-only
4. **MF4 (high, long-term):** rename `delegator_actor` →
   `caller_actor`; frame as graph position not 4th role; §9.1
   redesigned around 3 roles + 1 graph position + 1 identity marker
5. **MF5 (medium):** reframe "5 v0 producers" → "4 v0 emitters + 1
   v0 first consumer"; Bug Triage step 4 removed from payload
   `producer` enum
6. **MF6 (medium):** rename `INFERRED` → `DECLARED`; §11.1 adds
   explicit non-authoritative rule; DECLARED never used for
   enforcement or cross-source truthing
7. **MF7 (medium):** add sampled-truthing loop (§12.3 D2.3) —
   catches stable-wrong-non-NULL that other stack layers miss
8. **MF8 (medium-high):** DEFINITE ≠ canonical truth; cross-source
   reconciliation emits `suspected_mislabel` on divergence, requires
   separate adjudication before marking any producer wrong
9. **Bonus 9:** reserved-keys policy + per-field size caps +
   invariants I6 (caller_actor ≠ sponsor_actor) + I7 (no unknown
   payload keys)

## Files touched

- `docs/research/symbol_mapping_event_schema_design.md` (new — 1283 lines)
- `docs/research/ARCHITECTURE_INDEX.md` (updated to v8: §1.12
  registration, §5.2d closure, §5.2e implementation-slot, §8
  timeline S1275 row, §9 roadmap STAGE 4 CLOSED + STAGE 5 no-P0)
- `docs/handoffs/SESSION_1275_SYMBOL_MAPPING_EVENT_SCHEMA_DESIGN.md`
  (this handoff)

**Dismissed (belongs to another Claude Code session):**
`docs/research/platform/` directory. Not part of this commit.

## What's next

**Blocked on Chris canonical sign-off** of §1.12 before any
implementation PRs. Once ratified, §5.2e sequences the 5-phase
rollout across ~10 weeks.

**No P0 in front of STAGE 5.** Chris picks between:
- **STAGE 5 §5.3** Trust Propagation Model (P1)
- **STAGE 5 §5.4** Employee Boundary Escalation Contract (P1)
- Whole-platform arc top-3 per §1.9 §9 — Revenue Pipeline canonical
  architecture (§5.12), Observability Deduplication Audit (§5.13),
  Sports/DBAO ↔ AI Studio Integration Sketch (§5.14)

All parallel-safe if pursued independently.

## PA pin

Shared arc pin `pa-cbcc410b32714f60` (S1268 through S1275).
Session state: 8-10 turns / research-only session (not health-scored
because tool surface not stressed). Continue at rotation.
