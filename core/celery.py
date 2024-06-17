
from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
import sys
from django.conf import settings

# Redirect stdout and stderr to log files
sys.stdout = open('/var/log/ag_data_management/debug.log', 'a+')
sys.stderr = open('/var/log/ag_data_management/debug.log', 'a+')

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')



# Print to verify the concurrency setting
print(f"CELERY_WORKER_CONCURRENCY: {settings.CELERY_WORKER_CONCURRENCY}")
# Print environment variables for debugging
print(f"CELERY_BROKER_URL: {os.environ.get('CELERY_BROKER_URL')}")
print(f"CELERY_RESULT_BACKEND: {os.environ.get('CELERY_RESULT_BACKEND')}")
print(f"CELERY_WORKER_CONCURRENCY: {os.environ.get('CELERY_WORKER_CONCURRENCY')}")



app = Celery('core')
# Celery Configuration
app.conf.update(
    broker_url='redis://localhost:6379/0',
    result_backend='redis://localhost:6379/0',
    accept_content=['json'],
    task_serializer='json',
    result_serializer='json',
    timezone='UTC',
    worker_concurrency=5,
    beat_schedule={
        'update-top-chinese-channels': {
            'task': 'apps.yt_api.tasks.update_top_chinese_channels_task',
            'schedule': 3600,  # Adjust the schedule as needed
        },
    },
)


app.config_from_object('core:settings', namespace='CELERY')
app.autodiscover_tasks()
