---
title: "PA Workspace-Context Authz + Session-Lifecycle Design-Prep Audit (Group 2600 P3 Cat C)"
session: 2603
status: active (S2603 P3 Cat C PA Workspace-Context Authz + Session-Lifecycle Design-Prep — child audit CLOSED post-Chris "agree all" ratification 2026-07-06. Playbook §11.2 20-section child-audit template TWENTY-THIRD-consecutive application after S1301/S1401/S1501/S1601/S1701/S1801/S1901/S2001/S2101/S2102/S2103/S2104/S2201/S2202/S2203/S2204/S2401/S2402/S2403/S2404/S2501/S2601/S2602 twenty-two prior. Shape-card SIGN-preview via arc pin `pa-c17a8d7e0660413b` returned Rigby overall confidence HIGH with 2 folds (F-C1 evidence-first C2 lens + F-C2 AC-C1-2 wording); Chris "agree all" 2026-07-06 ratified both folds wholesale pre-drafting. Rigby SIGN cycle 1 on full audit doc via SINGLE-PIN close pattern (2-pin recovery NOT required; preemptive 2-batch × 2-Q batching from turn 1 prevented worker instability per `feedback_rigby_sign_worker_instability_recovery.md` — matches S2602 SINGLE-PIN success). Dedicated fresh SIGN isolation pin `pa-9f37a2818961487f` TWENTY-SEVENTH consecutive dedicated fresh SIGN pin retirement in Research OS after 26 prior — Batch 1 (Q1+Q2 coverage+maturity) HIGH confidence with 3 STRENGTHEN folds (F-C3 workspace-touching subset rule + F-C4 PA-produced outputs retention-impact + F-C5 24-hour lookback mechanism-constant) + Batch 2 (Q3+Q4 debt+boundary) HIGH confidence with 2 STRENGTHEN folds (F-C6 DEBT-C2-1 severity semantics governance-gap + F-C7 F5 Path-C-pure INVALID hard language) + 2 new debt items (DEBT-C1-7 workspace single-owner + DEBT-C1-8 workspace_id provenance implicit) + §7.2 fails-closed clarifier + §19.1 CRITICAL add (workspace_id sourcing enumeration). Chris "agree all" 2026-07-06 ratified all 5 folds + 2 debt items + clarifiers wholesale. Cycle 2 NOT required. Arc pin `pa-c17a8d7e0660413b` PRESERVED through S2603 per playbook §16 arc-standard behavior.)
arc: Research Group 2600 (PA — Cross-Arc Handoff Bundle Consuming CF-2600-PA + CF-D6 + F-B-HIGH-3 + Workspace-Context Authz + REST↔WS T7 Joint Dual-Owner) — S2603 P3 Cat C PA Workspace-Context Authz + Session-Lifecycle child audit
category: research (playbook §11.2 20-section child-audit template TWENTY-THIRD-consecutive application)
authors: Claude Code (S2603 P3 Cat C draft 2026-07-06 at HEAD `2a3bc20d`; parent-Claude verifier-loop applied per playbook §14 pre-draft on 6-Explore-agent sub-agent claims — 4 corrections landed pre-draft); Rigby SIGN cycle 1 CLOSED via dedicated fresh SIGN isolation pin `pa-9f37a2818961487f` (TWENTY-SEVENTH consecutive) with 5 STRENGTHEN folds (F-C3+F-C4+F-C5 Batch 1 + F-C6+F-C7 Batch 2) + 2 new DEBT items (DEBT-C1-7+DEBT-C1-8) baked per Chris "agree all" ratification 2026-07-06; Chris "commit it" ratification 2026-07-06
verifier_loop: |
  Parent-Claude verifier-loop applied per playbook §14 on 6-Explore-agent
  sub-agent claims pre-draft. Four verifier corrections landed pre-draft:

  1. **WORKSPACE_AWARE_AGENTS line-range CORRECTED to 3873-3907 at HEAD
     `2a3bc20d`.** Cat A companion anchor line 102 + parent scoping §2.1
     line 105 both cited `core/epa_handlers_tools.py:191-217`. Direct
     grep at HEAD returned `WORKSPACE_AWARE_AGENTS = [` at line 3873
     (`core/epa_handlers_tools.py:3873`). Explore Agents 1, 2, 4 all
     reported the corrected range. Cat A cite was drift from an
     earlier HEAD; Cat C denominator authoritative line-range is
     3873-3907 (20 agents, verified content match).

  2. **`WorkspaceManager.get_active_workspace()` at
     `core/services/workspace_manager.py:1697` (NOT :1710).** Explore
     Agents 1 + 2 reported 1710; direct grep at HEAD returned 1697.
     Small drift; corrected. This is the load-bearing method for the
     workspace-membership check delegated from
     `_write_files_to_workspace()`; see §5.1 for method body.

  3. **`session_tool` action enum = 7 values (create_fresh /
     list_recent / whoami / retire / set_active / seed /
     health_check).** Explore Agent 2 gave full bodies for 5
     (create_fresh 3881, retire 4011, set_active 4074, seed 4109,
     whoami 3961); Agent 3 listed 7 enum values but verified only 2
     bodies. Parent verifier grepped `elif action ==` in
     `core/services/td_handlers_core.py` and confirmed all 6 non-
     health_check branches at lines 3881, 3930, 3961, 4011, 4074,
     4109 (plus the top-level `health_check` early branch). Agent 3's
     7-count is authoritative; all 7 verified at HEAD.

  4. **3 logout endpoints confirmed at HEAD.** Explore Agents 2 + 3 +
     4 all reported 2-3 logout endpoints. Parent verifier grepped
     `^def logout|logout_view|logout_enhanced_view` and confirmed:
     (a) `logout_view` at `core/auth_views.py:85` (POST
     `/api/v1/auth/logout/` per `core/urls.py:2185`); (b)
     `logout_enhanced_view` at `core/auth_views_enhanced.py:541`
     (POST `/api/v1/auth/logout-enhanced/` per `core/urls.py:2196`);
     (c) `logout_view` at `core/urls_unified.py:46` (path
     `logout/` — the Cognito-bypass unified frontend variant per
     `core/urls_unified.py:97`). None call `session_tool.retire`
     iteration; none mutate PA conversation `session_active` state.

  Additional verifier confirmations (all sub-agent claims verified
  accurate at HEAD): (a) `execute_with_workspace()` at
  `core/agents/base_agent.py:5355` — CONFIRMED matches Cat A §16.1 +
  S2402 §14.2 baseline; (b) 285-entry path-list gate baseline at
  `core/auth_middleware.py` breakdown (265 PUBLIC_PATHS + 2
  PUBLIC_PATHS_EXACT + 7 OPTIONAL_AUTH_PATHS + 3 STAFF_REQUIRED_PATHS
  + 7 REVIEWER_BLOCKED_PATHS + 1 REVIEWER_ALLOWED_PATHS) — CONFIRMED
  match to S2504 §Cat D reference; (c) ZERO PA-path prefixes
  (`/api/pa/*` + `/api/assistant/*` + `/api/v1/assistant/*`) in any
  path-list constant — verified via direct grep, matches Agent 2/3
  reports; (d) NO `class WorkspaceMember` DRF permission class at HEAD
  — grep returned 0 matches across `core/*.py`; (e) NO
  `class IsWorkspaceMember` / `class WorkspacePermission` — same;
  (f) `WORKSPACE_AWARE_AGENTS` 20-string content matches parent
  scoping §2.1 + Cat A §5.1 evidence at HEAD.

  Verifier discipline aligned with S2601 §14.6 5-corrections pattern +
  S2602 §14.1 7-corrections pattern. Cat C boundary discipline
  preserved — evidence-only; no verdict recommendations on Path
  A/B/C+compensating (C1) or α/β/γ/PA-override (C2).
companion_anchors:
  - docs/PLATFORM_INVENTORY.md                                          # runtime counts anchor — 20 WORKSPACE_AWARE_AGENTS candidate; 285 path-list entries; 34 PA-path endpoints
  - docs/PLATFORM_WHAT_IT_IS.md                                         # narrative anchor — PA subsystem narrative
  - docs/topics/personal-assistant.md                                   # PA subsystem topic doc — NO workspace-enforcement subsection AND NO session-lifecycle subsection at HEAD (both are Cat C anchor-update candidates for S2699 xx99 cascade)
  - docs/research/DOMAIN_RESEARCH_PLAYBOOK.md                           # process contract §11.2 TWENTY-THIRD application
  - docs/research/domains/pa/2600_pa_domain_scoping.md                  # DIRECT PARENT — §3.C1 + §3.C2 + §5.3 AC + §2.6.A/B lens + §7 anti-scope
  - docs/research/domains/pa/2601_pa_backend_endpoint_contract_sot_design_prep_audit.md  # SIBLING PRIOR-CHILD Cat A — §6.1 F11 34-endpoint canonical inventory + §16.1 F-B-HIGH-3 boundary evidence baseline + §7.2 REST-side task-based-async statement
  - docs/research/domains/pa/2602_pa_client_contract_surface_design_prep_audit.md  # SIBLING PRIOR-CHILD Cat B — §4.1 F-B4 U7 paStore 16-field dump + §15.2 CF-C2 coordination debt + §16.1 F-B7 attribution + §7.1 8-step client flow
  - docs/research/domains/auth/2402_authorization_permission_floor_uniformity_audit.md  # F-B-HIGH-3 ORIGIN — Cat B §14.2 workspace-membership implicit-gate finding
  - docs/research/domains/auth/2403_session_lifecycle_logout_cleanup_contract_audit.md  # α/β/γ ORIGIN — §19.1 three-option decision-space + §9.2 CF-C2 handoff to Group 2600 PA
  - docs/research/domains/auth/2499_auth_canonical_summary.md          # Group 2400 arc close — α/β/γ verdict DEFERRED as of S2603 open
  - docs/research/domains/api/2504_api_permission_floor_registry_rest_ws_t7_joint_design_prep_audit.md  # 285-entry path-list gate reference for C1 Path B analog
  - docs/research/domains/api/2599_api_canonical_summary.md            # Group 2500 API canonical verdict — inherited as §2.6.A hard constraint per parent
  - docs/research/domains/frontend/2204_frontend_session_state_persistence_discipline_audit.md  # F5/F6/F7/F8 15-surface storageKeys inventory + syncUser incomplete finding
  - core/agents/base_agent.py:5355                                      # execute_with_workspace() — F-B-HIGH-3 implicit-gate location
  - core/services/workspace_manager.py:1697                             # WorkspaceManager.get_active_workspace() — delegated membership resolution
  - core/epa_handlers_tools.py:3873-3909                                # WORKSPACE_AWARE_AGENTS constant (20 agents) + dispatcher gate at line 3909
  - core/auth_middleware.py                                             # 285-entry path-list gate registry (6 constants) — NO PA-path coverage
  - core/services/td_handlers_core.py:3868-4163                         # session_tool handler (7 actions: health_check + create_fresh + list_recent + whoami + retire + set_active + seed)
  - core/auth_views.py:85                                               # logout_view (basic; deletes token only)
  - core/auth_views_enhanced.py:541                                     # logout_enhanced_view (enhanced; deletes token only)
  - core/urls_unified.py:46                                             # logout_view (Cognito-bypass unified frontend variant)
  - core/models/conversations/models.py:59                              # ChatConversation with session_active field
  - core/models_assistant_profile.py:122-129                            # AssistantProfile.workspace FK
  - frontend/src/stores/paStore.ts:24-193                               # paStore inline interfaces + syncUser 5-of-16 field wipe
  - CODEOWNERS                                                          # PA workspace-authz + session-lifecycle code paths ownership analysis
delegated_from:
  - Group 2600 S2600 §3.C1 Cat C1 mission — "workspace-context authz declaration policy — close F-B-HIGH-3 workspace-membership implicit-gate; declare enforcement point (Path A / Path B / Path C+compensating per F5 fold)"
  - Group 2600 S2600 §3.C2 Cat C2 mission — "PA session-lifecycle policy — session_tool.retire on logout + PA conversation retention window; α/β/γ from Group 2400 OR PA-override with rationale trace"
  - Group 2400 S2402 §14.2 F-B-HIGH-3 CF-B2 handoff — workspace-membership implicit-gate flagged for Group 2600 closure
  - Group 2400 S2403 §9.2 CF-C2 handoff — session_tool.retire disposition on user logout + PA conversation retention window scope
  - Group 2500 S2504 CF-D6 REST↔WS T7 joint (dual-owner) — Cat C1 REST-side vs Cat D S2604 WS-side authentication handshake boundary
delegates_to:
  - S2604 P4 Cat D REST↔WS T7 joint — Cat C1 REST-side workspace-authz verdict couples/decouples to Cat D WS channel authentication handshake (AC-C1-4 T7 cross-transport consistency check)
  - S2699 xx99 Group 2600 canonical summary — Cat C1 Path A/B/C+compensating + Cat C2 α/β/γ/PA-override Chris-D-verdict ratification
  - Group 2400 xx99 close (if reopened) — PA-slice α/β/γ application evidence contributed
lens: >
  Cat C boundary lens question (Chris-ratified per shape-card F3 fold
  2026-07-06 wholesale + F-C1 evidence-first C2 rewrite ratified
  2026-07-06):

  **C1 lens:** "Where does PA-path workspace-context authorization
  DECLARE its enforcement point at the REST boundary — HTTP
  permission-class layer (Path A), middleware path-list gate (Path
  B), or handler-internal WITH documented compensating controls
  (Path C+compensating)? Path C-pure is NOT a valid ratification per
  parent §5.3 AC#3 F5 fold."

  **C2 lens (F-C1 fold ratified 2026-07-06):** "Given current PA
  usage (arc pins, multi-thread sessions, `session_tool.retire`
  mechanics), does PA **inherit** the Group 2400 α/β/γ outcome
  unchanged, or does PA **declare** an override for arc-pin lifetime
  (coupled vs decoupled), with explicit rationale + user-safety
  tradeoff at xx99? If Group 2400 remains unresolved, record PA
  stance as 'defer + constraints' (no ratification)."

  Cat C boundary evidence-only: Cat C collects DECLARATION evidence
  (where the workspace-authz enforcement point IS declared + how the
  PA session-lifecycle policy IS declared) without recommending Path
  A/B/C+compensating verdict for C1, without authoring
  `WorkspaceMember` DRF class code, without ratifying α/β/γ or
  PA-override for C2, and without modifying `session_tool.retire`
  handler code (§7 anti-scope inheritance from parent §7 items #1-#10
  + Cat-C-specific micro-anti-scope Cat-C-1..9 per §16.4). Verdict
  on Path A/B/C+compensating for C1 + α/β/γ/PA-override for C2 is a
  Chris-D-verdict-request at S2699 xx99 close after all 4 children
  have contributed evidence.
playbook_application: §11.2 20-section child-audit template TWENTY-THIRD-consecutive application per S2600 §5.1 child mission sequence; §13 six-parallel-Explore-agent sweep contract applied at S2603 open — 6 Explore agents dispatched with self-contained briefs (Models + Persistence / Services + Runtime Flows / APIs + Tools + Tasks + Commands / Integrations + Cross-Domain / Documentation + Prior Research / Drift + Debt + Ownership + Maturity); §14 parent-Claude verifier-loop applied pre-draft — 4 corrections landed pre-draft; §15 SIGN cycle 1 REQUIRED at child-audit stage per playbook §15 stage-scoped routing — routed via dedicated fresh SIGN isolation pin (NOT arc pin `pa-c17a8d7e0660413b`) per playbook §15 SIGN-isolation discipline (TWENTY-SEVENTH consecutive dedicated fresh SIGN pin candidate under Research OS after 26 prior); §16 arc pin `pa-c17a8d7e0660413b` PRESERVED through S2603 per playbook §16 arc-standard behavior (no retirement until S2699 xx99 close)
---

