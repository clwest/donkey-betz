---
title: "Phase-0.5 — Feature-Flag Advisory-Only Router Scaffolding Design (Rigby SIGN 3-round CLEARED — routes to Chris D-verdict)"
status: post-Rigby-SIGN-3-round-cleared (cycle 1: 19 refinements + 1 F-BLOCKING; cycle 2: 2 fixes + 1 F-BLOCKING advisory-only-vs-execution boundary; cycle 2 CLEAR + 1 nit; 22 total refinements applied same-session; 0 F-BLOCKING remaining)
authority: design — not implementation; binds under B3 §10.7 discipline
session: 2823
generated: 2026-07-18
supersedes: none
related:
  - docs/research/discovery_layer/PHASE_0_5/BALANCED_P1_HARVEST_PLAN.md   # sister — Chris D-verdict gates this build
  - docs/research/discovery_layer/PHASE_0_5/ABSTAIN_POLICY_PROPOSAL.md   # abstain policy this scaffolding implements
  - docs/research/discovery_layer/PHASE_0/classifier_a.py   # decision engine (best HIGH-consequence F1 + zero wrong-but-plausible)
  - docs/research/implementation/RATIFICATION_2026-07-18_s2822_phase0_methodology_ratified_r1_r6.md   # §9 R2 instrumentation spec + Chris R2 advisory-only guardrail
  - core/services/td_handlers_ops.py   # kb_tool.semantic_search handler at :5905
  - docs/handoffs/SESSION_2822_PHASE0_TO_DOCS_AUDIT_BRIDGE.md   # §5.3 B2 scaffolding scope
scope:
  Designs the feature-flag advisory-only dogfood router scaffolding for the Phase-0.5 dogfood pilot. Design-only — no implementation until BALANCED_P1_HARVEST_PLAN + ABSTAIN_POLICY_PROPOSAL both Chris-ratified.
non_goals:
  - Building the scaffolding before Chris ratifies B1 + B3
  - Substrate code change to lexical top_k policy (frozen)
  - Auto-flipping semantic default (deferred per S2821)
  - Applying router to any call-site beyond kb_tool.semantic_search (single instrumentation point per bridge §5.3 B2)
  - Producing routing decisions the actual search behavior depends on (advisory-only per Chris R2)
---

# Phase-0.5 Feature-Flag Advisory-Only Router Scaffolding Design

**Design spec — no build. Implementation gated on Chris D-verdict RATIFY of BALANCED_P1_HARVEST_PLAN + ABSTAIN_POLICY_PROPOSAL.**

## §1 — What "advisory-only" means (Chris R2 + B3 §10.7 discipline)

Per Chris R2 in the S2822 D-verdict + Chris B3 §10.7 "no router build may weaken the ratified no-fusion, abstention, evidence-persistence, or integrity-stop rules":

- Router runs on the incoming query BEFORE the retrieval executes
- Router's predicted family + categorical confidence (HIGH/MEDIUM/LOW per B3 §10.4) + abstain outcome is LOGGED to durable persistence (per B3 §10.6.2 — NOT ephemeral logs alone)
- Router's advisory hint is optionally exposed to the caller in the response envelope as `_router_advisory` metadata (per B3 §10.1 no-fusion; NOTE: in Phase-0.5 advisory-only, parallel-both is LOGGED as the advised option but NOT EXECUTED — see §7 CRITICAL SCOPE DISTINCTION for the reserved future shape gated on separate Chris D-verdict)
- The actual retrieval substrate selection + parameters do NOT change based on router output
- Any UI/envelope presentation that fuses, interleaves, or cross-reranks substrates violates B3 R6 and triggers §10.5 integrity stop
- If the flag is off, ZERO behavior change (no logging, no metadata, no classification)

This preserves the current-best retrieval path as the ground truth for Phase-0.5 measurement while collecting router decisions as instrumentation data.

## §2 — Feature flag + measurement window configuration

### §2.1 Feature flag

**Setting:** `settings.PHASE_0_5_ROUTER_ENABLED` — bool, default `False`.

**Location:** `core/settings.py` — added near other feature-flag settings.

**Environment override:** `PHASE_0_5_ROUTER_ENABLED=true` env var opts local dev in without hard-coding.

**Off-behavior guarantee:** If flag is False, `search_embeddings` call path is byte-identical to current behavior. No classifier import, no logging, no envelope field additions.

### §2.2 Measurement window configuration (per B3 §10.6.1 Chris "measurement window" reframing)

Chris B3 R3 wording uses "measurement window" rather than "session" for the CONTEXT_NEEDED clarify-cap flip rule. A measurement window is a defined analysis interval that may or may not align with a session.

**Setting:** `settings.PHASE_0_5_MEASUREMENT_WINDOW` — string enum, default `"session"`.

