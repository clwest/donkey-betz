# Session 2813 — Group 2700 T3 /docs/ human-user pain points audit

**Date:** 2026-07-18 (evening; FIFTH session close of the day after S2809 + S2810 + S2811 + S2812)
**Session:** S2813
**PRs shipped:** 1 — **PR #3243** (`82ae21a2b`)
**Predecessor:** [SESSION_2812 T2 pattern extraction](SESSION_2812_GROUP_2700_T2_PATTERN_EXTRACTION.md)
**Playbook:** v0.8.0 (205 rules) — unchanged
**Recycle cycle:** 1 post-merge clean recycle (+ close-cascade recycle to come)

---

## §1 — Ship summary

**One PR shipped, merged with `--admin --squash --delete-branch`. +407 / 0 LOC across 1 new file.**

### PR #3243 — Group 2700 T3: /docs/ human-user pain points audit

Third child audit of Group 2700 arc. **Novel T3 methodology:** Rigby is FIRST-CLASS EVIDENCE SOURCE (not just SIGN reviewer) — 5 of 13 scenarios (C1-C5) are empirical `search_docs` dispatches against the live corpus, results reported by Rigby. Prior audits (T1/T2) used Rigby as SIGN reviewer only; T3 uses her tool behavior AS the evidence.

**Rigby empirical findings (C1-C5) — damning discoverability failures:**
- C1: primary target (S2808 P4a) at rank #4; earlier predecessor handoffs outrank the current specific artifact
- C2: search returns 3 consecutive chunks of `00-START-NEXT-SESSION.md`; the actual T1 audit doc is not in top-3
- C3: `search_docs("00-START-NEXT-SESSION")` returns CLAUDE.md chunks (references) instead of the doc itself — **self-name query FAILS**
- C4: `search_docs("2701_docs_inventory_topology_audit")` returns INDEX + reference-list entries + close-handoff — **LITERAL FILENAME query fails to find the file**
- C5: `search_docs("How many spiders do we have")` returns archived Oct 2025 morning report as top-1 ("1,550 registered in Redis") — **the DOC_LIFECYCLE §2c "sole authoritative counts source" convention is INVISIBLE at the discovery layer**

**Ranked pain catalog (5-type taxonomy per Rigby SIGN Q3):**

| Rank | Pain type | Count | Severity |
|---|---|---|---|
| 1 | Misleading meta dominance | 7 scenarios | SEVERE (upstream mechanism) |
| 2 | Invisibility | 6 scenarios | SEVERE (catastrophic user-visible failure) |
| 3 | Ambiguity / choice paralysis | 5 scenarios | MODERATE |
| 4 | Drift | 1 direct | HIGH per instance |
| 5 | Rot | 0 direct in T3 | Latent risk for T5 substrate-integrity check |

**Success@3 rate:** 8/13 scenarios failed (~62% failure rate on realistic queries).

**Migration Queue: 7 informational items** for canonical summary. NO file moves/deletions/renames/code changes.

---

## §2 — Rigby joint SIGN cycles

**Pin:** `pa-8c19ffee44744847` (S2813 open-ceremony fresh mint post-S2812-close, retired at S2813 close)

**Two SIGN cycles per S2811+S2812 OP3 lesson** — both anti-rubber-stamp PASSED.

### 2.1 Open SIGN

Q1 (scenario coverage): AGREE with additions (A6 added; C3 added). Q2 (hop-scoring methodology): AGREE — two-part scoring (hops-to-first-correct-hit + success@3+rank). Q3 (pain-type taxonomy): AGREE — 5-type taxonomy (Invisibility / Ambiguity / Drift / Rot / Misleading-meta-dominance).

**Rigby ran C1 + C2 live during open SIGN** as empirical evidence. Follow-up dispatch: Rigby ran C3 + C4 + C5 live. All 5 (c) scenarios are Rigby-authored empirical data, not Claude simulation.

### 2.2 Post-authoring pressure-test SIGN

