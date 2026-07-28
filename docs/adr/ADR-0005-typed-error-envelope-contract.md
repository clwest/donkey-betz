---
title: "ADR-0005 — Typed Error Envelope Contract (PROVISIONAL)"
adr_id: ADR-0005
slug: typed-error-envelope-contract
status: accepted
provisional: true
provisional_reason: "R6 top-level ErrorBoundary framework is a BLOCKING PREREQUISITE for the γ mechanism's Layer 2 (top-level ErrorBoundary catch of escaped errors) but NOT for Layer 1 (QueryClient default onError) or Layer 3 (per-hook opt-in). Layer 1 + Layer 3 can ship independently per §4.2. ErrorBoundary framework has zero adoption at HEAD (2503 §14 F5 + §9.2 gating relationship #2). Post-R6-establishment OR any T-slot ship named in §4 Consequences triggers an ADR-0005-successor that may flip provisional → false. (Rigby T1 SIGN Q1 STRENGTHEN + Q4 (ii) folded pre-Chris-ratification.)"
authority: design-decision
proposed: 2026-07-27
ratified: 2026-07-27
ratifier: chris
chris_ratification: "Ratify and open the PR" 2026-07-27 — after ADR-0005 T1 SIGN Cycle 1 completed across 2 dispatch turns (Q1 AGREE + minor STRENGTHEN / Q2 AGREE / Q3 AGREE with tool-verified HEAD claims / Q4 substantive zoom-out); Fold A applied pre-ratification (frontmatter provisional_reason wording aligned to Layer-1 independence per Q1 STRENGTHEN + Q4 (ii)). Draft-first workflow honored per playbook §16.
supersedes: (none)
superseded_by: (none)
design_prep: docs/research/domains/api/2503_api_error_envelope_refresh_logout_contracts_design_prep_audit.md
source_refs:
  - docs/research/domains/api/2503_api_error_envelope_refresh_logout_contracts_design_prep_audit.md §19.1 R1 (CRITICAL — Chris-D-verdict-request for typed-error-envelope + session-lifecycle + whitelist-replacement intersection)
  - docs/research/domains/api/2503_api_error_envelope_refresh_logout_contracts_design_prep_audit.md §9.1 (three α/β/γ decision spaces with Rigby Q6 fold reconciliation — γ mechanism ⊃ β UX policy)
  - docs/research/domains/api/2503_api_error_envelope_refresh_logout_contracts_design_prep_audit.md §9.2 (gating relationships — R6 ErrorBoundary prereq + F-C-VIP-1 risk-gate)
  - docs/research/domains/api/2503_api_error_envelope_refresh_logout_contracts_design_prep_audit.md §14.1 F1 (4 co-existing 401 shape families) + §14.5 F5 (SHAPE-BLIND interceptor) + §17 F2 (three envelope shape systems)
  - docs/research/domains/api/2599_api_canonical_summary.md §3 (four-plane consolidated shape) + §3.1 numerical summary + §8 T-slot follow-on queue
  - docs/research/domains/auth/2404_frontend_integration_silent_401_systemic_resolution_audit.md §19.1 (Cat D PROPOSED PRIMARY = γ RQ + ErrorBoundary)
  - docs/research/domains/auth/2499_auth_canonical_summary.md §8.4 (T-slot cross-arc handoff bundles — CF-D1 typed-error envelope)
  - core/api_responses.py:15-234 (APIResponseEnvelope — Family B typed shape at HEAD)
  - core/settings.py:652-653 (DRF DEFAULT_PERMISSION_CLASSES + EXCEPTION_HANDLER absent = Family A dominance mechanism)
  - frontend/src/lib/api.ts:63-82 (SHAPE-BLIND response interceptor — reads status + URL substring only; drifted from 2503's 43-62 baseline due to Session 819 request-interceptor growth above; structure IDENTICAL — RE-VERIFIED at HEAD c9b09d97d 2026-07-27)
  - frontend/src/main.tsx (QueryClient container present; zero onError defaults; zero ErrorBoundary)
  - docs/adr/ADR-0001-establish-adr-corpus.md §3.3 (frontmatter schema) + §3.4 (body-section template)
  - docs/adr/ADR-0004-rag-corpus-substrate-maturity-gradient.md (reference implementation for two-field PROVISIONAL pattern)
reversibility: 4
  # See §6. This ADR is docs-first — it ratifies a contract decision but
  # does NOT ship runtime code. Reversibility 4 (not 5) because §3.2
  # names APIResponseEnvelope shape B as the SoT emission target,
  # which future writes to core/api_responses.py must respect until
  # superseded. Rollback: `git revert <merge_sha>` returns the corpus
  # to a state where the decision is un-ratified; existing 14
  # APIResponseEnvelope sites remain functional (they were live
  # before ADR-0005 and are not created by it).
sign_cycle_1: complete 2026-07-27 — Rigby SIGN across 2 dispatch turns (arc pin pa-8e17b50843a34be5). Turn 1: Q1 AGREE + minor STRENGTHEN on frontmatter provisional_reason wording; Q2 STRENGTHEN (needed re-issue for T-slot enumeration read); Q3 BLOCKED (honestly declined to rubber-stamp HEAD empirical claims without tool_runs); Q4 substantive zoom-out (narrow scope right / provisional wording aligned to Layer-1 independence / coupling-risk preserved by §3.3 optionality). Turn 2: Q2 AGREE (7 T-slots verified vs 2499 §8.4 + 2599 §8; T-ENVELOPE-1 → T-ENVELOPE-0 dependency confirmed); Q3 AGREE (all 3 HEAD claims tool-verified — zero ErrorBoundary/componentDidCatch/getDerivedStateFromError in frontend/src; APIResponseEnvelope at core/api_responses.py:15; response interceptor at api.ts:63-82 SHAPE-BLIND identical structure). One fold landed pre-Chris-ratification: Fold A (frontmatter provisional_reason wording sharpened). Cycle 2 SIGN NOT scheduled.
sign_cycle_1_pin: pa-8e17b50843a34be5 (S3001 arc pin; NOT dedicated fresh isolation pin — SIGN reused arc pin per single-session ADR-authoring economy)
companion_docs:
  - docs/research/domains/api/2503_api_error_envelope_refresh_logout_contracts_design_prep_audit.md
  - docs/research/domains/api/2599_api_canonical_summary.md
  - docs/research/domains/auth/2404_frontend_integration_silent_401_systemic_resolution_audit.md
  - docs/research/domains/auth/2499_auth_canonical_summary.md
  - docs/adr/ADR-0001-establish-adr-corpus.md
  - docs/adr/ADR-0004-rag-corpus-substrate-maturity-gradient.md
owner: claude (S3001 v1 draft; Rigby SIGN cycle 1 pending)
---

# ADR-0005 — Typed Error Envelope Contract (PROVISIONAL)

## 1. Status

**Draft** — pending Rigby SIGN cycle 1 + Chris ratification.

**PROVISIONAL** — `provisional: true` per frontmatter. The mechanism ratified here (γ = React Query error callbacks + top-level ErrorBoundary + QueryClient default `onError`) depends on the R6 top-level ErrorBoundary framework being established. At HEAD `c9b09d97d`, `frontend/src/**` contains zero `ErrorBoundary`, `componentDidCatch`, or `getDerivedStateFromError` matches (2503 §14 F5 verified 2026-07-05; ADR-0005 draft re-verifies zero-delta). Post-R6-establishment OR any T-slot ship (see §4 Consequences) triggers an ADR-0005-successor that may flip `provisional: true` → `false`.

## 2. Context

### 2.1 Upstream research

Group 2400 Auth (S2400–S2499, closed 2026-07-05) and Group 2500 API (S2500–S2599, closed 2026-07-06) delivered a joint typed-error-envelope decision-space enumeration across four child audits: S2404 Cat D (Frontend Integration + Silent-401 SYSTEMIC Resolution), S2503 Cat C (Error-Envelope + Refresh + Logout API Contracts Design-Prep), S2502 Cat B (Frontend API-Client Architecture Design-Prep), S2501 Cat A (Backend Contract SoT Design-Prep).

The arcs' joint canonical verdict (2499 §1 + 2599 §1): **the platform's API surface is ACCRETION with declared-but-unenforced contracts — 4 co-existing 401 shape families at wire, SHAPE-BLIND interceptor at consumer, zero cross-transport SoT.** Mechanisms work at file-precision; the DECLARATION plane is fragmented across every axis inspected.

### 2.2 The problem this ADR resolves

At HEAD the platform emits four distinct 401/error shape families (per 2503 §14.1 F1 + 2599 §3.1):

- **Family A** — DRF default `{"detail": "..."}` (~80-90% implicit; drives most 401 emissions via absence of custom `EXCEPTION_HANDLER` at REST_FRAMEWORK settings)
- **Family B** — `APIResponseEnvelope` typed `{"success":false,"error":{"code":..., "message":...}}` (~14 emission sites at `core/api_responses.py:15-234`)
- **Family C** — bare DRF `Response({"message": "..."})` (enhanced-logout, `core/auth_views_enhanced.py:554`)
- **Family D** — non-DRF `JsonResponse({"success":false, "error":str})` (JsonResponse-dict bypass)

The consumer surface (`frontend/src/lib/api.ts:63-82` at HEAD `c9b09d97d`; drifted from 2503's `43-62` baseline due to request-interceptor growth) is **SHAPE-BLIND** — reads only `error.response?.status === 401` and branches solely on `url.includes('/auth/') || url.includes('/login')`. All four shape families flow through the same non-auth `console.warn + Promise.reject` branch. Consumer call-sites total 803 (57 direct + 667 useQuery/useMutation + 79 raw fetch bypass) with ~99% silent-swallow rate (2404 §14.5 + 2503 §14.5 F5).

Without a ratified typed-error-envelope contract:
- **No consumer-side shape-uniform handler is possible** without either shape-normalization at interceptor OR a shape-agnostic mechanism at RQ layer (2503 §15 top-5 Observability Risk #1).
- **803 consumer call-sites keep silently swallowing 401** — auth-related failures do not surface to the user; component-level opt-in error handling remains ad-hoc.
- **The three envelope shape systems coexist without SoT selection** (2503 §17 F2) — future backend endpoints have no ratified default to emit.
- **Session lifecycle β UX policy** (2503 §19.1 Cat C PROPOSED PRIMARY = explicit re-login) has no ratified handler locus to nest inside.

### 2.3 Design-preparation source

Per `docs/research/domains/api/2503_api_error_envelope_refresh_logout_contracts_design_prep_audit.md`, three α/β/γ decision spaces were enumerated with PROPOSED PRIMARY leans:

- **Cat D typed-error-envelope** (S2404 §19.1 + S2503 §19.1 R1): **γ React-Query error callbacks + top-level ErrorBoundary + QueryClient default `onError`** — PROPOSED PRIMARY.
- **Cat D whitelist-replacement** (S2404 §19.1): **γ per-api-module `authHandling: 'default' | 'suppress_redirect'` string enum + telemetry** — PROPOSED PRIMARY. **Not ratified by this ADR** (see §2.4).
- **Cat C session-lifecycle** (S2403 §19.1): **β explicit re-login** — PROPOSED PRIMARY. **Not ratified by this ADR as a session-lifecycle decision** (see §2.4); ratified here only as UX policy nested inside the γ default handler per §3.4.

Rigby SIGN cycle 1 on Cat D (S2404) established the key nesting: **γ (Cat D typed-error-envelope) = MECHANISM; β (Cat C explicit re-login) = message/UX policy nested inside γ default handler** (2404 §19.1 Q6 fold; 2503 §9.1 reconciliation). This ADR ratifies that nesting as the platform contract.

### 2.4 What this ADR does NOT decide

- **Cat C session-lifecycle α/β/γ as a whole.** The refresh endpoint necessity, Clear-Site-Data emission locus, and 15-surface storageKeys cleanup coordination remain Chris-D-verdict-request items for a future ADR (session-lifecycle ADR-N). This ADR narrowly ratifies β as the UX policy nested inside γ default handler and does NOT ratify silent-refresh mechanism, refresh endpoint semantics, or storage-cleanup contract.
- **Cat D whitelist-replacement α/β/γ.** The `authHandling` per-api-module string enum decision is coupled to but independent from typed-error-envelope. Deferred to whitelist-replacement ADR-N.
- **Cat A Path A/B/C backend contract SoT strictness.** The drf-spectacular wire-up decision, codegen tool selection, and per-endpoint decoration coverage decision are backend-DECLARATION-plane concerns owned by a future backend-SoT ADR-N.
- **Cat D permission-floor registry.** Per-endpoint permission-floor SoT is a separate Cat D S2504 decision-space; not ratified here.
- **REST↔WS T7 message-contract strictness.** WS envelope-schema selection (TypedDict / Protocol / BaseModel) is a separate Cat D + Group 2600 PA co-authorship decision.
- **F-C-VIP-1 enforcement mechanism.** The `VIPInvite.account_expires_at` runtime enforcement (2503 §14.7 F7) is a risk-gate for expiry-signal-bearing UX; this ADR names it as a §3.5 scope-tightening constraint but does NOT ratify its enforcement mechanism.
- **Backend `EXCEPTION_HANDLER` implementation choice.** Whether Family A → Family B normalization lands at DRF `EXCEPTION_HANDLER`, at custom middleware, or via per-endpoint APIResponseEnvelope adoption is deferred to T-slot execution PR (§4.1 T-ENVELOPE-2).
- **Migration schedule for the 803 consumer call-sites.** T-ENVELOPE-4 execution ordering is post-arc scope.
- **Any runtime code.** This ADR is docs-first per §6.

## 3. Decision

**Ratify the following typed-error-envelope contract as a platform PROVISIONAL ADR.**

### 3.1 Mechanism selection — Cat D typed-error-envelope γ

**Adopt γ** (React Query error callbacks + top-level ErrorBoundary + QueryClient default `onError`) as the platform-canonical typed-error-envelope mechanism, per 2503 §19.1 R1 PROPOSED PRIMARY + 2404 §19.1 Cat D PROPOSED PRIMARY.

Mechanism definition (verbatim from 2404 §19.1 + 2503 §9.1):

- **Layer 1** — QueryClient default `onError` handler at `frontend/src/main.tsx` (or QueryClient factory site) that fires for every query/mutation error not caught by a hook-scoped handler.
- **Layer 2** — Top-level `<ErrorBoundary>` wrapper at the React tree root that catches thrown errors escaping Layer 1 (e.g., render-time errors triggered by a mutation callback).
- **Layer 3** — Per-hook `useQuery({onError})` / `useMutation({onError})` opt-in overrides for domain-specific error UX.

Rationale (2503 §9.1 + 2404 §19.1): Layer 1 provides shape-agnostic default handling that works for any of the 4 co-existing 401 shape families without requiring backend shape-normalization to land first. Layer 2 catches escapes; Layer 3 permits opt-in customization. Blast radius LOW (framework layer only; call-sites remain unchanged unless opting in).

### 3.2 SoT emission shape — Family B (`APIResponseEnvelope`)

**Adopt `APIResponseEnvelope` at `core/api_responses.py:15-234` as the SoT emission shape** for endpoints under contract adoption. Family B shape:

```json
// Success
{"success": true, "data": <T>, "message": <optional str>}
// Error
{"success": false, "error": {"code": <str>, "message": <str>, ...}}
```

**This ADR does NOT mandate immediate Family A → Family B migration** across all 401 emission sites. Family A (`{"detail": ...}`) remains the DRF default and is tolerated at consumer via the Layer 1 shape-agnostic handler. Migration is per-endpoint opt-in via T-ENVELOPE-2 execution.

### 3.3 SHAPE-BLIND interceptor — retained + elevated

**Retain the `api.ts:63-82` response interceptor (drifted from 2503's `43-62`; structure IDENTICAL) unchanged in structure**; do NOT replace with shape-normalizer at this ADR ratification. Rationale: γ mechanism (§3.1) is shape-agnostic at Layer 1 (RQ default `onError` receives the entire `AxiosError` object with `.response.data` intact per whichever shape family), so shape-normalization at interceptor is NOT REQUIRED for correct auth recovery.

**Future ADR-N (Family B mandate) MAY elevate the interceptor to shape-normalizer** if Chris later ratifies a Family A → Family B mandate. This ADR preserves optionality.

### 3.4 Nested UX policy — Cat C β "explicit re-login"

**Adopt Cat C β "explicit re-login"** as the default UX policy nested inside the γ Layer 1 `onError` handler (2503 §9.1 Rigby Q6 fold reconciliation; not ratified as a stand-alone session-lifecycle decision — see §2.4).

Default handler behavior on 401 response (any shape family):
1. Clear client-side auth state (`useAuthStore.getState().logout()`).
2. Surface a user-facing "session expired — please log in" modal or toast (concrete UI component deferred to T-ENVELOPE-3).
3. Redirect to `/login` on user acknowledgment (NOT immediately, unless the request was itself an auth endpoint — preserving current interceptor behavior for `url.includes('/auth/') || url.includes('/login')`).

**Anti-pattern warning:** the default handler MUST NOT surface `VIPInvite.account_expires_at` or any other account-lifecycle-derived expiry copy until F-C-VIP-1 is enforced (§3.5).

### 3.5 Scope-tightening — F-C-VIP-1 risk-gate

**F-C-VIP-1** (`VIPInvite.account_expires_at` DECLARED-BUT-NOT-ENFORCED at HEAD per 2503 §14.7 F7) is a risk-gate for **any expiry-signal-bearing UX**. This ADR's γ Layer 1 default handler MUST NOT surface account-expiry copy (e.g., "your VIP account expired on {date}") until F-C-VIP-1 has runtime enforcement + periodic cleanup task. Session-expired copy (§3.4 step 2) is bounded to token/session lifecycle framing, not account lifecycle framing.

### 3.6 Ratification scope summary

**Ratified by this ADR:** (i) γ mechanism selection; (ii) APIResponseEnvelope as SoT emission shape (opt-in, not mandate); (iii) SHAPE-BLIND interceptor retention + elevation optionality; (iv) β nested UX policy for 401 default handler; (v) F-C-VIP-1 scope-tightening constraint.

**Not ratified by this ADR:** see §2.4.

## 4. Consequences

### 4.1 Post-arc T-slot execution PR requirements

The following T-slots are named as post-arc requirements. Each is a separate future implementation PR (not authored in this ADR; not scheduled here; enumerated for platform-ADR canonical anchoring).

- **T-ENVELOPE-0 (BLOCKING PREREQUISITE)** — R6 top-level ErrorBoundary framework establishment. Zero adoption at HEAD (2503 §14 F5 + §9.2 gating relationship #2 + S2499 §9 CF-D5). MUST land before any γ Layer 2 shipment. Dual-ownership per 2499 §9: (a) Cat D typed-envelope prerequisite (this ADR); (b) Group 2200 post-arc T-slot global-error-UX framework concern. Ownership: `@clwest` per CODEOWNERS (see 2503 §18).
- **T-ENVELOPE-1** — QueryClient default `onError` handler wire-up at `frontend/src/main.tsx` (or QueryClient factory site). Layer 1 implementation. Depends on T-ENVELOPE-0.
- **T-ENVELOPE-2** — Backend `EXCEPTION_HANDLER` choice + per-endpoint Family B adoption ramp. Options: (a) custom `EXCEPTION_HANDLER` at `REST_FRAMEWORK` settings-level that wraps Family A → Family B; (b) middleware-level normalization at `core/auth_middleware.py`; (c) per-endpoint APIResponseEnvelope adoption without global normalization. Chris-D-verdict at T-ENVELOPE-2 planning.
- **T-ENVELOPE-3** — "Session expired" modal/toast UI component implementation. Layer 1 default handler UX target per §3.4 step 2.
- **T-ENVELOPE-4** — Per-hook opt-in `onError` migration ramp for 803 consumer call-sites. Not a hard migration; ramp per domain area. Scheduling per Group 2200 post-arc T-slot maintainer-decision batch.
- **T-ENVELOPE-5** — Interceptor elevation to shape-normalizer (if Chris later ratifies Family A → Family B mandate at a future ADR-N). Optional per §3.3.
- **T-ENVELOPE-6** — Telemetry hookup for γ Layer 1 handler firings (envelope-adoption metric + silent-401-rate reduction observation). Ownership: Cat C CF-C3 handoff to Group 1700 Observability.
- **T-VIP-1** — F-C-VIP-1 `VIPInvite.account_expires_at` runtime enforcement + periodic cleanup task. Prerequisite for any expiry-signal-bearing UX per §3.5. Owned by session-lifecycle ADR-N or dedicated F-C-VIP-1 ADR-N; enumerated here only as risk-gate reference.

Each T-slot is future implementation-arc scope. No T-slot is admitted by this ADR. This ADR ratifies their identity as post-arc requirements; scheduling + Chris-per-slot ratification happen at the respective future arc-open events.

### 4.2 BLOCKING PREREQUISITE posture

**T-ENVELOPE-0 (R6 top-level ErrorBoundary framework) is a BLOCKING PREREQUISITE** for γ Layer 2 shipment. Until T-ENVELOPE-0 lands:

- `provisional: true` remains in this ADR's frontmatter.
- γ Layer 1 (QueryClient default `onError`) CAN ship independently (T-ENVELOPE-1 does not require ErrorBoundary).
- γ Layer 2 (top-level ErrorBoundary) CANNOT ship — this is the T-ENVELOPE-0 blocker itself.
- γ Layer 3 (per-hook `onError`) CAN ship as opt-in migration (T-ENVELOPE-4).

Post-T-ENVELOPE-0 ship OR any other §4.1 T-slot ship is a trigger for an ADR-0005-successor to flip `provisional`.

### 4.3 No runtime enforcement claims

This ADR codifies a **design-layer decision**. It does NOT claim:

- The γ Layer 1 default handler is wired at HEAD.
- APIResponseEnvelope is emitted by all endpoints (14/N ratio at HEAD, N not established at ADR scope).
- The 803 consumer call-sites have adopted per-hook `onError`.
- Family A → Family B migration is complete.
- The SHAPE-BLIND interceptor has been elevated to shape-normalizer.
- ErrorBoundary framework exists (T-ENVELOPE-0 blocker).

Each of the above is post-arc T-slot work (§4.1). The classification's "docs-first ratification" IS the ratified admission that runtime enforcement is deferred.

### 4.4 Preserved constraints from upstream research

- **α/β/γ label independence** (2503 §1.2): reader MUST NOT couple this ADR's γ selection to Cat C session-lifecycle α/β/γ or Cat D whitelist-replacement α/β/γ. Only the ONE nesting established at 2503 §9.1 (γ mechanism ⊃ β UX policy) is ratified here.
- **Level 0 anchor scope** (2503 §16 + 2504 §16): the "explicit CONTRACT for error envelope + refresh + logout semantics" Level 0 anchor is PARTIALLY discharged by this ADR (error envelope only); refresh + logout remain unratified per §2.4.
- **Cross-arc coordination flag CF-C3** (2503 §9): typed-envelope adoption metric + silent-401-rate telemetry handed to Group 1700 Observability per T-ENVELOPE-6.
- **Cross-arc coordination flag CF-C5** (2503 §9): R6 ErrorBoundary framework establishment is Group 2200 post-arc T-slot dual-ownership per T-ENVELOPE-0.

### 4.5 ADR corpus schema — no extension

This ADR uses the existing two-field PROVISIONAL pattern established by ADR-0004 (`status: draft` + `provisional: true` + `provisional_reason: str`). No new frontmatter fields introduced. ADR-0001 §3.3 forward-compat rule per ADR-0004 §4.4 F20 fold applies.

### 4.6 Downstream ADR references

Future ADRs SHOULD cite `ADR-0005 §3.1` (mechanism), `ADR-0005 §3.2` (SoT emission shape), or `ADR-0005 §3.4` (nested UX policy) instead of citing 2503 §19.1 R1 or 2404 §19.1 directly. Research docs (xx99 canonical summaries, arc scoping docs) MAY continue to cite 2503/2404 as their upstream evidence source.

### 4.7 Docs cascade + BACKLOG posture

At ADR PR merge:
- `docs/INDEX.md` gains a new ADR-0005 entry (autogen per `build_docs_index`).
- `docs/_provenance.json` gains ADR-0005 provenance metadata.
- ADR-0005 body embedded via `embed_documents --all-unembedded`.
- BACKLOG.md — no existing intake row corresponds to this ADR (S3001 opens ADR without a queued IB-* intake); intake row `IB-3001-T0-01` MAY be added post-ratification for T-ENVELOPE-* tracking if Chris directs.

No runtime code change. No DB migration. No feature flag introduction. No Celery task change. No API surface change.

## 5. Alternatives considered

Inherited from 2503 §19.1 R1 + 2404 §19.1 decision-space enumeration.

### 5.1 α (rejected) — Throw typed exceptions per HTTP status

Backend emits typed exceptions (`UnauthorizedError`, `PermissionError`, `ValidationError`, `ServerError`); frontend consumer catches typed exceptions via `AxiosError` extension.

**Rejected because:** blast radius HIGH — requires custom exception classes at both layers + coordinated migration of 803 consumer call-sites to explicit typed `catch` blocks + backend serialization contract for exception → response body shape. 2404 §19.1 evidence + Rigby SIGN precedent both weighted γ as PROPOSED PRIMARY over α on blast-radius grounds.

### 5.2 β (rejected) — Return Result<T, E> discriminated-union

Backend emits `{success, data | error}` discriminated union; frontend consumer branches on `.success` field.

**Rejected because:** blast radius MED but requires Family A → Family B migration to land FIRST (Family A `{"detail":...}` has no `success` field). γ is compatible with Family A retention. Per 2503 §3.2, Family B adoption is opt-in ramp; forcing discriminated-union at consumer requires the mandate that §3.3 preserves optionality against.

### 5.3 Shape-normalization at interceptor (rejected as gating)

Elevate `api.ts:43-62` interceptor to shape-normalizer: consume Family A/B/C/D on input, emit Family B on output.

**Rejected as gating requirement** (but retained as future optionality per §3.3): would gate γ shipment on interceptor rewrite + regression testing of every 401-emitting endpoint. γ Layer 1 shape-agnostic default handler eliminates the need. Preserved as future ADR-N optionality if Chris later ratifies Family A → Family B mandate.

### 5.4 Session-lifecycle α (silent-refresh) as bundled ratification (rejected)

Bundle typed-error-envelope γ with Cat C session-lifecycle α silent-refresh mechanism.

**Rejected because:** α session-lifecycle REQUIRES refresh endpoint (F-C-REFRESH-1 remediation) + Token expiry field (F-TOKEN-1) + rotation policy + FE 401-retry-with-refresh + cross-tab race handling + mobile SDK support (2503 §9.1). Blast radius HIGH; would violate §2.4 "one decision per ADR" discipline (ADR-0004 §5.6 precedent). Deferred to session-lifecycle ADR-N.

### 5.5 Whitelist-replacement γ as bundled ratification (rejected)

Bundle typed-error-envelope γ with Cat D whitelist-replacement γ `authHandling` per-api-module string enum.

**Rejected because:** whitelist-replacement is a distinct decision-space (2503 §1.2 label-independence guardrail) with its own α/β/γ options and its own PROPOSED PRIMARY (γ per-api-module enum). While both share γ label, coupling would erode reversibility. Deferred to whitelist-replacement ADR-N.

### 5.6 Defer this ADR until R6 ErrorBoundary lands (rejected)

Wait for a future arc to establish R6 top-level ErrorBoundary, then author a non-PROVISIONAL ADR-0005.

**Rejected because:** would leave the four-shape typed-error-envelope decision-space unratified indefinitely; Cat C R1 decision-space Chris-D-verdict at 2599 xx99 remains pending; the T-ENVELOPE-1 (Layer 1 QueryClient default `onError`) work can proceed without R6 and provides immediate value (surfaces silent-401 at Layer 1 default even before Layer 2 catches escapes). Deferral costs continued silent-swallow across 803 call-sites. PROVISIONAL posture is the accepted trade-off per ADR-0004 §5.7 precedent.

### 5.7 CX-P10 direct-ratification path (rejected)

Skip Stage 2 ADR authoring — the 2503 design-prep IS the ADR.

**Rejected because:** 2503 is a research-authority document explicitly framed as "Chris-D-verdict-request evidence, NOT recommendation" (2503 §1 boundary note + §19 non-prescriptive label). It does not fulfill the ADR corpus contract (ADR-0001 §3.3 frontmatter schema + §3.4 body-section template) and lacks the ratifier field. This ADR IS the required NEEDS_ADR discharge.

## 6. Reversibility

**Reversibility scale (per ADR-0001 §3.5): 4 (highly reversible, one-directional constraint).**

Rollback method:

1. `git revert <ADR-0005-merge-commit-sha>` — removes ADR-0005 file + cascade artifacts.
2. `docs/INDEX.md` + `docs/_provenance.json` unflip via revert (or via re-run `build_docs_index` + `build_docs_provenance`).
3. `DocumentEmbedding` rows for the removed file — orphan cleanup discipline per ADR-0004 §6 F21 fold precedent: leave as acceptable low-severity storage residue OR run cleanup command if available at revert time.

**One-directional constraint:** any code shipped between ADR-0005 merge and revert that opts in to γ Layer 1 QueryClient default `onError` MUST be independently reverted or updated to a different handler shape. The 14 existing APIResponseEnvelope sites (Family B emission) are NOT created by this ADR and remain functional at revert.

**No irreversible operations. No DB migration. No feature flag change. No runtime code change. No data-shape change.**

Rollback triggers:
- Rigby SIGN Cycle 1 on this ADR returns BLOCKED verdict AFTER Chris ratification (unlikely given design-prep pre-SIGN in 2503).
- T-ENVELOPE-0 (R6 ErrorBoundary) fails to land within a reasonable window and PROVISIONAL posture becomes structural.
- Chris explicit override.

Post-rollback state:
- Cat D typed-error-envelope α/β/γ decision returns to Chris-D-verdict-request pending per 2599 §8 T-slot follow-on queue.
- The 803 consumer call-sites remain in silent-swallow posture (HEAD baseline).

## 7. Provenance

- **Author.** Claude Code, S3001 open ADR-0005 body drafting session, 2026-07-27.
- **Design-prep source (canonical).** `docs/research/domains/api/2503_api_error_envelope_refresh_logout_contracts_design_prep_audit.md` (Chris ratification of 2599 canonical summary pending per 2599 frontmatter line 38 "commit it" candidate).
- **Rigby SIGN Cycle 1 target.** Pending on fresh isolation pin per playbook §15 SIGN-isolation discipline. Q-set will pressure-test §3 Decision content fidelity to 2503 §19.1 R1 + §4 Consequences T-slot enumeration + §5 Alternatives inheritance from 2404 §19.1 + §6 Reversibility rollback triggers + §3.5 F-C-VIP-1 scope-tightening constraint fidelity to 2503 §14.7 F7.
- **Chris ratification target.** After Rigby SIGN + fold application + Chris review of ratification card + Chris "commit it" or equivalent.
- **Session context.** S3001 opened on pivot decision after v2 findings-surface arc close (S2991–S3000). Chris ratified A3 → typed-error-envelope path after prior-session queue proposal (2400 Auth) was verified already-executed. Route documented in S3001 handoff (post-close).

### 7.1 Consumed sources (verified at HEAD `c9b09d97d`)

- 2503 §1 Executive Summary + §14.1 F1 (4 co-existing 401 shape families) + §14.5 F5 (SHAPE-BLIND interceptor RE-VERIFIED) + §14.7 F7 (F-C-VIP-1 preserved) + §17 F2 (three envelope shape systems) + §19.1 R1 (CRITICAL Chris-D-verdict-request).
- 2503 §9.1 (three α/β/γ decision spaces + Rigby Q6 fold reconciliation γ ⊃ β).
- 2503 §9.2 (gating relationships — R6 ErrorBoundary prereq + F-C-VIP-1 risk-gate).
- 2599 §1 (canonical verdict — ACCRETION with declared-but-unenforced contracts) + §3 (four-plane consolidated shape ASCII diagram) + §3.1 (numerical summary — 803 consumer surface, 4 shape families, 14 APIResponseEnvelope sites at HEAD).
- 2599 §8 (T-slot follow-on queue — CF-D1 typed-error envelope).
- 2404 §19.1 (Cat D PROPOSED PRIMARY = γ RQ + ErrorBoundary + Rigby Q6 nesting reconciliation).
- 2499 §8.4 (T-slot cross-arc handoff bundles — CF-D1 typed-error envelope + R6 BLOCKING PREREQUISITE marker).
- `core/api_responses.py:15-234` (APIResponseEnvelope — Family B typed shape at HEAD; direct file read).
- `frontend/src/lib/api.ts:63-82` (SHAPE-BLIND response interceptor — RE-VERIFIED IDENTICAL in structure at HEAD `c9b09d97d`; line-drift from 2503's `43-62` baseline due to Session 819 request-interceptor growth above lines 40-60; direct file read).
- **Emission-count sharpening pending Rigby SIGN.** ADR cites "14 APIResponseEnvelope emission sites" per 2503 metrics table; 2599 §3.1 cites "9 sites"; grep `APIResponseEnvelope` on `core/**` returns 15 matches (includes 1 class-definition site at `core/api_responses.py:15` + 14 consumer sites). Reconciliation: 14 (consumer sites; class def excluded) is the ADR-canonical count; discrepancy with 2599 §3.1 flagged for Rigby to sharpen at SIGN.
- ADR-0001 §3.3 frontmatter schema + §3.4 body-section template + §3.7 coupling.
- ADR-0004 (reference implementation of two-field PROVISIONAL pattern + §4.4 forward-compat rule + §5.6/§5.7 alternative-rejection precedent + §6 reversibility rollback triggers).

## 8. Follow-on ADRs (potentially blocked on this one)

- **ADR-N (successor to ADR-0005) — Post-T-ENVELOPE-0 or post-T-slot-ship typed-error-envelope contract refresh.** Triggered by R6 ErrorBoundary framework establishment OR any T-slot from §4.1 ship. Successor uses `supersedes: ADR-0005` frontmatter and may flip `provisional: true` → `false`.
- **ADR-N (session-lifecycle ADR) — Cat C α/β/γ session-lifecycle ratification.** Names refresh endpoint necessity (F-C-REFRESH-1), Clear-Site-Data emission locus (F-C-CSD-1), storageKeys 15-surface cleanup coordination (F-C-STORE-1), and MAY cite ADR-0005 §3.4 as the UX policy nesting anchor.
- **ADR-N (whitelist-replacement ADR) — Cat D whitelist-replacement α/β/γ ratification.** Names `authHandling: 'default' | 'suppress_redirect'` per-api-module string enum + telemetry (Cat D §19.1 γ PROPOSED PRIMARY). Independent of this ADR per §5.5.
- **ADR-N (Path A/B/C backend contract SoT) — Cat A backend DECLARATION plane ratification.** Names drf-spectacular wire-up, codegen tool selection, per-endpoint `@extend_schema` decoration coverage. Independent of this ADR (Cat A vs Cat C boundary preserved).
- **ADR-N (F-C-VIP-1 enforcement) — VIPInvite.account_expires_at runtime enforcement ratification.** Cited by ADR-0005 §3.5 as risk-gate for expiry-signal-bearing UX. Independent decision.
- **ADR-N (Family B mandate) — If Chris later ratifies Family A → Family B mandate.** Would elevate SHAPE-BLIND interceptor to shape-normalizer per §3.3 preserved optionality; supersedes ADR-0005 §3.2 opt-in-only qualifier.
