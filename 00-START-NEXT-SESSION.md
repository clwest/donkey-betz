# Next Session — Start Here

---

## READ THIS FIRST — S2602 P2 CAT B COMMITTED + T3 GROUP 2600 PA ARC 3-OF-6 SHIPPED + S2603 P3 CAT C NEXT

**S2602 P2 Cat B PA-Client Contract Surface Design-Prep child audit COMMITTED 2026-07-06.** Playbook §11.2 20-section child-audit template TWENTY-SECOND-consecutive application (after S1301/S1401/S1501/S1601/S1701/S1801/S1901/S2001/S2101/S2102/S2103/S2104/S2201/S2202/S2203/S2204/S2401/S2402/S2403/S2404/S2501/S2601 twenty-one prior). Doc: `docs/research/domains/pa/2602_pa_client_contract_surface_design_prep_audit.md` — ~980 lines post-fold (2 SIGN cycle 1 STRENGTHEN folds F-B9 + F-B10 baked). Chris "agree all" 2026-07-06 ratified 8 shape-card SIGN-preview folds (F-B1 through F-B8) wholesale pre-drafting + Chris "agree all" 2026-07-06 ratified 2 SIGN cycle 1 STRENGTHEN folds (F-B9 + F-B10) via **SINGLE-PIN close pattern** (2-pin recovery NOT required at Cat B despite 10,689-word doc — preemptive 2-batch × 2-Q batching from turn 1 prevented worker instability). Pin `pa-760b68d6e48d4448` TWENTY-SIXTH consecutive dedicated fresh SIGN pin retirement — Batch 1 (Q1+Q2) HIGH confidence with F-B9 STRENGTHEN + Batch 2 (Q3+Q4) HIGH confidence with F-B10 STRENGTHEN + retired 1 row. Cycle 2 NOT required. Arc pin `pa-c17a8d7e0660413b` PRESERVED through S2602.

**Group 2600 PA arc 3-of-6 sessions shipped** (S2600 parent scoping + S2601 Cat A + S2602 Cat B). **NEXT: S2603 P3 Cat C PA workspace-context authz + session lifecycle** (2 sub-tracks C1 + C2 per parent F2 fold) per §5.1 child mission sequence.

### `tools/pa_local.sh:348` UNCHANGED at S2602 close — arc pin PRESERVED

`tools/pa_local.sh:348` `--conversation` value UNCHANGED at S2602 close — arc pin `pa-c17a8d7e0660413b` continues to route all Claude Code → Rigby chatter through the Group 2600 PA arc pin per playbook §16 arc-standard behavior (no rotation until arc close at S2699 xx99).

**S2603 P3 arc-continue protocol:** `tools/pa_local.sh` invocation continues to route to active Group 2600 arc pin. Verify `service_context: local` via `platform_config_tool overview` at S2603 open turn 1 before any Cat C audit work.

## READ THIS SECOND — S2603 P3 CAT C PA WORKSPACE-CONTEXT AUTHZ + SESSION LIFECYCLE QUEUED

**S2603 P3 is the NEXT child per §5.1 child mission sequence** in `docs/research/domains/pa/2600_pa_domain_scoping.md`. Focus (2 parallel sub-tracks per F2 fold):

### C1 — Workspace-context authz declaration policy

- **Mission:** Close F-B-HIGH-3 workspace-membership implicit-gate. Declare where workspace-context authorization is enforced (HTTP permission-class layer / middleware path-list gate / handler-internal implicit) + ratify F-B-HIGH-3 closure condition per F5 fold.
- **Scope:**
  - WORKSPACE_AWARE_AGENTS at `core/epa_handlers_tools.py:191-217` (20 agents).
  - `execute_with_workspace()` internal membership check at `core/agents/base_agent.py:5355` (Cat A §16.1 evidence baseline).
  - PA-path endpoints that read/write workspace-scoped data.
- **Chris-D-verdict axes (F5 closure-condition fold):**
  - **Path A** — Retrofit `WorkspaceMember` DRF permission class at PA endpoints; membership enforced pre-handler at HTTP layer.
  - **Path B** — Declare workspace requirement at middleware path-list gate layer (analog to S2504 §Cat D 285-entry path-list gate mechanism).
  - **Path C+compensating (F5 fold)** — Handler-internal implicit-gate PRESERVED with documented compensating controls: (i) audit-log hook fires per workspace-scoped dispatch; (ii) explicit ADR; (iii) `docs/topics/pa.md` declares workspace-enforcement location for discoverability. **Path C-pure (implicit-gate WITHOUT compensating controls) is NOT a valid ratification per F5 fold.**