**Enum values:**
- `"session"` — window = single Rigby conversation session (bounded by pin lifecycle)
- `"rolling_n"` — window = rolling N routed queries (N configurable via `PHASE_0_5_MEASUREMENT_WINDOW_N`, default 20)
- `"harvest_phase"` — window = named harvest phase (bounded by explicit start/end events written to durable log)
- `"dogfood_observation"` — window = named dogfood observation period (bounded by explicit start/end events)

**Runtime state:** Router maintains window-scoped counters (clarify_count, routed_count, ambiguous_count, unclassifiable_count, etc.) for the currently active measurement window. Counters reset at window boundary.

**Persistence:** Window boundary events (start/end) written to durable log per §6 discipline so post-hoc analysis can reconstruct window scope + apply flip rules retroactively for audit.

### §2.3 Window boundary discipline (per Rigby SIGN Q2 R1+R2+R3)

**R1 — Bind-at-decision-time rule:** Each router event is bound to the measurement window that is ACTIVE at the MOMENT the router decision is made (i.e., before retrieval executes). Window transitions during retrieval do NOT retroactively rebind in-flight events. This makes in-flight events safe against window boundaries.

**R2 — Rolling_n boundary behavior:** No special carryover is needed for `rolling_n` mid-conversation boundaries. Each event carries its own `measurement_window_id` (per §6 schema). When the current window closes, the next query gets a new `window_id`. Counter state resets at boundary; historical events remain bound to their original window.

**R3 — Clarify-cap flip rule scope (per B3 R3):** The CONTEXT_NEEDED clarify-cap flip rule applies **within a `measurement_window_id`**, NOT "within a session" — even when the window type is `session`. This preserves the ratified "window" concept and avoids accidental coupling back to session pins. Flip state persists in window-scoped state; resets at window boundary.

## §3 — Single call-site instrumentation

**File:** `core/services/td_handlers_ops.py`
**Line:** `:5905` (kb_tool `semantic_search` action handler)

**Why only this call-site:** matches bridge §5.3 B2 instrumentation-point specification. `kb_tool.semantic_search` is the highest-volume Rigby retrieval-intent endpoint; instrumenting here captures the operator-in-tool-loop query dialect Phase-0.5 balanced P1 harvest is designed to characterize.

**Deferred-adjacency list (per Rigby SIGN Q1 R1+R2 — controlled expansion policy):**

Instrumenting the following retrieval-intent tools is EXPLICITLY DEFERRED to a Phase-0.5 revision request (Rigby SIGN + Chris D-verdict) — NOT opportunistically added during implementation:

| Adjacent call-site | Handler location | Retrieval semantics | Deferred rationale |
|---|---|---|---|
| `kb_tool.search_embeddings` | `td_handlers_ops.py:5877` (`elif action == 'search_embeddings':`) | text icontains + content_type filter over `UnifiedEmbedding` | Different retrieval semantics from semantic_search; comparability requires separate corpus + calibration |
| `search_docs` | `td_handlers_ops.py:~6011` | token-overlap over `.rag/corpus.jsonl` (local-file, not DB) | Local-file substrate; distinct measurement question from DB-embedding-based retrieval |
| `conversation_tool.search` | elsewhere in `td_handlers_ops.py` | semantic over past conversations | Conversation-domain retrieval; separate operator-intent distribution |
| `deliverable_tool.search` | elsewhere | structured field query over `Deliverable` model | Structured-query, not text-retrieval; likely out of Phase-0.5 scope entirely |

**Expansion gate:** Any attempt to co-instrument or add router advisory to these call-sites during Phase-0.5 build without a preceding SIGN cycle + Chris D-verdict is a §12 T1-adjacent integrity-stop trigger (opportunistic scope expansion violates B3 §10.7 downstream discipline).

## §4 — Router execution flow (per-query)

```
kb_tool semantic_search action handler receives payload
  │
  ├─ if settings.PHASE_0_5_ROUTER_ENABLED is False:
  │    └─ execute current search_embeddings → return current envelope
  │
  └─ if settings.PHASE_0_5_ROUTER_ENABLED is True:
       │
       ├─ Router.classify(query) → (predicted_family, confidence, all_family_scores)
       │
       ├─ Router.abstain_check(all_family_scores) → abstain_reason | None
       │
       ├─ execute current search_embeddings → chunks (UNCHANGED behavior)
       │
       ├─ log_router_decision(query, predicted_family, confidence,
       │                       all_family_scores, abstain_reason,
       │                       actual_substrate='semantic_search',
       │                       retrieval_count=len(chunks))
       │
       └─ return current envelope + _router_advisory: {
              predicted_family, confidence, abstain_reason,
              suggested_alternative_substrate  # optional; per §7 below
          }
```

## §5 — Router class + module layout

