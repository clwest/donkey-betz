---
title: "Memory Domain (Category F) — Conversational / Thread Memory Architecture Audit"
status: draft
authority: research
session_added: 1303
research_group: 1300
child_slot: P3
domain_slug: memory
date: 2026-07-01
last_verified: 2026-07-01
supersedes: none
sign_status: SIGN-clean (cycles 1 + 2 complete — Rigby verified E3/E4/E5 independently on `pa-23a38300dd84bae2`)
related:
  - docs/research/domains/memory/1300_memory_domain_scoping.md              # parent (P0)
  - docs/research/domains/memory/1301_memory_rag_retrieval_lanes_audit.md   # sibling (P1 — Cat D)
  - docs/research/domains/memory/1302_memory_persistence_architecture_audit.md   # sibling (P2 — Cat A+B+C)
  - docs/research/DOMAIN_RESEARCH_PLAYBOOK.md                                # process framework (v2)
  - docs/research/ARCHITECTURE_INDEX.md                                      # library navigation (v14 → v15)
  - docs/research/OPEN_ARCS.md                                               # cross-arc live manifest
  - docs/research/process/RESEARCH_OPERATING_SYSTEM.md                       # OS §0–§9
companion_anchors:
  - docs/PLATFORM_INVENTORY.md                                               # runtime counts anchor (Cat F has NO §3 row today — first-inventory landing)
  - docs/PLATFORM_WHAT_IT_IS.md                                              # narrative anchor
  - docs/research/platform_architecture_inventory.md                         # 32-domain map (S1273 — no §3.N row for Cat F; §3.2 Agent System + §4 Employee OS reference obliquely)
  - docs/research/platform/cross_domain_integration_audit.md                 # integration lens (S1274)
  - docs/UDB_BEHAVIOR_LAYER.md                                               # PA/Rigby behavior (turn contract; carry-forward semantics inform this domain)
dependencies_on:
  - group: 1300
    slug: memory
    role: "Parent §3F names the systems; parent §5 P3 rationale locks first-inventory discipline; S1302 §17.3 name-collision resolution (Django `ConversationMemory` = Cat B, in-process `ConversationMemory` = Cat F) MUST hold as the ConversationSession ↔ ConversationMemory boundary."
delegates_to: none
delegated_from: none
verifier_loop: |
  v0.4 draft (2026-07-01, S1303 SIGN cycle 2 complete → SIGN-clean):
  Rigby returned SIGN-clean on fresh SIGN isolation pin
  `pa-23a38300dd84bae2` after cycle 2 verification pass. She
  independently verified: (1) §14 F4 rewrite matches cycle 1 grep
  evidence + discipline note explicitly cites `tasks_agents.py:1262`
  `agent_results = phase_data.get('results', {})` as the load-
  bearing unrelated-variable example; (2) §19 R1 split R1.a/R1.b/
  R1.c ordering is defensible + "do R1.a first" is explicit; (3)
  §15 D1 widened framing matches `content_writer_agent.py:370` via
  direct code read — she confirmed `ConversationMemory` Django model
  at `models/conversations/models.py:19-31` has NO `memory_type`
  field, so import fix alone would shift crash class from import-
  time-soft-fail to query-time-FieldError. Bonus checks on §13
  bounded-maturity language (E1) passed. Cycle 2 was a verification
  pass, not a structural rewrite — no additional edits required.
  Cycle 2 outcome: **SIGN-clean**. Frontmatter `sign_status:` flipped
  to SIGN-clean; §20.10 gating checklist SIGN cycle 2 box ticked.
  Remaining gate: Chris commit-gate per playbook §16.
  v0.3 draft (2026-07-01, S1303 SIGN cycle 1 fold): Rigby returned
  SIGN-with-edits (2 fold cycles planned) on fresh SIGN isolation pin
  `pa-23a38300dd84bae2`. She independently grep-verified the load-
  bearing claims and confirmed the F4 discipline downgrade was
  correct — her `agent_results` sweep found `tasks_agents.py:1262-1264`
  matches were an unrelated local variable (`agent_results =
  phase_data.get('results', {})`), NOT a read of the ChatConversation
  field, which directly validates the F4-CANDIDATE hedge. Additional
  load-bearing finding surfaced during her review of
  `content_writer_agent.py`: the guarded branch at line 370 filters
  `ConversationMemory.objects.filter(user=user, memory_type__in=
  ['success', 'insight', 'learning'])` — but the Cat B Django
  `ConversationMemory` at `models/conversations/models.py:19` has no
  `memory_type` field (that field lives on `UserMemoryContext` at
  line 253). Consequence: fixing the D1 import alone would move the
  crash from import-time-soft-fail to query-time-FieldError. D1 must
  widen to "wrong model + wrong field," and F3 must add the query-
  time FieldError risk clause. All 12 SIGN cycle 1 edits (E1-E12)
  folded into this v0.3 draft. Cycle 2 (verification pass; not a
  structural rewrite) to follow — targeted grep re-run for E4/E5
  (F4/R1) + confirm D1 framing matches content_writer_agent.py
  reality. Cycle 2 outcome expected: SIGN-clean.
  v0.2 draft (2026-07-01, S1303 mid-session): §13 6-parallel-Explore
  sweep completed; parent Claude ran verifier-loop spot-checks per
  playbook §13 step 3 + memory rule
  feedback_verify_before_deleting_dead_code.md. Load-bearing spot-checks
  passed (all evidence path:line cites verified):
    • unified_pa_entrypoint.py 7613 lines confirmed (god-service verdict
      holds)
    • td_handlers_core.py 4168 lines confirmed; _handle_session at 3864
      confirmed; retire action at 4011-4072 confirmed; retire returns
      `retired: True` (line 4061) confirmed
    • conversation_action_dispatcher.py retired-thread gate at
      288-316 confirmed (matches S1248 fix for deliverable 777d9cd8)
    • unified_pa_entrypoint _load_conversation_history_from_db at
      7277-7343 confirmed; 10-row conversation-scoped window at
      7300-7302 confirmed; 8000-char assistant-response truncation at
      7327 confirmed (post-S1085 bump from 2000)
    • ChatConversation model at conversations/models.py:59 confirmed;
      session_active BooleanField at line 139 confirmed; context_used
      JSONField at 157 + agent_results JSONField at 167 confirmed
  Sweep findings folded with two verifier corrections:
    (1) F3 (broken import in content_writer_agent.py:76) SEVERITY
    DOWNGRADED — Agent 6 claimed "would fail at import time." Direct
    read of content_writer_agent.py:70-80 shows try/except ImportError
    guard that soft-fails to MEMORY_AVAILABLE=False + ConversationMemory
    =None. Correct classification: SOFT FAIL (feature degradation, not
    runtime crash). Severity: MED (feature silently disabled).
    (2) F4 (phantom fields `context_used` + `agent_results` on
    ChatConversation) DOWNGRADED FROM "DEAD-CODE CONFIRMED" TO
    "CANDIDATE — REQUIRES FULL-TREE VERIFICATION SWEEP." Rationale:
    memory rule feedback_verify_before_deleting_dead_code.md forbids
    dead-code verdicts without whole-tree consumer grep + docs/ +
    handoffs + audit deliverables via Rigby. Spot-check found 114
    context_used occurrences across 57 py files (many are OTHER
    models' fields — e.g., `scifi_context_used=bool(...)` on
    execution rows), and 101 agent_results occurrences across 22
    files. Distinguishing ChatConversation.field writes from other-
    model reads requires the S1302 §14.3 F1 dead-code methodology
    (owner+field-name-qualified grep on read pattern). Deferred to
    §19 as a follow-on audit target, NOT declared dead code here.
  Anchor evidence carried into synthesis: (a) S1302 §17.3
  ConversationMemory name-collision resolution, (b) S1302 §14.3 F1
  dead-code detection pattern (applied as F4-CANDIDATE, not F4-
  CONFIRMED, per verifier discipline), (c) memory rule
  feedback_session_tool_retire_works.md (F2 confirmed via direct
  read of td_handlers_core.py:4011-4072), (d) S1300 parent §3F stale-
  thread drift bullet (S1212 deliverable 777d9cd8, ~$3.60/day)
  RECONCILED — S1248 shipped the fix in two matched sites
  (retire handler at td_handlers_core.py:4011 + dispatcher gate at
  conversation_action_dispatcher.py:288-316). Chris ratified D10
  PROCEED + D11 RETAIN (`pa-aa54193f240f4846`) at S1303 open turn 1.
  Rigby SIGN routing planned via fresh isolation pin after v0.2 draft
  (playbook §15 "Child audit — Required full SIGN").
  v0.1 draft (2026-07-01, S1303 open): audit skeleton laid down per
  DOMAIN_RESEARCH_PLAYBOOK v2 §11.2 (20-section child audit template).
  Frontmatter registers first-inventory discipline — Category F has no
  S1273 §3.N row today; §7 (Runtime Flows) is planned load-bearing;
  §11 (Existing Documentation) expected LIGHT or NONE per playbook §12
  classification. §13 6-parallel-Explore sweep dispatched at skeleton-
  write time.
owner: claude (drafted S1303)
---

# Memory Domain (Category F) — Conversational / Thread Memory Architecture Audit

> **Scope.** Category F from parent `1300_memory_domain_scoping.md` §3F:
> ChatConversation identity, PA session pin semantics (`pa-*` strings),
> `session_tool` action surface (`create_fresh` / `retire` / `set_active`
> / `seed` / `health_check` / `list_recent` / `whoami`), tool-call
> history reinjection into subsequent turns, pin rotation policy
> (retire vs continue heuristics), and PA `unified_pa_entrypoint`
> enrichment pipeline as it relates to session identity carry-forward.
>
> **Anti-scope.** Category A (Semantic Knowledge Memory), B (Personal-
> Adaptive Memory), C (Agent Working Memory), D (RAG Retrieval Lanes),
> E (Documentation Corpus), G (Mission / Execution Memory — delegated
> to Employee OS 1200s arc), H (Runtime / Cache Memory — S1305 owned)
> are OUT OF SCOPE. When boundaries touch, cite the sibling audit and
> stop.
>
> **First-inventory notice.** Cat F has no
> `platform_architecture_inventory.md` §3.N row today. This audit
> produces the terrain, not just a re-inventory. §7 (Runtime Flows)
> and §4 (Major Models) are load-bearing. §11 (Existing Documentation)
> confirmed LIGHT per playbook §12 (see §11-§12 verdict).

---

## 1. Executive Summary

Category F — Conversational / Thread Memory — is the load-bearing
runtime substrate for every PA turn on the platform. It carries:
(a) the `pa-*` session pin identity that binds a series of PA turns
into one conversational thread; (b) the persisted turn history that
survives Celery worker recycling and gets reinjected into each new
LLM prompt; (c) the retire/set_active lifecycle that gates whether
retired threads receive downstream agent dispatches. The domain is
**PARTIAL/WORKING** — active-session flows are STABLE (session pin
generation, retire handler, retired-thread dispatcher gate all shipped
and tested), but retention / cleanup / observability edges are
MISSING (no auto-cleanup job for retired rows, no EventBus emission
for turn or session events, no notification surface for turn errors).

**Biggest gaps discovered:**

1. **No cleanup for retired rows.** `session_tool.retire` bulk-flips
   `session_active=False` but no Celery task or management command
   deletes/archives old retired rows. Retained indefinitely (§8
   Data Ownership + Lifecycle; §18 Ownership Gaps).
2. **No event emission on Cat F state changes.** The EventBus
   infrastructure (`core/event_bus.py`) exists with 8 streams
   defined; zero of them are `CONVERSATION_*`. ChatConversation
   writes are silent to observability + downstream consumers (§10
   Event Flows; §14 F7 drift class).
3. **Turn context does not enrich RAG queries.** S1301 Cat D found
   RAG lanes are tool-call-only; this audit confirms Cat F never
   feeds turn history into any RAG query — no auto-injection of
   recent turn context into `kb_tool semantic_search` calls (§9
   integration row Cat F ↔ Cat D = MISSING; §19 R3).
4. **Two orphan-field candidates.** `ChatConversation.context_used`
   and `ChatConversation.agent_results` show heavy producer surface
   but consumer-side reads are unclear on quick spot-check — flagged
   as F4-CANDIDATE for a follow-on S1302 §14.3-methodology sweep,
   NOT declared dead code here per memory rule
   `feedback_verify_before_deleting_dead_code.md` (§14 F4; §19 R1).
