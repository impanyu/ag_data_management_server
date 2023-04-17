# -*- encoding: utf-8 -*-
from typing import List, Any

from django.conf import settings
from django.core.files.storage import FileSystemStorage
import os
from pandas import DataFrame, read_csv
import json
import pandas as pd
import numpy as np
from datetime import datetime
from PIL import Image
import shutil
from sklearn import manifold
import rasterio
from rasterio.crs import CRS
from rasterio.warp import transform
import shapefile

import geopandas as gpd
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap


import pyinotify
import docker
import docker.errors

from .file_monitor import EventHandler



def convert_and_caching(file_path, username):
    real_path = map_file_path(file_path, username)
    suffix = file_path.split("/")[-1].split(".")[1]
    print(suffix)

    if (suffix == "jpg" or suffix == "png"):

        new_name = file_path.split("/")[-1]
        shutil.copy(real_path, "/static/data_cache/" + new_name)

    elif (suffix == "tif" or suffix == "tiff"):
        new_name = file_path.split("/")[-1].split(".")[0] + ".jpg"
        outfile = os.path.join(settings.CORE_DIR, 'data', 'data_cache', new_name)
        if (os.path.exists(outfile)):
            return "/static/data_cache/" + new_name

        im = Image.open(real_path)
        if (not im.mode == 'RGB'):
            im = im.convert('RGB')

        im.thumbnail((1000, 1000))

        im.save(outfile)

    return "/static/data_cache/" + new_name


def extract_coordinates(southwest, northeast):
    lower_lat = float(southwest.split(",")[0])
    upper_lat = float(northeast.split(",")[0])
    left_ln = float(southwest.split(",")[1])
    right_ln = float(northeast.split(",")[1])
    return lower_lat, upper_lat, left_ln, right_ln


def overlap(a1, b1, a2, b2):
    return max(a1, a2) <= min(b1, b2)


def string_to_time(t):
    return datetime.strptime(t, "%m/%d/%Y")


def decode_key(key):
    keys = key.split(",")
    return (float(keys[0]), float(keys[1]), float(keys[2]), float(keys[3]), datetime.strptime(keys[4], "%m/%d/%Y"),
            datetime.strptime(keys[5], "%m/%d/%Y"))


def query_domain(domain_name, start_date, end_date, southwest, northeast, query_range, username):
    domain_data_path = os.path.join(settings.CORE_DIR, 'data', domain_name + '.json')
    query_range = json.loads(query_range)
    query_result = []
    with open(domain_data_path, 'r') as domain_data_file:
        print("infile")
        domain_data = json.load(domain_data_file)
        for key, value in domain_data.items():
            item_lower_lat, item_left_ln, item_upper_lat, item_right_ln, item_start_date, item_end_date = decode_key(
                key)

            lower_lat, upper_lat, left_ln, right_ln = extract_coordinates(southwest, northeast)

            if (not overlap(item_lower_lat, item_upper_lat, lower_lat, upper_lat)):
                print("o1")
                continue

            if (not overlap(item_left_ln, item_right_ln, left_ln, right_ln)):
                print("o2")
                continue

            if (not overlap(item_start_date, item_end_date, string_to_time(start_date), string_to_time(end_date))):
                print("o3")
                continue

            # check  attributes
            satisfied = True

            for content_key, range_values in query_range.items():
                if (content_key not in value):
                    continue
                if (not value[content_key].isnumeric()):
                    continue
                if (not (float(range_values[0]) <= float(value[content_key]) and float(value[content_key]) <= float(
                        range_values[1]))):
                    satisfied = False
                    break

            print(satisfied)

            if (satisfied):
                result = {}

                for attr_key, attr_value in value.items():
                    if (not attr_value.isnumeric()):  # deal with file path
                        result[attr_key] = convert_and_caching(attr_value, username)
                    else:
                        result[attr_key] = attr_value

                item_southwest = str(item_lower_lat) + "," + str(item_left_ln)
                item_northeast = str(item_upper_lat) + "," + str(item_right_ln)
                result["bounding_box"] = [item_southwest, item_northeast]
                result["date_range"] = [datetime.strftime(item_start_date, "%m/%d/%Y"),
                                        datetime.strftime(item_end_date, "%m/%d/%Y")]

                query_result.append(result)

            print(query_result)

    return json.dumps(query_result)


# map logic_path to real_path, for example impanyu/ENREC/1.png -> /data/impanyu/ag_data/ENREC/1.png
def map_file_path(logic_path, username):
    real_path = ""

    for i in range(1, len(logic_path.split("/"))):
        real_path += "/" + logic_path.split("/")[i]

    if real_path == "":
        real_path = "."
    else:
        real_path = real_path[1:]

    real_path = os.path.join("/data/" + username + "/ag_data/", real_path)
    return real_path


def add_to_domain(domain_name, start_date, end_date, southwest, northeast, data_content):
    domain_data_path = os.path.join(settings.CORE_DIR, 'data', domain_name + '.json')
    if (southwest[0] == "("):
        item_key = southwest[1:-1] + "," + northeast[1:-1] + "," + start_date + "," + end_date
    elif (southwest[0].isnumeric()):
        item_key = southwest + "," + northeast + "," + start_date + "," + end_date
    else:
        item_key = "0,0,0,0," + start_date + end_date

    if not os.path.exists(domain_data_path):
        with open(domain_data_path, 'w') as domain_data_file:

            domain_data = {}
            domain_data[item_key] = json.loads(data_content)
            json.dump(domain_data, domain_data_file)

    else:
        with open(domain_data_path, 'r') as domain_data_file:
            domain_data = json.load(domain_data_file)
            if (item_key not in domain_data):
                domain_data[item_key] = {}
            for key, value in json.loads(data_content).items():
                domain_data[item_key][key] = value

        with open(domain_data_path, 'w') as domain_data_file:
            json.dump(domain_data, domain_data_file)

    return True


def get_domain_meta(domain_name):
    domains_file_path = os.path.join(settings.CORE_DIR, 'data', 'domains.json')
    with open(domains_file_path, "r") as domains_file:
        domains = json.load(domains_file)
    return domains[domain_name]


def create_new_domain(new_domain_name, start_date, end_date, southwest, northeast):
    domains_file_path = os.path.join(settings.CORE_DIR, 'data', 'domains.json')
    new_domain = {"date_range": [start_date, end_date], "bounding_box": [southwest, northeast]}
    # new_domain = {}
    if not os.path.exists(domains_file_path):
        with open(domains_file_path, 'w') as domains_file:
            domains = {new_domain_name: new_domain}
            json.dump(domains, domains_file)

    else:
        with open(domains_file_path, 'r') as domains_file:
            domains = json.load(domains_file)
        domains[new_domain_name] = new_domain
        with open(domains_file_path, 'w') as domains_file:
            json.dump(domains, domains_file)


def get_domains():
    domains_file_path = os.path.join(settings.CORE_DIR, 'data', 'domains.json')
    if not os.path.exists(domains_file_path):
        domains = {}
    else:
        with open(domains_file_path, "r") as domains_file:
            domains = json.load(domains_file)
    # print(domains)
    return domains


def retrieve_sub_domains(domain_path, session):
    if domain_path == "/spidercam":
        domains = ["1373", "all"]
        for i in [1374, 1375, 1376]:
            if str(i) in session:
                domains.append(str(i))

        # domains=[str(i) for i in [1373,1374,1375,1376]]
        # domains.insert(0,"spidercam")
        return domains
    elif domain_path == "/soilwater":
        domains = ["0.15m", "0.45m", "0.75m"]
        return domains
    else:
        return []


def retrieve_layers(domain_path):
    if domain_path == "/spidercam/1373":

        return ["RGB", "NIR", "Infrared_Soil", "Infrared_Vege", "Canopy_Height", "Canopy_Coverage",
                "Canopy_Temperature"]  # ,"PixelArray_Soil", "PixelArray_Vege","TemperatureMatrix_Soil",
        # "TemperatureMatrix_Vege"]
    elif domain_path == "/soilwater/0.15m":
        return ["water_content"]
    else:
        return []


def retrieve_times(subdomain_path, session):
    # print(session["1375"])
    if subdomain_path == "/spidercam/1373":
        return ["20210521182617"]

    elif subdomain_path == "/spidercam/1374":
        result = []
        if "20210521175836" in session["1374"]:
            result.append("20210521175836")
        if "20210521182634" in session["1374"]:
            result.append("20210521182634")

        return result

    elif subdomain_path == "/spidercam/1375":
        print(session["1375"])
        result = []

        if "20210521182651" in session["1375"]:
            result.append("20210521182651")

        if "20210521175855" in session["1375"]:
            result.append("20210521175855")
        print(session["1375"])

        return result
    elif subdomain_path == "/spidercam/1376":
        return ["20210521182709"]

    else:
        result = ["20210521182617", "20210521175836", "20210521182634", "20210521182651", "20210521175855",
                  "20210521182709"]
        '''
        for sub in [1373,1374,1375,1376]:
            tmps=retrieve_times("/spidercam/"+str(sub),session)
            print(tmps)
            for tmp in tmps:
                result.append(tmp)
        print(result)
        '''

        return result


