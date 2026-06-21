<!-- DOC-POINTER-V1 -->
> **⚠ Stats in this doc may drift from code.** For current verified numbers see [`../PLATFORM_INVENTORY.md`](/docs/PLATFORM_INVENTORY.md) (sole authoritative counts per `DOC_LIFECYCLE.md` §2c). Run `python manage.py verify_doc_claims --only-drift` to see which specific claims currently diverge from runtime reality (Session 1099 verifier).

# Active Module Ownership Map

Five subsystems live in the codebase as **active runtime code that is hard
to tell apart from dormant or duplicate code by file layout alone**.
Session 1111 flagged each of these as "underdocumented active" — they
work, they are imported by the live request path, but their
relationships to look-alike modules are not obvious without grep.

This doc names each one, says where it actually runs, and warns about
the look-alikes that have caused real misreads (including in Session
1111's own write-up). It is the durable answer so the next contributor
doesn't re-litigate the audit.

## TL;DR

| Active path | What it is | Most-confused look-alike |
|---|---|---|
| `revenue/revenue_verifier.py` | Active Redis-only payment-verification helper, instantiated at module load by `ai_platform/views.py` | `revenue/models.py` (broken/unwired — labelled `ACTIVE-COMPANION-PARTIAL` Session 1113) |
| `advisors/registry.py` + `advisors/llm_advisor_system.py` | Active 25+ domain-expert advisor registry, used by PA, agents, opportunity analyzer, audit coordinators | None — but Session 1111 mistakenly called it a namespace package; it has a real `__init__.py` |
| `llm/{base,ollama_provider,router}.py` (top-level) | Tiny ~52-line direct-Ollama chat helper used by two `core/views*.py` modules | `core/services/agent_llm_router.py` (697 LOC routing layer) and `core/services/llm_provider_registry.py` (`LLMProviderRegistry`) — *different layers* |
| `core/tasks_*.py` (12 modules, ~31.7k LOC) | Implementation modules behind the wrapper Celery tasks in `core/tasks.py`; loaded via lazy `_impl_*` imports | The wrapper pattern in `core/tasks.py` makes these look orphan; only `core.tasks_agents` is in `app.conf.imports` |
| `core/urls.py` (4,750 LOC) vs `core/urls_unified.py` (118 LOC) | `core/urls.py` is the entrypoint **and** the big monolith; `core/urls_unified.py` is a small redirect helper it includes | Session 1111's PR-D row swapped these — labelled `urls_unified.py` as the 4,750-line monolith |

---

## 1. `revenue/revenue_verifier.py` — active, Redis-only

**File:** `revenue/revenue_verifier.py` (456 LOC)
**Class:** `RevenueRealityVerifier`

### Where it runs

`ai_platform/views.py:15` imports `RevenueRealityVerifier` and
instantiates a module-level singleton at line 22:

```python
from revenue.revenue_verifier import RevenueRealityVerifier
...
revenue_verifier = RevenueRealityVerifier()
```

`ai_platform.urls` is `include()`-d at the root from
`core/urls.py:3179`:

```python
path('', include('ai_platform.urls')),  # AI Platform endpoints
```

So importing the verifier is **part of every web boot** — not lazy.

### What it does

Provides multi-source verification that revenue events are real, with
methods for Stripe, PayPal, bank, blockchain, and generic-API
transaction checks. The verifier:

- Connects to Redis on construction (DB **3** — dedicated, not the
  default DB 0).
- Reads `REDIS_HOST` / `REDIS_PORT` from `django.conf.settings`,
  falling back to `localhost:6379`.
- Stores per-transaction proof hashes and an audit trail with TTLs
  (90 days for proofs, 7 days for flow data).

### Failure semantics

Every Redis op is wrapped in `try/except Exception` that **logs the
error and returns `False` (or proceeds with degraded behavior)**. This
is closer to **fail-silent** than fail-open in the strict security
sense:

- A verification call that hits a Redis exception returns `False` from
  the relevant `_verify_*` method.
- The caller decides what to do with `False`.
- Process keeps running; no Redis = no proof storage, but no crash.

Worth confirming under load before any refactor — if Redis is down at
boot, construction itself can fail because `redis.Redis(...)` only
defers the connection, but the first hgetall/hset surfaces the error.

### Companion: `revenue/models.py`

Same directory, but `revenue/models.py` is currently
`ACTIVE-COMPANION-PARTIAL`:

- `revenue` is **not** in `core.settings.INSTALLED_APPS`.
- The 4 Django models lack `app_label` in `Meta`, so importing
  `revenue.models` raises:
  ```
  RuntimeError: Model class revenue.models.<X> doesn't declare an
  explicit app_label and isn't in an application in INSTALLED_APPS.
  ```
- No migrations exist; nothing imports the file.

The verifier is **Redis-only by design today**. The persistence layer
in `models.py` is a drafted-but-unwired companion that needs a product
decision (rehome in an installed app, or delete). See the Session 1113
banner in `revenue/models.py` and the Session 1111 deeper-review map.

---

## 2. `advisors/` — active domain-expert registry

**Files:** `advisors/__init__.py` (5 LOC), `advisors/registry.py`
(935 LOC), `advisors/llm_advisor_system.py` (701 LOC)

### Package status

This is a **regular Python package** with a real `__init__.py`. The
`__init__.py` carries only a docstring (no public re-exports), so
imports go through the submodules directly. Session 1111 described it
as a namespace package — that was incorrect. The file is committed and
non-empty.

### What it provides

`AdvisorRegistry` (defined in `advisors/registry.py:142`) holds:

- `AdvisorDomain` enum — domain specializations (financial, business,
  technology, legal, content, etc.).
- `AdvisorExpertiseLevel` enum.
- `AdvisorProfile` dataclass — name, domain, biography, signature
  voice patterns, methodology.
- `AdvisorConsultation` dataclass — request/response container.
- `AdvisorRegistry` class — registration, lookup by domain, expertise
  routing.
- A module-level singleton: `advisor_registry = get_advisor_registry()`
  at `advisors/registry.py:936`.

`advisors/llm_advisor_system.py` provides the LLM-backed consultation
layer that wraps the registry.

### Active importers (16+)

Direct importers in the live runtime — no archive paths:

- PA: `core/personal_ai_assistant.py`, `core/personal_ai_assistant_enhanced.py`,
  `core/unified_personal_assistant.py`, `core/assistant/base.py`,
  `core/unified_hub.py`, `core/epa_handlers_*.py`
- Opportunity / orchestration: `core/opportunity_ai_analyzer.py`,
  `core/orchestration_reality_connector.py`,
  `core/system_integration_orchestrator.py`
- Agents / audit: `core/agents/stocks/stock_audit_coordinator.py`,
  `core/agents/blockchain/blockchain_audit_coordinator.py`
- Action plans: `intelligence/action_plan_advisor_handoff.py`,
  `intelligence/action_plan_orchestrator.py`
- Service layer: `core/services/advisor_context_builder.py`
- Wiring: `agents/agent_wiring_system.py`
- Tests: `tests/integration/test_unified_integrations.py`

Most call sites use the lazy-singleton pattern shown in
`core/services/advisor_context_builder.py`:

```python
from advisors.registry import get_advisor_registry
self._advisor_registry = get_advisor_registry()
```

### Don't fold this into `core/`

Multiple modules import `advisors.registry` by absolute path. Moving it
under `core/services/` would break those imports without a
compatibility shim. Document, don't relocate.

---

## 3. Top-level `llm/` — direct Ollama helper, not the production router

**Files:** `llm/__init__.py` (empty), `llm/base.py` (14 LOC),
`llm/ollama_provider.py` (26 LOC), `llm/router.py` (12 LOC).

Total: ~52 LOC.

### What it is

A self-contained, dependency-light helper for talking to a local
Ollama HTTP server. Defines:

- `ChatMessage` dataclass.
- `LLMProvider` base class with a single `chat()` method.
- `OllamaProvider` that POSTs to `OLLAMA_BASE_URL` / `LLM_HTTP_TIMEOUT`
  from `django.conf.settings`.
- `chat()` function in `llm/router.py` that picks the provider by
  name (currently hard-coded: only `ollama`).

### Active importers

Two — both Django views:

- `core/views/main.py:1438`–1439
- `core/views.py:1607`–1608

Both use `from llm.base import ChatMessage` and `from llm import router`.

### What it is **not**

This is a different layer from the production LLM routing
infrastructure under `core/services/`:

| Layer | File | Purpose |
|---|---|---|
| Top-level `llm/` | `llm/router.py`, `llm/ollama_provider.py` | Direct one-shot Ollama chat for two view paths |
| Agent LLM router (production) | `core/services/agent_llm_router.py` (697 LOC) | Routes agents to optimal LLM models with telemetry, fallback, performance tracking |
| Provider registry (production) | `core/services/llm_provider_registry.py` (`LLMProviderRegistry` at line 1002) | Multi-provider selection across OpenAI, Anthropic, Together, Ollama, DeepSeek, Gemini |
| LLM call wrapper | `core/services/llm_call_wrapper.py` | `llm_call_span()` context manager — adopted across Tier-1 modules in Session 1098 |
| Universal executor | `core/services/universal_llm_executor.py` | Unified executor used by agents and tasks |

The two are **not interchangeable**: top-level `llm/` is fine for the
narrow direct-chat use case in views, but anything inside an agent or
Celery task should go through `core/services/agent_llm_router.py` or
`core/services/llm_call_wrapper.py` so telemetry and provider failover
work correctly.

---

## 4. `core/tasks_*.py` — implementation modules behind `core/tasks.py`

**Files:** `core/tasks.py` (12,575 LOC) plus 12 sibling
implementation modules:

| Module | LOC |
|---|---|
| `core/tasks_agents.py` | 5,622 |
| `core/tasks_misc.py` | 5,348 |
| `core/tasks_content.py` | 4,378 |
| `core/tasks_ops.py` | 3,878 |
| `core/tasks_conversations.py` | 3,553 |
| `core/tasks_initiatives.py` | 2,954 |
| `core/tasks_financial.py` | 2,642 |
| `core/tasks_media.py` | 1,356 |
| `core/tasks_spiders.py` | 909 |
| `core/tasks_body_systems.py` | 848 |
| `core/tasks_push_notifications.py` | 167 |
| `core/tasks_executor.py` | 111 |

### How they get loaded

Two paths:

1. **`tasks_agents` — explicit import (pinned at boot)** in `core/celery.py`:
   ```python
   # Session 919: Explicitly include task modules with non-standard names.
   # autodiscover_tasks() only finds tasks.py, not tasks_agents.py
   app.conf.imports = (
       'core.tasks_agents',
   )
   ```
   `tasks_agents` runs `execute_agent` / `execute_orchestration` and
   needs to be importable by every worker at boot, so it's pinned.

2. **The other 11 modules — lazy `_impl_*` import** inside wrapper
   tasks defined in `core/tasks.py`. The pattern looks like this
   (see `core/tasks.py` lines 402-1008 for many examples):

   ```python
   @shared_task(bind=True, name='cleanup_stale_agent_executions')
   def cleanup_stale_agent_executions(self, minutes_threshold=60):
       from core.tasks_agents import _impl_cleanup_stale_agent_executions
       return _impl_cleanup_stale_agent_executions(self, minutes_threshold)
   ```

   The wrapper is `@shared_task`-decorated so Celery autodiscovers it
   from `tasks.py`. The actual implementation lives in
   `core/tasks_<domain>.py` and is imported only when the task fires —
   keeping the import surface (and memory cost) out of worker boot
   for everything except the agents path.

### Why the indirection exists

- `app.autodiscover_tasks()` finds **`tasks.py` only** by Django-Celery
  convention. `tasks_<X>.py` files are not autodiscovered.
- Without this pattern you'd either need every `tasks_*.py` in
  `app.conf.imports` (bloating worker boot) or every task defined in
  `tasks.py` (which would be even larger than its current 12,575
  lines).
- Keeping wrappers in `tasks.py` and impls in `tasks_<X>.py` lets
  `tasks.py` register the public Celery surface while the heavy code
  is only paged in on first task run.

### Reading guide

- If you see a `_impl_<name>` function, its public registered name is
  the wrapper in `core/tasks.py` that does `from core.tasks_<X>
  import _impl_<name>`.
- A task that **doesn't** appear in `core/celery.py app.conf.imports`
  but is listed in `PeriodicTask` rows or `CELERY_TASK_ROUTES` should
  still resolve — its wrapper lives in `tasks.py`.
- "Module foo never gets loaded" suspicions are usually wrong; check
  whether a `_impl_` wrapper in `tasks.py` lazy-imports it.

---

## 5. `core/urls.py` vs `core/urls_unified.py` — the naming is misleading

### Actual line counts and roles

| File | LOC | path()/include() count | Role |
|---|---|---|---|
| `core/urls.py` | **4,750** | **1,759** | `ROOT_URLCONF = 'core.urls'` — entrypoint **and** the big monolith |
| `core/urls_unified.py` | 118 | 44 | Small redirect-only helper, included by `core/urls.py` |
| `core/urls_provenance.py` | (small) | — | API namespace |
| `core/urls_real_data.py` | (small) | — | API namespace |

### Settings + include chain

`core/settings.py:189`:

```python
ROOT_URLCONF = 'core.urls'
```

Inside `core/urls.py`:

```python
# core/urls.py:1559
path('', include('core.urls_unified')),    # Unified platform URLs
# core/urls.py:1745
path('api/provenance/', include('core.urls_provenance')),
# core/urls.py:1751
path('', include('core.urls_real_data')),
```

So:

- The request router is `core/urls.py`.
- `core/urls_unified.py` is a 118-line redirect helper that maps old
  Django URL names (e.g. `dashboard/`, `decisions/`, `analytics/`) to
  React frontend routes via `redirect()` views. It's included from
  `core/urls.py:1559` and adds 44 additional path() entries.

### Why this is worth a doc

Session 1111's PR-D row called `core/urls_unified.py` "the 4,750-line
monolith via `core/urls.py:1559`." That's backwards: the 4,750-line
monolith **is** `core/urls.py` itself, and `urls_unified.py` is the
small auxiliary redirect file it includes. The naming makes this easy
to misread. The 60+ legacy redirects Session 1111 separately mentions
("removing them breaks bookmarks") live in `urls_unified.py` — that
part is correct.

If you're touching the URL surface:

- `core/urls.py` is where the bulk of routes (API, admin, includes)
  live. Edit here for nearly any new endpoint.
- `core/urls_unified.py` only owns the legacy-Django-name → React
  redirect bag.
- The split is **historical, not architectural**: there's no clean
  ownership boundary; the file got carved out for redirect-helper
  reasons during Session 688's React migration.

---

## See also

- [`docs/handoffs/SESSION_1111_DEEPER_REVIEW_MAP.md`](../handoffs/SESSION_1111_DEEPER_REVIEW_MAP.md)
  — the deeper-review queue this doc closes (PR-D).
- [`docs/handoffs/SESSION_1113_DORMANT_PARTIAL_LABELS.md`](../handoffs/SESSION_1113_DORMANT_PARTIAL_LABELS.md)
  — the companion banner pass that labelled the *dormant* siblings of
  these active modules (e.g. `revenue/models.py`).
- [`docs/audit/CLEANUP_PLAN.md`](../audit/CLEANUP_PLAN.md) — the
  cleanup workspace that tracks PR-A through PR-E.
- [`PLATFORM_INVENTORY.md`](../PLATFORM_INVENTORY.md) — runtime
  inventory; regenerable.
- [`PLATFORM_WHAT_IT_IS.md`](../PLATFORM_WHAT_IT_IS.md) — narrative
  anchor.