5. **Pin rotation cadence lives only in `tools/pa_local.sh` header
   comments.** No formal policy doc, no automation, no audit trail
   for retire-vs-continue decisions. Rigby SIGN closes generate
   retire decisions; those decisions live only in handoffs (§14 F8;
   §18 Ownership Gaps).
6. **Reinjection metadata contract is undocumented (post-SIGN cycle
   1 E9).** `ChatConversation.metadata` carries load-bearing keys
   consumed by the turn-history reinjection path — `tool_calls`,
   `tool_results`, `response_id`, `source` — but no schema, no type
   annotations, and no formal contract lists what keys can appear
   or which writers own them. Silent regression risk if any writer
   drops a key or changes shape. Captured in §20.9 "Reinjection
   Metadata Contract"; also distinguishes model fields vs metadata
   dict keys to prevent F4-style false dead-code claims (§14 F4).

**Next research (§19 ranking):** R1 — full-tree verification of the
F4 phantom-field candidates (highest architectural uncertainty × risk
× unblocked flows because if confirmed dead, feeds into S1302 §14.3
methodology reuse); R2 — Cat F ↔ EventBus adoption design
preparation (delegate to Group 1700 Observability); R3 — turn-
context → RAG enrichment design preparation (delegate to S1304 Cat E
↔ D boundary); R4 — cleanup / retention lifecycle for retired rows.

Verifier discipline: two Agent-6 claims (F3 "would fail at import
time"; F4 "confirmed dead code") were downgraded during the parent-
Claude spot-check per playbook §14 grep-verify rule and memory rule
`feedback_verify_before_deleting_dead_code.md`. Corrections captured
in `verifier_loop:` frontmatter + §20.6.

---

## 2. Domain Purpose

**Domain purpose.** Category F is the state layer that makes a series
of PA turns feel like one continuous conversation: it (1) mints and
carries the `pa-*` pin that scopes turn history for a user; (2)
persists every user↔assistant exchange with its tool-call metadata so
context survives Celery worker `max_tasks_per_child` recycling; (3)
reinjects that history into the next turn's LLM prompt for coherence;
(4) gates dispatch of downstream agent runs behind a retire flag so
retired threads stop consuming compute. Without Cat F, each PA turn
would be a fresh cold-start; the whole "let's continue where we left
off" affordance depends on it.

**Category F ↔ Cat B boundary statement (post-S1302 §17.3
resolution).** The Django model class named `ConversationMemory` at
`core/models/conversations/models.py:19` is Category B (personal-
adaptive memory — S1302-owned). The in-process class named
`ConversationMemory` at `core/conversation_memory.py:59` is Category
F — it is a **facade** that wraps a Django model (not the same one:
per S1302 §17.3, the facade delegates to the Django model at the
same file, but the semantics are legacy-chat-path continuity, not
personal-adaptive learning). The primary Cat F storage model is
`ChatConversation` at `core/models/conversations/models.py:59` — that
is the row-per-exchange table that carries pin identity, session
lifecycle, and per-turn metadata. Anywhere this audit says "Cat F
conversation storage" without further qualification, that means
`ChatConversation`.

**Playbook §9 Q#1 (What is this domain for?).** Session identity + turn
persistence + turn-history reinjection + retire lifecycle for PA turns.

**Playbook §9 Q#2 (Who or what depends on it?).** Every PA REST call
(`/api/pa/chat/*`), every WebSocket PA consumer, the tool-dispatch
layer (`tool_dispatcher.py`), the enrichment pipeline (12+ services
lazy-loaded by `unified_pa_entrypoint.py`), the downstream agent-
dispatch layer (`conversation_action_dispatcher.py`), and every
frontend surface that renders PA conversation state.

---

## 3. Canonical Entry Points

The load-bearing entry points where PA turns cross the Cat F boundary:

| Entry Point | Path:Line | Kind | Notes |
|-------------|-----------|------|-------|
| `POST /api/pa/chat/` | `core/urls*.py` (canonical route per CLAUDE.md line 34) | REST | Async dispatch — enqueues `process_pa_chat_task` on Celery; returns `task_id`. Compat routes `/api/assistant/chat/` + `/api/v1/assistant/chat/` deprecated per CLAUDE.md. |
| `GET /api/pa/chat/status/<task_id>/` | `core/urls*.py` | REST | Poll Celery task status (Session 974b async pattern). |
| PA turn Celery task | `core/tasks.py:11912` (`process_pa_chat_task`) | Task | Entrypoint from the REST layer into `UnifiedPAEntrypoint.process_message()`. |
| `UnifiedPAEntrypoint` orchestrator | `core/services/unified_pa_entrypoint.py:216` (class def) | Service | 7613-line god-service; owns turn flow + tool loop + enrichment + history reinject. Entry at `process_message()` (per Agent 2). |
| `_load_conversation_history_from_db()` | `core/services/unified_pa_entrypoint.py:7277` | Method | Load-bearing turn-history reinject entry. 10-row conversation-scoped window at line 7300-7302. |
| `ChatConversation.get_or_create_session()` | `core/models/conversations/models.py:190` | Classmethod | Session identity mint + retrieval (24h reactivation window). |
| `session_tool` handler | `core/services/td_handlers_core.py:3864` (`_handle_session`) | Tool handler | 7 actions: `health_check` (3868), `create_fresh` (3881), `list_recent` (3930), `whoami` (3961), `retire` (4011), `set_active` (4074), `seed` (4109). |
| `session_tool` schemas | `core/services/pa_tool_schemas.py:4719-4797` (per Agent 3) | Tool schemas | 7 actions × JSONSchema for LLM function-calling. |
| WebSocket `ws/pa/conversations/<conversation_id>/` | `core/consumers_pa_conversation.py:175` (`PAConversationConsumer`, per Agent 3) | WS consumer | Session 1172 live tool ticker + 3-way messaging (user / claude-code / Rigby). |
| `conversation_action_dispatcher.dispatch_actions()` | `core/services/conversation_action_dispatcher.py:280` (retired-thread gate at 288-316) | Service | Post-turn dispatch of `next_steps` items. S1248 gate ensures no dispatch into retired threads. |
| `tools/pa_local.sh` wrapper | `tools/pa_local.sh:115` (final command) | CLI | Ships the arc pin hardcoded (currently `pa-aa54193f240f4846`); header comments are the only place pin-rotation policy is documented. |

**Client entry (used by Claude Code sessions):** `python tools/pa_chat.py "msg" --tools --conversation <pin>` per CLAUDE.md lines 8-9. Rigby is the primary conversational surface; every PA turn originates here or from the browser Chat UI.

---

## 4. Major Models

### 4.1 `ChatConversation` — Cat F primary storage (`core/models/conversations/models.py:59`)

Row-per-exchange table. One row = one user message + one assistant
response + all associated metadata. Session pin identity is the
`conversation_id` CharField. Cat F depends on this model as the
sole persistence surface for conversational state.

| Field | Type | Line | Purpose | Cat F relevance |
|-------|------|------|---------|-----------------|
| `user` | FK → auth_user (nullable, on_delete=CASCADE) | 69 | Owner (nullable for unlinked Discord users per S455) | Ownership + auth check |
| `conversation_id` | CharField(255, db_index=True), NOT FK | 76 | Session pin string — format `pa-<uuid.hex[:16]>` per session_tool.create_fresh (verified at `td_handlers_core.py:3885`) | **Load-bearing.** This is the pin. |
| `user_message` | TextField | 77 | Raw user input for this exchange | Turn history payload |
| `assistant_response` | TextField | 78 | Raw assistant output for this exchange | Turn history payload; truncated to 8000 chars during reinject (S1085) |
| `source` | CharField(30, choices) | 89 | Actor origin: `web` / `mobile` / `discord` / `api` / `claude-code` / `pa` | Speaker attribution in turn reinject (line 7316-7317 prefixes non-web) |
| `platform` | CharField(20, choices) | 104 | Platform origin: `web` / `discord` / `api` / `mobile` | Discord rows excluded from history load (line 7294) |
| `discord_user_id` / `discord_channel_id` / `discord_guild_id` | CharField(30, nullable, indexed on user_id) | 113-131 | Discord-native identity for unlinked users (S455) | Enables cross-platform session continuity |
| `session_title` | CharField(200, blank) | 134 | Auto-generated title (not updated after first turn per Agent 4) | Displayed in `list_recent` output |
| **`session_active`** | BooleanField(default=True, db_index=True) | 139-143 | **Retire marker.** `session_tool.retire` flips to False; `set_active` flips back. | **Load-bearing.** Retired-thread dispatcher gate reads this. |
| `workspace` | FK → `core.ProjectWorkspace` (nullable, SET_NULL) | 146-154 | Workspace scoping when the conversation started from a workspace | Set once at conversation start; not reactively re-scoped (per Agent 4) |
| `context_used` | JSONField(default=dict) | 157 | RAG context if any | **F4-CANDIDATE** — heavy producer surface, consumer surface unverified (see §14 F4 + §19 R1) |
| `metadata` | JSONField(default=dict) | 158 | Tool-call metadata: `tool_calls`, `tool_results`, `response_id`, `source` | Read at line 7311-7336 during turn reinject — CONFIRMED live consumer |
| `response_time_ms` / `model_used` / `provider_used` | Int / CharField | 161-163 | Performance metrics | Displayed in frontend; no downstream alert (per Agent 4) |
| `agents_used` | JSONField(default=list) | 166 | List of agent identifiers invoked during this turn | LIGHTLY-USED per Agent 6 (read in list/stats paths, not active turn) |
| `agent_results` | JSONField(default=dict) | 167 | Per-agent output payload | **F4-CANDIDATE** (see §14 F4 + §19 R1) |
| `created_at` | DateTimeField(auto_now_add=True) | 169 | Row creation timestamp | Sort key for turn ordering |

**Indexes:** `('user', '-created_at')`, `('conversation_id',)`, `('platform', '-created_at')`, `('discord_user_id', '-created_at')`, `('session_active', '-created_at')` at lines 174-179.

**Session identity classmethod:** `ChatConversation.get_or_create_session()` at line 190 — returns an existing active session within a 24-hour window (line 212 `cutoff = timezone.now() - timedelta(hours=24)`) or mints a new `str(uuid.uuid4())` id. This is a separate identity-mint path from `session_tool.create_fresh` (which uses `pa-<hex>` format). See §17 for the two-format-two-mechanism boundary flag.

### 4.2 Boundary — Django `ConversationMemory` at `models/conversations/models.py:19` (Cat B, S1302-owned)

Per S1302 §17.3 name-collision resolution: **flagged for boundary
visibility only; NOT audited here.** This model owns:
`user_message`, `response`, `agents_used`, `intent`, `success`,
`created_at`, `embedding` (pgvector 1536d, S729). It stores
personalization / semantic-search-ready user↔agent exchanges — a
different substrate than Cat F's `ChatConversation` (row-per-turn
with session pin identity). S1302 owns any changes to this model.

### 4.3 In-process facade `ConversationMemory` at `core/conversation_memory.py:59` — Cat F wrapper

211-line facade class. Methods:
- `save_conversation(user_id, user_message, assistant_response, metadata={})` — persists to `core.models.ConversationMemory` (the Cat B Django model) via `ConvModel` alias at line 87 (verified this import direction is correct).
- `get_conversation_history(user_id, limit=10)` — read-through for legacy chat-path consumers.
- `update_knowledge_metrics(user_id)` — dashboard stats aggregation.

Singleton at line 211: `conversation_memory = ConversationMemory()`.

**Consumer inventory** (from Agent 1 grep sweep):

- **Pattern A — `from core.models import ConversationMemory` (Cat B Django model direct):**
  `core/learning_bridges/personalization_bridge.py`, `core/epa_handlers_utility.py` (3 sites), `core/tasks_misc.py`, `core/tasks_conversations.py`, `core/services/content_idea_pipeline.py` (2 sites), `core/services/ops_autopilot/intelligence.py`.
- **Pattern B — `from core.conversation_memory import conversation_memory` (Cat F facade singleton):**
  `core/views/main.py:925`, `core/views.py:1094` (S1235 pivot PR).
- **Pattern C — `from core.conversation_memory import ConversationMemory` (facade class, rare):**
  `tests/unit/test_verbosity_fix.py` (test-only).