def retrieve_data(app, plot, time, layer, meta):
    fs_cache = FileSystemStorage(location=os.path.join(settings.CORE_DIR, 'data') + "/data_cache")
    data_file_name = "spidercam_data.json"
    data = {}

    if not fs_cache.exists(data_file_name):

        raw_file_path = os.path.join(settings.CORE_DIR, 'data/users/impanyu/DatasheetWithWeather_202106121607.xlsx')

        df = pd.read_excel(raw_file_path, converters={'Timestamp': str})

        df['Timestamp'].replace('', np.nan, inplace=True)
        # df = df[df['VAERS ID']!=np.nan]
        df.dropna(subset=['Timestamp'], inplace=True)

        for i in range(df.shape[0]):
            # print(df["Genotype"][i])

            p = int(df["Genotype"][i])  # remove the tailing .0
            t = df["Timestamp"][i]

            canopy_coverage = df["PlantCoverage"][i]
            canopy_height = df["CanopyHeight"][i]

            if p not in data:
                data[p] = {}
            if t not in data[p]:
                data[p][t] = {}

            data[p][t]["canopy_coverage"] = canopy_coverage
            data[p][t]["canopy_height"] = canopy_height

        data[1376]["May-21-2021 18:27"] = {}

        data[1376]["May-21-2021 18:27"]["RGB"] = "/static/data_cache/spidercam_1376_RGB_20210521182709.png"
        data[1376]["May-21-2021 18:27"]["NIR"] = "/static/data_cache/spidercam_1376_NIR_20210521182709.png"
        data[1376]["May-21-2021 18:27"][
            "Infrared_Vege"] = "/static/data_cache/spidercam_1376_Infrared_Vege_20210521182709.png"
        data[1376]["May-21-2021 18:27"][
            "Infrared_Soil"] = "/static/data_cache/spidercam_1376_Infrared_Soil_20210521182709.png"

        data[1375]["May-21-2021 18:26"] = {}

        data[1375]["May-21-2021 18:26"]["RGB"] = "/static/data_cache/spidercam_1375_RGB_20210521182651.png"
        data[1375]["May-21-2021 18:26"]["NIR"] = "/static/data_cache/spidercam_1375_NIR_20210521182651.png"
        data[1375]["May-21-2021 18:26"][
            "Infrared_Vege"] = "/static/data_cache/spidercam_1375_Infrared_Vege_20210521182651.png"
        data[1375]["May-21-2021 18:26"][
            "Infrared_Soil"] = "/static/data_cache/spidercam_1375_Infrared_Soil_20210521182651.png"

        data[1375]["May-21-2021 17:58"] = {}

        data[1375]["May-21-2021 17:58"]["RGB"] = "/static/data_cache/spidercam_1375_RGB_20210521175855.png"
        data[1375]["May-21-2021 17:58"]["NIR"] = "/static/data_cache/spidercam_1375_NIR_20210521175855.png"
        data[1375]["May-21-2021 17:58"][
            "Infrared_Vege"] = "/static/data_cache/spidercam_1375_Infrared_Vege_20210521175855.png"
        data[1375]["May-21-2021 17:58"][
            "Infrared_Soil"] = "/static/data_cache/spidercam_1375_Infrared_Soil_20210521175855.png"

        data[1374]["May-21-2021 18:26"] = {}

        data[1374]["May-21-2021 18:26"]["RGB"] = "/static/data_cache/spidercam_1374_RGB_20210521182634.png"
        data[1374]["May-21-2021 18:26"]["NIR"] = "/static/data_cache/spidercam_1374_NIR_20210521182634.png"
        data[1374]["May-21-2021 18:26"][
            "Infrared_Vege"] = "/static/data_cache/spidercam_1374_Infrared_Vege_20210521182634.png"
        data[1374]["May-21-2021 18:26"][
            "Infrared_Soil"] = "/static/data_cache/spidercam_1374_Infrared_Soil_20210521182634.png"

        with fs_cache.open(data_file_name, "w") as data_file:
            json.dump(data, data_file)


    else:
        with fs_cache.open(data_file_name, "r") as data_file:
            data = json.load(data_file)

    result = {}

    if plot == "":
        plot_lower = 1301
        plot_upper = 1380
    else:
        plot_lower = int(plot)
        plot_upper = int(plot)

    if time == "":
        time_lower = int(datetime.strptime("2030", "%Y").strftime("%s"))
        time_upper = int(datetime.strptime("2030", "%Y").strftime("%s"))
    else:
        # time_lower=new Date(new Date(time).getTime()-3600).toTimeString()
        # time_upper=new Date(new Date(time).getTime()+3600).toTimeString()
        time_lower = int(datetime.strptime(time, "%b-%d-%Y %H:%M").strftime("%s")) - 3600 * 3
        time_upper = int(datetime.strptime(time, "%b-%d-%Y %H:%M").strftime("%s")) + 3600 * 3

    for p in data.keys():
        if not (plot_upper >= int(p) >= plot_lower):
            continue

        for t in data[p].keys():
            t_s = int(datetime.strptime(t, "%b-%d-%Y %H:%M").strftime("%s"))
            if not (time_upper >= t_s >= time_lower):
                continue

            # print(data[p][t].keys())
            for l in data[p][t].keys():
                if layer == "" or l == layer:
                    if p not in result:
                        result[p] = {}
                    if t not in result[p]:
                        result[p][t] = {}

                    result[p][t][l] = data[p][t][l]

    return json.dumps(result)


def retrieve_sub_domain_data(subdomain_path, layer, time, session):
    subdomain_dir = subdomain_path.split('/')

    subdomain = subdomain_dir[1]

    for i in range(2, len(subdomain_dir)):
        subdomain = subdomain + "_" + subdomain_dir[i]
    # print(settings.MEDIA_ROOT)

    if subdomain_dir[1] == "spidercam":
        subdomain_name = subdomain.split("_")[1]

        if not subdomain_name == "all":

            return settings.STATIC_URL + "data_cache/" + subdomain + "_" + layer + "_" + time + ".png"
        else:
            result = {}

            if layer != "RGB" and layer != NIR and layer != "Infrared_Soil" and layer != "Infrared_Vege":
                for sub in [1373, 1374, 1375, 1376]:
                    print(sub)

                    result[sub] = settings.STATIC_URL + "data_cache/spidercam_" + str(
                        sub) + "_" + layer + "_" + time + ".png"
            else:
                layer = "Canopy_Height"
                for sub in [1373, 1374, 1375, 1376]:
                    fs_cache = FileSystemStorage(location=os.path.join(settings.CORE_DIR, 'data') + "/data_cache")
                    for t in ["20210521182617", "20210521175836", "20210521182634", "20210521182651", "20210521175855",
                              "20210521182709"]:
                        input_file_name = "spidercam_" + str(sub) + "_" + t + "_all"

                        if fs_cache.exists(input_file_name):

                            with fs_cache.open(input_file_name, "r") as input_file:
                                matlab_layers = json.load(input_file)
                                print(matlab_layers)

                                if layer == "Canopy_Height":

                                    result[sub] = matlab_layers["canopy_height"]

                                elif layer == "Canopy_Coverage":
                                    result[sub] = matlab_layers["canopy_coverage_and_temperature"][0]
                                else:
                                    result[sub] = matlab_layers["canopy_coverage_and_temperature"][1] / 30

            return json.dumps(result)

    elif (subdomain_dir[1] == "soilwater"):

        fs_cache = FileSystemStorage(location=os.path.join(settings.CORE_DIR, 'data') + "/data_cache")
        fs_data = FileSystemStorage(location=os.path.join(settings.CORE_DIR, 'data') + "/users/impanyu")

        output_file_name = subdomain + "_" + time + "_" + layer + ".json"
        output_time_file_name = "soilwater_time.json"

        if (not fs_cache.exists(output_file_name)):
            raw_file_path = os.path.join(settings.CORE_DIR, 'data/users/impanyu/soilwater.xlsx')
            print(raw_file_path)

            df = pd.read_excel(raw_file_path, converters={'z6-13171': str})

            df['z6-13171'].replace('', np.nan, inplace=True)
            # df = df[df['VAERS ID']!=np.nan]
            df.dropna(subset=['z6-13171'], inplace=True)

            soilwaters = df[subdomain_dir[2]][2:df.shape[0]].tolist()
            times = df['z6-13171'][2:df.shape[0]].tolist()

            with fs_cache.open(output_file_name, "w") as output_file:
                json.dump(soilwaters, output_file)

            with fs_cache.open(output_time_file_name, "w") as output_time_file:
                json.dump(times, output_time_file)

        else:

            with fs_cache.open(output_file_name, "r") as output_file:
                soilwaters = json.load(output_file)

            with fs_cache.open(output_time_file_name, "r") as output_time_file:
                times = json.load(output_time_file)

        return json.dumps({"soilwaters": soilwaters, "times": times})


