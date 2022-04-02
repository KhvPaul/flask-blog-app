web: gunicorn wsgi:app
worker: celery worker -A celery_worker.celery -l INFO & celery beat -A celery_worker.celery -l INFO