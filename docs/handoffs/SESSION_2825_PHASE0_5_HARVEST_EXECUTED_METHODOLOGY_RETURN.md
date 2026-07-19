---
title: "SESSION 2825 — Phase-0.5 balanced P1 harvest executed; §10.4 methodology-back-to-SIGN ratified; router flag dormant pending revised methodology"
session: 2825
date: 2026-07-19
predecessor: SESSION_2824_PHASE0_5_B2_BUILD_SHIPPED.md
successor: TBD
status: shipped
authority: implementation + governance
scope:
  Executed the S2823 Chris-ratified balanced P1 harvest per B1 §6.
  20 P1 rows harvested balanced across Chris (5) / Claude (8) / Rigby (7).
  Router self-aborted at decision #20 via T2 integrity stop (40% abstain
  rate > 30% cap) — constitutional discipline working as designed.
  §2.1 authoritative-full metric measured at 0/16 retrieval-strict-hit
  (0%). FOUR §10.4 methodology-back-to-SIGN triggers surfaced during
  execution. Rigby joint SIGN CLEARED with 4 F-BLOCKING refinements (all
  applied). Chris D-verdicts D1-D5 RATIFIED — Option A (revise §2.2
  methodology); router flag stays OFF pending revised methodology SIGN
  + Chris ratification.
---

# S2825 — Phase-0.5 balanced P1 harvest executed + methodology-back-to-SIGN ratified

## §1 One-paragraph summary

Balanced P1 harvest executed per S2823 Chris-ratified B1 §6 plan. 20 rows
harvested at hard-min operator-style balance (Chris 5, Claude 8, Rigby 7,
no synthesis per §3 R6). Dispatched through Rigby PA kb_tool.semantic_search
under flag-ON router. **Router self-aborted at decision #20 via T2 integrity
stop (abstain_rate=0.400 > 0.300 cap) — constitutional discipline in the
S2824 B2 substrate working AS DESIGNED**. Q27+Q28 got INTEGRITY_STOP_T2
decisions. Classifier aggregate accuracy 66.7% (18 measurable rows, in
≥60% continue band). **§2.1 authoritative-full metric (classifier AND
retrieval-strict-hit) = 0/16 (0%)** — every retrieval returned the wrong
top-1 file. Query-phenotype disaggregation revealed the CONVERSATIONAL_META
phenotype (conversational, context-dependent, conceptual/discovery
questions) at 20% classifier accuracy while COUNT/IDENTITY/SELF-REFERENCE
phenotypes at 80-100% — but ALL phenotypes 0% retrieval-strict-hit. Rigby
joint SIGN on measurement report CLEARED with 4 F-BLOCKING refinements
(all applied same-session). **Chris D-verdicts D1-D5 RATIFIED** —
Option A (revise §2.2 methodology); router flag OFF; no Phase-1 rollout
until revised methodology SIGN + Chris ratification. **Novel constitutional
finding (Chris verbatim, load-bearing): "a classifier can appear reasonably
accurate while authoritative retrieval is completely inadequate. That
distinction is now constitutionally visible."** SEVENTIETH close-cycle
post-PLAYBOOK-7.4.4.

## §2 Ship

| Focus | PR | Merged to | Files |
|---|---|---|---|
| Phase-0.5 harvest execution + measurement + D-verdict ratification | **#TBD** · (SHA at merge) | main | corpus.json + analyze.py wrapper + dispatch_harvest.py + measurement_report.md + harvest_verdict.md + integrity_stops/*.md + handoff + 00-START + OPEN_ARCS update + zoom-out ledger fold |

### Files shipped

