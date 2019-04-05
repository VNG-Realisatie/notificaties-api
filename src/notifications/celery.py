import os

from celery import Celery

from notifications.setup import setup_env

setup_env()

app = Celery("notifications")

app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
