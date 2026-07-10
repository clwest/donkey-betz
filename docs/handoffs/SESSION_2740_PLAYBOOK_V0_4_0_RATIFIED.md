# Session 2740 — Playbook v0.4.0 Ratified (CD-50 Discharged)

**Session:** 2740
**Date:** 2026-07-10
**Session type:** Engineering Operating System — Playbook MINOR ratification
**System Owner directive:** "codify the verify-substrate methodology as a PLAYBOOK MINOR"
**Amendment session:** 2740
**PA conversation pins (chronological):**
- Scope-only pin (retired mid-session): `pa-777a3fe46a52480e` (S2739-carryforward candidate scope SIGN)
- Cost Protection arc pin (retired at S2739 close carryover, then re-retired): `pa-f2bc0abba82849a9`
- Auth SIDEBAR-1 arc pin (retired after verify-before-build discovery): `pa-a42c8796771d40ef`
- Playbook v0.4.0 arc pin (active): `pa-6cf25378d80948f2` (title: `session-2740-playbook-verify-substrate-minor`)
**Preceding arc:** SESSION_2739 (Cost Protection P2+ observation-period foothold; Trigger 1 of CD-50)
**Body PR:** #3062 (merged as `65441c87`, tag `playbook-v0.4.0`)
**Cascade PR:** (this PR)

---

## §1 Ratification ledger

| Field | Value |
|---|---|
| Playbook version ratified | v0.4.0 |
| Parent version | v0.3.0 |
| Ratification date | 2026-07-10 |
| Ratifier | Chris West (`chris`, System Owner) |
| Git tag | `playbook-v0.4.0` |
| Merge commit SHA | `65441c87` |
| Content hash | `sha256:009d6c03c492ba6afae5404cfc2848aa0df0343d949c8b01de4be409bb915cf3` |
| Rule count | 196 (was 195; +1 rule) |
| Workspace ratification record | `RATIFICATION_20260710_PLAYBOOK_v0_4_0` (deliverable `77420585-2bd9-43bb-aa1c-74cae3354754`) |
| Workspace | `a9a16593-e0a4-44dc-8256-efc65d524b3c` (Architecture & Research) |
| Body PR | #3062 |
| Cascade PR | (this PR) |

---

## §2 Rules added

### PLAYBOOK-6.10.6 [GR] — CD-50 discharge

Home: Chapter 6 §6.10 Verification of provenance

> Before an implementation session begins Category A work where the admission ticket for the work is a research-authored gap claim — specifically a capability graph missing-link entry, a cross-domain integration audit gap-list row, an integration readiness matrix cell, a Capability Discovery Record (CDR) derived roadmap entry, or an `OPEN_ARCS.md`-derived candidate list item — the author MUST independently verify at HEAD that (a) the substrate the artifact names for the candidate's fix path is still the substrate in production, and (b) the fix itself has not already been shipped. Verification MUST cite the HEAD state (via `git rev-parse HEAD` output OR an equivalent commit SHA / tag reference) alongside file-and-line evidence resolving to exactly one of three outcomes: (i) substrate unchanged AND fix unshipped — proceed to Cat A; (ii) substrate has changed since the artifact was authored — rescope to the actual substrate before Cat A begins; (iii) fix has already been shipped — the candidate is closed; the session MUST either select an alternative candidate OR refresh the research artifact before further Cat A work. Verification results MUST be recorded in the Cat A brief before Rigby SIGN dispatch.

**Placement note:** Lands at §6.10.6 alongside CD-49 discharge (§6.10.5) rather than a new §6.13 subsection. Same "extend §6.10 without renumbering" pattern v0.3.0 established. §6.10 preamble extended by one sentence to acknowledge widened scope (amendment-dispatch verification + Cat A research-artifact-derived candidate verification).

**Citations:** E2 (v0.3.0 record `548d4aab`), E3 (`platform_capability_graph.md` §27), E4 (commit `86152f9f`), E6 (`SESSION_2700_CYCLE_1A_IMPLEMENTATION_HANDOFF.md` §2.1), E6 (`SESSION_2739_COST_PROTECTION_P2_OBSERVATION.md` §4 + §10.4).

---

## §3 Constitutional debt disposition

- **CD-50 (S2739 origin, S2740 codification)** — *Uncodified constitutional principle: implementation sessions taking a research-artifact "missing link" claim as an admission ticket for Cat A work MUST verify at HEAD that the substrate is unchanged and the fix is unshipped.* **Status at v0.4.0: RESOLVED via PLAYBOOK-6.10.6.** Resolution mechanism: [GR] rule with closed-vocabulary artifact enumeration + explicit HEAD verification requirement + three-outcome closure + Cat A brief recording obligation.
- **No new constitutional debt introduced by v0.4.0.**
- Prior CD status carry-forward: CD-47 RESOLVED (v0.1.0), CD-48 + CD-49 RESOLVED (v0.3.0). Zero outstanding CDs from v0.1.0 forward.