**New Python module:** `core/services/phase_0_5_router.py`

**Public interface:**

```python
class Phase0_5Router:
    """Advisory-only router — reuses Phase-0 classifier_a as decision engine.

    Chris R2 discipline: NEVER alters retrieval behavior; NEVER production-routing.
    Logs decisions per envelope §9 R2 spec; exposes advisory hint via envelope metadata.
    """

    def __init__(self, classifier_impl='classifier_a', confidence_thresholds=None):
        # Default thresholds from ABSTAIN_POLICY_PROPOSAL §3 placeholders;
        # calibrated post-Phase-0.5 balanced P1 harvest.
        ...

    def classify(self, query: str) -> RouterDecision:
        # Returns dataclass with predicted_family, confidence,
        # all_family_scores, abstain_reason (None | AMBIGUOUS | UNCLASSIFIABLE
        # | CONTEXT_NEEDED), suggested_alternative_substrate.
        ...

    def log_decision(self, query: str, decision: RouterDecision,
                     actual_substrate: str, retrieval_count: int,
                     operator_correction: Optional[str] = None) -> None:
        # Writes to logs/phase_0_5_router.jsonl per envelope §9 R2 spec.
        ...
```

**Classifier import:** `from docs.research.discovery_layer.PHASE_0.classifier_a import classify_query`
- Requires classifier_a.py to be importable as a module (may need `__init__.py` in PHASE_0/ path).
- If path issues arise, mirror `classifier_a.py` into `core/services/phase_0_5_classifier_a.py` for canonical import path. Decision at build time.

## §6 — Instrumentation log format (per envelope §9 R2 + B3 §10.6.2 durable-persistence discipline)

**Persistence discipline (per B3 §10.6.2):** Chris B3 D-verdict explicitly ratified that instrumentation MUST have (a) durable persistence location AND (b) defined extraction path for the Phase-0.5 measurement report. **Ephemeral logs alone are insufficient.** This design implements Option (iii) hybrid — JSONL primary + Django model mirror + committed extraction script:

- **Primary (SOURCE OF TRUTH per Rigby SIGN Q3 R1):** `logs/phase_0_5_router.jsonl` — line-delimited JSON, one row per router-instrumented query. Append-only file, retained across worker restarts. JSONL IS THE SOURCE OF TRUTH. If JSONL and model mirror diverge, measurement uses JSONL and RAISES A §12 T1-adjacent integrity flag.
- **Mirror (durable-query surface):** Django model `Phase0_5RouterEvent` (new — added at build time; ORM-queryable fields; managed retention via existing model-based retention policy). Every JSONL write mirrors to the model in a post-transaction hook. MIRROR IS NOT AUTHORITATIVE — it exists for fast structured querying only.
- **Idempotency key (per Rigby SIGN Q3 R2):** Every event carries an `event_id` UUID generated at router-decision time. JSONL and model both key off `event_id`. If a write retries (network / DB blip), the mirror uses `event_id` for upsert — no double-counts. Runtime abort triggers keyed on rates depend on this idempotency to be reliable.
- **Extraction path (committed, versioned):** `docs/research/discovery_layer/PHASE_0_5/analyze_router_log.py` — deterministic analysis script that reads JSONL (SoT) as primary, model as accelerator for structured queries, and produces the Phase-0.5 measurement report §NEW abstain-analysis section per B3 §4.2.

Rigby SIGN on this design AGREED with Option (iii) hybrid as best default per B3 §10.6.2 "ephemeral logs alone insufficient" directive.

**Schema (per B3 §10.4 categorical + §4 5-field discipline + Rigby SIGN Q3 R2 idempotency):**

```json
{
  "event_id": "<uuid — idempotency key per Rigby SIGN Q3 R2>",
  "ts": "2026-07-DD HH:MM:SS.mmm",
  "session": <int session number if resolvable from context>,
  "measurement_window_id": "<window uuid — bounds this event to a specific measurement window per §2.2>",
  "measurement_window_type": "session" | "rolling_n" | "harvest_phase" | "dogfood_observation",
  "operator_style": "chris" | "claude" | "rigby" | "unknown",
  "original_query": "<verbatim query text as received>",
  "predicted_family": "COUNT" | "PROCEDURAL" | "DISCOVERY" | "IDENTITY" | "SELF-REFERENCE" | "CONCEPTUAL" | null,
  "confidence_categorical": "HIGH" | "MEDIUM" | "LOW",
  "matched_rules": ["<rule names from classifier_a>"],
  "abstain_reason": null | "AMBIGUOUS" | "UNCLASSIFIABLE" | "CONTEXT_NEEDED",
  "abstain_option": null | "(a)" | "(b)" | "(c)" | "(d)",
  "abstain_confidence_snapshot": {"categorical": "HIGH/MEDIUM/LOW", "matched_rules": [...]},
  "clarify_context_type": null | "operational" | "conversational",  // populated when abstain_option == (a)
  "chosen_substrate": "semantic_search",
  "actual_substrate": "semantic_search",  // == chosen; router is advisory
  "fallback": null,  // n/a for advisory-only
  "retrieval_count": <int>,
  "operator_disambiguation_response": null,  // populated if (a) clarify triggered
  "router_recommendation_followed": null | true | false,  // per B3 §10.7 5th field discipline
  "operator_correction": null,  // post-hoc populated if operator disambiguates
  "final_successful_substrate": null  // post-hoc populated from outcome feedback
}
```

