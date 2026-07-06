# Next Session — Start Here

---

## READ THIS FIRST — S2502 P2 CAT B CLOSED + S2503 P3 CAT C QUEUED

**S2502 P2 Cat B Frontend API-Client Architecture Design-Prep CLOSED 2026-07-05.** Rigby SIGN cycle 1 COMPLETE via dedicated fresh SIGN isolation pin `pa-1164d91b3dce4b97` — **NINETEENTH consecutive dedicated fresh SIGN pin retirement** under Research OS after S1399/S1499/S1599/S1699/S1799/S1899/S1999/S2099/S2199/S2299/S2400/S2401/S2402/S2403/S2404/S2499/S2500/S2501 eighteen prior. Chris "commit it" 2026-07-05 ratified 20 folds wholesale — status flipped `draft` → `active`.

**Arc pin `pa-a03b111768464b3f` ACTIVE + PRESERVED** through S2503 per playbook §16 arc-standard behavior — no retirement until S2599 xx99 close. Runtime target 6 sessions per parent §5 (S2500 + S2501-S2504 + S2599 xx99); **3 of 6 shipped**.

`tools/pa_local.sh:280` points at active arc pin `pa-a03b111768464b3f`. Bare invocation `tools/pa_local.sh "message"` routes into the Group 2500 API arc thread.

### The correct LOCAL invocation
```bash
tools/pa_local.sh "message"
```

Per `.env` PA_API_TOKEN is production; bare `pa_chat.py` against local without local-token override → 401. Always use `tools/pa_local.sh` (sets URL + local token).

## READ THIS SECOND — S2503 P3 CAT C ERROR-ENVELOPE + REFRESH + LOGOUT API CONTRACTS DESIGN-PREP QUEUED

**S2503 P3 Cat C is the NEXT child audit** per S2500 parent §5 child mission sequence Chris-locked "agree all" 2026-07-05. Playbook §11.2 20-section child-audit template TWENTY-SECOND-consecutive application candidate after S1301+S1401+S1501+S1601+S1701+S1801+S1901+S2001+S2101+S2102+S2103+S2104+S2201+S2202+S2203+S2204+S2401+S2402+S2403+S2404+S2501+S2502 twenty-one prior.

- **Arc pin STATUS:** `pa-a03b111768464b3f` ACTIVE + PRESERVED per playbook §16 arc-standard behavior (no retirement until S2599 xx99 close). TWELFTH formal arc pin under Research OS.
- **SIGN pin STATUS:** Fresh SIGN isolation pin to be minted at S2503 open per playbook §15 SIGN-isolation discipline (TWENTIETH consecutive dedicated fresh SIGN pin candidate).

## READ THIS THIRD — S2502 CAT B LOAD-BEARING OUTPUTS FOR S2503

**Cat B boundary evidence handed forward to Cat C (S2503) per S2502 §19.2 + handoff residuals):**

- **SHAPE-BLIND silent-401 interceptor at api.ts:48–62** (KEY VERIFIER FINDING; §14 F3). Reads only `error.response?.status === 401`; branches solely on `url.includes('/auth/') || url.includes('/login')`. All four S2501 F6 shape families flow identically through non-auth reject-and-console.warn branch. **Cat C S2503 typed-error-envelope α/β/γ mechanism design-prep MAY depend on shape-normalization landing first as gating prerequisite** (Cat B assumed/gating hypothesis, not asserted as fact — Rigby SIGN cycle 1 batch 4 Q17 language guardrail).
- **803 consumer surface at HEAD `548f53a1`** (57 direct + 667 hook + 79 raw fetch across 74+31 files). IDENTICAL to S2404 baseline (5-session drift-frozen consumer surface). §14 F1 F5 RE-VERIFIED.
- **4 co-existing 401 shape families (S2501 §14.6 F6 inherited)** — (a) DRF default `{"detail":"..."}` + (b) APIResponseEnvelope + (c) bare DRF dict + (d) non-DRF JsonResponse string. Consumer-side treats identically.
- **Zero AxiosError typed catches + zero ErrorBoundary + zero codegen tooling** (S2404 F-D-ENVELOPE-1 + F-D-BOUNDARY-1 + S2203 §14 F5 RE-VERIFIED IDENTICAL at HEAD across 5 sessions).
- **CockpitApi typed island exemplar** (513 LOC + 96% typed at 52/54 + hand-written 104 types in types/cockpit.ts 820 LOC + 42 React Query hooks in hooks/cockpitQueries.ts inheriting 96% by construction). Sole existence-proof for feasibility of typed-client discipline.
- **CODEOWNERS at repo root (`./CODEOWNERS`, 48 lines).** api.ts + authStore.ts + Sidebar.tsx + App.tsx declared @clwest (lines 31–34). cockpitApi.ts + apiClient.ts + hooks/ + types/ UNASSIGNED per CODEOWNERS lines 8–13 explicit deferral to S2600+.
- **§1.1 Denominator Contract + Sampling Completeness box** and **§1.2 Do Not Misread** exec-summary boxes (Rigby SIGN cycle 1 fold — Cat C should adopt similar pattern for its own rate claims).

