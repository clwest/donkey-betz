---
title: "Symbol Mapping Architecture — Architectural Discovery (research only)"
status: draft
session: 1270
date: 2026-06-30
mission_type: architectural_discovery
authority: |
  Evidence-only research. No runtime changes. No PRs. No migrations.
  No model definitions. No proposed implementation. No contract
  changes. No API design. This doc inventories the vocabulary gap
  between JobContract.authority policy strings and runtime action
  surfaces, catalogs existing symbol systems that could be reused,
  enumerates candidate enforcement boundaries, and identifies the
  historical failures a symbol-mapping primitive would prevent. Any
  mapping "option" listed in §5 is a research description of a
  design space, NOT a design decision.
companion_docs:
  - docs/research/employee_os_communication_substrate_audit.md
  - docs/research/employee_os_communication_protocol_sketch.md
  - docs/research/employee_os_collaboration_patterns.md
  - docs/research/governance_authority_evolution.md
  - docs/research/ARCHITECTURE_INDEX.md
  - docs/EMPLOYEE_OS_PRIMITIVES.md
  - docs/handoffs/SESSION_1264_AUTHORITY_WARN_MODE.md
  - docs/handoffs/SESSION_1269_ARCHITECTURAL_RESEARCH_LIBRARY_ARC.md