def filtering_condition(meta_data, search_box, category, mode, format, label, realtime, time_range, bounding_box):
    # return True

    if meta_data["name"] == "ag_data":
        return False

    searched_words = search_box.split(" ")

    has_words = False

    for w in searched_words:
        if w in os.path.basename(meta_data["abs_path"]):
            has_words = True
            break
    if not has_words:
        print("not has word")
        return False

    has_category = False
    for c in category:
        if c == "All" or c in meta_data["category"]:
            has_category = True
            break
        # if c not in ["Genotype","Phenotype","Soil","Atmosphere"] and "Other" in category:
        #    has_category = True
        #    break
    if not has_category:
        print("not has category")
        return False

    has_mode = False
    for m in mode:
        if m == "All" or m in meta_data["mode"]:
            has_mode = True
            break
    if not has_mode:
        print("not has mode")
        return False

    has_format = False
    for f in format:
        if f == "All" or f in meta_data["format"]:
            has_format = True
            break
        # if f not in ["Image","Shape","CSV","Spreadsheet","Python","R","Matlab"] and "Other" in format:
        #    has_format = True
    if not has_format:
        print("not has format")
        return False

    has_label = False
    for l in label:
        if l == "All" or l in meta_data["label"]:
            has_label = True
            break
        # if l not in ["Spidercam","ENREC","Wheat"] and "Other" in label:
        #    has_label = True
    if not has_label:
        print("not has label")
        return False

    has_time_pattern = False
    for r in realtime:
        if r == "All" or r ==  meta_data["realtime"]:
            has_time_pattern = True
            break
        # if l not in ["Spidercam","ENREC","Wheat"] and "Other" in label:
        #    has_label = True
    if not has_time_pattern:
        print("not has time pattern")
        return False

    if not (time_range[0] == "start" or time_range[1] == "end"):
        start = datetime.strptime(time_range[0], "m/d/Y").timestamp()
        end = datetime.strptime(time_range[1], "m/d/Y").timestamp()
        item_start_time = datetime.strptime(meta_data["time_range"]["start"], "m/d/Y %H:%M:%S").timestamp()
        item_end_time = datetime.strptime(meta_data["time_range"]["end"], "m/d/Y %H:%M:%S").timestamp()

        if not overlap(start, end, item_start_time, item_end_time):
            print("not has time")
            return False

    southwest = bounding_box[0]
    northeast = bounding_box[1]

    item_northeast_lat = meta_data["spatial_range"]["northeast"]["lat"]
    item_northeast_lng = meta_data["spatial_range"]["northeast"]["lng"]
    item_southwest_lat = meta_data["spatial_range"]["southwest"]["lat"]
    item_southwest_lng = meta_data["spatial_range"]["southwest"]["lng"]

    if not (southwest == "southwest" or northeast == "northeast"):
        print(southwest)
        print(northeast)
        lower_lat, upper_lat, left_ln, right_ln = extract_coordinates(southwest, northeast)

        if not overlap(lower_lat, upper_lat, item_southwest_lat, item_northeast_lat):
            print("not has space")
            return False
        if not overlap(left_ln, right_ln, item_southwest_lng, item_northeast_lng):
            print("not has space")
            return False

    return True


from sklearn.metrics.pairwise import euclidean_distances


def list_distance(l1, l2):
    overlaps = set(l1) & set(l2)
    num_overlaps = len(overlaps)

    unions = set(l1) | set(l2)
    num_unions = len(unions)

    return 1 - num_overlaps / max(1, num_unions)


# [data["mode"],data["category"],data["label"],data["loc"],data["time"],data["format"]]
# mode, category and time are string, label and format are list, loc is dict
def distance(x, y):
    d = 0


    d += list_distance(x["mode"] ,y["mode"])
    d += list_distance(x["category"], y["category"])
    d += list_distance(x["label"], y["label"])
    d += list_distance(x["format"], y["format"])
    if not x["realtime"] == y["realtime"]:
        d +=1
    if not x["public"] == y["public"]:
        d +=1
    #if not x["owner"] == y["owner"]:
     #   d +=1

    if not overlap(x["time_range"]["start"], x["time_range"]["end"], y["time_range"]["start"], y["time_range"]["end"]):
        d += 1

    x_northeast_lat = x["spatial_range"]["northeast"]["lat"]
    x_northeast_lng = x["spatial_range"]["northeast"]["lng"]
    x_southwest_lat = x["spatial_range"]["southwest"]["lat"]
    x_southwest_lng = x["spatial_range"]["southwest"]["lng"]

    y_northeast_lat = y["spatial_range"]["northeast"]["lat"]
    y_northeast_lng = y["spatial_range"]["northeast"]["lng"]
    y_southwest_lat = y["spatial_range"]["southwest"]["lat"]
    y_southwest_lng = y["spatial_range"]["southwest"]["lng"]

    if not overlap(x_southwest_lat, x_northeast_lat, y_southwest_lat, y_northeast_lat) or not overlap(x_southwest_lng,
                                                                                                      x_northeast_lng,
                                                                                                      y_southwest_lng,
                                                                                                      y_northeast_lng):
        d += 1

    '''
    if not x[1] == y[1]:
        d = d + 1
    for l in x[2]:
        if not l in y[2]:
            d = d + 1
    for l in y[2]:
        if not l in x[2]:
            d = d + 1
    
    d = d+ euclidean_distances([[x[3]["lat"]/90,x[3]["lng"]/180]],[[y[3]["lat"]/90,y[3]["lng"]/180]])
    x_time = datetime.strptime(x[4], "%m/%d/%Y %H:%M:%S").timestamp()
    y_time = datetime.strptime(y[4], "%m/%d/%Y %H:%M:%S").timestamp()
    d = d+ abs(x_time - y_time) / (365*12*30*24*3600)
    
    for l in x[5]:
        if not l in y[5]:
            d = d + 1
    for l in y[5]:
        if not l in x[5]:
            d = d + 1
    '''

    return d


def data_metric(X, Y):
    result = np.zeros([len(X), len(Y)])
    i = 0
    for x in X:
        j = 0
        for y in Y:
            result[i][j] = distance(x, y)
            j = j + 1
        i = i + 1

    return result


def dim_reduction(points):
    if len(points) < 2:
        return np.array([[0, 0]])
    input = data_metric(points, points)
    t_sne = manifold.TSNE(
        n_components=2,
        perplexity=10,
        init="random",
        n_iter=250,
        random_state=0,
        metric="precomputed"
    )
    results = t_sne.fit_transform(input)

    return results


import copy


def top_down(dir_root, data_points):
    data_points[dir_root]["path"] = dir_root
    if not os.path.isdir(dir_root):
        register_file_meta(dir_root, data_points)
        return

    meta_data_file_path = dir_root + "/" + ".meta"
    if os.path.exists(meta_data_file_path):
        with open(meta_data_file_path, "r") as meta_data_file:
            meta_data = json.load(meta_data_file)
            for key in meta_data:
                data_points[dir_root][key] = copy.deepcopy(meta_data[key])

    meta_data = data_points[dir_root]

    for p in os.listdir(dir_root):

        path = dir_root + "/" + p
        if path.split(".")[-1] == "meta":
            continue
        data_points[path] = {"path": path, "mode": "other", "category": "other", "label": [],
                             "loc": {"lat": 0, "lng": 0}, "time": "2030/1/1 00:00:00", "format": []}

        for key in meta_data:
            data_points[path][key] = copy.deepcopy(meta_data[key])

        top_down(path, data_points)


def register_file_meta(file_path, data_points):
    meta_data_file_path = file_path + ".meta"
    if os.path.exists(meta_data_file_path):
        with open(meta_data_file_path, "r") as meta_data_file:
            meta_data = json.load(meta_data_file)
            for key in meta_data:
                data_points[file_path][key] = copy.deepcopy(meta_data[key])

    if file_path.split("/")[-1].split(".")[1] == ".py":
        data_points[file_path]["format"].append("Python")
    elif file_path.split("/")[-1].split(".")[1] == "tif" \
            or file_path.split("/")[-1].split(".")[1] == "tiff" \
            or file_path.split("/")[-1].split(".")[1] == "png" \
            or file_path.split("/")[-1].split(".")[1] == "jpg" \
            or file_path.split("/")[-1].split(".")[1] == "jpeg": \
            data_points[file_path]["format"].append("Image")
    elif file_path.split("/")[-1].split(".")[1] == ".m":
        data_points[file_path]["format"].append("Matlab")
    elif file_path.split("/")[-1].split(".")[1] == ".r":
        data_points[file_path]["format"].append("R")
    elif file_path.split("/")[-1].split(".")[1] == ".m":
        data_points[file_path]["format"].append("Matlab")
    elif file_path.split("/")[-1].split(".")[1] == "csv" or file_path.split("/")[-1].split(".")[1] == "xlsx" or \
            file_path.split("/")[-1].split(".")[1] == "xls":
        data_points[file_path]["format"].append("CSV/Spreadsheet")
    else:
        data_points[file_path]["format"].append("Other")