## READ THIS FOURTH — LOAD-BEARING INPUTS FOR S2503

**S2503 must consume + re-verify at HEAD:**
- `docs/research/domains/api/2500_api_domain_scoping.md` (primary predecessor — S2500 parent scoping §3.C Cat C mission + acceptance + inheritance)
- `docs/research/domains/api/2501_api_backend_contract_sot_design_prep_audit.md` (S2501 Cat A close — DECLARATION-side + F1 drf-spectacular disconnected + F6 FOUR-shape 401 heterogeneity)
- `docs/research/domains/api/2502_api_frontend_client_architecture_design_prep_audit.md` (S2502 Cat B close — CONSUMER-side boundary evidence for Cat C envelope design; §14 F3 SHAPE-BLIND interceptor + §19.1 R2 shape-normalization decision-point + §19.2 R4 R6)
- `docs/research/domains/auth/2403_session_lifecycle_logout_cleanup_contract_audit.md` (F-C-VIP-1 + F-C-REFRESH-1 + F-C-CSD-1 + F-C-STORE-1 + §19.1 α/β/γ session-lifecycle triad — Cat C S2503 owns downstream)
- `docs/research/domains/auth/2404_frontend_integration_silent_401_systemic_resolution_audit.md` (§19.1 typed-error-envelope α/β/γ decision-space + Cat D PROPOSED PRIMARY γ mechanism per Rigby Q6 fold; γ = mechanism / β = message/UX policy nested inside γ)
- `docs/research/domains/auth/2499_auth_canonical_summary.md` (S2499 xx99 — canonical verdict "ACCRETION with declared-but-unenforced contracts" + 26 cross-arc coordination flags + rank-1 P0 batch)

## READ THIS FIFTH — OUTSTANDING RESIDUALS

### S2502 close residuals

Per Chris "commit it" ratification at S2502 close 2026-07-05:

- **Post-commit docs cascade PR** — 4-step cascade (`build_docs_index` + `build_rag_corpus` + `sync_docs_index_to_documents` + `sync_docs_index_to_documents --embed`) + `build_docs_provenance` per `feedback_docs_cascade_at_every_close` + `feedback_cascade_pr_must_include_embed_step`. Verify final chunk count + provenance-json refresh in PR body.

- **ARCHITECTURE_INDEX.md + OPEN_ARCS.md drift preserved from S2501 close:** §1.93 S2501 backfill + §1.94 S2502 registration + v89 → v91 version bump deferred; OPEN_ARCS Group 2500 In-progress row "1 of 6 shipped" → "3 of 6 shipped" + NEXT = S2503 update deferred. Bundled into docs cascade PR or standalone follow-up at S2503 close.

- **Deferred anchor-update items to S2599 xx99 close:**
  - `docs/topics/api.md` CREATE (S2500 P-1 + S2501 §19.3 R6 + S2502 §19.3 R7 — recast to xx99-close artifact candidate).
  - PLATFORM_INVENTORY §API autoblock CREATE (S2500 §6 P-1 parked item).
  - PLATFORM_WHAT_IT_IS §API narrative subsection CREATE.
  - `platform_architecture_inventory.md` §3.22 API Layer REVISE with combined Cat A + Cat B DECLARATION + CONSUMER sub-layer evidence.
  - ARCHITECTURE_INDEX Path A/B/C decision matrix pointer + CONSUMER-side Path A/B/C independence note.

### Group 2400 post-arc remediation queue (unchanged carry into S2503 execution scope)

Per S2499 §8.1 rank-1 co-equal P0 batch preserved. Distribution across arcs unchanged; Group 2500 arc scope inherits P0-A + P0-B items for design-prep.

