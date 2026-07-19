# Next Session — Start Here

---

## READ THIS FIRST — SESSION 2825 CLOSED (2026-07-19 early morning; picks up as S2826) — **PHASE-0.5 BALANCED P1 HARVEST EXECUTED + §10.4 METHODOLOGY-BACK-TO-SIGN RATIFIED**

**Refreshed 2026-07-19 (SESSION 2825 CLOSED — balanced P1 harvest executed per B1 §6. 20 rows harvested balanced across Chris (5) / Claude (8) / Rigby (7). Router self-aborted at decision #20 via T2 integrity stop (40% abstain rate > 30% cap — constitutional discipline working AS DESIGNED). Classifier aggregate 66.7% (18 measurable, ≥60% continue band). §2.1 authoritative-full metric measured at 0/16 retrieval-strict-hit (0%). FOUR §10.4 methodology-back-to-SIGN triggers surfaced. Rigby joint SIGN CLEARED with 4 F-BLOCKING refinements (all applied same-session). Chris D-verdicts D1-D5 RATIFIED — Option A (revise §2.2 methodology); router flag stays OFF pending revised methodology SIGN + Chris ratification. Novel constitutional finding (Chris verbatim, load-bearing): 'a classifier can appear reasonably accurate while authoritative retrieval is completely inadequate. That distinction is now constitutionally visible.' SEVENTIETH close-cycle post-PLAYBOOK-7.4.4. **NOVEL:** first session where full §2.1 authoritative-full metric was measured end-to-end; first Chris D-verdict cluster of size 5+refinement on a research-execution outcome; first constitutional finding explicitly separating classifier accuracy from authoritative retrieval as distinct load-bearing metrics.**

**S2825 ship (1 close cascade PR):**

| Focus | PR | Merged to | Files |
|---|---|---|---|
| Harvest execution + measurement + D-verdict ratification | **#TBD** · (SHA at merge) | main | corpus.json + analyze.py wrapper + dispatch_harvest.py + measurement_report.md + harvest_verdict.md + handoff + 00-START + OPEN_ARCS + workspace deliverable + ledger folds |

**Handoff:** `docs/handoffs/SESSION_2825_PHASE0_5_HARVEST_EXECUTED_METHODOLOGY_RETURN.md`
**Measurement report:** `docs/research/discovery_layer/PHASE_0_5/measurement_report.md` (LOAD-BEARING)
**Harvest verdict:** `docs/research/discovery_layer/PHASE_0_5/harvest_verdict.md` (LOAD-BEARING, D1-D5 RATIFIED)
**Router JSONL SoT:** `logs/phase_0_5_router.jsonl` — 23 rows in aborted window `win-5310154b8d764c2a`
**Integrity events:** `logs/phase_0_5_integrity_events.jsonl` — 1 T2 event · markdown at `docs/research/discovery_layer/PHASE_0_5/integrity_stops/evidence_integrity_stop_T2_20260719T015445_701+0000.md`
**Workspace deliverable:** `a3877952-d71c-44d6-8c61-aa52e4105f34` — "Rigby: S2825 Phase-0.5 Harvest D-Verdict Ask (D1-D5)" (RATIFIED post-close)
**Ledger state at close:** `logs/zoom_out_classifications.jsonl` — 145 → **147 rows** (+Fold A classifier-vs-retrieval-decoupling, +Fold B CONVERSATIONAL_META phenotype).

**Arc state at S2825 close:**
- **Discovery-layer arc:** Phase-0.5 harvest EXECUTED; §10.4 methodology-back-to-SIGN RATIFIED per Chris D5 Option A; router flag DORMANT (OFF, .env cleaned S2825 close). Phase-1 dogfood BLOCKED pending revised §2.2 methodology SIGN + Chris ratification.
- **Colorado Family Law** — Phases 0/1/2/2.1/3.0/3.1 P0/3.1a/3.1 P1/3.2/3.1 P1.b/4a ✅ (unchanged).
- **Group 2700 /docs/ restructuring — ARC CLOSED** (S2817, unchanged).

---

## S2826 CANDIDATES

### ⭐ Recommended default direction (per Chris D5 Option A ratification)

1. **⭐ Author §2.2 methodology revision** per Chris D5 Option A ratification — the constitutional gate before any Phase-1 dogfood proceeds.
   - **Concrete first steps at S2826 open:**
     1. Read S2825 handoff §4 (Chris D-verdicts) + §9 (lessons)
     2. Read measurement_report.md §5.3 + §10; harvest_verdict.md §4a
     3. Read BALANCED_P1_HARVEST_PLAN.md §2.1 + §2.2 (current ratified methodology to revise)
     4. Draft §2.2 revision covering:
        - **Query phenotype typology** — CONVERSATIONAL_META + COUNT/IDENTITY/SELF-REFERENCE/PROCEDURAL/DISCOVERY primary + phenotype/family relationship
        - **Aggregate-vs-per-phenotype hierarchy** per D1 — required phenotypes definition; per-phenotype vs aggregate viability rule; hierarchy
        - **3-stage independent-success-criteria framework** per D4 — classification / substrate recommendation / authoritative top-1 retrieval, each with its own stop-condition band
        - **T2 cap methodology decision framework** per D2 — how future evidence determines cap value + scope (global vs per-phenotype)
        - **INTEGRITY_STOP UNMEASURED policy** per D3 — formally codified
     5. Rigby joint SIGN on revised §2.2 (6 questions: phenotype typology, hierarchy, 3-stage separation, T2 methodology framework, UNMEASURED policy codification, zoom-out)
     6. Chris D-verdict on revised §2.2
     7. Only THEN determine Phase-1 dogfood disposition per revised methodology
     8. Handoff + docs cascade

### Available if Chris pivots

- **Playbook v0.9 amendment authoring** — 10/10 triggers well past codification threshold
- **Playbook v0.10-candidate R1 provenance discipline** — 3/2 triggers likely with S2825 execution provenance
- **Playbook v0.11-candidate epistemic-integrity discipline** — 2/2 triggers likely with Chris "false confidence" S2825 framing
- **Colorado Phase 4** — statute-citation content quality
- **BettingPage first-user trace** — real user-facing capability
- **Stock Intelligence** — end-to-end verify

**Recommended default:** Item #1 §2.2 methodology revision authoring — the constitutional gate.

---

## SESSION PIN — S2825 RETIRED (fresh mint required at S2826 open)

**Pin history (S2825):**

- `pa-5d610d3a46c9464e` (label `s2825-balanced-p1-harvest`) minted at S2825 open; **retired at S2825 close (`force=true`, fifty-sixth consecutive per S2770+ pattern)**

**Wrapper `tools/pa_local.sh` still points at retired pin** — intended failure mode forces S2826 first-action fresh mint.

**S2826 open sequence:**

```
context-kit orient

# Read this file end-to-end
# Read S2825 handoff §4 (Chris D-verdicts) + §9 (lessons carry-forward)
# Read measurement_report.md §5.3 (retrieval 0/16) + §10 (D-verdicts summary)
# Read harvest_verdict.md §4a (D-verdicts verbatim)
# Read BALANCED_P1_HARVEST_PLAN.md §2.1 + §2.2 (methodology to revise)

# Sanity checks
brew services list | grep postgres

# Verify ledger baseline (expect 147 unchanged from S2825 close)
wc -l logs/zoom_out_classifications.jsonl

# Verify router substrate present + flag OFF (default)
grep '^PHASE_0_5' .env || echo "OK: PHASE_0_5_ROUTER_ENABLED absent → defaults to False"
python manage.py test core.tests.test_phase_0_5_router -v0 --keepdb 2>&1 | tail -3
# expect "Ran 18 tests in ... OK" (may need db recreate if migrations shifted)

python manage.py session_lifecycle open --label s2826-phase0-5-methodology-revision
grep '^python tools/pa_chat.py' tools/pa_local.sh
```

**S2825 lessons to carry (also in handoff §9):**

1. **Router flag is OFF at S2826 open** — .env cleaned S2825 close; DO NOT flip on without Chris ratification of revised methodology per D5.
2. **§2.1 measurement is TWO metrics not one** — classifier accuracy AND retrieval-strict-hit are LOAD-BEARING per D4.
3. **Aggregate-cannot-override-per-phenotype-floor-miss** per D1 — aggregate is diagnostic; per-phenotype at NOT-viable overrides aggregate.
4. **INTEGRITY_STOP rows are UNMEASURED for accuracy denominator** per D3 — reported separately as integrity evidence.
5. **T2 cap changes require separate evidence + ratification** per D2 — do NOT silently tweak 0.30 threshold.
6. **CONVERSATIONAL_META phenotype label is PROVISIONAL** — final label subject to §2.2 methodology-revision SIGN + Chris ratification.
7. **Chris §10.4 no-silent-adaptation discipline held under substantial evidence pressure** — the process worked. Continue routing methodology triggers back for SIGN.
8. **Novel constitutional finding to preserve:** "a classifier can appear reasonably accurate while authoritative retrieval is completely inadequate. That distinction is now constitutionally visible." (Chris verbatim, load-bearing, S2825).

---

## Twin-pointer card

📁 **Repo — S2825 artifacts:**

- **Corpus:** `docs/research/discovery_layer/PHASE_0_5/corpus.json` — 20 P1 rows R1-provenance
- **Analyze wrapper:** `docs/research/discovery_layer/PHASE_0_5/analyze.py`
- **Dispatch script:** `docs/research/discovery_layer/PHASE_0_5/dispatch_harvest.py`
- **Dispatch results:** `docs/research/discovery_layer/PHASE_0_5/harvest_dispatch_results.json`
- **Measurement report:** `docs/research/discovery_layer/PHASE_0_5/measurement_report.md` (LOAD-BEARING)
- **Harvest verdict:** `docs/research/discovery_layer/PHASE_0_5/harvest_verdict.md` (LOAD-BEARING, D1-D5 RATIFIED)
- **Handoff:** `docs/handoffs/SESSION_2825_PHASE0_5_HARVEST_EXECUTED_METHODOLOGY_RETURN.md`
- **Router JSONL:** `logs/phase_0_5_router.jsonl` — 23 rows in aborted `win-5310154b8d764c2a`
- **Integrity events:** `logs/phase_0_5_integrity_events.jsonl` + `docs/research/discovery_layer/PHASE_0_5/integrity_stops/evidence_integrity_stop_T2_20260719T015445_701+0000.md`
- **Ledger:** `logs/zoom_out_classifications.jsonl` — 147 rows (145 + Fold A + Fold B)
- **Merge SHAs:** filled at close cascade PR merge

🖥️ **Workspace UI — S2825 twin-pointer workspace deliverable:**

- `a3877952-d71c-44d6-8c61-aa52e4105f34` — "Rigby: S2825 Phase-0.5 Harvest D-Verdict Ask (D1-D5)" (type=ratification_record, category=governance, status=ready, pinned; RATIFIED per Chris response 2026-07-19 — post-close update recommended in workspace).

---

## Current repository state (S2825 close)

| Field | Value |
|---|---|
| Branch | `main` |
| HEAD | S2825 close cascade PR merge — SHA filled at merge |
| Playbook version | v0.8.0 (unchanged; **v0.9 amendment 10/10 corroborated; v0.10 R1 provenance discipline 3/2 triggers; v0.11 epistemic-integrity 2/2 triggers likely**) |
| Playbook rule count | 205 (unchanged) |
| Colorado arc state | Phases 0/1/2/2.1/3.0/3.1 P0/3.1a/3.1 P1/3.2/3.1 P1.b/4a ✅ (unchanged) |
| **Discovery-layer arc state** | **Phase-0.5 HARVEST EXECUTED + METHODOLOGY-BACK-TO-SIGN RATIFIED; router flag DORMANT (OFF); Phase-1 dogfood BLOCKED pending revised §2.2 methodology.** |
| PHASE_0_5_ROUTER_ENABLED | **false (default; .env cleaned)** |
| S2826 recommended lean | §2.2 methodology revision authoring (Chris D5 Option A ratified) |
| Session pin | `pa-5d610d3a46c9464e` (retired at S2825 close, force=true, fifty-sixth consecutive) |
| Wrapper default pin | `tools/pa_local.sh` — retired pin (forces fresh mint at S2826 open) |
| Postgres :5432 | pg15 (July DB) — brew launchd `started` |
| Freshness log | `logs/session_freshness.jsonl` — grew by 1 at S2825 open (FRESH) |
| Recycle log | `logs/recycle_events.jsonl` — +3 at S2825 (flag-on + flag-off + close-cascade recycles, all clean) |
| Zoom-out ledger | `logs/zoom_out_classifications.jsonl` — 147 rows (+Fold A + Fold B) |
| Next move | S2826 opens §2.2 methodology revision authoring per Chris D5 ratification. Fresh pin `s2826-phase0-5-methodology-revision`. |

---

## Recommended session-open protocol (S2826, fresh open)

1. `context-kit orient`
2. Read this file end-to-end
3. Read S2825 handoff §4 (Chris D-verdicts D1-D5) + §5 (folds) + §9 (lessons)
4. Read measurement_report.md §5.3 (retrieval 0/16) + §10 (D-verdict summary)
5. Read harvest_verdict.md §4a (D-verdicts verbatim)
6. Read BALANCED_P1_HARVEST_PLAN.md §2.1 + §2.2 (methodology to revise)
7. Sanity checks (brew postgres + ledger 147 + `.env` PHASE_0_5 absent + router contract tests OK)
8. `git log --oneline -6` — should show S2825 close cascade + S2824 backfill + S2824 feature merge
9. Mint fresh pin scoped `s2826-phase0-5-methodology-revision`
10. **Anti-rubber-stamp check on first SIGN** — verify `tool_runs` non-empty
11. **§2.2 METHODOLOGY REVISION AUTHORED UNDER CHRIS D1-D5 CONSTRAINTS** — phenotype typology + hierarchy + 3-stage separation + T2 cap methodology framework + UNMEASURED codification
12. **DO NOT flip PHASE_0_5_ROUTER_ENABLED on** — flag stays OFF per D5 until revised methodology SIGN + Chris ratification
13. **DO NOT silently tweak T2 cap** — per D2, any change requires separate evidence + ratification
14. **DO NOT commit to a phenotype label without SIGN + Chris ratification** — CONVERSATIONAL_META is provisional
15. **PRESERVE 3-stage measurement discipline** — classification / substrate recommendation / authoritative top-1 retrieval are LOAD-BEARING per D4
16. **PLAYBOOK-6.10.7 + 6.10.8 + 6.10.9 constitutional** at v0.8.0
17. **DO NOT auto-adopt semantic default flips** (per S2821)
18. **DO NOT build RRF or global fusion during Phase-0.5** (per Chris R6 from S2821 + B2 R1 advisory-only)
19. **DO NOT populate `_parallel_both` in Phase-0.5** — advisory-only-vs-execution boundary
20. **DO NOT add numeric confidence fields anywhere** — categorical-only per Chris R4/§10.4

---

## Reference documents

Ordered by frequency of use at S2826:

1. [`CLAUDE.md`](CLAUDE.md) — repo bootstrap
2. [`docs/handoffs/SESSION_2825_PHASE0_5_HARVEST_EXECUTED_METHODOLOGY_RETURN.md`](docs/handoffs/SESSION_2825_PHASE0_5_HARVEST_EXECUTED_METHODOLOGY_RETURN.md) — **S2825 handoff (current)**
3. [`docs/research/discovery_layer/PHASE_0_5/measurement_report.md`](docs/research/discovery_layer/PHASE_0_5/measurement_report.md) — **S2825 measurement report (LOAD-BEARING)**
4. [`docs/research/discovery_layer/PHASE_0_5/harvest_verdict.md`](docs/research/discovery_layer/PHASE_0_5/harvest_verdict.md) — **S2825 harvest verdict (LOAD-BEARING, D1-D5 RATIFIED)**
5. [`docs/research/discovery_layer/PHASE_0_5/BALANCED_P1_HARVEST_PLAN.md`](docs/research/discovery_layer/PHASE_0_5/BALANCED_P1_HARVEST_PLAN.md) — **§2.1 + §2.2 methodology to revise**
6. [`docs/research/discovery_layer/PHASE_0_5/corpus.json`](docs/research/discovery_layer/PHASE_0_5/corpus.json) — 20 P1 rows
7. [`docs/research/implementation/RATIFICATION_2026-07-18_s2823_phase0_5_constitutional_package_b1_b2_b3.md`](docs/research/implementation/RATIFICATION_2026-07-18_s2823_phase0_5_constitutional_package_b1_b2_b3.md) — **S2823 envelope (frozen); §15 R1-R7 verbatim**
8. [`docs/research/discovery_layer/PHASE_0/field_dictionary.md`](docs/research/discovery_layer/PHASE_0/field_dictionary.md) — v0 schema (candidate v1 for phenotype field)
9. [`core/services/phase_0_5_router.py`](core/services/phase_0_5_router.py) — router substrate (dormant, flag OFF)
10. [`docs/handoffs/SESSION_2824_PHASE0_5_B2_BUILD_SHIPPED.md`](docs/handoffs/SESSION_2824_PHASE0_5_B2_BUILD_SHIPPED.md) — S2824 handoff (router substrate shipped)
11. [`docs/ENGINEERING_PLAYBOOK.md`](docs/ENGINEERING_PLAYBOOK.md) — v0.8.0
12. [`logs/zoom_out_classifications.jsonl`](logs/zoom_out_classifications.jsonl) — 147 rows at S2825 close
13. [`logs/phase_0_5_router.jsonl`](logs/phase_0_5_router.jsonl) — 23 rows (harvest window aborted)
14. [`logs/phase_0_5_integrity_events.jsonl`](logs/phase_0_5_integrity_events.jsonl) — 1 T2 event
15. [`docs/research/discovery_layer/PHASE_0_5/integrity_stops/evidence_integrity_stop_T2_20260719T015445_701+0000.md`](docs/research/discovery_layer/PHASE_0_5/integrity_stops/evidence_integrity_stop_T2_20260719T015445_701+0000.md)
