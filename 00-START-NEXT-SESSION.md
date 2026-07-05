# Next Session — Start Here

---

## READ THIS FIRST — LOCAL vs PRODUCTION RIGBY TRAP + S2401 CLOSED + S2402 CAT B QUEUED

`tools/pa_chat.py:41` has `DEFAULT_BASE_URL = "http://localhost:8000"` (already local by default as of S1249 PR #2712). The `.env` file's `PA_API_TOKEN` is the **production** token — if you call `pa_chat.py` bare against local without a local-token override, you'll get 401. Always use `tools/pa_local.sh` (sets URL + local token).

**S2401 GROUP 2400 AUTH P1 CAT A CHILD AUDIT COMMITTED AT 2026-07-05.** Group 2400 Auth arc pin `pa-6279ead1714c4630` PRESERVED through S2401 per playbook §16 arc-standard behavior + MC-4 CODIFICATION-CONFIRMED-with-scope-guardrails (MC-14 CANDIDATE-threshold-satisfied 2-arc extension via Group 2200 + Group 2400 = 2 confirming arcs). `tools/pa_local.sh:280` unchanged. S2401 SIGN pin `pa-f0b18d20dbc244ef` retired at child-audit SIGN cycle 1 close (TWELFTH consecutive dedicated fresh SIGN pin retirement — 10 xx99 + 1 parent-scoping-light-SIGN + this cycle).

### The correct LOCAL invocation
```bash
tools/pa_local.sh "message"
```

**Before your first `pa_local.sh` call each session, ask Rigby to run `platform_config_tool overview` and confirm `service_context: local`.** Pin ownership already verified as chris at S2401 open (conversation_owner_match=true).

## READ THIS SECOND — GROUP 2400 AUTH ARC IN-PROGRESS (2 OF 6 SHIPPED); NEXT = S2402 P2 CAT B AUTHORIZATION + PERMISSION-FLOOR UNIFORMITY

**Group 2400 Auth: S2401 P1 Cat A CLOSED 2026-07-05.** Chris "commit it" 2026-07-05 ratified 20-fold SIGN-with-edits wholesale; status flipped `draft` → `active`. SIXTEENTH-consecutive application of playbook §11.2 20-section child-audit template per S2204 handoff.

- **Arc pin PRESERVED:** `pa-6279ead1714c4630` per playbook §16 arc-standard behavior (retirement at S2499 close)
- **SIGN pin RETIRED:** `pa-f0b18d20dbc244ef` at S2401 SIGN cycle 1 close (updated_count=8)
- **Arc progress:** S2400 parent scoping (shipped) + S2401 P1 Cat A (shipped) → **S2402 P2 Cat B Authorization + Permission-Floor Uniformity (NEXT)** → S2403 P3 Cat C → S2404 P4 Cat D → S2499 xx99. Runtime target 6 sessions — **2 of 6 shipped**; runtime cap 8.
- **MC-4 dial-back-resolution 5th confirming arc candidate** — Group 2400 4-child structure post-S2401 close extends MC-4 CODIFICATION-CONFIRMED across-4-consecutive-arcs (1900+2000++2100+2200) to across-5-consecutive-arcs, resolving S2199 Q3 STRENGTHEN dial-back at S2499 close.

## READ THIS THIRD — S2401 CAT A LOAD-BEARING INPUTS FOR S2402 CAT B

**S2401 5 headline findings (post-Rigby-SIGN-fold ranking):**

- **F-CRIT-1** PURGE_SECRET hardcoded fallback `'donkey-purge-2026'` at `core/views_home.py:259` — CRITICAL
- **F-BND-4a** Unauthenticated bet-placement WRITE at `core/auth_middleware.py:198` — CRITICAL (co-equal with F-CRIT-1; may outrank if prod-reachable)
- **F-BND-4b** Reviewer inversion at `core/auth_middleware.py:550` — HIGH (anon-can-bet-reviewers-cannot policy incoherence; discovered via Rigby SIGN cycle 1 Q16 grep-verify)
- **F-CRIT-2** Session 1171 503-fork zero smoke-test coverage — HIGH
- **F-HIGH-1** VIP TWO-LAYER drift — HIGH (HTTP HARD-gated since 2026-03-04; PA payload SOFT prompt-only)
- **F-HIGH-2** WebSocketAuthenticationMiddleware DEAD CODE at runtime — HIGH + extraction_candidate
- **F-HIGH-3** PUBLIC_PATHS 265-entry accretion — HIGH
- **F-DEC-1** `@token_auth_required` decorator drift — HIGH (Rigby SIGN cycle 1 promoted MED → HIGH)

**Trust-boundary rate table (§14.5)** enumerates 14 gate mechanisms × gate type × smoke-test evidence: 3 PRESENT + 2 PARTIAL + 9 ABSENT. **Blocker to acceptance criterion #6.**

**7 cross-arc coordination flags emitted** (CF-1 → 2600 PA + CF-2 → 1700 Observability + CF-3 → 2500 API + CF-4 conditional → 2300 Mobile + CF-5 → 1900 Governance/Authority + CF-6 → 2200 Frontend + CF-7 → External Integrations).

**S2402 Cat B inherits from S2401:** mechanism vocabulary + trust-boundary rate table + PUBLIC_PATHS 265-entry enumeration + STAFF_REQUIRED_PATHS (3) + REVIEWER_BLOCKED_PATHS (12) + REVIEWER_ALLOWED_PATHS (1) + `@authentication_classes([])` pattern inventory + `PublicIntelTokenAuth` custom DRF class inventory. Cat B measures + classifies; Group 2500 implements registry if option (c) chosen.

## READ THIS FOURTH — S2402 P2 CAT B SCOPE (AUTHORIZATION + PERMISSION-FLOOR UNIFORMITY)

**S2402 = P2 Cat B second child audit under Group 2400.** SEVENTEENTH-consecutive application of playbook §11.2 20-section child-audit template after S1301+S1401+S1501+S1601+S1701+S1801+S1901+S2001+S2101+S2102+S2103+S2104+S2201+S2202+S2203+S2204+S2401 prior sixteen.

**Scope** (per S2400 parent scoping §3.B):
- Extend Cat A's mechanism inventory from "authentication surface" to "authorization surface" over the full ~1,864 `path()` surface
- Uses Cat A's mechanism inventory as its gate-classification vocabulary
- Per-endpoint permission-floor cell + declared-permission-class + middleware-path-gate + implicit-inheritance flag
- Permission-untraced-rate extension (S2203 A3 sampled 20 endpoints ~40% permission-untraced rate → whole platform)
- STAFF_REQUIRED_PATHS + REVIEWER_BLOCKED_PATHS + REVIEWER_ALLOWED_PATHS registry audit
- Three-option decision space evidence per S2203 §19.1 R2 + recommendation lean

**Central question the audit answers.** *Does the platform have an explicit per-endpoint permission-floor contract (with declared permission-class + observable-untraced-rate) OR is authorization accreted through implicit inheritance + middleware-path-list gates with no per-endpoint registry?*

**Expected outputs (per S2400 §3.B):**
- (a) Gated endpoint inventory — permission-floor cell per endpoint across ~1,864 path() surface
- (b) Permission-untraced-rate extension — S2203 A3 sample → whole-platform measurement
- (c) STAFF_REQUIRED_PATHS + REVIEWER_BLOCKED_PATHS + REVIEWER_ALLOWED_PATHS registry audit + drift candidates
- (d) Three-option decision space evidence table + Chris-D-verdict-request (options: (a) uniform IsAuthenticated across all `/v1/**` + client-side auth-gate + observable-error surfacing; (b) uniform AllowAny for read paths + IsAuthenticated for writes + client-side auth-check-on-write; (c) per-endpoint permission registry)
- (e) Cross-arc coordination flag for Group 2500 API (per-endpoint registry as design-preparation candidate)

**Load-bearing inputs (Cat B must consume + re-verify at HEAD):**
- `core/auth_middleware.py` PUBLIC_PATHS (265) + PUBLIC_PATHS_EXACT (2) + OPTIONAL_AUTH_PATHS (7) + STAFF_REQUIRED_PATHS (3) + REVIEWER_BLOCKED_PATHS (12) + REVIEWER_ALLOWED_PATHS (1) — HEAD-verified enumeration from S2401 Cat A §3
- `core/vip_middleware.py` — VIP HARD RUNTIME gate + whitelists (F-HIGH-1 layer-1 HTTP layer)
- `docs/research/domains/auth/2401_authentication_surface_trust_boundaries_audit.md` §14.5 trust-boundary rate table (14-mechanism inventory)
- `docs/research/domains/auth/2400_auth_domain_scoping.md` §3.B expected outputs + §7.1 leak-vector guardrails (Cat B MEASURE-CLASSIFY-RECOMMEND framing; NOT authoring registry)
- `docs/research/domains/frontend/2203_frontend_api_contract_boundary_discipline_audit.md` §14 F3 silent-401 SYSTEMIC + §19.1 R2 three-option decision space
- Full sweep of `core/views*.py` for `@permission_classes` + `@authentication_classes([])` + `PublicIntelTokenAuth` custom auth class + `FleetSignatureRequired` + `FleetCapabilityRequired` usage sites
- ~1,864 `path()` patterns across `core/urls*.py` for permission-floor-cell mapping

**Sub-agent dispatch** per playbook §13 six-parallel-agent shape:
- Agent 1 Models + Persistence — Group + Permission + ContentType + any per-endpoint permission-registry model candidates
- Agent 2 Services + Runtime Flows — DRF permission-class dispatch + IsAuthenticated evaluation + custom permission classes
- Agent 3 APIs + Tools + Tasks + Commands — per-endpoint permission-floor cell inventory across ~1,864 paths + STAFF/REVIEWER gate audit + `@permission_classes` decorator sweep
- Agent 4 Integrations + Cross-Domain — permission-floor decision space + Group 2500 API scope adjacency
- Agent 5 Documentation + Prior Research — S2203 §14 F3 baseline + §3.27 permission enumeration + prior arcs coverage
- Agent 6 Drift + Debt + Ownership + Maturity — permission-untraced-rate extension + STAFF/REVIEWER gate drift + no-registry pattern

**Rigby SIGN cycle 1 REQUIRED** per playbook §15 stage-scoped routing (child audit = required full SIGN via dedicated fresh isolation pin). Expected cadence: 4-batch × 5-Q = 20 total Q per S2201-S2401 six-consecutive tested child-audit pattern (SEVENTH-consecutive 20-Q cadence application candidate).

## READ THIS FIFTH — OUTSTANDING RESIDUALS

### S2401 arc-close cascade residuals

Per Chris "commit it" ratification at S2401 close:

- **Post-commit docs cascade** — 4-step cascade (`build_docs_index` + `build_rag_corpus` + `sync_docs_index_to_documents` + `sync_docs_index_to_documents --embed`) + `build_docs_provenance` per `feedback_docs_cascade_at_every_close` + `feedback_cascade_pr_must_include_embed_step`. Execute post-merge.
- **Auth topic doc gap** — `docs/topics/auth.md` does NOT exist. Candidate S2499 xx99 anchor-update recommendation (a) per S2401 §19.4.
- **`PLATFORM_INVENTORY §Auth` autoblock gap** — no dedicated Auth autoblock exists. Candidate S2499 xx99 anchor-update recommendation (b) per S2401 §19.4.
- **`PLATFORM_WHAT_IT_IS §Auth` narrative subsection gap** — no dedicated Auth subsection exists. Candidate S2499 xx99 anchor-update recommendation per S2401 §19.4.

### S2401 CRITICAL findings post-arc remediation queue

Per S2401 §19.2 rank-1 co-equal P0 batch (POST-ARC — not this session's authoring scope):

- **F-CRIT-1** PURGE_SECRET hardcoded fallback remediation (P0 PR; decision-space per POSTURE-DECISION #3)
- **F-BND-4a** Unauthenticated bet-placement write remediation (P0 PR; permission-floor decision belongs to Cat B / Group 2500)
- **F-BND-4b** Reviewer inversion remediation (paired with F-BND-4a)
- **F-CRIT-2** Add smoke test for Session 1171 503-fork
- **F-HIGH-2** Delete OR wire WebSocketAuthenticationMiddleware (extraction_candidate)
- **F-HIGH-3** PUBLIC_PATHS registry design (Group 2500 coordination)

### Group 2200 T-slot follow-on queue (owed to Group 2400+ execution — unchanged)

- **T1 Group 2400 Auth cross-arc handoff bundle** — being executed by THIS arc (S2401-S2404) — silent-401 + logout cleanup + session lifecycle + permission-floor uniformity
- **T2 Group 2500 API cross-arc handoff bundle** — NEXT arc after Group 2400 close per S2299 §8.2
- **T3 Group 2600 PA cross-arc handoff bundle** — QUEUED after Group 2500 close
- **T4 Group 1700 Observability cross-arc handoff bundle** — QUEUED after Group 2600 close
- **Maintainer-decision batch (5 items governance gate)** — CODEOWNERS + DEAD-CANDIDATE consolidated cleanup + api.ts extraction + storageKeys registry + cockpitApi ownership
- **T2 post-arc T-slot (10 items)** — per S2299 §8
- **T3 conditional post-arc (4 items)** — cross-tab sync + Betting session-scoped state + runtime schema validation + REST↔WS joint T7

### S2199 post-arc T-slot execution queue (unchanged carry into S2402)

19 T-slot items distributed across 6 arcs + Employee OS per S2199 §8. All post-arc execution, NOT blocking S2402.

### Session count status

- Group 2400 In-progress at 2 of 6 sessions (S2400 parent + S2401 P1 Cat A shipped)
- Next child = S2402 P2 Cat B Authorization + Permission-Floor Uniformity
- Next `xx99` at S2499 canonical summary (playbook §11.3 ELEVENTH application per current TENTH baseline)

## SESSION READY CHECK (before opening S2402 P2 Cat B)

Before drafting the S2402 child audit doc:

1. `tools/pa_local.sh "platform_config_tool action=overview"` → confirm `service_context: local` (Group 2400 arc pin `pa-6279ead1714c4630` PRESERVED through S2401; `tools/pa_local.sh:280` unchanged from S2400 open)
2. Read `docs/research/DOMAIN_RESEARCH_PLAYBOOK.md` §11.2 20-section child-audit template + §11.2 exemplar chain (S2401 P1 Cat A most recent) for shape reference
3. Read `docs/research/domains/auth/2401_authentication_surface_trust_boundaries_audit.md` fully — Cat B's primary load-bearing input; §14.5 trust-boundary rate table + §5 Fleet auth + §6 REST auth endpoints + §11 doc gaps
4. Read `docs/research/domains/auth/2400_auth_domain_scoping.md` §3.B P2 Cat B expected outputs + §3.5 auth-adjacent probes disposition + §7.1 leak-vector guardrails
5. Read `docs/research/platform_architecture_inventory.md` §3.27 (row 27 baseline)
6. Read `core/auth_middleware.py` STAFF_REQUIRED_PATHS + REVIEWER_BLOCKED_PATHS + REVIEWER_ALLOWED_PATHS full at HEAD for line-anchor re-verification
7. Read `docs/research/domains/frontend/2203_frontend_api_contract_boundary_discipline_audit.md` §14 F3 SYSTEMIC baseline + §19.1 R2 three-option decision space
8. Dispatch 6-Explore-agent parallel sweep per playbook §13 (Agents 1-6 per §3.B expected outputs)
9. Draft the 20-section audit per §11.2 skeleton; verifier-loop per §14 discipline pre-Rigby-SIGN
10. Route to Rigby SIGN cycle 1 via dedicated fresh isolation pin per playbook §15 (child audit = required full SIGN); expected cadence 4-batch × 5-Q = 20-Q per S2201-S2401 six-consecutive tested child-audit pattern
11. Fold SIGN edits; land as `status: draft` on filesystem; present Chris ratification card
12. Arc pin `pa-6279ead1714c4630` preserved through S2402-S2404 per playbook §16 arc-standard behavior + MC-4 CODIFICATION-CONFIRMED-with-scope-guardrails + MC-14 CANDIDATE-threshold-satisfied 2-arc extension

**S2402 open command (Chris short command):** `Continue research group 2400: P2 Cat B` or `Continue research group 2400: authorization` or equivalent invocation.
