---
session: 2504
status: closed (S2504 P4 Cat D Permission-Floor Registry + REST↔WS T7 Joint Design-Prep child audit — draft written 2026-07-05 post-6-parallel-Explore-sweep + parent-Claude verifier-loop resolving 4 sub-agent conflicts pre-Rigby-SIGN routing, Rigby SIGN cycle 1 COMPLETE via dedicated fresh SIGN isolation pin `pa-1aad569644364682` — TWENTY-FIRST consecutive dedicated fresh SIGN pin retirement in Research OS after S1399/S1499/S1599/S1699/S1799/S1899/S1999/S2099/S2199/S2299/S2400/S2401/S2402/S2403/S2404/S2499/S2500/S2501/S2502/S2503 twenty prior — retired via `session_tool.retire force=true` at cycle close, updated_count=1, retired=true, previously_active=true; 4-batch × 5-Q = 20-Q child-audit cadence per S2201-S2503 twelve-consecutive tested pattern THIRTEENTH-consecutive application; Rigby overall confidence HIGH; cycle 2 NOT required per Rigby explicit verdict at Q20 close; 20 folds landed pre-Chris-ratification (7 AGREE Q1+Q4+Q7+Q9+Q11+Q13+Q14+Q17+Q19+Q20 ten + 10 STRENGTHEN Q2+Q3+Q5+Q6+Q8+Q10+Q12+Q15+Q16+Q18 ten) within 15-25-fold S2201-S2503 empirical baseline; Chris "commit it" 2026-07-06 ratified 20 folds wholesale — status flipped `draft` → `active` per playbook §16 draft-first workflow; playbook §11.2 20-section child-audit template TWENTY-THIRD-consecutive application after S1301+S1401+S1501+S1601+S1701+S1801+S1901+S2001+S2101+S2102+S2103+S2104+S2201+S2202+S2203+S2204+S2401+S2402+S2403+S2404+S2501+S2502+S2503 twenty-two prior; arc pin `pa-a03b111768464b3f` ACTIVE + PRESERVED through S2504 per playbook §16 arc-standard behavior — no retirement until S2599 xx99 close; 5 of 6 sessions shipped in Group 2500 arc.)
date: 2026-07-06
arc: Research Group 2500 (API — Contract SoT + Silent-401 Downstream Remediation + Session-Lifecycle API Contracts + Per-Endpoint Permission-Floor Registry Design-Prep + REST↔WS T7 Joint 2500+2600) — S2504 P4 Cat D Permission-Floor Registry + REST↔WS T7 Joint Design-Prep child audit + Rigby SIGN cycle 1 close
head_sha: 87624a3d (S2504 open) → post-commit sha (post-fold + Chris ratification)
---

# Session 2504 — Group 2500 API Cat D Permission-Floor Registry + REST↔WS T7 Joint Design-Prep + Rigby SIGN Cycle 1 Close

## What shipped

`docs/research/domains/api/2504_api_permission_floor_registry_rest_ws_t7_joint_design_prep_audit.md` — 20-section child audit per playbook §11.2 TWENTY-THIRD-consecutive application. **Boundary evidence + option-space inventory for the PERMISSION-FLOOR REGISTRY layer** (Cat B (c) LONG-TERM GOVERNANCE per S2499 CF-B1) **and REST↔WS T7 JOINT CONTRACT SoT layer** (S2203 §17.3 verbatim) at the tail of the Group 2500 arc between Cat A (S2501 DECLARATION), Cat B (S2502 CONSUMER), Cat C (S2503 CONTRACT-INTERSECTION), and the upcoming S2599 xx99 canonical summary.

**Doc size:** 989 lines post-fold / ~12k words. HEAD-verified baselines at draft-open (`87624a3d`) + post-verifier-loop reconciled + post-Rigby-SIGN 20 folds applied.

**Boundary discipline preserved (mirror Cat A + Cat B + Cat C posture):** Cat D enumerates + inventories + measures + classifies + defers + proposes evidence-collection; Cat D does NOT prescribe (a)/(b)/(c) permission-floor Cat B option selection, per-endpoint registry mechanism selection, REST↔WS message-contract strictness selection, or execution locus for whitelist-replacement γ mechanism. All "recommendations" in §19 are Chris-D-verdict-request evidence for S2599 xx99 close, NOT directives. Verbs stay `enumerate / inventory / measure / classify / verify / re-verify / defer / propose evidence-collection`.

