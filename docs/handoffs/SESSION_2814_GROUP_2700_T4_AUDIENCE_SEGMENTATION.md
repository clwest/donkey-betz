# Session 2814 — Group 2700 T4 /docs/ audience segmentation audit

**Date:** 2026-07-18 (evening; SIXTH session close of the day after S2809 + S2810 + S2811 + S2812 + S2813)
**Session:** S2814
**PRs shipped:** 1 — **PR #3245** (`bcc82a1a8`)
**Predecessor:** [SESSION_2813 T3 human pain audit](SESSION_2813_GROUP_2700_T3_HUMAN_PAIN.md)
**Playbook:** v0.8.0 (205 rules) — unchanged
**Recycle cycle:** 1 post-merge clean recycle (+ close-cascade recycle to come)

---

## §1 — Ship summary

**One PR shipped, merged with `--admin --squash --delete-branch`. +366 / 0 LOC across 1 new file.**

### PR #3245 — Group 2700 T4: /docs/ audience segmentation audit

Fourth child audit of Group 2700 arc. Classifies `/docs/` files by primary+secondary audience across **5 discovery surfaces** (surface 5 = runtime-injection, added per Rigby SIGN Q3 zoom-out).

**5 discovery surfaces enumerated:**
- Surface 1: `search_docs` RAG corpus — 3217 docs / all embedded / 65454 chunks (Rigby `kb_tool.stats`)
- Surface 2: `docs_context_builder.py` **CRITICAL_DOCS** — 5 items (unconditional full-content inject)
- Surface 2b: `docs_context_builder.py` **PRIORITY_DOCS** — 10 items (high-priority scoring, not injected; 5 overlap with CRITICAL_DOCS + 5 additional)
- Surface 3: CLAUDE.md pointer graph — 45 unique refs
- Surface 4: PLATFORM_WHAT_IT_IS narrative — ~7 unique refs
- Surface 5: Runtime prompt-pack assembly (bounded to surface 2 for T4; latent paths flagged)

**Primary audience counts (post-Rigby corrections):**
- Rigby primary (structural CRITICAL_DOCS): **5 exactly**
- Rigby high-priority (PRIORITY_DOCS non-overlap): **5 exactly**
- Claude primary (bootstrap graph, non-structural): ~35-40
- Multi primary (all 3 audiences by design): ~5
- **Human primary: ≤1730 UPPER BOUND** (residual bucket, not measured truth per Rigby Q4)

**Key findings:**
- **Discovery-vs-injection asymmetry:** 3 of 5 CRITICAL_DOCS + 2 of 10 PRIORITY_DOCS NOT in CLAUDE.md pointer graph (Rigby tool-verified via 5 targeted greps)
- **Retrieval-eligibility ≠ retrieval-behavior** (T3 §7 C5 evidence)
- **Rot signal:** PLATFORM_WHAT_IT_IS references `docs/current/` NOT in T1 §3.1 subdir inventory — flagged for T6
- Surface 4 mostly redundant with Surface 3 (5 of 7 refs overlap)

**Migration Queue: 7 informational items** for canonical summary. NO file moves/deletions/renames/code changes.

---

## §2 — Rigby joint SIGN cycles

**Pin:** `pa-0d04376abc074bcd` (S2814 open-ceremony fresh mint post-S2813-close, retired at S2814 close)

**Two SIGN cycles per OP3 pattern — FOURTH-CONSECUTIVE OP3 TRIGGER** (over-and-above the 3-trigger Playbook v0.9 promotion threshold met at S2813).

### 2.1 Open SIGN

Q1 (framing): substantive shift — **AGREE-C (Primary+Secondary)** not A (exclusive) or B (pure tags). Q2 (classification rules): **DISAGREE with N-threshold** — need 3-way distinction (structural / eligible / proven-UNKNOWN). Q3 (zoom-out): **AGREE + surface 5 identified** (runtime-injection distinct from "referenced in code"). Anti-rubber-stamp check PASSED — Rigby ran `kb_tool.stats` (3217 docs / 65454 chunks / all embedded) + `repo_tool.read_file`/`search` for CRITICAL_DOCS enumeration.

### 2.2 Post-authoring pressure-test SIGN — MAJOR catch

