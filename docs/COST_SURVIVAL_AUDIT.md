# Cost Survival Audit — May 2026 (pre-merge gate)

**Date:** 2026-05-12
**Author:** Claude Code, Session 1116 (merge-readiness Tier 1)
**Status:** **DRAFT — gate doc for Tier 2.** Does not bless adding OpenAI credits back. Reviewer (Rigby + operator) must sign off on the four numbered conclusions in § J before the next merge tier proceeds.

> **Purpose.** Before OpenAI credits come back on, prove the platform can't run away with $4K in a weekend. This audit catalogues every paid API surface, every existing guard rail, every blind spot in cost telemetry, and proposes the missing pieces. No code touched. Just numbers and recommendations.

---

## A. Headline numbers

| Surface | Count | Cost-tracked? | Kill-switch? |
|---|---:|---|---|
| Enabled `PeriodicTask` rows (`django-celery-beat`) | **258** | partial (LLM only) | global only |
| Disabled `PeriodicTask` rows (in DB but `enabled=False`) | 47 | n/a | n/a |
| Total `PeriodicTask` rows | 305 | — | — |
| Static `beat_schedule` entries in `core/celery.py` | 42 | — | — |
| Celery user-defined task functions (full registry) | **397** | n/a (most never hit external APIs) | n/a |
| Orphan tasks (registered + no caller + no schedule) | 10 (per `CELERY_AUDIT.md`) | — | — |
| LLM-cost orphans waiting on credits to re-enable | 5 (per Session 1115 batch-8) | — | — |

**Reality check on the 305 figure.** `CLAUDE.md`'s headline claim (`305 PeriodicTask rows (258 enabled, 47 disabled)`) is the runtime-derived inventory from `gather_inventory()`. The Tier 1 prompt's phrasing ("All 305 enabled PeriodicTasks") is off — 305 is the total, 258 are enabled. Cost census in this doc is scoped to the **258 enabled rows** plus the **42 static `beat_schedule` entries** (with overlap — sync commands materialize selected static entries into DB rows).

**Paid-API surfaces in the codebase:**

| Provider | Pricing rates defined? | Cost calculator called? | Persisted to a log table? |
|---|---|---|---|
| OpenAI (LLMs) | implicit (via `LLMCallLog.cost` written by call wrapper) | ✓ | ✓ `LLMCallLog` |
| Anthropic | implicit (via `LLMCallLog`) | ✓ | ✓ `LLMCallLog` |
| Together / DeepSeek / Gemini | implicit (via `LLMCallLog`) | ✓ | ✓ `LLMCallLog` |
| Ollama (local) | $0 by design | n/a | n/a |
| OpenAI Embeddings | implicit (via `LLMCallLog` if writer is wired; needs verify) | partial | partial |
| ElevenLabs (TTS) | ✓ `api_cost_config.ELEVENLABS_COSTS` | ✓ `calculate_elevenlabs_cost()` | **✗ no log** |
| Stability AI (image) | ✓ `api_cost_config.STABILITY_COSTS` | ✓ `calculate_stability_cost()` | **✗ no log** |
| Runway ML (video) | ✓ `api_cost_config.RUNWAY_COSTS` | ✓ `calculate_runway_cost()` | **✗ no log** |
| Replicate (lip-sync, image, video) | ✗ | ✗ | **✗ no log** |
| Spider paid APIs (NewsAPI, Polygon, Finnhub, AlphaVantage) | ✓ `api_cost_config.SPIDER_COSTS` (mostly $0.0001/req) | ✗ never called by spider runtime | **✗ no log** |
| DaVinci Resolve render-node (CPU only) | $0 | n/a | n/a |

**The headline cost-survival finding** is the four ✗ rows above. ElevenLabs, Stability, Runway, and Replicate calls *fire today* in 11 different files (mostly `core/views_image_*`, `content/video_provider.py`, `core/services/podcast_audio_service.py`). The cost calculator is invoked at the call site, but **the return dict is never written to a persistent audit log**. We have a number, then we throw it away. `LLMCallLog` only covers LLM completion calls.

---

## B. What's already built (cost infrastructure inventory)