1. **`docs/research/discovery_layer/PHASE_0_5/corpus.json`** — 20 P1 rows R1-provenance-tagged, field_dictionary v0 compliant, `authoring_discipline` block documenting advisory-blind labeling + verbatim-only + internal-paraphrase guard + provenance_source convention
2. **`docs/research/discovery_layer/PHASE_0_5/analyze.py`** — Phase-0.5-local wrapper over Phase-0 classifier evaluation (per Rigby S2825 Q1 SIGN refinement, avoids mutating Phase-0 substrate); computes per-family + per-operator-style accuracy
3. **`docs/research/discovery_layer/PHASE_0_5/dispatch_harvest.py`** — batch dispatcher via `tools/pa_local.sh` (Rigby PA-mediated kb_tool.semantic_search per Rigby Q4 SIGN AGREE)
4. **`docs/research/discovery_layer/PHASE_0_5/harvest_dispatch_results.json`** — raw dispatch envelope tails for retrieval-accuracy correlation
5. **`docs/research/discovery_layer/PHASE_0_5/measurement_report.md`** — full report per B1 §6 step 7; §5 observational retrieval-accuracy correlation; §8 Rigby SIGN record with 4 F-BLOCKING refinements; §10 Chris D-verdicts RATIFIED
6. **`docs/research/discovery_layer/PHASE_0_5/harvest_verdict.md`** — Chris D-verdict ask + §4a Chris D-verdicts RATIFIED (verbatim)
7. **`docs/research/discovery_layer/PHASE_0_5/integrity_stops/evidence_integrity_stop_T2_20260719T015445_701+0000.md`** — T2 abort evidence written by router at runtime (Rigby S2824 Q6-B refinement working)
8. **Workspace deliverable** `a3877952-d71c-44d6-8c61-aa52e4105f34` — Chris D-verdict ask visible in Chat UI; RATIFIED per Chris response 2026-07-19
9. **Handoff** — this doc
10. **00-START-NEXT-SESSION.md** — S2826 opens on §2.2 methodology revision authoring per D5 Option A
11. **OPEN_ARCS.md** — Phase-0.5 arc state updated; Phase-1 dogfood blocked pending methodology revision
12. **logs/zoom_out_classifications.jsonl** — folds recorded per PLAYBOOK-6.10.8 for load-bearing S2825 observations

### Ledger delta

- `logs/zoom_out_classifications.jsonl`: 145 → 147 (+2 folds; see §5)
- `logs/phase_0_5_router.jsonl`: 0 → 23 rows (1 window_start + 22 router_decision, in aborted window `win-5310154b8d764c2a`)
- `logs/phase_0_5_integrity_events.jsonl`: 0 → 1 (T2 event)
- `docs/research/discovery_layer/PHASE_0_5/integrity_stops/`: 0 → 1 markdown

## §3 Rigby joint SIGN record (S2825)

### §3.1 Cycle 1 — plan-alignment SIGN (turn ~2)

Q1-Q6 on execution plan (analyze.py substrate / two-analyzer authority / Rigby harvest source / dispatch shape / window segregation / zoom-out coupling).

| Q | Verdict | Refinement |
|---|---|---|
| Q1 | AGREE-with-refinements | Phase-0.5-local wrapper analyze.py; avoid mutating PHASE_0 |
| Q2 | AGREE | analyze.py = §2.2 authority; analyze_router_log.py = diagnostics |
| Q3 | AGREE | Handoff [PA_TASK_SUMMARY] primary; LLMCallEvent DEMOTED |
| Q4 | AGREE | Rigby PA-mediated dispatch through handler surface |
| Q5 | AGREE | window_type=harvest_phase segregation (fallback: post-hoc measurement_window_id filter) |
| Q6 | AGREE-with-refinements | Advisory-blind labeling discipline (labels authored BEFORE dispatches) |

**Anti-rubber-stamp PASSED** — 5 substantive tool_runs (repo_tool tree + 3 read_file + search_docs).

### §3.2 Harvest execution SIGNs

- **Chris §4.1 harvest** — Claude extracted 1 candidate from S2822 envelope §125; delegated §4.1 secondary to Rigby (Chat UI history); Rigby returned 4 verified candidates (Q10-Q13) with 1 re-verification round (canonical enum enforcement Q5 C2 discipline)
- **Claude §4.2 harvest** — Delegated to Rigby (Claude direct Grep/Read bypass PA logs); Rigby returned 8 candidates (Q14-Q21) from S2820/S2822 benchmark queries
- **Rigby §4.3 harvest** — 5 initial (Q22-Q26 from S2824 handoff §5.1/§5.2 validation tables) + 2 extension (Q27-Q28 from S2813/S2815 audit tool_runs) = 7 total

**Anti-rubber-stamp discipline** applied at each harvest dispatch — tool_runs verified non-empty with substantive conversation_tool.search + repo_tool probes.

### §3.3 Cycle 2 — measurement report SIGN (turn ~14)

Q1-Q5 on measurement report (§2.2 hierarchy / INTEGRITY_STOP counting / T2 cap right for real P1 / retrieval-correlation deferral / zoom-out).