**Field notes:**
- **`confidence_categorical` NOT numeric** — matches classifier_a substrate reality per B3 §10.4 R4 correction. NO numeric confidence field. Attempting to add one requires §7 trigger-list evidence-integrity stop per B3 §10.5.
- **`matched_rules`** — replaces numeric `all_family_scores` from prior draft. This is what classifier_a actually returns.
- **`measurement_window_id`** — bounds every event to a specific measurement window per B3 §10.6.1 Chris reframing.
- **`clarify_context_type`** — per B3 R3 operational-vs-conversational discipline.
- **`router_recommendation_followed`** — 5th field per B3 §10.7 discipline; enum/bool for clean measurement.

**Post-hoc fields** (`operator_correction`, `final_successful_substrate`) are populated by a Phase-0.5 close-cascade script that walks conversation history for follow-up queries after each router decision.

## §7 — Advisory metadata surface (envelope response addition) — Q5 F-BLOCKING FIXES APPLIED

**F-BLOCKING corrections (per Rigby SIGN Q5):**
1. Numeric confidence value in example REMOVED — spec must show categorical-only to prevent "just implement the doc" drift (per B3 §10.4 + §10.7)
2. Response key corrected from `"results"` (wrong) to `"chunks"` (actual handler output shape at `td_handlers_ops.py:5967`)
3. Envelope versioning ADDED (`_router_advisory.version: "v1"`) for forward compat

**Response envelope addition (when flag on):**

```json
{
  "action": "semantic_search",
  "count": N,
  "chunks": [...],
  ...current envelope fields (see `td_handlers_ops.py:5967`)...,
  "_router_advisory": {
    "version": "v1",
    "predicted_family": "COUNT",
    "confidence_categorical": "HIGH",
    "matched_rules": ["count_how_many + object_noun"],
    "abstain_reason": null,
    "abstain_option": null,
    "measurement_window_id": "<uuid>",
    "measurement_window_type": "session",
    "parallel_both_substrates": null
  }
}
```

**Parallel-both envelope shape — SPEC RESERVED, NOT EXECUTED IN PHASE-0.5 (per Rigby SIGN cycle 2 F-BLOCKING catch):**

**CRITICAL SCOPE DISTINCTION:**
- **B3 abstain policy §2.2** ratifies (c) parallel-both as the correct FALLTHROUGH for AMBIGUOUS. This is the POLICY.
- **B2 Phase-0.5 dogfood pilot** is ADVISORY-ONLY. Per Chris R2, the router MUST NOT alter retrieval substrate selection or parameters. Executing parallel retrieval WOULD alter retrieval behavior — running lexical + semantic where currently only semantic runs. That violates advisory-only.

**Phase-0.5 behavior on AMBIGUOUS:** The router LOGS that (c) parallel-both is the advised fallthrough via `_router_advisory.abstain_option: "(c)"`, but **does NOT execute parallel retrieval**. The current-best `search_embeddings` call runs unchanged. `_parallel_both` field IS ALWAYS NULL (or absent) in Phase-0.5 responses.

**Reserved future shape** (Phase-1+, ONLY if a subsequent Chris D-verdict lifts the advisory-only guardrail for parallel-both execution — separate ratification required):

```json
{
  "action": "semantic_search",
  "count": <N — see field notes>,
  "chunks": [...],   // Phase-0.5 always populated by unchanged semantic_search
  "_parallel_both": null,   // Phase-0.5 always null; reserved for future ratified flag
  "_router_advisory": {
    "version": "v1",
    "predicted_family": "AMBIGUOUS",
    "confidence_categorical": "MEDIUM",
    "abstain_reason": "AMBIGUOUS",
    "abstain_option": "(c)",
    "advisory_note": "In Phase-1+ ratified parallel-both execution, this envelope would carry substrate-separated `_parallel_both.lexical` + `_parallel_both.semantic` blocks; no fusion; deterministic grouping. In Phase-0.5 advisory-only, no such execution occurs.",
    ...
  }
}
```

**Reserved-shape data contract (for future Phase-1+ ratification only):** If parallel-both execution is EVER ratified in a future Chris D-verdict, the `_parallel_both` field MUST use substrate-separated candidate sets — NO blended ranking / interleaving / cross-reranking:

