# Session 1000C: Routed 60+ heavy tasks off default queue to prevent OOM
# Parent process holds ~200MB from imports (331 tasks, 82 agents, etc.)
# With -c 1 + 200MB child, peak = ~400MB — fits Railway 512MB limit
# Reduced max-tasks-per-child: celery-worker 50→25→10 (Session 1000C OOM fix)
# --pool=prefork on Linux (Railway) recycles child processes after N tasks
# macOS local dev should still use --pool=threads (prefork causes SIGSEGV) via Makefile
release: python manage.py migrate --noinput && python manage.py sync_celery_beat --apply && python manage.py setup_codebase_workspace
web: daphne -b 0.0.0.0 -p ${PORT:-8000} --http-timeout 120 --application-close-timeout 120 core.asgi:application
celery-worker: celery -A core worker -l info --pool=prefork -c 1 --max-tasks-per-child=10 --max-memory-per-child=200000 -Q default,agents,sports
celery-pa: celery -A core worker -l info --pool=prefork -c 1 --max-tasks-per-child=50 --max-memory-per-child=200000 -Q pa
celery-content: celery -A core worker -l info --pool=prefork -c 1 --max-tasks-per-child=30 --max-memory-per-child=200000 -Q content
celery-long-running: celery -A core worker -l info --pool=prefork -c 1 --max-tasks-per-child=10 --max-memory-per-child=300000 -Q long_running,ml
celery-broadcast: celery -A core worker -l info --pool=threads -c 1 --max-tasks-per-child=50 --max-memory-per-child=200000 -Q broadcast
celery-beat: celery -A core beat -l info
