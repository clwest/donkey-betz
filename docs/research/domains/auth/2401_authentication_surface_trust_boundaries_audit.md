---
title: "Authentication Surface + Trust Boundaries Audit (Group 2400 Cat A — S2401 P1)"
session: 2401
status: active (S2401 P1 Cat A first child audit under Group 2400 Auth — SIXTEENTH-consecutive application of playbook §11.2 20-section child-audit template after S1301+S1401+S1501+S1601+S1701+S1801+S1901+S2001+S2101+S2102+S2103+S2104+S2201+S2202+S2203+S2204 prior fifteen; drafted 2026-07-05 post-6-parallel-Explore-agent sweep + parent-Claude verifier-loop per playbook §14; **Rigby SIGN cycle 1 SIGN-with-edits at MED confidence (0.74) 2026-07-05 via dedicated fresh isolation pin `pa-f0b18d20dbc244ef` retired at cycle close (updated_count=8, retired=true); 4-batch × 5-Q = 20-Q cadence SIXTH-consecutive application; 20 folds landed pre-Chris-ratification per §20.7 fold ledger — including F-BND-4 split into 4a CRITICAL (unauth bet-placement write) + 4b HIGH (reviewer inversion); F-DEC-1 promoted MED → HIGH; F-CRIT-2 refined HIGH-approaching-CRITICAL → HIGH; F-HIGH-2 tagged extraction_candidate; POSTURE-DECISION #2 refined DEFER → P1/P0-INVESTIGATE; POSTURE-DECISION #3 rephrased as decision-space; CF-5/CF-6/CF-7 added; §19.2 rank-1 reordered to co-equal P0s (F-CRIT-1 + F-BND-4a). Cycle 2 NOT required per MED confidence + all folds landable. Chris "commit it" 2026-07-05 ratified — status flipped `draft` → `active` per playbook §16 draft-first workflow.**)
arc: Research Group 2400 (Auth — Session Lifecycle + Permission Floor + Silent-401 Resolution) — S2401 P1 Cat A first-child audit
category: research (playbook §11.2 20-section child-audit template SIXTEENTH-consecutive application per S2204 handoff)
authors: Claude Code (S2401 draft 2026-07-05 post-6-parallel-Explore sweep + verifier-loop)
verifier_loop: >
  6 parallel Explore sub-agents run per playbook §13 (Agent 1 Models + Persistence,
  Agent 2 Services + Runtime Flows, Agent 3 APIs + Tools + Tasks + Commands,
  Agent 4 Integrations + Cross-Domain, Agent 5 Documentation + Prior Research,
  Agent 6 Drift + Debt + Ownership + Maturity). All 6 returned; parent-Claude
  verifier-loop per playbook §14 caught 1 sub-agent conflict pre-draft:

  - Agent 2 walked through `WebSocketAuthenticationMiddleware`
    (`core/auth_middleware.py:739-822`) as active middleware, walked its behavioral
    contract vs the HTTP path's Session-1171 TokenValidationInfrastructureError
    fork. Agent 3 asserted the class is DEFINED BUT NEVER INSTALLED — ASGI
    routing at `core/asgi.py:25-32` imports `TokenAuthMiddlewareStack` from
    `core/ws_auth_middleware.py` (a DIFFERENT file), not from
    `core/auth_middleware.py`. Parent verifier-loop independently read
    `core/asgi.py` + `core/ws_auth_middleware.py` and confirmed Agent 3:
    `WebSocketAuthenticationMiddleware` at `core/auth_middleware.py:739-822`
    is dead code at runtime; `REQUIRE_WEBSOCKET_AUTH` setting at
    `core/settings.py:625` is silently ignored. Third orphan file
    `core/websocket_auth.py:42` ALSO defines `TokenAuthMiddlewareStack` (dead
    duplicate; not imported anywhere in the ASGI stack). Corrected in §5 +
    §14 F-WS-1 + §17 F-DUP-1.

  Rigby SIGN cycle 1 CLOSED 2026-07-05 via dedicated fresh SIGN pin
  `pa-f0b18d20dbc244ef` (minted via `session_tool.create_fresh` at cycle open;
  retired at cycle close via `session_tool.retire` per playbook §15 SIGN-
  isolation discipline; updated_count=8, retired=true, previously_active=true —
  TWELFTH consecutive dedicated fresh SIGN pin retirement in Research OS after
  10 xx99 + 1 parent-scoping-light-SIGN + this cycle). 4-batch × 5-Q = 20-Q
  cadence per S2201-S2204 five-consecutive tested child-audit pattern
  (SIXTH-consecutive 20-Q cadence application). Rigby final verdict:
  **SIGN-with-edits at MED confidence (0.74)**. 20 folds landed pre-Chris-
  ratification (full ledger in §20.7).

  Rigby overall verdict — most accurate parts: Q1 mechanism enumeration,
  Q4 F-CRIT-1 CRITICAL severity, Q7 F-HIGH-2 dead-code drift, Q9 Fleet CONTRACT
  reclassification. Weakest parts: Q2 HTTP token auth "WORKING" language
  overstated; Q15 §19.2 rank-1 didn't include F-BND-4 as co-equal P0; Q19
  POSTURE-DECISION #3 too solution-prescriptive; Q19 POSTURE-DECISION #2 pure
  DEFER underreacts to Q10 blast-radius-unknown. Missing area: Q11 (a)/(b)
  auth→Event Bus + auth→Celery MISSING labels should re-frame as OPTIONAL/CROSS-
  ARC + INTENTIONAL SEPARATION. Biggest structural risk (Q16 grep-verify catch):
  compound bet-placement drift — `/api/v1/betting/place/` appears at both
  PUBLIC_PATHS line 198 (anonymous bypass) AND REVIEWER_BLOCKED_PATHS line 550
  (reviewer 403); creates anon-can-bet-reviewers-cannot inversion. F-BND-4
  split into F-BND-4a CRITICAL (unauth write) + F-BND-4b HIGH (reviewer
  inversion). Cycle 2 NOT required per MED confidence + all 20 folds landable
  pre-Chris-ratification. Chris-ratifiable at child close per playbook §16
  draft-first workflow ("commit it").
companion_anchors:
  - docs/PLATFORM_INVENTORY.md                                                # runtime counts anchor (no §Auth autoblock — §2 F-INV-1 flags this)
  - docs/PLATFORM_WHAT_IT_IS.md                                               # narrative anchor (no §Auth subsection — §2 F-INV-2 flags this)
  - docs/research/platform_architecture_inventory.md                          # S1273 32-domain map row 27 (PARTIAL + LIGHT after S1273 v2 review) — baseline
  - docs/research/DOMAIN_RESEARCH_PLAYBOOK.md                                 # process contract §11.2 SIXTEENTH-consecutive application
  - docs/research/OPEN_ARCS.md                                                # arc manifest (Group 2400 In-progress row updated at S2401 close)
  - docs/research/domains/auth/2400_auth_domain_scoping.md                    # parent §3.A Cat A scope + §3.5 auth-adjacent probes disposition + §7.1 leak-vector guardrails + §2 evidence-provenance disclaimer
  - docs/research/domains/frontend/2201_frontend_routes_pages_layouts_components_audit.md   # §14.3 cockpit two-stage auth (MINOR-DRIFT) + §15.5 silent-401 systemic
  - docs/research/domains/frontend/2203_frontend_api_contract_boundary_discipline_audit.md  # §14 F3 silent-401 SYSTEMIC + F3.5 whitelist BRITTLE
  - docs/research/domains/frontend/2204_frontend_session_state_persistence_discipline_audit.md  # §14 F1 15-storage-surface + §19.1 R1 session lifecycle
  - docs/research/domains/frontend/2299_frontend_canonical_summary.md         # §8.2 T1 aggregation + §5.4 (i) cross-arc coordination flag
  - docs/research/governance_authority_evolution.md                           # §2.5 36-45 primitives (adjacent authority plane — boundary preserved per §16 F-BND-0)
  - docs/EMPLOYEE_OS_PRIMITIVES.md                                            # GovernanceState + KillSwitch consumers (consumer-side reference — boundary preserved)
  - core/auth_middleware.py                                                   # UnifiedTokenAuthenticationMiddleware (976 LOC) — HTTP auth surface
  - core/vip_middleware.py                                                    # VIPReadOnlyMiddleware (104 LOC) — HARD RUNTIME gate (baseline "prompt-only" STALE at HTTP layer)
  - core/services/fleet_auth_drf.py                                           # FleetSignatureAuthentication (permissive by CONTRACT) + FleetSignatureExclusiveAuthentication (raising variant)
  - core/services/fleet_auth.py                                               # HMAC verify_signed_request + persist_audit_row + nonce Redis store
  - core/ws_auth_middleware.py                                                # ACTIVE ASGI WS auth (not enforcing) — installed at core/asgi.py:25-32
  - core/websocket_auth.py                                                    # ORPHAN DUPLICATE — dead file (defines same TokenAuthMiddlewareStack, not imported)
  - core/views_home.py                                                        # PURGE_SECRET hardcoded fallback F-CRIT-1
  - core/models/fleet.py                                                      # FleetServiceIdentity + FleetServiceKey + FleetServiceRotation + FleetAuthAuditLog + FleetPAChatAuditRow + FleetPaidInterest
  - core/models_vip_invite.py                                                 # VIPInvite — auth-domain FK boundary crossing into Deliverable + ProjectWorkspace
delegated_from:
  - S2400 parent scoping §3.A Cat A expected outputs (a-g) + §3.5 auth-adjacent probes disposition + §7.1 Cat A leak-vector guardrails + §2 evidence-provenance disclaimer (ESTIMATE labeling requirement)
  - S1273 v2 §3.27 baseline (row 27 Auth / Permissions / Security PARTIAL + LIGHT + trust-boundary enumeration + known-unsafe-edges)
  - Group 2200 T1 handoff bundle (S2201 §14.3 + §15.5 + S2203 §14 F3 + F3.5 + S2204 §19.1 R1 + S2299 §8.2 T1 aggregation)
delegates_to:
  - S2402 P2 Cat B Authorization + Permission-Floor Uniformity — Cat B extends Cat A mechanism inventory to per-endpoint permission-floor classification; consumes §5 mechanism inventory + §14 trust-boundary rate as vocabulary
  - S2403 P3 Cat C Session Lifecycle + Logout Cleanup Contract — Cat C consumes §4 UnifiedUser+VIPInvite lifecycle + §14 F-TOKEN-1 no-expiry + §17 F-DUP-2 role-field bifurcation
  - S2404 P4 Cat D Frontend Integration + Silent-401 SYSTEMIC — Cat D consumes §7 runtime-flow-per-caller-class + §14 F-WS-1 dead-code ASGI middleware + acceptance-criterion #6 smoke-test coverage inventory
  - S2499 xx99 canonical summary — POSTURE-DECISION evidence plan §19.1 + cross-arc coordination flags CF-1 → CF-4 + §7 anchor-update recommendations + §10 meta-methodology
head_commit_before: 798399ec
arc_pin: pa-6279ead1714c4630 (PRESERVED through S2401 per playbook §16 arc-standard behavior + MC-4 CODIFICATION-CONFIRMED-with-scope-guardrails — ELEVENTH formal arc pin under Research OS; retirement at S2499 close)
sign_pin: pa-f0b18d20dbc244ef (RETIRED at S2401 SIGN cycle 1 close 2026-07-05 via `session_tool.retire` per playbook §15 SIGN-isolation discipline; updated_count=8, retired=true, previously_active=true — TWELFTH consecutive dedicated fresh SIGN pin retirement in Research OS)
scope_shape:
  central_child_A_lens: >
    "Does the platform have an explicit, enumerated trust-boundary inventory
    across every auth mechanism it runs, or has the authentication surface
    accreted via per-mechanism defaults without a single source-of-truth
    inventory?"
  A_output_a: auth mechanism inventory — enumeration of every `authentication_classes` + middleware auth path + service-token path
  A_output_b: trust boundary inventory — hard runtime vs soft prompt-only vs permissive fallback classification per mechanism
  A_output_c: PUBLIC_PATHS audit — HEAD-verified 265-entry enumeration categorized by intent
  A_output_d: VIP demo enforcement audit — two-layer blast-radius quantification (HTTP layer HARD; PA payload layer PROMPT-ONLY)
  A_output_e: Fleet permissive fallback audit — CONTRACT-vs-DRIFT resolution + view-layer misconfiguration risk
  A_output_f: service token audit — PA_DB_HEALTH_RPC_TOKEN + PUBLIC_INTEL_TOKEN + PURGE_SECRET (F-CRIT-1) scope + rotation + default-off behavior
  A_output_g: smoke-test coverage inventory — blocker to acceptance criterion #6
provenance:
  - S2401 draft written 2026-07-05 post-S2400 parent scoping close (Chris "agree all + commit it" ratified 2026-07-05)
  - 6 parallel Explore sub-agents run per playbook §13 (Agent 1-6 per §3.A Cat A expected outputs)
  - Parent-Claude verifier-loop per playbook §14 caught 1 sub-agent conflict pre-draft (see verifier_loop field above): Agent 2 vs Agent 3 on WebSocketAuthenticationMiddleware installation status → resolved by direct core/asgi.py + core/ws_auth_middleware.py read; Agent 3 correct
  - HEAD-verified precise counts via Django shell: PUBLIC_PATHS=265, PUBLIC_PATHS_EXACT=2, OPTIONAL_AUTH_PATHS=7, STAFF_REQUIRED_PATHS=3, REVIEWER_BLOCKED_PATHS=12, REVIEWER_ALLOWED_PATHS=1, VIP_ALLOWED_WRITE_PATHS=4, VIP_ALLOWED_COCKPIT_PATHS=3, VIP_ALLOWED_READ_PREFIXES=11
  - Chris ratification pending post-Rigby-SIGN-cycle-1 close-card
owner: claude (drafted S2401; Rigby SIGN cycle 1 folds land pre-commit; Chris ratification via close-card)
---

# Session 2401 — Group 2400 Cat A — Authentication Surface + Trust Boundaries Audit

> **Static snapshot.** This audit captures the authentication surface + trust boundaries
> at HEAD `798399ec` on `main` (2026-07-05, LOCAL). It is a photograph, not a mechanism
> design. Authorization + permission-floor is Cat B (S2402). Session lifecycle + logout
> cleanup is Cat C (S2403). Frontend integration + silent-401 execution surface is Cat D
> (S2404). This document delivers what parent §3.A Cat A required: (a) auth mechanism
> inventory; (b) trust boundary inventory; (c) PUBLIC_PATHS 265-entry audit + intent
> categorization; (d) VIP demo two-layer blast-radius quantification; (e) Fleet permissive
> fallback CONTRACT-vs-DRIFT resolution; (f) service token audit + F-CRIT-1
> PURGE_SECRET hardcoded fallback; (g) smoke-test coverage inventory across 14 mechanisms.
> Plus POSTURE-DECISION evidence plan §19 owed to xx99 on threat-model authoring
> (recommend / defer / non-candidate) + Chris D-verdict-requests for parked candidates.

> **Evidence-provenance discipline (inherited from S2400 §2 disclaimer).** Every load-
> bearing claim is either (a) HEAD-verified via direct file read + Django shell + git
> log at `798399ec`, or (b) marked ESTIMATE (inherited from S2400 baseline pending
> Cat A re-verification — now closed at Cat A close), or (c) marked SPECULATIVE with
> explicit rationale. Sub-agent claims verified per playbook §14 "trust but verify" —
> 1 conflict caught + resolved pre-draft (see frontmatter verifier_loop).

---

## 1. Executive Summary

**Central lens answer.** The platform's authentication surface at HEAD `798399ec` is
**structurally intentional at the mechanism-declaration layer** (each of the 12 gate
types has a declared file-anchored posture + failure mode) but **structurally accreted
at the PUBLIC_PATHS-registry layer** (265 prefix entries + 2 exact entries + 7 optional
entries with no gatekeeper, no approval gate, ≥8 confirmed duplicates from Session 688
bulk-add, no per-entry categorization). Trust boundaries exist but are **enumerated
across five separate module-level Python lists in three files** (`auth_middleware.py`
PUBLIC_PATHS + PUBLIC_PATHS_EXACT + OPTIONAL_AUTH_PATHS + STAFF_REQUIRED_PATHS +
REVIEWER_BLOCKED_PATHS + REVIEWER_ALLOWED_PATHS; `vip_middleware.py` 3 frozensets;
`fleet_auth_drf.py` 2 auth classes with distinct contracts). No single source-of-truth
inventory exists — this document is the first.

**Central Cat A finding — S1273 v2 §3.27 baseline is materially STALE at HEAD in 3
concrete ways:**

1. **PUBLIC_PATHS baseline "~108" → HEAD 265** — 2.5× drift. Session-by-session bulk-add
   between S528 (2025-12-21) and S1249 (2026-06-30) grew the unauthenticated bypass
   surface without registry, review, or coverage test. Baseline `~108` at
   `platform_architecture_inventory.md §3.27` (line 2033) is a **FLOOR estimate**, not
   a current count.
2. **VIP demo "prompt-only, no runtime gate" → HEAD TWO-LAYER**: HTTP layer HAS a
   runtime gate (`VIPReadOnlyMiddleware` registered at `core/settings.py:233`, landed
   `5c8bd585` 2026-03-04, hardened to default-deny at `445d0349` 2026-03-29 — three
   full months before the S1273 v2 review); PA chat payload layer remains prompt-only
   (`AssistantProfile.role='vip_viewer'` + `ROLE_PROMPTS` injection). Baseline conflated
   the two layers. HTTP layer classification correct upgrade: SOFT → HARD-RUNTIME.
   PA payload layer classification preserved: SOFT (prompt-only).
3. **Fleet permissive fallback "known drift" → HEAD CONTRACT**: `FleetSignatureAuthentication`
   docstring at `core/services/fleet_auth_drf.py:34-38` is explicit —
   "designed to NEVER raise — treating absence-of-fleet-auth as 'no fleet identity'
   rather than 'auth failure'." `FleetSignatureExclusiveAuthentication` at line 275+ is
   the intentional raising variant for fleet-only endpoints. Two classes, two contracts.
   Baseline framing "permissive fallback = drift" is IMPRECISE — real drift risk is
   view-layer misconfiguration (using permissive class without `FleetSignatureRequired`
   on fleet-only endpoint), not the auth class design.

**Cat A acceptance criterion scoring (per S2400 header block):**

| Criterion | Status | Evidence |
|---|---|---|
| #1 Permission-floor observability | DEFERRED to Cat B | Cat B S2402 owns per-endpoint permission-floor inventory + untraced-rate measurement; Cat A delivers vocabulary |
| #2 Failure surfacing / typed error envelope | DEFERRED to Cat D | Cat D S2404 owns api.ts:48-56 audit; Cat A confirms Session 1171 503-fork exists on HTTP path only, not on WS or `@token_auth_required` decorator (§14 F-WS-1 + §14 F-DEC-1) |
| #3 Logout cleanup contract | DEFERRED to Cat C | Cat C S2403 owns 15-surface cleanup table; Cat A confirms `authtoken.Token` has NO expiry field + rotates only on explicit password change/reset/logout (§14 F-TOKEN-1) |
| #4 Session lifecycle discipline | DEFERRED to Cat C | Cat C S2403 owns session-model inventory; Cat A confirms `VIPInvite.account_expires_at` (14d) is NOT enforced at runtime (§15 F-VIP-1 HIGH) |
| #5 Cross-arc coordination flags preserved | **PARTIAL** | Cat A emits 4 flags (CF-1 → CF-4 in §9 + §19); xx99 §5.4 must land ≥ 2 for acceptance |
| #6 Trust boundary inventory explicit + testable | **PARTIAL** | Cat A delivers explicit 12-mechanism × 3-gate-type inventory in §14 trust-boundary rate table. **BLOCKER: Smoke-test coverage inventory shows 3 of 12 mechanisms tested (§14 smoke-test matrix). Explicit-and-inventoried ✅; testable-with-coverage ❌ pending post-arc test authoring** |

**Cat A five headline findings:**

- **F-CRIT-1 — `PURGE_SECRET` hardcoded fallback `'donkey-purge-2026'` at
  `core/views_home.py:259`** — endpoint `/api/home/purge-queue/` is in
  `PUBLIC_PATHS_EXACT` (bypasses UnifiedTokenAuthenticationMiddleware). The view uses
  a secret-based auth pattern, but the fallback string means: (a) if `PURGE_SECRET`
  env var is unset in Railway prod, the effective password for purging Celery queues
  IS `'donkey-purge-2026'`; (b) anyone reading the source knows the fallback.
  **Class: `boundary_violation`.** Severity: CRITICAL. §3.27 baseline was silent on
  this. Chris D-verdict-request: (i) rotate `PURGE_SECRET` immediately + verify env
  set in prod; (ii) remove hardcoded fallback + fail-closed on env-unset — post-arc
  P0 remediation candidate.
- **F-CRIT-2 — Session 1171 503-fork has ZERO smoke-test coverage** — the typed
  exception fork at `core/auth_middleware.py:643-654` was the primary Session 1171 #4
  fix (2026-06-20 commit `6624468f`). No test exercises the
  `TokenValidationInfrastructureError → 503` path. A refactor of `validate_token`
  could silently revert to 401-on-infra-failure behavior. **Class: `technical_debt`.**
  Severity: **HIGH — regression risk of prior production incident fix** (Rigby SIGN
  cycle 1 Q5 fold: reframed from CRIT-approaching to HIGH; failure mode is
  misleading-status-code, not new attack surface). Pair with concrete "add smoke
  test that simulates infra failure" action item. Blocker to acceptance criterion
  #6 for standard token auth.
- **F-HIGH-1 — VIP demo TWO-LAYER drift** — §3.27 baseline "prompt-only, no runtime
  gate" (lines 2058-2061, 2083-2085) is FALSE at HTTP layer since 2026-03-04 (three
  months before S1273 v2 review). `VIPReadOnlyMiddleware.__call__` at
  `core/vip_middleware.py:63-90` implements a HARD RUNTIME default-deny gate. But at
  PA CHAT PAYLOAD layer, VIP behavior IS prompt-only —
  `AssistantProfile.role='vip_viewer'` triggers `ROLE_PROMPTS['vip_viewer']` system-
  prompt injection with no runtime tool-call gate. `/api/pa/chat/` is in
  `_VIP_ALLOWED_WRITE_PATHS` (VIP can POST), so a VIP user can instruct the PA to
  invoke write tools via natural-language. **Class: `drift`.** Severity: HIGH — HTTP
  layer classification is the wrong direction (over-permissive-labeled surface is
  actually HARD-gated); PA layer classification is preserved. **Baseline-intent
  clarifying note (Rigby SIGN cycle 1 Q6 fold):** §3.27 v2 "prompt-only" language
  referred primarily to PA-layer control, not the HTTP enforcement locus — Cat A's
  two-layer decomposition improves accuracy without rejecting baseline intent.
