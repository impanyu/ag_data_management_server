from celery import shared_task
from django.core.management import call_command

@shared_task
def update_top_chinese_channels_task():
    call_command('update_top_chinese_channels', initialize=False)

@shared_task
def initialize_top_chinese_channels_task():
    call_command('update_top_chinese_channels', initialize=True)    

@shared_task
def debug_task():
    print("Task executed")