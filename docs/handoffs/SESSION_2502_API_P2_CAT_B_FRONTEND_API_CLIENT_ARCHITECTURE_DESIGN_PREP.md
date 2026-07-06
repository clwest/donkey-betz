---
session: 2502
status: closed (S2502 P2 Cat B Frontend API-Client Architecture Design-Prep child audit — draft written 2026-07-05 post-6-parallel-Explore-sweep + parent-Claude verifier-loop resolving 4 sub-agent conflicts pre-Rigby-SIGN routing, Rigby SIGN cycle 1 COMPLETE via dedicated fresh SIGN isolation pin `pa-1164d91b3dce4b97` — NINETEENTH consecutive dedicated fresh SIGN pin retirement in Research OS after S1399/S1499/S1599/S1699/S1799/S1899/S1999/S2099/S2199/S2299/S2400/S2401/S2402/S2403/S2404/S2499/S2500/S2501 eighteen prior — retired via `session_tool.retire force=true` at cycle close, updated_count=5, retired=true, previously_active=true; 4-batch × 5-Q = 20-Q child-audit cadence per S2201-S2501 ten-consecutive tested pattern ELEVENTH-consecutive application; Rigby overall confidence MED-HIGH; cycle 2 NOT required per Rigby explicit verdict at Q20 close; 20 folds landed pre-Chris-ratification (5 AGREE + 14 STRENGTHEN + 1 Q20 combined verdict-format response) within 15-25-fold S2201-S2501 empirical baseline; Chris "commit it" 2026-07-05 ratified 20 folds wholesale — status flipped `draft` → `active` per playbook §16 draft-first workflow; playbook §11.2 20-section child-audit template TWENTY-FIRST-consecutive application after S1301+S1401+S1501+S1601+S1701+S1801+S1901+S2001+S2101+S2102+S2103+S2104+S2201+S2202+S2203+S2204+S2401+S2402+S2403+S2404+S2501 twenty prior; arc pin `pa-a03b111768464b3f` ACTIVE + PRESERVED through S2502 per playbook §16 arc-standard behavior — no retirement until S2599 xx99 close; 3 of 6 sessions shipped in Group 2500 arc.)
date: 2026-07-05
arc: Research Group 2500 (API — Contract SoT + Silent-401 Downstream Remediation + Session-Lifecycle API Contracts + Per-Endpoint Permission-Floor Registry Design-Prep + REST↔WS T7 Joint 2500+2600) — S2502 P2 Cat B Frontend API-Client Architecture Design-Prep child audit + Rigby SIGN cycle 1 close
head_sha: 548f53a1 (draft-open) → post-commit sha (post-fold + Chris ratification)
---

# Session 2502 — Group 2500 API Cat B Frontend API-Client Architecture Design-Prep + Rigby SIGN Cycle 1 Close

## What shipped

`docs/research/domains/api/2502_api_frontend_client_architecture_design_prep_audit.md` — 20-section child audit per playbook §11.2 TWENTY-FIRST-consecutive application. **Boundary evidence + option-space inventory for the frontend API-client CONSUMER surface at HEAD `548f53a1`.** Cat A S2501 DECLARATION-side handoff (F1 drf-spectacular INSTALLED-CONFIGURED-DECORATED-DISCONNECTED + F6 FOUR co-existing 401 shape families + 96 Serializer / 91 ModelSerializer / 16.2% coverage) → Cat B CONSUMER-side (SHAPE-BLIND interceptor at api.ts:48–62 + 803 consumer surface + 5-session drift-frozen posture + 18 DEAD-CANDIDATE all zero-consumer + 79-raw-fetch bypass parallel-untyped-surface + 0 codegen + 0 AxiosError catches + 0 ErrorBoundary).

**Doc size:** 1,162 lines post-fold / 17,037 words. HEAD-verified baselines at draft-open + post-verifier-loop reconciled.

**Boundary discipline preserved:** Cat B collects + inventories + measures + classifies + defers + proposes evidence-collection; Cat B does NOT prescribe path A/B/C selection, api.ts extraction ordering, DEAD-CANDIDATE removal policy, raw-fetch migration policy, or typed-client codegen framework choice. All "recommendations" in §19 are Chris-D-verdict-request evidence for S2599 xx99 close, NOT directives. Verbs stay `enumerate / inventory / measure / classify / verify / re-verify / defer / propose evidence-collection`.