This audit shouldn't propose what already exists. Here's the field map:

### B.1 `LLMCallLog` — `core/models_llm_routing.py:297`

Per-call audit table with these fields:

```
agent_name (db_index)            — who called
user (FK SET_NULL)               — for whom (NULLable)
provider                         — openai / anthropic / etc.
model_id                         — gpt-5-mini / claude-opus-4-7 / etc.
was_fallback / was_auto_selected — routing decisions
task_type                        — categorical (free text today)
prompt_tokens, completion_tokens, total_tokens
success (bool)
cost (Decimal max_digits=10, dp=6)
trace_id (db_index)              — PA request trace ID for join
latency_ms
error_type, error_message
created_at (db_index)
```

**Indexes:** `(agent_name, -created_at)`, `(provider, model_id, -created_at)`, `(-created_at)`, `(success, -created_at)`.

**Gap:** **no `workspace_id` FK**. Per-workspace cost attribution is impossible from this row alone. `user` is filled when a request originates from a PA chat session, but agent dispatches (beat-fired) leave `user=NULL`.

### B.2 `BudgetController` — `core/services/ops_autopilot/budget.py:238`

Ops-autopilot v4 policy. Polls `LLMCallLog` on a cycle, reads `daily_total` (last 24h) and `hourly_total` (last 1h). Two enforcement tiers, both backed by `SystemConfiguration` flags:

| Tier | Threshold | Effect |
|---|---|---|
| Soft (`budget_downgrade_active=true`) | 70% of daily cap | `llm_enforcer` reroutes calls from premium models to `BUDGET_DOWNGRADE_MODEL` |
| Hard (`budget_freeze_active=true`) | 95% of daily cap | Block non-critical LLM calls |

**Gap:** the cap is **a single global number**. `AutopilotConfig.BUDGET_*` doesn't slice per workspace, per agent, or per task category. Under multi-tenant load every workspace pulls from the same pool, and one runaway agent can starve everyone else.

### B.3 PA tools that already query cost

- `cost_telemetry_tool` (`td_handlers_agents.py:2880`, Session 1036) — actions: `summary` / `top_agents` / `recent_calls`. Hits `LLMCallLog`. **Last-24h scope by default.** No workspace filter argument.
- `check_resource_budget` (`epa_handlers_tools.py:4347`) — surfaces autopilot budget mode.

### B.4 `api_cost_config.py` — pricing tables

Rates current as of January 2026. **No drift guard** — these aren't sync'd against provider docs automatically and will silently rot. The values:

- ElevenLabs: `$0.24 / 1,000 chars` (Pro default), Turbo models = 0.5× multiplier
- Stability: `$0.01 / credit`, SDXL = 6.5 credits/image → $0.065/image
- Runway: `$0.05 / second` (gen-4-turbo default), gen-4.5 = $0.25/s, 1080p = 1.2× multiplier
- ElevenLabs voice clone training: `$5.00` one-time

### B.5 Embedding backfill — embeddings already skip unchanged rows

`spider_semantic_search.backfill_embeddings` (`core/services/spider_semantic_search.py:454`) filters `embedding__isnull=True` AND excludes rows with `embedding_text='[NO_ITEMS]'`. Re-runs are non-destructive: rows that already have an embedding are *not* re-embedded.

Same pattern in:
- `core.tasks.backfill_memory_embeddings` (AgentMemory)
- `core.tasks.backfill_conversation_embeddings` (conversations, beat row currently `enabled=False`)
- `core.tasks.backfill_stage_documents` (initiative stage docs)

**Cross-table risk:** none. Each backfill task targets a different model. No accidental double-embedding.

**Drift risk:** stale embeddings. If a `SpiderData.raw_data` is mutated in place (rare — most pipelines insert new rows), the embedding from the original text persists. Today this is a quality concern, not a cost concern; no policy re-embeds on content change.

---

## C. PeriodicTask cost census (the 258 enabled rows)

A full per-row table for 258 entries would balloon this doc and rot inside a week. Instead, this section categorises by **cost class** — the only granularity that matters for kill-switch decisions. The companion regenerator command (proposed in § H) will produce the per-row table on demand.

