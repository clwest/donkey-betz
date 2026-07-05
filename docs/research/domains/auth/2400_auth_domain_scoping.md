---
title: "Auth Domain Scoping (Group 2400 — Session Lifecycle + Permission Floor + Silent-401 Resolution)"
session: 2400
status: active (formal S2400 arc-open 2026-07-05 post-S2299 Group 2200 Frontend close; Chris "commit it" 2026-07-05 ratified post-Rigby SIGN cycle 1 SIGN-with-edits fold — status flipped `draft` → `active` per playbook §16 draft-first workflow; Chris D-override at S2299 close "agree all + (6) = 2400 Auth" 2026-07-05 ratified Auth over any playbook §22 default queue lean, per highest cross-arc-handoff-frequency signal (4/4 Group 2200 children reference silent-401 + logout cleanup + session lifecycle + permission-floor uniformity — S2201 §14.3 + §15.5 + S2202 no-drift-but-perms-floor-owned-here + S2203 §14 F3 + F3.5 + S2204 §19.1 R1); **Rigby SIGN cycle 1 SIGN-with-edits at Medium-High confidence 2026-07-05 via dedicated fresh isolation pin `pa-32400781523b4d5b` (retired at cycle close via `session_tool.retire` per playbook §15 SIGN-isolation discipline); 4 folds landed pre-Chris-ratification: (1) new §3.5 Auth-adjacent probes disposition addressing token rotation / JWT vs opaque / CSRF / session fixation / rate limiting / audit logging / MFA / lockout / SSO / cookie defaults + cross-cutter posture guardrail; (2) §7.1 Cat B + Cat D leak-vector guardrails strengthened with MEASURE-CLASSIFY-RECOMMEND explicit framing + anti-pattern-to-avoid callouts + S2203 A3 ~40% untraced sample referenced; (3) header acceptance criteria block augmented with per-criterion "_Measured by:_" clauses for #1-#6 to prevent Group 2500 registry-authoring drift + Group 2500 API contract SoT drift; (4) new §2 evidence-provenance disclaimer marking inherited numeric counts + file:line anchors as ESTIMATE with per-Cat re-verification-at-HEAD requirement + one preserved SPECULATIVE flag (cookie defaults). Rigby verdict: SIGN-with-edits (not NEEDS-MORE); Chris-ratifiable at parent scoping per playbook §16 draft-first workflow.**)
arc: Research Group 2400 (Auth — Session Lifecycle + Permission Floor + Silent-401 Resolution framing, Chris + Claude conceptual)
category: research (playbook §11.1 parent-scoping template TENTH application per S2299 canonical summary)
authors: Claude Code (S2400 arc-open draft 2026-07-05; Chris shape-card ratification "agree all" 2026-07-05 locked 4-children + central lens + 6-criterion acceptance + 6-item anti-scope; Rigby SIGN cycle 1 SIGN-with-edits at Medium-High confidence 2026-07-05 via dedicated fresh isolation pin pa-32400781523b4d5b retired at cycle close; 4 folds landed pre-Chris-ratification per verifier_loop field below)
verifier_loop: >
  Rigby SIGN cycle 1 (2026-07-05) via dedicated fresh isolation pin
  `pa-32400781523b4d5b` (per playbook §15 SIGN-isolation discipline;
  retired at cycle close via `session_tool.retire`). Single-batch × 4-Q
  cadence per S1899 + S1999 + S2099 + S2199 + S2299 five-consecutive
  tested pattern (MC-10 SIXTH-consecutive application candidate at
  parent-scoping stage).

  Rigby overall confidence: Medium-High. Most accurate part: Q1 taxonomy
  + Group 1900 boundary preservation correctly stated + consistently
  maintained. Weakest part: Q4 evidence/citation precision — inherited
  counts + file:line anchors read "verified" at parent scope but are
  estimate-/drift-prone. Missing area: explicit disposition of auth-
  adjacent probes (CSRF / rate-limiting / brute-force / audit logging /
  session fixation / JWT vs opaque / token rotation) as in-scope
  evidence vs non-candidates. Overstated scope: acceptance criteria #1
  reads like guarantees a full endpoint-registry outcome (Group 2500
  scope). Biggest structural risk: Q2 anti-scope leak via acceptance
  criteria #1 + #2 read as implying registry-authoring / envelope-
  adoption. What Claude got wrong: nothing conceptual — precision/wording
  only. Final verdict: **SIGN-with-edits**.

  Folds landed pre-Chris-ratification (4 items):
  1. Added §3.5 Auth-adjacent probes disposition (12-row disposition
     table + cross-cutter posture guardrail) — addresses Rigby "missing
     area" + Q1 probe-list-not-dispositioned. Location: between §3
     Explicit non-candidates and §4 Parent-vs-single recommendation.
  2. Strengthened §7.1 Cat B + Cat D leak-vector guardrails with
     MEASURE-CLASSIFY-RECOMMEND explicit framing + anti-pattern-to-
     avoid callouts + S2203 A3 ~40% untraced sample reference —
     addresses Rigby "biggest structural risk" (Q2 anti-scope leak).
  3. Augmented header acceptance criteria block with per-criterion
     "_Measured by:_" clauses for #1-#6 — addresses Rigby "make
     acceptance criteria measurable" + prevents Group 2500 registry-
     authoring drift + Group 2500 API contract SoT drift.
  4. Added §2 evidence-provenance disclaimer marking ~108 PUBLIC_PATHS
     + ~630 call-sites + 15 persistent-state surfaces + file:line
     anchors as ESTIMATE with per-Cat re-verification-at-HEAD
     requirement — addresses Rigby "harden SPECULATIVE/ESTIMATE
     labeling". One SPECULATIVE flag preserved (cookie defaults).

  Cycle 2 NOT required per Rigby cycle-1 Medium-High confidence + all
  folds landable pre-Chris-ratification. Chris-ratifiable at parent
  scoping per playbook §16 draft-first workflow ("commit it").
companion_anchors:
  - docs/PLATFORM_INVENTORY.md                                                # runtime counts anchor
  - docs/PLATFORM_WHAT_IT_IS.md                                               # narrative anchor
  - docs/research/platform_architecture_inventory.md                          # S1273 32-domain map row 27 (Auth / Permissions / Security — PARTIAL + LIGHT after S1273 v2 Rigby review)
  - docs/research/platform/cross_domain_integration_audit.md                  # S1274 cross-domain integration baseline
  - docs/research/DOMAIN_RESEARCH_PLAYBOOK.md                                 # process contract §11.1 TENTH application
  - docs/research/OPEN_ARCS.md                                                # arc manifest (Group 2400 In-progress row at open)
  - docs/research/domains/frontend/2299_frontend_canonical_summary.md         # T1 Group 2400 Auth cross-arc handoff bundle (§8.2 T1)
  - docs/research/domains/frontend/2201_frontend_routes_pages_layouts_components_audit.md   # §14.3 cockpit two-stage auth + §15.5 silent-401 systemic
  - docs/research/domains/frontend/2203_frontend_api_contract_boundary_discipline_audit.md  # §14 F3 silent-401 SYSTEMIC + F3.5 whitelist BRITTLE
  - docs/research/domains/frontend/2204_frontend_session_state_persistence_discipline_audit.md  # §19.1 R1 session lifecycle + F1 15-surface storageKeys
  - docs/research/governance_authority_evolution.md                           # §2.5 36-45 primitives (adjacent authority plane)
  - docs/EMPLOYEE_OS_PRIMITIVES.md                                            # GovernanceState + KillSwitch runtime consumers
  - core/auth_middleware.py                                                   # UnifiedTokenAuthenticationMiddleware (~108 PUBLIC_PATHS + STAFF_REQUIRED_PATHS + REVIEWER_BLOCKED_PATHS)
  - core/services/fleet_auth_drf.py                                           # FleetSignatureAuthentication HMAC + permissive fallback
  - core/vip_middleware.py                                                    # VIP demo prompt-only (no runtime gate)
  - frontend/src/lib/api.ts                                                   # silent-401 sole handler line 48-56 + whitelist BRITTLE
delegated_from:
  - Group 2200 S2201 §14.3 (cockpit redirect two-stage auth MINOR-DRIFT), §15.5 (silent 401 as frontend default at api.ts:48-56 — cross-arc dependency)
  - Group 2200 S2202 (no drift found at Child B; permission-floor uniformity owned here per xx99 §5.4 (i))
  - Group 2200 S2203 §14 F3 (silent-401 SYSTEMIC via api.ts:48-56 whole-frontend ~100% swallow rate; ~630 of ~1,300 gated call-sites at silent-401 risk per S2203 A3 grep-based hedged for wrapper duplicates), §14 F3.5 (auth-endpoint whitelist substring `/auth/` + `/login` hardcoded BRITTLE — MED per Q5 STRENGTHEN classic-footgun scales-badly-under-route-evolution)
  - Group 2200 S2204 §19.1 R1 (session lifecycle model + localStorage cleanup contract HIGH priority; two-sided FE-symptom-vs-BE-model framing mirror S2203 §14 F3), §14 F1 inventory (15 persistent-state surfaces potentially affected — 12 direct localStorage keys + 3 Zustand persist stores), §14 F6 + F8 (no-cleanup-on-logout systemic across authStore + workspaceStore + paStore)
  - Group 2200 S2299 §8.2 T1 (Group 2400 Auth cross-arc handoff bundle — full aggregation of the above four axes; three-option decision space (a) uniform IsAuthenticated across all `/v1/**` + client-side auth-gate + observable-error surfacing; (b) uniform AllowAny for read paths + IsAuthenticated for writes + client-side auth-check-on-write; (c) per-endpoint permission registry)
  - Group 1900 S1999 canonical summary (authority-vs-authentication plane demarcation — authority_enforcement covers authority DECISION plane; Group 2400 covers authentication + authorization + session-lifecycle + trust-boundary planes; scope guardrail preserved)
delegates_to:
  - (arc-close will populate)
lens: >
  Central lens question (Chris-locked "agree all" 2026-07-05, Rigby
  SIGN-preview-with-edits tightened wording folded pre-ratification):

  "Is the platform's auth model a contract (explicit trust
  boundaries + declared permission floors + declared
  session/refresh/logout semantics + consistent failure surfacing),
  or an accretion of per-surface defaults whose failures are
  silently swallowed (e.g., silent 401 / permissive fallbacks /
  ad-hoc public path lists)?"

  Canonical seam candidate: "defaults that silently swallow failure
  vs contracts that surface failure" — extends the S2299 Group 2200
  frontend framing upstream through backend middleware + DRF
  permission classes + PA workspace context + Fleet HMAC boundary.