### C2 — PA session-lifecycle policy

- **Mission:** Declare PA-specific session-lifecycle policy — `session_tool.retire` disposition on user logout + PA conversation retention window. Couple to Group 2400 Cat C α/β/γ verdict OR declare PA-specific override.
- **Scope:**
  - `session_tool.retire` behavior on PA conversation pin closure (verified working per S1301 memory rule `feedback_session_tool_retire_works.md`).
  - PA conversation retention window (arc-pin lifecycle vs user-session lifecycle vs storage-key TTL).
  - CF-C2 handoff scope — Group 2400 Cat C α/β/γ session-lifecycle verdict applied to PA slice.
- **Cat B U7 inheritance:** 2 UNKNOWN intent fields (`isDockOpen`, `isDockMinimized` from Cat B §4.1 F-B4 closure) with explicit pointer → Cat C2 verdict scope. Also 5 syncUser-wiped paStore fields (`messages`, `activeConversationId`, `conversations`, `currentInput`, `conversationsLoading`) as Cat C2 session-lifecycle retention-window inputs.
- **Chris-D-verdict axes:**
  - **α / β / γ** — Adopt Group 2400 Cat C verdict unchanged at PA layer.
  - **PA-override** — Declare PA-specific override (e.g., arc-pin lifetime decoupled from user session per playbook §16 arc-standard behavior). Requires explicit Chris-D-verdict + rationale trace at S2699 xx99 close.

### Cat A + Cat B inheritance for S2603

Cat A inheritance (S2601):
- §6.1 F11 canonical PA-path endpoint inventory (34 endpoints × 11 columns) — AC-A2 canonical artifact; DO NOT re-inventory PA-path endpoints.
- §16.1 F-B-HIGH-3 workspace-membership implicit-gate location at `core/agents/base_agent.py:5355 execute_with_workspace()`.
- §7.2 REST-side "task-based async, NO streaming" statement.

Cat B inheritance (S2602):
- §4.1 F-B4 U7 paStore 16-field dump (2 UNKNOWN intent → Cat C2 verdict scope for C2 sub-track).
- §16.1 F-B7 single-sentence F-B-HIGH-3 attribution (Cat B did NOT ratify closure; Cat C1 owns).
- §7.1 8-step client flow + REST↔WS parallel delivery observation (Cat C2 evidence baseline for retention-window decisions).
- §15.2 CF-C2 session-lifecycle handoff cross-arc coordination debt.

**S2603 arc-open protocol:**
1. `tools/pa_local.sh "platform_config_tool action=overview"` → verify `service_context: local` + `railway_environment: local` + `database_name: unified_donkey_betz` + `default_llm_provider: openai` under active Group 2600 arc pin `pa-c17a8d7e0660413b`.
2. Read `docs/research/domains/pa/2600_pa_domain_scoping.md` fully — DIRECT PARENT for Cat C + §3.C1 + §3.C2 scope + §5.3 AC + §2.5 evidence gaps.
3. Read `docs/research/domains/pa/2601_pa_backend_endpoint_contract_sot_design_prep_audit.md` — SIBLING PRIOR-CHILD Cat A (§6.1 F11 canonical inventory + §16.1 F-B-HIGH-3 boundary).
4. Read `docs/research/domains/pa/2602_pa_client_contract_surface_design_prep_audit.md` — SIBLING PRIOR-CHILD Cat B (§4.1 F-B4 U7 paStore field-list + §15.2 CF-C2 coordination debt).
5. Read `docs/research/domains/auth/2402_auth_permission_floor_uniformity_audit.md` — F-B-HIGH-3 ORIGIN for Cat C1.
6. Read appropriate S2403 predecessor (α/β/γ session-lifecycle verdict origin) for Cat C2 — verify exact predecessor filename at S2603 arc-open.
7. Read `docs/research/DOMAIN_RESEARCH_PLAYBOOK.md` §11.2 child audit template + §21 short-command vocabulary + §13 sub-agent Explore contracts + §14 verifier-loop discipline + §15 SIGN-isolation.
8. Read the 4 CF-* handed forward + F-* preserved: CF-2600-PA (S2501 Cat A) origin + F-B-HIGH-3 preserved (S2402→S2504→S2601 Cat A boundary + S2602 Cat B non-litigation) + CF-C2 (S2503) session-lifecycle.
9. Draft Cat C shape-card 4-Q (Q1 C1+C2 parallel-sub-track enumeration + Q2 F5 closure-condition lens + Q3 acceptance criteria for Cat C — F-B-HIGH-3 closure verdict + α/β/γ session-lifecycle verdict + Q4 anti-scope inheritance). Route to Rigby SIGN-preview via arc pin `pa-c17a8d7e0660413b` (single-batch × 4-Q preview cadence per S1899-S2602 ELEVENTH-consecutive tested pattern; TWELFTH-consecutive-at-child-scoping candidate).
10. Fold SIGN-preview edits pre-drafting.
11. Draft full Cat C audit doc as `docs/research/domains/pa/2603_pa_workspace_authz_session_lifecycle_design_prep_audit.md` per playbook §11.2 20-section template with 2 parallel sub-track output tables (C1 + C2).
12. Route full doc to Rigby SIGN cycle 1 via dedicated fresh SIGN isolation pin (TWENTY-SEVENTH consecutive candidate) per playbook §15 SIGN-isolation discipline. Preemptive: batch SIGN into 2-batch × 2-Q per S2602 SUCCESS pattern per `feedback_rigby_sign_worker_instability_recovery.md`.
13. Fold SIGN edits + retire SIGN pin at close.
14. Present Chris ratification card. Status flips `draft` → `active` on ratification.