```json
"_parallel_both": {
  "lexical": {"count": N_lexical, "chunks": [...]},
  "semantic": {"count": N_semantic, "chunks": [...]},
  "grouping": "HIGH-consequence: lexical-first | CONCEPTUAL: semantic-first",
  "no_fusion_attestation": true
}
```

Any consumer that reads `_parallel_both` (in a future ratified execution) and interleaves / cross-reranks / blends across `lexical` and `semantic` violates B3 §10.1 and triggers §12 T1-adjacent integrity stop.

**Attempting to populate `_parallel_both` in Phase-0.5 without prior ratification = §12 T1 integrity stop** (unauthorized weakening of advisory-only per B3 §10.7).

**Field discipline:**
- **NO numeric confidence field anywhere in `_router_advisory`** — categorical-only per B3 §10.4. Attempting to add one requires §12 T1 evidence-integrity stop.
- **`version: "v1"`** — forward-compat versioning. Downstream consumers key off version.
- **`measurement_window_id` + `measurement_window_type`** — bind advisory to specific window scope per B3 §10.6.1.

Underscore prefix signals "advisory metadata, not authoritative retrieval output." Consumers MUST NOT use `_router_advisory` fields to change retrieval behavior downstream. Rigby's UI may render it as a diagnostic annotation.

## §8 — Test surface (contract-level, not implementation)

The scaffolding ships with test cases that verify:
- Flag off → response envelope byte-identical to current (no `_router_advisory` field)
- Flag on → response envelope has current fields + `_router_advisory` field
- Router logs each query to `logs/phase_0_5_router.jsonl` when flag on
- Router does NOT log when flag off
- Router NEVER changes `search_embeddings` call arguments (Chris R2 discipline)
- Classifier import path works from `core/services/phase_0_5_router.py`

Test file: `core/tests/test_phase_0_5_router.py` — added to celery-safe test suite.

## §9 — Recycle discipline

Adding a new module + settings flag + touching `td_handlers_ops.py` invalidates worker imports. Post-merge cascade MUST include `make recycle-all` per PLAYBOOK-7.4.4 (constitutional as of Playbook v0.6.0). Cascade PR body includes `make recycle-all` step with output evidence.

## §10 — Rollback

If Phase-0.5 measurement report closes with stop-condition ≤40% (routing NOT viable), rollback = flip `PHASE_0_5_ROUTER_ENABLED=False` (default). Module + settings entry can remain in-place as inert code for audit trail OR be removed in a follow-up cleanup PR.

If stop-condition ≥60% (routing continues per OPTION A-DUAL), rollback shape depends on Chris D-verdict on Phase-1 production router design (out of Phase-0.5 scope).

## §11 — Non-goals reinforced

- NO alteration of `search_embeddings` behavior (Chris R2)
- NO application to additional call-sites (single-point instrumentation)
- NO auto-adopt of router advisory in Rigby's actual downstream tool chain
- NO numeric-confidence threshold recalibration until balanced P1 corpus closes AND classifier surface adds numeric scoring (per B3 §10.4 substrate correction)
- NO DISCOVERY-family fixes via router (Chris R3 preserve)
- NO substrate default flips (Chris R6 evidence-forward)
- **NO fusion, interleaving, cross-reranking, or blended ranking across substrates** (per B3 §10.1) — even in UI/envelope presentation
- **NO ephemeral-logs-only instrumentation** (per B3 §10.6.2) — durable persistence + defined extraction path REQUIRED

## §12 — Router-runtime abort conditions (per B3 §7/§10.5 trigger list)

Router runtime MUST detect these conditions and abort with an integrity-stop record BEFORE continuing execution. Aborting means: (a) stop routing decisions, (b) write an `evidence_integrity_stop_<trigger>_<ts>.md` record to `docs/research/discovery_layer/PHASE_0_5/`, (c) surface abort state to caller via `_router_advisory: {"integrity_stop": "<trigger_id>", "reason": "..."}`.

**Trigger classification (per Rigby SIGN Q4 R1+R2+R3 — reframed from monolithic "runtime aborts"):**

**Class A — Per-event runtime aborts (evaluated at each router decision):**

1. **T1 numeric-threshold detection** — If a code path attempts to compute a numeric confidence threshold OR passes a numeric value into a categorical decision boundary, abort at the offending call. (Guarded by dataclass typing + linter rule + spec examples.) This includes any attempt to add `_router_advisory.confidence: <float>` — the schema has NO numeric confidence field.

**Class B — Window-level runtime aborts (evaluated after each event, gated on minimum-N):**

Class B triggers evaluate ONLY after `routed_count >= 20` within the current `measurement_window_id`. Below min-N they are inactive (no false positives from small samples).