## Key verifier findings

1. **§14 F1 — Mega-module structural baseline UNCHANGED at HEAD (S2203 §14 F4 RE-VERIFIED, zero-drift 5 sessions).** api.ts 4194 LOC + 93 apiModule + 47 exported interfaces + 856 method defs + 913 total repo grep = 57 direct + 856 defs. All IDENTICAL to S2404 HEAD `31398008` baseline.

2. **§14 F2 — Typed-rate delta is mechanical, NOT progress.** 63/856 = 7.36% at HEAD (vs S2203 63/919 = 6.85%). Numerator unchanged; denominator drift = method cleanup. Relocated out of §1 headline per Rigby SIGN cycle 1 batch 1 Q3 fold.

3. **§14 F3 — SHAPE-BLIND silent-401 interceptor at api.ts:48–62 (KEY VERIFIER FINDING, NEW at Cat B).** Reads only `error.response?.status === 401` and branches solely on `url.includes('/auth/') || url.includes('/login')`. All four S2501 F6 shape families flow through the SAME non-auth reject-and-console.warn branch. Cat C S2503 typed-error-envelope α/β/γ mechanism design-prep MAY depend on shape-normalization landing first as gating prerequisite (assumed / gating hypothesis; not asserted as fact per Rigby SIGN cycle 1 batch 4 Q17 language guardrail). **Severity:** HIGH baseline independent + CRITICAL conditional (if Cat C requires shape-normalization first).

4. **§14 F4 — 18 DEAD-CANDIDATE apiModules ALL zero-consumer at HEAD.** Zero refutations across Agent 3 per-module `\bXxxApi\.` grep excluding api.ts. Persistence across 5 sessions = governance-stall signal (~2,700 LOC dead-weight estimated). Removal remains maintainer-intent-gated per S2203 §14 F6 delete-proof triad.

5. **§14 F5 — 79-raw-fetch bypass IDENTICAL at HEAD (S2404 F-D-BYPASS-1 RE-VERIFIED).** 9.8% of consumer surface operates outside interceptor. Zero token attach + zero 401 catch + zero visibility. 5 sessions no remediation.

6. **§14 F6 — Codegen tooling absence IDENTICAL at HEAD.** 0 of 9 (openapi-typescript / orval / kubb / swagger-codegen / zod / io-ts / valibot / superstruct / yup) in `frontend/package.json`. S2500 §7 anti-scope #7 forbids codegen framework selection at Group 2500; feasibility-only evidence.

7. **§14 F7 — S2404 F-D-OWN-1 CLOSED (partial-scope) at HEAD.** CODEOWNERS EXISTS at repo root (`./CODEOWNERS`, 48 lines) per S2499 AU-D5. api.ts + authStore.ts + Sidebar.tsx + App.tsx declared @clwest at lines 31–34.

8. **§14 F8 — CODEOWNERS coverage gap for cockpit/hooks/types UNASSIGNED at HEAD (NEW finding split from F7 per Rigby SIGN cycle 1 batch 2 Q8 STRENGTHEN).** cockpitApi.ts + apiClient.ts + hooks/cockpitQueries.ts + types/cockpit.ts UNASSIGNED per CODEOWNERS lines 8–13 EXPLICIT deferral to S2600+ per Group 2200 T-slot maintainer-decision batch. Cost-of-deferral note added per Rigby SIGN cycle 1 batch 3 Q15 fold (review latency + drift persistence, without prescription).

## Cross-arc handoff bundle

