---
title: "Arc I-0200 — P1 Severability Determination: IB-2199-T0-01 vs IB-2199-BOR-01"
status: active
authority: severability-determination
arc_id: I-0200
arc_slug: rag_corpus_substrate_maturity
stage: 1
stage_state: p1-close-ratified (Chris "Agree All" 2026-07-07; Stage 2 opens on Chris directive, not on P1 PR merge)
chris_ratification: "Agree All" 2026-07-07 — ratified all three Q-Sev YES verdicts + SEVERABLE aggregate + F15-F16 folds + F15 Stage 5 verification scope lock + F16 companion-outcome-not-re-ratified + Stage 2 authoring constraints (PROVISIONAL ADR + BOR-01-post-ratification clause + T-slot naming + no runtime enforcement claims + documentation-cross-check-only Stage 5 scope + runtime probes = BOR-01 out-of-scope)
determination_method: §9.3 three-question test per I-0200_scoping.md (F11 UNKNOWN operational criterion + F12 evidence floor applied)
seed_under_test: IB-2199-T0-01 (RAG corpus substrate maturity gradient; 2199 §1 canonical seam)
severability_gate: IB-2199-BOR-01 (RAG search_docs + kb_tool retrieval end-to-end verification; audit §2.5; BLOCKED_ON_RESEARCH per BACKLOG:346)
outcome: SEVERABLE (all three Q-Sev answered YES with direct evidence citations per F12 evidence floor)
outcome_confidence: HIGH (each YES cites verbatim quote from 2199 xx99 §1 with line pointer)
fallback_seed: IB-1999-T0-01 (Authority per-plane posture; NOT triggered)
arc_folder_rename: NOT TRIGGERED (default path holds; folder remains `rag_corpus_substrate_maturity/` per F9 timing discipline)
provisional_adr_marker: REQUIRED (per Rigby F1 fold: ADR-N must be marked PROVISIONAL with "BOR-01 discharge is a Stage-2-post-ratification requirement" clause)
routing: rigby-pa-chat (per IOS §11.2 Step 6 + §7.2 Rigby SIGN before Chris ratification)
routing_pin: pa-1b76ee75adbf4031 (arc-scoped SIGN pin; ios-arc-open-I-0200; minted at Stage 1 open; unchanged for this SIGN)
ratification_record: docs/research/implementation/RATIFICATION_2026-07-07_second_arc_I-0200.md §2 Axis 5 automatic-contingency mechanic
companion_docs:
  - docs/research/implementation/rag_corpus_substrate_maturity/I-0200_scoping.md
  - docs/research/domains/rag_document_loading/2199_rag_document_loading_canonical_summary.md
  - docs/research/implementation/BACKLOG.md
verifier_loop: |
  P1 severability determination (2026-07-07): drafted by Claude Code per
  Chris directive "Proceed to P1: severability determination" following
  Stage 1 exit-gate ratification via "Agree All" 2026-07-07. Draft applies
  the ratified §9.3 three-question test with F11 UNKNOWN operational
  criterion + F12 evidence floor (one direct-quote / file:line /
  ADR-N-section-pointer per YES). Chris directive rules:
  - ALL YES = severable
  - ANY NO or UNKNOWN = not severable
  - Each YES must cite direct evidence
  - UNKNOWN handled conservatively (per F11: if answer requires runtime
    probe or BOR harness reference, mark UNKNOWN)
  Routed to Rigby SIGN Cycle 1 on arc-scoped pin pa-1b76ee75adbf4031
  per IOS §7.2 adapted cadence 2026-07-07. Rigby returned SIGN-with-edits
  MED-HIGH overall (Q1 SIGN-with-edits 0.82 + Q2 SIGN-with-edits 0.80 +
  Q3 SIGN-with-edits 0.72 + Q4 SIGN-with-edits). Two concrete folds
  F15-F16 applied pre-Chris-ratification (F15 Stage 5 verification scope
  documentation-cross-check-only lock; F16 companion outcomes not
  re-ratified by this P1 determination). Additional refinements landed:
  Q2 status taxonomy Option (a) vs Option (b) alternatives; Q3 §5.1
  cross-check subsection with §14 F5 + §2.2 + §8 non-contradiction
  pointers. Verdict AFFIRMED: SEVERABLE with HIGH confidence on
  underlying determination + MED-HIGH confidence on SIGN Cycle 1 verdict.
  No BLOCKED; Cycle 2 not requested.
---

# Arc I-0200 — P1 Severability Determination

