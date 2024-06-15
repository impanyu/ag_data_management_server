from celery import shared_task
from django.core.management import call_command

@shared_task
def update_top_channels_task():
    call_command('update_top_channels')


@shared_task
def update_channels():
    call_command('update_channels')