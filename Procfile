web: daphne -b 0.0.0.0 -p ${PORT:-8000} --http-timeout 120 --application-close-timeout 120 core.asgi:application
celery-default: celery -A core worker -l info --pool=threads -c 4 -Q default,agents,sports,content,ml
celery-long-running: celery -A core worker -l info --pool=threads -c 2 -Q long_running
celery-broadcast: celery -A core worker -l info --pool=threads -c 2 -Q broadcast
celery-beat: celery -A core beat -l info
