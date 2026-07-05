# Next Session — Start Here

---

## READ THIS FIRST — LOCAL vs PRODUCTION RIGBY TRAP + GROUP 2200 CLOSED + GROUP 2400 QUEUED

`tools/pa_chat.py:41` has `DEFAULT_BASE_URL = "http://localhost:8000"` (already local by default as of S1249 PR #2712). The `.env` file's `PA_API_TOKEN` is the **production** token — if you call `pa_chat.py` bare against local without a local-token override, you'll get 401. Always use `tools/pa_local.sh` (sets URL + local token).

**GROUP 2200 CLOSED AT S2299 2026-07-05.** Group 2200 Frontend (Contract-Surface Arc) arc pin `pa-f7fd5016600f4513` RETIRED at S2299 close via `session_tool.retire` per playbook §16 arc-close discipline (TENTH formal arc-pin retirement in Research OS). S2299 SIGN pin `pa-c40f0a79d5f54fcc` also retired at cycle close. **`tools/pa_local.sh:234` still dispatches into `pa-f7fd5016600f4513`** — needs rotation to new Group 2400 Auth arc pin at S2400 arc-open (via `session_tool.create_fresh` per playbook §16 arc-open fresh-thread discipline; ELEVENTH formal arc pin under Research OS after Groups 1300/1400/1500/1600/1700/1800/1900/2000+/2100/2200 prior ten).

### The correct LOCAL invocation
```bash
tools/pa_local.sh "message"
```

**Before your first `pa_local.sh` call each session, ask Rigby to run `platform_config_tool overview` and confirm `service_context: local`.** After S2400 arc-open, verify pin ownership per `feedback_pa_local_verify_ownership.md`.

## READ THIS SECOND — GROUP 2200 S2299 CANONICAL SUMMARY CLOSED; NEXT = S2400 GROUP 2400 AUTH ARC-OPEN

**Group 2200 Frontend (Contract-Surface Arc): S2299 xx99 canonical summary CLOSED 2026-07-05.** Chris "agree all + (6) = 2400 Auth" 2026-07-05 ratified all 6 close-card items wholesale (4-fold SIGN cycle 1 acceptance + §7 anchor-update batch scope as single atomic follow-up PR + ~38 T-slot follow-on queue four-track structure + meta-methodology milestone updates MC-3 9→10 + MC-4 3→4 + MC-5 12→16 + MC-10 1→5 + 4 new milestone-CANDIDATES MC-11/MC-12/MC-13/MC-14 + arc-close cascade sequence + **next-arc D-override = Group 2400 Auth**). TENTH-consecutive application of playbook §11.3 12-section canonical-summary template + §11.3 §10 meta-methodology TENTH application after S1399 first + S1499 second + S1599 third + S1699 fourth + S1799 fifth + S1899 sixth + S1999 seventh + S2099 eighth + S2199 ninth. Runtime target 6 sessions ACHIEVED — **6 of 6 shipped** (S2200 parent + S2201 P1 + S2202 P2 + S2203 P3 + S2204 P4 + S2299 xx99).

- **Arc pin RETIRED:** `pa-f7fd5016600f4513` retired at S2299 close via `session_tool.retire` per playbook §16 arc-close discipline (TENTH formal arc-pin retirement in Research OS after S1399/S1499/S1599/S1699/S1799/S1899/S1999/S2099/S2199 prior nine). SIGN pin `pa-c40f0a79d5f54fcc` retired at cycle close per playbook §15 SIGN-isolation discipline (TENTH consecutive dedicated fresh SIGN pin retirement for canonical-summary shape).
- **Arc progress:** S2200 parent scoping (shipped) → S2201 P1 Child A Routes+Pages+Layouts+Component Patterns (shipped) → S2202 P2 Child B WebSocket Consumer Surface + `ui.render_hint` Envelope (shipped) → S2203 P3 Child C Frontend↔Backend API Contract + Boundary Discipline (shipped) → S2204 P4 Child D Session-scoped State Management + Persistence Discipline (shipped) → **S2299 xx99 Canonical Summary (shipped this session)**. Runtime target 6 sessions ACHIEVED — **6 of 6 shipped**.
- **Next-arc D-override:** **Group 2400 Auth** per highest cross-arc-handoff frequency signal (4/4 Group 2200 children reference silent-401 + logout cleanup + session lifecycle + permission-floor uniformity — S2201 §14.3 + §15.5 + S2202 no-drift-but-perms-floor-owned-here + S2203 §14 F3 + F3.5 + S2204 §19.1 R1). MC-4 dial-back-resolution 5th confirming arc candidate.

## READ THIS THIRD — S2299 CANONICAL SEAM STATEMENT + 6 CROSS-CUTTING PATTERNS

**Canonical seam statement (§5.1 verbatim post-Rigby SIGN Q1 STRENGTHEN fold):** *"The frontend at HEAD `294512e3` is an accreted UI mesh with declared-but-unenforced contracts — structurally healthy at the routing / auth-wrapper / layout / Zustand-persist boundary but structurally under-specified at the page-component / consumer-contract / API-typing / state-discipline boundary — where three of four contract-surface axes examined by this arc (component-boundary + envelope + API-typing) generalize as SYSTEMIC deficiencies with surface variance across the examined child surfaces, one axis (state persistence) is SURFACE-LOCAL + DOMAIN-SPECIFIC HYBRID confined to `/betting`, and the fix path is wiring the design-latent contract infrastructure (partially scaffolded; unevenly wired — e.g., drf-spectacular is sports-wired but not platform-wide; Zustand persist is 3-of-7-stores-adopted; `ui.render_hint` envelope is 0-of-40-conformant; error boundaries are 0-adopted) through cross-arc coordination with Group 2400 Auth + Group 2500 API + Group 2600 PA + Group 1700 Observability — not framework migration."*

**Six §4 cross-cutting patterns** (post-Rigby SIGN Q2 STRENGTHEN +2 additions §4.7 + §4.8):
- §4.1 no-CODEOWNERS + LIGHT-ownership across all 4 children
- §4.2 silent-failure defaults across P1+P2+P3
- §4.3 untyped/uncontracted defaults across P2+P3+P4 (design-latent infrastructure exists but unwired)
- §4.4 DEAD-CANDIDATE/MOCK-DATA/INTENT-NEUTRAL pattern class recurrence across P2+P3
- §4.5 god-file/god-component ≥1,500 LOC threshold across UI+infrastructure layers
- §4.6 cross-arc DEFER-with-escape-hatch pattern applied 3 times within-arc (MC-13 candidate)
- **§4.7 Context propagation fragility** — workspace identity + global dock coupling — Rigby SIGN Q2 addition
- **§4.8 Anchor + inventory drift** — docs + system inventories lag reality — Rigby SIGN Q2 addition

## READ THIS FOURTH — S2400 GROUP 2400 AUTH SCOPE

Per Chris D-override at S2299 close 2026-07-05. Group 2400 Auth = **ELEVENTH formal arc under the Research OS** after Groups 1300/1400/1500/1600/1700/1800/1900/2000+/2100/2200 prior ten. TENTH application of playbook §11.1 20-section parent-scoping template (per S2299 close; specific §11.1 skipped-arc identification deferred to S2499 xx99 close if load-bearing).

**S2400 load-bearing input from Group 2200 T1 cross-arc handoff bundle:**
- **Silent-401 SYSTEMIC resolution** — ~630 of ~1,300 gated call-sites at silent-401 risk (grep-based estimate hedged for wrapper duplicates per S2203 Q14 STRENGTHEN); `frontend/src/lib/api.ts:48-56` sole 401 handler with whitelist substring `/auth/` + `/login` (BRITTLE — MED per S2203 §14 F3.5); S2201 §14.3 MINOR two-stage cockpit drift; S2201 §15.5 silent 401 systemic HIGH baseline (CRITICAL for money-path/governance-path endpoints).
- **Logout cleanup contract** — 15 persistent-state surfaces potentially affected (12 direct localStorage keys + 3 Zustand persist stores; per S2204 F1 inventory); S2204 §14 F6 F8 no-cleanup-on-logout; S2204 §19.1 R1 two-sided FE-symptom-vs-BE-model framing.
- **Session lifecycle model** — token refresh + cookie SameSite/Secure defaults + explicit re-login vs silent-refresh + Clear-Site-Data header decision; S2204 §19.1 R1.
- **Per-endpoint permission floor uniformity** — three-option-space decision per S2203 §19.1 R2: (a) uniform IsAuthenticated across all `/v1/**` + client-side auth-gate + observable-error surfacing; (b) uniform AllowAny for read paths + IsAuthenticated for writes + client-side auth-check-on-write; (c) per-endpoint permission registry.

**S2400 acceptance criteria proposal (Chris-ratifiable at parent-scoping SIGN cycle 1):**
1. Every gated endpoint declares its permission-floor contract observably (client + server agree).
2. Auth failures surface to caller with typed error envelope (silent-401 anti-pattern extinct).
3. Logout eagerly clears all client-side per-user storage per declared cleanup contract.
4. Token refresh discipline (silent-refresh vs explicit re-login) is declared + observable.
5. Cross-arc coordination flags to Group 2500 API (per-endpoint permission registry) + Group 2600 PA (workspace-context vs user-context split) preserved.

**S2400 anti-scope proposal (Chris-ratifiable at parent-scoping):**
- No backend API design (Group 2500 API scope).
- No PA behavior spec (Group 2600 PA scope).
- No frontend framework migration (Group 2200 §7 anti-scope preserved).
- No mobile app auth (Group 2300 Mobile scope; row 19 stays deferred).
- No new session-model authoring at parent scope (design-preparation only per playbook §5 phase discipline).

## READ THIS FIFTH — OUTSTANDING RESIDUALS

### S2299 arc-close cascade residuals

Per Chris "agree all + (6) = 2400 Auth" ratification at S2299 close:

- **Post-commit docs cascade** — 4-step cascade (`build_docs_index` + `build_rag_corpus` + `sync_docs_index_to_documents` + `sync_docs_index_to_documents --embed`) + `build_docs_provenance` per `feedback_docs_cascade_at_every_close` + `feedback_cascade_pr_must_include_embed_step`. Execute post-merge.
- **PLATFORM_INVENTORY §Frontend `gather_inventory()` extension** — 3 new sub-sections (WebSocket Consumer Surface + REST API Contract Surface + Session-scoped State + Persistence Surface). Follow-up PR (Python code change; deferred from S2299 close per pragmatic scope). Runtime-derivable via inventory generator extension per §7.1.
- **PLATFORM_WHAT_IT_IS.md 'Frontend contract-surface governance' narrative subsection** — Follow-up PR (narrative-authored edit; deferred from S2299 close per pragmatic scope). See §7.2.

### Group 2200 T-slot follow-on queue owed to future arcs

- **T1 Group 2400 Auth cross-arc handoff bundle** — silent-401 + logout cleanup + session lifecycle model + permission-floor uniformity — S2400 first-order execution
- **T2 Group 2500 API cross-arc handoff bundle** — contract SoT + drf-spectacular platform-wide + canonical User + workspace_id + REST↔WS T7 joint 2500+2600
- **T3 Group 2600 PA cross-arc handoff bundle** — workspace-context resolver + persistence contract + WS↔polling consolidation + Path D1/D2
- **T4 Group 1700 Observability cross-arc handoff bundle** — envelope enforcement locus + Session 968 X-UI-Scope ring buffer ownership
- **Maintainer-decision batch (5 items governance gate)** — CODEOWNERS + DEAD-CANDIDATE consolidated cleanup + api.ts extraction + storageKeys registry + cockpitApi ownership
- **T2 post-arc T-slot (10 items)** — R2 Child E god-component subdivision Chris-gated + R1 test framework parallel + R3 routes.config source of truth + R5 cockpit retirement + R6 error-boundary framework + R7 session-annotation retrofit + R8 route-count reconciliation + R4 Route↔Consumer registry + R9 CI lint + R7 MSW integration tests
- **T3 conditional post-arc (4 items)** — cross-tab sync + Betting session-scoped state + runtime schema validation + REST↔WS joint T7

### S2199 post-arc T-slot execution queue (unchanged carry into S2400)

19 T-slot items distributed across 6 arcs + Employee OS per S2199 §8. All post-arc execution, NOT blocking S2400.

### Session count status

- Group 2200 CLOSED at 6 of 6 sessions
- Group 2400 pending arc-open at next session (S2400)
- Next `xx99` at S2499 canonical summary (playbook §11.3 ELEVENTH application per current TENTH baseline)

## SESSION READY CHECK (before opening S2400 Group 2400 Auth parent scoping)

Before drafting the S2400 parent scoping doc:

1. `tools/pa_local.sh "platform_config_tool action=overview"` → confirm `service_context: local` (Group 2200 arc pin `pa-f7fd5016600f4513` retired at S2299 close; `tools/pa_local.sh:234` needs rotation to new S2400 Group 2400 Auth arc pin at arc-open via `session_tool.create_fresh` — ELEVENTH formal arc pin under Research OS)
2. Read `docs/research/DOMAIN_RESEARCH_PLAYBOOK.md` §11.1 20-section parent-scoping template + §11.1 exemplar chain (S2200 parent scoping most recent) for shape reference
3. Read `docs/research/domains/frontend/2299_frontend_canonical_summary.md` T1 cross-arc handoff bundle (§8.2 T1 Group 2400 Auth) as load-bearing input
4. Read `docs/research/domains/frontend/2201_frontend_routes_pages_layouts_components_audit.md` §14.3 + §15.5 (silent-401 systemic + MINOR two-stage cockpit drift) + `2203_frontend_api_contract_boundary_discipline_audit.md` §14 F3 + F3.5 (silent-401 SYSTEMIC + auth-endpoint whitelist BRITTLE) + `2204_frontend_session_state_persistence_discipline_audit.md` §19.1 R1 (session lifecycle + cleanup contract two-sided framing) as evidence baseline
5. Read `docs/research/platform_architecture_inventory.md` row 22 (Auth / Permissions) for prior-arc research coverage baseline
6. Plan S2400 acceptance criteria + anti-scope + child-taxonomy per playbook §11.1
7. Plan Rigby SIGN cycle 1 batching per `feedback_rigby_sign_worker_instability_recovery` — parent scoping shape is smaller than child audits; may fit 4-batch × 3-Q cadence per S2200 precedent
8. Plan §8 D-verdicts + Chris "agree all" batch discipline
9. Consider MC-4 dial-back-resolution 5th confirming arc candidate — Group 2400 Auth 4-child structure would trigger resolution of S2199 Q3 STRENGTHEN dial-back per §5.3 Group 2200 canonical summary
10. Mint fresh Group 2400 Auth arc pin at S2400 open via `session_tool.create_fresh` per playbook §16 arc-open fresh-thread discipline; ELEVENTH formal arc pin under Research OS
11. Rotate `tools/pa_local.sh:234` to new arc pin + update header ledger with S2200 retirement (pa-f7fd5016600f4513) + S2400 open stanzas per S2200 documentation pattern

**S2400 open command (Chris short command):** `Start research group 2400: Auth` or `Continue research group 2400: parent scoping` or equivalent invocation.
