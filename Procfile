release: python manage.py migrate --noinput && python manage.py sync_celery_beat --apply && python manage.py setup_codebase_workspace
web: daphne -b 0.0.0.0 -p ${PORT:-8000} --http-timeout 120 --application-close-timeout 120 core.asgi:application
celery-worker: celery -A core worker -l info --pool=threads -c 4 -Q default,agents,sports,ml
celery-content: celery -A core worker -l info --pool=threads -c 4 -Q content
celery-long-running: celery -A core worker -l info --pool=threads -c 2 -Q long_running
celery-broadcast: celery -A core worker -l info --pool=threads -c 2 -Q broadcast
celery-beat: celery -A core beat -l info
