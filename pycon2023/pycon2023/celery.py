import os

from celery import Celery
from datetime import timedelta


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pycon2023.settings')

app = Celery('pycon2023')
app.config_from_object('django.conf:settings', namespace='CELERY')

app.conf.beat_schedule = {
    "chat_facts": {
        "task": "chat.tasks.send_chat_facts",
        "schedule": timedelta(seconds=3),
    }
}

app.autodiscover_tasks()