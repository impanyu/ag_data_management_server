# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.urls import path, re_path
from apps.home import views
from django.conf.urls.static import static
from django.conf import settings


urlpatterns = [

    # The home page
    #path('', views.index, name='home'),
    re_path(r'^create_new_domain',views.data,name='create_new_domain'),
    re_path(r'^domain_data',views.data,name='domain_data'),
    re_path(r'^domain_time',views.data,name='domain_time'),
    re_path(r'^file_system',views.data,name='file_system'),
    re_path(r'^add_domain',views.data,name='add_domain'),
    re_path(r'^canopy_height',views.data,name='canopy_height'),
    re_path(r'^canopy_coverage_and_temperature',views.data,name='canopy_coverage_and_temperature'),
    re_path(r'^upload_file',views.data,name='upload_file'),
    re_path(r'^delete_file',views.data,name='delete_file'),
    # Matches any html file
    re_path(r'^.*\.*', views.pages, name='pages')
]