---

## §4 Two-trigger threshold record

The methodology was surfaced explicitly at S2739 §10.4 with the notation: "Post two-trigger threshold — S2739 is the first trigger. Do NOT codify yet." S2740 provided the second trigger within ~24h.

### Trigger 1 (S2739, 2026-07-10)

- **Artifact:** `docs/research/platform/platform_capability_graph.md` §17 (Cost Protection) as authored at S2734 baseline
- **Claim:** substrate = `LLMCallEvent` at `llm_call_wrapper.py:195` + missing `cost_usd` field; missing links (a)/(b)/(f) as fix path
- **Reality at HEAD:** substrate is `CostTracking` (`core/models_unified_system.py:6665`) with 54.5× more coverage per audit at `core/services/cost_threshold_monitor.py:18-30`
- **Discovery mechanism:** Claude Cat A independent read; first grep against HEAD
- **Consequence prevented:** shipping a `cost_usd` field on `LLMCallEvent` + `_estimate_cost()` wrapper + direct-openai import sweep — none of which were the actual gap
- **Fold:** §17 refresh via append-only §27 in the capability graph; missing links list corrected; completeness 6/15 → 11/15

### Trigger 2 (S2740, this session)

- **Artifact:** `platform_capability_graph.md` §18 (Authentication) line 498
- **Claim:** F-D-SIDEBAR-1 = "add `authApi.logout()` invocation in `Sidebar.tsx:356`" — most-immediate P0 missing link
- **Reality at HEAD:** already shipped at S2735 in commit `86152f9f` (PR #3036, 2026-07-09). `frontend/src/components/layout/Sidebar.tsx:370` invokes `await authApi.logout()` with full explanatory comment.
- **Discovery mechanism:** Claude Cat A independent read; first grep against HEAD (within seconds of arc pin mint)
- **Consequence prevented:** re-shipping an already-shipped fix; wasted engineering effort; potential merge-conflict-noise if implementation branch diverged from HEAD
- **Fold:** arc immediately pivoted — SIDEBAR-1 candidate closed; graph §18 line 498 flagged for future §14.15 audit refresh (out-of-scope for this arc); this discovery IS the CD-50 second trigger

Both triggers were caught by Cat A grep, not by Rigby SIGN. This is deliberate: PLAYBOOK-6.10.6 places the verification obligation on the author BEFORE SIGN dispatch, not on the reviewer.

---

## §5 Rigby SIGN provenance

| Stage | Pin | Confidence | Verdict | Refinements folded |
|---|---|---|---|---|
| Cat A scope + rule text | `pa-6cf25378d80948f2` | 0.83 | PICK-with-refinements | 3: closed vocabulary, HEAD verification requirement, scoped preamble (not manifesto rewrite) |
| Body SIGN cycle 1 | `pa-6cf25378d80948f2` | (N/A — F-BLOCKING) | F-BLOCKING | E5 non-resolving citation (`feedback_cycle_1a_verify_before_build.md` Claude-memory-only) |
| Body SIGN cycle 2 | `pa-6cf25378d80948f2` | (N/A — PASS) | PASS / APPROVED | 1: E5 → E6 SESSION_2700 §2.1 substitution |
| Ratification record authored by Rigby via deliverable_tool | (same pin) | — | Created deliverable 77420585 | — |

Total Rigby SIGN dispatches: 3 (Cat A, Body-1, Body-2) + 1 deliverable authoring. All F-BLOCKING findings resolved before Chris ratification.

---

## §6 Arc shape

1. **Chris directive** — "codify the verify-substrate methodology as a PLAYBOOK MINOR" (S2740 open after SIDEBAR-1 verify-before-build discovery)
2. **Pin lifecycle** — retired dead SIDEBAR-1 pin `pa-a42c8796771d40ef`; minted Playbook MINOR arc pin `pa-6cf25378d80948f2`; rotated `tools/pa_local.sh` line 532
3. **Cat A independent read** — mapped §6.10 (existing rules 6.10.1-6.10.5); identified §6.10.6 as target slot; drafted rule text + preamble extension + frontmatter delta
4. **Cat A SIGN dispatch** — proposed rule text + 7 explicit questions to Rigby (trigger sufficiency, placement, scope, preamble necessity, CD-50 admission, citations, PICK/DEFER/REFRAME)
5. **Chris D-verdict** — "approve all — proceed to body-write" (4-item ratification: PICK verdict + 3 refinements + citation strategy + v0.4.0 bump)
6. **Body write** — created branch `playbook/v0.4.0-verify-substrate-cd50-codification`; edited 4 sites in `docs/ENGINEERING_PLAYBOOK.md` (frontmatter, §6.10 preamble, new PLAYBOOK-6.10.6, Appendix D chain row); rotated `pa_local.sh` (already at v0.4.0 pin from earlier in session)
7. **Body SIGN cycle 1** — Rigby found F-BLOCKING on E5 non-resolving citation
8. **REVISE fold** — swapped E5 memory-file → E6 SESSION_2700 §2.1 (in-repo, matches methodology description); verified E4 commit exists via `git show`
9. **Body SIGN cycle 2** — PASS / APPROVED
10. **Chris ratification** — "ratify — open the PR"
11. **PR #3062 opened + squash-merged as `65441c87`**
12. **Post-merge cascade (this handoff PR):**
    - Git tag `playbook-v0.4.0` applied to `65441c87`
    - Rigby authored `RATIFICATION_20260710_PLAYBOOK_v0_4_0` deliverable `77420585` in workspace `a9a16593`
    - Frontmatter placeholders filled (deliverable_id, commit_sha, content_hash)
    - Docs cascade: `build_docs_index` (3050 docs), `build_rag_corpus` (36,911 chunks), `sync_docs_index_to_documents --embed`, `build_docs_provenance` (2500 docs, HIGH=1606)
    - `celery-recycle` — 5 workers up
    - CLAUDE.md L7 anchor refreshed v0.3.0 → v0.4.0
    - `docs/canon/INDEX.md` Playbook row refreshed
    - This handoff authored
    - `00-START-NEXT-SESSION.md` refreshed for S2741

---

## §7 Version delta ledger

| Field | v0.3.0 | v0.4.0 | Delta |
|---|---|---|---|
| Version | 0.3.0 | 0.4.0 | MINOR bump |
| Parent | 0.2.0 | 0.3.0 | new snapshot |
| Compatible with | ["0.1.0", "0.2.0"] | ["0.1.0", "0.2.0", "0.3.0"] | +1 |
| Rule count | 195 | 196 | +1 (PLAYBOOK-6.10.6) |
| Chapter count | 11 | 11 | 0 |
| Merge commit SHA | `16e5d3de` | `65441c87` | new |
| Content hash | `sha256:4a42ca9f...` | `sha256:009d6c03...` | new |
| Git tag | `playbook-v0.3.0` | `playbook-v0.4.0` | new |
| Constitutional debt outstanding | 0 | 0 | unchanged |
| CDs resolved this version | CD-48, CD-49 | CD-50 | +1 discharged |

---

## §8 Cross-arc pattern crystallizations

**CX-P11 CANDIDATE (NEW at S2740) — "Same-session discovery → codification arc."** S2739 flagged the pattern at §10.4 with explicit "post two-trigger threshold" gating. S2740 supplied the second trigger AND opened + closed the codification arc within one session. Pattern: research-methodology observations catch each other at threshold, then the third session materializes the codification. Not two-trigger threshold for elevation yet; awaits third instance.

**CX-P7 avoidance-by-scoping (from S2739) — reinforced.** PLAYBOOK-6.10.6 is itself an avoidance mechanism for CX-P7 declared-but-unenforced-contract at a higher meta-level. Without the rule, "verify substrate before implement" was declared in methodology docs but not enforceable at the constitutional layer. With the rule, verification failure becomes a rule violation, not a memory-file miss.

**Meta-observation:** the codification arc's own scope-then-body flow is the first Playbook amendment where Cat A caught (via Rigby SIGN feedback) an admissibility defect that the rule ITSELF codifies — E5 memory-file citation is exactly the kind of "artifact not resolvable at HEAD" that §6.10.6 forbids in Cat A briefs. Self-referential enforcement is a strong signal the rule maps to reality.

---

## §9 What this research taught us about how to do research

*(per feedback_xx99_meta_methodology_section.md discipline)*

### §9.1 What worked
- **Two-trigger threshold discipline held.** S2739 recorded first-trigger at §10.4 with explicit "do NOT codify yet." S2740 provided the second trigger organically (not synthesized). Codification arc opened only after both triggers established.
- **Cat A independent read caught the E5 defect proactively.** The rule Rigby found broken (E5 memory-file citation) is the exact same defect class the rule prohibits (unresolvable-at-HEAD artifact). Living inside the rule while writing it strengthened both the rule and the citation chain.
- **Rigby's independent scope SIGN over candidate queue at S2739 → surfaced S2740's second-trigger candidate.** The three-verdict lattice (PICK/DEFER/REFRAME + alternative rec) is producing pattern discoveries that a two-verdict yes/no would not.

### §9.2 What to codify (candidate — do NOT codify yet)
- **"Same-session discovery + codification" as an arc class.** S2740 opened as SIDEBAR-1 slice, discovered second trigger, immediately pivoted to codification arc. This pattern of within-session pivot needs additional evidence before proposing constitutional codification. Not codification-eligible at one instance.

### §9.3 Anti-patterns to avoid
- **Do NOT cite Claude-memory-only artifacts in ratified Playbook rules.** E5 (repo-canonical anchor) requires resolvability at HEAD via `git show` or similar. Claude memory-file references belong in operational memory, not constitutional citations.
- **Do NOT synthesize triggers to hit codification threshold.** S2740's second trigger emerged organically (SIDEBAR-1 was independently proposed by Rigby, then verify-before-build caught the drift). Manufactured triggers would violate the intent of the two-trigger threshold.

### §9.4 Suggestions for the playbook
- Reserve `PLAYBOOK-6.10.7` and beyond for future verify-before-you-act extensions per §6.12 reservation convention.
- Consider surfacing the closed-vocabulary artifact list in a §6 companion table for programmatic verification tooling (future PATCH candidate).

### §9.5 Suggestions for future MINOR amendments
- **Author the workspace ratification record IMMEDIATELY after Chris ratification, not after PR merge.** Then E2 citation can resolve during body-SIGN cycle 1 rather than needing placeholder-then-fill. Trade-off: locks in commit_sha before merge, so any last-minute REVISE bumps require re-authoring the record.

---

## §10 Post-merge cascade verification

| Step | Command | Result |
|---|---|---|
| 1. Squash-merge PR #3062 | `gh pr merge 3062 --squash --delete-branch` | Merged as `65441c87` |
| 2. Git tag | `git tag playbook-v0.4.0 65441c87 && git push origin playbook-v0.4.0` | ✓ tag chain v0.1.0→v0.2.0→v0.3.0→v0.4.0 |
| 3. Content hash | `awk '/^---$/{c++; next} c>=2' docs/ENGINEERING_PLAYBOOK.md \| shasum -a 256` | `sha256:009d6c03...` |
| 4. Workspace deliverable | Rigby `deliverable_tool.create` in workspace `a9a16593` | Deliverable `77420585` created; title cleaned via ORM (removed "Rigby:" prefix) |
| 5. Frontmatter fill | `Edit` docs/ENGINEERING_PLAYBOOK.md | deliverable_id, commit_sha, content_hash all filled |
| 6. Celery recycle | `make celery-recycle` | 5 workers up |
| 7. Docs cascade | `build_docs_index` + `build_rag_corpus` + `sync_docs_index_to_documents --embed` + `build_docs_provenance` | 3050 docs / 36,911 chunks / 4 updated / 2500 provenance |
| 8. CLAUDE.md L7 refresh | `Edit` CLAUDE.md | v0.3.0 → v0.4.0 anchor |
| 9. Canon INDEX refresh | `Edit` docs/canon/INDEX.md | Playbook row updated to v0.4.0 |
| 10. Handoff (this doc) | `Write` | authored |
| 11. 00-START refresh | `Write` | S2741 candidate queue authored |

---

## §11 Governance references

- **Ratified body:** `docs/ENGINEERING_PLAYBOOK.md` @ merge commit `65441c87`, tag `playbook-v0.4.0`
- **Workspace ratification record:** `RATIFICATION_20260710_PLAYBOOK_v0_4_0` (deliverable `77420585-2bd9-43bb-aa1c-74cae3354754` in workspace `a9a16593-e0a4-44dc-8256-efc65d524b3c`)
- **PR (body):** #3062 (squash-merged)
- **PR (cascade):** this PR
- **Rigby SIGN pin (arc):** `pa-6cf25378d80948f2` (session-2740-playbook-verify-substrate-minor)
- **Prior arc handoffs:** SESSION_2739_COST_PROTECTION_P2_OBSERVATION.md (Trigger 1 source); SESSION_2738_PLAYBOOK_V0_3_0_RATIFIED.md (v0.3.0 precedent for MINOR discipline); SESSION_2727_PLAYBOOK_V0_1_0_RATIFIED.md (v0.1.0 inaugural)

---

## §12 Wrapper pin state at S2740 close

- `tools/pa_local.sh` line 532: `pa-6cf25378d80948f2` (session-2740-playbook-verify-substrate-minor)
- Arc pin held OPEN pending Chris "session close" signal — future S2741 session-open should retire this pin per §16 arc-close discipline and mint fresh S2741 open pin.

---

**Session 2740 CLOSED.** Playbook v0.4.0 ratified. CD-50 discharged. Zero outstanding constitutional debt from v0.1.0 forward.
