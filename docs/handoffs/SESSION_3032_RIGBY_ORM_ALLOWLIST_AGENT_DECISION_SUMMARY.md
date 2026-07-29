# Session 3032 — Rigby ORM allowlist: AgentDecisionSummary

**Date:** 2026-07-28 · **HEAD at close:** `4e8a6a353` (PR #3753 merged) + docs cascade

## What shipped

**1 feature PR merged this session** — third PR shipped in the same terminal as S3030 + S3031 (Chris ratified continuation after S3031 close asked which items were bumped vs still open).

### PR #3753 (`4e8a6a353`) — `feat(s3032): Rigby ORM allowlist — add AgentDecisionSummary entry`

Closes S3030 Fold A / S3031 Fold D (carried) — the Rigby Tool Gap Ledger candidate. Live trigger at S3030 T1 SIGN: Rigby needed to run `AgentDecisionSummary.filter(status='canonical', is_canonical=False).count()` to ground the backfill spec, but the model wasn't in `orm_inspect_tool`'s 17-entry allowlist, forcing fallback to Django shell via Claude. This closes the tool-surface gap so future S30XX arcs touching decision lifecycle can be verified end-to-end on Rigby's tool surface.

**Shape:**

New entry in `_MODEL_POLICIES` at `core/services/td_handlers_agents.py:911`:

```python
'AgentDecisionSummary': {
    'app_label': 'core', 'sensitive': False,
    'expensive_text_fields': (
        'recommended_stance', 'suggested_feature', 'rationale',
    ),
},
```

- **Non-sensitive**: content is agent-authored decision text (recommendations, rationale, feature suggestions), not credentials or user PII.
- **Expensive text fields**: `recommended_stance`, `suggested_feature`, `rationale` blocked from `contains`/`icontains` lookups per S2866 policy.
- **`topic`** (CharField(255)): safe for contains — allowed.
- **JSONFields** (`key_insights`, `participants`): non-sensitive, render via existing recursive-key-redaction path.

**NEW** `core/tests/test_s3032_orm_allowlist_agent_decision_summary.py` (+152, 5 tests):

- `test_list_models_includes_agent_decision_summary_as_non_sensitive`
- `test_describe_model_returns_expected_shape` (JSONField flags correct on key_insights + participants; scalar fields correct)
- `test_filter_runs_the_s3030_canonical_drift_probe` — end-to-end pin: exact S3030 T1 probe returns correct row set + topics
- `test_contains_rejected_on_expensive_text_fields` — all 3 expensive TextFields refuse contains scans
- `test_contains_allowed_on_topic_charfield` — proves policy is field-scoped, not model-scoped

## Results

| Metric | Actual |
|---|---|
| PR #3753 diff | +175/-0 (1 file mod + 1 new test) |
| S3032 suite | **5/5 pass in 0.028s** |
| Regression bundle (all orm_inspect_tool baseline S2866+S2867+S2871+S2873+S2931+S2991 + full S30xx canonical-promotion arc + S3032) | **191/191 pass in 9.080s** |
| Live E2E via `orm_inspect_tool` (Rigby, post-recycle) | drift probe returns 0 rows on local dev DB (matches S3030 result); list_models returns 18 entries with correct policy metadata |
| Post-merge `make recycle-all` | clean, `sha=4e8a6a353111` recorded in `logs/recycle_events.jsonl` |

## Cycle 1A verify-before-build wins

**17th consecutive session.** Verify pass at T1: grep for `orm_inspect_tool` allowlist location, read _MODEL_POLICIES structure at `td_handlers_agents.py:761-910`, review 17 existing entries + growth history (S2866 initial 3 → 7 accretion PRs). Grounded T1 spec in reality before dispatching to Rigby.

## Rigby SIGN quality this session

**2 substantive SIGN cycles.** All tool-grounded. **Zero hallucination triggers** — matches S3010 → S3031 pattern (**18 sessions continuous**).

Cycle summary:

1. **T1 SIGN — AGREE with strict single-model scope.** Rigby endorsed adding just `AgentDecisionSummary` (rejected scope-creep to `AgentConversation`/`HiveMindSession` without logged Ledger incidents — preserves the incremental discipline of the accretion pattern). Proposed policy shape (non-sensitive, 3 expensive_text_fields, topic safe for contains) accepted verbatim. Sensitivity check: no vector (agent-authored content, no user PII/credentials).
2. **A2 SIGN (post-code, live E2E) — AGREE with tool-surface proof.** Rigby executed the actual drift probe (`filter(status='canonical', is_canonical=False)`) via `orm_inspect_tool` — returned 0 rows on local dev DB (matches S3030 probe result; heal is prod-only). Also verified `list_models` returns 18 entries with `AgentDecisionSummary` at correct alphabetical position, `sensitive: false`, `expensive_text_fields: ["recommended_stance","suggested_feature","rationale"]`. Zoom-out flagged only an optional traceability micro-nit (Ledger tag in comment) which was already satisfied by the `S3032 Rigby Tool Gap Ledger` docstring prefix.

## Folds (pattern evidence, not automatic escalation)

### Fold A `2nd trigger` — Boolean-return semantics discipline (carried from S3031 Fold A)

Unchanged this session. Watch for 2nd `did_X`-style bool-return method to codify the "callers must treat False as idempotent no-op success, not error" contract.

### Fold B `informational` (carried from S3029 Fold A / S3030 Fold B / S3031 Fold B) — spy `side_effect=lambda` signature fragility

Unchanged. Not exercised this session (no spy tests added).

### Fold C `3rd cycle, no discovery` (carried unchanged from S3031 Fold C)

A2 zoom-out sweep pattern not exercised this session (single-file change; grep already covered at T1 verify). Fold C status preserved for the arc; no new evidence for or against codification.

### Fold D `RESOLVED` (was Rigby ORM allowlist gap)

**RESOLVED** by PR #3753. `AgentDecisionSummary` now on allowlist; Rigby verified live E2E. Removes the fallback-to-Django-shell requirement for the specific S30XX arc that generated the ledger entry.

## Forward carries

### New from S3032

- **Fold E `2nd cycle, non-blocking accretion evidence`** — orm_inspect_tool allowlist growth pattern (1 model per Ledger incident): now at 18 entries via 7 accretion PRs since S2866. Rigby A2 endorsed the pattern over periodic-sweep alternatives. If this becomes N+2 more accretion PRs in short succession, revisit whether a periodic-sweep RFC is warranted — for now, discipline holds.

### Carried from S3031 (STATUS UPDATED)

- **S3031 Fold A `2nd trigger` (bool-return semantics)** — carried unchanged.
- **S3031 Fold B `informational` (spy fragility)** — carried unchanged.
- **S3031 Fold C `3rd cycle, no-discovery` (A2 zoom-out sweep pattern)** — carried unchanged (not exercised).
- **S3031 Fold D `informational` (Rigby ORM allowlist gap)** — **RESOLVED** by this PR.

### Carried from S3030 (STATUS PRESERVED)

- **S3030 prod deploy carry** — still open: run `python manage.py backfill_canonical_drift --apply` against Railway prod when convenient.

### Carried from S3026 → S3029 (STATUS PRESERVED)

- **S3026 Fold A `1st trigger`** — fold descriptions backed by evidence. S3032 A2 live-E2E = additional supporting evidence (proof via actual tool invocation, not just grep).
- **S3026 Fold B `informational`** — spec-invalidation watch.
- **S3026 Fold C `informational`** — `learning_reason` bare-string typing.
- **Design-arc candidate** — KnowledgeTransfer model realignment.

### Carried from S3025 / S3024 / older — all preserved from S3031 close 00-START.

## Cross-cutting workflow references

- **Constitutional governance chain:** CLAUDE.md Playbook v0.10.0. No amendments this session.
- **Spec→ship contract:** PLAYBOOK-7.7.1. **1× Flow B spec→ship** (PR #3753 planned end-to-end from S3030 forward-carry).
- **SIGN evidence discipline:** PLAYBOOK-7.7.2. **2× substantive Rigby SIGN cycles this session (7× across S3030 + S3031 + S3032 terminal). Zero rubber-stamp. 24 sessions continuous.**
- **Chris-facing decision framing:** PLAYBOOK-7.7.3. Chris directive at S3031 close asked which items were bumped vs still open; Claude reported "Rigby ORM allowlist still open, not bumped"; Chris directive: "yes let's do it".
- **Recycle discipline (PLAYBOOK-7.4.4):** `make recycle-all` once post-PR-3753, clean at `sha=4e8a6a353111`.
- **Fold classification (PLAYBOOK-6.10.8):** 5 folds. A carried 2nd trigger. B/C carried informational + 3rd-cycle. D RESOLVED. E new 2nd-cycle accretion-pattern evidence.
- **Verify-before-build (Cycle 1A):** **17th consecutive session** — read allowlist location + structure + growth history before spec.

## Wrapper pin note

Session-open pin was `pa-3de83caf6bca4968` (minted at S3031 close). Close mints next pin; wrapper diff committed per `feedback_commit_wrapper_pin_bump_at_close`.

## Multi-session-in-one-terminal note

**Third session shipped in the same terminal (S3030 + S3031 + S3032).** S3030 was the primary directive (backfill deferred from PR #3747); S3031 was the S3030 close recommendation (Chris directive: "knock out the did_promote in this terminal session"); S3032 was the S3031 close carry (Chris directive: "yes let's do it" after Claude reported the Rigby ORM allowlist gap was still open). **Total: 6 PRs across the terminal** (#3749 S3030 code, #3750 S3030 docs, #3751 S3031 code, #3752 S3031 docs, #3753 S3032 code, this docs cascade for S3032 close).

Context density is high — future terminal continuation should still batch cleanly, but a session_lifecycle close (which happens at each session-close cascade) marks the natural break point. If a 4th mid-terminal S30XX slate is proposed, consider whether it's better shipped as a fresh terminal session rather than continuing to accrete context.
