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

## Continue-research options (post-S1275)

**The meta-observation from the S1268-S1275 arc.** After years of
building the platform, we now have enough architectural coverage to
spot **repeatable patterns** the research process itself has
surfaced — and those patterns will make future work easier for
everyone (Chris, Rigby, future Claude Code sessions, and any human
who joins later). Examples the research arc has already produced:

- **Design-preparation as its own class of doc** (S1268-style
  architectural discovery → S1272-style design-space enumeration →
  S1274-style option selection with evidence → S1275-style concrete
  spec). This 4-phase cadence should be reused, not reinvented.
- **The verifier loop** (independent grep/ORM/file-read check of
  every research claim before landing). Caught S1274 EventBus drift
  and S1275 producer-vs-consumer framing errors before ship.
- **Rigby SIGN-with-edits as a first-class review type.** Every
  arc doc since S1269 has been strengthened by 2-8 must-fix folds.
  The pattern should be codified — `DOMAIN_RESEARCH_PLAYBOOK.md`
  (§1.11) already starts this, but it can go further.
- **The two-surface + UNION view pattern** (S1275 §5) as a
  general-purpose way to reconcile "the honest place each event
  lives" with "the single logical stream consumers read." This is
  a *reusable architectural primitive*, not just an
  authority-observation trick.
- **DECLARED-vs-DEFINITE-vs-UNKNOWN as a three-tier confidence
  vocabulary** with explicit non-authoritative rules. Same shape
  should reappear in any future evidence-based system.
- **Sampled-truthing as the mitigation for stable-wrong-non-NULL.**
  Applies to every downstream system that populates a semantic
  label from a declared source.

**Immediate continue-research candidates** (Chris picks):

1. **STAGE 5 §5.3 — Trust Propagation Model** (P1). Inter-employee
   trust contract; today only per-employee trust exists.
2. **STAGE 5 §5.4 — Employee Boundary Escalation Contract** (P1).
   HAI escalation shape across employee boundaries.
3. **STAGE 5 §5.5 — Cross-Employee Scheduling** (P2). Depends on
   §5.3 + §5.4 + §5.6.
4. **STAGE 5 §5.6 — Mission Composition** (P1). Canonical
   idempotency key across orchestration paths.
5. **Whole-platform arc §5.12 — Revenue Pipeline canonical
   architecture doc** (P1). Rigby caught this as biggest missing
   platform subsystem at S1273 SIGN.
6. **Whole-platform arc §5.13 — Observability Deduplication
   Audit** (P1). EventBus stream count drift caught during S1268
   is the tip of a broader ambiguity.
7. **Whole-platform arc §5.14 — Sports/DBAO ↔ AI Studio
   Integration Sketch** (P1). Two sides do not compose today
   (`sports_odds` is not a valid SignalCluster data_type).
8. **New: Research-methodology synthesis** (P2). Codify the
   repeatable patterns above into an extension of
   `DOMAIN_RESEARCH_PLAYBOOK.md` (§1.11). Same-session self-audit
   that would formalize what S1268-S1275 discovered as a *process
   pattern library*, alongside the *architecture pattern library*.
9. **New: `authority_action_observed_stream` view pattern
   generalization** (P2). Extract the two-surface + UNION view
   idea as a reusable ADR/pattern doc — applicable to any future
   evidence stream that has mixed hosts.
10. **New: DEFINITE-vs-DECLARED-vs-UNKNOWN confidence-tier ADR**
    (P2). Same as above but for the confidence-vocabulary pattern.

All parallel-safe if pursued independently. Chris picks by
preference or by which pattern is closest to a real blocker.

## Why merge to main before picking

Reading the `docs/research/` directory should tell any observer —
Chris, Rigby, future Claude Code, or a human onboard — **exactly
what docs exist**. Keeping S1275 on a feature branch means the
next session that runs `ls docs/research/` sees only S1274-era
files and starts reasoning from an incomplete picture. Merging
now:

- Makes §1.12 discoverable via the on-main `ARCHITECTURE_INDEX.md`
- Puts the S1275 handoff in `docs/handoffs/` where future sessions
  actually look
- Removes the "which branch is authoritative?" question
- Frees the next research session to fork from a clean main

## PA pin

Shared arc pin `pa-cbcc410b32714f60` (S1268 through S1275).
Session state: 8-10 turns / research-only session (not health-scored
because tool surface not stressed). Continue at rotation.