def aggregate_meta_data(dir_path,upstream):
    meta_data = {}
    # if this is a file
    update_parent_meta(dir_path)
    if not os.path.isdir(dir_path):
        return generate_meta_data_for_file(dir_path,upstream)
    else:
        meta_data = generate_meta_data_for_dir(dir_path,upstream)

    # iterate through each sub path
    for p in os.listdir(dir_path):

        sub_path = os.path.join(dir_path, p)

        sub_meta_data = aggregate_meta_data(sub_path,upstream)
        meta_data["subdirs"].append(sub_path)
        '''
        for c in sub_meta_data["category"]:
            meta_data["category"].append(c)
        for f in sub_meta_data["format"]:
            meta_data["format"].append(f)
        for l in sub_meta_data["label"]:
            meta_data["label"].append(l)
        for m in sub_meta_data["mode"]:
            meta_data["mode"].append(m)

        meta_data["category"] = list(set(meta_data["category"]))
        meta_data["format"] = list(set(meta_data["format"]))
        meta_data["label"] = list(set(meta_data["label"]))
        meta_data["mode"] = list(set(meta_data["mode"]))

        current_start = datetime.strptime(meta_data["time_range"]["start"], "%m/%d/%Y %H:%M:%S").timestamp()
        sub_start = datetime.strptime(sub_meta_data["time_range"]["start"], "%m/%d/%Y %H:%M:%S").timestamp()
        current_end = datetime.strptime(meta_data["time_range"]["end"], "%m/%d/%Y %H:%M:%S").timestamp()
        sub_end = datetime.strptime(sub_meta_data["time_range"]["end"], "%m/%d/%Y %H:%M:%S").timestamp()

        meta_data["time_range"]["start"] = datetime.fromtimestamp(min(current_start, sub_start)).strftime(
            "%m/%d/%Y %H:%M:%S")
        meta_data["time_range"]["end"] = datetime.fromtimestamp(max(current_end, sub_end)).strftime("%m/%d/%Y %H:%M:%S")

        # here we only consider north america
        meta_data["spatial_range"]["northeast"]["lat"] = max(meta_data["spatial_range"]["northeast"]["lat"],
                                                             sub_meta_data["spatial_range"]["northeast"]["lat"])
        meta_data["spatial_range"]["northeast"]["lng"] = max(meta_data["spatial_range"]["northeast"]["lng"],
                                                             sub_meta_data["spatial_range"]["northeast"]["lng"])

        meta_data["spatial_range"]["southwest"]["lat"] = min(meta_data["spatial_range"]["southwest"]["lat"],
                                                             sub_meta_data["spatial_range"]["southwest"]["lat"])
        meta_data["spatial_range"]["southwest"]["lng"] = min(meta_data["spatial_range"]["southwest"]["lng"],
                                                             sub_meta_data["spatial_range"]["southwest"]["lng"])
        '''
    meta_data_file_name = "_".join(dir_path.split("/")[1:]) + ".json"

    with open(os.path.join(settings.CORE_DIR, 'data', meta_data_file_name), "w") as meta_data_file:
        json.dump(meta_data, meta_data_file)

    return meta_data


def generate_meta_data_for_dir(dir_path,upstream):
    meta_data = {}
    meta_data["mode"] = ["Data"]
    meta_data["category"] = []
    meta_data["format"] = ["Folder"]
    meta_data["label"] = []
    meta_data["time_range"] = {"start": "01/01/2030 00:00:00", "end": "01/01/2030 00:00:00"}
    meta_data["spatial_range"] = {"northeast": {"lat": 0, "lng": -180}, "southwest": {"lat": 0, "lng": -180}}
    meta_data["abs_path"] = dir_path
    meta_data["subdirs"] = []
    meta_data["public"] = "False"
    meta_data["name"] = dir_path.split("/")[-1]
    meta_data["realtime"] = "Non-Realtime"
    meta_data["upstream"] = upstream
    meta_data["introduction"] = ""
    from .views import username
    meta_data["owner"] = username


    meta_data_dir_name = "_".join(dir_path.split("/")[1:]) + ".json"

    if os.path.exists(os.path.join(settings.CORE_DIR, 'data', meta_data_dir_name)):

        return get_meta_data(dir_path)

    with open(os.path.join(settings.CORE_DIR, 'data', meta_data_dir_name), "w") as meta_data_file:
        json.dump(meta_data, meta_data_file)

    return meta_data



def generate_meta_data_for_file(file_path, upstream):
    meta_data = {}
    meta_data["mode"] = ["Data"]
    meta_data["category"] = []
    meta_data["format"] = []
    meta_data["label"] = []
    meta_data["time_range"] = {"start": "01/01/2030 00:00:00", "end": "01/01/2030 00:00:00"}
    meta_data["spatial_range"] = {"northeast": {"lat": 0, "lng": -180}, "southwest": {"lat": 0, "lng": -180}}
    meta_data["abs_path"] = file_path
    meta_data["subdirs"] = []
    meta_data["public"] = "False"
    meta_data["name"] = file_path.split("/")[-1]
    meta_data["realtime"] = "Non-Realtime"
    meta_data["upstream"] = upstream
    meta_data["introduction"] = ""
    from .views import username
    meta_data["owner"] = username

    suffix = file_path.split("/")[-1].split(".")[-1]

    if suffix == "py":
        meta_data["format"]=["Python"]
        meta_data["mode"]=["Tool"]
    elif suffix == "tif" or suffix == "tiff" or suffix == "png" or suffix == "jpg" or suffix == "jpeg":
        meta_data["mode"]=["Data"]
        meta_data["format"]=["Image"]
    elif suffix == "shp":
        meta_data["format"]=["Shape"]
        meta_data["mode"]=["Data"]

        # Read shapefile using geopandas
        gdf = gpd.read_file(file_path)
        gdf = gdf.to_crs('EPSG:4326')
        columns = [col for col in gdf.columns]

        # Get bounds of shapefile
        bounds = gdf.total_bounds if not gdf.empty else (-180, 0, -180, 0)
        minx, miny, maxx, maxy = bounds
        meta_data["spatial_range"] = {"southwest": {"lat": miny, "lng": minx}, "northeast": {"lat": maxy, "lng": maxx}}

        sf = shapefile.Reader(file_path)

        meta_data["native"] = {"fields": sf.fields, "numRecords": sf.numRecords, "shapeType": sf.shapeType,
                               "shapeTypeName": sf.shapeTypeName, "type": sf.__geo_interface__['type'], "columns": columns,"spatial_range":meta_data["spatial_range"]}


    elif suffix == "m" or suffix == ".mlx":
        meta_data["format"] = ["Matlab"]
        meta_data["mode"] = ["Tool"]
    elif suffix == "r":
        meta_data["format"] = ["R"]
        meta_data["mode"] = ["Tool"]
    elif suffix == "csv":
        meta_data["format"] = ["CSV"]
        meta_data["mode"] = ["Data"]
    elif suffix == "xlsx" or suffix == "xls":
        meta_data["format"] = ["Spreadsheet"]
        meta_data["mode"] = ["Data"]
    else:
        meta_data["format"] = ["Other"]

    if suffix == "tif" or suffix == "tiff":

        meta_data["native"] = read_tif_meta(file_path)
        if "spatial_range" in meta_data["native"]:
            meta_data["spatial_range"] = meta_data["native"]["spatial_range"]

    meta_data_file_name = "_".join(file_path.split("/")[1:]) + ".json"

    if os.path.exists(os.path.join(settings.CORE_DIR, 'data', meta_data_file_name)):
        return get_meta_data(file_path)

    with open(os.path.join(settings.CORE_DIR, 'data', meta_data_file_name), "w") as meta_data_file:
        json.dump(meta_data, meta_data_file)

    return meta_data


def recursive_update_public(file_path, value):
    meta_data_file_name = "_".join(file_path.split("/")[1:]) + ".json"
    with open(os.path.join(settings.CORE_DIR, 'data', meta_data_file_name), "r") as meta_data_file:
        meta_data = json.load(meta_data_file)

    meta_data["public"] = value

    with open(os.path.join(settings.CORE_DIR, 'data', meta_data_file_name), "w") as meta_data_file:
        #print(meta_data)
        json.dump(meta_data,meta_data_file)


    for p in meta_data["subdirs"]:
        #sub_path = os.path.join(file_path, p)
        recursive_update_public(p,value)

def update_file(file_path, new_content):
    with open(file_path, "w") as data_file:
        data_file.write(new_content)