- **→ Cat C S2503 (typed-error-envelope α/β/γ):** SHAPE-BLIND interceptor at api.ts:48–62 as attach point + 4-shape 401 downstream + zero AxiosError catches + zero ErrorBoundary + 803 consumer surface.
- **→ Cat D S2504 (permission-floor + REST↔WS T7):** 8 identified WS subscription sites (targeted enumeration; full deferred to Cat D) + 2 HYBRID surfaces (pa/conversations + dashboard) + 79-raw-fetch bypass per-site classification (auth-required vs public vs SSE vs streams) + whitelist substring replacement per S2404 §19.1 α/β/γ.
- **→ Group 2200 post-arc T-slot (Rigby SIGN cycle 1 batch 3 Q11 dual-owned R6):** ErrorBoundary framework establishment / global error UX contract. R6 dependency on Cat C typed-envelope mechanism preserved; R6 ownership NOT exclusively Cat C.
- **→ Group 2600 PA (open — S2600+ queued):** assistantApi 22-method cross-cutter + PA control-plane workflow silent-401 exposure + REST↔WS T7 joint co-authorship.
- **→ Group 1700 Observability (closed at S1799 with open envelope-enforcement decision):** request-log ring buffer (api.ts:3990–4048; Session 968) as client-side telemetry origination candidate.
- **→ S2599 xx99:** CONSUMER-side Path A/B/C evidence (INDEPENDENT of DECLARATION-side Path A/B/C per Rigby SIGN cycle 1 batch 3 Q12) + docs/topics/api.md CREATE candidate + PLATFORM_INVENTORY §API autoblock candidate + platform_architecture_inventory §3.22 REVISE.
- **→ Post-arc T-slot maintainer-decision batch:** 18 DEAD-CANDIDATE signoff + api.ts extraction ownership map + CODEOWNERS cockpit refinement (S2600+ per CODEOWNERS deferral) + 79-raw-fetch per-site classification.

## Rigby SIGN cycle 1 record

- **Fresh isolation pin:** `pa-1164d91b3dce4b97` (minted via `session_tool.create_fresh` at S2502 open per playbook §15 SIGN-isolation discipline; NINETEENTH-consecutive dedicated fresh SIGN pin candidate).
- **Cadence:** 4-batch × 5-Q = 20 Q (ELEVENTH-consecutive application after S2201-S2501 ten prior).
- **Verdict:** SIGN-WITH-EDITS at **MED-HIGH confidence**. Cycle 2 NOT required.
- **Tally:** 5 AGREE + 14 STRENGTHEN + 1 Q20 combined verdict-format response = 20 total. All 20 folds landable pre-Chris-ratification per §20.6.2 fold ledger.
- **Retirement:** via `session_tool.retire force=true` at cycle close (updated_count=5, retired=true, previously_active=true — NINETEENTH-consecutive dedicated fresh SIGN pin retirement in Research OS).

**Rigby verdict format (Q20):** Overall MED-HIGH. Most accurate = zero-drift baselines + verifier-loop conflict resolution (unusually well-triangulated for Cat B). Weakest = completeness-implicating enumerations (WS surface) + typed-rate delta framing. Missing area = consolidated Denominator Contract + Sampling Completeness box (folded to §1.1). Overstated maturity = "CRITICAL" if unconditional + "frozen" if implies intent (both folded). Understated maturity = verifier-loop rigor + drift=0 stability signal (folded via §15 label rename to "Observability Risks"). Biggest architectural risk = shape-blind error handling at interceptor layer. Most important next research = exhaustive WS subscription surface enumeration (Cat D T7 joint at S2504) + raw-fetch bypass per-site classification. What Claude got wrong = nothing major (pre-SIGN conflict resolution strengthens trust). What must change before canonical = language guardrails + hedges from the SIGN cycle folds.

## Parent-Claude verifier-loop conflicts resolved pre-Rigby-SIGN

1. **apiModule count = 93** (Agent 1 + Agent 3 + parent grep `^export const \w+Api\s*=` exact match; Agent 6 claim 97 REFUTED).
2. **platformApi method count ≈ 30** spanning lines 3257→3920 = 663 LOC monolithic apiModule (Agent 3; Agent 1 claim 414 REFUTED via direct read).
3. **Direct-consumer call count = 57** = 913 total repo grep − 856 defs in api.ts (Agent 3 + S2404 baseline; Agent 6 claim 87 REFUTED as counting axios-instance imports + method calls together).
4. **CODEOWNERS at HEAD: EXISTS at repo root `./CODEOWNERS`** (48 lines), NOT `.github/CODEOWNERS`. api.ts entry line 31 @clwest. cockpitApi.ts + hooks/ + types/ UNASSIGNED per CODEOWNERS lines 8–13 explicit deferral to S2600+.

## Distinguishing property

