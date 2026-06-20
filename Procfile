# Session 1000C: Routed 60+ heavy tasks off default queue to prevent OOM
# Parent process holds ~200MB from imports (331 tasks, 82 agents, etc.)
# With -c 1 + 200MB child, peak = ~400MB — fits Railway 512MB limit
# Reduced max-tasks-per-child: celery-worker 50→25→10→5 (Session 1000C OOM fix, lowered again Feb 2026)
# Session 1065: Moved 7 heavy tasks off default→long_running, lowered child memory limit 200→150MB
# Session 1003: Bumped pa to -c 2 (lighter tasks), broadcast to -c 3 (threads pool)
# Session 1068: PA back to -c 1, max-tasks 10, memory 200MB (enrichment caused 4GB spikes)
# Session 1009: Reduced content from -c 2 → -c 1 (OOM fix: deliberation + dream tasks are memory-heavy)
# Session 1040: Moved 5 heaviest tasks off content→long_running, recycle 5→2 tasks (repeated OOM with 25+ initiatives)
# Feb 2026: Reduced long_running from -c 3 → -c 1, max-tasks 10→3 (OOM: 3 concurrent heavy tasks + 200MB parent exceeds 512MB)
# Mar 2026: Bumped long_running -c 1 → -c 2 to prevent queue saturation, lowered child memory 250→150MB and tasks 3→2 to fit 512MB (200MB parent + 2×150MB = 500MB)
# Mar 2026: Added celery-long-running-2 — second worker for long_running,ml queues. Total capacity: 2 containers × 2 concurrency = 4 parallel slots
# --pool=prefork on Linux (Railway) recycles child processes after N tasks
# macOS local dev should still use --pool=threads (prefork causes SIGSEGV) via Makefile
#
# Session 1166 (COO Backlog item #2, MUST): every entry sets PG_APPLICATION_NAME=dbz:<role>
# so `SELECT application_name, count(*) FROM pg_stat_activity GROUP BY 1` shows a per-component
# breakdown. Tag scheme: dbz:<procfile-entry-name>. Verified at strict mode by
# scripts/verify_repo_guardrails.py (regex ^dbz:[a-z0-9\-]+$ on every entry).
# release runs only during deploys — its tag appears briefly then vanishes.
# resolve-node is a separate FastAPI service (port 5001) that doesn't hit the unified_donkey_betz
# Postgres in practice; tagging uniformly avoids special-case verifier debt.
release: PG_APPLICATION_NAME=dbz:release sh -c "chown -R appuser:appuser /app/workspaces 2>/dev/null || true; python manage.py collectstatic --noinput && python manage.py migrate --noinput && python manage.py sync_celery_beat --apply --create-only --disable-missing && python manage.py sync_task_queues --apply && python manage.py setup_codebase_workspace && python manage.py setup_pa_service_account"
web: PG_APPLICATION_NAME=dbz:web daphne -b 0.0.0.0 -p ${PORT:-8000} --http-timeout 120 --application-close-timeout 120 core.asgi:application
celery-worker: PG_APPLICATION_NAME=dbz:celery-worker celery -A core worker -l info --pool=prefork -c 1 --max-tasks-per-child=5 --max-memory-per-child=150000 -Q default,agents,sports
celery-pa: PG_APPLICATION_NAME=dbz:celery-pa celery -A core worker -l info --pool=prefork -c 1 --max-tasks-per-child=10 --max-memory-per-child=200000 -Q pa
celery-content: PG_APPLICATION_NAME=dbz:celery-content celery -A core worker -l info --pool=prefork -c 1 --max-tasks-per-child=2 --max-memory-per-child=250000 -Q content
celery-long-running: PG_APPLICATION_NAME=dbz:celery-long-running celery -A core worker -l info --pool=prefork -c 2 --max-tasks-per-child=2 --max-memory-per-child=150000 -Q long_running,ml
celery-long-running-2: PG_APPLICATION_NAME=dbz:celery-long-running-2 celery -A core worker -l info --pool=prefork -c 2 --max-tasks-per-child=2 --max-memory-per-child=150000 -Q long_running,ml
celery-broadcast: PG_APPLICATION_NAME=dbz:celery-broadcast celery -A core worker -l info --pool=threads -c 3 --max-tasks-per-child=50 --max-memory-per-child=200000 -Q broadcast
celery-beat: PG_APPLICATION_NAME=dbz:celery-beat celery -A core beat -l info
code-worker: PG_APPLICATION_NAME=dbz:code-worker celery -A core worker -l info --pool=prefork -c 1 --max-tasks-per-child=1 --max-memory-per-child=400000 -Q code_jobs
resolve-node: PG_APPLICATION_NAME=dbz:resolve-node sh -c "cd resolve_node && MOCK_MODE=true uvicorn app:app --host 0.0.0.0 --port ${PORT:-5001}"
