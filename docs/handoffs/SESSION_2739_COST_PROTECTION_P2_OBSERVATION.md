# Session 2739 — Cost Protection P2+ Observation-Period Foothold

**Session:** 2739
**Date:** 2026-07-10
**Session type:** Direct EOS campaign — Capability Graph chain (§17 Cost Protection P2+)
**System Owner directive:** "route both to Rigby for scope SIGN" → "take Rigby's rec — §17 Cost Protection P2+" → "Lets go with 1" (ratifying Cat 2 + Cat 4 scope) → "approve — open the PR" → "merge it and run the cascade"
**PA conversation pins:**
- Session-open (scope-SIGN only, retired mid-session): `pa-777a3fe46a52480e`
- Arc-scoped (active): `pa-f2bc0abba82849a9` (title: `session-2739-cost-protection-p2plus-arc`)
**Preceding arc:** SESSION_2738 (Playbook v0.3.0 ratified, CD-48 + CD-49 discharged)
**Merge commit:** `be9b9b1c` (PR #3060, squash-merged 2026-07-10)

---

## §1 Delivery ledger

| # | PR | Purpose |
|---|---|---|
| 1 | #3060 (`feat/session-2739-cost-protection-p2plus-observation`) | Cat 2 observation foothold + Cat 4 capability graph §17 refresh — 5 files, +490/-3 LOC |

**Ledger totals for S2739:** 1 PR · 1 feat · 6 new tests · 21/21 pass · zero regressions · zero governance side effect.

---

## §2 Arc shape — pre-Cat A → Cat A → ratification → implementation → SIGN → PR → cascade

1. **Chris opening question** — "What is the next steps that will make the overall platform better?" Claude cross-referenced audit's POSTURE-PENDING debt with S2739 candidate queue, proposed two candidates: §18 Auth full scope + Chapter 8 Runtime Discipline MINOR.
2. **Scope SIGN dispatch** — routed both to Rigby for independent scope SIGN. Rigby verdicts:
   - Candidate 1 (§18 Auth): **REFRAME**, 0.72 confidence — explicitly Chris-blocked in capability graph on D-verdict for 4-axis §14.14; over-scoped as single chain campaign.
   - Candidate 2 (Chapter 8 MINOR): **DEFER**, 0.84 confidence — Chris deferred twice; risk of becoming declared-but-unenforced doctrine itself.
   - Cross-check: Rigby independently proposed **§17 Cost Protection P2+** as the highest-leverage "platform better" move — no explicit Chris-blocker, concrete missing links, reliability/cost-safety class.
3. **Chris ratification** — "take Rigby's rec — §17 Cost Protection P2+".
4. **Pin management** — retired scope-only pin `pa-777a3fe46a52480e` via `session_tool.retire` (3 rows updated), minted arc pin `pa-f2bc0abba82849a9`, rotated `tools/pa_local.sh` line 532 to new pin.
5. **Cat A independent read (Claude)** — verified graph §17 spec is stale on architecture. P1 (S2735) shipped with `CostTracking` substrate (54.5× more coverage than `LLMCallEvent`); graph's missing links (a)/(b)/(f) point at wrong architecture. Recomposed P2+ scope into 4 categories: enforcement flip (Cat 1) OUT-OF-SCOPE per Chris's own gate discipline; observation-period foothold (Cat 2) shippable; startup config log (Cat 3) optional; graph refresh (Cat 4) required.
6. **Cat A SIGN dispatch** — Rigby verified all 3 substantive claims at HEAD:
   - Substrate mismatch real (CostTracking vs LLMCallEvent cite verified)
   - No partial enforcement shipped (`set_mode('freeze')` grep at HEAD returns only comments + test helper; zero runtime callers)
   - HAI consolidation is single-dispatch (bridge line 762-776 takes list, dispatches one item)
   - Scope soundness 0.86 → **PICK** Cat 2 + Cat 4, with 5 refinements to fold.
7. **Chris D-verdict** — "Lets go with 1" (ratifying scope + `would_freeze` naming + Cat 3 deferred as Rigby recommended).
8. **Implementation** — Cat 2 + Cat 4 shipped per Cat A ratified scope. 5 refinements folded during implementation: idempotency-tied semantics (softened per Cat B), `would_freeze` naming standardized, docstring touchpoint updated, test coverage per Rigby contract, Cat 3 deferred.
9. **Cat B implementation SIGN** — Rigby 0.91 confidence → **REVISE (tiny) → APPROVE**. One comment softened (aspirational "tied to HAI idempotency anchor" → literal "same tick / same breach set as HAI dispatch"). Re-ran tests: 21/21 pass. Chris approve → PR #3060 opened.
10. **Merge + cascade** — squash-merged to main as `be9b9b1c`; cascade executed (celery-recycle, build_docs_index, build_rag_corpus, sync_docs_index_to_documents, embed backlog, build_docs_provenance).

---

## §3 Rigby SIGN provenance

| Stage | Pin | Confidence | Verdict | Refinements folded |
|---|---|---|---|---|
| Candidate scope SIGN | `pa-777a3fe46a52480e` (retired) | Cand 1: 0.72; Cand 2: 0.84 | REFRAME + DEFER + independent rec for §17 | Rec taken by Chris |
| Cat A scope | `pa-f2bc0abba82849a9` | 0.86 | PICK (Cat 2 + Cat 4) | 5: idempotency semantics, naming standardization, docstring, tests, Cat 3 defer |
| Cat B implementation | `pa-f2bc0abba82849a9` | 0.91 | REVISE (tiny) → APPROVE | 1: comment softened |

Total substantive Rigby SIGN dispatches: 3 (scope, Cat A, Cat B). All folded before merge.

---

## §4 Substrate correction — S2734 baseline vs S2735 P1 reality

**Graph §17 as authored at S2734 baseline** (`platform_capability_graph.md:457-477`) described a speculative chain that P1 did NOT ship:

- Named substrate: `LLMCallEvent` at `llm_call_wrapper.py:195` + `cost_usd` field
- Missing links (a) add `cost_usd` on LLMCallEvent, (b) `_estimate_cost()` at wrapper, (f) direct openai import sweep

**Actual P1 shipment** (Session 2735 — 3 files: `cost_threshold_monitor.py`, `tasks_cost_protection.py`, `human_attention_bridge.py::create_cost_breach_attention`) chose `CostTracking.estimated_cost_usd` as substrate. Rationale documented explicitly in `cost_threshold_monitor.py:18-30`: "CostTracking sees ~54.5x more rows than LLMCallEvent today (3,215 vs 59 rows over 7d). CostTracking is the canonical cost substrate; LLMCallEvent covers only wrapper-instrumented paths (~1.8% of calls)."

**Consequence.** Graph §17 missing-links list needed correction, not implementation. Cat 4 append-only refresh (§27) preserves §17 as authored (matching §23/§25 discipline) while surfacing the corrections readers must cross-reference. **Completeness bumped 6/15 → 11/15.**

---

## §5 Deferred / out-of-scope work carried forward

| Item | Status | Blocker | Owner at defer |
|---|---|---|---|
| **Cat 1 — enforcement flip (auto-`set_mode('freeze')`)** | DEFERRED | S2735 P1 gate discipline: requires "monitor observation period + explicit approval" | Awaits Chris D-verdict |
| **Cat 3 — startup config log** | DEFERRED for S2739 (Rigby recommendation) | Optional cleanup; can ship independently | Available for future session |
| **Auto-thaw path decision** | Candidate missing link noted in §27.2 | (i) TTL-bound, (ii) manual-only, (iii) hybrid — needs Chris D-verdict before enforcement wiring | Awaits Chris D-verdict |
| **LLMCallEvent coverage-gap arc** (direct-openai import sweep, `cost_usd` on LLMCallEvent) | Orthogonal to §17 | Separate telemetry-completeness arc; NOT a cost-protection dependency | Available for future arc |
| **Auth full scope (§18)** | Chris-blocked | 4-axis §14.14 D-verdict pending | Awaits Chris D-verdict |
| **Chapter 8 Runtime Discipline MINOR** | DEFERRED (twice; third defer this session) | Chris hesitation signal; better vehicle candidate: CDR-004 or ops runbook per Rigby SIGN | Awaits Chris decision on vehicle |

---

## §6 Cross-arc pattern posture — CX-P7 avoidance

The S2739 slice was scoped explicitly to AVOID **CX-P7 declared-but-unenforced-contract** from `cross_domain_integration_audit.md` v4 §14.6. Shipping Cat 1 (enforcement flip) without observation-period data + explicit Chris approval would have created the exact pattern the audit warns against: `cost_protection_enforce_mode='freeze'` would be a *declared* contract with no *runtime enforcement* — matching the F-B-CRIT-2 silent-401 shape (declared inheritance, unenforced in practice).

Observation-period foothold (`would_freeze` shadow + payload field + shadow log) surfaces counterfactual data for future Chris D-verdict without violating the declared-contract enforcement principle. Explicit "avoidance-by-scoping" of CX-P7 is a new evidence point for the audit's pattern catalog.

---

## §7 Playbook rules exercised

- **PLAYBOOK-2.2.2** (R2 SIGN before Cat A) — Cat A + Rigby SIGN dispatch preceded Cat B implementation.
- **PLAYBOOK-6.10.5** (verify-before-build discipline — CD-49 discharge codification) — Cat A independent read caught the substrate mismatch BEFORE writing any code; reused P1-shipped substrate rather than shipping the graph's speculative one. This is a live application of `feedback_cycle_1a_verify_before_build.md` methodology to a non-ADR arc.
- **§17 (append-only refresh discipline)** — capability graph §27 follows §23/§25 pattern; §17 body preserved for provenance.

---

## §8 Post-merge cascade verification

| Step | Command | Result |
|---|---|---|
| 1. Celery recycle | `make celery-recycle` | 5 workers up + beat scheduler |
| 1a. Task registry check | `celery inspect registered \| grep check_cost_thresholds` | Registered on all 5 workers ✓ |
| 2. Doc index refresh | `python manage.py build_docs_index` | 3049 docs indexed |
| 3. RAG corpus rebuild | `python manage.py build_rag_corpus` | 36,895 chunks across 3049 files |
| 4. Sync docs to Document table | `python manage.py sync_docs_index_to_documents` | 2 updated, 3047 skipped |
| 5. Embed unembedded | `python manage.py embed_documents --all-unembedded` | 0 unembedded (backlog clear) |
| 6. Sync + embed force | `python manage.py sync_docs_index_to_documents --embed` | 0 updated (idempotent) |
| 7. Provenance refresh | `python manage.py build_docs_provenance` | 2499 docs indexed (HIGH=1605 / MED=394 / LOW=5 / UNKNOWN=495) |
| 8. Corpus content verification | `grep -c "Cost Protection refresh" .rag/corpus.jsonl` | 1 hit ✓ |
| 9. `would_freeze` in corpus | `grep -c "would_freeze" .rag/corpus.jsonl` | 2 hits ✓ |

Rigby's RAG will retrieve §27 content on §17 / cost-protection / `would_freeze` queries.

---

## §9 What Chris ratified (for archive)

- **Candidate selection:** §17 Cost Protection P2+ (per Rigby's independent rec over both Claude-proposed originals).
- **Scope:** Cat 2 (observation-period foothold: `would_freeze` shadow) + Cat 4 (capability graph §17 refresh).
- **Naming:** `would_freeze` (not `would_have_frozen`); consistent across code / tests / graph refresh.
- **Cat 3 disposition:** DEFERRED per Rigby recommendation (surface-area concern).
- **PR approval:** "approve — open the PR"; PR #3060 opened.
- **Merge + cascade approval:** "merge it and run the cascade"; squash-merged, cascade executed end-to-end.

---

## §10 What this research taught us about how to do research

*(per feedback_xx99_meta_methodology_section.md discipline — applied here to a direct-EOS campaign, not just canonical summaries)*

### §10.1 What worked
- **Scope SIGN over both original candidates, not just the top pick.** Rigby routing both surfaced a third candidate neither had considered. Prevented a session of shipping the wrong thing entirely.
- **Cat A independent read before dispatch.** Caught the substrate mismatch (LLMCallEvent vs CostTracking) in the first grep pass. Would have shipped a speculative migration otherwise.
- **Append-only §27 for graph refresh.** Preserved §17 provenance while surfacing corrections; matched existing discipline (§23/§25 precedent).
- **Deliberate CX-P7 avoidance framing.** Explicit anti-pattern posture in the PR + handoff makes the scope-shrinkage defensible in future review.

### §10.2 What to codify (candidate)
- **"Verify graph/audit specs against HEAD before treating them as ratified missing-links lists."** The graph is drafted, not runtime-verified per section. Cross-arc pattern candidate: audit-doc claims older than their source code decay; verify-before-implement discipline extends to research-artifact-derived roadmaps, not just to code reuse.

### §10.3 Anti-patterns to avoid
- **Do NOT propose an "obvious" candidate from a queue without cross-referencing audit POSTURE-PENDING debt AND capability-graph blockers.** The two initial candidates were both blocked; Rigby's cross-check saved a session.
- **Do NOT ship enforcement paths that satisfy a config gate but have no observation data.** The exact CX-P7 shape the audit warns against.

### §10.4 Suggestions for the playbook
- Chapter 6 §6.10 verify-before-build (PLAYBOOK-6.10.5) explicitly covers evidence provisioning. This session showed the same principle applies to *implementation dependency verification against HEAD* (was the substrate the graph named actually shipped?). Candidate for a §6.13 or §10.16 subsection: "before implementing a missing link named in an audit/research artifact, verify the substrate the artifact names is still the substrate in production." Post two-trigger threshold — S2739 is the first trigger. Do NOT codify yet.

### §10.5 Suggestions for future direct-EOS campaigns
- Always dispatch scope SIGN with an option to REFRAME + an option for Rigby to propose an ALTERNATIVE candidate. The three-verdict lattice (PICK/DEFER/REFRAME + optional third-candidate rec) yielded a better outcome than a two-verdict yes/no.

---

## §11 Governance references

- **P1 canonical record:** `core/tasks_cost_protection.py:6-10` + `core/services/cost_threshold_monitor.py:1-47`
- **P2+ implementation:** `core/tasks_cost_protection.py::check_cost_thresholds` + `core/services/human_attention_bridge.py:762 create_cost_breach_attention`
- **P2+ tests:** `core/tests/test_cost_protection_p2.py` (6 tests, 285 LOC; all pass at S2739 close)
- **Graph refresh:** `docs/research/platform/platform_capability_graph.md` §27 (append-only, 163 LOC)
- **PR:** #3060 (merged as `be9b9b1c`)
- **Chris ratification directives:** 2026-07-10 (multi-step: candidate SIGN routing → rec approval → scope + refinement ratification → PR approval → merge + cascade)
- **Rigby Cat A + Cat B SIGN pin:** `pa-f2bc0abba82849a9`
- **CX-P7 avoidance evidence:** `cross_domain_integration_audit.md` v4 §14.6 (Frontend + Auth first two triggers; S2739 explicit avoidance-by-scoping)

---

## §12 Wrapper pin state at S2739 close

- `tools/pa_local.sh` line 532: `pa-f2bc0abba82849a9` (session-2739-cost-protection-p2plus-arc)
- Arc pin held OPEN pending Chris "session close" signal — future S2740 session-open should either continue this arc (further P2+ work) OR retire this pin + mint fresh S2740 pin per §16 arc-close discipline.

---

**Session 2739 CLOSED.** Awaiting Chris signal for S2740 open — either continue Cost Protection arc (Cat 1 enforcement flip after observation-period data accumulates) or select a new direct-EOS candidate from the S2739 queue.
