# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

#from osgeo import gdal,osr
#from osgeo.gdalconst import GA_ReadOnly


from django import template
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.urls import reverse
from .data import *
from django.views.decorators.csrf import csrf_exempt
import stat
from pwd import getpwnam

import json
from django.core.files.storage import FileSystemStorage
from django.conf import settings
import os
import shutil
from .forms import UploadFileForm


# import matlab.engine as mat_eng


@login_required(login_url="/login/")
def index(request):
    context = {'segment': 'index'}

    print("in domains")
    domains = get_domains()

    context["domains"] = domains

    html_template = loader.get_template('home/main.html')
    return HttpResponse(html_template.render(context, request))


@login_required(login_url="/login/")
def pages(request):
    context = {}
    # All resource paths end in .html.
    # Pick out the html file name from the url. And load that template.
    try:

        load_template = request.path.split('/')[-1]

        load_template = load_template.split('?')[0]


        if load_template == "domain_main_page":
            context['segment'] = load_template
            context['domain'] = request.GET["domain"]
            domain_meta = get_domain_meta(request.GET["domain"])
            context['bounding_box'] = domain_meta["bounding_box"]

            html_template = loader.get_template('home/domain_main_page.html')
            return HttpResponse(html_template.render(context, request))

        elif load_template == 'domains.html':
            context = {'segment': 'index'}
            #print("in domains")
            domains = get_domains()

            domain_names=[]
            for domain_name in domains:
                domain_names.append(domain_name)

            context["domains"] = domain_names

            html_template = loader.get_template('home/domains.html')
            return HttpResponse(html_template.render(context, request))

        elif load_template == 'admin':
            return HttpResponseRedirect(reverse('admin:index'))

        elif load_template == 'domain_display':

            context['domain'] = request.GET["app"]

            domain_path = "/" + context['domain']
            # print(request.session.keys())

            subdomains = retrieve_sub_domains(domain_path, request.session)

            subdomain_paths = [domain_path + '/' + subdomain for subdomain in subdomains]

            context["subdomain_paths"] = subdomain_paths

            context['times'] = retrieve_times(subdomain_paths[0], request.session)
            context['layers'] = retrieve_layers(subdomain_paths[0])
            context['segment'] = load_template

            context['app'] = request.GET.get('app', "")
            context['location'] = request.GET.get('location', "")
            context['time'] = request.GET.get("time", "")
            context['layer'] = request.GET.get("layer", "")

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

        if load_template == 'query_domain':
            domain_name = request.POST.get("domain_name", "")
            start_date = request.POST.get("start_date", "")
            end_date = request.POST.get("end_date", "")
            southwest = request.POST.get("southwest", "")
            northeast = request.POST.get("northeast", "")
            query_range = request.POST.get("query_range", "")
            query_result = query_domain(domain_name,start_date,end_date,southwest,northeast,query_range,request.user.get_username())
            return HttpResponse(query_result)

        elif load_template == 'get_domains':
            domains = get_domains()
            return HttpResponse(json.dumps(list(domains.keys())))

        elif load_template == 'get_domains_meta':
            domains = get_domains()
            return HttpResponse(json.dumps(domains))

        elif load_template == 'add_to_domain':
            domain_name = request.POST.get("domain_name", "")
            start_date = request.POST.get("start_date", "")
            end_date = request.POST.get("end_date", "")
            southwest = request.POST.get("southwest", "")
            northeast = request.POST.get("northeast", "")
            data_content = request.POST.get("data_content","")

            add_to_domain(domain_name,start_date,end_date,southwest,northeast,data_content)
            return HttpResponse("item added to domain")

        elif load_template == 'create_new_domain':
            new_domain_name = request.POST.get("new_domain_name","")
            start_date = request.POST.get("start_date", "")
            end_date = request.POST.get("end_date","")
            southwest = request.POST.get("southwest","")
            northeast = request.POST.get("northeast","")


            create_new_domain(new_domain_name,start_date,end_date,southwest,northeast)


            return HttpResponse("domain created")


        elif load_template == 'domain_data':
            subdomain_path = request.GET.get('subdomain_path', "")
            layer = request.POST.get('layer', "")
            time = request.POST.get('time', "")

            # if(load_template.split('?')[1])=="app=soilwater"

            # data=retrieve_sub_domain_data(subdomain_path,layer,time,request.session)

            app = request.GET.get("app", "")
            plot = request.GET.get("plot", "")
            time = request.GET.get("time", "")
            layer = request.GET.get("layer", "")
            meta = request.GET.get("meta", "")
            # print(app)

            if app == "spidercam":
                data = retrieve_data(app, plot, time, layer, meta)
            elif app == "soilwater":
                data = retrieve_sub_domain_data(subdomain_path, layer, time, request.session)

            # url = "/static/assets/img/brand/ianr_bg.jpg"

            return HttpResponse(data)

        elif load_template == 'add_domain':
            time = request.POST['time']
            subdomain = request.POST['subdomain']
            # request.session.clear()
            print(subdomain)
            print(time)
            if subdomain not in request.session:
                request.session[subdomain] = {time: True}
            else:
                request.session[subdomain][time] = True
            request.session.modified = True
            print(request.session[subdomain])

            return HttpResponse("")

        elif load_template == 'canopy_height':
            dir_name = request.POST['dir_name']
            time = request.POST['time']
            subdomain = request.POST['subdomain']

            dir_path = os.path.join(settings.CORE_DIR, 'data/users/impanyu/winterwheatDataExample', dir_name)
            # print(dir_path)

            eng = mat_eng.start_matlab()
            matlab_scripts_dir = os.path.join(settings.CORE_DIR, 'data/users/impanyu/matlab_scripts')
            eng.cd(matlab_scripts_dir)
            height = eng.Process_LiDAR(dir_path)
            print(height)
            fs_cache = FileSystemStorage(location=os.path.join(settings.CORE_DIR, 'data') + "/data_cache")
            output_file_name = subdomain + "_" + time + "_all"

            if not fs_cache.exists(output_file_name):
                all_layers = {}
            else:
                with fs_cache.open(output_file_name, "r") as output_file:
                    all_layers = json.load(output_file)

            with fs_cache.open(output_file_name, "w") as output_file:
                all_layers["canopy_height"] = height

                json.dump(all_layers, output_file)

            return HttpResponse("")

        elif load_template == 'canopy_coverage_and_temperature':
            dir_name = request.POST['dir_name']
            time = request.POST['time']
            subdomain = request.POST['subdomain']

            dir_path = os.path.join(settings.CORE_DIR, 'data/users/impanyu/winterwheatDataExample', dir_name)
            # print(dir_path)

            eng = mat_eng.start_matlab()
            matlab_scripts_dir = os.path.join(settings.CORE_DIR, 'data/users/impanyu/matlab_scripts')
            eng.cd(matlab_scripts_dir)
            canopy_coverage_and_temperature = eng.Process_VNIRThermal(dir_path)

            fs_cache = FileSystemStorage(location=os.path.join(settings.CORE_DIR, 'data') + "/data_cache")
            output_file_name = subdomain + "_" + time + "_all"

            if not fs_cache.exists(output_file_name):
                all_layers = {}
            else:
                with fs_cache.open(output_file_name, "r") as output_file:
                    all_layers = json.load(output_file)

            with fs_cache.open(output_file_name, "w") as output_file:
                all_layers["canopy_coverage_and_temperature"] = canopy_coverage_and_temperature

                json.dump(all_layers, output_file)
            return HttpResponse("")

        elif load_template == 'domain_time':
            subdomain_path = request.POST['subdomain_path']
            times = retrieve_times(subdomain_path, request.session)

            return HttpResponse(json.dumps(times))

        elif load_template == "upload_file":
            current_path = request.POST['current_path']
            print(current_path)
            upload_files = request.FILES.getlist("files")
            upload_file_paths = request.POST.getlist("paths")

            modified_current_path = ""

            for i in range(1, len(current_path.split("/"))):
                modified_current_path += "/" + current_path.split("/")[i]

            if modified_current_path == "":
                current_path = "."
            else:
                current_path = modified_current_path[1:]

            if not upload_files:
                return HttpResponse('files not found')
            else:
                for file in upload_files:
                    position = os.path.join(
                        os.path.join("/home/" + request.user.get_username() + "/ag_data/", current_path),
                        '/'.join(upload_file_paths[upload_files.index(file)].split('/')[:-1]))

                    if not os.path.exists(position):
                        os.makedirs(position)
                    abs_file_path = position + "/" + file.name
                    print(abs_file_path)
                    copy_id = 1
                    if os.path.exists(abs_file_path):
                        while os.path.exists(abs_file_path + "_" + str(copy_id)):
                            copy_id += 1

                        abs_file_path += "_" + str(copy_id)

                    storage = open(abs_file_path, "wb+")

                    for chunk in file.chunks():
                        storage.write(chunk)
                    storage.close()

                    os.chmod(abs_file_path,stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR)
                    #os.chown(abs_file_path,getpwnam(request.user.get_username()).pw_uid,-1)

                return HttpResponse("upload complete!")

                # return HttpResponse("upload complete!")

        elif load_template == "delete_file":
            file_path = request.POST['current_path']
            file_name = request.POST['file_name']

            modified_file_path = ""
            for i in range(1, len(file_path.split("/"))):
                modified_file_path += "/" + file_path.split("/")[i]

            if modified_file_path == "":
                file_path = "."
            else:
                file_path = modified_file_path[1:]

            abs_path = "/home/" + request.user.get_username() + "/ag_data/" + file_path + "/" + file_name

            if os.path.isdir(abs_path):
                # shutil.rmtree(os.path.join(settings.CORE_DIR, 'data/users', current_path, file_name))
                shutil.rmtree(abs_path)
            else:
                os.remove(abs_path)
            return HttpResponse("delete complete!")

        elif load_template == 'file_system':
            file_path = request.POST['current_path']
            fs = FileSystemStorage(location=os.path.join(settings.CORE_DIR, 'data') + "/users")
            fs = FileSystemStorage(location="/home/" + request.user.get_username() + "/ag_data")

            print(request.user.get_username())

            modified_file_path = ""
            for i in range(1, len(file_path.split("/"))):
                modified_file_path += "/" + file_path.split("/")[i]

            if modified_file_path == "":
                file_path = "."
            else:
                file_path = modified_file_path[1:]

            dirs, files = fs.listdir(file_path)

            response = {"dirs": [], "files": []}

            for dir in dirs:
                if dir[0] == ".":
                    continue
                created_time = fs.get_created_time(file_path + "/" + dir)
                accessed_time = fs.get_accessed_time(file_path + "/" + dir)
                size = fs.size(file_path + "/" + dir)
                dir_item = {"dir_name": dir, "created_time": created_time.strftime("%m/%d/%Y, %H:%M:%S"),
                            "accessed_time": accessed_time.strftime("%m/%d/%Y, %H:%M:%S"), "size": size}
                response["dirs"].append(dir_item)

            for file in files:
                if file[0] == ".":
                    continue
                created_time = fs.get_created_time(file_path + "/" + file)
                accessed_time = fs.get_accessed_time(file_path + "/" + file)
                size = fs.size(file_path + "/" + file)
                file_item = {"file_name": file, "created_time": created_time.strftime("%m/%d/%Y, %H:%M:%S"),
                             "accessed_time": accessed_time.strftime("%m/%d/%Y, %H:%M:%S"), "size": size}
                response["files"].append(file_item)
            print(response)

            response = json.dumps(response)

            return HttpResponse(response)

    except template.TemplateDoesNotExist:

        html_template = loader.get_template('home/page-404.html')
        return HttpResponse(html_template.render(context, request))

    except:
        html_template = loader.get_template('home/page-500.html')
        return HttpResponse(html_template.render(context, request))
