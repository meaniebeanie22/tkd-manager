import os

from celery import Celery

app = Celery("tkdmanager")

app.config_from_object("django.conf:settings", namespace="CELERY")

# Load task modules from all registered Django apps.
app.autodiscover_tasks()


@app.task(bind=True, ignore_result=True)
def example_task(self):
    print("You've triggered the example task!")