**P0-A platform-wide (S2503-S2504 execution scope):**
- F-D-CALL-1 803-scale silent-401 remediation (typed-error-envelope Cat D α/β/γ) — **Cat C P3 primary owner (S2503)**
- F-D-BYPASS-1 79-raw-fetch bypass reconciliation — Cat B S2502 evidence handed; Cat D S2504 post-arc T-slot classification
- F-D-ENVELOPE-1 typed-error-envelope — **Cat C P3 primary owner (S2503)**
- F-D-BOUNDARY-1 error-boundary framework establishment — **dual-owned by Cat C S2503 (typed-envelope prerequisite) + Group 2200 post-arc T-slot (global error UX contract)** per S2502 Rigby SIGN cycle 1 batch 3 Q11 fold

**P0-B token lifecycle / security window (S2503-S2504 execution scope):**
- F-D-SIDEBAR-1 Sidebar backend-token-revoke fix — deferred to post-arc PR post-S2504
- F-C-REFRESH-1 refresh discipline decision-space execution — **Cat C P3 primary owner (S2503)**
- F-C-VIP-1 VIPInvite.account_expires_at ENFORCEMENT — cross-arc gate (Cat C boundary; risk-gate prereq)
- F-C-CSD-1 Clear-Site-Data emission on logout — **Cat C P3 primary owner (S2503)**
- F-C-STORE-1 15-surface × logout-cleanup declared contract execution — **Cat C P3 primary owner (S2503)**

**P0-C endpoint-specific (distributed across arcs; some remain Group 2400 backlog):**
- F-CRIT-1 PURGE_SECRET hardcoded fallback remediation — Group 2400 backlog
- F-BND-4a Unauthenticated bet-placement WRITE remediation — Group 2400 backlog
- F-B-CRIT-1 Permission-floor implicit-inheritance ~80-90% — Cat D P4 primary owner (S2504)
- F-B-CRIT-2 Silent-401 SYSTEMIC (Cat D delivered 803-scale evidence at S2404; Cat B S2502 RE-VERIFIED at HEAD) — Cat C P3 + Cat D P4
- F-D-WHITELIST-1 Whitelist replacement (Cat D α/β/γ × 2 second axis) — Cat C P3 primary owner (S2503)

### T-slot follow-on queue (post-Group-2500-close forward look)

- **T3 Group 2600 PA cross-arc handoff bundle** — QUEUED after Group 2500 close
- **T4 Group 1700 Observability cross-arc handoff bundle** — QUEUED after Group 2600 close
- **T5 Group 2300 Mobile (parallel)** — CF-D4 + CF-C4 + Cat A CF-4 — parallel silent-401 audit for mobile app
- **Maintainer-decision batch** — CODEOWNERS API-slice discipline + DEAD-CANDIDATE consolidated cleanup (18 modules verified zero-consumer at S2502) + api.ts extraction execution + storageKeys registry
- **CODEOWNERS cockpit refinement** — cockpitApi.ts + hooks/cockpitQueries.ts + apiClient.ts + types/cockpit.ts ownership assignment deferred to S2600+ per CODEOWNERS lines 8–13

### Session count status

- Group 2500 API arc OPEN at S2500 (3 of 6 sessions shipped: S2500 parent + S2501 Cat A + S2502 Cat B)
- Group 2400 Auth arc CLOSED at S2499 (previous arc)
- TWENTY-FIRST-consecutive child-audit template application at S2502
- TWELFTH formal arc pin ACTIVE + PRESERVED through S2502 (`pa-a03b111768464b3f`)
- NINETEENTH consecutive dedicated fresh SIGN pin retirement completed at S2502 Rigby SIGN cycle 1 close

## SESSION READY CHECK (before opening S2503 P3 Cat C)

Before drafting the S2503 P3 Cat C child audit:

1. `tools/pa_local.sh "platform_config_tool action=overview"` → verify `service_context: local` + `railway_environment: local` + `database_name: unified_donkey_betz` + `default_llm_provider: openai` under active arc pin `pa-a03b111768464b3f`.
2. `session_tool action=create_fresh` → mint fresh SIGN isolation pin for S2503 SIGN cycle 1 (TWENTIETH consecutive dedicated fresh SIGN pin candidate). Do NOT dispatch S2503 audit content through the SIGN pin until draft is complete; use arc pin `pa-a03b111768464b3f` for interim tool calls.
3. Read `docs/research/DOMAIN_RESEARCH_PLAYBOOK.md` §11.2 20-section child-audit template + §13 six-parallel-Explore-agent sweep contract + §14 verifier-loop discipline + §15 SIGN cadence stage-table.
4. Read `docs/research/domains/api/2500_api_domain_scoping.md` §3.C Cat C mission + §5 sequence + §6 P-1 through P-11 parked items.
5. Read `docs/research/domains/api/2502_api_frontend_client_architecture_design_prep_audit.md` fully — S2502 Cat B close is Cat C's PRIMARY CONSUMER-side predecessor input; SHAPE-BLIND interceptor at api.ts:48-62 is Cat C's central attach-point evidence.
6. Read `docs/research/domains/api/2501_api_backend_contract_sot_design_prep_audit.md` §14.6 F6 FOUR-shape 401 heterogeneity + §19.1 R2 + §19.2 R4.
7. Read `docs/research/domains/auth/2403_session_lifecycle_logout_cleanup_contract_audit.md` §14.2 15-surface storageKeys cleanup + §14.3 21-loci lifecycle-observability + §19.1 α/β/γ + F-C-VIP-1 risk-gate constraint.
8. Read `docs/research/domains/auth/2404_frontend_integration_silent_401_systemic_resolution_audit.md` §19.1 typed-error-envelope α/β/γ decision-space + Cat D PROPOSED PRIMARY γ mechanism per Rigby Q6 fold.
9. **First execution step at S2503 open: RE-VERIFY at HEAD** the SHAPE-BLIND interceptor at api.ts:48-62 + zero-emission Clear-Site-Data (grep on `Clear-Site-Data` = 0 matches at S2404 baseline) + missing refresh endpoint (grep on `refresh|renew_token` in core/urls*.py + core/auth_views*.py) + 14-of-15 no-cleanup surfaces per S2403.
10. Dispatch 6-parallel-Explore-agent sweep per playbook §13 (Agent 1 Models + Persistence — typed-error envelope shape candidates + refresh-token flow model + logout response envelope; Agent 2 Services + Runtime Flows — DRF-level error serialization + Django logout view + Clear-Site-Data emission point candidate + api.ts:48-62 SHAPE-BLIND interceptor re-verify; Agent 3 APIs + Tools + Tasks + Commands — logout endpoint at HEAD + candidate refresh endpoint spec + candidate typed-error envelope endpoints per gated-endpoint-slice; Agent 4 Integrations + Cross-Domain — S2501 F6 4-shape heterogeneity + S2502 F3 SHAPE-BLIND interceptor + S2403 F-C-STORE-1 15-surface + S2404 F-D-CALL-1 803-consumer downstream; Agent 5 Documentation + Prior Research — S2403 α/β/γ + S2404 α/β/γ × 2 + S2499 rank-1 P0 batch + S2502 §19.2 R4 R6; Agent 6 Drift + Debt + Ownership + Maturity — Cat C α/β/γ decision-space maturity + typed-error-envelope adoption feasibility + refresh-endpoint contract absence + Clear-Site-Data absence).
11. Parent-Claude verifier-loop applied per playbook §14 on sub-agent claims pre-draft.
12. Draft the S2503 20-section child audit per playbook §11.2 skeleton.
13. Route to Rigby SIGN cycle 1 via dedicated fresh SIGN isolation pin (NOT arc pin) per playbook §15; 4-batch × 5-Q = 20-Q child-audit cadence per S2201-S2502 eleven-consecutive tested pattern (TWELFTH-consecutive candidate); expected 15-25 folds landable pre-Chris-ratification.
14. Fold SIGN edits; retire SIGN pin at cycle close via `session_tool.retire` (TWENTIETH consecutive dedicated fresh SIGN pin retirement candidate).
15. Present Chris ratification card ("commit it" candidate). Status flips `draft` → `active` on ratification per playbook §16 draft-first workflow.
16. Fresh arc pin `pa-a03b111768464b3f` PRESERVED through S2503 per playbook §16 arc-standard behavior.
17. **After S2503 close: S2504 P4 Cat D Permission-floor registry design-prep + REST↔WS T7 joint next** — playbook §11.2 20-section child-audit template + Rigby SIGN cycle 1 via dedicated fresh SIGN isolation pin + 4-batch × 5-Q cadence per S2201-S2503 twelve-consecutive tested pattern (THIRTEENTH-consecutive candidate).

**S2503 open command (Chris short command):** `Continue research group 2500: Cat C` or `Start S2503` or equivalent invocation matching playbook §21 vocabulary + OS §3.2 deterministic route.