- **Pattern D — WRONG:** `core/agents/content_writer_agent.py:76` — `from core.models_unified_system import ConversationMemory` — see §14 F3 (SOFT FAIL under try/except guard).

### 4.4 `UserMemoryContext` at `models/conversations/models.py:253` — adjacent

18-choice `memory_type` enum. Boundary flag: S1302 §14.5 tags this
as boundary-adjacent to Cat B; Cat F does not own it. Cited here for
navigational completeness only.

### 4.5 `PaMessageFeedback` at `models/conversations/models.py:332` — Cat F (per Agent 1)

UUID PK. PA message thumbs-up/down (S1085, rebuilt S1243). Field
`conversation_id_str` (CharField 255, `db_index`) stores `pa-*` pin
strings **without an FK** to `ChatConversation.conversation_id`.
Unique constraint on `(user, conversation_id_str, message_index)`.
Design choice: intentional decoupling (S1085 rebuild context per
Agent 1); operational trade-off: cascade deletion of a
`ChatConversation` leaves orphan feedback rows (see §18).

**No other Cat F models found in sweep.**

---

## 5. Major Services

### 5.1 `unified_pa_entrypoint.py` — **GOD-SERVICE**

- **Path:** `core/services/unified_pa_entrypoint.py`
- **Line count:** **7,613** (verified) — flag per playbook §13 Agent 2 (>3000 lines).
- **Top-level classes:** `UnifiedPAEntrypoint`, `PAResponse`.
- **Role:** PA front-door. Owns: turn processing, context enrichment,
  function-calling loop, turn-history reinject, tool-call carry-
  forward, feature-flag gating.

Load-bearing lines (verified during spot-check):

- **`_load_conversation_history_from_db()`** at line 7277 — 10-row
  conversation-scoped window (line 7300-7302); Discord rows excluded
  (line 7294); 5-second `SET LOCAL statement_timeout = '5000'`
  (line 7291) so DB hiccups don't block startup; assistant response
  truncated to 8000 chars (line 7327, post-S1085 bump from 2000);
  tool-call metadata reinjected via `meta.get('tool_calls')` and
  `meta.get('tool_results')` (lines 7331-7336). Silent fail-open on
  exception (line 7342 sets `self._conversation_history = []` and
  logs debug-level only).
- **`PA_USE_FUNCTION_CALLING` env gate** at line 684 (per Agent 2) —
  memory rule `feedback_pa_worker_function_calling_env.md`
  confirmed. If False, source=claude-code messages short-circuit to
  `claude_code_coordination` intent (no tool path). Turn-history
  persistence is env-agnostic (verified per Agent 6 F6 → NO DRIFT).
- **Function-calling loop entry** at line 686 (per Agent 2) —
  `_run_agentic_loop()`; injects `arguments['conversation_id']` +
  `arguments['_bound_conversation_id']` sentinel (line 1771-1773
  per Agent 2) so `session_tool.retire` can trust its
  currently-bound check without trusting LLM-supplied fields.
- **Turn-history trim** at line 928-929 (per Agent 2) — caps
  in-memory history at 20 turns after each new turn.
- **Enrichment orchestration** at line 743-751 (per Agent 2) — fires
  15-second-budgeted service chain (intelligence, spider, blog,
  domain) on tool-run success.

**Cross-domain touch matrix** (per Agent 2): 20+ lazy-loaded property-
based services + 30+ in-function imports. Touches Cat A/B/C/D/E/F/G
per Agent 2's coupling scorecard. Necessary as orchestrator; density
is intentional. Extraction risk: any refactor of Cat F storage or
turn-reinject semantics must trace all 7613 lines.

### 5.2 `td_handlers_core.py`

- **Path:** `core/services/td_handlers_core.py`
- **Line count:** **4,168** (verified).
- **Top-level class:** `CoreHandlersMixin`.
- **Cat F handler:** `_handle_session(tool_name, payload, user_id, trace_id)` at line 3864-4166 (spans ~300 lines for the 7 actions).

Session action inventory (verified via direct read of 3864-4072 + Agent 2 extraction of 4074-4166):

| Action | Handler line range | Args | Return shape | Verifier notes |
|--------|--------------------|------|--------------|----------------|
| `health_check` | 3868-3879 | `conversation_id` (optional; falls back to `getattr(self, '_current_conversation_id', None)` at line 3871) | `{ action, ...health_dict }` (delegates to `get_session_health()` at `core/services/session_health_service`) | health details opaque here; see §16 for scoring authority UNKNOWN |
| `create_fresh` | 3881-3928 | `title` (str), `carry_forward_summary` (str) | `{ action, conversation_id, title, starter_prompt, message }` | Pin format `pa-{uuid.uuid4().hex[:16]}` (per Agent 1 at line 3885). Writes first ChatConversation row. |
| `list_recent` | 3930-3959 | `limit` (int, default 10, capped 25) | `{ action, conversations: [...], count }` | DB `.values(...).annotate(message_count, last_message)` per Agent 3 |
| `whoami` | 3961-4009 | `conversation_id` (optional) | `{ action, user_id, username, email, is_staff, is_superuser, conversation_id, conversation_owner_user_id, conversation_owner_username, conversation_owner_match }` | Added S1226 to close ownership-verification gap per Agent 3 |
| **`retire`** | **4011-4072** | `conversation_id` (required), `_bound_conversation_id` (sentinel-injected by PA entrypoint), `force` (bool, default False) | `{ action, conversation_id, is_current_bound, previously_active, retired: True/False, updated_count, [pin_rotation_notice] }` | **Verified directly** — memory rule `feedback_session_tool_retire_works.md` confirmed. Guards: refuses self-retire without `force=True` (line 4035-4050). Bulk update at line 4054. **Post-SIGN cycle 1 nuance (E8):** `force=True` is REQUIRED when the target pin equals `_bound_conversation_id`. Response includes `updated_count` (see line 4062) so caller can distinguish first-retire from double-retire; if the conversation is already fully retired, `updated_count=0` — behaviour is idempotent (`filter(session_active=True).update(...)` returns 0 rows updated). |
| `set_active` | 4074-4107 | `conversation_id` (required) | `{ action, conversation_id, previously_retired, reactivated: True, updated_count }` | Inverse of retire; symmetric + idempotent per Agent 2 |
| `seed` | 4109-4163 | `conversation_id` (required), `content` (required, non-empty) | `{ action, conversation_id, seeded: True, seed_message_id, content_length, marker: '[SYSTEM SEED]' }` | Rejects empty content (S1247 F2 fix per Agent 2) |

**S1248 sign-off provenance** captured inline in code comments at
`_handle_session`: line 4016 "Design Qs signed off by Rigby on
pa-3901b70e61934df7 (S1248): Q1(c) — require force=True if retiring
the currently-bound thread"; line 4079 "Design Qs signed off by
Rigby: Q2(c) — scope this PR to un-retire only."

### 5.3 `conversation_action_dispatcher.py` — retired-thread gate owner

- **Path:** `core/services/conversation_action_dispatcher.py`
- **Line count:** 716 (verified).
- **Top-level classes:** `ConversationActionDispatcher`, `DispatchResult`, `ParsedAction`.
- **Role:** Parses agent `DecisionSummary.next_steps` → Celery task
  dispatch after a PA turn completes.

**S1248 retired-thread gate at lines 288-316** (verified directly):

- Line 292: `allow_retired = bool(ctx.get('allow_retired'))` — staff/debug bypass.
- Line 293: `convo_qs = ChatConversation.objects.filter(conversation_id=conversation_id)`.
- Line 294: `has_active = convo_qs.filter(session_active=True).exists()`.
- Line 296: If `has_any and not has_active` (thread exists but every row retired) → block dispatch (line 305-316).
- Line 317-323: Fail-open envelope — `try/except` around the whole gate; DB hiccups do NOT block the live dispatch path (fail-open is intentional, per code comment).

This is the load-bearing fix for the S1212 stale-thread dispatcher
waste (deliverable `777d9cd8` — ~$3.60/day). Verified matched with
the retire handler side of the fix (§5.2). **F1 RECONCILED** — see §14.

### 5.4 `core/conversation_memory.py` — in-process facade (Cat F)

- **Path:** `core/conversation_memory.py`
- **Line count:** 211 (verified).
- **Class:** `ConversationMemory` (facade) — see §4.3.

Legacy-chat-path continuity shim. Hallucination filter at line 49-56
blocks pre-S1235 fitness-tracker hallucinations (Flutter / dashboard_
page.dart / etc.) from persisting. Two view consumers only
(`core/views/main.py:925`, `core/views.py:1094`). Not on the modern
PA path; would be a candidate for deprecation but Cat B / S1302
should decide since the facade delegates to the Cat B Django model.

### 5.5 `tool_dispatcher.py` — session_tool routing

- **Path:** `core/services/tool_dispatcher.py` (per Agent 2)
- **Line count:** 1,267 (per Agent 2).
- **Role:** Central tool-call orchestrator; routes `session_tool.*`
  to `_handle_session`. Records ToolCallRecord + injects
  conversation_id / trace_id at dispatch time (Agent 2 lines
  1797-1855).

### 5.6 Other services touched (out-of-scope for deep audit)

- `session_health_service` (called by `_handle_session[health_check]`)
  — scoring algorithm not audited here; boundary to a downstream
  audit if health-score becomes load-bearing for automation. UNKNOWN
  per §16.
- `pa_intelligence_enricher`, `docs_context_builder`,
  `spider_context_builder`, `blog_performance_context`,
  `domain_content_context`, `advisor_context`, and ~15 other
  enrichment services — lazy-loaded properties on
  `UnifiedPAEntrypoint`. Cat B/C/D/E/G territory; consume Cat F
  session identity but do not own it. See §9 integration table.

---

## 6. Major APIs and Interfaces

### 6.1 REST endpoints (per Agent 3, cross-referenced against CLAUDE.md line 34)

| Endpoint | Method | Handler | Auth | Cat F role |
|----------|--------|---------|------|-----------|
| `/api/pa/chat/` | POST | `unified_pa_chat` (views_personal_assistant.py:267 per Agent 3) | Token; fleet warn per S1132 | Ingress. Enqueues `process_pa_chat_task`. |
| `/api/pa/chat/status/<task_id>/` | GET | `pa_chat_status` (location UNKNOWN per Agent 3) | Token | Poll Celery task status |
| `/api/pa/conversations/` | GET | `list_pa_conversations` | IsAuthenticated | List recent per user (limit 25 default) |
| `/api/pa/conversations/new/` | POST | `create_pa_conversation` | IsAuthenticated | Fresh conversation mint (UUID pa-* format) |
| `/api/pa/conversations/<conversation_id>/` | GET | `get_pa_conversation` | IsAuthenticated + owner check | Full transcript |
| `/api/pa/conversations/<conversation_id>/message/` | POST | `pa_conversation_post_message` (views_personal_assistant.py:521) | IsAuthenticated + owner | Store-only message endpoint (3-way chat surface) |
| `/api/pa/conversations/<conversation_id>/messages/` | GET | `pa_conversation_messages` (views_personal_assistant.py:630) | IsAuthenticated + owner | Poll recent messages (`?after=<id>` supported) |
| `/api/pa/conversations/<conversation_id>/health/` | GET | `session_health` (views_personal_assistant.py:1715) | IsAuthenticated | Health score + starter prompt (S1087) |

Compat routes `/api/assistant/chat/` + `/api/v1/assistant/chat/` are
deprecated per CLAUDE.md line 34.

### 6.2 PA tool schemas + handlers (per Agent 3)

| Tool | Actions | Schema location | Handler location |
|------|---------|-----------------|------------------|
| `session_tool` | 7 (health_check, create_fresh, list_recent, whoami, retire, set_active, seed) | `pa_tool_schemas.py:4719-4797` | `td_handlers_core.py:3864` (§5.2 above) |
| `conversation_tool` | 5 (get, search, summary, pin_memory, recent) | `pa_tool_schemas.py:2186-2221` | `td_handlers_core.py:1966` (`_handle_conversation`) — cross-thread PA recall via pgvector CosineDistance + keyword fallback |
| `remember_tool` | 4 (save, list, delete, search) | `pa_tool_schemas.py:2134-2180` | `td_handlers_core.py:2192` (`_handle_remember`) — persistent memory (18 types); PII/secret redaction |
| `schedule_followup` | 1 (no action enum) | `pa_tool_schemas.py:4803-4834` | `td_handlers_agents.py:5126` (`_handle_schedule_followup`) — arms Celery task `agent_followup_fire` on completion |

