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
from .native_tools import *
from django.views.decorators.csrf import csrf_exempt
import stat
from pwd import getpwnam

import json
from django.core.files.storage import FileSystemStorage
from django.conf import settings
import os
import shutil
import zipfile

from django.contrib.auth import authenticate
from django.http import JsonResponse




from django.core.cache import cache
import docker

import copy

from PIL import Image
from PIL.TiffTags import TAGS
from datetime import datetime
from .forms import UploadFileForm


# import matlab.engine as mat_eng
username = ""

@login_required(login_url="/login/")
def index(request):
    context = {'segment': 'index'}

    #print("in domains")
    #domains = get_domains()

    #context["domains"] = domains
    global username
    username = request.user.get_username()

    html_template = loader.get_template('home/search.html')
    return HttpResponse(html_template.render(context, request))

@csrf_exempt
def authenticate_user(request):
    username = request.POST.get('username')
    password = request.POST.get('password')

    user = authenticate(request, username=username, password=password)

    if user is not None:
        return JsonResponse({"authenticated": True})
    else:
        return JsonResponse({"authenticated": False}, status=401)

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
        
        elif load_template == 'stock.html':
            #context['current_path'] = request.GET['current_path']
            context['segment'] = load_template

            file_names = ["super_high_freq_BCH","high_freq_BCH"]

            stock_data = []#{"high_freq_BCH":{},"super_high_freq_BCH":{}}
            

            
            for file_name in file_names:
                file_path = "/home/impanyu/stock/{}.json".format(file_name)
                try:
                    # Attempt to open the file
                    with open(file_path, 'r') as f:
                        stock = json.load(f)
                        if "name" in stock:
                            stock_data.append (stock)
                
                except FileNotFoundError:
                    print("The file does not exist.")
            

            context['stocks'] = stock_data
      
            #context = {'segment': 'index'}
            #print("in domains")
            #domains = get_domains()

            #domain_names=[]
            #for domain_name in domains:
            #    domain_names.append(domain_name)

            #context["domains"] = domain_names

            #from django.shortcuts import render
            html_template = loader.get_template('home/stock.html')
            #return render(request, "home/stock.html", context)
            return HttpResponse(html_template.render(context, request))

        elif load_template == 'collections.html':
            context['current_path'] = request.GET['current_path']
            context['segment'] = load_template

            #context = {'segment': 'index'}
            #print("in domains")
            #domains = get_domains()

            #domain_names=[]
            #for domain_name in domains:
            #    domain_names.append(domain_name)

            #context["domains"] = domain_names

            html_template = loader.get_template('home/collections.html')
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

            #JD_authorization_code = request.GET.get('code',"")
            #if not JD_authorization_code == "":
            #    get_JD_token(JD_authorization_code)




            html_template = loader.get_template('home/files.html')
            return HttpResponse(html_template.render(context, request))

        elif load_template == "collection.html":
            context['current_path'] = request.GET['current_path']
            context['segment'] = load_template





            html_template = loader.get_template('home/collection.html')
            return HttpResponse(html_template.render(context, request))

        elif load_template == "search.html":
            context['current_path'] = request.GET['current_path']
            context['segment'] = load_template



            html_template = loader.get_template('home/search.html')
            return HttpResponse(html_template.render(context, request))

        elif load_template == "tools.html":
            context['current_path'] = request.GET['current_path']
            context['segment'] = load_template

            html_template = loader.get_template('home/tools.html')
            return HttpResponse(html_template.render(context, request))

        context['segment'] = load_template
        global username
        username = request.user.get_username()

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

        elif load_template == 'add_to_collection':
            selected_collection = request.POST.get("selected_collection", "")
            selected_file_path = request.POST.get("selected_file_path", "")#already abs path


            add_to_collection(selected_collection,selected_file_path,request.user.get_username())

            return HttpResponse("add to collection")

            #return HttpResponse(a)

        elif load_template == 'remove_from_collection':
            collection_name = request.POST.get("collection_name", "")
            file_path = request.POST.get("file_path", "")#already abs path

            remove_from_collection(collection_name, file_path, request.user.get_username())

            return HttpResponse("removed from collection")



        elif load_template == 'create_new_domain':
            new_domain_name = request.POST.get("new_domain_name","")
            start_date = request.POST.get("start_date", "")
            end_date = request.POST.get("end_date","")
            southwest = request.POST.get("southwest","")
            northeast = request.POST.get("northeast","")


            create_new_domain(new_domain_name,start_date,end_date,southwest,northeast)


            return HttpResponse("domain created")

        elif load_template == "create_collection":
            #current_path = request.POST['current_path']
            current_path = request.user.get_username()+"/collections"
            new_collection_name = request.POST['new_collection_name']
            abs_path = os.path.join("/data", current_path,new_collection_name)
            suffix = abs_path.split(".")[-1]

            new_path = abs_path
            i = 1
            while(os.path.exists(new_path)):
                new_path = abs_path+"_"+str(i)
                i = i+1

            #open(new_path, "w")
            meta_data = generate_meta_data_for_dir(new_path,{"create":["null"]})
            update_parent_meta(new_path)

            meta_data["mode"] = ["Collection"]
            meta_data_name = "_".join(new_path.split("/")[1:]) + ".json"


            with open(os.path.join(settings.CORE_DIR, 'data', meta_data_name), "w") as meta_data_file:
                json.dump(meta_data, meta_data_file)

            return HttpResponse("collection creation complete!")


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

        elif load_template == "create_folder":
            #current_path = request.POST['current_path']
            current_path = request.POST.get("current_path", "")
            if current_path.split("/")[0] == "public":
                return HttpResponse("can not create folder to public directory!")
            if not current_path.split("/")[0] == request.user.get_username():
                return HttpResponse("can not create folder to public directory!")

            new_folder_name = request.POST['new_folder_name'].split(".")[0]
            abs_path = os.path.join("/data", current_path,new_folder_name)

            new_path = abs_path
            i = 1
            while(os.path.exists(new_path)):
                new_path = abs_path +"_"+str(i)
                i = i+1
            os.makedirs(new_path)
            aggregate_meta_data(new_path,{"create":["null"]})
            update_parent_meta(new_path)

            return HttpResponse("folder creation complete!")

        elif load_template == "create_file":
            #current_path = request.POST['current_path']
            current_path = request.POST.get("current_path", "")
            if current_path.split("/")[0] == "public":
                return HttpResponse("can not create file to public directory!")
            if not current_path.split("/")[0] == request.user.get_username():
                return HttpResponse("can not create file to public directory!")
            new_file_name = request.POST['new_file_name']
            abs_path = os.path.join("/data", current_path,new_file_name)
            suffix = abs_path.split(".")[-1]

            new_path = abs_path
            i = 1
            while(os.path.exists(new_path)):
                new_path = abs_path[0:-(len(suffix)+1)] +"_"+str(i)+"."+suffix
                i = i+1

            open(new_path, "w")
            generate_meta_data_for_file(new_path,{"create":["null"]})
            update_parent_meta(new_path)

            return HttpResponse("file creation complete!")



        elif load_template == "upload_file":
            current_path = request.POST['current_path']
            # if curren_path begins with public, then return
            if current_path.split("/")[0] == "public":
                return HttpResponse("can not upload files to public directory!")
            if not current_path.split("/")[0] == request.user.get_username():
                return HttpResponse("can not upload files to public directory!")
            
            print(current_path)
            upload_files = request.FILES.getlist("files")
            upload_file_paths = request.POST.getlist("paths")

            '''
            modified_current_path = ""

            for i in range(1, len(current_path.split("/"))):
                modified_current_path += "/" + current_path.split("/")[i]

            if modified_current_path == "":
                current_path = ""
            else:
                current_path = modified_current_path[1:]
            '''



            if not upload_files:
                return HttpResponse('files not found')
            else:
                # load data_and_files
                #data_and_files = open(os.path.join(settings.CORE_DIR, 'data', 'data_and_files.json'), "r")
                #data_points = json.load(data_and_files)
                #data_and_files.close()
                #print("abs")
                #print(upload_file_paths)

                if not upload_file_paths[0] == "":
                    root_abs_path = os.path.join("/data", current_path, upload_file_paths[0].split("/")[0])
                    if os.path.exists(root_abs_path):
                        return HttpResponse("Folder exists!")

                #upload each file
                for file in upload_files:

                    position = os.path.join("/data",current_path,
                                            '/'.join(upload_file_paths[upload_files.index(file)].split('/')[:-1]))
                    print("uploading file:", position,flush=True)
                    #print(file.name)

                    if not os.path.exists(position):
                        os.makedirs(position)
                    abs_file_path = os.path.join(position, file.name)
                    #print(abs_file_path)
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
                    #os.chown(abs_file_path,getpwnam(request.user.get_username()).pw_uid,getpwnam(request.user.get_username()).pw_uid)

                #aggregate meta data for each file

                '''
                cur = ""
                meta_data = {}
                current_abs_path = os.path.join("/data/" + request.user.get_username() + "/ag_data", current_path)
                for i,dir in enumerate(current_abs_path.split("/")):
                    cur = cur + "/"+ dir
                    if cur in data_points:
                        meta_data = data_points[cur]
                '''
                #upload single file, not relative path
                if(upload_file_paths[0] == ""):
                    root_abs_path = os.path.join("/data",current_path,upload_files[0].name)

                else:
                    root_abs_path = os.path.join("/data" ,current_path,upload_file_paths[0].split('/')[0])

                print("uploading files to: ", root_abs_path,flush=True)
                aggregate_meta_data(root_abs_path,{"upload":["external resources"]})
                print("agreregate meta data complete",flush=True)
                # adjust meta data of its parent dir

                if not root_abs_path.split("/")[-2] == "home":
                    parent_dir = "/".join(root_abs_path.split("/")[:-1])
                    parent_meta_data_file_name = "_".join(parent_dir.split("/")[1:]) + ".json"
                    parent_meta_data_file_path = os.path.join(settings.CORE_DIR, 'data', parent_meta_data_file_name)

                    if not os.path.exists(parent_meta_data_file_path):
                        parent_meta_data = {"subdirs":[]}
                        parent_meta_data["subdirs"].append(root_abs_path)

                        #with open(parent_meta_data_file_path, "w") as parent_meta_data_file:
                        #    json.dump({"subdirs":[]}, parent_meta_data_file)

                    else:

                        with open(parent_meta_data_file_path, "r") as parent_meta_data_file:
                            parent_meta_data = json.load(parent_meta_data_file)
                            if "subdirs" not in parent_meta_data:
                                parent_meta_data["subdirs"] = []
                            if root_abs_path not in parent_meta_data["subdirs"]:
                                parent_meta_data["subdirs"].append(root_abs_path)

                    with open(parent_meta_data_file_path, "w") as parent_meta_data_file:
                        json.dump(parent_meta_data, parent_meta_data_file)

                
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




                    #dir_root = os.path.join("/data/" + request.user.get_username() + "/ag_data", current_path,'/'.join(upload_file_paths[0].split('/')[0]))




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
                        #data_point["time"] = datetime.strptime(abs_file_path.split("/")[-2].split("_")[5], "%Y%m%d%H%M%S").strftime("%m/%d/%Y %H:%M:%S")

                    data_points.append(data_point)
                    '''

                #data_and_files = open(os.path.join(settings.CORE_DIR, 'data', 'data_and_files.json'), "w")
                #json.dump(data_points, data_and_files)
                #data_and_files.close()


                return HttpResponse("upload complete!")

                # return HttpResponse("upload complete!")

        elif load_template == "duplicate":
            
            file_path = request.POST['file_path']
            file_name = os.path.basename(file_path)
            parent_path = os.path.dirname(file_path)

            suffix = file_path.split(".")[-1]
            original_user = file_path.split("/")[2]

            if request.user.get_username() is original_user:
                new_path = file_path
                initial_path = file_path
            else:
                initial_path = os.path.join("/data",request.user.get_username(),"ag_data",file_name)
                new_path = os.path.join("/data",request.user.get_username(),"ag_data",file_name)

            i = 1

            while (os.path.exists(new_path)):
                new_path = initial_path[0:-(len(suffix) + 1)] + "_" + str(i) + "." + suffix
                i = i + 1

            #open(new_path, "w")


            '''
            meta_data["name"] = os.path.basename(new_path)
            meta_data["abs_path"] = new_path
            meta_data["upstream"] = {}
            meta_data["upstream"]["duplicate"] = [file_path]


            new_meta_data_file_name = "_".join(new_path.split("/")[1:]) + ".json"

            with open(os.path.join(settings.CORE_DIR, 'data', new_meta_data_file_name), "w") as new_meta_data_file:
                json.dump(meta_data, new_meta_data_file)
            '''
            print("starting duplicating",flush=True)
            print("file_path",new_path,flush=True)
            
            #generate_meta_data_for_file(new_path, {"duplicate": [file_path]})
            update_parent_meta(new_path)
            

            # if file_name is not a path
            #if not os.path.isdir(file_path):
            if "." in file_name:
                print("duplicating file",flush=True)

                shutil.copy2(file_path,new_path)
                meta_data = generate_meta_data_for_file(new_path, {"duplicate": [file_path]})
            else:
                print("duplicating dir",flush=True)
                shutil.copytree(file_path,new_path)
                meta_data = generate_meta_data_for_dir(new_path, {"duplicate": [file_path]})


            return HttpResponse("file duplicated!")



        elif load_template == "delete_file":
            file_path = request.POST['file_path']
            if file_path.split("/")[2] == "public":
                return HttpResponse("can not delete files in public directory!")
            if not file_path.split("/")[2] == request.user.get_username():
                return HttpResponse("can not delete files to public directory!")
            #file_name = request.POST['file_name']



            '''
            modified_file_path = ""
            for i in range(1, len(file_path.split("/"))):
                modified_file_path += "/" + file_path.split("/")[i]

            if modified_file_path == "":
                file_path = ""
            else:
                file_path = modified_file_path[1:]
            '''

            abs_path = file_path#os.path.join("/data",file_path,file_name)

            # remove corresponding meta data files
            meta_data_file_name = "_".join(abs_path.split("/")[1:]) + ".json"
            meta_data_path = os.path.join(settings.CORE_DIR, 'data', meta_data_file_name)
            meta_data = get_meta_data(abs_path)

            if not meta_data["owner"] == request.user.get_username():
                return HttpResponse("can not delete other's data!")

            delete_meta_data(meta_data_path)





            if os.path.isdir(abs_path):
                # shutil.rmtree(os.path.join(settings.CORE_DIR, 'data/users', current_path, file_name))
                shutil.rmtree(abs_path)
            else:
                os.remove(abs_path)



            # adjust meta data of its parent dir
            if not abs_path.split("/")[-2] == "data":
                parent_dir = "/".join(abs_path.split("/")[:-1])
                parent_meta_data_file_name = "_".join(parent_dir.split("/")[1:]) + ".json"
                parent_meta_data_file_path = os.path.join(settings.CORE_DIR, 'data', parent_meta_data_file_name)
                with open(parent_meta_data_file_path,"r") as parent_meta_data_file:
                    parent_meta_data = json.load(parent_meta_data_file)
                    parent_meta_data["subdirs"].remove(abs_path)
                with open(parent_meta_data_file_path, "w") as parent_meta_data_file:
                    json.dump(parent_meta_data,parent_meta_data_file)
                #adjust_meta_data(parent_dir)



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

        elif load_template == 'download_file': #directly download file or folder
            file_path = request.POST['current_path']
            abs_path = os.path.join("/data", file_path)

            # Check if the path exists
            if not os.path.exists(abs_path):
                raise Http404("Path does not exist")

            if os.path.isfile(abs_path):

                with open(abs_path, 'rb') as file:
                    response = HttpResponse(file.read())
                response['Content-Type'] = 'application/octet-stream'
                response['Content-Disposition'] = f'attachment; filename={os.path.basename(file_path)}'

            else:
                # If the path is a folder, create a ZIP archive of the folder and return it as a response
                zip_filename = f"{os.path.basename(file_path)}.zip"
                zip_file_path = os.path.join(settings.CORE_DIR, 'data', zip_filename)
                with zipfile.ZipFile(zip_file_path, 'w') as zip:
                    for root, dirs, files in os.walk(abs_path):
                        for file in files:
                            abs_file_path = os.path.join(root, file)
                            rel_file_path = os.path.relpath(abs_file_path, abs_path)
                            zip.write(abs_file_path, rel_file_path)
                with open(zip_file_path, 'rb') as zip_file:
                    response = HttpResponse(zip_file.read())
                response['Content-Type'] = 'application/zip'
                response['Content-Disposition'] = f'attachment; filename="{zip_filename}"'
                os.remove(zip_file_path)

            return response


        elif load_template == 'get_file': # try to display file in front end
            file_path = request.POST['current_path']
            abs_path = os.path.join("/data", file_path)
            


            # Check if the path exists
            if not os.path.exists(abs_path):
                raise Http404("Path does not exist")

            suffix = abs_path.split("/")[-1].split(".")[-1]

            #if suffix == "tif" or suffix == "tiff":
            if suffix == "shp":
                col = request.POST['col']
                img_path = shp_to_image(abs_path,col)
                print(img_path,flush=True)
                with open(img_path, 'rb') as file:
                    response = HttpResponse(file.read())
                response['Content-Type'] = 'image/jpg'
                response['Content-Disposition'] = f'inline; filename={os.path.basename(img_path)}'

            elif suffix == "tif" or suffix == "tiff":
                band = request.POST['band']
                img_path = tif_to_image(abs_path,band)
                if img_path =="":
                    response = HttpResponse(bytes())
                else:
                    with open(img_path, 'rb') as file:
                        response = HttpResponse(file.read())
                #response = HttpResponse()
                response['Content-Type'] = 'image/jpg'
                response['Content-Disposition'] = f'inline; filename={os.path.basename(img_path)}'

            elif suffix == "jpg" or suffix == "jpeg":
                with open(abs_path, 'rb') as file:
                    response = HttpResponse(file.read())
                response['Content-Type'] = 'image/jpg'
                response['Content-Disposition'] = f'inline; filename={os.path.basename(file_path)}'

            elif suffix == "png":
                with open(abs_path, 'rb') as file:
                    response = HttpResponse(file.read())
                response['Content-Type'] = 'image/png'
                response['Content-Disposition'] = f'inline; filename={os.path.basename(file_path)}'

            else:
                with open(abs_path, 'rb') as file:
                    response = HttpResponse(file.read())
                response['Content-Type'] = 'application/octet-stream'
                response['Content-Disposition'] = f'inline; filename={os.path.basename(file_path)}'



            return response

        elif load_template == "get_running_containers":
            current_path = request.POST['current_path']
            abs_path = f"/data/{current_path}"
            running_containers = get_running_containers(abs_path)


            response = json.dumps(running_containers)
            return HttpResponse(response)


        elif load_template == "get_collections":

            abs_path = f"/data/{request.user.get_username()}/collections"

            meta_data = get_meta_data(abs_path)

            collections = []

            for collection_path in meta_data["subdirs"]:
                # if collection_path == f"/data/{request.user.get_username()}/collections":
                #    continue
                collection_meta_data = get_meta_data(collection_path)

                collections.append(collection_meta_data)

            public_abs_path = "/data/public/collections"

            public_collections = get_meta_data(public_abs_path)

            for collection_path in public_collections["subdirs"]:
                collection_meta_data = get_meta_data(collection_path)

                collections.append(collection_meta_data)

            # remove duplicates
            collections = set(json.dumps(d) for d in collections)
            collections = [json.loads(s) for s in collections]

            response = json.dumps(collections)

            return HttpResponse(response)


        elif load_template == "file_system_virtual":
            current_path = request.POST['current_path']#f"{request.user.get_username()}/ag_data/collections"
            abs_path = f"/data/{current_path}"
            items = []


            if abs_path == f"/data/{request.user.get_username()}/ag_data/ENREEC_Testbed":
                import requests

                # API Endpoint
                url = "https://sandboxapi.deere.com/platform/organizations/4193081/fields"

                # Headers
                headers = {
                    "Authorization": "Bearer eyJraWQiOiI1VkRFMldCSTc4RjNMdDczUnMxQnNVWUZ2dTFHWXV4YmI1T18wekViai1rIiwiYWxnIjoiUlMyNTYifQ.eyJ2ZXIiOjEsImp0aSI6IkFULl9TT2h3N3NWTHpSRTFVOGNLS0hSOHZiNzF0R01BMUwybnpjU0dvWGM5YVUub2FyMWhzYmRsNzBja2p5dDI1ZDciLCJpc3MiOiJodHRwczovL3NpZ25pbi5qb2huZGVlcmUuY29tL29hdXRoMi9hdXM3OHRubGF5c01yYUZoQzF0NyIsImF1ZCI6ImNvbS5kZWVyZS5pc2cuYXhpb20iLCJpYXQiOjE3MTE3MjIyNDAsImV4cCI6MTcxMTc2NTQ0MCwiY2lkIjoiMG9hYnFpM2ljN1pGRVpFM3o1ZDciLCJ1aWQiOiIwMHVicWhqc2ozM2ZLd1ZvcTVkNyIsInNjcCI6WyJhZzIiLCJhZzEiLCJvZmZsaW5lX2FjY2VzcyIsImZpbGVzIiwiYWczIiwid29yazEiLCJvcmcxIiwid29yazIiLCJvcmcyIiwiZXEyIiwiZXExIl0sImF1dGhfdGltZSI6MTcwMTM4MTMxMSwic3ViIjoieXUucGFuQHVubC5lZHUiLCJpc2NzYyI6dHJ1ZSwidGllciI6IlNBTkRCT1giLCJjbmFtZSI6ImFnIGRhdGEgbWFuYWdlbWVudCIsInVzZXJUeXBlIjoiQ3VzdG9tZXIifQ.vaysqOYi77HvYbAFeHTiCLWdqm43tTLO_YgdEbPxPxfo_OVwzMcNhHWVvkNF44afFmyLvoxy_vxaO-omS5T6ib25mHbaG04c2qdRlgi_Ah66E4it20xperluckS36REwbmVk8IeKnwNXauSwr2IKBh_B4s7o4i5CFEUclemD_WhWxVs1vdgQFbt_8Kzrn3mjiww2qr-bIv3aooHV_dt5gLaJWzLhVCZoZ4w7VYoXSVYsfAg5aOQ83mNJSyzz5CjrbHWRLrq9jUGTlKKq96pqfzKmhcywNrVtKWgGhnmoSu97wzl8G0F78ZabHvbEJFD2O6CYTRNgxdUUn6RtgqA3Ow",
                    #"Host": "http://unlagdatamanagement.hopto.org/",
                    "User-Agent": "ADMA",
                    "Accept": "application/vnd.deere.axiom.v3+json",
                    "Connection": "keep-alive",
                    "Accept-Encoding": "gzip, deflate, br"
                }

                # Sending the GET request
                jd_response = requests.get(url, headers=headers)

                # Checking the response
                if jd_response.status_code == 200:
                    print("Success:")
                    fields = jd_response.json()
                    for field in fields["values"]:
                        #items.append({"name":"ENREEC TestBed", "running": "False",  "abs_path" :current_path+"/ENREEC_Testbed", "native":{"created_time":"01/01/2020 00:00:00","access_time":"01/01/2020 00:00:00","size":"0"}})
                        item = {"native":{}}
                        item["name"] = field["name"]
                        item["running"] = "False"
                        item["abs_path"] = abs_path + "/" + field["id"]

                        # Original date string
                        date_str = field["lastModifiedTime"] 

                        # Parse the original string into a datetime object
                        date_obj = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S.%fZ")

                        # Format the datetime object into the desired string format
                        item["native"]["created_time"] = date_obj.strftime("%d/%m/%Y %H:%M:%S")
                        item["native"]["access_time"] = date_obj.strftime("%d/%m/%Y %H:%M:%S")
                        item["native"]["size"] = 0
                        items.append(item)


               
                else:
                    print("Failed to retrieve data:")
                
                response = json.dumps(items)

                return HttpResponse(response)
            
            if abs_path.startswith(f"/data/{request.user.get_username()}/ag_data/ENREEC_Testbed") and len(abs_path.split("/"))==6: #a field is selected
                import requests
                field_id = abs_path.split("/")[-1]

                # API Endpoint
                url = "https://sandboxapi.deere.com/platform/organizations/4193081/fields/"+field_id+"/fieldOperations"

                # Headers
                headers = {
                    "Authorization": "Bearer eyJraWQiOiI1VkRFMldCSTc4RjNMdDczUnMxQnNVWUZ2dTFHWXV4YmI1T18wekViai1rIiwiYWxnIjoiUlMyNTYifQ.eyJ2ZXIiOjEsImp0aSI6IkFULl9TT2h3N3NWTHpSRTFVOGNLS0hSOHZiNzF0R01BMUwybnpjU0dvWGM5YVUub2FyMWhzYmRsNzBja2p5dDI1ZDciLCJpc3MiOiJodHRwczovL3NpZ25pbi5qb2huZGVlcmUuY29tL29hdXRoMi9hdXM3OHRubGF5c01yYUZoQzF0NyIsImF1ZCI6ImNvbS5kZWVyZS5pc2cuYXhpb20iLCJpYXQiOjE3MTE3MjIyNDAsImV4cCI6MTcxMTc2NTQ0MCwiY2lkIjoiMG9hYnFpM2ljN1pGRVpFM3o1ZDciLCJ1aWQiOiIwMHVicWhqc2ozM2ZLd1ZvcTVkNyIsInNjcCI6WyJhZzIiLCJhZzEiLCJvZmZsaW5lX2FjY2VzcyIsImZpbGVzIiwiYWczIiwid29yazEiLCJvcmcxIiwid29yazIiLCJvcmcyIiwiZXEyIiwiZXExIl0sImF1dGhfdGltZSI6MTcwMTM4MTMxMSwic3ViIjoieXUucGFuQHVubC5lZHUiLCJpc2NzYyI6dHJ1ZSwidGllciI6IlNBTkRCT1giLCJjbmFtZSI6ImFnIGRhdGEgbWFuYWdlbWVudCIsInVzZXJUeXBlIjoiQ3VzdG9tZXIifQ.vaysqOYi77HvYbAFeHTiCLWdqm43tTLO_YgdEbPxPxfo_OVwzMcNhHWVvkNF44afFmyLvoxy_vxaO-omS5T6ib25mHbaG04c2qdRlgi_Ah66E4it20xperluckS36REwbmVk8IeKnwNXauSwr2IKBh_B4s7o4i5CFEUclemD_WhWxVs1vdgQFbt_8Kzrn3mjiww2qr-bIv3aooHV_dt5gLaJWzLhVCZoZ4w7VYoXSVYsfAg5aOQ83mNJSyzz5CjrbHWRLrq9jUGTlKKq96pqfzKmhcywNrVtKWgGhnmoSu97wzl8G0F78ZabHvbEJFD2O6CYTRNgxdUUn6RtgqA3Ow",
                    #"Host": "http://unlagdatamanagement.hopto.org/",
                    "User-Agent": "ADMA",
                    "Accept": "application/vnd.deere.axiom.v3+json",
                    "Connection": "keep-alive",
                    "Accept-Encoding": "gzip, deflate, br"
                }

                # Sending the GET request
                jd_response = requests.get(url, headers=headers)

                # Checking the response
                if jd_response.status_code == 200:
                    print("Success:")
                    field_ops = jd_response.json()
                    for field_op in field_ops["values"]:
                        item = {"native":{}}
                        #items.append({"name":"ENREEC TestBed", "running": "False",  "abs_path" :current_path+"/ENREEC_Testbed", "native":{"created_time":"01/01/2020 00:00:00","access_time":"01/01/2020 00:00:00","size":"0"}})
                        item["name"] = field_op["id"]
                        item["running"] = "False"
                        item["abs_path"] = abs_path + "/" + field_op["id"]

                        # Original date string
                        date_str = field_op["modifiedTime"] 

                        # Parse the original string into a datetime object
                        date_obj = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S.%fZ")

                        # Format the datetime object into the desired string format
                        item["native"]["access_time"] = date_obj.strftime("%d/%m/%Y %H:%M:%S")

                        # Original date string
                        date_str = field_op["startDate"] 

                        # Parse the original string into a datetime object
                        date_obj = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S.%fZ")

                        # Format the datetime object into the desired string format
                        item["native"]["created_time"] = date_obj.strftime("%d/%m/%Y %H:%M:%S")


                        item["native"]["size"] = 0
                        items.append(item)


               
                else:
                    print("Failed to retrieve data:")
                
                response = json.dumps(items)

                return HttpResponse(response)

            print("Start to get meta data",abs_path,flush=True)
            meta_data = get_meta_data(abs_path)
            print("Meta data retrieved",abs_path,flush=True)

            

            if not abs_path.split("/")[2] == request.user.get_username() and  meta_data["public"] == "False":
                return HttpResponse(json.dumps(items))

            if f"/data/public" in abs_path or "Collection" in meta_data["mode"]:
                i = 0
                while i < len(meta_data["subdirs"]):  
                    sub_path = meta_data["subdirs"][i]



                    # if collection_path == f"/data/{request.user.get_username()}/collections":
                    #    continue
                    
                    sub_meta_data = get_meta_data(sub_path)
                    
                    if sub_meta_data=={}:
                        meta_data["subdirs"].remove(sub_path)
                        continue
                    else:
                        i = i + 1

                    if not sub_path.split("/")[2] == request.user.get_username() and sub_meta_data["public"] == "False":
                        continue
                    if "Tool" in sub_meta_data["mode"]:
                        running_containers = get_running_containers(sub_path)
                        if len(running_containers) == 0:
                            sub_meta_data["running"] = "False"
                        else:
                            sub_meta_data["running"] = "True"

                    items.append(sub_meta_data)
                items = sorted(items, key=lambda item: item["name"])

                parent_dir = "/".join(abs_path.split("/")[:4])
                #parent_dir = "/".join(abs_path.split("/"))
                parent_meta_data_file_name = "_".join(parent_dir.split("/")[1:]) + ".json"
                parent_meta_data_file_path = os.path.join(settings.CORE_DIR, 'data', parent_meta_data_file_name)
                with open(parent_meta_data_file_path,"r") as parent_meta_data_file:
                    parent_meta_data = json.load(parent_meta_data_file)
                    parent_meta_data["subdirs"] = meta_data["subdirs"]
                with open(parent_meta_data_file_path, "w") as parent_meta_data_file:
                    json.dump(parent_meta_data,parent_meta_data_file)








                response = json.dumps(items)

                return HttpResponse(response)
            
            
            




            #if abs_path == f"/data/{request.user.get_username()}/ag_data":
            #    sub_meta_data = get_meta_data("/data/public/ag_data")
            #    items.append(sub_meta_data)

        
            #for sub_path in meta_data["subdirs"]:
            for sub_name in os.listdir(meta_data["abs_path"]):
                #print(meta_data["abs_path"],flush=True)
                print(sub_name,flush=True)
                if sub_name[0] == ".":
                    continue
                sub_path = meta_data["abs_path"] + "/" + sub_name
                
                #if collection_path == f"/data/{request.user.get_username()}/collections":
                #    continue
                print("start to get meta data",sub_path,flush=True)
                sub_meta_data = get_meta_data(sub_path)
                print("meta data retrieved",sub_path,flush=True)

                if not sub_path.split("/")[2] == request.user.get_username() and sub_meta_data["public"] == "False":
                    continue
                if "Tool" in sub_meta_data["mode"]:
                    running_containers = get_running_containers(sub_path)
                    if len(running_containers) == 0:
                        sub_meta_data["running"] = "False"
                    else:
                        sub_meta_data["running"] = "True"
                

                items.append(sub_meta_data)
            items = sorted(items, key= lambda item: item["name"])

            response = json.dumps(items)

            return HttpResponse(response)



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
            #fs = FileSystemStorage(location="/data/" + request.user.get_username() + "/ag_data")
            fs = FileSystemStorage(location="/data/" + file_path)


            #print(request.user.get_username())

            '''
            modified_file_path = ""
            for i in range(1, len(file_path.split("/"))):
                modified_file_path += "/" + file_path.split("/")[i]

            if modified_file_path == "":
                file_path = "."
                abs_path = "/data/" + request.user.get_username() + "/ag_data"
            else:
                file_path = modified_file_path[1:]
                abs_path = os.path.join("/data/" + request.user.get_username() + "/ag_data", file_path)
            '''


            dirs, files = fs.listdir(".")

            response = {"dirs": [], "files": []}

            # query all the data points or files in current path
            #data_and_files = open(os.path.join(settings.CORE_DIR, 'data', 'data_and_files.json'), "r")
            #data_points = json.load(data_and_files)
            #data_and_files.close()
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
                #if file_path == "ypan12/ag_data" and dir == "collections":
                #    continue
                created_time = fs.get_created_time( dir)
                accessed_time = fs.get_accessed_time( dir)
                size = fs.size( dir)
                dir_item = {"dir_name": dir, "created_time": created_time.strftime("%m/%d/%Y, %H:%M:%S"),
                            "accessed_time": accessed_time.strftime("%m/%d/%Y, %H:%M:%S"), "size": size}
                response["dirs"].append(dir_item)

            for file in files:
                if file[0] == ".": #not display hidden file
                    continue
                created_time = fs.get_created_time( file)
                accessed_time = fs.get_accessed_time( file)
                size = fs.size(file)
                file_item = {"file_name": file, "created_time": created_time.strftime("%m/%d/%Y, %H:%M:%S"),
                             "accessed_time": accessed_time.strftime("%m/%d/%Y, %H:%M:%S"), "size": size}
                response["files"].append(file_item)


            response = json.dumps(response)

            return HttpResponse(response)

        elif load_template == 'get_pipeline':
            current_path = request.POST['current_path']


            graph = get_pipeline("/data/" + current_path)
            response = json.dumps(graph)
            return HttpResponse(response)

        elif load_template == 'meta_data':
            current_path = request.GET['current_path']
            meta_data={}
            meta_data = get_meta_data("/data/"+current_path)
            response = json.dumps(meta_data)
            return HttpResponse(response)

        elif load_template == 'run_tool':
            request_data = json.loads(request.body)
            entry_point = request_data["entry_point"]
            arg_values = request_data["arg_values"]
            arg_types = request_data["arg_types"]
            exe_env = request_data["exe_env"]
            print(request.user.get_username())


            run_tool(entry_point,arg_values, arg_types,request.user.get_username(),exe_env)

            response = "success"
            return HttpResponse(response)

        elif load_template == 'update_meta':
            request_data = json.loads(request.body)
            file_path = request_data['current_path']
            meta_data = request_data["meta_data"]

            abs_path = "/data/"+file_path
            response = "success"

            if not abs_path.split("/")[2] == request.user.get_username() and  meta_data["public"] == "False":
                pass
            else:
                update_meta("/data/"+file_path,meta_data)

            return HttpResponse(response)

        elif load_template == 'update_file':

            request_data = json.loads(request.body)
            current_path = request_data['current_path']
            new_content = request_data["new_content"]


            print(new_content)

            update_file("/data/"+current_path,new_content)
            response = "success";
            return HttpResponse(response)


        elif load_template == 'mode_search':
            #print(request.method)
            #print(request.body)
            request_data = json.loads(request.body)

            file_path = request_data['current_path']

            search_box = request_data['search_box']
            category = request_data['category']
            mode = request_data['mode']
            format = request_data['format']
            label = request_data['label']
            privilege = request_data['privilege']
            realtime = request_data['realtime']
            time_range = request_data['time_range']
            spatial_range = request_data['bounding_box']


            #print("search_box: " + search_box)
            #print("mode: " + str(mode))
            #print("format: " + str(format))
            #print("label: " + str(label))

            # fs = FileSystemStorage(location=os.path.join(settings.CORE_DIR, 'data') + "/users")
            #fs = FileSystemStorage(location="/data/" + request.user.get_username() + "/ag_data")

            # print(request.user.get_username())

            '''
            modified_file_path = ""
            for i in range(1, len(file_path.split("/")))
                modified_file_path += "/" + file_path.split("/")[i]

            if modified_file_path == "":
                file_path = "."
                abs_path = "/data/" + request.user.get_username() + "/ag_data"
            else:
                file_path = modified_file_path[1:]
                abs_path = os.path.join("/data/" + request.user.get_username() + "/ag_data", file_path)

            dirs, files = fs.listdir(file_path)
            '''

            response = {"items": [], "2d_points":[]}
            points = []

            # query all the data points or files in current path
            #data_and_files = open(os.path.join(settings.CORE_DIR, 'data', 'data_and_files.json'), "r")
            #data_points = json.load(data_and_files)
            #data_and_files.close()
            # print(abs_path)


            # search the user's own items
            if "All" in privilege or "My Own Data" in privilege:
                root_dir = os.path.join("/data",request.user.get_username(),"ag_data")
                response["items"] = search(root_dir,search_box,category,mode,format,label,realtime,time_range,spatial_range)

                root_dir = os.path.join("/data", request.user.get_username(), "collections")
                response["items"] += search(root_dir, search_box, category, mode, format, label, realtime, time_range, spatial_range)

            '''
            if "All" in privilege or "Public Data" in privilege:
                root_dir = os.path.join("/data", "public", "ag_data")
                response["items"] += search(root_dir, search_box, category, mode, format, label, realtime, time_range,spatial_range)

                root_dir = os.path.join("/data", "public", "collections")
                response["items"] += search(root_dir, search_box, category, mode, format, label, realtime, time_range,spatial_range)
            '''

            #print(response)
            #remove duplicates
            item_set = set(json.dumps(d) for d in response["items"])
            response["items"] = [json.loads(s) for s in item_set]

            item_paths_set = set([item["abs_path"] for item in response["items"]])

            new_items = []
            for item in response["items"]:
                if os.path.dirname(item["abs_path"]) not in item_paths_set:
                    new_items.append(item)
            response["items"] = new_items




            #if "Domain" in mode:
                #search_domains()
                #print(response["items"])
            # search public items
            # still need to differentiate between own and public items
            '''
            root_dir = "/data/public/ag_data"
            public_items = search(root_dir, search_box, category, mode, format, label, time_range, spatial_range)

            response["items"] += public_items
            '''
            response["2d_points"] = dim_reduction(response["items"]).tolist()




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
