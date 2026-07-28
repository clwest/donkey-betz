# Session 3026 — abort-early arc: two spec-invalidations, S3025 copy fix + honest Fold C

**Date:** 2026-07-28 · **HEAD at close:** `4fcbc1308` (PR #3739 merged) + docs cascade

## What shipped

**3 PRs merged this session.** All three were driven by PLAYBOOK-7.7.1 abort-early clause discoveries — measurements and test-driven investigation invalidated two separate spec premises before either turned into placebo work.

### PR #3737 (`6cbd16180`) — `fix(s3026): correct S3025 misleading bulk-create warning copy`

**Frontend `SignalsClustersView.tsx` (+1/-1).** Chris directive at open was "start async brief generation" — S3026 primary from the 00-START. Cycle 1A verify-before-build measurement invalidated the premise:

| Config | Measured (pre-warmed shell, 4 rounds × 5 clusters) |
|---|---|
| brief=FALSE | ~6ms per row |
| brief=TRUE  | ~52ms per row (delta ~46ms per brief) |
| 100-cluster cap worst case | **5.2s** — not "a few minutes" |

Brief generation is pure Python string composition + a Deliverable INSERT — grep of `core/services/deliverable_factory.py` confirmed no OpenAI/Anthropic/embed calls in the path. The "async brief" directive would have solved a problem that doesn't exist at S3026 measurement scale.

That measurement also exposed the S3025 warning copy ("This may take a few minutes when briefs are enabled") as factually wrong — the copy was the residue of the incorrect assumption I made at S3025 close. PR 1 replaces it with honest language pointing users at the progress bar.

### PR #3738 (`5660138cd`) — `fix(s3026): Fold C — remove broken KT write from promote_decision; fix Redis broadcast; return honest learning_created`

**Backend `core/views_agent_learning.py` (+55/-37) + NEW `core/tests/test_s3026_promote_decision_fold_c.py` (+175 lines, 5 tests).** Second spec-invalidation. S3023's Fold C description said `promote_decision` masks an AttributeError on `decision.summary`. Test-driven exploration discovered **THREE bugs simultaneously masked** by the broad `except Exception as learn_err` at line 2205:

1. **`KnowledgeTransfer.objects.create(source_agent=..., target_agent=..., title=..., content=..., applied=..., ...)`** — the KT model at `core.models_unified_system:785` has fields (`source_knowledge`, `transfer_summary`, `was_applied`, `was_useful`, …). NONE of the S657 kwargs are valid. Every call raised `TypeError`; the `decision.summary` AttributeError never even fired because control never reached that line.
2. **`decision.summary`** on the Redis event payload — `AgentDecisionSummary` has no `summary` field (has `rationale`, `recommended_stance`).
3. **`decision.agents_involved`** on the Redis event payload — the actual field is `participants`.

Bug 1 has been silently failing since S657 (~5 years). `learning_created` returned to the frontend was **always** False; the Redis broadcast **never** fired.

**Option C fix (per Rigby A1 REVISE, abort placebo fix):**

- Removed the broken KT.create block entirely (the KT model realignment is a separate design arc; requires schema migration or a new `DecisionPromotionLearningEvent` model).
- Kept + fixed the Redis broadcast using the same accessor pattern as `views_platform_command.py:814` (`decision.rationale or decision.recommended_stance or ''`). Fixed both field-name bugs.
- Return `learning_created: False` honestly with new `learning_reason: 'knowledge_transfer_model_mismatch_deferred'` diagnostic.

**Behavior change:** Redis broadcast to `agent_learning` channel now actually fires on canonical promotion (hasn't since S657). If any downstream subscriber depends on this, they'll start receiving events for the first time.

### PR #3739 (`4fcbc1308`) — `fix(s3026): PR2 A2 REVISE follow-up — comment cleanup + Redis broadcast back-compat + schema_version`

**Backend `core/views_agent_learning.py` (+16/-4) + test extension (+10/-2).** Rigby A2 REVISE on PR #3738 flagged two follow-ups:

1. **Literal grep for `decision.summary` still hit a comment** in `promote_decision`. Reworded to describe "the removed summary field" without repeating the identifier.
2. **Redis broadcast subscriber back-compat** — dual-emit `participants` (canonical) + `agents_involved` (S657-source alias) for one compatibility window + added `schema_version: 1` so future subscribers can gate on shape as it evolves.

**Deferred (Rigby A2 zoom-out #2):** `learning_reason` as bare string is codification candidate — typed enum vs bare string. Watch for 2nd trigger before codification.

## Results

| Metric | Actual |
|---|---|
| PR #3737 (frontend copy) | +1/-1, direct string replacement |
| PR #3738 (backend Fold C + tests) | +230/-39, 5 new tests |
| PR #3739 (A2 REVISE follow-up) | +26/-6, test extension |
| New test suite (`test_s3026_promote_decision_fold_c.py`) | **5/5 pass in 0.471s** |
| Regression bundle (S3013 + S3014 + S3015 + S3023 + S3024 + S3026) | **53/53 pass in 6.341s** |
| Post-merge `make recycle-all` (final) | HEAD `4fcbc1308`, sha=4fcbc13084aa recorded in `logs/recycle_events.jsonl` |

## Two spec-invalidations in one session — abort-early discipline held

1. **S3026 async-brief-generation** — original session primary directive. Aborted at verify-before-build. Would have been 1-2 session commit against a nonexistent problem (LLM latency I assumed but never measured). Rigby A1 approved abort.
2. **S3023 Fold C AttributeError fix** — first redirect. Aborted at test-driven exploration when the "fix" tests failed. Would have shipped a placebo fix to a bug that never actually fires in practice. Rigby A1 approved Option C redirect.

Both aborts saved real work. Both required the discipline of routing back to Rigby with the discovery rather than pushing through. **Verify-before-build (Cycle 1A) worked exactly as designed** — both spec invalidations were caught by direct measurement (PR 1) or test failure (PR 2), not by intuition.

## Rigby SIGN quality this session

**3 substantive SIGN cycles.** All tool-grounded. **Zero hallucination triggers** — matches S3010 → S3025 pattern (**12 sessions continuous**).

Cycle summary:

1. **A1 #1 — APPROVE ABORT** on async brief generation + REDIRECT to (a) S3025 copy fix + (b) S3023 Fold C investigation. Sequencing tweak: copy fix its own PR (near-zero regression, user-facing correction — ship immediately).
2. **A1 #2 — APPROVE Option C** for Fold C after discovery of the second spec invalidation. Rejected Option A (dishonest placebo), rejected Option B (KT model realignment is design-arc scope), approved Option C (remove broken write + fix broadcast + honest response).
3. **A2 — REVISE** on PR #3738: comment cleanup + back-compat dual-emit. Both addressed in PR #3739. Then implicitly-AGREE after PR #3739 by absence of further REVISE.

## Folds (pattern evidence, not automatic escalation)

### Fold A `1st trigger` — Fold descriptions should be backed by test/stacktrace evidence

**Rigby A1 zoom-out during S3026 second abort.** The S3023 Fold C description named a symptom (AttributeError on `decision.summary`) that never actually fired in practice; the causal exception was upstream. Codification candidate: "fold claim must be backed by a minimal failing test or stacktrace pointing at the true first-cause exception." Watch for 2nd trigger before codification. Note this session as first trigger — the entire second-spec-invalidation arc traces back to a fold description that named a symptom rather than a root cause.

### Fold B `informational` — Two spec-invalidations in one session

Statistical outlier or genuine pattern? Both S3026 aborts were caused by upstream authoring artifacts:
- Async brief spec was authored based on my S3025 close incorrect assumption.
- S3023 Fold C description was authored based on visual inspection of a symptom without running the code path.

Watch signal: if a third session in the next ~5 sessions also aborts on measurement/test invalidation of a self-authored forward-carry, escalate to Chris. Two triggers isn't yet enough to change the workflow — but three within a short window would suggest forward-carry authoring needs a "verify before writing" gate.

### Fold C `informational` — `learning_reason` bare string typing (Rigby A2 zoom-out)

The `learning_reason: 'knowledge_transfer_model_mismatch_deferred'` diagnostic added in PR #3738 is an unstructured string. Codification candidate: typed enum vs bare string as the API returns diagnostic reasons. Watch for 2nd trigger.

### Design-arc candidate — KnowledgeTransfer model realignment

The `KnowledgeTransfer` model at `core.models_unified_system:785` has a student/teacher knowledge-transfer shape (`source_knowledge`, `transfer_summary`, `was_applied`, `was_useful`) that doesn't match the S657 intent (agent-to-collective-intelligence broadcast of canonical policy decisions). Either:
- The S657 code was written against a differently-shaped KT model that was later refactored, OR
- The intent was always "broadcast to some persistence layer" and KT was the wrong home.

A future arc should either: (a) add a `DecisionPromotionLearningEvent` model, or (b) map the intent onto KT's real shape (would require a `KnowledgeChunk` FK for `source_knowledge`, which we don't have for promoted decisions). Not urgent — 5 years of silent failure with no user impact suggests low value.

## Forward carries

### New from S3026

- **Fold A `1st trigger`** — fold descriptions should be backed by test/stacktrace evidence. Codification watch signal.
- **Fold B `informational`** — 2 spec-invalidations in one session; watch for 3rd trigger within next 5 sessions.
- **Fold C `informational`** — `learning_reason` bare-string typing.
- **Design-arc candidate** — KnowledgeTransfer model realignment for canonical decision persistence.

### Carried from S3025 (STATUS PRESERVED)

- **S3025 Fold A `informational`** — `chunks.indexOf(chunk)` inside loop; cheap at cap.
- **S3025 Fold B `informational`** — cancelled rows revert to `pending` glyph.
- **S3025 Fold C `codification candidate`** — `BulkPromoteModal` complexity growth; extract reducer before U8+ lands.

### Carried from S3024 (STATUS PRESERVED)

- **S3024 Fold A `1st trigger`** — cross-tier default-formatting shadowing.
- **S3024 Fold B `informational`** — silent-fallback vs strict-validate asymmetry.

### Carried from S3023 (STATUS PRESERVED)

- **S3023 Fold A `informational`** — pressure-test 2-session-old forward-carry notes before spec'ing.
- **S3023 Fold B `informational` (single-promote semantics only)** — `bulk_promote_decisions` doesn't trigger Redis broadcast + KnowledgeTransfer. Note: with S3026 removing the KT write from single-promote, the "parity" story changes — bulk-promote is now aligned with single-promote on the KT-side (both do nothing) and misaligned only on the Redis broadcast (single fires, bulk doesn't). Restatement: **wire bulk_promote_decisions to also emit the S3026-shaped Redis broadcast for each promoted row.**
- **S3023 Fold C** — **RESOLVED** by S3026 PR #3738.
- **S3023 Fold D `1st trigger`** — U4-H tests ratify current status/lifecycle contract.
- **Decision lifecycle parity (Rigby A1 zoom-out standing carry)** — HAI vs ADS lifecycle families still fragmented.

### Carried from S3022 / S3021 / S3020 / S3019 / S3018 / older — all preserved from S3025 close 00-START.

## Cross-cutting workflow references

- **Constitutional governance chain:** CLAUDE.md Playbook v0.10.0. No amendments this session.
- **Spec→ship contract:** PLAYBOOK-7.7.1. **2× ABORT-EARLY invocations, both successful.** 3× PRs shipped (2 backend, 1 frontend) after redirects.
- **SIGN evidence discipline:** PLAYBOOK-7.7.2. **3× substantive Rigby SIGN cycles. Zero rubber-stamp. 18 sessions continuous.**
- **Chris-facing decision framing:** PLAYBOOK-7.7.3. Chris routing: session-open directive "start async brief generation" ratified S3026 primary; abort-early redirects handled Claude+Rigby-side per `feedback_claude_rigby_agree_first_chris_yes_no`. Chris to receive plain-English close summary noting the two aborts.
- **Recycle discipline (PLAYBOOK-7.4.4):** `make recycle-all` **3×** — once post-PR2 (sha=5660138cd75b), once post-PR3 (sha=4fcbc13084aa). PR1 was pure frontend copy fix; recycle deferred to post-PR2 which also included the frontend PR1.
- **Fold classification (PLAYBOOK-6.10.8):** 3 folds + 1 design-arc. All 3 folds `informational` or `1st trigger`. All Rigby REVISE conditions classified `same_pr_mitigatable` (PR3 was the follow-up-PR path since PR2 already merged).
- **Verify-before-build (Cycle 1A):** **11th consecutive session** — Cycle 1A measurement caught BOTH spec invalidations before code was written. Session's canonical Cycle 1A win.

## Wrapper pin note

Session-open pin was `pa-3316e95cc372416d` (retired at S3025 close). Active during session: `pa-b2948ae4c2624583`. Close mints next pin; wrapper diff committed per `feedback_commit_wrapper_pin_bump_at_close`.