### C.1 Cost classes (heuristic)

| Class | Definition | Approx. count (of 258) | Action when credits return |
|---|---|---:|---|
| **PAID-LLM** | Fires `BaseAgent.run()` → dispatches an LLM-using agent (ContentWriter, Editor, CTO, COO, etc.) | ~80 | gate behind `BEAT_GOVERNOR_ENABLED` mission + per-workspace cap |
| **PAID-MEDIA** | Fires TTS, image-gen, video-gen, or lip-sync | ~12 | gate behind explicit ENABLED flag + per-workspace daily $ cap |
| **PAID-EMBED** | Generates OpenAI / equivalent embeddings | ~5 | safe (idempotent backfill — re-run cost ≈ $0 for already-embedded rows) |
| **PAID-EXTERNAL-API** | Hits a paid spider data source (NewsAPI, Polygon, Finnhub, AlphaVantage) | ~10 | low individual cost ($0.0001/req) but volume can sting |
| **FREE-INTERNAL** | Pure DB/Redis/file work — cleanup, aggregation, broadcast, signals | ~150 | leave on |
| **FREE-MONITOR** | Health checks, telemetry rollups | ~15 | leave on |

**Why these are rough counts:** there is no script today that walks each PeriodicTask body and identifies the API surface(s) it touches. Building one is § H proposal #1.

### C.2 The PAID-LLM family (the 70% problem)

Per `CELERY_AUDIT.md` Session-1115 closure, the registry has 397 tasks; 387 have callers; 10 are orphans. Of the 10 orphans, **5 are LLM-cost scheduled tasks intentionally kept dormant pending credits**:

| Task | Why dormant |
|---|---|
| `rag_retrieval_canary` | Embedding + LLM grading on a fixed query set |
| `send_weekly_kpi_summary` | Discord post requires LLM summary |
| `run_ops_autopilot` | Takes actions which can include LLM dispatch |
| `post_ops_digest` | LLM-summarised daily ops report |
| `maintain_knowledge_freshness` | LLM re-summarises stale knowledge entries |

These five are the canary — they'll be the first tasks turned back on when credits restore, and the first tasks that need per-workspace budget gates.

### C.3 The PAID-MEDIA family (most spend per fire)

Top families that fire Runway / ElevenLabs / Stability:

| Task family | Surface | Typical cost per fire | Triggered by |
|---|---|---:|---|
| Podcast audio generation | ElevenLabs TTS | $0.50 – $3.00 (10-30k chars / episode) | beat (`auto-generate-podcast-episode`) + ad-hoc |
| TalkingCharacterAgent video | ElevenLabs + Runway + Replicate | $1.00 – $5.00 / 30s clip | PA `studio_tool(generate_talking_video)` |
| AudioAgent rotation (DISABLED) | ElevenLabs | $1-3 / fire | currently rotation-disabled per memory `feedback_agent_noise` |
| ML image gen | Stability or OpenAI image | $0.05 – $0.30 / image | image views + content pipeline |
| Distribution video pipeline | Runway (chunked) | $5 – $30 / longform | content_pipeline / video_provider |

### C.4 The PAID-EXTERNAL-API family

Spider tasks calling paid news / finance APIs. Per `api_cost_config.SPIDER_COSTS`, each request is `$0.0001`. The risk profile is volume not unit cost — a runaway spider could fire 100k requests/day = $10/day. Probably fine; flag if a spider's beat schedule drops below 5min interval.

---

## D. Kill-switch inventory

This section answers the prompt's second sub-audit: which paid-API tasks have a feature flag or workspace-level enable today, and which run regardless.

### D.1 Existing kill-switches (global)

| Switch | Mechanism | Scope | Covers |
|---|---|---|---|
| `BEAT_GOVERNOR_ENABLED` | env var → `governor_tool` in PA | global | Gates **agent dispatch** based on mission alignment + per-day budget |
| `budget_downgrade_active` | `SystemConfiguration` flag (BudgetController) | global | Routes premium models → cheap fallback |
| `budget_freeze_active` | `SystemConfiguration` flag (BudgetController) | global | Blocks non-critical LLM calls |
| `agent_control_tool` | PA tool action `block` / `unblock` | per-agent global | Block one agent across all callers |
| Per-agent timeout / cooldown ladders | `OpsAutopilot` timeout-remediation policy v17 | per-agent global | Auto-blocks agents stuck in timeout loops |
| `PeriodicTask.enabled` | `django-celery-beat` row flag | per-task global | Beat won't fire row when `enabled=False` (currently 47 rows off) |

