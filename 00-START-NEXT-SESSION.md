# Next Session — Start Here

---

## READ THIS FIRST — LOCAL vs PRODUCTION RIGBY TRAP + ACTIVE GROUP 2100 ARC PIN

`tools/pa_chat.py:41` has `DEFAULT_BASE_URL = "http://localhost:8000"` (already local by default as of S1249 PR #2712). The `.env` file's `PA_API_TOKEN` is the **production** token — if you call `pa_chat.py` bare against local without a local-token override, you'll get 401. Always use `tools/pa_local.sh` (sets URL + local token + arc pin).

**ACTIVE ARC PIN:** Group 2100 arc pin `pa-18b095bb7c4740be` is ACTIVE as of S2100 open 2026-07-04 (minted via `session_tool.create_fresh` after `pa-dd7e973617da464d` retired at S2099 close). `tools/pa_local.sh:215` dispatches into this pin. Do NOT rotate this pin during the Group 2100 arc (S2100 → S2101 → **S2102** → S2103 → S2104 → S2199) — playbook §16 arc-standard behavior + MC-4 CODIFICATION-CONFIRMED-with-scope-guardrails at S1999 close (guardrails-retained-but-generalized per S2099 MC-4 extension).

### The correct LOCAL invocation
```bash
tools/pa_local.sh "message"
```

**Before your first `pa_local.sh` call each session, ask Rigby to run `platform_config_tool overview` and confirm `service_context: local`.**

## READ THIS SECOND — GROUP 2100 P0 PARENT SCOPING LANDED AT S2100; NEXT-SESSION = S2101 P1 CAT A CORPUS STATE REALITY→KNOWLEDGE GAP AUDIT

**Group 2100 RAG / Document Loading (Knowledge Loop) arc: S2100 parent scoping shipped → next is S2101 P1 Cat A Corpus State Reality→Knowledge Gap Audit** per parent `2100_rag_document_loading_domain_scoping.md` §5.1.

- **Active arc pin:** `pa-18b095bb7c4740be` — preserved through S2101 per playbook §16 arc-standard behavior + MC-4 CODIFICATION-CONFIRMED-with-scope-guardrails.
- **Arc progress:** S2100 parent scoping (shipped) → S2101 P1 (next) → S2102 P2 Ingestion Pipeline → S2103 P3 Retrieval Authority Framework + Corpus Governance Design → S2104 P4 Behavior Substrate Structured Observation + Integration → S2199 xx99 canonical summary. Runtime target: 6 sessions (matches Groups 1900 + 2000+ shape).

## READ THIS THIRD — S2100 PARENT SCOPING FRAMING + RATIFICATION STATE

Parent scoping doc: `docs/research/domains/rag_document_loading/2100_rag_document_loading_domain_scoping.md` (~1400+ lines post-SIGN-fold; `status: active`).

**Arc frame (Chris + Claude conceptual, NOT inherited canonical doctrine — verified S1799 zero "loop" mentions + S1899 one finding-level "learning-loop-coupling" use, not arc-frame doctrine):**
- Group 1700 = execution / observability lens (retro-fitted)
- Group 1800 = human feedback / learning lens (retro-fitted; partial S1899 finding-level support)
- **Group 2100 = knowledge lens (proposed)** — how does validated research / code / doc knowledge become operational memory that improves Rigby's future behavior?

Loop-closure rubric: *Execution Loop = execution signals feed ops governance; Learning Loop = human feedback feeds preference/skill updates; Knowledge Loop = corpus governance feeds retrieval behavior + decisions.*

**Reality → Research → Knowledge → Behavior conceptual model** — arc audits Research → Knowledge and Knowledge → Behavior transitions.

**Central lens question (maturity form per Q3 SIGN fold):** *"Where on the spectrum from passive index → governed institutional knowledge layer does Rigby's corpus currently sit, and what contracts (authority / freshness / governance / behavior) are required to reach the next maturity tier?"* Institutional-knowledge-layer defined with 5 falsifiable acceptance criteria per §1 preamble.

**Load-bearing hypothesis (D2100.7 conditional elevation rule per Q12 SIGN fold):** "RAG freshness bounds SIGN quality" is a hypothesis. Group 2100 P4 delivers Option A structured observation (retrospective incident review, N ≥ 10 cases per Q6 SIGN fold). If P4 finds repeated attributable patterns with enforceable remediation hooks → elevate hypothesis → provisional contract. If weak → keep as hypothesis.

**D-verdicts (all 10 RATIFIED or EXECUTED as of 2026-07-04):**
- D2100.1a [B] Scope lock (RATIFIED via Chris "agree all")
- D2100.1b [NB] Framing adoption with Q1-fold disclaimer (RATIFIED)
- D2100.2 [B] 4-child + xx99 taxonomy Option (b) (RATIFIED)
- D2100.3 Arc pin mint (EXECUTED — pa-18b095bb7c4740be)
- D2100.4 Rigby SIGN cycle 1 (EXECUTED — 9 STRENGTHEN + 3 CLEAN + 0 FOLD + 0 REJECT)
- D2100.5 Design-preparation authority only (RATIFIED via Chris directive point 9)
- D2100.6 Central lens question with Q3-fold maturity form (RATIFIED)
- D2100.7 Hypothesis + Q12-fold conditional elevation (RATIFIED)
- D2100.8 [B for P3 close] 8-axis retrieval authority framework adoption (RATIFIED IN PRINCIPLE)
- D2100.9 [B for P1 close] Hybrid metadata contract shape (RATIFIED)
- D2100.10 [NB] Health Score as standing governance metric (DEFERRED to P4 close; revisit S2199)

## READ THIS FOURTH — S2101 P1 CAT A CORPUS STATE REALITY→KNOWLEDGE GAP AUDIT SCOPE

Per parent §5.1:

**Scope.** Audit the current state of the RAG corpus. What documents exist on disk (Reality), what's in the Document table (Research → institutional record), what's embedded and retrievable (Knowledge), and where the gaps are.

**Load-bearing questions:**
- Corpus state gap matrix: on-disk → `docs/_index.json` → `.rag/corpus.jsonl` → `Document` rows → `DocumentEmbedding` rows deltas per cascade step
- Q1 (redistributed per W7): How do we know every closed research artifact is embedded?
- Q4: How do we detect missing embeddings after cascade PRs?
- Q8-a: What metadata EXISTS in `DocumentEmbedding` schema today? (P3 designs SHOULD-carry contract.)
- 18-field metadata ROI-trim (schema-present / derivable at ingest / requires frontmatter / research-artifact-specific)
- Fatal-if-missing categorization (per D2100.9 hybrid contract): core required + doc-type profile

**Belongs-to boundary rule (per Q5 SIGN fold):** P1 deliverable = gap matrix + metadata inventory (static snapshot) with high-level "likely cause" tags only — does NOT explain causality beyond brief hypotheses (that's P2's job).

**Expected shape.** ~700-1000 lines. 20-section playbook §11.2 template child-audit shape. Ships: Reality→Knowledge gap matrix + metadata inventory table + knowledge-debt classification framework + core-required metadata contract candidate list.

**Inherits from prior work:**
- S1304 §14 D7 `DocumentEmbedding.ingested_via` orphan claim — full-tree recheck routed via S1399 §19 R1
- S1304 §15 T1 provenance-index rebuild cadence — freshness inventory side
- MEMORY.md `feedback_cascade_pr_must_include_embed_step` — informalize S1802 6-unembedded-docs incident as knowledge-debt sample
- Group 2000+ S2001 F3 SPIDER_DATA MISSING-producer / WEAK-consumer

## READ THIS FIFTH — OUTSTANDING RESIDUALS

### §7 anchor-update batch from S2099 (queued as separate follow-up PR)

Per Q4b SIGN batch-discipline attestation at S2099 close + parent §5.5 handoff: the §7 anchor-update batch is queued as a single atomic follow-up PR — NOT bundled with S2100 arc-open per parallel-safety scope discipline. Batch scope:

- 10 per-plane topic docs
- 1 index / overview doc
- `PLATFORM_INVENTORY.md` subsection
- `PLATFORM_WHAT_IT_IS.md` §7 update
- `EVENT_SYSTEM_INVENTORY.md` §13 with NEW §13.1.5 Fleet Events sidecar subtable
- `ARCHITECTURE_INDEX.md` v70 §1.73 (already registered at S2099 close)
- `CLAUDE.md` Detailed Breakdown row (Fleet Events)
- `OPEN_ARCS.md` Closed section

Owner: Group 2000+ residual (Claude next session or dedicated batch session). Not blocking S2101 P1 open but should land before S2199 to keep anchors current.

## SESSION READY CHECK (before opening S2101 P1)

Before writing the S2101 P1 audit:
1. `tools/pa_local.sh "platform_config_tool action=overview"` → confirm `service_context: local`
2. Verify arc pin ownership: Rigby returns `conversation_owner_match=true`
3. Read parent scoping doc `docs/research/domains/rag_document_loading/2100_rag_document_loading_domain_scoping.md` §5.1 + §7 anti-scope + §8 ratified D-verdicts
4. Read S1304 boundary audit `docs/research/domains/memory/1304_memory_docs_rag_boundary_audit.md` for depth/lens starting inventory
5. Verifier-loop pre-draft: sample corpus row counts via ORM (`Document.objects.count()`, `DocumentEmbedding.objects.count()`); list latest 20 files under `docs/` + check embedded state for each; validate S1304 findings still hold (grep `lru_cache(1)` at `_load_provenance_docs`, check `AIEmployee` handles for docs owner, check beat schedule for embedding periodic tasks)

**S2101 P1 open command (Chris short command):** `Start research group 2101` or `Continue research group 2100` — either invokes S2101 P1 Cat A Corpus State Reality→Knowledge Gap Audit under Group 2100 arc pin `pa-18b095bb7c4740be`.