verifier_loop: |
  Five parallel Explore sub-agents produced evidence reports
  (authority-string enumeration, runtime action-surface inventory,
  existing symbol-system inventory, enforcement-boundary inventory,
  historical-failure inventory). All load-bearing structural claims
  spot-verified by Claude via direct Grep/Read against source
  before the doc was written. Two minor sub-agent drifts corrected:
  (a) REMOVED_TOOL_ALIASES = 13 entries, not 12; (b) GATEWAY_TOOLS
  = 22 entries, not 23. Two count-anchor conflicts resolved
  in favor of PLATFORM_INVENTORY per DOC_LIFECYCLE §2c:
  (a) PA tool schemas = 113 (runtime anchor), not 71 (sub-agent 2)
  or 119 (raw name-token grep); (b) management commands = 193
  (runtime anchor), not 275 (sub-agent 2). Independent SIGN review
  by Rigby complete (S1270 PA conversation pa-cbcc410b32714f60):
  **SIGN-with-edits**. Two must-fix edits folded (§8 narrowed
  `_AuthorityContractMalformedError` scope to contract-shape only;
  §2.6 added parallel-vocabulary type/shape anchor with
  mission_runner.py:849-861 cite). Three strongly-recommended
  optional edits folded (I-S4 softened "rather than" wording; I-S3
  now dual-cites F1+F3 from governance_authority_evolution.md;
  §5.5 Option E added "reversibility ≠ preference" disclaimer).
  One Q3-flagged omission folded (§4.1 gained row 24 for
  AssistantProfile.get_allowed_tools as identifier registry, not
  just enforcement precedent). One Q1 clarification folded (§2.4
  now notes normalization alone doesn't close the enforcement gap).
  Seven Q4 architectural blind spots folded as new finding F11 in
  §9 (namespace/collision, symbol lifecycle governance,
  bidirectionality/invertibility, granularity mismatch, policy rail
  proliferation, WORKSPACE_AWARE_AGENTS as identity rail,
  auditability/evidence semantics). Rigby SIGN-clean on the load-
  bearing YES incidents (I-S1 through I-S5) after direct source
  verification: I-S2 (mission_runner.py:821-900), I-S4
  (bug_triage.py:1154-1180 + mission_runner.py:1127-1145), I-S5
  (bug_triage.py:396-453), I-S3 (governance_authority_evolution.md
  F1+F3), I-S1 (governance_authority_evolution.md §6.1 I-G1 within
  repo-evidence limits — PR #2756 content not filesystem-verifiable).
  Rigby SIGN-clean on Q6 (Symbol Mapping is truly the P0 foundational
  blocker for contract-layer enforcement + coherent authority
  telemetry) and Q7 (no preceding research needed; Evidence-only
  telemetry hardening and Cross-plane composition are adjacent-not-
  blocking).
owner: claude (drafted S1270) + rigby (independent SIGN review, S1270)
---

# Symbol Mapping Architecture — Architectural Discovery

> **What this is.** The canonical research anchor for the
> foundational architectural question every future authority
> enforcement discussion must answer: what bridge exists (or must
> be built) between the policy-description strings in
> `JobContract.authority` and the runtime symbols (tool names,
> step names, task names, function calls, model writes) that
> actually execute the work? Built from direct file:line evidence
> + five parallel sub-agent sweeps + spot verification.
>
> **What this is not.** A design. A decision. A PR sketch. A
> recommendation to pick one mapping option over another. A
> proposal to add classes, models, registries, or admin UIs. The
> options in §5 are a *design space*, not a design. The findings
> in §9 are *architectural observations*, not resolutions. Chris
> gates every downstream design decision.

---

## 1. Executive Summary

The platform has **57 unique authority strings** (68 total entries
across 4 employees) declared as `dict[str, str]` keys in each
employee's `JobContract.authority` (`core/employees/jobs.py:238-250`
Rigby, `489-505` Auditor, `782-812` Chief of Staff, `1098-1116`
Bug Triage). Every string carries a policy meaning
(`"modify_docs_files" → PROHIBITED`) but **zero strings bind to
any runtime symbol** — no tool carries an `action_class`
attribute, no step declares its invoked actions, no ORM handler
resolves an incoming call against the contract dict. The runner
itself comments this out loud at
`core/employees/mission_runner.py:895-899`:

> "Observation of contract shape only; not violation detection.
> Enforce-mode requires future symbol mapping (S1264 discovery)."

### The architectural gap in one sentence

**Between MissionRunner's dispatch of a step and the step's
actual runtime behavior, there is no vocabulary that both sides
can agree on: the contract speaks `"modify_docs_files"`, the
runtime speaks `Document.objects.create()` — and nothing bridges
the two.**

### The four planes of the gap

1. **Vocabulary gap.** 57 unique policy strings in the contract;
   ≥7 distinct runtime identifier systems (tool names, step
   names, task names, model classes, agent names, OpsRunEvent
   labels, mission_run_kinds); zero cross-references between
   them.
2. **Runtime-attribute gap.** Zero surfaces in the runtime carry
   authority metadata today. Every one of the 12 action surfaces
   enumerated in §3 has stable identifiers, but none of them
   declares which `action_class` they satisfy.
3. **Enforcement gap.** 20 architecturally-possible interception
   layers exist (§6); zero of them read `JobContract.authority`
   before allowing an action to proceed. All 35 existing runtime
   gates (per `governance_authority_evolution.md` §4) operate at
   HTTP / middleware / tool-handler boundaries, not at the
   contract-symbol boundary.
4. **Observation-vs-enforcement gap.** S1264 warn-mode observes
   the contract *shape* (counts, hash, level breakdown) but
   cannot observe or block a *violation* because the runtime
   never emits action_class evidence.

### Major findings

**F1 — The vocabulary imbalance is asymmetric.** 57 authority
strings vs. 3 fully identified action-surface families (PA tools:
113 schemas, steps: 17 across 4 employees, Celery tasks: ~414
functions). Even after deduping and grouping by intent, the
authority strings outnumber the largest single stable action
family. Any registry design must bridge many-to-many, not 1:1.

**F2 — Cross-employee vocabulary convergence is partial.** Of 57
unique strings: 1 appears in all 4 employees (`open_pull_request`,
uniformly `PROHIBITED`); 2 appear in 3 (`certify_mission_run`,
`recommend_remediations`); 4 appear in 2; **50 strings (88%)
appear in exactly one employee** (per sub-agent 1 enumeration).
Convergence exists but is thin.

**F3 — Every candidate mapping option requires new metadata
somewhere.** The three known options from S1264 discovery
(steps self-declare, tool registry, hybrid) plus two additional
options surfaced in this research (§5) all require *either* a
new attribute on an existing primitive *or* a new registry
mapping strings to callables. None of them can be built from
pure reuse of existing symbol systems without adding a schema
layer.

**F4 — Existing symbol systems that are authority-adjacent are
tiny.** `AuthorityLevel` enum has 4 members; `REMOVED_TOOL_ALIASES`
has 13 entries; `AUTHORITY_CONTRACT_OBSERVED_LABEL` +
`AUTHORITY_CONTRACT_SCHEMA_VERSION` are single constants. The
raw material for a symbol registry exists in prototype scale but
would need a formal registry primitive to become load-bearing.

**F5 — The enforcement boundary problem is orthogonal to the
symbol problem.** Even a perfect action_class → runtime-symbol
map would not, by itself, block any action. It would only make
blocking *possible* — the enforcement layer (per-tool gate,
per-step gate, per-model-write signal, dispatcher gate) is a
separate design that can only be scoped once the symbol layer
is decided.

**F6 — Existing precedents show enforcement can be added at
multiple layers.** `AssistantProfile.get_allowed_tools()`
gates tool access at ToolDispatcher entry
(`tool_dispatcher.py:687-720` per sub-agent 4);
`LLMEnforcer.check_budget()` gates LLM calls
(`llm_enforcer.py:200-260`); `messaging_tool.send_message`
feature-flag guard (`td_handlers_core.py:3693-3711`) gates a
specific tool action. Each is a working precedent for a
runtime enforcement layer, but each uses a *different* identifier
vocabulary (user profile, budget flag, feature flag) — none
uses the JobContract authority dict.

**F7 — The historical case for Symbol Mapping is strong, not
absolute.** Of 23 historical incidents catalogued (§7): 5 (22%)
would be directly prevented by symbol mapping, 10 (43%) would
be partially prevented / significantly reduced, 8 (35%) are
orthogonal (LLM SDK, infrastructure, error handling). The 5
YES cases include the S1264 warn-mode discovery itself, the
Bug Triage v0 opt-out from `certify_mission_run`, and the
architectural absence of any contract-level gate.

**F8 — Cross-plane composition is undesigned.** If symbol
mapping lands and enforcement is layered on top, the
composition with the four governance planes (per
`governance_authority_evolution.md` F1: autonomy / authority
/ budget / human governance) is not scoped anywhere.
`KillSwitch.is_active` (autonomy plane) and
`JobContract.authority` (authority plane) could both block a
dispatch — but nothing declares the order or precedence.
That is a follow-on design question, not scope of this doc.

### Overall observation

**Symbol mapping is a foundational primitive, not a feature.**
Every downstream authority research mission (Trust Propagation,
Memory Architecture, Cross-Employee Delegation) requires this
layer to exist before it can be scoped meaningfully. The design
space is small (§5 enumerates 5 options), but the tradeoffs are
significant enough that a research doc — not a sprint plan — is
the right vehicle for choosing.

**The next research mission after this one is not "implement
symbol mapping." It is "choose an option from §5 with Chris
gating."** Choice = design decision; scoping = research.
This doc is scoping.

---

## 2. Current Authority Vocabulary

The 57-unique-string vocabulary that `JobContract.authority`
declares today. Enumerated by direct read of
`core/employees/jobs.py`; totals verified against the
`governance_authority_evolution.md` §2.2 row 11 claim of "68
authority entries."

### 2.1 Counts

| Metric | Value | Source |
|---|---|---|
| Authority entries across all 4 employees | **68** | jobs.py:238-250 (Rigby=11) + jobs.py:489-505 (Auditor=15) + jobs.py:782-812 (Chief=25) + jobs.py:1098-1116 (Triage=17) |
| Unique deduplicated action_class strings | **57** | Sub-agent 1 enumeration |
| Prohibited_actions tuple entries (all employees) | **30** | 4 (Rigby) + 7 (Auditor) + 10 (Chief) + 9 (Triage) |
| Distinct AuthorityLevel values | **4** | jobs.py:41-52 (OBSERVE / RECOMMEND / EXECUTE / PROHIBITED) |
| Strings with runtime binding evidence | **0** | Sub-agent 1: every string is "STRING-ONLY-IN-JOBS-PY" (no grep hits elsewhere as runtime symbol) |

### 2.2 Grouping by employee-sharing pattern

Per sub-agent 1 sharing analysis:

| Sharing pattern | Count | Strings |
|---|---|---|
| **4-of-4 (universal)** | 1 | `open_pull_request` (PROHIBITED across all 4) |
| **3-of-4** | 2 | `certify_mission_run` (EXECUTE in Rigby/Auditor/Chief; opt-out in Triage per `auto_emit_verdict=False`); `recommend_remediations` (RECOMMEND in Auditor/Chief/Triage; absent in Rigby by design) |
| **2-of-4** | 4 | `delete_database_rows`, `execute_arbitrary_code`, `modify_any_file`, `modify_settings` (all PROHIBITED, Auditor + Triage) |
| **1-of-4 (unique)** | 50 | 88% of unique strings — employee-scoped policy |

### 2.3 Grouping by AuthorityLevel

Per sub-agent 1 level enumeration:

| Level | Count of (employee, string) pairs | Notes |
|---|---|---|
| **OBSERVE** | 13 | Read-only surfaces: `read_*`, `check_*`, `count_*`, `run_drift_observation` |
| **RECOMMEND** | 6 | Escalation surfaces: `recommend_remediations` (×3), `broken_link_sweep`, `narrative_refresh_suggestion`, `recommend_daily_priorities` |
| **EXECUTE** | 17 | Direct-action authority: `certify_mission_run` (×3), `save_*_to_deliverable` (×3), `synthesize_*` (×2), etc. |
| **PROHIBITED** | 32 | Explicit denials: `open_pull_request` (×4), plus scope-specific PROHIBITED (delete/modify/execute) |
| **Total** | 68 | Matches governance_authority_evolution.md §2.2 |

### 2.4 Naming inconsistencies

Per sub-agent 1 pattern analysis:

**Consistency #1 — Case:** All 57 unique strings use `snake_case`
exclusively. Zero dashes, zero camelCase.

**Inconsistency #1 — Modify vocabulary:** Rigby uses
`modify_docs_files` (docs/-scoped); Auditor + Triage use
`modify_any_file` (generic); Chief uses `modify_source_documents`
+ `modify_platform_settings` (granular). Same conceptual action,
four different strings. Any future registry needs a merge policy
or the drift persists.

**Inconsistency #2 — Delete vocabulary:** Rigby uses
`delete_document_rows` + `delete_document_embedding_rows`
(model-specific, docs cascade scope); Auditor + Triage use
`delete_database_rows` (generic). Model-specific granularity vs.
generic policy — both valid, both inconsistent.

**Inconsistency #3 — Read/Check/Count verb split:** Auditor mixes
`read_platform_docs`, `check_env_config_status`,
`count_database_models`; Chief + Triage standardize on `read_*`.
Verb choice reflects operation semantics, not just naming style.

**Inconsistency #4 — Recommend naming split:** Rigby uses
job-specific names (`broken_link_sweep`,
`narrative_refresh_suggestion`); Auditor + Chief + Triage use
generic `recommend_remediations`. Suggests Rigby's escalation
scope was designed before the shared `recommend_remediations`
convention emerged.

**Verb-object vs. object-verb:** Most strings are verb_object
(`build_docs_index`, `create_escalation_deliverable`), but
`certify_mission_run` is object_verb, and `broken_link_sweep`
is adjective_noun. No enforced convention.

**Caveat (per Rigby S1270 SIGN Q1 note): normalization alone
cannot close the enforcement gap.** Even a perfect
canonicalization of the 57 strings would leave the deeper
problem unaddressed — no runtime surface today emits
action_class metadata (per F2 in §9). Normalizing
`modify_docs_files` and `modify_any_file` to a common string
does not automatically tell the runtime which tool call
satisfied that string. Symbol mapping is the mechanism that
bridges normalized strings to runtime symbols; normalization
without symbol binding leaves the same gap.

### 2.5 Coverage gaps (declared vs. inferable)

**Missing across employees where behavior clearly happens:**

- Bug Triage does NOT declare `certify_mission_run`. This is
  intentional (uses `auto_emit_verdict=False`,
  `mission_runner.py:1127-1145`); Rigby/human issues verdict via
  `mission_verdict` PA tool later. The absence is a design
  decision, not an oversight. Symbol mapping would need to
  express "authority is contextually optional" here.
- Rigby does NOT declare `recommend_remediations`. Also
  intentional — Rigby's job is docs cascade operational health,
  not platform-wide remediation; escalations go directly to
  human via `create_escalation_deliverable` (EXECUTE) +
  `post_escalation_to_pa_chat` (EXECUTE).
- No employee declares an explicit `write_deliverable` /
  `create_deliverable` authority — every employee has some
  `save_*_to_deliverable` variant (`save_audit_to_deliverable`,
  `save_brief_to_deliverable`, `save_triage_to_deliverable`) or
  `create_escalation_deliverable`. The generic write authority
  is absent; only the job-specific variants exist.

**Present as recommend_* but no corresponding execute_*:**
`recommend_remediations` implies a downstream `execute_remediation`
which no employee declares (correctly — humans execute
remediations per each employee's `what_chris_approves` tuple).
The absence is authority-consistent but symbol-mapping-relevant:
a registry would need to know that `recommend_*` is a terminal
authority for the AI employee, not a delegate to an
`execute_*` action.

### 2.6 The `prohibited_actions` tuple — parallel vocabulary

Per jobs.py:252-257 (Rigby), 507-517 (Auditor), 814-830 (Chief),
1122-1131 (Triage): every employee declares a
`prohibited_actions: tuple[str, ...]` of human-readable denial
strings *separate from* the PROHIBITED-level entries in the
authority dict. Sub-agent 1 confirmed the two vocabularies are
complementary, not duplicate:

- Dict PROHIBITED entries: machine-oriented strings
  (`"open_pull_request"`)
- Tuple entries: human-readable prose (`"Open or merge pull
  requests."`)

**Type/shape anchor (per Rigby S1270 SIGN edit #2).** The two
rails are shape-validated distinctly by MissionRunner at load
time. `mission_runner.py:849-861` enforces:

```
authority = getattr(contract, "authority", None)
if not isinstance(authority, dict):
    raise _AuthorityContractMalformedError(...)
prohibited = getattr(contract, "prohibited_actions", None)
if not isinstance(prohibited, (tuple, list)):
    raise _AuthorityContractMalformedError(...)
```

Two distinct `isinstance` checks (dict vs. tuple/list) confirm
the rails are intentionally different data types, not two
renderings of the same source. **Neither the runtime nor the
contract file today asserts any convergence between them.** Any
symbol-mapping design that treats prohibited_actions as
auto-derivable from the dict is inventing a contract that does
not exist in code.

**Symbol-mapping implication:** A registry design has to decide
whether prohibited_actions is a *rendering* of the PROHIBITED
dict subset (auto-derivable) or a *first-class* second vocabulary
(hand-maintained alongside the dict). Today it is hand-maintained
in parallel with the dict, at cost of drift risk.

### 2.7 The boundary tuples — third parallel vocabulary

Each JobContract also carries `what_chris_approves`,
`what_chris_handles`, `what_i_can_do_alone` tuples of free-text
strings (jobs.py:152-154, 359-381, 626-655, 933-965, 1154-1172
per sub-agent 3). Total per employee: 3–8 strings each.

These are human-readable scope statements, not authority strings.
They describe the *human decision boundary* around the employee's
authority. Symbol-mapping candidates? Only if the design promotes
them from documentation to enforceable — which nothing in scope
today does.

### 2.8 Cross-employee shared surface (potential future template)

Per sub-agent 1 + `governance_authority_evolution.md` F6:

| Shared string | Level | Employees | Convergence direction |
|---|---|---|---|
| `open_pull_request` | PROHIBITED | 4/4 | Universal invariant |
| `certify_mission_run` | EXECUTE | 3/4 (Triage opt-out) | Near-universal; opt-out has design justification |
| `recommend_remediations` | RECOMMEND | 3/4 (Rigby scope-specific) | Near-universal within remediation scope |
| `modify_any_file` | PROHIBITED | 2/4 | Emerging pattern; not consistent with Rigby's granular version |
| `delete_database_rows` | PROHIBITED | 2/4 | Same as above |
| `execute_arbitrary_code` | PROHIBITED | 2/4 | Same as above |
| `modify_settings` | PROHIBITED | 2/4 | Same as above |

If a future "shared authority template" is designed, these 7
strings would be the seed. That is out of scope here but
flagged in §10 Q4 as a candidate downstream research question.

---

## 3. Runtime Action Vocabulary

Every runtime action surface enumerated by sub-agent 2, verified
against source. This is the *other* side of the mapping gap —
what the runtime actually knows about the actions it dispatches.

### 3.1 Full inventory of action surfaces

| # | Surface | Identifier today | Count | Location | Authority metadata? |
|---|---|---|---|---|---|
| 1 | **MissionRunner steps** | `Step.name: str` | 17 (4+5+1+7 across 4 employees) | jobs.py per-job `daily_routine` tuples; Step dataclass at `mission_runner.py:372-388` | **NO** — Step dataclass has only `name` + `fn` |
| 2 | **PA tool schemas** | Tool name string | **113** (per PLATFORM_INVENTORY runtime anchor; raw name-token grep = 119, PLATFORM_INVENTORY wins) | `core/services/pa_tool_schemas.py:24-5013` | **NO** — no `action_class` attribute on any schema (grep confirmed 0 hits) |
| 3 | **PA tool actions** (action enum per tool) | `payload['action']` string, per-tool enum | ~200+ actions across 113 tools; scattered per-tool inline in schemas | pa_tool_schemas.py per-tool `properties.action.enum` arrays | **NO** — action enum values carry no authority metadata |
| 4 | **Celery tasks** | Task name (routing key from function name) | **~414** user-defined tasks per PLATFORM_INVENTORY | `core/tasks*.py`, `core/tasks_*.py` files (17+ modules) | **NO** — `@shared_task` decorator has no authority kwarg |
| 5 | **Django management commands** | Command class name (= filename) | **193** per PLATFORM_INVENTORY | `core/management/commands/` | **NO** — standard Django command classes |
| 6 | **AGENT_MAP agents** | Agent name string | **83** per PLATFORM_INVENTORY | `core/agent_router.py` AGENT_MAP dict | **NO** — agents are class references |
| 7 | **OpsRunEvent labels** | `label: str` CharField | ≥4 named constants; many inline strings | `mission_runner.py:264-316` + per-job constants (e.g., `docs_cascade.py:105`) | **NO** for most; **YES-ADJACENT** for `AUTHORITY_CONTRACT_OBSERVED_LABEL` |
| 8 | **HumanAttentionItem creators** | Caller context only (no HAI-row identifier) | 31 call sites per `substrate_audit.md` §3.5 | scattered across handlers, agents, tasks, views | **NO** — HAI carries category/priority but no `authority_action` |
| 9 | **Deliverable creation sites** | Caller context only | ~101 create calls across 44 files (sub-agent 2 grep) | scattered | **NO** — Deliverable has type/category/publish_intent but no authority |
| 10 | **Model writes (structural)** | Model class + operation (implicit) | 100s of `.save()` / `.create()` call sites | throughout codebase | **NO** — no model carries `action_class` field today |
| 11 | **HTTP endpoint views** | URL path + method + view class | ~1857 path() patterns per PLATFORM_INVENTORY across 208 views files | `core/views*.py`, `core/urls*.py` | **NO** — DRF `permission_classes` bind to user role, not action_class |
| 12 | **LLM tool_calls (function-calling)** | tool_name + parameters (from LLM response) | Runtime-dependent; recorded per-call | `LLMCallEvent` + `ToolCallRecord` | **NO** — records tool_name + parameters, no action_class field |

### 3.2 Identifier stability rank

Per sub-agent 2 stability analysis:

**Fully identified (stable string keys today, ready to be mapped
without new metadata):** MissionRunner steps, PA tool names,
Celery tasks, management commands, AGENT_MAP agents. **5
surfaces.**

**Partially identified (has an identifier but drift risk or
free-form):** OpsRunEvent labels, HTTP endpoints, LLM tool_calls,
mission step internal actions. **4 surfaces.**

**Unidentified (no runtime string identifier — would need one
added):** Model writes, Deliverable creation, HAI creators. **3
surfaces.**

### 3.3 Cardinality between authority strings and runtime surfaces

Per sub-agent 2 cardinality analysis, mapping is NOT 1:1:

| Cardinality | Example | Implication for symbol mapping |
|---|---|---|
| **1 authority : 1 surface** | `"modify_periodic_task_enabled"` → `PeriodicTask.enabled` write | Trivial mapping; single hook |
| **1 authority : N surfaces** | `"certify_mission_run"` → OpsRun.status write + `verdict_issued` event + `mission_verdict` tool | Registry must handle multi-surface fan-out |
| **N authorities : 1 surface** | `run_docs_cascade_commands` + `run_drift_observation` both fire during docs cascade steps | Registry must handle surface disambiguation |
| **1 authority : 0 surfaces** (gap) | `"open_pull_request"` — no runtime hook exists (shell subprocess) | Symbol mapping cannot bind to a non-existent hook |
| **0 authorities : N surfaces** | Every LLM call (there is no `use_llm` authority string) | Symbol mapping does not have to cover every surface |

### 3.4 Gap surfaces (actions with no runtime observation point)

Per sub-agent 2 §E and sub-agent 4 §D, some authority strings
have **no runtime hook** to observe:

| Authority string | Employee(s) | Why there's no hook |
|---|---|---|
| `open_pull_request` | 4/4 (PROHIBITED) | Would happen via `subprocess.run(['gh', 'pr', 'create', ...])`; no centralized subprocess wrapper |
| `restart_worker` | Triage (PROHIBITED) | Would happen via `pkill -f daphne` or Celery SIGKILL; no process-control instrumentation |
| `modify_any_file` | Auditor + Triage (PROHIBITED) | Python `open(mode='w')` + `write()`; no file-system audit hook |
| `send_emails_externally` | Chief (PROHIBITED) | Would use SMTP or external service; no outbound-email gate |
| `send_external_messages` | Chief (PROHIBITED) | Same as above |
| `post_publicly` | Chief (PROHIBITED) | Would use social API clients; no outbound-post gate |
| `execute_arbitrary_code` | Auditor + Triage (PROHIBITED) | `exec()`, `eval()`, dynamic imports; unbounded surface |
| `access_secret_values` | Auditor (PROHIBITED) | Reading `os.environ[SECRET_KEY]` or `settings.SECRET_KEY`; no import-time gate |

**Symbol-mapping implication:** Even a perfect registry could not
prevent these actions from happening — the hooks don't exist.
For these, the only defenses are (a) contract-review (code
review catches at PR time) and (b) enforcement rely on human
observation. Any symbol-mapping design must decide whether to
mark these strings as `enforcement_scope='code_review_only'` or
similar, so future readers know the registry does not extend to
them.

### 3.5 Surfaces where authority is already partially observable

Per sub-agent 4 §D, existing enforcement gates already bind some
identifier vocabularies to some actions:

| Gate | Vocabulary | Binds to | Precedent value |
|---|---|---|---|
| `AssistantProfile.get_allowed_tools()` | Tool names (subset per profile) | ToolDispatcher entry | Tool-name-level authority (not action-level) |
| `LLMEnforcer.check_budget()` | Budget freeze flag + purpose enum | LLM call surface | Purpose-based enforcement pattern |
| `messaging_tool.send_message` gate | `MESSAGING_TOOL_ALLOW_SEND` feature flag | One tool action | Feature-flag-per-action pattern |
| `REMOVED_TOOL_ALIASES` (13 entries) | Old tool name → (new tool, new action) tuple | Deprecated dispatch redirect | **This IS a symbol map** — for tool deprecation, not authority |
| `governance_tool` PA tool | Autonomy plane mode names | GovernanceState + KillSwitch write | Cross-plane precedent |

**REMOVED_TOOL_ALIASES is the closest existing thing to what
symbol mapping would look like:** it's a dict-keyed registry
mapping a source string (`"initiative_tool"`) to a target
(`("work_tool", "initiative_list")`). The shape is exactly the
shape a symbol registry would take, just serving a different
purpose (deprecation tracking, not authority enforcement).

---

## 4. Existing Symbol Systems

Per sub-agent 3 enumeration + one Rigby SIGN addition = 24
identifier registries already inside the platform. Any
symbol-mapping design should maximize reuse; new registries are
anti-pattern per `EMPLOYEE_OS_PRIMITIVES.md` §2 anti-duplication
matrix.

### 4.1 Full symbol-system inventory

| # | System | Type | Count | Reuse potential for symbol mapping | File:line |
|---|---|---|---|---|---|
| 1 | PA tool schemas | dict-keyed list (PR-reviewed) | 113 | **MEDIUM** — stable names, but tool-level not action-level | pa_tool_schemas.py:24-5013 |
| 2 | PA tool actions (per-tool enums) | inline enum arrays (per schema) | ~200+ | **MEDIUM** — stable within tool scope, no central registry | pa_tool_schemas.py per-tool blocks |
| 3 | AGENT_MAP agent names | dict-keyed registry | 83 | **MEDIUM** — user-facing not authority-facing | agent_router.py AGENT_MAP |
| 4 | Employee handles | frozen dataclass constants | 4 | **HIGH-for-scope** — stable + PR-reviewed but narrow | jobs.py:87 (handle field), 1327-1347 (registry) |
| 5 | Job / mission_run_kind | frozen dataclass constants | 4 | **HIGH-for-scope** — stable, one per employee | jobs.py per-job dataclasses |
| 6 | Step names | frozen tuple fields on JobContract | 17 | **MEDIUM** — stable within job; not globally unique across jobs | per-job daily_routine / weekly_routine |
| 7 | AuthorityLevel enum | str enum (4 members) | 4 | **HIGH — already authority-primitive** | jobs.py:41-52 |
| 8 | OpsRunEvent label constants | module-level string constants | ≥4 named + many inline | **HIGH — already authority-adjacent** (AUTHORITY_CONTRACT_OBSERVED_LABEL) | mission_runner.py:264 + per-job files |
| 9 | Model TextChoices / IntegerChoices | Django enums (per-model) | 25+ enums | **MEDIUM** — stable, migration-backed, but domain-specific | core/models_*.py across 20+ files |
| 10 | EventBus streams | str enum (8 members) | 8 | **LOW** — infrastructure identifier, not action | event_bus.py:21-31 |
| 11 | Deliverable category (free CharField) | free string | UNKNOWN | **LOW** — no schema, drift-prone | Deliverable model |
| 12 | Deliverable types | TextChoices (12 members) | 12 | **MEDIUM** — content-focused | models_deliverables.py:31-44 |
| 13 | HumanAttentionItem enums | TextChoices (4 fields) | 4+8+8+5 = 25 values | **MEDIUM** — some (approve/reject/escalate) mirror authority concepts | models_human_interface.py:20-89 |
| 14 | PeriodicTask names (beat) | dict-keyed schedule | 91 enabled + 5 disabled = 96 per PLATFORM_INVENTORY | **MEDIUM** — task-execution primitives | celery.py app.conf.beat_schedule |
| 15 | URL route names | Django URL registry | ~1857 paths per PLATFORM_INVENTORY | **LOW** — too many, web-layer detail | core/urls*.py |
| 16 | Signal names | scattered convention | UNKNOWN | **LOW** — loose coupling by design | core/signals/*.py |
| 17 | Feature flag names | convention (no central registry) | ≥12 per `governance_authority_evolution.md` §2.7 | **INAPPLICABLE** — feature toggles ≠ action identifiers | settings.py + scattered |
| 18 | Celery queue names | string literals | ≥7 per Procfile (worker/pa/content/long-running/long-running-2/broadcast/beat) | **LOW** — too few, execution context only | Procfile + Makefile + task_routes |
| 19 | Body system names | model-per-system | 9 per PLATFORM_INVENTORY | **LOW** — orthogonal to authority | 9 body system models |
| 20 | `prohibited_actions` tuples | frozen dataclass tuples | 30 entries across 4 employees | **INAPPLICABLE for enforcement** — documentation-only vocabulary | per-employee JobContract fields |
| 21 | Boundary tuples (`what_chris_approves`, etc.) | frozen dataclass tuples | 3–8 per employee | **INAPPLICABLE** — human-readable scope statements | per-employee JobContract fields |
| 22 | REMOVED_TOOL_ALIASES | dict-keyed mapping | **13** entries (verified; sub-agent 3 said 12) | **HIGH — is a symbol registry** (for deprecation, not authority) | tool_dispatcher.py:210-229 |
| 23 | GATEWAY_TOOLS | frozenset | **22** entries (verified; sub-agent 3 said 23) | **MEDIUM** — canonical gateway tool set | tool_dispatcher.py:232-242 |
| 24 | `AssistantProfile.get_allowed_tools()` | DB-backed per-user allowlist (queryable) | UNKNOWN per-profile size; used at dispatcher gate | **MEDIUM** — is a symbol-gated allowlist keyed on tool names; per Rigby S1270 Q3 flag, deserves listing as an identifier registry (not just as an enforcement precedent per §6.4). Reuse as PA-tool authorization pattern; distinct from JobContract authority (per-user vs. per-employee-role). | tool_dispatcher.py:687-720 (consumer); AssistantProfile model UNKNOWN location |

### 4.2 Registry shapes (what "shape" a mapping registry could take)

Per sub-agent 3 §B, the shape options that already exist as
prior art in the codebase:

| Shape | Existing example | Notes |
|---|---|---|
| **dict-keyed registry (module-level)** | PA_TOOL_SCHEMAS, REMOVED_TOOL_ALIASES, `app.conf.beat_schedule` | Simplest; PR-reviewed changes; no migration |
| **class-based registry (register method)** | `ToolDispatcher._register_default_handlers()` (tool_dispatcher.py:249+) | Explicit registration API; testable |
| **TextChoices / IntegerChoices enum** | DeliverableType, HumanAttentionItem status/urgency/decision | Django-native; migration-backed; DB-validated |
| **str enum (module-level)** | AuthorityLevel, EventStream | Type-safe; no migration; enumerable |
| **frozen dataclass field (tuple)** | `daily_routine`, `prohibited_actions`, boundary tuples | Ordered, immutable; per-job scope |
| **JSONField with implicit convention** | Deliverable.metadata, OpsRunEvent.detail | Maximum flexibility; zero schema enforcement |
| **Convention only (grep-discoverable)** | Signal names, feature flags | Lowest friction to add, highest drift risk |

**Observation:** the shape a symbol-mapping registry takes should
match the *lifecycle* of what it registers. Authority strings are
edited via PR review (frozen dataclass fields); a mapping
registry probably wants the same lifecycle. Enum options and
dict-keyed module-level registries both fit. TextChoices adds
migration cost that authority strings don't currently pay.

### 4.3 Symbol systems already authority-adjacent

Per sub-agent 3 §D:

1. **`AuthorityLevel` enum** (4 members) — core authority
   primitive; every authority dict value maps to one of these.
2. **`AUTHORITY_CONTRACT_OBSERVED_LABEL` constant** — the
   OpsRunEvent label that today observes contract shape;
   would be reused (or paralleled) by any future violation
   event.
3. **`prohibited_actions` tuple** — parallel human-readable
   vocabulary to the PROHIBITED-level dict entries.
4. **`REMOVED_TOOL_ALIASES` dict** — structurally IS a symbol
   registry; different purpose (deprecation redirect vs.
   authority binding).
5. **Per-tool `action` enums in PA tool schemas** — implicitly
   authority-scoped (only users with tool access can invoke
   any action within it).

These five are the reuse-first candidates. Any symbol-mapping
design should show whether it extends any of these or requires a
new primitive.

### 4.4 Naming convention consistency across systems

Per sub-agent 3 §F:

- **Employee handles, job names, step names, PA tool names,
  authority action strings** — all snake_case, mostly
  consistent.
- **Verb-object vs. object-verb** — not enforced. Authority
  strings mix `build_docs_index` (verb-object) with
  `certify_mission_run` (verb-object) with `broken_link_sweep`
  (adjective-object).
- **Django enum values** — lowercase strings (Django
  convention).
- **Constants** — SCREAMING_SNAKE_CASE (Python convention).

**Overall consistency: MEDIUM.** Any registry design that
introduces a new naming convention should either match one of
the existing patterns exactly OR document why it differs.

---

## 5. Mapping Possibilities

**Research description of a design space, NOT a design.** Each
option is inventoried with its evident tradeoffs. Ranking, cost
estimates, and pick-one selection are downstream decisions with
their own review cycle.

The three known options from S1264 discovery — steps
self-declare, tool registry, hybrid — plus two additional
options surfaced during this research: a central symbol
registry and an evidence-only (retrospective) approach.

### 5.1 Option A — Steps declare `action_classes_invoked`

**Shape.** Extend the `Step` dataclass (mission_runner.py:372-388)
with a new field:

- Today: `Step(name, fn)` — two fields, frozen dataclass
- Proposed: add `action_classes_invoked: tuple[str, ...] = ()`

Each per-job step declaration (jobs.py per-job daily_routine)
gains explicit action_class declarations:

```
# HYPOTHETICAL SHAPE ONLY — not a design
Step(
    name="step_1_index",
    fn=step_1_build_docs_index,
    action_classes_invoked=("run_docs_cascade_commands",),
)
```

Runner cross-checks declared action_classes against the
JobContract.authority dict before invoking `step.fn(mission)`
(candidate boundary: layer 4 per §6).

**Benefits:**
- Steps own their own action attribution — most local to the
  code that performs the action.
- Zero coupling between step body and central registry.
- Backward-compatible if `action_classes_invoked=()` defaults
  to "unrestricted" (no enforcement).
- Compatible with warn-mode → enforce-mode migration (step
  declarations start optional, become required over time).

**Costs:**
- Requires step maintainer to keep declarations synchronized
  with step body actions.
- Declarations can drift silently (declared string X, body
  does string Y; runner has no way to detect).
- Every new authority string requires touching every
  affected step declaration.
- Steps that invoke tools transitively (via `ToolDispatcher`)
  can't declare tool-level actions without knowing what the
  tool will do.

**Migration impact:** 17 existing steps across 4 employees
would need declarations. Small surface, contained.

**Review surface:** PR review checks declaration matches
observed behavior. Standard code review workflow.

**Backward compatibility:** Adding optional field with default
`()` preserves all existing steps.

**Telemetry impact:** New event or new detail field could
record "declared vs. observed" for each mission.

**Failure modes:**
- **Declaration drift** — step body changes without updating
  declaration. Enforcement layer would gate on stale
  declarations.
- **Overdeclaration** — step declares actions it doesn't
  actually invoke. False positives on authority check.
- **Underdeclaration** — step invokes actions not in declared
  set. Enforcement would block or violation-detect.

**Unknowns:**
- Does declaration cover tool calls made by the step, or only
  direct model writes / operations?
- How do delegated agent calls (via `route()`) get attributed?

### 5.2 Option B — Tools carry `action_class` attribute

**Shape.** Extend PA tool schemas (pa_tool_schemas.py) with an
`action_class` field per tool (or per tool+action pair):

```
# HYPOTHETICAL SHAPE ONLY — not a design
{
    "name": "deliverable_tool",
    "action_class": {  # NEW — per-action mapping
        "create": "create_escalation_deliverable",
        "update": None,  # not authority-tracked
        "set_status": "certify_mission_run",
    },
    ...
}
```

Dispatcher reads the calling agent's employee_handle from
context, looks up JobContract.authority[action_class], and
gates before handler invocation (candidate boundary: layer
6-7 per §6).

**Benefits:**
- Centralized declaration in tool schema (one file to
  maintain).
- Attribution is at the tool boundary — matches existing
  dispatcher gate pattern (`AssistantProfile.get_allowed_tools`).
- Tool schema is already PR-reviewed; adding action_class
  fits the review cycle.
- Compatible with `REMOVED_TOOL_ALIASES` pattern (both are
  tool-name-keyed registries).

**Costs:**
- Not every action_class corresponds to a tool call. Model
  writes (Document.create, PeriodicTask.enabled=…) happen
  outside tool dispatch.
- Steps that invoke non-tool actions (raw ORM writes, shell
  subprocess, agent delegation) are still unobserved.
- Requires 113 tool schemas × ~200 actions = many action_class
  cells to fill; most likely `None` (no authority tracked).
- Coupling: tool schema author has to know what authority the
  action serves — knowledge that may live only in the employee
  contract.

**Migration impact:** 113 tool schemas would need review; most
likely small % need action_class annotation.

**Review surface:** PR review of tool schema; standard.

**Backward compatibility:** Adding optional `action_class`
field preserves all existing schemas.

**Telemetry impact:** `ToolCallRecord` could gain
`action_class` column; enforcement events could reference tool
name + action_class pair.

**Failure modes:**
- **Attribution gap** — action happens outside tool dispatch
  (model write, shell command). Registry cannot bind.
- **Multi-action tools** — tool with 10 actions needs
  per-action registration; risk of stale entries.
- **Cross-tool actions** — an authority like `certify_mission_run`
  can happen via `mission_verdict` tool OR via direct
  `OpsRun.status = 'passed'` write. Registry would need both
  registrations OR both surfaces would need identical wiring.

**Unknowns:**
- Should `action_class` be per-tool or per-tool+action?
- How does the dispatcher get the calling employee's contract?
  (Contract available in mission context, but tool dispatcher
  is called from many surfaces beyond MissionRunner.)

### 5.3 Option C — Hybrid: steps declare + tools carry attribute

**Shape.** Both A and B. Steps declare their action_classes;
tools carry `action_class` per action. Runner cross-checks
both. Tool-carrying `action_class` becomes the authoritative
source when the step invokes a tool; step declaration becomes
the source when the step invokes non-tool actions (model
writes, shell commands, direct agent delegation).

**Benefits:**
- Defense-in-depth (per sub-agent 4 §F composition analysis).
- Complementary coverage — steps handle non-tool actions;
  tools handle in-dispatcher actions.
- Progressive rollout — either half can ship first.
- Discrepancy detection: if step declares X and tool declares
  Y for the same call, mismatch is observable.

**Costs:**
- Two registries to maintain.
- Precedence question (step declaration vs. tool declaration)
  must be resolved.
- Redundancy risk (both declare the same action_class,
  runner sees duplicate).
- Complexity for downstream consumers reading the audit
  chain — they see both declarations and have to reconcile.

**Migration impact:** Combined A + B surface.

**Review surface:** PR review of both step declarations and
tool schemas.

**Backward compatibility:** Additive on both surfaces.

**Telemetry impact:** Both surfaces emit; consumers must
dedupe.

**Failure modes:**
- **Precedence ambiguity** — step declares EXECUTE for
  `send_emails_externally`, tool declares PROHIBITED. Which
  wins?
- **Coordination burden** — refactoring a step requires
  touching two surfaces.

**Unknowns:**
- Which surface is "primary" for a given action_class?
- How is discrepancy surfaced (audit event, hard fail, log
  only)?

### 5.4 Option D — Central symbol registry

**Shape.** A new module-level registry (dict / class /
frozen mapping) that binds every action_class string to a
runtime *predicate* (a callable that returns True when the
runtime is invoking that action_class). The predicate could
inspect the current mission context, active tool call,
in-flight model save, etc.

```
# HYPOTHETICAL SHAPE ONLY — not a design
ACTION_CLASS_REGISTRY = {
    "run_docs_cascade_commands": lambda ctx: ctx.tool_name in (
        "management_command", "docs_cascade_tool"
    ),
    "create_escalation_deliverable": lambda ctx: (
        ctx.model == "Deliverable"
        and ctx.op == "create"
        and ctx.category == "escalation"
    ),
    "certify_mission_run": lambda ctx: (
        ctx.event_label == "verdict_issued:certified"
        OR (ctx.model == "OpsRun" and ctx.field == "status" and ctx.value == "passed")
    ),
    ...
}
```

Runner (or dispatcher, or signal handler) invokes the
predicate with runtime context; if predicate matches AND
authority is PROHIBITED, block.

**Benefits:**
- Single source of truth for action_class → runtime binding.
- Steps and tools don't need to know they're being observed
  (no declaration burden).
- Retroactive: predicates can be added as new action_classes
  are needed; existing code untouched.
- Testable: predicates are pure functions.

**Costs:**
- Highest new-metadata cost — the registry is entirely new
  primitive.
- Predicate quality determines coverage; a predicate that
  misses cases lets violations through.
- Registry becomes a single point of failure — one bad
  predicate can block a whole employee's work.
- Predicate authoring requires knowing every runtime surface
  where the action could happen.
- Registry can grow unbounded (57 unique strings today; more
  as employees are added).

**Migration impact:** 57 predicates to author.

**Review surface:** PR review of registry file; every
predicate change is a small, focused review.

**Backward compatibility:** Registry starts empty; predicates
added incrementally. Warn-mode compatible.

**Telemetry impact:** Predicate evaluation events could
record match/no-match per dispatch.

**Failure modes:**
- **Predicate coverage gap** — an action happens that no
  predicate covers. Silent under-enforcement.
- **Predicate false positive** — action doesn't happen but
  predicate returns True. False block.
- **Registry drift** — code changes but predicate doesn't.
- **Composability** — two predicates could return True for
  the same context. Which action_class is authoritative?

**Unknowns:**
- Where does the predicate get invoked (dispatcher, signal,
  postflight)?
- What does the runtime context object contain? Is there a
  canonical shape?

### 5.5 Option E — Evidence-only (retrospective observation)

> **Reversibility ≠ preference (Rigby S1270 SIGN clarification).**
> Option E is presented alongside Options A-D as a research
> description of the design space. The fact that it is *the most
> reversible* option (per F7) is a mechanical property, not a
> recommendation. Any preference among the 5 options is a Chris-
> gated design decision downstream of this research; nothing in
> this section marks Option E as preferred.

**Shape.** No enforcement. No pre-dispatch check. Every action
surface emits action_class as part of its audit row
(`ToolCallRecord.action_class`, `OpsRunEvent.detail.action_class`,
etc.). Post-mission (or post-hoc via analytics), compare
observed action_classes against the contract's authority dict
to detect violations. Violations surface as HumanAttentionItems
or as summary events on the next mission run.

**Benefits:**
- Zero risk of false blocks — the runtime never gates.
- Preserves warn-mode invariant (mission NEVER halts).
- Compatible with all other options (any of A-D could bolt
  onto the same audit trail).
- Lowest structural risk: pure telemetry addition.
- Immediate downstream consumer: Bug Triage step 4
  (`bug_triage.py:396-453`) already aggregates
  `authority_contract_observed` events — a violation
  aggregator could parallel it.

**Costs:**
- No prevention — violations happen; only detection.
- Requires action_class field on 5+ audit models
  (`ToolCallRecord`, `OpsRunEvent`, `LLMCallEvent`,
  potentially others).
- Fills the audit chain but doesn't close the enforcement
  gap.
- Producers (tools, runner, signal handlers) all need to
  populate action_class fields.

**Migration impact:** Model migrations for 5+ audit tables;
producer changes wherever audit rows are written.

**Review surface:** PR review of migrations + producer
changes.

**Backward compatibility:** Fully additive.

**Telemetry impact:** Every audit row grows a new column;
storage cost proportional to row count (~1.14M
SpiderItemHash rows suggest observation costs are non-
trivial at scale).

**Failure modes:**
- **Observability without accountability** — violations
  detected but not blocked.
- **Producer omission** — a code path writes audit row
  without populating action_class. Silent gap.
- **Consumer lag** — violations detected in next mission's
  step 4, not in real-time.

**Unknowns:**
- Does audit data live long enough for meaningful analysis?
  (`CELERY_TASK_EVENT_RETENTION_DAYS=30` per memory rule
  suggests audit rows have a bounded window.)
- Does the analytics layer become the enforcement layer
  (turning violations into human attention)?

### 5.6 Cross-option comparison

| Option | New attribute location | Enforcement possible? | Coverage | Reuse of existing systems |
|---|---|---|---|---|
| A: Steps self-declare | `Step` dataclass field | YES (pre-dispatch, layer 4) | Steps only — no non-mission surfaces | High reuse of Step primitive |
| B: Tools carry attribute | Tool schema field | YES (pre-dispatch, layer 6) | Tool-mediated actions only | High reuse of pa_tool_schemas + REMOVED_TOOL_ALIASES pattern |
| C: Hybrid | Both above | YES (compound) | Broadest — steps + tools | High reuse; two-surface maintenance |
| D: Central registry | New module | YES (any layer) | Predicate-defined (potentially universal) | Low reuse — new primitive |
| E: Evidence-only | 5+ audit models | NO (retrospective only) | All audit-emitting surfaces | High reuse of existing audit chain |

### 5.7 What is *not* an option

Explicitly out of the design space (would require radically
new architecture):
- **Per-request LLM authority check.** LLM cannot be trusted
  to know its own authority; would defeat the purpose.
- **Runtime introspection of `step.fn.__code__`.** AST
  analysis of step bodies to detect action classes.
  Fragile and expensive.
- **Manual review of every PR for authority drift.** Not
  a symbol mapping design; that's the current status quo.

---

## 6. Enforcement Boundaries

Per sub-agent 4's inventory: 20 architecturally-possible
interception layers, from "before MissionRunner starts" to
"post-invocation retrospective." **This section enumerates,
does not rank.**

### 6.1 Enforcement mode taxonomy

| Mode | Definition | When violation is detected |
|---|---|---|
| **PRE-DISPATCH** | Check runs before action is invoked | Before any side-effect |
| **INLINE** | Check runs during action's execution flow | Mid-execution; may abort |
| **POST-DISPATCH** | Check runs after action has occurred | After side-effect; observation only |

### 6.2 20 candidate layers

| # | Layer | Mode | Existing precedent? | Signal coverage |
|---|---|---|---|---|
| 1 | Beat scheduler / employee_tool / mgmt command | PRE-DISPATCH | AssistantProfile.get_allowed_tools (tool-level) | Tool/mission name only |
| 2 | MissionRunner preflight (warn-mode) | POST-DISPATCH | **EXACT — this is where warn-mode lives** | Contract shape only |
| 3 | Between preflight and first step | N/A | None — no hook exists | N/A |
| 4 | Before each Step.fn invocation | PRE-DISPATCH | None | Step name only |
| 5 | Inside Step.fn execution | INLINE | Decorator patterns exist | Depends on step |
| 6 | ToolDispatcher.execute() entry | PRE-DISPATCH | AssistantProfile + LLMEnforcer | tool_name + action visible |
| 7 | Inside tool handler | INLINE | messaging_tool feature-flag guard | action + handler context |
| 8 | Before LLM call | INLINE | **LLMEnforcer.check_budget is exact precedent** | Budget purpose only |
| 9 | After LLM returns tool_calls | PRE-DISPATCH | None | tool_call name visible |
| 10 | Before Celery task.delay() | PRE-DISPATCH | Task queue routing | Task name only |
| 11 | Django pre_save / pre_delete signal | INLINE | Validation signals exist | Model + operation |
| 12 | After step returns (post-step hook) | POST-DISPATCH | OpsRunEvent emission | Result + name only |
| 13 | Post-mission postflight | POST-DISPATCH | postflight_fn hook (per mission_runner.py:1080-1105) | Outcome only |
| 14 | Audit chain (evidence_for_mission) | POST-DISPATCH | ToolCallRecord + OpsRunEvent queries | All audit rows — IF populated |
| 15 | HTTP endpoint / DRF permission | PRE-DISPATCH | IsAuthenticated, admin gate | User role only |
| 16 | OpsRunEvent post_save signal | POST-DISPATCH | None wired today | Event detail — IF populated |
| 17 | Agent-to-agent delegation | INLINE | None | Agent name only |
| 18 | WorkspaceTrigger fire event | PRE-DISPATCH | Trigger configuration | Trigger action |
| 19 | Subprocess wrapper | PRE-DISPATCH | None (no centralized wrapper today) | Command name only |
| 20 | Post-invocation retrospective | POST-DISPATCH | Audit query patterns | All rows — IF populated |

### 6.3 Signal coverage per layer

Sub-agent 4 §C quantified visibility of the 57 unique authority
strings if a check was inserted at each layer:

| Signal category | Meaning | Layers |
|---|---|---|
| **All strings visible** | Every action_class observable at this layer | 11 (pre_save signal, IF model.action_class field exists), 14 (audit chain, IF audit models carry action_class), 20 (retrospective, IF audit rows populated) |
| **Some strings visible** | Subset visible (typically tool-mediated actions only) | 6 (dispatcher: tool + action), 9 (post-LLM: tool_calls), 15 (HTTP: user role), 17 (agent delegation: agent name) |
| **Symbol-dependent visibility** | Visible IF the mapping option provides an attribute | 4 (steps: needs `action_classes_invoked`), 5 (inside step: needs contract in scope), 7 (handler: needs registry), 10 (Celery: needs task registry), 16 (event signal: needs event field), 18 (trigger: needs mapping) |
| **No strings visible** | Layer has no authority-relevant identifier | 1, 2, 8, 12, 13, 15 (mostly), 19 |

**Observation:** Every "all strings visible" layer requires a
new field on an audit model. Every "symbol-dependent" layer
requires the design option to add an attribute somewhere.
No layer provides "all strings visible" for free.

### 6.4 Existing precedents (already-live enforcement patterns)

Per sub-agent 4 §D, the platform already has 11 authority-like
patterns in production:

| Pattern | Location | Enforcement mode | Vocabulary |
|---|---|---|---|
| Tool access gating (allowed_tools) | tool_dispatcher.py:687-720 | PRE-DISPATCH | Tool names (per-profile allowlist) |
| Budget authority (LLMEnforcer.check_budget) | llm_enforcer.py:200-260 | INLINE | Budget freeze flag + purpose enum |
| Feature-flag gating (messaging_tool) | td_handlers_core.py:3693-3711 | INLINE | Feature flag boolean |
| Django pre_save signal validation | Various models_*.py signals | INLINE | Model state |
| DRF IsAuthenticated permission | Various views | PRE-DISPATCH | Auth status |
| Admin gate (is_staff check) | auth_middleware.py:610-614 | PRE-DISPATCH | Staff status |
| Retry budget (check_retry_budget) | retry_policy.py:141-200 | INLINE | Rate limit counter |
| CELERY_TASK_ROUTES queue routing | tool_dispatcher (queue field) | PRE-DISPATCH | Queue name |
| Timeout enforcement (asyncio.wait_for) | tool_dispatcher.py:759-772 | INLINE | Duration |
| Spider governance check (freeze/safe_mode) | tasks_spiders.py:381-398 | PRE-DISPATCH | GovernanceState.mode |
| VIP scope injection | views_personal_assistant.py:316-346 | INLINE (prompt-injection) | User role |

**Notable pattern:** LLMEnforcer.check_budget is architecturally
the closest analog to a runtime authority gate. It sits INLINE,
gates a semantic action (LLM call), and uses a purpose enum
that maps 1:1 to authority-adjacent semantics. Any INLINE
authority enforcement would likely reuse the same pattern.

### 6.5 Layer composition constraints

Per sub-agent 4 §F, checks at multiple layers compose in
predictable but non-trivial ways:

**Sequential PRE-DISPATCH layers (1, 4, 6, 10):** Redundant if
they gate the same identifier vocabulary; reinforcing if they
gate different ones (defense-in-depth). Trade-off: consistency
vs. coverage.

**Warn-mode preflight (layer 2) invariant:** Per S1264 decree
(mission_runner.py:833-843 + Rigby SIGN edit #5), preflight
NEVER blocks. Any enforce-mode check must sit *after* preflight,
not *within* it.

**Signal handler (layer 11) transaction safety:** Django
pre_save signal runs in-transaction; raising rolls back. Side
effects from other signal handlers on the same save are also
rolled back. Transactional care required.

**Audit-chain (layer 14, 20) retrospective:** Cannot prevent
violations, only detect. Composes with any PRE-DISPATCH layer
as a safety net for cases the pre-check missed.

### 6.6 What every candidate layer needs to work

Per sub-agent 4 §E, minimum requirements per layer:

- **Layer 4 (before step):** Step dataclass extended
  (Option A).
- **Layer 6 (dispatcher):** Tool schema extended (Option B)
  OR central registry (Option D).
- **Layer 8 (LLM call):** Contract in call context; new
  authority-check function parallel to check_budget.
- **Layer 11 (pre_save signal):** Action_class field on model
  (Option E) + producer instrumentation.
- **Layer 14 (audit chain):** Action_class field on
  `ToolCallRecord.action_class` + `OpsRunEvent.detail.action_class`
  + producer instrumentation.
- **Layer 20 (retrospective):** Same as layer 14.

**Cross-cutting requirement:** Every enforcement layer needs
the contract available. `MissionRunnerConfig.job_contract` is
in-scope inside MissionRunner; outside the runner (e.g., in
Celery task callbacks, agent delegation, direct HTTP handler),
the contract must be looked up from `_JOBS_BY_EMPLOYEE`
(jobs.py registry) using the employee handle.

---

## 7. Failure Analysis

Per sub-agent 5's catalog of 23 historical incidents, would
Symbol Mapping have prevented each?

### 7.1 Verdict distribution

| Verdict | Count | Percentage |
|---|---|---|
| **YES** — Symbol Mapping directly prevents | 5 | 22% |
| **PARTIALLY** — Symbol Mapping enables enforcement gate that would help | 10 | 43% |
| **NO** — Root cause is orthogonal to authority binding | 8 | 35% |
| **Total** | 23 | 100% |

**Effective case strength: 15 / 23 = 65% would be prevented or
significantly improved by Symbol Mapping.**

### 7.2 YES cases (5)

These are the 5 incidents where Symbol Mapping's central mechanism
(binding action_class strings to runtime symbols) directly closes
the failure class:

**I-S1: S1264 warn-mode discovery of 68 unbound authority strings.**
The discovery itself. `MissionRunner` cannot compare mission
behavior to `JobContract.authority` because strings don't bind.
S1264 shipped warn-mode (shape observation only); enforce-mode
blocked on this research. Source: PR #2756 + governance_authority_evolution.md §6.1 I-G1.

**I-S2: S1264 authority contract observation is shape-only.**
`_emit_authority_contract_event` (mission_runner.py:835-900)
observes counts + hash + level breakdown but cannot observe
violation because no runtime side emits action_class evidence.
Source: mission_runner.py:895-899 explicit comment.

**I-S3: Zero contract-layer enforcement gates.** 35 runtime
gates exist per governance_authority_evolution.md §4; zero read
`JobContract.authority` before dispatch. Symbol Mapping is the
prerequisite for adding a contract-layer gate. Source:
governance_authority_evolution.md **F1 + F3** (F1: only consumer
of the authority dict is `_emit_authority_contract_event`; F3:
"There is no enforcement primitive that reads
`JobContract.authority` before dispatching an action").

**I-S4: `certify_mission_run` is 3-of-4 employees.** Bug Triage
opts out via `auto_emit_verdict=False`. Symbol Mapping could
allow the same policy to be expressed via authority-mapped
conditional (only employees with `certify_mission_run: EXECUTE`
in dict trigger the verdict emit path) instead of a bespoke
config-flag branch in runner code — if the design mission
chooses that path. Per Rigby S1270 SIGN clarification: Symbol
Mapping does not automatically eliminate the config flag; it
enables the policy to move from a boolean to a symbol-mapped
check *if that is the chosen design*. Source: bug_triage.py:1179
(config flag set) + mission_runner.py:1128-1145 (conditional
branch).

**I-S5: Bug Triage authority telemetry is by-employee-handle only.**
Step 4 (bug_triage.py:396-453) aggregates
`authority_contract_observed` events by employee handle + count.
Without action_class in the event detail, cross-employee
comparison of *which actions* were observed is impossible.
Source: bug_triage.py:396-453.

### 7.3 PARTIALLY cases (10 highlights)

Symbol Mapping enables an enforcement gate that would reduce
likelihood of these incidents, but is not sufficient alone:

- **auto_followup=False forensic suppression** (S1184): could be
  gated as a `forensic_dispatch` authority — only executor with
  the authority may suppress banner.
- **Placeholder-stall pattern** (S1226, S1241): could be gated
  as `mark_deliverable_completed` requires PUBLISH-equivalent
  authority.
- **Deliverable create defaults to completed** (S1241): status
  transitions could be authority-gated.
- **Deliverable update silent fallback >~6kB** (S1176): update
  vs. list dispatch could be verified against action_class the
  caller declared.
- **Verdict emit skip on auto_emit_verdict=False** (S1267):
  same as I-S4 above, contextually.
- **KillSwitch is write-only** (governance_authority_evolution.md
  F3): symbol mapping would enable gating on
  `KillSwitch.filter(target=…).is_active` at action time.
- **GovernanceState modes are ASPIRATIONAL outside freeze/safe_mode**
  (governance_authority_evolution.md F8): `throttle` mode
  gates could be added at action-class boundaries.
- **HumanPreference.topic_weights never populated**
  (governance_authority_evolution.md F10): authority around
  when/how the field is written could be scoped.
- **context['user'] is dict vs. FK** (S1234): contract-level
  action bindings could enforce "actions taking a User FK
  must receive a User instance."
- **WorkflowOrchestrationAgent result-key mismatch** (S1234):
  return-value contract could be authority-adjacent.

### 7.4 NO cases (8)

These are orthogonal to Symbol Mapping — root cause is
elsewhere:

- **Claude Code receipt vanishing** (S1262): task_entry
  architecture issue; fixed by wiring AgentExecution row +
  fail-loud post-back.
- **LLM autofills booleans** (S1227-1228): GPT-5.2 schema
  behavior; fixed by truthy-only guards.
- **WorkflowOrchestrationAgent return-key naming** (S1234):
  contract naming convention; Symbol Mapping doesn't fix
  wrong-key reads.
- **Celery queue parity drift** (S1244): infrastructure
  routing; fixed by parity canary tests.
- **Broad except swallows TypeError** (S1234 D16): error
  handling; fixed by narrowing except clauses.
- **Procfile/Makefile queue stall** (S1226): infrastructure.
- **Trust math persisted (anti-pattern avoided)**
  (EMPLOYEE_OS_PRIMITIVES.md §4.4): design decision;
  no incident.
- **Shift-report metadata unbounded (anti-pattern avoided)**
  (EMPLOYEE_OS_PRIMITIVES.md): design decision.

### 7.5 Failure class heat map

Per sub-agent 5 §C, ranked by count of incidents:

| Class | Count | Symbol Mapping ROI |
|---|---|---|
| Symbol mismatch | 3 | **HIGH** |
| Contract violation classes | 5 | **MEDIUM-HIGH** |
| Silent failure classes | 5 | **MEDIUM** |
| Tool dispatch failures | 4 | LOW-MEDIUM |
| Authorization failures | 4 | **HIGH** |
| Hardcoded behavior | 4 | **HIGH** |
| Permissions / authority failures | 3 | **HIGH** |
| Action attribution failures | 2 | MEDIUM-HIGH |
| Telemetry gaps | 2 | MEDIUM |
| Policy drift | 1 | MEDIUM |
| Missing receipts | 1 | LOW |
| Author/caller identity confusion | 0 | N/A |

**Highest-ROI classes:** symbol mismatch, authorization
failures, hardcoded behavior, permissions/authority failures.
Sub-agent 5 counted 14 incidents across these four classes —
61% of the historical catalog.

### 7.6 Recurrence risk

Per sub-agent 5 §D, failure classes that have recurred after
first fix:

1. **Tool dispatch receipt chains** (S1257 → S1261 → S1262) —
   pattern recurs for each new dispatch surface. Symbol
   Mapping would make receipt structure a contract.
2. **Procfile/Makefile queue parity** (S1226 → S1244) —
   pattern recurs on new queues. Symbol Mapping does not
   address (orthogonal).
3. **LLM autofill booleans** (S1227 → S1228 → ongoing) —
   pattern recurs per new optional-boolean param. Symbol
   Mapping does not address (LLM-side).
4. **Placeholder-stall** (endemic, S1226, S1241) —
   human-behavior pattern. Symbol Mapping enables structural
   gate (`mark_completed` requires PUBLISH authority).
5. **Authority observation without enforcement** (S1264 →
   waiting for Symbol Mapping) — STRUCTURAL recurrence per
   each new employee added.

The last one is the strongest recurrence argument for the
research: every new employee added without symbol mapping
inherits observation-only authority.

### 7.7 Silent-vs-loud analysis

| Class | Count | % | Symbol Mapping value |
|---|---|---|---|
| Silent (no evidence at time of failure) | 7 | 30% | **HIGHEST** — enables action-level logging |
| Semi-silent (evidence exists but hard to interpret) | 5 | 22% | HIGH — makes contract-level failure loud |
| Loud (thrown exception, obvious failure) | 11 | 48% | MEDIUM — enables structural prevention |

30% of historical failures were silent at time of occurrence.
Symbol Mapping's biggest architectural value is closing this
silent-failure window at the dispatch-audit boundary.

---

## 8. Reuse Classification

Per the standard research-doc format used by prior architecture
research (`substrate_audit.md` §8, `collaboration_patterns.md`
§8, `governance_authority_evolution.md` §7). Symbol-mapping-scoped
reuse classifications for the primitives, helpers, and models
relevant to symbol mapping — a curated subset of the 24 §4.1
systems (identifier registries that are LOW/INAPPLICABLE for
symbol mapping — e.g., URL route names, signal names, feature
flag registry, body system names — are inventoried in §4.1 but
not re-classified here since they are not candidate infrastructure
for a symbol registry). Total classified: 21 primitives (7 SAFE
+ 11 WRAPPER + 0 DO-NOT + 0 DEPRECATED + 3 UNKNOWN).

### 8.1 SAFE TO REUSE (7)

Systems that can be directly extended (or reused as-is) to
support symbol mapping without introducing footguns:

1. **`AuthorityLevel` enum** (jobs.py:41-52). Extend if new
   levels needed; reuse as-is otherwise. Already the core
   authority primitive.
2. **`AUTHORITY_CONTRACT_OBSERVED_LABEL` constant + schema
   version** (mission_runner.py:264-265). Reuse as the label
   for existing warn-mode; a violation event would use a
   parallel label.
3. **`_hash_contract_shape` helper** (mission_runner.py:278-303).
   Reuse for cross-mission contract grouping.
4. **`_AuthorityContractMalformedError` exception**
   (mission_runner.py:268-275). Reuse **narrowly** as the
   *contract-shape* validation error (dict-ness of `authority`,
   tuple/list-ness of `prohibited_actions`). Per Rigby S1270
   SIGN edit #1: this exception should **NOT** be repurposed as
   a general-purpose "mapping registry malformed" error — the
   registry surface, if introduced, would need its own error
   type (e.g., hypothetically `MappingRegistryMalformedError`,
   name TBD by the design mission) to avoid semantic drift on
   what "contract malformed" means. This doc does not propose
   such a type; it flags the risk.
5. **`MissionRunnerConfig.job_contract` field**
   (mission_runner.py:562-572). Reuse — already the contract
   handoff point.
6. **`_emit_authority_contract_event` method**
   (mission_runner.py:835-900). Reuse pattern (event
   emission with shape counts) for future violation-detection
   events.
7. **`Step` dataclass** (mission_runner.py:372-388). Reuse
   as-is for options that don't extend it (B, D, E); extend
   for Option A.

### 8.2 REUSE WITH WRAPPER (11)

Systems that could serve as symbol-mapping infrastructure but
need adapter code:

1. **PA tool schemas** (pa_tool_schemas.py) — Option B wraps
   with action_class attribute per action.
2. **PA tool actions** (per-tool enums) — same as above; per-
   action wrapping.
3. **`ToolDispatcher.execute`** (tool_dispatcher.py:585-653) —
   wraps to consult symbol registry (Option D) or per-tool
   attribute (Option B) before handler invocation.
4. **`Deliverable` model** — wrap create/update/delete to
   include action_class attribution (Option E requires this).
5. **`ToolCallRecord` model** (models_tool_calls.py) — wrap
   with action_class column for Option E.
6. **`OpsRunEvent` model** (models_ops_runs.py:91-118) —
   wrap detail with action_class key for Option E (JSONField,
   no migration needed).
7. **`LLMCallEvent` model** (models_llm_telemetry.py:30-116)
   — wrap with action_class metadata for Option E.
8. **`REMOVED_TOOL_ALIASES` dict** (tool_dispatcher.py:210-229)
   — pattern reuse for the registry shape; not the specific
   entries.
9. **`AGENT_MAP` agent names** — wrapper needed to bind
   agent → action_class if agent-delegation is scoped.
10. **`bug_triage.py:396-453` authority telemetry collector**
    — wrap to also collect violation events (parallel to
    contract-observed).
11. **`AssistantProfile.get_allowed_tools`** — wrapper pattern
    for adding contract-level authority checks parallel to
    tool-level.

### 8.3 DO NOT REUSE (0)

No existing symbol system is so broken that it shouldn't be
reused for symbol mapping. The 11 WRAPPER classifications
cover the friction cases.

### 8.4 DEPRECATED (0)

No deprecated identifier systems identified at this revision.
`REMOVED_TOOL_ALIASES` itself is not deprecated — it's a live
registry that would parallel a future symbol map.

### 8.5 UNKNOWN (3)

Systems where scope of reuse can't be determined without
choosing a mapping option first:

1. **Central symbol registry (Option D)** — would be new
   primitive; no existing system to reuse or wrap.
2. **`Step.action_classes_invoked` field (Option A)** —
   doesn't exist yet; would need adding.
3. **Cross-employee shared-authority template** (per §2.8 +
   governance_authority_evolution.md F6) — no existing
   primitive to reuse; may or may not be scope of this arc.

### 8.6 Anti-duplication check

Per `EMPLOYEE_OS_PRIMITIVES.md` §2 (anti-duplication matrix),
before introducing any new registry, model, or admin UI, check
existing:

| Proposed new primitive | Existing equivalent(s) | Anti-duplication verdict |
|---|---|---|
| Central action_class → predicate registry (Option D) | REMOVED_TOOL_ALIASES (dict-keyed), PA_TOOL_SCHEMAS (dict-keyed list), `AGENT_MAP` (dict-keyed) | Shape reuse OK; no existing registry does what Option D would need |
| `Step.action_classes_invoked` field (Option A) | `Step.name` field (existing) | Additive; no duplication |
| Tool `action_class` attribute (Option B) | PA tool schema (existing dict), `REMOVED_TOOL_ALIASES` (existing symbol map) | Additive; extends existing PR-reviewed surface |
| Audit-model `action_class` column (Option E) | Deliverable/HAI/OpsRunEvent already have JSONField for details | Extend existing JSONField OR add new column; both anti-duplication-safe |
| New `ActionClass` model / table | 22 existing identifier systems | **BLOCKED** — no design currently proposes one, but any future proposal must justify against these 22 |

---

## 9. Architectural Findings

Synthesis of the evidence into canonical findings every future
symbol-mapping discussion should start from.

### F1 — The authority vocabulary is dominated by unique per-employee strings

57 unique strings across 4 employees, but 88% (50 strings)
appear in only one employee. Shared strings are the exception,
not the rule. A registry design must handle high per-employee
cardinality, not assume a small shared vocabulary.

**Evidence:** Sub-agent 1 §B. 4-of-4 = 1, 3-of-4 = 2, 2-of-4 =
4, 1-of-4 = 50.

### F2 — No runtime surface carries authority metadata today

All 12 runtime action surfaces (§3.1) have stable identifiers,
but zero carry an `action_class` attribute or equivalent
authority binding. Grep against `pa_tool_schemas.py` for
`action_class` / `authority_key` / `permission_class` returned
0 hits.

**Evidence:** Sub-agent 2 §A + §F ("ZERO surfaces carry
authority-related metadata today"); direct grep verification
by Claude.

### F3 — The authority↔runtime cardinality is many-to-many, not 1:1

Some authority strings correspond to multiple runtime surfaces
(`certify_mission_run` = OpsRun.status write + verdict event +
mission_verdict tool). Some runtime surfaces correspond to
multiple authority strings (docs_cascade Celery task = both
`run_docs_cascade_commands` and `run_drift_observation`). Some
authority strings correspond to zero runtime surfaces
(`open_pull_request` — no hook exists). Some runtime surfaces
correspond to zero authority strings (LLM calls generically).

**Evidence:** Sub-agent 2 §C cardinality analysis, §E gap
surfaces; sub-agent 4 §C signal coverage.

### F4 — REMOVED_TOOL_ALIASES is structurally the closest existing symbol registry

13 entries (verified by direct read of tool_dispatcher.py:210-229;
sub-agent 3 undercount of 12 corrected). Maps deprecated tool
name → (new_tool_name, new_action_name). Shape matches what a
symbol registry would need — a dict-keyed table with tuple
values. Purpose differs (deprecation redirect vs. authority
binding), but shape reuse is available.

**Evidence:** tool_dispatcher.py:210-229 direct read; sub-agent
3 §A row 22.

### F5 — Warn-mode already emits the shape of the future violation event

`AUTHORITY_CONTRACT_OBSERVED_LABEL` +
`AUTHORITY_CONTRACT_SCHEMA_VERSION` + detail schema
(schema_version, employee_handle, contract_version_tag,
authority_entries_total, level_counts, prohibited_actions_count,
mode='warn') is the observation counterpart to what a violation
event would emit. Any Symbol Mapping enforcement design should
parallel this event shape, not invent a new one.

**Evidence:** mission_runner.py:264-265 + 880-900; sub-agent 3
§D row 8.

### F6 — S1264's honest note is the load-bearing citation for Symbol Mapping

`mission_runner.py:895-899` reads:

> "Observation of contract shape only; not violation detection.
> Enforce-mode requires future symbol mapping (S1264 discovery)."

The runtime itself declares symbol mapping is the prerequisite
for enforcement. This is not aspirational language — it's
in-code assertion that any downstream authority research must
respect.

**Evidence:** mission_runner.py:895-899 direct read.

### F7 — The five mapping options are not equally reversible

Option E (evidence-only) is the most reversible — pure additive,
no enforcement risk, no false blocks. Option D (central
registry) is the least reversible — introduces a new primitive
that becomes a single point of authority for the entire
platform. Options A, B, C are middle: additive attributes on
existing primitives.

**Evidence:** §5 tradeoff analysis per option.

### F8 — Composition of Symbol Mapping with the four governance planes is undesigned

Per governance_authority_evolution.md F1, four governance planes
(autonomy / authority / budget / human governance) do not
compose today. Adding symbol-mapping-enabled authority
enforcement introduces new composition questions:

- If `KillSwitch.is_active(target='publishing')` AND
  `JobContract.authority['post_publicly'] == EXECUTE`, does
  the kill switch win?
- If `SystemConfiguration.budget_freeze_active` AND authority
  is EXECUTE, does the freeze win?
- If human approval is required (`HumanAttentionItem` in
  pending state) AND authority is EXECUTE, does the wait win?

None of these are answered anywhere in code. Symbol Mapping
does not have to answer them — but any enforcement layer built
on top does.

**Evidence:** governance_authority_evolution.md F1 + sub-agent
4 §F composition analysis.

### F9 — Per-employee scope is currently the boundary

Symbol Mapping is naturally per-employee: contract lives on
JobContract, dispatch happens per-mission, evidence rolls up
per-employee. Extending to cross-employee (e.g., "Chief of
Staff dispatches Bug Triage — whose authority governs?") is
NOT in scope of this research. That is the Trust Propagation
research per governance_authority_evolution.md §10.2 and
ARCHITECTURE_INDEX.md §5.3.

**Evidence:** §2.2 per-employee dictionaries; sub-agent 1
grouping showing 88% unique-per-employee strings.

### F10 — The gap surfaces are the honest limit

For `open_pull_request`, `restart_worker`, `modify_any_file`,
`send_emails_externally`, `execute_arbitrary_code`,
`access_secret_values`: no runtime hook exists. Symbol Mapping
cannot enforce these regardless of design choice. The honest
answer for these strings is "code-review-only" enforcement.

**Evidence:** §3.4 gap surfaces per sub-agent 2 §E and sub-agent
4 §D.

### F11 — Seven architectural blind spots surfaced by Rigby S1270 SIGN

Rigby's independent SIGN review surfaced seven architectural
observation categories that this doc did not fully enumerate
in F1-F10 but that any Symbol Mapping design must confront.
These are recorded here as findings so the Option Selection
Design mission (§11.1) cannot skip them.

1. **Namespace + collision domain.** If action_class becomes
   canonical, at what scope is it defined? Global
   platform-wide? Per employee? Per desk? Per tool family?
   Without an explicit scope rule, collisions on common verbs
   (`publish`, `approve`, `dispatch`, `block`) are inevitable
   as vocabulary grows.
2. **Symbol lifecycle governance.** `REMOVED_TOOL_ALIASES`
   (§4.1 row 22) is precedent for a lifecycle primitive set
   (canonical symbol + aliases + deprecation markers + removal
   window). Symbol Mapping likely needs the same lifecycle
   pattern; "string stability" is directly tied to
   enforceability and auditability, not just cosmetic.
3. **Bidirectionality / invertibility.** Is the mapping
   required to be contract → runtime only ("what actions does
   this contract permit?"), OR also runtime → contract
   ("what action_class does this observed tool call bind
   to?")? The latter is required for reverse-mapping audit;
   many designs die at this boundary because every runtime
   action must emit enough metadata to be reversed.
4. **Granularity mismatch (mapping cardinality).** One runtime
   operation might correspond to multiple action_classes
   (composite action) OR one action_class might cover
   multiple runtime verbs (coarse gate). This is
   F3's many-to-many cardinality sharpened to a design
   constraint: any registry must handle mixed cardinality
   explicitly.
5. **Policy rail proliferation.** Multiple parallel rails
   already exist: JobContract authority dict,
   prohibited_actions tuple, tool allowlists,
   `AssistantProfile.get_allowed_tools`, workspace-scope
   gating on agent names, feature flags. Symbol Mapping must
   declare its stance: (a) UNIFIER across rails, or (b)
   BRIDGE from authority-rail to runtime-rails only leaving
   others separate. This is a scope decision that shapes
   every subsequent design.
6. **WORKSPACE_AWARE_AGENTS as identity rail.** Per Rigby
   S1270 SIGN Q4 flag: `core/epa_handlers_tools.py:3873-3909`
   is an existing symbol-gated behavior rail keyed on agent
   identifiers. It is NOT a mapping option in Option A/B/C/D
   category unless Symbol Mapping is redefined to cover
   agent-identity routing. Treat as either (a) narrowly
   out-of-scope (authority → runtime only), or (b) explicit
   future incorporation under the same lifecycle policy. This
   doc treats it as (a) — see Q8 in §10 for the open
   question.
7. **Auditability & evidence semantics.** Option E
   (evidence-only) requires defining what counts as evidence
   of an "action." Tool call record? Dispatch intent vs.
   execution completion? Side effects (deliverable created,
   message posted)? Without a definition, "enforcement is
   correct" cannot be claimed — only "enforcement ran."

**Evidence:** Rigby S1270 SIGN review Q4 answer folded into
this finding.

---

## 10. Open Questions

Genuine research questions that remain unanswered. Not
implementation tasks. Not invented answers.

**Q1 — Which mapping option should be chosen?**
§5 enumerates 5 options with tradeoffs. This research does
not rank them. Rigby SIGN review + Chris design decision
required.

**Q2 — Should the vocabulary be normalized?**
Per §2.4, the current authority vocabulary has inconsistencies
(modify_docs_files vs. modify_any_file vs.
modify_source_documents). Should a symbol-mapping design
introduce a canonicalization step (e.g., renaming to a common
convention)? Or preserve per-employee vocabulary and map
canonically only in the registry?

**Q3 — What is the migration path for existing employees?**
If Option A/B/C ships, 17 existing steps + 113 tools need
attribution updates. Big-bang vs. incremental? Warn-mode
during migration (log missing action_class declarations) vs.
enforce-mode (block missing)?

**Q4 — Should shared authority be extracted to a template?**
Per F6 in governance_authority_evolution.md, 7 strings (mostly
PROHIBITED) appear across 2+ employees. A shared template
would DRY the per-employee dicts but introduce
inheritance/override semantics that don't exist today. Is
this in scope for Symbol Mapping or a separate mission?

**Q5 — How does the runtime reach the contract from non-mission
surfaces?**
`MissionRunnerConfig.job_contract` is available inside
MissionRunner. Outside the runner (HTTP handler, Celery
callback, agent delegation), the contract must be looked up.
Which layers need the lookup? What's the caching story?

**Q6 — What is the action_class vocabulary for actions no
employee has authority over?**
Every LLM call is an action, but no employee declares a
`use_llm` authority. Should Symbol Mapping cover this
(introduce `use_llm` as universal `EXECUTE`)? Or explicitly
scope authority to a subset of actions?

**Q7 — What is the failure mode when action_class is missing?**
If Option A ships and a new step is added without declaring
`action_classes_invoked`, what happens? Warn (soft)? Block
(hard)? Passthrough (unrestricted)? The default has strong
downstream consequences.

**Q8 — How does Symbol Mapping interact with `WORKSPACE_AWARE_AGENTS`
list (core/epa_handlers_tools.py:3873-3909)?**
The workspace-aware agent list is an existing enforcement
gate that gates 20 agents by name. Should agent name binding
be part of Symbol Mapping's scope, or is it orthogonal?

**Q9 — Should evidence-only (Option E) ship first regardless
of enforcement choice?**
Option E is the most reversible and provides the audit chain
data any enforcement option (A/B/C/D) will need. Is it a
prerequisite for the other options?

**Q10 — What audit-model migration cost is acceptable?**
Options E and D both require adding `action_class` columns or
JSONField keys to audit models (`ToolCallRecord`,
`OpsRunEvent`, `LLMCallEvent`). These tables have significant
row counts (per PLATFORM_INVENTORY: user-defined Celery tasks
414; `AgentExecution` volumes UNKNOWN but non-trivial).
Migration cost estimates?

**Q11 — Is symbol mapping per-employee scoped or platform-wide?**
Per F9, the natural scope is per-employee. But if two
employees both declare `certify_mission_run` with different
levels (e.g., EXECUTE vs. RECOMMEND), should the symbol
registry be per-employee OR platform-wide with per-employee
overrides?

**Q12 — What is the smallest viable v0?**
Per mission spec: "the smallest architectural bridge." One
employee, one option, one enforcement layer? Or one option
across all employees but zero enforcement (Option E only)?
This is the scope-cutting question that a downstream mission
must answer.

---

## 11. Recommended Next Research

Based only on evidence, not preference. Three research
missions surface as candidates for the next step after this
one.

### 11.1 Option Selection Design (P0 — the immediate next step)

**Scope.** Take the 5 options from §5 and produce a design
proposal: pick one (or a hybrid), scope the v0 employee +
layer + surface, sequence the migration. Rigby SIGN review;
Chris design gate.

**Why P0.** Every downstream research question (Q1-Q12) is
gated on this decision. Without a choice, no implementation
research can start.

**Why NOT part of this doc.** This research inventories the
design space; picking within it is the next mission.

**Prerequisites.** None beyond this research doc.

**Expected outcome.** A design decision document (not a research
doc) with Chris's ratification.

### 11.2 Trust Propagation Model (P1 — was ARCHITECTURE_INDEX §5.3)

**Scope.** Once symbol mapping exists, inter-employee trust
becomes designable. Today `derive_status()` computes
per-employee trust; cross-employee is undefined.

**Why P1.** Depends on Symbol Mapping shipping AND on the
cross-employee delegation surface (per collaboration audit §5).

**Prerequisites.** Option Selection Design (§11.1).

### 11.3 Cross-plane Composition (P1)

**Scope.** Per F8: how do the four governance planes
(autonomy, authority, budget, human) compose when all are
active? Today they don't. If authority becomes enforceable,
composition questions (KillSwitch vs. JobContract, freeze vs.
EXECUTE, HAI-pending vs. EXECUTE) become operationally
relevant.

**Why P1.** Not blocking symbol mapping design, but blocking
enforcement layer design that follows.

**Prerequisites.** Option Selection Design (§11.1).

### 11.4 Explicitly NOT recommended as next research

- **Memory Architecture** (ARCHITECTURE_INDEX §5.4) — waits
  for both Symbol Mapping AND Trust Propagation.
- **Cross-Employee Scheduling** (ARCHITECTURE_INDEX §5.5) —
  same waits.
- **Mission Composition** (ARCHITECTURE_INDEX §5.6) — same
  waits.
- **Focus Mode Inventory** (governance_authority_evolution.md
  §10.8) — orthogonal to symbol mapping; can happen in
  parallel.

---

## 12. Appendix

### 12.1 Explicit answers to mission-spec Q1-Q8

**Q1 — What exactly is an authority symbol?**
A string in `JobContract.authority` dict that names a class of
runtime action (e.g., `"modify_docs_files"`,
`"open_pull_request"`, `"certify_mission_run"`). 57 unique
strings exist across 4 employees; 68 total entries. Each is
mapped to an `AuthorityLevel` value (OBSERVE / RECOMMEND /
EXECUTE / PROHIBITED). Today the strings are policy
descriptions only — no runtime side treats them as machine-
readable symbols.

**Q2 — What exactly is an action?**
Any runtime operation that has an authority-relevant
consequence. Per §3.1's 12 surfaces: a step invocation, a
tool call, a Celery task dispatch, a management command
invocation, an agent dispatch, a model write, an
OpsRunEvent emission, a Deliverable creation, an HAI
creation, an HTTP endpoint invocation, an LLM tool_call
fire, a subprocess call. Actions may correspond to zero,
one, or many authority strings.

**Q3 — Does the platform already have symbol systems?**
Yes — 22+ identifier registries per §4.1, including PA tool
names (113), Celery task names (~414), agent names (83),
mgmt command names (193), OpsRunEvent labels, TextChoices
enums, EventBus streams (8), PeriodicTask names (96), and
more. The closest existing thing to an authority-adjacent
symbol registry is `REMOVED_TOOL_ALIASES` (13 entries in
tool_dispatcher.py:210-229) — but its purpose is
deprecation redirect, not authority binding. The AuthorityLevel
enum (4 members) is the only existing enum specifically for
authority semantics.

**Q4 — Where does authority disappear today?**
Per governance_authority_evolution.md §3 (referenced) and this
doc §1 + §6: authority disappears between MissionRunner
preflight (which observes contract shape) and Step.fn
invocation (which never receives contract-derived guidance).
Between ToolDispatcher.execute and the tool handler, contract
also has no expression path. In the audit chain (post-mission),
contract is queryable but was never persisted alongside the
actions taken.

**Q5 — What is the smallest architectural bridge?**
Not answered — that's the Option Selection Design mission
(§11.1). This research enumerates 5 options (§5); the
smallest bridge is Option E (evidence-only) because it's
purely additive and provides the audit-chain foundation any
other option needs. But "smallest bridge" is a design
question, not a research question — Chris gates.

**Q6 — Which existing primitives should be reused?**
Per §8: 7 SAFE, 11 WRAPPER, 0 DO-NOT-REUSE, 0 DEPRECATED, 3
UNKNOWN. The highest-reuse candidates are `AuthorityLevel`
enum (extend or reuse), `_emit_authority_contract_event`
pattern (parallel for violation events),
`REMOVED_TOOL_ALIASES` shape (dict-keyed registry pattern),
and any of the 12 existing enforcement gates (per §6.4) as
architectural precedent.

**Q7 — Which historical failures become impossible?**
Per §7: 5 YES + 10 PARTIALLY = 15 of 23 historical incidents
(65%) would be prevented or significantly improved. The 5 YES
cases are (a) the S1264 warn-mode discovery itself, (b) the
observation-shape-only limitation, (c) zero contract-layer
gates, (d) `certify_mission_run` 3-of-4 employees, and (e)
Bug Triage authority telemetry limited to by-employee-handle.

**Q8 — What research should happen next?**
Per §11: Option Selection Design (P0) — pick from §5's 5
options, scope v0, sequence migration. This is a design
decision, not a research mission. Rigby SIGN + Chris gate.
After that (P1): Trust Propagation (blocked on Symbol
Mapping shipping) and Cross-plane Composition (blocked on
authority becoming enforceable).

### 12.2 Cross-reference

| Prior research | Relationship |
|---|---|
| `docs/EMPLOYEE_OS_PRIMITIVES.md` §2 anti-duplication matrix | This doc's §8 reuse classifications + §4.1 anti-duplication check honor the matrix |
| `docs/research/employee_os_communication_substrate_audit.md` §4.7 (messaging guard) | Referenced in §6.4 as an existing feature-flag enforcement precedent |
| `docs/research/employee_os_communication_protocol_sketch.md` §8.1 (Auditor no HAI authority) | Referenced as evidence that authority absence has design meaning (§2.5) |
| `docs/research/employee_os_collaboration_patterns.md` §10 Q11 | Symbol mapping named as the "core architectural blocker" — this doc IS that mission |
| `docs/research/governance_authority_evolution.md` §11 | Named Symbol Mapping Architecture as the P0 next research mission. This doc IS that mission. |
| `docs/research/ARCHITECTURE_INDEX.md` §5.2 | Same — Symbol Mapping named as recommended P0 next per §1.4 §11 |
| `docs/handoffs/SESSION_1264_AUTHORITY_WARN_MODE.md` | Named symbol mapping as prerequisite for enforce-mode |
| `docs/handoffs/SESSION_1269_ARCHITECTURAL_RESEARCH_LIBRARY_ARC.md` | Governance research closed, named Symbol Mapping as next |

### 12.3 Documentation drift surfaced

| Item | Source A says | Source B (runtime) says | Resolution |
|---|---|---|---|
| REMOVED_TOOL_ALIASES entry count | Sub-agent 3: 12 | Direct read of tool_dispatcher.py:210-229: 13 | Runtime wins per DOC_LIFECYCLE §2c. This doc uses 13. |
| GATEWAY_TOOLS entry count | Sub-agent 3: 23 | Direct read of tool_dispatcher.py:232-242: 22 | Runtime wins. This doc uses 22. |
| PA tool count | Sub-agent 2: 71; raw name-token grep: 119 | PLATFORM_INVENTORY: 113 tool schemas | PLATFORM_INVENTORY is the runtime anchor per DOC_LIFECYCLE §2c. This doc uses 113. Raw grep over-counts due to nested `"name"` fields in parameter schemas. |
| Management command count | Sub-agent 2: 275 | PLATFORM_INVENTORY: 193 | PLATFORM_INVENTORY wins. This doc uses 193. |
| Celery task count | Sub-agent 2: ~399 | PLATFORM_INVENTORY: 414 user-defined | PLATFORM_INVENTORY wins. This doc uses 414. |
| Bug Triage `job_contract` wired to MissionRunner? | Prior sub-agent 1 report (in governance_authority_evolution.md §12.3): initially ASPIRATIONAL, corrected to RUNTIME-VERIFIED | Direct read of `core/jobs/bug_triage.py:1169` (assumed; not re-verified in this pass) | Preserved from governance_authority_evolution.md fix; this doc treats Bug Triage as wired. |

### 12.4 Verifier-loop pass notes

**Sub-agent tasking:** 5 parallel Explore agents tasked with
inventory + classification. Explicit "no design proposals"
discipline stated in each prompt.

**Load-bearing claims spot-verified by Claude:**
- `Step` dataclass shape at `mission_runner.py:372-388` (fields
  = `name`, `fn`; no action_class attribute) ✓
- JobContract.authority shape at `jobs.py:238-250` (Rigby
  example — `dict[str, str]`, 11 entries) ✓
- AuthorityLevel enum at `jobs.py:41-52` (4 members: OBSERVE,
  RECOMMEND, EXECUTE, PROHIBITED) ✓
- REMOVED_TOOL_ALIASES at `tool_dispatcher.py:210-229` (13
  entries; sub-agent 3 undercount corrected) ✓
- GATEWAY_TOOLS at `tool_dispatcher.py:232-242` (22 entries;
  sub-agent 3 overcount corrected) ✓
- `_emit_authority_contract_event` iteration at
  `mission_runner.py:870` (`for action_class, level_value in
  authority.items():` — only counts by level, doesn't
  cross-check runtime) ✓
- In-code Symbol Mapping citation at
  `mission_runner.py:895-899` ("Enforce-mode requires future
  symbol mapping (S1264 discovery)") ✓
- Bug Triage authority telemetry step at
  `bug_triage.py:396-453` (aggregates by employee handle +
  count; no action_class in aggregation) ✓
- No `action_class` attribute in pa_tool_schemas.py (grep = 0
  matches) ✓
- Total `action_class` grep across repo = 47 hits across 12
  files, mostly docs; runtime uses limited to
  `mission_runner.py` (4) + `jobs.py` (1) + `mythology/`
  (unrelated) ✓

**Sub-agent drift corrected:**
- Sub-agent 2's "71 PA tools" → runtime anchor 113 used.
- Sub-agent 2's "275 mgmt commands" → runtime anchor 193 used.
- Sub-agent 3's "12 REMOVED_TOOL_ALIASES" → verified 13.
- Sub-agent 3's "23 GATEWAY_TOOLS" → verified 22.
- Sub-agent 4 included "Layer 6 is architecturally optimal"
  language in its report summary. This doc does not
  propagate that recommendation — §6 enumerates without
  ranking, per mission-spec discipline.

**Cross-doc consistency:**
- 68 authority entries: matches governance_authority_evolution.md
  §2.2 row 11 + this doc §2.1.
- 4 governance planes: matches governance_authority_evolution.md
  F1; referenced in this doc's §1 + §9 F8.
- 35 runtime gates: matches governance_authority_evolution.md
  §4 total; referenced in this doc's §1 + §6.4.
- Symbol Mapping as P0 next research: matches
  ARCHITECTURE_INDEX.md §5.2 + governance_authority_evolution.md
  §11.

**Self-verifier pass (one round) before finalization
identified and fixed:**
- Initially had "5 options" but only 4 substantively enumerated
  in §5. Added Option E (evidence-only) explicitly; verified
  it's distinct from Options A-D.
- Initially had §7 verdict counts inconsistent with sub-agent
  5's report. Reconciled to 5 YES + 10 PARTIALLY + 8 NO = 23
  (matches sub-agent 5 headline).
- Initially §8 SAFE list included `AuthorityLevel` but not the
  helper functions; expanded to 7 entries covering all
  authority-adjacent primitives.
- Initially §11.1 named a specific option as "recommended";
  removed per research-only discipline. Rewrote as scoping the
  Option Selection Design mission without picking.
- Confirmed no §5 option is presented as "recommended" —
  each is neutral tradeoff description.

**Status after self-verifier pass.** Publishable as draft.

**Rigby independent SIGN review (S1270 PA conversation
pa-cbcc410b32714f60):** **SIGN-with-edits**.
- Must-fix folded: §8.1 item 4 narrowed
  `_AuthorityContractMalformedError` scope to contract-shape only;
  §2.6 added parallel-vocabulary type/shape anchor with
  mission_runner.py:849-861 cite showing distinct `isinstance`
  validation for dict vs. tuple/list.
- Optional folded: I-S4 wording softened; I-S3 dual-cites F1+F3;
  §5.5 Option E has reversibility-≠-preference disclaimer.
- Q3 addition folded: §4.1 gained row 24 (AssistantProfile.get_allowed_tools).
- Q1 clarification folded: §2.4 caveat that normalization alone
  doesn't close the enforcement gap.
- Q4 blind spots folded: §9 F11 records all 7 Rigby-surfaced
  categories.
- Rigby SIGN-clean on all 5 YES incidents (I-S1 → I-S5) after
  direct source verification.
- Rigby SIGN-clean on Q6 (Symbol Mapping is the P0 blocker) and
  Q7 (no preceding research needed).
- Rigby offered a diff-based re-SIGN pass on the changed sections
  if requested; not invoked at close (edits are contained and
  the verdict is SIGN-with-edits, not NEEDS-MORE).

### 12.5 Evidence integrity notes

- Five parallel Explore sub-agents produced the source material
  for §2-§7 (authority-string enumeration, runtime-action-surface
  inventory, existing-symbol-system inventory, enforcement-
  boundary inventory, historical-failure inventory).
- No runtime state observed; research-only per mission spec.
- All "today" / "is" language describes runtime state verified
  by direct file read; all "would" / "could" language is
  research description of design space, marked as such.
- Every option in §5 explicitly labeled "HYPOTHETICAL SHAPE
  ONLY — not a design" to prevent readers from mistaking
  research description for design decision.
- No code changes made writing this doc. No files touched
  besides this one.