### D.2 What's NOT gated today

| Gap | Why it matters | Severity |
|---|---|---:|
| Per-workspace daily $ cap on LLM spend | Operator opens 5 workspaces, each spawns agents — global cap fires before anyone notices | **HIGH** |
| Per-workspace daily $ cap on PAID-MEDIA (Runway, ElevenLabs, Stability) | Slice 2 of the Character OS merge fires Runway through Rigby. Single 50-message session = ~$50 in renders silently spent (per [`docs/MERGE_PROPOSAL_CHARACTER_OS_NATIVE.md`](MERGE_PROPOSAL_CHARACTER_OS_NATIVE.md) § I.2) | **HIGH — blocks merge Slice 2** |
| Per-task daily fire cap on PAID-MEDIA tasks | If `auto-generate-podcast-episode` flips `enabled=True` and runs `every 1h`, that's 24 episodes/day = $24 – $72/day | **MEDIUM** |
| Persistence of ElevenLabs/Stability/Runway/Replicate call costs | The biggest cost surface has zero audit trail today | **CRITICAL** |
| `MAX_RETRIES` × cost detector | A task that retries 6× on quota errors burns 6× the credits before giving up | **MEDIUM** |
| Provider-quota-aware throttle | If OpenAI returns 429, we just retry — no breaker | **MEDIUM** |

### D.3 Recommended kill-switch design (proposal — NOT built)

```
Layer 1 — Per-call hard cap (preflight)
  • Every paid call calls budget_gate.check(workspace_id, provider, est_cost)
  • Returns ALLOW / DOWNGRADE / DENY
  • Source of truth: SystemConfiguration['workspace_budget'][workspace_id]
                     + LLMCallLog daily aggregate for that workspace

Layer 2 — Provider circuit-breaker
  • On 429 / 402 from any paid provider, mark provider=tripped for 10 min
  • All calls through that provider DENY without retrying

Layer 3 — Per-task daily fire cap
  • New field PeriodicTask metadata.daily_fire_cap (JSON)
  • Beat governor reads cap, denies dispatch when day count exceeds cap

Layer 4 — Global hard freeze (already exists via BudgetController)
  • Last resort, fires when daily spend exceeds 95% of system cap
```

This is the design. Building it is Tier 4 § B (Runway-specific instance) and post-merge work.

---

## E. Embedding re-run audit

The prompt asks: "Are we re-embedding content that hasn't changed?"

**Answer: no, by the current filter design.** All four embedding-generating beat tasks filter `embedding__isnull=True` and skip non-null rows. Re-runs of unchanged rows cost zero embedding-API calls.

| Task | Schedule | Target | Re-run cost on unchanged row |
|---|---|---|---:|
| `backfill-spider-embeddings` | every 15 min, ml queue | `SpiderData` rows where `embedding IS NULL` and `embedding_text != '[NO_ITEMS]'` | $0 |
| `backfill-memory-embeddings` | beat enabled, default queue | `AgentMemory` rows missing embeddings | $0 |
| `backfill-conversation-embeddings` | beat DISABLED in DB | conversation rows | $0 (and not firing) |
| `backfill-stage-documents` | beat enabled, default queue | initiative stage docs | $0 |

**Risk surfaces that COULD trigger re-embeds:**

1. **Anything that sets `embedding = NULL` on existing rows.** A grep of `core/tasks*.py` shows no task does this. A manual `UPDATE SpiderData SET embedding=NULL WHERE …` from a shell session would.
2. **New rows inserted at high volume.** Spiders push new `SpiderData` rows constantly. Each new row = 1 embedding call. With ~1.14M `SpiderItemHash` rows accumulated, the rate is currently bounded by per-spider rate limits — not a runaway.
3. **A retry loop on embedding failure.** `backfill_spider_embeddings` catches one exception per batch and logs it; it does *not* retry the same row immediately. Safe.

