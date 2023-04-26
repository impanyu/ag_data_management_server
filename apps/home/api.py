# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

#from osgeo import gdal,osr
#from osgeo.gdalconst import GA_ReadOnly


from django import template
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.template import loader
from django.urls import reverse
from .data import *
from django.views.decorators.csrf import csrf_exempt

from django.contrib.auth import authenticate
from django.http import JsonResponse



@csrf_exempt
def data(request):
    context = {}
    # All resource paths end in .html.
    # Pick out the html file name from the url. And load that template.
    try:
        load_template = request.path.split('/')[-1]
        load_template = load_template.split('?')[0]

        if load_template == 'api_meta_data':
            current_path = request.GET['current_path']
            api_key = request.GET['key']
            user = current_path.split("/")[1]
            meta_data = {}
            api_keys = get_api_keys()
            if api_key in api_keys and user in api_keys[api_key]:
                meta_data = get_meta_data("/data" + current_path)
            else:
                meta_data = "API key is not valid!"
            response = json.dumps(meta_data)
            return HttpResponse(response)

    except template.TemplateDoesNotExist:

        html_template = loader.get_template('home/page-404.html')
        return HttpResponse(html_template.render(context, request))

    except:
        html_template = loader.get_template('home/page-500.html')
        return HttpResponse(html_template.render(context, request))