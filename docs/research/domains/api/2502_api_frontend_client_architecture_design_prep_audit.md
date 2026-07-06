---
title: "S2502 P2 Cat B — Frontend API-Client Architecture Design-Prep"
status: active
session: 2502
date: 2026-07-05
arc: Research Group 2500 (API — Contract SoT + Silent-401 Downstream Remediation + Session-Lifecycle API Contracts + Per-Endpoint Permission-Floor Registry Design-Prep + REST↔WS T7 Joint 2500+2600)
child_slot: P2 Cat B — Frontend API-Client Architecture Design-Prep
head_sha: 548f53a1
parent: 2500_api_domain_scoping.md
siblings:
  - 2501_api_backend_contract_sot_design_prep_audit.md
  - 2503_api_error_envelope_refresh_logout_contracts_design_prep_audit.md (pending)
  - 2504_api_permission_floor_registry_rest_ws_t7_design_prep_audit.md (pending)
delegates_to: []
inherits_from:
  - docs/research/domains/frontend/2203_frontend_api_contract_boundary_discipline_audit.md (F1 SoT-ABSENT + F3 silent-401 + F3.5 whitelist BRITTLE + F4 6.85% typed + F5 drf-spectacular partial + F6 18 DEAD-CANDIDATE + §20.6 Path A/B/C triad)
  - docs/research/domains/frontend/2299_frontend_canonical_summary.md (§5.1 canonical seam + §7.5 anchor updates + §8.2 T2 Group 2500 API cross-arc handoff bundle + §8.4 T2 R6 error-boundary framework)
  - docs/research/domains/auth/2404_frontend_integration_silent_401_systemic_resolution_audit.md (F-D-CALL-1 803 classification + F-D-BYPASS-1 79-raw-fetch NEW HIGH + F-D-ENVELOPE-1 zero typed AxiosError + F-D-BOUNDARY-1 zero error boundaries + F-D-WHITELIST-1 brittle substring + F-D-OWN-1 CODEOWNERS)
  - docs/research/domains/api/2501_api_backend_contract_sot_design_prep_audit.md (F1 drf-spectacular INSTALLED-CONFIGURED-DECORATED-DISCONNECTED + F6 FOUR-shape 401 heterogeneity + 96 Serializer + 91 ModelSerializer + 16.2% model→serializer coverage + 3-slice API-slice manifest)
owner: Claude Opus 4.7 (draft) + Chris ratification (pending)
verifier_loop: |
  Sub-agent conflicts resolved pre-Rigby-SIGN:
  1. apiModule count = 93 (Agent 1 + Agent 3 + parent grep `^export const \w+Api\s*=` exact match; Agent 6 claim 97 REFUTED).
  2. platformApi method count ≈ 30 spanning lines 3257→3920 = 663 LOC (Agent 3; Agent 1 claim 414 REFUTED via direct read — line-range is monolithic 663 LOC but method count is well under 400).
  3. Direct-consumer call count = 57 = 913 total repo grep − 856 defs in api.ts (Agent 3 + S2404 baseline; Agent 6 claim 87 REFUTED as counting axios-instance imports + method calls together, wrong denominator).
  4. CODEOWNERS at HEAD: EXISTS at repo root `./CODEOWNERS` (48 lines), NOT `.github/CODEOWNERS`. api.ts entry line 31 @clwest. cockpitApi.ts + hooks/ UNASSIGNED per CODEOWNERS lines 8-13 explicit deferral to S2600+.

  Rigby SIGN cycle 1 COMPLETE (2026-07-05) via fresh isolation pin `pa-1164d91b3dce4b97` — NINETEENTH-consecutive dedicated fresh SIGN pin candidate. Verdict: SIGN-WITH-EDITS at MED-HIGH confidence. Cadence: 4-batch × 5-Q = 20 Q (ELEVENTH-consecutive application). 20 folds landed pre-Chris-ratification (5 AGREE + 14 STRENGTHEN + 1 Q20 combined verdict-format response). Cycle 2 NOT required. Full fold ledger at §20.6.2. Standard Rigby verdict format at §20.6.1: overall MED-HIGH confidence; most accurate = zero-drift baselines + verifier-loop conflict resolution; weakest = completeness-implicating enumerations + typed-rate delta framing; missing area = consolidated Denominator Contract box (folded to §1.1); overstated maturity = CRITICAL unconditional + "frozen" without observed-outcome clarification (both folded); understated maturity = verifier-loop rigor + drift=0 stability signal (folded via §15 label rename to "Observability Risks"); biggest risk = shape-blind error handling at interceptor; next research = exhaustive WS surface enumeration + raw-fetch bypass mapping; what Claude got wrong = nothing major (pre-SIGN conflict resolution strengthens trust). SIGN pin retirement pending at cycle close.
---

# S2502 P2 Cat B — Frontend API-Client Architecture Design-Prep

## 1. Executive Summary

At HEAD `548f53a1`, the **frontend API-client architecture is structurally _drift-frozen_ (observed drift=0, not intentional policy freeze) at PARTIAL maturity across 5 sessions** on every measured axis (Rigby SIGN cycle 1 batch 1 Q1 fold — "drift-frozen (observed)" clarifies observed outcome vs intent). The consumer-side surface is a 4,194-LOC mega-module `frontend/src/lib/api.ts` exporting 93 `\w+Api` object-literal modules (~856 method definitions), 47 exported TypeScript response/request types, and 1 shared `axios.create()` instance at api.ts:13 — all IDENTICAL to the S2404 baseline (HEAD `31398008`, 5 sessions ago) and IDENTICAL to the S2203 baseline where the mega-module pathology was first named. 803 consumer call-sites (57 direct `api.<verb>()` in components + 667 `useQuery`/`useMutation` React Query wrappers across 74 files + 79 raw `fetch()` calls across 31 files) all still flow through — or bypass — the same silent-401 interceptor and the same 4-shape-blind error surface characterized by sibling S2501 Cat A.

**Typed-response coverage at HEAD:** 63/856 = **7.36%** in api.ts itself (Coverage A). **Denominator Contract note (Rigby SIGN cycle 1 batch 1 Q3 fold + batch 2 Q9 fold — see §1.1 Denominator Contract box below):** the +0.51pp delta from the S2203 6.85% baseline (63/919) is _mechanical denominator drift_ (method cleanup — numerator held constant at 63), NOT governance-driven typed-adoption improvement; treat as sanity metric, not progress signal; 52/54 = **96%** in `frontend/src/lib/cockpitApi.ts` (513 LOC, sole "typed island" exemplar); 42 typed React-Query hooks in `frontend/src/hooks/cockpitQueries.ts` inherit the cockpit island's 96% rate by construction. The **hand-written contract SoT for the cockpit surface** lives in `frontend/src/types/cockpit.ts` (820 LOC, 104 exported types); it is the ONLY file under `frontend/src/types/` at HEAD and the ONLY existence-proof that typed-client discipline is feasible on the platform. Every other apiModule (91 of 93) returns bare `Promise<AxiosResponse<any>>` at HEAD.

**Consumer-side of S2501 Cat A F6 four-shape 401 heterogeneity is SHAPE-BLIND.** The lone response interceptor at api.ts:48–62 reads only `error.response?.status === 401` and branches solely on `url.includes('/auth/') || url.includes('/login')` (S2203 §14 F3.5 whitelist substring, RE-VERIFIED BRITTLE at HEAD). All four S2501 F6 shape families — (a) DRF default `{"detail":"..."}`, (b) `APIResponseEnvelope` typed shape, (c) bare DRF dict, (d) non-DRF `JsonResponse` string family — flow through the SAME reject-and-console.warn branch for non-auth endpoints. This is Cat B's **KEY VERIFIER FINDING**: the consumer surface treats the four backend shape families as one indistinguishable failure event.

**Structural governance signals at HEAD:** (i) 18 DEAD-CANDIDATE apiModules (S2203 §14 F6 baseline) verified ZERO-consumer across `frontend/src/**/*.{ts,tsx}` outside api.ts itself — zero refutations at HEAD, none consumed; (ii) 79-raw-fetch bypass across 31 files verified IDENTICAL to S2404 baseline — a parallel, untyped, uninterceptable API surface that has neither shrunk (no migration) nor grown at file-count (accretion frozen at 31 files); (iii) codegen tooling `openapi-typescript` / `orval` / `kubb` / `swagger-codegen` / `zod` / `io-ts` / `valibot` / `superstruct` / `yup` — **0 of 9** present in `frontend/package.json` at HEAD (S2203 §14 F5 baseline UNCHANGED); (iv) `AxiosError` typed catches / `axios.isAxiosError` guards — 0 matches; (v) React `ErrorBoundary` / `componentDidCatch` / `getDerivedStateFromError` — 0 matches; (vi) `CODEOWNERS` at repo root (S2499 AU-D5 remediation) declares `/frontend/src/lib/api.ts @clwest` explicitly at line 31, but `cockpitApi.ts` + `hooks/cockpitQueries.ts` remain UNASSIGNED per CODEOWNERS lines 8–13 explicit deferral to S2600+ per Group 2200 T-slot maintainer-decision batch.

