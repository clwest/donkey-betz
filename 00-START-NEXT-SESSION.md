# Next Session — Start Here

---

## READ THIS FIRST — RETIRED ARC PIN + LOCAL vs PRODUCTION RIGBY TRAP + S2100 FRESH-PIN OWED

`tools/pa_chat.py:41` has `DEFAULT_BASE_URL = "http://localhost:8000"` (already local by default as of S1249 PR #2712). The `.env` file's `PA_API_TOKEN` is the **production** token — if you call `pa_chat.py` bare against local without a local-token override, you'll get 401. Always use `tools/pa_local.sh` (sets URL + local token + arc pin).

**RETIRED ARC PIN — `pa-dd7e973617da464d` retired at S2099 close 2026-07-04** via `session_tool.retire` per playbook §16 arc-close discipline (retired=true, previously_active=true, updated_count=35). **`tools/pa_local.sh:215` still hardcodes this retired pin** — any subsequent `tools/pa_local.sh` invocation will dispatch into a retired thread until rotated. **FRESH ISOLATION PIN OWED AT S2100 ARC-OPEN** via `session_tool.create_fresh` per playbook §16 arc-open fresh-thread discipline; then rotate `tools/pa_local.sh:215` to new pin + add S2099 retirement entry to header ledger inside `pa_local.sh:200-214` per S1900/S2000 arc-open documentation pattern.

### The correct LOCAL invocation (after S2100 fresh pin mint + rotation)
```bash
tools/pa_local.sh "message"
```

**Before your first `pa_local.sh` call each session, ask Rigby to run `platform_config_tool overview` and confirm `service_context: local`.**

## READ THIS SECOND — GROUP 2000+ CLOSED AT S2099; NEXT-SESSION = S2100 RAG DOCUMENT LOADING PARENT SCOPING (ARC-OPEN)

**Group 2000+ Event / Integration Architecture arc: S2000 parent shipped + S2001 P1 shipped + S2002 P2 shipped + S2003 P3 shipped + S2004 P4 shipped + S2099 xx99 shipped → ARC CLOSED 2026-07-04** per playbook §16 arc-close discipline.

- **Runtime target 6 sessions HELD (S2000 + S2001 + S2002 + S2003 + S2004 + S2099 = 6 sessions); runtime cap 8 never invoked.** Matches Group 1900 S1999 close pattern exactly.
- **Arc pin `pa-dd7e973617da464d` RETIRED** at S2099 close — EIGHTH formal arc-pin retirement in Research OS after S1399/S1499/S1599/S1699/S1799/S1899/S1999.
- **Chris D-override at S2099 close 2026-07-04:** Group 2100+ **RAG Document Loading** selected for next-arc queue lean over playbook §22 default. Candidate per project memory (`memory/project_2100_plus_queue_ranking.md`) + pre-existing scaffolding `docs/research/domains/rag_document_loading/` directory.

## READ THIS THIRD — S2100 RAG DOCUMENT LOADING PARENT SCOPING (ARC-OPEN) — EIGHTH APPLICATION OF PLAYBOOK §11.1

**S2100 opens Group 2100+ RAG Document Loading** as **EIGHTH application of playbook §11.1 9-section parent-scoping template** (after S1400 Revenue first + S1500 Sports second + S1600 Content third + S1700 Observability fourth + S1800 HumanAttention fifth + S1900 Authority Enforcement sixth + S2000 Event/Integration Architecture seventh).

**Chris D-override lean rationale (per project memory):** RAG Document Loading is a load-bearing subsystem for Rigby's cross-conversation search + long-term research continuity. Recent gaps documented at Group 1234/S1802 close ("prod corpus 12d stale + 1820 docs never pushed") + `feedback_docs_pipeline_4_step_cascade.md` + `feedback_cascade_pr_must_include_embed_step.md` MEMORY.md rules all point at RAG document loading as high-leverage arc scope.

**Arc-open protocol at S2100:**

1. **Mint fresh isolation pin** via `session_tool.create_fresh` per playbook §16 arc-open discipline. Rotate `tools/pa_local.sh:215` to new pin. Add S2099 retirement + S2100 mint entry to `pa_local.sh:200-214` header ledger.
2. **Read pre-existing scaffolding** in `docs/research/domains/rag_document_loading/` if any files exist. Verify pre-existing status.
3. **Read Research OS §5 request-classification** for RESEARCH class §8.1 startup contract.
4. **Read DOMAIN_RESEARCH_PLAYBOOK.md §11.1** for 9-section parent-scoping template.
5. **Draft S2100 parent scoping doc** `docs/research/domains/rag_document_loading/2100_rag_document_loading_domain_scoping.md` per playbook §11.1.
6. **Route to Rigby SIGN cycle 1** on fresh isolation pin. Single-batch 4-question canonical cadence per parent-scoping stage-table row.
7. **Present Chris D-verdict decision card** (child taxonomy + child count + operational defaults + Rigby-SIGN opt-in cadence + arc-pin routing lean).

**Anticipated arc shape (subject to Chris ratification at S2100 open):**

- Runtime target: 6 sessions (parent + 4 children + xx99) per Group 1900 + Group 2000+ precedent.
- Runtime cap: 8 sessions.
- Playbook §11.2 20-section child audit template application EIGHTEENTH-plus consecutive (MC-5 CODIFICATION-CONFIRMED post-S2099).
- Cat F CONSOLIDATION shape at final child slot per MC-6 CODIFICATION-CONFIRMED at S2099.

**Inheritances from prior arcs:**

- **Group 1300 Memory** — six-plane learning-write fragmentation; RAG corpus generation intersects with Memory writer plane.
- **Group 1600 Content** — S1601 T1 R.CONTENT.RAG-SCOPE (cross-tenant/workspace data exposure risk at `claims_pack_builder._from_user_documents:245` no user_id/workspace_id scoping); UNK-1 Document workspace FK schema.
- **Group 2000+ Event / Integration** — §7 anchor-update batch owed (10 per-plane topic docs + PLATFORM_INVENTORY subsection + PLATFORM_WHAT_IT_IS §7 + EVENT_SYSTEM_INVENTORY §13 + CLAUDE.md Detailed Breakdown) as single atomic follow-up PR. Consider batching within S2100 arc-open close or dedicated batch session.

## READ THIS FOURTH — S2099 CLOSE COMPLETED

**Session 2099 shipped the Group 2000+ Event / Integration Architecture xx99 canonical summary at `docs/research/domains/event_integration_architecture/2099_event_integration_architecture_canonical_summary.md`** (`status: active`, `category: canonical_summary`, `session: 2099`, `child_slot: xx99`, `research_group: 2000`; ~733 lines post-Rigby SIGN cycle 1 9 folds landed pre-commit; EIGHTH-consecutive playbook §11.3 12-section canonical-summary template + §10 meta-methodology template).

**S2099 shipped all 12 sections + Appendix:**

- §1 Executive Summary: **"design-complete, runtime-scaffolding, closure-gated on 4 T1 items"** — matches S1999 authority-enforcement close phrasing (durable-across-two-xx99s).
- §2 Per-child × 28 canonical Qs rollup + P2 D-verdicts D1-D5 + P3 D-verdicts D1-D5 + P4 5-verdict decision card.
- §3 6-substrate landscape + Fleet Events INTENTIONAL SIDECAR + 12-event catalog + 10-plane posture + canonical + mirror invariants (ASCII art diagram).
- §4 7 cross-cutting patterns (F11 Fleet Events + F13 zero-emission + F14 activation-verification + F15 correlation_id + F16 render_hint + F17 mirror_of + F18 test-gap).
- §5 Canonical seam-posture statement + posture verdict distribution normalized roll-up (Q1b fold) + resolved contradictions.
- §6 Unresolved Unknowns (12 items).
- §7 Anchor-update batch scope as single atomic follow-up PR (Q4b batch-discipline attestation).
- §8 26-item T-slot queue (2 T0/Gate + 7 T1 + 10 T2 + 7 T3) with T1 ordering per Q10 SIGN STRENGTHEN.
- §9 Cross-Links to 10 Delegated Arcs.
- §10 EIGHTH meta-methodology application with MC-3 + MC-4 (guardrails retained but generalized) + MC-6 CODIFICATION-CONFIRMED promotions.
- §11 Arc Change Log (6 rows).
- §12 Appendix Provenance.

**Rigby SIGN cycle 1 CLEAN across 4 questions at Medium-High confidence with 9 folds landed pre-commit** on preserved arc pin `pa-dd7e973617da464d`: Q1a §5.1 closure-prerequisite + Q1b §5.2 normalized roll-up + Q1c §5.1 S1999 phrase precedent + Q2b §8.2 T1 #2 HAI wiring parallel-framing tighten + Q3a MC-4 wording generalized-not-removed + Q3c §10.4 MC-3 vs §20 non-conflation + Q4a Fleet Events sidecar §10.1.5 + Q4b §7 batch-discipline attestation + Q4c CLAUDE.md Detailed Breakdown only. Cycle 2 NOT required.

**D48 42nd arm turn 1 CLEAN → 40-consecutive-fully-clean-arms sub-pattern EXTENDED to 41-consecutive** (MC-2 CODIFICATION-CONFIRMED milestone extended 40 → 41 at S2099 close per single-batch 4-question SIGN criterion).

**Chris "AGREE ALL + (f)=RAG" ratification 2026-07-04** on 6-item close card: (a) §5.1 canonical seam-posture statement + (b) §7 anchor-update batch as single atomic follow-up PR + (c) 26 T-slot queue T1 ordering per Q10 SIGN STRENGTHEN + (d) MC-3 + MC-4 (guardrails retained but generalized) + MC-6 CODIFICATION-CONFIRMED milestone promotions + (e) arc pin retirement + (f) next-arc queue lean = RAG Document Loading D-override selection.

## Session-open protocol (universal — see Research OS §4)

1. `context-kit orient` — source-of-truth chain + latest handoff.
2. Absorb this `CLAUDE.md` + `MEMORY.md` (both auto-injected).
3. Read this `00-START-NEXT-SESSION.md` in full.
4. Read Research OS §0–§5 (skim §6–§9 headings).
5. Record repo state (branch + SHA + `git status`).
6. Note request context (change vs explain; explicit constraints; for bugs: repro path).
7. Classify the request via OS §5 router → load the matching §8 startup contract.
8. If PA calls will happen: **mint fresh isolation pin via `session_tool.create_fresh` FIRST** (arc pin `pa-dd7e973617da464d` is RETIRED) + rotate `tools/pa_local.sh:215` to new pin + verify `service_context: local` via `platform_config_tool overview`.
9. If S2100 RAG Document Loading arc-open: apply playbook §11.1 9-section parent-scoping template + Research OS §11.1 EIGHTH application discipline.

## Post-S2099-commit docs cascade (owed after S2099 close PR merges)

Per `feedback_docs_cascade_at_every_close.md` + `feedback_cascade_pr_must_include_embed_step.md` — MUST run all 4 steps after commit merges:

1. `python manage.py build_docs_index`
2. `python manage.py build_rag_corpus`
3. `python manage.py sync_docs_index_to_documents`
4. `python manage.py embed_documents --all-unembedded` (state chunk count in PR body as evidence)

Then `python manage.py build_docs_provenance` per §11.4 provenance discipline.

## §7 anchor-update batch — queued as single atomic follow-up PR

Per S2099 §7 batch-discipline attestation (Q4b SIGN fold) — scope:

- 10 per-plane topic docs `docs/topics/{memory,sports,content,observability,hai,authority,employee-os,frontend,api,discord}-event-integration.md`.
- 1 index/overview doc `docs/topics/event-integration-architecture.md`.
- PLATFORM_INVENTORY.md new subsection under `## Event / Integration Architecture` (net-new; append after `## URL Routes`).
- PLATFORM_WHAT_IT_IS.md §7 Current State Honesty Group 2000+ subsection.
- EVENT_SYSTEM_INVENTORY.md §13 new subsection with §13.1 six intra-application substrates + NEW §13.1.5 Fleet Events sidecar subtable (per Q4a fold).
- CLAUDE.md Detailed Breakdown row for Event/Integration seam maturity (per Q4c fold — NOT Live Counts autoblock) + Subsystem Documentation row for new index doc.

**Owner:** Group 2000+ residual (Claude next session or dedicated batch session). Not blocking for S2100 RAG Document Loading arc-open.