2. **T2 abstain-rate cap** — If `AMBIGUOUS_count + UNCLASSIFIABLE_count > 30% of routed_count` within the current measurement window AND `routed_count >= 20`, abort.
3. **T3 operator override rate** — If `router_recommendation_followed=false` count > 50% of instrumented queries within the current measurement window AND `routed_count >= 20`, abort.

**Class C — Window-level runtime aborts with observable runtime proxies (evaluated after each event, gated on min-N + proxy signals):**

4. **T4 parallel-retrieval confusion pattern** — **Scoped: ACTIVE ONLY WHEN parallel-both execution is enabled by a separately-ratified flag** (per Rigby SIGN cycle 2 catch on advisory-only-vs-execution boundary). In Phase-0.5 advisory-only, parallel-both is NOT executed (per §7 CRITICAL SCOPE DISTINCTION), so T4 is INACTIVE. If a future Chris D-verdict lifts the advisory-only guardrail and permits parallel-both execution, T4 activates with these runtime proxies (per Rigby SIGN Q4 R3): (a) same-query re-issue within window (operator repeats after (c) parallel-both) OR (b) disambiguating follow-up query about the router's own output. Threshold: >3 such events within a window of ≥20 routed queries. Below min-N: post-hoc-only (measurement-report trigger).
5. **T5 missed-CONTEXT_NEEDED clustering** — Runtime proxies (per Rigby SIGN Q4 R3): (a) spike in `operator_override` combined with immediate re-query pattern within same window AND (b) high rate of `abstain_reason=CONTEXT_NEEDED` AFTER a misroute was attempted (detected by follow-up clarify or operator correction event). If neither proxy is observable at runtime, T5 falls back to measurement-report trigger only.

**Class D — Post-hoc-only measurement-report triggers (evaluated at Phase-0.5 close cascade, not runtime):**

If Class B or Class C triggers cannot achieve min-N (e.g., balanced P1 harvest closes at n<20 in a window), they DOWNGRADE to measurement-report triggers automatically. The Phase-0.5 measurement report flags Class D findings; they do NOT interrupt the router at runtime.

**Abort scope:** Class A/B/C aborts are per `measurement_window_id` (per §2.2 window scope). Aborting a window does NOT disable the router globally — the next measurement window boundary re-enables. Every abort event is itself logged to durable persistence (per §6) as `abort_reason: T1|T2|T3|T4|T5` for measurement audit.

## §13 — Build gate

Implementation begins ONLY when:
1. ~~Chris ratifies BALANCED_P1_HARVEST_PLAN~~ ✅ **D-RATIFIED at S2823 turn ~14** (§2.1 metric + §2.2 stop-condition + §3 balance targets)
2. ~~Chris ratifies ABSTAIN_POLICY_PROPOSAL~~ ✅ **D-RATIFIED at S2823 turn ~18** (§2.2/§2.3/§2.4 defaults + §3 categorical + §7 trigger list + §10 measurement-window + durable-persistence)
3. ~~This design routed through Rigby joint SIGN and refinements applied~~ ✅ **Rigby SIGN cycle 1 completed at S2823 turn ~22 with F-BLOCKING on §7 envelope example; F-BLOCKING fixes applied at turn ~24. Confirmation dispatch pending (§14 records the SIGN cycle).**
4. Chris ratifies this design ← **NEXT STEP after Rigby F-BLOCKING confirmation clears**

## §14 — Rigby joint SIGN cycle 1 record

**Executed at S2823 turn ~22 via pin `pa-d63796dde6404d0f`.** Anti-rubber-stamp check PASSED — Rigby verified against ABSTAIN_POLICY_PROPOSAL.md §10, `td_handlers_ops.py:5905` (semantic_search handler), `core/settings.py` (feature-flag pattern), and this design draft.

### §14.1 Question-by-question verdicts

| Q | Subject | Verdict | Refinements |
|---|---|---|:---:|
| Q1 | §3 single call-site instrumentation scope | AGREE-with-refinements-2 | 2 |
| Q2 | §2.2 measurement window + transitions | AGREE-with-refinements-3 | 3 |
| Q3 | §6 hybrid durable persistence Option (iii) | AGREE-with-refinements-2 | 2 |
| Q4 | §12 T1-T5 runtime abort triggers | AGREE-with-refinements-3 | 3 |
| **Q5** | **§7 _router_advisory envelope contract** | **F-BLOCKING** (numeric-confidence-leak + wrong-key + no-versioning) | **4** |
| Q6 | zoom-out + B3 §10.7 discipline gaps | AGREE-with-refinements-5 (contingent on Q5 fix) | 5 |
| — | **Total** | **1 F-BLOCKING + 5/5 AGREE-with-refinements** | **19** |

### §14.2 Q5 F-BLOCKING resolution (applied same-turn per S2822 precedent)

