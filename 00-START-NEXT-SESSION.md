# Next Session — Start Here

---

## READ THIS FIRST — LOCAL vs PRODUCTION RIGBY TRAP + S2400 CLOSED + S2401 CAT A QUEUED

`tools/pa_chat.py:41` has `DEFAULT_BASE_URL = "http://localhost:8000"` (already local by default as of S1249 PR #2712). The `.env` file's `PA_API_TOKEN` is the **production** token — if you call `pa_chat.py` bare against local without a local-token override, you'll get 401. Always use `tools/pa_local.sh` (sets URL + local token).

**S2400 GROUP 2400 AUTH PARENT SCOPING COMMITTED AT 2026-07-05.** Group 2400 Auth arc pin `pa-6279ead1714c4630` ACTIVE (ELEVENTH formal arc pin under Research OS after Groups 1300/1400/1500/1600/1700/1800/1900/2000+/2100/2200 prior ten). `tools/pa_local.sh:280` already points to it. S2400 SIGN pin `pa-32400781523b4d5b` retired at parent-scoping SIGN cycle 1 close (ELEVENTH consecutive dedicated fresh SIGN pin retirement — 10 xx99 + 1 parent-scoping-light-SIGN).

### The correct LOCAL invocation
```bash
tools/pa_local.sh "message"
```

**Before your first `pa_local.sh` call each session, ask Rigby to run `platform_config_tool overview` and confirm `service_context: local`.** Pin ownership already verified as chris at S2400 open (conversation_owner_match=true).

## READ THIS SECOND — GROUP 2400 AUTH ARC OPEN; NEXT = S2401 P1 CAT A AUTHENTICATION SURFACE + TRUST BOUNDARIES

**Group 2400 Auth: S2400 parent scoping CLOSED 2026-07-05.** Chris "agree all + commit it" 2026-07-05 wholesale-ratified 4-child taxonomy + tightened lens + 6-criterion acceptance + 6-item anti-scope + Rigby SIGN cycle 1 SIGN-with-edits 4 folds (all landed pre-commit). TENTH application of playbook §11.1 parent-scoping template per S2299 close statement.

- **Arc pin ACTIVE:** `pa-6279ead1714c4630` per playbook §16 arc-open fresh-thread discipline (ELEVENTH formal arc pin)
- **SIGN pin RETIRED:** `pa-32400781523b4d5b` at parent-scoping SIGN cycle 1 close (updated_count=4)
- **Arc progress:** S2400 parent scoping (shipped) → **S2401 P1 Cat A Authentication Surface + Trust Boundaries (NEXT)** → S2402 P2 Cat B → S2403 P3 Cat C → S2404 P4 Cat D → S2499 xx99. Runtime target 6 sessions; runtime cap 8.
- **MC-4 dial-back-resolution 5th confirming arc candidate** — Group 2400 4-child structure extends MC-4 CODIFICATION-CONFIRMED across-4-consecutive-arcs (1900+2000++2100+2200) to across-5-consecutive-arcs, resolving S2199 Q3 STRENGTHEN dial-back at S2499 close.

## READ THIS THIRD — S2400 CENTRAL LENS + 6 ACCEPTANCE CRITERIA + 6 ANTI-SCOPE

**Central lens question (Chris "agree all" 2026-07-05, Rigby SIGN-preview tightened wording verbatim):**

*"Is the platform's auth model a contract (explicit trust boundaries + declared permission floors + declared session/refresh/logout semantics + consistent failure surfacing), or an accretion of per-surface defaults whose failures are silently swallowed (e.g., silent 401 / permissive fallbacks / ad-hoc public path lists)?"*

Canonical seam candidate: "defaults that silently swallow failure vs contracts that surface failure" — extends S2299 Group 2200 frontend framing upstream through backend middleware + DRF permission classes + PA workspace context + Fleet HMAC boundary.

**6-criterion acceptance (with "_Measured by:_" clauses per Rigby SIGN cycle 1 Q3 fold):**
1. Permission-floor observability → measured by Cat B endpoint-inventory matrix + untraced-rate reduction
2. Failure surfacing / typed error envelope → measured by Cat D api.ts audit + call-site classification + envelope candidate-design
3. Logout cleanup contract → measured by Cat C 15-surface cleanup table + Zustand persist logout hygiene
4. Session lifecycle discipline / token refresh declared + observable → measured by Cat C session-model inventory + Chris-D-verdict
5. Cross-arc coordination flags preserved → measured by xx99 §5.4 flag count ≥ 2
6. **Trust boundary inventory explicit + testable** (Rigby SIGN-preview fold) → measured by Cat A trust-boundary registry existence + smoke-test coverage inventory

**6-item anti-scope:**
1. No backend API design (Group 2500)
2. No PA behavior spec (Group 2600)
3. No frontend framework migration (Group 2200 §7 preserved)
4. No mobile app auth (Group 2300)
5. No new session-model authoring at parent scope (design-preparation only per playbook §5 phase discipline)
6. **No new auth provider additions (SSO/OAuth) at parent scope** (Rigby SIGN-preview fold)

## READ THIS FOURTH — S2401 P1 CAT A SCOPE (AUTHENTICATION SURFACE + TRUST BOUNDARIES)

**S2401 = P1 Cat A first child audit under Group 2400.** SIXTEENTH-consecutive application of playbook §11.2 20-section child-audit template after S1301+S1401+S1501+S1601+S1701+S1801+S1901+S2001+S2101+S2102+S2103+S2104+S2201+S2202+S2203+S2204 prior fifteen.

**Scope** (per S2400 parent scoping §3.A):
- Enumerate every authentication mechanism the platform runs (standard user token auth + ~108 PUBLIC_PATHS + STAFF_REQUIRED_PATHS + REVIEWER_BLOCKED_PATHS + FleetSignatureAuthentication HMAC + VIP demo prompt-only + service tokens)
- For each mechanism: intended caller class + allowed routes + gate type (hard runtime vs soft prompt-only vs permissive fallback) + failure mode

**Central question the audit answers.** *Does the platform have an explicit, enumerated trust-boundary inventory across every auth mechanism it runs, or has the authentication surface accreted via per-mechanism defaults without a single source-of-truth inventory?*

**Expected outputs (per S2400 §3.A):**
- (a) Auth mechanism inventory — full enumeration with gate type + intended caller + allowed routes
- (b) Trust boundary inventory — hard runtime gate vs soft prompt-only vs permissive fallback classification per mechanism
- (c) PUBLIC_PATHS audit — the ~108 entries categorized by intent (health / demo / public-read / callback / never-should-be-public); flag drift candidates
- (d) VIP demo enforcement audit — quantify blast radius of prompt-only gate; propose runtime-gate design candidates (research only, not authoring)
- (e) Fleet permissive fallback audit — quantify silent-accept path; distinguish grace-period-intent from tech-debt
- (f) Service token audit — PA_DB_HEALTH_RPC_TOKEN + PUBLIC_INTEL_TOKEN scope + rotation policy + default-off behavior
- (g) Smoke-test coverage inventory — blocker to acceptance criterion #6

**Load-bearing inputs (Cat A must consume + re-verify at HEAD):**
- `core/auth_middleware.py` (UnifiedTokenAuthenticationMiddleware — full read; verify ~108 PUBLIC_PATHS + STAFF_REQUIRED_PATHS + REVIEWER_BLOCKED_PATHS at HEAD line ranges)
- `core/services/fleet_auth_drf.py` (FleetSignatureAuthentication — full read; verify HMAC + permissive fallback at HEAD)
- `core/vip_middleware.py` (VIP demo — full read; verify prompt-only + no runtime gate at HEAD)
- `docs/research/platform_architecture_inventory.md` §3.27 (Auth / Permissions / Security row 27 baseline)
- `docs/research/governance_authority_evolution.md` §2.5 (36-45 primitives — adjacent authority plane; boundary preservation)
- `docs/EMPLOYEE_OS_PRIMITIVES.md` (GovernanceState + KillSwitch runtime consumers; consumer-side reference only)
- `docs/research/domains/auth/2400_auth_domain_scoping.md` §2 evidence-provenance disclaimer + §3.A expected outputs + §3.5 Auth-adjacent probes disposition + §7.1 leak-vector guardrails

**Sub-agent dispatch** per playbook §13 six-parallel-agent shape:
- Agent 1 Models + Persistence — token model + authtoken + UnifiedUser + auth-related migrations
- Agent 2 Services + Runtime Flows — auth-middleware call graph + FleetSignatureAuthentication + VIP demo flow
- Agent 3 APIs + Tools + Tasks + Commands — auth endpoints + management commands (token rotation etc.)
- Agent 4 Integrations + Cross-Domain — authority-vs-authentication demarcation preservation (Group 1900 boundary) + PA workspace-context adjacency (Group 2600 handoff)
- Agent 5 Documentation + Prior Research — §3.27 baseline + governance_authority_evolution.md + EMPLOYEE_OS_PRIMITIVES.md + gap analysis (no `docs/topics/auth.md` exists yet)
- Agent 6 Drift + Debt + Ownership + Maturity — verify S1273 v2 PARTIAL classification at HEAD + trust-boundary rate + smoke-test coverage inventory

**Rigby SIGN cycle 1 REQUIRED** per playbook §15 stage-scoped routing (child audit = required full SIGN via dedicated fresh isolation pin). Expected cadence: 4-batch × 5-Q = 20 total Q per S2201-S2204 five-consecutive tested child-audit pattern (not single-batch × 4-Q; that's parent-scoping-light-SIGN cadence). SIXTH-consecutive 20-Q cadence application candidate.

## READ THIS FIFTH — OUTSTANDING RESIDUALS

### S2400 arc-open cascade residuals

Per Chris "commit it" ratification at S2400 close:

- **Post-commit docs cascade** — 4-step cascade (`build_docs_index` + `build_rag_corpus` + `sync_docs_index_to_documents` + `sync_docs_index_to_documents --embed`) + `build_docs_provenance` per `feedback_docs_cascade_at_every_close` + `feedback_cascade_pr_must_include_embed_step`. Execute post-merge.
- **Auth topic doc gap** — `docs/topics/auth.md` does NOT exist. Candidate S2499 xx99 anchor-update recommendation post-arc (per S2400 parked candidate #8).
- **`PLATFORM_INVENTORY §Auth` autoblock gap** — no dedicated Auth autoblock exists. Candidate S2499 xx99 anchor-update recommendation for inventory generator extension (per S2400 §2.1 anchor drift observation).
- **Threat model / trust-boundary doc gap** — §3.27 explicitly notes gap. Parked candidate #1 per S2400 §6 (NOT this arc's authoring scope; post-arc ADR if Chris ratifies).

### Group 2200 T-slot follow-on queue (owed to Group 2400+ execution)

- **T1 Group 2400 Auth cross-arc handoff bundle** — being executed by THIS arc (S2401-S2404) — silent-401 + logout cleanup + session lifecycle + permission-floor uniformity
- **T2 Group 2500 API cross-arc handoff bundle** — contract SoT + drf-spectacular platform-wide + canonical User + workspace_id + REST↔WS T7 joint 2500+2600 — NEXT arc after Group 2400 close per S2299 §8.2
- **T3 Group 2600 PA cross-arc handoff bundle** — workspace-context resolver + persistence contract + WS↔polling consolidation + Path D1/D2 — QUEUED after Group 2500 close
- **T4 Group 1700 Observability cross-arc handoff bundle** — envelope enforcement locus + Session 968 X-UI-Scope ring buffer ownership — QUEUED after Group 2600 close
- **Maintainer-decision batch (5 items governance gate)** — CODEOWNERS + DEAD-CANDIDATE consolidated cleanup + api.ts extraction + storageKeys registry + cockpitApi ownership
- **T2 post-arc T-slot (10 items)** — R2 Child E god-component subdivision Chris-gated + R1 test framework parallel + R3 routes.config source of truth + others per S2299 §8
- **T3 conditional post-arc (4 items)** — cross-tab sync + Betting session-scoped state + runtime schema validation + REST↔WS joint T7

### S2199 post-arc T-slot execution queue (unchanged carry into S2401)

19 T-slot items distributed across 6 arcs + Employee OS per S2199 §8. All post-arc execution, NOT blocking S2401.

### Session count status

- Group 2400 In-progress at 1 of 6 sessions (S2400 parent scoping shipped)
- Next child = S2401 P1 Cat A Authentication Surface + Trust Boundaries
- Next `xx99` at S2499 canonical summary (playbook §11.3 ELEVENTH application per current TENTH baseline)

## SESSION READY CHECK (before opening S2401 P1 Cat A)

Before drafting the S2401 child audit doc:

1. `tools/pa_local.sh "platform_config_tool action=overview"` → confirm `service_context: local` (Group 2400 arc pin `pa-6279ead1714c4630` ACTIVE at S2400 open; `tools/pa_local.sh:280` already rotated)
2. Read `docs/research/DOMAIN_RESEARCH_PLAYBOOK.md` §11.2 20-section child-audit template + §11.2 exemplar chain (S2204 P4 most recent) for shape reference
3. Read `docs/research/domains/auth/2400_auth_domain_scoping.md` §3.A P1 Cat A expected outputs + §3.5 auth-adjacent probes disposition + §7.1 leak-vector guardrails + §2 evidence-provenance disclaimer (ESTIMATE labeling requirement)
4. Read `docs/research/platform_architecture_inventory.md` §3.27 (row 27 Auth / Permissions / Security prior-coverage baseline)
5. Read `core/auth_middleware.py`, `core/services/fleet_auth_drf.py`, `core/vip_middleware.py` full at HEAD for line-anchor re-verification (per S2400 §2 evidence-provenance disclaimer requirement)
6. Read `docs/research/governance_authority_evolution.md` §2.5 (36-45 primitives — adjacent authority plane) + `docs/EMPLOYEE_OS_PRIMITIVES.md` (consumer-side reference)
7. Dispatch 6-Explore-agent parallel sweep per playbook §13 (Agents 1-6 per §3.A expected outputs)
8. Draft the 20-section audit per §11.2 skeleton; verifier-loop per §14 discipline pre-Rigby-SIGN
9. Route to Rigby SIGN cycle 1 via dedicated fresh isolation pin per playbook §15 (child audit = required full SIGN); expected cadence 4-batch × 5-Q = 20-Q per S2201-S2204 five-consecutive tested child-audit pattern
10. Fold SIGN edits; land as `status: draft` on filesystem; present Chris ratification card
11. Arc pin `pa-6279ead1714c4630` preserved through S2401-S2404 per playbook §16 arc-standard behavior + MC-4 CODIFICATION-CONFIRMED-with-scope-guardrails

**S2401 open command (Chris short command):** `Continue research group 2400: P1 Cat A` or `Continue research group 2400: authentication surface` or equivalent invocation.