playbook_application: §11.1 20-section parent-scoping template TENTH application per S2299 canonical summary handoff (prior applications across arcs Groups 1300/1400/1500/1600/1700/1800/1900/2000+/2100/2200 per exemplar chain; specific §11.1 skipped-arc identification deferred to S2499 xx99 close if load-bearing per S2200 §playbook_application precedent); §14 verifier-loop REQUIRED CODIFICATION-CONFIRMED discipline applied pre-draft; §15 SIGN cycle 1 OPTIONAL-LIGHT at parent scoping per playbook §15 stage-scoped routing — Chris to gate directly OR route via dedicated fresh isolation pin (NOT arc pin `pa-6279ead1714c4630`) per playbook §15 SIGN-isolation discipline; §16 arc pin: `pa-6279ead1714c4630` ACTIVE at S2400 open per ELEVENTH formal arc (Groups 1300/1400/1500/1600/1700/1800/1900/2000+/2100/2200 prior = 10 arcs); prior `pa-f7fd5016600f4513` retired at S2299 close (Group 2200 Frontend Contract-Surface Arc — retired=true via session_tool.retire per playbook §16 arc-close discipline)
arc_open_provenance:
  - Chris D-override at S2299 close 2026-07-05 ratified Group 2400 = Auth via "agree all + (6) = 2400 Auth" per highest cross-arc-handoff-frequency signal (4/4 Group 2200 children reference silent-401 + logout cleanup + session lifecycle + permission-floor uniformity); MC-4 dial-back-resolution 5th confirming arc candidate
  - S2400 shape-card presented to Rigby via arc pin `pa-6279ead1714c4630` 2026-07-05 with 3 taxonomy options + central lens draft + 5-criterion acceptance from start-here + 5-item anti-scope from start-here; Rigby SIGN-preview-with-edits verdict — Option C 4-child STRONG + tightened lens wording (remove "five surfaces" count, foreground failure-mode pivot) + 6th acceptance criterion (Trust boundary inventory is explicit and testable) + 6th anti-scope (No new auth provider additions SSO/OAuth at parent scope)
  - Chris shape-card ratification card presented 2026-07-05 with Claude + Rigby leans per Q1-Q4; Chris "agree all" 2026-07-05 ratified all 4 items wholesale — locked Option C 4-children + Rigby-tightened lens verbatim + 6-criterion acceptance + 6-item anti-scope
  - Arc pin `pa-6279ead1714c4630` minted at S2400 open via `session_tool.create_fresh` — ELEVENTH formal arc pin (health_check pending Rigby session_tool.health_check at first substantive turn)
  - `tools/pa_local.sh:280` rotated to new pin + header ledger updated with S2200 retirement (pa-f7fd5016600f4513) + S2400 open (pa-6279ead1714c4630) stanzas per S2000/S2100/S2200 documentation pattern; pin ownership verified as chris via `session_tool whoami` at S2400 arc-open turn 2 (conversation_owner_match=true) per feedback_pa_local_verify_ownership.md
  - Draft written 2026-07-05 post-shape-card ratification; Rigby SIGN cycle 1 OPTIONAL-LIGHT at parent scoping per playbook §15 — Chris to gate directly OR route via dedicated fresh isolation pin
---

# Group 2400 — Auth Domain Scoping (Session Lifecycle + Permission Floor + Silent-401 Resolution)

> **DRAFT.** Formal S2400 arc-open executed 2026-07-05 post-S2299 Group 2200
> Frontend (Contract-Surface Arc) canonical summary close per Chris D-override
> ratification "agree all + (6) = 2400 Auth" 2026-07-05. Group 2400 arc pin
> `pa-6279ead1714c4630` minted at open via `session_tool.create_fresh`.
> Rigby SIGN cycle 1 OPTIONAL-LIGHT on this parent scoping per playbook §15.

> **Central lens question (Chris-locked "agree all" 2026-07-05):**
>
> *"Is the platform's auth model a contract (explicit trust boundaries +
> declared permission floors + declared session/refresh/logout semantics +
> consistent failure surfacing), or an accretion of per-surface defaults
> whose failures are silently swallowed (e.g., silent 401 / permissive
> fallbacks / ad-hoc public path lists)?"*
>
> **Auth-contract acceptance criteria** (Chris "agree all" 2026-07-05
> — 6 criteria total; #6 added per Rigby SIGN-preview fold; measured-by
> clauses added per Rigby SIGN cycle 1 Q3 fold — 2026-07-05):
>
> 1. **Permission-floor observability.** Every gated endpoint declares its
>    permission-floor contract observably (client + server agree).
>    _Measured by: Cat B endpoint-inventory matrix (permission-floor cell
>    per endpoint) + permission-untraced-rate reduced from S2203 A3
>    baseline ~40% toward zero. Explicitly NOT a per-endpoint registry
>    authoring outcome (Group 2500 scope); the ARC delivers an evidence
>    table + Chris-D-verdict-request across the three-option decision
>    space per S2203 §19.1 R2._
> 2. **Failure surfacing.** Auth failures surface to caller with typed error
>    envelope (silent-401 anti-pattern extinct).
>    _Measured by: Cat D api.ts:48-56 audit + silent-401 call-site
>    classification (money/governance/read/write) + typed-envelope
>    candidate-design mapping. Explicitly NOT a typed-envelope adoption
>    outcome (Group 2500 API + Group 2200 T-slot R6 error-boundary
>    framework scope); the ARC delivers a candidate-design + Chris-D-
>    verdict-request._
> 3. **Logout cleanup contract.** Logout eagerly clears all client-side
>    per-user storage per declared cleanup contract.
>    _Measured by: Cat C 15-surface storageKeys cleanup-table per surface
>    (declared vs accidental) + Zustand persist logout hygiene evidence._
> 4. **Session lifecycle discipline.** Token refresh discipline (silent-refresh
>    vs explicit re-login) is declared + observable.
>    _Measured by: Cat C session-model inventory (issuance + refresh + logout
>    + cookie discipline) + declared-refresh-posture evidence + Chris-D-
>    verdict on silent-refresh vs explicit-re-login vs hybrid._
> 5. **Cross-arc coordination preserved.** Flags to Group 2500 API (per-endpoint
>    permission registry) + Group 2600 PA (workspace-context vs user-context
>    split) preserved.
>    _Measured by: xx99 §5.4 cross-arc coordination flag count ≥ 2 (Group
>    2500 API + Group 2600 PA at minimum); optionally Group 1700
>    Observability + Group 2300 Mobile if load-bearing findings surface._
> 6. **Trust boundary inventory explicit + testable** (Rigby SIGN-preview
>    fold). Single enumerated list of auth mechanisms + intended callers +
>    allowed routes, with at least smoke-test coverage. Prevents P1 Cat A
>    from turning into narrative-only auditing.
>    _Measured by: Cat A trust-boundary registry existence + smoke-test
>    coverage inventory (rate ≥ one smoke-test-per-mechanism) +
>    hard-runtime-gate vs soft-prompt-only vs permissive-fallback
>    classification evidence._