# PA Workspace-Context Authz + Session-Lifecycle Design-Prep Audit (Group 2600 P3 Cat C)

> **DRAFT.** S2603 P3 Cat C child audit drafted 2026-07-06 (HEAD `2a3bc20d`). 6-parallel-Explore-agent sweep + parent-Claude verifier-loop per playbook §14 (4 pre-draft corrections) + Rigby shape-card SIGN-preview HIGH confidence with 2 folds (F-C1 + F-C2, Chris "agree all" 2026-07-06 ratified). Rigby SIGN cycle 1 on full audit doc via dedicated fresh SIGN isolation pin PENDING. Arc pin `pa-c17a8d7e0660413b` PRESERVED through S2603. TWENTY-THIRD-consecutive playbook §11.2 20-section child-audit template application.

> **Cat C boundary discipline paramount.** Cat C collects EVIDENCE for future Chris-D-verdicts on Path A / Path B / Path C+compensating (C1) and α / β / γ / PA-override (C2). Cat C does NOT recommend verdicts; Cat C does NOT retrofit `WorkspaceMember` DRF class code; Cat C does NOT modify `WORKSPACE_AWARE_AGENTS` list; Cat C does NOT modify `execute_with_workspace()` internals; Cat C does NOT implement audit-log hook; Cat C does NOT modify `session_tool.retire` handler; Cat C does NOT create new `docs/topics/personal-assistant.md` workspace-enforcement documentation section (§16.4 Cat-C-1..9 micro-anti-scope; parent §7 items #1-#10 inheritance).

> **Two parallel sub-tracks (F2 parent fold).** Cat C delivers TWO parallel decision tables inside one audit doc: C1 (workspace-context authz declaration) + C2 (PA session-lifecycle policy). Sub-tracks are ORTHOGONAL unless coupling evidence surfaces per S2504 §88 discipline. §-sub-organization uses "**C1**" and "**C2**" labels throughout.

## 1. Executive Summary

**PA workspace-context authorization enforcement at HEAD `2a3bc20d` is UNIFORMLY UNDECLARED at the REST boundary.** All 34 PA-path URL patterns (Cat A §6.1 F11 canonical inventory) carry `@permission_classes([IsAuthenticated])` uniformly — **NONE declare a `WorkspaceMember` DRF permission class** (verified: 0 `class WorkspaceMember` matches across `core/*.py`), and **NONE are covered by any of the 285 path-list gate entries** across `core/auth_middleware.py`'s 6 constants (verified: 0 `/api/pa/` or `/api/assistant/` prefix matches in PUBLIC_PATHS + PUBLIC_PATHS_EXACT + OPTIONAL_AUTH_PATHS + STAFF_REQUIRED_PATHS + REVIEWER_BLOCKED_PATHS + REVIEWER_ALLOWED_PATHS). Workspace-membership enforcement occurs **INSIDE the handler layer** via `execute_with_workspace()` at `core/agents/base_agent.py:5355`, which delegates to `WorkspaceManager.get_active_workspace()` at `core/services/workspace_manager.py:1697` — a service-layer query filtering `ProjectWorkspace.objects.filter(user=self.user, is_active=True)`. Membership is inferred from **direct `ProjectWorkspace.user` OneToOneField ownership** (verified: no `WorkspaceMember` junction table exists at HEAD). This is the F-B-HIGH-3 implicit-gate location, preserved from S2402 §14.2 + confirmed at S2601 §16.1. **Cat A observed the boundary; Cat C1 owns the closure-condition verdict per parent §5.3 AC#3 F5 fold.**

**PA session-lifecycle policy at HEAD is UNIFORMLY UNDECLARED at both HTTP + client layers.** Three logout endpoints (`/api/v1/auth/logout/` at `core/auth_views.py:85` + `/api/v1/auth/logout-enhanced/` at `core/auth_views_enhanced.py:541` + Cognito-bypass `logout_view` at `core/urls_unified.py:46`) all **delete the DRF auth token only** — NONE iterate `session_tool.retire` across `ChatConversation.filter(user_id=user, session_active=True)`; NONE mutate `paStore` fields; NONE emit `Clear-Site-Data` header (verified: 0 emission per S2403 §14 F-C-CSD-1 preserved at HEAD). Client-side `authStore.logout()` at `frontend/src/stores/authStore.ts:34-39` sets state to null but does NOT trigger `paStore.reset()` or `session_tool.retire()` RPC; `paStore.syncUser(null)` at `frontend/src/stores/paStore.ts` wipes **5-of-16 fields** (`messages`, `activeConversationId`, `conversations`, `currentInput`, `conversationsLoading`) but LEAVES 2 UNKNOWN-intent fields (`isDockOpen`, `isDockMinimized`) + 9 other fields intact — persisting UI state + WS-driven live-tool state across the logout boundary. `session_tool.retire` is **verified working** at `core/services/td_handlers_core.py:4011` (7-action enum per verifier §14, including bulk-update `session_active=False` for user-scoped conversation_id rows), but is invoked by manual PA tool-call only, never auto-fired from any logout path. **Group 2400 α/β/γ session-lifecycle verdict remains DEFERRED as of S2603 open** (per S2499 canonical summary evidence).

**F8 baseline codification NEGATIVE for both sub-tracks at HEAD.** For C1: neither `docs/topics/personal-assistant.md` nor `CLAUDE.md` nor `docs/PLATFORM_WHAT_IT_IS.md` declares WHERE the workspace-membership check is enforced (HTTP / middleware / handler-internal). CLAUDE.md line 34 declares the canonical PA route but not the enforcement boundary. For C2: NO existing doc declares PA conversation retention window, arc-pin lifecycle policy, or session_tool.retire disposition on logout. Both declaration gaps make Path C-pure (implicit-gate WITHOUT compensating controls) strictly-worse than Path C+compensating (implicit-gate WITH audit-log hook + ADR + doc section) per parent §5.3 AC#3 F5 fold. Cat C records evidence; **Cat C does NOT recommend Path selection or verdict** per boundary discipline.

**Biggest Cat-C-boundary evidence items (§19 recommends future research — Chris-D-verdict-request at S2699 xx99):**

1. **`class WorkspaceMember` DRF permission class does NOT exist at HEAD** — Path A adoption requires CREATING this class (not just decorating with an existing one). Compare to S2504 §Cat D `IsAuthenticated` DEFAULT + custom Permission class inventory (3 custom classes total, none workspace-scoped).
2. **PA-path completely absent from 285-entry path-list gate registry** — Path B adoption would add a **7th constant** (e.g., `WORKSPACE_REQUIRED_PATHS` or `PA_WORKSPACE_PATHS`) to `core/auth_middleware.py`, growing the shadow per-endpoint registry per S2504 §Cat D framing.
3. **`execute_with_workspace()` at `core/agents/base_agent.py:5355` delegates to `WorkspaceManager.get_active_workspace()` at line 1697** — the membership check is a **user-owns-workspace query** (not a member-of-workspace query). This is a DESIGN CONSTRAINT for Path C+compensating: any audit-log hook must fire from `_write_files_to_workspace()` or `WorkspaceManager.get_active_workspace()`, not from `execute_with_workspace()` directly.
4. **3 logout endpoints × 0 PA-state mutations** — decoupling between platform session-lifecycle and PA session-lifecycle is CURRENTLY COMPLETE. Neither adopting α (silent-refresh) nor β (explicit-re-login) verdict at PA layer requires refactoring the logout handlers; each Chris-D-verdict path is additive.
5. **`session_tool.retire` guardrail on currently-bound conversation** — verified at `core/services/td_handlers_core.py:4011-4072`: refuses to retire currently-bound arc pin without `force=true` + pin_rotation_notice returned. This is a PA-override design constraint per playbook §16 arc-standard behavior.
6. **paStore U7 2 UNKNOWN intent fields + 9 non-wiped fields** — Cat B §4.1 F-B4 evidence preserved: `isDockOpen`, `isDockMinimized` intent UNKNOWN; 9 memory-only + persist fields NOT wiped on syncUser. C2 verdict-scope for retention-window disposition (§8.4 evidence).

**What comes next.** S2604 Cat D receives Cat C1 REST-side workspace-authz evidence for AC-C1-4 T7 cross-transport consistency check (F12 parent AC#8 inheritance) — Cat D S2604 owns WS-side authentication handshake verdict. S2699 xx99 receives BOTH C1 (Path A/B/C+compensating) + C2 (α/β/γ/PA-override) Chris-D-verdict axes for ratification. Group 2400 xx99 close (if reopened) receives PA-slice α/β/γ application evidence.

## 2. Domain Purpose

**Playbook §9 canonical Q1-Q2 — What is this domain?**

Cat C owns the **DECLARATION plane** of two orthogonal PA subsystem policies at the REST + client boundaries:

- **C1 workspace-context authorization declaration policy** — how PA endpoints DECLARE (or fail to declare) workspace-membership as a prerequisite for handler dispatch. Not the enforcement MECHANISM (which is Cat A §7.1 flow evidence + Agent 2 runtime flow §7 evidence — working at handler-internal), but the CONTRACT DECLARATION at REST + middleware boundaries.

- **C2 PA session-lifecycle policy** — how PA DECLARES (or fails to declare) the coupling between platform session lifecycle (user login/logout, token expiration) and PA-specific lifecycle artifacts (ChatConversation `session_active` flag, PA arc-pin lifecycle, paStore field-list cleanup, PA conversation retention window). Not the runtime session mechanics (Django sessions + DRF Token + Redis backend — working at S2403 §6 evidence), but the CONTRACT DECLARATION for what happens at logout / refresh / pin-rotation boundaries.

At HEAD `2a3bc20d`, **both C1 + C2 declaration layers are EXPERIMENTAL** per §13 maturity evidence — MECHANISM WORKING (execute_with_workspace() + session_tool.retire() both functional), DECLARATION-plane EXPERIMENTAL (no HTTP boundary contract; no ADR; no docs/topics/ subsection; no PLATFORM_WHAT_IT_IS.md declaration).

**Cat C boundary — what Cat C owns:** DECLARATION plane for C1 (where + how workspace-context authz is declared to consumers) + DECLARATION plane for C2 (where + how PA session-lifecycle policy is declared). Cat C does NOT own the RUNTIME mechanics (Cat A §7 covered REST-side runtime; Cat B §7 covered client-side runtime; Cat D S2604 will cover WS-side runtime).

**Domain purpose scope discipline (per playbook §5 phase discipline research-only + design-prep; §16.4 Cat-C-1..9 micro-anti-scope):** Cat C collects evidence for future Chris-D-verdicts. Cat C does NOT recommend, decide, or author. Cat C does NOT change endpoint behavior. Cat C does NOT add or remove decorators. Cat C does NOT retrofit `WorkspaceMember` class code. Cat C does NOT modify `session_tool.retire` handler. Cat C does NOT create documentation sections. Everything below is EVIDENCE. Nothing below is DIRECTIVE.

## 3. Canonical Entry Points

**Playbook §9 canonical Q3 — Where does the domain enter the system?**

### 3.1 C1 workspace-context authz declaration entry points

Cat C1 evidence-collection scope entry points at HEAD `2a3bc20d`:

| Entry point | Location | Layer | Role |
|---|---|---|---|
| PA-path REST endpoint definitions | `core/urls.py:2485-2540 + 4900-4903` | HTTP URL registration | 34 PA-path URL patterns per Cat A §6.1 F11 canonical inventory |
| DRF DEFAULT permission class | `core/settings.py:645-669 REST_FRAMEWORK[DEFAULT_PERMISSION_CLASSES] = [IsAuthenticated]` | DRF permission dispatch | Platform-wide default; PA-path inherits unless overridden |
| `@permission_classes([IsAuthenticated])` uniformly at PA view functions | `core/views_personal_assistant.py:31-32 + 34+ per-view` | DRF permission decorator | All 34 PA-path endpoints declare `[IsAuthenticated]` uniformly (Cat A §6.1 verified) |
| **`WorkspaceMember` DRF permission class** | `core/*.py` — **DOES NOT EXIST at HEAD** (0 `class WorkspaceMember` matches) | Would-be Path A layer | Path A adoption requires CREATING this class |
| Middleware path-list gate registry (6 constants) | `core/auth_middleware.py` — 285 entries total per S2504 §Cat D baseline | Middleware pre-DRF layer | **ZERO PA-path prefixes in ANY of 6 constants** (verified: PUBLIC_PATHS + PUBLIC_PATHS_EXACT + OPTIONAL_AUTH_PATHS + STAFF_REQUIRED_PATHS + REVIEWER_BLOCKED_PATHS + REVIEWER_ALLOWED_PATHS) |
| `WORKSPACE_AWARE_AGENTS` constant | `core/epa_handlers_tools.py:3873` (verifier-corrected from Cat A anchor 191-217) | Handler-internal gate | 20 agent-handle strings; C1 denominator scope |
| WORKSPACE_AWARE_AGENTS dispatcher | `core/epa_handlers_tools.py:3909` | Handler-internal gate | `if agent_name in WORKSPACE_AWARE_AGENTS and write_to_workspace:` routes to `execute_with_workspace()` |
| `execute_with_workspace()` method | `core/agents/base_agent.py:5355` | Handler-internal implicit gate | **F-B-HIGH-3 implicit-gate location** (S2402 §14.2 preserved + Cat A §16.1 confirmed) |
| `WorkspaceManager.get_active_workspace()` | `core/services/workspace_manager.py:1697` | Service-layer delegated resolution | Actual membership-check delegate: `ProjectWorkspace.objects.filter(user=self.user, is_active=True)` |
| `_write_files_to_workspace()` permission check | `core/agents/base_agent.py:5188-5200` | Handler-internal | `workspace.allow_file_write` flag check (NOT membership check — a permission flag AFTER active-workspace resolution) |

**F8 baseline codification test at PA-path (per parent §3.A + Cat A §3.3 pattern):**

| Check | Result | Evidence |
|---|---|---|
| Docstring workspace-membership annotation | NEGATIVE | `core/views_personal_assistant.py:267-289` docstring for `/api/pa/chat/` contains no workspace-membership requirement declaration |
| ADR declaring workspace-context enforcement policy | NEGATIVE | No `docs/decisions/` or `docs/adr/` file mentions workspace-context authz enforcement location |
| `docs/topics/personal-assistant.md` §Workspace-enforcement subsection | NEGATIVE | No such subsection exists at HEAD (verified via Agent 5 doc coverage evidence) |
| `docs/PLATFORM_WHAT_IT_IS.md` PA §Layer 4 workspace-enforcement declaration | NEGATIVE | Line ~187-228 PA narrative does NOT declare enforcement location (only mentions 20 WORKSPACE_AWARE_AGENTS in SKIN context) |
| CLAUDE.md §Working with Rigby workspace enforcement declaration | NEGATIVE | Line 34 declares canonical PA route; no enforcement-location statement |
| Audit-log hook emission on workspace-scoped dispatch | NEGATIVE | Grep `audit_log|workspace_audit` returned no runtime emission at `execute_with_workspace()` / `_write_files_to_workspace()` / `WORKSPACE_AWARE_AGENTS` dispatcher call sites |

**F8 verdict for C1: NEGATIVE at HEAD.** Path C-pure (defer without compensating controls) is strictly-worse relative to Path C+compensating (defer WITH audit-log hook + ADR + doc section) for the S2699 xx99 Chris-D-verdict. Cat C records this evidence; Cat C does NOT recommend verdict per boundary discipline.

### 3.2 C2 PA session-lifecycle declaration entry points

Cat C2 evidence-collection scope entry points at HEAD `2a3bc20d`:

| Entry point | Location | Layer | Role |
|---|---|---|---|
| `logout_view` (basic) | `core/auth_views.py:85` (routed at `core/urls.py:2185` as `/api/v1/auth/logout/`) | HTTP endpoint | Deletes `request.user.auth_token`; returns `{"detail": "Successfully logged out"}` |
| `logout_enhanced_view` (enhanced) | `core/auth_views_enhanced.py:541` (routed at `core/urls.py:2196` as `/api/v1/auth/logout-enhanced/`) | HTTP endpoint | Deletes token; swallows exceptions (degraded); returns `{"message": "Logged out successfully"}` |
| `logout_view` (Cognito-bypass unified frontend) | `core/urls_unified.py:46` (routed at `core/urls_unified.py:97` as `logout/`) | HTTP endpoint | Cognito-bypass alternate logout |
| `session_tool` schema | `core/services/pa_tool_schemas.py:4719-4798` | PA tool schema | 7 actions enum: `health_check` / `create_fresh` / `list_recent` / `whoami` / `retire` / `set_active` / `seed` |
| `session_tool` handler | `core/services/td_handlers_core.py:3868-4163` | PA tool handler | 7-action `elif` branch at lines 3868 (health_check top) + 3881 (create_fresh) + 3930 (list_recent) + 3961 (whoami) + 4011 (retire) + 4074 (set_active) + 4109 (seed) |
| `session_tool.retire` action | `core/services/td_handlers_core.py:4011-4072` | PA tool handler action | Bulk `session_active=False` update; user-scoped; guards currently-bound conversation without `force=true` |
| `ChatConversation.session_active` field | `core/models/conversations/models.py:139-143` | Django model field | BooleanField default=True; db_index=True; retention flag |
| `AgentFollowupSubscription.expires_at` field | `core/models_unified_system.py:1063-1073` | Django model field | NULL = auto-wake (execution-lifecycle-bound); non-NULL = TTL-bounded (MAX_TTL_SECONDS=600) |
| `expire_stale_followup_subscriptions` beat task | `core/tasks.py:13444-13470` | Celery beat task | TTL cleanup for non-NULL-expires_at rows in `state=armed`; queue=`broadcast` |
| `MobilePushToken.revoked_at` field | `core/models_mobile.py:25` | Django model field | Nullable; NOT set by any logout endpoint at HEAD (verified) |
| `authStore.logout()` (client) | `frontend/src/stores/authStore.ts:34-39` | Client Zustand action | Sets token/user/isAuthenticated to null; NO paStore.reset() call; NO session_tool.retire() RPC |
| `paStore.syncUser(null)` (client) | `frontend/src/stores/paStore.ts` | Client Zustand action | Wipes 5-of-16 fields (Cat B §4.1 F-B4 evidence); 2 UNKNOWN intent + 9 not wiped |
| `Clear-Site-Data` header emission | `core/*.py` — **DOES NOT EXIST at HEAD** (0 emission per S2403 §14 F-C-CSD-1 preserved) | HTTP response header | Not emitted at any logout endpoint |
| Refresh-token endpoint | `core/*.py` — **DOES NOT EXIST at HEAD** (per S2403 §14 F-C-REFRESH-1 preserved) | HTTP endpoint | Not a first-party endpoint; only third-party OAuth refresh_token at unrelated URL |

**F8 baseline codification test at PA session-lifecycle:**

| Check | Result | Evidence |
|---|---|---|
| ADR declaring session-lifecycle policy | NEGATIVE | No `docs/decisions/` or `docs/adr/` file mentions PA session-lifecycle |
| `docs/topics/personal-assistant.md` §Session-lifecycle subsection | NEGATIVE | No such subsection exists at HEAD |
| CLAUDE.md §Working with Rigby session-lifecycle declaration | NEGATIVE | No session-lifetime or retention statement |
| PA conversation retention window declaration | NEGATIVE | 24-hour lookback hardcoded in `ChatConversation.get_or_create_session()` at `core/models/conversations/models.py:212` but NOT documented as retention policy |
| Arc-pin lifecycle declaration | NEGATIVE (in codebase); PARTIAL (in playbook §16 arc-standard behavior) | Playbook §16 declares arc-standard behavior for RESEARCH pins; no codebase-wide arc-pin lifecycle documentation |

**F8 verdict for C2: NEGATIVE at HEAD.** PA-override (arc-pin lifetime decoupled from user-session per playbook §16) is not declared anywhere in codebase or PA topic docs. Cat C records evidence; Cat C does NOT recommend verdict.

## 4. Major Models

**Playbook §9 canonical Q4-Q5 — What are the major models + how do they relate?**

**Cat C boundary: models participating in C1 workspace-membership resolution + C2 session-lifecycle state.** Full PA persistence inventory is out of Cat C scope; Cat C records only workspace/lifecycle-relevant subset.

### 4.1 C1 workspace-context authz relevant models

| Model | File:line | Role in C1 evidence | Contract-declaration state |
|---|---|---|---|
| `ProjectWorkspace` | `core/models_skin_layer.py:31-214` | Workspace container; `user` OneToOneField (line 55-59; single owner per workspace); `is_active` UniqueConstraint (line 196-201; only one active per user) | Field-shape hand-constructed at REST; no ModelSerializer binding for workspace-context declaration |
| `AssistantProfile.workspace` | `core/models_assistant_profile.py:122-129` | Nullable FK to `ProjectWorkspace`; `on_delete=SET_NULL`; `related_name='assistant_profiles'`; optional workspace-pinning for PA mode | Not directly REST-exposed at PA-path; used internally for workspace-mode resolution |
| `ChatConversation.workspace` | `core/models/conversations/models.py:146-154` | Nullable FK to `ProjectWorkspace`; `on_delete=SET_NULL`; `db_index=True`; `related_name='chat_conversations'` | Optional conversation-to-workspace binding at creation time |
| `WorkspaceOperation` | Referenced in workspace-write audit trail (CASCADE from ProjectWorkspace) | Operation history per workspace | Not currently emitted at `execute_with_workspace()` dispatch (per §14.1 D3 drift finding) |
| `WorkspaceContext` | Referenced (CASCADE from ProjectWorkspace) | Extended workspace context | Cat C boundary — not directly involved in C1 membership check |
| **`WorkspaceMember`** | **DOES NOT EXIST at HEAD** (0 matches for `^class WorkspaceMember` across `core/*.py`) | Would-be membership junction table | Path A adoption requires CREATING this model (or equivalent) |

**Cat C1 observation:** Workspace membership at HEAD is a **user-owns-workspace** relationship via `ProjectWorkspace.user` OneToOneField, NOT a **member-of-workspace** relationship via a junction table. Path A adoption would either:
- Wrap the existing single-owner semantics into a `WorkspaceMember` façade (workspace's single user = single member), or
- Extend workspace to support multi-user membership + backfill existing single-owner rows.

Either sub-path is post-verdict implementation scope; Cat C records the design constraint per boundary discipline.

### 4.2 C2 PA session-lifecycle relevant models

| Model | File:line | Role in C2 evidence | Contract-declaration state |
|---|---|---|---|
| `ChatConversation.session_active` | `core/models/conversations/models.py:139-143` | BooleanField default=True; db_index=True; session resumption gate | 24-hour lookback hardcoded at `get_or_create_session()` line 212 as retention window (Explore Agent 1 evidence) |
| `ChatConversation.user` | `core/models/conversations/models.py:68-75` | ForeignKey nullable; retention scope | User-scoped retention per S2403 §9.2 CF-C2 |
| `ChatConversation.created_at` | `core/models/conversations/models.py:169` | DateTimeField auto_now_add | Only timestamp field — **no `updated_at`** (Agent 1 gap finding); session last-touch NOT tracked |
| `ConversationMemory` | `core/models/conversations/models.py:19-56` | Per-user conversation history; no TTL; no explicit cleanup policy | Retention policy UNDECLARED |
| `AgentFollowupSubscription` | `core/models_unified_system.py:1017-1115` | Per-execution completion wake subscription; state machine (armed → fired/expired/cancelled) | TTL policy: NULL = auto-wake execution-lifecycle-bound; non-NULL = MAX_TTL_SECONDS=600 (line 1064-1065) |
| `AgentFollowupSubscription.conversation_id` | `core/models_unified_system.py:1077` | CharField denormalized reference to ChatConversation | Not FK; string-scoped lookup |
| `MobilePushToken.revoked_at` | `core/models_mobile.py:25` | DateTimeField nullable; device notification revocation | NOT set by any logout endpoint at HEAD (S2403 CF-C4 gap preserved) |

**Cat C2 observation:** Retention policy is fragmented across at least 4 models (ChatConversation, ConversationMemory, AgentFollowupSubscription, MobilePushToken) with **no unified retention-window declaration**. C2 verdict (α/β/γ/PA-override) selects the coupling policy across these; Cat C records fragmentation evidence.

## 5. Major Services

**Playbook §9 canonical Q4-Q5 — What are the major services?**

**Cat C boundary: services participating in C1 workspace-membership resolution + C2 session-lifecycle mutation.**

### 5.1 C1 workspace-context authz relevant services

| Service | File:line | Role at C1 boundary |
|---|---|---|
| `execute_with_workspace()` | `core/agents/base_agent.py:5355` | F-B-HIGH-3 implicit-gate host method; wraps `execute()` with post-execution `_write_files_to_workspace()` call (per Agent 2 evidence) |
| `_write_files_to_workspace()` | `core/agents/base_agent.py:5161-5227` (per Agent 2 evidence) | Delegates to `manager.get_active_workspace()`; enforces `workspace.allow_file_write` flag (line 5188-5200) |
| `_get_workspace_manager()` | `core/agents/base_agent.py:5075-5105` (per Agent 1 evidence) | Instantiates `WorkspaceManager(user=target_user)`; fail-open if manager init fails |
| `WorkspaceManager.get_active_workspace()` | `core/services/workspace_manager.py:1697` (verifier-corrected from :1710) | Actual membership check delegate: filters `ProjectWorkspace.objects.filter(user=self.user, is_active=True)` |
| WORKSPACE_AWARE_AGENTS dispatcher | `core/epa_handlers_tools.py:3873-3922` | Gate + branch: `if agent_name in WORKSPACE_AWARE_AGENTS and write_to_workspace:` → `execute_with_workspace()`; otherwise fall back to `router.route()` |
| `UnifiedTokenAuthenticationMiddleware` | `core/auth_middleware.py:85` (per S2504 §Cat D reference) | Path-list gate evaluator; runs BEFORE DRF permission-class dispatch; does NOT check workspace-membership for PA-path (0 PA-path coverage in 285-entry registry) |
| `FleetSignatureAuthentication` | `core/services/fleet_auth_drf.py:65-220` (per Cat A §5.4 + Agent 4 evidence) | Auth mixin; sets `request.fleet_identity` dict — does NOT convey workspace_id (Agent 4 gap finding) |
| **`WorkspaceMember` DRF permission class** | **DOES NOT EXIST at HEAD** | Path A adoption requires CREATING (or naming a workspace-permission analog); no `IsWorkspaceMember` / `WorkspacePermission` class exists |

**Cat C1 service-layer observation:** The membership check is **twice-delegated** from HTTP boundary (DRF `IsAuthenticated`) → handler-internal (`execute_with_workspace()`) → service-layer (`WorkspaceManager.get_active_workspace()`). This is the F-B-HIGH-3 implicit-gate depth chain. Path C+compensating audit-log hook design must fire at ONE of these three layers with documented emission spec.

### 5.2 C2 PA session-lifecycle relevant services

| Service | File:line | Role at C2 boundary |
|---|---|---|
| `session_tool` handler | `core/services/td_handlers_core.py:3868-4163` | 7-action PA tool handler; user-scoped bulk updates |
| `session_tool.create_fresh` | `core/services/td_handlers_core.py:3881-3928` | Creates new `pa-` prefixed conversation_id; inserts one ChatConversation row (session_active defaults True); returns conversation_id + starter_prompt |
| `session_tool.retire` | `core/services/td_handlers_core.py:4011-4072` | Bulk UPDATE `session_active=False` for user-scoped conversation_id rows; refuses currently-bound arc pin without `force=true`; returns pin_rotation_notice if `force=true` on currently-bound |
| `session_tool.set_active` | `core/services/td_handlers_core.py:4074-4107` | Bulk UPDATE `session_active=True`; inverse of retire; oops-rollback path |
| `session_tool.seed` | `core/services/td_handlers_core.py:4109-4163` | Backfill starter context via SYSTEM SEED message insert; user-scoped |
| `session_tool.whoami` | `core/services/td_handlers_core.py:3961-4009` | Read-only user identity + optional conversation ownership query |
| `session_tool.list_recent` | `core/services/td_handlers_core.py:3930-3960` | Read-only recent conversations list |
| `session_tool.health_check` | `core/services/td_handlers_core.py:3868-3879` (top-of-handler early branch) | Read-only session health snapshot |
| `logout_view` (basic) | `core/auth_views.py:85-94` | `request.user.auth_token.delete()`; NO PA state mutation |
| `logout_enhanced_view` | `core/auth_views_enhanced.py:541-556` | Enhanced logout; exception swallowing (degraded); NO PA state mutation |
| `logout_view` (Cognito-bypass) | `core/urls_unified.py:46` | Alternate logout; NO PA state mutation |
| `UnifiedPAEntrypoint.process_message()` | `core/services/unified_pa_entrypoint.py:552` (per Cat A §7.1) | Injects `self.conversation_id` + `_bound_conversation_id` sentinel into every tool call (line 1771-1773 per Agent 2 evidence); decouples arc-pin conversation from user-session token |
| `expire_stale_followup_subscriptions` task | `core/tasks.py:13444-13470` | Non-NULL-TTL AgentFollowupSubscription cleanup; state=armed + expires_at<=now → state=expired |

**Cat C2 service-layer observation:** All 7 `session_tool` actions are user-scoped (require `user_id`); NONE cross-user; `retire` guards currently-bound conversation with `force=true` requirement + pin_rotation_notice. The `_bound_conversation_id` sentinel injection at UnifiedPAEntrypoint line 1771-1773 is the mechanism enabling `retire`'s currently-bound guard — critical for playbook §16 arc-pin lifecycle discipline.

## 6. Major APIs and Interfaces

**Playbook §9 canonical Q6 — What are the major APIs?**

**Cat A + Cat B canonical artifact citation discipline (§16.4 Cat-C-7 anti-scope):** Cat C DOES NOT re-inventory PA-path endpoints. Cat A §6.1 F11 34-row canonical inventory is the AUTHORITATIVE denominator; Cat C filters it for workspace-scoped-data-touching subset (see §6.1 below).

### 6.1 C1 workspace-scoped-data-touching PA-path endpoint subset (Cat A F11 34-row FILTER)

**F-C3 fold ratified 2026-07-06 — workspace-touching subset rule (auditable at S2699 xx99):**

An endpoint or agent "touches workspace" iff **at least one of the following holds**:
1. Calls `WorkspaceManager.get_active_workspace()` (directly or via `execute_with_workspace()` delegation chain).
2. Dispatches an agent in `WORKSPACE_AWARE_AGENTS` (via `core/epa_handlers_tools.py:3909` gate).
3. Reads or writes any `ProjectWorkspace`-bound model row (ProjectWorkspace itself, WorkspaceOperation, WorkspaceContext, WorkspaceTrigger, AssistantProfile with non-null workspace, ChatConversation with non-null workspace, or PA-produced deliverable/artifact rows carrying `workspace_id` FK per §8.7).

Adjacent-bypass candidates (out of Cat C scope, flagged as adjacent risk per Rigby SIGN Batch 1 Q1b): Django admin surfaces, management commands, Celery tasks that call agent execution directly — none of these are PA-path endpoints, so out-of-scope for Cat C but named for cross-arc awareness.

Per Explore Agent 3 evidence + parent-Claude verifier cross-check:

| Cat A row # | Method | Path | View | Workspace-Scoped-Data Touch | Enforcement Layer |
|---|---|---|---|---|---|
| 16 | POST | `/api/pa/chat/` | `unified_pa_chat` | **DIRECT** (reads `request.data['workspace_id']` at `core/views_personal_assistant.py:446-450`; validates ProjectWorkspace lookup with warn-only on failure) | Handler-internal (validation is warn-log only, not 403 return) |
| 1 | GET | `/api/v1/assistant/context/` | `assistant_context` | **INDIRECT** (context read may traverse workspace via UnifiedPAEntrypoint dispatch) | Handler-internal (implicit) |
| 19 | GET | `/api/pa/context/` | `unified_pa_context` | **INDIRECT** (agentic handler reads workspace state) | Handler-internal (implicit) |
| 20 | GET | `/api/pa/conversations/` | `list_pa_conversations` | **INDIRECT** (conversation list scoped to user; workspace not explicitly filtered at REST) | Handler-internal (implicit) |
| 22 | GET | `/api/pa/conversations/<id>/` | `get_pa_conversation` | **INDIRECT** (conversation may bind to workspace via ChatConversation.workspace FK) | Handler-internal (implicit) |
| 23 | POST | `/api/pa/conversations/<id>/message/` | `pa_conversation_post_message` | **INDIRECT** (message storage scoped to user conversation; workspace dispatch internal) | Handler-internal (implicit) |
| 24 | GET | `/api/pa/conversations/<id>/messages/` | `pa_conversation_messages` | **INDIRECT** (message read scoped to user conversation) | Handler-internal (implicit) |
| 25 | GET | `/api/pa/activity/` | `pa_activity_feed` | **INDIRECT** (ToolCallRecord source; may include workspace context) | Handler-internal (implicit) |
| 21 | POST | `/api/pa/conversations/new/` | `create_pa_conversation` | **NO** (conversation_id generation only) | N/A |
| 26 | GET | `/api/pa/conversations/<id>/health/` | `session_health` | **NO** (freshness score; not workspace-scoped) | N/A |
| 27 | POST | `/api/pa/boardroom/maintenance/` | `trigger_boardroom_maintenance` | **NO** (staff-only; not workspace-scoped) | Handler-internal `is_staff` check |
| 18 | POST | `/api/pa/feedback/` | `pa_message_feedback` | **NO** (feedback on messages; user-scoped, not workspace-scoped) | N/A |
| 28 | POST | `/api/pa/voice_session/` | `f2f_create_voice_session` | **NO** (F2F session allocation) | N/A |
| 29 | POST | `/api/pa/voice_session/<id>/speak/` | `f2f_speak_voice_session` | **NO** | N/A |
| 30 | POST | `/api/pa/voice_session/<id>/end/` | `f2f_end_voice_session` | **NO** | N/A |
| 2-15, 17 | (mixed) | `/api/(v1/)assistant/*` compat prefixes | (various) | **INDIRECT** (compat routes may traverse workspace via UnifiedPAEntrypoint dispatch) | Handler-internal (implicit) |
| 31-34 | (mixed) | `/api/assistant/dev/*` + `/api/assistant/minimal/*` | (dev/minimal, view def-site UNKNOWN per Cat A §14 gap) | **UNKNOWN** | UNKNOWN |

**C1 workspace-scoped-data touch summary at HEAD:**
- **DIRECT (REST-boundary reads `workspace_id`):** 1 row (`/api/pa/chat/` row 16).
- **INDIRECT (handler-internal traversal):** ~8-12 rows (all `/api/(pa|assistant|v1/assistant)/*` message + context + conversation + activity routes that route through UnifiedPAEntrypoint agentic dispatch).
- **NO workspace-scoped-data touch:** ~14 rows (create-conversation, feedback, voice-session lifecycle, F2F routes, staff-only boardroom, health/status polling).
- **UNKNOWN:** 4 rows (dev/minimal variants).

**C1 denominator disposition (evidence-only per AC-C1-2 F-C2 fold):** For each of the 20 `WORKSPACE_AWARE_AGENTS` at `core/epa_handlers_tools.py:3873-3907` AND each workspace-scoped-data-touching PA-path endpoint (~9-13 direct + indirect rows above), workspace enforcement declaration point at HEAD is:

- **Permission-class layer:** NONE (0 endpoints; 0 agents declare workspace-membership via DRF class)
- **Middleware path-list gate:** NONE (0 endpoints; 0 agents covered by 285-entry `core/auth_middleware.py` registry)
- **Handler-internal (implicit):** 20 agents (100%; via `execute_with_workspace()` at `core/agents/base_agent.py:5355` + `_write_files_to_workspace()` + `WorkspaceManager.get_active_workspace()` at `core/services/workspace_manager.py:1697`) + ~9-13 endpoints (via UnifiedPAEntrypoint dispatch)
- **None:** 0 (or 4 UNKNOWN dev/minimal — verification next-step)

**0 UNKNOWN on existence-of-declaration (F-C2 fold discipline target met):** every workspace-scoped-data-touching endpoint + every WORKSPACE_AWARE_AGENTS entry has a categorized enforcement point at HEAD.

### 6.2 C2 session-lifecycle-relevant PA tool schemas + handlers

Per Explore Agent 3 evidence + parent-Claude verifier cross-check:

| PA tool | Schema | Handler | C2 relevance |
|---|---|---|---|
| `session_tool` | `core/services/pa_tool_schemas.py:4719-4798` | `core/services/td_handlers_core.py:3868-4163` (7 actions) | **DIRECT** — session_active mutation + create/retire/seed/whoami/list_recent |
| `workspace_tool` | `core/services/pa_tool_schemas.py:822-914` | `core/services/td_handlers_agents.py:1115` (per Agent 3 evidence) | **INDIRECT** — workspace CRUD + workspace_id filter for deliverable scope |
| `deliverable_tool` | `core/services/pa_tool_schemas.py:3392-3450` | (handler location per Agent 3) | **INDIRECT** — workspace_id filter param at line 3432; `orphans` logic scoped to workspace-null |
| `initiative_tool` | `core/services/pa_tool_schemas.py:1100-1200+` | (handler location per Agent 3) | **INDIRECT** — `target_workspace_id` param for initiative updates |
| `autopilot_tool` | `core/services/pa_tool_schemas.py:2371-2430` | (handler location UNKNOWN — verifier next-step) | **INDIRECT** — `workspace_metrics` action reads per-ProjectWorkspace stats |

**C2 tool observation:** 5 PA tools touch workspace state; only `session_tool` directly mutates PA conversation lifecycle. The 4 workspace-adjacent tools (`workspace_tool`, `deliverable_tool`, `initiative_tool`, `autopilot_tool`) are OUT of C2 scope but demonstrate that **workspace_id propagation is the primary C2 coupling axis** for PA-adjacent state.

### 6.3 C2 logout endpoints inventory

Per Explore Agent 3 + Agent 4 evidence + parent-Claude verifier cross-check (verifier §14 correction #4):

| # | Method | Path | View | File:line | Response envelope | Response code | PA State Mutation |
|---|---|---|---|---|---|---|---|
| 1 | POST | `/api/v1/auth/logout/` | `logout_view` | `core/auth_views.py:85-94` | `{"detail": "Successfully logged out"}` or fallback | 200 | **NO** — deletes DRF Token only |
| 2 | POST | `/api/v1/auth/logout-enhanced/` | `logout_enhanced_view` | `core/auth_views_enhanced.py:541-556` | `{"message": "Logged out successfully"}` | 200 | **NO** — deletes token; swallows exceptions (degraded) |
| 3 | GET/POST | `/accounts/logout/` (Cognito-bypass unified) | `logout_view` (unified variant) | `core/urls_unified.py:46,97` | Django session.flush + redirect | 302 | **NO** — flushes Django session |

**C2 logout observation:** **ZERO logout endpoints mutate PA conversation state or call `session_tool.retire` iteration.** No `Clear-Site-Data` header emission at any endpoint (S2403 §14 F-C-CSD-1 preserved at HEAD). This is the CURRENT state; C2 verdict (α/β/γ/PA-override) at S2699 xx99 determines whether this decoupling is intentional (PA-override) or gap (α + refresh mechanism + logout cleanup coupling).

### 6.4 C2 PA `pa` Celery queue tasks

Per Explore Agent 3 evidence:

| Task | Queue | Lines | C2 relevance |
|---|---|---|---|
| `process_pa_chat_task` | `pa` | `core/tasks.py:11912-11914`; impl `core/tasks_misc.py:4672+` | Creates ChatConversation row per message |
| `rebuild_pa_context_task` | `pa` | `core/tasks.py:11920-11930` | Rebuilds PA context caches; lock-based stampede prevention |
| `expire_stale_followup_subscriptions` | `broadcast` | `core/tasks.py:13444-13470` | AgentFollowupSubscription TTL cleanup; NOT tied to user logout |

**C2 task observation:** 3 `pa`-queue tasks; NONE tied to user-logout event. Retention cleanup is TTL-based only (AgentFollowupSubscription). No task iterates `session_tool.retire` for retention-window enforcement.

## 7. Runtime Flows

**Playbook §9 canonical Q9 — What are the major runtime flows?**

### 7.1 C1 workspace-scoped PA dispatch flow (10-step; Cat A §7.1 pattern inheritance)

Per Explore Agent 2 evidence + parent-Claude verifier cross-check:

1. **HTTP POST** `/api/pa/chat/` request arrives at `core/views_personal_assistant.py:267`.
2. **View auth:** DRF auth chain validates token/session via `UnifiedTokenAuthenticationMiddleware` → sets `request.user`. Middleware path-list gates evaluated at `core/auth_middleware.py`; **0 PA-path prefixes in 285-entry registry** — PA-path skips middleware gating; falls through to DRF permission-class layer.
3. **Permission class:** `@permission_classes([IsAuthenticated])` at PA view (line 32); passes if authenticated. **NO workspace-membership check at REST boundary.**
4. **View handler:** `unified_pa_chat(request)` extracts message, conversation_id, `workspace_id` from `request.data` (line 302-308 + 446).
5. **VIP scope check:** `get_vip_scope(request)` may inject workspace_id (line 317-324). Two channels merged.
6. **Workspace validation (warn-only):** `ProjectWorkspace.objects.get(id=workspace_id)` at line 446-450; **on failure, logger.warning + workspace_id set to None fallback** — request proceeds without 403.
7. **Celery dispatch:** `process_pa_chat_task.delay(...)` to `pa` queue; returns HTTP 200 immediately with `{"success": True, "task_id": "<uuid>", "status": "processing"}`.
8. **Celery worker:** `UnifiedPAEntrypoint(user, conversation_id)` init at `core/services/unified_pa_entrypoint.py:552`. Auto-inject `_bound_conversation_id` sentinel + `workspace_id` into every tool call arguments (line 1771-1795 per Agent 2 evidence).
9. **PA agentic loop:** LLM function-calling; tool dispatch to `WORKSPACE_AWARE_AGENTS`-gated handler at `core/epa_handlers_tools.py:3909`. **IF** `agent_name in WORKSPACE_AWARE_AGENTS AND write_to_workspace=True`: dispatch `execute_with_workspace()` at `core/agents/base_agent.py:5355`; **ELSE** fall back to `router.route()`.
10. **Membership resolution (implicit-gate host):** `execute_with_workspace()` calls `execute()` first (standard agentic run) then `_write_files_to_workspace()` at line 5161+. Latter delegates to `WorkspaceManager.get_active_workspace()` at `core/services/workspace_manager.py:1697` which returns `ProjectWorkspace.objects.filter(user=self.user, is_active=True)`. **If no active workspace → return early with `'reason': 'No active workspace'`** (fail-open on non-workspace-write path). **If active workspace but `allow_file_write=False` → return early with `'reason': 'Workspace does not allow file writes'`** (fail-open on permission-flag-blocked writes). **This is the F-B-HIGH-3 implicit-gate resolution point.**

### 7.2 C1 workspace-context enforcement observation (F-B-HIGH-3 attribution)

**Implicit-gate depth chain (verifier §14 evidence):**
1. HTTP DRF `IsAuthenticated` (all 34 PA-path endpoints uniformly)
2. Middleware path-list gate: **SKIPPED** (0 PA-path coverage in 285 entries)
3. Handler-internal (`execute_with_workspace()` at base_agent.py:5355) — F-B-HIGH-3 boundary evidence baseline
4. Service-layer (`WorkspaceManager.get_active_workspace()` at workspace_manager.py:1697) — actual membership-check delegate

**Fails-closed observation (Rigby SIGN Batch 1 Q2a clarifier ratified 2026-07-06):** `execute_with_workspace()` fails closed on the workspace-write path: `_write_files_to_workspace()` at `core/agents/base_agent.py:5175-5186` returns early with `{'success': False, 'written': False, 'reason': 'No active workspace. Register a workspace first.'}` if `manager.get_active_workspace()` returns None (no active workspace found for the user). Similarly at line 5188-5200, `_write_files_to_workspace()` returns early with `{'reason': 'Workspace does not allow file writes'}` if `workspace.allow_file_write=False`. Both are structured error dicts, NOT silent-degrade — the runtime does NOT default to a fallback workspace on missing/inactive workspace. This is a design-critical invariant for Path C+compensating audit-log hook design: the emit point can capture the fail-closed decision without needing to distinguish "no membership" from "wrong workspace" upstream (both cases converge at the same return-early branch).

**Membership-check semantics:** user-owns-workspace (`ProjectWorkspace.user` OneToOneField) — NOT member-of-workspace (no junction table exists at HEAD; see DEBT-C1-7). Path A adoption requires either extending workspace model or wrapping single-owner semantics in a `WorkspaceMember` façade.

**workspace_id provenance (DEBT-C1-8 evidence):** The `workspace_id` reaching `_write_files_to_workspace()` may come from at least 5 sources: (i) HTTP request payload `workspace_id` field (Cat A §7.1 flow evidence + `core/views_personal_assistant.py:446-450`); (ii) VIP scope injection via `get_vip_scope(request)` at line 317-324; (iii) `AssistantProfile.workspace` FK per-user default (`core/models_assistant_profile.py:122-129`); (iv) agent-internal state (per-agent context.workspace_id key); (v) `WorkspaceManager.get_active_workspace()` fallback lookup of user's `is_active=True` workspace. Sourcing precedence is UNDECLARED at HEAD — critical for observability + Path C+compensating audit-log hook design (compensating control (i) must record which provenance chain produced the write).

**Cross-transport consistency check (AC-C1-4 F12 T7 inheritance):** REST-side C1 verdict on workspace-authz declaration is **ORTHOGONAL** to Cat D S2604 WS channel authentication handshake unless coupling evidence surfaces. WS channels for PA (chat-response streaming + task-status broadcast + rigby.tool.* lifecycle per Cat B §6.2) reuse SessionAuthentication + TokenAuthentication path per S2504 baseline; workspace-membership at WS layer is **UNKNOWN pre-Cat D S2604** (Cat D scope, not Cat C).

**C1 REST↔WS consistency statement (AC-C1-4 F12):** *"At HEAD `2a3bc20d`, PA REST-side workspace-context enforcement is handler-internal implicit-gate at `execute_with_workspace()`; WS-side enforcement is UNKNOWN pending Cat D S2604 evidence. Cat C1 verdict on Path A/B/C+compensating at REST is ORTHOGONAL to Cat D WS verdict unless S2604 opening surfaces coupling evidence (e.g., shared `WorkspaceMember` permission class enforced at both REST + WS handshake). If Chris ratifies Path A (WorkspaceMember DRF class) at C1, Cat D S2604 has a natural coupling axis to consider for WS-side symmetry."*

### 7.3 C2 PA session-lifecycle runtime flow (logout → PA state)

Per Explore Agent 2 + Agent 4 evidence:

**Logout flow (client + server):**
1. **User clicks logout** at `frontend/src/components/layout/Sidebar.tsx:356` — invokes `setUserMenuOpen(false)` + `syncUser(null)` + `logout()` sequentially.
2. **`syncUser(null)`** at `frontend/src/stores/paStore.ts` — wipes 5-of-16 fields (`messages`, `activeConversationId`, `conversations`, `currentInput`, `conversationsLoading`); LEAVES intact: `userId` (implicit; new user_id triggers wipe) + `isDockOpen` + `isDockMinimized` (UNKNOWN intent) + `currentPage` + `isSidebarOpen` + `activeTool` + `recentTool` + `seenSeqs` + `recentAgentCompletion` + `agentCompletionQueue` + `seenCompletions`.
3. **`authStore.logout()`** at `frontend/src/stores/authStore.ts:34-39` — sets `token: null, user: null, isAuthenticated: false`; **NO `paStore.reset()` call; NO `session_tool.retire()` RPC**.
4. **HTTP POST `/api/v1/auth/logout/`** — reaches `logout_view` at `core/auth_views.py:85`; deletes `request.user.auth_token.delete()`; returns 200.
5. **Server-side:** **NO ChatConversation `session_active` mutation; NO `session_tool.retire` iteration; NO MobilePushToken `revoked_at` set.** PA state persists indefinitely.
6. **Post-logout state:** User's PA arc-pin conversation_ids remain `session_active=True` in DB; `paStore` retains 11-of-16 fields in localStorage; `pa-dock-state` Zustand persist key survives; user's PA notification tokens remain "active" for Expo push service (revoked_at IS NULL).

**Refresh flow:** **DOES NOT EXIST at HEAD.** S2403 §14 F-C-REFRESH-1 preserved: no first-party refresh-token endpoint. Client-side silent-401 interceptor at `api.ts:43-62` (Cat B §5.1) does NOT retry with refresh; non-whitelist 401s `Promise.reject(error)` uniformly.

**Arc-pin rotation flow (playbook §16 arc-standard behavior):**
1. **Arc close:** Research session closes arc (e.g., S2599 Group 2500 close) → `session_tool.retire` invoked on arc pin (verified working per S1301 memory rule `feedback_session_tool_retire_works.md`).
2. **Currently-bound guard:** If arc pin === `_bound_conversation_id`, retire refuses without `force=true` (per `core/services/td_handlers_core.py:4031-4051`); returns `pin_rotation_notice` requesting `tools/pa_local.sh` line 348 rotation.
3. **Post-rotation:** `tools/pa_local.sh:348 --conversation` updated to new arc pin; `platform_config_tool overview` verifies rotation.

**C2 arc-pin lifecycle observation:** PA arc-pin lifecycle is **DECOUPLED from user-session lifecycle** at HEAD by design (verified: 0 logout endpoints mutate arc-pin state). This matches playbook §16 arc-standard behavior. Whether this decoupling IS the PA-override (C2 verdict) or is unintended gap is Chris-D-verdict scope at S2699 xx99.

## 8. Data Ownership and Lifecycle

**Playbook §9 canonical Q16-Q18 — What data does Cat C scope own / consume / produce?**

### 8.1 C1 data owned (workspace-context authz)

- `WORKSPACE_AWARE_AGENTS` constant (20-string list at `core/epa_handlers_tools.py:3873-3907`) — source-of-truth for workspace-write dispatch.
- `execute_with_workspace()` method body (`core/agents/base_agent.py:5355+`) — F-B-HIGH-3 implicit-gate host.
- `WorkspaceManager` instance state (`core/services/workspace_manager.py`) — per-user workspace resolution.
- `ProjectWorkspace` model row(s) — one active per user (UniqueConstraint at `core/models_skin_layer.py:196-201`).

### 8.2 C1 data consumed

- HTTP request auth headers (`Authorization: Token <token>`) via DRF authentication chain.
- Request payload `workspace_id` field (at `/api/pa/chat/` — line 446-450).
- VIP scope context (via `get_vip_scope(request)` at line 317-324).
- `AssistantProfile.workspace` FK (optional workspace-pinning per user profile).
- 285 path-list gate entries (evaluated at middleware — SKIPPED for PA-path).

### 8.3 C1 data produced

- Handler dispatch outcome — either `execute_with_workspace()` path (workspace write) or `router.route()` path (non-workspace).
- Workspace write result dict (`{'written': bool, 'reason': str, 'workspace': str, ...}`) at `_write_files_to_workspace()` return.
- **NO audit-log emission at HEAD** (Cat A §5.1 D3 drift preserved — Cat C §14.1 D3 preserved).

### 8.4 C2 data owned (PA session-lifecycle)

`ChatConversation` table rows keyed by `conversation_id` × `user_id`:
- `session_active` BooleanField (default=True; db_index=True) — lifecycle gate.
- `created_at` DateTimeField (auto_now_add) — only timestamp field (no `updated_at`).
- `user` ForeignKey (nullable) — retention scope.
- `workspace` ForeignKey (nullable, SET_NULL) — optional workspace binding.
- `session_title` CharField — auto-generated per session.

`AgentFollowupSubscription` table rows keyed by `execution × conversation_id`:
- `state` CharField (`armed` / `fired` / `expired` / `cancelled`) — subscription lifecycle.
- `expires_at` DateTimeField nullable — NULL = auto-wake execution-lifecycle-bound; non-NULL = TTL-bounded (MAX_TTL_SECONDS=600).
- `fired_at` DateTimeField nullable.
- `result_payload` JSONField — snapshot of agent.completed.

`paStore` client-side 16 fields (Cat B §4.1 F-B4 canonical artifact — CITE):
- 7 localStorage-persisted (userId, isDockOpen, isDockMinimized, messages, currentInput, activeConversationId, isSidebarOpen).
- 9 memory-only (currentPage, conversations, conversationsLoading, activeTool, recentTool, seenSeqs, recentAgentCompletion, agentCompletionQueue, seenCompletions).
- 5 syncUser wiped (messages, activeConversationId, conversations, currentInput, conversationsLoading).
- 2 UNKNOWN intent (isDockOpen, isDockMinimized) — **C2 verdict-scope target per parent §3.C2 + AC-C2-4**.
- 9 not wiped by syncUser at HEAD.

### 8.5 C2 data consumed

- User-scoped conversation_id inputs (from `_bound_conversation_id` sentinel injection at UnifiedPAEntrypoint line 1771-1773).
- `session_tool` action arguments (conversation_id + force + content per action).
- User authentication (from `request.user.id`).
- Group 2400 α/β/γ verdict (upstream input — **DEFERRED as of S2603 open** per Explore Agent 4 evidence).
- MobilePushToken.revoked_at UNKNOWN (no logout writes at HEAD).

### 8.6 C2 data produced

- `session_active` bulk updates (via `session_tool.retire` / `set_active`).
- New `ChatConversation` rows (via `session_tool.create_fresh` / `seed`).
- `AgentFollowupSubscription` state transitions (armed → expired via beat task; armed → fired via agent completion signal handler).
- **NO Clear-Site-Data header emission** at any logout endpoint at HEAD (S2403 §14 F-C-CSD-1 preserved).
- **NO `session_tool.retire` iteration on logout** at HEAD (Cat C §7.3 evidence).

### 8.7 Retention window declarations at HEAD

| Retention scope | Declaration point | Value | Gap |
|---|---|---|---|
| ChatConversation session resumption | Hardcoded at `get_or_create_session()` line 212 | 24 hours from `created_at` | NOT documented as retention policy; NOT parameterized |
| AgentFollowupSubscription TTL (non-NULL expires_at) | Model constants at `core/models_unified_system.py:1063-1065` | DEFAULT_TTL_SECONDS=60; MAX_TTL_SECONDS=600 | Documented via docstring; not cascade to user-logout |
| ConversationMemory retention | **UNDECLARED** at HEAD | Indefinite accumulation | No cleanup policy documented |
| MobilePushToken.revoked_at | **UNDECLARED** at HEAD | Not set on logout | S2403 CF-C4 handoff to Group 2300 Mobile |
| PA arc-pin lifecycle | **UNDECLARED at codebase; PARTIAL at playbook §16** | Playbook §16 arc-standard: retire at arc close | Not enforced by any Celery task; manual-only via `session_tool.retire` |
| paStore field retention (16 fields) | **PARTIAL at Zustand config** | 7-field partialize + syncUser 5-field wipe | 2 UNKNOWN intent + 9 non-wiped fields |

**C2 retention observation:** Retention is fragmented across at least 6 declaration points (5 with partial declaration + 1 UNDECLARED). C2 verdict (α/β/γ/PA-override) selects a UNIFIED retention-window policy or explicitly declares PA-override with the fragmentation preserved + rationale.

### 8.8 PA-produced outputs as retention-impact surfaces (F-C4 fold ratified 2026-07-06)

Per F-C4 fold ratified 2026-07-06 (SIGN cycle 1 Batch 1 Q1c STRENGTHEN), PA-produced outputs are **retention-impact surfaces** (not "state stores" per §8.4 but adjacent surfaces whose lifecycle is coupled to PA session decisions). This prevents Cat C2 retention-window discussion from being artificially narrow:

- **`Deliverable` rows** produced by PA runs — carry `workspace_id` FK (nullable); lifecycle scoped by workspace ownership; retention window UNDECLARED; cross-user visibility governed by `data_sensitivity` field. Deliverable_tool at `core/services/pa_tool_schemas.py:3392-3450` reads/writes with `workspace_id` filter (Cat C §6.2 evidence). PA-produced deliverables persist post-logout at HEAD (no logout endpoint mutates).
- **Blog/Publication rows** produced by PA content-agent runs — workspace-scoped when produced by workspace-aware agents; retention UNDECLARED.
- **DocumentEmbedding rows** produced by PA memory-persistence pipeline — Group 1300 Memory arc scope; PA-produced embeddings inherit retention decisions from Group 1300; adjacent to Cat C2 verdict-space.
- **ToolCallRecord rows** produced by every PA tool dispatch — user-scoped audit trail; NOT workspace-scoped (unless workspace_id captured in metadata); retention TTL UNDECLARED at Cat C boundary.

**Cat C2 F-C4 observation:** PA-produced output lifecycle is an INHERITED consequence of Cat C2 verdict (α/β/γ/PA-override) — if PA adopts α (silent-refresh) with logout cleanup coupling, PA-produced deliverables + blogs + embeddings become candidates for cascade retention. If PA declares PA-override (arc-pin lifetime decoupled from user-session), PA-produced outputs persist per their own lifecycle. Cat C records evidence + coupling axes; Chris-D-verdict at S2699 xx99 selects retention posture for PA-produced surfaces.

## 9. Integrations With Other Domains

**Playbook §9 canonical Q14 + Q17 + Q18 + Q21 + Q22 — Integrations.**

Per Explore Agent 4 evidence + parent-Claude verifier-loop cross-check:

### 9.1 Integration classification matrix

| Domain | Relationship | Classification | Evidence |
|---|---|---|---|
| **Auth (Group 2400)** | HTTP auth chain → workspace_id resolution at PA view; α/β/γ upstream for C2 | **STRONG (C1 mechanism) + DEFERRED (C2 verdict)** | `core/views_personal_assistant.py:16-23 + 317-324 + 446-450`; α/β/γ open per S2499 |
| **Workspace + Agent-Registry** | 20 WORKSPACE_AWARE_AGENTS × execute_with_workspace() dispatch | **STRONG** | `core/epa_handlers_tools.py:3873-3922`; agent registry via `router.get_agent_class()` |
| **Frontend (Group 2200)** | workspaceStore.activeWorkspace passed via paStore → assistantApi.paChat; paStore 16-field cleanup | **STRONG (C1 payload) + PARTIAL (C2 cleanup)** | Cat B §9 integrations + `frontend/src/components/GlobalPADock.tsx:341,351`; Cat B §4.1 F-B4 U7 |
| **API (Group 2500)** | Inherit Group 2500 baseline verdict per parent §2.6.A hard constraint | **STRONG (constraint inheritance)** | S2599 canonical summary |
| **Fleet-Federation** | FleetSignatureAuthentication conveys NO workspace_id at HEAD | **MISSING (boundary gap)** | `core/services/fleet_auth_drf.py:65-220`; anti-scope per parent §7 #7 |
| **Mobile (Group 2300)** | MobilePushToken.revoked_at NOT set on logout | **WEAK (CF-C4 handoff)** | `core/models_mobile.py:25`; S2403 §9.2 CF-C4 |
| **Discord** | 10-min TTL bridge; NO PA state mutation | **ORTHOGONAL** | S2403 §9.1 preserved; verified 0 discord-adjacent PA state touches |
| **Content (Group 1600)** | Anti-scope #6 preserved | **ORTHOGONAL** | Cat B §16.2 verified |
| **Observability (Group 1700)** | No workspace-authz audit-log OR session-lifecycle transition event emission at HEAD | **WEAK / MISSING (CF-C3 candidate)** | Cat A §14.3 preserved + S2403 CF-C3 preserved |
| **Cat D (S2604)** | Cat C1 REST-side evidence feeds Cat D WS-side authentication handshake decision | **STRONG (feeds forward — CF-D6)** | Parent §3.D + AC-C1-4 F12 T7 inheritance |
| **S2699 xx99** | Cat C1 + Cat C2 verdicts consumed for arc close | **STRONG (feeds forward)** | Parent §5.1 child mission sequence |

### 9.2 Cross-arc coordination flags (CF-C1..CF-C4 verification at S2603 open)

**F-B-HIGH-3** (S2402 origin) — **PRESERVED at HEAD `2a3bc20d`.** Workspace-membership implicit-gate location at `core/agents/base_agent.py:5355 execute_with_workspace()` + delegated resolution at `core/services/workspace_manager.py:1697`. Cat C1 owns closure verdict per parent §5.3 AC#3 F5 fold.

**CF-C2** (S2503 origin) — **FORWARDED to S2603 Cat C2.** Session-lifecycle PA handoff (session_tool.retire disposition on user logout + PA conversation retention window). S2603 records disposition options; verdict deferred to S2699 xx99.

**CF-D6** (S2504 origin) — **BOUNDARY PRESERVED at HEAD.** Cat C1 REST-side workspace-authz evidence + AC-C1-4 T7 statement contribute to Cat D S2604 WS-side ownership; dual-owner arrangement respects orthogonality unless coupling evidence surfaces.

**CF-C4** (S2403 origin) — **HANDOFF TO GROUP 2300 MOBILE preserved.** MobilePushToken.revoked_at NOT set at PA logout; mobile-slice lifecycle out-of-scope for Group 2600.

### 9.3 Group 2400 α/β/γ verdict status at S2603 open

Per Explore Agent 4 evidence (2499 canonical summary review):

**S2499 §19.1 three-option decision-space (α silent-refresh / β explicit-re-login / γ hybrid) is DEFERRED as of S2603 open** (2026-07-06). CF-C2 to Group 2600 PA is a **forwarded request, NOT a closed verdict**. Consequence for Cat C2:

- If Chris-D-verdict on Group 2400 α/β/γ lands BEFORE S2699 xx99: Cat C2 records adoption verdict + PA-slice-specific application evidence.
- If Group 2400 α/β/γ remains UNRESOLVED at S2699 xx99: Cat C2 records **"defer + constraints"** stance per F-C1 fold ratified 2026-07-06 (no ratification; PA-override with rationale trace as alternate path).

**Implication:** Cat C2 verdict path (α/β/γ adoption vs PA-override vs defer+constraints) is a THREE-WAY option, not a binary. Chris-D-verdict scope at S2699 xx99.

## 10. Event Flows

**Playbook §9 canonical Q19-Q20 — What events emitted / should be emitted?**

### 10.1 C1 events currently observed

- Log emission at WORKSPACE_AWARE_AGENTS dispatcher: `logger.info(f"Universal Agent Tool: Using workspace-aware execution for {agent_name}")` at `core/epa_handlers_tools.py:3910`.
- Log emission at workspace validation warn-only at `unified_pa_chat` line 448: `logger.warning(f"PA chat received invalid workspace_id: {workspace_id}")`.
- Log emission at fallback in `_get_workspace_manager()`: `logger.warning(f"Could not initialize WorkspaceManager: {e}")` (per Agent 1 evidence).
- **NO structured audit-log emission** on workspace-scoped dispatch (Cat A §14.3 evidence baseline + verifier §14 D3 drift preserved — `docs/PLATFORM_WHAT_IT_IS.md` audit-trail claim NOT matched by runtime).

### 10.2 C1 events that could be emitted (evidence for §19)

- **Workspace-scoped dispatch audit event** — no client-side or server-side event fires on `execute_with_workspace()` completion. Cat C1 Path C+compensating spec REQUIRES this as compensating control (i) per parent §3.C1 + §5.3 AC#3.
- **Membership-check failure telemetry** — `_write_files_to_workspace()` returns fail-open dict with `'reason': 'No active workspace'` but NO event emission. Silent-degrade risk.
- **Fleet-federation workspace-boundary crossing event** — no event when fleet-signed request touches workspace state without workspace_id declaration.

### 10.3 C2 events currently observed

- `agent.completed` WS event (Cat B §6.2) — fires from agent execution terminal; broadcasts to `pa_conversation_<conversation_id>` channel per AgentFollowupSubscription signal handler docstring (per Agent 1 evidence).
- `message.created` WS event (Cat B §6.2) — fires on ChatConversation message row insert.
- `rigby.tool.started` + `rigby.tool.completed` WS events (Cat B §6.2) — fire on tool dispatch lifecycle.
- **NO session-lifecycle transition events** — no event fires on:
  - user login / logout success/failure
  - `session_tool.retire` / `create_fresh` / `set_active` action
  - `session_active` field transition
  - PA arc-pin rotation
  - AgentFollowupSubscription state transition (armed → expired)

### 10.4 C2 events that could be emitted (evidence for §19)

- **Login/logout success/failure events** — S2403 §14 F-CRIT-2 preserved; no event emission for security telemetry. Cat C2 records; CF-C3 → Group 1700 Observability.
- **Session_tool action audit events** — retire/create_fresh/set_active mutations lack observability. PA-override C2 path would benefit from arc-pin lifecycle event emission.
- **Retention-window expiration events** — no event when ChatConversation `session_active=True` exceeds 24-hour lookback (implicit expiration; no cleanup task).

## 11. Existing Documentation

**Playbook §9 canonical Q10-Q11 — Existing documentation + prior research.**

Per Explore Agent 5 evidence:

| Doc | File:line | Cat C coverage |
|---|---|---|
| `docs/topics/personal-assistant.md` | 1-149 | **C1 workspace-enforcement subsection: DOES NOT EXIST. C2 session-lifecycle subsection: DOES NOT EXIST.** Line 15 mentions "workspace mode activates only from explicit workspace context" but does NOT declare enforcement location. |
| `docs/topics/frontend.md` | 100, 139-140 | PARTIAL — paStore + workspaceStore named; syncUser semantics NOT documented; workspace-context-loss risk NOT declared; dock-state persistence intent NOT specified. |
| `docs/PLATFORM_WHAT_IT_IS.md` | 187-228 (PA narrative) | **C1 workspace-enforcement declaration: ABSENT** from PA subsection (20 WORKSPACE_AWARE_AGENTS mentioned in SKIN context only). **C2 session-lifecycle policy: ABSENT** entirely. |
| `CLAUDE.md` | 34 (canonical route); 7-36 (Rigby coord) | Line 34 declares canonical PA route + compat routes; NO enforcement-location declaration; NO session-lifecycle statement. Line 15 declares `global` vs `workspace` mode resolution from explicit context but not the enforcement point. |
| `docs/PLATFORM_INVENTORY.md` | Autoblock | **`WORKSPACE_AWARE_AGENTS` count NOT in autoblock** at HEAD (verifier confirmed). Post-arc anchor-update candidate for S2699 xx99. |
| `docs/decisions/ADR-0001-execution-per-run-ephemeral-containers.md` | full | Unrelated (Celery execution scope); no workspace-authz or PA session-lifecycle ADR at HEAD. |
| `docs/research/domains/pa/2600_pa_domain_scoping.md` | full | DIRECT PARENT — §3.C1 + §3.C2 + §5.3 AC + §2.6 lens + §7 anti-scope. |
| `docs/research/domains/pa/2601_pa_backend_endpoint_contract_sot_design_prep_audit.md` | §6.1 F11 + §16.1 F-B-HIGH-3 + §7.2 streaming-negative | SIBLING PRIOR-CHILD Cat A — CITED as canonical artifact. |
| `docs/research/domains/pa/2602_pa_client_contract_surface_design_prep_audit.md` | §4.1 F-B4 U7 + §7.1 8-step + §15.2 CF-C2 + §16.1 F-B7 | SIBLING PRIOR-CHILD Cat B — CITED as canonical artifact. |
| `docs/research/domains/auth/2402_authorization_permission_floor_uniformity_audit.md` | §14.2 F-B-HIGH-3 + §14 F-B-BND-1 | F-B-HIGH-3 ORIGIN — CITED. |
| `docs/research/domains/auth/2403_session_lifecycle_logout_cleanup_contract_audit.md` | §5 session_tool + §7 flows + §9.2 CF-C2 + §14 F-C-* + §19.1 α/β/γ | α/β/γ ORIGIN — CITED. |
| `docs/research/domains/auth/2499_auth_canonical_summary.md` | Group 2400 arc close | α/β/γ verdict status: DEFERRED as of S2603 open. |
| `docs/research/domains/api/2504_api_permission_floor_registry_rest_ws_t7_joint_design_prep_audit.md` | §3.1 285-entry path-list gate | Path B analog reference — CITED. |
| `docs/research/domains/api/2599_api_canonical_summary.md` | Group 2500 arc close | Baseline inheritance constraint per parent §2.6.A. |
| `docs/research/domains/frontend/2204_frontend_session_state_persistence_discipline_audit.md` | §14 F5 + F6 + F7 + F8 | F5 workspaceStore in-memory + F7 paStore.syncUser incomplete — CITED. |

**Documentation gap severity per Cat C scope:** **HIGH.** Neither C1 workspace-enforcement location nor C2 session-lifecycle policy is declared at any authoritative doc anchor. Path C+compensating (C1) explicitly requires `docs/topics/personal-assistant.md` §Workspace-enforcement subsection creation (spec-only per §16.4 Cat-C-9 anti-scope; implementation is post-xx99 anchor-update cascade scope).

## 12. Research Coverage

**Playbook §12 classification.**

**PA WORKSPACE-CONTEXT AUTHZ + SESSION-LIFECYCLE research coverage at S2603 close: DEEP (upgrading toward CANONICAL as Group 2600 arc closes at S2699 xx99).**

Evidence:
- Prior Group 2400 auth arc (S2402 + S2403) provides DEEP baseline for F-B-HIGH-3 origin + α/β/γ decision-space.
- Prior Group 2500 API arc (S2504) provides DEEP baseline for 285-entry path-list gate mechanism (C1 Path B analog).
- Prior Group 2200 frontend arc (S2204) provides DEEP baseline for 15-surface session-state persistence (C2 client-side inheritance).
- Cat A (S2601) provides DEEP baseline for PA REST endpoint contract (Cat C1 workspace-scoped-data-touching subset filter).
- Cat B (S2602) provides DEEP baseline for PA-client contract (Cat C2 paStore U7 inheritance).
- This audit (S2603) contributes DEEP evidence for PA-specific C1 (workspace-authz declaration policy) + C2 (session-lifecycle policy) design-prep.
- Cat D (S2604) + S2699 xx99 will complete Group 2600 arc — expected CANONICAL at arc close.

## 13. Architecture Maturity

**Playbook §12 classification.**

**PA workspace-context authz + session-lifecycle architecture maturity at HEAD `2a3bc20d`: PARTIAL (both sub-tracks).**

Cat C distinguishes MECHANISM-layer maturity (Cat A + Cat B pattern precedent) from DECLARATION-layer maturity per playbook §13.5 correctness-vs-governance-axis framing.

### 13.1 C1 workspace-context authz plane maturity

| Axis | Rating | Rationale |
|---|---|---|
| Correctness (mechanism runtime) | **WORKING** | `execute_with_workspace()` → `WorkspaceManager.get_active_workspace()` chain confirmed operational (Cat A §7.1 evidence + Agent 2 runtime flow §7.1). 20 WORKSPACE_AWARE_AGENTS all dispatchable. No runtime failure observed. |
| Governance (declaration at REST + client boundaries) | **EXPERIMENTAL** | REST layer enforces `@permission_classes([IsAuthenticated])` only. NO `WorkspaceMember` DRF class exists. NO middleware path-list gate for PA workspace requirement. NO ADR. NO docs/topics subsection. F-B-HIGH-3 open finding preserved. |
| **Overall C1 maturity** | **PARTIAL** | MECHANISM WORKING + DECLARATION EXPERIMENTAL. Cat C1 Chris-D-verdict at S2699 xx99 determines DECLARATION-plane upgrade path. |

### 13.2 C2 PA session-lifecycle plane maturity

| Axis | Rating | Rationale |
|---|---|---|
| Correctness (mechanism runtime) | **WORKING** | 3 logout endpoints delete auth tokens successfully. `session_tool.retire` verified working per S1301. AgentFollowupSubscription TTL cleanup task operational. Basic mechanics functional. |
| Governance (declaration of lifecycle policy) | **EXPERIMENTAL** | Zero Clear-Site-Data emission (S2403 F-C-CSD-1). No refresh-token endpoint (F-C-REFRESH-1). No session_tool.retire iteration at logout. 14 of 15 client-side surfaces persist across logout. NO retention-window declaration. NO ADR. NO docs subsection. **F-C5 fold ratified 2026-07-06:** 24-hour lookback hardcoded at `core/models/conversations/models.py:212 get_or_create_session()` is a **mechanism constant** (unsurfaced, unowned, unjustified), NOT a policy declaration — does NOT upgrade C2 declaration maturity from EXPERIMENTAL. |
| **Overall C2 maturity** | **PARTIAL** | MECHANISM WORKING + DECLARATION EXPERIMENTAL. Cat C2 Chris-D-verdict at S2699 xx99 determines coupling/decoupling policy. |

**Distinguish from Cat B §13 client-side maturity:** Cat B assessed PA-client contract typing at PARTIAL (5/20 assistantApi typed = 25%). Cat C assesses ENFORCEMENT-layer maturity (C1) + LIFECYCLE-layer maturity (C2) at PARTIAL both. These are ORTHOGONAL axes per S2504 §88 discipline.

## 14. Known Drift

**Playbook §9 canonical Q27 — Drift.**

### 14.1 Drift resolved by verifier-loop pre-draft (4 corrections)

Recorded in frontmatter `verifier_loop` field. Reproduced here for §-anchor:

1. **WORKSPACE_AWARE_AGENTS at `core/epa_handlers_tools.py:3873`** (not 191-217 as Cat A companion anchor + parent scoping §2.1 line 105 cited). Cat A + parent cites reflect earlier HEAD (probably pre-S2551 refactor). Corrected at HEAD `2a3bc20d`.
2. **`WorkspaceManager.get_active_workspace()` at `core/services/workspace_manager.py:1697`** (not :1710 as Agent 1 + Agent 2 reported). Small line-drift; corrected.
3. **`session_tool` 7-action enum verified via direct grep** at HEAD (create_fresh 3881 / list_recent 3930 / whoami 3961 / retire 4011 / set_active 4074 / seed 4109 + health_check top-of-handler). Agent 3's 7-count authoritative; Agent 2's partial 5-body reproduction cross-verified.
4. **3 logout endpoints confirmed** — Agent 2 initially reported 1; Agents 3 + 4 reported 3. Direct grep confirmed 3 (`core/auth_views.py:85` + `core/auth_views_enhanced.py:541` + `core/urls_unified.py:46`).

### 14.2 Drift confirmed at HEAD (Cat C evidence)

- **`docs/PLATFORM_WHAT_IT_IS.md` claim "audit trail" for WORKSPACE_AWARE_AGENTS** — per Explore Agent 6 D3 finding. Runtime grep returns ZERO audit-log emission at `execute_with_workspace()` / `_write_files_to_workspace()` / dispatcher call sites. Severity MEDIUM. NEW DRIFT NOT PREVIOUSLY LOGGED — Cat C §19.3 MEDIUM follow-on for docs cascade OR Path C+compensating spec fulfillment.
- **`docs/topics/personal-assistant.md:15` claim "workspace mode activates from explicit workspace context"** partially drifted — statement is correct but INCOMPLETE (does not declare enforcement location). Severity LOW; documentation-gap not runtime-drift.
- **`docs/topics/personal-assistant.md` line 22 "106 tool schemas" (Explore Agent 6 D4)** — DRIFT from runtime 113. Severity MEDIUM. Already surfaced at Cat A §14.2 (104) + Cat B §14.2 (104 + 109 + 101 variants in PLATFORM_WHAT_IT_IS.md); Cat C §19.3 confirms + preserves as MEDIUM follow-on.
- **paStore.ts `isDockOpen` + `isDockMinimized` retention intent DRIFT (Explore Agent 6 D5)** — Cat B §4.1 F-B4 evidence baseline: 2 UNKNOWN intent fields NOT wiped by syncUser. Cat C2 owns retention verdict per parent §3.C2 + AC-C2-4. Severity MEDIUM; C2 verdict-scope target.

### 14.3 Drift observation from Agent 6 verify_doc_claims cross-check

Per Agent 6 evidence: `verify_doc_claims` at HEAD does NOT surface any workspace-context authz OR PA session-lifecycle claim. Declaration-layer drift detection for C1/C2 is UNMONITORED at HEAD. Cat C records + §19.3 follow-on: register workspace-enforcement + session-lifecycle claims for future drift detection.

## 15. Known Technical Debt

**Playbook §9 canonical Q26 — Technical debt.**

### 15.1 C1 workspace-context authz debt (Cat C boundary scope)

**Severity rubric note (F-C6 fold ratified 2026-07-06 — applied across §15):** HIGH severity captures two distinct classes: (a) HIGH runtime-defect risk (confirmed bug or high-probability failure), (b) HIGH decision-risk / governance-gap (ambiguous authorization semantics OR undeclared+unbounded lifecycle policy that may produce cross-user surprises DEPENDING on Chris-D-verdict at xx99). Cat C flags Class (b) items explicitly to preserve severity + accurate framing.

- **DEBT-C1-1 (HIGH):** All 34 PA-path endpoints declare `@permission_classes([IsAuthenticated])` uniformly — **NONE declare workspace-membership requirement at REST boundary**. F-B-HIGH-3 implicit-gate preserved. Path A retrofit requires `class WorkspaceMember` DRF class creation (does not exist at HEAD).
- **DEBT-C1-2 (MEDIUM):** No `IsWorkspaceMember` / `WorkspacePermission` DRF class analog exists at HEAD. Fleet auth has 3 custom Permission classes (`FleetSignatureAuthentication`, `FleetSignatureRequired`, `FleetCapabilityRequired` per Agent 6 evidence) — none workspace-scoped.
- **DEBT-C1-3 (MEDIUM):** No ADR for workspace-context enforcement policy. F-B-HIGH-3 has been open since S2402 close; no architecture decision record authored.
- **DEBT-C1-4 (HIGH):** No audit-log hook emission on workspace-scoped dispatch. `docs/PLATFORM_WHAT_IT_IS.md` audit-trail claim NOT matched by runtime. Path C+compensating spec requires this as compensating control (i). **Rigby SIGN Batch 2 Q3(e) identified DEBT-C1-4 as SINGLE MOST IMPORTANT DEBT for Chris to prioritize post-arc** — both truthfulness/compliance issue AND required compensating control if Chris selects Path C+compensating at xx99.
- **DEBT-C1-5 (MEDIUM):** `AssistantProfile.workspace` FK creation migration UNKNOWN (per Agent 1 evidence gap). Historical evidence lost.
- **DEBT-C1-6 (LOW):** `execute_with_workspace()` membership-check depth chain (HTTP → handler-internal → service-layer at 3 layers) is undocumented; observability tools cannot inspect the delegation without code-reading.
- **DEBT-C1-7 (MEDIUM — F-C6 severity semantics per Rigby Q3b Batch 2):** Workspace model is single-owner (`ProjectWorkspace.user` OneToOneField at `core/models_skin_layer.py:55-59`); NO `WorkspaceMember` junction table exists at HEAD. This is a **product-constraint debt** — Path A "WorkspaceMember" DRF class name implies a table + FK semantics that don't exist. Path A adoption at C1 verdict requires EITHER (i) extending workspace to multi-user membership (schema migration + backfill), OR (ii) wrapping single-owner semantics in a WorkspaceMember façade. Severity MEDIUM as design-clarity debt (can make Path A/B framing misleading if reviewers assume multi-member workspaces).
- **DEBT-C1-8 (MEDIUM — Rigby Q3b Batch 2):** `execute_with_workspace()` workspace_id **provenance is implicit** — the chosen workspace can come from (i) request payload `workspace_id` field, (ii) VIP scope injection at `unified_pa_chat` line 317-324, (iii) user default via `AssistantProfile.workspace` FK, (iv) agent-internal state, (v) `WorkspaceManager.get_active_workspace()` fallback to user's active workspace. Enumerate + document sourcing precedence for observability + Path A/B/C+compensating audit-log hook design (compensating control (i) needs to know which provenance chain the write followed).

### 15.2 C2 PA session-lifecycle debt (Cat C boundary scope)

- **DEBT-C2-1 (HIGH — F-C6 fold ratified 2026-07-06 severity semantics):** 3 logout endpoints × 0 `session_tool.retire` iterations. PA state fully decoupled from platform session-lifecycle at HEAD. **HIGH as verdict-scope governance gap** — at HEAD PA lifecycle is decoupled by default, which may be intentional (PA-override) but is currently **undeclared and unbounded**. Severity reflects decision-risk + user-safety ambiguity (cross-user retention surprises DEPENDING on Chris-D-verdict at S2699 xx99), NOT a proven defect. Blocks coherent lifecycle policy authoring. Escalates to confirmed-defect classification IF Chris ratifies α/β/γ (adoption implies logout coupling) at xx99 without accompanying retention-window spec.
- **DEBT-C2-2 (MEDIUM — F-C6 severity semantics per Rigby Q3a Batch 2):** paStore 2 UNKNOWN-intent fields (`isDockOpen`, `isDockMinimized`) NOT wiped by syncUser. Cross-user retention risk on shared devices. Cat C2 verdict-scope per AC-C2-4. **Escalates to HIGH if PA couples to auth lifecycle** (α/β/γ adoption at C2 verdict) — cross-user shared-device scenarios become active failure surface. Preserved MEDIUM at baseline; conditional escalation flagged.
- **DEBT-C2-3 (MEDIUM):** No unified PA conversation retention window declaration. 24-hour lookback hardcoded at `get_or_create_session()` line 212; NOT documented as retention policy; NOT parameterized. Cat C2 verdict-scope per AC-C2-3.
- **DEBT-C2-4 (LOW):** No PA arc-pin lifecycle documentation at codebase level (playbook §16 declares research arc-pin behavior only; PA runtime arc-pin lifecycle for user sessions UNDECLARED).
- **DEBT-C2-5 (MEDIUM):** No Clear-Site-Data header emission at any logout endpoint (S2403 F-C-CSD-1 preserved). C2 verdict-scope (α/β/γ adoption implies emission).
- **DEBT-C2-6 (MEDIUM):** No refresh-token endpoint at HEAD (S2403 F-C-REFRESH-1 preserved). C2 verdict-scope (α adoption requires this).
- **DEBT-C2-7 (LOW):** No ChatConversation `updated_at` field (Agent 1 evidence). Session last-touch NOT tracked; retention decisions cannot use last-activity semantics.
- **DEBT-C2-8 (LOW):** MobilePushToken.revoked_at NOT set at logout. CF-C4 handoff to Group 2300 Mobile scope.

### 15.3 Cross-arc coordination debt (adjacent to Cat C)

- **F-B-HIGH-3** — Cat C1 owns closure per parent §5.3 AC#3 F5 fold.
- **CF-C2** (S2503) — Cat C2 owns disposition; Group 2400 α/β/γ upstream input DEFERRED as of S2603 open.
- **CF-D6** (S2504) — Cat D S2604 owns WS-side; Cat C1 AC-C1-4 T7 statement records REST-side.
- **CF-C4** (S2403) — MobilePushToken lifecycle handoff to Group 2300 Mobile; Cat C boundary preserved.

## 16. Boundary Violations

**Playbook §9 canonical Q24 — Boundary violations.**

### 16.1 F-B-HIGH-3 workspace-membership implicit-gate (from S2402 preserved + Cat A §16.1 attribution)

**Location:** `core/agents/base_agent.py:5355 execute_with_workspace()` (implicit-gate host) → `core/services/workspace_manager.py:1697 WorkspaceManager.get_active_workspace()` (membership-check delegate). Membership check semantics: user-owns-workspace via `ProjectWorkspace.user` OneToOneField.

**HTTP boundary state at PA-path (34/34 endpoints, verified via Cat A §6.1 F11 + parent-Claude verifier):**
- `@permission_classes([IsAuthenticated])` uniformly (Cat A §6.1 evidence).
- **NO explicit `WorkspaceMember` DRF class enforcement** (0 `class WorkspaceMember` matches at HEAD).
- **NO middleware path-list gate** for PA-path workspace requirement (0 PA-path prefixes in any of 6 constants; 285 entries total per S2504 baseline).

**Classification:** Not a violation per se (implicit-gate is working at RUNTIME per S2402 finding + Cat A §7.1 flow evidence + Cat C §7.1 flow evidence). But contract-DECLARATION at REST boundary DOES NOT declare workspace-membership requirement. **Cat C1 OWNS Path A/B/C+compensating verdict per parent §3.C1 + F5 fold closure discipline.** Per Cat C1 F5 fold ownership: **Path C-pure without compensating controls is NOT a valid ratification.**

**F5 closure discipline enforcement (F-C7 fold ratified 2026-07-06 — hard "INVALID" language):** Chris-D-verdict at S2699 xx99 must select one of the following:

- **Path A** — WorkspaceMember DRF class retrofit + REST-boundary declaration.
- **Path B** — middleware path-list gate 7th constant addition + middleware declaration.
- **Path C+compensating** — implicit-gate PRESERVED + audit-log hook (i) + ADR (ii) + `docs/topics/personal-assistant.md` section (iii).

**Path C-pure (implicit-gate WITHOUT compensating controls) is INVALID under F5**: selecting Path C-pure at S2699 xx99 **fails closure and must be recorded as "rejected / non-ratifiable."** Only Path C+compensating is admissible on the Path-C axis. F5 blocks paper-victory; there is no "defer without controls" landing spot. This is not a "discouraged" verdict — it is a "non-selectable" verdict. Cat C1 records this constraint; Chris cannot ratify Path C-pure at xx99 without violating F5 closure discipline.

### 16.2 PA-adjacent boundary preservation (anti-scope verification)

Verifier confirmed at HEAD:
- **Anti-scope #4 (agent-registry mutations):** NOT VIOLATED — Cat C does NOT modify WORKSPACE_AWARE_AGENTS list content; evidence-only inventory (§5.1).
- **Anti-scope #5 (Discord bot PA proxy):** NOT VIOLATED (Cat A §16.2 + Cat B §16.2 baseline; no PA state touch at Discord layer).
- **Anti-scope #6 (Content Studio PA endpoints):** NOT VIOLATED.
- **Anti-scope #7 (Fleet HMAC PA signature):** Preserved — Fleet-federation workspace-boundary is out-of-scope; Cat C1 records fleet-identity NO workspace_id conveyance (§9.1) as boundary evidence, does NOT ratify verdict.
- **Anti-scope #8 (PA/auth token rotation):** Preserved — Cat C does NOT modify token rotation policy; logout mechanism is Group 2400 Auth scope.
- **Anti-scope #9 (LLM provider/model policy):** Preserved — no PA behavior scope in Cat C.
- **Anti-scope #10 (agent timeout tuning):** Preserved — retention window is DECLARATION scope, not runtime timeout scope.

### 16.3 Cat C boundary preservation at Cat C draft (Cat-C-1..9 micro-anti-scope compliance)

Cat C draft compliance verified per §16.4 Cat-C-1..9 enumeration below (F-B9 fold Cat B §16.4 precedent + Chris "agree all" ratified 2026-07-06 for Cat C F-C1 + F-C2 shape-card folds).

### 16.4 Cat-C micro-anti-scope enumeration (Cat-C-1..9 ID-stable list)

Cat C inherits parent §7 anti-scope items #1-#10 unchanged. Additional Cat-C-specific micro-anti-scope (Cat-C-1 through Cat-C-9, ID-stable per F-B9 fold precedent):

- **Cat-C-1** — Cat C does NOT retrofit `WorkspaceMember` DRF permission class code (evidence-only; retrofit is post-verdict Path-A implementation scope).
- **Cat-C-2** — Cat C does NOT modify `WORKSPACE_AWARE_AGENTS` list content at `core/epa_handlers_tools.py:3873-3907` (agent-registry mutations preserved per parent anti-scope #4).
- **Cat-C-3** — Cat C does NOT modify `execute_with_workspace()` internal check logic at `core/agents/base_agent.py:5355` (PA behavior mutations preserved per parent anti-scope #1).
- **Cat-C-4** — Cat C does NOT implement audit-log hook code for Path C+compensating (spec-only per AC-C1-3; implementation is post-verdict scope).
- **Cat-C-5** — Cat C does NOT re-litigate Group 2400 Cat C α/β/γ verdict CONTENT — only the PA-application decision. Group 2400 α/β/γ verdict is DEFERRED as of S2603 open; Cat C2 records the axis without ratifying.
- **Cat-C-6** — Cat C does NOT modify `session_tool.retire` handler code at `core/services/td_handlers_core.py:4011` (verified working per S1301 memory rule `feedback_session_tool_retire_works.md`; policy decision only).
- **Cat-C-7** — Cat C does NOT re-inventory PA-path endpoints (Cat A §6.1 F11 34-row canonical artifact per F7 fold — cite table). Cat C-scope endpoint subset (workspace-scoped-data-touching endpoints) is FILTERED from Cat A inventory, NOT re-inventoried (§6.1 above).
- **Cat-C-8** — Cat C does NOT enumerate WS envelope Path A/B/C option space (Cat D S2604 owned per parent §3.D). Cross-transport consistency check (AC-C1-4 §7.2) records COUPLING/DECOUPLING statement only, NOT WS envelope verdict.
- **Cat-C-9** — Cat C does NOT create new `docs/topics/personal-assistant.md` workspace-enforcement documentation section (Path C+compensating specifies as REQUIREMENT, not deliverable; documentation update is post-xx99 anchor-update cascade scope).

## 17. Duplicate or Overlapping Systems

**Playbook §9 canonical Q23 — Duplicate/overlapping systems.**

- **3 logout endpoints** — `logout_view` at `core/auth_views.py:85` + `logout_enhanced_view` at `core/auth_views_enhanced.py:541` + `logout_view` at `core/urls_unified.py:46` (Cognito-bypass variant). All three delete auth token; NONE mutate PA state. Cat C records overlapping surfaces; **verdict on consolidation is Group 2400 Auth scope**, not Cat C.
- **`AssistantProfile.workspace` + `ChatConversation.workspace` FK** — parallel nullable FKs to same `ProjectWorkspace` model; different lifecycle scopes (profile-scoped vs conversation-scoped). Cat C records; deliberate parallel design, not duplication.
- **Membership-check depth chain (3 layers)** — DRF `IsAuthenticated` at HTTP + `execute_with_workspace()` at handler + `WorkspaceManager.get_active_workspace()` at service. NOT duplicate (each serves distinct role); OVERLAP in scope (workspace resolution). Consolidation would require Chris-D-verdict at C1 Path A/B/C selection.

## 18. Ownership Gaps

**Playbook §9 canonical Q25 — Ownership gaps.**

Per Explore Agent 6 evidence + parent-Claude verifier cross-check:

**C1 workspace-context authz code paths:**

| Path | CODEOWNERS entry | Declared? | Effective owner |
|---|---|---|---|
| `core/agents/base_agent.py` (F-B-HIGH-3 boundary at line 5355) | NOT LISTED | NO | `* @clwest` (default) |
| `core/epa_handlers_tools.py` (WORKSPACE_AWARE_AGENTS dispatcher at line 3873-3922) | NOT LISTED | NO | `* @clwest` (default) |
| `core/auth_middleware.py` (path-list gates at lines 94-561) | `/core/auth_middleware.py @clwest` (line 21) | YES | `@clwest` |
| `core/services/fleet_auth_drf.py` (permission classes; no WorkspaceMember class) | `/core/services/fleet_auth_drf.py @clwest` (line 25) | YES | `@clwest` |
| `core/services/workspace_manager.py` (get_active_workspace() at line 1697) | NOT LISTED | NO | `* @clwest` (default) |
| `core/models_skin_layer.py` (ProjectWorkspace model at line 31-214) | NOT LISTED | NO | `* @clwest` (default) |

**C2 PA session-lifecycle code paths:**

| Path | CODEOWNERS entry | Declared? | Effective owner |
|---|---|---|---|
| `core/auth_views.py` (logout_view at line 85) | NOT LISTED | NO | `* @clwest` (default) |
| `core/auth_views_enhanced.py` (logout_enhanced_view at line 541) | `/core/auth_views_enhanced.py @clwest` (line 23) | YES | `@clwest` |
| `core/urls_unified.py` (Cognito-bypass logout_view at line 46) | NOT LISTED | NO | `* @clwest` (default) |
| `core/services/td_handlers_core.py` (session_tool handler at line 3868-4163) | NOT LISTED | NO | `* @clwest` (default) |
| `core/models/conversations/models.py` (ChatConversation session_active field) | NOT LISTED | NO | `* @clwest` (default) |
| `frontend/src/stores/paStore.ts` (paStore) | `/frontend/src/stores/paStore.ts @clwest` (line 32) | YES | `@clwest` |
| `frontend/src/stores/authStore.ts` (authStore.logout()) | NOT LISTED | NO | `* @clwest` (default) |

**PA doc paths EXPLICITLY listed** (unchanged from Cat A §18 + Cat B §18 baseline):
- `/docs/topics/ @clwest` (includes personal-assistant.md — target for Path C+compensating spec fulfillment)
- `/docs/PLATFORM_INVENTORY.md @clwest` (PA counts anchor — WORKSPACE_AWARE_AGENTS 20-count autoblock target)

**Ownership-gap observation:** C1 + C2 code path ownership is via default fallback per S2499 AU-D5 baseline (established at Group 2400 Auth close) + preserved through Cat A + Cat B. **S2699 xx99 anchor-update recommendation candidate:** PA-slice CODEOWNERS refinement extending Cat A + Cat B pattern (analog to Group 2500 API-slice discipline carried in S2599 close residuals).

## 19. Recommended Future Research

**Playbook §9 canonical Q28 — What should be researched next?**

Cat C DOES NOT recommend implementation. Cat C recommends **evidence-collection follow-ons** ranked by architectural uncertainty × risk × unblocked flows:

### 19.1 CRITICAL — Blocks Chris-D-verdict at S2699 xx99

1. **Cat D S2604 evidence on PA WS channel authentication handshake.** Cat C1 REST-side records enforcement point; Cat D S2604 owns WS-side. AC-C1-4 T7 cross-transport consistency check depends on Cat D output.
2. **Group 2400 α/β/γ verdict finalization.** As of S2603 open, α/β/γ verdict is DEFERRED. Cat C2 verdict path depends on Group 2400 close. If Group 2400 remains OPEN at S2699 xx99, Cat C2 records "defer + constraints" stance per F-C1 fold.
3. **Rigby SIGN Batch 2 highest-priority follow-on: confirm `execute_with_workspace()` fails closed + enumerate workspace_id provenance sources (Rigby "most important next research" verdict 2026-07-06).** Fails-closed confirmed at Cat C §7.2 (clarifier ratified 2026-07-06 via F-C7 supplementary); 5-source provenance enumerated at DEBT-C1-8 + §7.2. Follow-on: formalize sourcing precedence + observability at pre-xx99 or S2701+ session.

### 19.2 HIGH — Enables Chris-D-verdict at S2699 xx99

3. **`WorkspaceMember` DRF permission class design spec (if Chris ratifies Path A at C1).** Path A requires class creation (not adoption of existing). Cat C1 records evidence; xx99 xx99 or S2701+ session drafts spec.
4. **7th middleware path-list constant design spec (if Chris ratifies Path B at C1).** Path B requires new constant addition to `core/auth_middleware.py` (e.g., `WORKSPACE_REQUIRED_PATHS` or `PA_WORKSPACE_PATHS`). Cat C1 records; xx99 xx99 or S2701+ drafts spec.
5. **Audit-log hook signature + emit point design spec (if Chris ratifies Path C+compensating at C1).** Path C+compensating requires (i) audit-log hook, (ii) ADR, (iii) `docs/topics/personal-assistant.md` section. Cat C1 records requirements; xx99 xx99 or S2701+ drafts spec.
6. **PA `updated_at` field addition on ChatConversation model.** Session last-touch tracking prerequisite for retention-window decisions. Migration + backfill required.

### 19.3 MEDIUM — Post-arc follow-on

7. **`docs/PLATFORM_WHAT_IT_IS.md` audit-trail claim reconciliation.** Runtime lacks audit-log emission; doc claim requires either correction (drift fix) OR runtime implementation (Path C+compensating spec fulfillment). Cat C §14.2 D3 preserved.
8. **`docs/PLATFORM_INVENTORY.md` WORKSPACE_AWARE_AGENTS 20-count autoblock addition.** Cat C evidence baseline for future drift detection.
9. **PA-slice CODEOWNERS refinement extending Cat A + Cat B pattern.** C1 + C2 code paths CODEOWNERS declaration.
10. **paStore U7 2 UNKNOWN intent field verdict** (isDockOpen, isDockMinimized) — Cat C2 verdict-scope per parent §3.C2 + AC-C2-4.
11. **PA conversation retention window explicit policy** — Cat C2 verdict-scope per AC-C2-3.
12. **`session_tool` action shape drift monitoring.** 5-of-7 handler bodies verified at HEAD; 2 remaining (list_recent, health_check top-branch) — verifier next-step for full shape lock.

## 20. Appendix

### 20.1 Files inspected

Absolute paths + relevant line ranges (parent-Claude verifier + 6-Explore-agent aggregate at HEAD `2a3bc20d`):

- `core/agents/base_agent.py:5075-5227, 5355-5450` — execute_with_workspace + _write_files_to_workspace + _get_workspace_manager
- `core/services/workspace_manager.py:1697-1730` — get_active_workspace method body
- `core/epa_handlers_tools.py:3873-3922` — WORKSPACE_AWARE_AGENTS + dispatcher
- `core/services/td_handlers_core.py:3868-4163` — session_tool 7-action handler (create_fresh 3881 / list_recent 3930 / whoami 3961 / retire 4011 / set_active 4074 / seed 4109 + health_check top-branch)
- `core/services/pa_tool_schemas.py:4719-4798` — session_tool schema (7 actions enum)
- `core/services/pa_tool_schemas.py:822-914, 2371-2430, 3392-3450, 1100-1200+` — workspace-adjacent tool schemas (workspace_tool, autopilot_tool, deliverable_tool, initiative_tool)
- `core/services/unified_pa_entrypoint.py:552, 1771-1795` — process_message + _bound_conversation_id injection
- `core/services/fleet_auth_drf.py:65-220` — FleetSignatureAuthentication + 3 custom Permission classes (no WorkspaceMember)
- `core/views_personal_assistant.py:16-23, 31-32, 267-289, 302-324, 446-450` — auth chain + permission_classes + docstring + workspace_id extraction
- `core/urls.py:2185, 2196, 2485-2540, 4900-4903` — logout URL registrations + PA-path URL registrations (Cat A §6.1 canonical inventory reference)
- `core/urls_unified.py:46, 97` — Cognito-bypass unified frontend logout_view
- `core/auth_views.py:85-94` — logout_view (basic)
- `core/auth_views_enhanced.py:541-556` — logout_enhanced_view (enhanced)
- `core/auth_middleware.py:85, 94-561` — UnifiedTokenAuthenticationMiddleware + 285-entry path-list gate registry (6 constants)
- `core/models_skin_layer.py:31-214` — ProjectWorkspace model
- `core/models_assistant_profile.py:90-176` — AssistantProfile model + workspace FK + get_workspace_mode
- `core/models/conversations/models.py:19-222` — ChatConversation (session_active + workspace FK + get_or_create_session) + ConversationMemory
- `core/models_unified_system.py:1017-1115` — AgentFollowupSubscription (state machine + TTL)
- `core/models_mobile.py:1-34` — MobilePushToken (revoked_at)
- `core/tasks.py:11912-11930, 13444-13470` — PA queue tasks
- `frontend/src/stores/paStore.ts` (multiple line ranges) — 16-field paStore (Cat B §4.1 F-B4 canonical artifact — CITED, not re-inventoried)
- `frontend/src/stores/authStore.ts:34-39` — authStore.logout()
- `frontend/src/stores/workspaceStore.ts:1-28` — workspaceStore
- `frontend/src/components/layout/Sidebar.tsx:356` — logout invocation site
- `frontend/src/components/GlobalPADock.tsx:341, 351` — workspace_id payload assembly
- `CODEOWNERS` — ownership analysis (lines 21, 23, 25, 32 for declared paths)

### 20.2 Docs inspected

- `docs/topics/personal-assistant.md` (1-149)
- `docs/topics/frontend.md` (100, 139-140)
- `docs/PLATFORM_WHAT_IT_IS.md` (187-228 PA subsection)
- `docs/PLATFORM_INVENTORY.md` (autoblock + generation invariants)
- `CLAUDE.md` (7-36 Rigby coord + 34 canonical route)
- `docs/decisions/ADR-0001-execution-per-run-ephemeral-containers.md` (unrelated)
- All research docs cited in frontmatter `companion_anchors`.

### 20.3 Grep patterns used

- `^WORKSPACE_AWARE_AGENTS\s*=` — locate constant
- `^\s*def execute_with_workspace` — locate F-B-HIGH-3 method
- `get_active_workspace` — locate delegation
- `^\s*elif action == '(create_fresh|retire|set_active|seed|whoami|health_check|list_recent)'` — session_tool 7-action enum verification
- `^def logout|^class.*[Ll]ogout|logout_view|logout_enhanced_view` — logout endpoint inventory
- `class WorkspaceMember` / `IsWorkspaceMember` / `WorkspacePermission` — negative existence check
- `/api/pa/|/api/assistant/` on `core/auth_middleware.py` — path-list gate PA-path coverage check
- `audit_log|workspace_audit` — audit-log emission check (returned 0 runtime matches)
- `Clear-Site-Data` — logout header emission check (0 emission per S2403 F-C-CSD-1 preserved)

### 20.4 Unresolved unknowns

- `session_tool.list_recent` handler body — partial (line 3930 confirmed; body content not read in full).
- `autopilot_tool` handler location — not confirmed at HEAD.
- Dev/minimal PA-path routes (Cat A §6.1 rows 31-34) — Cat A §14 UNKNOWN preserved; Cat C does not re-litigate (§16.4 Cat-C-7).
- `AssistantProfile.workspace` FK creation migration number — Agent 1 evidence gap.
- **Group 2400 α/β/γ verdict finalization timing** — DEFERRED as of S2603 open; verdict path for Cat C2 depends on Group 2400 close BEFORE S2699 xx99 (else "defer + constraints" stance).

### 20.5 Conflicts between sources (verifier-loop corrections)

Recorded at frontmatter `verifier_loop` field + §14.1 (4 corrections total):
1. WORKSPACE_AWARE_AGENTS line-range: Cat A anchor 191-217 vs HEAD 3873-3907 → HEAD authoritative.
2. `WorkspaceManager.get_active_workspace()` line: Explore Agents 1+2 report 1710 vs HEAD 1697 → HEAD authoritative.
3. session_tool action-body coverage: Agent 2 5 bodies vs Agent 3 7 enum values → 7 enum values authoritative, all confirmed at HEAD.
4. Logout endpoint count: Agent 2 initial 2 vs Agents 3+4 3 → 3 authoritative at HEAD.

### 20.6 Rigby SIGN cycle 1 fold record (CLOSED 2026-07-06)

- **Dedicated SIGN pin ID:** `pa-9f37a2818961487f` (minted 2026-07-06 via `session_tool action=create_fresh title='Group 2600 PA Cat C SIGN cycle 1 (S2603 close) — TWENTY-SEVENTH consecutive dedicated fresh SIGN pin candidate'`).
- **SIGN batch structure:** Preemptive 2-batch × 2-Q per S2602 SUCCESS pattern (per MEMORY `feedback_rigby_sign_worker_instability_recovery.md`). SINGLE-PIN close pattern — 2-pin recovery NOT required (matches S2602 pattern).
- **SIGN verdict per Q:**
  - Batch 1 Q1 (coverage completeness): **STRENGTHEN** — F-C3 workspace-touching subset rule (Q1a) + F-C4 PA-produced outputs retention-impact surfaces (Q1c) + AGREE Q1b/d/e.
  - Batch 1 Q2 (maturity assessment): **STRENGTHEN** — F-C5 24-hour lookback mechanism-constant vs policy-declaration clarification (Q2d) + AGREE Q2a/b/c/e (with supplementary "fails closed vs open" clarifier ratified at §7.2).
  - Batch 2 Q3 (technical debt identification): **STRENGTHEN** — F-C6 DEBT-C2-1 severity semantics recast as verdict-scope governance gap (Q3a) + 2 new debt items DEBT-C1-7 workspace single-owner (Q3b) + DEBT-C1-8 workspace_id provenance implicit (Q3b) + AGREE Q3c/d/e (DEBT-C1-4 identified as SINGLE MOST IMPORTANT DEBT).
  - Batch 2 Q4 (boundary discipline preservation): **STRENGTHEN** — F-C7 Path C-pure INVALID hard language (Q4d) + AGREE Q4a/b/c/e.
- **Overall confidence:** **HIGH** (both batches).
- **Fold adoption:** All 5 folds (F-C3, F-C4, F-C5, F-C6, F-C7) + 2 new DEBT items (DEBT-C1-7, DEBT-C1-8) + §7.2 fails-closed clarifier + §7.2 workspace_id provenance enumeration + §19.1 CRITICAL research follow-on — baked in-place; §-anchors documented above.
- **SIGN pin retirement:** RETIRED 2026-07-06 via `session_tool action=retire conversation_id=pa-9f37a2818961487f force=true` (updated_count=1). TWENTY-SEVENTH consecutive dedicated fresh SIGN pin retirement in Research OS after 26 prior.
- **Chris ratification:** "agree all" 2026-07-06 wholesale — 5 folds + 2 DEBT items + clarifiers. Frontmatter `status: draft` → `status: active` per playbook §16 draft-first workflow.

### 20.7 Cat C boundary discipline attestation

Cat C draft ships with the following boundary attestations (per playbook §5 phase discipline + §16.4 Cat-C-1..9 micro-anti-scope):

- Cat C is EVIDENCE-ONLY. No Chris-D-verdict recommendations on Path A / Path B / Path C+compensating (C1) or α / β / γ / PA-override (C2).
- Cat C did NOT retrofit `WorkspaceMember` DRF class code (Cat-C-1).
- Cat C did NOT modify WORKSPACE_AWARE_AGENTS list (Cat-C-2).
- Cat C did NOT modify `execute_with_workspace()` internals (Cat-C-3).
- Cat C did NOT implement audit-log hook code (Cat-C-4).
- Cat C did NOT re-litigate Group 2400 α/β/γ verdict content (Cat-C-5); Group 2400 DEFERRED status preserved.
- Cat C did NOT modify `session_tool.retire` handler (Cat-C-6).
- Cat C did NOT re-inventory PA-path endpoints (Cat-C-7); Cat A §6.1 F11 CITED as canonical artifact.
- Cat C did NOT enumerate WS envelope Path A/B/C option space (Cat-C-8); Cat D S2604 boundary preserved.
- Cat C did NOT create `docs/topics/personal-assistant.md` documentation section (Cat-C-9); spec-only per AC-C1-3.

### 20.8 Verifier-loop 4-correction chain (§14 evidence)

Per playbook §14 evidence rules — 4 verifier corrections landed pre-draft (recorded in frontmatter + §14.1 body). Verifier discipline aligned with S2601 §14.6 5-corrections pattern + S2602 §14.1 7-corrections pattern. Cat C boundary discipline preserved — evidence-only; no verdict recommendations on Path A/B/C+compensating (C1) or α/β/γ/PA-override (C2).

### 20.9 SIGN cycle 1 lineage summary (post-close)

Playbook §11.2 20-section child-audit template TWENTY-THIRD-consecutive application closed 2026-07-06 with 5 STRENGTHEN folds baked wholesale + 2 new debt items baked wholesale + §7.2 clarifiers baked wholesale + §19.1 CRITICAL research follow-on baked wholesale. TWENTY-SEVENTH-consecutive dedicated fresh SIGN pin retirement in Research OS. SINGLE-PIN close pattern preserved from S2602 SUCCESS; 2-pin recovery NOT required. Preemptive 2-batch × 2-Q batching from turn 1 prevented worker instability per `feedback_rigby_sign_worker_instability_recovery.md`. Arc pin `pa-c17a8d7e0660413b` PRESERVED through S2603 per playbook §16 arc-standard behavior (no rotation until S2699 xx99 close).

**Group 2600 PA arc status at S2603 close:** 4-of-6 sessions shipped (S2600 parent scoping + S2601 Cat A + S2602 Cat B + S2603 Cat C). Remaining: S2604 P4 Cat D REST↔WS T7 joint (dual-owner PA side) + S2699 xx99 canonical summary.