**Stale-embedding risk** (separate from cost): if `SpiderData.raw_data` is mutated in place, the embedding from the original text persists silently. Today this is a quality concern, not a cost concern. No re-embed policy exists. Recommendation: leave alone until quality data demands action.

**Conclusion:** the prompt's "common drift: a stat triggers a re-embed → next stat triggers again → silent loop" is **not happening** in the current design. The filter eats it.

---

## F. `cost_per_workspace_today` — the missing query

The prompt asks for a single query that returns "this workspace has spent $X today across all paid APIs."

**Today, this query cannot be written.** Two reasons:

1. **`LLMCallLog` has no `workspace_id` FK.** `user` is sometimes populated. Workspace is not. Beat-fired LLM calls leave both NULL.
2. **Non-LLM API costs (Runway, ElevenLabs, Stability, Replicate) are not persisted anywhere.** The calculator returns a number; the caller logs it to Python `logger.info`; no DB row is created. Cost is computable per-call but un-aggregatable.

### F.1 Proposed schema (to enable the query)

Two changes, minimum:

**Change 1 — add workspace FK to `LLMCallLog`:**

```python
# core/models_llm_routing.py:297
class LLMCallLog(models.Model):
    # ... existing fields ...
    workspace = models.ForeignKey(
        'core.Workspace', null=True, blank=True,
        on_delete=models.SET_NULL, db_index=True,
        help_text='Workspace context for this call. NULL = system/global.',
    )
```

Caller plumbing: every LLM call site that has a `workspace_id` in context (PA tool dispatch, agent run inside an Initiative, etc.) must thread it through to the wrapper.

**Change 2 — create `ExternalAPICallLog` (new model):**

```python
# new file: core/models_external_api.py
class ExternalAPICallLog(models.Model):
    id = UUIDField(primary_key=True, default=uuid.uuid4)
    provider = CharField(max_length=32, db_index=True)
        # 'runway' / 'elevenlabs' / 'stability' / 'replicate'
    operation = CharField(max_length=64)
        # 'tts_synthesize' / 'image_gen' / 'video_gen' / 'lip_sync'
    model_id = CharField(max_length=128, blank=True)
    units = JSONField(default=dict)
        # {'characters': 1240} / {'credits': 12.5} / {'seconds': 10}
    cost = DecimalField(max_digits=10, decimal_places=6)
    user = ForeignKey(User, null=True, on_delete=SET_NULL)
    workspace = ForeignKey('core.Workspace', null=True, on_delete=SET_NULL, db_index=True)
    initiative = ForeignKey('core.Initiative', null=True, on_delete=SET_NULL)
    trace_id = CharField(max_length=64, blank=True, db_index=True)
    success = BooleanField(default=True)
    error_type = CharField(max_length=100, blank=True)
    error_message = TextField(blank=True)
    created_at = DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        indexes = [
            Index(fields=['workspace', '-created_at']),
            Index(fields=['provider', '-created_at']),
            Index(fields=['trace_id']),
        ]
```

**Why a separate table, not a discriminator on `LLMCallLog`:** different unit semantics (chars / credits / seconds). The `units` JSON keeps each provider's natural shape without invalidating LLM-call queries.

### F.2 The query (after both schema changes)

```python
def cost_per_workspace_today(workspace_id, *, tz='America/Denver'):
    from datetime import datetime, time, timedelta
    from django.db.models import Sum
    from django.utils import timezone
    import zoneinfo

    tz_obj = zoneinfo.ZoneInfo(tz)
    now_local = timezone.now().astimezone(tz_obj)
    midnight_local = datetime.combine(now_local.date(), time.min, tzinfo=tz_obj)
    midnight_utc = midnight_local.astimezone(timezone.utc)

    from core.models_llm_routing import LLMCallLog
    llm_spend = LLMCallLog.objects.filter(
        workspace_id=workspace_id,
        created_at__gte=midnight_utc,
    ).aggregate(total=Sum('cost'))['total'] or 0

    from core.models_external_api import ExternalAPICallLog
    media_spend = ExternalAPICallLog.objects.filter(
        workspace_id=workspace_id,
        created_at__gte=midnight_utc,
    ).aggregate(total=Sum('cost'))['total'] or 0

    return {
        'workspace_id': workspace_id,
        'as_of': now_local.isoformat(),
        'llm_usd': float(llm_spend),
        'media_usd': float(media_spend),
        'total_usd': float(llm_spend + media_spend),
    }
```