**Handler registration** at `tool_dispatcher.py` lines 339, 449, 452,
563 per Agent 3. No orphan schema (schema without handler) or orphan
handler (handler without schema) detected.

### 6.3 WebSocket consumer (per Agent 3)

- **Path:** `core/consumers_pa_conversation.py:175`
- **Class:** `PAConversationConsumer`
- **Group:** `pa_conversation_{conversation_id}` (per Agent 3)
- **Events emitted:** `message.created`, `participant.typing`,
  `participant.joined`, `rigby.tool.started`, `rigby.tool.completed`
- **Backend push pattern:**
  `channel_layer.group_send(f"pa_conversation_{cid}", {...})` (per Agent 3)
- **Lifecycle:** connect → authenticate via scope['user'] → join
  group → accept. Disconnect → leave group.

Session 1172 live tool ticker + 3-way messaging (user / claude-code / Rigby).

### 6.4 Celery tasks (per Agent 3)

| Task | Location | Purpose |
|------|----------|---------|
| `process_pa_chat_task` | `tasks.py:11912` | Main PA turn processing; entrypoint from `/api/pa/chat/` |
| `process_pa_tts_task` | `tasks.py:12042` | TTS audio generation post-turn |
| `summarize_conversation_task` | `tasks.py:13072` | Async LLM summarization for `conversation_tool.summary` |
| `agent_followup_fire` | `tasks_agents.py` (inferred per Agent 3) | Fire follow-up when `AgentFollowupSubscription` TTL arms |
| `backfill_conversation_embeddings` | `tasks.py:3752` | Backfill pgvector embeddings for Cat B `ConversationMemory` (S729) |
| `cleanup_conversation_duplicates_task` | `tasks.py:12317` | Dedup `AgentConversation` (S1032) — Cat B/C adjacent |
| `broadcast_conversation_status` | `tasks.py:3250` | Broadcast state changes via WebSocket |

**Beat schedule:** none of these are periodically scheduled per Agent
3 sweep of the beat table; all are ad-hoc dispatched. **UNKNOWN
whether Procfile / Makefile queue parity is intact** for these
tasks — memory rule `feedback_procfile_makefile_queue_parity.md`
applies but not verified in this audit.

### 6.5 Management commands (per Agent 3)

| Command | Purpose |
|---------|---------|
| `session_provenance` (`management/commands/session_provenance.py:71`) | Cluster docs by session via git history + frontmatter override; read-only |
| `cleanup_conversation_duplicates` (`management/commands/cleanup_conversation_duplicates.py:29`) | Fuzzy-duplicate detection over `AgentConversation`; dry-run default; `--fix` to delete |
| `pa_acks_health` (`management/commands/pa_acks_health.py`) | Health check for `/api/pa/chat/` availability |

None of these delete/archive retired `ChatConversation` rows. See §18.

### 6.6 Frontend touchpoints (per Agent 3 skim)

- PA Chat UI state store: `frontend/src/stores/paStore.ts` (WebSocket
  subscription to `ws/pa/conversations/<id>/`; user-scope clear
  logic at line 181 to prevent cross-user bleed).
- Conversation detail route: `frontend/src/App.tsx:112` (per Agent 3).
- Session health / fresh button: implicit in PA chat; polls
  `/api/pa/conversations/<id>/health/`.

### 6.7 Missing surface (per Agent 3 MISSING classification)

Explicit gaps flagged for §19:

1. **Conversation search by title** — no REST/tool to filter by
   `session_title`; must use `conversation_tool.search` which
   searches user_message (not title).
2. **Conversation archive / soft delete** — retire is a scope-gate
   flip (`session_active`), not a visibility archive. Retired rows
   still surface in `list_recent` unless filtered client-side.
3. **Pin lifecycle history query** — `conversation_tool.pin_memory`
   creates a Deliverable but no queryable per-conversation pin
   index exists.
4. **Cross-user conversation access** — single-user-owned; no
   sharing / grant mechanism.
5. **`pa_chat_status` handler location** — grep found reference at
   `urls.py:2509` per Agent 3 but handler definition not located.
   UNKNOWN.

---

## 7. Runtime Flows (LOAD-BEARING SECTION — first-inventory discipline)

### Flow A — First turn on a fresh pin (`session_tool.create_fresh`)

Per Agent 2 step-by-step + verifier spot-check on line 3881-3928:

1. **Client → REST.** `pa_chat.py` client (or browser) POSTs to
   `/api/pa/chat/` with initial payload (no `conversation_id`).
2. **REST → Celery.** View enqueues `process_pa_chat_task` (task at
   `tasks.py:11912`); returns `{task_id}` to client for polling.
3. **Celery → Entrypoint.** Task instantiates
   `UnifiedPAEntrypoint(user, conversation_id=None)` at line 216.
4. **History load — empty.** `_load_conversation_history_from_db()`
   at line 7277 fires with `self.conversation_id=None`; hits the
   unscoped fallback branch at line 7304-7305 (last 5 rows across
   all conversations) — but for a genuinely fresh session, callers
   typically dispatch `session_tool.create_fresh` first.
5. **Function-calling loop.** LLM picks `session_tool` with
   `action=create_fresh` (or the caller supplies it directly).
   PA entrypoint injects `conversation_id=None` +
   `_bound_conversation_id=None` sentinels at lines 1771-1773.
6. **Handler → ChatConversation.create.** `_handle_session[create_
   fresh]` at line 3881-3928 mints new `pa-<uuid.hex[:16]>`, writes
   ChatConversation row with title + first assistant message,
   optionally calls `get_session_health()` on the old conversation
   to pull a carry-forward starter_prompt (line 3898-3920 per Agent
   1). Returns `{action, conversation_id, title, starter_prompt,
   message}`.
7. **Client pins.** Client updates its wrapper (e.g., editing
   `tools/pa_local.sh` line 115) to use the new pin for subsequent
   turns. **This is manual** — see §14 F8.

### Flow B — Subsequent turn on an active pin (turn-history reinjection)

Per Agent 2 + direct read of line 7277-7343:

1. **Client → REST.** `pa_chat.py "message" --conversation <pin>` POSTs
   to `/api/pa/chat/` with `conversation_id=<pin>`.
2. **REST → Celery → Entrypoint.**
   `UnifiedPAEntrypoint(user, conversation_id=<pin>)` at line 216.
3. **History load — scoped.** `_load_conversation_history_from_db()`
   at line 7277:
   - Query: `ChatConversation.objects.filter(user=user).exclude(platform='discord').filter(conversation_id=<pin>).order_by('-created_at')[:10]` (line 7292-7302).
   - Reversed to chronological order at line 7309 (`reversed(list(recent))`).
   - Each row emits up to 2 turns (user + assistant); assistant
     response truncated to 8000 chars (line 7327 — S1085 bump).
   - Tool-call metadata reinjected: `meta.get('tool_calls')` and
     `meta.get('tool_results')` (lines 7331-7336).
   - Silent fail-open on exception (line 7342-7343 → empty list).
4. **Context builder.** History passed to LLM prompt at line 2511
   per Agent 2 (`context['conversation_history'] =
   self._conversation_history[-10:]` — last 10 turns).
5. **Function-calling loop.** LLM sees prior turns; can reference
   them or call tools.
6. **Per-tool-call injection.** For every tool call, entrypoint
   sets `arguments['conversation_id'] = self.conversation_id` and
   `arguments['_bound_conversation_id'] = self.conversation_id`
   at lines 1771-1773 per Agent 2. This is what
   `session_tool.retire` uses to detect "you're trying to retire
   the thread you're talking through."
7. **Turn persistence.** After the turn completes, a new
   ChatConversation row is written (writer location UNKNOWN in
   sweep — likely in `views_personal_assistant.py` or a task hook;
   see §16).
8. **In-memory trim.** `_conversation_history` capped at 20 turns
   after each new turn (line 928-929 per Agent 2).

**Windowing summary:** DB load = last 10 rows per conversation_id
(chronological); in-memory cap = 20 turns; LLM context = last 10
turns.

### Flow C — Pin retirement (`session_tool.retire`) — verified directly

Direct read of line 4011-4072:

1. **Handler entry** at line 4011. Extracts `target = payload.get('conversation_id')` (line 4027), `bound = payload.get('_bound_conversation_id')` (line 4031), `force = bool(payload.get('force'))` (line 4033).
2. **Validation.** If `target` empty → `{'error': '...requires conversation_id.'}` (line 4028-4029).
3. **Self-retire guard.** `is_current_bound = bool(bound) and target == bound` (line 4032). If `is_current_bound and not force` → refuse with clear message (line 4035-4050); returns `{retired: False, is_current_bound: True, error: '...'}`.
4. **Bulk update.** `ChatConversation.objects.filter(conversation_id=target, user_id=user_id).filter(session_active=True).update(session_active=False)` (line 4052-4054). Records `previously_active` and `updated_count`.
5. **Response.** Line 4056-4063 assembles `{action, conversation_id, is_current_bound, previously_active, retired: True, updated_count}`. If `is_current_bound and force` was used, adds `pin_rotation_notice` (line 4064-4071) instructing wrapper edit at `tools/pa_local.sh` line 70.
6. **Downstream effect.** `conversation_action_dispatcher.dispatch_actions()` at line 288-316 (verified — §5.3) blocks any subsequent `next_steps` dispatch into rows where `session_active=False`.

**Boundary:** retire does NOT delete rows, does NOT tombstone, does
NOT emit any event. It only flips the flag. Cleanup is UNKNOWN — see
§14 F9, §18.

### Flow D — `unified_pa_entrypoint` enrichment pipeline

Per Agent 2:

1. **Trigger.** Line 743: `if tool_runs_raw and any(r.get('ok') ...)`
   after the function-calling loop succeeds.
2. **Intent inference.** Line 722: `_infer_intent_from_tools()`
   (deferred imports at 2350-2489 per Agent 2). Maps to
   `INTENT_ENRICHMENT_MAP` (defined at class level).
3. **Service chain fires.** 15-second total budget via
   `asyncio.wait_for()` at line 746-751. Services:
   `intelligence_enricher`, `blog_performance`, `domain_context`,
   `spider_trends`, `advisor_context`, `platform_briefing` (per
   Agent 2 lines 4086-4150 partial read).
4. **Fire-and-forget per service.** One failure never blocks
   others. Each service reads `self.conversation_id` (line 1807)
   for join keys but does not mutate Cat F state.
5. **`PA_USE_FUNCTION_CALLING=true` gate** at line 684 — if False,
   the whole loop is skipped and message routes to keyword lane
   `claude_code_coordination` (Agent 6 F6, Agent 2 verification
   both confirm turn-history persistence is env-agnostic).

### Flow E — Stale-thread dispatcher pattern (drift RECONCILED)

Anchor: S1212 deliverable `777d9cd8-5526-4acf-a167-374c05e6e425` documented ~$3.60/day waste on retired-thread dispatches.

**Historic problem (pre-S1248):** Agents complete a turn → emit a
`DecisionSummary` with `next_steps` → `conversation_action_
dispatcher.dispatch_actions()` unconditionally parses the steps and
enqueues Celery tasks → tasks fire into threads that had already
been retired (dead pins from `tools/pa_local.sh` retirement record).
24/41 24-hour dispatches (59%) hit retired threads per the deliverable.

**S1248 fix (verified via direct read):**

1. **Retire handler** at `td_handlers_core.py:4011-4072` sets
   `session_active=False` on all rows for the retiring pin.
2. **Dispatcher gate** at `conversation_action_dispatcher.py:288-316`:
   before firing next_steps, checks `has_active =
   convo_qs.filter(session_active=True).exists()` (line 294). If
   thread exists but has no active rows, returns early with a clear
   error at line 305-316 (`Refusing to dispatch into retired
   thread ...`). Emits `logger.warning` (line 315).
3. **Escape hatch** at line 292: `allow_retired=True` context flag
   bypasses the gate for staff/debug (emits WARN log at line
   298-303).
4. **Fail-open envelope** at line 317-323 — DB hiccups do NOT
   block the live path; gate wraps in try/except.

