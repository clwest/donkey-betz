---
title: "Session 1117 — local-portfolio-grounding vision shipped: Rigby corpus + fleet network + engine bridge"
date: 2026-05-21
status: active
session: 1117
originating_session: 1117
previous_handoff: SESSION_1116_PART_2_INTEGRATIONS_AND_CHANNELS.md
provenance_confidence: HIGH
provenance_note: Hand-authored handoff. Cited by Session 1158 narratives M (Fleet Integration milestone 1) + N (24/7 Global AI strategy milestone 4) + O (Spokesperson + Character OS milestone 3) — first proof case for the "u-d-b is brain bridge for laptop-local fleet" pattern; corpus + fleet-net + consult_engine bridge shipped end-to-end.
---

# Session 1117 — local-portfolio-grounding vision shipped: Rigby corpus + fleet network + engine bridge

> **Read this if** you need to understand how Rigby-on-Character-OS got
> wired to u-d-b's PA, what the new `fleet-net` Docker network is for,
> or where the 24/7 spokesperson corpus lives in Character OS now.
> Closes the headline project Chris flagged at end of Session 1116:
> the local-only portfolio + Character OS Rigby grounding vision.

## TL;DR

Three slices landed end-to-end in one session, all in mock-or-cheap mode:

1. **Slice 1 — Rigby corpus ingest.** The just-shipped
   `docs/spokesperson/` corpus from u-d-b (9 markdown chunks, 24/7
   Global AI voice) is now ingested as KnowledgeDocuments in Rigby's
   Character OS workspace, M2M-bound to her, with real OpenAI
   embeddings (`text-embedding-3-small`, $0.0002 total spend).

2. **Slice 2 — Fleet network anchor.** `fleet-net` external Docker
   network exists with all four data containers attached. Manifest
   doc at `/Users/donkeyking/development/infra/README.md` codifies
   the convention. Future fleet apps can `docker network connect`
   and reach `unified-postgres`, `character_os_postgres`, etc. by
   stable hostname.

3. **Slice 3 — `consult_engine` bridge.** New realtime tool on
   Character OS that HTTP-POSTs to u-d-b's `/api/pa/chat/`. End-to-end
   tested through the live Runway realtime UI: Chris talked to Rigby,
   she invoked `consult_engine` with "What is currently running on
   the engine?", u-d-b's deeper Rigby answered in 9.59 s via GPT-5.2.
   The vision pointer in
   [`memory/project_local_portfolio_rigby_grounding.md`](../../../.claude/projects/-Users-donkeyking-development-unified-donkey-betz/memory/project_local_portfolio_rigby_grounding.md)
   is now first-pass realised.

Total OpenAI spend tonight: **~$0.03**.

## What shipped (artifacts)

### Character OS (`character-os/`)

| Path | Change | Purpose |
|---|---|---|
| `shell/apps/realtime/tools/consult_engine.py` | NEW | The bridge tool — HTTP POST to u-d-b PA + poll for result. Under the 500-char description cap (failing-loud after one over-cap miss). |
| `shell/apps/realtime/tools/__init__.py` | edit | Import `consult_engine` to trigger registry side-effect. |
| `scripts/ingest-udb-spokesperson-corpus.py` | NEW | Idempotent ingester — reads u-d-b `docs/spokesperson/*.md`, content-hash-deduped, binds to a target Spokesperson. |
| `.env` | edit | Added `UDB_PA_API_URL` + `UDB_PA_API_TOKEN` for the bridge. |

### Top-level fleet (`/Users/donkeyking/development/infra/`)

| Path | Change | Purpose |
|---|---|---|
| `docker-compose.yml` | NEW | Declares `fleet-net` as external. No services — anchor only. |
| `README.md` | NEW | Network convention, host-port policy, when-to-grow guidance, **Docker Desktop multi-network host-port caveat** (hit twice tonight). |

### u-d-b (`unified-donkey-betz/`)