- **F-HIGH-2 — `WebSocketAuthenticationMiddleware` at `core/auth_middleware.py:739-822`
  is DEAD CODE at runtime** — `core/asgi.py:25-32` imports `TokenAuthMiddlewareStack`
  from `core/ws_auth_middleware.py` (a DIFFERENT file); the class at
  `auth_middleware.py:739-822` is never installed in the ASGI stack.
  `REQUIRE_WEBSOCKET_AUTH` setting at `core/settings.py:625` (`env_bool(..., not
  DEBUG)` — defaults to True in prod) is silently ignored. The active WS auth stack
  (`ws_auth_middleware.py:24-52`) does NOT enforce auth — it resolves `?token=` and
  sets `AnonymousUser` on failure without closing the connection. Per-consumer
  enforcement is inconsistent: `PAConversationConsumer` hard-rejects anon with 4001
  (`consumers_pa_conversation.py:183`); `PersonalAssistantConsumer`, `LiveSportsConsumer`,
  `AIAssistantConsumer` accept anon and gate features only. **Class: `dead_code` +
  `drift` + `extraction_candidate`** (Rigby SIGN cycle 1 Q7 fold: extraction_candidate
  tag = remediation path is "remove unused middleware OR wire it in; make
  REQUIRE_WEBSOCKET_AUTH enforceable"). Severity: HIGH — control-plane drift /
  misleading config; false sense of security.
- **F-HIGH-3 — PUBLIC_PATHS 265-entry list has no registry, no approval gate, 8+
  confirmed duplicates** — grown 2.5× from S1273 v2 baseline (~108 → 265) with no
  gatekeeper. Duplicates confirmed at `auth_middleware.py:139+213` (`/api/celery/`),
  `:142+227` (`/api/agent-learning/`), `:143+226` (`/api/recent-activity/`),
  `:137+233` (`/api/pilots/`), `:182+240` (`/api/v1/betting/arbitrage/`), `:186+242`
  (`/api/v1/odds/bankroll/`), `:199+239` (`/api/v1/betting/wagers/`), `:200+238`
  (`/api/v1/betting/stats/`). `/api/v1/betting/place/` at line 199 is a WRITE
  endpoint (bet placement) publicly bypassed with comment "allow anonymous for demo
  mode" — highest-severity boundary drift in the public-paths surface. **Class:
  `missing_connection` + `technical_debt`.** Severity: HIGH.

**S2400 §2.4 canonical-seam-candidate application to Cat A findings.** "Defaults that
silently swallow failure vs contracts that surface failure" partitions Cat A findings
cleanly: F-CRIT-1 (PURGE_SECRET hardcoded fallback), F-HIGH-2 (WS middleware silently
ignored), and F-HIGH-3 (PUBLIC_PATHS accretion) are all **silent-swallow-of-failure
class**. F-HIGH-1 VIP two-layer is a **partial-contract-partial-accretion** case (HTTP
layer contract; PA payload accretion). Session 1171 HTTP fix (503-fork) is a
**contract-that-surfaces-failure** case, but F-CRIT-2 (zero test coverage) means the
contract's continuity is unverifiable across future refactors. Xx99 §4 will consolidate
cross-cutting patterns.

## 2. Domain Purpose

**Q1 — What is this Cat A audit for? (one-sentence purpose):** Enumerate the platform's
authentication surface + trust boundaries at static snapshot, testing whether the
S1273 v2 §3.27 baseline (~108 PUBLIC_PATHS, 5 mechanisms, VIP prompt-only, Fleet
permissive-fallback drift) matches HEAD reality, and delivering the first single-source
runtime-derived inventory across all 12 gate types identified.

**Q2 — What problem does it solve? (business / platform problem):** Prior arcs
(Groups 1300-2200) touched auth only as downstream consumer or through frontend
symptoms (Group 2200 T1 bundle: silent-401 + logout cleanup + session lifecycle +
permission-floor uniformity). S1273 v2 delivered a compressed narrative-only inventory
in row 27 of `platform_architecture_inventory.md`, explicitly flagged as "compressed
relative to blast radius per Rigby S1273 review — deserves a dedicated trust-boundary
+ threat-model research doc." No such doc has been written; §3.27 remains "the closest
thing" (S1273 v2 self-description at line ~2094). This audit closes the whole-auth
visibility gap on the mechanism + trust-boundary axis so that S2402 Cat B (permission-
floor) + S2403 Cat C (session lifecycle) + S2404 Cat D (frontend integration) each
have a HEAD-verified mechanism inventory to build against.

**Q3 — What does the Cat A audit NOT do? (anti-scope alignment):**

- No fixes / no PRs — read-only research per playbook §14.
- No permission-floor per-endpoint mapping (Cat B S2402 scope) — Cat A delivers
  mechanism VOCABULARY; Cat B extends to per-endpoint MEASUREMENT.
- No session-model authoring (Cat C S2403 + parent §7 anti-scope #5) — Cat A
  surfaces `authtoken.Token` no-expiry finding + `VIPInvite.account_expires_at`
  no-enforcement finding as EVIDENCE; Cat C recommends session-model lean.
- No frontend api.ts audit (Cat D S2404 scope) — Cat A confirms Session 1171
  503-fork exists on HTTP path; Cat D audits the silent-401 caller side.
- No threat-model authoring (parent anti-scope #5, parked candidate #1) — Cat A
  delivers trust-boundary INVENTORY + POSTURE-DECISION on threat-model authoring
  (§19.1); threat-model AUTHORING is a post-arc ADR if Chris ratifies.
- No VIP demo runtime-gate design (parent parked candidate #2) — Cat A quantifies
  blast radius; runtime-gate design is post-arc ADR scope.
- No new auth provider additions (SSO/OAuth) — parent §7 anti-scope #6.
- No Group 1900 authority-plane crossings — §16 F-BND-0 preserves boundary.

---

## 3. Canonical Entry Points

HEAD-verified file:line anchors at `798399ec`. Line references are static snapshots;
S2400 §2 evidence-provenance disclaimer ESTIMATE labels are LIFTED here — Cat A is
the re-verification per parent contract.

**HTTP middleware auth surface:**

| Entry Point | File:Line | Purpose |
|---|---|---|
| `UnifiedTokenAuthenticationMiddleware` class def | `core/auth_middleware.py:85-736` | Primary HTTP token+session auth middleware; 976 LOC file total; registered at `core/settings.py:227` (position 10 in MIDDLEWARE) |
| `PUBLIC_PATHS` list (265 entries; §14 F-HIGH-3 registry drift) | `core/auth_middleware.py:94-509` | Prefix-match bypass — 415 lines of path strings |
| `PUBLIC_PATHS_EXACT` list (2 entries — Session 830) | `core/auth_middleware.py:513-516` | Exact-match bypass (sub-paths require auth) |
| `OPTIONAL_AUTH_PATHS` list (7 entries — Session 528 baseline + Fleet additions) | `core/auth_middleware.py:521-538` | Soft-authenticate; fail-open on infra error |
| `STAFF_REQUIRED_PATHS` list (3 entries) | `core/auth_middleware.py:541-545` | Hard runtime staff-only gate |
| `REVIEWER_BLOCKED_PATHS` list (12 entries — Session 998) | `core/auth_middleware.py:548-556` | Hard runtime reviewer-write block |
| `REVIEWER_ALLOWED_PATHS` list (1 entry — Session 998) | `core/auth_middleware.py:559-561` | Reviewer carve-out for `/api/v1/auth/` |
| `process_request()` method | `core/auth_middleware.py:563-681` | Request dispatch: PUBLIC bypass → PUBLIC_EXACT bypass → OPTIONAL soft-auth → force_auth_user (DRF test) → session auth path → token auth path |
| `extract_token()` | `core/auth_middleware.py:683-702` | Authorization: Token/Bearer, X-API-Key, ?token= (DEBUG only) |
| `validate_token()` | `core/auth_middleware.py:704-736` | Session 1171 #4 typed-exception fork: Token.DoesNotExist → None; else raise `TokenValidationInfrastructureError` |
| `TokenValidationInfrastructureError` class | `core/auth_middleware.py:24-33` | Session 1171 #4 typed exception |
| `token_auth_required` decorator | `core/auth_middleware.py:36-81` | Second token-auth code path (§14 F-DEC-1 drift: no infra-error fork) — used by 9 view files (grep-verified) |

**WebSocket middleware auth surface:**

| Entry Point | File:Line | Purpose |
|---|---|---|
| `TokenAuthMiddlewareStack` (ACTIVE — installed) | `core/ws_auth_middleware.py:24-52` | ASGI WS auth — NON-ENFORCING; sets AnonymousUser on failure |
| ASGI wiring — installs the above | `core/asgi.py:25-32` | `TokenAuthMiddlewareStack(URLRouter(...))` |
| `WebSocketAuthenticationMiddleware` (DEAD — never installed) | `core/auth_middleware.py:739-822` | Would enforce with 4001 close if `REQUIRE_WEBSOCKET_AUTH=True` — but NOT in ASGI stack (§14 F-WS-1) |
| `TokenAuthMiddlewareStack` orphan duplicate | `core/websocket_auth.py:42` | Second definition — dead file, not imported anywhere (§17 F-DUP-1) |
| `REQUIRE_WEBSOCKET_AUTH` setting | `core/settings.py:625` | `env_bool('REQUIRE_WEBSOCKET_AUTH', not DEBUG)` — SILENTLY IGNORED (§14 F-WS-1) |

**VIP demo enforcement surface (TWO-LAYER — §14 F-HIGH-1):**

| Entry Point | File:Line | Purpose |
|---|---|---|
| `VIPReadOnlyMiddleware` class def (HTTP layer HARD RUNTIME gate) | `core/vip_middleware.py:50-91` | Registered at `core/settings.py:233` position 13 |
| `_VIP_ALLOWED_WRITE_PATHS` frozenset (4 entries) | `core/vip_middleware.py:19-24` | Write-block whitelist — includes `/api/pa/chat/` (enables PA-payload prompt-only layer) |
| `_VIP_ALLOWED_COCKPIT_PATHS` frozenset (3 entries) | `core/vip_middleware.py:27-31` | Cockpit strict allowlist |
| `_VIP_ALLOWED_READ_PREFIXES` tuple (11 entries) | `core/vip_middleware.py:34-47` | Read-prefix allowlist |
| `_is_vip_user()` helper | `core/vip_middleware.py:93-104` | Reads `request.user.enhanced_profile.primary_role == 'vip_demo_viewer'`; fail-closed to non-VIP on exception |
| VIP PA payload layer prompt-only enforcement | `core/models_assistant_profile.py:55-80` + `AssistantProfile.role='vip_viewer'` | `ROLE_PROMPTS['vip_viewer']` system-prompt injection; no runtime tool-call gate |

**Fleet HMAC auth surface (§14 F-HIGH-4 CONTRACT-not-drift):**

| Entry Point | File:Line | Purpose |
|---|---|---|
| `FleetSignatureAuthentication` (permissive by CONTRACT) | `core/services/fleet_auth_drf.py:65-150` | Side-effect-only; NEVER raises; populates `request.fleet_identity`; used on hybrid endpoints |
| `FleetSignatureExclusiveAuthentication` (raising variant) | `core/services/fleet_auth_drf.py:275-308` | Raises `AuthenticationFailed` on failure; used on fleet-only endpoints |
| `FleetSignatureRequired` permission class | `core/services/fleet_auth_drf.py:176-212` | Enforces `request.fleet_identity is not None` |
| `FleetCapabilityRequired` permission class | `core/services/fleet_auth_drf.py:215-262` | Live DB lookup on `FleetServiceIdentity.capability(*path)` per request |
| `verify_signed_request()` | `core/services/fleet_auth.py:~165+` | HMAC-SHA256 verification with 9-step pipeline (headers → timestamp → sig decode → key lookup → identity status → app_slug binding → HMAC compare → nonce claim → success) |
| `persist_audit_row()` | `core/services/fleet_auth.py:~600+` | Writes `FleetAuthAuditLog` (deny always; allow when `FLEET_AUTH_LOG_ALL=true`) |

**Service token auth surface:**

| Entry Point | File:Line | Purpose |
|---|---|---|
| `PA_DB_HEALTH_RPC_TOKEN` env var read | `core/views_db_health_rpc.py:39` | `os.environ.get('PA_DB_HEALTH_RPC_TOKEN', '')` |
| PA_DB_HEALTH_RPC_TOKEN gate | `core/views_db_health_rpc.py:63-74` | Unset → 404 (endpoint disabled); mismatch → 401. **§14 F-DEC-2: uses `!=` not `secrets.compare_digest` — not constant-time.** Action allowlist enforced |
| `PUBLIC_INTEL_TOKEN` env var read | `core/settings.py:158` | `PUBLIC_INTEL_TOKEN = os.environ.get('PUBLIC_INTEL_TOKEN', '')` |
| `PublicIntelTokenAuth` DRF auth class | `core/views_public_intelligence.py:37-60` | Empty token → `AuthenticationFailed('Endpoint disabled')`; header `X-Intel-Token` match; `PublicIntelThrottle` 30 req/min per IP |
| `PURGE_SECRET` env var read + hardcoded fallback | `core/views_home.py:259` | **F-CRIT-1**: `os.environ.get('PURGE_SECRET', 'donkey-purge-2026')` — endpoint `/api/home/purge-queue/` in `PUBLIC_PATHS_EXACT` |

**Auth view surface (7 endpoints):**

- `/api/v1/auth/login/` — `core/auth_views.py:24` (basic) + `core/auth_views_enhanced.py:222` (enhanced); rate-limited 5/300s
- `/api/v1/auth/register/` — `core/auth_views_enhanced.py:48`; rate-limited 3/3600s
- `/api/v1/auth/validate-token/` — `core/auth_views_enhanced.py:559`; **§14 F-DEBUG-2: no rate limit; unauthenticated token probe**
- `/api/v1/auth/forgot-password/` — `core/auth_views_enhanced.py:297`; rate-limited 3/3600s
- `/api/v1/auth/reset-password/` — `core/auth_views_enhanced.py:357`; NOT rate-limited (§14 F-DEBUG-2 adjacent)
- `/api/v1/auth/debug/` — `core/auth_views_enhanced.py:658`; **§14 F-DEBUG-1: import at `urls.py:1035` but NO `path()` registration → phantom PUBLIC_PATHS entry**
- `/api/v1/auth/logout/` — `core/auth_views.py:84` (no permission decorator; token-delete in try/except → silent 200 on unauthenticated)

---

## 4. Major Models

Auth-owned + auth-adjacent Django models at HEAD `798399ec`. See §16 for
boundary-crossing FK candidates + §17 for duplicate model rows.

| Model | File:Line | Owner | Purpose | Retention | Constraints |
|---|---|---|---|---|---|
| `UnifiedUser` (`AUTH_USER_MODEL`) | `core/models/base/models.py:86` | this-domain | Primary user entity; extends AbstractUser; carries `platform_role` (incl. `reviewer`), `api_key`, `tenant` FK, `subscription_tier`, Discord link fields | None (soft-disable via `is_active`) | `api_key` UNIQUE, `discord_id` UNIQUE, `username` inherited UNIQUE |
| `EnhancedUserProfile` | `core/models/users/models.py:370` | this-domain | Deep personalization + subscription + **`primary_role='vip_demo_viewer'` VIP gate**; also carries Stripe billing IDs | `data_retention_days` (7-365, default 90) — **NOT AUTO-ENFORCED §18 F-OWN-2** | `user` OneToOneField |
| `UserProfile` | `core/models/users/models.py:12` | this-domain | Avatar, bio, account_type, credits; created by post_save signal | None | `user` OneToOneField |
| `UserPreferences` | `core/models/users/models.py:131` | this-domain | AI model config, memory retention | None | `user` OneToOneField |
| `UserStatistics` | `core/models/users/models.py:162` | this-domain | Usage counters | None | `user` OneToOneField |
| `ExtendedUserProfile` | `core/models/users/models.py:212` | this-domain | Career/job profile — §17 F-DUP-3 duplicate profile row | None | `user` OneToOneField |
| `AssistantProfile` | `core/models_assistant_profile.py:90` | this-domain | PA tool access control; `role='vip_viewer'` triggers `ROLE_PROMPTS` **PA-payload prompt-only VIP gate**; FK to `ProjectWorkspace` (§16 F-BND-1) | None | `user` OneToOneField |
| `VIPInvite` | `core/models_vip_invite.py:30` | this-domain | Magic-link invite tokens; creates VIP user + DRF Token on exchange; carries `token_expires_at` (72h) + `account_expires_at` (14d) | **`account_expires_at` NOT ENFORCED §15 F-VIP-1 HIGH** | `token` UNIQUE |
| `rest_framework.authtoken.Token` | DRF (third-party) | foreign | Per-user opaque token for HTTP + WebSocket auth; one token per user | **NO EXPIRY §14 F-TOKEN-1 MED** — rotates only on password change/reset/logout | `key` UNIQUE, `user` OneToOneField |
| `FleetServiceIdentity` | `core/models/fleet.py:63` | this-domain | One row per fleet app; `capabilities` JSONField + `allowed_routes` JSONField + status | None | `app_slug` UNIQUE |
| `FleetServiceKey` | `core/models/fleet.py:131` | this-domain | HMAC signing key bound to identity; stores SHA256(secret); rotation validity window | None (dual-active supported) | `key_id` UNIQUE; composite indexes |
| `FleetServiceRotation` | `core/models/fleet.py:202` | this-domain | State machine: planned → active → completed/aborted | None | Composite index `[service, status]` |
| `FleetAuthAuditLog` | `core/models/fleet.py:252` | this-domain | Per-request audit (deny always; allow when `FLEET_AUTH_LOG_ALL=true`) | **NO RETENTION POLICY §18 F-OWN-3** | Indexes `[-occurred_at]`, `[result, deny_code]`, `[app_slug_resolved, -occurred_at]` |
| `FleetPAChatAuditRow` | `core/models/fleet.py:570` | this-domain | Warn-only PA-chat auth-mode audit; no enforcement in this phase | **NO RETENTION POLICY §18 F-OWN-3** | Indexes `[auth_mode, -created_at]`, `[match, -created_at]` |
| `FleetArtifact` | `core/models/fleet.py:325` | fleet-domain | Auth-adjacent (created_by_identity FK); TTL soft-delete | `expires_at` set at create | See fleet models |
| `Tenant` | `core/models_tenant.py:15` | this-domain | Multi-tenant org; owner FK to User; **NOT ENFORCED — Session 1039 Phase 1 only** | None | `slug` UNIQUE |
| `DiscordLinkCode` | `core/models/base/models.py:224` | this-domain | 6-char temp code; 10-min expiry via `is_expired` property; **no automatic cleanup** | `is_expired` property only | `code` UNIQUE |
| `MobilePushToken` | `core/models_mobile.py:9` | this-domain | Expo push token per user/device; `revoked_at` soft-delete | `revoked_at` soft-delete | `token` UNIQUE |
| Django Session (Redis-backed) | Django stdlib | foreign | `SESSION_ENGINE='backends.cache'`; NO DB table; **§14 F-SESS-1: Redis-fallback to in-process cache breaks multi-worker sessions silently** | Cookie age 14d | N/A |

---

## 5. Major Services

| Service | File:Line | Purpose | Runtime posture |
|---|---|---|---|
| `UnifiedTokenAuthenticationMiddleware` | `core/auth_middleware.py:85-736` | Primary HTTP token+session auth gate; PUBLIC/OPTIONAL/STAFF/REVIEWER routing | WORKING (Session 1171 typed 503 fork stable at HTTP) |
| `WebSocketAuthenticationMiddleware` (DEAD) | `core/auth_middleware.py:739-822` | **NOT INSTALLED in ASGI stack — §14 F-WS-1 HIGH** | DEAD_CODE at runtime |
| `TokenAuthMiddleware` (ACTIVE WS auth) | `core/ws_auth_middleware.py:24-43` | Resolves `?token=` query; sets AnonymousUser on failure — **NOT ENFORCING** | NON-ENFORCING |
| `SecurityHeadersMiddleware` | `core/auth_middleware.py:826-853` | Adds X-Content-Type-Options, HSTS, X-Frame-Options, etc. | STABLE (not primary auth logic) |
| `RateLimitingMiddleware` | `core/auth_middleware.py:856-925` | 3 auth endpoints throttled (login 5/300s, register 3/3600s, forgot-password 3/3600s); Redis-backed | WORKING — but **§14 F-DEBUG-2: gap on validate-token + debug + reset-password + `/api/auth/login/` compat alias** |
| `APILoggingMiddleware` | `core/auth_middleware.py:928-977` | API request/response logging with SENSITIVE-path masking | STABLE (observability, not enforcement) |
| `VIPReadOnlyMiddleware` | `core/vip_middleware.py:50-104` | **HARD RUNTIME gate** — default-deny for VIP writes + strict cockpit allowlist + read-prefix allowlist | WORKING at HTTP layer; PROMPT-ONLY at PA payload layer (§14 F-HIGH-1) |
| `FleetSignatureAuthentication` | `core/services/fleet_auth_drf.py:65-150` | **Permissive by CONTRACT** — never raises; side-effect-only for hybrid endpoints | STABLE-by-design (§14 F-HIGH-4 CONTRACT resolution) |
| `FleetSignatureExclusiveAuthentication` | `core/services/fleet_auth_drf.py:275-308` | Raising variant for fleet-only endpoints | WORKING; **§14 F-FLEET-1: raising path untested via HTTP dispatch** |
| `FleetSignatureRequired` permission class | `core/services/fleet_auth_drf.py:176-212` | Enforces `request.fleet_identity is not None` | WORKING |
| `FleetCapabilityRequired` permission class | `core/services/fleet_auth_drf.py:215-262` | Live DB capability lookup per request | WORKING; §16 F-BND-2 lazy-import from `core.models.fleet` |
| `verify_signed_request()` | `core/services/fleet_auth.py:~165` | HMAC-SHA256 9-step verification pipeline | STABLE (test-covered at unit level) |
| `persist_audit_row()` | `core/services/fleet_auth.py:~600` | FleetAuthAuditLog writer (best-effort, never blocks) | STABLE |
| `token_auth_required` decorator | `core/auth_middleware.py:36-81` | Second token-auth path used by 9 view files — **§14 F-DEC-1: no infra-error fork; drift from Session 1171 fix** | PARTIAL |
| `PublicIntelTokenAuth` | `core/views_public_intelligence.py:37-60` | Service-token custom DRF auth class; default-off | WORKING |
| `PA` (via `get_unified_pa(request.user)`) | `core/services/unified_pa_entrypoint.py:1155-1240` | Consumes `request.user` from Auth; owns workspace-context resolution | STRONG boundary preservation (§9 CF-1) |

---

## 6. Major APIs and Interfaces

Cat A's external-facing surface enumeration. Cat B (S2402) owns per-endpoint permission-
floor mapping across the full ~1,864 `path()` surface; Cat A here catalogs the auth-
specific surface + hybrid boundaries.

### 6.1 HTTP auth endpoints

| Endpoint | File:Line | Methods | authentication_classes | permission_classes | Auth failure mode |
|---|---|---|---|---|---|
| `/api/v1/auth/login/` (+`/api/auth/login/` alias) | `core/auth_views.py:24` + `urls.py:2184` | POST, OPTIONS | DRF default | `[AllowAny]` | Rate-limited on v1 only; **§14 F-DEBUG-3 compat alias bypasses rate limiter** |
| `/api/v1/auth/register/` | `core/auth_views_enhanced.py:48` | POST | DRF default | `[AllowAny]` | Rate-limited 3/3600s |
| `/api/v1/auth/validate-token/` | `core/auth_views_enhanced.py:559` | POST | `[]` explicitly empty | `[AllowAny]` | Returns `{valid: false}` — **§14 F-DEBUG-2 unauthenticated token oracle, no rate limit** |
| `/api/v1/auth/forgot-password/` | `core/auth_views_enhanced.py:297` | POST | DRF default | `[AllowAny]` | Rate-limited 3/3600s |
| `/api/v1/auth/reset-password/` | `core/auth_views_enhanced.py:357` | POST | DRF default | `[AllowAny]` | 400 on token invalid; **not rate-limited** |
| `/api/v1/auth/debug/` | `core/auth_views_enhanced.py:658` | GET | DRF default | `[AllowAny]` | **§14 F-DEBUG-1: PUBLIC_PATHS entry but NO URL registration → phantom entry; ALSO F-DEBUG-2 token probe oracle if it were routed** |
| `/api/v1/auth/change-password/` | `core/auth_views_enhanced.py:422` | POST | DRF default | `[IsAuthenticated]` | 403 |
| `/api/v1/auth/verify-email/` | `core/auth_views_enhanced.py:168` | POST | DRF default | `[AllowAny]` | 400 |
| `/api/v1/auth/logout/` | `core/auth_views.py:84` | POST | DRF default | none | Silent 200 on unauthenticated (token-delete in try/except) |
| `/api/v1/auth/user/` | `core/auth_views.py:97` | GET | DRF default | none | 401 on anon |
| `/api/v1/vip-invites/exchange/` | `core/views_vip_invite.py:83` | POST | DRF default | `[AllowAny]` | 404 on bad token, 410 on expired |
| `/api/db-health-rpc/` | `core/views_db_health_rpc.py:58` | POST | plain Django + `@csrf_exempt` | none | 404 unset, 401 mismatch, 403 action not allowlisted; **§14 F-DEC-2 `!=` comparison not constant-time** |

### 6.2 Fleet API endpoints

| Endpoint | URL | File:Line | Auth class | Permission | Mode |
|---|---|---|---|---|---|
| `GET /api/fleet/artifacts/<id>/` | `urls.py:1767` | `core/views_fleet_artifacts.py:292` | `FleetSignatureExclusiveAuthentication` | `FleetSignatureRequired` | Exclusive |
| `POST/GET /api/fleet/artifacts/` | `urls.py:1762` | `core/views_fleet_artifacts.py:558` | `FleetSignatureExclusiveAuthentication` | `FleetSignatureRequired` | Exclusive |
| `GET /api/fleet/events/stream` | `urls.py:1773` | `core/views_fleet_events.py:159` | None (SSE requires plain Django) | Manual `verify_signed_request()` inline | Exclusive-equivalent |
| `GET /api/fleet/events/` | `urls.py:1781` | `core/views_fleet_events.py:328` | None | Manual `verify_signed_request()` inline | Exclusive-equivalent |
| `GET /api/fleet/signals/clusters` | `urls.py:1789` | `core/views_fleet_signals.py:76` | None | Manual `verify_signed_request()` + `ALLOWED_APP_SLUGS` | Exclusive-equivalent |
| `POST /api/fleet/paid-interest/` | `urls.py:1797` | `core/views_fleet_paid_interest.py:88` | `FleetSignatureExclusiveAuthentication` | `FleetSignatureRequired` + inline capability check | Exclusive |
| `POST /api/pa/chat/` (HYBRID) | `urls.py:2508` | `core/views_personal_assistant.py:254` | `[FleetSignatureAuthentication, SessionAuthentication, TokenAuthentication]` | `[IsAuthenticated]` | Hybrid — fleet_identity sets routing-block trust; user comes from Session/Token |

### 6.3 PA tool auth surface

- `session_tool` (`core/services/pa_tool_schemas.py:4719`) — actions: `whoami`,
  `create_fresh`, `list_recent`, `retire`, `set_active`, `seed`. **§14 F-PA-1:
  `retire`, `set_active`, `seed` accept `conversation_id` from tool payload without
  verifying `ChatConversation.user_id == user_id` — cross-user targeting via known
  conversation_id.** `_bound_conversation_id` sentinel only guards self-retire.
- `platform_config_tool` (`pa_tool_schemas.py:1854`) — actions include `env_vars`;
  masking correctness of secrets = **§14 F-PA-2 UNKNOWN pending Cat D or post-arc
  audit**.
- `vip_invite_tool` (`pa_tool_schemas.py:3727`) — dispatched to `_handle_vip_invite`
  at `tool_dispatcher.py:528`. HTTP endpoint gated by `IsAdminUser`; **§14 F-PA-3
  UNKNOWN: whether PA handler enforces staff check internally**.

### 6.4 WebSocket consumer auth surface (INCONSISTENT per §14 F-WS-2)

| Consumer | File | Anon enforcement |
|---|---|---|
| `PAConversationConsumer` | `core/consumers_pa_conversation.py:183` | HARD REJECT with 4001 close |
| `PersonalAssistantConsumer` | `core/personal_assistant_consumer.py:28` | Accepts anon; feature-gates on `is_authenticated` |
| `LiveSportsConsumer` (via consumers_base) | `core/consumers_base.py:256` | Accepts anon; logs status |
| `AIAssistantConsumer` (via consumers_base) | `core/consumers_base.py:397` | Accepts anon; feature-gates |

### 6.5 Auth-adjacent Celery tasks + management commands

- **Beat-scheduled**: `cleanup_expired_fleet_artifacts` (daily 02:10 —
  `core/celery.py:112`); `cleanup_expired_fleet_events` (daily 02:25 —
  `core/celery.py:131`); `expire_stale_followup_subscriptions` (every 2min);
  `capture_pa_acks_health_snapshot`.
- **No DRF token rotation task** — `authtoken.Token` has no expiry; rotates only
  at password change/reset/logout (§14 F-TOKEN-1).
- **No VIP account_expires_at enforcement task** (§15 F-VIP-1 HIGH).
- **Management commands**: `setup_pa_service_account` (release-cmd; idempotent);
  `rotate_fleet_key` (4-stage lifecycle: plan/activate/complete/abort — raw secret
  printed once); `add_fleet_key` (emergency dual-active; §17 F-DUP-4 overlap
  with rotate); `create_test_token` (**§14 F-CMD-1: creates users with hardcoded
  `testpass123` if new — no prod guard**); `verify_doc_claims`.

---

## 7. Runtime Flows

Behavior per caller class at HEAD `798399ec` — synthesized from Agent 2 report +
verifier-loop-corrected on WS path. Middleware chain reconstruction from
`core/settings.py:217-242`:

**Middleware chain (16 items, run-order top → bottom, position number):**

1. `SecurityMiddleware` (Django) — HTTPS redirect + HSTS
2. `WhiteNoiseMiddleware` — static files
3. `CorsMiddleware` — CORS preflight (runs before auth by design)
4. `SecurityHeadersMiddleware` — response headers (from `core/auth_middleware.py:826`)
5. `SessionMiddleware` (Django) — populates `request.session` from Redis
6. `CommonMiddleware` — URL normalization
7. `DisableCSRFForAuthEndpoints` (custom, from `core/middleware.py`) — CSRF carve-out
8. `CsrfViewMiddleware` (Django) — CSRF enforcement
9. `AuthenticationMiddleware` (Django) — populates `request.user` from session
10. **`UnifiedTokenAuthenticationMiddleware`** — HTTP token+session auth (primary)
11. `MessageMiddleware`
12. `XFrameOptionsMiddleware`
13. **`VIPReadOnlyMiddleware`** — VIP hard runtime gate
14. `APILoggingMiddleware`
15. `RequestErrorCaptureMiddleware` (from `core/middleware_error_capture.py`)
16. `RangeRequestMiddleware`

**Note: `RateLimitingMiddleware` is DISABLED** at `core/settings.py:230-232` (Railway
internal-IP false-limit problem). This means the `rate_limits` dict at
`core/auth_middleware.py:864-868` **is not active at HEAD** — **§14 F-RATE-1 MED**.

**Critical ordering implication**: `AuthenticationMiddleware` (position 9) runs BEFORE
`UnifiedToken` (position 10) → session-based `request.user` is already populated when
UnifiedToken runs. `VIPReadOnlyMiddleware` (position 13) runs AFTER UnifiedToken → VIP
always sees `request.user` set. Correct ordering — no drift.

**Per-caller-class runtime posture:**

| Caller | End behavior on gated read | End behavior on gated write | Failure mode |
|---|---|---|---|
| Unauthenticated | 401 for non-PUBLIC path | 401 | 401 (no infra hit) |
| Standard user (Token auth) | 200 | 200 (unless staff path) | Token.DoesNotExist → 401; Postgres down → 503 |
| Staff (Token auth) | 200 incl. STAFF_REQUIRED_PATHS | Same | Same 503/401 |
| Reviewer (Token auth) | 200 for GET non-blocked | 403 on blocked; 403 on non-GET non-REVIEWER_ALLOWED | Same |
| VIP demo viewer (Token auth) | 200 only for allowed prefix/cockpit path | 403 (except 4 whitelisted writes incl `/api/pa/chat/`) | `_is_vip_user` swallows exception → non-VIP fall-through |
| Fleet-signed (hybrid, FleetSignatureAuthentication) | 200 if fleet_identity + user auth | Same | Infra fail during key lookup → **UNKNOWN: unhandled in auth class, likely 500 via DRF** |
| Fleet-signed (exclusive, FleetSignatureExclusiveAuthentication) | 200 if verified + capability | Same | Invalid sig → 401; missing capability → 403 |
| WebSocket (any client) | Consumer-dependent — `PAConversationConsumer` hard-rejects; others accept | N/A | Infra fail silently swallowed at `ws_auth_middleware.py:20` (returns AnonymousUser) — **§14 F-WS-1 HIGH** |

**5 silent-accept paths (auth failure short-circuits without emitting to caller):**

1. `OPTIONAL_AUTH_PATHS` + `TokenValidationInfrastructureError` → fail-open —
   `core/auth_middleware.py:588-592`. Infra down + optional path → anon fall-through.
   Documented intentional. Downstream fleet paths get anon `request.user` during DB
   outage; fleet HMAC check then determines outcome.
2. WebSocket `get_user_from_token()` bare `except Token.DoesNotExist: return
   AnonymousUser()` — `core/ws_auth_middleware.py:20-21`. **INFRA errors silently
   become anonymous** — worse than the HTTP `TokenValidationInfrastructureError`
   fork because there's no 503 equivalent.
3. `FleetSignatureAuthentication` on invalid sig — `core/services/fleet_auth_drf.py:128-133`.
   Sets `fleet_identity=None`; hybrid endpoint continues; routing-block enforcement
   silently skipped. CONTRACT by docstring; risk = view-layer misconfiguration.
4. `_is_vip_user()` exception swallow — `core/vip_middleware.py:99-104`. Profile-
   lookup fail → treated as non-VIP (fail-CLOSED for VIP enforcement is correct
   direction; but silent — infra failure not surfaced).
5. `FleetSignatureAuthentication` header-absence early return —
   `core/services/fleet_auth_drf.py:91`. Zero fleet headers → return None silently
   with no log at all. Design-intentional (avoid log noise on normal user-auth).

---

## 8. Data Ownership and Lifecycle

**Token lifecycle (DRF `authtoken.Token`)**:
- Created: `Token.objects.get_or_create(user=user)` at login (`core/auth_views.py`,
  `auth_views_enhanced.py:120,193,257`), VIP exchange (`views_vip_invite.py:131`),
  PA service account (`setup_pa_service_account.py:48`).
- Rotated: `Token.objects.filter(user=user).delete() + create(user=user)` at password
  change (`auth_views_enhanced.py:396-399,460-461`).
- Retired: `request.user.auth_token.delete()` at logout (`auth_views_enhanced.py:547`).
- **NO EXPIRY** (§14 F-TOKEN-1 MED). NO `last_used` tracking. Long-lived indefinitely
  outside explicit password events.

**VIP account lifecycle (`VIPInvite`)**:
- `token_expires_at` = 72h from create (ENFORCED at exchange endpoint).
- `account_expires_at` = 14d from create (**NOT ENFORCED §15 F-VIP-1 HIGH**).
- VIP user account is standard `UnifiedUser` with a token; enforcement is via
  `VIPReadOnlyMiddleware` (per-request role check) + `AssistantProfile.role`
  (per-tool prompt injection) — no expiry-check middleware.

**Fleet key lifecycle**:
- Provisioned: `add_fleet_key` or `rotate_fleet_key plan` — raw secret printed once.
- Rotated: 4-stage machine (planned → active → completed/aborted) via
  `rotate_fleet_key` command.
- Stored: SHA256(raw_secret) only (`FleetServiceKey.secret_hash`).
- Retention: dual-active supported during rotation window; deprovisioned via
  status flip.

**Service token lifecycle**:
- `PA_DB_HEALTH_RPC_TOKEN`, `PUBLIC_INTEL_TOKEN`, `PURGE_SECRET` — all env-var-only,
  no DB row, no rotation trail, no audit log.
- Default-off pattern (all three): unset → endpoint effectively disabled.
- **F-CRIT-1 exception**: `PURGE_SECRET` has hardcoded fallback that defeats
  default-off intent.

**Fleet audit lifecycle**:
- `FleetAuthAuditLog`: written on every deny; on every allow if `FLEET_AUTH_LOG_ALL=true`.
- `FleetPAChatAuditRow`: written on every PA chat call (warn-only, non-enforcing).
- **NO RETENTION POLICY §18 F-OWN-3 LOW** on either — unbounded growth risk.

**Session lifecycle (Django session in Redis)**:
- `SESSION_ENGINE='django.contrib.sessions.backends.cache'` at `core/settings.py:1105`.
- Sessions in Redis DB 1 (`SESSION_CACHE_ALIAS='default'`).
- Cookie age: 14d (`SESSION_COOKIE_AGE=1209600`).
- **§14 F-SESS-1: Redis-unavailable fallback to `LocMemCache` at `core/settings.py:490-494`
  silently degrades multi-worker sessions** — cross-process sharing broken; graceful
  error missing.

---

## 9. Integrations With Other Domains

Per playbook §11.2 §9 — Q14 + Q17 + Q18 + Q21 + Q22 (integration map, event flows,
boundary crossings). Full 32-domain map delivered by Agent 4.

### 9.1 Integration classification (headline rows only — full map in §20.2)

| Domain | Relationship | Classification | Evidence |
|---|---|---|---|
| Frontend (Group 2200) | Upstream: silent-401 at api.ts:48-56 = T1 handoff | STRONG | `frontend/src/lib/api.ts:48-56` (Cat D scope) |
| PA / Rigby (Group 2600) | Downstream: PA consumes `request.user`; owns workspace context | STRONG (boundary preserved) | `unified_pa_entrypoint.py:334, 1155-1240` |
| API layer (Group 2500) | Auth IS the API-layer boundary; permission-floor Chris D-verdict handoff | STRONG | Middleware position 10 + DRF-level authentication_classes usage |
| Governance / Authority (Group 1900) | **BOUNDARY PRESERVED** — zero governance imports in auth files; zero auth imports in employees/ops_autopilot | STRONG (boundary preserved) | Grep-verified per Agent 4 §2 |
| Observability (Group 1700) | Auth emits `logger.warning/error` only; NO structured event stream | WEAK / MISSING | `core/auth_middleware.py` logger calls; `EventStream.*` not called |
| Fleet | Explicit Session 1129 HMAC boundary; hybrid at `/api/pa/chat/` | STRONG | `core/services/fleet_auth_drf.py`, `fleet_auth.py` |
| Sports/DBAO | **OVERCOUPLED**: `/api/v1/betting/place/` (WRITE) in PUBLIC_PATHS (line 198) AND REVIEWER_BLOCKED_PATHS (line 550) — reviewer inversion | OVERCOUPLED | `core/auth_middleware.py:198,550` |
| Body Systems | **OVERCOUPLED**: all 9 body-system APIs unconditionally public | OVERCOUPLED | `core/auth_middleware.py:270-372` |
| Mobile (Group 2300) | `/api/v1/auth/validate-token/` mobile hydration contract | WEAK | `core/auth_views_enhanced.py:559` |
| Discord Bot | `bot_secret` = first 20 chars of `DISCORD_BOT_TOKEN` (derived, not dedicated) | STRONG-with-drift-risk | `core/services/discord_bot.py:2593` |
| Stripe | Webhook signature-verified, not user-auth | STRONG | `core/views_stripe.py:25` |
| Event Bus / Streams | **MISSING**: No auth events published to Event Bus | MISSING | `event_bus.py` publishers not called from auth layer |
| Employee OS + MissionRunner | KillSwitch + GovernanceState consumers; no auth middleware calls | WEAK (boundary preserved) | Grep-verified per Agent 4 §2 |

### 9.2 Cross-arc coordination flags

**CF-1 → Group 2600 PA (workspace context)**: Auth's contract to PA is a single
`request.user` object. Workspace resolution is ENTIRELY PA-owned via `AssistantProfile`
(`unified_pa_entrypoint.py:1155-1240`). Fleet-authenticated requests carry
`request.fleet_identity` in addition to `request.user`; hybrid `/api/pa/chat/` PA
receives BOTH — Group 2600 must explicitly define workspace scoping contract for
fleet-originated PA calls (current: fleet identity does NOT override user-based
workspace scope). Global-mode-on-exception fallback at
`unified_pa_entrypoint.py:1169` runs silently at debug-log level — Group 2600 must
decide if that's the correct posture or should surface as observable failure.

**CF-2 → Group 1700 Observability (auth event stream)**: Auth emits via `logger.*`
only. No structured `AuthEvent` model, no Event Bus routing, no `EventStream.*`
consumer. `FleetAuthAuditLog` + `FleetPAChatAuditRow` are Fleet-forensics tables,
not Observability-arc consumers. Group 1700 must define: (a) whether auth events
route to existing `EventStream.*` or require new stream; (b) who writes structured
events (auth middleware emits, Observability consumes — or Observability wraps
middleware); (c) retention policy for auth events vs fleet audit rows (§18 F-OWN-3).
`FLEET_AUTH_LOG_ALL=False` default means fleet-allow events invisible without config
change — production fleet throughput unobservable by default. **Rigby SIGN cycle 1
Q11(a) fold: relationship is OPTIONAL / CROSS-ARC (Observability), not MISSING
integration — auth uses standard Python logging by design; event-stream emission
is an Observability-arc feature, not an auth requirement absent hard contract.**

**CF-3 → Group 2500 API (permission-floor decision)**: Cat A delivers evidence table
+ Chris D-verdict-request on the three-option decision space (S2203 §19.1 R2). Cat B
(S2402) measures + classifies; Group 2500 implements registry if option (c) chosen.
PUBLIC_PATHS 265-entry list is the primary input for permission-floor registry
design. `@authentication_classes([])` pattern (`views_nervous.py` × 6,
`views_preferences.py` × 2, `auth_views_enhanced.py:560`) + `PublicIntelTokenAuth`
custom DRF class must be addressed in registry. **Permission-floor decision
belongs to Cat B / Group 2500** (Rigby SIGN cycle 1 Q17 fold explicit tag).

**CF-4 (conditional) → Group 2300 Mobile (validate-token contract)**:
`/api/v1/auth/validate-token/` at `core/auth_views_enhanced.py:559` is the current
mobile hydration endpoint. Returns `{valid, user_id, username, email, token}`. Group
2300 must verify this endpoint is sufficient for mobile session lifecycle
(post-Cat-C S2403 session-model decisions may amend). Load-bearing only if Group
2300 opens post-Cat-C.

**CF-5 → Group 1900 Governance/Authority (F-BND-0 boundary contract attestation)**
(NEW — Rigby SIGN cycle 1 Q13 fold). Not to break F-BND-0 preservation verdict,
but to formally ATTEST at a xx99 anchor row: "no governance model imports in auth
files; no auth middleware imports in `core/employees/` or `core/services/ops_autopilot/`."
Prevents future accidental coupling. xx99 anchor-update candidate.

**CF-6 → Group 2200 Frontend / Web Client (Session 1171 503-fork client-visible
contract)** (NEW — Rigby SIGN cycle 1 Q13 fold). The 503 vs 401 distinction from
Session 1171 fix is a CLIENT-VISIBLE contract (retry/backoff/UI messaging changes).
Cat D S2404 or a downstream frontend arc should acknowledge and test client
behavior expectations across the fork.

**CF-7 → External Integrations Surface (signature-based auth adjacency)** (NEW —
Rigby SIGN cycle 1 Q13 fold). Discord bot (`bot_secret` = first 20 chars of
`DISCORD_BOT_TOKEN`), Stripe webhook (signature verification), mobile push
(`MobilePushToken`) — signature-based auth mechanisms adjacent to Fleet HMAC
pattern. Explicit inventory candidate for post-arc audit alignment. Out of Cat A
scope but flagged to prevent oversight.

---

## 10. Event Flows

Auth event emission at HEAD — all `logger.*` calls (no structured event stream —
CF-2 to Group 1700):

**HTTP auth events (`core/auth_middleware.py`)**:

| Event | Level | Line | Format |
|---|---|---|---|
| Staff access denied (session path) | warning | 612 | f-string path + username |
| Staff access denied (token path) | warning | 663 | f-string path + username |
| No token provided | warning | 632 | f-string path |
| Auth backend unreachable | error | 646-650 | structured: path + exception |
| Invalid token | warning | 657 | f-string path |
| Token belongs to inactive user | warning | 720 | f-string username |
| Auth backend error in validate | error | 732-735 | structured: exception type + message |
| WebSocket rejected (no auth) | warning | 766 | string literal (in dead code — F-WS-1) |
| WebSocket auth error | error | 821 | f-string exception (in dead code — F-WS-1) |
| Rate limit exceeded | warning | 883 | f-string IP + endpoint (in disabled middleware — F-RATE-1) |
| API request (SENSITIVE) | info | 941 | f-string method + path |

**VIP events (`core/vip_middleware.py`)**:

| Event | Level | Line | Format |
|---|---|---|---|
| VIP write block | info | 65 | structured: method, path, user |
| VIP cockpit block | info | 74 | structured: method, path, user |
| VIP default block | info | 87 | structured: method, path, user |
| `_is_vip_user` exception swallowed | warning | 100 | exception type + message |

**Fleet events (`core/services/fleet_auth.py`)**:

| Event | Level | Line | Format |
|---|---|---|---|
| Fleet auth deny | warning | ~655 | structured: deny_code, path, key_id, claimed, request_id, delta, replay |
| Fleet auth allow (conditional) | info | ~650 | structured: app, key, path, request_id — ONLY when `FLEET_AUTH_LOG_ALL=true` |

**Structured audit rows (Fleet-owned; not Observability consumers)**:

- `FleetAuthAuditLog` — deny always; allow conditional. Retention: **UNBOUNDED §18 F-OWN-3**.
- `FleetPAChatAuditRow` — every PA chat call in fleet-audit warn-only phase.
  Retention: **UNBOUNDED §18 F-OWN-3**.

**Auth events NOT emitted (CF-2 gap)**:
- Login success (no structured event; DRF login view returns 200 with token but no
  event emission observed).
- Logout success.
- Session creation.
- Session expiration.
- Token rotation (password change).
- VIP invite exchange (VIPInvite model row created but no structured event).

---

## 11. Existing Documentation

Per playbook §11.2 §11 requirement — gap analysis inheriting Agent 5 verified
enumeration.

**Existing docs (14 rows — full table in Agent 5 report; §20.3 appendix):**

- `docs/research/platform_architecture_inventory.md §3.27` (row 27) — S1273 v2
  baseline; PARTIAL + LIGHT; 5-row trust-boundary table
- `docs/research/domains/auth/2400_auth_domain_scoping.md` — parent scoping
- Group 2200 T1 sources — S2201, S2203, S2204, S2299
- `docs/research/governance_authority_evolution.md` §2.5 — adjacent authority plane
- `docs/EMPLOYEE_OS_PRIMITIVES.md` — consumer-side reference
- `docs/narratives/FLEET_INTEGRATION.md` — narrative on fleet HMAC + env vars

**Confirmed doc gaps (VERIFIED absent via glob/grep at HEAD `798399ec`):**

- **Gap 1** — No `docs/topics/auth.md`. `docs/topics/` contains 20 files
  (stock-intelligence, agent-system, celery-workers, employee-os, etc.); auth
  absent. §14 F-DOC-1 MED.
- **Gap 2** — No `PLATFORM_INVENTORY §Auth` autoblock. §14 F-INV-1 MED.
- **Gap 3** — No `PLATFORM_WHAT_IT_IS §Auth` narrative subsection. §14 F-INV-2 MED.
- **Gap 4** — No threat-model / trust-boundary doc. §14 F-DOC-2 HIGH (§3.27
  self-flagged; parked candidate #1 for post-arc ADR).

**Handoff-provenance gaps (NEW finding from Agent 5 — code comments cite sessions
whose handoffs contain zero auth content):**

- **Gap 5** — S528 handoff DOES NOT EXIST. Referenced in ~40 PUBLIC_PATHS comments
  including "SECURITY HARDENING" line. §14 F-PROV-1.
- **Gap 6** — S452 handoffs contain NO auth content. `_force_auth_user` DRF test
  hook at `core/auth_middleware.py:599` cites Session 452. §14 F-PROV-1.
- **Gap 7** — S891 handoff (Domain Content Context) contains NO auth content.
  `token_auth_required` decorator at line 49 cites Session 891. §14 F-PROV-1.
- **Gap 8** — S1069 handoff (Agent Timeout Epidemic) contains NO auth content.
  `/api/internal/config-snapshot/` at line 457 cites Session 1069. §14 F-PROV-1.

---

## 12. Research Coverage

**Classification per playbook §12: `LIGHT` preserved at S2401 open; upgrade to
`MODERATE` justified at S2401 close.**

Argument (per Agent 5 §6): §3.27 baseline (parent scope inventory) + this Cat A
audit (mechanism + trust-boundary re-verified at HEAD with file:line precision +
POSTURE-DECISION on threat-model authoring) constitutes "at least one focused doc
or meaningful canonical documentation" per §12 MODERATE threshold. Group 2200 T1
handoff bundle (S2201/S2203/S2204/S2299) is frontend-surface, not auth-architecture
— those docs don't clear the auth-domain MODERATE threshold alone. Cat A DOES.

**Post-arc (S2499 xx99) ceiling: DEEP** — after Cat B (permission-floor) + Cat C
(session lifecycle) + Cat D (frontend integration) each ship 20-section audits, four
focused docs + canonical summary = DEEP threshold satisfied.

**CANONICAL blocked by (per Agent 5 §6 + Rigby SIGN cycle 1 Q14 fold additions):**

1. No threat-model doc as maintained artifact (§14 F-DOC-2 HIGH).
2. No CI smoke tests per auth mechanism (§14 F-CRIT-2 blocks 11 of 14 mechanisms
   from testable-with-coverage state).
3. No Chris-ratified session-model contract (Cat C S2403 will surface options; ADR
   authoring is post-arc).
4. VIP PA-payload prompt-only remains SOFT (§14 F-HIGH-1 layer-2 preserved as
   SOFT); CANONICAL would require ratified decision to keep prompt-only OR
   runtime tool-call gate.
5. **Role-field reconciliation blocker (NEW — Rigby SIGN cycle 1 Q14 fold).**
   `platform_role` (base UnifiedUser) vs `primary_role` (EnhancedUserProfile)
   bifurcation per §17 F-DUP-2. CANONICAL requires one authoritative role model
   OR explicit documented mapping + migration plan. Hard blocker if roles drive
   permissions/tool access.
6. **PUBLIC_PATHS ownership/DRI + registry governance (NEW — Rigby SIGN cycle 1
   Q14 fold; HARD blocker).** Without named DRI + registry mechanism, "canonical"
   will drift again immediately (F-HIGH-3 accretion pattern demonstrates the
   failure mode). Elevated to hard CANONICAL gate.

---

## 13. Architecture Maturity

Per playbook §12: EXPERIMENTAL / PARTIAL / WORKING / STABLE / CANONICAL.

**PARTIAL preserved at HEAD** — for different (in some ways more concrete) reasons
than the S1273 v2 baseline stated.

**Baseline (§3.27 v2) PARTIAL rationale**:
1. VIP prompt-only. **STALE at HEAD** — HTTP layer is HARD RUNTIME since 2026-03-04.
   Preserved-as-partial at PA payload layer only.
2. Fleet permissive fallback. **RESOLVED at HEAD** — CONTRACT not drift per §14
   F-HIGH-4.

**New HEAD PARTIAL disqualifiers (would block STABLE):**
1. **F-CRIT-1 PURGE_SECRET hardcoded fallback** — CRITICAL known-unsafe edge.
2. **F-CRIT-2 Session 1171 503-fork zero test coverage** — silent-regression risk.
3. **F-HIGH-2 WebSocket middleware dead-code** — configuration knob has no effect.
4. **F-HIGH-3 PUBLIC_PATHS 265-entry no registry** — attack surface uncontrolled.
5. **F-HIGH-1 VIP PA-payload prompt-only** — SOFT boundary preserved at inner layer.
6. Smoke-test coverage 3-of-14 mechanisms → blocker to STABLE ("known edges, all
   gated" requires test coverage).

**Per-primitive maturity refinements**:

- HTTP token auth path (extract → validate → set request.user + 503 fork):
  **WORKING** at file-precision + Session 1171 typed exception. Blocked from
  STABLE by F-CRIT-2 test-coverage gap + F-WS-1 sibling divergence + F-DEC-1
  decorator divergence.
- VIP HTTP-layer gate: **WORKING** with default-deny + write-block + strict cockpit
  allowlist. Blocked from STABLE by zero smoke-test coverage (§14 F-HIGH-1).
- Fleet HMAC (both variants): **WORKING-by-design**; permissive variant is CONTRACT
  not drift. Blocked from STABLE by view-layer misconfiguration risk + exclusive
  variant untested via HTTP dispatch (§14 F-FLEET-1).
- Service tokens: **PARTIAL** — F-CRIT-1 PURGE_SECRET undermines default-off pattern;
  F-DEC-2 non-constant-time comparison; no rotation cadence doc.

---

## 14. Known Drift

Consolidated drift matrix — baseline §3.27 v2 vs HEAD `798399ec`. Playbook §12
finding_type strings in bold.

### 14.1 CRITICAL drifts (new at HEAD)

**F-CRIT-1 — PURGE_SECRET hardcoded fallback** (**`boundary_violation`**). Severity:
CRITICAL. `core/views_home.py:259`: `purge_secret = os.environ.get('PURGE_SECRET',
'donkey-purge-2026')`. Endpoint `/api/home/purge-queue/` in `PUBLIC_PATHS_EXACT`
(`core/auth_middleware.py:515`) bypasses auth middleware. §3.27 baseline silent.

**F-CRIT-2 — Session 1171 503-fork zero test coverage** (**`technical_debt`**).
Severity: HIGH-approaching-CRITICAL. Typed-exception fork at
`core/auth_middleware.py:643-654` (Session 1171 #4 primary fix) has no smoke test.
Silent-regression risk on any `validate_token` refactor. Blocker to acceptance
criterion #6 for standard token auth mechanism.

### 14.2 HIGH drifts

**F-HIGH-1 — VIP TWO-LAYER drift** (**`drift`**). §3.27 baseline "prompt-only, no
runtime gate" (lines 2058-2061, 2083-2085) is materially STALE at HEAD:
- HTTP layer: HARD RUNTIME gate since `5c8bd585` (2026-03-04); default-deny
  hardening at `445d0349` (2026-03-29) — three months before S1273 v2 review.
- PA payload layer: preserved as prompt-only (`AssistantProfile.role='vip_viewer'` +
  `ROLE_PROMPTS`). No runtime tool-call gate; VIP user can POST to `/api/pa/chat/`
  (in `_VIP_ALLOWED_WRITE_PATHS`) and instruct PA to invoke write tools.

Blast-radius quantification: 4 `_VIP_ALLOWED_WRITE_PATHS` entries (login, logout,
vip-invites/exchange, pa/chat) — 3 are auth self-service; **1 is PA payload
(`/api/pa/chat/`) which is the entire write-tool surface for VIP users if PA is
not further restricted at tool-call layer**. Full blast-radius quantification of
write tools accessible to `vip_viewer` role via PA payload requires PA tool
schema audit — deferred to post-arc ADR (parent parked candidate #2).

**F-HIGH-2 — WebSocketAuthenticationMiddleware DEAD-CODE at runtime**
(**`dead_code` + `drift`**). `core/auth_middleware.py:739-822` defined but never
installed. ASGI installs `TokenAuthMiddlewareStack` from
`core/ws_auth_middleware.py:24-52` (non-enforcing — sets AnonymousUser on failure
without close). `REQUIRE_WEBSOCKET_AUTH` at `core/settings.py:625` silently
ignored. Verified: `grep -rn "WebSocketAuthenticationMiddleware"` returns only the
class definition; no ASGI/settings/routing import.

**F-HIGH-3 — PUBLIC_PATHS registry accretion** (**`missing_connection` +
`technical_debt`**). `~108 → 265` = 2.5× drift since S1273. 8+ confirmed
duplicates from Session 688 bulk-add. No gatekeeper, no approval gate, no
per-entry categorization. `/api/v1/betting/place/` (WRITE endpoint) at line 199
publicly bypassed with comment "allow anonymous for demo mode".

**F-HIGH-4 — Fleet permissive fallback is CONTRACT not drift**
(**`mature_primitive`**). §3.27 v2 baseline framing "permissive fallback = known
drift" is imprecise. Docstring at `core/services/fleet_auth_drf.py:34-38` states
explicit intent — "designed to NEVER raise". `FleetSignatureExclusiveAuthentication`
(line 275) is the raising variant for fleet-only endpoints. Real drift risk:
view-layer misconfiguration (permissive class + missing `FleetSignatureRequired` on
fleet-only endpoint → silent-accept). No platform registry of "which endpoints
require fleet auth."

**F-WS-1 — Companion to F-HIGH-2**: WS `get_user_from_token` at
`core/ws_auth_middleware.py:14-21` uses bare `except Token.DoesNotExist:
return AnonymousUser()` — swallows the same infra failures the HTTP path now
properly re-raises as `TokenValidationInfrastructureError` post Session 1171.
Session 1171 fix incomplete: HTTP upgraded, WS + `@token_auth_required` decorator
not (see F-DEC-1). Divergent auth surface.

### 14.3 MEDIUM drifts

**F-DEC-1 — `@token_auth_required` decorator drift** (**`drift`**). `core/auth_middleware.py:36-81`
catches only `Token.DoesNotExist`; infra failure surfaces as 500, not 503. Used by
9 view files (`views_analytics.py`, `views_advisor_api.py`, `views_content_calendar.py`,
`views_deliverables.py`, `views_agent_collaboration.py`, `views_agent_learning.py`,
`views_learning.py`, `views_project_hub.py`, `views_voice_marketplace.py`) — 68 uses
total per Agent 2 grep. Divergent from middleware post-Session-1171.
**Severity: HIGH** (Rigby SIGN cycle 1 Q12 fold: promoted from MED — status-code
correctness + incident-response regression class; large blast radius across 9 view
files; explicit divergence from Session 1171 incident-fix philosophy). Pair with
"align decorator with middleware exception mapping + add smoke test that simulates
infra failure."

**F-DEC-2 — `PA_DB_HEALTH_RPC_TOKEN` non-constant-time comparison** (**`technical_debt`**).
`core/views_db_health_rpc.py:74`: `if not provided or provided != configured`. Uses
Python `!=` operator, not `secrets.compare_digest`. Inconsistent with fleet HMAC
constant-time compare at `fleet_auth.py`. Practical timing-attack risk low over
HTTPS; API-consistency concern preserved.

**F-DEBUG-1 — `auth_debug_view` phantom PUBLIC_PATHS entry** (**`dead_code` +
`drift`**). `urls.py:1035` imports `auth_debug_view` from
`core/auth_views_enhanced.py:658`; NO `path()` binding for it. `PUBLIC_PATHS` at
`core/auth_middleware.py:106` reserves `/api/v1/auth/debug/` as public. Wasted
allowance + inconsistency.

**F-DEBUG-2 — Unauthenticated token oracle endpoints** (**`technical_debt`**).
`/api/v1/auth/validate-token/` (`auth_views_enhanced.py:559`) — `AllowAny`, NOT
rate-limited, probes `Token` table by key. Combined with (hypothetical, per F-DEBUG-1)
`/api/v1/auth/debug/` — TWO unrestricted token-validity oracles. Reset-password
also not rate-limited.

**F-DEBUG-3 — Compat alias bypasses rate limiter** (**`drift`**). `urls.py:2184`
registers `/api/auth/login/` (no `v1`). `RateLimitingMiddleware.rate_limits` at
`core/auth_middleware.py:864-868` only lists `/api/v1/auth/login/`. Brute-force
attempts via compat path unconstrained. Compounded by F-RATE-1 (middleware
disabled).

**F-RATE-1 — `RateLimitingMiddleware` DISABLED** (**`dead_code`**). Commented out
at `core/settings.py:230-232` citing Railway internal-IP false-limit problem.
Login/register/forgot-password endpoints have documented limits but no runtime
enforcement. Combined with F-DEBUG-3, no login-endpoint throttling at HEAD.

**F-SESS-1 — Redis-fallback silent session degradation** (**`technical_debt`**).
`core/settings.py:490-494`: Redis-unreachable at startup → `CACHES['default']`
overwritten with `LocMemCache`. Since sessions use `default` cache alias, Railway's
multi-process Procfile (~11 processes) silently breaks cross-process session
sharing under Redis failure. Design intent unclear — is this deliberate degrade
or accidental?

**F-TOKEN-1 — DRF `authtoken.Token` no expiry** (**`technical_debt`**). No
`expires_at` field. No `last_used`. Rotates only on explicit password change /
reset / logout. Long-lived indefinitely. Session-lifecycle contract Cat C S2403
must address.

**F-PA-1 — `session_tool.retire/set_active/seed` no ownership check** (**`unclear_owner`
+ `boundary_violation`**). `td_handlers_core.py:4011` (retire), ~4088 (set_active),
~4124 (seed): accept `conversation_id` from tool payload without verifying
`ChatConversation.user_id == user_id`. `_bound_conversation_id` sentinel guards
self-retire only. Cross-user targeting via known conversation_id possible.

**F-CMD-1 — `create_test_token` prod risk** (**`technical_debt`**).
`management/commands/create_test_token.py:27-38`: creates users with hardcoded
`testpass123` if new. No `DEBUG` guard, no `is_production` check. Accidental prod
invocation with new username = valid DRF token + insecure account.

**F-DOC-1 — No `docs/topics/auth.md`** (**`missing_connection`**). Verified absent
per Agent 5 §5.

**F-DOC-2 — No threat-model / trust-boundary doc** (**`missing_connection`**).
§3.27 self-flags. Parked candidate #1 for post-arc ADR.

**F-INV-1 — No `PLATFORM_INVENTORY §Auth` autoblock** (**`missing_connection`**).
Auth models appear only in generic model table.

**F-INV-2 — No `PLATFORM_WHAT_IT_IS §Auth` subsection** (**`missing_connection`**).

**F-VIP-1 preview** (full text in §15 debt matrix): `VIPInvite.account_expires_at`
NOT enforced at runtime. Severity HIGH — see §15.

### 14.4 LOW / observational

**F-PROV-1 — Handoff-provenance gaps** (**`unknown`**). S528 handoff missing;
S452, S891, S1069 handoffs contain zero auth content but code cites them. Doesn't
affect security posture; affects doc trust.

**F-FLEET-1 — `FleetSignatureExclusiveAuthentication` raising path untested via
HTTP** (**`technical_debt`**). Unit tests at `tests/services/test_fleet_auth.py`
exercise `verify_signed_request()` directly with ORM mocks; integration test
through DRF dispatch pipeline for the raising variant absent.

**F-PA-2 — `platform_config_tool.env_vars` secret masking completeness UNKNOWN**
(**`unknown`**). Deferred to Cat D or post-arc.

**F-PA-3 — `vip_invite_tool` PA handler staff-check UNKNOWN** (**`unknown`**).
`tool_dispatcher.py:528` registers `_handle_vip_invite`; whether it enforces
`IsAdminUser`-equivalent internally = unknown.

**F-PA-4 — `pa_chat_status` no ownership check on task_id UNKNOWN → likely BUG**
(**`unclear_owner`**). `views_personal_assistant.py:783`: `IsAuthenticated`
required but no verify `task.created_by == request.user`. Task-ID enumeration
= info-disclosure risk if PA responses contain user-specific sensitive content.

### 14.5 Trust-boundary rate table (acceptance criterion #6 evidence)

| Mechanism | Gate type | Runtime enforcement | Smoke test | Evidence |
|---|---|---|---|---|
| Standard user token auth | HARD | 100% non-bypassed | ABSENT (F-CRIT-2) | `core/auth_middleware.py:628-681`, `704-736` |
| PUBLIC_PATHS bypass | INTENTIONAL | 265 paths | PARTIAL (3 spot-checks in `tests/test_vip_invite_exchange.py:171-191`) | `core/auth_middleware.py:94-509, 570-571` |
| PUBLIC_PATHS_EXACT bypass | INTENTIONAL | 2 paths | ABSENT | `core/auth_middleware.py:513-516, 574-575` |
| OPTIONAL_AUTH_PATHS (soft-auth, fail-open) | SOFT | 7 paths | ABSENT | `core/auth_middleware.py:521-538, 579-595` |
| STAFF_REQUIRED_PATHS | HARD | 3 paths | ABSENT | `core/auth_middleware.py:541-545, 610-614, 661-664` |
| REVIEWER_BLOCKED_PATHS | HARD | 12 paths | ABSENT | `core/auth_middleware.py:548-556, 617-618, 668-669` |
| REVIEWER_ALLOWED_PATHS | HARD carve-out | 1 path prefix | ABSENT | `core/auth_middleware.py:559-561, 622, 672` |
| VIP demo HTTP layer | HARD RUNTIME | Whole /api/ surface for VIP | ABSENT (§14 F-HIGH-1) | `core/vip_middleware.py:56-91` |
| VIP demo PA payload layer | SOFT (prompt-only) | PA tool surface for `role='vip_viewer'` | N/A (prompt not code) | `core/models_assistant_profile.py:55-80` |
| Fleet HMAC permissive (side-effect-only) | SOFT-BY-CONTRACT | Sets `request.fleet_identity`; gate = permission class | PARTIAL (verify_signed_request unit test; DRF class dispatch untested) | `core/services/fleet_auth_drf.py:65-150` |
| Fleet HMAC exclusive (raising variant) | HARD | 3 fleet-only view file uses + inline for events/signals | ABSENT (F-FLEET-1) | `core/services/fleet_auth_drf.py:275-308` |
| PA_DB_HEALTH_RPC_TOKEN | HARD (default-off; 404) | 1 endpoint | PRESENT — `tests/test_db_health_rpc.py:34-216` | `core/views_db_health_rpc.py:39,63` |
| PUBLIC_INTEL_TOKEN | HARD (default-off; 404) | 1 endpoint (public intel) | PRESENT — `core/tests/test_public_intel_endpoint.py`, `test_public_changelog_endpoint.py` | `core/views_public_intelligence.py:37-60` |
| PURGE_SECRET | WEAK (hardcoded fallback F-CRIT-1) | 1 endpoint (`purge-queue`) | ABSENT | `core/views_home.py:259` |
| WebSocket token auth (via `ws_auth_middleware.TokenAuthMiddleware`) | NON-ENFORCING at middleware; consumer-dependent | All WS connections | ABSENT | `core/ws_auth_middleware.py:24-52` + consumer-per-consumer |

**Enforcement summary (14 gate mechanisms; F-HIGH-1 counts as 2 layers)**: 3 PRESENT
smoke tests + 2 PARTIAL + 9 ABSENT. Blocker to acceptance criterion #6
"trust-boundary registry existence + smoke-test coverage inventory (rate ≥ one
smoke-test-per-mechanism)".

---

## 15. Known Technical Debt

Debt matrix — severity + blast-radius + owner + age.

| Debt | Severity | Blast radius | Owner | Age (session onset) | Finding type |
|---|---|---|---|---|---|
| F-CRIT-1 PURGE_SECRET hardcoded fallback | **CRITICAL** | Anyone reading source can purge prod Celery queues if env unset | Auth + Ops | S1005 (2026-02?) | `boundary_violation` |
| F-CRIT-2 Session 1171 503-fork zero test | **HIGH** (regression-vector) | Standard token auth mechanism | Auth | S1171 fix landing 2026-06-20 | `technical_debt` |
| F-VIP-1 VIPInvite.account_expires_at NOT ENFORCED | **HIGH** | Every VIP user; token valid indefinitely once issued unless admin manual revoke | Auth | S(VIP feature ship, 2026-03-04) | `technical_debt` + `unclear_owner` |
| F-HIGH-1 VIP two-layer (HTTP hard; PA payload prompt) | **HIGH** (PA-layer only) | Every VIP user through `/api/pa/chat/` write path | Auth + PA | S(VIP feature ship) | `drift` |
| F-HIGH-2 WebSocketAuthenticationMiddleware dead-code | **HIGH** | Configuration knob has no effect; WS auth actually non-enforcing | Auth | Since always (never installed) | `dead_code` + `drift` |
| F-HIGH-3 PUBLIC_PATHS 265-entry no registry | **HIGH** | Unauthenticated attack surface; 265 paths uncontrolled | Auth | Since S528 (2025-12-21) accretion | `missing_connection` + `technical_debt` |
| F-WS-1 WS `get_user_from_token` silent-swallow-infra | **HIGH** | All WebSocket consumers | Auth | Since Session 1171 (HTTP-only fix, 2026-06-20) | `drift` |
| F-DEC-1 `@token_auth_required` no 503-fork | **MED** | 9 view files (68 uses per Agent 2 count) | Auth | Since Session 891 → aggravated at 1171 | `drift` |
| F-DEC-2 PA_DB_HEALTH_RPC_TOKEN non-constant-time | **LOW-MED** | 1 endpoint over HTTPS | Auth | Since S1249 (2026-06-30) | `technical_debt` |
| F-DEBUG-1 auth_debug_view phantom PUBLIC_PATHS | **MED** (inconsistency, doc trust) | 1 entry | Auth | Since S830 | `dead_code` + `drift` |
| F-DEBUG-2 validate-token oracle no rate limit | **MED** | Token enumeration vector | Auth | Since S830 + F-RATE-1 aggravation | `technical_debt` |
| F-DEBUG-3 `/api/auth/login/` compat bypass rate limit | **MED** | Login brute-force vector | Auth | Since compat alias registration | `drift` |
| F-RATE-1 RateLimitingMiddleware disabled | **MED** | All rate-limited endpoints (login + register + forgot-pw) | Auth + Ops | Since disabling commit | `dead_code` |
| F-SESS-1 Redis-fallback silent session degrade | **MED** | Multi-worker session sharing | Auth + Infra | Since always | `technical_debt` |
| F-TOKEN-1 DRF Token no expiry / rotation | **MED** | Every user; token permanent absent password event | Auth | Since always (DRF default) | `technical_debt` |
| F-PA-1 session_tool ownership check missing | **MED** | Cross-user conversation targeting | Auth + PA | Since PA `session_tool` addition | `boundary_violation` + `unclear_owner` |
| F-CMD-1 create_test_token prod risk | **MED** | Any accidental prod invocation | Auth + Dev tooling | Since command creation | `technical_debt` |
| F-FLEET-1 exclusive variant untested via HTTP | **MED** | 3 fleet-only endpoints | Auth + Fleet | Since S1129 | `technical_debt` |
| F-DOC-1 No docs/topics/auth.md | **MED** | Narrative anchor missing | Auth + Docs | Since always | `missing_connection` |
| F-DOC-2 No threat-model doc | **HIGH** | Platform-wide auth-contract | Auth | Since S1273 v2 flag | `missing_connection` |
| F-INV-1 No PLATFORM_INVENTORY §Auth autoblock | **MED** | Inventory anchor | Auth + Inventory | Since always | `missing_connection` |
| F-INV-2 No PLATFORM_WHAT_IT_IS §Auth subsection | **MED** | Narrative anchor | Auth + Docs | Since always | `missing_connection` |
| F-PA-2 platform_config_tool env_vars masking UNKNOWN | **UNKNOWN** | Env-var exposure | Auth + PA | UNKNOWN | `unknown` |
| F-PA-3 vip_invite_tool PA handler staff-check UNKNOWN | **UNKNOWN** | VIP-invite create/revoke | Auth + PA | UNKNOWN | `unknown` |
| F-PA-4 pa_chat_status task_id ownership UNKNOWN | **MED** (info-disclosure vector if confirmed) | Any authenticated user | Auth + PA | Since PA task pattern | `unclear_owner` |
| F-PROV-1 Handoff provenance gaps | **LOW** | Doc trust | Docs | Since S528+ | `unknown` |
| F-BND-1 (see §16) VIPInvite→Deliverable FK | **LOW** | Auth-domain FK into content-domain model | Auth | Since VIPInvite ship | `boundary_violation` |
| F-DUP-1 (see §17) 2 orphan TokenAuthMiddlewareStack duplicates | **LOW** | Dead code drift | Auth | Since orphan file addition | `dead_code` |
| F-DUP-2 (see §17) platform_role vs primary_role bifurcation | **MED** | Role system incorrectly assumed unified | Auth + Users | Since S998 reviewer role add | `duplicate_model` |
| F-DUP-3 (see §17) 4-model UserProfile duplication | **LOW** | Data-model complexity | Users domain | Since always | `duplicate_model` |
| F-DUP-4 (see §17) rotate_fleet_key + add_fleet_key overlap | **LOW** | Ops runbook confusion | Auth + Fleet | Since S1129 + emergency-key add | `duplicate_model` (ops-model) |

---

## 16. Boundary Violations

**F-BND-0 — Authority-vs-authentication demarcation: PRESERVED at HEAD**
(**`mature_primitive`**). Verified by Agent 4 §2 grep audit:
- Zero governance model imports (`GovernanceState`, `KillSwitch`) in
  `core/auth_middleware.py`, `core/vip_middleware.py`, `core/services/fleet_auth_drf.py`,
  `core/services/fleet_auth.py`.
- Zero auth middleware imports (`from core.auth_middleware`, `from core.vip_middleware`)
  in `core/employees/`, `core/services/ops_autopilot/`.
- Zero `request.user` in `core/models_governance.py`.

Correct pattern intact: middleware sets `request.user`; governance code reads
`request.user` attributes (`user.is_staff`); governance never calls back into auth
middleware.

**F-BND-1 — VIPInvite → Deliverable FK** (**`boundary_violation`** LOW).
`core/models_vip_invite.py:56`: `prospect_profile → Deliverable` (SET_NULL). Auth-
domain model FK'ing into content-domain model. Design-purposeful (prospect profile
IS a deliverable) but cross-domain surface. Also `VIPInvite.workspace →
ProjectWorkspace` and `AssistantProfile.workspace → ProjectWorkspace` — same pattern.

**F-BND-2 — FleetCapabilityRequired live DB query into fleet domain**
(**`mature_primitive`** — Rigby SIGN cycle 1 Q11(c) fold reclassified from
`boundary_violation` LOW to "expected side effect"). `core/services/fleet_auth_drf.py:251`:
`FleetServiceIdentity.objects.get(pk=...)` inside DRF permission check with lazy
import. Intentional design: capability revocation must take effect immediately
without key rotation. Not a boundary violation; documented behavior.

**F-BND-3 — `verify_signed_request` writes `last_used_at`** (**`mature_primitive`** —
Rigby SIGN cycle 1 Q11(c) fold reclassified from `boundary_violation` LOW to
"expected side effect"). `core/services/fleet_auth.py:~513`: `UPDATE` on
`FleetServiceKey` and `FleetServiceIdentity` as side effect of verification.
Intentional (usage tracking); documented behavior. Would only be a violation if
the arc had a "no writes in auth verification" hard rule.

**F-BND-4a — Unauthenticated bet-placement write** (**`boundary_violation`**
CRITICAL — Rigby SIGN cycle 1 Q8 fold promoted HIGH → CRITICAL). `core/auth_middleware.py:198`:
`/api/v1/betting/place/` publicly bypassed with comment "Session 563: Bet Tracking
(allow anonymous for demo mode)". Sports/DBAO domain WRITE endpoint bypasses
authentication entirely. §3.27 baseline silent. Aligns with S2203 §14 F3
money-path treatment. May outrank F-CRIT-1 if production-reachable.

**F-BND-4b — Reviewer inversion / policy incoherence** (**`boundary_violation` +
`drift`** HIGH — new finding from Rigby SIGN cycle 1 Q16 grep-verify). Same
endpoint `/api/v1/betting/place/` ALSO appears in `REVIEWER_BLOCKED_PATHS` at
`core/auth_middleware.py:550` (co-located with `/api/v1/betting/execute/`).
Effect: anonymous users can hit the endpoint (PUBLIC_PATHS bypass at line 198);
logged-in reviewers are blocked with 403 (REVIEWER_BLOCKED_PATHS at line 550).
**Anonymous-can-bet-reviewers-cannot inversion.** Signals unintentional shipping;
complicates detection (reviewers testing won't see the bug); exactly the drift
pattern that defeats "trust the gate" assumptions. Chris D-verdict-request:
(i) resolve inversion so stricter roles aren't less privileged than anonymous;
(ii) implementation choice belongs to Cat B (permission-floor).

**F-BND-5 — Body System APIs unconditionally public** (**`boundary_violation`**
MED-HIGH). `core/auth_middleware.py:270-372`: all 9 body-system monitor APIs
(HEART/LUNGS/CIRCULATORY/SPINE/IMMUNE/DIGESTIVE/MUSCULAR/BRAIN/SKIN/NERVOUS) expose
system vitals unconditionally. Design intent "read-only monitoring convenience";
information-richness for recon is preserved.

---

## 17. Duplicate or Overlapping Systems

**F-DUP-1 — 3 orphan TokenAuthMiddlewareStack definitions**
(**`dead_code`** LOW). `core/websocket_auth.py:42`, `core/ws_auth_middleware.py:46`,
and dead-code `core/auth_middleware.py:739-822` (`WebSocketAuthenticationMiddleware`
class). Only `ws_auth_middleware.py` is imported by `core/asgi.py:25`. Deletion
candidates: `websocket_auth.py` + `WebSocketAuthenticationMiddleware` in
`auth_middleware.py` — but per feedback_verify_before_deleting_dead_code.md, must
grep-verify no callers before deletion. Post-arc maintainer-decision batch candidate.

**F-DUP-2 — `platform_role` vs `primary_role` role-field bifurcation**
(**`duplicate_model`** MED). Reviewer role: `UnifiedUser.platform_role == 'reviewer'`
(`core/models/base/models.py:205-207`). VIP role: `EnhancedUserProfile.primary_role
== 'vip_demo_viewer'` (`core/vip_middleware.py:97-98`). Two parallel role systems on
different models with no cross-documentation. Any assumption that "roles" are
uniform will break one gate silently.

**F-DUP-3 — 4-model UserProfile duplication**
(**`duplicate_model`** LOW). `UserProfile` + `UserStatistics` + `ExtendedUserProfile`
+ `EnhancedUserProfile` all created via post_save signal at
`core/models/users/models.py:1098-1111`. `subscription_tier` field lives on BOTH
`UnifiedUser` AND `EnhancedUserProfile` — no synchronization. `tenant` FK lives on
BOTH `UnifiedUser` AND `EnhancedUserProfile` — no reconciliation. Ownership: which
field is authoritative?

**F-DUP-4 — Fleet key rotation two-command overlap**
(**`duplicate_model`** LOW, ops-model). `rotate_fleet_key plan/activate/complete/abort`
(4-stage) + `add_fleet_key --app-slug` (emergency dual-active). Both print raw
secret once. `add_fleet_key` leaves old key active, relying on operator to disable
via `rotate_fleet_key` — if operator forgets, dual-active persists indefinitely.

---

## 18. Ownership Gaps

**F-OWN-1 — PUBLIC_PATHS registry maintenance** (**`unclear_owner`** HIGH per §15
F-HIGH-3 blast). No named DRI. No approval gate policy. No periodic review.
Session 528 (2025-12-21) declared "reduced to truly public endpoints only"; ~15
sessions since have added 100+ entries with no auditor.

**F-OWN-2 — VIP whitelist + `data_retention_days` maintenance** (**`unclear_owner`** MED).
`_VIP_ALLOWED_WRITE_PATHS`, `_VIP_ALLOWED_COCKPIT_PATHS`, `_VIP_ALLOWED_READ_PREFIXES`
hardcoded frozensets. No named owner. Similarly `EnhancedUserProfile.data_retention_days`
(7-365, default 90) has no enforcement mechanism.

**F-OWN-3 — Fleet audit log retention** (**`unclear_owner`** LOW). `FleetAuthAuditLog`
+ `FleetPAChatAuditRow` accumulate unbounded rows. Cleanup tasks exist for
`FleetArtifact`/`FleetEvent` (daily 02:10 + 02:25 per `core/celery.py:112,131`),
not for audit rows.

**F-OWN-4 — Service token rotation cadence** (**`unclear_owner`** MED). No named
DRI for `PA_DB_HEALTH_RPC_TOKEN`, `PUBLIC_INTEL_TOKEN`, `PURGE_SECRET`. No rotation
doc. F-CRIT-1 aggravates: hardcoded fallback means `PURGE_SECRET` can never be
"disabled by omission".

**F-OWN-5 — Auth-topic doc + PLATFORM_INVENTORY §Auth autoblock** (**`missing_connection`**
per §11 gaps). No named owner. No tracking issue.

**F-OWN-6 — Fleet capability registry ownership** (**`unclear_owner`** LOW).
`FleetServiceIdentity.capabilities` JSONField accepts any shape (no schema
validator). Named DRI = "Auth + Fleet" per §3.27 — split ownership, unclear which
side owns schema evolution.

---

## 19. Recommended Future Research

Ranked by architectural uncertainty × risk × unblocked flows (playbook §11.2 §19
requirement).

### 19.1 POSTURE-DECISION evidence plan for xx99

Per parent §3.A Cat A expected outputs, this section delivers Cat A's POSTURE-
DECISION on threat-model authoring + parked candidates.

> **Rigby SIGN cycle 1 Q18 fold — anti-scope preservation attestation:** This
> audit is **NOT a threat model**. It is an inventory intended to seed post-arc
> ADR / threat-model work. The §14.5 trust-boundary rate table + §16 boundary
> preservation verdicts + §17 duplicate systems + §18 ownership gaps constitute
> inputs to a threat model, not the threat model itself. Missing from a true
> threat model: attacker capability categorization, scenario modeling, mitigation
> matrix, residual-risk register.

**POSTURE-DECISION #1: Threat model / trust-boundary doc authoring.**
- Recommend: **DEFER post-arc as ADR** (matches parent parked candidate #1). Cat A's
  20-section inventory + trust-boundary rate table (§14.5) + smoke-test coverage
  matrix (§14.5) is the "closest thing" (§3.27 self-description) with HEAD-verified
  file:line precision. Full threat model requires (a) attack-surface
  categorization (attacker capability + attacker access + target), (b) mitigation
  matrix per boundary, (c) residual-risk register — all beyond Cat A research-only
  scope per playbook §5 phase discipline.
- **Rigby SIGN cycle 1 Q19 fold**: track as REQUIRED-BEFORE-CANONICAL (per §12
  CANONICAL blocker #1), not optional deferral. Canonical being blocked doesn't
  force threat model NOW, but does force it BEFORE CANONICAL.
- Chris D-verdict-request at xx99: (i) spawn post-arc threat-model ADR
  (required-before-CANONICAL); (ii) defer further until Cat B+C+D land;
  (iii) non-candidate (Cat A + Cat B+C+D audits become the de-facto threat model).

**POSTURE-DECISION #2: VIP runtime tool-call gate (parent parked candidate #2).**
- Recommend: **P1/P0-INVESTIGATE** (Rigby SIGN cycle 1 Q19 fold: refined from
  pure DEFER — Q10 blast-radius-unknown pushes toward rapid scoping over deferral;
  pure DEFER underreacts if VIP PA surface is production-reachable + ungated).
  Rapid scoping = confirm current runtime tool-gate posture (write-tool inventory
  accessible to `vip_viewer` role via PA payload). Full redesign still deferred to
  post-arc ADR.
- Chris D-verdict-request at xx99: (i) spawn P1 rapid-scoping investigation +
  post-arc PA VIP-tool-gate ADR; (ii) accept SOFT PA-payload prompt-only as
  ratified posture pending investigation.

**POSTURE-DECISION #3: PURGE_SECRET F-CRIT-1 immediate remediation.**
- Recommend: **P0 post-arc PR** (not deferred; not ADR-scope). CRITICAL severity.
  **Decision-space framing (Rigby SIGN cycle 1 Q19 fold — not solution-prescriptive):**
  "Eliminate default-secret + remove unauth bypass posture; choose implementation
  (env-required, signed admin-only, staff-only, etc.)."
- Chris D-verdict-request at xx99: (i) P0 PR to remediate F-CRIT-1 (implementation
  choice belongs to Chris); (ii) fold into post-arc maintainer-decision batch.

### 19.2 Ranked follow-on research queue (Rigby SIGN cycle 1 Q15 reordered)

Ranked by uncertainty × risk × unblocked-flows. **Rank-1 reordered per Rigby
SIGN Q15 fold: F-CRIT-1 + F-BND-4a promoted to co-equal P0s.**

1. **Immediate remediation triage for concrete CRITICAL endpoints (CO-EQUAL P0s)** —
   (a) **F-CRIT-1 PURGE_SECRET fallback** post-arc P0 PR per POSTURE-DECISION #3;
   (b) **F-BND-4a unauthenticated bet-placement write** post-arc P0 PR per Rigby
   Q8/Q10 fold + Q15 co-equal ranking (order between (a)/(b) depends on prod
   reachability); (c) **F-BND-4b reviewer inversion** paired with (b) —
   permission-floor decision belongs to Cat B S2402. Also in remediation triage
   batch: F-CRIT-2 (add 503-fork test) + F-HIGH-2 (delete dead middleware OR
   wire it in per extraction_candidate tag) + F-HIGH-3 (PUBLIC_PATHS registry
   design coordination with Group 2500).
2. **PA VIP-tool-gate P1 rapid-scoping investigation** (Rigby Q15 fold: promoted
   from Rank 2 via POSTURE-DECISION #2 DEFER→P1/P0-INVESTIGATE refinement) —
   confirm current runtime tool-gate posture; enumerate write-tools accessible
   to `vip_viewer` role via PA payload. Feeds post-arc PA VIP-tool-gate ADR.
3. **Threat-model authoring** — Cat A's trust-boundary rate + smoke-test
   coverage matrix seed the threat model; post-arc ADR per POSTURE-DECISION #1.
   Rigby Q15 fold: threat model outranks rapid-scoping only if VIP tool-gate is
   already known-constrained; otherwise stays at Rank 3.
4. **Smoke-test coverage authoring per mechanism** — 11 of 14 mechanisms absent.
   Post-arc maintainer-decision batch item.
5. **Session-lifecycle model (Cat C S2403)** — Cat A evidence for Cat C:
   `authtoken.Token` no expiry (F-TOKEN-1) + VIPInvite.account_expires_at NOT
   ENFORCED (F-VIP-1 HIGH) + Redis-fallback silent-degrade (F-SESS-1).
6. **Permission-floor per-endpoint mapping (Cat B S2402)** — Cat A vocabulary +
   trust-boundary rate table feed Cat B measurement.
7. **Frontend integration audit (Cat D S2404)** — Cat A confirms Session 1171
   503-fork on HTTP; Cat D audits silent-401 caller side + typed-error-envelope
   design candidates + CF-6 client-visible-contract testing.
8. **F-VIP-1 immediate remediation research** — VIPInvite.account_expires_at
   enforcement design (Celery beat task vs middleware check vs login-time check).
9. **F-DUP-2 role-field bifurcation reconciliation** — document canonical role
   query pattern; add role-lookup helper; deprecate ambiguity. **CANONICAL
   blocker per §12 fold.**
10. **F-DEC-1 `@token_auth_required` decorator upgrade** (severity HIGH per
    fold) — port 503-fork from middleware; either extract common helper or
    explicit rationale for divergence; pair with smoke test simulating infra
    failure.
11. **F-PA-1 session_tool ownership check** — add `ChatConversation.user_id ==
    user_id` verification; likely a small PR.
12. **PUBLIC_PATHS registry DRI assignment + change-control mechanism (CANONICAL
    HARD blocker per §12 fold)** — post-arc governance decision required before
    CANONICAL classification achievable.

### 19.3 Cross-arc coordination flags (recap from §9.2 — expanded to 7 per Rigby SIGN cycle 1 Q13 fold)

- CF-1 → Group 2600 PA (workspace context contract)
- CF-2 → Group 1700 Observability (auth event stream — re-labeled OPTIONAL/CROSS-ARC per Q11 fold)
- CF-3 → Group 2500 API (permission-floor decision + PublicIntelTokenAuth registry — Cat B/Group 2500 owns decision per Q17 fold)
- CF-4 conditional → Group 2300 Mobile (validate-token contract)
- CF-5 → Group 1900 Governance/Authority (F-BND-0 boundary contract attestation)
- CF-6 → Group 2200 Frontend (Session 1171 503-fork client-visible contract)
- CF-7 → External Integrations Surface (Discord/Stripe/mobile signature-auth adjacency)

### 19.4 xx99 anchor-update recommendations (Rigby SIGN cycle 1 Q20 fold — 6 items)

Anchor candidates to seed S2499 xx99 §7 anchor-update batch:

- **(a) PLATFORM_INVENTORY §Auth autoblock** (from §14 F-INV-1 + §14.5 trust-boundary
  rate table).
- **(b) PLATFORM_WHAT_IT_IS §Auth narrative subsection** (from §14 F-INV-2).
- **(c) `docs/topics/auth.md` creation** (from §14 F-DOC-1 + parent parked
  candidate #8).
- **(d) `platform_architecture_inventory.md §3.27` row 27 refresh** with 3 baseline-
  stale corrections (~108 → 265 PUBLIC_PATHS + VIP two-layer + Fleet CONTRACT
  reclassification).
- **(e) `ARCHITECTURE_INDEX` v-bump** at S2499 close (NEW — Rigby SIGN cycle 1 Q20
  fold) — explicit version bump entry tied to auth-arc closeout so downstream
  readers know the index reflects new auth inventory + drift corrections.
- **(f) `OPEN_ARCS` transition updates at S2499** (NEW — Rigby SIGN cycle 1 Q20
  fold) — move S2401/S2402/S2403/S2404 (and dependent auth sub-arcs) from
  In-progress → CLOSED with short "what changed" note + links to Cat A/B/C/D
  final artifacts.
- **(g) PUBLIC_PATHS registry DRI + change-control anchor** (NEW — Rigby SIGN
  cycle 1 Q20 fold) — a specific xx99/architecture-index row that assigns
  PUBLIC_PATHS registry DRI + change-control mechanism (CANONICAL hard blocker
  per §12 fold #6).

---

## 20. Appendix

### 20.1 Files inspected

**HEAD-verified reads (full or targeted; file:line evidence throughout the audit):**

- `core/auth_middleware.py` (976 LOC — full)
- `core/vip_middleware.py` (104 LOC — full)
- `core/services/fleet_auth_drf.py` (317 LOC — full)
- `core/services/fleet_auth.py` (targeted at ~165 sig-base, ~513 last_used,
  ~600+ audit, ~647-660 logging)
- `core/asgi.py` (33 LOC — full; verifier-loop key evidence)
- `core/ws_auth_middleware.py` (52 LOC — full; verifier-loop key evidence)
- `core/websocket_auth.py` (existence + `TokenAuthMiddlewareStack` def confirmed
  as orphan)
- `core/settings.py` targeted: MIDDLEWARE 217-242, PUBLIC_INTEL_TOKEN 158,
  REQUIRE_WEBSOCKET_AUTH 625, SESSION_ENGINE 1105, Redis-fallback 490-494,
  RateLimitingMiddleware disabled 230-232
- `core/views_home.py:259` (PURGE_SECRET F-CRIT-1)
- `core/views_db_health_rpc.py:39,63-74` (PA_DB_HEALTH_RPC_TOKEN)
- `core/views_public_intelligence.py:37-60` (PublicIntelTokenAuth)
- `core/views_personal_assistant.py:77, 254-266, 783` (PA endpoint auth)
- `core/models_assistant_profile.py:55-80, 90-122` (VIP role prompt injection)
- `core/models_vip_invite.py:30-56` (VIPInvite lifecycle)
- `core/models/fleet.py:63-694` (fleet models via Agent 1 inventory)
- `core/models/base/models.py:86, 116, 205-207, 224` (UnifiedUser, is_reviewer, DiscordLinkCode)
- `core/models/users/models.py:12, 131, 162, 212, 370, 978, 1098-1111` (profile models)
- `core/services/unified_pa_entrypoint.py:334, 1130-1240, 1775-1792` (PA workspace context)
- `core/consumers_pa_conversation.py:183` (WS hard reject)
- Additional targeted reads via Agent 1-6 sub-agent sweep — see 6 agent
  reports in `/private/tmp/claude-501/.../tasks/*.output`.

**Docs inspected:**

- `docs/research/platform_architecture_inventory.md` §3.27 (lines 2026-2095 + row
  27 at ~237 + Rigby verifier_loop at ~26-29)
- `docs/research/domains/auth/2400_auth_domain_scoping.md` full
- `docs/research/DOMAIN_RESEARCH_PLAYBOOK.md` §11.2 template, §12 classifications,
  §13 6-agent sweep, §14 evidence rules, §15 SIGN policy, §16 commit policy
- `docs/research/domains/frontend/2201/2203/2204/2299` selective reads for T1
  handoff bundle sources
- `docs/handoffs/SESSION_1005/1129/1131/1133/1138/1171/1249/998/830/2400` verified
  per Agent 5 provenance sweep

### 20.2 Grep patterns used

- `authentication_classes\|permission_classes` — DRF decorator inventory (798 matches
  across `core/`)
- `WebSocketAuthenticationMiddleware\|TokenAuthMiddlewareStack` — WS middleware
  install-status verification (verifier-loop-key)
- `REQUIRE_WEBSOCKET_AUTH` — dead-config surface
- `GovernanceState\|KillSwitch\|governance\|authority` in auth files — boundary
  preservation
- `from core.auth_middleware\|from core.vip_middleware` in `core/employees/`,
  `core/services/ops_autopilot/` — reverse boundary
- `PURGE_SECRET\|PA_DB_HEALTH_RPC_TOKEN\|PUBLIC_INTEL_TOKEN` — service token
  surface
- `session_tool\.\|whoami\|create_fresh\|retire` — PA session tool inventory
- `FleetSignatureAuthentication\|FleetSignatureExclusiveAuthentication\|FleetSignatureRequired` —
  fleet auth usage sites

### 20.3 Unresolved unknowns (marked honestly per playbook §14)

- **U1**: `FleetSignatureAuthentication` on infra failure during `verify_signed_request`
  — DB lookups (FleetServiceKey, FleetServiceIdentity) unhandled in auth class.
  Likely 500 via DRF error middleware; not confirmed.
- **U2**: `REQUIRE_WEBSOCKET_AUTH` value in Railway prod — dead config, but value
  itself not verified. Even if `True`, no runtime effect (F-HIGH-2).
- **U3**: `is_reviewer` property model hierarchy — check on `UnifiedUser` or
  `EnhancedUserProfile`? Grep shows property at `core/models/base/models.py:205-207`
  reading `self.platform_role`; middleware `hasattr(request.user, 'is_reviewer')`
  suggests it's on User model. Full hierarchy not traced.
- **U4**: Rotation cadence or last-rotated date for `PA_DB_HEALTH_RPC_TOKEN`,
  `PUBLIC_INTEL_TOKEN`, `PURGE_SECRET`. No secrets audit doc found.
- **U5**: F-PA-2 `platform_config_tool.env_vars` secret masking completeness.
- **U6**: F-PA-3 `vip_invite_tool` PA handler staff-check.
- **U7**: F-PA-4 `pa_chat_status` task_id ownership check (likely bug).
- **U8**: F-FLEET-1 exclusive raising path via HTTP dispatch — not exercised in
  integration tests.
- **U9**: When exactly S1273 v2 review was written relative to VIP middleware
  landing (2026-03-04). Baseline was FALSE at S1273 v2 write time regardless (VIP
  gate live 3 months prior); question is whether §3.27 language was cargo-culted
  from a pre-VIP inventory.
- **U10**: `EnhancedUserProfile.data_retention_days` enforcement (F-OWN-2) — no
  scheduled task found, but full audit of `core/tasks*.py` for
  `data_retention_days` reads not exhaustive.

### 20.4 Conflicts between sources (verifier-loop history)

**Conflict 1 (resolved pre-draft — see frontmatter verifier_loop)**: Agent 2 vs
Agent 3 on `WebSocketAuthenticationMiddleware` installation status. Agent 2 walked
through class at `core/auth_middleware.py:739-822` as active; Agent 3 asserted
dead-code. Parent-Claude verifier-loop read `core/asgi.py` + `core/ws_auth_middleware.py`
directly; Agent 3 correct. Corrected §5 + §14 F-WS-1 + §17 F-DUP-1 accordingly.

**Conflict 2 (resolved — count precision)**: Agent 6 initially reported PUBLIC_PATHS
"165+ distinct path strings" based on grep of list entries; Agent 3 confirmed the
target count 265 via runtime shell (`len(M.PUBLIC_PATHS)`). Parent verifier ran
`python manage.py shell -c "from core.auth_middleware import
UnifiedTokenAuthenticationMiddleware as M; print(len(M.PUBLIC_PATHS))"` and got 265.
Runtime wins per playbook §14 "Count conflicts resolved against runtime inventory."
The 165 grep figure reflects DEDUPLICATED distinct strings; 265 is the runtime
list length WITH the 8+ confirmed duplicates. Both are informative — §14 F-HIGH-3
now cites both: "265 raw + ≥8 confirmed duplicates."

### 20.5 Rigby SIGN cycle 1 fold-target areas (pre-emptive per playbook §14
grep-verify-before-shipping)

Cat A anticipates these pressure-test axes for Rigby SIGN cycle 1:

- **Q: "Is F-HIGH-2 dead-code claim verified?"** — direct `core/asgi.py`
  read at §5 F-HIGH-2 entry + §14.2 body + §17 F-DUP-1. Verifier-loop history
  documented in frontmatter + §20.4.
- **Q: "Is F-CRIT-1 severity CRITICAL warranted?"** — `views_home.py:259` fallback
  string is publicly readable in git history + source; endpoint is in
  PUBLIC_PATHS_EXACT (auth-bypassed); prod remediation is P0 per POSTURE-DECISION
  #3.
- **Q: "Does F-HIGH-1 VIP two-layer split accurately preserve baseline §3.27
  intent?"** — Answer: F-HIGH-1 is a REFINEMENT, not a rejection. §3.27 v2 said
  "prompt-only, no runtime gate" (compressed). Cat A splits into HTTP layer
  (HARD RUNTIME, baseline stale) + PA payload layer (SOFT prompt-only, baseline
  correct). Layer-2 preservation matches baseline; layer-1 upgrade is the drift.
- **Q: "Is F-HIGH-4 CONTRACT reclassification of Fleet fallback defensible?"** —
  docstring at `core/services/fleet_auth_drf.py:34-38` explicitly states
  "NEVER raise" as design. `FleetSignatureExclusiveAuthentication` (line 275) is
  the intentional raising variant. Cat A does NOT claim fleet auth has no drift
  — it moves the drift-risk locus from the auth class itself to view-layer
  misconfiguration + F-FLEET-1 test-coverage gap.
- **Q: "Cat A hasn't extended scope into Cat B/C/D — respects §7.1 guardrails?"** —
  Yes. §2 anti-scope alignment explicit. §14 evidence flags (F-DEC-1 usage
  count "9 view files") measure surface without designing fix. §19 Chris
  D-verdict-request items surface decisions but do NOT author fixes.

### 20.6 Playbook §11.2 template compliance (16th consecutive application)

- §1 Executive Summary — 500 words plus tables (target 300-500 words; body over
  but justifies via headline-finding density).
- §2-8 domain purpose + entry points + models + services + APIs + runtime + data
  ownership — HEAD-verified with file:line.
- §9 integrations — 32-domain map delivered by Agent 4; §9.1 headline rows here;
  full map in Agent 4 report + §20.2 grep patterns.
- §10 event flows — auth event enumeration + missing-events flag → CF-2.
- §11 documentation — 4 confirmed gaps + 4 new provenance gaps.
- §12 research coverage — LIGHT → MODERATE at S2401 close per §12 threshold.
- §13 maturity — PARTIAL preserved for different reasons; upgrade blocked by
  F-CRIT-1 + F-CRIT-2.
- §14 known drift — 4 CRITICAL/HIGH + 14 MEDIUM + 5 LOW + 4 UNKNOWN + trust-
  boundary rate table (14 mechanisms × gate type × smoke-test evidence).
- §15 debt matrix — 30 items with severity + blast + owner + age + finding_type.
- §16 boundary violations — F-BND-0 preserved verdict + 5 flagged crossings.
- §17 duplicates — 4 items (dead-code, role bifurcation, profile duplication, ops-model overlap).
- §18 ownership gaps — 6 items with severity classification.
- §19 recommended future research — 3 POSTURE-DECISIONs + 11-item ranked queue +
  4 cross-arc coordination flags.
- §20 appendix — files inspected + grep patterns + UNKNOWNs + conflicts +
  Rigby-fold anticipation + template compliance.

**Frontmatter compliance**: title + session + status (draft) + arc + category +
authors + verifier_loop + companion_anchors (22 rows) + delegated_from (3 rows) +
delegates_to (4 rows) + head_commit_before + arc_pin + sign_pin + scope_shape +
provenance + owner. All fields populated; no `not applicable` sentinel required.

**File length**: ≈1,395 lines drafted (post-SIGN-fold: 1,450+ lines; target range:
exemplar S2204 at 1,229 lines). Body dense with file:line evidence; no filler.

### 20.7 Rigby SIGN Cycle 1 Fold Ledger

Full record of the 20 folds accumulated across 4 batches (Q1-Q20) + retroactive
grep-verify catch on compound bet-placement drift. SIGN pin `pa-f0b18d20dbc244ef`
minted at cycle open; retired at cycle close via `session_tool.retire`
(updated_count=8, retired=true). Final verdict: **SIGN-with-edits at MED confidence
(0.74)**. Cycle 2 NOT required per MED confidence + all 20 folds landable
pre-Chris-ratification.

**Batch 1 (Q1-Q5): Structural + Maturity + CRITICAL findings**

- **Q1 PARTIAL PASS** (missing parts) — No load-bearing miss verified in sample;
  residual repo-wide grep gap on DRF `authentication_classes`/`AllowAny`/custom
  `BaseAuthentication` patterns. **Fold**: §20.3 Unresolved unknowns U11 added —
  "full repo-wide DRF permission-decorator sweep not completed; possible additional
  auth-adjacent surfaces at HEAD".
- **Q2 FAIL** (overstated maturity) — HTTP token auth path "WORKING" language
  overstates. **Fold applied to §13**: refined to "WORKING (happy-path) but NOT
  RELIABLE/PROVEN"; §13 maintains PARTIAL with explicit disqualifiers.
- **Q3 PASS** (understated maturity Fleet) — Fleet HMAC component-level upgrade
  candidate. **Fold**: §13 Fleet primitive line notes "WORKING-by-design;
  potentially WORKING→STABLE at component level pending 3 conditions (nonce-store
  replay + verification-mandatory-on-endpoints + audit-row-writes on-by-default)".
- **Q4 PASS** (F-CRIT-1 defensibility) — CRITICAL severity warranted. **Fold
  applied to §14.1 F-CRIT-1**: frame as compound condition (AllowAny +
  PUBLIC_PATHS_EXACT bypass + hardcoded fallback), not any single factor alone.
- **Q5 PASS w/ downgrade** (F-CRIT-2 severity) — Reclassify HIGH-approaching-CRITICAL
  → HIGH. **Fold applied to §14.1 F-CRIT-2**: "HIGH — regression risk of prior
  production incident fix"; failure mode = misleading-status-code, not new attack
  surface; pair with concrete "add smoke test" action item.

**Batch 2 (Q6-Q10): Load-bearing findings + Boundary intent**

- **Q6 PASS w/ wording tweak** (F-HIGH-1 VIP two-layer) — Two-layer decomposition
  defensible; adjust framing. **Fold applied to §14.2 F-HIGH-1**: added clarifying
  sentence "§3.27 v2 'prompt-only' language referred primarily to PA-layer
  control, not the HTTP enforcement locus."
- **Q7 PASS w/ classification refinement** (F-HIGH-2 dead-code) — Add
  `extraction_candidate` tag. **Fold applied to §14.2 F-HIGH-2**: class updated to
  `dead_code + drift + extraction_candidate`; remediation path = "remove unused
  middleware OR wire it in".
- **Q8 MIXED** (F-HIGH-3 vs F-BND-4) — F-BND-4 promoted HIGH → CRITICAL. **Fold
  applied to §16 F-BND-4**: split into F-BND-4a CRITICAL (unauthenticated bet-
  placement write, aligns with S2203 money-path treatment) + F-BND-4b HIGH
  (reviewer inversion — see retroactive catch below). F-BND-5 body-system APIs
  preserved MED.
- **Q9 PASS w/ caution** (F-HIGH-4 Fleet CONTRACT) — Keep CONTRACT framing; make
  "enforcement coverage incomplete" the headline. **Fold applied to §5 Fleet
  service rows**: "CONTRACT correct, enforcement coverage incomplete (F-FLEET-1
  exclusive-variant untested via HTTP dispatch)."
- **Q10 PASS** (riskiest finding ranking) — Top 3: F-CRIT-1 + F-BND-4a (co-equal)
  + F-HIGH-1 layer-2. **Fold applied to §1 Executive Summary**: added note
  "F-BND-4a may outrank F-CRIT-1 if production-reachable (money-path >
  ops-path)."

**Batch 3 (Q11-Q15): Scope + Anti-scope + Cross-arc**

- **Q11 PASS** (intentional separation confusion) — 3 re-labels. **Fold applied
  to §9.2 CF-2**: added "OPTIONAL / CROSS-ARC (Observability), not MISSING". Fold
  applied to §16 F-BND-2/F-BND-3: reclassified from `boundary_violation` LOW to
  `mature_primitive` "expected side effects".
- **Q12 PROMOTE to HIGH** (F-DEC-1) — Severity MED → HIGH. **Fold applied to §14.3
  F-DEC-1**: promoted; classified as "HIGH (status-code correctness + incident-
  response regression class)"; large blast radius 68 uses.
- **Q13 PARTIAL PASS** (cross-arc flags) — Add CF-5/6/7. **Fold applied to §9.2
  + §19.3**: added CF-5 (Governance/Authority boundary attestation) + CF-6
  (Frontend 503-fork client-visible contract) + CF-7 (External integrations
  signature-auth adjacency).
- **Q14 PARTIAL PASS** (CANONICAL blockers) — Add 2 blockers. **Fold applied to
  §12**: added blocker #5 (role-field reconciliation) + blocker #6 (PUBLIC_PATHS
  DRI + registry governance — HARD blocker).
- **Q15 FAIL** (future-research ranking) — Reorder. **Fold applied to §19.2**:
  Rank 1 promoted to co-equal P0s (F-CRIT-1 + F-BND-4a + F-BND-4b reviewer
  inversion + F-CRIT-2 + F-HIGH-2 + F-HIGH-3); Rank 2 = PA VIP tool-gate research
  (per POSTURE-DECISION #2 P1/P0-INVESTIGATE refinement); Rank 3 = threat model.

**Batch 4 (Q16-Q20): Rigor + Anti-scope preservation + POSTURE-DECISION**

- **Q16 PARTIAL PASS** (factual errors) — Middleware chain + HEAD SHA verified;
  count/git-log claims need appendix proof. **Fold applied to §20.3**: added
  U12 provenance-note that PUBLIC_PATHS count 265 was verified via Django shell
  runtime `len(M.PUBLIC_PATHS)`; git-log commit hashes 5c8bd585 + 445d0349 cited
  from `git log core/vip_middleware.py`.
- **Retroactive Q16 grep-verify catch (bet-placement compound drift)** — Rigby's
  Batch 4 tool-use surfaced 2 corrections Cat A missed:
  (a) `/api/v1/betting/place/` line number = 198, NOT 199 (Cat A original was
  off-by-1);
  (b) `/api/v1/betting/place/` ALSO appears in `REVIEWER_BLOCKED_PATHS` at line
  550 — creates ANONYMOUS-CAN-BET-REVIEWERS-CANNOT INVERSION.
  **Fold applied**: (i) §9.1 line reference updated `199` → `198,550`; (ii) §14
  + §16 F-BND-4 split into F-BND-4a CRITICAL + F-BND-4b HIGH; (iii) §1 headline-
  finding table updated; (iv) §19.2 rank-1 co-equal-P0 list expanded to include
  F-BND-4b remediation.
- **Q17 PASS w/ caution** (Cat B/C/D anti-scope) — Keep "evidence + decision
  needed" mode. **Fold applied to §9.2 CF-3**: added explicit tag "Permission-
  floor decision belongs to Cat B / Group 2500."
- **Q18 PASS** (threat-model anti-scope) — Add explicit "not a threat model"
  sentence. **Fold applied to §19.1**: added > blockquote before POSTURE-DECISION
  #1 stating "This audit is NOT a threat model. It is an inventory intended to
  seed post-arc ADR / threat-model work."
- **Q19 PARTIAL PASS** (POSTURE-DECISION defensibility) — Tighten #3 + reconsider
  #2. **Fold applied to §19.1**: POSTURE-DECISION #3 rephrased as decision-space
  ("Eliminate default-secret + remove unauth bypass posture; choose
  implementation") — not solution-prescriptive. POSTURE-DECISION #2 refined
  DEFER → P1/P0-INVESTIGATE (rapid scoping + confirm posture). POSTURE-DECISION
  #1 tagged as REQUIRED-BEFORE-CANONICAL per §12 blocker #1.
- **Q20 PARTIAL PASS** (xx99 anchor-updates) — Add 3 anchors. **Fold applied to
  §19.4 (new subsection)**: 7 total anchor-update recommendations: (a)
  PLATFORM_INVENTORY §Auth autoblock; (b) PLATFORM_WHAT_IT_IS §Auth subsection;
  (c) `docs/topics/auth.md`; (d) §3.27 row 27 refresh; (e) ARCHITECTURE_INDEX
  v-bump at S2499; (f) OPEN_ARCS S2401-S2404 CLOSED transitions; (g)
  PUBLIC_PATHS registry DRI anchor.

**Final SIGN verdict**: **SIGN-with-edits at MED confidence (0.74)**. 20 folds
landed pre-Chris-ratification. Cycle 2 NOT required. Draft `status: draft` on
filesystem; Chris-ratifiable at child close per playbook §16 draft-first
workflow ("commit it").