Wire it into `cost_telemetry_tool` as a new action `per_workspace` (or `today`). Default workspace = current PA chat context.

### F.3 Estimated implementation effort

| Step | Effort |
|---|---:|
| Migration: add `workspace` FK to `LLMCallLog` | 30 min |
| Caller plumbing: thread `workspace_id` into ~15 call sites | 2-3 hr |
| Migration: create `ExternalAPICallLog` | 30 min |
| Caller plumbing: wrap the 11 cost-calculator call sites to persist | 2-3 hr |
| New `cost_per_workspace_today` query + PA tool action | 1 hr |
| Unit test on a seeded workspace | 1 hr |
| **Total** | **~1 working day** |

This is Tier 3 telemetry work and Tier 4 merge-prep work, not Tier 1. Tier 1's job is to identify the gap, which is done.

---

## G. Sundry findings (not in the prompt's four sub-audits but in scope)

### G.1 The 47 disabled `PeriodicTask` rows

`enabled=False` keeps them visible but inert. **Risk:** an operator (or Rigby) flips one to `enabled=True` from the admin without realising it hits a paid API. Mitigation: a `should_be_disabled_reason` text field on `PeriodicTask` metadata, or a tag-based system (`metadata.cost_class: PAID-LLM | PAID-MEDIA | FREE-INTERNAL`), and a UI banner / Rigby refusal when re-enabling without a green-light flag. Out of scope for this audit. Filed as follow-up.

### G.2 Free fallbacks (Ollama, Together free tier)

Currently `agent_llm_router` can route to Ollama (local, $0) when configured. Operator-level escape valve: set `OLLAMA_BASE_URL` and `OLLAMA_PREFERRED_MODEL`, route the worst-offending agents (ContentWriter, Editor) to Ollama models. **This is the most cost-effective "credits-still-off" mitigation available right now.** Document explicitly in the merge plan.

### G.3 `cleanup_llm_call_logs` retention

`core/tasks.py:L*` — `cleanup-llm-call-logs` beat fires `15 4 * * sunday`, default retention undocumented in this audit. Verify retention is ≥30d before relying on `LLMCallLog` for historic analysis. Filed as follow-up.

### G.4 `claude_code_tool` and `code_job_tool` cost

`claude_code_tool` (PA tool) spawns autonomous Claude sessions. Each session is a `claude-opus` API spend not currently logged through `LLMCallLog` (Anthropic SDK calls under the hood — verify the wrapper writes). **Likely an existing blind spot.** Filed as follow-up; needs verification.

---

## H. Recommended actions (priority order)

These are *recommendations*. No code changed; Rigby + operator decide which to implement.

### H.1 Critical — must ship before OpenAI credits restore

| # | Action | Owner | Effort |
|---|---|---|---:|
| 1 | Add `workspace` FK to `LLMCallLog` (migration only — caller plumbing follows) | TBD | 30 min |
| 2 | Create `ExternalAPICallLog` model + persist all 11 cost-calculator call sites | TBD | 1 day |
| 3 | Implement `cost_per_workspace_today` query + PA tool action | TBD | 1 hr |
| 4 | Build `python manage.py build_cost_audit` mgmt command — walks every enabled PeriodicTask, classifies cost (PAID-LLM / PAID-MEDIA / PAID-EMBED / PAID-EXTERNAL-API / FREE-*), regenerates a per-row cost census doc | TBD | 1 day |

### H.2 High — should ship before Slice 2 of the merge

