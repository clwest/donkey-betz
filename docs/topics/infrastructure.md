<!-- DOC-POINTER-V1 -->
> **⚠ Stats in this doc may drift from code.** For current verified numbers see [`../PLATFORM_INVENTORY.md`](/docs/PLATFORM_INVENTORY.md) (sole authoritative counts per `DOC_LIFECYCLE.md` §2c). Run `python manage.py verify_doc_claims --only-drift` to see which specific claims currently diverge from runtime reality (Session 1099 verifier).

# Infrastructure & Deployment

Django web application deployed on Railway with Redis, PostgreSQL (pgvector), and Celery workers.

## Stack

- **Backend:** Django 4.2+ with Daphne (ASGI)
- **Database:** PostgreSQL with pgvector extension (570 concrete models across 23 apps)
- **Cache/Broker:** Redis (DB1: cache, DB2: broker, DB3: results — 3 distinct DBs in settings.py; channel layer uses default)
- **Task Queue:** Celery with 7 worker processes + beat + code-worker + resolve-node = 10 Procfile celery-tier entries (see celery-workers.md)
- **Frontend:** React + TypeScript + Vite + Tailwind
- **LLM Providers:** OpenAI (GPT-5), Anthropic (Claude 4), Together AI, Ollama, DeepSeek, Gemini

## Railway Deployment

- **Environment detection:** `os.environ.get('RAILWAY_ENVIRONMENT')`
- **Healthcheck:** 600s timeout (increased for migration-heavy deploys)
- **Start command:** `sh -c` wrapper required for `$PORT` expansion
- **Ephemeral filesystem:** Workspace file writes fail between deploys (expected, not a bug)
- **Blue-green deploys:** Migrations can hang on lock during deploy; temporarily remove from start command if needed
- **Workspace path self-healing (Session 1034):** `_get_workspace_for_skin_layer()` auto-detects stale local macOS paths (stored in DB), recomputes from `__file__`, and updates the DB record. Handles Railway vs local path mismatch.
- **Cost budget:** $1,500/month (raised from $1,200 in Session 1034). Schedule throttling reduces unnecessary task runs.

## Release Command (Procfile)

The `release:` line runs on every Railway deploy:

```
release: python manage.py migrate --noinput && python manage.py sync_celery_beat --apply --create-only --disable-missing && python manage.py sync_task_queues --apply && python manage.py setup_codebase_workspace
```

| Step | Purpose |
|------|---------|
| `migrate` | Apply DB migrations |
| `sync_celery_beat` | Create/disable PeriodicTask records from celery.py definitions |
| `sync_task_queues` | Sync PeriodicTask.queue fields to match CELERY_TASK_ROUTES (Session 1064) |
| `setup_codebase_workspace` | Initialize workspace file structure |

## Settings

- **Module:** `core.settings` (NOT `config.settings`)
- **Test with:** `DJANGO_SETTINGS_MODULE=core.settings`

## Database Notes

- Both `core/models.py` (file) AND `core/models/` (package) exist — Django uses the PACKAGE
- New model imports go in `core/models/__init__.py` with `from ..models_xxx import ClassName`
- New external models MUST have `app_label = 'core'` in Meta
- DO NOT add imports to `core/models.py` — it's dead code

## GPT-5-mini Configuration

```python
# Reasoning model — different parameters
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

## Discord Integration

112 bot commands across 12 notification channels. See `docs/DISCORD_INTEGRATION.md` for full command list and ACTIVE/DORMANT status.