| Q | Verdict | Refinement applied |
|---|---|---|
| Q1 | **AGREE (F-BLOCKING)** | §3.1 stop-condition-band-shape trigger acknowledged as §10.4-load-bearing |
| Q2 | **AGREE-with-refinements (F-BLOCKING)** | Q27+Q28 UNMEASURED for accuracy denominator; still integrity-evidence |
| Q3 | **AGREE-with-refinements (F-BLOCKING)** | T2 cap methodology decision required; no silent tweaks |
| Q4 | AGREE-with-refinements (NOT F-BLOCKING) | Retrieval correlation computed NOW as observational; BARRED from go/no-go until §10.4 resolved |
| Q5 | **AGREE-with-refinements (F-BLOCKING)** | Reframe verdict from "Chris personally" to "query phenotype" |

**Anti-rubber-stamp PASSED** — 4 substantive search_docs probes across BALANCED_P1_HARVEST_PLAN §2.2, ROUTER_SCAFFOLDING_DESIGN §12 T2, field_dictionary rule 6, and harvest_plan §5 rule 4.

**All 5 refinements applied to measurement_report.md + harvest_verdict.md same-session before Chris routing.**

## §4 Chris D-verdicts RATIFIED (2026-07-19)

**All five D-verdicts + phenotype-rename refinement RATIFIED** per Chris response. See §4a of `harvest_verdict.md` for full verbatim ratifications. Summary:

- **D1** RATIFIED — aggregate is diagnostic only; per-phenotype failure cannot be masked; §2.2 revision must explicitly define phenotypes + hierarchy
- **D2** RATIFIED-with-refinement — T2 cap 0.30 stays in force; NO silent cap changes; any change requires separate evidence + ratification
- **D3** RATIFIED — INTEGRITY_STOP rows UNMEASURED for accuracy denominator; reported separately as integrity evidence
- **D4** RATIFIED — strict retrieval accuracy is LOAD-BEARING; 3-stage separate measurement (classification / substrate recommendation / authoritative top-1 retrieval) with independent success criteria
- **D5** RATIFIED **Option A** — revise §2.2 methodology; NO universal rollout; NO phenotype-partial rollout; router flag stays OFF pending revised methodology SIGN + Chris ratification
- **Additional** — "Chris-style" renamed to **CONVERSATIONAL_META query phenotype** (conversational / context-dependent / conceptual-discovery); final label subject to methodology-revision SIGN

**Chris framing (verbatim, load-bearing constitutional finding):**

> "The important outcome of S2825 is not that the router 'passed' or 'failed.' It is that the constitutional process exposed a methodological weakness before the platform could make a misleading claim. That is a successful experiment."

> "The biggest discovery from S2825 is not classifier accuracy. It is that a classifier can appear reasonably accurate while authoritative retrieval is completely inadequate. That distinction is now constitutionally visible. That is exactly the kind of false confidence this platform exists to prevent."

## §5 Zoom-out folds (per PLAYBOOK-6.10.8 + 6.10.9 evidence discipline)

Two folds persisted to `logs/zoom_out_classifications.jsonl` at S2825 close (145 → 147):

### §5.1 Fold A — classifier-vs-retrieval decoupling as first-class metric

- **Class:** `same_pr_actionable` — new constitutional discovery load-bearing enough to shape S2826 methodology revision
- **Trigger source:** S2825 measurement report §5.3 finding + Chris D4 ratification
- **Evidence pointers:** measurement_report.md §5.3 (§2.1 authoritative-full = 0/18 = 0%); harvest_verdict.md §4a.4 (D4 verbatim); Chris framing §4 above
- **Constitutional shift:** classifier accuracy is diagnostic; authoritative retrieval is LOAD-BEARING; the two must be measured separately with independent success criteria
- **Same-PR mitigation:** measurement_report.md §5.3 + §10 documenting this discovery + D4 ratification captured verbatim + S2826 methodology revision arc opened via 00-START

### §5.2 Fold B — CONVERSATIONAL_META query-phenotype as first-class unit

- **Class:** `future_trigger` — phenotype-typology needs formal definition during S2826 methodology revision
- **Trigger source:** Rigby Q5 F-BLOCKING refinement + Chris additional-ratification (phenotype rename)
- **Evidence pointers:** measurement_report.md §6 reframing; harvest_verdict.md §4a.6 (phenotype rename ratification); §2 headline metrics per-phenotype table
- **Why future_trigger:** the phenotype label is provisional (working label CONVERSATIONAL_META); formal typology + criteria for "phenotype-hierarchy" per D1 requires §2.2 methodology revision authoring — not codifiable in S2825 close alone
- **Extension point:** BALANCED_P1_HARVEST_PLAN.md §3 (balance targets) needs phenotype-column parallel to operator-style-column; requires field_dictionary v1 amendment for `query_phenotype` field