## Key verifier findings

1. **§14.1 F-D-REGISTRY-1 NEW** — Per-endpoint permission-floor registry ABSENT at HEAD (Cat B (c) LONG-TERM GOVERNANCE per S2499 CF-B1 = **greenfield**). Parent-Claude ripgrep for `APIEndpoint`, `RouteFloor`, `EndpointPermission`, `PermissionRegistry` in `core/models*.py` + all app-level `models.py` = zero matches. **Class:** `missing_connection` + `technical_debt` (governance). **Severity:** HIGH baseline. **Classification note per Q14:** "design-plane SoT gaps, not violations of an explicitly adopted standard" — `boundary_violation` classification deliberately NOT applied.

2. **§14.2 F-D-WSENVELOPE-1 NEW** — WS message-contract SoT ABSENT at HEAD (T7 joint per S2203 §17.3 = **greenfield**). Zero TypedDict/Protocol/BaseModel/dataclass envelope shapes in `**/consumers*.py`; zero `channels_graphql`; zero `.schema.json` files for WS message types. S2202 §14 F3 preserved: 0/40 unique consumer classes with `group_send` conform to `ui.render_hint` envelope schema. **Class:** `missing_connection` + `technical_debt`. **Severity:** HIGH baseline.

3. **§14.3 F-D-4LAYERSPLIT-1 NEW SYNTHESIS** — Permission-floor stack fragmented across 4 architecturally independent layers at HEAD with no cross-layer SoT: (i) DRF DEFAULT layer (`DEFAULT_PERMISSION_CLASSES = [IsAuthenticated]` at `core/settings.py:652-653`), (ii) explicit decorator layer (838 `@permission_classes` sites + 74 class-attr sites), (iii) path-list gate layer (285 total entries across 6 constants in `core/auth_middleware.py`), (iv) custom Permission class layer (3 classes: FleetSignatureRequired, FleetCapabilityRequired, PublicIntelTokenAuth). Middleware path-list (layer 3) evaluates FIRST + short-circuits before DRF dispatch — SOURCE of F-B-HIGH-2 `/api/v1/betting/place/` inversion dead-code. **Class:** `technical_debt` + `unclear_owner`. **Severity:** MEDIUM (governance discipline gap).

4. **§14.9 REVIEWER_BLOCKED_PATHS REDUCTION DRIFT NEW** — S2402 baseline 12 entries → HEAD 7 entries = **-5 REDUCTION drift** (positive governance signal per Q15 STRENGTHEN fold — softened to "observed reduction drift suggests pruning; intent/lineage not established here"). Optional post-arc T-slot task: git lineage trace to identify pruning commit.

5. **§14.10 WS route -5 drift NEW** — S2202 baseline 125 → HEAD 120 = -5 drift (low severity denominator alignment).

6. **§14.8 F-B-HIGH-4 1-file REDUCTION DRIFT NEW** — S2402 baseline 4 files with `@authentication_classes([])` → HEAD 3 files (`core/views_nervous.py` cleaned up between S2402 close + HEAD `87624a3d`); 6 sites across 3 files preserved; CRITICAL-per-site for `core/auth_views_enhanced.py:560` (contains logout). Findings-appendix per Q1 P4-retitle fold.

7. **§9.2 CF-D6 NEW cross-arc coordination flag** — REST↔WS T7 joint contract SoT dual-owned Group 2500 API + Group 2600 PA per S2500 §3.D language. **Secondary stakeholders (non-owners) per Q9 AGREE fold:** Group 1700 Observability (emission/telemetry implications); Group 2300 Mobile (client interception implications). No flag-explosion.

8. **§5.5 + §9.3 + R1 FleetCapabilityRequired mechanism-vs-governance distinction** — `core/services/fleet_auth_drf.py:215-263` `.for_capability(*path)` classmethod demonstrates a DRF-layer capability gating MECHANISM PRIMITIVE (per-endpoint declarable intent + model-backed check) is viable at HEAD; **does NOT demonstrate a full Cat B (c) registry/governance system** (per Q5 + Q18 STRENGTHEN folds). Registry model + admin UI + CI-lint gate + governance workflow are additive to the mechanism primitive.