Q1 (surface enumeration): **DISAGREE — CRITICAL_DOCS has 5 items, NOT 10.** My open-SIGN pass conflated CRITICAL_DOCS (line 362, unconditional inject) with PRIORITY_DOCS (line 176, high-priority scoring only). Rigby tool-verified the distinction.

Q2 (Primary+Secondary calibration): AGREE-WITH-EDITS — counts are over-precise; residual ~1730 Human bucket is UPPER BOUND, not measured truth. Some residual are ops/spec docs whose intent is agent consumption via retrieval-eligibility.

Q3 (§6.3 asymmetry finding): AGREE — real finding, not grep miss. Rigby ran 5 targeted greps on CLAUDE.md; all returned 0 matches for SYSTEM_OWNER / CURRENT_MISSION / USER_FEEDBACK_QUEUE / docs/CAPABILITIES.md / DATABASE_MODEL_REFERENCE. Asymmetry confirmed: 3 CRITICAL_DOCS + 2 additional PRIORITY_DOCS missing from bootstrap graph.

Q4 (false-precision risk): AGREE — canonical summary authors would overfit to point counts. Relabel as estimates with confidence bands; separate measurable (surface counts) from residual bucket (not automatically Human-primary).

**6 substantive edits applied:**
1. §3.2b PRIORITY_DOCS split as distinct surface
2. §5.1 / §5.1b split (5 CRITICAL vs 5 additional PRIORITY)
3. §6.1 reframed as ESTIMATES with UPPER BOUND labels + residual bucket concept
4. §6.3 asymmetry corrected (3+2 not 5)
5. §7 Q2/Q5/Q7 count updates + false-precision caveats
6. §10 provenance with 4/4 OP3 trigger note

**No zoom-out folds persisted this session.** Ledger holds at 114 rows.

---

## §3 — Novel-precedent moments

**A. Fourth-consecutive OP3 trigger — SAME failure-mode class as S2811.** The T4 CRITICAL_DOCS/PRIORITY_DOCS conflation is structurally identical to S2811's `docs/18960/` ghost: Claude open-SIGN misread source code, only caught by post-authoring rigor. **Pattern is now empirically ratified across 4 audit shapes** — measurement (T1), primitive extraction (T2), behavioral pain (T3), audience classification (T4). Playbook v0.9 amendment ready; consideration is separate arc.

**B. Second-consecutive audit where Rigby is FIRST-CLASS EVIDENCE SOURCE.** T3 established the methodology (Rigby runs `search_docs` scenarios); T4 extended to `kb_tool.stats` for corpus enumeration + targeted greps for asymmetry verification. Two triggers for this methodology — closer to formalization. If T5 also uses Rigby-runs-tool shape (citation-graph analysis?), that's the third trigger.

**C. First arc audit where UPPER BOUND labels are load-bearing.** Rigby's Q4 caught that "1730 Human-primary" would be read as measured truth by canonical-summary authors. Adding explicit precision qualifiers (exact / approximate / upper-bound) prevents false-precision cascade into downstream work. May generalize as a T-audit convention.

**D. First anchor-verify catch that conflated two SIMILAR but DIFFERENT data structures in the same source file** — CRITICAL_DOCS at line 362 vs PRIORITY_DOCS at line 176 in `docs_context_builder.py`. Both are hardcoded doc lists but serve different mechanisms (unconditional inject vs retrieval-ranking-boost). Substrate lesson: when the source has multiple similarly-named lists, enumerate each explicitly rather than treating them as one concept.

**E. EIGHTEENTH-consecutive same-day multi-ship session** (S2797 → ... → S2813 → **S2814**) and SIX-CLOSE-CASCADE day (S2809-S2814 all closed 2026-07-18).

---

## §4 — Session-open infra story

**S2814 opened evening after S2813 close.** Wrapper `tools/pa_local.sh` pointed at `pa-8c19ffee44744847` (retired at S2813 close). First-action fresh mint: `pa-0d04376abc074bcd` labeled `s2814-group-2700-t4-audience-segmentation`. Freshness FRESH · head `a839e2ffb4db` (matches S2813 close cascade merge SHA) · 0/5 stale workers.

**Anchor-verify at open (before Rigby SIGN):** Read parent §4 T4 scope block; grepped CLAUDE.md for `docs/` refs (45 unique); grepped PLATFORM_WHAT_IT_IS for `docs/` refs (~7 unique); read `docs_context_builder.py` for CRITICAL_DOCS + auto-inject candidates. Rigby's Q1 post-authoring correction caught that I read PRIORITY_DOCS as auto-inject candidates rather than as a distinct list.

