# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.contrib import admin
from apps.home import views
from django.urls import path, re_path,include  # add this
from django.conf.urls.static import static
from django.conf import settings


from apps.home import api
from django.contrib.auth.models import User
from rest_framework import routers, serializers, viewsets


# Add static files serving for converted_static_files (for ArcGIS Online access)
# IMPORTANT: This must be BEFORE the home.urls include to avoid being caught by the catch-all pattern
static_files_patterns = static('/static_files/', document_root = settings.CONVERTED_STATIC_FILES_ROOT)

urlpatterns = [
    path('admin/', admin.site.urls),          # Django admin route
    path('accounts/', include('allauth.urls')),
    path('yt/', include('apps.yt_api.urls')),
    path("", include("apps.authentication.urls")),  # Auth routes - login / register
] + static_files_patterns + [
    path("", include("apps.home.urls")),      # UI Kits Html files - MUST BE LAST due to catch-all pattern
]

#urlpatterns += router.urls

# only in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)