9. **§16 Level 0 anchor DE-INFLATION per Q16 STRENGTHEN fold** — Cat C S2503 canonical Level 0 anchor scope (3 domains: error envelope + refresh + logout) PRESERVED. Cat D adds 2 "Level 0-adjacent candidates for xx99 consolidation" (permission-floor semantics + REST↔WS message-contract strictness semantics), NOT a redefinition. xx99 canonical summary owns whether to consolidate.

10. **§1.1 Denominator Contract with 6 denominator definitions per Q2 STRENGTHEN fold** — D1 URL route count 1,856 core-only; D2 permission decoration sites 838; D3 class-attr sites 74; D4 unique view functions UNKNOWN (deferred); D5 WS route count 120; D6 Consumer class definitions 87. **Reconciliation with S2402 F-B-CRIT-1**: 838/1,856 = 49% "route-indexed explicit surface ratio" is NOT directly comparable to S2402's ~84.4% implicit-inheritance estimate (view-level inference vs route-level site ratio); Cat D preserves S2402 as authoritative for platform-wide rate.

## Rigby SIGN cycle 1 verdict

**Dedicated fresh SIGN isolation pin `pa-1aad569644364682`** minted at S2504 open per playbook §15 (TWENTY-FIRST consecutive dedicated fresh SIGN pin under Research OS after twenty prior). Cycle 1 completed with **20 folds landed** via 4-batch × 5-Q = 20-Q child-audit cadence per S2201-S2503 twelve-consecutive tested pattern (THIRTEENTH-consecutive application). Retired via `session_tool.retire force=true` at cycle close (updated_count=1, retired=true, previously_active=true).

**Rigby verdict at cycle 1 close:** SIGN-with-edits + **cycle 2 NOT required** (no new research; only phrasing + anchoring precision). Overall confidence HIGH.

**Fold cadence per batch:**

- **Batch 1 (Q1-Q5) §1-§5 Executive + Denominator + Purpose + Entry Points + Models:** Q1 AGREE + Q2 STRENGTHEN + Q3 STRENGTHEN + Q4 AGREE + Q5 STRENGTHEN. Key folds: "zero" language softened; Denominator Definitions block D1-D6 added; §1.2 note 3 out-of-scope guardrail; REQUIRE_WEBSOCKET_AUTH T-slot candidate; FleetCapabilityRequired mechanism-vs-governance distinction.
- **Batch 2 (Q6-Q10) §6-§10 APIs + Runtime + Data Ownership + Integrations + Event Flows:** Q6 STRENGTHEN + Q7 AGREE + Q8 STRENGTHEN + Q9 AGREE + Q10 STRENGTHEN. Key folds: 79.3% upper-bound risk-weighted disambiguation; §7.2 decision-space pointer (Cat C R2 territory); §7.4 REST-per-request vs WS-per-connection unit-mismatch + Group 1700 measurement handoff; CF-D6 secondary stakeholders line; §8.1 "MUST" prescriptive language removed.
- **Batch 3 (Q11-Q15) §11-§15 Documentation + Research Coverage + Maturity + Drift + Debt:** Q11 AGREE + Q12 STRENGTHEN + Q13 AGREE + Q14 AGREE + Q15 STRENGTHEN. Key folds: anti-fatigue justification for anchor-update deferral; coverage labels "HEAD implementation evidence depth vs conceptual-spec depth" clarification + T7 split; 8-dimension anti-dilution note + owner/decision pointer; findings classification "design-plane SoT gaps, not violations"; REVIEWER_BLOCKED_PATHS intent-attribution softened + optional lineage T-slot.
- **Batch 4 (Q16-Q20) §16-§20 Boundary Violations + Duplicate/Overlap + Ownership + Recommendations + Appendix:** Q16 STRENGTHEN + Q17 AGREE + Q18 STRENGTHEN + Q19 AGREE + Q20 AGREE. Key folds: Level 0 anchor de-inflation (Cat D adjacent-candidates for xx99 consolidation); F-D-OWN-1 partial-scope resolution language; R1 mechanism-primitive-vs-governance-system exact rewrite; R10 depends_on: R2 lineage linkage; verifier-loop count within expected range.