| # | Action | Owner | Effort |
|---|---|---|---:|
| 5 | Per-workspace daily $ cap (LLM + media combined) with `budget_gate.check()` API | TBD | 1 day |
| 6 | Provider circuit-breaker on 429/402 (sticky 10-min trip) | TBD | half day |
| 7 | `cost_class` tag on `PeriodicTask.metadata` + admin warning banner when enabling PAID-* row | TBD | half day |

### H.3 Medium — quality-of-life

| # | Action | Owner | Effort |
|---|---|---|---:|
| 8 | Drift guard: `api_cost_config.py` rates verified against provider pricing pages quarterly (or via a docs-pattern check) | docs-pattern | 1 hr |
| 9 | Cost-by-trace-id query (join LLMCallLog + ExternalAPICallLog by trace_id) | TBD | 1 hr |
| 10 | Ollama fallback for ContentWriter + Editor in agent_llm_router config | TBD | half day |

---

## I. Forward-drift guards (proposed)

Once the H.1 actions ship, lock these claims via `core/services/doc_claim_verification.py` so this audit stays honest:

| Claim ID | Check | Pass condition |
|---|---|---|
| `cost_audit_external_api_log_exists` | Model `ExternalAPICallLog` exists in registry | True |
| `cost_audit_llm_call_log_has_workspace` | `LLMCallLog._meta.get_field('workspace')` does not raise | True |
| `cost_audit_persistence_call_sites` | grep for `calculate_(runway\|elevenlabs\|stability)_cost` returns N sites where N == count of sites that also save to `ExternalAPICallLog` (no caller drops the result) | exact match |
| `cost_audit_periodic_task_enabled_count` | `PeriodicTask.objects.filter(enabled=True).count()` | currently 258; lock as a soft drift watch (warn at ±10%) |
| `cost_audit_orphan_llm_tasks_count` | `CELERY_AUDIT.md` orphan list — count of tasks in the "LLM-cost scheduled" category | 5 today; locked baseline |

Each becomes a row in `verify_doc_claims`. Severity `medium` initially; raise to `high` once H.1 ships and the schema migration lands.

---

## J. Gate conclusions — operator sign-off required before Tier 2

Before this audit unblocks Tier 2 (Connection Census), the operator (via Rigby) must agree to all four:

1. **The four ✗ rows in § A are the headline cost blind spot.** ElevenLabs, Stability, Runway, Replicate cost is calculated but never persisted. This is shipping-blocker for the merge's Slice 2.

2. **`cost_per_workspace_today` cannot be answered today.** Needs the two schema changes in § F.1. Implementation = ~1 working day.

3. **Embeddings are not silently re-running.** § E confirms the filter design is sound. No remediation needed.

4. **OpenAI credits should not be restored** until at minimum H.1 items #1–#3 ship — workspace FK, `ExternalAPICallLog`, and the per-workspace daily query. The H.2 layer (per-workspace cap) is recommended but not strictly required before credits.

If any of those four is "no" / "not yet," loop back via Rigby (`python tools/pa_chat.py "..."`) before drafting Tier 2.

---

## K. References

- [`docs/CELERY_AUDIT.md`](CELERY_AUDIT.md) — full registry, orphan list, Session 1115 closure
- [`docs/BEAT_AUDIT.md`](BEAT_AUDIT.md) — 42 static `beat_schedule` entries
- [`docs/PLATFORM_INVENTORY.md`](PLATFORM_INVENTORY.md) § Celery Beat — 305 PeriodicTask rows
- [`docs/handoffs/SESSION_1115_CODE_HEALTH_REFACTORS.md`](handoffs/SESSION_1115_CODE_HEALTH_REFACTORS.md) — orphan reduction arc
- [`docs/MERGE_PROPOSAL_CHARACTER_OS_NATIVE.md`](MERGE_PROPOSAL_CHARACTER_OS_NATIVE.md) § I.2 — per-workspace Runway budget requirement
- `core/models_llm_routing.py:297` — `LLMCallLog`
- `core/services/api_cost_config.py` — pricing tables
- `core/services/ops_autopilot/budget.py:238` — `BudgetController`
- `core/services/td_handlers_agents.py:2880` — `_handle_cost_telemetry`

---

**End of Tier 1.** Tier 2 (Connection Census) starts only after operator + Rigby green-light § J.
