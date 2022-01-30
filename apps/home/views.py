# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django import template
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.urls import reverse
from .data import * 
from django.views.decorators.csrf import csrf_exempt

import json
from django.core.files.storage import FileSystemStorage
from django.conf import settings
import os


@login_required(login_url="/login/")
def index(request):
    context = {'segment': 'index'}

    html_template = loader.get_template('home/domains.html')
    return HttpResponse(html_template.render(context, request))


@login_required(login_url="/login/")
def pages(request):
    context = {}
    # All resource paths end in .html.
    # Pick out the html file name from the url. And load that template.
    try:


        load_template = request.path.split('/')[-1]
        load_template = load_template.split('?')[0]

        if load_template == 'admin':
            return HttpResponseRedirect(reverse('admin:index'))

        elif load_template == 'domain_display':  
            
            context['domain'] = request.GET['domain']

            domain_path = "/"+context['domain']
            print(request.session.keys())



            subdomains = retrieve_sub_domains(domain_path,request.session)

 

            subdomain_paths= ["/"+context['domain']+'/'+subdomain for subdomain in subdomains]

            context["subdomain_paths"]= subdomain_paths
            context['layers'] = retrieve_layers(subdomain_paths[0])
            context['times'] = retrieve_times(subdomain_paths[0],request.session)
     


            context['segment'] = load_template

            html_template = loader.get_template('home/domain_display.html')

            return HttpResponse(html_template.render(context, request))

        elif load_template == "files.html":
            context['current_path'] = request.GET['current_path']
            context['segment'] = load_template

            html_template = loader.get_template('home/files.html')
            return HttpResponse(html_template.render(context, request))

          

        context['segment'] = load_template

        html_template = loader.get_template('home/' + load_template)
        return HttpResponse(html_template.render(context, request))

    except template.TemplateDoesNotExist:

        html_template = loader.get_template('home/page-404.html')
        return HttpResponse(html_template.render(context, request))

    except:
        html_template = loader.get_template('home/page-500.html')
        return HttpResponse(html_template.render(context, request))







@login_required(login_url="/login/")
@csrf_exempt
def data(request):
    context = {}
    # All resource paths end in .html.
    # Pick out the html file name from the url. And load that template.
    try:
      
        load_template = request.path.split('/')[-1]
        load_template = load_template.split('?')[0]

        if load_template == 'domain_data':  
            subdomain_path = request.POST['subdomain_path']
            layer = request.POST['layer']
            time = request.POST['time']




            url=retrieve_sub_domain_data(subdomain_path,layer,time)
            

            #url = "/static/assets/img/brand/ianr_bg.jpg" 

            
            return HttpResponse(url)

        elif load_template == 'add_domain':
            time = request.POST['time']
            subdomain=request.POST['subdomain']
            #request.session.clear()
            print(subdomain)
            print(time)
            if subdomain not in request.session:
                request.session[subdomain]={time:True}

            else:
                request.session[subdomain][time]=True
            request.session.modified=True
            print(request.session[subdomain])


            return HttpResponse("")
            
                



        elif load_template == 'domain_time':  
            subdomain_path = request.POST['subdomain_path']
            times=retrieve_times(subdomain_path,request.session)
            
            return HttpResponse(json.dumps(times))

        elif load_template == 'file_system':
            file_path = request.POST['current_path']
            fs = FileSystemStorage(location=os.path.join(settings.CORE_DIR, 'data')+"/users")
            dirs,files=fs.listdir(file_path)

            response={"dirs":[], "files":[]}
           
            for dir in dirs:
                created_time=fs.get_created_time(file_path+"/"+dir)
                accessed_time=fs.get_accessed_time(file_path+"/"+dir)
                size=fs.size(file_path+"/"+dir)
                dir_item={"dir_name":dir,"created_time":created_time.strftime("%m/%d/%Y, %H:%M:%S"),"accessed_time":accessed_time.strftime("%m/%d/%Y, %H:%M:%S"),"size":size}
                response["dirs"].append(dir_item)

            for file in files:
                created_time=fs.get_created_time(file_path+"/"+file)
                accessed_time=fs.get_accessed_time(file_path+"/"+file)
                size=fs.size(file_path+"/"+file)
                file_item={"file_name":file,"created_time":created_time.strftime("%m/%d/%Y, %H:%M:%S"),"accessed_time":accessed_time.strftime("%m/%d/%Y, %H:%M:%S"),"size":size}
                response["files"].append(file_item)
            


            response=json.dumps(response)


            return HttpResponse(response)




    except template.TemplateDoesNotExist:

        html_template = loader.get_template('home/page-404.html')
        return HttpResponse(html_template.render(context, request))

    except:
        html_template = loader.get_template('home/page-500.html')
        return HttpResponse(html_template.render(context, request))