Rigby's F-BLOCKING correctly caught two load-bearing contract violations in the §7 envelope example:

1. **Numeric confidence leak** (`confidence: 0.82`) — contradicted B3 §10.4 categorical-only ratification. This is exactly the drift-vector B3 §10.7 discipline was written to prevent.
2. **Wrong response key** (`results` instead of actual handler `chunks`) — verified against `td_handlers_ops.py:5967` handler output shape.

**Corrections applied to §7:**
- Numeric confidence value REMOVED; replaced with `confidence_categorical: "HIGH"` + `matched_rules` array (matches classifier_a output)
- `results` → `chunks` (matches handler)
- Versioning ADDED: `_router_advisory.version: "v1"` for forward compat
- Parallel-both envelope shape ADDED with explicit `_parallel_both` substrate-separated structure + `no_fusion_attestation: true` field — enforceable data contract for B3 R1 no-fusion (Q6 C2 refinement)

### §14.3 19 refinements applied

- **Q1 R1** — §3 deferred-adjacency policy: adjacent tools require SIGN + Chris D-verdict, NOT opportunistic addition during build
- **Q1 R2** — §3 explicit deferred-adjacency list with handler locations (search_embeddings :5877, search_docs :~6011, conversation_tool.search, deliverable_tool.search)
- **Q2 R1** — §2.3 bind-at-decision-time rule for window binding
- **Q2 R2** — §2.3 rolling_n boundary: measurement_window_id per event handles carryover; no special logic needed
- **Q2 R3** — §2.3 clarify-cap flip applies within window_id, not session (preserves ratified "window" concept per B3 §10.6.1)
- **Q3 R1** — §6 JSONL declared as SOURCE OF TRUTH; model is mirror; divergence raises integrity flag
- **Q3 R2** — §6 event_id UUID idempotency key; prevents double-counts on retry
- **Q4 R1** — §12 T4/T5 reframed as window-level abort triggers gated on min-N (n≥20)
- **Q4 R2** — §12 Class D fallback: post-hoc measurement-report triggers if min-N not achievable
- **Q4 R3** — §12 T5 observable runtime proxies defined (spike in override + immediate re-query pattern; CONTEXT_NEEDED after misroute)
- **Q5 F-BLOCKING fixes** — §7 categorical confidence + `chunks` key + `version: v1` + parallel-both substrate-separated envelope shape (4 fixes)
- **Q6 C1** — §7 categorical-only enforced in example spec (F-BLOCKING resolution covers)
- **Q6 C2** — §7 no-fusion enforceable data contract via `_parallel_both` structure + `no_fusion_attestation` field
- **Q6 C3** — §6 SoT declaration + event_id idempotency (Q3 covers)
- **Q6 C4** — §12 all trigger evaluation keys off measurement_window_id + min-N gates (Q4 covers)
- **Q6 C5** — §3 deferred-adjacency list with SIGN gate (Q1 covers)

### §14.4 F-BLOCKING confirmation cycle results

**Cycle 1 confirmation dispatch (turn ~25):** Rigby returned **NOT CLEAR** — original F-BLOCKING items (numeric-confidence-leak, wrong `results` key, no versioning) all resolved, BUT a new follow-on issue surfaced:
- §7 `_parallel_both` envelope shape implied EXECUTING parallel retrieval, which conflicts with advisory-only guarantee that retrieval substrate + parameters do NOT change
- §12 T4 was written as if parallel-both was actually executed in Phase-0.5

**Cycle 1 fixes applied (turn ~26):**
- §7 rewritten with explicit CRITICAL SCOPE DISTINCTION block: B3 policy vs B2 advisory-only-execution boundary; `_parallel_both` field ALWAYS NULL in Phase-0.5; reserved-shape data contract preserved for future Phase-1+ ratification only; unauthorized population = §12 T1 integrity stop
- §12 T4 scoped as "ACTIVE ONLY WHEN parallel-both execution is enabled by a separately-ratified flag" — INACTIVE in Phase-0.5

**Cycle 2 confirmation dispatch (turn ~27):** Rigby returned **CLEAR**. Optional non-blocking §1 consistency nit applied same-turn.

### §14.5 Final SIGN state: CLEAR — routes to Chris D-verdict

- Cycle 1: 19 refinements applied + 1 F-BLOCKING
- Cycle 2: 2 additional fixes + 1 F-BLOCKING (advisory-only-vs-execution boundary)
- Cycle 2 CLEAR verdict + 1 optional consistency nit applied
- **Total: 22 refinements applied same-session; 0 F-BLOCKING remaining**
- Anti-rubber-stamp discipline PASSED across 3 SIGN rounds (12+ tool_runs verified against ABSTAIN_POLICY_PROPOSAL.md, td_handlers_ops.py, core/settings.py, classifier_a.py, this design)

