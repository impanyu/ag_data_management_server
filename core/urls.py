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


urlpatterns = [
    path('admin/', admin.site.urls),          # Django admin route
    path('accounts/', include('allauth.urls')),
    path('yt_api/', include('apps.yt_api.urls')),
    path("", include("apps.authentication.urls")), # Auth routes - login / register
    path("", include("apps.home.urls"))             # UI Kits Html files
    

]

#urlpatterns += router.urls

# only in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)