| Path | Change | Purpose |
|---|---|---|
| (DB only) `chat_conversations` | manual ALTER | Added 6 columns to unblock PA chat: `platform`, `discord_user_id`, `discord_channel_id`, `discord_guild_id`, `session_title`, `session_active`. Discord_* are nullable (matches model). Session ones are NOT NULL with defaults. **No migration committed yet** — code-model drift remains for a future migration pass. |
| `docs/handoffs/SESSION_1117_*.md` | NEW (this file) | Session record. |

## Concept refresh — what "the brain" actually is

Mid-session question from Chris: "How do we get the brain from u-d-b to Character OS?"

Honest framing: u-d-b's "brain" has four layers, and they need different bridges.

| Layer | u-d-b shape | Character OS shape | Bridge built tonight |
|---|---|---|---|
| **Knowledge** | Documents + pgvector | KnowledgeDocument + chunks | ✓ Slice 1 — one-direction static corpus copy |
| **Tools** | 101 PA tool schemas, 166 handlers | Realtime tools | ✓ Slice 3 — `consult_engine` is the first |
| **Agents** | 83 specialised agents in AGENT_MAP | (none yet) | ⏳ Future — call AGENT_MAP via PA, eventually direct |
| **Live signals** | Spider network, signal clusters, body systems | (none yet) | ⏳ Future — likely via new realtime tools or scheduled grounding-doc refresh |

The bridge architecture decision: **u-d-b stays put as the engine; Character OS becomes a face for it.** Aligns with the public taxonomy
([`docs/24_7_GLOBAL_AI_APP_ATLAS.md`](../24_7_GLOBAL_AI_APP_ATLAS.md))
where u-d-b is "the engine, not a product."

## Slice-by-slice detail

### Slice 1 — Rigby corpus ingest

**Starting state**: Chris had created a Rigby Spokesperson
(`d3d0fb14-193e-4c4c-88d1-acae9af25bb5`) in Character OS's
admins-workspace (`f4f2aa20-e2e2-4ae2-85a0-abacd8bea231`). The
workspace already had 36 KnowledgeDocuments seeded earlier
(charos/CK/MF/CC corpus from Sessions 209+). The new
`docs/spokesperson/` corpus that landed in u-d-b commit `a68eb8f1`
was NOT ingested.

**What I did**: Wrote
[`character-os/scripts/ingest-udb-spokesperson-corpus.py`](../../character-os/scripts/ingest-udb-spokesperson-corpus.py)
following the existing `upload-context-kit-demo-grounding.py`
pattern. The script reads each markdown file, calls
`apps.embeddings.ingestion.ingest_text` with the workspace + Rigby
M2M binding, then synchronously embeds via
`apps.embeddings.tasks.embed_document`.

**Outcome**:
- 9 new `KnowledgeDocument` rows (titles prefixed `24/7 Global AI —`)
- 55 chunks total (`KnowledgeChunk` rows)
- Real OpenAI embeddings, $0.0002 spend
- M2M to Rigby; she now has 45 docs bound (up from 36)

**Bug surfaced + already fixed in a parallel session**:

The mock/real embedding cache collision (mock vectors getting served
on subsequent real-mode calls because the cache key didn't namespace
by mode) was independently caught and fixed by a parallel Character
OS Claude Code session — see character-os commit `9c10b57
fix(embeddings): mock-mode bypasses cache to prevent real-mode
poisoning`. My session worked around it by manually
`cache.delete_many()`-ing the 55 affected keys before the real-mode
re-embed. After their fix lands locally, the workaround is no longer
needed for future re-ingests.

### Slice 2 — Fleet network

**Motivation**: prerequisite for cross-app addressing. Without
stable hostnames, every cross-app call hardcodes a host port that
can shift when collisions are resolved.

**What I did**:

```bash
docker network create fleet-net
docker network connect fleet-net unified-postgres
docker network connect fleet-net session1115-redis
docker network connect fleet-net character_os_postgres
docker network connect fleet-net character_os_redis
```

Then wrote
[`/Users/donkeyking/development/infra/README.md`](../../../infra/README.md)
and
[`/Users/donkeyking/development/infra/docker-compose.yml`](../../../infra/docker-compose.yml)
(network anchor only; no services).