**Cadence totals:** 10 AGREE + 10 STRENGTHEN = 20 folds; within 15-25 empirical baseline per S2201-S2503 tested pattern.

## Verifier-loop pre-Rigby-SIGN discipline

Per playbook §14 discipline: **4 sub-agent conflicts resolved via parent-Claude definitive HEAD greps pre-draft:**

1. Agent 2 said PUBLIC_PATHS = 263 entries; Agent 6 said 265. Parent-Claude Python-parser: **265** confirmed (Agent 6 correct).
2. Agent 2 said REVIEWER_BLOCKED_PATHS = 18; Agent 6 said 11; S2402 said 12. Parent-Claude Python-parser: **7** → NEW -5 REDUCTION drift observation (§14.9).
3. Agent 3 said "51 WS patterns in core/routing.py" + "59 total"; parent-Claude grep: **107 core / 120 total** across 5 routing.py files (Agent 3 miscounted).
4. S2402 said 4 files with `@authentication_classes([])`; parent-Claude grep at HEAD: **3 files, 6 sites** → NEW -1 file REDUCTION drift observation (§14.8).

Conflict count within expected ~3-7 range per S2201-S2503 twelve-consecutive tested pattern; verifier-loop discipline proportionate; no evidence 6-parallel sweep was mis-scoped.

## Load-bearing outputs handed forward to S2599 xx99

- **§9.1 α/β/γ intersection model preserved:** 4 independent decision-spaces (Cat D typed-error-envelope + Cat D whitelist-replacement + Cat B permission-floor + REST↔WS T7 Path A/B/C); ONE established nesting from Cat C S2503 §9.1 Q12 (Cat D γ = mechanism; Cat C β = UX policy nested inside γ default handler). All other pairings INDEPENDENT unless explicitly coupled by xx99 verdict.

- **§13 Cat D 8-dimension maturity table** (dimensions constant across arc children per Q13 AGREE fold; overlap tolerated when dimensions map to distinct decision-spaces): 2 GREENFIELD (permission-floor registry F6 + whitelist-replacement F8) + 1 WORKING (path-list gate registry F3) + 1 EXPERIMENTAL (REST↔WS T7 parallel F5) + 4 dimensions preserved from Cat C S2503 lineage.

- **§16 Level 0-adjacent candidates for xx99 consolidation** (per Q16 fold): permission-floor semantics + REST↔WS message-contract strictness semantics; xx99 owns consolidation decision.

- **§19 Chris-D-verdict-request handed forward:** R1 Cat B (a)/(b)/(c) selection (with FleetCapabilityRequired mechanism-primitive-viability evidence) + R2 REST↔WS T7 Path A/B/C strictness selection + R3-R5 anchor-update batch (docs/topics/api.md + PLATFORM_INVENTORY §API autoblock + PLATFORM_WHAT_IT_IS §API narrative + platform_architecture_inventory.md §3.22 REVISE + ARCHITECTURE_INDEX updates) + R7 F-B-HIGH-1 + F-B-HIGH-4 cleanup (findings-appendix) + R8 REVIEWER_BLOCKED_PATHS drift documentation + R10 CF-D6 execution (depends_on R2) + R11 F-D-4LAYERSPLIT-1 execution (contingent on R1).

- **CODEOWNERS Cat D surface partial-resolution per Q17 AGREE fold:** backend Cat D surface ~95% explicit-assigned to `@clwest` (7 files explicit + `core/routing.py` + `core/consumers*.py` via `*` fallback); frontend Cat D surface 4-of-9 explicit-assigned (~44%); 5 files UNASSIGNED and deferred to S2600+ per CODEOWNERS lines 8-13 explicit-deferral to Group 2200 T-slot maintainer-decision batch. F-D-OWN-1: partial-scope resolution (backend clarified; frontend deferred); Cat D does NOT declare "closed."

## Post-close residuals for S2599 xx99

Per Chris "commit it" ratification at S2504 close 2026-07-06:

