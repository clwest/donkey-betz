# Next Session — Start Here

---

## READ THIS FIRST — LOCAL vs PRODUCTION RIGBY TRAP + S2402 CLOSED + S2403 CAT C QUEUED

`tools/pa_chat.py:41` has `DEFAULT_BASE_URL = "http://localhost:8000"` (already local by default as of S1249 PR #2712). The `.env` file's `PA_API_TOKEN` is the **production** token — if you call `pa_chat.py` bare against local without a local-token override, you'll get 401. Always use `tools/pa_local.sh` (sets URL + local token).

**S2402 GROUP 2400 AUTH P2 CAT B CHILD AUDIT COMMITTED AT 2026-07-05.** Group 2400 Auth arc pin `pa-6279ead1714c4630` PRESERVED through S2402 per playbook §16 arc-standard behavior + MC-4 CODIFICATION-CONFIRMED-with-scope-guardrails (MC-14 CANDIDATE-threshold-satisfied extended to 3-arc-stages via Group 2200 + Group 2400 Cat A + Group 2400 Cat B = 3 confirming arc-stages). `tools/pa_local.sh:280` unchanged. S2402 SIGN pin `pa-d1d4c68981fc4b3c` retired at child-audit SIGN cycle 1 close (THIRTEENTH consecutive dedicated fresh SIGN pin retirement — 10 xx99 + 1 parent-scoping-light-SIGN + 1 Cat A child audit + this cycle).

### The correct LOCAL invocation
```bash
tools/pa_local.sh "message"
```

**Before your first `pa_local.sh` call each session, ask Rigby to run `platform_config_tool overview` and confirm `service_context: local`.** Pin ownership already verified as chris at S2401 open (conversation_owner_match=true) — Cat A + Cat B preserved pin, so verification carries forward.

## READ THIS SECOND — GROUP 2400 AUTH ARC IN-PROGRESS (3 OF 6 SHIPPED); NEXT = S2403 P3 CAT C SESSION LIFECYCLE + LOGOUT CLEANUP CONTRACT

**Group 2400 Auth: S2402 P2 Cat B CLOSED 2026-07-05.** Chris "commit it" 2026-07-05 ratified 20-fold SIGN-with-edits wholesale at MED-HIGH confidence (~0.8; higher than Cat A 0.74); status flipped `draft` → `active`. SEVENTEENTH-consecutive application of playbook §11.2 20-section child-audit template per S2401 handoff.

- **Arc pin PRESERVED:** `pa-6279ead1714c4630` per playbook §16 arc-standard behavior (retirement at S2499 close)
- **SIGN pin RETIRED:** `pa-d1d4c68981fc4b3c` at S2402 SIGN cycle 1 close (updated_count=1)
- **Arc progress:** S2400 parent scoping (shipped) + S2401 P1 Cat A (shipped) + S2402 P2 Cat B (shipped) → **S2403 P3 Cat C Session Lifecycle + Logout Cleanup Contract (NEXT)** → S2404 P4 Cat D → S2499 xx99. Runtime target 6 sessions — **3 of 6 shipped**; runtime cap 8.
- **MC-4 dial-back-resolution 5th confirming arc candidate** — Group 2400 4-child structure post-S2402 close continues MC-4 CODIFICATION-CONFIRMED-with-scope-guardrails momentum toward across-5-consecutive-arcs, resolving S2199 Q3 STRENGTHEN dial-back at S2499 close.

## READ THIS THIRD — S2402 CAT B LOAD-BEARING INPUTS FOR S2403 CAT C

**S2402 7 headline findings (post-Rigby-SIGN-fold ranking):**

- **F-B-CRIT-1** Permission-floor implicit-inheritance rate ~80-90% ESTIMATE whole-platform (CRITICAL for observability; LOW for correctness; ~1,200-1,600 of ~1,866 endpoints inherit `IsAuthenticated` from `DEFAULT_PERMISSION_CLASSES` at `core/settings.py:652-653`)
- **F-B-CRIT-2** S2203 F3 silent-401 SYSTEMIC as DOWNSTREAM SYMPTOM of F-B-CRIT-1 (necessary-enabling-condition causal chain; option (b) client-side auth-check-on-write minimum intervention)
- **F-B-HIGH-1** STAFF_REQUIRED_PATHS 2-of-3 PHANTOM (`/api/v1/admin/` + `/api/v1/metrics/admin/` verifier-loop grep-verified NO `path()` registration; only `/api/v1/system/reality-check/` at `core/urls.py:3353` registered)
- **F-B-HIGH-2** Cat A F-BND-4a/4b re-verified at HEAD; `/api/v1/betting/place/` REVIEWER_BLOCKED entry DEAD-CODE (middleware early-returns on PUBLIC match at line 570; REVIEWER check at line 668 never reached)
- **F-B-HIGH-3** Workspace-membership implicit permission gate via WORKSPACE_AWARE_AGENTS 20 agents (Cat B owns identification; Group 2600 PA owns policy per CF-B2 — **direct handoff to Cat C consideration for session-lifecycle workspace context**)
- **F-B-HIGH-4** `@authentication_classes([])` + `[IsAuthenticated]` stacking (4 files: `ai_core/api/freelance_api.py` + `core/views_preferences.py` + `core/auth_views_enhanced.py` + `core/views_nervous.py`; works-by-accident via middleware precedence; `auth_views_enhanced.py` per-site CRITICAL escalation for login/token flows)
- **F-B-MED-1** 2 mythology `@permission_classes([])` empty declarations (hygiene debt)

**§14.5 permission-floor rate table extension** — 21 authorization-plane enforcement loci (10 WORKING + 6 PARTIAL + 4 EXPERIMENTAL + 3 MED-HIGH drift + 1 DEAD) + 2 out-of-table (object-level + serializer-level authorization).

**5 cross-arc coordination flags emitted** (CF-B1 → Group 2500 API registry design-prep + CF-B2 → Group 2600 PA workspace-context authz + CF-B3 → Cat D + Group 2200 Frontend integration point + CF-B4 → Group 2400 arc VIP demo two-layer reference + CF-B5 → Group 1700 Observability 503-fork asymmetry + smoke-test coverage).

**Cat B recommendation lean for xx99 Chris D-verdict:** Option **(b) split-read-write + client-side auth-check-on-write** as PRIMARY for REMEDIATION WINDOW (stabilization step) + Option **(c) per-endpoint permission registry** as PRIMARY for LONG-TERM GOVERNANCE (inevitable convergence target for Group 2500 API arc) + Option **(a) uniform IsAuthenticated NOT recommended**.

**Cat B emerging weak-spot pattern (Q20 fold):** **denominator ambiguity / metric provenance drift** — playbook §20 codification candidate at S2499 xx99 close if 2nd application follows.

**S2403 Cat C inherits from Cat A + Cat B:** Cat A mechanism vocabulary + Cat A §14 F-VIP-1 (VIPInvite.account_expires_at not enforced) + F-TOKEN-1 (DRF authtoken.Token no expiry) + F-SESS-1 (Django session Redis-fallback silent degrade) + Cat B F-B-HIGH-3 workspace-membership implicit-gate + Cat B F-B-DUP-1 role-field bifurcation lifecycle (4-model landscape) + Cat B F-B-OWN-4 STAFF/REVIEWER list ownership + Cat B §13.5 correctness-WORKING-governance-EXPERIMENTAL maturity axis framing.

## READ THIS FOURTH — S2403 P3 CAT C SCOPE (SESSION LIFECYCLE + LOGOUT CLEANUP CONTRACT)

**S2403 = P3 Cat C third child audit under Group 2400.** EIGHTEENTH-consecutive application of playbook §11.2 20-section child-audit template after S1301+S1401+S1501+S1601+S1701+S1801+S1901+S2001+S2101+S2102+S2103+S2104+S2201+S2202+S2203+S2204+S2401+S2402 prior seventeen.

**Scope** (per S2400 parent scoping §3.C):
- Enumerate platform's session model: token issuance + token refresh discipline + cookie SameSite/Secure/HttpOnly defaults + Clear-Site-Data header usage + explicit re-login vs silent-refresh decision + logout endpoint behavior + client-side storage cleanup contract
- Extend to 15 persistent-state surfaces (S2204 F1 inventory) enumerating cleanup contract per surface
- 4-role-field bifurcation lifecycle (Cat A F-DUP-2 + Cat B F-B-DUP-1: platform_role + customer_role + primary_role + AssistantProfile.role across 3 models)
- S2201 §14.3 cockpit two-stage auth MINOR-DRIFT re-verification
- Three-option decision space for silent-refresh vs explicit-re-login vs hybrid

**Central question the audit answers.** *Does the platform have a declared session lifecycle contract (issuance + refresh + logout + cleanup semantics all observable), or does the "no logout cleanup" + "no session lifecycle spec" pattern (S2204 §14 F6 F8 + §19.1 R1) leave session boundaries at BE/FE-implicit-agreement?*

**Expected outputs (per S2400 §3.C):**
- (a) Session model inventory — issuance (`obtain_token`), refresh (does one exist?), logout (`revoke_token` semantics), cookie discipline (SameSite/Secure/HttpOnly/Domain defaults)
- (b) 15-surface storageKeys cleanup contract per surface (does logout clear? does session expiry clear? is discipline declared or accidental?)
- (c) Clear-Site-Data header decision evidence — is it used? Should it be? Blast radius (does it clear third-party cookies affecting demo mode).
- (d) Silent-refresh vs explicit-re-login three-option decision space evidence + Cat C recommendation lean + Chris D-verdict-request
- (e) Cockpit two-stage drift verification (S2201 §14.3 MINOR-DRIFT still-live?)

**Load-bearing inputs (Cat C must consume + re-verify at HEAD):**
- `core/models_vip_invite.py` VIPInvite.account_expires_at (Cat A §15 F-VIP-1) + token_expires_at (72h)
- `rest_framework.authtoken.Token` DRF model (Cat A §14 F-TOKEN-1 no-expiry)
- `core/settings.py:625` REQUIRE_WEBSOCKET_AUTH (Cat A F-WS-1 silently ignored)
- `core/auth_middleware.py` session vs token auth flow (Cat A §7 runtime flows)
- Django session engine `backends.cache` at `core/settings.py` (Cat A F-SESS-1 Redis-fallback silent degrade)
- `docs/research/domains/frontend/2204_frontend_session_state_persistence_discipline_audit.md` §14 F1 15-surface storageKeys inventory + F6 + F8 no-cleanup-on-logout systemic
- `docs/research/domains/frontend/2201_frontend_routes_pages_layouts_components_audit.md` §14.3 cockpit two-stage auth MINOR-DRIFT baseline
- `docs/research/domains/auth/2401_authentication_surface_trust_boundaries_audit.md` §4 UnifiedUser + VIPInvite lifecycle + §14 findings
- `docs/research/domains/auth/2402_authorization_permission_floor_uniformity_audit.md` §17 F-B-DUP-1 4-role-field bifurcation lifecycle + §14.2 F-B-HIGH-3 workspace-membership implicit-gate + §14.2 F-B-HIGH-4 auth_views_enhanced.py stacking session-touching-flow concern

**Sub-agent dispatch** per playbook §13 six-parallel-agent shape:
- Agent 1 Models + Persistence — Token + Session + Cookie models + VIPInvite lifecycle + 4-role-field lifecycle consolidation candidates
- Agent 2 Services + Runtime Flows — Session engine + token refresh service + logout flow + Clear-Site-Data + FE/BE session-boundary contract
- Agent 3 APIs + Tools + Tasks + Commands — auth endpoints logout/refresh semantics + PA session_tool + AssistantProfile session touch points
- Agent 4 Integrations + Cross-Domain — 15-surface storageKeys × cleanup contract table + Zustand persist logout discipline + workspace-context session boundary
- Agent 5 Documentation + Prior Research — S2204 R1 session-lifecycle two-sided framing + S2201 §14.3 cockpit drift + Cat A/B lifecycle findings
- Agent 6 Drift + Debt + Ownership + Maturity — session-model coverage rate + logout cleanup pattern rate + Clear-Site-Data drift + cookie-defaults SPECULATIVE probe from S2400 §2.3

**Rigby SIGN cycle 1 REQUIRED** per playbook §15 stage-scoped routing (child audit = required full SIGN via dedicated fresh isolation pin). Expected cadence: 4-batch × 5-Q = 20 total Q per S2201-S2402 seven-consecutive tested pattern (EIGHTH-consecutive 20-Q cadence application candidate; MC-10 codification-ready-pending-Chris at 8-arc baseline).

## READ THIS FIFTH — OUTSTANDING RESIDUALS

### S2402 arc-close cascade residuals

Per Chris "commit it" ratification at S2402 close:

- **Post-commit docs cascade** — 4-step cascade (`build_docs_index` + `build_rag_corpus` + `sync_docs_index_to_documents` + `sync_docs_index_to_documents --embed`) + `build_docs_provenance` per `feedback_docs_cascade_at_every_close` + `feedback_cascade_pr_must_include_embed_step`. Execute post-merge.
- **Auth topic doc gap** — `docs/topics/auth.md` + `docs/topics/authorization.md` do NOT exist. Cat B AU-B1 recommends BOTH; if separate, MUST cross-link (Rigby Q19 fold). Candidate S2499 xx99 anchor-update recommendations per Cat B §19.4.
- **`PLATFORM_INVENTORY §Auth` + §Authorization autoblock gap** — no dedicated Auth/Authorization autoblocks exist. Candidate S2499 xx99 anchor-update recommendations per Cat A §19.4 AU-1 + Cat B AU-B2.
- **`PLATFORM_WHAT_IT_IS §Auth` + §Authorization narrative subsection gap** — no dedicated Auth/Authorization subsections exist. Candidate S2499 xx99 anchor-update recommendations per Cat A + Cat B §19.4.

### S2402 CRITICAL findings post-arc remediation queue (Cat B additions to Cat A rank-1)

Per Cat B §19.2 rank-1 co-equal P0 batch preserved from Cat A + extended by Cat B (POST-ARC — not this session's authoring scope):

- **F-B-CRIT-1** Permission-floor implicit-inheritance rate ~80-90% ESTIMATE (post-arc option (a)/(b)/(c) Chris D-verdict at xx99)
- **F-B-CRIT-2** Silent-401 SYSTEMIC as F-B-CRIT-1 downstream symptom (deferred to Cat D S2404)
- **Cat A F-CRIT-1** PURGE_SECRET hardcoded fallback remediation (P0 PR)
- **Cat A F-BND-4a** Unauthenticated bet-placement WRITE remediation (P0 PR; permission-floor decision belongs to Cat B / Group 2500)
- **F-B-HIGH-1** STAFF_REQUIRED_PATHS phantom-entries cleanup OR add explicit views
- **F-B-HIGH-4** auth_views_enhanced.py `@authentication_classes([])` + `[IsAuthenticated]` per-site CRITICAL escalation
- **F-B-OWN-6** CI test-harness enforce permission-floor declarations (NEW at Cat B)

### Group 2200 T-slot follow-on queue (owed to Group 2400+ execution — unchanged)

- **T1 Group 2400 Auth cross-arc handoff bundle** — being executed by THIS arc (S2401-S2404) — silent-401 + logout cleanup + session lifecycle + permission-floor uniformity — **S2402 Cat B DELIVERED permission-floor evidence** + Cat C S2403 owns session lifecycle + logout cleanup + Cat D S2404 owns silent-401
- **T2 Group 2500 API cross-arc handoff bundle** — NEXT arc after Group 2400 close per S2299 §8.2 (Cat B CF-B1 elevates registry design-prep candidate)
- **T3 Group 2600 PA cross-arc handoff bundle** — QUEUED after Group 2500 close (Cat B CF-B2 elevates workspace-context authz)
- **T4 Group 1700 Observability cross-arc handoff bundle** — QUEUED after Group 2600 close (Cat B CF-B5 elevates 503-fork asymmetry + smoke-test coverage)
- **Maintainer-decision batch (5 items governance gate)** — CODEOWNERS + DEAD-CANDIDATE consolidated cleanup + api.ts extraction + storageKeys registry + cockpitApi ownership
- **T2 post-arc T-slot (10 items)** — per S2299 §8
- **T3 conditional post-arc (4 items)** — cross-tab sync + Betting session-scoped state + runtime schema validation + REST↔WS joint T7

### S2199 post-arc T-slot execution queue (unchanged carry into S2403)

19 T-slot items distributed across 6 arcs + Employee OS per S2199 §8. All post-arc execution, NOT blocking S2403.

### Session count status

- Group 2400 In-progress at 3 of 6 sessions (S2400 parent + S2401 P1 Cat A + S2402 P2 Cat B shipped)
- Next child = S2403 P3 Cat C Session Lifecycle + Logout Cleanup Contract
- Next `xx99` at S2499 canonical summary (playbook §11.3 ELEVENTH application per current TENTH baseline)

## SESSION READY CHECK (before opening S2403 P3 Cat C)

Before drafting the S2403 child audit doc:

1. `tools/pa_local.sh "platform_config_tool action=overview"` → confirm `service_context: local` (Group 2400 arc pin `pa-6279ead1714c4630` PRESERVED through S2402; `tools/pa_local.sh:280` unchanged from S2400 open)
2. Read `docs/research/DOMAIN_RESEARCH_PLAYBOOK.md` §11.2 20-section child-audit template + §11.2 exemplar chain (S2402 P2 Cat B most recent) for shape reference
3. Read `docs/research/domains/auth/2402_authorization_permission_floor_uniformity_audit.md` fully — Cat C's primary Cat-B-inheritance load-bearing input; §14 F-B-HIGH-3 workspace-membership + §17 F-B-DUP-1 role-field bifurcation lifecycle + §13.5 correctness-vs-governance axis + §19.1 three-option decision space precedent for Cat C's silent-refresh-vs-explicit-re-login-vs-hybrid three-option
4. Read `docs/research/domains/auth/2401_authentication_surface_trust_boundaries_audit.md` §4 UnifiedUser + VIPInvite lifecycle + §14 F-VIP-1 F-TOKEN-1 F-SESS-1 lifecycle-relevant findings + §17 F-DUP-2 role-field bifurcation baseline
5. Read `docs/research/domains/auth/2400_auth_domain_scoping.md` §3.C P3 Cat C expected outputs + §3.5 auth-adjacent probes disposition + §7.1 leak-vector guardrails
6. Read `docs/research/domains/frontend/2204_frontend_session_state_persistence_discipline_audit.md` §14 F1 15-surface storageKeys inventory + F6/F8 no-cleanup-on-logout systemic + §19.1 R1 session-lifecycle two-sided framing
7. Read `docs/research/domains/frontend/2201_frontend_routes_pages_layouts_components_audit.md` §14.3 cockpit two-stage auth MINOR-DRIFT baseline
8. Read `docs/research/platform_architecture_inventory.md` §3.27 (row 27 baseline)
9. Dispatch 6-Explore-agent parallel sweep per playbook §13 (Agents 1-6 per §3.C expected outputs)
10. Draft the 20-section audit per §11.2 skeleton; verifier-loop per §14 discipline pre-Rigby-SIGN (especially: Rigby caught denominator ambiguity at Cat B Q20 — Cat C should PRE-EMPTIVELY apply denominator-discipline before Rigby SIGN)
11. Route to Rigby SIGN cycle 1 via dedicated fresh isolation pin per playbook §15 (child audit = required full SIGN); expected cadence 4-batch × 5-Q = 20-Q per S2201-S2402 seven-consecutive tested pattern
12. Fold SIGN edits; land as `status: draft` on filesystem; present Chris ratification card
13. Arc pin `pa-6279ead1714c4630` preserved through S2403-S2404 per playbook §16 arc-standard behavior + MC-4 CODIFICATION-CONFIRMED-with-scope-guardrails + MC-14 CANDIDATE-threshold-satisfied extended-to-3-arc-stages

**S2403 open command (Chris short command):** `Continue research group 2400: P3 Cat C` or `Continue research group 2400: session lifecycle` or equivalent invocation.
