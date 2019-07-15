from celery import Celery

from nrc.setup import setup_env

setup_env()

app = Celery("nrc")

app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
