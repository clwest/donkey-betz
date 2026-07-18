---
title: "S2813 /docs/ Human-User Pain Points Audit (T3 of Group 2700 arc)"
status: active (audit deliverable — scenario evidence + ranked pain catalog)
authority: T3 child audit of Group 2700 parent arc
session: 2813
date: 2026-07-18
domain_slug: docs_restructuring
research_group: 2700
thread: T3
authors: Claude Code (Chris directed at S2813 open); Rigby (ran C1-C5 search_docs scenarios as first-class evidence source)
supersedes: none
related:
  - docs/research/domains/docs_restructuring/2700_docs_restructuring_domain_scoping.md    # parent (Chris-locked 2026-07-16)
  - docs/research/domains/docs_restructuring/2701_docs_inventory_topology_audit.md        # T1 predecessor (S2811)
  - docs/research/domains/docs_restructuring/2702_docs_research_pattern_extraction_audit.md # T2 predecessor (S2812)
  - docs/00-START-HERE/DOC_LIFECYCLE.md                                                    # §2c sole-counts-source convention that C5 falsifies at discovery layer
  - docs/PLATFORM_INVENTORY.md                                                             # runtime counts anchor (invisible in C5 evidence)
  - docs/INDEX.md                                                                          # docs corpus index (surfaces as pointer, not target — C4 evidence)