def add_to_public(file_path):


    public_user_file_name = f"/data/public"
    public_user_meta_file_name = "_".join(public_user_file_name.split("/")[1:]) + ".json"
    public_data_file_name = f"/data/public/ag_data"
    public_meta_data_file_name = "_".join(public_data_file_name.split("/")[1:]) + ".json"
    public_collection_file_name = f"{public_data_file_name}/collections"
    public_collection_meta_file_name = "_".join(public_collection_file_name.split("/")[1:]) + ".json"

    if not os.path.exists(os.path.join(settings.CORE_DIR, 'data', public_user_meta_file_name)):

        public_user_meta_data = generate_meta_data_for_dir(public_user_file_name,{"create":["null"]})

        with open(os.path.join(settings.CORE_DIR, 'data', 'data.json'), 'r') as root_meta_data_file:
            root_meta_data = json.load(root_meta_data_file)
            if public_user_file_name not in root_meta_data["subdirs"]:
                root_meta_data["subdirs"].append(public_user_file_name)

        with open(os.path.join(settings.CORE_DIR, 'data', 'data.json'), 'w') as root_meta_data_file:
            json.dump(root_meta_data, root_meta_data_file)

        public_meta_data = generate_meta_data_for_dir(public_data_file_name,{"create":["null"]})

        if public_data_file_name not in public_user_meta_data["subdirs"]:
            public_user_meta_data["subdirs"].append(public_data_file_name)

        with open(os.path.join(settings.CORE_DIR, 'data', public_user_meta_file_name), 'w') as public_user_meta_data_file:
            json.dump(public_user_meta_data, public_user_meta_data_file)

        public_collection_meta_data = generate_meta_data_for_dir(public_collection_file_name,{"create":["null"]})
        public_collection_meta_data["mode"] = ["Collection"]

        if public_collection_file_name not in public_meta_data["subdirs"]:
            public_meta_data["subdirs"].append(public_collection_file_name)

        with open(os.path.join(settings.CORE_DIR, 'data', public_meta_data_file_name), 'w') as public_meta_data_file:
            json.dump(public_meta_data, public_meta_data_file)

        with open(os.path.join(settings.CORE_DIR, 'data', public_collection_meta_file_name), 'w') as public_collection_meta_file:
            json.dump(public_collection_meta_data, public_collection_meta_file)


   
    meta_data = get_meta_data(file_path)
    

    if "Collection" in meta_data["mode"]:
        public_collection_meta_data = generate_meta_data_for_dir(public_collection_file_name,{"create":["null"]})
        if meta_data["abs_path"] not in public_collection_meta_data["subdirs"]:
            public_collection_meta_data["subdirs"].append(meta_data["abs_path"])
        with open(os.path.join(settings.CORE_DIR, 'data', public_collection_meta_file_name), 'w') as public_collection_meta_file:
            json.dump(public_collection_meta_data, public_collection_meta_file)


    else:
        public_meta_data = generate_meta_data_for_dir(public_data_file_name,{"create":["null"]})
        if meta_data["abs_path"] not in public_meta_data["subdirs"]:
            public_meta_data["subdirs"].append(meta_data["abs_path"])
        with open(os.path.join(settings.CORE_DIR, 'data', public_meta_data_file_name), 'w') as public_meta_data_file:
            json.dump(public_meta_data, public_meta_data_file)




def update_meta(file_path,new_meta_data):
    meta_data_file_name = "_".join(file_path.split("/")[1:]) + ".json"
    with open(os.path.join(settings.CORE_DIR, 'data', meta_data_file_name), "r") as meta_data_file:
        meta_data = json.load(meta_data_file)

    #meta_data ={"public" : "True"}

    #meta_data = {}

    print(new_meta_data)

    for key in new_meta_data:
        if key == "category" or key == "mode" or key == "format" or key == "label":

            meta_data[key] = new_meta_data[key]
            #print(key)
            #print(meta_data[key])

        elif key == "realtime":
            meta_data[key] = new_meta_data[key]

        elif key == "public":
            meta_data[key] = new_meta_data[key]

            # recursively change the subdirs and files
            recursive_update_public(file_path,new_meta_data[key])

            if new_meta_data[key] == "True":
                add_to_public(file_path)


        elif key == "time_range":
            if new_meta_data["time_range"]["start"] == "start":
                continue
            #meta_data[key]={"start": "01/01/2030 00:00:00", "end": "01/01/2030 00:00:00"}
            meta_data[key]["start"] = datetime.strptime(new_meta_data["time_range"]["start"], "%m/%d/%Y").strftime("%m/%d/%Y %H:%M:%S")
            meta_data[key]["end"] = datetime.strptime(new_meta_data["time_range"]["end"], "%m/%d/%Y").strftime("%m/%d/%Y %H:%M:%S")


        elif key == "spatial_range":
            if new_meta_data[key]["southwest"] == "southwest":
                continue
            lower_lat, upper_lat, left_ln, right_ln = extract_coordinates(new_meta_data[key]["southwest"].strip("()"), new_meta_data[key]["northeast"].strip("()"))
            meta_data["spatial_range"]={"southwest":{"lat":0,"lng":-180},"northeast":{"lat":0,"lng":-180}}
            meta_data["spatial_range"]["southwest"]["lat"] = lower_lat
            meta_data["spatial_range"]["southwest"]["lng"] = left_ln
            meta_data["spatial_range"]["northeast"]["lat"] = upper_lat
            meta_data["spatial_range"]["northeast"]["lng"] = right_ln

        elif key == "entry_point":
            meta_data["entry_point"] = "/data"+new_meta_data["entry_point"]

        elif key == "args":
            meta_data["args"] = new_meta_data["args"]

        else:
            meta_data[key] = new_meta_data[key]

        '''
          elif key == "other_meta":
              #other_meta = new_meta_data[key].replace("\n",",")
              #other_meta = json.loads("{" + other_meta + "}")
              #meta_data.update(other_meta)


              for p in new_meta_data[key].split("\n"):
                  if ":" not in p:
                      continue
                  k = p.split(":")[0].strip()
                  v = p.split(":")[1].strip()


                  v = json.loads(v)

                  meta_data[k] = v
          '''


    #return

    print(meta_data)
    with open(os.path.join(settings.CORE_DIR, 'data', meta_data_file_name), "w") as meta_data_file:
        #print(meta_data)
        json.dump(meta_data,meta_data_file)


def read_tif_meta(file_path):
    native_meta = {}
    with rasterio.open(file_path) as src:
        # Create metadata dictionary
        native_meta = {
            'filename': src.name,
            'bands': src.count,
            'width': src.width,
            'height': src.height,
            'dtype': str(src.dtypes[0]),
            'transform': src.transform,
            'tags': src.tags()
        }

    # Open the GeoTIFF file
    with rasterio.open(file_path) as src:
        # Get the image's CRS (Coordinate Reference System)
        src_crs = src.crs
        dst_crs = CRS.from_epsg(4326)
        if src_crs is None:
            return native_meta

        native_meta['crs'] = src.crs.to_dict()

        #if src.crs != crs:
        #    return {"northeast": {"lat": 0, "lng": -180}, "southwest": {"lat": 90, "lng": 0}}

        # Get the image's transform (mapping from pixel coordinates to world coordinates)
        transform_matrix = src.transform



        # Get the image's width and height in pixels
        width = src.width
        height = src.height

        # Get the longitude and latitude coordinates of the southeast and northwest corners of the image
        nw_lng, nw_lat = transform_matrix * (0, 0)
        se_lng, se_lat = transform_matrix * (width, height)

        lngs, lats = transform(src_crs, dst_crs, [nw_lng,se_lng],[nw_lat,se_lat])
        native_meta["spatial_range"] = {"northeast": {"lat": lats[0], "lng": lngs[1]}, "southwest": {"lat": lats[1], "lng": lngs[0]}}


    return native_meta


def adjust_meta_data(dir_path):
    meta_data = {}
    meta_data_file_name = "_".join(dir_path.split("/")[1:]) + ".json"
    meta_data_file_path = os.path.join(settings.CORE_DIR, 'data', meta_data_file_name)
    with open(meta_data_file_path, "r") as meta_data_file:
        meta_data = json.load(meta_data_file)

    meta_data["mode"] = []
    meta_data["category"] = []
    meta_data["format"] = []
    meta_data["label"] = []
    meta_data["time_range"] = {"start": "01/01/2030 00:00:00", "end": "01/01/2030 00:00:00"}
    meta_data["spatial_range"] = {"northeast": {"lat": 0, "lng": -180}, "southwest": {"lat": 90, "lng": 0}}
    # meta_data["subdirs"] = []
    meta_data["abs_path"] = dir_path
    meta_data["name"] = dir_path.split("/")[-1]

    # iterate through each sub path
    for p in meta_data["subdirs"]:
        sub_path = os.path.join(dir_path, p)
        sub_meta_data_file_name = "_".join(sub_path.split("/")[1:]) + ".json"
        with open(os.path.join(settings.CORE_DIR, 'data', sub_meta_data_file_name), "r") as sub_meta_data_file:
            sub_meta_data = json.load(sub_meta_data_file)

        # meta_data["subdirs"].append(sub_path)
        for c in sub_meta_data["category"]:
            meta_data["category"].append(c)
        for f in sub_meta_data["format"]:
            meta_data["format"].append(f)
        for l in sub_meta_data["label"]:
            meta_data["label"].append(l)
        for m in sub_meta_data["mode"]:
            meta_data["mode"].append(m)

        meta_data["category"] = list(set(meta_data["category"]))
        meta_data["format"] = list(set(meta_data["format"]))
        meta_data["label"] = list(set(meta_data["category"]))
        meta_data["mode"] = list(set(meta_data["mode"]))

        current_start = datetime.strptime(meta_data["time_range"]["start"], "%m/%d/%Y %H:%M:%S").timestamp()
        sub_start = datetime.strptime(sub_meta_data["time_range"]["start"], "%m/%d/%Y %H:%M:%S").timestamp()
        current_end = datetime.strptime(meta_data["time_range"]["end"], "%m/%d/%Y %H:%M:%S").timestamp()
        sub_end = datetime.strptime(sub_meta_data["time_range"]["end"], "%m/%d/%Y %H:%M:%S").timestamp()

        meta_data["time_range"]["start"] = datetime.fromtimestamp(min(current_start, sub_start)).strftime(
            "%m/%d/%Y %H:%M:%S")
        meta_data["time_range"]["end"] = datetime.fromtimestamp(max(current_end, sub_end)).strftime("%m/%d/%Y %H:%M:%S")

        # here we only consider north america
        meta_data["spatial_range"]["northeast"]["lat"] = max(meta_data["spatial_range"]["northeast"]["lat"],
                                                             sub_meta_data["spatial_range"]["northeast"]["lat"])
        meta_data["spatial_range"]["northeast"]["lng"] = max(meta_data["spatial_range"]["northeast"]["lng"],
                                                             sub_meta_data["spatial_range"]["northeast"]["lng"])

        meta_data["spatial_range"]["southwest"]["lat"] = min(meta_data["spatial_range"]["southwest"]["lat"],
                                                             sub_meta_data["spatial_range"]["southwest"]["lat"])
        meta_data["spatial_range"]["southwest"]["lng"] = min(meta_data["spatial_range"]["southwest"]["lng"],
                                                             sub_meta_data["spatial_range"]["southwest"]["lng"])

    meta_data_file_name = "_".join(dir_path.split("/")[1:]) + ".json"

    with open(os.path.join(settings.CORE_DIR, 'data', meta_data_file_name), "w") as meta_data_file:
        json.dump(meta_data, meta_data_file)

    if dir_path.split("/")[-2] == "home":
        return
    parent_dir = "/".join(dir_path.split("/")[:-1])
    adjust_meta_data(parent_dir)