**Post-SIGN cycle 1 nuance (E7).** The retired-thread gate's
enforcement is **best-effort / fail-open** by design: the entire
gate check (lines 288-316) is wrapped in `try/except Exception`
that swallows errors and continues dispatching (line 317-323
`_gate_err` log-warn + fall-through). Availability wins over
correctness under DB errors. That's the right operational
tradeoff, but it means "retired" is not a hard invariant — a
sustained DB fault or ORM regression could let dispatches leak
into retired threads until observability catches it. Compounded
by the escape hatch `allow_retired=True` (line 292; emits WARN
log at line 298-303 but does not alert).

**F1 verdict:** CONFIRMED RECONCILED. §14 F1 severity LOW; residual
observability question (how often is `allow_retired` actually used
in production? How often does the fail-open envelope fire?)
deferred to §14 F7 (Cat F ↔ EventBus MISSING) and §19 R2.

---

## 8. Data Ownership and Lifecycle

**Playbook §9 Q#4-Q#9 answers:**

- **Q#4 Who mints session identity?** Two paths in the code today
  (see §17 for overlap flag):
  1. `session_tool.create_fresh` at `td_handlers_core.py:3885` —
     format `pa-<uuid.hex[:16]>`.
  2. `ChatConversation.get_or_create_session()` at
     `models/conversations/models.py:190-222` — format
     `str(uuid.uuid4())` (no `pa-` prefix), with a 24-hour
     reactivation window.
  Callers currently split by surface (Discord bot uses
  `get_or_create_session` per Agent 3; PA tool loop uses
  `create_fresh`). No unified session broker.
- **Q#5 Who writes rows?** PA turn writer location UNKNOWN in the
  sweep — likely `views_personal_assistant.py` view handlers or
  a task-side hook after the turn completes. Directly writable via
  ORM `ChatConversation.objects.create()` by any service that
  imports the model — no service wrapper / no permission gate (per
  Agent 4 overcoupling flag).
- **Q#6 Who reads rows?**
  - `_load_conversation_history_from_db()` at line 7277 (turn
    reinject) — CONFIRMED consumer.
  - `session_tool.list_recent` handler at line 3930-3959 — read.
  - `session_tool.whoami` handler at line 3961-4009 — read.
  - `session_tool.retire` handler at line 4052 — read + write.
  - `conversation_action_dispatcher.py:293` — read (retire gate).
  - REST endpoints `/api/pa/conversations/*` — read.
  - PAConversationConsumer WebSocket — read for state.
- **Q#7 Retention policy?** **UNKNOWN.** No Celery task, no
  management command, no TTL config found for `ChatConversation`.
  Retired rows (`session_active=False`) live forever unless
  manually deleted. Filed as §14 F9 + §19 R4.
- **Q#8 Orphan detection?** None found. `on_delete=CASCADE` on the
  `user` FK handles user-deletion cascade, but there is no orphan-
  handling logic for unlinked Discord rows (§14 F10), and
  `PaMessageFeedback.conversation_id_str` (CharField, no FK) will
  orphan on ChatConversation delete (§17).
- **Q#9 Reactivation semantics?** `set_active` handler at line
  4074-4107 exists and is idempotent (Agent 2). `get_or_create_
  session` reactivates within 24h (line 212). No formal contract
  for when reactivation is appropriate.

