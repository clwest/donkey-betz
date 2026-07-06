---
title: "API Domain Scoping (Group 2500 — Contract SoT + Silent-401 Downstream Remediation + Session-Lifecycle API Contracts + Per-Endpoint Permission-Floor Registry Design-Prep + REST↔WS T7 Joint 2500+2600)"
session: 2500
status: active (S2500 P0 arc-open 2026-07-05 post-S2499 Group 2400 Auth close; shape-card Chris "agree all" 2026-07-05 ratified 4 items wholesale — Q1 Option C 4-child + P4 retitle "Permission-floor registry design-prep + REST↔WS contract joint (T7)" + Q2 central lens + "OpenAPI as canonical SoT" clause + Q3 7 acceptance criteria including AC#7 scoped API-slice + repeatable measurement harness + Q4 8 anti-scope items including #7 no codegen framework selection + #8 no WS protocol redesign; **Rigby SIGN cycle 1 COMPLETE 2026-07-05 via dedicated fresh isolation pin `pa-0420acab54b74c14` (SEVENTEENTH consecutive dedicated fresh SIGN pin retirement in Research OS after S1399/S1499/S1599/S1699/S1799/S1899/S1999/S2099/S2199/S2299/S2400/S2401/S2402/S2403/S2404/S2499 sixteen prior — retired via `session_tool.retire force=true` at cycle close, updated_count=4, retired=true, previously_active=true) — 6 folds landed pre-Chris-ratification (Q2-1 Cat C→Cat B 803-call-site re-verify owner + Q2-2 S2503→S2504 WS emit re-verify session + Q3-1 AC#7 spec-only guardrail + Q3-2 §API autoblock language de-gravitation + Q4-1 Refutation-would-look-like 4-criteria block + Q4-2 verdict-neutral ternary seam wording); Rigby overall confidence HIGH; Cycle 2 NOT required per explicit Rigby verdict; single-batch × 4-Q cadence SEVENTH-consecutive application at parent-scoping stage after S1899/S1999/S2099/S2199/S2299/S2400 six prior; Chris "commit it" 2026-07-05 ratified SIGN-with-edits wholesale — status flipped `draft` → `active` per playbook §16 draft-first workflow.**)
arc: Research Group 2500 (API — Contract SoT + Silent-401 Downstream Remediation + Session-Lifecycle API Contracts + Per-Endpoint Permission-Floor Registry Design-Prep + REST↔WS T7 Joint 2500+2600, Chris + Claude conceptual)
category: research (playbook §11.1 parent-scoping template ELEVENTH-consecutive application per S2499 canonical summary handoff — prior applications Groups 1300/1400/1500/1600/1700/1800/1900/2000+/2100/2200/2400)
authors: Claude Code (S2500 arc-open draft 2026-07-05; shape-card Rigby SIGN-preview via arc pin `pa-a03b111768464b3f` 2026-07-05 SIGN-with-edits on Q1/Q3/Q4 + SIGN with optional clause on Q2 — all folds landable pre-Chris-ratification; Chris "agree all" 2026-07-05 ratified 4 items wholesale — locked shape); Rigby SIGN cycle 1 on completed draft PENDING via dedicated fresh isolation pin per playbook §15
verifier_loop: >
  Shape-card SIGN-preview via fresh arc pin `pa-a03b111768464b3f`
  2026-07-05 (single-batch × 4-Q preview cadence — NOT the formal
  §15 SIGN cycle; formal cycle runs on completed draft via dedicated
  fresh isolation pin). Rigby verdict: SIGN-with-edits on Q1/Q3/Q4 +
  SIGN with optional clause on Q2; folds landable pre-Chris-
  ratification. Cycle 2 NOT required at shape-card stage.

  Shape-card folds landed pre-Chris-ratification (4 items):
  1. Q1: P4 retitle "Permission-floor registry design-prep + REST↔WS
     contract joint (T7)" — moves F-B-HIGH-1 STAFF_REQUIRED_PATHS
     phantom + F-B-HIGH-4 auth_views_enhanced.py from framing header
     into an audit-findings-appendix inside P4 (still tracked; not
     framing the child as auth cleanup PR). Rationale: prevents P4
     from violating Q4 anti-scope by reading as "auth hardening PR."
  2. Q2: Central lens acquires clause "with OpenAPI as the canonical
     SoT (and typed client as a derived artifact)" — prevents
     interpretive drift into "frontend types are the SoT" (which
     historically justifies api.ts accretion).
  3. Q3: AC#7 added — "Scoped API-slice definition + repeatable
     coverage measurement." Written API-slice manifest (money-path +
     governance-path + PA-path endpoints + WS channels) + repeatable
     script/report spec that can recompute extend_schema coverage,
     permission-floor declaration coverage, typed-response coverage,
     typed-error coverage, and raw-fetch bypass counts. Rationale:
     without harness, AC#1/#4/#5 measurements degrade into "best-
     effort sampling" (debate, not closure).
  4. Q4: Anti-scope #7 + #8 added — "No typed-client/codegen
     framework selection" (openapi-typescript / orval / kubb / etc)
     + "No WebSocket protocol / channel redesign" (message types /
     channel naming / auth handshake). Rationale: prevents the exact
     scope-magnet derails named in Claude's own Q4 tail.

  Rigby SIGN cycle 1 COMPLETE via dedicated fresh isolation pin
  `pa-0420acab54b74c14` (SEVENTEENTH consecutive dedicated fresh SIGN
  pin in Research OS after S1399/S1499/S1599/S1699/S1799/S1899/S1999/
  S2099/S2199/S2299/S2400/S2401/S2402/S2403/S2404/S2499 sixteen prior;
  retired at cycle close via `session_tool.retire`). Single-batch × 4-Q
  cadence per S1899-S2400 SEVEN-consecutive tested pattern (SEVENTH-
  consecutive application at parent-scoping stage). Rigby overall
  confidence: HIGH (with 6 folds landed).

  Verdicts per Q: Q1 SIGN (no folds — coverage complete); Q2 SIGN-
  with-edits (2 folds — Q2-1 803-call-site re-verify owner Cat C→Cat B
  + Q2-2 WS emit-site re-verify session S2503→S2504); Q3 SIGN-with-
  edits (2 folds — Q3-1 AC#7 spec-only guardrail + Q3-2 §API autoblock
  language de-gravitation); Q4 SIGN-with-edits (2 folds — Q4-1 explicit
  refutation criteria block + Q4-2 verdict-neutral ternary seam
  wording).

  6 folds landed pre-Chris-ratification:
  1. Q2-1: `Cat C re-verifies at S2502` → `Cat B re-verifies at S2502`
     for 803 consumer call-sites bullet (consumer inventory is api.ts-
     adjacent, owned by Cat B not Cat C).
  2. Q2-2: `Cat D re-verifies at S2503` → `Cat D re-verifies at S2504`
     for ~40 WS emit sites bullet (Cat D session is S2504 not S2503).
  3. Q3-1: AC#7 acquired sentence "Deliverable is a measurement _spec_
     (commands + report schema + acceptance thresholds), not a shipped
     script or CI job in this arc." — explicit spec-only guardrail
     preventing implementation-gravity misread.
  4. Q3-2: §API autoblock reference acquired clause "proposal-only;
     implementation deferred to a post-arc ADR / separate initiative"
     — de-gravitation preventing Cat A from turning into a tooling
     build.
  5. Q4-1: New "Refutation would look like" block in header (4 concrete
     criteria: spectacular schema generation + core/*.py @extend_schema
     coverage + typed client derivation alignment + permission-floor
     registry derivability without ad-hoc lists) — forces arc to
     actively look for "contract IS coherent" evidence.
  6. Q4-2: "Candidate arc seam" replaced with verdict-neutral ternary
     framing (three outcomes: coherent spine / declared-but-uneven /
     implicit accretion) — Children collect evidence supporting any
     of the three; parent verdict CONFIRMED or REFUTED.

  Cycle 2 NOT required per Rigby explicit "not-required (assuming Q2
  label fixes + Q3 magnet-guard sentences + Q4 refutation criteria +
  ternary seam neutralization are applied)." Chris-ratifiable at
  parent scoping per playbook §16 draft-first workflow.
companion_anchors:
  - docs/PLATFORM_INVENTORY.md                                                # runtime counts anchor (URL Routes 1,864 path() patterns; 209 core/views*.py files; 199 mgmt commands — NO dedicated API contract row)
  - docs/PLATFORM_WHAT_IT_IS.md                                               # narrative anchor
  - docs/research/platform_architecture_inventory.md                          # S1273 32-domain map (nearest row: §3.30 API layer if extant OR §3.27 Auth adjacent for permission-floor context)
  - docs/research/platform/cross_domain_integration_audit.md                  # S1274 cross-domain integration baseline
  - docs/research/DOMAIN_RESEARCH_PLAYBOOK.md                                 # process contract §11.1 ELEVENTH application
  - docs/research/OPEN_ARCS.md                                                # arc manifest (Group 2500 In-progress row at open)
  - docs/research/domains/auth/2499_auth_canonical_summary.md                 # T2 Group 2500 API cross-arc handoff bundle (primary predecessor input)
  - docs/research/domains/auth/2404_frontend_integration_silent_401_systemic_resolution_audit.md   # §19.1 α/β/γ × 2 decision spaces + §14.5 803-consumer classification
  - docs/research/domains/auth/2402_authorization_permission_floor_uniformity_audit.md             # §19.1 (a)/(b)/(c) three-option + §14.5 21-loci permission-floor rate
  - docs/research/domains/auth/2403_session_lifecycle_client_persistence_audit.md                   # §19.1 α/β/γ session lifecycle + 15-surface storageKeys
  - docs/research/domains/frontend/2203_frontend_api_contract_boundary_discipline_audit.md          # §14 F1 SoT-ABSENT + F3 silent-401 + F3.5 whitelist BRITTLE + F4 mega-module + F5 DEAD-CANDIDATE
  - docs/research/domains/frontend/2299_frontend_canonical_summary.md                              # §5.1 canonical seam + §8.2 T2 handoff + §8.3 R6 error-boundary framework
  - docs/research/domains/frontend/2202_frontend_realtime_websocket_consumer_audit.md              # §17 T6 message routing parallels REST + §20.6 envelope enforcement locus DEFER + Path A/B/C
  - frontend/src/lib/api.ts                                                                       # 4194 LOC + 93 apiModule exports + 63 typed / 856 bare (6.85%) + silent-401 sole handler line 48-56 + whitelist BRITTLE
  - sports/views.py                                                                              # drf-spectacular @extend_schema partial-wiring locus (16 decorators)
  - requirements.txt                                                                             # drf-spectacular==0.28.0 (INSTALLED but partial-wired to sports only)
delegated_from:
  - Group 2200 S2203 §14 F1 (contract SoT-ABSENT — no single-source-of-truth for backend API contract; drf-spectacular INSTALLED @0.28.0 but wired only to sports/views.py 16 @extend_schema; core/*.py 0 @extend_schema; api.ts consumes both with untyped inference — 6.85% typed rate = 63 typed / 919 total)
  - Group 2200 S2203 §14 F3 (silent-401 SYSTEMIC at api.ts:48-56 as downstream symptom of contract accretion; ~630 of ~1,300 gated call-sites at silent-401 risk per S2203 A3 grep-based hedged for wrapper duplicates)
  - Group 2200 S2203 §14 F3.5 (auth-endpoint whitelist BRITTLE — MED per Q5 STRENGTHEN; hardcoded substrings `/auth/` + `/login` at api.ts:48-56 scales badly under route evolution)
  - Group 2200 S2203 §14 F4 (api.ts mega-module 4194-LOC + 93 apiModule exports + 407-session churn; god-file with 47 exported interfaces most orphan)
  - Group 2200 S2203 §14 F5 (18 DEAD-CANDIDATE api-modules — unimported or single-import-only inside api.ts itself)
  - Group 2200 S2203 §19.1 R1 (contract SoT design ownership CROSS-ARC DEFERRED to Group 2500 API arc per §20.6 Option (c) + REST-native Path A/B/C triad + escape hatch preserved + fallback clause "or next arc explicitly owning backend API contract design if ownership shifts" per Q11 STRENGTHEN)
  - Group 2200 S2203 §17.3 T7 (REST↔WS transport parallel joint 2500+2600)
  - Group 2200 S2204 §19.3 R3 (canonical User type + workspace_id contract inclusion at API-contract layer — cross-arc coordination flag)
  - Group 2200 S2299 §8.2 T2 (Group 2500 API cross-arc handoff bundle — full aggregation of the above; blast radius 93 api-modules × avg 15 methods = ~1,417 method definitions in api.ts + 47 exported interfaces + ~40 WS emit sites + ~1,300 gated call-sites)
  - Group 2200 S2299 §8.3 R6 (error-boundary framework establishment as BLOCKING PREREQUISITE for typed-error-envelope option-γ)
  - Group 2400 S2404 CF-D1 (typed-error-envelope Cat D α/β/γ decision-space — envelope γ = mechanism; Cat C β = message/UX policy nested inside γ per Cat D Rigby Q6 fold; whitelist replacement γ per-api-module `authHandling: 'default' | 'suppress_redirect'` string enum + telemetry on every suppress_redirect use per Cat D Rigby Q7 fold)
  - Group 2400 S2404 CF-D2 (F-D-CALL-1 803 consumer call-sites at HEAD — 57 direct + 667 hook + 79 raw fetch — ~99% silent-swallow rate; typed-error-envelope adoption is the systemic remediation path)
  - Group 2400 S2404 CF-D3 (F-D-BYPASS-1 79 raw fetch() across 31 files bypass interceptor entirely — 9.8% of surface; reconciliation candidate at api.ts extraction)
  - Group 2400 S2402 CF-B1 (per-endpoint permission registry Cat B (c) decision-space — Group 2400 Cat B PRIMARY = (b) split-read-write + (c) per-endpoint permission registry PRIMARY for LONG-TERM GOVERNANCE)
  - Group 2400 S2402 CF-B3 (F-B-HIGH-1 STAFF_REQUIRED_PATHS 2-of-3 PHANTOM entries — cleanup candidate in P4 findings-appendix)
  - Group 2400 S2402 CF-B4 (F-B-HIGH-4 auth_views_enhanced.py `@authentication_classes([])` + `[IsAuthenticated]` stacking across 4 files — cleanup candidate in P4 findings-appendix)
  - Group 2400 S2403 CF-C1 (refresh endpoint contract F-C-REFRESH-1 — no session-token refresh endpoint exists; Cat C α/β/γ = (α) silent-refresh + (β) explicit re-login (PROPOSED) + (γ) hybrid)
  - Group 2400 S2403 CF-C2 (logout envelope + Clear-Site-Data emission F-C-CSD-1 — zero Clear-Site-Data emission on logout at HEAD)
  - Group 2400 S2403 CF-C3 (F-C-STORE-1 14 of 15 client-side persistence surfaces lack DECLARED logout-cleanup contract — 6.7% declared cleanup rate)
  - Group 2400 S2499 canonical verdict Chris-locked 2026-07-05: "ACCRETION with declared-but-unenforced contracts" — mechanisms generally work at file-precision in the sampled surfaces; contract silently violated across all 4 axes examined; pattern generalizes as one architectural posture, not scattered defects
delegates_to:
  - (arc-close will populate at S2599 xx99)
lens: >
  Central lens question (Chris-locked "agree all" 2026-07-05, Rigby
  SIGN-preview optional clause folded pre-ratification):

  "Does the platform's API surface have a source-of-truth contract
  (typed responses + typed errors + per-endpoint permission floor +
  refresh + logout envelope), with OpenAPI as the canonical SoT (and
  typed client as a derived artifact) — or is it an accretion of
  implicit shapes with drf-spectacular partial-wiring at sports only
  + silent-401 SYSTEMIC downstream symptom?"

  Candidate arc seam (verdict-neutral ternary, Rigby SIGN cycle 1 Q4-2
  fold — replaces prior binary "declared-but-uneven + accretion"
  phrasing that read as verdict-leading): Evidence may support (i) a
  coherent contract spine (OpenAPI as canonical SoT is real and
  broadly adhered to), (ii) declared-but-uneven contracts (SoT exists
  but is inconsistently applied), or (iii) implicit shape accretion
  (contracts are primarily emergent from runtime/client behavior).
  Children must collect evidence supporting any of the three outcomes;
  parent verdict CONFIRMED or REFUTED accordingly. Refutation criteria
  per Rigby Q4-1 fold in header block Refutation-would-look-like
  section (4 criteria; ≥3 refute → coherent spine holds; 0-1 refute
  → accretion holds; 2 refute → declared-but-uneven middle).
playbook_application: §11.1 20-section parent-scoping template ELEVENTH-consecutive application per S2499 canonical summary handoff (prior applications across arcs Groups 1300/1400/1500/1600/1700/1800/1900/2000+/2100/2200/2400 per exemplar chain); §14 verifier-loop REQUIRED CODIFICATION-CONFIRMED discipline applied pre-draft; §15 SIGN cycle 1 REQUIRED at parent scoping per playbook §15 stage-scoped routing — routed via dedicated fresh isolation pin (NOT arc pin `pa-a03b111768464b3f`) per playbook §15 SIGN-isolation discipline; §16 arc pin: `pa-a03b111768464b3f` ACTIVE at S2500 open per TWELFTH formal arc (Groups 1300/1400/1500/1600/1700/1800/1900/2000+/2100/2200/2400 prior = 11 arcs); prior `pa-6279ead1714c4630` retired at S2499 close (Group 2400 Auth arc pin — retired=true, updated_count=25, previously_active=true via `session_tool.retire force=true` per playbook §16 arc-close discipline — ELEVENTH formal arc-pin retirement in Research OS)
arc_open_provenance:
  - Group 2500 API queued NEXT (T2) per S2299 §8.2 T2 handoff bundle + S2499 §8.4 arc-queue standing; alternative candidates per project memory post-S2099 ranking (2300 Mobile / 2500 API / 2600 PA); no D-override invoked at S2500 open — Chris short command "Start research group 2500: API" matches playbook §21 vocabulary + OS §3.2 deterministic route
  - Cross-arc handoff selection signal: 4 of 4 Group 2200 children referenced API contract discipline (S2203 F1 SoT-ABSENT + F3 silent-401 + F3.5 whitelist BRITTLE + F4 mega-module api.ts + F5 DEAD-CANDIDATE modules); ALL 4 Cat A/B/C/D children of Group 2400 emitted CF-*1 flags to Group 2500 (refresh endpoint + logout envelope + Clear-Site-Data + typed-error-envelope + per-endpoint permission registry design-prep + drf-spectacular retrofit)
  - Arc pin `pa-a03b111768464b3f` minted at S2500 open via `session_tool.create_fresh` — TWELFTH formal arc pin under Research OS after Groups 1300/1400/1500/1600/1700/1800/1900/2000+/2100/2200/2400 prior eleven; health check at open: `platform_config_tool overview` = service_context: local ✓ + pin ownership verified as `chris` via `ChatConversation.objects.filter(conversation_id='pa-a03b111768464b3f').user.username='chris'` per feedback_pa_local_verify_ownership.md
  - `tools/pa_local.sh:280` rotated from retired `pa-6279ead1714c4630` to new arc pin `pa-a03b111768464b3f`; header ledger updated with S2400 retirement stanza (Sessions 2400-2404 + S2499 arc summary; ELEVENTH formal arc-pin retirement in Research OS) + S2500 open stanza (TWELFTH formal arc pin under Research OS with full scope description) per S2000/S2100/S2200/S2400 documentation pattern
  - Shape-card Q1-Q4 drafted post-startup + predecessor-input synthesis; presented to Chris in-session 2026-07-05 with Claude leans (Option C 4-child + Q2 verbatim from START-NEXT + 6 AC + 6 anti-scope); Chris routed to Rigby SIGN-preview via arc pin `pa-a03b111768464b3f`
  - Rigby SIGN-preview verdict via arc pin `pa-a03b111768464b3f` 2026-07-05 (single-batch × 4-Q): SIGN-with-edits on Q1/Q3/Q4 + SIGN with optional clause on Q2; 4 folds landable pre-Chris-ratification (P4 retitle + Q2 OpenAPI canonical clause + AC #7 scoped API-slice + repeatable measurement harness + anti-scope #7 no codegen framework + #8 no WS protocol redesign); cycle 2 NOT required
  - Chris "agree all" 2026-07-05 ratified 4 items wholesale — locked Option C 4-child with P4 retitle + Q2 lens with OpenAPI clause + 7 acceptance criteria + 8 anti-scope items
  - Draft written 2026-07-05 post-shape-card ratification; Rigby SIGN cycle 1 on completed draft PENDING via dedicated fresh isolation pin per playbook §15 (parent scoping = required light SIGN); expected cadence single-batch × 4-Q per S1899-S2400 SEVEN-consecutive tested pattern (SEVENTH-consecutive candidate)
---

# Group 2500 — API Domain Scoping (Contract SoT + Silent-401 Downstream Remediation + Session-Lifecycle API Contracts + Per-Endpoint Permission-Floor Registry Design-Prep + REST↔WS T7 Joint 2500+2600)

> **DRAFT.** Formal S2500 arc-open executed 2026-07-05 post-S2499 Group 2400
> Auth canonical summary close. Group 2500 arc pin `pa-a03b111768464b3f`
> minted at open via `session_tool.create_fresh` (TWELFTH formal arc pin
> under Research OS after Groups 1300/1400/1500/1600/1700/1800/1900/2000+/2100/2200/2400
> prior eleven). Shape-card Chris "agree all" 2026-07-05 ratified 4-child
> Option C + central lens + 7 AC + 8 anti-scope with Rigby folds. Rigby
> SIGN cycle 1 on this parent scoping doc PENDING via dedicated fresh
> isolation pin per playbook §15.

> **Central lens question (Chris-locked "agree all" 2026-07-05, Rigby
> SIGN-preview OpenAPI-canonical clause folded):**
>
> *"Does the platform's API surface have a source-of-truth contract
> (typed responses + typed errors + per-endpoint permission floor +
> refresh + logout envelope), with OpenAPI as the canonical SoT (and
> typed client as a derived artifact) — or is it an accretion of
> implicit shapes with drf-spectacular partial-wiring at sports only
> + silent-401 SYSTEMIC downstream symptom?"*

> **Candidate arc seam (verdict-neutral, Rigby SIGN cycle 1 Q4-2 fold
> — replaces prior binary "declared-but-uneven" phrasing that read as
> verdict-leading):** Evidence may support **(i) a coherent contract
> spine** (OpenAPI as canonical SoT is real and broadly adhered to),
> **(ii) declared-but-uneven contracts** (SoT exists but is
> inconsistently applied across endpoint families / consumers), or
> **(iii) implicit shape accretion** (contracts are primarily emergent
> from runtime/client behavior rather than declared). **Children must
> collect evidence that could support any of the three outcomes**, and
> the parent verdict can be **CONFIRMED** or **REFUTED** accordingly.

> **Refutation would look like** (Rigby SIGN cycle 1 Q4-1 fold —
> explicit refutation criteria forcing the arc to actively look for
> "contract IS coherent" evidence):
> 1. `python manage.py spectacular --file schema.yaml` generates a
>    coherent OpenAPI 3.0 schema for at least the money-path +
>    governance-path + PA-path scoped API-slice (S2299 §6 UNKNOWN 5
>    resolves positive at S2501 open).
> 2. `core/*.py` endpoint declarations are consistently @extend_schema-
>    decorated (or evidently derivable) across the scoped slice at
>    HEAD, not just at sports/.
> 3. Typed client derivation (via drf-spectacular's schema output)
>    aligns with runtime responses/errors observed at api.ts
>    consumption points — no silent inference drift.
> 4. Per-endpoint permission-floor registry can be derived directly
>    from `permission_classes` declarations without needing ad-hoc
>    STAFF_REQUIRED_PATHS / PUBLIC_PATHS list-based augmentation.
>
> If ≥3 of the above 4 refute, the "coherent contract spine" verdict
> holds. If 0-1 refute, the accretion end of the seam holds. Mixed
> (2 refute) → "declared-but-uneven" middle seam.

> **API-contract acceptance criteria** (Chris "agree all" 2026-07-05
> — 7 criteria total; #7 added per Rigby SIGN-preview Q3 fold —
> measured-by clauses per S2400 fold precedent):
>
> 1. **Contract SoT observability.** Every gated endpoint at scoped
>    API-slice has a declared schema (OpenAPI 3.0) either via
>    `@extend_schema` or a designed alternative (Path A/B/C from
>    S2203 §20.6).
>    _Measured by: baseline @extend_schema coverage matrix at HEAD
>    (currently 16 in `sports/views.py` + 0 in `core/*.py`) + gap-
>    per-endpoint at scoped API-slice + Chris-D-verdict on Path
>    A/B/C triad + drf-spectacular platform-wide retrofit design-prep.
>    EXPLICITLY NOT a platform-wide `@extend_schema` authoring
>    outcome (Group 2500 execution scope + Group 2500 code-arc T-slot
>    scope); the ARC delivers evidence table + Chris-D-verdict-
>    request across the three-option decision space per S2203
>    §20.6 + §19.1 R1._
> 2. **Typed error envelope contract.** Auth failures + non-2xx
>    responses have a typed envelope contract usable by frontend
>    interceptors.
>    _Measured by: Cat D α/β/γ envelope-shape feasibility mapping
>    (γ = mechanism per Cat D Rigby Q6 fold; whitelist replacement
>    per Cat D Rigby Q7 fold `authHandling: 'default' |
>    'suppress_redirect'` string enum + telemetry) + integration-point
>    spec (top-level ErrorBoundary + interceptor + optional handler
>    override) + Chris-D-verdict resolution. EXPLICITLY NOT a typed-
>    envelope adoption outcome (S2299 §8.3 R6 error-boundary
>    framework establishment is BLOCKING PREREQUISITE for option-γ);
>    the ARC delivers candidate-design + Chris-D-verdict-request._
> 3. **Session-lifecycle API contracts.** Refresh endpoint + logout
>    envelope + Clear-Site-Data emission contracted at API layer
>    (not just frontend behavior).
>    _Measured by: refresh endpoint contract spec (F-C-REFRESH-1
>    downstream) + logout envelope schema (F-C-CSD-1 downstream) +
>    Clear-Site-Data emission discipline + Cat C α/β/γ resolution
>    (Cat C PROPOSED = β explicit re-login as least-assumption
>    default; nested inside envelope γ per Cat D Rigby Q6 fold) +
>    Chris-D-verdict on hybrid vs α vs β for session lifecycle._
> 4. **Per-endpoint permission-floor observability.** Every gated
>    endpoint declares its permission-floor contract; per-endpoint
>    permission registry design-prep matures Group 2400 Cat B (c)
>    input.
>    _Measured by: registry design-prep spec + permission-floor cell
>    per endpoint at scoped API-slice (money-path + governance-path
>    + PA-path) + Chris-D-verdict on (a)/(b)/(c) resolution for
>    scoped surface OR platform-wide. EXPLICITLY NOT a per-endpoint
>    registry authoring outcome (design-prep only per playbook §5
>    phase discipline); the ARC delivers registry-shape proposal +
>    Chris-D-verdict-request. Preserves Group 2400 Cat B PRIMARY =
>    (b) split-read-write + client-side auth-check-on-write for
>    REMEDIATION WINDOW + (c) per-endpoint registry PRIMARY for
>    LONG-TERM GOVERNANCE._
> 5. **REST↔WS message contract strictness joint.** REST↔WS parallel
>    T7 (S2203 §17.3 + S2202 §17 T6) jointly owned with Group 2600
>    PA; message-contract discipline extends to WebSocket emit
>    surface.
>    _Measured by: WS emit-site inventory (~40 sites per S2203) +
>    REST↔WS parallel-message-contract joint-owner spec + Group 2600
>    PA CF hand-off count. EXPLICITLY NOT a WS protocol / channel
>    redesign outcome (Q4 anti-scope #8 — contract joint is inventory
>    + spec-only)._
> 6. **Cross-arc coordination preserved.** Flags to Group 2600 PA
>    (workspace-context resolver + WS↔polling consolidation) +
>    Group 1700 Observability (silent-401 rate telemetry +
>    envelope enforcement locus + `authHandling: 'suppress_redirect'`
>    telemetry per Cat D Rigby Q7 fold) + Group 2300 Mobile
>    (parallel silent-401 audit + 401-handling parity between web +
>    mobile) preserved.
>    _Measured by: xx99 §5.4 cross-arc coordination flag count ≥ 3
>    (Group 2600 PA + Group 1700 Observability + Group 2300 Mobile
>    at minimum); optionally Group 1600 Content + Group 1900
>    Authority Enforcement if load-bearing findings surface._
> 7. **Scoped API-slice definition + repeatable coverage measurement**
>    (Rigby SIGN-preview Q3 fold). Written API-slice manifest +
>    repeatable script/report spec that can recompute coverage rates.
>    Prevents AC #1/#4/#5 measurements from degrading into "best-
>    effort sampling" (debate, not closure).
>    _Measured by: (a) API-slice manifest (money-path + governance-
>    path + PA-path endpoints list + WS channels list — specific
>    endpoint enumeration deferred to Cat A + Cat D scoping at
>    S2501+S2504); (b) repeatable script/report spec that recomputes:
>    `@extend_schema` coverage, permission-floor declaration
>    coverage, typed-response coverage, typed-error coverage, and
>    raw-fetch bypass counts for that slice. Delivered as design-prep
>    (script skeleton + manifest structure), NOT executable at parent
>    scope._ **Deliverable is a measurement _spec_ (commands + report
>    schema + acceptance thresholds), not a shipped script or CI job
>    in this arc** (Rigby SIGN cycle 1 Q3-1 fold — explicit spec-only
>    guardrail preventing implementation-gravity misread).

> **API-contract anti-scope** (Chris "agree all" 2026-07-05 — 8 items
> total; #7 + #8 added per Rigby SIGN-preview Q4 fold):
>
> - **No backend API implementation (no code PR).** Design-preparation
>   only per playbook §5 phase discipline.
> - **No PA behavior spec.** Group 2600 PA scope preserved.
> - **No mobile app API design.** Group 2300 Mobile scope.
> - **No new endpoint authoring at parent scope.** Design-preparation
>   only.
> - **No auth mechanism changes** (no new SSO/OAuth/JWT-vs-opaque).
>   Group 2400 scope preserved per S2400 §7 anti-scope #6 pattern.
> - **No framework migration** (Django-DRF-to-FastAPI, GraphQL,
>   tRPC, etc.). Classic scope magnet.
> - **No typed-client/codegen framework selection** (Rigby SIGN-preview
>   Q4 fold). openapi-typescript / orval / kubb / etc are feasibility-
>   only if discussed; explicitly non-binding at this arc. Framework
>   choice deferred to post-arc ADR OR Group 2500 code-arc T-slot if
>   drf-spectacular Path A ratified.
> - **No WebSocket protocol / channel redesign** (Rigby SIGN-preview
>   Q4 fold). Message types / channel naming / auth handshake changes
>   are OUT-OF-SCOPE at REST↔WS T7 joint; contract joint is inventory
>   + spec-only. WS protocol changes deferred to a targeted post-arc
>   ADR if load-bearing.

---

## 1. Why Phase 0

The Research Operating System calls Phase 0 a **parent-scoping
Session**: propose the child taxonomy + central lens + acceptance
criteria + anti-scope + child mission sequence, then let Chris
ratify BEFORE any child audits run. The playbook §11.1 template
formalizes the shape. This is the ELEVENTH-consecutive application
of that template (after Groups 1300/1400/1500/1600/1700/1800/1900/
2000+/2100/2200/2400 prior ten).

The Group 2500 API scope is materially different from prior arcs
in three ways that justify the Phase 0 gate:

1. **Three-arc convergent handoff bundle.** Group 2500 API is the
   endpoint of three prior arcs' CROSS-ARC DEFERRED contract work:
   - Group 2200 S2203 §20.6 Option (c) DEFER contract SoT design
     to Group 2500 API arc close with escape hatch + Path A/B/C
     triad;
   - Group 2400 Cat A/B/C/D emitted 7 CF-*1 flags to Group 2500
     (refresh endpoint + logout envelope + Clear-Site-Data +
     typed-error-envelope + per-endpoint permission registry design-
     prep + drf-spectacular retrofit + F-B-HIGH-1/HIGH-4 auth
     cleanup);
   - Group 2200 S2203 §17.3 T7 REST↔WS transport parallel joint
     2500+2600.
   Phase 0 pressure-tests the taxonomy for completeness across all
   three handoff bundles WITHOUT collapsing distinct decision axes
   into a monolith (Q1 shape-card fold prevented Option B's P3
   overloading).

2. **§3.30 API layer baseline (or nearest) — inventory-only, not
   a contract.** The 32-domain map does not carry a dedicated
   `API contract` row equivalent to §3.27 Auth's threat-model gap
   flag. API surface is inventoried indirectly via `PLATFORM_INVENTORY`
   URL Routes (1,864 `path()` patterns) + Django View Files (209
   `core/views*.py`) + Management commands (199). Phase 0 declares
   the arc's research posture on the contract gap: is the arc's
   deliverable an API-contract topic doc (like `docs/topics/api.md`
   analog to `docs/topics/auth.md` shipped at S2499 close) + a
   §3.30-analog runtime-inventory row + a §Auth-autoblock-analog
   `inventory_gathers().api` extension? Playbook §5 phase discipline
   anchors research-only + design-prep at parent scope; formal
   deliverables from parent + 4 children promoted to `docs/topics/`
   + `PLATFORM_INVENTORY §API` at S2599 xx99 close if load-bearing.

3. **MC-14 threshold-satisfied pattern (Group 2400 confirmation +
   Group 2500 candidate ELEVENTH-consecutive 4-child arc).** Per
   S2499 xx99 §10.2 MC-14 fold, "arc-pin preservation across ALL
   children of a 4-child arc as CHECKABLE §16 rule" reached
   CANDIDATE (threshold satisfied; pending Chris ratification
   wording) at 2 arc applications (Group 2100 + Group 2200). Group
   2400 = FIFTH arc application (Groups 1900/2000+/2100/2200/2400
   FIFTH-consecutive), which resolves the S2199 Q3 STRENGTHEN dial-
   back to CODIFICATION-CONFIRMED (per S2499 xx99 §10.2 fold).
   Group 2500 = SIXTH-consecutive 4-child arc candidate — extends
   MC-14 stability + MC-4 CODIFICATION-CONFIRMED-with-scope-
   guardrails to sixth-consecutive baseline. **Group 2500 is not a
   stress-test arc for MC-14; it is a consolidation arc that
   confirms MC-4/MC-14 durability across a materially-different
   scope shape** (contract-and-envelope surface, not
   authentication-and-authorization surface).

**Runtime target: 6 sessions.** Matches Groups 1600 through 2400
precedent (parent + 4 children + xx99 canonical summary). Runtime
cap: 8. Never invoked in prior 4-child arcs; invoke only if a
child requires split (candidate: Cat A backend contract SoT if
core/*.py 0-decorator scope requires per-app subdivision).

---

## 2. What existing inventory already tells us

> **Evidence-provenance disclaimer.** Numeric counts + file:line
> anchors in §2 (and where they recur in §3 child scopes) are a
> mix of **RUNTIME-VERIFIED at HEAD `4e6c1ee8`** and **ESTIMATE**
> inherited from prior arcs. Each Cat re-verifies its cited numbers
> at HEAD at child open (per Group 2400 §2 evidence-provenance
> disclaimer pattern established S2400 Rigby Q4 fold):
>
> - `api.ts 4194 LOC` — RUNTIME-VERIFIED at HEAD `4e6c1ee8` via
>   `wc -l frontend/src/lib/api.ts`.
> - `93 apiModule exports` — RUNTIME-VERIFIED at HEAD via
>   `grep -c "^export const \w\+Api" frontend/src/lib/api.ts`.
> - `63 typed api.method<> + 856 bare = 919 total; 6.85% typed
>   rate` — RUNTIME-VERIFIED at HEAD via
>   `grep -c "api\.\(get\|post\|patch\|delete\|put\)<"` +
>   `grep -oE "api\.(get|post|patch|delete|put)\("`.
> - `16 @extend_schema in sports/views.py + 0 in core/*.py` —
>   RUNTIME-VERIFIED at HEAD via `grep -c "@extend_schema" sports/views.py`
>   + `grep -rl "@extend_schema" core/*.py`.
> - `drf-spectacular==0.28.0 INSTALLED` — RUNTIME-VERIFIED via
>   `grep drf-spectacular requirements.txt`.
> - `~1,300 gated call-sites` — ESTIMATE per S2203 A3 grep-based
>   hedged for wrapper duplicates (S2299 §8.2 T2 explicit hedge);
>   Cat B re-verifies at S2502 HEAD via full call-site inventory.
> - `~40 WS emit sites` — ESTIMATE per S2203 §17.3; Cat D re-verifies
>   at S2504 HEAD via full WS emit-site inventory (Rigby SIGN cycle 1
>   Q2-2 fold — Cat D session is S2504 not S2503).
> - `803 consumer call-sites (57 direct + 667 hook + 79 raw fetch)`
>   — RUNTIME-VERIFIED at S2404 HEAD per F-D-CALL-1; Cat B re-verifies
>   at S2502 HEAD in case new hooks / raw fetches landed since S2404
>   close (Rigby SIGN cycle 1 Q2-1 fold — consumer inventory is
>   frontend / api.ts-adjacent, owned by Cat B not Cat C).
> - `47 exported interfaces + 18 DEAD-CANDIDATE api-modules` —
>   ESTIMATE per S2203 §14 F4 + F5; Cat B re-verifies at S2502 HEAD.
> - `1,864 URL Routes + 209 core/views*.py files + 199 mgmt commands`
>   — RUNTIME INVENTORY per PLATFORM_INVENTORY.md Git HEAD `e617af59`
>   (2026-07-05); not ESTIMATE. Regenerate via
>   `python manage.py generate_platform_inventory` if drift observed
>   at S2501 open.

### 2.1 Runtime anchor (PLATFORM_INVENTORY — no dedicated API contract row)

`PLATFORM_INVENTORY.md` (Git HEAD `e617af59`, generated 2026-07-05)
does NOT carry a dedicated API contract section. API surfaces
appear implicitly:
- **URL Routes** — 1,864 `path()` patterns across `core/urls*.py`
  files. §3.30 API layer baseline (or nearest §3.27 Auth adjacent
  for permission-floor context) reports these as the aggregate
  endpoint inventory.
- **Django View Files** — 209 files matching `core/views*.py`; the
  majority declare no `@extend_schema` decorator (0 decorators in
  `core/*.py` per HEAD verification).
- **Django Management Commands** — 199 commands; some are API-
  adjacent (schema generation, contract validation) but no
  spectacular-linked management command exists (only
  `python manage.py spectacular --file schema.yaml` untested per
  S2299 §6 UNKNOWN 5).
- **`sports/views.py`** — sole @extend_schema-declaring module at
  HEAD; 16 decorators applied across sports subsurface.

**Anchor drift observation.** No `PLATFORM_INVENTORY §API` sub-
section exists — API contracts are inventoried indirectly via
routes + views + management commands. This is DIFFERENT from
Frontend (which has `§Frontend` autoblock post-S2299) and from
Auth (which has `§Auth` autoblock CREATED at S2499 close per
AU-1+AU-B2+AU-C2+AU-D3 fold). S2500 §7 will consider whether an
`inventory_gathers().api` extension is warranted (P1 Cat A output
candidate) analog to Auth's §Auth autoblock work at S2499 close.

### 2.2 32-domain map (S1273 platform_architecture_inventory nearest row)

The 32-domain map does NOT explicitly enumerate a dedicated "API
Contract" or "API Layer" row. Nearest relevant rows:
- **Row 27 Auth / Permissions / Security** — PARTIAL + LIGHT
  (Group 2400 scope; permission-floor uniformity here per S2402
  §14.5 21-loci — cross-boundary shared with Group 2500 API scope
  via per-endpoint permission registry).
- **Row 30 API layer (or equivalent) — TBD baseline** — Cat A P1
  re-verifies whether §3.30 exists as authored or requires
  synthesis at S2501 open; if absent, S2599 xx99 §7.3 recommends
  adding §3.30 to platform_architecture_inventory + a `docs/
  topics/api.md` companion (analog to Group 2400's `docs/topics/
  auth.md` CREATE at S2499 close per AU-D2 + AU-D7 fold).

**Research coverage baseline (inherited from adjacent-domain
reviews):**
- Group 2200 S2203 §14 F1 identified contract SoT-ABSENT as a
  systemic-across-frontend finding but explicitly deferred owning
  arc to Group 2500 API per §20.6 Option (c) + Path A/B/C triad.
- No prior arc has authored an API-contract research doc at
  Group 2500's proposed scope (backend contract SoT + typed-error-
  envelope + refresh + logout envelope + per-endpoint permission-
  floor registry + REST↔WS T7 joint).

**Architecture maturity:** PARTIAL (implied from S2203 F1
SoT-ABSENT; formal maturity assessment authored at S2501 open Cat
A §13).

**Risk:** MEDIUM-HIGH (inherited from S2299 §8.4 T2 handoff
priority signal: "Group 2500 API owns the infrastructure gate —
drf-spectacular INSTALLED but wired only in `sports/views.py`;
extending to `core/*.py` unlocks generated typed client for
`frontend/` via `openapi-typescript` or `orval`" — but framework
choice deferred per Q4 anti-scope #7).

### 2.3 Group 2200 T2 cross-arc handoff bundle (S2299 §8.2)

The primary load-bearing input from Group 2200 close. S2299 §8.2
T2 aggregates findings across Group 2200 Child C (Frontend API
Contract-Boundary Discipline Audit S2203):
- **S2203 §14 F1 (SoT-ABSENT — SYSTEMIC).** No single-source-of-truth
  for backend API contract. drf-spectacular INSTALLED @0.28.0
  but partial-wired to sports/ only (16 @extend_schema); core/*.py
  has 0 @extend_schema. api.ts consumes both with untyped
  inference (6.85% typed rate). **Confirmed structural evidence at
  whole-file scale (macro-evidence anchor per S2203 Q8 STRENGTHEN
  dual-evidence framing).**
- **S2203 §14 F3 (silent-401 SYSTEMIC).** api.ts:48-56 sole 401
  handler; ~630 of ~1,300 gated call-sites at silent-401 risk
  (grep-based hedged for wrapper duplicates per Q14 STRENGTHEN).
  CRITICAL for money-path (betting.placeBet, wager settlement,
  billing.stripe) + governance-path (humanApi.decide) endpoints.
- **S2203 §14 F3.5 (auth-endpoint whitelist BRITTLE — MED).**
  Whitelist substring `/auth/` + `/login` hardcoded in api.ts:48-56.
  Classic-footgun scales-badly-under-route-evolution per Q5
  STRENGTHEN.
- **S2203 §14 F4 (api.ts mega-module).** 4194-LOC + 93 apiModule
  exports + 407-session churn (extraction candidate per S2203 R4
  + F5 DEAD-CANDIDATE cleanup).
- **S2203 §14 F5 (18 DEAD-CANDIDATE api-modules).** Unimported or
  single-import-only inside api.ts itself (potential 18-module
  cleanup at api.ts extraction).

**REST-native Path A/B/C triad (S2203 §20.6):**
- **Path A** — Full drf-spectacular retrofit across `core/*.py` +
  generated typed client via `openapi-typescript`. High infrastructure
  investment; unlocks typed client universally.
- **Path B** — Selective @extend_schema for money-path + governance-
  path only + manual TypeScript for rest (hybrid, prioritizes high-
  risk surfaces).
- **Path C** — Middle-ground: @extend_schema for integrity /
  governance / money / state-changing flows + AllowAny discipline
  for read-only public paths + no codegen framework selection at
  parent scope.
- **Escape hatch preserved (Q11 STRENGTHEN):** "or next arc
  explicitly owning backend API contract design if ownership
  shifts."

Owner: Group 2500 API (this arc). Blast radius: 93 api-modules ×
avg 15 methods = ~1,417 method definitions in api.ts; 47 exported
interfaces (most orphan); ~40 WS emit sites; ~1,300 gated call-
sites (permission-floor overlap with Group 2400).

### 2.4 Group 2400 CF-*1 handoff bundle (S2499 §5.4 cross-arc flags)

The secondary load-bearing input from Group 2400 close. S2499 xx99
§5.4 cross-arc coordination flags emit to Group 2500:
- **CF-D1 (typed-error-envelope Cat D α/β/γ decision-space).**
  - **α**: React Query global onError + interceptor override per
    module. Simpler mechanism; risks silent-degrade at boundary
    edges.
  - **β**: Interceptor-only + typed AxiosError catches inline at
    every consumer. Highest visibility; highest boilerplate cost.
  - **γ (PROPOSED PRIMARY per Cat D Rigby Q6 fold)**: RQ error
    callback + top-level ErrorBoundary. γ = mechanism; Cat C β
    "explicit re-login" = message/UX policy nested inside γ.
    Requires S2299 §8.3 R6 error-boundary framework establishment
    as BLOCKING PREREQUISITE.
- **CF-D2 (F-D-CALL-1 803 consumer call-sites remediation).** 57
  direct + 667 hook + 79 raw fetch = 803 total at HEAD; ~99%
  silent-swallow rate. Typed-error-envelope adoption is the
  systemic remediation path (option-γ execution).
- **CF-D3 (F-D-BYPASS-1 79 raw fetch reconciliation).** 79 raw
  fetch() across 31 files bypass interceptor entirely (9.8% of
  surface). Reconciliation candidate at api.ts extraction — either
  (a) migrate all raw fetch to api. methods + interceptor coverage,
  or (b) explicit fetch-through-interceptor pattern per surface
  with documented exceptions.
- **CF-B1 (per-endpoint permission registry Cat B (c) design-prep).**
  Group 2400 Cat B PRIMARY = (b) split-read-write + client-side
  auth-check-on-write for REMEDIATION WINDOW + (c) per-endpoint
  permission registry PRIMARY for LONG-TERM GOVERNANCE. Group 2500
  matures (c) into design-prep spec.
- **CF-B3 (F-B-HIGH-1 STAFF_REQUIRED_PATHS 2-of-3 PHANTOM).** 2
  of 3 staff-required path entries in
  `UnifiedTokenAuthenticationMiddleware.STAFF_REQUIRED_PATHS` are
  PHANTOM (route paths that don't exist at HEAD). Cleanup
  candidate in P4 findings-appendix.
- **CF-B4 (F-B-HIGH-4 auth_views_enhanced.py stacking).** 4 files
  in `auth_views_enhanced.py` stack `@authentication_classes([])`
  + `[IsAuthenticated]` (conflict). Cleanup candidate in P4
  findings-appendix.
- **CF-C1 (F-C-REFRESH-1 refresh endpoint contract).** No session-
  token refresh endpoint exists at HEAD. Cat C α/β/γ = (α) silent-
  refresh + (β) explicit re-login (Group 2400 PROPOSED PRIMARY as
  least-assumption default per Cat C α/β/γ decision-space) + (γ)
  hybrid.
- **CF-C2 (F-C-CSD-1 Clear-Site-Data emission).** Zero
  Clear-Site-Data emission on logout at HEAD. Contract-level
  addition candidate to logout endpoint response envelope.
- **CF-C3 (F-C-STORE-1 14/15 client-side storage surfaces lack
  DECLARED logout-cleanup contract).** 6.7% declared cleanup rate
  at HEAD; contract-level API-response-based cleanup coordination
  candidate.

### 2.5 Adjacent-domain baseline

- **`docs/research/domains/frontend/2299_frontend_canonical_summary.md`
  §5.1** — Canonical seam statement: "React-frontend contract
  discipline as a whole is NOT canonical." Verdict pattern: 3 of
  4 falsifier tests resolve SYSTEMIC + 1 resolves SURFACE-LOCAL.
  Group 2500's central lens directly extends S2299 §5.1's frontend-
  scoped seam upstream through backend contract layer.
- **`docs/research/domains/auth/2499_auth_canonical_summary.md`** —
  Group 2400 canonical verdict: "ACCRETION with declared-but-
  unenforced contracts." Group 2500's candidate seam mirrors the
  pattern at contract-shape layer: "declared-but-uneven contracts +
  implicit shape accretion."
- **`docs/topics/frontend.md`** — Stale-warned at Group 2200 arc;
  refresh explicitly deferred to post-S2299 follow-on cascade per
  S2299 §7.4 fold. Group 2500's Cat B may re-surface stale-warning
  status at S2502 open.
- **`docs/topics/auth.md`** — CREATED at S2499 close per AU-D2 +
  AU-D7 fold. Group 2500's parallel deliverable candidate:
  `docs/topics/api.md` CREATE at S2599 xx99 close if load-bearing.

### 2.6 Documentation baseline (gap-flagging per playbook §11.2 §11)

**Existing.**
- `docs/research/platform_architecture_inventory.md` nearest row
  (§3.30 API layer if extant OR §3.27 Auth adjacent for
  permission-floor context).
- Group 2200 S2203 §14 F1-F5 findings (SoT-ABSENT + silent-401 +
  whitelist + mega-module + DEAD-CANDIDATE).
- Group 2400 S2404 §14.5 803-consumer classification (57 direct
  + 667 hook + 79 raw fetch).
- Group 2200 S2202 §17 T6 REST↔WS message routing parallels.

**Gap (S2500 arc-scope identifies these).**
- **No API-contract topic doc.** No `docs/topics/api.md` exists
  (compare `docs/topics/auth.md` CREATED at S2499 close for shape).
  Analog to Group 2400's Auth-surface-topic-doc gap; parallel
  deliverable candidate at S2599 xx99 close if load-bearing.
- **No API-slice manifest.** No written enumeration of money-path
  + governance-path + PA-path endpoints + WS channels exists at
  HEAD. Cat A + Cat D scoping at S2501 + S2503 delivers this per
  AC #7.
- **No repeatable coverage measurement harness.** No script/report
  spec exists to recompute @extend_schema coverage, permission-
  floor declaration coverage, typed-response coverage, typed-error
  coverage, and raw-fetch bypass counts. AC #7 (Rigby SIGN-preview
  Q3 fold) mandates design-prep of this harness.
- **No PLATFORM_INVENTORY §API autoblock.** Cat A P1 output
  candidate — **proposal-only; implementation deferred to a post-arc
  ADR / separate initiative** (Rigby SIGN cycle 1 Q3-2 fold —
  autoblock language de-gravitation preventing Cat A from turning
  into a tooling build).
- **No trust-boundary inventory at API layer.** Group 2400 Cat A
  delivered auth-mechanism trust-boundary inventory; Group 2500
  Cat A delivers API-endpoint-permission-floor trust-boundary
  inventory (per AC #4).

---

## 3. Candidate subdomain taxonomy

Four child audit slots (Chris-locked "agree all" 2026-07-05,
Rigby SIGN-preview Q1 P4-retitle fold applied), each targeting one
of the four contract axes surfaced by the S2299 T2 + S2499 CF-*1
handoff bundles. Option C 4-child taxonomy ratified over Option A
(2-child too narrow; permission registry + REST↔WS T7 orphaned)
and Option B (3-child; P3 conflates 5 distinct Chris-D-verdict
axes).

### A — P1 Cat A: Backend API contract SoT design-prep (S2501)

**Mission:** Establish research-only + design-prep baseline for
backend API contract source-of-truth. Enumerate `@extend_schema`
coverage at HEAD (16 sports + 0 core), gap-per-endpoint at scoped
API-slice, generated-client feasibility (Path A/B/C from S2203
§20.6), and drf-spectacular platform-wide retrofit design-prep.

**Scope (S2501 P1 20-section child audit):**
- **§3 Canonical Entry Points:** `sports/views.py` (16 @extend_schema
  decorators as HEAD baseline) + `core/*.py` (0 decorators baseline)
  + `drf-spectacular==0.28.0` INSTALLED (in `requirements.txt`) +
  `python manage.py spectacular --file schema.yaml` (untested per
  S2299 §6 UNKNOWN 5).
- **§4 Major Models:** DRF `Serializer` + `ModelSerializer` hierarchy
  + declared @extend_schema payload types.
- **§5 Major Services:** drf-spectacular schema generator + any
  spectacular-linked management commands + CI schema validation
  hooks (if any).
- **§6 Major APIs:** All URL-registered endpoints inventoried at
  HEAD (1,864 path() patterns) vs. @extend_schema-decorated subset
  (16 declared vs. 1,848 undeclared).
- **§7 Runtime Flows:** Request → view → serializer → response
  path; @extend_schema declaration → spectacular schema.yaml →
  generated typed client (if Path A ratified).
- **§9 Integrations With Other Domains:** All 32-domain map rows
  that consume/expose API endpoints; specifically sports (already
  wired), betting (money-path candidate), governance/decisions
  (governance-path candidate), pa (pa-path candidate), content
  (content-path adjacent).
- **§14 Known Drift:** SoT-ABSENT F1 (RE-VERIFY at HEAD); Path
  A/B/C triad status; drf-spectacular schema.yaml generation
  feasibility (S2299 §6 UNKNOWN 5 → resolve at S2501 open via
  first execution step).
- **§19 Recommended Future Research:** Chris-D-verdict on Path
  A/B/C triad; drf-spectacular platform-wide retrofit design-
  prep; PLATFORM_INVENTORY §API autoblock proposal; `docs/topics/
  api.md` CREATE proposal.

**Findings inheritance:** S2203 §14 F1 SoT-ABSENT.

**Cross-arc coordination:** Group 2400 (permission-floor overlap
via per-endpoint registry design-prep in P4); Group 2200 (S2203
§20.6 Path A/B/C escape hatch preserved).

**Blast radius baseline:** 1,864 URL routes + 209 core/views*.py
files at HEAD `e617af59`; 16 @extend_schema (sports) + 0
@extend_schema (core) = 16 of ~1,864 = ~0.86% declaration rate at
HEAD (Cat A verifies exact denominator at S2501 open).

### B — P2 Cat B: Frontend API-client architecture design-prep (S2502)

**Mission:** Establish research-only + design-prep baseline for
frontend API-client architecture. api.ts 4194-LOC extraction
feasibility (S2203 R4), 93 apiModule inventory + typed-rate
tracking (63/919 = 6.85% at HEAD), DEAD-CANDIDATE cleanup (18
modules per S2203 §14 F5), raw-fetch bypass reconciliation (79
across 31 files per S2404 F-D-BYPASS-1), and interceptor coverage
matrix.

**Scope (S2502 P2 20-section child audit):**
- **§3 Canonical Entry Points:** `frontend/src/lib/api.ts` (4194
  LOC + 93 apiModule exports at HEAD) + all consumer sites (803
  total per S2404 §14.5 = 57 direct + 667 hook + 79 raw fetch).
- **§4 Major Models:** 47 exported TypeScript interfaces (most
  orphan per S2203 §14 F4) + 93 apiModule exports.
- **§5 Major Services:** api.ts as god-file (407-session churn per
  S2203 §14 F4); axios interceptor (silent-401 handler at line
  48-56).
- **§6 Major APIs:** 93 apiModule × avg 15 methods = ~1,417 method
  definitions in api.ts + hook wrappers (~667 hook consumer call-
  sites).
- **§7 Runtime Flows:** Consumer → api.moduleName.methodName() →
  axios → interceptor → backend; typed vs. bare method-call rate
  per module.
- **§9 Integrations With Other Domains:** All frontend consumer
  surfaces (Workspace / Betting / Command Center / PA / Neural
  Orchestra / Revenue / Advisor etc.); WS emit-site parallel
  (P4 REST↔WS T7 joint).
- **§14 Known Drift:** mega-module F4 (RE-VERIFY 4194 at HEAD);
  DEAD-CANDIDATE F5 (RE-VERIFY 18 at HEAD); raw-fetch bypass F-D-
  BYPASS-1 (RE-VERIFY 79 at HEAD).
- **§19 Recommended Future Research:** api.ts extraction design-
  prep (module-split strategy + per-module ownership); DEAD-
  CANDIDATE cleanup batch (18 modules); raw-fetch bypass
  reconciliation options.

**Findings inheritance:** S2203 §14 F4 mega-module + F5 DEAD-
CANDIDATE + S2404 F-D-BYPASS-1 raw-fetch + F-D-CALL-1 803-call-site
classification.

**Cross-arc coordination:** Group 2400 (silent-401 systemic
downstream symptom); Group 2200 (S2203 R4 api.ts extraction).

**Blast radius baseline:** 4194 LOC + 93 apiModule + 47 interfaces
+ 803 consumer sites (RE-VERIFY at HEAD `4e6c1ee8`).

### C — P3 Cat C: Error-envelope + refresh + logout API contracts design-prep (S2503)

**Mission:** Establish research-only + design-prep baseline for
typed-error-envelope contract (Cat D α/β/γ from S2499 CF-D1),
refresh endpoint contract (F-C-REFRESH-1 downstream from S2499
CF-C1), logout envelope + Clear-Site-Data emission (F-C-CSD-1
downstream from S2499 CF-C2), and logout cleanup contract via API
envelope (F-C-STORE-1 6.7%-declared-rate downstream from S2499
CF-C3).

**Scope (S2503 P3 20-section child audit):**
- **§3 Canonical Entry Points:** logout endpoint + refresh endpoint
  (F-C-REFRESH-1 = MISSING at HEAD) + Clear-Site-Data response
  header emission + api.ts interceptor + Zustand persist logout
  hygiene.
- **§4 Major Models:** typed-error envelope shape candidate
  (Cat D α/β/γ mechanisms); refresh-token flow model; logout
  response envelope + Clear-Site-Data spec.
- **§5 Major Services:** DRF-level error serialization (or lack
  thereof); Django logout view; Clear-Site-Data emission point
  candidate.
- **§6 Major APIs:** logout endpoint at HEAD + candidate refresh
  endpoint spec + candidate typed-error envelope endpoints per
  gated-endpoint-slice.
- **§7 Runtime Flows:** logout → clear tokens → clear localStorage
  → emit Clear-Site-Data → redirect; refresh → issue new token →
  respond → update client cache; auth-failure → typed envelope →
  interceptor → handler → UI surface.
- **§9 Integrations With Other Domains:** Group 2400 Cat C 15-
  surface storageKeys cleanup contract; Group 2200 Cat C stale
  paStore fields cleanup coordination.
- **§14 Known Drift:** F-C-REFRESH-1 MISSING (RE-VERIFY at HEAD);
  F-C-CSD-1 zero-emission-rate (RE-VERIFY at HEAD); F-C-STORE-1
  6.7%-declared-rate (RE-VERIFY 14/15 at HEAD).
- **§19 Recommended Future Research:** Cat D α/β/γ typed-error-
  envelope Chris-D-verdict-request; refresh endpoint contract
  spec; logout envelope + Clear-Site-Data emission spec; logout
  cleanup contract via API envelope coordination.

**Findings inheritance:** S2499 CF-D1 typed-error-envelope Cat D
α/β/γ + CF-C1 F-C-REFRESH-1 + CF-C2 F-C-CSD-1 + CF-C3 F-C-STORE-1.

**Cross-arc coordination:** Group 2400 Cat C session-lifecycle α/β/γ
(β PROPOSED as message/UX policy nested inside envelope γ per Cat D
Rigby Q6 fold); Group 2400 Cat D typed-error-envelope Cat D α/β/γ
(γ PROPOSED PRIMARY as mechanism); Group 1700 Observability (silent-
401 rate telemetry + envelope enforcement locus).

**Blast radius baseline:** 803 consumer call-sites (typed-error-
envelope adoption target); 15 client-side persistence surfaces
(logout cleanup contract target); 1 missing refresh endpoint;
1 missing Clear-Site-Data emission (RE-VERIFY at HEAD).

### D — P4 Cat D: Permission-floor registry design-prep + REST↔WS contract joint (T7) (S2504)

**Mission (Rigby SIGN-preview Q1 P4-retitle fold — retitled to
prevent P4 from reading as "auth hardening PR" per Q4 anti-scope):**
Establish research-only + design-prep baseline for per-endpoint
permission-floor registry (Cat B (c) LONG-TERM GOVERNANCE per
S2499 CF-B1) + REST↔WS message contract strictness joint 2500+2600
(S2203 §17.3 T7 + S2202 §17 T6).

**Scope (S2504 P4 20-section child audit):**
- **§3 Canonical Entry Points:** `core/auth_middleware.py`
  (STAFF_REQUIRED_PATHS + REVIEWER_BLOCKED_PATHS + PUBLIC_PATHS —
  centralized list-based permission floor) + all `@extend_schema`-
  declaring views (permission-floor declaration candidate at
  view-level via `permission_classes` DRF attribute) + WebSocket
  consumers (~40 emit sites per S2203 §17.3 — permission-floor
  parallel at WS layer).
- **§4 Major Models:** permission_classes DRF attribute + custom
  Permission classes (`FleetCapabilityRequired` + service-token
  gates) + WS-layer authentication middleware (from Group 2400
  F-WS-1 findings).
- **§5 Major Services:** DRF permission dispatcher + WS consumer
  auth middleware + per-endpoint permission registry candidate
  service (design-prep target).
- **§6 Major APIs:** All 1,864 URL-registered endpoints + ~40 WS
  channels + their permission-floor declarations (RE-VERIFY per-
  endpoint at S2504 HEAD).
- **§9 Integrations With Other Domains:** Group 2400 Cat B (a)/
  (b)/(c) decision-space (matures (c) into design-prep spec);
  Group 2600 PA (workspace-context authz for WS channels; REST↔WS
  joint owner).
- **§14 Known Drift:** F-B-CRIT-1 permission-floor implicit-
  inheritance ~80-90% (RE-VERIFY at HEAD); F-B-CRIT-2 silent-401
  SYSTEMIC (symptom of permission-floor accretion — validated in
  S2404); REST↔WS parallel T7 (message contract discipline extends
  to WS emit surface).
- **§19 Recommended Future Research:** Per-endpoint permission
  registry design-prep spec + Chris-D-verdict-request on scope
  (money-path + governance-path + PA-path first vs. platform-wide);
  REST↔WS message contract joint 2500+2600 spec + Group 2600 PA
  CF hand-off.

**Findings inheritance:** S2499 CF-B1 per-endpoint permission
registry Cat B (c) + S2203 §17.3 T7 REST↔WS parallel + S2202 §17
T6 message routing.

**Cross-arc coordination:** Group 2400 (Cat B (c) matured into
design-prep); Group 2600 PA (REST↔WS T7 joint owner + workspace-
context authz).

**Findings-appendix (Rigby SIGN-preview Q1 P4-retitle fold —
moved from framing header to appendix to prevent P4 reading as
auth cleanup PR):**
- **F-B-HIGH-1 STAFF_REQUIRED_PATHS 2-of-3 PHANTOM entries**
  (S2499 CF-B3): 2 of 3 staff-required path entries in
  `UnifiedTokenAuthenticationMiddleware.STAFF_REQUIRED_PATHS` are
  PHANTOM (route paths that don't exist at HEAD). Cleanup candidate
  at post-arc T-slot OR follow-on PR post-S2504.
- **F-B-HIGH-4 auth_views_enhanced.py `@authentication_classes([])`
  + `[IsAuthenticated]` stacking** (S2499 CF-B4): 4 files in
  `auth_views_enhanced.py` stack conflicting decorators. Cleanup
  candidate at post-arc T-slot OR follow-on PR post-S2504.

**Blast radius baseline:** 1,864 URL routes + ~40 WS emit sites +
21-loci permission-floor rate (S2402 §14.5 baseline; RE-VERIFY at
S2504 HEAD).

### Explicit non-candidates

- **Payment / billing API contract design.** Adjacent domain
  (billing.stripe + revenueApi) — inventoried at Cat A + Cat B but
  design-prep for payment-flow-specific contracts deferred to
  targeted post-arc ADR if load-bearing.
- **Content Studio API contracts.** Group 1600 Content scope; API
  layer inventoried at Cat A but contract-shape decisions owned by
  Group 1600 semantically.
- **Advisor / Governance API contracts.** Group 1900 Authority
  Enforcement + Group 1800 HumanAttention semantic scope; API
  layer inventoried at Cat A + Cat D but semantic contracts owned
  by respective arcs.
- **PA-side WS contract mutations.** Group 2600 PA scope; REST↔WS
  T7 joint owns the parallel-message-contract inventory + spec
  ONLY, not PA-side WS behavior.
- **Discord bot API surface.** Adjacent domain (48 slash + 48
  prefix + 25 Cog classes per PLATFORM_INVENTORY.md); not in
  Group 2500 API arc scope at parent scoping (candidate for
  targeted post-arc research if load-bearing).
- **Fleet HMAC signature contract.** Group 2400 Cat A scope
  preserved (permissive-fallback classification); Group 2500 Cat D
  may reference at permission-floor overlap but no re-authoring.

### §3.5 API-adjacent probes disposition

> Rigby SIGN-preview Q1 fold context (S2400 §3.5 pattern
> established S2400 Rigby cycle 1 Q1 fold): explicit disposition
> of API-adjacent probes as in-scope evidence vs non-candidates
> prevents scope-drift.

| Probe | Disposition | Rationale |
|-------|-------------|-----------|
| OpenAPI 3.0 vs 3.1 fork | **NON-CANDIDATE** at parent scope | Format-version choice = Path A implementation detail; deferred to Path A ADR if ratified |
| Typed-client codegen framework (openapi-typescript / orval / kubb) | **NON-CANDIDATE** per Q4 anti-scope #7 | Framework selection is a scope magnet; feasibility-only if discussed |
| gRPC / GraphQL / tRPC framework | **NON-CANDIDATE** per Q4 anti-scope #6 | Framework migration = classic scope magnet |
| API versioning strategy (v1/v2) | **NON-CANDIDATE at parent scope** | Endpoint-level design decision; deferred to per-endpoint ADR |
| Rate limiting per endpoint | **IN-SCOPE at Cat D permission-floor** | Adjacent to permission-floor discipline; inventoried as declared-vs-undeclared per endpoint |
| CORS policy contract | **NON-CANDIDATE** at parent scope | Adjacent to Auth arc + platform-security-unifier scope; deferred to security-review ADR |
| Idempotency key contract | **NON-CANDIDATE at parent scope** | Money-path specific; deferred to targeted ADR if Cat A slice discovery surfaces load-bearing gap |
| Pagination contract discipline | **IN-SCOPE at Cat A contract SoT** | Standard DRF pagination = declared-in-contract; verify @extend_schema declares pagination shape per endpoint |
| Response caching + ETag contract | **NON-CANDIDATE** at parent scope | HTTP-level; deferred to Group 1700 Observability adjacent |
| WebSocket protocol version | **NON-CANDIDATE** per Q4 anti-scope #8 | Explicit anti-scope Q4 #8 |
| Auth handshake for WS channels | **IN-SCOPE at Cat D REST↔WS joint** | Permission-floor parallel at WS layer; inventoried but no protocol change |
| API telemetry envelope (per Group 1700) | **CROSS-ARC FLAG** to Group 1700 | Cross-arc coordination flag per AC #6 |

**Cross-cutter posture guardrail** (mirror S2400 §3.5 pattern):
API-adjacent probes NOT in the disposition table above are
NON-CANDIDATES at parent scope by default; Cat A + Cat B + Cat C
+ Cat D may re-surface probe candidacy at child scoping with
Chris-D-verdict route.

---

## 4. Parent-vs-single recommendation

**Recommendation: PARENT-WITH-4-CHILDREN.** Chris-locked "agree
all" 2026-07-05 shape-card Q1 ratification.

**Arithmetic verification (per S2299 §10.4 §4 arithmetic-verification
anti-pattern mitigation established S2200 Q11 FOLD 2026-07-05):**

Prior 4-child arcs at S2500 arc-open (Groups 1900/2000+/2100/2200/2400):
- Group 1900 Authority Enforcement (S1900-S1904 + S1999) — 4 children
- Group 2000+ Event/Integration (S2000-S2004 + S2099) — 4 children
- Group 2100 RAG/Document Loading (S2100-S2104 + S2199) — 4 children
- Group 2200 Frontend Contract-Surface (S2200-S2204 + S2299) — 4 children
- Group 2400 Auth (S2400-S2404 + S2499) — 4 children

Group 2500 API = **SIXTH-consecutive parent-with-4-children arc**
(if Chris ratifies P4 as 4th child per Q1 shape-card). Extends MC-4
CODIFICATION-CONFIRMED-with-scope-guardrails to SIXTH-consecutive
baseline; extends MC-14 CANDIDATE (threshold-satisfied) to 3rd arc
application (Group 2100 + Group 2200 + Group 2500 candidate; Group
2400 was 5th arc-pin preservation across all children per S2499
xx99 §10.2 fold — Group 2500 = 6th at close if runtime target met).

**Rationale (Q1 shape-card):**
- Option A (2 children) is too narrow — permission registry + REST↔WS
  T7 joint would be orphaned.
- Option B (3 children) compresses P3 into 5 distinct Chris-D-verdict
  axes (typed-error-envelope + refresh + logout + Clear-Site-Data +
  permission registry) — conflates independent decision spaces.
- Option C (4 children) preserves clean seams: backend contract SoT
  (P1) + frontend consumer architecture (P2) + error/refresh/logout
  API contracts (P3) + permission registry + REST↔WS joint (P4) —
  each child = 1 dominant Chris-D-verdict axis + supplemental
  design-prep spec.

**Runtime target: 6 sessions.** Matches Groups 1600 through 2400
precedent.

**Runtime cap: 8.** Never invoked in prior 4-child arcs; invoke
only if Cat A's core/*.py 0-decorator scope requires per-app
subdivision at S2501 open.

---

## 5. Child mission sequence (Chris-locked "agree all" 2026-07-05)

**Sequence:** S2501 → S2502 → S2503 → S2504 → S2599 xx99 canonical
summary.

**Rationale (Chris shape-card Q1 fold + Rigby Q1 seam-clarification
fold):** Cat A (backend contract SoT) precedes Cat B (frontend
consumer) because frontend consumer patterns depend on backend
contract SoT posture (Path A/B/C affects extraction strategy);
Cat C (error/refresh/logout API contracts) follows Cat B because
error-envelope design depends on api-client architecture context;
Cat D (permission registry + REST↔WS joint) is terminal because
it consumes Cat A (permission-floor declarations at view level)
+ Cat B (WS parallel at emit-site level) + Cat C (envelope
interaction with 401/403 refresh) simultaneously.

| Session | Child | Focus | Blast radius | Inheritance |
|---------|-------|-------|--------------|-------------|
| S2501 | P1 Cat A | Backend API contract SoT design-prep | 16 @extend_schema / 1,864 URL routes / 209 core/views*.py files / drf-spectacular==0.28.0 | S2203 §14 F1 SoT-ABSENT + §20.6 Path A/B/C |
| S2502 | P2 Cat B | Frontend API-client architecture design-prep | 4194 LOC api.ts / 93 apiModule / 6.85% typed / 18 DEAD-CANDIDATE / 803 call-sites | S2203 §14 F4 + F5 + S2404 F-D-CALL-1 + F-D-BYPASS-1 |
| S2503 | P3 Cat C | Error-envelope + refresh + logout API contracts | 803 call-sites (typed-error) + 15 storage surfaces (logout cleanup) + 1 missing refresh + 1 missing CSD | S2499 CF-D1 + CF-C1 + CF-C2 + CF-C3 |
| S2504 | P4 Cat D | Permission-floor registry design-prep + REST↔WS contract joint (T7) | 1,864 URL routes + ~40 WS emit sites + 21-loci permission-floor rate | S2499 CF-B1 + S2203 §17.3 T7 + S2202 §17 T6 |
| S2599 | xx99 | Canonical summary + arc close | Consolidated + cross-arc handoff bundle emit | All above |

**Rigby SIGN cycle 1 per child (§15):** 4-batch × 5-Q cadence per
S2201-S2404 nine-consecutive tested pattern (TENTH-consecutive
candidate per S2499 §10 fold). Dedicated fresh isolation pin per
child (NOT arc pin) per playbook §15 SIGN-isolation discipline;
retire at each child cycle close via `session_tool.retire`.

**Arc-pin preservation:** `pa-a03b111768464b3f` preserved through
all 4 children + S2599 xx99 = 6 routing sessions per playbook §16
arc-standard behavior (MC-4 CODIFICATION-CONFIRMED-with-scope-
guardrails SIXTH-consecutive candidate).

---

## 6. Parked candidate issues

Items surfaced during shape-card synthesis that are load-bearing
but NOT in Group 2500 arc scope. Parked for post-arc ADR or
targeted follow-on research if Chris re-raises.

- **P-1: PLATFORM_INVENTORY §API autoblock creation.** Analogous
  to Group 2400's §Auth autoblock CREATED at S2499 close per
  AU-1+AU-B2+AU-C2+AU-D3 fold. Deferred to Cat A output (S2501)
  as recommendation; formal autoblock code addition at follow-on
  cascade PR post-S2599 xx99.
- **P-2: `docs/topics/api.md` CREATE.** Analog to `docs/topics/
  auth.md` CREATED at S2499 close per AU-D2 + AU-D7 fold. Deferred
  to S2599 xx99 close recommendation; formal doc addition at
  follow-on cascade PR post-S2599 xx99.
- **P-3: ARCHITECTURE_INDEX §1.NN decision matrix pointer for
  Group 2500 α/β/γ decision spaces.** Cat A Path A/B/C + Cat C
  Cat D α/β/γ + Cat D permission registry (a)/(b)/(c) — three
  decision matrices from Group 2500 execution. Deferred to
  post-arc cascade PR analog to Group 2400 AU-D6.
- **P-4: drf-spectacular schema.yaml generation feasibility
  (S2299 §6 UNKNOWN 5 resolution).** `python manage.py spectacular
  --file schema.yaml` untested at S2299 close. **Resolution at
  S2501 P1 first execution step** — verifies whether existing 16
  @extend_schema decorators produce a working OpenAPI 3.0 spec.
- **P-5: Typed-client codegen framework decision (per Q4 anti-
  scope #7).** Feasibility-only at Group 2500; framework choice
  deferred to post-arc ADR OR Group 2500 code-arc T-slot if
  drf-spectacular Path A ratified. Candidate frameworks:
  openapi-typescript / orval / kubb.
- **P-6: WebSocket protocol / channel redesign (per Q4 anti-scope
  #8).** Explicitly OUT-OF-SCOPE at REST↔WS T7 joint; deferred to
  targeted post-arc ADR if load-bearing.
- **P-7: F-B-HIGH-1 STAFF_REQUIRED_PATHS 2-of-3 PHANTOM cleanup
  (S2499 CF-B3).** Move from Cat D framing to findings-appendix
  per Rigby Q1 P4-retitle fold; execution at post-arc T-slot or
  follow-on PR post-S2504.
- **P-8: F-B-HIGH-4 auth_views_enhanced.py stacking cleanup
  (S2499 CF-B4).** Move from Cat D framing to findings-appendix
  per Rigby Q1 P4-retitle fold; execution at post-arc T-slot or
  follow-on PR post-S2504.
- **P-9: Discord bot API surface (48 slash + 48 prefix + 25 Cog
  classes per PLATFORM_INVENTORY).** Adjacent domain; NON-CANDIDATE
  at Group 2500 (see §3 Explicit non-candidates). Candidate for
  targeted post-arc research if Discord contract discipline
  becomes load-bearing.
- **P-10: Rate limiting per endpoint (in-scope at Cat D permission-
  floor per §3.5 disposition).** Inventoried as declared-vs-
  undeclared per endpoint; if load-bearing, spawn targeted rate-
  limit ADR post-arc.
- **P-11: Pagination contract discipline (in-scope at Cat A
  contract SoT per §3.5 disposition).** Verify @extend_schema
  declares pagination shape per endpoint at S2501 open; if
  load-bearing, spawn pagination ADR post-arc.

---

## 7. Anti-scope

Referenced from header block. Reiterated here for §11.1 template
completeness:

- **No backend API implementation (no code PR).** Design-preparation
  only per playbook §5 phase discipline.
- **No PA behavior spec.** Group 2600 PA scope preserved.
- **No mobile app API design.** Group 2300 Mobile scope.
- **No new endpoint authoring at parent scope.** Design-preparation
  only.
- **No auth mechanism changes** (no new SSO/OAuth/JWT-vs-opaque).
  Group 2400 scope preserved per S2400 §7 anti-scope #6 pattern.
- **No framework migration** (Django-DRF-to-FastAPI, GraphQL,
  tRPC, etc.). Classic scope magnet.
- **No typed-client/codegen framework selection** (Rigby SIGN-preview
  Q4 fold). openapi-typescript / orval / kubb / etc are feasibility-
  only if discussed; explicitly non-binding at this arc.
- **No WebSocket protocol / channel redesign** (Rigby SIGN-preview
  Q4 fold). Message types / channel naming / auth handshake changes
  are OUT-OF-SCOPE at REST↔WS T7 joint; contract joint is inventory
  + spec-only.

---

## 8. Decisions recorded (Chris-locked "agree all" 2026-07-05)

Ratified at S2500 arc-open post-shape-card Chris "agree all"
2026-07-05:

1. **Central lens question** (with OpenAPI-canonical clause) — Q2
   fold from Rigby SIGN-preview.
2. **Option C 4-child taxonomy** with P4 retitle "Permission-floor
   registry design-prep + REST↔WS contract joint (T7)" — Q1 fold
   from Rigby SIGN-preview.
3. **7 acceptance criteria** with measured-by clauses + AC #7
   scoped API-slice + repeatable coverage measurement — Q3 fold
   from Rigby SIGN-preview.
4. **8 anti-scope items** with #7 no codegen framework selection +
   #8 no WS protocol redesign — Q4 fold from Rigby SIGN-preview.
5. **Runtime target 6 sessions** matching Groups 1600 through 2400
   precedent.
6. **Arc pin `pa-a03b111768464b3f`** ACTIVE — TWELFTH formal arc
   pin under Research OS.

Pending (not yet locked):
- **Rigby SIGN cycle 1 verdict on completed draft** (this document).
  Expected cadence single-batch × 4-Q per S1899-S2400 SEVEN-
  consecutive tested pattern (SEVENTH-consecutive candidate). Fold
  record populated post-SIGN in verifier_loop frontmatter.
- **Chris ratification of completed draft** ("commit it" candidate).
  Status flips `draft` → `active` on ratification per playbook §16
  draft-first workflow.

---

## 9. Next step

**Immediate (S2500 session close):**
1. Route completed draft to Rigby SIGN cycle 1 via dedicated fresh
   isolation pin per playbook §15 (parent scoping = required light
   SIGN; single-batch × 4-Q cadence).
2. Fold SIGN edits into draft; retire SIGN pin at cycle close via
   `session_tool.retire` (SEVENTEENTH consecutive dedicated fresh
   SIGN pin retirement in Research OS after S1399/S1499/S1599/
   S1699/S1799/S1899/S1999/S2099/S2199/S2299/S2400/S2401/S2402/
   S2403/S2404/S2499 sixteen prior).
3. Present Chris ratification card with Rigby SIGN + Claude leans;
   Chris "commit it" ratifies → status flip `draft` → `active`.
4. Post-commit 4-step docs cascade (`build_docs_index` +
   `build_rag_corpus` + `sync_docs_index_to_documents` +
   `sync_docs_index_to_documents --embed`) + `build_docs_provenance`
   per feedback_docs_cascade_at_every_close + feedback_cascade_pr_
   must_include_embed_step. Include chunk count in PR body.
5. ARCHITECTURE_INDEX v88 → v89 with §1.NN registration.
6. OPEN_ARCS Group 2500 row transition Not-started → In-progress.
7. tools/pa_local.sh header ledger already updated with S2400
   retirement stanza + S2500 open stanza (completed at arc-open).
8. Handoff `docs/handoffs/SESSION_2500_API_PARENT_SCOPING.md`.
9. Overwrite `00-START-NEXT-SESSION.md` with S2501 P1 Cat A first-
   child priorities.

**Next arc session (S2501 P1 Cat A):**
1. Mint fresh SIGN isolation pin (NOT arc pin) via `session_tool
   action=create_fresh` per playbook §15.
2. Read startup + arc pin state + this parent scoping doc §3.A +
   inheritance list.
3. First execution step: RESOLVE S2299 §6 UNKNOWN 5 via `python
   manage.py spectacular --file schema.yaml` (verifies drf-
   spectacular actually generates working OpenAPI 3.0 spec from
   existing 16 @extend_schema decorators).
4. Draft the S2501 20-section child audit per playbook §11.2.
5. Route to Rigby SIGN cycle 1 via dedicated fresh isolation pin;
   4-batch × 5-Q cadence per S2201-S2404 nine-consecutive tested
   pattern (TENTH-consecutive candidate).
6. Fold + present Chris ratification card; Chris ratifies →
   status draft → active.
7. Retire SIGN pin at cycle close via `session_tool.retire`.
8. Docs cascade + handoff + overwrite 00-START-NEXT-SESSION with
   S2502 P2 priorities.

---

## Appendix — Frontmatter provenance

**Draft provenance (S2500 arc-open 2026-07-05):**
- HEAD at draft time: `4e6c1ee8` (S2404 P4 Cat D merge PR #2915).
- Arc pin minted: `pa-a03b111768464b3f` via `session_tool
  create_fresh` on retired Group 2400 pin `pa-6279ead1714c4630`
  (retired via `session_tool.retire force=true` at S2499 close;
  updated_count=25, retired=true, previously_active=true — ELEVENTH
  formal arc-pin retirement in Research OS).
- Fresh arc pin ownership verified as `chris` via
  `ChatConversation.objects.filter(conversation_id='pa-a03b111768464b3f').user.username='chris'`.
- Fresh arc pin health check via `platform_config_tool overview`
  = `service_context: local` ✓ + `railway_environment: local` ✓ +
  `database_name: unified_donkey_betz` ✓ + `default_llm_provider:
  openai` ✓.
- `tools/pa_local.sh:280` rotated from retired `pa-6279ead1714c4630`
  to new arc pin `pa-a03b111768464b3f`; header ledger updated with
  S2400 retirement stanza + S2500 open stanza per S2000/S2100/
  S2200/S2400 documentation pattern.
- Shape-card Q1-Q4 drafted post-startup + predecessor-input
  synthesis; routed to Rigby SIGN-preview via arc pin
  `pa-a03b111768464b3f` (single-batch × 4-Q preview cadence — NOT
  formal §15 SIGN cycle).
- Rigby SIGN-preview verdict 2026-07-05: SIGN-with-edits on Q1/Q3/Q4
  + SIGN with optional clause on Q2 (4 folds landable pre-Chris-
  ratification; cycle 2 not required).
- Chris "agree all" 2026-07-05 ratified 4 items wholesale — locked
  shape.
- Full parent scoping doc drafted 2026-07-05 with locked shape
  incorporated at frontmatter + header block + §3 taxonomy + §3.5
  probes disposition + §4 arithmetic + §5 sequence + §6 parked +
  §7 anti-scope + §8 decisions + §9 next-step.

**HEAD-verified runtime baselines at draft time (`4e6c1ee8`):**
- api.ts: 4194 LOC + 93 apiModule exports + 63 typed / 856 bare =
  919 total; 6.85% typed rate.
- sports/views.py: 16 @extend_schema decorators.
- core/*.py: 0 @extend_schema decorators.
- drf-spectacular==0.28.0 INSTALLED in requirements.txt.
- PLATFORM_INVENTORY.md Git HEAD `e617af59` (2026-07-05): 1,864
  URL Routes + 209 core/views*.py files + 199 mgmt commands.

**Rigby SIGN cycle 1 on completed draft: PENDING** via dedicated
fresh isolation pin per playbook §15.

**Chris "commit it" ratification: PENDING** post-SIGN fold. Status
`draft` → `active` on ratification.

**Arc pin preservation:** `pa-a03b111768464b3f` ACTIVE through
S2500 arc-open (no retirement until S2599 xx99 close per playbook
§16 arc-standard behavior — TWELFTH formal arc pin, SIXTH-consecutive
4-child arc candidate).