## §6 What worked / what to fold forward / methodology-teaches (Playbook §11.3)

### §6.1 What worked

- **Rigby joint SIGN discipline held under execution pressure** — 4 F-BLOCKING catches on measurement report caught real methodology gaps that would have shipped a misleading verdict silently
- **Anti-rubber-stamp check on Rigby SIGN passed both cycles** — verified tool_runs non-empty and substantive at plan-alignment SIGN + measurement-report SIGN
- **Advisory-blind labeling discipline (Q6 refinement) prevented label contamination** — known_correct_target_strict was authored from architectural knowledge BEFORE dispatches; router advisory output confirmed after had zero opportunity to backwash into labels
- **Router T2 integrity stop worked as designed** — the constitutional discipline shipped in S2824 caught real measurement-integrity issue in first actual harvest use, preventing 40%-abstain-rate data from being interpreted as valid measurement
- **Chris §10.4 discipline prevented silent adaptation** — 4 methodology triggers surfaced with clear "route back to SIGN + Chris D-verdict" path; no attempt to raise T2 cap or ignore Chris-phenotype-20% or apply an unauthorized default
- **Verbatim quote preservation held** — no case-fold/whitespace-normalize on any of 20 harvested query_texts; §4.4 internal-paraphrase guard applied to Rigby-originated candidates
- **Balance-not-synthesis discipline held** — Chris hard-min 5 met via §4.1 secondary source rather than backfill; DISCOVERY family gap not filled with synthetic rows
- **Chris framing "constitutional process exposed methodological weakness before misleading claim"** — this IS the platform's constitutional purpose realized in a research outcome

### §6.2 What to fold forward to Playbook v0.9+ / future arcs

- **Classifier-vs-retrieval-separation as first-class metric structure** — see Fold A. Once corroborated in one more independent arc (or explicit Chris ratification of the methodology-revision output), consider Playbook amendment codifying "any routing/classification measurement MUST report authoritative-retrieval as independent stage with independent success criteria."
- **Aggregate-vs-per-phenotype hierarchy rule** — S2825 first instance where aggregate says continue but sub-phenotype says NOT viable. Future stop-condition-band definitions should explicitly resolve this hierarchy per D1. Candidate Playbook rule for §2.2-style bands: "aggregate metrics MUST be accompanied by per-phenotype disaggregation for any required phenotype; aggregate CANNOT override per-phenotype floor miss."
- **CONVERSATIONAL_META phenotype recognition** — see Fold B. The category of "conversational, context-dependent, conceptual/discovery" queries is empirically a distinct class from well-formed COUNT/IDENTITY/SELF-REFERENCE queries. Formal typology + criteria to be authored in S2826 methodology revision.

### §6.3 Anti-patterns avoided

- **Did NOT** silently raise T2 cap from 0.30 to accommodate the 40% observed abstain rate
- **Did NOT** treat balanced-set 62.5% as authoritative continue without exposing Chris-phenotype 20% failure
- **Did NOT** synthesize Chris-style queries to reach n≥8 preferred balance (§3 R6 preserved)
- **Did NOT** allow router advisory output to influence known_correct_target_strict labeling (Q6 refinement worked)
- **Did NOT** frame the phenotype-finding as "Chris personally" — Rigby Q5 F-BLOCKING caught this + Chris explicitly ratified the phenotype reframing
- **Did NOT** flip the router flag off silently — surfaced the decision to Chris + preserved the option for methodology-revision re-enable

## §7 What S2826 opens on

**Recommended default direction:** author the §2.2 methodology revision per Chris D5 Option A ratification. Concrete first steps:

1. Open S2826 with fresh pin `s2826-phase0-5-methodology-revision`
2. Read S2825 handoff + measurement_report.md §5.3 + §10 + harvest_verdict.md §4a
3. Read BALANCED_P1_HARVEST_PLAN.md §2.1 + §2.2 (current ratified methodology)
4. Draft §2.2 methodology revision covering:
   - **Query phenotype typology** — CONVERSATIONAL_META + COUNT/IDENTITY/SELF-REFERENCE/PROCEDURAL/DISCOVERY primary + phenotype/family relationship
   - **Aggregate-vs-per-phenotype hierarchy** — how required phenotypes are defined; whether viability is per-phenotype or aggregate rule; hierarchy between metrics
   - **3-stage independent-success-criteria framework** — classification / substrate recommendation / authoritative top-1 retrieval, each with its own stop-condition band
   - **T2 cap methodology decision framework** — how future evidence determines cap value + scope (global vs per-phenotype)
   - **INTEGRITY_STOP UNMEASURED policy** — formally codified per D3
