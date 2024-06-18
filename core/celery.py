
from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
import sys
from django.conf import settings
import logging

# Redirect stdout and stderr to log files
sys.stdout = open('/var/log/ag_data_management/debug.log', 'a+')
sys.stderr = open('/var/log/ag_data_management/debug.log', 'a+')

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')


# Print to verify the concurrency setting
print(f"CELERY_WORKER_CONCURRENCY: {settings.CELERY_WORKER_CONCURRENCY}")



app = Celery('core')


#app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()

# Configure logging
logging.basicConfig(filename='/var/log/ag_data_management/celery.log',
                    level=logging.INFO,
                    format='%(asctime)s %(levelname)s %(message)s')