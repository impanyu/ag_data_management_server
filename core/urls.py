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


# Add CORS-enabled static files serving for converted_static_files (for ArcGIS Online access)
# IMPORTANT: This must be BEFORE the home.urls include to avoid being caught by the catch-all pattern
from apps.home.views import serve_static_file_with_cors
from django.http import JsonResponse

# Simple debug endpoint to test API routing
def debug_api_test(request):
    return JsonResponse({
        "success": True,
        "message": "API routing works!",
        "path": request.path,
        "user_authenticated": request.user.is_authenticated if hasattr(request, 'user') else False
    })

static_files_patterns = [
    re_path(r'^static_files/(?P<file_path>.*)$', serve_static_file_with_cors, name='serve_static_with_cors'),
    path('debug-api-test/', debug_api_test, name='debug_api_test'),
]

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

