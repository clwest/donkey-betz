---
session: 2401
status: closed (S2401 P1 Cat A Authentication Surface + Trust Boundaries Audit CLOSED under Group 2400 Auth arc pin `pa-6279ead1714c4630` preserved through S2401 per playbook §16 arc-standard behavior + MC-4 CODIFICATION-CONFIRMED-with-scope-guardrails; SIXTEENTH-consecutive application of playbook §11.2 20-section child-audit template after S1301+S1401+S1501+S1601+S1701+S1801+S1901+S2001+S2101+S2102+S2103+S2104+S2201+S2202+S2203+S2204 prior fifteen; Rigby SIGN cycle 1 SIGN-with-edits at MED confidence (0.74) via dedicated fresh SIGN pin `pa-f0b18d20dbc244ef` retired at cycle close via `session_tool.retire` (updated_count=8, retired=true, previously_active=true — TWELFTH consecutive dedicated fresh SIGN pin retirement in Research OS after 10 xx99 + 1 parent-scoping-light-SIGN + this cycle); 4-batch × 5-Q = 20-Q child-audit cadence per S2201-S2204 five-consecutive tested pattern — SIXTH-consecutive same-cadence application at child-audit stage; MC-10 codification-ready-pending-Chris at 6-arc baseline; 20 folds landed pre-Chris-ratification per §20.7 fold ledger; cycle 2 NOT required per Rigby cycle-1 MED confidence + all folds landable; Chris "commit it" 2026-07-05 ratified drafted-doc post-SIGN cycle 1 folds — status flipped `draft` → `active` per playbook §16 draft-first workflow; ARCHITECTURE_INDEX v83 → v84 with §1.87 registration; OPEN_ARCS Group 2400 In-progress row updated from "S2400 parent scoping (2026-07-05)" to "S2400 parent scoping + S2401 P1 Cat A (2026-07-05) — 2 of 6 shipped"; 00-START-NEXT-SESSION.md overwritten with S2402 P2 Cat B open priorities; Runtime target 6 sessions — **2 of 6 shipped**)
date: 2026-07-05
arc: Research Group 2400 (Auth — Session Lifecycle + Permission Floor + Silent-401 Resolution) — S2401 P1 Cat A first-child audit + arc-preservation cascade
head_commit_before: 798399ec (S2400 arc-open merge PR #2909)
head_commit_after: TBD (S2401 P1 Cat A merge PR TBD)
arc_pin: pa-6279ead1714c4630 (PRESERVED through S2401 per playbook §16 arc-standard behavior + MC-4 CODIFICATION-CONFIRMED-with-scope-guardrails — ELEVENTH formal arc pin under Research OS; retirement at S2499 close; MC-14 CANDIDATE-threshold-satisfied 2-arc arc-pin-preservation-CHECKABLE §16 rule extended to 2+arcs via Group 2200 + Group 2400 = 2 confirming arcs post-S2401 close)
sign_pin: pa-f0b18d20dbc244ef (RETIRED at S2401 SIGN cycle 1 close 2026-07-05 via `session_tool.retire` per playbook §15 SIGN-isolation discipline; updated_count=8, retired=true, previously_active=true — TWELFTH consecutive dedicated fresh SIGN pin retirement in Research OS after S1399/S1499/S1599/S1699/S1799/S1899/S1999/S2099/S2199/S2299 prior ten xx99 + S2400 parent-scoping-light-SIGN + this cycle)
---

# Session 2401 — Group 2400 Cat A — Authentication Surface + Trust Boundaries Audit

## What shipped

**Doc:** `docs/research/domains/auth/2401_authentication_surface_trust_boundaries_audit.md` (1,650 lines post-fold; `status: active` post-Chris-"commit it"-2026-07-05 ratification).

**Playbook §11.2 20-section child-audit template SIXTEENTH-consecutive application** after S1301+S1401+S1501+S1601+S1701+S1801+S1901+S2001+S2101+S2102+S2103+S2104+S2201+S2202+S2203+S2204 prior fifteen.

**HEAD-verified at `798399ec`.** Delivers parent §3.A Cat A expected outputs (a-g): auth mechanism inventory + trust boundary inventory + PUBLIC_PATHS 265-entry audit + VIP TWO-LAYER blast-radius quantification + Fleet permissive-fallback CONTRACT-vs-DRIFT resolution + service-token audit + smoke-test coverage inventory.

**6-parallel-Explore-agent sweep per playbook §13 dispatched.** Agent 1 Models + Persistence + Agent 2 Services + Runtime Flows + Agent 3 APIs + Tools + Tasks + Commands + Agent 4 Integrations + Cross-Domain + Agent 5 Documentation + Prior Research + Agent 6 Drift + Debt + Ownership + Maturity.

**Parent-Claude verifier-loop per playbook §14 caught 1 sub-agent conflict pre-draft:** Agent 2 walked `WebSocketAuthenticationMiddleware` (`core/auth_middleware.py:739-822`) as active middleware; Agent 3 asserted DEFINED BUT NEVER INSTALLED. Parent verifier-loop read `core/asgi.py` + `core/ws_auth_middleware.py` directly; Agent 3 correct — ASGI stack installs `TokenAuthMiddlewareStack` from `ws_auth_middleware.py` (non-enforcing); `WebSocketAuthenticationMiddleware` at `auth_middleware.py:739-822` is dead code at runtime; `REQUIRE_WEBSOCKET_AUTH` at `core/settings.py:625` silently ignored. Third orphan file `core/websocket_auth.py:42` ALSO defines `TokenAuthMiddlewareStack` (dead duplicate; not imported anywhere in the ASGI stack). Corrected in §5 + §14 F-HIGH-2 + §17 F-DUP-1.

**Rigby SIGN cycle 1 result: SIGN-with-edits at MED confidence (0.74)** via dedicated fresh SIGN isolation pin `pa-f0b18d20dbc244ef` (minted at draft-complete via `session_tool.create_fresh` per playbook §15 SIGN-isolation discipline; retired at cycle close via `session_tool.retire`). 4-batch × 5-Q = 20-Q child-audit cadence per S2201-S2204 five-consecutive tested pattern — **SIXTH-consecutive same-cadence application at child-audit stage; MC-10 codification-ready-pending-Chris at 6-arc baseline**. **20 folds landed pre-Chris-ratification** per §20.7 fold ledger. Cycle 2 NOT required per Rigby cycle-1 MED confidence + all folds landable.

## Rigby SIGN cycle 1 20-fold ledger (summary — full detail in doc §20.7)

**Batch 1 (Q1-Q5) — Structural + Maturity + CRITICAL findings:**
- Q1 PARTIAL PASS (missing parts) → §20.3 U11 residual-repo-wide-grep-gap noted
- Q2 FAIL (overstated maturity) → §13 HTTP token auth language refined "WORKING (happy-path) but NOT RELIABLE/PROVEN"
- Q3 PASS (understated maturity Fleet) → §13 Fleet primitive line notes WORKING-by-design + potential-STABLE-with-3-conditions
- Q4 PASS (F-CRIT-1 CRITICAL warranted) → §14.1 framed as compound condition (AllowAny + PUBLIC_PATHS_EXACT bypass + hardcoded fallback)
- Q5 PASS w/ downgrade (F-CRIT-2 severity) → §14.1 refined HIGH-approaching-CRITICAL → HIGH (regression risk of prior production incident fix)

**Batch 2 (Q6-Q10) — Load-bearing findings + Boundary intent:**
- Q6 PASS w/ wording tweak (F-HIGH-1 VIP two-layer) → §14.2 clarifying sentence added "§3.27 v2 'prompt-only' referred primarily to PA-layer control"
- Q7 PASS w/ classification refinement (F-HIGH-2 dead-code) → §14.2 `extraction_candidate` tag added
- Q8 MIXED (F-HIGH-3 vs F-BND-4 severity) → **F-BND-4 promoted HIGH → CRITICAL** with split into F-BND-4a CRITICAL + F-BND-4b HIGH (see retroactive Q16 catch below); F-BND-5 preserved MED
- Q9 PASS w/ caution (F-HIGH-4 Fleet CONTRACT) → §5 Fleet service rows headline "CONTRACT correct, enforcement coverage incomplete"
- Q10 PASS (riskiest finding ranking) → §1 exec summary note "F-BND-4a may outrank F-CRIT-1 if production-reachable"

**Batch 3 (Q11-Q15) — Scope + Anti-scope + Cross-arc:**
- Q11 PASS (intentional separation confusion) → §9.2 CF-2 relabeled OPTIONAL/CROSS-ARC; §16 F-BND-2/F-BND-3 reclassified `mature_primitive` "expected side effects"
- Q12 PROMOTE to HIGH (F-DEC-1 decorator drift) → §14.3 promoted MED → HIGH (68 uses across 9 view files + explicit Session 1171 divergence)
- Q13 PARTIAL PASS (cross-arc flags) → §9.2 + §19.3 added **CF-5 Governance/Authority attestation + CF-6 Frontend 503-fork client-visible contract + CF-7 External Integrations signature-auth adjacency**
- Q14 PARTIAL PASS (CANONICAL blockers) → §12 added blockers **(5) role-field reconciliation + (6) PUBLIC_PATHS DRI + registry governance HARD blocker**
- Q15 FAIL (future-research ranking) → §19.2 rank-1 promoted to co-equal P0s (F-CRIT-1 + F-BND-4a + F-BND-4b + F-CRIT-2 + F-HIGH-2 + F-HIGH-3); rank 2 = PA VIP tool-gate P1 rapid-scoping investigation; rank 3 = threat model

**Batch 4 (Q16-Q20) — Rigor + Anti-scope preservation + POSTURE-DECISION:**
- **Q16 PARTIAL PASS + RETROACTIVE GREP-VERIFY CATCH** — Middleware chain + HEAD SHA verified; count/git-log claims flagged for appendix proof. **CRITICAL retroactive catch: `/api/v1/betting/place/` appears at both `PUBLIC_PATHS` line 198 (Cat A original was 199 — off-by-1) AND `REVIEWER_BLOCKED_PATHS` line 550. Compound drift: anonymous users can bet (PUBLIC_PATHS bypass); logged-in reviewers are blocked (REVIEWER_BLOCKED_PATHS 403). Anonymous-can-bet-reviewers-cannot inversion.** Fold applied: (i) §9.1 line reference `199` → `198,550`; (ii) §14 + §16 F-BND-4 split into F-BND-4a CRITICAL + F-BND-4b HIGH; (iii) §1 headline-finding table updated; (iv) §19.2 rank-1 co-equal-P0 list expanded with F-BND-4b remediation
- Q17 PASS w/ caution (Cat B/C/D anti-scope) → §9.2 CF-3 explicit tag "Permission-floor decision belongs to Cat B / Group 2500"
- Q18 PASS (threat-model anti-scope) → §19.1 blockquote added "This audit is NOT a threat model. It is an inventory intended to seed post-arc ADR / threat-model work"
- Q19 PARTIAL PASS (POSTURE-DECISION defensibility) → §19.1 POSTURE-DECISION #3 rephrased decision-space (not solution-prescriptive) + POSTURE-DECISION #2 refined DEFER → P1/P0-INVESTIGATE + POSTURE-DECISION #1 tagged REQUIRED-BEFORE-CANONICAL
- Q20 PARTIAL PASS (xx99 anchor-updates) → §19.4 (new subsection) expanded to 7 anchor-update recommendations: (a) PLATFORM_INVENTORY §Auth autoblock + (b) PLATFORM_WHAT_IT_IS §Auth subsection + (c) `docs/topics/auth.md` + (d) §3.27 row 27 refresh + (e) ARCHITECTURE_INDEX v-bump at S2499 + (f) OPEN_ARCS S2401-S2404 CLOSED transitions + (g) PUBLIC_PATHS registry DRI anchor

## 5 headline findings post-fold ranking

- **F-CRIT-1 PURGE_SECRET hardcoded fallback** — CRITICAL — `core/views_home.py:259` `os.environ.get('PURGE_SECRET', 'donkey-purge-2026')`; endpoint `/api/home/purge-queue/` in `PUBLIC_PATHS_EXACT` bypasses UnifiedTokenAuthenticationMiddleware. May outrank F-BND-4a if F-BND-4a is not production-reachable. Class: `boundary_violation`.
- **F-BND-4a Unauthenticated bet-placement WRITE** — CRITICAL (Rigby SIGN cycle 1 Q8 fold promoted HIGH → CRITICAL) — `core/auth_middleware.py:198`: `/api/v1/betting/place/` publicly bypassed with comment "Session 563: Bet Tracking (allow anonymous for demo mode)". Money-path bypass; aligns with S2203 §14 F3 money-path treatment. May outrank F-CRIT-1 if production-reachable. Class: `boundary_violation`.
- **F-BND-4b Reviewer inversion** — HIGH (new finding from Rigby SIGN cycle 1 Q16 retroactive grep-verify) — same endpoint at `core/auth_middleware.py:550` in `REVIEWER_BLOCKED_PATHS`. Anonymous-can-bet-reviewers-cannot policy incoherence. Class: `boundary_violation + drift`.
- **F-CRIT-2 Session 1171 503-fork zero smoke-test coverage** — HIGH (Rigby SIGN cycle 1 Q5 fold refined from HIGH-approaching-CRITICAL) — typed exception fork at `core/auth_middleware.py:643-654` (Session 1171 #4 primary fix); no test exercises `TokenValidationInfrastructureError → 503` path. Regression risk on any `validate_token` refactor. Class: `technical_debt`.
- **F-HIGH-1 VIP TWO-LAYER drift** — HIGH — §3.27 baseline "prompt-only, no runtime gate" (lines 2058-2061, 2083-2085) is FALSE at HTTP layer since 2026-03-04 commit `5c8bd585` (three months before S1273 v2 review); hardened to default-deny at `445d0349` 2026-03-29. `VIPReadOnlyMiddleware.__call__` at `core/vip_middleware.py:63-90` is HARD RUNTIME gate registered at `core/settings.py:233`. PA payload layer preserved as SOFT prompt-only (`AssistantProfile.role='vip_viewer'` + `ROLE_PROMPTS` injection). Class: `drift`.
- **F-HIGH-2 WebSocketAuthenticationMiddleware DEAD CODE** — HIGH (Rigby SIGN cycle 1 Q7 fold added `extraction_candidate` tag) — `core/auth_middleware.py:739-822` defined but never installed. `core/asgi.py:25-32` installs `TokenAuthMiddlewareStack` from `core/ws_auth_middleware.py:24-52` (non-enforcing). `REQUIRE_WEBSOCKET_AUTH` at `core/settings.py:625` silently ignored. Class: `dead_code + drift + extraction_candidate`.
- **F-HIGH-3 PUBLIC_PATHS 265-entry accretion** — HIGH — grown 2.5× from ~108 baseline; 8+ confirmed duplicates from Session 688 bulk-add; no gatekeeper. Class: `missing_connection + technical_debt`.
- **F-DEC-1 `@token_auth_required` decorator drift** — HIGH (Rigby SIGN cycle 1 Q12 fold promoted MED → HIGH) — 68 uses across 9 view files; explicit divergence from Session 1171 incident fix. Class: `drift`.

## Trust-boundary rate table (§14.5) — acceptance criterion #6 evidence

14 gate mechanisms × gate type × smoke-test evidence enumerated. **Coverage breakdown: 3 PRESENT + 2 PARTIAL + 9 ABSENT.** Blocker to acceptance criterion #6.

- PRESENT: PA_DB_HEALTH_RPC_TOKEN (tests/test_db_health_rpc.py:34-216), PUBLIC_INTEL_TOKEN (core/tests/test_public_intel_endpoint.py + test_public_changelog_endpoint.py), Fleet HMAC verify (tests/services/test_fleet_auth.py unit tests)
- PARTIAL: PUBLIC_PATHS (3 spot-checks in tests/test_vip_invite_exchange.py:171-191), Fleet HMAC DRF class dispatch integration untested
- ABSENT: STAFF_REQUIRED_PATHS + REVIEWER_BLOCKED_PATHS + REVIEWER_ALLOWED_PATHS + PUBLIC_PATHS_EXACT + OPTIONAL_AUTH_PATHS + VIP write-block (F-HIGH-1) + Fleet exclusive raising path (F-FLEET-1) + Session 1171 503-fork HTTP path (F-CRIT-2) + WebSocket auth 4001 close (F-HIGH-2 dead-code) + PURGE_SECRET gate (F-CRIT-1)

## 7 cross-arc coordination flags (§9.2 + §19.3)

- CF-1 → Group 2600 PA (workspace context contract; PA owns AssistantProfile-keyed resolution)
- CF-2 → Group 1700 Observability (auth event stream — relabeled OPTIONAL/CROSS-ARC per Rigby Q11 fold, not MISSING)
- CF-3 → Group 2500 API (permission-floor decision + PublicIntelTokenAuth custom class registry — Cat B/Group 2500 owns decision per Rigby Q17 fold)
- CF-4 conditional → Group 2300 Mobile (validate-token contract)
- **CF-5 NEW → Group 1900 Governance/Authority** (F-BND-0 boundary attestation)
- **CF-6 NEW → Group 2200 Frontend** (Session 1171 503-fork client-visible contract)
- **CF-7 NEW → External Integrations** (Discord/Stripe/mobile signature-auth adjacency)

## POSTURE-DECISION triad for xx99

- **#1 Threat-model authoring** — DEFER post-arc ADR + REQUIRED-BEFORE-CANONICAL per §12 blocker per Rigby Q19 fold
- **#2 VIP runtime tool-call gate** — P1/P0-INVESTIGATE (Rigby Q19 fold refined DEFER → rapid scoping; Q10 blast-radius-unknown pushes toward investigation)
- **#3 F-CRIT-1 remediation** — P0 post-arc PR + decision-space framing per Rigby Q19 fold ("Eliminate default-secret + remove unauth bypass posture; choose implementation")

## §12 CANONICAL blockers (6 items post-Rigby Q14 fold)

1. No threat-model doc as maintained artifact (§14 F-DOC-2)
2. No CI smoke tests per auth mechanism (§14 F-CRIT-2 + 11-of-14-mechanisms absent)
3. No Chris-ratified session-model contract (Cat C S2403 will surface options)
4. VIP PA-payload prompt-only remains SOFT (§14 F-HIGH-1 layer-2)
5. **NEW**: Role-field reconciliation `platform_role` vs `primary_role` bifurcation (§17 F-DUP-2)
6. **NEW HARD**: PUBLIC_PATHS DRI + registry governance (F-HIGH-3 accretion pattern demonstrates failure mode)

## Cross-arc handoffs delivered

- **delegates_to S2402 P2 Cat B**: Mechanism vocabulary + trust-boundary rate table feed Cat B permission-floor measurement
- **delegates_to S2403 P3 Cat C**: F-VIP-1 (VIPInvite.account_expires_at NOT ENFORCED) + F-TOKEN-1 (authtoken no expiry) + F-SESS-1 (Redis-fallback silent degrade) feed session-model evidence
- **delegates_to S2404 P4 Cat D**: F-CRIT-2 (503-fork zero-coverage) + F-HIGH-2 (WS middleware dead-code) + Session 1171 503-fork client-visible contract per CF-6 feed frontend integration audit
- **delegates_to S2499 xx99**: POSTURE-DECISION triad + 7 cross-arc flags + §19.4 anchor-update batch (7 items)

## Meta-methodology datapoints (playbook §14 evidence discipline)

**FIRST arc under Research OS to split a single finding into 4a + 4b via Rigby SIGN cycle grep-verify.** F-BND-4 compound drift caught retroactively at Batch 4 Q16 — Cat A missed pre-SIGN both (i) line number off-by-1 (199 → 198) and (ii) bet-placement double-registration in REVIEWER_BLOCKED_PATHS at line 550. This pattern validates playbook §14 "grep-verify binary claims before shipping to Rigby" rule + validates the entire SIGN-cycle-as-quality-gate design. MC-15 CANDIDATE (compound drift caught via SIGN-cycle grep-verify) if 2nd application follows.

**MC-10 codification-ready-pending-Chris at 6-arc baseline.** SIXTH-consecutive 4-batch × 5-Q child-audit cadence application (S2201-S2204 five prior + this = 6 consecutive same-cadence). Rigby Q19 fold explicitly flagged as MC-10 extension candidate.

**MC-14 CANDIDATE-threshold-satisfied 2-arc extension.** Arc-pin-preservation-CHECKABLE §16 rule extended to 2+arcs via Group 2200 (arc pin `pa-f7fd5016600f4513` preserved through S2201-S2204) + Group 2400 (arc pin `pa-6279ead1714c4630` preserved through S2401) = 2 confirming arcs post-S2401 close.

## Arc-close cascade

- ✅ Doc `docs/research/domains/auth/2401_authentication_surface_trust_boundaries_audit.md` written + Rigby SIGN cycle 1 SIGN-with-edits + 20 folds landed pre-Chris-ratification + status flipped `draft` → `active`
- ✅ ARCHITECTURE_INDEX v83 → v84 with §1.87 registration + v83 preamble preserved as narrative
- ✅ OPEN_ARCS Group 2400 In-progress row updated with S2401 close narrative (2 of 6 shipped)
- ✅ SIGN pin `pa-f0b18d20dbc244ef` retired via `session_tool.retire` (updated_count=8)
- ✅ 00-START-NEXT-SESSION.md overwritten with S2402 P2 Cat B open priorities
- ⏳ Commit + push + PR (executing)
- ⏳ Post-merge docs cascade (4-step: `build_docs_index` + `build_rag_corpus` + `sync_docs_index_to_documents` + `sync_docs_index_to_documents --embed`) + `build_docs_provenance` per `feedback_docs_cascade_at_every_close`

## Load-bearing evidence at HEAD `798399ec`

- `core/auth_middleware.py` (976 LOC) — UnifiedTokenAuthenticationMiddleware + PUBLIC_PATHS (265) + PUBLIC_PATHS_EXACT (2) + OPTIONAL_AUTH_PATHS (7) + STAFF_REQUIRED_PATHS (3) + REVIEWER_BLOCKED_PATHS (12) + REVIEWER_ALLOWED_PATHS (1) + WebSocketAuthenticationMiddleware DEAD (739-822) + SecurityHeadersMiddleware + RateLimitingMiddleware DISABLED (F-RATE-1) + APILoggingMiddleware + TokenValidationInfrastructureError typed exception (24-33) + token_auth_required decorator (36-81; F-DEC-1)
- `core/vip_middleware.py` (104 LOC) — VIPReadOnlyMiddleware HARD RUNTIME gate + _VIP_ALLOWED_WRITE_PATHS (4) + _VIP_ALLOWED_COCKPIT_PATHS (3) + _VIP_ALLOWED_READ_PREFIXES (11) + _is_vip_user fail-closed
- `core/services/fleet_auth_drf.py` (317 LOC) — FleetSignatureAuthentication (permissive by CONTRACT, docstring 34-38) + FleetSignatureExclusiveAuthentication (raising variant, line 275) + FleetSignatureRequired + FleetCapabilityRequired
- `core/asgi.py` (33 LOC) — ASGI stack installs `TokenAuthMiddlewareStack` from `core/ws_auth_middleware.py:25-32` (verifier-loop key evidence)
- `core/ws_auth_middleware.py` (52 LOC) — ACTIVE non-enforcing WS auth
- `core/websocket_auth.py:42` — ORPHAN dead-duplicate `TokenAuthMiddlewareStack` (F-DUP-1)
- `core/settings.py:217-242` MIDDLEWARE chain (16 items; UnifiedToken=10, VIP=13; RateLimitingMiddleware DISABLED at 230-232) + `:625` REQUIRE_WEBSOCKET_AUTH dead config + `:1105` SESSION_ENGINE cache-backed + `:490-494` Redis-fallback LocMemCache silent-degrade (F-SESS-1)
- `core/views_home.py:259` — F-CRIT-1 PURGE_SECRET hardcoded fallback `'donkey-purge-2026'`

## Session count status

- Group 2400 In-progress at 2 of 6 sessions (S2400 parent scoping + S2401 P1 Cat A shipped)
- Next child = S2402 P2 Cat B Authorization + Permission-Floor Uniformity per parent §5.B
- Next `xx99` at S2499 canonical summary (playbook §11.3 ELEVENTH application per current TENTH baseline)
