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
import copy

from PIL import Image
from PIL.TiffTags import TAGS
import datetime
from .forms import UploadFileForm


# import matlab.engine as mat_eng


@login_required(login_url="/login/")
def index(request):
    context = {'segment': 'index'}

    print("in domains")
    domains = get_domains()

    context["domains"] = domains

    html_template = loader.get_template('home/search.html')
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

        elif load_template == "search.html":
            context['current_path'] = request.GET['current_path']
            context['segment'] = load_template

            html_template = loader.get_template('home/search.html')
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
                current_path = ""
            else:
                current_path = modified_current_path[1:]

            if not upload_files:
                return HttpResponse('files not found')
            else:
                # load data_and_files
                data_and_files = open(os.path.join(settings.CORE_DIR, 'data', 'data_and_files.json'), "r")
                data_points = json.load(data_and_files)
                data_and_files.close()
                print("abs")
                print(upload_file_paths)

                #upload each file
                for file in upload_files:

                    position = os.path.join("/home/" + request.user.get_username() + "/ag_data",current_path,
                                            '/'.join(upload_file_paths[upload_files.index(file)].split('/')[:-1]))
                    print(position)
                    print(file.name)

                    if not os.path.exists(position):
                        os.makedirs(position)
                    abs_file_path = os.path.join(position, file.name)
                    print(abs_file_path)
                    copy_id = 1

                    if os.path.exists(abs_file_path):
                        #while os.path.exists(abs_file_path + "_" + str(copy_id)):
                            #copy_id += 1
                        return HttpResponse("File exists!")

                        #abs_file_path += "_" + str(copy_id)

                    storage = open(abs_file_path, "wb+")

                    for chunk in file.chunks():
                        storage.write(chunk)
                    storage.close()
                    os.chmod(abs_file_path,stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR)
                    os.chown(abs_file_path,getpwnam(request.user.get_username()).pw_uid,getpwnam(request.user.get_username()).pw_uid)

                #aggregate meta data for each file

                '''
                cur = ""
                meta_data = {}
                current_abs_path = os.path.join("/home/" + request.user.get_username() + "/ag_data", current_path)
                for i,dir in enumerate(current_abs_path.split("/")):
                    cur = cur + "/"+ dir
                    if cur in data_points:
                        meta_data = data_points[cur]
                '''
                #upload single file, not relative path
                if(upload_file_paths[0] == ""):
                    root_abs_path = os.path.join("/home/" + request.user.get_username() + "/ag_data",current_path,upload_files[0].name)
                else:
                    root_abs_path = os.path.join("/home/" + request.user.get_username() + "/ag_data",current_path,upload_file_paths[0].split('/')[0])

                aggregate_meta_data(root_abs_path)

                # adjust meta data of its parent dir

                if not root_abs_path.split("/")[-2] == "home":
                    parent_dir = "/".join(root_abs_path.split("/")[:-1])
                    parent_meta_data_file_name = "_".join(parent_dir.split("/")[1:]) + ".json"
                    parent_meta_data_file_path = os.path.join(settings.CORE_DIR, 'data', parent_meta_data_file_name)

                    with open(parent_meta_data_file_path, "w+") as parent_meta_data_file:
                        parent_meta_data = json.load(parent_meta_data_file)
                        if "subdirs" in parent_meta_data:
                            parent_meta_data["subdirs"].append(root_abs_path)
                        else:
                            parent_meta_data["subdirs"] = [root_abs_path]
                    '''
                    with open(parent_meta_data_file_path, "w") as parent_meta_data_file:
                        json.dump(parent_meta_data, parent_meta_data_file)
                    '''
                
                    #adjust_meta_data(parent_dir)


                '''
                data_points[root_abs_path] = {"path": root_abs_path, "mode": "other", "category":"other", "label":[],"loc":{"lat":0,"lng":0},"time":"1970/1/1 00:00:00","format":[]}
                for key in meta_data:
                    data_points[root_abs_path][key] = copy.deepcopy(meta_data[key])

                top_down(root_abs_path,data_points)
                '''

                '''
                if os.path.isdir(root_abs_path):
                    dfs(fs,data_points)
                #a single file is uploaded
                else:
                    register_file_meta(root_abs_path,data_points)

                    # a meta file is uploaded
                    if file.name[-5:] == ".meta":
                        with open(abs_file_path, "r") as meta_data_file:
                            meta_data = json.load(meta_data_file)
                        # a meta file for dir
                        if file.name[:-5] == abs_file_path.split("/")[-2]:
                            data_points[abs_file_path[:(len(abs_file_path.split("/")[-1])+1)]] = meta_data
                        else:
                            data_points[abs_file_path[:-5]] = meta_data
                    else:
                        continue




                    #dir_root = os.path.join("/home/" + request.user.get_username() + "/ag_data", current_path,'/'.join(upload_file_paths[0].split('/')[0]))




                    #data["mode"],data["category"],data["label"],data["loc"],data["time"]
                    data_point = {"path": abs_file_path, "mode": "other", "category":"other", "label":[],"loc":{"lat":0,"lng":0},"time":"1970/1/1 00:00:00"}



                    # register meta
                    if ".meta" in abs_file_path:
                        meta_data_file_path = abs_file_path + "/"+file".meta"

                    # read meta data
                    meta_data_file_path = abs_file_path+".meta"
                    if os.path.exists(meta_data_file_path):
                        with open(meta_data_file_path,"r") as meta_data_file:
                            meta_data = json.load(meta_data_file)
                            for key in meta_data:
                                data_point[key] = meta_data[key]

                    # extract meta data from file
                    data_point["size"]=os.path.getsize(abs_file_path)
                    if abs_file_path.split(".")[-1] == "tif" or abs_file_path.split(".")[-1] == "tiff":
                        with Image.open(abs_file_path) as img:
                            #print("here")
                            for key in img.tag.keys():
                                print(TAGS[key])
                                if not TAGS[key].startswith('Strip'):
                                    data_point[TAGS[key]] = img.tag[key]
                            #meta_dict = {TAGS[key] : img.tag[key] for key in img.tag.keys()}
                            #print(meta_dict)
                    #data_points[position] = {"loc":loc, "time":time, "public": False, "category":"UAV", "format":"image"}

                    # infer meta data from file
                    if abs_file_path.split("/")[-3] == "winterwheatDataExample":
                        lower_lat = 41.145632
                        left_ln = -96.439434
                        upper_lat = 41.145942
                        right_ln = -96.439201

                        lat_per_rect = (upper_lat - lower_lat) / 8
                        ln_per_rect = (right_ln - left_ln) / 10

                        plot_id = int(abs_file_path.split("/")[-2].split("_")[3])
                        data_point["plot_id"] = plot_id
                        data_point["category"] = "spidercam"
                        data_point["labels"] = ["wheat"]
                        if abs_file_path.split("/")[-1].startswith("NIR"):
                            data_point["labels"].append("NIR")
                        elif abs_file_path.split("/")[-1].startswith("RGB"):
                            data_point["labels"].append("RGB")
                        elif abs_file_path.split("/")[-1].startswith("Infrared"):
                            data_point["labels"].append("Infrared")
                        elif abs_file_path.split("/")[-1].startswith("LiDAR"):
                            data_point["labels"].append("LiDAR")

                        i = int((plot_id - 1301) / 10)
                        j = (plot_id - 1301) % 10

                        rect_lower_lat = lower_lat + i * lat_per_rect
                        rect_upper_lat = rect_lower_lat + lat_per_rect
                        rect_left_ln = left_ln + j * ln_per_rect
                        rect_right_ln = rect_left_ln + ln_per_rect

                        data_point["loc"] = {"lat": (rect_lower_lat+rect_upper_lat)/2, "lng": (rect_left_ln+ rect_right_ln)/2}
                        #data_point["time"] = datetime.strptime(abs_file_path.split("/")[-2].split("_")[5], "%Y%m%d%H%M%S").strftime("%Y/%m/%d %H:%M:%S")

                    data_points.append(data_point)
                    '''

                #data_and_files = open(os.path.join(settings.CORE_DIR, 'data', 'data_and_files.json'), "w")
                #json.dump(data_points, data_and_files)
                #data_and_files.close()


                return HttpResponse("upload complete!")

                # return HttpResponse("upload complete!")

        elif load_template == "delete_file":
            file_path = request.POST['current_path']
            file_name = request.POST['file_name']

            modified_file_path = ""
            for i in range(1, len(file_path.split("/"))):
                modified_file_path += "/" + file_path.split("/")[i]

            if modified_file_path == "":
                file_path = ""
            else:
                file_path = modified_file_path[1:]

            abs_path = os.path.join("/home/" + request.user.get_username() + "/ag_data/",file_path,file_name)

            if os.path.isdir(abs_path):
                # shutil.rmtree(os.path.join(settings.CORE_DIR, 'data/users', current_path, file_name))
                shutil.rmtree(abs_path)
            else:
                os.remove(abs_path)

            # remove corresponding meta data files
            meta_data_file_name = "_".join(abs_path.split("/")[1:]) + ".json"
            meta_data_path = os.path.join(settings.CORE_DIR, 'data', meta_data_file_name)
            delete_meta_data(meta_data_path)

            # adjust meta data of its parent dir
            if not abs_path.split("/")[-2] == "home":
                parent_dir = "/".join(abs_path.split("/")[:-1])
                parent_meta_data_file_name = "_".join(parent_dir.split("/")[1:]) + ".json"
                parent_meta_data_file_path = os.path.join(settings.CORE_DIR, 'data', parent_meta_data_file_name)
                with open(parent_meta_data_file_path,"r") as parent_meta_data_file:
                    parent_meta_data = json.load(parent_meta_data_file)
                    parent_meta_data["subdirs"].remove(abs_path)
                with open(parent_meta_data_file_path, "w") as parent_meta_data_file:
                    json.dump(parent_meta_data,parent_meta_data_file)
                adjust_meta_data(parent_dir)



            '''
            #modify data_and_files
            data_and_files = open(os.path.join(settings.CORE_DIR, 'data', 'data_and_files.json'), "r")
            data_points = json.load(data_and_files)
            data_and_files.close()


            data_points = {path: data_points[path] for path in data_points if not (path.startswith(abs_path))}


            data_and_files = open(os.path.join(settings.CORE_DIR, 'data', 'data_and_files.json'), "w")
            json.dump(data_points, data_and_files)
            data_and_files.close()
            '''

            return HttpResponse("delete complete!")

        elif load_template == 'file_system':
            file_path = request.POST['current_path']
            '''
            search_box = request.POST['search_box']
            category = request.POST['category']
            mode = request.POST.getlist('mode')
            format = request.POST.getlist('format')
            label = request.POST.getlist('label')
            time_range = request.POST.getlist('time_range')
            bounding_box = request.POST.getlist('bounding_box')
            '''

            #fs = FileSystemStorage(location=os.path.join(settings.CORE_DIR, 'data') + "/users")
            fs = FileSystemStorage(location="/home/" + request.user.get_username() + "/ag_data")


            #print(request.user.get_username())

            modified_file_path = ""
            for i in range(1, len(file_path.split("/"))):
                modified_file_path += "/" + file_path.split("/")[i]

            if modified_file_path == "":
                file_path = "."
                abs_path = "/home/" + request.user.get_username() + "/ag_data"
            else:
                file_path = modified_file_path[1:]
                abs_path = os.path.join("/home/" + request.user.get_username() + "/ag_data", file_path)


            dirs, files = fs.listdir(file_path)

            response = {"dirs": [], "files": []}

            # query all the data points or files in current path
            data_and_files = open(os.path.join(settings.CORE_DIR, 'data', 'data_and_files.json'), "r")
            data_points = json.load(data_and_files)
            data_and_files.close()
            response["data_points"] = []
            #print(abs_path)

            '''
            for data in data_points:

                if "path" in data and data["path"].startswith(abs_path) and filtering_condition(data,search_box,category,mode,format,label,time_range,bounding_box):
                    file_name = data["path"][len(abs_path)+1:]
                    if data["mode"] == "Data":

                        if fs.exists(file_path + "/" + file_name):
                            if os.path.isdir(data["path"]):
                                dir = file_name
                                created_time = fs.get_created_time(file_path + "/" + dir)
                                accessed_time = fs.get_accessed_time(file_path + "/" + dir)
                                size = fs.size(file_path + "/" + dir)
                                dir_item = {"dir_name": dir, "created_time": created_time.strftime("%m/%d/%Y, %H:%M:%S"),
                                            "accessed_time": accessed_time.strftime("%m/%d/%Y, %H:%M:%S"), "size": size}
                                response["dirs"].append(dir_item)
                            else:
                                file = file_name
                                created_time = fs.get_created_time(file_path + "/" + file)
                                accessed_time = fs.get_accessed_time(file_path + "/" + file)
                                size = fs.size(file_path + "/" + file)
                                file_item = {"file_name": file, "created_time": created_time.strftime("%m/%d/%Y, %H:%M:%S"),
                                             "accessed_time": accessed_time.strftime("%m/%d/%Y, %H:%M:%S"), "size": size}
                                response["files"].append(file_item)
                    else:
                        response["domain"] = []
                    response["data_points"].append(data)
            '''

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

        elif load_template == 'mode_search':
            file_path = request.POST['current_path']

            search_box = request.POST['search_box']
            category = request.POST.getlist('category')
            mode = request.POST.getlist('mode')
            format = request.POST.getlist('format')
            label = request.POST.getlist('label')
            time_range = request.POST.getlist('time_range')
            spatial_range = request.POST.getlist('bounding_box')


            # fs = FileSystemStorage(location=os.path.join(settings.CORE_DIR, 'data') + "/users")
            #fs = FileSystemStorage(location="/home/" + request.user.get_username() + "/ag_data")

            # print(request.user.get_username())

            '''
            modified_file_path = ""
            for i in range(1, len(file_path.split("/")))
                modified_file_path += "/" + file_path.split("/")[i]

            if modified_file_path == "":
                file_path = "."
                abs_path = "/home/" + request.user.get_username() + "/ag_data"
            else:
                file_path = modified_file_path[1:]
                abs_path = os.path.join("/home/" + request.user.get_username() + "/ag_data", file_path)

            dirs, files = fs.listdir(file_path)
            '''

            response = {"items": [], "2d_points":[]}
            points = []

            # query all the data points or files in current path
            #data_and_files = open(os.path.join(settings.CORE_DIR, 'data', 'data_and_files.json'), "r")
            #data_points = json.load(data_and_files)
            #data_and_files.close()
            # print(abs_path)

            root_dir = "/"+request.user.get_username()
            response["items"] = search(root_dir,search_box,category,mode,format,label,time_range,spatial_range)

            '''
            for path in data_points:
                data = data_points[path]

                if filtering_condition(data,search_box,category,mode,format,label,time_range,bounding_box):
                    item_name = data["path"].split("/")[-1]
                    data["name"] = item_name
                    points.append([data["mode"],data["category"],data["label"],data["loc"],data["time"],data["format"]])
                    response["items"].append(data)

            response["2d_points"] = dim_reduction(points).tolist()

            print(response)
            '''

            response = json.dumps(response)


            return HttpResponse(response)

    except template.TemplateDoesNotExist:

        html_template = loader.get_template('home/page-404.html')
        return HttpResponse(html_template.render(context, request))

    except:
        html_template = loader.get_template('home/page-500.html')
        return HttpResponse(html_template.render(context, request))