Design is CLEAR for Chris D-verdict routing.

## §15 — Chris D-verdict RATIFIED (2026-07-18 S2823 turn ~28)

**Verdict:** **RATIFY** — the router-scaffolding design approved as the implementation boundary for the Phase-0.5 advisory-only pilot. Build may proceed under the ratified advisory-only constraints.

### §15.1 R1 — Advisory-only boundary: RATIFIED

- Phase-0.5 logs router recommendations but does NOT alter retrieval behavior.
- (c) parallel-both is a ratified policy outcome, NOT a Phase-0.5 execution behavior.
- `_parallel_both` remains null unless a future Chris D-verdict explicitly authorizes execution.
- **Any attempt to populate or execute `_parallel_both` in Phase-0.5 without prior ratification constitutes a §12 T1 integrity stop.**

### §15.2 R2 — Measurement windows: RATIFIED (elevated to CANONICAL UNIT OF OBSERVATION)

- **The measurement window becomes the canonical unit of observation** (Chris framing — stronger than "used for scoping"; measurement window is now the fundamental analysis primitive).
- Bind every router event to the active `measurement_window_id` at decision time.
- Clarify-cap behavior, trigger evaluation, and reporting all scope to the measurement window rather than the session.

### §15.3 R3 — Instrumentation scope: RATIFIED

- `kb_tool.semantic_search` is the SOLE Phase-0.5 instrumentation surface.
- Expansion to adjacent retrieval surfaces remains explicitly DEFERRED and requires BOTH SIGN AND a future D-verdict.

### §15.4 R4 — Durable evidence: RATIFIED

- JSONL is the declared SOURCE OF TRUTH.
- Django model is a durable MIRROR.
- `event_id` idempotency and the committed extraction path are REQUIRED parts of the design.
- **Any divergence between source of truth and mirror raises an integrity event rather than silently reconciling** (per Chris explicit "integrity event, not silent reconciliation").

### §15.5 R5 — Advisory contract: RATIFIED

- `_router_advisory` is versioned (`v1`).
- Confidence remains CATEGORICAL only.
- Envelope matches the live handler contract (`chunks` key per `td_handlers_ops.py:5967`).
- **Advisory surface remains strictly ADDITIVE and NON-BREAKING** (per Chris explicit downstream-compat discipline).

### §15.6 R6 — Integrity triggers: RATIFIED (with runtime-vs-post-hoc epistemic boundary)

- The four trigger classes (A/B/C/D) appropriately distinguish per-event, window-level, proxy-driven, and post-hoc analysis.
- **Runtime checks must only evaluate signals that are actually observable at runtime.**
- **Post-hoc conclusions must never be presented as runtime facts** (Chris framing — this is an epistemic-integrity discipline: T4/T5 without observable runtime proxies MUST downgrade to Class D report-only, not fake runtime confidence).

### §15.7 R7 — Build authorization: RATIFIED

- **B1, B2, and B3 now form a coherent constitutional package.**
- Build authorization is granted only within the documented advisory-only constraints.
- **Any implementation that changes retrieval behavior, weakens no-fusion discipline, weakens evidence persistence, bypasses integrity-stop rules, or expands instrumentation beyond the ratified surface must return through SIGN and a new D-verdict before proceeding.**

### §15.8 Constitutional package: LOAD-BEARING

- BALANCED_P1_HARVEST_PLAN §10 D-RATIFIED (S2823 turn ~14)
- ABSTAIN_POLICY_PROPOSAL §10 D-RATIFIED (S2823 turn ~18)
- ROUTER_SCAFFOLDING_DESIGN §15 D-RATIFIED (S2823 turn ~28) — this document

Phase-0.5 design phase is COMPLETE. Build may proceed under R1-R7 constraints. Implementation lands as a single PR per §13 build-gate spec (module + settings + handler diff + tests + logs + handoff + envelope diff). Build execution begins in a separate session (typically S2824) to preserve the clean design-vs-implementation boundary.

---

**End of design spec. B2 D-RATIFIED at S2823 turn ~28. Constitutional package B1+B2+B3 coherent and LOAD-BEARING. Build authorization: GRANTED under R1-R7 constraints. Next: A3 pointer-chunk spot-check + close cascade for S2823.**

At that point, implementation lands as a single PR containing:
- `core/services/phase_0_5_router.py` (new module)
- `core/settings.py` diff (flag)
- `core/services/td_handlers_ops.py` diff (:5905 flag-guarded instrumentation)
- `core/tests/test_phase_0_5_router.py` (contract tests)
- `logs/phase_0_5_router.jsonl` initial empty file
- Handoff doc + envelope diff

---

**End of design spec. NEXT: build gate = Chris D-verdict RATIFY on B1 + B3 + this design. No code until then.**