**S1302 §14.3 D3 orphan-write pattern inheritance.** Cat F was
supposed to inherit S1302's row-level orphan-write concern per S1300
parent §5 P3 rationale ("Inherits S1301 §14.3 D3 row-level orphan-
write pattern as first-order scope"). Applied here:
`ChatConversation.workspace` (nullable FK, SET_NULL) does not
maintain a producer↔consumer symmetric write authority — anything
that imports the model can write. This is not strictly the S1302 D3
class (that was about MemoryPromotionService auto-writing without a
gate), but the pattern class is analogous. Filed as §16
OVERCOUPLED-1.

---

## 9. Integrations With Other Domains

Cat F integration map — per Agent 4 sweep + verifier reconciliation:

| From | To | Strength | Evidence path:line | Notes |
|------|-----|---------|-------------------|-------|
| Cat F | Agent System (§3.2) | **WEAK** | `unified_pa_entrypoint.py:686` (`_run_agentic_loop`); tool_dispatcher integration | Turn history loaded from DB per turn (line 7277); reinjected into LLM context (line 2511 per Agent 2). No structured reinjection contract per agent-execution boundary. |
| Cat F | Cat A/B/C Memory (S1302) | **WEAK** | `models/conversations/models.py:19` (Django `ConversationMemory` = Cat B, S1302-owned); `conversation_memory.py:59` (in-process facade = Cat F, delegates to Cat B model) | S1302 §17.3 name-collision resolved by import discipline (§4.3 consumer patterns A-D). No cross-boundary write-authority gate on `MemoryPromotionService` — S1302 F6 finding stands here as an inbound boundary concern (§16). |
| Cat F | Cat D RAG (S1301) | **OBSERVED GAP** (owner confirmation required — reframed post-SIGN cycle 1 E6) | 0 RAG imports in `unified_pa_entrypoint.py` (per Agent 4 grep) | **Observed gap:** No verified wiring found from turn-history reinjection (Cat F) to retrieval query augmentation (Cat D). **Interpretation:** Could be intentional separation (thread memory is user-scoped; corpus retrieval is source-scoped), or missing integration (turn context could enrich query reformulation / intent disambiguation). **Owner confirmation required** before classifying as defect. Filed as §19 R3 for design-preparation-doc-level decision. |
| Cat F | Cat E Docs Corpus (S1304 planned) | **MISSING** | S1301 §19 handoff | Deferred to S1304. |
| Cat F | Employee OS (§4) | **WEAK** | `core/employees/mission_runner.py` — 0 `ChatConversation` imports (per Agent 4). `core/jobs/bug_triage.py:42-43` shows mission_verdict as explicit user tool call, not auto-emit | OpsRun linkage from ChatConversation: PARTIAL. Mission completion → PA turn is user-initiated only (tool call). ChatConversation does NOT emit mission-completion signal. Parent §5 delegated Cat G to Employee OS 1200s arc — this weak-link finding is a delegation-boundary observation, not a Cat F fix scope. |
| Cat F | Content Pipeline (§5) | **WEAK** | `deliverable_factory.py` reads intent + `agents_used`; ChatConversation stores agents_used + agent_results (models.py:166-167) | Deliverables surfaced from PA turns: PARTIAL. `agent_results` field observed as heavy-producer / consumer-unclear (§14 F4-candidate). Content deliberation reads via tool-call argument passing, not via turn-history dump. |
| Cat F | Workspace (§3.19) | **WEAK** | `models/conversations/models.py:146-154` (workspace FK, set at session start); `td_handlers_core.py:134-136` (active_repo cache) | Session ↔ workspace scoping: ONE-DIRECTIONAL. Set once at conversation creation; no reactive re-scoping if user switches workspaces. Active-repo pointer cached per user (Redis, 7-day TTL, per Agent 4) but NOT bound to session lifetime. |
| Cat F | Discord / other interfaces | **WEAK** | `models/conversations/models.py:81-95` (SOURCE_CHOICES + Discord IDs); Session 455 cross-platform continuity | Cross-surface session identity: PARTIAL. `get_or_create_session` (line 190) finds active session per user/discord_user_id/platform. **No unified session broker.** Unlinked Discord users create orphan rows (null user_id) with no return-to-session mechanism (§14 F10). |
| Cat F | Signal Aggregation (§3.7) | **MISSING** | 0 matches for `ChatConversation` in `signal_aggregation_service.py`, `scoring_dispatcher.py`, `platform_event_view.py` (per Agent 4 grep) | Turn events → signals: NOT WIRED. ChatConversation rows (user intents, agents_used) NEVER feed SignalCluster. Signals → PA context is unidirectional only (via enrichment). |
| Cat F | Observability / Telemetry (§3.25) | **MISSING** | `core/event_bus.py:21-31` (8 streams); 0 `CONVERSATION_*` streams; `scoring_dispatcher.py:282,480` (only publisher confirmed) | Session lifecycle → observability sink: NOT WIRED. See §14 F7. |
| Cat F | HumanAttention (§3.18) | **MISSING** | 0 hits for `conversation.*notification` or `turn.*alert` (per Agent 4) | Turn completions do not emit web-push / Discord / inbox notifications. No escalation for long-running or error states per turn. |
| Cat F | Frontend / Workspace UI (§3.17) | **WEAK** | `models/conversations/models.py:157-158` (context_used + metadata JSONFields); `views_personal_assistant.py`; auto-generated session_title | Frontend receives per-turn metadata; polls ~15s (S1274 §1 finding #2 pattern applies). Session title auto-set at first turn, never updated (per Agent 4). |

**Overcoupling summary** (per Agent 4 §6):

- PA entrypoint writes ChatConversation directly — no service wrapper.
- `agent_results` schema coupling — content deliberation reads
  JSONField shape that has no formal contract.
- `session_tool` state machine tightly bound to
  `session_active` BooleanField — evolving to a multi-state
  machine (draft/active/archived) would require handler rewrite.

See §16 for full overcoupling table.

---

## 10. Event Flows

Playbook §9 Q#19 + Q#20:

**Producers.** Zero Cat F event streams. `core/event_bus.py:21-31`
declares 8 streams (per Agent 4); the only confirmed active
publisher is `scoring_dispatcher.py:282,480`
(`OPPORTUNITY_SCORED`). No `CONVERSATION_CREATED` /
`CONVERSATION_RETIRED` / `TURN_PROCESSED` streams exist.

**Consumers.** Three consumer tasks exist (`tasks.py:4726, 4760, 4794`
→ `process_event_bus_scoring_queue`, `_validation_queue`,
`_analytics_queue` per Agent 4); none listen for conversation events.

**Direct-call pattern.** All Cat F state changes today are synchronous
ORM writes in the request handler. Post-turn work (enrichment,
dispatch_actions) is directly called, not event-mediated.

**S1274 continuity.** S1274 flagged EventBus as "partially implemented,
weakly adopted, unverified end-to-end." Cat F adoption = **0**.

**Verdict:** No event flow for Cat F. Filed as §14 F7 + §19 R2
(delegate to Group 1700 Observability future arc).

---

## 11. Existing Documentation

Per Agent 5's exhaustive sweep, docs touching Cat F:

| Path | Coverage | Notes |
|------|----------|-------|
| `docs/research/domains/memory/1300_memory_domain_scoping.md` §3F | OUTLINE | Names systems, no architecture detail |
| `docs/research/domains/memory/1301_memory_rag_retrieval_lanes_audit.md` §14.2 / §19 | STUB | Silent-failure class pattern (adjacent); routes provenance drift downstream |
| `docs/research/domains/memory/1302_memory_persistence_architecture_audit.md` §17.3, §14.3 F1, §19.1 | OUTLINE | Name-collision resolution; dead-code detection methodology; hands S1303 the boundary |
| `docs/handoffs/SESSION_1212_AGENTS_REFERENCE_AND_PA_SPEND_AUDIT.md` (deliverable `777d9cd8`) | COMPLETE | Stale-thread dispatcher waste: 24/41 24h dispatches on retired threads; ~$3.60/day burn; 3 fix options (A/B/C); Lean A |
| `docs/handoffs/SESSION_1300/1301/1302` | STUB | Group 1300 sibling handoffs |
| `docs/PLATFORM_WHAT_IT_IS.md` | OUTLINE | PA section mentions "conversation IDs rotate per session arc"; `tools/pa_local.sh` pinned; health-score behavior at S1217-1222 "strongly_recommend_fresh" example |
| `docs/CLAUDE.md` | STUB | Canonical PA route (line 34); pa_chat.py tool invocation (line 8-9); PA_USE_FUNCTION_CALLING mentioned in troubleshooting |
| `docs/narratives/KNOWLEDGE_RAG_MEMORY.md` (S1158) | COMPLETE | ConversationMemory mentioned at line 100 as one of 5 memory stores; Cat F session state NOT in the 5-store framing |
| `tools/pa_local.sh` header comments | COMPLETE | **Only place pin rotation policy exists** — retirement record for S1098, S1165, S1267, S1300, S1301, S1302 pins; retire-vs-continue heuristic in prose |
| `docs/research/DOMAIN_RESEARCH_PLAYBOOK.md` | OUTLINE | Meta-process; no Cat F-specific content |
| `docs/research/platform_architecture_inventory.md` | (Cat F NOT in §3.N) | First-inventory landing target — see §19 R5 |
| `docs/research/ARCHITECTURE_INDEX.md` v14 | (S1303 slot reserved) | v15 bump expected at S1303 close |

**Auto-injected memory rules touching Cat F semantics** (per Agent 5):
`feedback_session_tool_retire_works.md`,
`feedback_pa_worker_function_calling_env.md`,
`feedback_pa_chat_local_override.md`,
`feedback_pa_local_verify_ownership.md`,
`feedback_claude_directs_rigby_then_verifies.md`,
`feedback_rigby_tool_verification.md`.

## 12. Research Coverage

**Verdict: LIGHT.**

Evidence for LIGHT (per playbook §12 matrix):

- **Systems named:** 5 subsystems in S1300 §3F (ConversationSession,
  PA pin, session_tool, tool-call reinjection, unified_pa_entrypoint
  enrichment).
- **Boundary calls:** S1302 §17.3 name-collision resolution;
  S1300 §3F known drift bullets.
- **Oblique references:** CLAUDE.md, PLATFORM_WHAT_IT_IS.md,
  KNOWLEDGE_RAG_MEMORY.md all mention conversation state but do
  not detail Cat F architecture.
- **No flow diagrams:** Zero step-by-step runtime flows for
  create_fresh, turn reinject, retirement lifecycle prior to this
  audit.
- **No model audit:** ConversationSession model (a name used in
  parent scoping) does not actually exist in code — the primary
  storage is `ChatConversation` (this audit clarifies the naming
  for the first time).
- **No authority framework:** Who may create / retire sessions,
  what workspace scoping means, etc. — undocumented.

Playbook §12 expectation MET: LIGHT confirmed for first-inventory audits.

---

## 13. Architecture Maturity

**Verdict (post-SIGN cycle 1 fold, E1):**

- **WORKING (bounded):** interactive web PA sessions with
  DB-backed turn reinjection are stable.
- **PARTIAL:** lifecycle hygiene (cleanup / events), analytics
  completeness, and hard policy enforcement (retired-thread
  gating is best-effort / fail-open under exceptions).

Applied per S1274 continuous-language rule for continuous
reality — the platform-wide sweep of "WORKING" without a bound
is what Rigby's SIGN cycle 1 flagged as too generous (she was
right; happy-path is stable but the edges are not).

Per Agent 6 + verifier reconciliation:

| Dimension | Status | Evidence |
|-----------|--------|----------|
| Turn persistence | **STABLE** | ChatConversation schema stable; 3 migrations (0095, 0236, 0341 per Agent 4); synchronous writes; index coverage adequate |
| Turn history retrieval | **WORKING** | 10-row conversation-scoped window at `unified_pa_entrypoint.py:7300-7302` verified; 8000-char truncation post-S1085 verified; fail-open on DB timeout |
| Retire lifecycle (`retire` + `set_active` + gate) | **STABLE** | Verified: handler `td_handlers_core.py:4011-4072` + gate `conversation_action_dispatcher.py:288-316`. S1248 fix intact. Tests pass per Agent 6. |
| Session pin identity mint | **PARTIAL** | Two mechanisms (`create_fresh` `pa-<hex>` vs `get_or_create_session` `uuid4()`) split by caller — see §17 overlap |
| Cross-surface continuity | **PARTIAL** | Web / Discord / API sources tracked; unlinked Discord users leave orphan rows with no linkage-completion signal (§14 F10) |
| Workspace scoping | **WEAK** | FK set at creation, nullable, no reactive re-scoping; multi-workspace session safety UNTESTED |
| Event emission | **MISSING** | Zero `CONVERSATION_*` streams on EventBus (§10, §14 F7) |
| Turn error alerting | **MISSING** | `response_time_ms` captured; no downstream alert consumer (Agent 4) |
| Retention / cleanup lifecycle | **MISSING** | No auto-cleanup task found (Agent 6) |
| Pin rotation cadence | **PARTIAL** | Manual; policy lives only in `pa_local.sh` header (§14 F8) |
| Turn context → RAG enrichment | **MISSING** | 0 RAG imports in `unified_pa_entrypoint.py` (§9 Cat F ↔ Cat D) |

Mixed verdict reflects the reality: active flows are STABLE; edges
are MISSING. Ship-quality for daily operator use; not ship-quality
for a resilient multi-year platform without follow-on work.

---

## 14. Known Drift

Per Agent 6 sweep + verifier corrections (see `verifier_loop:`
frontmatter for the two downgrades).

| ID | Title | Doc says | Runtime does | Evidence | Verdict | Severity |
|----|-------|----------|--------------|----------|---------|----------|
| **F1** | Stale-thread dispatcher waste | S1212 deliverable `777d9cd8`: ~$3.60/day burn; S1300 §3F named as known drift | S1248 shipped matched-pair fix: retire handler flips `session_active=False`; dispatcher gate blocks. Verified directly. | `td_handlers_core.py:4011-4072`, `conversation_action_dispatcher.py:288-316`, `tests/test_session_tool_retire_set_active_seed.py` | **CONFIRMED RECONCILED** | LOW |
| **F2** | `session_tool.retire` action existence | S1300 §3F: "does not exist; retire = stop using + repin." Memory rule `feedback_session_tool_retire_works.md`: verified working S1301 close | Handler at `td_handlers_core.py:4011-4072` returns `{retired: True}` on success. Direct read verified. Memory rule stands. | Direct read of retire handler | **CONFIRMED PRESENT** | LOW |
| **F3** | `ConversationMemory` import + wrong-model+wrong-field usage in `content_writer_agent.py` | S1302 §17.3: name-collision creates consumer-import ambiguity | `content_writer_agent.py:76` uses `from core.models_unified_system import ConversationMemory`. Import wrapped in try/except (line 74-80) that sets `MEMORY_AVAILABLE=False` + `ConversationMemory=None` on failure — SOFT FAIL at import time. **Post-SIGN cycle 1 finding (E2):** Rigby's grep surfaced a deeper issue at line 370 — the guarded branch filters `ConversationMemory.objects.filter(user=user, memory_type__in=['success','insight','learning']).order_by('-created_at')[:5]`. But the Cat B Django `ConversationMemory` at `models/conversations/models.py:19` has NO `memory_type` field (that field lives on `UserMemoryContext` at line 253). Consequence: fixing D1's import alone would move the crash class from import-time-soft-fail to query-time-`FieldError`. Full fix requires both. See §15 D1 (widened). | `content_writer_agent.py:70-80` + `content_writer_agent.py:370` direct reads | **CONFIRMED SOFT FAIL AT IMPORT + LATENT QUERY-TIME FieldError under guard** | MED |
| **F4** | Consumer surface unverified on ChatConversation.`context_used` + ChatConversation.`agent_results` | S1302 §14.3 F1 dead-code detection methodology — as an evidence-gathering approach, NOT as a dead-code assertion | Both fields are heavily written (verifier spot-check: 114 `context_used` occurrences across 57 py files; 101 `agent_results` occurrences across 22 files). **Post-SIGN cycle 1 rewrite (E4):** Rigby's independent grep confirmed the raw-keyword approach catches unrelated variables/methods — e.g., `tasks_agents.py:1262` `agent_results = phase_data.get('results', {})` is a local variable in a different scope, NOT a read of the model field. **No verified model-field consumer of `ChatConversation.context_used` or `ChatConversation.agent_results` has been surfaced yet. Evidence is incomplete.** This audit does not assert dead/unused; a candidate for follow-on research under §19 R1 (split into R1.a/R1.b/R1.c per E5) that must apply an owner-model-qualified consumer-inventory methodology, classify by consumer type (runtime vs analytics vs UI), and determine whether the canonical source-of-truth for turn-level tool/context payloads is these first-class fields or `ChatConversation.metadata`. | Agent 6 partial evidence + Rigby SIGN cycle 1 independent grep-verify | **CANDIDATE — NOT YET PROVEN EITHER WAY** — evidence incomplete; do not assert dead/unused. Verdict pending §19 R1.a/b/c. | UNKNOWN (depends on R1.a-c) |
| **F5** | Turn-history reinjection boolean-autofill filter | Memory rule `feedback_llm_autofills_boolean_params_with_false.md` | Turn-history reinject at `unified_pa_entrypoint.py:7292-7337` loads unconditionally — no boolean param filters in the path. Retire handler at `td_handlers_core.py:4033` correctly guards `force = bool(payload.get('force'))` (matches memory-rule PR4 pattern). | Direct read of reinject path + Agent 2 verification | **NO DRIFT** | LOW |
| **F6** | `PA_USE_FUNCTION_CALLING=true` dependency on turn-history persistence | Memory rule: without env, source=claude-code short-circuits to `claude_code_coordination` | Env gate at `unified_pa_entrypoint.py:684` (per Agent 2); turn-history load path is env-agnostic — verified by direct read at lines 7277-7343 (no env check in that function). Persistence survives env-off state. | Direct read + Agent 2 + Agent 6 | **NO DRIFT (RECONCILED)** | LOW |
| **F7** | No Cat F event stream on EventBus observed today | S1274: EventBus partial adoption; no doc claim about Cat F specifically | Zero `CONVERSATION_*` streams in `event_bus.py:21-31`. Zero consumers for turn events. **Post-SIGN cycle 1 reframe (E11):** describe as observed gap / partial adoption, NOT as defect that must exist. Cat F event streams may be intentional-not-yet-spec'd, not just missing. Delegated to Group 1700 Observability future arc for spec + adoption decision (§19 R2). | Agent 4 grep verified | **GAP / PARTIAL** — lifecycle analytics not yet implemented; owner spec required before "defect" classification | MED (compounds with F9 + F1 residual fail-open observability) |
| **F8** | Pin rotation policy lives only in `pa_local.sh` header comments | S1300 §3F does not name this as drift; parent scoping treated it as background context | Retire-vs-continue heuristics articulated only inline in `tools/pa_local.sh` retirement record. No formal doc; no automation; no audit trail beyond handoff prose. | Agent 5 evidence extraction | **CONFIRMED — governance drift** (policy-in-tooling anti-pattern) | LOW |
| **F9** | No auto-cleanup for retired rows | Not documented anywhere pre-audit | Zero Celery task, zero management command, zero TTL config for retired-thread deletion or archival. Rows accumulate indefinitely. | Agent 6 grep-verified null finding | **CONFIRMED MISSING** | LOW (storage cost; not blocking) |
| **F10** | Unlinked Discord user → linkage-completion signal | Not documented pre-audit | Discord users start sessions unlinked (`user_id=None`, `discord_user_id=<X>`). No signal fires when the user later links accounts; orphan rows persist. | Agent 4 grep | **CONFIRMED MISSING** | LOW (orphan-row hygiene; not blocking) |

**F4 discipline note (post-SIGN cycle 1 rewrite E4).** F4 is a
**CANDIDATE ONLY**. No verified model-field consumer of
`ChatConversation.context_used` or `ChatConversation.agent_results`
has been surfaced. Evidence is incomplete on both directions —
"heavy write surface" is confirmed but "no reads" is NOT. Rigby's
SIGN cycle 1 grep matched unrelated variables and methods (e.g.,
`tasks_agents.py:1262` `agent_results` is a local dict in a
different scope; `epa_handlers_utility.py:2910`
`aggregate_agent_results()` is a method aggregating over
`execution_ids`, not reading `ChatConversation.agent_results`).
Memory rule `feedback_verify_before_deleting_dead_code.md` +
Chris's S1242 directive — "Code that looks dead may be staged for
an unbuilt connection" — require: full owner-model-qualified
consumer inventory (§19 R1.a); runtime vs analytics vs UI
classification (§19 R1.b); canonical source-of-truth resolution
(§19 R1.c — first-class fields vs `metadata` dict). The audit
does NOT assert dead/unused for these fields. Future PR proposals
based on this audit MUST wait for R1.a-c to complete before
touching them.

---

## 15. Known Technical Debt

Per Agent 6 + verifier reconciliation:

| ID | Description | Evidence | Class | Severity | Fix Effort |
|----|-------------|----------|-------|----------|-----------|
| D1 | **ConversationMemory name collision + wrong model/field usage (import soft-fail + query-time FieldError risk)** — post-SIGN cycle 1 widen (E3) | `content_writer_agent.py:76` imports from wrong module (soft-fails via try/except); if fixed to `from core.models import ConversationMemory`, the guarded branch at line 370 then queries `ConversationMemory.objects.filter(user=user, memory_type__in=['success','insight','learning'])` — but the Cat B Django ConversationMemory has NO `memory_type` field (that field lives on `UserMemoryContext` at `models/conversations/models.py:253`). Fix requires **both**: canonical model choice (likely `UserMemoryContext`, not `ConversationMemory`) AND corresponding ORM field alignment. Import fix alone moves the crash from import-time to query-time. | wrong_import + wrong_model + wrong_field + silent_feature_degradation | MED | S-M (one PR that swaps model + realigns field query; needs a decision on which memory model was intended) |
| D2 | `_bound_conversation_id` payload sentinel not in PA tool schema | `pa_tool_schemas.py:4757-4795` documents `conversation_id` for `session_tool.retire` but does NOT document the internal `_bound_conversation_id` (injected by entrypoint at line 1771-1773). Hidden contract requires reader to open both schema + handler + entrypoint to understand. | missing_documentation / hidden_contract | MED | S |
| D3 | No idempotency test for double-retire on already-retired thread | Agent 6: `retire` handler at `td_handlers_core.py:4011-4072` correctly no-ops when `previously_active=False`, but no test covers this branch. | missing_test | LOW | S |
| D4 | No type annotations / schema for turn-history metadata keys | `unified_pa_entrypoint.py:7311-7336` reads `meta.get('source')`, `meta.get('tool_calls')`, `meta.get('response_id')` without schema enforcement. Silent miss on unexpected key shapes. | missing_type / drift_risk | LOW | M |
| D5 | Two session-identity mint paths coexist | `create_fresh` mints `pa-<hex[:16]>`; `get_or_create_session` mints `str(uuid.uuid4())`. Callers split by surface. No unified broker. | duplicate / boundary_violation | MED | M-L |
| D6 | `PaMessageFeedback.conversation_id_str` not FK'd | Design choice (S1085) — CharField, not FK. On CASCADE delete of ChatConversation, feedback rows will orphan. | missing_referential_integrity / by_design | LOW | S (design decision, not code) |

D1 could ship as an isolated PR; D2 could bundle with a wider PA tool
schema doc pass; D3 is a two-line pytest add; D4 requires deciding on
TypedDict vs pydantic vs "leave as JSONField and document" — deferred
to a separate design-preparation doc.

---

## 16. Boundary Violations

Per Agent 4 §6 + verifier reconciliation.

| ID | Boundary | Violation | Severity | Notes |
|----|----------|-----------|----------|-------|
| **OC1** | PA entrypoint → ChatConversation write authority | PA entrypoint writes `ChatConversation.objects.create()` directly (writer location UNKNOWN in sweep; likely in `views_personal_assistant.py` or a task-side hook). No service wrapper. No permission gate. No pre/post-save signal. | MED | Any downstream schema change breaks the writer directly; refactor difficulty scales with §5.1 god-service size (7613 lines). |
| **OC2** | `session_tool` state → `ChatConversation.session_active` BooleanField | S1248 retire logic hard-codes `session_active` flip. If session lifecycle evolves to multi-state (draft/active/retired/archived), the handler + gate + dispatcher gate must all change together. | MED | Design constraint captured but not blocking today. |
| **OC3** | Agent execution → `ChatConversation.agent_results` JSONField shape | Content deliberation + agent learning read `.agent_results`; shape not formally contracted. If AgentExecution model adds a field, who updates the ChatConversation serialization contract? | LOW-MED | Compounds with §15 D4 (no type annotations). |
| **OC4** | Session identity mint boundary | `create_fresh` and `get_or_create_session` mint different formats. Discord bot uses one; PA tool loop uses the other. Cross-surface reconciliation logic UNKNOWN. | MED | See §15 D5. |
| **OC5** | Retire without observability | `session_tool.retire` mutates state; no event emission. Downstream systems (workspace UI, HumanAttention inbox) have no signal. | MED | Compounds with §14 F7. |

**Load-bearing boundary verifier:** the `_bound_conversation_id`
sentinel at `unified_pa_entrypoint.py:1771-1773` is the ONLY defense
against LLM-supplied `conversation_id` overrides in `session_tool.
retire`. If entrypoint injection ever drops (regression, refactor,
new dispatcher path), the retire handler's self-retire guard breaks
silently. Not currently a violation — but the contract is fragile.
Filed as §18 ownership gap.

---

## 17. Duplicate or Overlapping Systems

Per Agent 1 + Agent 4:

- **Name collision: `ConversationMemory`** (S1302 §17.3 anchor).
  - Django model at `models/conversations/models.py:19` (Cat B, S1302-owned).
  - In-process facade at `conversation_memory.py:59` (Cat F).
  - Consumer imports split cleanly by pattern (§4.3 A-D). One WRONG
    import at `content_writer_agent.py:76` — see §14 F3.
- **Session identity mint paths:** two formats, two callers (§8
  Q#4, §15 D5, §16 OC4). Not strictly a duplicate MODEL, but a
  duplicate MECHANISM.
- **Cross-domain string ID storage:**
  - `ChatConversation.conversation_id` (CharField 255, source of truth).
  - `PaMessageFeedback.conversation_id_str` (CharField 255, no FK).
  - `ToolCallRecord.conversation_id` (UUIDField per Agent 1) — implicit reference.
  - `ExecutionRun.conversation_id` (CharField per Agent 1, `executor/models.py:271`) — implicit reference.
  - **No formal referential integrity across these.** By design
    (S1085 explicit design choice for feedback per Agent 1). §15 D6
    filed for the design-intent question.

**No other overlaps detected** per Agent 1's cross-reference against
`platform_architecture_inventory.md` §5. `DeliberationSession` and
`AgentConversation` are separate domains (deliberation persistence
and multi-agent collaboration logging respectively).

---

## 18. Ownership Gaps

Per Agent 6 + verifier:

| Stage | Owner | Clarity |
|-------|-------|---------|
| Pin creation | `session_tool.create_fresh` handler | **CLEAR** (`td_handlers_core.py:3881-3928`) |
| Pin creation (Discord path) | `ChatConversation.get_or_create_session()` | **CLEAR** but duplicates path 1 (§17) |
| Session `session_active=True` initial state | ChatConversation model default | **CLEAR** (`models/conversations/models.py:139-142`) |
| Session retire | `session_tool.retire` handler | **CLEAR** (`td_handlers_core.py:4011-4072`) |
| Retired-thread dispatch gate | `conversation_action_dispatcher.dispatch_actions()` | **CLEAR** (`conversation_action_dispatcher.py:288-316`) |
| Turn history reinject contract | `_load_conversation_history_from_db()` + gate | **CLEAR** (`unified_pa_entrypoint.py:7277-7343`) |
| Row-writer for post-turn ChatConversation.create() | UNKNOWN in sweep (likely `views_personal_assistant.py` or task hook) | **GAP** — see §16 OC1 |
| Cleanup / archival of retired rows | **NOBODY** | **GAP** — see §14 F9 + §19 R4 |
| Pin rotation cadence audit | **NOBODY** — lives in `tools/pa_local.sh` header comments | **GAP** — see §14 F8 |
| Orphan Discord row reconciliation on account linkage | **NOBODY** | **GAP** — see §14 F10 |
| `_bound_conversation_id` sentinel maintainer | UnifiedPAEntrypoint | **CLEAR** but fragile (§16 note) |
| Turn error / long-running turn alerts | **NOBODY** | **GAP** — Cat F ↔ HumanAttention MISSING (§9) |

Four confirmed ownership gaps.

---

## 19. Recommended Future Research

Ranked by playbook §11.2 rubric (architectural uncertainty × risk ×
unblocked flows):

1. **R1 — Owner-model-qualified F4 candidate verification (split into R1.a / R1.b / R1.c per SIGN cycle 1 E5).**
   Applies S1302 §14.3 methodology, but tightened to prevent the
   keyword-grep-catches-similarly-named-variables failure mode that
   Rigby SIGN cycle 1 caught. Three independent sub-questions must
   be answered in order:
   - **R1.a — Owner-model-qualified consumer inventory.** Enumerate
     every code path that reads OR writes
     `ChatConversation.context_used` and
     `ChatConversation.agent_results` **as model fields** — NOT dict
     keys inside `ChatConversation.metadata`, NOT logging strings,
     NOT schema comments, NOT similarly-named local variables in
     different scopes (e.g., `agent_results = phase_data.get(
     'results', {})` at `tasks_agents.py:1262`). Verify via
     owner-model-qualified grep (e.g., `\.context_used\b` where the
     preceding object is confirmed-typed as `ChatConversation`) and
     direct AST inspection where necessary. Route back through
     Rigby for grep-verify.
   - **R1.b — Runtime vs analytics vs UI classification.** For every
     consumer found under R1.a, classify: (i) runtime behaviour
     (LLM prompt building, dispatch, gate decisions), (ii)
     analytics / telemetry (dashboards, reporting jobs), (iii)
     admin / debug UI (Django admin, workspace pages). "Dead for
     runtime" ≠ "dead overall" — a field consumed only in a
     dashboard is still consumed.
   - **R1.c — Canonical source-of-truth resolution.** Determine
     whether the intended canonical store is the first-class
     JSONField (`ChatConversation.context_used`,
     `ChatConversation.agent_results`) or `ChatConversation.metadata`
     dict-keys. If canonical is `metadata`, the first-class fields
     are legacy / compat and this audit files a design-preparation
     doc proposing either (a) drop the fields with migration +
     consumer sweep or (b) formally document them as legacy with a
     deprecation timeline. If canonical is the first-class fields,
     document why `metadata` keys shadow them.

   **Do R1.a first.** It determines whether ANY dead-code claim is
   permissible; without it, F4 stays CANDIDATE indefinitely. R1.b
   and R1.c depend on R1.a's output.

   **Highest priority** because it materially changes the F4
   verdict AND validates S1302's dead-code methodology on a new
   domain with the required owner-model qualification.
2. **R2 — Cat F ↔ EventBus adoption design preparation.** Delegate
   to Group 1700 Observability (future arc). Deliverables: define
   candidate streams (`CONVERSATION_CREATED`, `CONVERSATION_RETIRED`,
   `TURN_PROCESSED`, `TURN_FAILED`), consumers (observability sink,
   HumanAttention error escalation), and reconciliation with S1274
   §12.1 EventBus adoption arc. **Blocks:** F7, F10 (linkage-
   completion signal would ride the event bus), and part of F9
   (cleanup consumer could subscribe to `CONVERSATION_RETIRED`).
3. **R3 — Turn-context → RAG query enrichment design preparation.**
   Delegate to S1304 (Cat E ↔ D boundary) OR spin a Cat F ↔ Cat D
   design-preparation arc under S1399. Deliverable: schema for how
   recent turn context (last N user messages) should enrich
   `kb_tool semantic_search` calls without over-fetching. Ties to
   S1301 §14.5 provenance drift work.
4. **R4 — Retention lifecycle for retired rows.** Deliverable:
   design-preparation doc naming the target retention (e.g., 90-day
   TTL vs indefinite with pgvector-embedded search fallback),
   cleanup Celery task specification, migration plan. **Blocks:** F9.
5. **R5 — Land the first inventory row for Category F in
   `platform_architecture_inventory.md`.** This audit produces the
   evidence base; the row itself lands via S1399 canonical summary
   (per parent §5). Deliverable: proposed `§3.N` row content
   (systems, anchor, coverage, maturity, drift).
6. **R6 — Formalize session identity mint contract.** Reconcile
   `create_fresh` and `get_or_create_session` (§17 duplicate
   mechanism). Design-preparation doc: unified session broker vs
   dual paths preserved with documentation. Ties to Discord unlinked-
   user reconciliation (§14 F10).
7. **R7 — Doc-in-tooling reconciliation for pin rotation policy
   (F8).** Move the policy from `pa_local.sh` header comments to a
   canonical doc (or ADR). Deliverable: formal retire-vs-continue
   heuristic doc; audit trail for arc-pin rotation decisions.
8. **R8 — Fix D1 broken import in `content_writer_agent.py:76`.**
   Runtime PR — not research. Filed for §19 completeness. Move to
   an issue.

---

## 20. Appendix

### 20.1 Files inspected (from 6 sub-agents + verifier spot-checks)

Direct-read verification files (spot-check subset):
- `core/services/unified_pa_entrypoint.py` (7613 lines total; read
  lines 7275-7343 directly)
- `core/services/td_handlers_core.py` (4168 lines total; read lines
  3864-4108 directly)
- `core/services/conversation_action_dispatcher.py` (716 lines total;
  read lines 280-323 directly)
- `core/models/conversations/models.py` (373 lines total; read lines
  55-222 directly)
- `core/conversation_memory.py` (211 lines total; read via Agent 1
  full inventory)
- `core/agents/content_writer_agent.py` (read lines 70-99 directly
  for F3 verifier)

Sub-agent-inspected surfaces (paths cited without independent verify;
trust per playbook §14 "trust but verify" applies only to load-bearing
claims):
- `core/services/pa_tool_schemas.py` (2134-2221, 4719-4834)
- `core/services/tool_dispatcher.py` (1267 lines; handlers registered
  at 339, 449, 452, 563)
- `core/services/td_handlers_agents.py:5126`
- `core/consumers_pa_conversation.py:175`
- `core/urls*.py` (REST routing per Agent 3)
- `core/tasks.py:3250, 3752, 4726, 4760, 4794, 11912, 12042, 12317, 13072`
- `core/tasks_agents.py`
- `core/management/commands/session_provenance.py:71`
- `core/management/commands/cleanup_conversation_duplicates.py:29`
- `core/management/commands/pa_acks_health.py`
- `core/event_bus.py:21-31`
- `core/services/scoring_dispatcher.py:282, 480`
- `frontend/src/stores/paStore.ts` (Agent 3 skim)
- `frontend/src/App.tsx:112`
- `tools/pa_local.sh` (header + line 115)
- `tools/pa_chat.py`

### 20.2 Docs inspected (from Agent 5)

Per §11 table.

### 20.3 Grep patterns used (load-bearing)

- Sweep 6 F3 sweep: `import ConversationMemory` across all `.py` —
  distinguished patterns A/B/C/D (§4.3).
- Sweep 6 F4 sweep: `context_used` (114 total matches; 57 files);
  `agent_results` (101 total matches; 22 files). **Verifier note:**
  keyword-level grep does NOT distinguish `ChatConversation.context_
  used` from `ExecutionRow.scifi_context_used=bool(...)`. F4 requires
  field-owner-qualified grep — filed as §19 R1.
- Sweep 4 event-bus grep:
  `ChatConversation` in `signal_aggregation_service.py`,
  `scoring_dispatcher.py`, `platform_event_view.py` → 0 hits (per
  Agent 4).
- Sweep 4 RAG grep: RAG imports in `unified_pa_entrypoint.py` → 0
  hits.
- Sweep 6 null-finding greps: `ChatConversation.*\.delete()` → 0
  active-row deletion; `session_active.*cleanup\|housekeeping` → 0
  cleanup task; `context_used.*filter()\|\.get(context_used` → 0
  reads via those patterns (see F4 discipline note).

### 20.4 Unresolved unknowns

- **Row-writer location for post-turn `ChatConversation.create()`.**
  Sweep did not surface the exact call site. Likely in
  `views_personal_assistant.py` or a task-side hook. Fills
  §16 OC1 verifier + §18 gap.
- **`session_health_service` scoring algorithm.** Health-check
  handler at `td_handlers_core.py:3868-3879` delegates but audit
  did not read the service. Boundary to a downstream audit if
  health-score becomes load-bearing for automation.
- **F4 phantom-field consumer surface** (§14 F4; §19 R1) — deferred.
- **`pa_chat_status` endpoint handler location** (§6.1) — Agent 3
  found REST route reference; handler definition offset beyond
  read limit.
- **`AgentFollowupSubscription` fire timing details** (Agent 3
  inferred).
- **VIP mode scoping enforcement completeness** (Agent 3 mentioned
  S1132 vip_scope gate; enforcement rules 9-strong per code
  comment; not audited here).
- **Fleet signature algorithm and key rotation policy** (S1129 —
  Agent 3 mention; not audited here).
- **Retire → workspace UI subscription propagation** (Agent 2
  UNKNOWN — retire flips the flag but downstream WebSocket
  subscribers may not react).
- **Retire → Celery beat task blocking** (Agent 2 UNKNOWN — beat
  tasks likely bypass the gate; verify per-task).
- **Multi-tenant conversation isolation across all code paths**
  (Agent 2 UNKNOWN — spot checks pass but not exhaustive).
- **`get_or_create_session` 24-hour reactivation semantics** —
  what happens if two consumers concurrently try to reactivate
  the same row? No lock.

### 20.5 Conflicts between sources

- **Agent 6 F3 severity vs verifier.** Agent 6 claimed
  `content_writer_agent.py:76` "would fail at import time." Direct
  read of lines 70-80 shows try/except ImportError. Downgraded
  from CRITICAL to MED (see §14 F3 + `verifier_loop:` frontmatter).
- **Agent 6 F4 verdict vs memory rule.** Agent 6 declared
  `context_used` + `agent_results` "phantom fields, dead-code."
  Memory rule `feedback_verify_before_deleting_dead_code.md`
  forbids dead verdicts without whole-tree consumer verification.
  Downgraded to CANDIDATE + filed §19 R1 (see §14 F4 +
  `verifier_loop:` frontmatter).
- **S1300 §3F "session_tool.retire does not exist" vs S1301 close
  memory rule.** Memory rule wins (verified working; S1303 direct
  read confirms). §14 F2 CONFIRMED PRESENT.

### 20.6 Verifier-loop corrections

Two corrections during synthesis (captured in `verifier_loop:`
frontmatter):

1. **F3 severity downgrade** — try/except guard changes the failure
   class from runtime-crash to soft-fail.
2. **F4 verdict downgrade** — CANDIDATE not CONFIRMED, per memory-
   rule discipline against premature dead-code verdicts.

Both corrections improve audit accuracy without changing the sweep's
overall shape.

### 20.7 Rigby SIGN fold notes

_To fill after SIGN cycles — one subsection per cycle (§20.7.1,
§20.7.2, …). Verdict + edits + final `sign_status` frontmatter
value._

### 20.8 Chris ratification thread

- 2026-07-01 (S1303 open, turn 1): D10 PROCEED + D11 RETAIN (arc
  pin `pa-aa54193f240f4846`), "agree all" on Rigby's default leans.
- 2026-07-01 (S1303 mid-session): "send it to rigby for sign" →
  routed audit v0.2 to fresh SIGN pin `pa-23a38300dd84bae2` (E1-E12
  fold list returned; cycle 2 verification passed → SIGN-clean).
- _Chris commit-gate pending — v0.4 SIGN-clean; ready for merge on
  explicit "commit it" instruction._

### 20.9 Reinjection Metadata Contract (new subsection — post-SIGN cycle 1 E10)

`ChatConversation.metadata` (JSONField, default=dict, at
`core/models/conversations/models.py:158`) is the load-bearing
carrier for turn-history reinjection. It is a first-class Cat F
consumer surface — distinguishing this from the F4-CANDIDATE
first-class fields (`context_used`, `agent_results`) is important
because the metadata dict is VERIFIED consumed by the reinjection
path.

**Expected keys on read (verified consumers at
`unified_pa_entrypoint.py:7311-7336`):**

| Key | Type | Producer surface | Consumer effect | Cite |
|-----|------|------------------|-----------------|------|
| `source` | string | writer at turn-persist time; values from `SOURCE_CHOICES` at `models/conversations/models.py:81-88` (`web`/`mobile`/`discord`/`api`/`claude-code`/`pa`) | If not `web`/`web-dock`, user turn is prefixed `[<source>] <content>` for speaker attribution (avoids OpenAI `name` field) | `unified_pa_entrypoint.py:7312-7317` |
| `tool_calls` | list[dict] | writer at post-turn tool-call-record step (writer UNKNOWN in sweep — see §20.4) | Reinjected into assistant turn dict at key `tool_calls`; passed to LLM for function-calling continuity | `unified_pa_entrypoint.py:7331-7333` |
| `tool_results` | list[dict] | writer paired with `tool_calls` (UNKNOWN — same location as `tool_calls` writer) | Reinjected into assistant turn dict at key `tool_results`; paired with `tool_calls` for LLM's memory of prior tool outputs | `unified_pa_entrypoint.py:7334` |
| `response_id` | string | writer at OpenAI response persist time | Reinjected into assistant turn dict at key `response_id`; used for function-calling response chaining | `unified_pa_entrypoint.py:7335-7336` |

**Expected keys on write (partial — this list is NOT complete; the
audit did not surface every write site):**

- All 4 read keys above.
- Session identity fields (`source`) mandatory for correct speaker
  attribution.
- Any additional writer-side keys are effectively silent —
  reinjection reads via `meta.get('<key>')` at lines 7311-7336, so
  unexpected keys are ignored gracefully.

**Discipline (post-F4 lesson).** A key living in
`ChatConversation.metadata` is NOT the same thing as a first-class
model field. When auditing consumer surface (F4 methodology), the
grep pattern MUST distinguish `chat.metadata.get('foo')` from
`chat.foo` — the former reads a dict key, the latter reads a model
field. R1.a explicitly separates them.

**Gaps for §19 backlog:**
- Producer catalogue (writer sites) incomplete — see §20.4 unknown
  list ("Row-writer location for post-turn `ChatConversation.
  create()`").
- No formal schema (TypedDict / pydantic model / JSONSchema); D4
  in §15 files the type-annotation debt.
- Silent-drop-on-unexpected-key behaviour means a future producer
  can drop a key with no consumer alert.

### 20.10 Draft → Active gating checklist (new subsection — post-SIGN cycle 1 E12)

Playbook §16 requires explicit gates for a research-status flip.
Post-SIGN cycle 1, this audit's flip to `status: active` requires:

- [x] F4 language fixed — no "dead / unused / 0 reads" claims
      (E4 folded).
- [x] D1 widened — wrong model + wrong field, not just wrong import
      (E3 folded).
- [x] Cat F ↔ Cat D reframe — observed gap + owner-confirmation-
      required (E6 folded).
- [x] Metadata contract subsection present — §20.9 (E9 + E10
      folded).
- [x] Maturity verdict bounded — WORKING(bounded) + PARTIAL split
      (E1 folded).
- [x] F3 nuance added — soft-fail-at-import + latent-FieldError-at-
      query (E2 folded).
- [x] F7 reframed as gap / partial, not defect (E11 folded).
- [x] Retire nuance added to §5.2 — force required, idempotency,
      updated_count (E8 folded).
- [x] Flow E fail-open nuance added to §7 (E7 folded).
- [x] R1 split into R1.a/b/c (E5 folded).
- [x] Rigby SIGN cycle 2 verification pass — 2026-07-01, `pa-23a38300dd84bae2`.
      Independent verification of E3 (D1 widen) via direct read of
      `content_writer_agent.py:330-450` + `models/conversations/models.py:1-31`;
      E4 (F4 CANDIDATE) held; E5 (R1.a/b/c) coherent. Bonus checks on §13
      passed. **Outcome: SIGN-clean.**
- [ ] Chris commit-gate per playbook §16 — explicit "commit it"
      instruction before merge to `main`.

Only after both remaining boxes tick does `status: draft` become
`status: active` and `sign_status:` become `SIGN-clean`.

---

## Appendix — Frontmatter Provenance

- **Parent-scoping arc:** Group 1300 (Memory / Knowledge / Embeddings),
  parent doc `docs/research/domains/memory/1300_memory_domain_scoping.md`
  (S1300, Chris-locked 2026-07-01).
- **Prior siblings merged to `main`:**
  - S1301 (P1, Cat D — RAG Retrieval Lanes), PRs #2775 + #2776.
  - S1302 (P2, Cat A+B+C — Memory Persistence Architecture), PR #2777
    (`c053272a`), SIGN-clean after 3 fold cycles.
- **This session (S1303):** P3 (Cat F — Conversational / Thread Memory),
  first-inventory landing. Branch
  `docs/session-1303-memory-conversational-thread-memory` off `main`.
- **Playbook version:** DOMAIN_RESEARCH_PLAYBOOK v2 (S1276-added
  formalization).
- **Research OS:** `docs/research/process/RESEARCH_OPERATING_SYSTEM.md`
  §0–§9 (bootstrap + child-audit contract).
- **ARCHITECTURE_INDEX:** v14 at S1303 open; expected v15 bump at
  S1303 close (adds §1.18 row + §8 timeline row).
- **OPEN_ARCS:** Group 1300 row P3 slot flip at S1303 close.
- **First-inventory discipline:** Category F produces `PLATFORM_INVENTORY.md`
  §3.N candidate row (proposal only — landed by S1399 canonical
  summary per parent §5).