scope: T3 = concrete-scenario evidence + ranked pain catalog per parent §4 — hops-to-target + success@3 + pain-type tagging across three audiences (Chris / fresh-Claude / Rigby)
non_goals:
  - audience segmentation (that's T4)
  - restructuring proposal (canonical summary at 2799)
  - file moves, deletions, renames, code changes (arc non-goals per parent §5)
  - fixing search / RAG behavior (that's downstream implementation)
  - proposing new pain types beyond the S2813 SIGN-ratified 5-type taxonomy
delegates_to: T4 (audience segmentation); T5 (handoffs+audits proliferation); T6 (anchor drift); canonical summary 2799 (synthesis + restructuring proposal)
owner: claude+rigby
---

# Session 2813 — /docs/ Human-User Pain Points Audit (Group 2700, Thread 3)

> **What this doc is.** T3 evidence — 13 concrete scenarios across three audiences (Chris / fresh-Claude / Rigby), each measured for hops-to-target + success@3 + pain-type tags. Rigby's 5 `search_docs` runs (C1-C5) provide the strongest evidence: real tool behavior against the current corpus, not simulation.
>
> **What this doc is not.** A proposal to fix any pain. A ranking of docs by importance. A restructuring plan. Those belong to T5/T6/canonical summary per parent §4.

---

## 1. Why T3 third

Per parent doc §4:

> T3 — Human-user pain points. Scope: where discoverability breaks for Chris (single human user in single-user pre-prod per `project_single_user_pre_prod_operating_context`) and for fresh-Claude sessions. Chris/Claude/Rigby workflow friction. Method: trace concrete user journeys; measure how many hops until they land on the right doc. Deliverable: ranked pain catalog + concrete-scenario evidence.

T3 follows T1 (what's IN `/docs/` — 3201 files, 99 loose at root) and T2 (what makes `/docs/research/` work — 31 primitives with per-primitive transferability challenge). T3 shifts from **substrate analysis** to **behavioral measurement**: given real user intent, does the current substrate actually deliver the target doc?

**Key T3 innovation vs T1/T2:** Rigby is a **first-class evidence source**, not just a SIGN reviewer. For audience (c) scenarios she runs `search_docs` herself and reports rank + top-3 files. T1/T2 measurements were static (grep/find/wc); T3 (c) measurements are behavioral (real RAG queries against the live corpus).

**Discipline for reading T3:** the (c) evidence is empirical; the (a) and (b) evidence is simulated based on reasonable-user-behavior estimates. The strongest findings come from (c). Don't over-weight the (a)/(b) hop counts.

---

## 2. Anchors T3 cites (never restates)

| Source | What it authoritatively holds | This doc's usage |
|---|---|---|
| Parent doc §4 T3 scope | Method + deliverable + explicit-out | T3 respects |
| [`docs/00-START-HERE/DOC_LIFECYCLE.md`](../../../00-START-HERE/DOC_LIFECYCLE.md) §2c | "PLATFORM_INVENTORY.md is sole authoritative counts source" convention | **T3 evidence C5 falsifies this at the discovery layer** — the convention holds in-doc but breaks when a user searches for a count |
| [`docs/PLATFORM_INVENTORY.md`](../../../PLATFORM_INVENTORY.md) | Runtime counts | Cited as the target that C5 fails to reach |
| [`docs/INDEX.md`](../../../INDEX.md) | Docs corpus index (auto-gen) | Cited as the pointer that C4 surfaces INSTEAD OF the target file |
| [`docs/CLAUDE.md`](../../../CLAUDE.md) | Repo bootstrap graph | Cited as the first-hop for fresh-Claude scenarios (b) |

---

## 3. Scenario inventory (13 across 3 audiences)

**Audience (a) — Chris asks "where do I see X?" (6 scenarios):**

| ID | Scenario | Intended target |
|---|---|---|
| A1 | "Where is the current mission?" | `docs/missions/CURRENT_MISSION.md` |
| A2 | "How many spiders do we have?" | `docs/PLATFORM_INVENTORY.md` |
| A3 | "What did we ship in the last session?" | `docs/handoffs/SESSION_2812_*.md` (most recent handoff) |
| A4 | "What did we decide about attorney sub-forms?" | `docs/handoffs/SESSION_2810_ATTORNEY_SUBFORM_WIZARD.md` |
| A5 | "Which audit dirs are duplicated?" | `docs/research/domains/docs_restructuring/2701_docs_inventory_topology_audit.md` §7.1 |
| A6 | "Where is the docs index / map?" | `docs/INDEX.md` OR `docs/00-START-NEXT-SESSION.md` (per Rigby SIGN Q1 addition) |

**Audience (b) — fresh Claude asked to fix Y (3 scenarios):**

| ID | Scenario | Probable target (candidates) |
|---|---|---|
| B1 | "Add a new spider to the network" | `docs/topics/spider-network.md` (primary) OR `docs/SPIDERS.md` OR `docs/architecture/` |
| B2 | "Understand the PA tool schema pattern before adding a new tool" | `docs/topics/personal-assistant.md` (primary) OR `docs/PA_TOOL_AUDIT.md` OR `docs/PERSONAL_ASSISTANT_ARCHITECTURE.md` |
| B3 | "Where should I put a new ADR?" | `docs/adr/` (4 files) OR `docs/decisions/` (2 files) — convention collision |

**Audience (c) — Rigby asked to search for Z (5 scenarios, ALL RUN LIVE):**

| ID | Query | Intended target |
|---|---|---|
| C1 | `search_docs("Colorado JDF form-selection intelligence")` | `docs/handoffs/SESSION_2808_COLORADO_FAMILY_LAW_PHASE4A_FORM_SELECTION.md` |
| C2 | `search_docs("Group 2700 docs restructuring T1 audit")` | `2701_docs_inventory_topology_audit.md` + `2700_docs_restructuring_domain_scoping.md` |
| C3 | `search_docs("00-START-NEXT-SESSION")` | `docs/00-START-NEXT-SESSION.md` (self-reference test) |
| C4 | `search_docs("2701_docs_inventory_topology_audit")` | `2701_docs_inventory_topology_audit.md` (literal filename query) |
| C5 | `search_docs("How many spiders do we have")` | `docs/PLATFORM_INVENTORY.md` |

---

## 4. Hop-scoring methodology + pain-type taxonomy

**Hop-scoring (per Rigby SIGN Q2 AGREE):**

- **Primary metric:** hops-to-first-correct-hit. One hop = one navigation action (open a file, tab to another window, run a `search_docs` call, re-read `context-kit orient` output).
- **Secondary metric:** success@3 + best-rank observed.
- (a)/(b) scenarios: hops = simulated "how many files a reasonable person would open" to land on target.
- (c) scenarios: hops = number of `search_docs` dispatches needed + whether target appears in top-3.

**Pain-type taxonomy (per Rigby SIGN Q3 AGREE):**

- **Invisibility** — user didn't know the doc exists (search/query mismatch, naming mismatch, doc unregistered in visibility mechanics per T2 OP4)
- **Ambiguity / choice paralysis** — multiple plausible docs exist; no canonical pointer disambiguates
- **Drift** — doc found, but content is outdated/wrong vs current reality
- **Rot** — doc references missing paths / dead links / renamed concepts
- **Misleading meta dominance** — search returns "orientation" / "recap" / "handoff" docs instead of the primary artifact the user sought

Each scenario outcome gets tagged with one or more pain types.

---

## 5. Audience (a) — Chris asks "where do I see X?" (simulated)

**Method note:** (a) scenarios are simulated based on reasonable-Chris-behavior. Chris's actual navigation habits vary; hops shown are conservative estimates for a Chris who does NOT already have the target file's path memorized.

### A1 — "Where is the current mission?"

- **Path traced:** Chris opens `docs/` in file explorer → 48 subdirs visible → scans for "mission" → sees `docs/missions/` → opens → sees `CURRENT_MISSION.md` alone → hop 3.
- **Alternative (worst case):** Chris tries `docs/00-START-NEXT-SESSION.md` first (habit) → doesn't find current mission → back to `docs/` → then `missions/` → hop 4-5.
- **Hops (primary):** **3-5**
- **Success@3:** **Y** (target reachable in ≤3 hops for the direct path)
- **Pain tags:** none significant (target is named clearly; subdir name matches intent)

### A2 — "How many spiders do we have?"

- **Path traced:** Chris knows to look at `docs/PLATFORM_INVENTORY.md` (habit) → hop 1. **DONE for habit-Chris.**
- **Alternative (forgetful-Chris or fresh-Chris):** Chris searches "spiders" via file browser → 99 loose files, 48 subdirs, no clear hit → tries `docs/SPIDERS.md` → sees narrative not counts → wonders where counts are → hop 4+
- **Rigby-mediated (see C5):** if Chris asks Rigby "how many spiders" → Rigby returns archived Oct 2025 morning report showing "1,550 registered in Redis" — **wrong answer surfaced as authoritative**. Pain compounds.
- **Hops (primary):** **1 (habit-Chris) / 4+ (fresh-Chris)**
- **Success@3:** **Y for habit-Chris / N for fresh-Chris**
- **Pain tags:** **Invisibility** (fresh-Chris doesn't find the sole-counts-source convention); **Drift/Misleading-meta-dominance** propagates via Rigby (C5).

### A3 — "What did we ship in the last session?"

- **Path traced:** Chris opens `docs/handoffs/` → 1035 files → sorts by modification date OR by session number → clicks most recent → hop 3.
- **Alternative:** Chris opens `docs/00-START-NEXT-SESSION.md` → sees "Refreshed 2026-07-18 late-afternoon (SESSION 2812 CLOSED...)" — has the answer without opening a handoff → hop 1.
- **Hops (primary):** **1-3**
- **Success@3:** **Y**
- **Pain tags:** none significant. `00-START-NEXT-SESSION.md` acts as effective recap.

### A4 — "What did we decide about attorney sub-forms?"

- **Path traced:** Chris types "attorney" in file browser filter → matches include `docs/audits/`, historical handoffs, memory files — no obvious pointer to S2810 → Chris navigates by memory ("that was Saturday afternoon") → opens `docs/handoffs/SESSION_2810_ATTORNEY_SUBFORM_WIZARD.md` → hop 3-4.
- **Alternative:** Chris asks Rigby → Rigby searches "attorney sub-form wizard" → probably surfaces S2810 handoff + related memory (not tested in T3).
- **Hops (primary):** **3-4**
- **Success@3:** **Y (if Chris remembers the session number OR uses Rigby)**
- **Pain tags:** **Ambiguity** (many docs mention "attorney"; canonical pointer only exists in handoffs/ + memory).

### A5 — "Which audit dirs are duplicated?"

- **Path traced:** Chris would have to remember T1 (`2701_docs_inventory_topology_audit.md`) was authored recently AND that §7.1 covers this. Absent that memory, Chris could grep `docs/` for "audit" → 138 files across `audit/` + `audit-2026/` + `audits/` + 20 loose `*AUDIT.md` → get confused → give up or ask Rigby.
- **Rigby-mediated:** search_docs("duplicated audit dirs") likely surfaces T1 audit doc. Not tested in T3.
- **Hops (primary):** **5+ or fail (without memory of T1)**
- **Success@3:** **N (Chris) / probably Y (Rigby)**
- **Pain tags:** **Invisibility** (finding the answer requires knowing T1 exists); **Misleading-meta-dominance** (searching "audit" surfaces 138 files, none of which are the meta-answer).

### A6 — "Where is the docs index / map?"

- **Path traced:** Chris has 4 plausible candidates:
  - `docs/INDEX.md` (auto-gen list of all 3201 docs — overwhelming)
  - `docs/00-START-NEXT-SESSION.md` (current session state — not a map)
  - `docs/research/ARCHITECTURE_INDEX.md` (research-scoped, not `/docs/`-scoped)
  - `docs/CLAUDE.md` (repo bootstrap — includes some pointers)
- Chris likely opens 2-3 before finding what he wanted → hop 2-4.
- **Hops (primary):** **2-4**
- **Success@3:** **Y (probably; depends on what "docs map" means to Chris)**
- **Pain tags:** **Ambiguity / choice paralysis** (4 candidate docs, no canonical "start here for docs" pointer beyond `00-START-NEXT-SESSION`).

---

## 6. Audience (b) — Fresh Claude asked to fix Y (simulated)

**Method note:** (b) scenarios simulate fresh-Claude starting a session, reading `CLAUDE.md`, then trying to find the doc that would help. Actual Claude behavior varies; hops shown are the median-path for a Claude following the documented bootstrap sequence.

### B1 — "Add a new spider to the network"

- **Path traced:** Fresh Claude reads `CLAUDE.md` → sees `docs/topics/spider-network.md` in the Subsystem Documentation table → opens → gets the pattern. Hop 2.
- **Alternative (Claude doesn't check CLAUDE.md first):** search "add spider" → hits `docs/SPIDERS.md` + `docs/topics/spider-network.md` + `docs/architecture/` — 3 candidates → hop 3-4.
- **Hops (primary):** **2-4**
- **Success@3:** **Y**
- **Pain tags:** **Ambiguity** (`SPIDERS.md` at root vs `topics/spider-network.md` vs `architecture/spiders_*` — no canonical routing).

### B2 — "Understand the PA tool schema pattern before adding a new tool"

- **Path traced:** Fresh Claude reads `CLAUDE.md` → sees `docs/topics/personal-assistant.md` reference AND `PA_TOOL_AUDIT.md` mention AND `PERSONAL_ASSISTANT_ARCHITECTURE.md` in the file table → THREE candidate docs → opens all three sequentially trying to find "schema pattern" → hop 4-5.
- **Pain compound:** each doc has partial info; canonical schema definition lives in `core/services/pa_tool_schemas.py` code, not docs — Claude eventually reads code. Hop 5-6.
- **Hops (primary):** **4-6**
- **Success@3:** **Ambiguous — Claude finds "a doc" in top-3 but no canonical one**
- **Pain tags:** **Ambiguity / choice paralysis** (3 candidate docs at same abstraction level); **Invisibility** (canonical schema definition isn't in any doc — it's in code).

### B3 — "Where should I put a new ADR?"

- **Path traced:** Fresh Claude reads `CLAUDE.md` → sees no explicit ADR-location guidance → checks `docs/` → sees BOTH `docs/adr/` (4 files) AND `docs/decisions/` (2 files) → convention collision → checks `README.md` in each? Neither has one → picks one (probably `adr/` because it's more filled) → hop 4-5 with genuine uncertainty.
- **Alternative:** Fresh Claude checks recent handoffs for ADR context → finds `SESSION_2701_...` mentioning `docs/decisions/ADR-*.md` pattern → but that's from a different arc thread → hop 6+.
- **Hops (primary):** **4-6**
- **Success@3:** **N (Claude chooses without confidence)**
- **Pain tags:** **Ambiguity / choice paralysis** (real convention collision — `adr/` vs `decisions/` with different naming schemes and no README explaining which is canonical). *Per Rigby SIGN Q2:* the "partially populated" observation is a subcase of Ambiguity (multiple plausible homes), not Rot (Rot = dead links / missing referenced artifacts).

---

## 7. Audience (c) — Rigby asked to search for Z (EMPIRICAL — Rigby ran these live)

**Method note:** These are the strongest T3 evidence — real `search_docs` dispatches against the live corpus, results reported by Rigby. Hop-scoring is dispatch count; success@3 is whether the target file appears in the returned top-3 results.

### C1 — `search_docs("Colorado JDF form-selection intelligence")`

- **Top-3 returned:**
  1. `docs/handoffs/SESSION_2804_COLORADO_FAMILY_LAW_PHASE3_1_AGENT_RELIABILITY.md`
  2. `docs/handoffs/SESSION_2805_COLORADO_FAMILY_LAW_PHASE3_1_P1_CASEPROFILE_UNIFICATION.md`
  3. `docs/handoffs/SESSION_2806_COLORADO_FAMILY_LAW_PHASE3_2_CASE_WIZARD.md`
- **Intended target present?** `SESSION_2808_...PHASE4A_FORM_SELECTION.md` at **rank #4** (not in top-3).
- **Hops:** 1 dispatch.
- **Success@3:** **N** (target at rank 4).
- **Pain tags:** **Misleading-meta-dominance** (earlier session handoffs that MENTION the topic outrank the primary specific artifact). *Commentary (not a formal tag):* the same behavior is drift-adjacent — S2804/S2805 were superseded by S2808 but still outrank it — but per Rigby SIGN Q2 this is primarily a ranking issue, not a formal Drift instance for the §8 count.

### C2 — `search_docs("Group 2700 docs restructuring T1 audit")`

- **Top-3 returned:**
  1. `docs/00-START-NEXT-SESSION.md` (chunk 2)
  2. `docs/00-START-NEXT-SESSION.md` (chunk 6)
  3. `docs/00-START-NEXT-SESSION.md` (chunk 10)
- **Intended target present?** `2701_docs_inventory_topology_audit.md` — **NOT in top-3** or in the full returned set. Parent `2700_docs_restructuring_domain_scoping.md` — NOT in top-3 either. `SESSION_2801_DOCS_RESTRUCTURING_ARC_OPEN.md` at rank 5.
- **Hops:** 1 dispatch.
- **Success@3:** **N** (three consecutive chunks of the same orientation doc; actual target files absent).
- **Pain tags:** **Misleading-meta-dominance** (severe — one doc dominates the top-3). **Invisibility** (target files exist but are not surfaced even with a targeted query).

### C3 — `search_docs("00-START-NEXT-SESSION")`

- **Top-3 returned:**
  1. `docs/CLAUDE.md` (chunk 6 — mentions `00-START-NEXT-SESSION.md` in pointer-stability contract)
  2. `docs/CLAUDE.md` (chunk 9 — tactical contract section)
  3. (additional CLAUDE.md chunks per truncated output)
- **Intended target present?** `docs/00-START-NEXT-SESSION.md` itself — **NOT in top-3** (only files that reference it appear).
- **Hops:** 1 dispatch.
- **Success@3:** **N** (self-reference query fails — the doc doesn't rank for its own name).
- **Pain tags:** **Invisibility** (fundamental: even the literal doc name doesn't retrieve the doc). **Misleading-meta-dominance** (references outrank the referent).

### C4 — `search_docs("2701_docs_inventory_topology_audit")`

- **Top-3 returned:**
  1. `docs/00-START-NEXT-SESSION.md` (chunk 10 — Reference documents section)
  2. `docs/INDEX.md` (chunk 12 — auto-gen index entry)
  3. `docs/handoffs/SESSION_2811_GROUP_2700_T1_INVENTORY_AUDIT.md` (T1 close handoff — mentions the target file but is not the target)
- **Intended target present?** `2701_docs_inventory_topology_audit.md` itself — **NOT in top-3**. All three top results are docs that REFERENCE the target rather than the target itself.
- **Hops:** 1 dispatch.
- **Success@3:** **N** (**LITERAL FILENAME query fails to find the file**).
- **Pain tags:** **Invisibility** (catastrophic — the file's own filename doesn't retrieve it). **Misleading-meta-dominance** (INDEX entry + reference-list entry + close-handoff all outrank the target).

### C5 — `search_docs("How many spiders do we have")`

- **Top results:**
  1. `docs/archive/old-structure/status/historical/morning-report-2025-10-02.md` (contains "1,550 registered in Redis" from Oct 2025)
  2. `docs/AUDIT_FINDINGS.md`
  - (Additional results beyond top-2 present in returned set; exact ordering not quoted here to avoid unverified claims per Rigby SIGN Q1 edit.)
- **Intended target present?** `docs/PLATFORM_INVENTORY.md` (sole counts source per DOC_LIFECYCLE §2c) — **NOT in top-2**. Rigby drift spot-check re-ran this query minutes later; identical top-2 results returned — finding is indexing-bias, not query-fragility.
- **Hops:** 1 dispatch.
- **Success@3:** **N**, and worse — a **stale answer surfaces as authoritative** from a doc that lives in `archive/`.
- **Pain tags:** **Drift** (Oct 2025 count "1,550" is wrong for July 2026 reality — 80 spiders per current PLATFORM_INVENTORY). **Misleading-meta-dominance** (archived historical outranks canonical counts source). **The DOC_LIFECYCLE §2c "sole authoritative counts source" convention is INVISIBLE at the discovery layer.**

### C6 (implicit) — Cross-scenario finding: `archive/` is not partitioned from search

Every (c) scenario's search corpus includes `docs/archive/` (1388 files). C5 explicitly returned an `archive/old-structure/status/historical/` doc as top-1. **The archive partitioning that T1 §3.1 notes as "already-partitioned, leave-alone" is a filesystem partition, not a search partition.**

- **Pain tags:** **Drift** (archive is meant to be read-once historical; search treats it as live). **Misleading-meta-dominance** (archived content outranks canonical content).

---

### Snapshot warning (per Rigby SIGN Q4)

C1-C5 measurements are **point-in-time retrieval behaviors** at git HEAD `1dacec3999b6` (S2812 close cascade). Retrieval can drift when:
- new handoffs land in `docs/handoffs/` (00-START-NEXT-SESSION.md changes frequently, affecting its search dominance)
- `build_docs_index` regenerates the corpus
- `build_rag_corpus` re-chunks (chunk boundaries shift; embedding neighborhoods change)
- corpus growth changes embedding-neighborhood density

**Rigby drift spot-check (during post-authoring SIGN):** re-ran C4 and C5 immediately after the initial runs; identical top-2 results returned. This confirms C4 and C5 findings are **structural indexing bias**, not query fragility. However, T4/T5/T6 or canonical-summary authors relying on §7 evidence should re-run C1-C5 after major doc adds or index rebuilds; snapshot may drift.

---

## 8. Ranked pain catalog (aggregated across all 13 scenarios)

Each pain type below carries a **severity** (COUNT of scenarios where it appears + SEVERITY of the individual scenario impact):

### Rank 1 — Misleading meta dominance (7 scenarios; SEVERE)

- **Where surfaced:** C1 (rank 4 for target), C2 (three consecutive chunks of one meta doc), C3 (references outrank referent), C4 (LITERAL FILENAME finds INDEX + close-handoff not file), C5 (archive outranks canonical), A2 (Chris route via Rigby hits archive), A5 (searching "audit" surfaces 138 files, none the meta answer).
- **Severity: SEVERE.** The RAG substrate is actively harmful for counts + specific-artifact queries. Users who type reasonable queries get pointers-to-the-answer or historical-stale-answers instead of the answer itself.
- **Why Rank 1 (per Rigby SIGN Q3 clarification):** Misleading-meta-dominance is the **upstream mechanism** that produces the downstream harms — including Invisibility-by-proxy (C3, C4, C5 targets are technically indexed but hidden under meta) and Drift-by-surfacing-stale-answer (C5 archive returned as authoritative). Ranking this at #1 is a claim about *mechanism*, not user-visible severity. Invisibility (Rank 2) is the more catastrophic user-visible failure — C3 and C4 return zero relevant target results — but the substrate cause is the meta-dominance ranking behavior.
- **Downstream implication for canonical summary:** target-doc retrieval requires either (a) archive-partitioned search corpus, (b) authority weighting in the ranker (`authority: state` docs boost over `authority: session-snapshot`), or (c) both.

### Rank 2 — Invisibility (6 scenarios; SEVERE)

- **Where surfaced:** C2 (target files absent from top-3), C3 (self-name query fails), C4 (literal-filename query fails), A2 fresh-Chris (sole-counts convention invisible), A5 (T1 audit invisible without prior knowledge), B2 (canonical PA schema is in code not docs — no doc-layer canonical).
- **Severity: SEVERE.** Documents that exist and are indexed are still functionally invisible to reasonable queries.
- **Downstream implication:** RAG embedding + retrieval strategy needs tuning; file-name-in-query should heavily boost the file itself.

### Rank 3 — Ambiguity / choice paralysis (5 scenarios; MODERATE)

- **Where surfaced:** A4 (many "attorney" hits), A6 (4 candidate index docs), B1 (3 spider-doc locations), B2 (3 PA-doc locations), B3 (adr/ vs decisions/ collision).
- **Severity: MODERATE.** Each collision costs 2-3 extra hops; not catastrophic but consistent friction.
- **Downstream implication for canonical summary:** each collision needs a canonical pointer (README with "if you want X, read Y") or consolidation.

### Rank 4 — Drift (1 scenario direct; HIGH severity per instance)

- **Where surfaced:** C5 (Oct 2025 spider count returned for July 2026 query). *Per Rigby SIGN Q2, C1's rank-4-for-current-target is reclassified as Misleading-meta-dominance rather than Drift for the formal count.*
- **Severity: HIGH per instance.** When drift-pain fires, the user gets a wrong answer as authoritative — worse than not finding the doc at all. Single scenario direct in T3, but C5 alone is a catastrophic failure of the sole-counts-source convention.
- **Downstream implication:** archive segregation from RAG corpus; `status: superseded` should heavily deprioritize in retrieval.

### Rank 5 — Rot (0 scenarios direct in T3; latent risk in unprobed corpus)

- **Where surfaced:** No T3 scenario tagged Rot after Rigby SIGN Q2 edit (B3's `adr/`+`decisions/` collision reclassified as Ambiguity — parallel-populated is "multiple plausible homes" not "dead links / missing referenced artifacts").
- **Severity: unknown (as measured in T3).** Rot may still be latent in scenarios T3 didn't probe — old handoff cross-refs, moved-doc references, deprecated-command mentions. T5's substrate-integrity spot-check (per parent §4 T5) is the appropriate measurement vector.
- **Downstream implication for T5:** citation-integrity spot-check per parent §4 T5 — T3 did NOT probe this dimension; do not assume Rot is absent from the corpus.

---

## 9. Playbook §9 canonical questions (adapted to T3 scope)

| Q# | Question (adapted) | T3 answer |
|---|---|---|
| Q1 | How many scenarios were measured? | 13 (6 audience-a + 3 audience-b + 5 audience-c-empirical) |
| Q2 | How many scenarios failed (success@3 = N)? | 8 of 13 (~62%) — 4 (c) empirical + 4 (a)/(b) simulated |
| Q3 | Which pain type dominates? | Misleading-meta-dominance + Invisibility tied at 6-7 scenarios each |
| Q4 | Which single doc appears most as "wrong-answer meta-dominance"? | `docs/00-START-NEXT-SESSION.md` (dominates C2 top-3 as three consecutive chunks; appears in C3 outranked by CLAUDE.md; appears in C4 as top-1 pointer instead of target) |
| Q5 | Which single doc appears most as "unreachable target"? | `2701_docs_inventory_topology_audit.md` (C2 + C4 both fail to surface it) — T1's own audit doc is discovery-invisible |
| Q6 | Does the DOC_LIFECYCLE §2c "sole authoritative counts source" convention hold at the discovery layer? | **NO** (C5 evidence — archived October 2025 morning report outranks PLATFORM_INVENTORY.md for "how many spiders" query) |
| Q7 | Is `docs/archive/` partitioned from RAG search corpus? | **NO** (C5 top-1 is `docs/archive/old-structure/status/historical/morning-report-2025-10-02.md`) |
| Q8 | Does literal-filename search retrieve the file? | **NO** (C4 evidence — literal filename `2701_docs_inventory_topology_audit` returns INDEX + reference-list entries, not the file itself) |
| Q9 | Does a doc's own name retrieve the doc? | **NO** (C3 evidence — `search_docs("00-START-NEXT-SESSION")` returns CLAUDE.md chunks that reference the doc, not the doc itself) |
| Q10 | Are convention collisions (adr/decisions, ops/operations, roadmap/roadmaps) surfaced as pain to fresh Claude? | **YES** (B3 direct evidence; T1 §7.1 measurements + T3 (b) scenario confirms behavioral impact) |
| Q11-Q28 | Restructuring proposal; audience segmentation; migration ordering; search-tuning proposals; citation-graph analysis | **Out of T3 scope** — T4/T5/T6/canonical summary owns |

---

## 10. Migration Queue (post-arc)

Per parent §5. T3 items are **behavioral evidence + pain-type diagnosis**, not fix proposals. **Severity: INFORMATIONAL (evidence for canonical summary + downstream implementation).**

| # | Item | Evidence source (this doc) | Severity | Notes for migration session |
|---|---|---|---|---|
| MQ-T3-1 | Archive is not partitioned from RAG search corpus — archived Oct 2025 morning report surfaces as top-1 for counts queries | §7 C5 + §9 Q7 | INFORMATIONAL | Do not move during arc. Canonical summary decides: archive-corpus segregation OR authority-weighted ranker OR `status: superseded` heavy deprioritization. |
| MQ-T3-2 | `docs/00-START-NEXT-SESSION.md` dominates multiple search results (3× in C2 top-3, references outrank targets in C3+C4) | §7 C2/C3/C4 + §8 Rank 1 | INFORMATIONAL | Canonical summary considers: chunk-diversity constraint on ranker; or authority weighting to demote session-snapshot docs when target-artifact docs exist. |
| MQ-T3-3 | Literal filename search fails to retrieve the file (C4) — RAG treats reference-list entries as more relevant than the file itself | §7 C4 + §9 Q8 | INFORMATIONAL | Highest-severity finding for search-layer implementation. Canonical summary flags for downstream implementation session. |
| MQ-T3-4 | DOC_LIFECYCLE §2c "sole authoritative counts source" convention holds in-doc but fails at discovery — users searching for counts get archived stale answers | §7 C5 + §9 Q6 | INFORMATIONAL | Canonical summary considers making the convention discoverability-enforceable (auto-tag PLATFORM_INVENTORY.md with high retrieval weight, or add explicit "you probably want PLATFORM_INVENTORY.md" hint on stale answers). |
| MQ-T3-5 | Convention collisions with real behavioral impact: `docs/adr/` vs `docs/decisions/`; `docs/topics/spider-network.md` vs `docs/SPIDERS.md`; 3 PA doc locations | §6 B1/B2/B3 + §8 Rank 3 | INFORMATIONAL | Canonical summary decides consolidation OR canonical-pointer READMEs. T5 (handoffs+audits) handles the audit-dir triple. |
| MQ-T3-6 | 4 candidate "docs index" locations (INDEX.md / 00-START-NEXT-SESSION.md / research/ARCHITECTURE_INDEX.md / CLAUDE.md) — no single "start here for docs" | §5 A6 | INFORMATIONAL | Canonical summary picks one canonical "start here" or accepts the 4 with a routing README. |
| MQ-T3-7 | 8 of 13 scenarios failed success@3 (~62% failure rate on realistic queries) | §9 Q2 | INFORMATIONAL | Overall substrate score. Canonical summary uses as baseline for post-restructure re-measurement. |

---

## 11. What T3 does NOT resolve (explicit hand-offs)

Per parent §4 anti-scope:

| Question | Handed off to |
|---|---|
| Which audience is each doc PRIMARILY for? | T4 (audience segmentation) |
| Which specific handoffs/audits are read later vs never? | T5 (handoffs+audits proliferation) — citation-graph analysis |
| Which duplicated rules across playbook / CLAUDE.md / memory drift? | T6 (anchor drift) |
| Design of new `/docs/` tree that solves the 5 pain types | Canonical summary at 2799 |
| Search-layer tuning (RAG re-ranking, archive segregation, authority weights) | Post-arc implementation session (canonical summary flags priorities) |
| Whether to rename docs so their names retrieve them (RAG-friendly naming) | Canonical summary decides; migration session executes |
| Fix for `docs/adr/` vs `docs/decisions/` collision | Canonical summary + migration session |

---

## 12. Provenance

**Session:** S2813 (2026-07-18, late-afternoon-to-evening, immediately post-S2812-close)
**Ratifier:** Chris D-verdict "Let's continue" at S2813 open (implicit T3 authorization per ⭐ default in S2813 start-here)
**Git HEAD at authoring:** `1dacec3999b6` (S2812 close cascade)
**Rigby SIGN cycles (TWO per S2811+S2812 OP3 lesson):**

- **Open SIGN** (Q1 scenario coverage / Q2 hop-scoring methodology / Q3 pain-type taxonomy). AGREE on all three with additions (A6 added; C3 added; pain-type taxonomy adopted). Anti-rubber-stamp check PASSED — Rigby ran C1 + C2 live during open-SIGN as empirical evidence. Follow-up dispatch: Rigby ran C3 + C4 + C5 live to seed remaining evidence.

- **Post-authoring pressure-test SIGN** (Q1 scenario evidence integrity / Q2 pain taxonomy application / Q3 §8 rank calibration / Q4 zoom-out on drift potential). AGREE-WITH-EDITS on all 4. Anti-rubber-stamp check PASSED — **Rigby re-ran C4 + C5 live** during pressure-test to spot-check drift potential; identical top-2 results returned in both cases → findings confirmed as structural indexing bias, not query fragility.

**Post-authoring SIGN edits applied (6):**
- §7 C4 top-3 corrected: added actual #3 (`SESSION_2811_..._T1_INVENTORY_AUDIT.md`) — all 3 top results are docs that REFERENCE the target, not the target itself
- §7 C5 phrasing tightened: quote only what tool output confirmed (top-2 + "additional beyond")
- §7 C1 pain tags: drift-adjacent reclassified as commentary; formal count is Misleading-meta-dominance only
- §6 B3 pain tags: Rot removed; Ambiguity retained (partial-population is choice-paralysis, not dead-links)
- §8 Rank 1 mechanism justification: added clarifying sentence — Misleading-meta at #1 is a claim about upstream MECHANISM; Invisibility (Rank 2) is the more catastrophic user-visible failure
- §8 Rank 4 + Rank 5 count adjustments: Drift = 1 direct (C5); Rot = 0 direct in T3, latent risk flagged for T5 substrate-integrity check
- §7 Snapshot warning added post-C5: measurements are point-in-time at HEAD `1dacec3999b6`; T4/T5/T6 authors should re-run before relying

**Third-consecutive OP3 trigger observed.** T3 post-authoring SIGN caught 6 substantive edits including a factual completeness gap (C4 #3 file), 2 tag misclassifications, 2 count corrections, 1 mechanism-vs-severity distinction, 1 methodology rigor addition. Consistent with S2811 T1 and S2812 T2 patterns. **Promotion threshold satisfied for Playbook v0.9 amendment consideration** codifying "audit-shape sessions require post-authoring SIGN in addition to open-scope SIGN."

**Novel T3 methodology:** Rigby was **first-class evidence source** (not just SIGN reviewer). 5 of 13 scenarios (C1-C5) are empirical `search_docs` dispatches; the other 8 (A1-A6, B1-B3) are simulated on reasonable-user-behavior estimates. Rigby's tool_runs are the strongest evidence in T3.

**Tools used:**
- Rigby `search_docs` for C1-C5 empirical measurements
- `ls docs/adr/` + `ls docs/decisions/` for B3 collision verification
- CLAUDE.md read for B1/B2 fresh-Claude path simulation
- Human estimation (mine) for A1-A6 path traces — flagged as simulated

**T3 does NOT re-measure counts** — cites T1 (§3.1: 3201 total .md files, 99 loose at root, 3 parallel audit dirs) as evidence source. Any count in T3 that isn't already in T1 is a scenario-specific measurement (e.g., "4 candidate docs index locations" in A6).

---

**End of T3 — Human-user pain points. T4 (`2704_docs_audience_segmentation_audit.md`) opens next in the audit sequence.**
