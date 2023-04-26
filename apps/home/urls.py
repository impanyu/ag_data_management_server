# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.urls import path, re_path
from apps.home import views
from apps.home import api
from django.conf.urls.static import static
from django.conf import settings


urlpatterns = [

    # The home page
    path('', views.index, name='home'),
    path('api/authenticate/', views.authenticate_user, name='authenticate_user'),
    re_path(r'^api_list_sub_items',api.data,name='api_list_sub_items'),
    re_path(r'^api_meta_data',api.data,name='api_meta_data'),
    re_path(r'^get_running_containers',views.data,name='get_running_containers'),
    re_path(r'^get_collections',views.data,name='get_collections'),
    re_path(r'^duplicate',views.data,name='duplicate'),
    re_path(r'^remove_from_collection',views.data,name='remove_from_collection'),
    re_path(r'^create_collection',views.data,name='create_collection'),
    re_path(r'^add_to_collection',views.data,name='add_to_collection'),
    re_path(r'^file_system_virtual',views.data,name='file_system_virtual'),
    re_path(r'^get_pipeline',views.data,name='get_pipeline'),
    re_path(r'^run_tool',views.data,name='run_tool'),
    re_path(r'^create_file',views.data,name='create_file'),
    re_path(r'^create_folder',views.data,name='create_folder'),
    re_path(r'^update_file',views.data,name='update_file'),
    re_path(r'^download_file',views.data,name='download_file'),
    re_path(r'^get_file',views.data,name='get_file'),
    re_path(r'^update_meta',views.data,name='update_meta'),
    re_path(r'^meta_data',views.data,name='meta_data'),
    re_path(r'^mode_search',views.data,name='search'),
    re_path(r'^query_domain',views.data,name='query_domain'),
    re_path(r'^get_tif_range',views.data,name='get_tif_range'),
    re_path(r'^get_domains',views.data,name='get_domains'),
    re_path(r'^get_domains_meta',views.data,name='get_domains_meta'),

    re_path(r'^add_to_domain',views.data,name='add_to_domain'),
    re_path(r'^create_domain',views.data,name='create_domain'),
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




