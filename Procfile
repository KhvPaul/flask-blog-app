web: gunicorn wsgi:app
worker: celery -A celery_worker.celery worker -l INFO