def delete_meta_data(meta_data_path):
    with open(meta_data_path, "r") as meta_data_file:
        meta_data = json.load(meta_data_file)
    os.remove(meta_data_path)
    sub_dirs = meta_data["subdirs"]
    for subdir in sub_dirs:
        sub_meta_data_path = os.path.join(settings.CORE_DIR, 'data', "_".join(subdir.split("/")[1:]) + ".json")
        delete_meta_data(sub_meta_data_path)


def search(root_dir, search_box, category, mode, format, label,  realtime, time_range, spatial_range):
    result = []
    #if not os.path.exists(root_dir):
    #    return result

    # print(len(search_box))
    # search data
    # if we need to do a full search

    # print("mode " + str(mode))
    # if "File" in mode or "Folder" in mode:

    # root_dir = root_dir + "/ag_data"
    meta_data_file_name = "_".join(root_dir.split("/")[1:]) + ".json"
    #if not os.path.exists(os.path.join(settings.CORE_DIR, 'data', meta_data_file_name)):
    #    return [root_dir,os.path.join(settings.CORE_DIR, 'data', meta_data_file_name)]
    with open(os.path.join(settings.CORE_DIR, 'data', meta_data_file_name), "r") as meta_data_file:
        meta_data = json.load(meta_data_file)
        if "Collection" in meta_data["mode"]  and meta_data["name"] == "collections":
            for subdir in meta_data["subdirs"]:
                if filtering_condition(meta_data, search_box, category, mode, format, label, realtime, time_range, spatial_range):
                    sub_meta = get_meta_data(subdir)
                    result.append(sub_meta)
        else:
            if filtering_condition(meta_data, search_box, category, mode, format, label, realtime, time_range, spatial_range):
                result.append(meta_data)
            for subdir in meta_data["subdirs"]:

                sub_result = search(subdir, search_box, category, mode, format, label,  realtime, time_range, spatial_range)
                result += sub_result

    return result

    '''
    if "Domain" in mode:
        root_dir = root_dir + "/domains"
        meta_data_file_name = "_".join(root_dir.split("/")[1:]) + ".json"
        with open(os.path.join(settings.CORE_DIR, 'data', meta_data_file_name), "r") as meta_data_file:
            meta_data = json.load(meta_data_file)
            if filtering_condition(meta_data, search_box, category, mode, format, label, time_range, spatial_range):
                result.append(meta_data)

    if "Tool" in mode:
        root_dir = root_dir + "/tools"
        meta_data_file_name = "_".join(root_dir.split("/")[1:]) + ".json"
        with open(os.path.join(settings.CORE_DIR, 'data', meta_data_file_name), "r") as meta_data_file:
            meta_data = json.load(meta_data_file)
            if filtering_condition(meta_data, search_box, category, mode, format, label, time_range, spatial_range):
                result.append(meta_data)

    if "Model" in format:
        root_dir = root_dir + "/models"
        meta_data_file_name = "_".join(root_dir.split("/")[1:]) + ".json"
        with open(os.path.join(settings.CORE_DIR, 'data', meta_data_file_name), "r") as meta_data_file:
            meta_data = json.load(meta_data_file)
            if filtering_condition(meta_data, search_box, category, mode, format, label, time_range, spatial_range):
                result.append(meta_data)
    '''


def get_meta_data(path):
    meta_data_file_name = "_".join(path.split("/")[1:]) + ".json"
    meta_data_file_path = os.path.join(settings.CORE_DIR, 'data', meta_data_file_name)
    '''
    if not os.path.exists(meta_data_file_path):
 

        if("." in os.path.basename(path)):
            generate_meta_data_for_file(path,{"create":["null"]})
        else:
            generate_meta_data_for_dir(path,{"create":["null"]})

        parent_path = "/".join(path.split("/")[:-1])
        parent_meta_data_file_name = "_".join(parent_path.split("/")[1:]) + ".json"


        print(parent_meta_data_file_name)


        with open(os.path.join(settings.CORE_DIR, 'data', parent_meta_data_file_name), "r") as parent_meta_data_file:
            parent_meta_data = json.load(parent_meta_data_file)
            if path not in parent_meta_data["subdirs"]:
                parent_meta_data["subdirs"].append(path)

        with open(os.path.join(settings.CORE_DIR, 'data', parent_meta_data_file_name), "w") as parent_meta_data_file:
            json.dump(parent_meta_data,parent_meta_data_file)
    '''


    with open(os.path.join(settings.CORE_DIR, 'data', meta_data_file_name), "r") as meta_data_file:
        meta_data = json.load(meta_data_file)


    #if "Collection" in meta_data["mode"]:
    #    return meta_data

    if os.path.exists(path):
        # Get file/directory size
        size = os.path.getsize(path)
        # Get file/directory creation time
        create_time = datetime.fromtimestamp(os.path.getctime(path)).strftime("%m/%d/%Y, %H:%M:%S")
        # Get file/directory access time
        access_time = datetime.fromtimestamp(os.path.getatime(path)).strftime("%m/%d/%Y, %H:%M:%S")

    else:
        # Get file/directory size
        size = os.path.getsize(meta_data_file_path)
        # Get file/directory creation time
        create_time = datetime.fromtimestamp(os.path.getctime(meta_data_file_path)).strftime("%m/%d/%Y, %H:%M:%S")
        # Get file/directory access time
        access_time = datetime.fromtimestamp(os.path.getatime(meta_data_file_path)).strftime("%m/%d/%Y, %H:%M:%S")


    native_meta = {"name": os.path.basename(path), "created_time": create_time,
     "access_time": access_time, "size": size}

    if "native" not in meta_data:
        meta_data["native"] = {}

    for key in native_meta:
        meta_data["native"][key] = native_meta[key]


    #with open(os.path.join(settings.CORE_DIR, 'data', meta_data_file_name), "w") as meta_data_file:
    #    json.dump(meta_data,meta_data_file)


    file_name = path.split("/")[-1]
    if "." not in file_name:
        return meta_data
    suffix = file_name.split(".")[1]
    '''
    if suffix == "shp":
        sf = shapefile.Reader(path)
        meta_data["native"] = {"fields":sf.fields, "numRecords":sf.numRecords, "shapeType":sf.shapeType,"shapeTypeName":sf.shapeTypeName,"type":sf.__geo_interface__['type']}

        # Read shapefile using geopandas
        gdf = gpd.read_file(path)
        gdf = gdf.to_crs('EPSG:4326')
        # Get bounds of shapefile
        bounds = gdf.total_bounds if not gdf.empty else (-180, 0, -180, 0)
        minx, miny, maxx, maxy = bounds
        meta_data["native"]["spatial_range"]={"southwest":{"lat":miny,"lng":minx},"northeast":{"lat":maxy,"lng":maxx}}
    '''
    return meta_data





def get_file(path):
   return