- **Post-commit docs cascade PR** — 4-step cascade (`build_docs_index` + `build_rag_corpus` + `sync_docs_index_to_documents` + `sync_docs_index_to_documents --embed`) + `build_docs_provenance` per `feedback_docs_cascade_at_every_close` + `feedback_cascade_pr_must_include_embed_step`. Verify final chunk count + provenance-json refresh in PR body.

- **ARCHITECTURE_INDEX.md + OPEN_ARCS.md drift preserved from S2501+S2502+S2503 close:** §1.93 S2501 backfill + §1.94 S2502 backfill + §1.95 S2503 registration + §1.96 S2504 registration + v89 → v93 version bump deferred; OPEN_ARCS Group 2500 In-progress row "4 of 6 shipped" → "5 of 6 shipped" + NEXT = S2599 xx99 update deferred. Bundled into docs cascade PR or standalone follow-up at S2599 xx99 close.

- **Deferred anchor-update items to S2599 xx99 close (extends Cat C S2503 deferrals):**
  - `docs/topics/api.md` CREATE (S2500 P-1 + S2501 §19.3 R6 + S2502 §19.3 R7 + S2503 §19.3 R8 + Cat D §19 R3 — recast to xx99-close artifact candidate; Cat D contributions to include: 4-layer permission-floor split narrative + FleetCapabilityRequired mechanism-exemplar reference + REST↔WS T7 joint architecture + 8-dimension maturity table).
  - PLATFORM_INVENTORY §API autoblock CREATE (S2500 §6 P-1 parked item; Cat D denominators: 285 path-list gate entries + 74 class-attr + 838 decorator sites + 3 custom Permission classes + 120 WS route entries + 87 Consumer class definitions + 0% WS envelope conformance rate).
  - PLATFORM_WHAT_IT_IS §API narrative subsection CREATE.
  - `platform_architecture_inventory.md` §3.22 API Layer REVISE with combined Cat A + Cat B + Cat C + Cat D DECLARATION + CONSUMER + CONTRACT + REGISTRY sub-layer evidence.
  - ARCHITECTURE_INDEX Path A/B/C decision matrix pointer + CONSUMER-side Path A/B/C independence note + Cat C α/β/γ intersection model pointer + §16 Level 0 explicit-contract-missing anchor pointer + Cat D α/β/γ + Cat B (a)/(b)/(c) intersection + FleetCapabilityRequired exemplar reference.

## Group 2400 post-arc remediation queue (unchanged carry into S2599 xx99 execution scope)

Per S2499 §8.1 rank-1 co-equal P0 batch preserved. Distribution across arcs unchanged; Group 2500 arc scope Cat D S2504 closed with the following disposition table:

**P0-A platform-wide (execution scope):**
- F-D-CALL-1 803-scale silent-401 remediation — Cat D S2504 CLOSED as design-prep evidence-plane; execution deferred to post-arc T-slot
- F-D-BYPASS-1 79-raw-fetch bypass reconciliation — Cat B S2502 evidence handed; Cat D S2504 post-arc T-slot classification preserved
- F-D-ENVELOPE-1 typed-error-envelope — Cat C S2503 CLOSED as design-prep evidence-plane; Cat D S2504 preserves attach-point evidence at api.ts:43-62 SHAPE-BLIND interceptor RE-VERIFIED IDENTICAL at HEAD
- F-D-BOUNDARY-1 error-boundary framework establishment — Cat C S2503 CLOSED as prerequisite evidence; dual-owned Cat D + Group 2200 post-arc T-slot preserved

**P0-B token lifecycle / security window:**
- F-D-SIDEBAR-1 Sidebar backend-token-revoke fix — Cat C S2503 expected owner Cat D per Rigby Q9 fold; Cat D S2504 preserves post-arc T-slot ownership
- F-C-REFRESH-1 refresh discipline decision-space execution — Cat C S2503 CLOSED as design-prep evidence-plane; execution COUPLED to R1 α/β/γ verdict at xx99
- F-C-VIP-1 VIPInvite.account_expires_at ENFORCEMENT — Cat C S2503 CLOSED with 4-option evidence-candidates + Rigby Q18 selection criteria rubric; execution locus Chris-D-verdict at xx99 OR post-arc dedicated ADR
- F-C-CSD-1 Clear-Site-Data emission on logout — Cat C S2503 CLOSED as design-prep evidence-plane; 3 candidate loci enumerated
- F-C-STORE-1 15-surface × logout-cleanup declared contract execution — Cat C S2503 CLOSED as design-prep evidence-plane