> **Auth-contract anti-scope** (Chris "agree all" 2026-07-05 — 6 items
> total; #6 added per Rigby SIGN-preview-with-edits fold):
>
> - **No backend API design.** Group 2500 API scope.
> - **No PA behavior spec.** Group 2600 PA scope.
> - **No frontend framework migration.** Group 2200 §7 anti-scope preserved.
> - **No mobile app auth.** Group 2300 Mobile scope.
> - **No new session-model authoring at parent scope.** Design-preparation
>   only per playbook §5 phase discipline; new session-model ADR spawned
>   post-arc if load-bearing.
> - **No new auth provider additions (SSO/OAuth) at parent scope** (Rigby
>   SIGN-preview fold). Classic scope magnet; deferred to post-arc ADR if
>   Chris re-raises.

---

## 1. Why Phase 0

The Research Operating System calls Phase 0 a **parent-scoping
Session**: propose the child taxonomy + central lens + acceptance
criteria + anti-scope + child mission sequence, then let Chris
ratify BEFORE any child audits run. The playbook §11.1 template
formalizes the shape. This is the TENTH application of that
template.

The Group 2400 Auth scope is materially different from prior arcs
in two ways that justify the Phase 0 gate:

1. **Four-axis cross-arc handoff bundle from Group 2200.** S2299
   §8.2 T1 identified four contract axes (silent-401 SYSTEMIC +
   logout cleanup contract + session lifecycle model +
   per-endpoint permission-floor uniformity) that ALL trace to Auth
   as owning arc but were surfaced from the frontend surface. The
   frontend-surface framing risks a narrow taxonomy that misses the
   §3.27 baseline dimensions (trust boundaries, Fleet HMAC, VIP
   demo, service tokens). Phase 0 pressure-tests the taxonomy for
   completeness across BOTH the T1 handoff bundle AND the §3.27
   authentication baseline.

2. **§3.27 PARTIAL + LIGHT baseline is a research posture, not a
   maturity claim.** S1273 v2 Rigby review revised §3.27 from
   STABLE to PARTIAL — the token auth path itself works, but VIP
   demo enforcement is prompt-only (no runtime gate) and Fleet
   signature has permissive fallback. These are **known unsafe
   edges**, not unknown gaps. Phase 0 declares the arc's research
   posture on each unsafe edge: does the arc surface + inventory
   the edges (research-only), or does it recommend the fix path
   (design-preparation)? The playbook §5 phase discipline anchors
   research-only at parent scope.

**MC-4 dial-back-resolution 5th confirming arc candidate.** Per
S2299 canonical summary §5.3, Group 2400 Auth with a 4-child
structure would extend the MC-4 CODIFICATION-CONFIRMED pattern
from 4 consecutive arcs (Groups 1900 + 2000+ + 2100 + 2200) to 5
consecutive arcs, resolving the S2199 Q3 STRENGTHEN dial-back
("fully generalized" removal contingent on 5th arc or materially
different stress condition). Auth is materially different in
scope (full auth stack, not a single UI surface family), so the
5th-arc extension IS a stress test.

**Runtime target: 6 sessions.** Matches Groups 1600 through 2200
precedent (parent + 4 children + xx99 canonical summary). Runtime
cap: 8. Never invoked in prior arcs; invoke only if a child
requires split.

---

## 2. What existing inventory already tells us

> **Evidence-provenance disclaimer** (Rigby SIGN cycle 1 Q4 fold —
> 2026-07-05). Numeric counts + file:line anchors in §2 (and where
> they recur in §3 child scopes) are **ESTIMATE**s inherited from
> prior arcs — not verified at S2400 HEAD:
>
> - `~108 PUBLIC_PATHS` — ESTIMATE per §3.27 platform_architecture_inventory
>   (S1273 v2 review baseline); Cat A re-verifies at HEAD via full
>   `PUBLIC_PATHS` enumeration.
> - `~630 of ~1,300 gated call-sites at silent-401 risk` — ESTIMATE
>   per S2203 A3 grep-based extraction hedged for wrapper duplicates
>   (S2299 §8.2 T1 explicit hedge); Cat D re-verifies at HEAD via
>   full call-site inventory.
> - `15 persistent-state surfaces (12 direct localStorage + 3 Zustand
>   persist)` — ESTIMATE per S2204 §14 F1 baseline at S2204 HEAD; Cat
>   C re-verifies at S2403 HEAD in case new stores landed since S2204
>   close.
> - File:line anchors (`core/auth_middleware.py:563-681`,
>   `.py:541-544, 610-614`, `.py:548-556, 615-623`,
>   `core/services/fleet_auth_drf.py:65-150`,
>   `core/vip_middleware.py:50-105`, `frontend/src/lib/api.ts:48-56`)
>   — ESTIMATE per S1273 v2 review + S2203 §14 F3.5; Cat A + Cat D
>   re-verify at HEAD line ranges (line-drift possible since S1273
>   review closed).
> - `~1,864 path() patterns` + `209 core/views*.py files` — RUNTIME
>   INVENTORY per PLATFORM_INVENTORY.md Git HEAD `f3fe1493` (2026-07-02);
>   not ESTIMATE. Regenerate via `python manage.py generate_platform_inventory`
>   if drift observed at S2401 open.
>
> One remaining SPECULATIVE flag preserved: §2.3 "No cookie SameSite/
> Secure default declared in searchable form" — Cat C verifies at
> S2403.

### 2.1 Runtime anchor (PLATFORM_INVENTORY — no dedicated Auth row)

`PLATFORM_INVENTORY.md` (Git HEAD `f3fe1493`, generated 2026-07-02)
does NOT carry a dedicated Auth section. Auth surfaces appear
implicitly:
- **URL Routes** — 1,864 `path()` patterns across `core/urls*.py`;
  §3.27 baseline reports ~108 PUBLIC_PATHS in
  `UnifiedTokenAuthenticationMiddleware`.
- **Django View Files** — 209 files matching `core/views*.py`;
  most are gated by the middleware default (`TokenAuthentication`).
- **Database Models** — 585 concrete models; token model
  (`authtoken`) + user model (`UnifiedUser`) live here.
- **Management commands** — 199; several are auth-adjacent
  (token rotation, staff seed).

**Anchor drift observation.** No `PLATFORM_INVENTORY §Auth`
sub-section exists — auth is inventoried indirectly via routes +
views + models. This is DIFFERENT from Frontend (which had
`§Frontend` autoblock post-S2299). S2400 §7 will consider whether
an `inventory_gathers().auth` extension is warranted (P1 Cat A
output candidate).

### 2.2 32-domain map (S1273 platform_architecture_inventory row 27)

Row 27 = **Auth / Permissions / Security**. Post-S1273 v2 Rigby
review:
- **Research coverage:** LIGHT ("compressed relative to blast
  radius per Rigby S1273 review — deserves a dedicated
  trust-boundary + threat-model research doc alongside a proper
  architectural contract")
- **Architecture maturity:** PARTIAL (revised from STABLE)
  - VIP demo enforcement is prompt-only — PA can ignore the
    "read-only" injection; no runtime gate on write operations
    from a `vip_demo_viewer` role. **Soft gate, not enforcement
    boundary.**
  - Fleet signature permissive fallback — `FleetSignatureAuthentication`
    does NOT raise on missing/invalid signature; flags as
    unverified and defers to downstream `FleetCapabilityRequired`.
    **Two-layer gate, but first layer is soft.**
- **Risk (from S1274 recommendation matrix):** MEDIUM-HIGH risk +
  HIGH priority + YELLOW status. Recommended action: "Trust-
  boundary + threat-model doc + VIP demo API-layer enforcement
  plan."

**Canonical entry points (§3.27):**
- `core/auth_middleware.py:563-681` — UnifiedTokenAuthenticationMiddleware
  (~108 PUBLIC_PATHS).
- `.py:541-544, 610-614` — STAFF_REQUIRED_PATHS.
- `.py:548-556, 615-623` — REVIEWER_BLOCKED_PATHS.
- `core/services/fleet_auth_drf.py:65-150` — FleetSignatureAuthentication
  (HMAC X-Fleet-Signature; permissive fallback).
- `core/vip_middleware.py:50-105` — VIP demo (read-only +
  workspace-scope; **prompt-only** — no runtime gate).
- Service tokens: `PA_DB_HEALTH_RPC_TOKEN`, `PUBLIC_INTEL_TOKEN`.

**Trust boundaries (S1273 v2 explicit enumeration):**
| Boundary | Type | Notes |
|---|---|---|
| VIP viewer | SOFT (prompt-only) | Should NOT be treated as hard boundary against writes |
| Fleet callers | HMAC canonical + permissive fallback | Real gate is downstream capability check |
| Internal service tokens | Service-specific gates | `PUBLIC_INTEL_TOKEN` default-off (endpoint 404s when unset) |
| Staff / reviewer path lists | Hard runtime gates | No centralized registry; maintained as Python lists |
| Standard user token auth | DRF TokenAuthentication | Battle-tested |

### 2.3 Group 2200 T1 cross-arc handoff bundle (S2299 §8.2)

The load-bearing input from Group 2200 close. S2299 §8.2 T1 aggregates
findings across all four Group 2200 children:

- **S2201 §14.3 (MINOR-DRIFT).** Cockpit redirect two-stage auth —
  historically-observed transient double-redirect on session expiry.
  Frontend-side symptom of session-lifecycle ambiguity.
- **S2201 §15.5 (cross-arc dependency).** Silent 401 as frontend
  default behavior at `frontend/src/lib/api.ts:48-56`. Whole-frontend
  ~100% swallow rate.
- **S2202 (no drift found).** Child B WebSocket Consumer Surface
  audit found NO auth drift; permission-floor uniformity owned by
  Auth arc per xx99 §5.4 (i).
- **S2203 §14 F3 (silent-401 SYSTEMIC).** api.ts:48-56 sole 401
  handler; ~630 of ~1,300 gated call-sites at silent-401 risk (grep-based
  hedged for wrapper duplicates per Q14 STRENGTHEN). CRITICAL for
  money-path (betting.placeBet, wager settlement, billing.stripe)
  + governance-path (humanApi.decide) endpoints.
- **S2203 §14 F3.5 (auth-endpoint whitelist BRITTLE — MED).**
  Whitelist substring `/auth/` + `/login` hardcoded in api.ts:48-56.
  Classic-footgun scales-badly-under-route-evolution per Q5
  STRENGTHEN.
- **S2204 §14 F1 (15 persistent-state surfaces inventory).** 12
  direct localStorage keys + 3 Zustand persist stores. All 15
  affected by logout cleanup contract if implemented.
- **S2204 §14 F6 + F8 (no-cleanup-on-logout systemic).** authStore +
  workspaceStore + paStore all lack logout-time cleanup.
- **S2204 §19.1 R1 (session lifecycle two-sided framing).** Same
  design gap as S2203 §14 F3 seen from the state-persistence side.
  FE symptom (silent 401 swallow + no logout cleanup) vs BE model
  (no declared session lifecycle contract).

**Three-option decision space (S2203 §19.1 R2 for permission-floor
uniformity):**
- **(a) Uniform IsAuthenticated across all `/v1/**` endpoints** +
  client-side auth-gate + observable-error surfacing.
- **(b) Uniform AllowAny for read paths + IsAuthenticated for
  writes** + client-side auth-check-on-write.
- **(c) Per-endpoint permission registry.**

Owner: Group 2400 Auth (this arc). Blast radius: ~630 call-sites +
15 persistent-state surfaces.

### 2.4 Adjacent-domain baseline

- **`docs/research/governance_authority_evolution.md` §2.5** — 36-45
  authority primitives adjacent to but distinct from Group 2400
  scope. Authority = decision plane (who ratifies what); Auth =
  authentication + authorization + session lifecycle + trust
  boundaries. Group 1900 canonical summary § authority-vs-
  authentication demarcation preserves the boundary.
- **`docs/EMPLOYEE_OS_PRIMITIVES.md`** — GovernanceState +
  KillSwitch runtime consumers. Auth surface CONSUMES governance
  primitives (kill-switch check on gated endpoints) but does not
  AUTHOR them. Scope-guardrail preserved.
- **`docs/research/domains/frontend/2299_frontend_canonical_summary.md`
  §5.4 (i)** — Cross-arc coordination flag: "silent-401 + logout
  cleanup with Group 2400 Auth." Group 2200 close preserved this
  as the highest-frequency (4/4 children) cross-arc-handoff signal.

### 2.5 Documentation baseline (gap-flagging per playbook §11.2 §11)

**Existing.**
- §3.27 platform_architecture_inventory row (inventory-only, not a
  contract).
- Rigby S1273 v2 review notes (embedded in row commentary).
- `docs/research/governance_authority_evolution.md` (adjacent
  plane, referenced not authored).
- `docs/EMPLOYEE_OS_PRIMITIVES.md` (consumer-side).

**Gap (S1273 v2 review directly names):**
- **No threat model.** §3.27 explicitly notes "No threat model /
  trust-boundary doc exists; §3.27 here is the closest thing
  (research-only inventory, not a contract)."
- **No auth-surface topic doc.** No `docs/topics/auth.md` exists
  (compare topics/frontend.md for shape). Analogous gap to Group
  2200's stale-warned topics/frontend.md — but Group 2400 has
  no doc to be stale, which is a bigger gap.
- **No trust-boundary inventory.** Row 27 has partial enumeration
  in §3.27 narrative; no runtime-derivable inventory exists.

---

## 3. Candidate subdomain taxonomy

Four child audit slots (Chris-locked "agree all" 2026-07-05), each
targeting one of the four contract axes surfaced by the S2299 T1
handoff bundle + §3.27 baseline. Option C 4-child taxonomy ratified
over Option A (T1-mirror-only, too frontend-flavored) + Option B
(5-child, breaks MC-4 target).

### A — Authentication Surface + Trust Boundaries (S2401 P1)

**Scope.** Enumerate every authentication mechanism the platform
runs: standard user token auth (DRF `TokenAuthentication`) + the
~108 PUBLIC_PATHS + STAFF_REQUIRED_PATHS + REVIEWER_BLOCKED_PATHS
in `UnifiedTokenAuthenticationMiddleware` +
`FleetSignatureAuthentication` HMAC + `VIP demo` middleware +
internal service tokens (`PA_DB_HEALTH_RPC_TOKEN`,
`PUBLIC_INTEL_TOKEN`). For each: intended caller class + allowed
routes + gate type (hard runtime vs soft prompt-only vs permissive
fallback) + failure mode.

**Central question the audit answers.** *Does the platform have an
explicit, enumerated trust-boundary inventory across every auth
mechanism it runs, or has the authentication surface accreted
via per-mechanism defaults without a single source-of-truth
inventory?*

**Load-bearing signals from prior arcs:**
- §3.27 platform_architecture_inventory row 27 lists 5 auth
  mechanisms + 5 trust boundaries in narrative form; no runtime-
  derivable inventory exists.
- S1273 v2 Rigby review flagged §3.27 STABLE → PARTIAL specifically
  because VIP demo is prompt-only + Fleet permissive fallback. The
  narrative names these as "known unsafe edges" but does not
  quantify blast radius.
- `docs/research/governance_authority_evolution.md` covers adjacent
  authority plane; explicitly distinguishes authority (decision)
  from auth (authentication + authorization). Boundary preserved.
- No `docs/topics/auth.md` exists. Documentation gap named in §2.5.

**Expected output.** 20-section audit doc + POSTURE-DECISION evidence
plan owed to xx99 on:
- (a) **Auth mechanism inventory** — full enumeration of every
  `authentication_classes` + middleware auth path + service-token
  path in the platform. Include gate type + intended caller +
  allowed routes per mechanism.
- (b) **Trust boundary inventory** — hard runtime gate vs soft
  prompt-only vs permissive fallback classification per mechanism,
  with concrete evidence rate (`grep` count of runtime enforcement
  vs prompt-only vs fallback silent-accept).
- (c) **PUBLIC_PATHS audit** — the ~108 entries at
  `core/auth_middleware.py`. Categorize by intent (health / demo /
  public-read / callback / never-should-be-public). Flag drift
  candidates.
- (d) **VIP demo enforcement audit** — quantify how many endpoints a
  VIP viewer role could theoretically write to today; propose
  runtime-gate design candidates without authoring the fix.
- (e) **Fleet permissive fallback audit** — quantify the silent-
  accept path in `FleetSignatureAuthentication`. Distinguish
  grace-period-intent from tech-debt.
- (f) **Service token audit** — `PA_DB_HEALTH_RPC_TOKEN` +
  `PUBLIC_INTEL_TOKEN` scope + rotation policy + default-off
  behavior + drift candidates.
- (g) **Smoke-test coverage inventory** — existing test coverage
  per auth mechanism; identify which mechanisms have no smoke test
  (blocker to acceptance criterion #6).

**Delegates from.** §3.27 platform_architecture_inventory row 27;
S1273 v2 Rigby review PARTIAL classification + trust-boundary
enumeration; S2299 §8.2 T1 aggregation.

### B — Authorization + Permission-Floor Uniformity (S2402 P2)

**Scope.** Enumerate every gated endpoint — the ~1,864 `path()`
patterns minus ~108 PUBLIC_PATHS — and classify by permission floor
(IsAuthenticated / IsAdmin / IsStaff / IsReviewer / IsFleetCaller /
None-declared). For each: identify DRF-level permission_class vs
middleware-level path gate vs undeclared-implicit. Enumerate the
three-option decision space per S2203 §19.1 R2 with concrete
blast-radius per option.

**Central question the audit answers.** *Is the platform's
permission floor uniform + observable + declared per endpoint, or
does the "no per-endpoint permission-floor contract" pattern
(implicit in the ~40% permission-untraced endpoint sample from
S2203 A3) generalize across the whole gated surface?*

**Load-bearing signals from prior arcs:**
- S2203 A3 sampled 20 endpoints; ~40% not traced (view functions
  not indexed via grep). Full permission-floor uniformity assessment
  requires this arc.
- S2203 §19.1 R2 three-option decision space (a) uniform
  IsAuthenticated / (b) split read-vs-write / (c) per-endpoint
  registry.
- STAFF_REQUIRED_PATHS + REVIEWER_BLOCKED_PATHS at
  `core/auth_middleware.py:610-614` + `615-623` — hard runtime gates
  but no centralized registry.
- S2200 xx99 §5.4 (i) cross-arc coordination flag: permission-
  floor owned here.

**Expected output.** 20-section audit doc + POSTURE-DECISION evidence
plan owed to xx99 on:
- (a) **Gated endpoint inventory** — full enumeration of
  `path()` × permission-floor cell. Include declared-permission-class
  + middleware-path-gate + implicit-inheritance flag.
- (b) **Permission-untraced rate** — S2203 A3 sampled 20; extend
  to whole platform. Cite untraced endpoints by file:line.
- (c) **STAFF_REQUIRED_PATHS + REVIEWER_BLOCKED_PATHS registry
  audit** — Python-list format; propose evidence for/against
  centralization without authoring the registry.
- (d) **Three-option decision space evidence** — blast radius per
  option; migration cost per option; observability cost per option.
  Recommend a lean; escalate to Chris D-verdict at S2402 close.
- (e) **Cross-arc coordination flag: per-endpoint permission
  registry** — flag Group 2500 API as owning-arc if per-endpoint
  registry lands, per S2200 xx99 §5.4 (ii).

**Delegates from.** S2203 §14 F3 (silent-401 SYSTEMIC as
permission-floor observability symptom) + §19.1 R2 (three-option
decision space) + A3 (~40% untraced sample). Cross-arc coordination
flag for Group 2500 API arc.

### C — Session Lifecycle + Logout Cleanup Contract (S2403 P3)

**Scope.** Enumerate the platform's session model: token issuance
+ token refresh discipline + cookie SameSite / Secure / HttpOnly
defaults + Clear-Site-Data header usage + explicit re-login vs
silent-refresh decision + logout endpoint behavior + client-side
storage cleanup contract. Extend to the 15 persistent-state
surfaces (S2204 F1 inventory) and enumerate the cleanup contract
per surface.

**Central question the audit answers.** *Does the platform have a
declared session lifecycle contract (issuance + refresh + logout
+ cleanup semantics all observable), or does the "no logout
cleanup" + "no session lifecycle spec" pattern (S2204 §14 F6 F8
+ §19.1 R1) leave session boundaries at BE/FE-implicit-agreement?*

**Load-bearing signals from prior arcs:**
- S2204 §19.1 R1 session lifecycle two-sided framing — HIGH priority
  active-research track owed to Group 2400 Auth.
- S2204 §14 F1 15-surface storageKeys inventory: 12 direct
  localStorage keys + 3 Zustand persist stores.
- S2204 §14 F6 F8 no-cleanup-on-logout systemic across authStore +
  workspaceStore + paStore.
- S2201 §14.3 cockpit redirect two-stage auth MINOR-DRIFT — FE
  symptom of session-lifecycle ambiguity.
- No cookie SameSite/Secure default is declared in
  `core/settings*.py` in searchable form (SPECULATIVE — audit will
  verify).

**Expected output.** 20-section audit doc + POSTURE-DECISION evidence
plan owed to xx99 on:
- (a) **Session model inventory** — issuance (`obtain_token`
  endpoint), refresh (does one exist? silent vs explicit?), logout
  (`revoke_token` endpoint semantics), cookie discipline
  (SameSite / Secure / HttpOnly / Domain defaults).
- (b) **15-surface storageKeys cleanup contract** — per surface
  (auth-token, workspace-selected, ...): does logout clear? Does
  session expiry clear? Is the discipline declared or accidental?
- (c) **Clear-Site-Data header decision** — is it used? Should
  it be? Blast radius (does it clear third-party cookies as a
  side-effect that affects the demo mode surface).
- (d) **Silent-refresh vs explicit-re-login decision evidence** —
  three-option decision space: (α) silent-refresh (opaque to user;
  hides expiry); (β) explicit re-login (visible; user-friction);
  (γ) hybrid (silent while active, explicit after N-min idle).
  Recommend a lean; escalate to Chris D-verdict.
- (e) **Cockpit two-stage drift verification** — S2201 §14.3
  MINOR-DRIFT re-verification; confirm still-live vs pattern-fixed.

**Delegates from.** S2204 §19.1 R1 + §14 F1 + F6 + F8; S2201
§14.3. Cross-arc coordination flag for Group 2600 PA (workspace-
context storage lives in this contract).

### D — Frontend Integration + Silent-401 SYSTEMIC Resolution (S2404 P4)

**Scope.** Frontend surface of the auth contract. Enumerate the
silent-401 handler at `frontend/src/lib/api.ts:48-56` + its whitelist
substring behavior + the ~630 call-site blast radius + the typed
error envelope design candidate + error-boundary integration
coordination. Includes the T1 cross-arc handoff execution: how
does Group 2400 Auth deliver the contract to the frontend such
that acceptance criteria #1 (permission-floor observability) and
#2 (failure surfacing) both hold at the api.ts layer?

**Central question the audit answers.** *Does the frontend
integration surface expose auth failures as first-class typed
errors observable at every gated call site, or does the
"silent-401 SYSTEMIC" + "brittle whitelist" pattern (S2203 §14
F3 F3.5) require redesign at the api.ts layer + cross-arc
coordination with error-boundary framework + typed-error-envelope
adoption?*

**Load-bearing signals from prior arcs:**
- S2203 §14 F3 silent-401 SYSTEMIC via api.ts:48-56 — ~630 of
  ~1,300 gated call-sites at risk. Whole-frontend ~100% swallow
  rate.
- S2203 §14 F3.5 whitelist substring `/auth/` + `/login` hardcoded
  BRITTLE — MED per Q5 STRENGTHEN.
- S2201 §15.5 silent 401 systemic + no error boundaries anywhere —
  paired weakness (silent failure + no framework to surface it).
- S2299 §5.1 canonical seam statement identifies "defaults that
  silently swallow failure vs contracts that surface failure" as
  the design lean bridging Group 2200 → Group 2400.
- S2299 §8.3 maintainer-decision batch item R6 error-boundary
  framework establishment — tied to Group 2400 Auth handoff.

**Expected output.** 20-section audit doc + POSTURE-DECISION evidence
plan owed to xx99 on:
- (a) **api.ts:48-56 audit** — full behavior enumeration (redirect
  target + whitelist substring rules + retry semantics + wrapper-
  duplicate accounting from S2203 Q14).
- (b) **Silent-401 call-site inventory** — extend S2203 A3 grep-
  based ~630 estimate. Per call-site: money-path / governance-path
  / read-path / write-path classification (CRITICAL for money +
  governance).
- (c) **Typed error envelope design candidates** — three options:
  (α) throw typed exceptions per HTTP status; (β) return
  discriminated-union response types; (γ) React-Query error
  callbacks with typed error envelope. Recommend a lean; escalate
  to Chris D-verdict.
- (d) **Whitelist replacement design** — S2203 §14 F3.5 BRITTLE
  substring → replacement candidates: (α) explicit endpoint list
  registry; (β) 401-response-suppression header from BE; (γ)
  per-api-module explicit `noAuthRedirect` flag.
- (e) **Cross-arc coordination flags** — error-boundary framework
  (S2299 §8.3 R6) + typed-error-envelope adoption (Group 2200
  post-arc T-slot) + T1 handoff execution readiness.

**Delegates from.** S2203 §14 F3 + F3.5; S2201 §15.5. Cross-arc
coordination flag for Group 2200 post-arc T-slot (R6 error boundary
framework).

### Explicit non-candidates

Deliberately EXCLUDED from Group 2400 scope:

- **Mobile app auth.** Row 19 of the 32-domain map (Mobile App;
  Expo scaffolding; PARTIAL; LIGHT). Deferred to Group 2300 Mobile
  per post-S2099 project memory queue ranking. Anti-scope #4.
- **Backend API design + per-endpoint permission registry
  *authoring*.** Cat B audits the FE + middleware side of the
  "no per-endpoint permission-floor contract" debt; authoring the
  registry is Group 2500 API scope. Anti-scope #1.
- **PA behavior spec + workspace-context vs user-context split
  *authoring*.** Cat C flags workspace-context storage lives in
  the session-lifecycle contract; PA-side behavior spec is Group
  2600 PA scope. Anti-scope #2.
- **Authority (decision) plane.** Group 1900 covered authority
  enforcement — decision-plane framework distinct from
  authentication + authorization. Boundary preserved per S1999
  canonical summary. Not this arc.
- **Frontend framework migration.** Cat D audits api.ts + typed-
  error-envelope design; no React → Next.js or Vite → Turbopack
  proposal. Anti-scope #3 (Group 2200 §7 preserved).
- **New session-model authoring.** Cat C recommends a lean on
  silent-refresh vs explicit-re-login vs hybrid but does NOT
  author the session-model ADR. Design-preparation only per
  playbook §5 phase discipline. Anti-scope #5.
- **New auth provider additions (SSO/OAuth).** Rigby SIGN-preview
  fold #6. Classic scope magnet; deferred to post-arc ADR if
  Chris re-raises. Anti-scope #6.
- **Fixing findings.** Every child audit surfaces findings; none
  of them are fixed inside Group 2400. Findings graduate to
  T-slot post-arc queue at S2499 xx99 close.

### 3.5 Auth-adjacent probes disposition (Rigby SIGN cycle 1 Q1 fold — 2026-07-05)

The shape-card discussion surfaced auth-adjacent probes that don't
map cleanly onto the 4-child taxonomy. Rigby SIGN cycle 1 Q1 fold
requires explicit disposition of each — is it in-scope-as-evidence,
non-candidate, or deferred? This subsection resolves the ambiguity
so no child drifts into un-scoped territory.

| Probe | Disposition | Owning child (if in-scope) | Rationale |
|---|---|---|---|
| **Token rotation policy** | In-scope as evidence | Cat A (mechanism inventory) + Cat C (session-lifecycle contract) | Cat A inventories issuance mechanism; Cat C audits refresh + rotation cadence. Overlap intentional: Cat A cites Cat C for lifecycle detail. |
| **Refresh token security posture** | In-scope as evidence | Cat C (session lifecycle) | Session-model inventory owns refresh token semantics (silent vs explicit; rotation-on-use vs long-lived). |
| **JWT vs opaque tokens** | In-scope as evidence | Cat A (mechanism inventory) + Cat C (session-model design) | Cat A inventories current mechanism (opaque DRF `TokenAuthentication`); Cat C recommends a lean if session-model ADR spawns post-arc. NOT authoring the JWT-vs-opaque ADR at parent scope. |
| **CSRF discipline** | Conditionally in-scope | Cat C IF cookie-auth surface exists; otherwise N/A | Token-header auth doesn't need CSRF gates; cookie-auth partial surface (session middleware, admin, staff login form) does. Cat C inventories which surfaces use cookie auth + surfaces CSRF status per surface. If no cookie-auth surface exists, section marks N/A with grep evidence. |
| **Session fixation defense** | In-scope as evidence | Cat C (session lifecycle) | Session-model inventory covers post-login token-rotation-on-privilege-escalation vs same-token-reused. Evidence only; no defense-mechanism authoring. |
| **Rate limiting / brute-force** | Inventory-only, defer post-arc | (none — cross-cutting) | Cross-cutting concern touching auth (login endpoint) + API (throttle_classes) + Observability (event emit). Cat A inventories what rate-limit posture exists on auth endpoints; full rate-limit ADR deferred to post-arc if load-bearing. |
| **Audit logging (auth events)** | Inventory-only, defer post-arc | (Group 1700 Observability adjacent) | Group 1700 owns event-emit + retention discipline. Cat A cites auth-event emit sites without authoring emit design. Cross-arc coordination flag to Group 1700 if load-bearing. |
| **Password policy + reset flow** | Non-candidate | (none) | Framework-provided (Django auth); no known drift. Explicit non-candidate to prevent scope magnet. |
| **MFA / TOTP / hardware token** | Non-candidate | (none) | No MFA currently in platform; adding = provider addition = Anti-scope #6. Parked candidate #9 if Chris re-raises. |
| **Impersonation / sudo mode** | Non-candidate | (none) | No impersonation surface currently in platform. Explicit non-candidate. |
| **Account lockout / suspicious-activity blocks** | Non-candidate | (none) | Same posture as rate-limiting — cross-cutting; parked. |
| **Cookie SameSite / Secure / HttpOnly defaults** | In-scope as evidence | Cat C (session lifecycle) | §2.3 SPECULATIVE flag lifts here; Cat C verifies default declarations. |

**Cross-cutter posture guardrail.** Cat A does NOT extend into audit-logging emit design (Group 1700 scope). Cat B does NOT extend into rate-limiting design (cross-cutting post-arc ADR). Cat C does NOT extend into MFA/OAuth/SSO framework additions (Anti-scope #6 preserved). Any child that surfaces an auth-adjacent probe finding beyond its disposition row above MUST flag as cross-arc coordination + defer to post-arc rather than expand scope in-arc.

---

## 4. Parent-vs-single recommendation

**RECOMMEND: parent-with-4-children** (rather than a single audit).

**Reasoning.**

The four child slots (A + B + C + D) partition the auth surface
along orthogonal contract axes. Each is independently investigatable
in one session (parent scoping precedent from Groups 1600 through
2200 all landed at 6-session runtime = parent + 4 children + xx99).

A single-doc arc would risk two failure modes:
1. **Underweighting the trust-boundary inventory** (P1 Cat A) —
   the S1273 v2 Rigby review already flagged §3.27 as
   compressed relative to blast radius. A single-doc arc pressures
   towards headline findings + defers depth. Cat A alone deserves
   a 20-section audit against Rigby SIGN.
2. **Frontend-flavored taxonomy drift** — the T1 handoff bundle is
   4-axis and frontend-surfaced. A single-doc arc that leads with
   T1 would risk mirroring the frontend framing verbatim and
   missing the §3.27 baseline dimensions. The 4-child partition
   forces Cat A ≠ frontend-lens, Cat B ≠ frontend-lens, Cat C
   partial-frontend-lens (state persistence + logout cleanup +
   session lifecycle), Cat D frontend-lens (silent-401 execution
   surface). Each Cat gets audited on its own terms.

**Parent-with-4-children extension precedent.** Groups 1500, 1600,
1700, 1800, 2100, 2200 all landed at parent + 4 children + xx99.
MC-4 dial-back-resolution 5th confirming arc candidate per S2299
§5.3. Group 2400 continuing the 4-child pattern would extend MC-4
from CODIFICATION-CONFIRMED-across-4-consecutive-arcs to
CODIFICATION-CONFIRMED-across-5-consecutive-arcs, resolving the
S2199 Q3 STRENGTHEN dial-back.

**Runtime target.** 6 sessions:
- S2400 = parent scoping (this doc)
- S2401 = P1 Cat A Authentication surface + Trust boundaries
- S2402 = P2 Cat B Authorization + Permission-floor uniformity
- S2403 = P3 Cat C Session lifecycle + Logout cleanup contract
- S2404 = P4 Cat D Frontend integration + Silent-401 SYSTEMIC
- S2499 = xx99 canonical summary + arc-close cascade

**Runtime cap.** 8 sessions. Never invoked in prior arcs; invoke
only if a child requires split (e.g., Cat A trust-boundary inventory
requires a separate threat-model-only child).

---

## 5. Child mission sequence (Chris-locked "agree all" 2026-07-05)

**Sequencing rationale.** Backend-first order (A → B → C → D):

- **Cat A (Authentication + Trust Boundaries) first** — establishes
  the baseline inventory that Cats B, C, D reference. Cat A defines
  what the auth mechanisms ARE; Cats B/C/D define what they DO,
  WHEN, and WHERE.
- **Cat B (Authorization + Permission Floor) second** — extends Cat A
  from "authentication surface" to "authorization surface" over
  ~1,700 gated endpoints. Uses Cat A's mechanism inventory as its
  gate-classification vocabulary.
- **Cat C (Session Lifecycle + Logout Cleanup) third** — session
  lifecycle contract sits between authentication (Cat A) + client-
  side persistence (Cat C-owned). Requires Cats A + B outputs to
  ground its recommended discipline.
- **Cat D (Frontend Integration + Silent-401) fourth** — executes
  the T1 cross-arc handoff. Requires Cats A + B + C outputs to
  design the frontend contract with concrete backend semantics.

### S2401 — Child A: Authentication Surface + Trust Boundaries

Runtime: 1 session. Rigby full SIGN required per playbook §15.
Deliverable: 20-section audit + POSTURE-DECISION evidence plan
owed to xx99.

**Key outputs.**
- Auth mechanism inventory (5+ mechanisms enumerated + gate type
  classified).
- Trust boundary inventory (hard runtime / soft prompt-only /
  permissive fallback rate).
- PUBLIC_PATHS ~108-entry audit + intent classification.
- VIP demo + Fleet permissive fallback blast-radius quantification.
- Service token scope audit.
- Smoke-test coverage inventory (blocker to acceptance criterion #6).

**Rigby SIGN cadence.** Single-batch × 4-Q per S1899 + S1999 +
S2099 + S2199 + S2299 five-consecutive tested pattern (MC-10
CODIFICATION-READY-pending-Chris at 5-arc baseline).

### S2402 — Child B: Authorization + Permission-Floor Uniformity

Runtime: 1 session. Rigby full SIGN required per playbook §15.
Deliverable: 20-section audit + POSTURE-DECISION evidence plan
owed to xx99.

**Key outputs.**
- Gated endpoint inventory (permission-floor cell per endpoint).
- Permission-untraced rate extension (S2203 A3 sample → whole
  platform).
- STAFF_REQUIRED_PATHS + REVIEWER_BLOCKED_PATHS registry audit.
- Three-option decision space evidence + recommendation lean.
- Cross-arc coordination flag for Group 2500 API (per-endpoint
  registry as design-preparation candidate).

**Rigby SIGN cadence.** Single-batch × 4-Q per S2401 precedent.

### S2403 — Child C: Session Lifecycle + Logout Cleanup Contract

Runtime: 1 session. Rigby full SIGN required per playbook §15.
Deliverable: 20-section audit + POSTURE-DECISION evidence plan
owed to xx99.

**Key outputs.**
- Session model inventory (issuance + refresh + logout + cookie
  discipline).
- 15-surface storageKeys cleanup contract per surface.
- Clear-Site-Data header decision evidence.
- Silent-refresh vs explicit-re-login vs hybrid decision space
  evidence + recommendation lean.
- S2201 §14.3 cockpit two-stage drift verification.

**Rigby SIGN cadence.** Single-batch × 4-Q per S2401 precedent.

### S2404 — Child D: Frontend Integration + Silent-401 SYSTEMIC Resolution

Runtime: 1 session. Rigby full SIGN required per playbook §15.
Deliverable: 20-section audit + POSTURE-DECISION evidence plan
owed to xx99.

**Key outputs.**
- api.ts:48-56 audit (full behavior enumeration).
- Silent-401 call-site inventory (~630 estimate extension + money/
  governance/read/write classification).
- Typed error envelope design candidates + recommendation lean.
- Whitelist replacement design + recommendation lean.
- Cross-arc coordination flags for R6 error-boundary framework +
  typed-error-envelope adoption + T1 handoff execution readiness.

**Rigby SIGN cadence.** Single-batch × 4-Q per S2401 precedent.

### S2499 — xx99 Canonical Summary

Runtime: 1 session. Rigby full SIGN required per playbook §15.
Deliverable: 12-section canonical summary per playbook §11.3
+ §10 meta-methodology ELEVENTH application after S1399/S1499/
S1599/S1699/S1799/S1899/S1999/S2099/S2199/S2299 ten prior.

**Key outputs.**
- Canonical seam statement synthesizing the four children.
- Cross-cutting patterns (target: 4-6 §4 items).
- Anchor-update recommendations for PLATFORM_INVENTORY (auth
  autoblock candidate), PLATFORM_WHAT_IT_IS (Auth-contract
  governance narrative subsection candidate), ARCHITECTURE_INDEX
  v-bump, platform_architecture_inventory row 27 upgrade candidate
  (PARTIAL → WORKING or CANONICAL depending on child findings).
- Cross-arc T-slot follow-on queue (T1 execution to Group 2500 API +
  Group 2600 PA + Group 1700 Observability; maintainer-decision
  batch; post-arc T-slot; conditional post-arc).
- Arc-close cascade (commit + push + PR + ARCHITECTURE_INDEX v-bump
  + OPEN_ARCS transition + 00-START-NEXT next-arc queue + 4-step
  docs cascade + build_docs_provenance + SESSION_2499 handoff + arc
  pin retirement via session_tool.retire + SIGN pin retirement).

**Rigby SIGN cadence.** Single-batch × 4-Q per S1899 + S1999 + S2099
+ S2199 + S2299 five-consecutive tested pattern (MC-10 SIXTH-
consecutive same-cadence application = CODIFICATION-CONFIRMED
threshold candidate).

---

## 6. Parked candidate issues

Not scope of Group 2400 but flagged for adjacent-arc pickup:

1. **Threat model / trust-boundary ADR.** §3.27 explicitly notes
   "No threat model / trust-boundary doc exists." Cat A produces
   the trust-boundary INVENTORY (research); the threat-model
   AUTHORING is a design-preparation ADR that spawns post-arc if
   Chris ratifies. Not this arc's authoring scope per anti-scope
   #5.

2. **VIP demo runtime-gate design.** S1273 v2 review recommendation
   matrix names "VIP demo API-layer enforcement plan" as an
   action. Cat A inventories the blast radius; the enforcement-
   plan ADR is design-preparation that spawns post-arc.

3. **Per-endpoint permission registry design.** Cat B recommends
   a lean across three options; the registry ITSELF is Group 2500
   API scope. Cross-arc coordination flag preserved.

4. **Session-model ADR.** Cat C recommends a lean across three
   options for silent-refresh vs explicit-re-login vs hybrid;
   authoring the ADR spawns post-arc if Chris ratifies. Not this
   arc's authoring scope per anti-scope #5.

5. **Typed error envelope adoption.** Cat D recommends a lean
   across three envelope-design options; execution is post-arc
   maintenance batch (Group 2200 post-arc T-slot R6 error boundary
   framework establishment overlaps).

6. **Fleet permissive fallback design intent resolution.** Cat A
   distinguishes grace-period-intent from tech-debt; the design-
   intent resolution requires Chris + Fleet-owning-service-owner
   dialogue. Not this arc's authoring scope.

7. **Clear-Site-Data header decision blast radius.** Cat C flags
   the header decision surfaces a third-party-cookie side-effect
   affecting demo mode. If the decision is HIGH-impact, spawn a
   post-arc demo-mode-integration ADR.

8. **Auth topic doc (`docs/topics/auth.md`).** §2.5 named the doc
   gap. Cat A xx99 anchor-update recommendation candidate: author
   `docs/topics/auth.md` post-arc as narrative-authored subsystem
   doc (analogous to topics/frontend.md).

9. **Extending SSO/OAuth support.** Anti-scope #6 explicitly parks
   this. If Chris re-raises post-arc, spawn a dedicated
   provider-addition ADR.

---

## 7. Anti-scope

Deliberately excluded from Group 2400 scope. Six anti-scope items
per Chris "agree all" 2026-07-05 ratification (5 from
00-START-NEXT-SESSION.md §4 + 1 Rigby SIGN-preview fold):

1. **No backend API design.** Cat B recommends a permission-floor
   lean but does not author the API contract. Group 2500 API scope.
2. **No PA behavior spec.** Cat C flags workspace-context storage
   lives in the session-lifecycle contract but does not author the
   PA behavior spec. Group 2600 PA scope.
3. **No frontend framework migration.** Cat D audits api.ts +
   typed-error-envelope design; no React → Next.js or Vite →
   Turbopack proposal. Group 2200 §7 anti-scope preserved.
4. **No mobile app auth.** Row 19 of the 32-domain map deferred
   to Group 2300 Mobile per post-S2099 project memory queue
   ranking.
5. **No new session-model authoring at parent scope.** Cats A/B/C/D
   surface findings + recommend leans; the session-model ADR is
   design-preparation that spawns post-arc if Chris ratifies. Per
   playbook §5 phase discipline.
6. **No new auth provider additions (SSO/OAuth) at parent scope**
   (Rigby SIGN-preview fold). Classic scope magnet; deferred to
   post-arc ADR if Chris re-raises.

### 7.1 Scope guardrails by leak vector (borrows S2200 §7.1 pattern)

- **Leak: Cat A drifts into threat-model authoring.** Guardrail:
  Cat A output includes a trust-boundary INVENTORY + a POSTURE-
  DECISION on threat-model authoring (recommend / defer / not-
  applicable); does NOT author the threat model. Anti-scope #5
  preserved.
- **Leak: Cat B drifts into per-endpoint registry authoring**
  (Rigby SIGN cycle 1 Q2 STRENGTHEN fold — 2026-07-05). Guardrail:
  Cat B's job is to **MEASURE** (extend the S2203 A3 sampled 20
  endpoints ~40% permission-untraced rate across the full ~1,864
  `path()` surface), **CLASSIFY** (per-endpoint permission-floor
  cell + declared-permission-class + middleware-path-gate +
  implicit-inheritance flag), and **RECOMMEND** a lean across the
  three-option decision space per S2203 §19.1 R2. Cat B does NOT
  design nor author the per-endpoint registry itself — registry
  design + authoring is Group 2500 API scope. Anti-scope #1
  preserved. Cross-arc coordination flag in Cat B §19. Explicit
  anti-pattern to avoid: Cat B produces "recommended permission-
  floor mapping table" that reads as a de-facto registry authoring
  deliverable; that MUST land as a decision-space evidence table
  with a Chris-D-verdict-request instead.
- **Leak: Cat C drifts into session-model ADR authoring.**
  Guardrail: Cat C recommends a lean across three options for
  silent-refresh vs explicit-re-login vs hybrid; ADR authoring
  spawns post-arc. Anti-scope #5 preserved.
- **Leak: Cat D drifts into typed-error-envelope adoption
  execution** (Rigby SIGN cycle 1 Q2 STRENGTHEN fold — 2026-07-05).
  Guardrail: Cat D **MEASURES** the ~630-of-~1,300 silent-401
  call-site blast radius (ESTIMATE inherited from S2203 A3 grep-
  based hedged for wrapper duplicates; Cat D re-verifies at HEAD),
  **CLASSIFIES** per call-site (money-path / governance-path /
  read-path / write-path), and **RECOMMENDS** a lean across three
  typed-error-envelope design candidates. Cat D does NOT execute
  envelope ADOPTION at call sites — adoption is post-arc T-slot
  (typed-envelope adoption tied to Group 2500 API contract SoT +
  Group 2200 post-arc T-slot R6 error-boundary framework
  establishment). Anti-scope #1 preserved. Explicit anti-pattern to
  avoid: Cat D produces a "typed error envelope migration guide"
  that reads as adoption-scoped deliverable; that MUST land as
  candidate-design evidence + Chris-D-verdict-request instead.
- **Leak: any child drifts into fixing findings.** Guardrail:
  every child §19 recommends future-research + parked-candidate
  items; no PRs open in this arc. Playbook §14 discipline: no
  implementation during research.
- **Leak: any child drifts into SSO/OAuth addition.** Guardrail:
  anti-scope #6 explicit; parked candidate #9 preserves the
  potential-post-arc-pickup slot.
- **Leak: xx99 drifts into re-authoring findings.** Guardrail:
  xx99 synthesizes + adds cross-cutting patterns + anchor-update
  recommendations; does NOT re-author child findings. Playbook
  §11.3 shape enforced.

---

## 8. Decisions recorded (Chris-locked "agree all" 2026-07-05)

### D1 — Arc structure: parent-with-4-children

Chris "agree all" 2026-07-05 (post-Rigby SIGN-preview-with-edits at
`pa-6279ead1714c4630` turn 2 ratification of Option C 4-child
taxonomy over Options A + B).

Precedent: Groups 1500-2200 consecutive 4-child parent-with-children
pattern.

### D2 — Central lens question (Rigby SIGN-preview fold verbatim)

*"Is the platform's auth model a contract (explicit trust boundaries
+ declared permission floors + declared session/refresh/logout
semantics + consistent failure surfacing), or an accretion of
per-surface defaults whose failures are silently swallowed (e.g.,
silent 401 / permissive fallbacks / ad-hoc public path lists)?"*

Chris "agree all" 2026-07-05.

### D3 — 6-criterion acceptance (5 start-here + 1 Rigby fold)

Chris "agree all" 2026-07-05 wholesale.

1. Permission-floor observability.
2. Failure surfacing (typed error envelope).
3. Logout cleanup contract.
4. Session lifecycle discipline.
5. Cross-arc coordination flags preserved.
6. **Trust boundary inventory explicit + testable** (Rigby SIGN-preview
   fold).

### D4 — 6-item anti-scope (5 start-here + 1 Rigby fold)

Chris "agree all" 2026-07-05 wholesale.

1. No backend API design.
2. No PA behavior spec.
3. No frontend framework migration.
4. No mobile app auth.
5. No new session-model authoring at parent scope.
6. **No new auth provider additions (SSO/OAuth) at parent scope**
   (Rigby SIGN-preview fold).

### D5 — Child mission sequence: backend-first A → B → C → D

- S2401 Cat A Authentication surface + Trust boundaries
- S2402 Cat B Authorization + Permission-floor uniformity
- S2403 Cat C Session lifecycle + Logout cleanup contract
- S2404 Cat D Frontend integration + Silent-401 SYSTEMIC resolution

Chris "agree all" 2026-07-05.

### D6 — Runtime target: 6 sessions; cap: 8

Precedent: Groups 1600-2200 all landed at 6-session runtime =
parent + 4 children + xx99. Runtime cap 8 never invoked. Chris
"agree all" 2026-07-05.

### D7 — MC-4 dial-back-resolution 5th confirming arc candidate

Group 2400 Auth 4-child structure = 5th consecutive 4-child arc
after Groups 1900 + 2000+ + 2100 + 2200. Extends MC-4 CODIFICATION-
CONFIRMED across-5-consecutive-arcs, resolving S2199 Q3 STRENGTHEN
dial-back. Recognized at S2400 open; codification recorded at S2499
xx99 close.

### D8 — Rigby SIGN cadence: single-batch × 4-Q per child audit + xx99

Per S1899 + S1999 + S2099 + S2199 + S2299 five-consecutive tested
pattern. MC-10 SIXTH-consecutive same-cadence application at S2499
xx99 = CODIFICATION-CONFIRMED threshold candidate. Chris "agree all"
2026-07-05.

### D9 — Arc-open mechanics verified

- `platform_config_tool overview` → `service_context: local` ✓
- `session_tool create_fresh` → `pa-6279ead1714c4630` ✓ (ELEVENTH
  formal arc pin under Research OS after Groups 1300/1400/1500/1600/
  1700/1800/1900/2000+/2100/2200 prior ten)
- `tools/pa_local.sh:280` rotated + header ledger updated with
  S2200 retirement + S2400 open stanzas
- Pin ownership: `chris` (conversation_owner_match=true) per
  feedback_pa_local_verify_ownership.md ✓

### D10 — Documentation baseline gap flagged

- No `docs/topics/auth.md` exists (candidate xx99 anchor-update
  recommendation post-arc).
- No `PLATFORM_INVENTORY §Auth` autoblock exists (candidate xx99
  anchor-update recommendation for inventory generator extension).
- No threat-model / trust-boundary doc exists (parked candidate #1
  per §6; NOT this arc's authoring scope).

Recorded at parent scope; execution deferred to xx99 §7 anchor-update
recommendation batch.

---

## 9. Next step

**Immediate.** Land this parent scoping doc as `status: draft` on
local filesystem (do NOT commit yet per playbook §16 draft-first
workflow). Route to Rigby for optional-light SIGN cycle 1 per
playbook §15 stage-scoped routing at parent scoping (Chris to gate
directly OR route via dedicated fresh isolation pin — Chris's
default has been ratify-directly-after-shape-card).

**S2401 open.** Once S2400 parent scoping is ratified + committed,
S2401 Cat A Authentication Surface + Trust Boundaries opens. Cat A
consumes:
- §3.27 platform_architecture_inventory row 27 baseline
- S1273 v2 Rigby review PARTIAL classification evidence
- `core/auth_middleware.py` full read
- `core/services/fleet_auth_drf.py` full read
- `core/vip_middleware.py` full read
- `docs/research/governance_authority_evolution.md` §2.5 primitives
  cross-reference
- Rigby-dispatched `explore` sub-agent sweep per playbook §13 six-
  parallel-agent shape

**Commit sequence at S2400 close (if Chris ratifies at S2400 close
turn 1):**
1. Land parent scoping doc at `docs/research/domains/auth/2400_auth_domain_scoping.md`
2. Update `docs/research/OPEN_ARCS.md` — Group 2400 row from
   "pending — S2400 arc-open queued" → "In-progress: S2400 parent
   scoping (2026-07-05)"; update `last_updated` field
3. Update `docs/research/ARCHITECTURE_INDEX.md` — add §1.N row +
   §8 timeline row + §3 domain map row 27 update (research
   coverage LIGHT → MODERATE post-Cat-A) + §5 gap map update +
   §7 decision matrix update + §9 roadmap update; bump v82 → v83
4. Overwrite `00-START-NEXT-SESSION.md` with S2401 Cat A open
   priorities + arc pin `pa-6279ead1714c4630` reference
5. Commit stagediff (`docs/research/` only) per playbook §16
   commit-policy
6. Write `docs/handoffs/SESSION_2400_AUTH_PARENT_SCOPING.md`

**Post-commit docs cascade** per `feedback_docs_cascade_at_every_close.md`
+ `feedback_cascade_pr_must_include_embed_step.md`:
1. `python manage.py build_docs_index`
2. `python manage.py build_rag_corpus`
3. `python manage.py sync_docs_index_to_documents`
4. `python manage.py sync_docs_index_to_documents --embed` (or
   `python manage.py embed_documents --all-unembedded`) — state
   chunk count in PR body as evidence
5. `python manage.py build_docs_provenance`

**Arc target close cascade at S2499 xx99** (deferred; not this
session):
- SIGN cycle 1 canonical summary; fold; commit
- ARCHITECTURE_INDEX v-bump + OPEN_ARCS Group 2400 → Closed
  transition + §22 next-arc queue update
- Arc pin retirement (`session_tool.retire pa-6279ead1714c4630`)
  per playbook §16 arc-close discipline; ELEVENTH formal arc-pin
  retirement in Research OS
- 4-step docs cascade + build_docs_provenance
- SESSION_2499 handoff
- Next-arc D-override determination (candidate: Group 2500 API per
  T2 handoff bundle from Group 2200; or Group 2600 PA per T3
  handoff bundle)

---

## Appendix — Frontmatter provenance

**Session:** S2400
**Repo state at draft:** `main @ be56a17d` (post-S2299 canonical
summary + arc close merge PR #2907; working tree clean minus
`.claude/scratch/`).
**Arc pin:** `pa-6279ead1714c4630` (ELEVENTH formal arc pin under
Research OS)
**SIGN pin:** pending fresh isolation pin at Rigby SIGN cycle 1
(if Chris routes to formal light SIGN rather than ratify directly).
**Draft written:** 2026-07-05 post-shape-card ratification.

**Prior parent-scoping exemplar consulted (structural reference):**
`docs/research/domains/frontend/2200_frontend_domain_scoping.md`
(NINTH §11.1 application; 1,026 lines; Chris ratified "agree all"
2026-07-05).

**Cited runtime evidence.**
- `core/auth_middleware.py` (UnifiedTokenAuthenticationMiddleware
  ~108 PUBLIC_PATHS + STAFF_REQUIRED_PATHS + REVIEWER_BLOCKED_PATHS)
- `core/services/fleet_auth_drf.py` (FleetSignatureAuthentication
  HMAC + permissive fallback)
- `core/vip_middleware.py` (VIP demo prompt-only)
- `frontend/src/lib/api.ts:48-56` (silent-401 sole handler + BRITTLE
  whitelist)
- `frontend/src/pages/BettingPage.tsx` (money-path CRITICAL sample)
- `docs/PLATFORM_INVENTORY.md` (Git HEAD `f3fe1493`)

**Cited research evidence.**
- `docs/research/platform_architecture_inventory.md` §3.27 (row 27
  PARTIAL + LIGHT post-S1273 v2 Rigby review)
- `docs/research/domains/frontend/2299_frontend_canonical_summary.md`
  §5.4 (i) + §8.2 T1 (Group 2400 Auth cross-arc handoff bundle)
- `docs/research/domains/frontend/2201_frontend_routes_pages_layouts_components_audit.md`
  §14.3 + §15.5
- `docs/research/domains/frontend/2203_frontend_api_contract_boundary_discipline_audit.md`
  §14 F3 + F3.5 + A3 + §19.1 R2
- `docs/research/domains/frontend/2204_frontend_session_state_persistence_discipline_audit.md`
  §14 F1 + F6 + F8 + §19.1 R1
- `docs/research/governance_authority_evolution.md` §2.5 (adjacent
  authority plane demarcation)
- `docs/EMPLOYEE_OS_PRIMITIVES.md` (consumer-side auth surface)

**Playbook applications.**
- §11.1 20-section parent-scoping template TENTH application
- §14 verifier-loop REQUIRED CODIFICATION-CONFIRMED discipline
- §15 SIGN cycle 1 OPTIONAL-LIGHT at parent scoping
- §16 arc pin: `pa-6279ead1714c4630` ACTIVE (ELEVENTH formal arc
  pin); prior `pa-f7fd5016600f4513` RETIRED at S2299 close (TENTH
  formal arc-pin retirement)

**Verifier-loop check (per playbook §14 pre-draft discipline).**
- ✓ File:line cited for every load-bearing runtime reference above
- ✓ Adjacent-arc boundary preservation cited (governance_authority
  vs auth demarcation from S1999 canonical summary)
- ✓ Anti-scope leak vector guardrails enumerated §7.1
- ✓ Runtime counts NOT invented (defer to Cat A audits for concrete
  numbers on PUBLIC_PATHS + trust-boundary rates)
- ✓ No SPECULATIVE claims marked as fact — one SPECULATIVE flag
  raised (§2.3 "No cookie SameSite/Secure default declared in
  searchable form"; Cat C audit will verify)