## READ THIS THIRD — S2602 CAT B LOAD-BEARING OUTPUTS

**Cat B audit doc at `docs/research/domains/pa/2602_pa_client_contract_surface_design_prep_audit.md`:**

- **§6.1 F-B5 assistantApi denominator lock: 20 exported methods** at `frontend/src/lib/api.ts:1147-1230` (F-B1 grep-locked region). Typed rate = **5/20 = 25%** (EXCEEDS platform 7.36% baseline ~3.4x, evidence-only). assistantApi covers 16 of Cat A's 34 F11 endpoints; 18 rows NOT covered (§19.3 MEDIUM follow-on candidate).
- **§4.1 F-B4 U7 paStore field-list dump: 16 fields, 0 UNKNOWN names, 2 UNKNOWN intent** (`isDockOpen`, `isDockMinimized` → Cat C2 S2603). AC-B4 canonical artifact for U7 evidence-gap closure turn 1.
- **§6.2 F-B3 U6 WS envelope inventory: 1 PA-client channel + 3 canonical classes** (message.created / agent.completed / rigby.tool.* lifecycle — F-B3 verifier-loop RE-LABEL from "async-audio-url delivery" per §6.3 evidence). All envelope grade `observed-JSON-only`. Cat D S2604 owns Path A/B/C verdict.
- **§6.5 F-B6 cockpitApi 96%-typed exemplar structural prerequisites: 1-of-3 at HEAD** (types/pa.ts NEGATIVE + hooks/paQueries.ts NEGATIVE + shared api instance POSITIVE). Retrofit requires sibling file creation per F-B8 no-file-moves discipline.
- **§16.1 F-B7 F-B-HIGH-3 single-sentence attribution** preserved (Cat C1 S2603 owned).
- **§16.4 F-B9 Cat-B micro-anti-scope enumeration** (Cat-B-1 through Cat-B-9 explicit list).
- **§19.2 item #6 F-B10 boundary-neutral Cat D audio_url evidence follow-on** (rephrased per SIGN cycle 1 STRENGTHEN).
- **§14 7 pre-draft verifier-loop corrections + §14.2 3 confirmed drifts + §14.3 verify_doc_claims 0 PA-CLIENT claims + §20.5 6 conflicts logged + §20.8 SIGN cycle 1 fold record (Batch 1 F-B9 + Batch 2 F-B10).**

## READ THIS FOURTH — LOAD-BEARING INPUTS FOR NEXT SESSION