**P0-C endpoint-specific:**
- F-CRIT-1 PURGE_SECRET hardcoded fallback remediation — Group 2400 backlog
- F-BND-4a Unauthenticated bet-placement WRITE remediation — Group 2400 backlog
- **F-B-CRIT-1 Permission-floor implicit-inheritance ~80-90% — Cat D S2504 CLOSED as design-prep evidence-plane** (D4 unique-view denominator UNKNOWN; xx99 decision candidate: fund route→view normalization pass)
- F-B-CRIT-2 Silent-401 SYSTEMIC — Cat C S2503 CLOSED + Cat D S2504 execution owner preserved
- **F-D-WHITELIST-1 Whitelist replacement — Cat D S2504 CLOSED as design-prep evidence-plane** (Rigby Q7 fold `authHandling: 'default' | 'suppress_redirect'` string enum + telemetry PROPOSED PRIMARY γ preserved)

## T-slot follow-on queue (post-Group-2500-close forward look)

- **T3 Group 2600 PA cross-arc handoff bundle** — QUEUED after S2599 xx99 close
- **T4 Group 1700 Observability cross-arc handoff bundle** — QUEUED after Group 2600 close (extended CF-D6 secondary stakeholder from Q9 fold)
- **T5 Group 2300 Mobile (parallel)** — CF-D4 + CF-C4 + Cat A CF-4 + Cat D CF-D6 secondary stakeholder — parallel silent-401 audit for mobile app
- **T6 Group 1600 Content (per Cat C S2503 Rigby SIGN Q11 fold CF-C8)** — Content/Publishing surfaces call auth-protected endpoints; envelope-shape variability leaks into editor/publisher UX
- **Maintainer-decision batch** — CODEOWNERS API-slice discipline + DEAD-CANDIDATE consolidated cleanup (18 modules verified zero-consumer at S2502) + api.ts extraction execution + storageKeys registry + basic vs enhanced logout consolidation (F-C-DUP-1 same-issue lineage + Cat C F6 key-name divergence) + STAFF_REQUIRED_PATHS 2-of-3 phantom cleanup + @authentication_classes([]) 3-file × 6-site stacking cleanup (F-B-HIGH-4 CRITICAL-per-site for auth_views_enhanced.py:560)
- **CODEOWNERS cockpit refinement** — cockpitApi.ts + hooks/cockpitQueries.ts + apiClient.ts + types/cockpit.ts + useWebSocket.ts ownership assignment deferred to S2600+ per CODEOWNERS lines 8-13

## Session count status

- Group 2500 API arc OPEN at S2500 (5 of 6 sessions shipped: S2500 parent + S2501 Cat A + S2502 Cat B + S2503 Cat C + S2504 Cat D)
- Group 2400 Auth arc CLOSED at S2499 (previous arc)
- TWENTY-THIRD-consecutive child-audit template application at S2504
- TWELFTH formal arc pin ACTIVE + PRESERVED through S2504 (`pa-a03b111768464b3f`)
- TWENTY-FIRST consecutive dedicated fresh SIGN pin retirement completed at S2504 Rigby SIGN cycle 1 close (`pa-1aad569644364682` retired)

## Next mission: S2599 xx99 canonical summary

Playbook §11.3 12-section canonical-summary template + §11.3 §10 meta-methodology template + all 4 child findings cross-cutting synthesis (Cat A DECLARATION + Cat B CONSUMER + Cat C CONTRACT-INTERSECTION + Cat D PERMISSION-FLOOR REGISTRY + REST↔WS T7 JOINT) + anchor-update batch preparation + Chris-D-verdict-request evidence rollup for all α/β/γ decision-spaces + Cat B (a)/(b)/(c) + Path A/B/C + Level 0-adjacent-candidates consolidation decision.
