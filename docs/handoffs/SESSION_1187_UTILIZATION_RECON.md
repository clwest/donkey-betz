# Session 1187 — Utilization Recon: Agents × Spiders × Knowledge E2E

**Status:** Recon-only session. 7 deliverables filed in Local QA workspace. No code changes shipped. Remediation work explicitly deferred to a future session per Chris's scope.
**Date:** 2026-06-21
**Pinned conversation:** `pa-10df024c0bd8` (carried from Sessions 1184-1186; health was 60-75/100 at session close — likely rotate for Session 1188).
**Driving artifact:** Master tracking deliverable `88952c54-a4a4-47e8-9fe1-85b3d747be03` in Local QA workspace.
**Prior session:** [`SESSION_1186_PR_C_BUCKET_4_CELERY_TASKS.md`](./SESSION_1186_PR_C_BUCKET_4_CELERY_TASKS.md) (PR #2376 bucket 4 close + #2378 docs close).

## TL;DR

Pivoted off provenance remediation onto a strategic recon: Chris asked *"go through all of the Agents, right now we have them but they aren't really doing anything. We also need to verify that the spiders are actually pulling in data to feed the system."* Routed scope through Rigby (added axis D — output utilization — to my proposed A/A2/B/B2/C). Filed 7 deliverables in Local QA with verifier commands per AC item, matching the `verify_doc_claims` alignment contract Chris valued.

**The recon answer inverted the framing.** Agents are dormant, not wild. 67% of AGENT_MAP entries (56/83) have ZERO dispatches in 30d. Spiders are the opposite — they pulled 198,678 items in 30d across 78 spiders. The break is in the **wiring layer**: `SpiderContextBuilder.AGENT_SPIDER_MAPPINGS` (in-code dict, 51 agents) doesn't route any huggingface/ai_ml data anywhere, and the parallel `AgentSpiderConnection` table (DB, 55 rows) is dead code in the read path. Confirmed at runtime: 0 of 92 recent dispatches reference huggingface despite 331 fully-embedded SpiderData rows being available.

## What landed (this session)

**Zero code changes on main.** All output is deliverables in Local QA workspace.

### Master tracking deliverable

`88952c54-a4a4-47e8-9fe1-85b3d747be03` — Session 1187 Utilization Recon — Master Tracking. AC checklist per axis + verifier commands + child deliverable_ids + final headline summary appended on close.

### 7 child deliverables (Local QA workspace)

| # | Axis | deliverable_id | Status |
|---|---|---|---|
| 1 | A — Agent Utilization (Rigby's axis, data via my SQL) | `3fe30a8e-8c53-4b59-ba3c-ebd61d1ad7ea` | ✓ complete |
| 2 | A2 — Agent Intent vs Reality | `bb9d7437-3cb5-45c8-9d60-db875c4a98f6` | ✓ complete |
| 3 | B — Spider Utilization | `623dcf5c-6c15-44af-8b20-6456959712f2` | ◐ B.3 (embedding coverage) + B.4 (query traffic) aspirational |
| 4 | B2 — Spider→Agent Linkage | `13c6bd32-67eb-4d89-a7d7-3935e4fa65c5` | ✓ complete |
| 5 | **C — Huggingface E2E trace** | `1f548d38-8971-4780-a798-03e79399f322` | **✓ complete — 3 break points identified** |
| 6 | D — Output Utilization | `518a77c5-13a9-4d09-a763-f15db39a0369` | ◐ D.3 (wagers) + D.5 (outreach) aspirational |
| 7 | Missing PA Tools (running list per Chris's instruction) | `13032820-1f36-4a1c-8843-6a9d53653405` | ✓ filed for future build session |

## Headline findings

### Agents are dormant, not wild

- **67% of AGENT_MAP entries (56/83) have ZERO dispatches in 30 days** (Local DB)
- **9 Hot** (1d): AudioAgent, COOAgent, ContentWriterAgent, EditorAgent, ImageAgent, ResearchAgent, SystemIntelligenceAgent, ThinkingAgent, WorkflowAgent
- **0 Warm** — binary cliff between Hot and Cold
- **18 Cold** — most from a bootstrap burst on 2026-06-13/14 (10 agents fired exactly once on those dates then never again)
- All specialized verticals (sports betting, blockchain, stock analysis) are zombie

### Spiders are cranking

- **78 spiders in SpiderItemHash, 198,678 total rows in 30d**
- Top: kalshi 154,942 / 30d (78% of all volume), legislation 9,920, huggingface 6,620, adzuna 6,018, sports_news 2,775
- ~50+ spiders Hot (>100 items/7d); essentially zero Zombie

### The wiring gap is the root finding

- **Only 19/83 agents (23%) declare any AgentSpiderConnection** linkage
- Linkage is at **SpiderCategory level** (12 of 41 categories wired) — too coarse
- **Only 26% of recent dispatches (23/87) carry spider-related context** in input_data
- **3 distinct break points** identified via huggingface E2E trace:
  1. `SpiderContextBuilder.build_context_for_agent` queries category KEY STRINGS (`'tech'`, `'creative'`) that don't match `SpiderCategory.name` (`'AI & Creative Tools'`) or `data_type` (`'ai_ml'`)
  2. `AgentSpiderConnection` table is **dead code in the read path** — runtime builder doesn't consult it
  3. `SpiderContextBuilder.AGENT_SPIDER_MAPPINGS` (in-code, 51 agents) is the actual driver, but 32/83 AGENT_MAP entries are missing including 3 of 9 Hot agents, and **zero** entries route huggingface/ai_ml data anywhere

### Outputs are 90% concentrated in 8 agents

ResearchAgent (50), Rigby (47), ContentWriterAgent (17), NewsletterTool (6), COOAgent (6), CTOAgent (5), ThinkingAgent (5), DevOpsAgent (4). 75/83 AGENT_MAP agents produced ZERO Deliverables in 30d.

### Missing PA tools (filed for future build session)

6 gaps Rigby hit during the recon, blocking her from independently running this utilization audit going forward:
1. Per-row AgentExecution telemetry (success_rate / latency / last_seen)
2. Paginated spider list
3. 30d/90d spider counts
4. Per-spider embedding-index coverage
5. Spider-data query traffic counter
6. Cross-workspace deliverables enumeration

Recommended build order in deliverable `13032820-...`.

## How the work split happened (collaboration log)

| Axis | Owner | How it ran |
|---|---|---|
| Master tracking | Claude drafted skeleton (per `feedback_rigby_deliverable_content.md`); Rigby created the deliverable | Verbatim handoff — no placeholder content |
| A telemetry | Rigby pulled via `ops_tool.noise_metrics` (partial), then surfaced the 6-tool blocker → Claude ran SQL via Django ORM | Honest "I can't do this with current tools" per `feedback_corpus_walks_surface_mechanism_drift.md` |
| A2, B2, C | Claude code-side | AST introspection + Django ORM probes + manage.py shell |
| B telemetry | Same hybrid as A (Rigby spider_status_tool partial + Claude SQL) | |
| D telemetry | Same hybrid | |
| All filing | Claude wrote markdown contents to /tmp + Python script called `create_deliverable` factory directly (skipped PA round-trip for speed) | Used `trigger_source='direct'` for clean provenance synthesis |

**Mid-session structural finding (key collaboration moment):** before implementing the A2 cross-reference, Claude discovered that `AgentExecution.owner_agent` is empty in ~75% of rows in local DB; had to re-query by `agent.name` FK instead. Surfaced the schema-drift finding rather than silently routing around it.

**Second mid-session structural finding:** when implementing bucket 4 callsite B in Session 1186, Claude discovered the dedupe-collision drift between agent's internal `_save_to_deliverable` and the task's external `create_deliverable` — surfaced to Rigby for the B.2 design call rather than silently bridging. Same pattern applied here.

## Open invariants now load-bearing

1. **Master tracking deliverable + 6 child deliverables are the snapshot.** Reviewable as the source of truth for what the platform is actually doing. Re-runnable via the scripts referenced inside each deliverable (`/tmp/recon_proper.py`, `/tmp/a2_agent_introspect.py`, `/tmp/c_trace_huggingface.py`).
2. **Recon-only contract held.** No code changes in this session. Remediation is a separate session.
3. **`SpiderContextBuilder.AGENT_SPIDER_MAPPINGS` is the actual driver of spider→agent context injection.** Not `AgentSpiderConnection`. Any future remediation MUST account for this.

## What's still open (Session 1188)

### The 4-item remediation queue (from C trace)

Out-of-scope for the recon but explicitly named for prioritization:

1. **Unify the spider→agent routing source of truth.** Pick either `AgentSpiderConnection` (DB) or `AGENT_SPIDER_MAPPINGS` (code) and delete the other. Currently both exist; only the in-code one is read.
2. **Bridge the category vocabulary.** `SpiderCategory.name` ("AI & Creative Tools") vs builder query keys (`'tech'`, `'creative'`) — pick one taxonomy and map cleanly.
3. **Add the missing Hot agents to AGENT_SPIDER_MAPPINGS.** ImageAgent, ResearchAgent, ThinkingAgent, AudioAgent, EditorAgent, COOAgent, ContentWriterAgent, SystemIntelligenceAgent, WorkflowAgent.
4. **Audit the orphan spiders.** ~60 actionable spiders with no consumer in AGENT_SPIDER_MAPPINGS — either wire them or stop crawling (waste of compute).

### Building Rigby's missing PA tools (deliverable `13032820-...`)

6 tools enumerated with proposed signatures. Recommended build order:
1. `agent_telemetry_tool.utilization` (biggest unblock — covers A.3/A.4/A.5)
2. `spider_status_tool` v2 (paginated + 30d/90d window)
3. `deliverable_telemetry_tool.outputs` (cross-workspace)
4. `spider_status_tool.embedding_coverage` (requires schema work)
5. `spider_status_tool.query_traffic` (requires schema + instrumentation)

### Adjacent investigations surfaced

- **`MarketingStrategyAgent` is the only agent inheriting `execute()` from BaseAgent** — likely broken/abandoned. Worth a 5-minute look.
- **`AgentExecution.owner_agent` is empty in ~75% of local rows.** Schema-drift question: was this a Session-1184 field that's not being populated correctly anywhere? Cross-reference with provenance work to confirm.
- **`item_title='Unknown'` on huggingface SpiderItemHash rows** — cosmetic but suggests the spider isn't extracting a title from the huggingface API response.
- **ImageAgent + AudioAgent dispatch but produce 0 Deliverables** — they write to other tables (Image/MediaAsset/etc.). D axis didn't cover those; partial blind spot.

## Verifier scripts (kept in /tmp, NOT committed — by design)

All recon scripts live in `/tmp/`. They're re-runnable but workspace-private — the deliverables hold the captured results, not the scripts. To re-verify any claim:

| Verifier | What it checks |
|---|---|
| `/tmp/recon_proper.py` | Axes A + B + B2 + D — full SQL queries against AgentExecution / SpiderItemHash / AgentSpiderConnection / Deliverable / SelfBlog / SignalCluster |
| `/tmp/a2_agent_introspect.py` | Axis A2 — AGENT_MAP class introspection (docstrings, LLM signals, label-only, clones) |
| `/tmp/c_trace_huggingface.py` | Axis C — E2E huggingface trace through all 8 steps |
| Inline `manage.py shell` probes | C trace break points #1, #2, #3 (see C deliverable § Verifier) |

If a future session wants to re-run these against production DB, swap `USE_PGBOUNCER=0` for the prod env vars.

## Memory rules in play

- `feedback_no_fluff_verify_truth.md` — every claim has a runtime verifier; aspirational items explicitly marked
- `feedback_corpus_walks_surface_mechanism_drift.md` — surfaced the dedupe collision (in 1186) and the AGENT_SPIDER_MAPPINGS-vs-AgentSpiderConnection split (in this session) instead of bridging
- `feedback_rigby_deliverable_content.md` — Claude drafted all 7 deliverable contents; Rigby's role was create + ack
- `feedback_deliverable_workspace.md` — all 7 deliverables assigned to Local QA workspace
- `feedback_rigby_scope.md` — Rigby ran what her tools could do, flagged the 6 gaps for Chris's "save for later" instruction
- `feedback_triage_decision_card_pattern.md` — proposed scope card to Rigby with leans before kicking off

## Memory updates

No new memories added this session. Existing rules covered every collaboration moment cleanly.

## Watch checklist for Session 1188 first 30 minutes

1. Disk + swap (per `00-START` READ THIS SECOND): `df -h /System/Volumes/Data`, `sysctl vm.swapusage`
2. `tools/pa_local.sh "platform_config_tool overview"` → confirm `service_context: local`
3. `session_tool health_check` on `pa-10df024c0bd8` — at 60-75/100 at Session 1187 close; will likely need rotation to fresh Session 1188 thread
4. `gh pr list --author @me --state open` — should be empty (all 11 Sessions 1185+1186 PRs merged + Session 1187 was recon-only)
5. Read master tracking deliverable `88952c54-...` for the full snapshot before choosing this session's work
6. Pick a slice of the remediation queue OR start building Rigby's missing PA tools — both are warranted

## Stats

- 0 PRs opened (recon-only)
- 7 deliverables filed in Local QA workspace (~120kB total content)
- 0 commits on main (this docs PR is the only commit landing for the session)
- 0 new memories
- 4 verifier scripts kept in `/tmp/` for re-run
- 1 Rigby blocker → routed via "X" hybrid path (Claude runs SQL, Rigby composes)
- 3 distinct spider→agent wiring break points identified for next session's work
