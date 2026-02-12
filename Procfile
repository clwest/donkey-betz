# Session 985: Reduced celery-worker to -c 1 and 200MB after repeated OOM crashes
# Parent process holds ~200MB from imports (262 tasks, 76 agents, TensorFlow, etc.)
# With -c 2 + 300MB children, peak = ~800MB which exceeds Railway limits
# With -c 1 + 200MB child, peak = ~400MB — much safer
# --pool=prefork on Linux (Railway) recycles child processes after 50 tasks
# macOS local dev should still use --pool=threads (prefork causes SIGSEGV) via Makefile
release: python manage.py migrate --noinput && python manage.py sync_celery_beat --apply && python manage.py setup_codebase_workspace
web: daphne -b 0.0.0.0 -p ${PORT:-8000} --http-timeout 120 --application-close-timeout 120 core.asgi:application
celery-worker: celery -A core worker -l info --pool=prefork -c 1 --max-tasks-per-child=50 --max-memory-per-child=200000 -Q default,agents,sports,ml
celery-pa: celery -A core worker -l info --pool=prefork -c 1 --max-tasks-per-child=50 --max-memory-per-child=200000 -Q pa
celery-content: celery -A core worker -l info --pool=prefork -c 1 --max-tasks-per-child=30 --max-memory-per-child=200000 -Q content
celery-long-running: celery -A core worker -l info --pool=prefork -c 1 --max-tasks-per-child=10 --max-memory-per-child=300000 -Q long_running
celery-broadcast: celery -A core worker -l info --pool=threads -c 1 --max-tasks-per-child=50 --max-memory-per-child=200000 -Q broadcast
celery-beat: celery -A core beat -l info