def shp_to_image(shp_path,col): # plot a column of shape file as png image
    meta_data_file_name = "_".join(shp_path.split("/")[1:]) + ".json"

    #with open(os.path.join(settings.CORE_DIR, 'data', meta_data_file_name), "r") as meta_data_file:
    #    meta_data = json.dump(meta_data_file)

    img_path = f"{shp_path}_col_{col}.png"

    if os.path.exists(img_path):
        return img_path
        # Define colormap and plot the shapefile

    cmap = ListedColormap(
        ['#1a9850', '#91cf60', '#d9ef8b', '#fee08b', '#fc8d59', '#d73027', '#a50026', '#f46d43', '#fdae61',
         '#f0f0f0'])

    # Read shapefile using geopandas
    gdf = gpd.read_file(shp_path)
    gdf = gdf.to_crs('EPSG:4326')

    # Get bounds of shapefile
    bounds = gdf.total_bounds if not gdf.empty else (-180, 0, -180, 0)
    minx, miny, maxx, maxy = bounds

    aspect_ratio = (maxy - miny) / (maxx - minx)
    ax = gdf.plot(column=col, cmap=cmap, figsize=(12, 12 * aspect_ratio))

    # Set x and y limits based on the converted coordinates
    ax.set_xlim(minx, maxx)
    ax.set_ylim(miny, maxy)

    # Add title and remove axes
    # ax.set_title('Shapefile Plot')
    ax.set_axis_off()
    # remove all the margins
    plt.subplots_adjust(left=0, right=1, bottom=0, top=1, wspace=0, hspace=0)
    ax.margins(0)

    # Save figure to file
    plt.savefig(img_path, dpi=300, bbox_inches='tight')

    img_meta_data = generate_meta_data_for_file(img_path,{"shp to image":[shp_path]})
    img_meta_data["spatial_range"] = {"southwest": {"lat": miny, "lng": minx}, "northeast": {"lat": maxy, "lng": maxx}}

    shp_meta = get_meta_data(shp_path)
    if "downstream" not in shp_meta:
        shp_meta["downstream"] = {}

    if "shp to image" not in shp_meta["downstream"]:
        shp_meta["downstream"]["shp to image"] = []
    if img_path not in shp_meta["downstream"]["shp to image"]:
        shp_meta["downstream"]["shp to image"].append(img_path)

    #shp_meta["downstream"]["shp to image"] = [img_path]
    shp_meta_data_file_name = "_".join(shp_path.split("/")[1:]) + ".json"
    with open(os.path.join(settings.CORE_DIR, 'data', shp_meta_data_file_name), "w") as shp_meta_data_file:
        json.dump(shp_meta, shp_meta_data_file)



    img_meta_data_file_name = "_".join(img_path.split("/")[1:]) + ".json"

    with open(os.path.join(settings.CORE_DIR, 'data', img_meta_data_file_name), "w") as img_meta_data_file:
        json.dump(img_meta_data, img_meta_data_file)

    img_parent_path = "/".join(img_path.split("/")[:-1])
    img_parent_meta_data_file_name = "_".join(img_parent_path.split("/")[1:]) + ".json"
    with open(os.path.join(settings.CORE_DIR, 'data', img_parent_meta_data_file_name), "r") as img_parent_meta_data_file:
        img_parent_meta_data = json.load(img_parent_meta_data_file)

    if img_path not in img_parent_meta_data["subdirs"]:
        img_parent_meta_data["subdirs"].append(img_path)
    with open(os.path.join(settings.CORE_DIR, 'data', img_parent_meta_data_file_name), "w") as img_parent_meta_data_file:
        json.dump(img_parent_meta_data,img_parent_meta_data_file)

    return img_path


def tif_to_image(tif_path,band):

    img_path = f"{tif_path}_band_{band}.png"

    if os.path.exists(img_path):
        return img_path
        # Define colormap and plot the shapefile

    cmap = ListedColormap(
        ['#1a9850', '#91cf60', '#d9ef8b', '#fee08b', '#fc8d59', '#d73027', '#a50026', '#f46d43', '#fdae61',
         '#f0f0f0'])

    print(img_path)

    # Open TIF file
    with rasterio.open(tif_path) as dataset:

        if band == "RGBA":
            # Get image dimensions
            height = dataset.height
            width = dataset.width

            # Read red, green, blue, and alpha bands
            bands = dataset.read([1, 2, 3, 4], out_shape=(4, height, width))

            # Create a single RGBA array
            rgba_data = np.dstack((bands[0], bands[1], bands[2], bands[3])).astype(np.float32)

            # Scale the data to the range 0-255
            rgba_min = np.nanmin(rgba_data)
            rgba_max = np.nanmax(rgba_data)
            rgba_data_scaled = (255 * (rgba_data - rgba_min) / (rgba_max - rgba_min)).astype('uint8')

            # Create a PIL Image object and save as PNG
            image = Image.fromarray(rgba_data_scaled, mode='RGBA')
            image.save(img_path)

        else:


            band_data = dataset.read(int(band)).astype('float32')
            band_min = np.max([np.nanmin(band_data), 0])
            band_max = np.nanmax(band_data)
            print(band_min)
            print(band_max)

            #print(np.where(band_data <= 0, 0, band_data))
            band_data_scaled = (255 * (band_data - band_min) / (band_max - band_min)).astype('uint8')
            band_image = Image.fromarray(band_data_scaled)
            band_image.save(img_path)



    img_meta_data = generate_meta_data_for_file(img_path,{"tif to image":[tif_path]})
    tif_meta = get_meta_data(tif_path)
    if "downstream" not in tif_meta:
        tif_meta["downstream"] = {}

    if "tif to image" not in tif_meta["downstream"]:
        tif_meta["downstream"]["tif to image"] = []

    if img_path not in tif_meta["downstream"]["tif to image"]:
        tif_meta["downstream"]["tif to image"].append(img_path)

    tif_meta_data_file_name = "_".join(tif_path.split("/")[1:]) + ".json"
    with open(os.path.join(settings.CORE_DIR, 'data', tif_meta_data_file_name), "w") as tif_meta_data_file:
        json.dump(tif_meta,tif_meta_data_file)


    if "spatial_range" in tif_meta:
        img_meta_data["spatial_range"] = tif_meta["spatial_range"]

    img_meta_data_file_name = "_".join(img_path.split("/")[1:]) + ".json"

    with open(os.path.join(settings.CORE_DIR, 'data', img_meta_data_file_name), "w") as img_meta_data_file:
        json.dump(img_meta_data, img_meta_data_file)

    img_parent_path = "/".join(img_path.split("/")[:-1])
    img_parent_meta_data_file_name = "_".join(img_parent_path.split("/")[1:]) + ".json"
    with open(os.path.join(settings.CORE_DIR, 'data', img_parent_meta_data_file_name), "r") as img_parent_meta_data_file:
        img_parent_meta_data = json.load(img_parent_meta_data_file)

    if img_path not in img_parent_meta_data["subdirs"]:
        img_parent_meta_data["subdirs"].append(img_path)
    with open(os.path.join(settings.CORE_DIR, 'data', img_parent_meta_data_file_name), "w") as img_parent_meta_data_file:
        json.dump(img_parent_meta_data,img_parent_meta_data_file)


    return img_path


def update_parent_meta(abs_path):
    parent_dir = "/".join(abs_path.split("/")[:-1])
    parent_meta_data_file_name = "_".join(parent_dir.split("/")[1:]) + ".json"
    parent_meta_data_file_path = os.path.join(settings.CORE_DIR, 'data', parent_meta_data_file_name)

    if not os.path.exists(parent_meta_data_file_path):
        parent_meta_data = {"subdirs": []}
        if abs_path not in parent_meta_data["subdirs"]:
            parent_meta_data["subdirs"].append(abs_path)

        # with open(parent_meta_data_file_path, "w") as parent_meta_data_file:
        #    json.dump({"subdirs":[]}, parent_meta_data_file)

    else:
        with open(parent_meta_data_file_path, "r") as parent_meta_data_file:
            parent_meta_data = json.load(parent_meta_data_file)
            if "subdirs" not in parent_meta_data:
                parent_meta_data["subdirs"] = []
            if abs_path not in parent_meta_data["subdirs"]:
                parent_meta_data["subdirs"].append(abs_path)

    with open(parent_meta_data_file_path, "w") as parent_meta_data_file:
        json.dump(parent_meta_data, parent_meta_data_file)