**Biggest CONSUMER-side gaps for S2599 xx99 close:** (i) no adopted typed-client codegen path (openapi-typescript / orval / kubb / zod — feasibility-only per S2500 §7 anti-scope #7 — Chris-D-verdict-request at xx99); (ii) no error-envelope boundary framework at the consumer (R6 error-boundary framework establishment per S2299 §8.4 T2 R6 gated on Cat C S2503 + Cat A S2501); (iii) no per-surface consumption-discipline baseline for Workspace / Betting / Command Center / PA / Neural Orchestra / Revenue / Advisor pages (Cat B enumerates but does not prescribe); (iv) no api.ts extraction / domain-scoping strategy (S2299 §8.3 R3 CODEOWNERS-dependent + S2203 R4 post-arc T-slot); (v) 79-raw-fetch bypass classification is UNKNOWN at file-shape level (public / SSE / streams / auth-required-migration-candidate).

**Cat B boundary discipline (mirroring Cat A):** this audit COLLECTS boundary evidence + INVENTORIES option-space for downstream design-prep + Chris-D-verdicts at S2599 xx99 close; it does NOT prescribe path A/B/C selection, api.ts extraction ordering, DEAD-CANDIDATE removal, raw-fetch migration policy, or typed-client codegen framework choice. Verbs stay `enumerate / inventory / measure / classify / defer / propose evidence-collection`. Every "recommendation" in §19 is decision-candidate evidence for Chris-D-verdict at xx99, not a directive.

**R6 error-boundary framework gap-record note (Rigby SIGN cycle 1 batch 4 Q16 fold — explicit gap-record + non-prescription scope statement):** Cat B verifies at HEAD `ErrorBoundary` / `componentDidCatch` / `getDerivedStateFromError` = 0 matches across `frontend/src/**` (R6 error-boundary framework establishment prerequisite per S2299 §8.4 T2). Cat B RECORDS the gap as verified-absent boundary evidence for downstream owners; Cat B does NOT prescribe framework design (owned by Cat C S2503 typed-envelope γ mechanism + Group 2200 post-arc T-slot for global error UX contract per Rigby SIGN cycle 1 batch 3 Q11 fold — ownership NOT exclusively Cat C).

### 1.1 Denominator Contract + Sampling Completeness (Rigby SIGN cycle 1 batch 2 Q9 STRENGTHEN + batch 4 Q17 STRENGTHEN + Q20 fold — consolidated per Rigby "missing area" verdict)

Cat B rate claims + numeric baselines with unit of analysis + scope + verification method:

| Metric | Numerator | Denominator | Rate | Unit of analysis | Scope | Method |
|---|---|---|---|---|---|---|
| Coverage A typed rate (api.ts internal) | 63 | 856 | **7.36%** | typed-generic `api.\w+<` calls / total `api.\w+(` calls | api.ts only | Exhaustive internal grep. **Delta from S2203 6.85% is mechanical denominator drift (919→856 cleanup), NOT numerator growth.** |
| Coverage B typed rate (global) | 115 | 910 | **~12.6%** | api.ts + cockpitApi.ts combined | frontend/src/lib/ | Derived (Coverage A + cockpitApi 52/54). Adjusted from S2203 11.8% via method-count delta. |
| DEAD-CANDIDATE apiModule rate | 18 | 93 | **19.4%** | zero-consumer apiModules / total exports | api.ts | Exhaustive per-module `\bXxxApi\.` grep excluding api.ts; zero refutations at HEAD. |
| Raw-fetch bypass share | 79 | 803 | **9.8%** | raw fetch() calls / total consumer sites | frontend/src/ | Exhaustive `fetch(` grep. |
| CockpitApi typed island rate | 52 | 54 | **96%** | typed `api.\w+<` / total `api.\w+(` | cockpitApi.ts | Exhaustive internal grep. |
| Consumer surface total | 803 | — | — | direct 57 + hook 667 + fetch 79 | frontend/src/ | S2404 §14.5 methodology RE-VERIFIED IDENTICAL. |
| WS subscription sites | 8 | — | — | targeted enumeration | frontend/src/ | Agent 4 TARGETED SAMPLE, NOT exhaustive; full enumeration deferred to Cat D T7/S2504 (Rigby SIGN cycle 1 batch 2 Q7 hedge). |
| CODEOWNERS coverage | 4 explicit / (unknown total files) | — | — | explicit-owner entries / files owned | frontend/src/lib/ | Direct read of `./CODEOWNERS`. cockpitApi.ts + apiClient.ts + hooks/ + types/ UNASSIGNED (§14 F7 + F8). |

**Sampling completeness statement (Rigby SIGN cycle 1 batch 2 Q10 fold):** Cat B used 6-parallel-Explore sweeps + targeted samples; did NOT perform exhaustive (apiModule × consumer file) Cartesian grep. `.js` / `.jsx` and non-standard call sites may exist (frontend uses `.ts` / `.tsx` at HEAD — S2203 §20.4 baseline: `Glob frontend/src/**/*.{js,jsx}` = 0 files — RE-VERIFIED assumption at Cat B). Macro zero-drift metrics REDUCE but do NOT ELIMINATE miss risk. Cycle 2 SIGN was NOT required per Rigby verdict; the completeness reduction is explicitly declared here.

### 1.2 Do Not Misread (Rigby SIGN cycle 1 batch 4 Q17 STRENGTHEN — exec-sum warning box)

1. **§14 F3 SHAPE-BLIND interceptor severity is CRITICAL only if S2503 Cat C requires shape-normalization landing first as a gating prerequisite; otherwise treat as HIGH.** Cat B does NOT assert the Cat C dependency as fact; the CRITICAL classification is CONDITIONAL on Cat C's future mechanism design (α/β/γ decision-space at S2503). If Cat C designs a mechanism that does NOT require shape-normalization first, F3 severity remains HIGH at consumer-observability impact.
2. **Typed-rate deltas (7.36% Coverage A vs 6.85% S2203 baseline) are mechanical unless numerator changes.** Do NOT interpret the +0.51pp delta as governance-driven typed-adoption progress. Numerator (63 typed calls) is UNCHANGED; denominator (856 vs 919) drifted downward via method cleanup. The delta is a sanity metric, not a signal.

## 2. Domain Purpose

**Playbook §9 canonical Q1 — What is the domain's job?**

The **frontend API-client layer** is the browser-side subsystem that translates React component / hook / store consumption calls into backend HTTP requests, attaches session credentials, routes error signals back to callers, and materializes typed vs untyped consumption discipline as an architectural policy. Concretely, at HEAD `548f53a1` it consists of:

1. A **single shared `axios` instance** at `frontend/src/lib/api.ts:13` (verified S2404 §17 zero-duplication holds; only 1 `axios.create()` match in the entire `frontend/src/` tree).
2. A **stack of 4 interceptors** on that instance: request-interceptor for `Token ${token}` attachment (api.ts:27–40); response-interceptor for silent-401 handling with brittle-substring whitelist (api.ts:43–62); a second request-interceptor pair for the Session-968 request-log circular buffer metadata (api.ts:3990–4048).
3. **93 apiModule object-literal exports** in api.ts (verified via `^export const \w+Api\s*=` exhaustive grep — 93 matches) with ~856 `api.<verb>()` invocations distributed across them (verified via internal-file grep).
4. A **typed island surface** consisting of `cockpitApi.ts` (513 LOC, 54 wrapper functions, 96% typed generics) + `types/cockpit.ts` (820 LOC, 104 hand-written types) + `hooks/cockpitQueries.ts` (42 React Query hooks wrapping cockpitApi 100%).
5. A **scoped-header helper** `apiClient.ts` that wraps `api.get/post` with `X-UI-Scope` custom header injection (Session 968 request-log filtering; no independent HTTP client, no interceptor override).
6. **803 consumer call-sites** across `frontend/src/**` distributed as 57 direct `api.<verb>()` in non-api.ts files + 667 `useQuery|useMutation` React Query wrappers across 74 files + 79 raw `fetch()` calls across 31 files that BYPASS the axios interceptor entirely.

**Playbook §9 canonical Q2 — What are the boundaries?**

Cat B's boundary is CONSUMER-SIDE: how frontend clients CONSUME the API (typing, error handling, response validation, module ownership, subsurface consumption patterns). Cat B does NOT own:

- Backend API contract SoT DECLARATION (Cat A S2501 owns: drf-spectacular retrofit, `@extend_schema` decoration, 96 Serializer bindings, OpenAPI 3.0 schema generation).
- Typed-error-envelope MECHANISM (Cat C S2503 owns α/β/γ decision-space including message/UX policy nested inside envelope mechanism per S2404 Rigby Q6 fold).
- Per-endpoint permission-floor registry (Cat D S2504 owns Cat B (c) LONG-TERM GOVERNANCE per S2499 CF-B1).
- REST↔WS message contract joint T7 (Cat D S2504 co-owns with Group 2600 PA).
- Auth mechanism / token lifecycle / refresh-endpoint (Group 2400 arc owned; closed at S2499; downstream execution T-slot).
- Backend response validation (Group 1700 Observability envelope enforcement locus; closed at S1799; envelope enforcement decision REMAINS OPEN per S2299 §9.5).
- Frontend rendering / component boundary discipline / god-component pattern (Group 2200 Cat A S2201 owned; closed at S2299).
- Frontend state / persistence discipline (Group 2200 Cat D S2204 owned; closed at S2299).

Cat B's job: **collect boundary evidence + inventory option-space** for the CONSUMER-side design-prep decisions that Cat C + Cat D + xx99 will ratify or defer per Chris-D-verdict.

## 3. Canonical Entry Points

**Playbook §9 canonical Q3 — Where does the domain live in code (file:line)?**

### 3.1 Single shared axios instance (HTTP substrate)

- `frontend/src/lib/api.ts:13` — `export const api = axios.create({ baseURL: API_BASE_URL, headers: { 'Content-Type': 'application/json' }, timeout: 90000, withCredentials: true })`
- `API_BASE_URL = import.meta.env.VITE_API_URL || '/api'` at api.ts:11
- Session annotations at HEAD: `Session 802` for timeout, `Session 819` for withCredentials, `Session 968` for request-log metadata extension via TypeScript module augmentation at api.ts:5–9.
- **Zero-duplication verified at HEAD**: `axios\.create\(` grep across `frontend/src/**/*.{ts,tsx}` = 1 match (api.ts:13). `cockpitApi.ts` + `apiClient.ts` re-use the shared `api` instance via `import { api } from '@/lib/api'`.

### 3.2 Interceptor stack (auth + silent-401 + request-log)

- `frontend/src/lib/api.ts:27–40` — request interceptor: `const token = useAuthStore.getState().token; if (token) config.headers.Authorization = 'Token ${token}'`. NB: **Django TokenAuth prefix `Token ` — NOT `Bearer `**. Debug logging at line 31–33 for dev-mode + `/platform/` URLs.
- `frontend/src/lib/api.ts:43–62` — response interceptor with silent-401 handler (see §7.3 runtime flow for full trace).
- `frontend/src/lib/api.ts:~3990–4048` (Session 968) — second request/response interceptor pair for request-log circular-buffer metadata (max 200 entries dev-only per S2204 §18.6 baseline). Extends `InternalAxiosRequestConfig` interface at api.ts:5–9 with `metadata?: { requestId: number; startTime: number }` field.

### 3.3 apiModule exports (93 total at HEAD)

- First apiModule: `homeApi` at api.ts:67 (Session 884 annotation).
- Last apiModule: `bpaasApi` at api.ts:4187 (build-packet-as-a-service surface).
- Full 93-module enumeration in §6.1 table below.

### 3.4 Typed-island surface

- `frontend/src/lib/cockpitApi.ts` — 513 LOC, 54 exported functions with explicit generic bindings `api.get<T>()` / `api.post<T>()`. Imports the shared `api` instance at line 1. No independent interceptor.
- `frontend/src/types/cockpit.ts` — 820 LOC, 104 exported types (23 type unions + ~81 interfaces per Agent 1 spot-check; 60+ interfaces + 23 unions per Agent 1 sample). This is the ONLY file under `frontend/src/types/` at HEAD (grep confirmed).
- `frontend/src/hooks/cockpitQueries.ts` — 42 exported React Query hooks (per Agent 3 count); all 42 wrap `cockpitApi` functions with `useQuery` / `useMutation`. `queryKey` naming convention `cockpit-{entity}` / `cockpit-{entity}-{param}`. `refetchInterval` 15,000–30,000 ms polling for real-time surfaces. No global config.

### 3.5 Scoped-header wrapper

- `frontend/src/lib/apiClient.ts` — `scopedGet<T>()` / `scopedPost<T>()` inject `X-UI-Scope: <scope>` header into `AxiosRequestConfig.headers`. Purpose: request-log filtering by UI context per Session 968 metadata-stamping. No auth override.

### 3.6 Consumer call-site distribution (803 total at HEAD)

- **57 direct `api.<verb>()` in non-api.ts files** across `frontend/src/**/*.{ts,tsx}` (57 = 913 total repo grep − 856 defs in api.ts itself). Sample sites include `WorkspaceCreatePage.tsx`, `Sidebar.tsx`, `HowItWorksPage.tsx`, `DemoPipelineCard.tsx`, `TriggerRulesPanel.tsx`, `ActionsPanel.tsx`, `ProjectHubPage.tsx`, `ProjectsPage.tsx`, and 13 additional pages/components.
- **667 `useQuery`|`useMutation` React Query wrappers** across 74 files. Largest hook file: `hooks/cockpitQueries.ts` with 58 matches. Second-highest: `CommandCenterPage.tsx` with 26, `AgentsPage.tsx` with 22, `IntelligencePage.tsx` with 21, `BettingPage.tsx` with 20, `AIConsciousnessTab.tsx` with 20, `ContentStudioTab.tsx` with 20, `VideoStudioPage.tsx` with 18, `OrchestrationTab.tsx` with 17, `KnowledgeTab.tsx` with 17.
- **79 raw `fetch()` calls across 31 files** — parallel untyped surface that bypasses the axios interceptor entirely. Sample files: `paStore.ts`, `usePageTracking.ts`, `DemoModeBanner.tsx`, `BlogViewerPage.tsx`, `DocsIndexPage.tsx`, `VipAcceptPage.tsx`, `GlobalPADock.tsx`, `HeartWidget.tsx`, `OperatorEdgePage.tsx`, `LiveMetricsDashboard.tsx`, `ConversationsPanel.tsx`, `DataIntelTab.tsx`, `DreamsPanel.tsx`, `InitiativesTab.tsx`, `OpsConsoleTab.tsx`, `IntelligenceTab.tsx`, `Stage3EvaluationTab.tsx`, `AIConsciousnessTab.tsx`, `LaunchpadTab.tsx`, `ConceptForgeTab.tsx`, `ToolCallAnalyticsTab.tsx`, `ContentStudioTab.tsx`, `CampaignTab.tsx`, `OrchestrationTab.tsx`, `GitTab.tsx`, `BuildPacketWizard.tsx`, `InfrastructureTab.tsx`, `CareerTab.tsx`, `KnowledgeTab.tsx`.

## 4. Major Models

**Playbook §9 canonical Q4 + Q5 — Which types/models represent the domain? What are their relationships?**

### 4.1 api.ts exported types (47 total at HEAD)

Verified via `^export (interface|type) \w+` grep on `frontend/src/lib/api.ts` = **47 matches** (IDENTICAL to S2203 §14 F4 baseline; zero-drift 5 sessions since S2203 close; zero-drift since S2404 close). Per Agent 1 spot-check classification (top 15 sample + random 5-sample):

| Type family | Sample count | Wired-vs-orphan |
|---|---|---|
| Wired (consumed as generic in `api.get<X>()` or referenced outside api.ts) | ~12–13 | E.g. `TimeRange` (line 215), `ToolRun` (1085), `UnifiedPAResponse` (1093), `PAChatAsyncResponse` (1108), `PAChatStatusResponse` (1115), `ConversationSummary` (1131), `ConversationMessage` (1139), `StockDashboard` (1285), `MarketBrief` (1304), `GovernmentBill` (1399), `Blog` (3882), `BlogListResponse` (3905), `RequestLogEntry` (3968). |
| Orphan (declared but not referenced outside api.ts) | ~3 (sample) | `FeedbackRequest` (768), `GoalProgressRequest` (779), `SkillDemonstrationRequest` (785). Sample orphan rate ~6–20% (n=15 spot-check + 5 random). |

**Cat B verifier note (Rigby SIGN cycle 1 pre-emptive fold candidate):** the 47-count is the exported TypeScript surface; the actual _internal-to-api.ts_ interface count is higher (Agent 6 counted 51 total interface definitions inside api.ts by grep pattern, some non-exported). The 47-exported-vs-51-internal-defined delta is a de-facto internal-vs-external boundary — not a drift finding at Cat B scope. Adopt 47 EXPORTED as canonical per S2203 §14 F4 predecessor precedent.

### 4.2 types/cockpit.ts (typed contract SoT for the cockpit surface)

- **820 LOC** at HEAD (S2203 baseline 821; 1-LOC drift; immaterial).
- **104 exported types** per S2203 baseline (Cat B RE-VERIFY not re-executed; parent-Claude uses S2203 count as adopted).
- Composition per Agent 1 spot-check: 23 type unions (`RunStatus`, `InboxSeverity`, `AlertKind`, etc.) + ~81 interfaces (`RunTrigger`, `RunImportance`, `InboxItem`, `AlertsResponse`, `ConfigProvider`, `AutopilotPolicy`, etc.).
- Import pattern: `cockpitApi.ts` imports type-only via `import type { ... } from '@/types/cockpit'` at line 2. **No circular dependency with api.ts.**

### 4.3 Other type files under `frontend/src/types/`

- **NONE.** Only `cockpit.ts` exists at HEAD (S2203 §14.5 baseline VERIFIED). No `betting.ts`, no `pa.ts`, no `workspace.ts`. All other apiModules infer response shape from view code or use `any` implicit.
- **Implication:** 91 of 93 apiModules (excluding cockpitApi + platformApi's inline generics) have no exported response type at all. Consumer components either inline-declare local `interface *Response` at call-sites (S2203 §15.6 baseline: ~12+ sampled inline duplications; full count deferred per S2299 §6 U4) or use `.data` bare access with no type discipline.

### 4.4 apiModule object-literal shape (structural type)

Each apiModule at HEAD follows the shape:

```typescript
export const \w+Api = {
  method1: (params?: T1) => api.<verb><ResponseType>('/url/', options),
  method2: (id: string, body?: T2) => api.<verb>(`/url/${id}/`, body),
  ...
}
```

- **93 modules × ~9.2 methods/module average** = ~856 method definitions (verified via api.ts internal grep `api\.(get|post|put|delete|patch)\(` = 856 matches).
- **Typed-generic invocations**: 63 of 856 = 7.36% at HEAD (verified via internal grep `api\.\w+<` — 63 matches). This is +0.51pp from S2203 baseline (63/919 = 6.85%); the delta is _method cleanup_ (919→856), not net-new typing.
- **cockpitApi typed rate**: 52 of 54 methods use explicit `<T>` generics = 96% (S2203 baseline unchanged at HEAD).
- **platformApi note**: line 3257→3920 spans 663 LOC (monolithic apiModule; 7.1% of api.ts total LOC). Per Agent 3 sample: platformApi uses `api.get<{...inline typed response...}>('/url/')` pattern with **inline anonymous response types** (not exported interfaces) for ~30 methods. This is neither the cockpitApi typed-island pattern (imported types) nor the bare-api pattern (untyped `.data` access) — it is a **third partial-typing pattern**. Cat B classifies as MED-adoption-signal; whether it graduates to typed-island discipline or churns under a codegen path is S2599 xx99 Chris-D-verdict-request evidence per S2299 §6 U3.

## 5. Major Services

**Playbook §9 canonical Q6–Q8 — What services operate on this data?**

The frontend API-client layer is not a "service" surface in the Django-app sense; there are no Celery tasks, no cross-domain service classes. The service-adjacent primitives at HEAD are:

### 5.1 Files under `frontend/src/lib/` with HTTP surface

| File | LOC | axios | fetch | Purpose |
|---|---|---|---|---|
| `api.ts` | 4,194 | 1 `axios.create()` at line 13 + 4 interceptor `use()` calls | 0 | Core mega-module: 93 apiModule + shared axios instance + 2×interceptor pair (auth + request-log) |
| `apiClient.ts` | ~20 (est.) | Uses shared `api` instance (type-only axios import) | 0 | X-UI-Scope scoped-header wrapper for request-log filtering (Session 968) |
| `cockpitApi.ts` | 513 | Uses shared `api` instance (import at line 1) | 0 | Typed-island wrapper: 54 functions with explicit `api.get<T>()` generics + response destructuring |
| `cn.ts` | (small) | — | — | CSS utility (not HTTP) |
| `pdfExport.ts` | (small) | — | — | PDF generation (not HTTP) |
| `time.ts` | (small) | — | — | Date utilities (not HTTP) |

**S2404 §17 zero-duplication claim RE-VERIFIED at HEAD:** exactly 1 `axios.create()` call across all of `frontend/src/**`; both `cockpitApi.ts` + `apiClient.ts` re-use the shared `api` instance from api.ts.

### 5.2 Interceptor stack summary at HEAD

The response-interceptor call ordering (post-registration) is chained: register first = called first for requests, called last for responses (per axios interceptor semantics).

1. **Request pass** (in registration order): `api.ts:27–40` auth-token attach → `api.ts:~3990–4005` request-log metadata stamp (requestId + startTime).
2. **Response pass** (in REVERSE registration order): `api.ts:~4009–4048` request-log status+duration update + subscriber notify → `api.ts:43–62` silent-401 handler.

Consequence: by the time the silent-401 handler runs, the request-log entry has ALREADY been updated with the 401 status. This means the observability substrate (request-log ring buffer) captures 401 events regardless of whether the interceptor's whitelist matches. **Consumer-visible telemetry EXISTS at the interceptor layer**; it is dev-only and 200-entry-capped per S2204 §18.6, and there is no server-side auth-event emission (S2404 F-D-EVENT-1 CF-D3 to Group 1700 Observability roll-up).

### 5.3 `cockpitApi.ts` typed-wrapper pattern

Sample from S2404 §17 + Agent 1 spot-check:

```typescript
// cockpitApi.ts pattern (verified)
export async function getRuns(params?: RunsParams): Promise<RunSummary[]> {
  const { data } = await api.get<RunSummary[]>('/cockpit/runs/', { params })
  return data
}
```

- **Explicit generics** on every `api.get<T>()` / `api.post<T>()` call.
- **Destructuring `const { data } = await ...`** returns the response body directly, not the AxiosResponse envelope.
- **Types imported** from `types/cockpit.ts` via `import type { ... }`.
- **No independent interceptor** — inherits full stack from shared `api` instance.

### 5.4 `hooks/cockpitQueries.ts` React-Query wrapper pattern

Sample from Agent 2 spot-check:

```typescript
// cockpitQueries.ts pattern (verified)
export function useRuns(params?: RunsParams) {
  return useQuery({
    queryKey: ['cockpit-runs', params],
    queryFn: () => getRuns(params),  // wraps cockpitApi.getRuns()
    refetchInterval: 15_000,
  })
}
```

- **Wraps `cockpitApi.ts` functions**, not api.ts directly.
- **Inherits 96% typed rate** from cockpitApi typed-island.
- **queryKey convention**: `['cockpit-{entity}', ...params]`.
- **No global config**; uses `@tanstack/react-query` defaults for stale/gc timing.
- **No error-handling / retry / TError generic set** in sampled hooks (per S2404 §20.3 U1: exact React Query `TError` generic adoption estimated ≤1% of 667 RQ sites; refinement deferred).

## 6. Major APIs and Interfaces

**Playbook §9 canonical Q9 — What external-facing surfaces exist?**

### 6.1 93-apiModule inventory at HEAD

Verified via `^export const \w+Api\s*=` exhaustive grep = 93 matches. Per Agent 1 enumeration + parent-Claude verifier-loop reconciliation:

| # | apiModule | Line | Approx. methods | Notes |
|---|---|---|---|---|
| 1 | homeApi | 67 | 3 | Session 884; home boot |
| 2 | authApi | 73 | 4 | login, logout, getUser, validateToken |
| 3 | agentsApi | 81 | 7 | Agent lifecycle |
| 4 | agentChannelsApi | 95 | ~12 | CRUD channels/memberships |
| 5 | agentMonitoringApi | 123 | 6 | Real-time agent metrics |
| 6 | agentToolsApi | 140 | 9 | Tool CRUD |
| 7 | agentTemplatesApi | 158 | 8 | Template CRUD |
| 8 | agentOrchestrationsApi | 188 | 9 | **DEAD-CANDIDATE (S2203 §14 F6 RE-VERIFIED zero-consumer at HEAD)** |
| 9 | activityApi | 207 | 2 | recent, learning |
| 10 | dreamsApi | 217 | ~11 | Dream pipeline |
| 11 | conversationsApi | 248 | ~8 | Multi-agent conversations |
| 12 | conversationContractApi | 277 | 2 | overview, detail |
| 13 | hiveMindApi | 285 | 5 | Hive mind lifecycle |
| 14 | memoryPalaceApi | 305 | ~19 | Memory palace CRUD + explore |
| 15 | memoryClustersApi | 357 | ~10 | Cluster CRUD + merge/rename |
| 16 | evolutionApi | 394 | ~16 | Timeline + milestones |
| 17 | moodApi | 430 | ~12 | Mood tracking |
| 18 | timeTravelApi | 464 | ~19 | Snapshots + restore |
| 19 | timeCapsuleApi | 512 | 8 | Time capsule CRUD |
| 20 | classificationApi | 538 | 6 | **DEAD-CANDIDATE (S2203 §14 F6 RE-VERIFIED zero-consumer at HEAD)** |
| 21 | decisionsApi | 550 | 8 | Boardroom decisions (URL prefix `/api/boardroom/decisions/` per Agent 4 verify) |
| 22 | bodyApi | 564 | ~10 | Body-systems overview |
| 23 | intelligenceApi | 583 | 3 | Summary/dashboard/insights |
| 24 | incomeBuilderApi | 590 | ~10 | Income-builder pipeline |
| 25 | opportunitiesApi | 615 | 5 | Opportunity CRUD |
| 26 | ecosystemApi | 626 | 2 | **DEAD-CANDIDATE (S2203 §14 F6 RE-VERIFIED zero-consumer at HEAD)** |
| 27 | dashboardApi | 631 | 6 | Dashboard overview |
| 28 | spidersApi | 641 | 2 | Spider list/manage |
| 29 | spiderIntegrationApi | 647 | ~18 | Spider install/config/test/sync |
| 30 | spiderFeedApi | 693 | 5 | Feed subscription |
| 31 | pilotsApi | 721 | 9 | Pilot lifecycle |
| 32 | experimentsApi | 739 | 8 | Experiment CRUD/run/analyze |
| 33 | learningApi | 754 | 8 | Learning stats |
| 34 | userLearningApi | 793 | ~16 | User learning profile |
| 35 | researchApi | 840 | 3 | **DEAD-CANDIDATE (S2203 §14 F6 RE-VERIFIED zero-consumer at HEAD)** |
| 36 | distributionApi | 847 | ~28 | Distribution CRUD |
| 37 | contentApi | 895 | ~51 | Content Studio; **1 of 4 primary cross-cutter** |
| 38 | settingsApi | 1048 | ~17 | User settings |
| 39 | assistantApi | 1147 | ~22 | **1 of 4 primary cross-cutter**; PA-path (typed generics on paChat, paChatStatus) |
| 40 | bettingApi | 1229 | ~25 | **Money-path**; BettingPage primary consumer |
| 41 | sportsHubApi | 1279 | 1 | overview |
| 42 | governmentApi | 1464 | 8 | Bills/members/voting |
| 43 | stockApi | 1475 | 9 | Stock intelligence dashboard |
| 44 | legacyLearningApi | 1494 | ~12 | **DEAD-CANDIDATE (S2203 §14 F6 RE-VERIFIED zero-consumer at HEAD)** |
| 45 | legalApi | 1517 | ~17 | Legal docs |
| 46 | podcastApi | 1548 | 9 | Podcast pipeline |
| 47 | portfolioApi | 1575 | ~16 | Portfolio assets |
| 48 | humanApi | 1607 | ~20 | **1 of 4 primary cross-cutter** |
| 49 | adminApi | 1667 | ~13 | Admin CRUD |
| 50 | workspaceApi | 1695 | ~18 | **1 of 4 primary cross-cutter** |
| 51 | workspaceOperationsApi | 1737 | 5 | Workspace ops |
| 52 | workspaceTriggersApi | 1748 | ~11 | Trigger CRUD |
| 53 | workspaceTriggerConfigsApi | 1783 | ~12 | **DEAD-CANDIDATE (S2203 §14 F6 RE-VERIFIED zero-consumer at HEAD)** |
| 54 | llmApi | 1811 | 7 | **DEAD-CANDIDATE (S2203 §14 F6 RE-VERIFIED zero-consumer at HEAD)** |
| 55 | heartApi | 1849 | 5 | Body-systems: heart |
| 56 | lungsApi | 1869 | 7 | Body-systems: lungs |
| 57 | circulatoryApi | 1894 | 8 | **DEAD-CANDIDATE (S2203 §14 F6 RE-VERIFIED zero-consumer at HEAD)** |
| 58 | spineApi | 1925 | 9 | **DEAD-CANDIDATE (S2203 §14 F6 RE-VERIFIED zero-consumer at HEAD)** |
| 59 | llmRoutingApi | 1963 | 4 | LLM routing |
| 60 | immuneApi | 1987 | ~13 | **DEAD-CANDIDATE (S2203 §14 F6 RE-VERIFIED zero-consumer at HEAD)** |
| 61 | digestiveApi | 2042 | 8 | **DEAD-CANDIDATE (S2203 §14 F6 RE-VERIFIED zero-consumer at HEAD)** |
| 62 | muscularApi | 2072 | 8 | **DEAD-CANDIDATE (S2203 §14 F6 RE-VERIFIED zero-consumer at HEAD)** |
| 63 | brainApi | 2103 | 5 | **DEAD-CANDIDATE (S2203 §14 F6 RE-VERIFIED zero-consumer at HEAD)** |
| 64 | skinApi | 2122 | 6 | **DEAD-CANDIDATE (S2203 §14 F6 RE-VERIFIED zero-consumer at HEAD)** |
| 65 | nervousApi | 2144 | 6 | **DEAD-CANDIDATE (S2203 §14 F6 RE-VERIFIED zero-consumer at HEAD)** |
| 66 | advisorsApi | 2166 | 5 | Advisors CRUD |
| 67 | relationshipsApi | 2185 | ~10 | Relationships |
| 68 | ragApi | 2215 | ~17 | RAG retrieval |
| 69 | neuralOrchestraApi | 2290 | 7 | Neural Orchestra |
| 70 | mythologyApi | 2315 | ~17 | Mythology surfaces |
| 71 | collectiveApi | 2365 | ~26 | Collective intelligence |
| 72 | reasoningApi | 2418 | ~16 | Reasoning surfaces |
| 73 | experimentRecommendationsApi | 2457 | 1 | recommend |
| 74 | autonomousApi | 2462 | ~15 | **DEAD-CANDIDATE (S2203 §14 F6 RE-VERIFIED zero-consumer at HEAD)** |
| 75 | analyticsApi | 2492 | ~24 | Analytics |
| 76 | journeyApi | 2546 | ~16 | **DEAD-CANDIDATE (S2203 §14 F6 RE-VERIFIED zero-consumer at HEAD)** |
| 77 | billingApi | 2577 | ~15 | **Money-path**; BillingPage primary consumer |
| 78 | voiceMarketplaceApi | 2609 | ~27 | Voice marketplace |
| 79 | ttsApi | 2665 | 8 | TTS surface |
| 80 | integrationHealthApi | 2711 | 4 | **DEAD-CANDIDATE (S2203 §14 F6 RE-VERIFIED zero-consumer at HEAD)** |
| 81 | orchestrationApi | 2948 | ~11 (Agent 3) or ~26 (Agent 1) — parent verifier note: Agent counts diverge; adopt Agent 3 conservative estimate; orchestration surface is monolithic-adjacent | Orchestration workflows |
| 82 | docsIndexApi | 3101 | 4 (Agent 3; typed) or ~12 (Agent 1) — same divergence pattern | Docs index; 100% typed per Agent 3 |
| 83 | platformApi | 3257 | ~30 (Agent 3 verified) — **MONOLITHIC**: 3257→3920 = 663 LOC (7.1% of api.ts total). Inline anonymous typed responses (third pattern between cockpitApi typed-island and bare api). | Platform mission/metrics/governance/canon/playbooks etc. |
| 84 | blogsApi | 3921 | ~22 | Blog CRUD (typed via `BlogListResponse` at line 3905) |
| 85 | campaignApi | 4054 | 8 | Campaign CRUD |
| 86 | auditApi | 4069 | 4 | Audit logs |
| 87 | executorApi | 4081 | 8 | Executor lifecycle |
| 88 | deliverablesApi | 4095 | ~11 | Deliverable CRUD |
| 89 | previewApi | 4113 | ~24 | Preview environments |
| 90 | reviewApi | 4161 | 4 | Review context |
| 91 | statusApi | 4178 | 1 | overview |
| 92 | revenueApi | 4182 | 2 | Revenue summary/record |
| 93 | bpaasApi | 4187 | 4 | BPaaS schema |

**Cat B verifier-loop note:** Sub-agent method-count estimates diverge on ~10 modules due to counting convention (nested `api.<verb>(` invocations for cascade-fetch patterns vs top-level method keys). Adopt CONSERVATIVE Agent-3-verified counts where they exist; mark other module counts as APPROXIMATE. Load-bearing count is the ARCHITECTURAL PATTERN, not the per-module tally: 93 modules × ~9.2 methods avg = ~856 total defs (VERIFIED via internal grep).

### 6.2 Primary cross-cutter modules (S2203 §17.2 baseline verified at HEAD)

Per Agent 3 verified enumeration:

| Module | Line | ~Method count | ~Consumer file count (grep `\bXxxApi\.` across `frontend/src/**` excluding api.ts) |
|---|---|---|---|
| `humanApi` | 1607 | ~20 | 15 files |
| `assistantApi` | 1147 | ~22 | 22 files |
| `workspaceApi` | 1695 | ~18 | 23 files |
| `contentApi` | 895 | ~51 | 47 files (highest-traffic cross-cutter) |

All 4 primary cross-cutters VERIFIED PRESENT at HEAD line numbers; consumer-file counts approximate per Agent 3 grep.

### 6.3 Typed-rate matrix at HEAD (verified)

| Surface | Typed calls | Total calls | Typed rate | Delta from S2203 baseline |
|---|---|---|---|---|
| **api.ts (Coverage A)** | 63 | 856 | **7.36%** | +0.51pp (was 6.85% at 63/919; delta = method cleanup) |
| **cockpitApi.ts (typed island)** | 52 | 54 | **96%** | 0 (identical) |
| **Global (Coverage B: api.ts + cockpitApi.ts)** | 115 | 910 | **12.6%** | slight +0.8pp from S2203 11.8% baseline (adjusted for total method delta) |
| **hooks/cockpitQueries.ts (inherits cockpit)** | ~42 | 42 | ~100% (wraps cockpitApi 96%) | 0 (identical) |

**Cat B boundary observation:** the 91-of-93 apiModule bare-call pattern is UNCHANGED at HEAD; the typed-island (cockpitApi) is UNCHANGED at HEAD; the platformApi inline-typed-generic pattern is a THIRD pattern not previously named at S2203 (Rigby SIGN-preview candidate for confirmation). No apiModule outside cockpitApi has adopted typed-island discipline in 5 sessions.

### 6.4 WebSocket subscription surface at HEAD (T7 REST↔WS parallel)

Per Agent 4 TARGETED enumeration at HEAD, **8 identified WebSocket subscription sites** exist from targeted grep on `new WebSocket(`, `useWebSocket`, and hook-factory search (Rigby SIGN cycle 1 batch 2 Q7 fold — hedged from "8 total" to "8 identified from targeted enumeration"; full enumeration deferred to Cat D T7 joint at S2504 which may extend the pattern set with `socket.io`, `useSubscription`, `ws://` / `wss://` literals if applicable):

| Hook / subscription | Endpoint | Consumer pages | REST-parallel? |
|---|---|---|---|
| `useSystemEvents()` | `/ws/system-events/` | IntelligencePage + AgentsPage + WorkspacePageNew | Disjoint from REST |
| `useAgentUpdates()` | `/ws/agent-updates/` | AgentsPage | Disjoint |
| `useLearningFeed()` | `/ws/learning-feed/` | AgentsPage | Disjoint |
| `useAgentConversations()` | `/ws/agent-conversations/` | (defined but unused at HEAD) | Disjoint |
| `useHeartUpdates()` | `/ws/heart/` | Layout.tsx (via HeartWidget) | Disjoint |
| Generic `useWebSocket()` | `/ws/pa/conversations/{id}/` | CommandCenterPage (dynamic) | **HYBRID**: REST list via api.pa.conversations + WS stream |
| Generic `useWebSocket()` | `/ws/dashboard/` | HeartWidget | Disjoint |
| Hook factory count | 5 exported + 1 base function = 6 factories in `hooks/useWebSocket.ts` | — | — |

**Cat B boundary observation for T7:** REST and WS transports are ARCHITECTURALLY DISJOINT at the client — no shared cache, no cross-transport sync, no invalidation link. Component re-renders trigger independent REST queries; WS messages trigger separate state updates. The 2 HYBRID surfaces (pa/conversations + dashboard) are the natural REST↔WS T7 joint scope; Cat D S2504 owns the joint-contract design-prep with Group 2600 PA co-authorship.

### 6.5 Codegen tooling absence RE-VERIFIED at HEAD

Per Agent 4 verified grep on `frontend/package.json`: `openapi-typescript`, `orval`, `kubb`, `swagger-codegen`, `zod`, `io-ts`, `valibot`, `superstruct`, `yup` — **0 of 9 present at HEAD**. S2203 §14 F5 baseline UNCHANGED. Frontend continues to hand-write all 93 apiModule + 47 exported types + 104 cockpit types + 42 React Query hooks without any auto-generation or runtime validation library.

## 7. Runtime Flows

**Playbook §9 canonical Q19 + Q20 — What are the request/response runtime flows?**

### 7.1 Standard consumer → backend request flow (typed-island path)

```
Component (e.g. CockpitPage.tsx)
  ↓
useRuns(params)              // hooks/cockpitQueries.ts:26
  ↓                          //   useQuery wrap
getRuns(params)              // cockpitApi.ts:38
  ↓                          //   const { data } = await api.get<RunSummary[]>('/cockpit/runs/', { params })
axios request pipeline:
  1. axios prepares request
  2. request interceptor 1 (api.ts:27–40): attach Token ${token}
  3. request interceptor 2 (api.ts:~3990–4005): stamp metadata (requestId, startTime)
  4. HTTP request emitted with credentials
  ↓
Backend response (200 OK)
  ↓
axios response pipeline (REVERSE registration order):
  5. response interceptor 2 (api.ts:~4009–4048): update request-log entry (status, duration)
  6. response interceptor 1 (api.ts:43–62): pass-through (no 401)
  ↓
cockpitApi destructures { data } → returns RunSummary[]
  ↓
useQuery caches with queryKey ['cockpit-runs', params] + refetchInterval 15s
  ↓
Component receives typed RunSummary[]
```

### 7.2 Standard consumer → backend request flow (bare-api path, 91 of 93 modules)

```
Component (e.g. BettingPage.tsx)
  ↓
useQuery({
  queryKey: ['betting-stats'],
  queryFn: () => bettingApi.stats(),
  ...
})
  ↓
bettingApi.stats()           // api.ts:1229ish
  ↓                          //   api.get('/api/v1/betting/stats/')  — NO generic type parameter
axios pipeline (identical to 7.1 steps 1–5)
  ↓
Component receives AxiosResponse<any> and ACCESSES response.data with no type discipline
```

**Consequence:** the 91-module bare-api path returns `AxiosResponse<any>`; consumer components either inline-declare `interface StatsResponse { ... }` at the call-site (S2203 §15.6 baseline; ~12+ sampled inline duplications), destructure `response.data` bare, or use `.data as SomeType` type-assertion. **No runtime shape validation; no compile-time type safety.**

### 7.3 Silent-401 runtime flow at HEAD — KEY VERIFIER FINDING

**Verified source at api.ts:43–62** (parent-Claude direct read):

```typescript
// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    // Session 819: Only redirect to login for explicit auth endpoints
    // Other 401s should be handled by the component (user might just need to refresh)
    if (error.response?.status === 401) {
      const url = error.config?.url || ''
      const isAuthEndpoint = url.includes('/auth/') || url.includes('/login')

      // Only force logout/redirect for auth-related 401s
      if (isAuthEndpoint) {
        useAuthStore.getState().logout()
        window.location.href = '/login'
      }
      // For other endpoints, just log the error - component can handle it
      console.warn('Authentication required for:', url)
    }
    return Promise.reject(error)
  }
)
```

**Trace: `api.get('/api/v1/betting/top-plays/')` returns 401 with S2501 F6 shape (a) `{"detail": "Authentication required."}`:**

1. axios receives 401 response body `{"detail": "Authentication required."}`.
2. Interceptor called with `error` = AxiosError with `response.status === 401`.
3. `url = '/api/v1/betting/top-plays/'`.
4. `isAuthEndpoint = url.includes('/auth/') || url.includes('/login')` = **FALSE** (betting URL matches neither).
5. `if (isAuthEndpoint)` branch skipped: `authStore.logout()` NOT called; `window.location.href = '/login'` NOT triggered.
6. `console.warn('Authentication required for:', url)` executed — visible only in dev-console.
7. `Promise.reject(error)` — caller receives raw AxiosError with untyped body.

**Trace: same URL returns 401 with S2501 F6 shape (b) `{"success": false, "error": {"code": "AUTH_REQUIRED", "message": "...", "details": {...}}}`:**

Steps 1–7 IDENTICAL. Interceptor reads only `error.response?.status === 401`; body shape is not inspected. Caller receives raw AxiosError; component MUST parse `error.response.data.error.code` if it expects shape (b), or fall back to `error.response.data.detail` for shape (a) — but neither pattern is enforced at the interceptor layer.

**Trace: same URL returns 401 with S2501 F6 shape (d) non-DRF `JsonResponse({"success": false, "error": "Sign-in required"}, status=401)`:**

Steps 1–7 IDENTICAL. Body is a plain object with `error` as a STRING (not dict). Component parsing `error.response.data.error.code` receives `undefined`; parsing `error.response.data.error` receives a string; there is NO code / message / details split.

**Cat B KEY VERIFIER FINDING (§14 F3 below):** the interceptor is **SHAPE-BLIND**. All four S2501 F6 shape families flow through the same reject-and-console.warn branch for non-auth endpoints. The consumer surface treats the backend's 4-shape heterogeneity as ONE indistinguishable failure event. Cat C S2503 (typed-error-envelope mechanism α/β/γ) depends on this: any typed-error envelope adoption path must FIRST land a shape-aware interceptor OR global error-transformer at the api.ts boundary — otherwise the typed-envelope contract cannot flow through to component-level catch blocks.

### 7.4 Auth-endpoint redirect flow (whitelist match)

**Trace: `api.post('/api/v1/auth/logout/')` returns 401:**

1. `error.response.status === 401` matches.
2. `url = '/api/v1/auth/logout/'`.
3. `isAuthEndpoint = url.includes('/auth/')` = **TRUE**.
4. `useAuthStore.getState().logout()` clears localStorage (authStore-managed keys only; see S2404 F-D-SIDEBAR-1 for full-cleanup gap).
5. `window.location.href = '/login'` triggers full-page reload + redirect.
6. `console.warn` still executes.
7. `Promise.reject(error)` — caller never sees it (page reloaded).

**Cat B boundary observation on whitelist:** `url.includes('/auth/')` also matches unrelated paths (hypothetical `/api/v1/beta/authorization-flow/` would match substring `/auth/`). S2203 §14.3 F3.5 flagged BRITTLE-MEDIUM at Rigby SIGN cycle 1 fold (LOW → MED); Cat B RE-VERIFIES at HEAD (whitelist substring string-literal UNCHANGED at api.ts:50). Cat D S2504 owns whitelist-replacement α/β/γ decision-space per S2404 §19.1 (Cat B does not prescribe a fix).

### 7.5 Raw-fetch bypass runtime flow (79 sites, 31 files)

```
Component (e.g. DemoModeBanner.tsx)
  ↓
const res = await fetch(url, {
  credentials: 'include',   // (optional; not enforced pattern-wide)
  headers: {...}            // (no token attach unless manually added)
})
  ↓
NO interceptor runs
NO token auto-attached
NO 401 auto-handled
NO request-log entry created
  ↓
Component MUST manually handle: !res.ok → error path; res.status === 401 → ???
```

**Cat B boundary observation:** the 79-site raw-fetch surface is a PARALLEL, UNTYPED, UNINTERCEPTABLE API surface operating alongside the interceptor-routed 803 (non-fetch) consumer surface. Neither cursor-typing nor shape-aware interceptor rewiring can affect it. S2404 §17 non-classification precedent: NOT a "wrapper-duplicate", but a "contract-bypass". Cat B enumerates; Cat D S2504 owns the classification refinement (per S2404 §19.3 item 2b post-arc T-slot: 3-axis classification — auth-required-vs-public + credentials-mode + response-type).

## 8. Data Ownership and Lifecycle

**Playbook §9 canonical Q11–Q13 — Who owns what data, and what is its lifecycle?**

### 8.1 Ownership at HEAD

Per `CODEOWNERS` at repo root (verified — file EXISTS at `./CODEOWNERS`, 48 lines; not `.github/CODEOWNERS` — S2404 F-D-OWN-1 partially remediated by S2499 AU-D5 with location established at repo root):

| Path | Owner | Coverage |
|---|---|---|
| `*` (default) | @clwest | Universal fallback |
| `/frontend/src/lib/api.ts` | @clwest | Explicit at CODEOWNERS:31 |
| `/frontend/src/stores/authStore.ts` | @clwest | Explicit at CODEOWNERS:32 |
| `/frontend/src/components/layout/Sidebar.tsx` | @clwest | Explicit at CODEOWNERS:33 |
| `/frontend/src/App.tsx` | @clwest | Explicit at CODEOWNERS:34 |
| `/frontend/src/lib/cockpitApi.ts` | UNASSIGNED | Falls to `*` default; NO explicit entry |
| `/frontend/src/lib/apiClient.ts` | UNASSIGNED | Falls to `*` default; NO explicit entry |
| `/frontend/src/hooks/` (glob) | UNASSIGNED | ZERO entries; falls to `*` default |
| `/frontend/src/hooks/cockpitQueries.ts` | UNASSIGNED | Falls to `*` default; NO explicit entry |
| `/frontend/src/types/` (glob) | UNASSIGNED | ZERO entries; falls to `*` default |
| `/frontend/src/types/cockpit.ts` | UNASSIGNED | Falls to `*` default; NO explicit entry |

**Cat B boundary observation (from CODEOWNERS lines 8–13 explicit comment):**

> "Cross-arc typed-error-envelope + whitelist-replacement ownership remains UNASSIGNED at Group 2400 close; will be reassigned at T2 Group 2500 API arc.
> Frontend-specific ownership (api.ts + authStore.ts + Sidebar.tsx) refined at S2600+ per Group 2200 T-slot maintainer-decision batch."

Cat B RE-VERIFIES this deferral is STILL PRESENT at HEAD — no incremental refinement between S2499 close and S2502 open. The cockpitApi + hooks/ + types/ ownership is EXPLICITLY QUEUED for post-arc T-slot; Cat B does NOT prescribe assignment (S2299 §8.3 maintainer-decision batch owned; single review pass discipline).

### 8.2 Lifecycle at HEAD

- **api.ts churn**: S2203 baseline said "407-session churn"; Agent 6 sampled git log at HEAD and found ~185 lifetime commits; drift note = probably counted different unit (session-count vs commit-count are not the same). **Load-bearing lifecycle signal**: high churn is CONFIRMED at HEAD by both counts; exact ratio is NOT LOAD-BEARING at Cat B scope.
- **cockpitApi.ts churn**: cockpit surface added Sessions ~795–968 range (per Session-tag annotations sampled); most active recent surface with typed contract SoT + 96% typed rate. Adopted post-S1505 baseline.
- **hooks/cockpitQueries.ts churn**: co-evolved with cockpitApi; wraps cockpitApi.ts 100%.
- **Raw-fetch bypass churn**: 79 sites at HEAD IDENTICAL to S2404 baseline (5 sessions; zero net-drift on site count). Whether individual sites have been added-and-removed vs additive-only is UNKNOWN at Cat B scope (Rigby SIGN cycle 1 preemptive fold candidate).

### 8.3 Data lifetimes at consumer

- **AxiosResponse envelope**: consumed immediately by cockpitApi destructure OR discarded by bare api consumer at method invocation.
- **useQuery cache**: `@tanstack/react-query` default staleTime + gcTime; cockpitQueries.ts uses `refetchInterval` 15–30s for polling.
- **Request-log ring buffer** (Session 968): dev-only, 200-entry cap per S2204 §18.6; consumer subscribers via `subscribe()` callback registration. NO server-side auth-event emission (S2404 F-D-EVENT-1 CF-D3 to Group 1700 Observability roll-up).

## 9. Integrations With Other Domains

**Playbook §9 canonical Q14 + Q17 + Q18 + Q21 + Q22 — What integrations exist?**

| Peer domain | Direction | Coupling type | Blast radius | Notes |
|---|---|---|---|---|
| **Group 2500 API Backend (Cat A S2501)** | Inbound (Cat B consumes Cat A) | STRONG (co-owner within Group 2500 arc) | 93 apiModule × ~856 methods → 1,873 URL patterns backend | Cat A DECLARATION-side handoff → Cat B CONSUMER-side handoff for S2599 xx99. F1 drf-spectacular disconnected + F6 4-shape 401 heterogeneity are Cat B's PRIMARY inherited findings. 3-slice API-slice sample (money/governance/PA) VERIFIED CONSUMED by Cat B (§9.2). |
| **Group 2400 Auth (closed at S2499)** | Inbound (Cat B is CONSUMER-side downstream) | STRONG (silent-401 SYSTEMIC per S2404 F-D-CALL-1) | 803 consumer sites at silent-401 exposure per S2404 §14.5; 79-raw-fetch bypass adds 9.8% invisible surface | Cat B RE-VERIFIED 803 count IDENTICAL at HEAD. Cat B has downstream inheritance-only; Cat D S2504 owns permission-floor remediation. |
| **Group 2200 Frontend (closed at S2299)** | Inbound (Cat B is CONSUMER-side follow-up to Cat C S2203) | STRONG (direct predecessor) | 4194 LOC + 93 module + 47 interface baseline | S2203 §14 F4 (mega-module) + F6 (18 DEAD-CANDIDATE) + §17.2 (4 cross-cutter) all RE-VERIFIED. Cat B extends 407-session-churn observation with S2404 F-D-CALL-1 803-classification overlay. |
| **Group 1700 Observability (closed at S1799)** | Bidirectional (request-log emit + envelope-enforcement consumption) | WEAK (envelope-enforcement locus decision REMAINS OPEN per S2299 §9.5) | Request-log ring buffer 200-entry dev-only cap | Cat B enumerates request-log at api.ts:3990–4048; envelope enforcement is Cat C S2503 (α/β/γ) + xx99 Chris-D-verdict at Group 2500 close. |
| **Group 2600 PA (open — S2600+ queued)** | Inbound (Cat B consumes PA endpoints via assistantApi) | STRONG (assistantApi = 1 of 4 primary cross-cutter, ~22 methods, 22 consumer files) | assistantApi consumer surface | Cat B enumerates; PA-side behavior spec is Group 2600 scope. T3 handoff bundle per S2299 §8.2 preserved. |
| **Group 1600 Content (semantic scope preserved)** | Inbound (Cat B consumes content endpoints via contentApi) | STRONG (contentApi = 1 of 4 primary cross-cutter, ~51 methods, 47 consumer files — highest-traffic) | contentApi consumer surface | Cat B enumerates render-authority split preserved; contentApi consumption discipline = Cat B scope, content semantic contracts = Group 1600 scope. |
| **Group 2300 Mobile (queued post-Group 2500)** | Adjacent (parallel silent-401 audit target) | UNKNOWN (Mobile surface not audited at S2502) | UNKNOWN | S2299 §9.1 Mobile queued post-arc; T5 cross-arc parallel silent-401 audit per S2404 §19.2 (CF-D4 + CF-C4 + Cat A CF-4) is Cat B adjacent. |
| **Group 1300 Memory + Group 1800 HumanAttention** | Adjacent (render-authority split preserved) | STRONG (memoryPalaceApi, humanApi = 1 of 4 primary cross-cutter) | humanApi consumer surface (~20 methods, 15 files); memoryPalaceApi + memoryClustersApi + evolutionApi + moodApi + timeTravelApi + timeCapsuleApi ≈ 6 memory-scope modules | Render-shape = Cat B; semantic-authority = Groups 1300/1800. |

### 9.1 Consumer-side coverage of S2501 3-slice API-slice sample

Per Agent 4 verified enumeration at HEAD:

**Money-path (`/api/v1/betting/`, `/api/v1/wager/`, `/api/v1/billing/`):**
- `bettingApi` (api.ts:1229) → BettingPage.tsx (primary) + CommandCenterPage.tsx (secondary). Endpoints: stats, wagers, arbitrageScan, liveOddsWithScores, markets, lineMovement, todaysGames, bettingBrief, sharpAction, trackRecord, pipelineStatus, quickPick, placeBet. All backend URL patterns present in api.ts URL literals.
- `sportsHubApi` (api.ts:1279) → BettingPage.tsx (live-odds integration).
- `billingApi` (api.ts:2577) → BillingPage.tsx (dedicated surface). Endpoints: subscriptionStatus, subscriptionPlans, paymentMethods, invoices, upcomingInvoice, usage, subscribe, cancelSubscription, resumeSubscription, setDefaultPaymentMethod, removePaymentMethod, billingPortal.

**Governance-path (`/api/boardroom/decisions/`, `/api/v1/advisor/`):**
- `decisionsApi` (api.ts:550) → AgentsPage.tsx (read) + workspace/tabs/BoardroomTab.tsx (approve/reject/promote). **URL prefix at HEAD is `/api/boardroom/decisions/`, NOT `/api/v1/governance/`** — Agent 4 verifier correction (S2500 §3.B naming imprecision; Cat B corrects at HEAD).
- `advisorsApi` (api.ts:2166) → AdvisorsPage.tsx + workspace/tabs/OrchestrationTab.tsx.

**PA-path (`/api/pa/`, `/api/v1/assistant/`):**
- `assistantApi` (api.ts:1147) → CommandCenterPage.tsx (primary) + GovernmentPage.tsx (secondary). Endpoints: paChat (typed), paChatStatus (typed), getConversation, getLearning, getAttentionItems, transcribe, voiceChat, speak, feedback, reset. **paChat is the primary typed exemplar OUTSIDE cockpitApi at HEAD**; adopts inline typed-generic pattern (PAChatAsyncResponse, PAChatStatusResponse).

**Cat B verifier finding**: 100% of S2501 §6.1 sample-slice endpoints have identifiable CONSUMERS at HEAD; zero orphaned backend endpoints at slice-sample scope. This is a load-bearing observation for xx99 Chris-D-verdict on Path A/B/C: any Path selection that leaves ~1,857 endpoints undecorated on the backend AUTOMATICALLY leaves the corresponding CONSUMER-side untyped (as it is today).

### 9.2 Surface-to-module consumption map (per Agent 4)

| Frontend surface | Primary apiModules consumed |
|---|---|
| WorkspacePageNew.tsx + workspace tabs | workspaceApi, workspaceOperationsApi, workspaceTriggersApi + tab-specific modules |
| BettingPage.tsx | bettingApi, sportsHubApi, humanApi |
| CommandCenterPage.tsx | assistantApi, contentApi, userLearningApi, bodyApi, humanApi, homeApi, agentsApi, orchestrationApi |
| AgentsPage.tsx | agentsApi, activityApi, dreamsApi, decisionsApi, experimentsApi, agentChannelsApi, agentMonitoringApi, agentToolsApi |
| AnalyticsDashboardPage.tsx | analyticsApi |
| BillingPage.tsx | billingApi |
| AdvisorsPage.tsx | advisorsApi |
| NeuralOrchestraPage.tsx | neuralOrchestraApi |
| workspace/tabs/BoardroomTab.tsx | decisionsApi, humanApi |
| workspace/tabs/OrchestrationTab.tsx | orchestrationApi, adminApi, agentsApi, advisorsApi |

Cat B does NOT recommend a specific per-surface consumption discipline — this is CONSUMER-side inventory for xx99 Chris-D-verdict evidence on Path A/B/C scope selection.

## 10. Event Flows

**Playbook §9 canonical Q19 + Q20 — What event flows exist?**

### 10.1 REST↔WS transport parallel at HEAD

Per Agent 4 verified enumeration, **8 distinct WebSocket subscription sites** operate in parallel with the 803-site REST consumer surface. Full table at §6.4 above.

**Cat B boundary observation**: no shared cache / no cross-transport sync / no cache-invalidation hooks tying WS message receipt to REST query re-fetch. Two example concrete risks:

1. **PA chat REST↔WS race**: `/api/pa/conversations/{id}/` (REST history fetch via assistantApi.getConversation) + `/ws/pa/conversations/{id}/` (WS stream of new messages) are architecturally disjoint. User sees REST-fetched history render while WS pushes new messages independently; there is NO React Query cache-invalidation hook triggered by WS message receipt. Cat D S2504 T7 joint scope.
2. **HeartWidget dashboard**: `HeartWidget.tsx` uses `useWebSocket('/ws/dashboard/')` for real-time metrics; if a REST fetch also touches `heartApi.overview()`, the two data sources are independently rendered.

Cat B enumerates; Cat D S2504 T7 joint contract-design-prep owns the joint contract with Group 2600 PA co-authorship.

### 10.2 Request-log observability substrate

`api.ts:3990–4048` (Session 968) request-log ring buffer emits events on every request-response cycle:

- **onRequest**: metadata stamped (requestId, startTime).
- **onResponse**: entry updated (status, duration, headers.X-UI-Scope).
- **onError**: entry updated with error status.
- **subscribe()**: callback registration for subscribers (dev-only UI, paStore, request-log tab).

**Cat B observation for Group 1700 T4 handoff**: this substrate is dev-only + 200-entry-capped + zero server-side auth-event emission (S2404 F-D-EVENT-1 CF-D3). If Cat C S2503 typed-error-envelope adopts γ-mechanism (RQ error callbacks + boundary), the ring buffer becomes the natural client-side telemetry origination; Group 1700 Observability envelope enforcement locus decision (S1799 close + open decision per S2299 §9.5) inherits.

## 11. Existing Documentation

**Playbook §9 canonical Q10 — What documentation exists?**

### 11.1 Direct-coverage docs at HEAD

| Doc | HEAD coverage | Coverage of Cat B scope |
|---|---|---|
| `docs/topics/frontend.md` | Lines 106–116 (§Contract-Surface Governance) + lines 128–135 (§REST API Contract Surface) refreshed at S2299 close per §7.5 anchor updates | Covers DECLARATION counts (93 apiModule + 6.85% typed + drf-spectacular partial + silent-401 SYSTEMIC + 18 DEAD-CANDIDATE) BUT does NOT cover CONSUMER-side contract discipline / typed-response adoption mechanics / cockpitApi-as-exemplar guidance / api.ts extraction / error-boundary framework |
| `docs/PLATFORM_INVENTORY.md` §Frontend | Lines 2058 area: 61 routes + 5 workspace tabs + 9 betting tabs | NO API-module row (S2203 §14.2 F2 baseline VERIFIED at HEAD); NO REST-consumer count; NO typed-rate; NO cockpitApi reference. Autoblock candidate per S2500 §6 P-1 (deferred to S2599 xx99). |
| `docs/PLATFORM_WHAT_IT_IS.md` | Layer 9 Frontend section (routes only); Layer 4 mentions PA tools | Does NOT cover api.ts / typed contracts / silent-401 / CONSUMER-side contract discipline. Narrative subsection candidate per S2500 §6 P-1 + S2501 §20.5 deferred (S2599 xx99 close artifact candidate). |
| `docs/topics/api.md` | **DOES NOT EXIST at HEAD** — verified via Glob | S2500 §6 P-1 CREATE candidate; S2501 §19.3 R6 recast to xx99-close artifact candidate; Cat B RE-VERIFIES absence; deferred per S2501 §20.5. |

### 11.2 Predecessor research docs (already inventoried)

- `docs/research/domains/frontend/2203_frontend_api_contract_boundary_discipline_audit.md` — F1 SoT-ABSENT + F3 silent-401 SYSTEMIC + F3.5 whitelist BRITTLE + F4 6.85% typed + F5 drf-spectacular partial + F6 18 DEAD-CANDIDATE INTENT-NEUTRAL + §20.6 Path A/B/C triad. **PRIMARY predecessor for Cat B.**
- `docs/research/domains/frontend/2299_frontend_canonical_summary.md` — §5.1 canonical seam ("accreted UI mesh with declared-but-unenforced contracts") + §7.5 anchor updates + §8.2 T2 Group 2500 API cross-arc handoff bundle + §8.3 maintainer-decision batch + §8.4 T2 R6 error-boundary framework.
- `docs/research/domains/auth/2404_frontend_integration_silent_401_systemic_resolution_audit.md` — F-D-CALL-1 803-classification + F-D-BYPASS-1 79-raw-fetch NEW HIGH + F-D-ENVELOPE-1 zero typed AxiosError + F-D-BOUNDARY-1 zero error boundaries + F-D-WHITELIST-1 brittle substring + F-D-OWN-1 CODEOWNERS.
- `docs/research/domains/api/2500_api_domain_scoping.md` — §3.B Cat B mission + §5 sequence + §6 P-1 through P-11 parked items.
- `docs/research/domains/api/2501_api_backend_contract_sot_design_prep_audit.md` — SIBLING Cat A DECLARATION-side; F1 drf-spectacular disconnected + F6 FOUR-shape 401 heterogeneity + 96 Serializer + 91 ModelSerializer + 16.2% model→serializer coverage + 3-slice API-slice manifest.

### 11.3 Handoffs

- S1505 baseline: first "no API contract SoT" observation. S2203 first dedicated audit. No intervening handoff documents api.ts structural design.
- Session-annotation stream in api.ts itself (comment tags `// Session NNN: ...`): Session 802 (timeout), Session 819 (withCredentials + silent-401 delegation), Session 884 (homeApi added), Session 968 (request-log). Cat B does NOT enumerate every session-annotation; it exists in the file for git-log historical navigation.

### 11.4 Gap statement (Rigby SIGN-preview candidate for adoption)

Existing documentation COVERS: 93 apiModule inventory, 6.85%/7.36% typed rate, cockpitApi as typed-island exemplar, drf-spectacular PARTIAL-WIRED, silent-401 SYSTEMIC ~630 call-sites (S2203) then 803 (S2404) classification, 18 DEAD-CANDIDATE modules, S2501 F6 4-shape 401 heterogeneity, S2404 F-D-CALL-1 803 classification, S2404 F-D-BYPASS-1 79-raw-fetch.

Existing documentation DOES NOT COVER: (i) how frontend clients SHOULD enforce API contracts at consumption time; (ii) typed API client codegen adoption path (openapi-typescript / orval / kubb feasibility-only per S2500 §7 anti-scope #7); (iii) cockpitApi-as-exemplar extraction guidance; (iv) api.ts domain-scoping ownership map; (v) client-side error boundaries + UX policy for API failures; (vi) per-surface consumption discipline baseline (Workspace / Betting / Command Center / PA / Neural Orchestra / Revenue / Advisor); (vii) apiModule CODEOWNERS refinement (cockpitApi + hooks/ UNASSIGNED per CODEOWNERS lines 8–13 deferral).

## 12. Research Coverage

**Playbook §12 classifications: NONE / LIGHT / MODERATE / DEEP / CANONICAL.**

Cat B assesses the CONSUMER-side surface research coverage at HEAD:

| Sub-surface | Classification | Rationale |
|---|---|---|
| api.ts as mega-module | **MODERATE** | S2203 first dedicated audit; S2404 extended with 803-classification; S2501 handed DECLARATION-side. Coverage exists but design-prep still Cat B-in-progress. |
| cockpitApi.ts typed island | **LIGHT-TO-MODERATE** | S2203 §5.1 named + §6.2 documented; no dedicated exemplar-guidance doc. |
| hooks/cockpitQueries.ts React Query surface | **LIGHT** | Only briefly named in S2203; no per-hook typing / TError adoption analysis. S2404 §20.3 U1 explicitly UNKNOWN. |
| Raw-fetch bypass (79 sites, 31 files) | **LIGHT** | S2404 F-D-BYPASS-1 identified + noted; per-site classification (auth-required-vs-public + credentials-mode + response-type) deferred per S2404 §19.3 item 2b. |
| Per-surface consumption discipline (Workspace / Betting / etc.) | **LIGHT** | Agent 4 mapping is first CONSUMER-side surface-to-module cross-reference at S2502; not previously enumerated. |
| Error boundary + UX policy | **NONE** | Zero adopted at HEAD; S2299 §8.4 T2 R6 gate on T1/T2 execution; Cat B does NOT design (Cat C S2503 α/β/γ mechanism gates R6). |
| Codegen tooling adoption path | **LIGHT** | S2203 §20.6 Path A/B/C triad names openapi-typescript / orval / kubb; S2500 §7 anti-scope #7 = feasibility-only; Cat B collects boundary evidence but does not prescribe. |

**Overall CONSUMER-side research coverage at HEAD: MODERATE at inventory + DECLARATION-side inheritance, LIGHT at CONSUMER-side architectural design-prep.** Cat B is the natural OWNER of the CONSUMER-side design-prep boundary evidence; S2599 xx99 Chris-D-verdict-request evidence is the natural NEXT step.

## 13. Architecture Maturity

**Playbook §12 classifications: EXPERIMENTAL / PARTIAL / WORKING / STABLE / CANONICAL.**

| Artifact | Maturity | Evidence |
|---|---|---|
| **api.ts (mega-module)** | **PARTIAL** | 4194 LOC + 93 apiModule + 47 interfaces + 856 methods FROZEN 5 sessions. Brittle-substring whitelist for silent-401 UNCHANGED at api.ts:50. SHAPE-BLIND to S2501 F6 4-shape 401 heterogeneity. 7.36% typed rate. Neither STABLE (design boundaries not agreed) nor WORKING (silent-401 SYSTEMIC + shape-blind is design limitation, not just implementation gap). |
| **cockpitApi.ts (typed island)** | **WORKING** | 513 LOC + 54 functions + 96% typed rate + hand-written 104 types in `types/cockpit.ts` + Session-968 provenance + inherits shared axios instance discipline. Working exemplar of typed-client discipline; not CANONICAL because pattern is not documented as adoption guidance + not scaled beyond cockpit surface. |
| **hooks/cockpitQueries.ts (React Query wrap)** | **WORKING** | 42 hooks wrap cockpitApi 100%. Inherits 96% typed rate. Sensible refetchInterval + queryKey conventions. Not CANONICAL because TError generic adoption ≤1% per S2404 §20.3 U1. |
| **apiClient.ts (X-UI-Scope helper)** | **STABLE** | ~20 LOC + Session 968 provenance + zero-independent-interceptor + zero-drift 5 sessions. Small surface + clear responsibility + inherits shared instance. STABLE at Cat B scope. |
| **Raw-fetch bypass (79 sites, 31 files)** | **EXPERIMENTAL** | Zero interceptor + zero token attach + zero 401 catch + zero type discipline + zero centralized ownership. Neither controlled nor governed; per-site classification UNKNOWN at HEAD. |
| **Overall CONSUMER surface** | **PARTIAL** | Aggregate: WORKING at cockpit typed island; PARTIAL at api.ts mega-module; EXPERIMENTAL at raw-fetch bypass. 5-session zero-drift signals FROZEN posture rather than active governance. |

**Cat B boundary observation for xx99 Chris-D-verdict-request:** the WORKING classification for cockpitApi + hooks/cockpitQueries.ts is a POSITIVE existence-proof that typed-client discipline is FEASIBLE on this platform + this stack. The PARTIAL classification for api.ts is CONFIRMED by the shape-blind interceptor + 91-module bare-call pattern. The EXPERIMENTAL classification for raw-fetch is CONFIRMED by absence of any governance mechanism. Path A/B/C decision at xx99 must reconcile these three coexisting maturity tiers.

## 14. Known Drift

**Playbook §9 canonical Q26 — What drift exists between docs and runtime?**

### 14.1 F1 — Mega-module structural baseline UNCHANGED at HEAD (S2203 §14 F4 RE-VERIFIED)

**Predecessor claim (S2203 §14 F4):** api.ts mega-module 4194 LOC + 93 apiModule + 47 exported interfaces + 856 method defs.

**Cat B verifier at HEAD `548f53a1`:**
- `wc -l frontend/src/lib/api.ts` = **4194** (identical).
- `^export const \w+Api\s*=` grep = **93** matches (identical).
- `^export (interface|type) \w+` grep = **47** matches (identical).
- `api\.(get|post|put|delete|patch)\(` internal grep in api.ts = **856** matches (identical).
- Repo-wide grep total = **913 across 21 files** (identical).

**Delta:** ZERO across 5 sessions since S2404 close (HEAD `31398008`). ZERO across ~5 sessions since S2203 close.

**Class:** `observation` (structural baseline STABLE). Severity: LOW at the drift level; MED-HIGH at the maturity signal (accretion / churn frozen at these numbers is a positive design signal OR a stagnation signal depending on interpretation — Cat B does NOT verdict; xx99 Chris-D-verdict-request evidence).

### 14.2 F2 — Typed-rate delta at HEAD is mechanical (Rigby SIGN cycle 1 batch 1 Q3 STRENGTHEN — RELOCATED headline metric out of §1 primary narrative; retained here as sanity metric with explicit numerator-unchanged callout)

**Predecessor claim (S2203 §14 F4):** 63 typed / 919 total = 6.85% typed rate in api.ts.

**Cat B verifier at HEAD:**
- `api\.\w+<` internal grep = **63** matches (identical numerator).
- `api\.\w+\(` internal grep = **856** matches (denominator DECREASED from 919; delta = method cleanup).
- **Rate: 63/856 = 7.36%** at HEAD.

**Delta:** +0.51pp mechanical drift due to denominator decrease. Numerator (63 typed calls) UNCHANGED.

**Class:** `observation` (mechanical rate arithmetic without qualitative shift). Severity: LOW.

**Cat B explicit non-progress statement (Rigby SIGN cycle 1 batch 1 Q3 fold — numerator-unchanged callout):** the 7.36%-vs-6.85% delta is NOT a typed-adoption improvement; it is a method-cleanup artifact with typed-numerator held constant at 63. This finding is retained as a sanity metric only; it is EXCLUDED from the §1 headline narrative per Rigby's fold recommendation to prevent reader conflation of mechanical drift with governance progress.

### 14.3 F3 — SHAPE-BLIND silent-401 interceptor (KEY VERIFIER FINDING; NEW at Cat B, extends S2203 §14 F3 with S2501 F6 downstream)

**Predecessor claims combined:**
- S2203 §14 F3: silent-401 SYSTEMIC across ~630 call-sites (grep-based estimate hedged for wrapper duplicates per Rigby SIGN cycle 1 Q14 STRENGTHEN).
- S2404 §14.5: 803 consumer classification (57 direct + 667 hook + 79 raw fetch); ~99% silent-degrade rate; 90.2% interceptor coverage.
- S2501 §14.6 F6: FOUR co-existing 401 shape families at HEAD (DRF default + APIResponseEnvelope + bare DRF dict + non-DRF JsonResponse string).

**Cat B extension at HEAD:** the response interceptor at `frontend/src/lib/api.ts:43–62` is **SHAPE-BLIND**. It reads only `error.response?.status === 401` (not body) and branches only on `url.includes('/auth/') || url.includes('/login')`. All four S2501 F6 shape families flow through the SAME non-auth reject-and-console.warn branch. The whitelist substring UNCHANGED at api.ts:50 (Cat B RE-VERIFIED via Agent 2 direct read).

**Cat B boundary observation (Rigby SIGN cycle 1 batch 1 Q2 STRENGTHEN + batch 4 Q17 fold — dependency language guardrail added to prevent Cat B "smuggling" Cat C policy):** Cat C S2503 typed-error-envelope α/β/γ mechanism design-prep MAY depend on this: if a typed envelope adoption path requires shape-normalization landing first as a gating prerequisite, then any envelope contract cannot flow through to component-level catch blocks even if the backend adopts a canonical shape — because the interceptor at api.ts:43–62 will pre-empt the envelope with its own shape-blind reject path. This dependency is _assumed / gating hypothesis_ from Cat B's boundary perspective; Cat C S2503 owns the final α/β/γ mechanism design and may or may not require shape-normalization first. Cat B does NOT assert the dependency as fact.

**Class:** `technical_debt` (structural — shape-blind observer at consumer boundary) + `drift` (interceptor discipline lags Cat A backend heterogeneity documentation).

**Severity (Rigby SIGN cycle 1 batch 1 Q2 STRENGTHEN — CRITICAL uplift is CONDITIONAL on Cat C dependency):**

- **HIGH baseline** at consumer-observability impact (independent of Cat C dependency; shape-blind observer at consumer boundary is a HIGH structural debt on its own merits).
- **CRITICAL conditional** _if_ Cat C S2503 requires shape-normalization landing first as a gating prerequisite for typed-envelope mechanism adoption. In that case F3 becomes a platform-level gating defect. This CRITICAL classification is CONDITIONAL — Cat B does NOT declare it unconditional per Rigby SIGN cycle 1 batch 4 Q17 fold (highest-risk misinterpretation = unconditional CRITICAL framing).

Cat B boundary observation; remediation policy belongs to Cat C S2503 + Cat D S2504.

### 14.4 F4 — 18 DEAD-CANDIDATE apiModules ALL zero-consumer at HEAD (S2203 §14 F6 RE-VERIFIED)

**Predecessor claim (S2203 §14 F6):** 18 verifier-confirmed DEAD-CANDIDATE apiModules (INTENT-NEUTRAL; delete-proof requires MANDATORY intent-statement per Rigby SIGN cycle 1 Q15 STRENGTHEN).

**Cat B verifier at HEAD** via Agent 3 per-module grep of `\bXxxApi\.` across `frontend/src/**/*.{ts,tsx}` excluding api.ts:

| Module | Line | Consumers at HEAD | Status |
|---|---|---|---|
| nervousApi | 2144 | 0 | DEAD-CANDIDATE CONFIRMED |
| skinApi | 2122 | 0 | DEAD-CANDIDATE CONFIRMED |
| spineApi | 1925 | 0 | DEAD-CANDIDATE CONFIRMED |
| muscularApi | 2072 | 0 | DEAD-CANDIDATE CONFIRMED |
| circulatoryApi | 1894 | 0 | DEAD-CANDIDATE CONFIRMED |
| digestiveApi | 2042 | 0 | DEAD-CANDIDATE CONFIRMED |
| brainApi | 2103 | 0 | DEAD-CANDIDATE CONFIRMED |
| immuneApi | 1987 | 0 | DEAD-CANDIDATE CONFIRMED |
| agentOrchestrationsApi | 188 | 0 | DEAD-CANDIDATE CONFIRMED |
| autonomousApi | 2462 | 0 | DEAD-CANDIDATE CONFIRMED |
| classificationApi | 538 | 0 | DEAD-CANDIDATE CONFIRMED |
| ecosystemApi | 626 | 0 | DEAD-CANDIDATE CONFIRMED |
| legacyLearningApi | 1494 | 0 | DEAD-CANDIDATE CONFIRMED |
| journeyApi | 2546 | 0 | DEAD-CANDIDATE CONFIRMED |
| researchApi | 840 | 0 | DEAD-CANDIDATE CONFIRMED |
| workspaceTriggerConfigsApi | 1783 | 0 | DEAD-CANDIDATE CONFIRMED |
| integrationHealthApi | 2711 | 0 | DEAD-CANDIDATE CONFIRMED |
| llmApi | 1811 | 0 | DEAD-CANDIDATE CONFIRMED |

**Delta:** ZERO refutations across all 18 at HEAD.

**Class:** `dead_code`-DEAD-CANDIDATE INTENT-NEUTRAL (per S2203 §14 F6 delete-proof discipline). Severity: LOW-MEDIUM (hygiene + documentation debt; no runtime risk).

**Cat B boundary observation:** delete-proof requires triad with INTENT-STATEMENT MANDATORY per S2203 Rigby SIGN cycle 1 Q15 STRENGTHEN. Cat B does NOT prescribe removal; post-arc maintainer-decision batch per S2299 §8.3 owns.

**5-session persistence governance-signal note (Rigby SIGN cycle 1 batch 2 Q6 STRENGTHEN):** persistence across 5 sessions (S2404 baseline → S2502 HEAD, all 18 modules still zero-consumer) indicates a governance-stall signal (dead-weight ~2,700 LOC estimated at ~150 LOC average across the 18 modules per line-range sampling); removal remains maintainer-intent-gated per S2203 §14 F6 delete-proof triad. This signal is severity-neutral (does not elevate LOW-MEDIUM); it is a trajectory observation for xx99 Chris-D-verdict evidence.

### 14.5 F5 — 79-raw-fetch bypass IDENTICAL at HEAD (S2404 F-D-BYPASS-1 RE-VERIFIED)

**Predecessor claim (S2404 §14.5 + §16 F-D-BYPASS-1):** 79 raw `fetch()` calls across 31 files bypass axios interceptor entirely (no token attach + no 401 catch + relies on session cookie via `credentials: 'include'`).

**Cat B verifier at HEAD:** `fetch\(` grep = **79 matches across 31 files** (IDENTICAL).

**Delta:** ZERO across 5 sessions.

**Class:** `boundary_violation` (F-D-BYPASS-1 NEW HIGH per S2404 §16). Severity: HIGH baseline; Cat B RE-VERIFIED at HEAD.

**Cat B boundary observation:** Cat D S2504 post-arc T-slot owns per-site classification refinement (S2404 §19.3 item 2b: auth-required-vs-public + credentials-mode + response-type). Cat B does NOT prescribe migration policy.

### 14.6 F6 — Codegen tooling absence IDENTICAL at HEAD (S2203 §14 F5 partial RE-VERIFIED)

**Predecessor claim (S2203 §14 F5):** 0 codegen tools (openapi-typescript / orval / kubb / swagger-codegen); 0 runtime validation (zod / io-ts / valibot / superstruct / yup) in `frontend/package.json`.

**Cat B verifier at HEAD:** All 9 libraries confirmed ABSENT per Agent 4 verified grep on `package.json`.

**Delta:** ZERO across 5 sessions.

**Class:** `technical_debt` (structural — pattern-support tooling absent).

**Cat B boundary observation:** S2500 §7 anti-scope #7 explicitly forbids codegen framework selection at Group 2500 arc. Cat B collects feasibility-adjacent evidence only; Chris-D-verdict at S2599 xx99 or post-arc ADR.

### 14.7 F7 — S2404 F-D-OWN-1 CLOSED (partial-scope) at HEAD (Rigby SIGN cycle 1 batch 2 Q8 STRENGTHEN — split from single "PARTIAL-REMEDIATED" finding into F7 CLOSED + F8 NEW to preserve remediation progress signal while surfacing live gap)

**Predecessor claim (S2404 F-D-OWN-1):** CODEOWNERS absent at all three canonical locations (.github/, root, docs/).

**Cat B verifier at HEAD:** CODEOWNERS EXISTS at repo root (`./CODEOWNERS`, 48 lines). `/frontend/src/lib/api.ts @clwest` declared explicitly at line 31. `authStore.ts` + `Sidebar.tsx` + `App.tsx` explicit at lines 32–34.

**Class:** `observation` — S2404 F-D-OWN-1 original absence-defect (scope: any CODEOWNERS declaration at all) is **REMEDIATED (partial-scope) at HEAD** per S2499 AU-D5 anchor-update. api.ts + authStore.ts + Sidebar.tsx + App.tsx have explicit @clwest declaration.

Severity: NONE at this finding (it is a closure).

### 14.8 F8 — CODEOWNERS coverage gap: cockpit/hooks/types UNASSIGNED at HEAD (NEW finding split from F7 per Rigby SIGN cycle 1 batch 2 Q8 STRENGTHEN)

**Cat B verifier at HEAD:** `cockpitApi.ts` + `apiClient.ts` + `hooks/` (glob) + `hooks/cockpitQueries.ts` + `types/` (glob) + `types/cockpit.ts` all UNASSIGNED per CODEOWNERS (fall to `*` default per line 18; no explicit entry).

**CODEOWNERS lines 8–13 EXPLICIT DEFERRAL COMMENT (verbatim):**

> "Cross-arc typed-error-envelope + whitelist-replacement ownership remains UNASSIGNED at Group 2400 close; will be reassigned at T2 Group 2500 API arc.
> Frontend-specific ownership (api.ts + authStore.ts + Sidebar.tsx) refined at S2600+ per Group 2200 T-slot maintainer-decision batch."

Cat B RE-VERIFIES the deferral is still in place at HEAD — no incremental refinement in 5 sessions.

**Class:** `technical_debt` (governance-class; declared-deferral gap with material downstream cost). Severity: LOW at HEAD (sole-operator context per S2201 §14 rationale); becomes MEDIUM at the moment a second contributor joins the cockpit surface.

**Cost-of-deferral note (Rigby SIGN cycle 1 batch 3 Q15 fold — cost quantification without prescription):** unassigned cockpit surface ownership extends review latency and allows drift/defects (e.g., silent-401 behavior in cockpitQueries.ts hooks + typed contract drift in types/cockpit.ts) to persist across sessions without a formal review-and-approve gate. Cat B does NOT recommend reassignment; the deferral to S2600+ is DECLARED-INTENTIONAL per CODEOWNERS lines 8–13; the cost-of-deferral is documented here as Chris-D-verdict-request evidence for xx99 or S2600+ maintainer-decision batch review.

## 15. Known Technical Debt

**Playbook §9 canonical Q23 — What technical debts exist?**

**Top-5 Cat B Observability Risks (ranked by CONSUMER-observability impact; label renamed from "technical debt" to "Observability Risks" per Rigby SIGN cycle 1 batch 1 Q5 STRENGTHEN fold — allows rank-1 meta-observation to coexist with concrete debts under a unified taxonomy without violating Cat A "concrete contract/observability debt only" precedent; non-prescriptive per Cat A precedent):**

1. **5-session drift-frozen consumer surface** (F1 F4 F5 F6 RE-VERIFIED). 4194 LOC + 93 apiModule + 47 interfaces + 803 consumer sites + 79-raw-fetch UNCHANGED at HEAD; codegen tooling ABSENT; error-boundary framework ABSENT. **Trajectory / Governance Signal**: either governance discipline holding OR accretion stall + no owner pushing changes. Cat B boundary observation; framing interpretation belongs to S2599 xx99 Chris-D-verdict.

2. **SHAPE-BLIND silent-401 interceptor** (F3 NEW). api.ts:43–62 treats all four S2501 F6 shape families identically. **Blocks Cat C α/β/γ typed-error-envelope adoption path IF Cat C requires replacement interceptor to land first** (dependency assumed / gating hypothesis; not asserted as fact per Rigby SIGN cycle 1 batch 4 Q17 language guardrail). Cat B boundary observation; remediation policy Cat C S2503.

3. **api.ts 4194-LOC mega-module** (F1 RE-VERIFIED). Domain-scoping and per-module ownership are not declared. **platformApi 663-LOC sub-monolith at api.ts:3257–3920 (~7.1% of api.ts total) is a concrete internal pressure point / extraction candidate exemplar of the mega-module pattern** (Rigby SIGN cycle 1 batch 3 Q14 fold — kept as sub-observation under F1, not spun to distinct finding, to prevent double-counting the same root cause). Extraction debt; blast radius per S2203 §14 F4 = ~1,417 method definitions + 47 orphan interfaces + 407-session churn. Cat B boundary observation; extraction path Chris-D-verdict at xx99.

4. **79-raw-fetch bypass parallel-untyped-surface** (F5 F-D-BYPASS-1 RE-VERIFIED). 9.8% of frontend HTTP surface operates outside the interceptor; zero token attach; zero 401 catch; per-site classification UNKNOWN. Not a wrapper-duplicate; a contract-bypass. Cat B boundary observation; per-site classification Cat D S2504 post-arc T-slot.

5. **91-of-93 apiModule bare-call pattern + 47 exported interfaces mostly-orphan** (F1 F2 F6 combined). Only cockpitApi (96%) + platformApi (inline generics, ~100% on ~30 methods) + assistantApi (partial: paChat/paChatStatus typed) have any typed discipline. 47 exported interfaces have ~6–20% orphan rate at sample; consumer components either inline-declare `interface *Response` at call-sites (S2203 §15.6) or use `.data as SomeType` type-assertion. Cat B boundary observation; typing-adoption Path A/B/C Chris-D-verdict at xx99.

**Cat B boundary discipline preservation:** risks observed + ranked by CONSUMER-observability impact; NOT recommendation at any item. Chris-D-verdict-request at S2599 xx99 close after all 4 children contribute evidence.

## 16. Boundary Violations

**Playbook §9 canonical Q24 — What boundary violations exist?**

**Cat B boundary observation** (mirror Cat A precedent per §14.6 fold): at HEAD the CONSUMER-side contract discipline is largely NOT DECLARED (per §14 F3 + F5 + F6), so "boundary violation" is a less useful frame than "missing / undeclared consumer contract discipline" — Cat D S2504 may still classify specific items as violations depending on enforcement mechanisms.

**Two-level frame (Rigby SIGN cycle 1 batch 3 Q13 STRENGTHEN — logic-tightening fold that preserves the "missing/undeclared" primary posture while acknowledging the implicit-contract exception):** some CONSUMER-side boundaries are implicitly declared even in the absence of formal spec. The interceptor chain at api.ts:13–62 + api.ts:3990–4048 functions as an **implicit boundary** — the architectural convention (repeated in doc + code comments + Session-968 provenance) is "all HTTP requests route through the shared axios instance + interceptor chain". The 79-raw-fetch surface (§14.5 F5 F-D-BYPASS-1 RE-VERIFIED) constitutes a **concrete bypass of that implicit contract**. Two-level classification:

- **Level 1 (primary posture):** formal CONSUMER-side contracts are not declared (typed-response envelope shape, error handling contract, response validation) — "boundary violation" frame under-applies.
- **Level 2 (implicit-contract exception):** the interceptor chain IS an implicitly-declared boundary; 79-raw-fetch violates it. This is a concrete boundary violation at the implicit level, distinct from missing formal contracts.

**Adjacent boundary violation candidates observed but not owned by Cat B:**

- **F-D-SIDEBAR-1 (S2404 §16):** Sidebar logout at `frontend/src/components/layout/Sidebar.tsx:356` clears authStore but does not call `authApi.logout()`. Frontend-symptom-vs-backend-model boundary violation; Cat D S2504 findings-appendix per S2500 §3.D or post-arc T-slot per S2404 §19.2 P0-B.
- **F-D-BYPASS-1 (S2404 §16):** 79 raw fetch() calls violate the "all HTTP requests route through interceptor" implicit contract. Cat B RE-VERIFIED; Cat D S2504 post-arc T-slot owns per-site classification.
- **F-C-COCKPIT-1 (S2404 §16):** 16 cockpit `<Navigate>` at App.tsx:134–149 NOT wrapped by ProtectedRoute (S2404 baseline STILL-LIVE at HEAD per Agent 6 spot-check). Cross-arc navigation-guard boundary; Group 2200 post-arc R5 cockpit-retirement decision Chris-gated per S2201 baseline.

Cat B boundary: NOT OWNED at CONSUMER surface directly; adjacent to F-D-BYPASS-1 which Cat B RE-VERIFIED at §14.5 F5.

## 17. Duplicate or Overlapping Systems

**Playbook §9 canonical Q25 — What duplicate or overlapping systems exist?**

**Cat B verifier at HEAD:**

1. **Zero axios wrapper duplication** (S2404 §17 preservation VERIFIED at HEAD). Single `api = axios.create({...})` instance at `frontend/src/lib/api.ts:13`. `cockpitApi.ts` + `apiClient.ts` re-use shared `api` instance; no independent interceptor.

2. **cockpitApi vs api.ts vs apiClient.ts co-existence** — NOT DUPLICATE. Three distinct responsibilities:
   - api.ts: shared axios instance + interceptor stack + 93 apiModule bare-call pattern.
   - cockpitApi.ts: typed-island wrapper with explicit `<T>` generics + response destructuring + typed imports from `types/cockpit.ts`.
   - apiClient.ts: X-UI-Scope scoped-header helper (Session 968 request-log filtering).
   
   Cat B boundary observation: three-file layering is a natural extraction seam. cockpitApi.ts + apiClient.ts are CANDIDATES for the eventual api.ts extraction pattern (per S2299 §8.3 maintainer-decision batch item 3: "api-module extraction + cross-cutter documentation"). Cat B does NOT prescribe.

3. **REST + WS transport parallel** (T7 cross-arc flag). 8 WS subscription sites + 803 REST consumer sites operate in parallel with 2 explicit HYBRID surfaces (pa/conversations + dashboard). NOT DUPLICATE; two disjoint transports for related concerns. T7 joint owned by Cat D S2504 + Group 2600 PA co-authorship.

4. **79-raw-fetch = parallel untyped surface** (NOT DUPLICATE per S2404 §17 non-classification precedent — "not a wrapper-duplicate, it is a contract-bypass"). 9.8% of HTTP surface operating outside interceptor. Cat B RE-VERIFIED at §14.5 F5.

5. **platformApi as nested-monolithic apiModule inside api.ts mega-module.** 663 LOC at api.ts:3257–3920 = 7.1% of api.ts total. Uses inline-anonymous-typed-response pattern (third pattern between cockpitApi typed-island and bare api). NOT DUPLICATE; a MICRO-MONOLITH inside the MEGA-MONOLITH. Cat B boundary observation; extraction candidate at post-arc T-slot.

## 18. Ownership Gaps

**Playbook §9 canonical Q27 — What ownership gaps exist?**

CODEOWNERS at HEAD (established S2499 Group 2400 Auth arc AU-D5 per Cat D F-D-OWN-1 remediation; file exists at `./CODEOWNERS` at repo root; 48 lines):

- **Default:** `* @clwest` (sole operator per line 18).
- **Explicitly declared for Cat-B-adjacent surfaces:**
  - `/frontend/src/lib/api.ts @clwest` (line 31).
  - `/frontend/src/stores/authStore.ts @clwest` (line 32).
  - `/frontend/src/components/layout/Sidebar.tsx @clwest` (line 33).
  - `/frontend/src/App.tsx @clwest` (line 34).

**UNASSIGNED at Cat B boundary (fall to `*` default):**
- `/frontend/src/lib/cockpitApi.ts` — Cat B primary typed-island exemplar. NO explicit entry.
- `/frontend/src/lib/apiClient.ts` — X-UI-Scope helper. NO explicit entry.
- `/frontend/src/lib/*.ts` (glob) — NO glob entry for lib/.
- `/frontend/src/hooks/cockpitQueries.ts` — 42 React Query hooks. NO explicit entry.
- `/frontend/src/hooks/` (glob) — NO glob entry for hooks/.
- `/frontend/src/types/cockpit.ts` — 104 hand-written types. NO explicit entry.
- `/frontend/src/types/` (glob) — NO glob entry for types/.

**CODEOWNERS lines 8–13 EXPLICIT DEFERRAL COMMENT (verbatim):**

> "Cross-arc typed-error-envelope + whitelist-replacement ownership remains UNASSIGNED at Group 2400 close; will be reassigned at T2 Group 2500 API arc.
> Frontend-specific ownership (api.ts + authStore.ts + Sidebar.tsx) refined at S2600+ per Group 2200 T-slot maintainer-decision batch."

**Severity:** LOW at HEAD (sole-operator context per S2201 §14 rationale + S2404 §18 F-D-OWN-1 partial-close). Becomes MEDIUM at the moment a second contributor joins the cockpit surface. **Cat B boundary observation:** the cockpit ownership deferral is DECLARED (not accidental); Cat B RE-VERIFIES the deferral is still in place at HEAD — no incremental refinement in 5 sessions. Post-arc CODEOWNERS refinement batch T-slot per S2299 §8.3 maintainer-decision batch item 5 owns.

**Cost-of-deferral operational note (Rigby SIGN cycle 1 batch 3 Q15 STRENGTHEN — cost quantification without prescription):** unassigned cockpit surfaces extend review latency + allow drift/defects (e.g., silent-401 behavior in cockpitQueries.ts hooks + typed contract drift in types/cockpit.ts) to persist across sessions without a formal review-and-approve gate. Cross-reference §14.8 F8 for cost-of-deferral evidence. Cat B does NOT recommend reassignment (per Rigby SIGN cycle 1 batch 3 Q15 fold preservation of Cat B non-prescription discipline); the deferral to S2600+ is DECLARED-INTENTIONAL per CODEOWNERS lines 8–13. Cost is expressed as risk + time-to-fix drag, not as a directive.

## 19. Future Research — Chris-D-verdict-request evidence (non-prescriptive)

**Playbook §9 canonical Q28 — What should be researched next?**

**Cat B boundary discipline note (mirror Cat A §19 fold):** section labeled "Future Research — Chris-D-verdict-request evidence (non-prescriptive)" to preempt "Cat B recommends" misread. Tiers below are decision candidates / evidence prompts, NOT recommendations. Cat B collects evidence for future Chris-D-verdicts; Cat B does NOT recommend implementation.

Ranked by architectural uncertainty × risk × unblocked flows per playbook §19.

### 19.1 CRITICAL tier — evidence collected for S2599 xx99 close

**R1 — [S2599 xx99 close Chris-D-verdict-request] CONSUMER-side typed-client adoption Path A/B/C.** Cat B boundary evidence: 93 apiModule + 47 exported interfaces + 6.85%→7.36% typed rate + cockpitApi 96% typed-island exemplar + 0 codegen tooling in package.json + platformApi inline-typed-generic third pattern + hooks/cockpitQueries.ts 42-hook typed-inheritance surface. This is Chris-D-verdict-request evidence for the CONSUMER-side of the S2203 §20.6 Path A/B/C triad; consumer-side complements DECLARATION-side Path selection from Cat A F1:

- **Path A (Full-spectrum)** — Adopt openapi-typescript / orval codegen for all 93 apiModules; retrofit consumer components to typed responses; blast radius LARGE.
- **Path B (Money-path/integrity-critical only)** — Extend cockpitApi typed-island discipline to money-path modules (bettingApi, billingApi, portfolioApi, humanApi decision-path) — ~10-15 modules; BOUNDED blast radius.
- **Path C (Middle-ground)** — Typed discipline mandatory for money/governance/state-changing modules; lighter for read-only/display-only; per-endpoint by "authoritative-state-mutation?" axis.

**Explicit independence statement (Rigby SIGN cycle 1 batch 3 Q12 STRENGTHEN):** CONSUMER-side adoption Paths A/B/C are **INDEPENDENT** of DECLARATION-side (Cat A S2501 §19.1 R1) Path selection strategy; mixed combinations are valid (e.g., backend Path C decorator scope + frontend cockpitApi-extension Path B + zod-adoption on money-path only). Reader should NOT assume coupling between the two triads even though the axes share A/B/C labels for symmetry. xx99 close synthesizes both triads but does not pre-couple them.

Cat B boundary preserved: Cat B does NOT recommend Path A/B/C verdict; Cat B provides EVIDENCE for the Chris-D-verdict at S2599 xx99 close.

**Cat B enumerates axes only; Cat C owns selection** (Rigby SIGN cycle 1 batch 3 Q11 fold — explicit non-verdict qualifier).

**R2 — [S2599 xx99 close Chris-D-verdict-request] SHAPE-BLIND interceptor replacement decision-point.** Cat B evidence per §14.3 F3 KEY VERIFIER FINDING: the interceptor at api.ts:43–62 is shape-blind to S2501 F6 4-shape 401 heterogeneity. Cat C S2503 typed-error-envelope α/β/γ adoption depends on this. Three sub-questions Cat C must answer at S2503 (Cat B collects evidence):

- (i) Does a shape-aware interceptor land BEFORE typed-envelope mechanism, or DOES THE TYPED-ENVELOPE MECHANISM LAND FIRST as the shape-normalizer?
- (ii) Does the request-log ring buffer (api.ts:3990–4048) become the client-side telemetry origin for typed-envelope success/failure metrics?
- (iii) Does whitelist substring replacement (S2404 F-D-WHITELIST-1) happen inside shape-aware interceptor OR as an independent step?

Cat B boundary preserved: Cat B does NOT recommend order; evidence handed to Cat C S2503.

**R3 — [S2599 xx99 close Chris-D-verdict-request] 79-raw-fetch bypass reconciliation options.** Cat B evidence: 79 raw fetch() sites across 31 files IDENTICAL at HEAD to S2404 baseline; 5 sessions no migration. Three-option decision-space (from S2404 §19.3 item 2b):

- **(a) migrate fetch → api conversions per-site** — reduce bypass surface to 0; requires per-site classification (auth-required vs public vs SSE vs streams vs non-JSON payload) first.
- **(b) global fetch wrapper at api-boundary layer** — intercept fetch at wrapper layer + apply same interceptor stack; requires monkey-patch or ambient module augmentation.
- **(c) leave as-is** — accept 9.8% invisible surface; document as anti-scope; Cat D S2504 post-arc T-slot per-site classification.

Cat B boundary preserved.

### 19.2 HIGH tier — evidence for S2503 Cat C + S2504 Cat D

**R4 — [S2503 Cat C boundary evidence] SHAPE-BLIND interceptor at api.ts:48–56 is the consumer-side attach point for typed-error-envelope adoption.** Cat B boundary evidence for Cat C α/β/γ mechanism design-prep (Cat C β = message/UX policy nested inside Cat D mechanism γ per S2404 Rigby Q6 fold). The four S2501 F6 shape families all flow through the same non-auth reject branch; whatever mechanism Cat C designs (RQ error callbacks + boundary + envelope discriminated-union) will require shape-normalization at this interceptor OR replacement of the interceptor as the first landing step.

**R5 — [S2504 Cat D boundary evidence] REST↔WS T7 joint contract inventory at HEAD.** Cat B evidence: 8 distinct WebSocket subscription sites at HEAD (5 specialized hooks + 2 generic + 1 dashboard) + 803 REST consumer sites operating in parallel + 2 HYBRID surfaces (pa/conversations REST-list-plus-WS-stream + HeartWidget dashboard WS-plus-implicit-REST). No shared cache; no cross-transport sync; no invalidation-hook link. Cat D S2504 T7 joint scope with Group 2600 PA co-authorship.

**R6 — [S2503 Cat C + S2504 Cat D + Group 2200 post-arc T-slot + S2299 §8.4 T2 R6 execution] Error-boundary framework prerequisite.** Cat B evidence: 0 `ErrorBoundary` / `componentDidCatch` / `getDerivedStateFromError` matches at HEAD. R6 error-boundary framework establishment per S2299 §8.4 T2 is a BLOCKING PREREQUISITE for Cat C typed-envelope γ mechanism per S2404 §9 CF-D5 ⚠ BLOCKING PREREQUISITE marker. Cat B RE-VERIFIES the zero-adoption baseline; Cat C S2503 owns the typed-error-envelope mechanism whose adoption depends on R6 landing; Cat D S2504 owns permission-floor whose downstream affects R6 rendering surface.

**R6 dual-ownership handoff (Rigby SIGN cycle 1 batch 3 Q11 STRENGTHEN):** R6 is both (a) a typed-envelope / shape-normalization prerequisite for Cat C AND (b) a broader cross-cutting **frontend error UX / global boundary framework** concern that historically lives well in Group 2200 post-arc "platform contract discipline" lane. Cat B explicitly hands to Group 2200 post-arc T-slot for "ErrorBoundary framework establishment / global error UX contract" AS WELL AS to Cat C S2503 as the typed-envelope prerequisite. R6 ownership is NOT exclusively Cat C. Cat B RECORDS the gap; Cat B does NOT prescribe framework design.

### 19.3 MEDIUM tier — evidence for S2599 xx99 anchor-update

**R7 — [S2599 xx99 close artifact candidate] `docs/topics/api.md` CREATE + PLATFORM_INVENTORY §API autoblock + PLATFORM_WHAT_IT_IS §API narrative subsection.** Cat B extends S2500 §6 P-1 + S2501 §19.3 R6 candidacy with CONSUMER-side evidence: 93 apiModule + 47 interfaces + 803 consumer sites + typed-rate + cockpitApi typed-island + 79-raw-fetch bypass + 4 primary cross-cutter + 18 DEAD-CANDIDATE + 8 WS subscription sites + SHAPE-BLIND interceptor. Analog to Group 2400 close `docs/topics/auth.md` + §Auth autoblock + narrative subsection per S2499 AU-D2 + AU-D7. Cat B boundary evidence supports the candidacy; Chris-D-verdict at S2599 xx99 close (proposal-only per S2500 §6 P-1). Doc-system owner (per S2499 AU-D5 CODEOWNERS `/docs/topics/ @clwest`) agrees at xx99 close before authoring commences.

**R8 — [S2599 xx99 close anchor-update recommendation] `platform_architecture_inventory.md` §3.22 API Layer REVISE (per Cat A §14.4 F4 + Cat B extension).** Cat A §14.4 F4 established §3.22 API Layer row EXISTS at STABLE + MODERATE posture; Cat B extends with CONSUMER-side sub-layer evidence: mega-module PARTIAL + typed-island WORKING + raw-fetch EXPERIMENTAL = overall PARTIAL. Cat A + Cat B combined revision candidate at S2599 xx99 anchor-update batch.

**R9 — [Post-arc T-slot maintainer-decision batch] api.ts domain-scoping ownership map + CODEOWNERS cockpit refinement.** Cat B extends S2299 §8.3 maintainer-decision batch item 3 (api-module extraction + cross-cutter documentation) with CONSUMER-side ownership evidence: cockpitApi.ts + apiClient.ts + hooks/cockpitQueries.ts + types/cockpit.ts UNASSIGNED at CODEOWNERS; explicit deferral to S2600+. platformApi 663-LOC nested monolith is extraction-candidate. Post-arc T-slot; maintainer-decision gate per S2299 §8.3 discipline (single review pass).

**R10 — [Post-arc T-slot maintainer-decision batch] 18 DEAD-CANDIDATE apiModule signoff.** Cat B RE-VERIFIES all 18 zero-consumer at HEAD; delete-proof requires INTENT-STATEMENT triad per S2203 §14 F6 Rigby SIGN cycle 1 Q15 STRENGTHEN. Post-arc T-slot; batch signoff before removal PR.

### 19.4 Boundary questions Cat B must NOT resolve (§16 anti-scope guardrails)

Cat B discovers scope-magnets; Cat B enumerates evidence only:

1. **Should openapi-typescript / orval / kubb be adopted for typed-client codegen?** Explicit S2500 §7 anti-scope #7; Cat B collects feasibility-adjacent evidence only.
2. **Should api.ts extract to per-domain module files?** Chris-D-verdict at S2599 xx99 close or post-arc T-slot per S2299 §8.3.
3. **Should the SHAPE-BLIND interceptor be replaced with a shape-aware envelope-normalizer?** Cat C S2503 α/β/γ mechanism scope; Cat B collects evidence.
4. **Should 79-raw-fetch migrate wholesale to api-modules?** Cat D S2504 post-arc T-slot per S2404 §17 + §19.3 item 2b.
5. **Should whitelist substring `url.includes('/auth/')` be replaced with explicit endpoint list or authHandling enum?** S2404 §19.1 α/β/γ decision-space; Cat D S2504.
6. **Should cockpitApi typed-island pattern extend to money-path modules (bettingApi, billingApi, portfolioApi)?** R1 Path A/B/C sub-question; Chris-D-verdict at xx99.
7. **Should platformApi 663-LOC monolithic apiModule sub-extract?** R9 post-arc T-slot.
8. **Should we migrate from `@tanstack/react-query` to a different data-fetching layer?** NOT in Cat B scope; classic framework-migration scope-magnet per S2500 §7 anti-scope pattern.

## 20. Appendix

### 20.1 Files inspected (HEAD-verified at `548f53a1`)

- `frontend/src/lib/api.ts` (4194 LOC) — full read of lines 1–100 (axios + interceptor + first apiModule) + strategic sample at 3255–3292 (platformApi head), 3900–3921 (platformApi tail + blogsApi head), 4187 (last apiModule).
- `frontend/src/lib/cockpitApi.ts` (513 LOC) — Agent 1 sample + Agent 2 pattern verification.
- `frontend/src/lib/apiClient.ts` (~20 LOC) — Agent 1 X-UI-Scope pattern verification.
- `frontend/src/types/cockpit.ts` (820 LOC) — Agent 1 composition survey (23 unions + ~81 interfaces).
- `frontend/src/hooks/cockpitQueries.ts` (485 LOC per Agent 6; 42 exported hooks per Agent 3) — Agent 3 hook enumeration + Agent 2 pattern verification.
- `frontend/src/hooks/useWebSocket.ts` — Agent 4 factory enumeration.
- `frontend/src/pages/**` — Agent 4 surface-to-module mapping (BettingPage, BillingPage, CommandCenterPage, AgentsPage, AnalyticsDashboardPage, AdvisorsPage, NeuralOrchestraPage, WorkspacePageNew, GovernmentPage, HeartWidget).
- `frontend/src/pages/workspace/tabs/**` — Agent 4 tab-consumer mapping.
- `CODEOWNERS` at repo root (48 lines) — Cat B ownership verifier direct read.
- `frontend/package.json` — Agent 4 codegen tooling absence verification.
- `docs/topics/frontend.md` — Agent 5 direct-coverage assessment (lines 1–148).
- `docs/PLATFORM_INVENTORY.md` — Agent 5 §Frontend row inspection.
- `docs/PLATFORM_WHAT_IT_IS.md` — Agent 5 API-mention survey.
- `docs/research/DOMAIN_RESEARCH_PLAYBOOK.md` — parent-Claude §11.2 20-section template + §13 6-parallel-Explore-sweep + §14 verifier-loop + §15 SIGN cadence + §16 draft-first workflow.
- `docs/research/domains/frontend/2203_frontend_api_contract_boundary_discipline_audit.md` — parent-Claude §14 F1/F3/F3.5/F4/F5/F6 + §20.6 Path A/B/C.
- `docs/research/domains/frontend/2299_frontend_canonical_summary.md` — parent-Claude §5.1 seam + §7 anchor updates + §8.2 T2 + §8.3 maintainer batch + §8.4 T2 R6.
- `docs/research/domains/auth/2404_frontend_integration_silent_401_systemic_resolution_audit.md` — parent-Claude §14.5 803 classification + §17 zero-axios-duplication + §18 F-D-OWN-1 + §20.2 grep patterns.
- `docs/research/domains/api/2500_api_domain_scoping.md` — parent-Claude §3.B Cat B mission + §5 sequence + §6 P-1 through P-11.
- `docs/research/domains/api/2501_api_backend_contract_sot_design_prep_audit.md` — parent-Claude §14.1 F1 + §14.5 F5 + §14.6 F6 + §15 top-5 debt + §18 CODEOWNERS + §19.1 R1 + §19.3 R5/R6.

### 20.2 Grep commands used (HEAD-verified via parent-Claude + Agent execution)

| Pattern | Path | Result at HEAD |
|---|---|---|
| `api\.(get\|post\|put\|delete\|patch)\(` | `frontend/src/` | 913 across 21 files (856 defs in api.ts; 57 direct consumer). IDENTICAL to S2404 baseline. |
| `api\.(get\|post\|put\|delete\|patch)\(` | `frontend/src/lib/api.ts` internal | 856 (VERIFIED matches expected denominator). |
| `useQuery\|useMutation` | `frontend/src/` | 667 across 74 files. IDENTICAL to S2404 baseline. |
| `fetch\(` | `frontend/src/` | 79 across 31 files. IDENTICAL to S2404 baseline. |
| `axios\.create\(` | `frontend/src/` | 1 match at `api.ts:13`. IDENTICAL to S2404 baseline. |
| `AxiosError\|axios\.isAxiosError` | `frontend/src/` | 0 matches (F-D-ENVELOPE-1 IDENTICAL). |
| `ErrorBoundary\|componentDidCatch\|getDerivedStateFromError` | `frontend/src/` | 0 matches (F-D-BOUNDARY-1 / R6 IDENTICAL). |
| `^export const \w+Api\s*=` | `frontend/src/lib/api.ts` | 93 matches. IDENTICAL to S2203 baseline. |
| `^export (interface\|type) \w+` | `frontend/src/lib/api.ts` | 47 matches. IDENTICAL to S2203 baseline. |
| `api\.\w+<` | `frontend/src/lib/api.ts` internal | 63 matches. IDENTICAL to S2203 baseline. |
| `api\.\w+<` | `frontend/src/lib/cockpitApi.ts` | 52 matches. IDENTICAL to S2203 baseline. |
| `Authorization` | `frontend/src/` | 1 match at api.ts:35. IDENTICAL to S2203 baseline (0 outside api.ts). |
| `Bearer ` | `frontend/src/` | 0 matches (Django TokenAuth prefix `Token ` used, not Bearer). |
| `openapi-typescript\|orval\|kubb\|swagger-codegen\|zod\|io-ts\|valibot\|superstruct\|yup` | `frontend/package.json` | 0 matches (all 9 libraries absent). IDENTICAL to S2203 baseline. |
| `CODEOWNERS` file location | filesystem | Exists at `./CODEOWNERS` (repo root); NOT `.github/CODEOWNERS`; NOT `docs/CODEOWNERS`. S2404 F-D-OWN-1 partially remediated by S2499 AU-D5. |
| Per-module `\bXxxApi\.` grep (18 DEAD-CANDIDATE list) | `frontend/src/**/*.{ts,tsx}` excluding api.ts | 0 consumers for all 18 modules. IDENTICAL to S2203 baseline. |

### 20.3 Docs inspected

Listed at §20.1.

### 20.4 Sampling completeness note (Rigby SIGN cycle 1 batch 2 Q10 STRENGTHEN — explicit hedge for enumeration methods that were targeted rather than exhaustive)

Cat B relied on 6-parallel-Explore sweeps + targeted samples per playbook §13; Cat B did NOT perform exhaustive `apiModule × consumer file` Cartesian grep. Specifically:

- **Exhaustive verified:** api.ts internal grep for `^export const \w+Api\s*=` (93), `^export (interface|type) \w+` (47), `api\.\w+\(` (856), `api\.\w+<` (63); repo-wide grep for `api\.(get|post|put|delete|patch)\(` (913), `useQuery|useMutation` (667), `fetch\(` (79), `axios\.create\(` (1), `AxiosError|axios\.isAxiosError` (0), `ErrorBoundary|componentDidCatch|getDerivedStateFromError` (0); package.json codegen library grep (0/9); CODEOWNERS file existence + entries; 18 DEAD-CANDIDATE per-module `\bXxxApi\.` grep.
- **Targeted (NOT exhaustive):** WS subscription surface enumeration (Agent 4 pattern set: `new WebSocket(`, `useWebSocket`, hook factory — 8 identified). Full enumeration may extend under `socket.io`, `useSubscription`, `channel.subscribe`, `ws://` / `wss://` literals — deferred to Cat D T7 joint at S2504. Sample per-module method-count divergence between Agent 1 + Agent 3 on ~10 modules (adopted conservative Agent 3 estimates + noted approximation). Inline `interface *Response` declarations at call-sites (S2203 §15.6 sampled ~12+; full count deferred).
- **Sampled + hedged:** typed-vs-orphan classification for the 47 exported types (Agent 1 spot-check n=15 + random 5-sample; ~6-20% orphan rate at sample; full-repo verification deferred).
- **Assumed (verified in prior sessions):** `Glob frontend/src/**/*.{js,jsx}` = 0 files (S2203 §20.4 baseline; if `.js`/`.jsx` files added since S2203 close, Cat B numeric baselines could shift — verifier assumed absence at HEAD without re-glob).
- **Not-in-scope-verified:** production DCE / tree-shaking behavior for the request-log ring buffer (§20.3 U7); TError generic adoption rate for 667 RQ sites (§20.3 U1 ≤1% sample); 79-raw-fetch per-site classification (§20.3 U3).

Macro zero-drift metrics + verifier-loop conflict resolution reduce but do NOT eliminate miss risk. Cycle 2 SIGN was NOT required per Rigby verdict; the completeness reduction is explicitly declared here per Rigby "missing area" verdict at Q20.

### 20.4b Unresolved unknowns (promotes to S2599 xx99 §6)

- **U1** — Exact React Query `TError` generic adoption rate across 667 useQuery/useMutation sites. Sampled per S2404 §20.3 U1 as ≤1%; formal audit deferred.
- **U2** — Per-module method count for the ~10 apiModules where sub-agents diverged (Agent 1 vs Agent 3 counted differently for orchestrationApi, docsIndexApi, platformApi). Adopted Agent 3 conservative estimate + noted approximation. Full method-count reconciliation deferred to post-arc T-slot or Rigby SIGN cycle 1 if load-bearing.
- **U3** — 79-raw-fetch site classification (auth-required-vs-public + credentials-mode + response-type). S2404 §19.3 item 2b deferred to post-arc T-slot.
- **U4** — Inline `interface *Response` declaration count across `frontend/src/pages/**` + `frontend/src/components/**` (S2203 §15.6 sampled ~12+; full count deferred per S2299 §6 U4).
- **U5** — Whether platformApi's ~30 methods with inline-anonymous-typed responses will graduate to typed-island discipline via cockpitApi pattern extension OR churn under codegen path A. Cat B boundary observation only; Chris-D-verdict at xx99.
- **U6** — Whether the 79-raw-fetch site count of 31 files at HEAD is additive-only across sessions or whether individual sites have been added-and-removed. Site-add-vs-site-drop dynamics UNKNOWN; only net-count zero-drift observed.
- **U7** — Whether the request-log ring buffer (api.ts:3990–4048) is production-DCE-tree-shaken or ships to production bundle. S2204 §20.3 U4 identical unknown at Cat B scope.

### 20.5 Conflicts between sources (verifier-loop pre-Rigby-SIGN discipline)

**Four sub-agent conflicts resolved before Rigby SIGN routing:**

1. **apiModule count.** Agent 1 + Agent 3 said 93; Agent 6 said 97. Parent-Claude direct grep `^export const \w+Api\s*=` = 93. **Adopted 93 as canonical.**
2. **platformApi method count.** Agent 1 said 414; Agent 3 said 30 (100% typed). Parent-Claude direct read of lines 3257–3920 (663 LOC monolithic apiModule) shows platformApi structure with inline typed responses (`api.get<{...inline...}>('/platform/...')` pattern). 663 LOC / 30 methods ≈ 22 LOC/method is plausible given inline typed-response bodies; 663 LOC / 414 methods ≈ 1.6 LOC/method is implausible. **Adopted Agent 3's ~30 methods as canonical; Agent 1's 414 REFUTED as likely miscount of nested `:` inside response type declarations.**
3. **Direct-consumer call count.** Agent 3 + parent-Claude said 57 (= 913 total − 856 defs); Agent 6 said 87. Parent-Claude verified 856 defs internal to api.ts + 913 total repo grep. **Adopted 57 as canonical; Agent 6's 87 REFUTED as counting axios-instance imports + method calls together (wrong denominator).**
4. **CODEOWNERS existence + location.** Agent 5 said "S1505 to S2404 baseline was 'absent'"; Agent 6 said "file exists (48 lines) at repo root". Parent-Claude direct `ls` verified: `.github/CODEOWNERS` DOES NOT EXIST; `./CODEOWNERS` at repo root EXISTS (48 lines, 1642 bytes). **Adopted `./CODEOWNERS` at repo root as canonical; F-D-OWN-1 PARTIALLY-REMEDIATED per S2499 AU-D5 (location established at repo root, cockpit surface deferral explicit at lines 8–13).**

All 4 conflicts resolved pre-Rigby-SIGN per playbook §14 verifier-loop discipline.

### 20.6 Verifier-loop corrections (Rigby SIGN cycle 1 fold notes)

**Rigby SIGN cycle 1 executed 2026-07-05.**

- **Fresh isolation pin:** `pa-1164d91b3dce4b97` (minted via `session_tool.create_fresh` per playbook §15 SIGN-isolation discipline; NINETEENTH-consecutive dedicated fresh SIGN pin candidate).
- **Cadence:** 4-batch × 5-Q = 20 Q per S2201–S2501 TEN-consecutive tested pattern (ELEVENTH-consecutive application).
- **Retirement:** via `session_tool.retire` at cycle close (NINETEENTH-consecutive dedicated fresh SIGN pin retirement candidate).
- **Verdict:** SIGN-WITH-EDITS at MED-HIGH confidence. Cycle 2 NOT required per Rigby verdict.
- **Tally:** 20 Q → 5 AGREE + 14 STRENGTHEN + 1 combined Q20 verdict-format response. All 20 folds landable pre-Chris-ratification.

### 20.6.1 Standard Rigby verdict format (Q20)

- **Overall confidence:** MED-HIGH.
- **Most accurate part:** zero-drift baselines + verifier-loop conflict resolution (unusually well-triangulated for Cat B; 4 sub-agent conflicts resolved pre-SIGN strengthen trust).
- **Weakest part:** completeness-implicating enumerations (notably WS subscription sites) + typed-rate delta framing (readable as governance progress by fast readers).
- **Missing area:** consolidated §1 Denominator Contract + Sampling Completeness box (folded per Q9 + Q10 + Q20; now §1.1).
- **Overstated maturity:** "CRITICAL" F3 severity if written unconditional (folded per Q2 + Q17 conditional language guardrail); "frozen" if implies intentional policy freeze rather than observed drift=0 (folded per Q1 "drift-frozen (observed)" clarification).
- **Understated maturity:** verifier-loop rigor + structural stability signal (drift=0 across 5 sessions is a legitimate maturity dimension if labeled correctly — stability, not progress; folded across §14 + §15 label rename to "Observability Risks").
- **Biggest architectural risk:** shape-blind error handling at the interceptor layer causing silent auth/error failures + blocking typed-envelope normalization downstream.
- **Most important next research:** exhaustive-or-near-exhaustive WS subscription surface enumeration (Cat D T7 joint at S2504) + formal mapping of raw-fetch bypass sites to "should-intercept" contract claims (Cat D T7 + post-arc T-slot per §19.3 R9).
- **What Claude got wrong:** nothing major; the 4 pre-SIGN sub-agent conflicts (apiModule count, platformApi method count, direct-consumer count, CODEOWNERS location) were resolved via parent-Claude verifier-loop pre-Rigby-SIGN routing and strengthen trust. The only "wrong risk" would be lingering phrasing implying completeness when sampling was used (folded per Q7 + Q10 hedges).
- **What must change before canonical:** apply the language guardrails + hedges from the SIGN cycle folds (F3 CRITICAL-conditional, WS "identified from targeted enumeration", typed-rate delta as mechanical, drift-frozen as observed).
- **Final verdict:** SIGN-WITH-EDITS. Cycle 2 not needed.

### 20.6.2 Fold ledger (20 folds landed pre-Chris-ratification)

| # | Q ref | Batch | Section | Fold summary |
|---|---|---|---|---|
| 1 | Q1 AGREE + micro-edit | 1 | §1 | "Structurally FROZEN" → "structurally drift-frozen (observed drift=0, not intentional policy freeze)" — clarifies observed outcome vs intent. |
| 2 | Q2 STRENGTHEN | 1 | §14 F3 | F3 severity split into HIGH baseline (independent) + CRITICAL conditional (if Cat C requires shape-normalization landing first as gating prerequisite). Cat B does NOT assert Cat C dependency as fact; CRITICAL is CONDITIONAL. Prevents Cat B "smuggling" Cat C policy. |
| 3 | Q3 STRENGTHEN | 1 | §1 + §14 F2 | Typed-rate delta 6.85% → 7.36% RELOCATED out of §1 headline narrative into §14 F2 + §1.1 Denominator Contract box as sanity metric with explicit numerator-unchanged callout. |
| 4 | Q4 AGREE + optional micro-add | 1 | §19.1 R1 | Preserves Cat C S2503 authority. Added explicit "Cat B enumerates axes only; Cat C owns selection" non-verdict qualifier. |
| 5 | Q5 STRENGTHEN | 1 | §15 | §15 top-5 debt list RENAMED to "Top-5 Observability Risks" to allow rank-1 meta-observation (5-session drift-frozen consumer surface) to coexist with concrete debts under unified taxonomy. Rank-1 labeled "Trajectory / Governance Signal". |
| 6 | Q6 AGREE + strengthening language | 2 | §14 F4 | DEAD-CANDIDATE 18-module severity KEPT at LOW-MEDIUM; added 5-session persistence governance-signal note ("~2,700 LOC dead-weight; removal remains maintainer-intent-gated"). |
| 7 | Q7 STRENGTHEN | 2 | §6.4 + §20.4 | WS subscription enumeration REPHRASED from "8 distinct WebSocket subscription sites" to "8 identified from targeted enumeration"; full enumeration deferred to Cat D T7/S2504. Method-tag added: targeted grep on `new WebSocket(`, `useWebSocket`, hook-factory. |
| 8 | Q8 STRENGTHEN | 2 | §14 F7 → F7 CLOSED + F8 NEW | CODEOWNERS finding SPLIT: F7 = S2404 F-D-OWN-1 CLOSED (partial-scope) per S2499 AU-D5; F8 = NEW finding for cockpit/hooks/types coverage-gap deferred per CODEOWNERS lines 8–13. Preserves remediation progress + surfaces live gap. |
| 9 | Q9 STRENGTHEN | 2 | §1.1 (NEW) | Denominator Contract box added to §1.1 with unit-of-analysis + scope + verification-method per rate claim. Prevents reader conflation. §14 per-finding math preserved. |
| 10 | Q10 AGREE + explicit note | 2 | §20.4 (NEW) | Sampling completeness note added at §20.4 (renumbered §20.4b for unknowns per S2203 pattern) with exhaustive-vs-targeted-vs-sampled taxonomy + explicit non-exhaustive method disclosure. |
| 11 | Q11 STRENGTHEN | 3 | §19.2 R6 | R6 error-boundary handoff dual-owned: Cat C S2503 (typed-envelope prerequisite) AND Group 2200 post-arc T-slot (global error UX / boundary framework). R6 ownership NOT exclusively Cat C. |
| 12 | Q12 STRENGTHEN | 3 | §19.1 R1 | Explicit INDEPENDENCE statement added: DECLARATION-side Path A/B/C (Cat A) + CONSUMER-side Path A/B/C (Cat B) are INDEPENDENT decision-spaces; mixed combinations valid (e.g., backend Path C + frontend Path B). |
| 13 | Q13 STRENGTHEN | 3 | §16 | Two-level frame added: Level 1 (formal contracts not declared — primary posture) + Level 2 (implicit interceptor contract IS declared by convention; 79-raw-fetch bypass is concrete violation of implicit contract). Preserves primary posture while acknowledging exception. |
| 14 | Q14 AGREE | 3 | §17 + §15 rank-3 | platformApi 663-LOC nested-monolith kept as SUB-OBSERVATION under F1 mega-module (not spun to distinct finding). Prevents double-counting same root cause. |
| 15 | Q15 AGREE + cost-of-deferral note | 3 | §14 F8 + §18 | Ownership deferral preserved (Cat B does NOT prescribe reassignment); added cost-of-deferral operational note quantifying risk (review latency + drift persistence) without recommendation. |
| 16 | Q16 STRENGTHEN + one sentence | 4 | §1 R6 gap-record | Added explicit R6 error-boundary gap-record + non-prescription scope statement at §1: "Cat B RECORDS the gap as verified-absent boundary evidence for downstream owners; Cat B does NOT prescribe framework design (owned by Cat C + Group 2200)." |
| 17 | Q17 STRENGTHEN | 4 | §1.2 (NEW) | Added "Do Not Misread" 2-bullet box at §1.2: (1) F3 CRITICAL is conditional on Cat C dependency; (2) typed-rate deltas are mechanical unless numerator changes. Highest-risk misinterpretation prevention. |
| 18 | Q18 AGREE as-is | 4 | §19.3 R7 | §19.3 R7 recommendation-strength language preserved. Cat B does NOT prescribe xx99 close artifacts beyond evidence-backed candidacy per playbook §19 discipline. |
| 19 | Q19 AGREE + xx99 evidence framing | 4 | §20.7 | §11.2 template TWENTY-FIRST-consecutive application kept as Chris-D-verdict-request EVIDENCE for xx99 close (NOT self-codified per Cat B non-verdict discipline). Codification language conditional: "promotion to TEMPLATE-CANONICAL requires xx99/Chris trigger satisfaction". |
| 20 | Q20 combined verdict-format response | 4 | §20.6.1 (NEW) | SIGN-WITH-EDITS at MED-HIGH confidence. Cycle 2 NOT required. Standard Rigby verdict format populated at §20.6.1. All 20 folds landable pre-Chris-ratification. |

**All 20 folds landable pre-Chris-ratification.** Cycle 2 not required per Rigby cycle-1 MED-HIGH confidence + all folds non-controversial (mostly phrasing/structure per Q20 verdict).

### 20.7 S2502 arc metadata

- **Arc:** Research Group 2500 (API — Contract SoT + Silent-401 Downstream Remediation + Session-Lifecycle API Contracts + Per-Endpoint Permission-Floor Registry Design-Prep + REST↔WS T7 Joint 2500+2600).
- **Child slot:** P2 Cat B — Frontend API-Client Architecture Design-Prep.
- **Predecessor:** S2500 parent scoping + S2501 P1 Cat A Backend API Contract SoT Design-Prep.
- **Successors:** S2503 P3 Cat C Error-envelope + refresh + logout API contracts design-prep (next); S2504 P4 Cat D Permission-floor registry design-prep + REST↔WS T7 joint (after Cat C); S2599 xx99 canonical summary + arc close.
- **Arc pin:** `pa-a03b111768464b3f` ACTIVE + PRESERVED through S2502 per playbook §16 arc-standard behavior; TWELFTH formal arc pin under Research OS.
- **SIGN pin:** `pa-1164d91b3dce4b97` (minted at S2502 open; NINETEENTH-consecutive dedicated fresh SIGN pin candidate).
- **Playbook §11.2 20-section child-audit template TWENTY-FIRST-consecutive application** after S1301+S1401+S1501+S1601+S1701+S1801+S1901+S2001+S2101+S2102+S2103+S2104+S2201+S2202+S2203+S2204+S2401+S2402+S2403+S2404+S2501 twenty prior. **Codification language conditionality preserved (Rigby SIGN cycle 1 batch 4 Q19 AGREE fold):** 21-consecutive stable-shape indicates strong stability signal; **promotion to TEMPLATE-CANONICAL requires xx99 / Chris trigger satisfaction beyond mere repetition** (e.g., cross-team adoption OR measurable defect reduction OR explicit Chris ratification). Cat B does NOT self-codify; codification claim remains Chris-D-verdict-request EVIDENCE for S2599 xx99 close per Cat B §16 discipline preservation. MC-5 CODIFICATION-CONFIRMED-with-scope-guardrails candidate extension 20 → 21 registered for xx99 review.
- **Rigby SIGN cycle 1 COMPLETE** (2026-07-05): SIGN-WITH-EDITS at MED-HIGH confidence via dedicated fresh SIGN isolation pin `pa-1164d91b3dce4b97` — NINETEENTH-consecutive dedicated fresh SIGN pin candidate. 20 folds landed pre-Chris-ratification per playbook §20.6 fold ledger discipline (see §20.6.2 fold table). Cycle 2 NOT required.
- **ELEVENTH-consecutive 4-batch × 5-Q cadence application** after S2201+S2202+S2203+S2204+S2401+S2402+S2403+S2404+S2499+S2501 ten prior. Codification framing CONDITIONAL pending xx99 review per Q19 discipline preservation.
- **Playbook §13 6-parallel-Explore-agent sweep** executed at draft-open per S2201–S2501 pattern; 6 sub-agents dispatched in single message (Models & Persistence + Services & Runtime Flows + APIs & Tools & Tasks & Commands + Integrations & Cross-Domain + Documentation & Prior Research + Drift & Debt & Ownership & Maturity).
- **Playbook §14 verifier-loop** applied pre-Rigby-SIGN with 4 sub-agent conflicts resolved (§20.5).
- **HEAD `548f53a1`** at draft-open (2 commits past S2500 baseline `77564f76`; post-S2501 close + S2501 docs cascade).
- **Cat B boundary discipline:** design-preparation + boundary evidence only per playbook §5 phase discipline + S2501 Cat A precedent + S2500 §7 anti-scope; no code changes; no runtime modifications; no remediation prescription; option-space enumeration + Chris-D-verdict-request evidence for S2599 xx99 close.
- **Verbs used:** enumerate / inventory / measure / classify / verify / re-verify / defer / propose evidence-collection. **Verbs NOT used:** decorate / implement / migrate / adopt / remediate / require / fix / correct (except when directly quoting predecessor documents' recommendations).
