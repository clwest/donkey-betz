# Session 984: Switch Railway workers to prefork pool for memory recycling
# --pool=threads ignores max_tasks_per_child (threads share one process, memory never recycles)
# --pool=prefork on Linux (Railway) recycles child processes after 50 tasks, capping memory growth
# --max-memory-per-child=300000 (300MB) kills children that exceed limit
# macOS local dev should still use --pool=threads (prefork causes SIGSEGV) via Makefile
release: python manage.py migrate --noinput && python manage.py sync_celery_beat --apply && python manage.py setup_codebase_workspace
web: daphne -b 0.0.0.0 -p ${PORT:-8000} --http-timeout 120 --application-close-timeout 120 core.asgi:application
celery-worker: celery -A core worker -l info --pool=prefork -c 2 --max-tasks-per-child=50 --max-memory-per-child=300000 -Q default,agents,sports,ml
celery-pa: celery -A core worker -l info --pool=prefork -c 2 --max-tasks-per-child=50 --max-memory-per-child=300000 -Q pa
celery-content: celery -A core worker -l info --pool=prefork -c 2 --max-tasks-per-child=30 --max-memory-per-child=300000 -Q content
celery-long-running: celery -A core worker -l info --pool=prefork -c 1 --max-tasks-per-child=10 --max-memory-per-child=500000 -Q long_running
celery-broadcast: celery -A core worker -l info --pool=prefork -c 2 --max-tasks-per-child=50 --max-memory-per-child=300000 -Q broadcast
celery-beat: celery -A core beat -l info
