# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

import os


from django.core.wsgi import get_wsgi_application

import sys
import logging


# Redirect stdout and stderr to log files
sys.stdout = open('/home/ypan12/ag_data_management_server/log/debug.log', 'a+')
sys.stderr = open('/home/ypan12/ag_data_management_server/log/debug.log', 'a+')




os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

application = get_wsgi_application()