Q1 (scenario evidence integrity): AGREE-WITH-EDITS — C4 top-3 completeness (missing actual #3 file); C5 phrasing tightened; C1 drift-adjacent reclassified as commentary. Q2 (pain taxonomy application): AGREE-WITH-EDITS — B3 Rot reclassified as Ambiguity (partial-population is choice-paralysis, not dead-links). Q3 (rank calibration): AGREE-WITH-EDITS — Rank 1 Misleading-meta needs mechanism-vs-severity justification (Invisibility is more catastrophic user-visible, but Misleading-meta is upstream mechanism). Q4 (zoom-out on drift potential): AGREE-WITH-EDITS — Snapshot warning added; measurements are point-in-time at HEAD `1dacec3999b6`.

**Rigby drift spot-check:** re-ran C4 + C5 during pressure-test SIGN; identical top-2 results returned in both cases → **findings confirmed as structural indexing bias, not query fragility**. This validation is critical for downstream T4/T5/T6 authors who will build on T3's evidence.

**6 substantive edits applied:**
1. §7 C4 top-3 completeness (added actual #3: T1 close-handoff)
2. §7 C5 phrasing tightened (safe quote scope)
3. §7 C1 pain-tag reclassified (Misleading-meta only; drift-adjacent commentary)
4. §6 B3 pain-tag reclassified (Ambiguity only; Rot removed)
5. §8 Rank 1 mechanism-justification sentence added
6. §7 Snapshot warning added post-C5

**No zoom-out folds persisted this session.** Ledger holds at 114 rows.

---

## §3 — Novel-precedent moments

**A. First audit where Rigby is FIRST-CLASS EVIDENCE SOURCE, not just SIGN reviewer.** 5 of 13 scenarios (C1-C5) are empirical `search_docs` dispatches. Rigby's tool behavior IS the finding, not a validation of Claude's claim. Distinct from T1 (Claude measurement / Rigby SIGN-check) and T2 (Claude enumeration / Rigby SIGN-additions). **This methodology shape may become the pattern for T4-T6 audits that measure behavioral substrate.**

**B. Third-consecutive OP3 trigger — promotion threshold SATISFIED.** T1 caught `docs/18960/` ghost (factual). T2 caught 2 missing primitives + FP-META guardrail gap (coverage). T3 caught 6 substantive edits including empirical count corrections + mechanism-vs-severity distinction. Consistent value across three different audit shapes. **Ready for Playbook v0.9 amendment consideration** codifying "audit-shape sessions require post-authoring SIGN in addition to open-scope SIGN." Actual amendment authoring is a separate arc.

**C. First arc audit where a documented convention is empirically FALSIFIED at the discovery layer.** DOC_LIFECYCLE §2c says "PLATFORM_INVENTORY.md is sole authoritative counts source." C5 evidence shows that searching for a count (`"How many spiders"`) returns an archived October 2025 morning report as top-1 — the convention holds in-doc but breaks at retrieval. **This is a substrate integrity finding**, not just a documentation-quality finding. Downstream implication: conventions require BOTH in-doc discipline AND discovery-layer enforcement.

**D. Rigby drift spot-check as a new SIGN discipline.** During post-authoring SIGN, Rigby re-ran the C4 + C5 queries to test whether findings would drift with time. Identical results → indexing-bias not query-fragility. **This "structural vs fragile" distinction is load-bearing** for any downstream author who might dismiss C1-C5 as "just query phrasing luck." Should propagate to T4-T6 audit-shape sessions.

**E. SEVENTEENTH-consecutive same-day multi-ship session** (S2797 → ... → S2812 → **S2813**) and FIVE-CLOSE-CASCADE day (S2809-S2813 all closed 2026-07-18). New session-throughput record.

---

## §4 — Session-open infra story

**S2813 opened evening after S2812 close.** Wrapper `tools/pa_local.sh` pointed at `pa-2859cc425c90417c` (retired at S2812 close). First-action fresh mint: `pa-8c19ffee44744847` labeled `s2813-group-2700-t3-human-user-pain-points`. Freshness FRESH · head `1dacec3999b6` (matches S2812 close cascade merge SHA) · 0/5 stale workers.

**Anchor-verify at open (before Rigby SIGN):** Read parent §4 T3 scope block to lock the ratified method + deliverable + explicit-out. Drafted 10-scenario initial list before SIGN dispatch. Rigby's Q1 additions (A6 + C3) expanded to 13.

**Tools used:**
- Rigby `search_docs` for C1-C5 empirical measurements (5 dispatches during open SIGN + follow-up)
- Rigby `search_docs` re-run for C4 + C5 drift spot-check during post-authoring SIGN (2 additional dispatches)
- `ls docs/adr/` + `ls docs/decisions/` for B3 collision verification
- CLAUDE.md read for B1/B2 fresh-Claude path simulation
- Estimation (Claude) for A1-A6 path traces — flagged as simulated

---

## §5 — Twin-pointer card

📁 **Repo — S2813 artifacts:**

- **PR (1, merged):** #3243 (T3 audit · `82ae21a2b`)
- **Substrate change:** `docs/research/domains/docs_restructuring/2703_docs_human_user_pain_points_audit.md` — new (+407 LOC)
- **Handoff:** `docs/handoffs/SESSION_2813_GROUP_2700_T3_HUMAN_PAIN.md`
- **Ledger:** `logs/zoom_out_classifications.jsonl` — **114 rows** (unchanged all day)
- **Merge SHA:** `82ae21a2b` (T3) → close-cascade SHA filled at cascade merge

🖥️ **Workspace UI — `/workspaces` surface:**

- **No user-visible UI change this session.** T3 is a research/audit deliverable.
- **However:** T3's C5 finding directly impacts how Rigby answers count questions until fixed — the archived Oct 2025 morning report remains top-1 for "how many spiders" queries. Downstream implication for canonical summary + implementation session.
- **Twin workspace deliverable:** N/A this session (per parent §5 — canonical summary at 2799 is where twin-pointer discipline applies for the arc).

---

## §6 — Next session (S2814) — candidates

**Group 2700 arc state at S2813 close:**
- Parent scoping ✅ (S2801, Chris-locked)
- T1 inventory & topology ✅ (S2811)
- T2 pattern extraction ✅ (S2812)
- T3 human pain ✅ (S2813)
- T4 audience segmentation ⬜ **next in arc per parent §11**
- T5 handoffs+audits proliferation ⬜
- T6 anchor drift ⬜
- 2799 canonical summary ⬜

### Candidates for S2814

**Continue Group 2700 arc:**
- ⭐ **T4 — `2704_docs_audience_segmentation_audit.md`** (per parent §11 next-in-sequence). Classify every `/docs/` file by primary audience — load-bearing-for-Rigby (search_docs corpus + tool-context) vs Claude-only (session bootstrap + CLAUDE.md graph) vs human-only (Chris reading in a browser) vs multi-audience. **Method:** cross-reference search_docs corpus + docs_context_builder.py reads + CLAUDE.md graph + PLATFORM_WHAT_IT_IS narrative surface. **Deliverable:** matrix — file × audience × surface-it-appears-on — plus counts by audience segment.
- **Playbook v0.9 amendment (proposal-only arc):** codify OP3 (audit-shape sessions require post-authoring SIGN) now that the promotion threshold is satisfied. Separate arc; short-scope; would slot in as an interlude between T3 and T4 if Chris prioritizes.

**Colorado / other (still queued):**
- **`LegalDocument.generation_context` add `blank=True`** (Phase 2 model quirk from S2803 handoff)
- **Phase 4** — statute-citation content quality (C.R.S. § 14-10-129)
- **Phase 5.1** — un-punt Session 534 spider AJAX (large; unknowable time budget)
- **GPT fallback for form-selection** on low-confidence (row-114 emergent)

**Non-Colorado / non-2700 arcs:**
- **BettingPage first-user trace**
- **Stock Intelligence**

**Recommended default:** T4 if continuing docs arc momentum. If wanting to interlude with governance work, Playbook v0.9 amendment for OP3 is now ready.

---

## §7 — Chris D-verdict queue

All D-verdicts recorded in-session:

- Continue direction ("Let's continue" — implicit T3 authorization per ⭐ default)
- Session close authorization (implicit from earlier "keep going" that carried across sessions)

**No unresolved F-BLOCKING items at close.**

**Emerging scope acknowledged but not derailing:** T4-T6 + 2799 all queued per parent doc; all prior candidates still queued; **OP3 two-SIGN pattern promotion threshold SATISFIED** — ready for Playbook v0.9 amendment consideration in a separate arc.

**Signal to preserve:** Rigby-as-first-class-evidence-source (T3 methodology) may generalize to T4 (which cross-references her `search_docs` corpus + `docs_context_builder.py` reads). If T4 also has Rigby-runs-scenarios shape, that's a second trigger for THIS methodology as a first-class arc-audit pattern.