5. Rigby joint SIGN + Chris D-verdict on revised §2.2
6. Only THEN determine Phase-1 dogfood disposition (universal / phenotype-partial / shelve)

**Router substrate remains DORMANT** (flag OFF, .env cleaned S2825 close) — do NOT re-enable during methodology revision authoring without explicit Chris ratification. The S2824 substrate is READY to be re-enabled once revised methodology defines how it should be used.

**Available if Chris pivots:**

- **Playbook v0.9 amendment authoring** — 10/10 triggers well past codification threshold (unchanged from S2823/S2824)
- **Playbook v0.10-candidate R1 provenance discipline** — 3/2 triggers likely with S2825 execution provenance
- **Playbook v0.11-candidate epistemic-integrity discipline** — 2/2 triggers likely with Chris "false confidence" S2825 framing
- **Colorado Phase 4** — statute-citation content quality
- **BettingPage first-user trace** — real user-facing capability
- **Stock Intelligence** — end-to-end verify

## §8 Twin-pointer card

📁 **Repo — S2825 artifacts:**

- **Corpus:** `docs/research/discovery_layer/PHASE_0_5/corpus.json` — 20 P1 rows
- **Analyze wrapper:** `docs/research/discovery_layer/PHASE_0_5/analyze.py`
- **Dispatch script:** `docs/research/discovery_layer/PHASE_0_5/dispatch_harvest.py`
- **Dispatch results:** `docs/research/discovery_layer/PHASE_0_5/harvest_dispatch_results.json`
- **Measurement report:** `docs/research/discovery_layer/PHASE_0_5/measurement_report.md` (LOAD-BEARING)
- **Harvest verdict:** `docs/research/discovery_layer/PHASE_0_5/harvest_verdict.md` (LOAD-BEARING — D1-D5 RATIFIED)
- **Router log SoT:** `logs/phase_0_5_router.jsonl` — 23 rows in aborted window `win-5310154b8d764c2a`
- **Integrity events:** `logs/phase_0_5_integrity_events.jsonl` — 1 T2 event
- **Integrity-stop markdown:** `docs/research/discovery_layer/PHASE_0_5/integrity_stops/evidence_integrity_stop_T2_20260719T015445_701+0000.md`
- **Handoff:** this doc
- **Ledger:** `logs/zoom_out_classifications.jsonl` — 145 → 147 (+Fold A + Fold B)
- **Merge SHAs:** filled at feature PR + close cascade PR merges

🖥️ **Workspace UI — S2825 twin-pointer workspace deliverable:**

- `a3877952-d71c-44d6-8c61-aa52e4105f34` — "Rigby: S2825 Phase-0.5 Harvest D-Verdict Ask (D1-D5)" (type=ratification_record, category=governance, status=ready, pinned). Chris D-verdicts RATIFIED per this handoff §4 — deliverable should be updated post-cascade with RATIFIED status + verbatim D-verdicts + link to this handoff.

## §9 Lessons carry-forward for S2826

1. **Router flag is OFF at S2826 open** — flag OFF is now default via .env-cleanup. Do NOT flip on without Chris ratification of revised methodology per D5.
2. **§2.1 measurement is TWO metrics not one** — classifier accuracy AND retrieval-strict-hit are LOAD-BEARING per D4. Any future measurement must report both with independent success criteria.
3. **Aggregate-cannot-override-per-phenotype-floor-miss** per D1 — aggregate is diagnostic; per-phenotype at NOT-viable overrides aggregate at continue.
4. **INTEGRITY_STOP rows are UNMEASURED for accuracy denominator** per D3 — reported separately as integrity evidence.
5. **T2 cap changes require separate evidence + ratification** per D2 — do NOT silently tweak the 0.30 threshold.
6. **CONVERSATIONAL_META phenotype label is PROVISIONAL** — final label subject to §2.2 methodology-revision SIGN + Chris ratification.
7. **Chris §10.4 no-silent-adaptation discipline held under substantial evidence pressure** — the process worked. Continue routing methodology triggers back for SIGN rather than silently adapting.
8. **The novel constitutional finding to preserve at CLAUDE.md / 00-START anchor level:** "a classifier can appear reasonably accurate while authoritative retrieval is completely inadequate" — this is the S2825 discovery worth remembering in future substrate design.