def run_tool(entry_point,arg_values, arg_types,user):


    root_dir = f"/data/{user}/ag_data"


    client = docker.from_env()

    # assuming that the uploaded script is saved to a file on disk
    script_path = f"{entry_point}"


    entry_point_path = f"/data{entry_point}"
    entry_point_meta_data = get_meta_data(entry_point_path)
    tool = entry_point_path

    if "main_tool" in entry_point_meta_data:
        tool = entry_point_meta_data["main_tool"]

    # assuming that the script takes command-line arguments

    #mount_dirs_on_host = ["/".join(script_path.split("/")[:-1])]




    # Define the PID of the program to filter out
    pid = 1234

    # Define the events to watch for
    mask = pyinotify.IN_MODIFY | pyinotify.IN_CREATE | pyinotify.IN_DELETE | pyinotify.IN_ACCESS

    # Create a new WatchManager
    wm = pyinotify.WatchManager()

    # Associate the event handler with the WatchManager
    handler = EventHandler(pid)

    # Add a watch for the path with the specified mask
    wm.add_watch(root_dir, mask, rec=True, auto_add=True)

    notifier = pyinotify.Notifier(wm, handler)

    import threading
    # Start the notifier
    # Run the notifier in a separate thread

    import time
    notifier_thread = threading.Thread(target=notifier.loop, daemon=True)
    notifier_thread.start()

    if ".py" in entry_point.split("/")[-1]:
        image_name = "python_test"
        main_cmd = "python"


        output = client.containers.run(
            image_name,
            command=[main_cmd, script_path] + [arg_values[arg_name] for arg_name in arg_values],
            # command=[main_cmd, script_path],
            volumes={f"/data/{user}": {"bind": f"/{user}", "mode": "rw"}},
            # working_dir=working_dir,
            # environment={"VAR1": "value1", "VAR2": "value2"},
            detach=True,
            auto_remove=True
        )
    elif ".m" in entry_point.split("/")[-1]:
        image_name = "matlab_image"
        args =""
        i = 1
        for arg_value in arg_values:
            args += f"arg{i}='{arg_value}';"
            i = i+1

        #args = "arg1='{arg1}';arg2='{arg2}'"
        matlab_cmd = f"{args} run('{entry_point}');exit;"

        command = f"matlab -nodisplay -nosplash -nodesktop -r \""+matlab_cmd+"\""
        output = client.containers.run(
            image_name,
            command=command,#"matlab -nodisplay -nosplash -nodesktop -r \"arg1='/ypan12/ag_data'; arg2='/ypan12/ag_data'; run('/ypan12/ag_data/calcualte_canopy_height.m');exit\"" ,#"matlab -nodisplay -nosplash -nodesktop -r \"fid=fopen('/ypan12/ag_data/canopyheight.txt', 'w');fclose(fid);exit\"",
            # command=[main_cmd, script_path],
            volumes={f"/data/{user}": {"bind": f"/{user}", "mode": "rw"}},
            # working_dir=working_dir,
            # environment={"MLM_LICENSE_FILE": f"/{user}/ag_data/license.lic"},
            detach=True,
            auto_remove=True,
            user='root:root',
            mac_address='02:42:EF:BA:E1:95'
        )


    else:
        return



    '''
    timeout_seconds = 1000  # Set your desired timeout value in seconds

    try:
        output.wait(timeout=timeout_seconds)
    except docker.errors.Timeout:
        print(f"Container exceeded the {timeout_seconds} seconds time limit.")
        output.stop()
        output.remove(force=True)
    '''

    output.wait()
    notifier.stop()

    #time.sleep(3)
    #notifier_thread.join()


    written_files = list(handler.written_files)
    read_files = list(handler.accessed_files.difference(handler.written_files))
    created_files = list(handler.created_files)

    sorted_created_files = sorted(created_files, key=len)
    
    
    for created_file in sorted_created_files:
        if os.path.isfile(created_file):
            generate_meta_data_for_file(created_file,{})
        else:
            generate_meta_data_for_dir(created_file,{"create":["null"]})

        parent_path = "/".join(created_file.split("/")[:-1])
        parent_meta_data_file_name = "_".join(parent_path.split("/")[1:]) + ".json"

        with open(os.path.join(settings.CORE_DIR, 'data', parent_meta_data_file_name),"r") as parent_meta_data_file:
            parent_meta_data = json.load(parent_meta_data_file)
            if created_file not in parent_meta_data["subdirs"]:
                parent_meta_data["subdirs"].append(created_file)

        with open(os.path.join(settings.CORE_DIR, 'data', parent_meta_data_file_name), "w") as parent_meta_data_file:
            json.dump(parent_meta_data, parent_meta_data_file)


    for written_file in written_files:
        if os.path.isdir(written_file):
            continue

        written_meta_data_file_name = "_".join(written_file.split("/")[1:]) + ".json"
        with open(os.path.join(settings.CORE_DIR, 'data', written_meta_data_file_name),"r") as written_meta_data_file:
            written_meta_data = json.load(written_meta_data_file)
        if "upstream" not in written_meta_data:
            written_meta_data["upstream"] = {}
        if tool not in written_meta_data["upstream"]:
            written_meta_data["upstream"][tool] = []
        #written_meta_data["upstream"][tool] = []

        for read_file in read_files:
            if os.path.isdir(read_file):
                continue
            if tool in read_file:
                continue
            if read_file in written_meta_data["upstream"][tool]:
                continue

            written_meta_data["upstream"][tool].append(read_file)

        with open(os.path.join(settings.CORE_DIR, 'data', written_meta_data_file_name),"w") as written_meta_data_file:
            json.dump(written_meta_data,written_meta_data_file)

    for read_file in read_files:
        if os.path.isdir(read_file) or tool in read_file:
            continue

        read_meta_data_file_name = "_".join(read_file.split("/")[1:]) + ".json"
        with open(os.path.join(settings.CORE_DIR, 'data', read_meta_data_file_name), "r") as read_meta_data_file:
            read_meta_data = json.load(read_meta_data_file)
        if "downstream" not in read_meta_data:
            read_meta_data["downstream"] = {}
        #read_meta_data["downstream"][tool] = []
        if tool not in read_meta_data["downstream"]:
            read_meta_data["downstream"][tool] = []

        for written_file in written_files:
            if os.path.isdir(written_file):
                continue
            if written_file in read_meta_data["downstream"][tool]:
                continue

            read_meta_data["downstream"][tool].append(written_file)

        with open(os.path.join(settings.CORE_DIR, 'data',  read_meta_data_file_name),"w") as  read_meta_data_file:
            json.dump( read_meta_data, read_meta_data_file)




    return


def trim_path_header(path):
    if path[:5] == "/data":
        return path[5:]
    else:
        return path

def get_pipeline(path):
    graph = {"nodes":[],"links":[]}
    graph["nodes"].append({"id":trim_path_header(path), "label":trim_path_header(path),"node_status":"current"})
    meta_data = get_meta_data(path)
    if "upstream" in meta_data:
        for upstream_tool in meta_data["upstream"]:
            for upstream_path in meta_data["upstream"][upstream_tool]:
                graph["links"].append({"source":trim_path_header(upstream_path),"target":trim_path_header(path),"label":trim_path_header(upstream_tool)})

                get_upstream(upstream_path,graph)

    if "downstream" in meta_data:
        for downstream_tool in meta_data["downstream"]:
            for downstream_path in meta_data["downstream"][downstream_tool]:
                graph["links"].append({"source":trim_path_header(path),"target":trim_path_header(downstream_path),"label":trim_path_header(downstream_tool)})

                get_downstream(downstream_path,graph)
    return graph

def get_upstream(path,graph):
    for node in graph["nodes"]:
        if node["id"] == trim_path_header(path):
            return
    if not os.path.exists(path):
        graph["nodes"].append({"id": trim_path_header(path), "label": trim_path_header(path),"node_status":"dead"})
        return


    graph["nodes"].append({"id": trim_path_header(path), "label": trim_path_header(path)})

    meta_data = get_meta_data(path)
    if "upstream" in meta_data:
        for upstream_tool in meta_data["upstream"]:
            for upstream_path in meta_data["upstream"][upstream_tool]:
                graph["links"].append({"source":trim_path_header(upstream_path),"target":trim_path_header(path),"label":trim_path_header(upstream_tool)})

                get_upstream(upstream_path, graph)


def get_downstream(path,graph):
    for node in graph["nodes"]:
        if node["id"] == trim_path_header(path):
            return

    if not os.path.exists(path):
        graph["nodes"].append({"id": trim_path_header(path), "label": trim_path_header(path),"node_status":"dead"})
        return



    graph["nodes"].append({"id": trim_path_header(path), "label": trim_path_header(path)})

    meta_data = get_meta_data(path)
    if "downstream" in meta_data:
        for downstream_tool in meta_data["downstream"]:
            for downstream_path in meta_data["downstream"][downstream_tool]:
                graph["links"].append({"source":trim_path_header(path),"target":trim_path_header(downstream_path),"label":trim_path_header(downstream_tool)})

                get_downstream(downstream_path, graph)


def add_to_collection(selected_collection,selected_file_path,username):

    selected_collection_path = f"/data/{username}/ag_data/collections/{selected_collection}"

    selected_collection_meta_data = get_meta_data(selected_collection_path)

    if selected_file_path in selected_collection_meta_data["subdirs"]:
        return


    selected_collection_meta_data["subdirs"].append(selected_file_path)
    
    selected_collection_meta_data_file_name = "_".join(selected_collection_path.split("/")[1:]) + ".json"
    with open(os.path.join(settings.CORE_DIR, 'data', selected_collection_meta_data_file_name), "w") as selected_collection_meta_data_file:
        json.dump(selected_collection_meta_data,selected_collection_meta_data_file)



def remove_from_collection(collection_name, file_path, username):
    collection_path = f"/data/{username}/ag_data/collections/{collection_name}"
    collection_meta_data = get_meta_data(collection_path)

    collection_meta_data["subdirs"].remove(file_path)

    collection_meta_data_file_name = "_".join(collection_path.split("/")[1:]) + ".json"
    with open(os.path.join(settings.CORE_DIR, 'data', collection_meta_data_file_name),
              "w") as collection_meta_data_file:
        json.dump(collection_meta_data, collection_meta_data_file)