**Tools used:**
- Rigby `kb_tool.stats` for surface (1) corpus enumeration
- Rigby `repo_tool.search`/`read_file` for surface (2) CRITICAL_DOCS + PRIORITY_DOCS distinction
- Rigby 5 targeted greps on CLAUDE.md for asymmetry verification (post-authoring SIGN)
- Claude `grep -oE "docs/[a-zA-Z0-9_/-]*\.md|docs/[a-zA-Z0-9_-]+/"` on CLAUDE.md (45 refs) + PLATFORM_WHAT_IT_IS.md (~7 refs) for surfaces 3+4

---

## §5 — Twin-pointer card

📁 **Repo — S2814 artifacts:**

- **PR (1, merged):** #3245 (T4 audit · `bcc82a1a8`)
- **Substrate change:** `docs/research/domains/docs_restructuring/2704_docs_audience_segmentation_audit.md` — new (+366 LOC)
- **Handoff:** `docs/handoffs/SESSION_2814_GROUP_2700_T4_AUDIENCE_SEGMENTATION.md`
- **Ledger:** `logs/zoom_out_classifications.jsonl` — **114 rows** (unchanged all day)
- **Merge SHA:** `bcc82a1a8` (T4) → close-cascade SHA filled at cascade merge

🖥️ **Workspace UI — `/workspaces` surface:**

- **No user-visible UI change this session.** T4 is a research/audit deliverable.
- **However:** T4 §6.3 discovery-vs-injection asymmetry finding has substrate implications — future canonical summary decides whether to add missing 5 docs to CLAUDE.md or reduce CRITICAL_DOCS scope.

---

## §6 — Next session (S2815) — candidates

**Group 2700 arc state at S2814 close:**
- Parent scoping ✅ (S2801, Chris-locked)
- T1 inventory & topology ✅ (S2811)
- T2 pattern extraction ✅ (S2812)
- T3 human pain ✅ (S2813)
- T4 audience segmentation ✅ (S2814)
- T5 handoffs+audits proliferation ⬜ **next in arc per parent §11**
- T6 anchor drift ⬜
- 2799 canonical summary ⬜

### Candidates for S2815

**Continue Group 2700 arc:**
- ⭐ **T5 — `2705_docs_handoffs_audits_proliferation_audit.md`** (per parent §11). 1035 handoffs + 138 audit files + citation-graph analysis + substrate-integrity spot-check (per parent §4 T5). This is a BIG scope — Rigby likely runs citation-integrity checks. If T5 uses Rigby-runs-tool shape, third trigger for that methodology.
- **Playbook v0.9 amendment (proposal-only interlude arc):** Codify OP3 (audit-shape sessions require post-authoring SIGN). 4/4 triggers now support it. Separate short-scope arc.

**Colorado / other (still queued):**
- **`LegalDocument.generation_context` add `blank=True`** (Phase 2 model quirk from S2803 handoff)
- **Phase 4** — statute-citation content quality (C.R.S. § 14-10-129)
- **Phase 5.1** — un-punt Session 534 spider AJAX
- **GPT fallback for form-selection** (row-114 emergent)

**Non-Colorado / non-2700 arcs:**
- **BettingPage first-user trace**
- **Stock Intelligence**

**Recommended default:** T5 if continuing docs arc — momentum solid + T5-T6 are the largest remaining scopes (T5 covers ~1173 files across handoffs+audits).

---

## §7 — Chris D-verdict queue

All D-verdicts recorded in-session:

- Continue direction ("Let's do T4")
- Session close authorization (implicit continuation)

**No unresolved F-BLOCKING items at close.**

**Emerging scope acknowledged but not derailing:** T5-T6 + 2799 all queued per parent doc; all prior candidates still queued; **OP3 pattern 4/4 triggers** — ready for Playbook v0.9 amendment consideration in separate arc when Chris chooses.

**Signal to preserve:** Rigby-as-first-class-evidence-source (T3+T4 shape) at 2 triggers. Also — same failure-mode class as S2811 (`docs/18960/`) recurred at T4 (CRITICAL_DOCS vs PRIORITY_DOCS conflation): open-SIGN misread structurally similar data, caught by post-authoring rigor. Post-authoring SIGN discipline empirically load-bearing across all audit shapes.