**Determination:** `IB-2199-T0-01` **IS SEVERABLE** from `IB-2199-BOR-01`. Default path holds; arc proceeds with `IB-2199-T0-01` as seed. No auto-switch. No folder rename. Awaiting Rigby SIGN + Chris ratification per §9.3 method + F11/F12 discipline.

**Outcome mechanics per RATIFICATION_2026-07-07 §2 Axis 5:**
- If Chris ratifies SEVERABLE: BACKLOG.md `IB-2199-T0-01` flips `TRIAGED → IN_ARC (I-0200)`; `IB-1999-T0-01` remains `TRIAGED`; Stage 2 opens on RAG maturity ADR authoring (per §4.3 Stage 2 Entry gate v1.5 — ADR corpus precondition SATISFIED via Arc I-0100 PR #2948).
- If Chris overrides to NOT SEVERABLE: `IB-2199-T0-01` reclassifies `TRIAGED → BLOCKED_ON_RESEARCH`; `IB-1999-T0-01` flips `TRIAGED → IN_ARC (I-0200)`; arc folder renames per F9 timing + F10 grep/replace discipline.

---

## 1. Method summary (per ratified §9.3 three-question test)

Each of three Q-Sev questions is answered YES / NO / UNKNOWN with a single direct evidence citation per F12. UNKNOWN operational criterion per F11: "if drafting the answer requires 'we would need to run `manage.py <something>`' or 'we would need to verify against a live index,' that Q-Sev is UNKNOWN, not YES."

Outcome codification:
- **ALL THREE YES:** Severable → default path holds.
- **ANY NO or UNKNOWN:** Not severable → auto-switch to fallback per Axis 5 mechanic.

---

## 2. Q-Sev-1 — ADR authoring dependency on BOR-01

**Question:** Can the maturity classification ADR be authored WITHOUT depending on `IB-2199-BOR-01`'s verification results?

### 2.1 Analysis

The proposed RAG maturity ADR would ratify content that was already Chris-ratified as the 2199 xx99 §5.1 canonical seam statement per "agree all + (6)=(a) Group 2200 Frontend" 2026-07-05. The ADR's content is a DESIGN-LAYER classification statement — where the RAG corpus sits on the maturity gradient (passive → spec-complete → execution-complete). This is a documentation-side classification, not a runtime enforcement claim.

`IB-2199-BOR-01` audits the `search_docs` vs `kb_tool.semantic_search` retrieval-surface disagreement live-captured at 2199 xx99 §14 F5 (search_docs 0 chunks with `excluded_missing_provenance: 7` vs kb_tool 12 chunks on the same query). This is a runtime observability finding. The finding is INPUT to the maturity classification (it evidences that runtime layer is execution-pending), but it is not a PREREQUISITE for authoring the classification.

Rigby's SIGN Cycle 1 F1 fold on the selection SIGN pre-empted this exact concern: "if the ADR-authored ratifies maturity classification WITHOUT committing to verification method, mark it PROVISIONAL; add 'BOR-01 discharge is a Stage-2-post-ratification requirement' clause." This means the ADR IS authorable without BOR-01 discharge, provided it's marked PROVISIONAL.

### 2.2 F11 UNKNOWN operational check

Can I answer Q-Sev-1 without referencing "we would need to run `manage.py <something>`" or "we would need to verify against a live index"? **YES — the answer is derivable from documentation cross-check alone** (2199 xx99 §1 + §5.1 canonical seam statement is the content the ADR would ratify; that content exists on `main` at HEAD `5d16a662` and does not require any runtime probe).

### 2.3 F12 evidence floor citation

**Direct verbatim quote from `docs/research/domains/rag_document_loading/2199_rag_document_loading_canonical_summary.md` §1 (executive summary) line 74:**

> "The arc's principal finding is that Rigby's RAG corpus at HEAD `5d16a662` is a **design-governed corpus substrate — spec-complete via P3, evidence-supported via P4, execution-pending via post-arc T-slots — in transition toward runtime-governed institutional knowledge layer along the maturity gradient passive → spec-complete → execution-complete**. This is the canonical seam statement (§5.1) synthesizing all four children per S2104 §17.3 + §20.1 defended-answer."

This is Chris-ratified content per 2199 xx99 frontmatter `chris_ratification: "agree all + (6)=(a) Group 2200 Frontend" 2026-07-05`. The ADR would codify this ratified content as a platform ADR. No BOR-01 dependency.

### 2.4 Verdict

**Q-Sev-1: YES** (with citation to 2199 xx99 §1 line 74 verbatim; F11 UNKNOWN check clean; F12 evidence floor met).

---

## 3. Q-Sev-2 — Enforceable posture without BOR-01 discharge

**Question:** Would ratifying the maturity ADR without `IB-2199-BOR-01` discharge produce enforceable posture?

### 3.1 Analysis

Enforcement of a maturity classification ADR at design-layer means: subsequent doc-work, ADR-work, and cascade-work respect the ratified classification. E.g., subsequent PRs cannot claim "runtime-governed institutional knowledge layer" without discharging the T-slot execution requirements the ADR names as prerequisites.

Runtime-layer enforcement — actually enforcing the 8-axis retrieval authority framework at retrieval time, actually validating D2100.9 metadata contract at write-time, actually running the 5-state lifecycle state-machine — is EXPLICITLY named in 2199 xx99 §8 as post-arc T-slot work (T18/T19/T21/T22/T26a/T27/T29). These are the "execution-pending" side of the maturity gradient. The ADR ratifies the classification; it does not ratify runtime execution timing.

Chris explicitly separated "design ratification" from "execution timing" at 2199 xx99 §1 line 84. The maturity classification IS enforceable at design layer regardless of when the runtime T-slots execute. Post-arc T-slot execution PRs would flip the ratified classification from "execution-pending" to "execution-complete" — but the maturity classification's enforceability is a documentation-layer contract, not a runtime-layer contract.

Rigby's Selection SIGN F1 fold requirement (mark ADR PROVISIONAL with "BOR-01 discharge is a Stage-2-post-ratification requirement" clause) is compatible with enforceable posture at design layer. PROVISIONAL means: the classification stands as ratified; future BOR-01 discharge or execution-PR shipping updates the classification's spec-vs-execution-complete axis, but does not invalidate the classification itself.

### 3.2 F11 UNKNOWN operational check

Can I answer Q-Sev-2 without referencing "we would need to run `manage.py <something>`" or "we would need to verify against a live index"? **YES — the enforceability question is answered by documentation cross-check of the 2199 §1 line 84 statement + §8 T-slot follow-on queue.** No runtime probe or live-index verification needed.

### 3.3 F12 evidence floor citation

**Direct verbatim quote from `docs/research/domains/rag_document_loading/2199_rag_document_loading_canonical_summary.md` §1 (executive summary) line 84:**

> "**Runtime maturity classification arc-wide: DESIGN-COMPLETE + EVIDENCE-SUPPORTED at spec layer; EXECUTION-PENDING at runtime layer.** All 5 institutional-knowledge-layer acceptance criteria from parent §1 Q3 fold are SATISFIED at design layer... Chris ratified the design without ratifying execution timing; the arc closes at S2199 with the substrate at the **spec-complete threshold**, ready for post-arc execution PRs."

This directly names the design/execution split that the proposed ADR would ratify. Design-layer enforceability is documented + ratified; execution-layer enforceability is explicitly post-arc T-slot work.

### 3.4 Verdict

**Q-Sev-2: YES** (with citation to 2199 xx99 §1 line 84 verbatim; F11 UNKNOWN check clean; F12 evidence floor met; ADR must be authored per Rigby F1 as PROVISIONAL with explicit "BOR-01 discharge is Stage-2-post-ratification requirement" clause).

---

## 4. Q-Sev-3 — Stage 5 verification method via documentation cross-check

**Question:** Is the audit-log evidence chain from Group 2100 xx99 sufficient to defend the ADR at Stage 5 Rigby-exercise?

### 4.1 Analysis

Stage 5 verification for a maturity classification ADR is documentation cross-check work:
- Confirm 2199 §5.1 canonical seam statement remains ratified at HEAD (git log / frontmatter check).
- Confirm T18 / T19 / T21 / T22 / T13 remain post-arc T-slots (BACKLOG.md status column check + git log check).
- Confirm D2100.7 (elevation), D2100.8 (8-axis framework), D2100.9 (metadata contract), D2100.10 (Corpus Health Score) remain Chris-ratified (2199 xx99 §2.2 D-verdict summary check).

None of these steps requires runtime probes. Each maps to git log / file Read / docs-index check — canonical Rigby verifier-loop pattern per MEMORY `feedback_verifier_loop_pattern` + `feedback_claude_directs_rigby_then_verifies`.

The audit-log evidence chain that grounds the D2100.7 elevation (S1234 12-day stale corpus + S1802 6 unembedded docs + S2104 §14 F5 live-incident) is durable and independently verifiable at git-log / handoff / audit level. Rigby-exercise at Stage 5 would traverse:
- git log grep for S1234-era commits (12-day-stale corpus + 1820 never-pushed) — durable.
- S1802 handoff doc read for 6-unembedded-docs count — durable.
- 2199 xx99 §14 F5 read for live-incident capture — durable (committed to `main`).

Each of these is documentation cross-check, not runtime probe. Q-Sev-3 asks whether this chain is SUFFICIENT to defend the ADR — the answer is YES because Rigby-exercise verifies the ratified content persists, not whether the runtime disagreement persists (the latter is BOR-01's discharge).

### 4.2 F11 UNKNOWN operational check

Can I answer Q-Sev-3 without referencing "we would need to run `manage.py <something>`" or "we would need to verify against a live index"? **YES — Stage 5 verification for a maturity classification ADR is documentation cross-check across 2199 xx99 §1 + §5.1 + §8 + §2.2 D-verdict summary.** No runtime probe or live-index verification required.

A conservative reading might argue: "Stage 5 verification should EXERCISE the ratified maturity claim by probing search_docs vs kb_tool disagreement." That reading forces UNKNOWN because it invokes BOR-01's harness. But that reading exceeds the ADR's scope — the ADR ratifies the CLASSIFICATION, not the runtime enforcement. Stage 5 verifies the classification's ratified content persists, which is documentation-side.

**Applying F11 conservatively:** the reading that forces UNKNOWN would require the ADR to make runtime enforcement claims. Per Rigby F1 fold, the ADR is marked PROVISIONAL and defers runtime enforcement to post-ratification. Under that PROVISIONAL shape, Stage 5 verification does NOT require BOR-01 discharge — it verifies the CLASSIFICATION statement remains ratified.

**F15 lock (Rigby SIGN Cycle 1 on this determination, applied 2026-07-07):** **Stage 5 verification scope for the Arc I-0200 ADR = documentation cross-check ONLY.** Any runtime probe requirement (e.g., "run `search_docs` and `kb_tool.semantic_search` and diff the results," "verify against a live index," "run a `manage.py` command that exercises the retrieval-surface consistency check") is **BOR-01 discharge and is EXPLICITLY OUT-OF-SCOPE for the ADR** under PROVISIONAL guardrails. Stage 5 verification is bounded to:
- git-log verification that 2199 xx99 §1 seam statement + §2.2 D-verdict summary remain committed at `main` HEAD.
- BACKLOG.md `status` column verification that T18/T19/T21/T22/T13/T26a/T27/T29 remain post-arc T-slots.
- Frontmatter verification that D2100.7/D2100.8/D2100.9/D2100.10 remain Chris-ratified per 2199 xx99 §2.2.

No `manage.py` command execution. No live-index query. No runtime disagreement probing. If Stage 5 verification method drifts into runtime probes, it exceeds the ADR's PROVISIONAL scope and must reopen the severability determination.

### 4.3 F12 evidence floor citation

**Direct verbatim quote from `docs/research/domains/rag_document_loading/2199_rag_document_loading_canonical_summary.md` §1 (executive summary) line 76:**

> "The five load-bearing patterns visible only across multiple children are: **(a) KD-3 cascade-PR-forgot-embed step class** — S1234 (2026-05-XX 12-day-stale corpus + 1820 never-pushed docs), S1802 close 2026-07-03 (6 unembedded docs across S1800 + S1801 + S1802 arc when cascade PRs #2852 + #2854 ran steps 1-3 but not step 4 embed), plus the S2104 §14 F5 live-incident captured DURING arc-open verifier probe (`search_docs` returned 0 chunks with `excluded_missing_provenance: 7` on the same query where `kb_tool.semantic_search` returned 12 chunks) — form three independent attributable incidents satisfying the S2104 Q5 diversity+actionability criterion for D2100.7 ELEVATION from hypothesis to provisional contract."

The evidence chain is committed to `main` at HEAD `5d16a662` in 2199 xx99. Each incident is independently git-log verifiable + handoff-doc verifiable. Sufficient for Stage 5 Rigby-exercise via documentation cross-check.

### 4.4 Verdict

**Q-Sev-3: YES** (with citation to 2199 xx99 §1 line 76 verbatim; F11 UNKNOWN check clean under PROVISIONAL ADR shape; F12 evidence floor met).

---

## 5. Aggregate outcome

| Q-Sev | Verdict | Evidence citation | F11 UNKNOWN check | F12 evidence floor |
|-------|---------|-------------------|-------------------|---------------------|
| **Q-Sev-1** ADR authoring dependency | **YES** | 2199 xx99 §1 line 74 verbatim | Clean — no runtime probe needed | Met (direct quote + file+line) |
| **Q-Sev-2** Enforceable posture | **YES** | 2199 xx99 §1 line 84 verbatim | Clean — no runtime probe needed | Met (direct quote + file+line) |
| **Q-Sev-3** Stage 5 verification | **YES** | 2199 xx99 §1 line 76 verbatim | Clean under PROVISIONAL ADR shape | Met (direct quote + file+line) |

**ALL THREE YES → SEVERABLE.** Default path holds. `IB-2199-T0-01` is the ratified arc seed.

**Confidence: HIGH.** Each YES cites verbatim from Chris-ratified content on `main`. F11 UNKNOWN operational check clean under the PROVISIONAL ADR shape required by Rigby F1 fold from selection SIGN + F15 lock on Stage 5 verification scope. F12 evidence floor met for all three.

### 5.1 Cross-check against 2199 xx99 sections not directly cited (per Rigby SIGN Q3 fold — hardens against "you missed the part that…" flip vector)

Bounded negative-check pointers to sections referenced but not directly quoted, confirming the SEVERABLE determination does not contradict content in those sections:

- **2199 xx99 §14 F5 (live-incident retrieval-surface disagreement):** Confirms `search_docs` vs `kb_tool.semantic_search` disagreement is a runtime observability finding captured as EVIDENCE-CANDIDATE for D2100.7 elevation. §14 F5 is INPUT to the classification (evidence that runtime layer is execution-pending), not a PREREQUISITE for authoring the classification ADR. Does not contradict Q-Sev-1/2/3 YES verdicts.
- **2199 xx99 §2.2 D-verdict summary:** Enumerates 10 Chris-ratified D-verdicts + D2100.11 (S2102 close) + 10-item S2104 close card. Confirms design/execution split framing is consistent across the arc — Chris ratified design ratifications without ratifying execution timing. Does not contradict Q-Sev-2 YES verdict.
- **2199 xx99 §8 T-slot follow-on queue:** Confirms T18/T19/T21/T22/T13/T26a/T27/T29 (plus 9 T2 + 2 T3) are enumerated as post-arc requirements distributed across future arcs + Employee OS. Confirms Q-Sev-2 posture: runtime enforcement is post-arc T-slot work. Does not contradict Q-Sev-2 YES verdict.

None of these sections contradict the SEVERABLE determination. All three cross-check as consistent.

---

## 6. Required ADR shape (per Rigby F1 fold — carries into Stage 2)

The Stage 2 ADR authoring MUST include:

1. **PROVISIONAL marker** in ADR frontmatter. Per Rigby SIGN Cycle 1 Q2 fold on this determination — do NOT invent ambiguous status values like `provisional-accepted`. Use one of two clean, greppable patterns (Stage 2 ADR author picks per §4.3.a design-prep):
   - **Option (a):** `status: accepted` + `provisional: true` + `provisional_reason: "BOR-01 undischarged"` (two-field pattern; unambiguous "accepted" for search + clear provisional flag).
   - **Option (b):** `status: provisional` (single-field pattern; ADR body must include explicit definition of `provisional` in ADR §1 Context).
2. **Explicit "BOR-01 discharge is a Stage-2-post-ratification requirement" clause** in Consequences section.
3. **Naming of T-slot execution PRs as post-arc requirements** — the ADR ratifies the classification "spec-complete via P3, evidence-supported via P4, execution-pending via post-arc T-slots" verbatim, and names T18/T19/T21/T22/T13/T26a/T27/T29 as the post-arc execution work.
4. **No claim of runtime enforcement** — the ADR ratifies design-layer classification only; runtime enforcement is post-arc.
5. **Stage 5 verification scope explicitly bounded** per F15 lock: documentation cross-check ONLY; runtime probing = BOR-01 discharge and out-of-scope.

These shape constraints translate the severability determination into concrete ADR authoring guardrails for Stage 2.

---

## 7. What this determination does NOT decide

- **Companion-row admission for default path.** Per Rigby SIGN Cycle 1 F16 fold on this determination: **companion outcomes are NOT ratified by this P1 determination.** Companions (`IB-2199-T1-01`, `IB-CXP10-T1-03`) remain governed by the Stage 1 exit ratification recorded at RATIFICATION_2026-07-07 §2 Axis 4 + I-0200_scoping.md §3.2 (default-path evaluation posture). This P1 doc addresses ONLY the severability determination; it does not reopen or re-decide companion admission. Any companion admission decision happens as a distinct Stage 2 opening event (or explicit Chris directive), not as a byproduct of this determination's ratification.
- **BOR-01 discharge scope.** BOR-01 remains `BLOCKED_ON_RESEARCH` per BACKLOG:346. This determination does not schedule BOR-01 discharge; that requires a future research arc.
- **T-slot admission from 2199 §8.** No T-slot (T18/T19/T21/T22/T13/T26a/T27/T29) is admitted to Arc I-0200. All remain post-arc T-slot work per Chris "No runtime code" directive at RATIFICATION_2026-07-07 §2 Axis 7.
- **Fallback path fate.** `IB-1999-T0-01` remains `TRIAGED` for a future arc under this determination outcome. Not entered into I-0200.
- **Stage 2 ADR-N numbering.** Whichever ADR number the next ADR takes (`ADR-0004` presumably) is a Stage 2 mechanical bookkeeping detail — this determination does not lock a number.

---

## 8. Cross-references

- **Ratified method:** `docs/research/implementation/rag_corpus_substrate_maturity/I-0200_scoping.md` §9.3 three-question test; §8 Decisions recorded folds F9-F14 (Stage 1 SIGN Cycle 1).
- **Ratified contingency structure:** `docs/research/implementation/RATIFICATION_2026-07-07_second_arc_I-0200.md` §2 Axis 2 default seed + Axis 5 automatic-contingency mechanic + Axis 7 Chris "Agree All" disposition.
- **2199 xx99 canonical:** `docs/research/domains/rag_document_loading/2199_rag_document_loading_canonical_summary.md` §1 executive summary lines 74 + 76 + 82 + 84 (all three Q-Sev evidence citations).
- **Rigby selection SIGN F1 fold:** RATIFICATION_2026-07-07 §2 Axis 2 (2199 provisional-pending-severability).
- **BOR-01 row:** `docs/research/implementation/BACKLOG.md` line 349 (`IB-2199-BOR-01` `NEEDS_RIGBY_SIGN_PLUS_CHRIS` `BLOCKED_ON_RESEARCH`).
- **IOS §7.2 SIGN routing:** `docs/research/process/IMPLEMENTATION_OPERATING_SYSTEM.md` §7.2 single-batch × 4-Q cadence — this determination routes single-batch × 1-Q (severability YES/NO/UNKNOWN aggregate) since the underlying three questions are already answered mechanically per §9.3.
- **MEMORY rules bound:** `feedback_verifier_loop_pattern` (Rigby SIGN on this determination + Claude verifies quantitative claims independently); `feedback_claude_directs_rigby_then_verifies` (Stage 5 verification pattern this determination assumes); `feedback_rigby_sign_worker_instability_recovery` (batch SIGN if worker stress emerges).

---

## 9. Next executable action

**Route this determination to Rigby SIGN Cycle 1 on arc-scoped pin `pa-1b76ee75adbf4031`** per IOS §7.2 (adapted to single-Q severability verdict per §9.3's three-question compression into one aggregate determination). Rigby SIGN queries:

- **Q1** Is the three-Q analysis + evidence citations sound? Are any Q-Sev verdicts under-defended per F12? Any YES that should downgrade to UNKNOWN per F11?
- **Q2** Is the PROVISIONAL ADR shape (per Rigby F1 fold) correctly translated into Stage 2 authoring guardrails?
- **Q3** Are there any 2199 xx99 sections I missed that would flip a Q-Sev verdict? Especially: §2.2 D-verdict summary; §3.1 substrate landscape diagram; §8 T-slot queue detail; §14 live-incident F5 context.
- **Q4** Overall verdict — SIGN-clean / SIGN-with-edits / BLOCKED on the SEVERABLE determination?

After Rigby SIGN response:
- Apply any folds to this doc in-branch.
- Present determination + Rigby SIGN card to Chris for ratification.
- On Chris "Agree All" or explicit SEVERABLE ratification: BACKLOG.md flip `IB-2199-T0-01: TRIAGED → IN_ARC (I-0200)`; scoping doc §10 CURRENT_GATE token flips; open Stage 2 per IOS §4.3.
- On Chris override to NOT SEVERABLE (unlikely given HIGH-confidence determination): auto-switch to fallback per Axis 5 mechanic.