**S2603 P3 Cat C arc-open must consume:**
- `docs/research/domains/pa/2600_pa_domain_scoping.md` (S2600 parent scoping — DIRECT PARENT + §3.C1 + §3.C2 + §5.3 AC#3 F5 closure-condition fold + §2.5 evidence gaps)
- `docs/research/domains/pa/2601_pa_backend_endpoint_contract_sot_design_prep_audit.md` (S2601 Cat A — §6.1 F11 canonical inventory + §16.1 F-B-HIGH-3 boundary)
- `docs/research/domains/pa/2602_pa_client_contract_surface_design_prep_audit.md` (S2602 Cat B — §4.1 F-B4 U7 paStore 16-field dump + §15.2 CF-C2 coordination debt + §16.1 F-B7 attribution)
- `docs/research/domains/auth/2402_auth_permission_floor_uniformity_audit.md` (F-B-HIGH-3 ORIGIN)
- `docs/research/domains/auth/2403*.md` (α/β/γ session-lifecycle verdict origin — verify exact predecessor filename at S2603 arc-open)
- `docs/research/domains/api/2504_api_permission_floor_registry_rest_ws_t7_joint_design_prep_audit.md` (S2504 Cat D — 285-entry path-list gate mechanism reference for C1 Path B)
- `docs/research/domains/api/2599_api_canonical_summary.md` (S2599 xx99 — Group 2500 API canonical verdict inheritance)
- `docs/research/DOMAIN_RESEARCH_PLAYBOOK.md` §11.2 + §13 + §14 + §15 + §16 + §21

## READ THIS FIFTH — OUTSTANDING RESIDUALS

### S2602 close residuals — post-Cat-B-audit docs cascade PR

Per Chris "agree all" ratification at S2602 close 2026-07-06:

- **Post-commit docs cascade PR** — 4-step cascade (`build_docs_index` + `build_rag_corpus` + `sync_docs_index_to_documents` + `sync_docs_index_to_documents --embed`) + `build_docs_provenance` per `feedback_docs_cascade_at_every_close` + `feedback_cascade_pr_must_include_embed_step`. Verify final chunk count + provenance-json refresh in PR body.

- **ARCHITECTURE_INDEX.md + OPEN_ARCS.md deferred anchor cascade** (extends S2600 + S2601 close deferrals):
  - **AU-7** ARCHITECTURE_INDEX §1.99 S2602 backfill (Group 2600 PA Cat B child audit registration) + v-bump.
  - **AU-8** ARCHITECTURE_INDEX §8 timeline: 1 row added (S2602 Cat B).
  - **AU-9** ARCHITECTURE_INDEX §3 domain map PA row: Cat B closed at S2602; 2-of-4 children remaining.
  - **AU-10** ARCHITECTURE_INDEX §9 roadmap T-slot queue advance: unchanged.
  - **OPEN_ARCS.md** Group 2600 PA row S2602 child-registration update (in-progress → 3-of-6 sessions shipped).

- **Cat B new anchor-update candidates for S2699 xx99:**
  - **AU-B1** PLATFORM_INVENTORY §PA autoblock EXTEND (PA-client typed rate 5/20 = 25% + paStore field count 16 + WS canonical class count 3).
  - **AU-B2** `docs/topics/personal-assistant.md` EXTEND (PA-client contract surface subsection referencing Cat B §6.1 + §4.1 + §6.2 + §6.4).
  - **AU-B3** `docs/topics/frontend.md` EXTEND (PA-client contract surface mini-section under PA integration).
  - **AU-B4** `docs/PLATFORM_WHAT_IT_IS.md:192 + :219` INTERNAL-CONTRADICTION-AND-DRIFT FIX (109 + 101 → runtime 113). NEW drift not previously logged.

- **Deep anchor-update items deferred from S2599** (still pending):
  - AU-1 PLATFORM_INVENTORY §API autoblock CREATE + AU-3 PLATFORM_WHAT_IT_IS §API narrative + AU-10 `docs/topics/api.md` CREATE + AU-11 `platform_architecture_inventory.md` §3.22 API Layer REVISE + AU-12 CODEOWNERS cockpit surface refinement.

### Group 2400 + Group 2500 post-arc remediation queue (unchanged carry into S2603)

**P0-A platform-wide (S2599 xx99 execution scope carry):**
- AU-U1 Route→view normalization pass to compute D4 unique-view denominator.
- F-D-CALL-1 803-scale silent-401 remediation.
- F-D-BYPASS-1 79-raw-fetch bypass reconciliation.
- F-D-ENVELOPE-1 typed-error-envelope execution.
- F-D-BOUNDARY-1 error-boundary framework establishment.

**P0-B token lifecycle / security window (unchanged):**
- F-D-SIDEBAR-1, F-C-REFRESH-1, F-C-VIP-1, F-C-CSD-1, F-C-STORE-1.

**P0-C endpoint-specific (unchanged):**
- F-CRIT-1, F-BND-4a, F-B-CRIT-1, F-B-CRIT-2, F-D-WHITELIST-1, F-D-REGISTRY-1, F-D-WSENVELOPE-1.

### T-slot follow-on queue (post-Group-2600-close forward look — unchanged)

- **T3 Group 2600 PA** — **IN-PROGRESS**, 3-of-6 sessions shipped (S2600 parent scoping + S2601 Cat A + S2602 Cat B).
- **T4 Group 1700 Observability** — QUEUED after Group 2600 close.
- **T5 Group 2300 Mobile (parallel)** — QUEUED after Group 2600 close.
- **T6 Group 1600 Content** — QUEUED after Group 2600 close per Cat C S2503 Rigby SIGN Q11 fold CF-C8.
- **Maintainer-decision batch** (unchanged carry).

### Session count status

- Group 2500 API arc CLOSED at S2599 xx99 close 2026-07-06.
- Group 2400 Auth arc CLOSED at S2499 (prior arc).
- Group 2600 PA arc — **3-of-6 sessions shipped** (S2600 parent scoping 2026-07-06 + S2601 Cat A 2026-07-06 + S2602 Cat B 2026-07-06).
- **TWENTY-SIXTH consecutive dedicated fresh SIGN pin retirement** at S2602 close (Pin `pa-760b68d6e48d4448`).
- SEVENTH-consecutive parent-with-4-children arc under Research OS — MC-4 CODIFICATION-CONFIRMED-with-scope-guardrails SEVENTH-consecutive extension.
- **TWENTY-SECOND-consecutive playbook §11.2 20-section child-audit template application** at S2602 (after 21 prior).
- **FIRST SINGLE-PIN Cat B close in Group 2600 PA arc** — S2601 Cat A required 2-pin recovery (8,729 words + turn-3 worker instability); S2602 Cat B (10,689 words) closed with 1 pin via preemptive 2-batch × 2-Q batching from turn 1. Recovery pattern preserved as fallback per `feedback_rigby_sign_worker_instability_recovery.md`; single-pin close is preferred when preemptive batching is applied from the start.

## SESSION READY CHECK (before opening S2603 P3 Cat C child audit)

Before drafting Cat C shape card:

1. `tools/pa_local.sh "platform_config_tool action=overview"` → verify `service_context: local` + `railway_environment: local` + `database_name: unified_donkey_betz` + `default_llm_provider: openai` under active Group 2600 arc pin `pa-c17a8d7e0660413b`.
2. Read `docs/research/domains/pa/2600_pa_domain_scoping.md` fully — DIRECT PARENT.
3. Read `docs/research/domains/pa/2601_pa_backend_endpoint_contract_sot_design_prep_audit.md` — SIBLING Cat A (§6.1 F11 canonical inventory + §16.1 F-B-HIGH-3 boundary).
4. Read `docs/research/domains/pa/2602_pa_client_contract_surface_design_prep_audit.md` — SIBLING Cat B (§4.1 F-B4 U7 paStore + §15.2 CF-C2 coordination debt + §16.1 F-B7 attribution).
5. Read `docs/research/domains/auth/2402_auth_permission_floor_uniformity_audit.md` — F-B-HIGH-3 ORIGIN.
6. Read `docs/research/DOMAIN_RESEARCH_PLAYBOOK.md` §11.2 + §13 + §14 + §15 + §16 + §21.
7. **First execution step at S2603 open:** draft Cat C shape card 4-Q (Q1 C1+C2 parallel-sub-track enumeration + Q2 F5 closure-condition lens + Q3 AC with F-B-HIGH-3 closure + α/β/γ verdict + Q4 anti-scope inheritance). Route to Rigby SIGN-preview via arc pin `pa-c17a8d7e0660413b` (single-batch × 4-Q preview cadence).
8. Fold SIGN-preview edits.
9. Six-parallel-Explore-agent sweep per playbook §13 dispatched at S2603 open turn 2 (after shape-card ratification).
10. Parent-Claude verifier-loop applied pre-draft per playbook §14 (S2601 5-corrections + S2602 7-corrections precedent).
11. Draft full Cat C child audit doc as `docs/research/domains/pa/2603_pa_workspace_authz_session_lifecycle_design_prep_audit.md` per playbook §11.2 template with 2 parallel sub-track output tables (C1 + C2).
12. Route full audit to Rigby SIGN cycle 1 via dedicated fresh SIGN isolation pin (TWENTY-SEVENTH consecutive candidate). **Preemptive: batch SIGN into 2-batch × 2-Q per S2602 SUCCESS pattern** per `feedback_rigby_sign_worker_instability_recovery.md`.
13. Fold SIGN edits + retire SIGN pin.
14. Present Chris ratification card. Status flips `draft` → `active`.
15. Docs cascade + handoff + overwrite `00-START-NEXT-SESSION.md` with S2604 P4 Cat D priorities.

**S2603 arc-continue command (Chris short command):** `Continue research group 2600: S2603` or `Continue research group 2600: P3 Cat C workspace authz + session lifecycle` per playbook §21 vocabulary + OS §3.2 deterministic route.