**Verification**: spun up a throwaway `postgres:15` container on
`fleet-net`, confirmed DNS resolution to all four hostnames + TCP
reachability to both postgres instances on port 5432 internal.
Same with `redis:7-alpine` for both redis instances on 6379
internal.

**Docker Desktop bug hit twice**: attaching a running container to
a second Docker network silently breaks its host-port mapping. Hit
on `unified-postgres` (host psql started timing out at :5432) and
on `character_os_redis` (Character OS Celery worker started getting
`Connection reset by peer` at :6381). Fix is `docker restart
<name>` — re-establishes the host-port bridge. Now codified in the
infra README's "Known caveats" section so future fleet attachments
don't trip on it cold.

**What I intentionally did not do**:

- Did NOT rehome the existing data containers into a new compose
  project (volumes attached; recreation risks data loss).
- Did NOT containerise either Django app (Full scope; ~half day +
  high blast radius; deferred until a third fleet app needs it).
- Did NOT resolve the `:8000` host-port collision (deferred —
  pivoted u-d-b's Daphne to :8020 for this session instead).

### Slice 3 — `consult_engine` bridge

**Architecture choice**: HTTP, not Python import. Both apps stay
independent Django projects with their own models, settings, data.
The bridge is intentionally a network call so neither side absorbs
the other.

**Tool shape**:

- Sync (the LLM blocks on the tool result, matching `recall_knowledge`
  shape).
- Polls u-d-b's `/api/pa/chat/status/<task_id>/` every 1.5 s up to
  `MAX_POLL_SECONDS = 25` then surfaces a timeout error.
- Errors are RETURNED, not raised — the avatar narrates degraded
  behaviour instead of dropping into a dispatcher error toast.
- Description kept under the 500-char Pydantic cap on the media-engine
  schema (recall_knowledge's hard-won constraint).
- `cost_micros=5_000` ($0.005). Engine PA cost is ~$0.0005 per
  simple GPT-5.2 turn plus dispatched tools; $0.005 covers the
  common case.

**End-to-end test via realtime UI** (the deliverable):

| Step | What happened |
|---|---|
| Operator opened `/spokespeople/<rigby>/talk` | Realtime session 0ca84d1f-e2e7-4cd4-aaa5-a21eea78af98 created (201) |
| Avatar/LLM session config | 7 tools sent to Runway, including `consult_engine`. Grounding doc composed (39,866 chars) from Rigby's 45 KDs |
| Operator asked: "What is currently running on the engine?" | Rigby's LLM picked `consult_engine` |
| consult_engine fired | HTTP POST to `http://localhost:8020/api/pa/chat/` |
| u-d-b PA processed | GPT-5.2, 1 iteration, 9.59 s, intent=general, $0.0081 |
| Bridge response | Real multi-paragraph answer about how to check Celery workers, beat schedule, body systems, etc. |
| Audit row recorded | `RealtimeToolInvocation` tool=`consult_engine` status=succeeded |

**Cosmetic issue surfaced**: PA's persistence to u-d-b's
`chat_conversations` failed initially because `discord_user_id`
was `NOT NULL` despite the model declaring `null=True`. My initial
manual `ALTER TABLE` set it `NOT NULL DEFAULT ''` but Django
inserts explicit NULL (not absent value) so the default never
kicks in. Fixed mid-session via `ALTER TABLE chat_conversations
ALTER COLUMN discord_user_id DROP NOT NULL` (plus the other two
discord_* columns). Retest verified persistence works; row id=4
saved cleanly with no warnings.

## Local-only stack snapshot

Single-machine processes at session close:

| Service | Port | Notes |
|---|---|---|
| u-d-b Daphne | :8020 | Custom port to dodge :8000 (Character OS has it) |
| u-d-b PA Celery worker | (broker :6379) | `-Q pa --pool=threads --concurrency=2` |
| Character OS Django | :8000 | Default — owns this port locally |
| Character OS Celery worker | (broker :6381) | `--pool=solo`; restarted mid-session after Redis fleet-net restart |
| Character OS Vite | :5174 | Dev server; proxy targets `:8000` for Django, `:8001` for media-engine |
| Character OS media-engine | :8001 | Required for realtime; uvicorn FastAPI |
| `unified-postgres` (Docker) | host :5432 → container :5432 | u-d-b + `fleet-net` |
| `character_os_postgres` (Docker) | host :5433 → container :5432 | Character OS + `fleet-net` |
| `session1115-redis` (Docker) | host :6379 → container :6379 | u-d-b + `fleet-net` |
| `character_os_redis` (Docker) | host :6381 → container :6379 | Character OS + `fleet-net` |

## What's NOT done (carry-over for future sessions)

1. **u-d-b local DB is mostly empty.** I created a `donkeyking`
   superuser + DRF token (`e3c7276f00f12b77bda365c7c186577cd854cf2a`,
   matches `tools/pa_local.sh`). No workspaces, no recent
   deliverables, no agent execution history. PA's responses are
   competent about platform mechanics but light on portfolio
   specifics. **Next slice**: seed u-d-b's local data so the engine
   has something portfolio-shaped to say back when consulted.

2. **u-d-b schema drift not properly migrated.** Manual ALTER
   added 6 columns to `chat_conversations`; a proper
   `makemigrations` pass would generate **0340_*.py** plus several
   other model changes (Narrative, NarrativeEvidence, etc.) that
   are code-but-not-DB. Deferred because the auto-generated
   migration captures more than just my drift fix. Run when you're
   ready to commit a multi-model migration on a clean branch.

3. **Mock-vs-real embedding cache collision — closed.** Independently
   fixed by the parallel Character OS CC session (commit `9c10b57`).
   No carry-over.

4. **Host-port collision long-term solution.** Currently u-d-b is on
   :8020 just for this session; default u-d-b workflows (Makefile,
   Procfile, browser bookmarks) assume :8000. Eventually either
   move Character OS to :8010 permanently (vite proxy 4-line edit
   + Django runserver flag) or containerise one of the apps so it
   doesn't compete for the host port.

5. **Bridge tool catalogue not expanded.** `consult_engine` is the
   first engine-bridge tool. Two clear next ones:
   - `query_spider_data` — search recent SpiderData rows by topic
   - `agent_consult` — invoke a specific u-d-b agent (e.g.
     `MarketIntelligenceAgent`) with a question
   Both follow the same HTTP-POST + poll pattern. Add when you
   have a question shape that wants them.

## Files to read for context next session

| File | Why |
|---|---|
| `character-os/shell/apps/realtime/tools/consult_engine.py` | The bridge tool — pattern reference for future engine-bridge tools |
| `character-os/scripts/ingest-udb-spokesperson-corpus.py` | Ingestion pattern; copy + parameterise for other apps' corpora |
| `/Users/donkeyking/development/infra/README.md` | Fleet network convention + Docker caveat |
| `character-os/shell/apps/embeddings/embedding_service.py` | Cache collision bug to fix |
| `docs/spokesperson/` (this repo) | The corpus that's now grounded into Rigby — refresh and re-ingest when it changes |

## Runtime reminders

- **u-d-b on :8020**: `PORT=8020 make start` (Daphne) + a PA-queue
  Celery worker. Default :8000 is taken by Character OS locally.
- **Bridge env vars** (Character OS-side, in `.env`): `UDB_PA_API_URL`,
  `UDB_PA_API_TOKEN`. Restart Character OS Django after changing.
- **Docker fleet-net restart-after-attach rule** — if you attach a new
  container to `fleet-net`, restart it (`docker restart <name>`)
  before relying on its host-port mapping again. Documented in
  `/Users/donkeyking/development/infra/README.md`.
- **PA chat round-trip latency**: 2-10 s typical, up to 25 s before
  the bridge tool times out. The avatar should narrate "the engine's
  thinking" pre-invoke rather than waiting silently.