- **TWENTY-FIRST-consecutive playbook §11.2 20-section child-audit template application.** Codification framing conditional pending xx99/Chris trigger satisfaction per Rigby SIGN cycle 1 batch 4 Q19 fold.
- **ELEVENTH-consecutive 4-batch × 5-Q cadence application** after S2201-S2501 ten prior.
- **First arc under Research OS to formalize the CONSUMER-side Path A/B/C triad as INDEPENDENT from DECLARATION-side Path A/B/C** (Rigby SIGN cycle 1 batch 3 Q12 STRENGTHEN — explicit independence statement + mixed-combination validity note).
- **First arc under Research OS to identify SHAPE-BLIND interceptor as CONSUMER-side attach point for Cat C typed-envelope adoption** with CONDITIONAL CRITICAL severity language guardrail (Rigby SIGN cycle 1 batch 1 Q2 + batch 4 Q17 folds — prevents Cat B "smuggling" Cat C policy).
- **First arc to split S2404 F-D-OWN-1 CODEOWNERS finding into CLOSED (partial-scope) + NEW (cockpit-gap) child findings** per Rigby SIGN cycle 1 batch 2 Q8 STRENGTHEN (preserves remediation progress signal while surfacing live gap).
- **First arc to introduce two-level boundary-violation frame** (Rigby SIGN cycle 1 batch 3 Q13 STRENGTHEN — implicit-interceptor-contract exception layered on primary missing/undeclared posture).
- **First arc to consolidate rate claims into a §1.1 Denominator Contract + Sampling Completeness box at exec summary** (Rigby SIGN cycle 1 batch 2 Q9 + batch 4 Q20 folds).
- **Rigby SIGN cycle 1 highest-fold-density for Cat B in Group 2500 arc to date** (20 folds on a 20-Q cadence = 100% fold rate — all 20 landable).

## What's next

**S2503 P3 Cat C Error-envelope + refresh + logout API contracts design-prep** per S2500 parent §5 child mission sequence:
- Cat D α/β/γ typed-error-envelope decision space
- F-C-REFRESH-1 refresh endpoint contract (currently MISSING at HEAD)
- F-C-CSD-1 Clear-Site-Data emission spec (currently zero-emission at HEAD)
- F-C-STORE-1 logout cleanup contract via API envelope (14 of 15 client-side persistence surfaces lack DECLARED logout-cleanup per S2403)
- Cat B S2502 SHAPE-BLIND interceptor → shape-normalization prerequisite question
- Arc pin `pa-a03b111768464b3f` PRESERVED through S2503 (TWELFTH formal arc pin under Research OS)
- Fresh SIGN pin to be minted at S2503 open (TWENTIETH-consecutive dedicated fresh SIGN pin candidate)
- Playbook §11.2 template TWENTY-SECOND-consecutive application candidate
- 4-batch × 5-Q Rigby SIGN cycle 1 cadence TWELFTH-consecutive candidate

**Runtime target: 6 sessions.** After S2503 close: **4 of 6 shipped.** S2504 Cat D + S2599 xx99 remaining.

## Residuals (deferred)

- **ARCHITECTURE_INDEX.md §1.93 backfill for S2501** + §1.94 registration for S2502 + version bump v89 → v91 (2-step). S2501 close PR (#2921) did NOT touch ARCHITECTURE_INDEX; drift preserved. Docs cascade PR OR follow-up commit at S2503 close may reconcile.
- **OPEN_ARCS.md Group 2500 In-progress row update** ("1 of 6 shipped" → "3 of 6 shipped"; NEXT = S2503 P3 Cat C). Same drift-preservation pattern as S2501 close. Docs cascade PR or follow-up commit.
- **Post-commit 4-step docs cascade PR** (`build_docs_index` + `build_rag_corpus` + `sync_docs_index_to_documents` + `sync_docs_index_to_documents --embed`) + `build_docs_provenance` per `feedback_docs_cascade_at_every_close` + `feedback_cascade_pr_must_include_embed_step`. Verify final chunk count + provenance-json refresh in PR body.

## Session count status

- Group 2500 API arc OPEN at S2500 (**3 of 6 sessions shipped**: S2500 parent + S2501 Cat A + S2502 Cat B).
- Group 2400 Auth arc CLOSED at S2499 (previous arc).
- TWENTY-FIRST-consecutive child-audit template application at S2502.
- TWELFTH formal arc pin ACTIVE + PRESERVED through S2502 (`pa-a03b111768464b3f`).
- NINETEENTH consecutive dedicated fresh SIGN pin retirement completed at S2502 Rigby SIGN cycle 1 close.
- ELEVENTH-consecutive 4-batch × 5-Q child-audit SIGN cadence application at S2502.
