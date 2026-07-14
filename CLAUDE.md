# CLAUDE - AI Session Entry Point

**Last Updated:** July 13, 2026 (Session 2781 — **N17 shipped**: small UX shortcut for the S2771 N14 close-ceremony ledger search input. When operator types a 4- or 5-digit session number, an inline "→ S{num}" pill appears on the right edge; one click promotes text-substring search to exact session-scope filter with a 5-second Undo chip protecting against destructive misclick. Frontend-only, non-ops-surface (unaffected by S2774 pause). Joint SIGN outcome: AGREE ship with V2 non-blocking regex tightening (`\d{2,5}` → `\d{4,5}` — real session numbers ≥ 1000) + V3 mitigation (Undo chip); V5 zoom-out surfaced 2 folds classified + persisted before D-verdict (smart-command-box creep = `future_trigger`; destructive clear = `same_pr_mitigatable`, mitigated same-PR). **First observed in-wild consumer of the S2780 N22 v3 ledger read surface** — Rigby dogfooded `zoom_out_tool.list` during her T1 verification to consult prior UI-scope folds. Anti-rubber-stamp gate PASS. PR #3174 merged as `2fc68b79d`. Handoff: `docs/handoffs/SESSION_2781_N17_SESSION_NUMBER_PILL_SEARCH_CHIP.md`. Ledger grew 20 → 22 rows. Eighteenth close-cycle post-PLAYBOOK-7.4.4-codification. S2771-rule streak now spans 11 sessions (S2771–S2781) with 3 F-BLOCKING DISAGREEs and 1 constitutional codification. Prior S2780 anchor: **N22 v3 shipped**: same-session discharge of the S2779 V6 fold's `future_trigger`. Trigger B ("first non-Rigby consumer of zoom_out_ledger") fired with the UI ship, and the corresponding amendment (factor-out to dedicated `zoom_out_tool` PA tool + `/api/governance/zoom-out-ledger/` REST endpoint + Chris-facing `system.sign-ledger` Workspace sub-tab with `ZoomOutLedgerSection` component) shipped in the same PR per PLAYBOOK-6.10.8 discipline. **First in-wild example of the future_trigger→amendment loop closing without a gap session.** Third F-BLOCKING DISAGREE of the S2771 streak (V1 Trigger B disposition + V3 canonical home) — resolved by SCOPE EXPANSION rather than reduction; Chris D-verdict "A: factor-out + UI" authorized expanded scope in one turn. Anti-rubber-stamp gate caught two BLOCKING design leans on T1 (6+ real tool_runs). New backend home: `core/services/td_handlers_governance.py` (`GovernanceHandlersMixin`) — establishes discrete surface for future governance-scoped tools; `ops_tool` stays focused on runtime signal. Autofill guard for `session=0` caught in live smoke, tested. Advisory posture preserved across all 3 surfaces (PA tool / REST / UI) via 3 redundant response fields + prominent UI banner + non-severity color palette. PR #3172 merged as `b16b3b981`. Handoff: `docs/handoffs/SESSION_2780_N22V3_ZOOM_OUT_TOOL_FACTOR_OUT_GOVERNANCE_UI.md`. Ledger grew 18 → 20 rows. Sixteenth close-cycle post-PLAYBOOK-7.4.4-codification. S2771-rule streak now spans 10 sessions (S2771–S2780) with 3 F-BLOCKING DISAGREEs and 1 constitutional codification. Prior S2778 anchor: **Playbook v0.7.0 MINOR ratified** — PLAYBOOK-6.10.7 + 6.10.8 codified zoom-out SIGN discipline; rule count 202 → 204; envelope `docs/research/implementation/RATIFICATION_2026-07-13_PLAYBOOK_V0_7_0.md`.)

> **Anchors (context-kit pattern):** [`docs/PLATFORM_WHAT_IT_IS.md`](docs/PLATFORM_WHAT_IT_IS.md) is the **narrative anchor** (system glossary, subsystem summaries — not a counts source). [`docs/PLATFORM_INVENTORY.md`](docs/PLATFORM_INVENTORY.md) is the **runtime/inventory anchor** and is the **sole authoritative source for system counts** (agents, spiders, models, tasks, etc.) per `DOC_LIFECYCLE.md` §2c. When any doc disagrees with PLATFORM_INVENTORY on a count, the inventory wins. Run `python manage.py verify_doc_claims --only-drift` to see which claims drift from reality.

> **Constitutional governance (Playbook v0.7.0 + Cycle 0/1):** The **Engineering Playbook v0.7.0** at `docs/ENGINEERING_PLAYBOOK.md` (ratified 2026-07-13 S2778, tag `playbook-v0.7.0`, merge commit filled at merge, **204 rules** across 11 chapters — 4 FULL: 0/1/6/10; 6 STUB: 2/3/4/5/8/9; Ch 7 **partial activation** — §7.4/§7.5/§7.6 authored with §7.4 extended at v0.6.0). v0.7.0 is the **second consecutive MINOR shipped in single-session shape**: 2 new [GR] rules — PLAYBOOK-6.10.7 (joint SIGN routings MUST include at least one open-ended zoom-out ask; "joint SIGN routing" definition inlined) + PLAYBOOK-6.10.8 (folds MUST be classified {`same_pr_actionable`/`same_pr_mitigatable`/`future_trigger`} + persisted to `logs/zoom_out_classifications.jsonl` via `record_zoom_out_concern` before D-verdict; no-folds carve-out; graceful-degradation clause for command failure). Author-side sequencing note: I-0302 three-PR pattern candidate previously proposed for PLAYBOOK-6.10.7 (RATIFICATION_2026-07-10_i0302_arc_close.md §11) re-slotted to PLAYBOOK-6.10.9 per PLAYBOOK-10.7.5 (next-unused-integer). Precedent extended at v0.7.0: **substrate dogfooding at authoring** — 4 V6 zoom-out folds classified + persisted before D-verdict, demonstrating the discipline in-wild before ratification. Corroboration streak: 7 in-wild sessions (S2771 memory-rule authoring + S2772–S2777 application, 2 F-BLOCKING DISAGREEs) + S2777 N22 substrate ship (13-row seed ledger). Amendment provenance envelope: `docs/research/implementation/RATIFICATION_2026-07-13_PLAYBOOK_V0_7_0.md` (recorded 3-turn joint SIGN §5 + V6 zoom-out folds §5.2 + Chris D-verdict §6). **Version ancestry:** v0.7.0 → v0.6.0 (playbook-v0.6.0, 2026-07-11 S2766, 1 new [GR] rule PLAYBOOK-7.4.4 — recycle-after-merge) → v0.5.0 (playbook-v0.5.0, 2026-07-11 S2753, 5 new [GR] rules for Ch 7 partial activation, deliverable `4c322f48-3d0b-4e32-8a30-15a08400f887`) → v0.4.1 (playbook-v0.4.1, 2026-07-10, informative-only §6.12 note re: capability graph refresh cadence, deliverable `bb01b377-5953-4cb3-adc5-67135367121c`) → v0.4.0 (playbook-v0.4.0, 2026-07-10, codifies CD-50 as PLAYBOOK-6.10.6, deliverable `77420585-2bd9-43bb-aa1c-74cae3354754`) → v0.3.0 (playbook-v0.3.0, 2026-07-10, codifies CD-48 + CD-49 as PLAYBOOK-6.6.14 + 6.10.5, deliverable `548d4aab-88bf-470f-9dea-b3b7400ce36e`) → v0.2.0 (playbook-v0.2.0, 2026-07-09, codifies R1/R2/R3 EOS rules as PLAYBOOK-5.2.2/2.2.2/3.2.2, deliverable `fbcfcfde-9da9-48b1-8bd8-187885382521`) → v0.1.0 (playbook-v0.1.0, 2026-07-08, inaugural, deliverable `b083c034-5aba-4dc3-9758-57eba29b4bf2`). Current workspace ratification record: `RATIFICATION_20260713_PLAYBOOK_v0_7_0` (deliverable filled at close in workspace `a9a16593-e0a4-44dc-8256-efc65d524b3c` — Architecture & Research). Session handoffs: `docs/handoffs/SESSION_2778_PLAYBOOK_V0_7_0_RATIFIED.md` (current), `docs/handoffs/SESSION_2766_PLAYBOOK_V0_6_0_RATIFIED.md`, `docs/handoffs/SESSION_2753_PLAYBOOK_V0_5_0_RATIFIED.md`, `docs/handoffs/SESSION_2752_PLAYBOOK_V0_5_STAGE_1_SHAPE_RATIFIED.md`, `docs/handoffs/SESSION_2742_PLAYBOOK_V0_4_1_RATIFIED.md`, `docs/handoffs/SESSION_2740_PLAYBOOK_V0_4_0_RATIFIED.md`, `docs/handoffs/SESSION_2727_PLAYBOOK_V0_1_0_RATIFIED.md` (inaugural). Pre-Playbook governance still applies: Cycle 0 foundational ADRs (0000/0005/0010/0020), Cycle 1 open (0100), Cycle 1A implementation ADRs (0110/0120/0130/0140/0150), and their ratification records live in the same workspace `a9a16593-e0a4-44dc-8256-efc65d524b3c`. Discover via `deliverable_tool.list workspace_id=a9a16593-e0a4-44dc-8256-efc65d524b3c show_all=true` (PA route) or `Deliverable.objects.filter(workspace_id='a9a16593-e0a4-44dc-8256-efc65d524b3c')` (ORM route). Current deployment binding: latest `MANIFEST_*` in the workspace (as of this anchor's authoring, `MANIFEST_v20260707` = `4b2a655a-35f6-48de-9db8-3afcffc80476` §8.3; consult the workspace for newer manifests). Fresh implementation-pin lifecycle documented in `tools/pa_local.sh` header comment block. Pointer stability contract: these targets — the workspace UUID, `tools/pa_local.sh`, `00-START-NEXT-SESSION.md`, `docs/ENGINEERING_PLAYBOOK.md`, `docs/canon/INDEX.md` — are stable bootstrap artifacts under this repo's convention; if any is renamed or relocated, update CLAUDE.md in the same PR.

## Working with Rigby (PA)

Claude Code MUST coordinate with Rigby (the Personal Assistant) for all decision-making, questions, and status updates. **Do not ask yes/no or approval questions in the terminal** — route them through Rigby via `python tools/pa_chat.py "message" --tools --conversation <conversation_id>`. The user (Chris) will respond via the Chat UI. Only use the terminal for questions if explicitly told to do so for a specific reason.

### Collaboration shape: Claude directs, Rigby executes, Claude verifies

The default workflow is a three-step loop:

1. **Direct** — Claude writes a concrete instruction for Rigby: action name, exact arguments, files touched, expected output shape. Not "investigate X" — "run `deliverable_tool list show_all=true workspace_id=…` and report the row count + status breakdown."
2. **Execute** — Rigby runs the work via her PA tool surface.
3. **Verify** — Claude independently confirms the result by reading the `Tool Runs (verbose)` block in her reply and cross-checking via Django ORM, `git log`, file Read, or build check. Don't trust the summary text; look at raw tool output.

**Splits by work type:**
- **Investigations, audits, deliverable edits, tool-surface queries, status checks, row counts, deliverable content sweeps** — route to Rigby; Claude verifies.
- **Code edits, PRs, deploys, git ops, repo file edits** — Claude executes (Rigby has no repo-write surface). For design judgment calls inside that work (which fields to expose, what defaults to pick, which transitions to allow), route options through Rigby BEFORE coding so the diff lands on a decision she's signed off on.
- **Post-merge behavior verification of new tools** — Rigby exercises the new surface; Claude reads the tool-output block to confirm shape + values match the spec.

**Why:** (1) Rigby is the platform's first-class interface; giving her real work exercises and improves that surface every session. (2) Claude's direct file/git reads bypass the platform — fine for verification, wrong as the default execution path. (3) Independent verification catches Rigby's known failure modes (placeholder-stall, wrong-baseline-default, premature `completed` flips) before they ship.

**Override conditions:** If Rigby is mid-tool-failure, has a confirmed conversation rotation pending, or the loop needs sub-second turnaround (live debug), Claude self-executes for speed and states the reason out loud.

### Tactical contract

- **Active conversation:** Set per session (check with Chris or Rigby)
- **Tool:** `python tools/pa_chat.py "message" --tools --conversation <id>`
- **Rigby knows:** current priorities, context, errors, and Chris's preferences
- **Rigby modes:** `global` and `workspace`. Workspace mode activates only from explicit workspace context (`workspace_id`, profile scope, or workspace-aware UI context). Do not guess.
- **Canonical PA route:** `POST /api/pa/chat/`. `/api/assistant/chat/` and `/api/v1/assistant/chat/` are compatibility-only.
- **Generated docs are not hand-edited.** Files starting with `<!-- DOC-AUTOGEN ... -->` (currently `docs/INDEX.md`, regenerated by `python manage.py build_docs_index`) must be refreshed via their command, never edited in place. `scripts/verify_repo_guardrails.py` enforces this.
- **Close the loop:** before calling work complete, verify the live path/build, update the relevant handoff, and run `python manage.py verify_doc_claims --only-drift` if docs changed.

## Quick Start

```bash
# 1. Read current context (MANDATORY)
cat 00-START-NEXT-SESSION.md

# 2. Start platform
make start && make celery

# 3. Access AI Studio
open http://localhost:8000/ai-studio/
```

## Research Library

Donkey Betz ships a canonical **Research Operating System** that
governs how Claude Code approaches every class of work in the repo
(research, design, implementation, bugs, docs, ops). Session
S1279 installed it as the default workflow — every future session
executes it automatically.

### Where to start

| For… | Read this first |
|------|-----------------|
| Any new session, regardless of intent | [`docs/research/process/RESEARCH_OPERATING_SYSTEM.md`](docs/research/process/RESEARCH_OPERATING_SYSTEM.md) §0–§5 (bootstrap + request classification) |
| Starting a research group | [`docs/research/DOMAIN_RESEARCH_PLAYBOOK.md`](docs/research/DOMAIN_RESEARCH_PLAYBOOK.md) (research-class specialization of the OS) |
| Navigating the library | [`docs/research/ARCHITECTURE_INDEX.md`](docs/research/ARCHITECTURE_INDEX.md) §7 decision matrix |
| Knowing what's in flight | [`docs/research/OPEN_ARCS.md`](docs/research/OPEN_ARCS.md) — machine-readable arc manifest |
| Understanding library history | ARCHITECTURE_INDEX §8 timeline |

### The Research OS in one sentence

Bootstrap → classify request into 1 of 11 classes → run the
matching startup contract → execute → close per §14 completion
contract. Chris ratifies decisions; Rigby SIGN pressure-tests
research; the OS makes everything in between deterministic.

### Research group short commands

Chris opens work with commands like:

- `Start research group 1400: Revenue` — opens a new arc parent
- `Continue research group 1300: <child slot>` — advances a child
- `Close research group 1300` — opens the canonical summary (`xx99`)

### How groups are organized

```
docs/research/
├── ARCHITECTURE_INDEX.md            # navigation (v12)
├── DOMAIN_RESEARCH_PLAYBOOK.md      # research-class contract (v2)
├── OPEN_ARCS.md                     # cross-arc live manifest
├── process/                         # the OS + startup introspection
├── platform/                        # whole-platform-scope research
└── domains/<slug>/                  # per-domain arcs
    ├── NN00_<slug>_domain_scoping.md   # parent
    ├── NN01–NN98_<slug>_<topic>_audit.md   # children
    └── NN99_<slug>_canonical_summary.md    # summary
```

Legacy S1268–S1275 arc docs live at `docs/research/` top-level;
they are grandfathered in place.

### Startup checklist (universal, ~5 min)

Every session runs these steps regardless of the requested work:

1. `context-kit orient` — source-of-truth chain, latest handoff.
2. Absorb this `CLAUDE.md` and `MEMORY.md` (both auto-injected).
3. Read `00-START-NEXT-SESSION.md` in full.
4. Read Research OS §0–§5 (skim §6–§9 headings) if the request
   might touch research, docs, or governance.
5. Record repo state (branch + SHA + `git status`).
6. Note request context (change vs explain; explicit constraints;
   for bugs: repro path).
7. Classify the request via OS §5 router → load the matching §8
   startup contract.
8. If PA calls will happen: verify `service_context: local` via
   `platform_config_tool overview`.

Full spec: OS §4 Bootstrap Sequence.

### Don't duplicate

CLAUDE.md points into the Research OS. Do NOT restate OS rules,
playbook contracts, INDEX content, or OPEN_ARCS rows here. If the
OS changes, this section stays stable — the pointers do the work.

## System Stats

> Verified 2026-04-20 against code. See PLATFORM_WHAT_IT_IS.md for full breakdown + glossary.

### Live Counts (auto-refreshed)

The block below is regenerated by `python manage.py refresh_doc_inventory_blocks` from `gather_inventory()`. To update, run that command. Do not hand-edit between the markers.

<!-- @inventory-block:platform-stats -->
| Component | Live Count |
|---|---|
| **Agents** | 83 agents in AGENT_MAP (74 enabled, 9 rerouted, 0 blocked); 90 rows in Agent table. |
| **Spiders** | 80 spiders across 41 categories (80 working, 0 placeholder) |
| **Services** | 112 `*Service` classes across 362 files in core/services/ |
| **Celery Tasks** | 415 user-defined Celery tasks (excludes celery.* internals) |
| **Beat Schedule** | 92 enabled + 5 disabled = 97 PeriodicTask rows |
| **PA Tools** | 113 tool schemas + 156 registered handlers; 8 enrichment services |
| **Database Models** | 585 concrete models across 23 apps |
| **Discord** | 96 @*.command decorators, 48 @app_commands.command, 25 Cog classes in discord_bot.py |
| **Body Systems** | 9 body systems monitored by run_all_systems_scan |
| **LLM Providers** | 6 providers registered in LLMProviderRegistry |
| **Signal Pattern Types** | 10 SignalCluster pattern types, MIN_CLUSTER_SIZE=3 |
| **Frontend** | 61 routes in App.tsx, 5 workspace primary tabs, 9 betting dashboard tabs |

_Auto-generated by `refresh_doc_inventory_blocks` from `gather_inventory()`. Do not hand-edit between markers._
<!-- @inventory-block:end -->

### Detailed Breakdown

| Component | Count | Details |
|-----------|-------|---------|
| **Agents (AGENT_MAP)** | _see autoblock above_ | DB persona rows are tracked separately; provenance-tracked and workspace-aware subsets documented elsewhere |
| **Spiders** | _see autoblock above_ | Across categories; ~1.14M SpiderItemHash rows tracked |
| **PA Tools (Rigby)** | _see autoblock above_ | GPT-5.2 function calling, 6 gateway tools, 8 enrichment services, dedicated `pa` Celery queue |
| **LLM Providers** | 6 | OpenAI, Anthropic, Together AI, Ollama, DeepSeek, Gemini |
| **Database Models** | _see autoblock above_ | Concrete Django models across apps (PostgreSQL + pgvector) |
| **Celery Tasks** | _see autoblock above_ | User-defined `@task` + `PeriodicTask` rows; sync/bootstrap commands materialize or repair selected rows from `core/celery.py` into `django-celery-beat` |
| **Procfile entries** | 11 | release + web + 7 celery workers (worker/pa/content/long-running/long-running-2/broadcast/beat) + code-worker + resolve-node |
| **Services** | ~351 | Signal aggregation, content scoring, deliberation, enrichment, advisors |
| **Body Systems** | 9 | HEART, LUNGS, CIRCULATORY, SPINE, IMMUNE, DIGESTIVE, MUSCULAR, BRAIN, SKIN (+ BodyCoordinator autonomic reflex layer) |
| **Advisors** | 30 | 30 functional domain specialists across investment strategy, AI/ML, content/creator economy, sports analytics, negotiation, healthcare, cybersecurity, education, operations, IP counsel, leadership coaching, regulatory compliance. Identities are functional (no real-person names). See [`docs/ADVISOR_AUDIT.md`](docs/ADVISOR_AUDIT.md). |
| **Signal pattern types** | 10 | demand_spike, trend_emergence, sentiment_shift, opportunity_window, knowledge_gap, competitive_signal, market_movement, skill_demand, content_gap, user_need |
| **Frontend** | 61 routes | `<Route>` entries in `frontend/src/App.tsx`; Command Center + 5-tab workspace; 9-tab betting dashboard |
| **Discord bot** | 96 commands | 48 slash (`@app_commands.command`) + 48 prefix (`@*.command`) across 25 Cog classes in `core/services/discord_bot.py` (11,676 lines). See [`docs/DISCORD_AUDIT.md`](docs/DISCORD_AUDIT.md). |
| **Employees (Employee OS)** | 3 | Documentation Manager (Rigby) + Platform Auditor + Chief of Staff. Frozen `AIEmployee` + `JobContract` in `core/employees/jobs.py`; orchestrated by `MissionRunner`; audit via `OpsRun(domain='mission')` + `OpsRunEvent`. Reuse [`EMPLOYEE_OS_PRIMITIVES.md`](docs/EMPLOYEE_OS_PRIMITIVES.md) primitives — do not invent parallel models, tools, or admin UIs. |

## Project Structure

### Key Directories
- `core/agents/` — 83 AGENT_MAP agent classes with learning hooks; BaseAgent is 5,575 lines
- `core/services/` — ~351 service modules
- `ai_core/spiders/` — 80 registered spiders
- `docs/topics/` — Embedding-optimized subsystem docs (current state)
- `docs/handoffs/` — 676 session handoff documents (build history)

### Key Files
| File | Purpose |
|------|---------|
| `00-START-NEXT-SESSION.md` | Current session priorities |
| `docs/PLATFORM_WHAT_IT_IS.md` | Platform narrative + glossary (context-kit narrative anchor — NOT a counts source) |
| `docs/PLATFORM_INVENTORY.md` | Runtime-derived inventory (context-kit inventory anchor — authoritative for counts, regenerable) |
| `core/agent_router.py` | Deterministic agent routing (AGENT_MAP lives here) |
| `core/tasks.py` | Celery background tasks |
| `core/conversation_orchestrator.py` | Multi-agent conversations |
| `core/services/unified_pa_entrypoint.py` | PA: GPT-5.2 function calling agentic loop, enrichment pipeline |
| `core/services/tool_dispatcher.py` | PA: 152 tool handlers |
| `core/services/pa_tool_schemas.py` | PA: 109 OpenAI function-calling tool schemas |
| `core/services/signal_aggregation_service.py` | Signal clustering & auto-topic generation |
| `core/services/content_scoring_service.py` | Rule-based reach/intent/replicability scoring |
| `core/services/content_deliberation_runner.py` | v2 content pipeline |
| `core/services/doc_claim_verification.py` | Doc-vs-reality verifier (Session 1099) |
| `core/epa_handlers_tools.py` | WORKSPACE_AWARE_AGENTS constant (20 agents) |
| `core/employees/jobs.py` | Employee OS: `AIEmployee` + `JobContract` frozen-dataclass registry; `_EMPLOYEES_BY_HANDLE` + `_JOBS_BY_EMPLOYEE` |
| `core/employees/mission_runner.py` | Employee OS: MissionRunner orchestrator (preflight → steps → postflight → verdict → escalation) |
| `core/models_ops_runs.py` | Employee OS: `OpsRun(domain='mission')` + `OpsRunEvent` audit rows (no separate MissionRun model) |
| `frontend/src/pages/WorkspacePageNew.tsx` | 5-tab modular workspace |
| `frontend/src/pages/workspace/tabs/FilesTab.tsx` | Workspace file preview, edit/save, and history |
| `frontend/src/pages/CommandCenterPage.tsx` | Command Center with PA chat |

## Subsystem Documentation

Detailed current-state docs for each subsystem (designed for embedding). **Some per-topic stats tables drift from reality — for authoritative counts see [`PLATFORM_INVENTORY.md`](docs/PLATFORM_INVENTORY.md) (per `DOC_LIFECYCLE.md` §2c).**

| Topic File | Covers |
|------------|--------|
| [docs/topics/personal-assistant.md](docs/topics/personal-assistant.md) | PA GPT-5.2 function calling, tools, enrichment, async flow |
| [docs/topics/content-pipeline.md](docs/topics/content-pipeline.md) | ClaimsPack, deliberation, reviewers, PublishGate |
| [docs/topics/agent-system.md](docs/topics/agent-system.md) | AGENT_MAP agents, routing, ToolCallRecord, provenance |
| [docs/topics/initiative-pipeline.md](docs/topics/initiative-pipeline.md) | Dreams, 5-stage pipeline, signals, action items |
| [docs/topics/celery-workers.md](docs/topics/celery-workers.md) | Worker processes, queues, memory management, observability |
| [docs/topics/body-systems.md](docs/topics/body-systems.md) | 9 health systems, coordinator, scoring |
| [docs/topics/spider-network.md](docs/topics/spider-network.md) | Spiders, data types, signal aggregation |
| [docs/topics/stock-intelligence.md](docs/topics/stock-intelligence.md) | Dashboard, briefs, alerts, predictions |
| [docs/topics/frontend.md](docs/topics/frontend.md) | Workspace tabs, PA integration, telemetry |
| [docs/topics/infrastructure.md](docs/topics/infrastructure.md) | Django, Railway, Redis, PostgreSQL |
| [docs/topics/employee-os.md](docs/topics/employee-os.md) | Employee OS: MissionRunner orchestration, `AIEmployee` + `JobContract` primitives, OpsRun audit; 3 production employees (Documentation Manager, Platform Auditor, Chief of Staff). Canonical primitives + anti-duplication rules in [`EMPLOYEE_OS_PRIMITIVES.md`](docs/EMPLOYEE_OS_PRIMITIVES.md). |

## GPT-5-mini Configuration

```python
# CORRECT - Reasoning model has different parameters
response = client.chat.completions.create(
    model="gpt-5-mini",
    messages=messages,
    max_completion_tokens=6000  # NOT max_tokens, NO temperature
)
```

## Troubleshooting

```bash
# Full restart
pkill -f daphne; pkill -f redis; pkill -f celery
rm -f .daphne.pid .celery.pid .celery-beat.pid
make start && make celery

# macOS Celery SIGSEGV fix
OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES celery -A core worker -l INFO --pool=solo
```

## Reference Documentation

| Doc | Purpose |
|-----|---------|
| [PLATFORM_WHAT_IT_IS.md](docs/PLATFORM_WHAT_IT_IS.md) | **Start here** for narrative + glossary (context-kit narrative anchor — not a counts source) |
| [PLATFORM_INVENTORY.md](docs/PLATFORM_INVENTORY.md) | Runtime-derived inventory (context-kit inventory anchor — sole authoritative counts, regenerable via `generate_platform_inventory`) |
| [ARCHITECTURE.md](docs/ARCHITECTURE.md) | System architecture |
| [AGENTS.md](docs/AGENTS.md) | Agent documentation (stats may drift — see PLATFORM_INVENTORY for counts) |
| [SPIDERS.md](docs/SPIDERS.md) | Spider network (stats may drift — see PLATFORM_INVENTORY for counts) |
| [SERVICES.md](docs/SERVICES.md) | Services layer |
| [DATABASE_MODEL_REFERENCE.md](docs/DATABASE_MODEL_REFERENCE.md) | Which DB table for what |
| [API_PATH_POLICY.md](docs/API_PATH_POLICY.md) | API path conventions |
| [DREAM_INITIATIVE_WORKFLOW.md](docs/DREAM_INITIATIVE_WORKFLOW.md) | Initiative 5-stage pipeline |
| [DISCORD_INTEGRATION.md](docs/DISCORD_INTEGRATION.md) | Discord bot: 144 commands across 25 Cogs |
| [demo_mode.md](docs/demo_mode.md) | Resolve demo mode guardrails, demo clip generation |
| [governance_redesign.md](docs/governance_redesign.md) | Governance UX redesign spec, 7 implementation tickets |
| [EMPLOYEE_OS_PRIMITIVES.md](docs/EMPLOYEE_OS_PRIMITIVES.md) | **Canonical Employee OS primitives + anti-duplication matrix + lifecycle + warnings + quick-start. Read before adding a new employee or job.** |

**Documentation Index:** Run `python manage.py build_docs_index` to regenerate `docs/INDEX.md`
**Doc verifier:** Run `python manage.py verify_doc_claims --only-drift` to see which claims drift from reality

---

**Always read `00-START-NEXT-SESSION.md` first - it has the current priorities!**
