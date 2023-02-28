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


# map logic_path to real_path, for example impanyu/ENREC/1.png -> /home/impanyu/ag_data/ENREC/1.png
def map_file_path(logic_path, username):
    real_path = ""

    for i in range(1, len(logic_path.split("/"))):
        real_path += "/" + logic_path.split("/")[i]

    if real_path == "":
        real_path = "."
    else:
        real_path = real_path[1:]

    real_path = os.path.join("/home/" + username + "/ag_data/", real_path)
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
        time_lower = int(datetime.strptime("1970", "%Y").strftime("%s"))
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


def filtering_condition(data, search_box, category, mode, format, label, time_range, bounding_box):
    return True
    item_name = data["path"].split("/")[-1]
    if not search_box in data["path"]:
        return False

    has_category = False
    for c in category:
        if c in data["category"]:
            has_category = True
            break
    if not has_category:
        return False

    for m in mode:
        if not m == data["mode"]:
            return false

    has_format = False
    for f in format:
        if f in data["format"]:
            has_format = True
            break
    if not has_format:
        return False

    has_label = False
    for l in label:
        if l in data["label"]:
            has_label = True
            break
    if not has_label:
        return False

    start = datetime.strptime(time_range[0], "Y/m/d").timestamp()
    end = datetime.strptime(time_range[1], "Y/m/d").timestamp()
    item_time = datetime.strptime(data["time"], "Y/m/d %H:%M:%S").timestamp()

    if item_time > end or item_time < start:
        return False

    southwest = bounding_box[0]
    northeast = bounding_box[1]
    item_loc = data["loc"]

    if not (southwest == "Southwest Corner" and northeast == "Northeast Corner"):
        lower_lat, upper_lat, left_ln, right_ln = extract_coordinates(southwest, northeast)
        if item_loc["lat"] < lower_lat or item_loc["lat"] > upper_lat:
            return False
        if item_loc["lng"] < left_ln or item_loc["lng"] > right_ln:
            return False

    return True


from sklearn.metrics.pairwise import euclidean_distances


# [data["mode"],data["category"],data["label"],data["loc"],data["time"],data["format"]]
# mode, category and time are string, label and format are list, loc is dict
def distance(x, y):
    d = 0

    if not x[0] == y[0]:
        d = d + 1
    if not x[1] == y[1]:
        d = d + 1
    for l in x[2]:
        if not l in y[2]:
            d = d + 1
    for l in y[2]:
        if not l in x[2]:
            d = d + 1
    '''
    d = d+ euclidean_distances([[x[3]["lat"]/90,x[3]["lng"]/180]],[[y[3]["lat"]/90,y[3]["lng"]/180]])
    x_time = datetime.strptime(x[4], "%Y/%m/%d %H:%M:%S").timestamp()
    y_time = datetime.strptime(y[4], "%Y/%m/%d %H:%M:%S").timestamp()
    d = d+ abs(x_time - y_time) / (365*12*30*24*3600)
    '''
    for l in x[5]:
        if not l in y[5]:
            d = d + 1
    for l in y[5]:
        if not l in x[5]:
            d = d + 1

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
        return np.array([])
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
                             "loc": {"lat": 0, "lng": 0}, "time": "1970/1/1 00:00:00", "format": []}

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


def aggregate_meta_data(dir_path):
    meta_data = {}
    # if this is a file
    if not os.path.isdir(dir_path):
        return generate_meta_data_for_file(dir_path)
    meta_data["mode"] = "Folder"
    meta_data["category"] = []
    meta_data["format"] = []
    meta_data["label"] = []
    meta_data["time_range"] = {"start": "2030/01/01 00:00:00", "end": "1970/01/01 00:00:00"}
    meta_data["spatial_range"] = {"northeast": {"lat": 0, "lng": -180}, "southwest": {"lat": 90, "lng": 0}}
    meta_data["subdirs"] = []

    # iterate through each sub path
    for p in os.listdir(dir_path):
        sub_path = os.path.join(dir_path,p)
        sub_meta_data = aggregate_meta_data(sub_path)
        meta_data["subdirs"] .append(sub_path)
        for c in sub_meta_data["category"]:
            meta_data["category"].append(c)
        for f in sub_meta_data["format"]:
            meta_data["format"].append(f)
        for l in sub_meta_data["label"]:
            meta_data["format"].append(l)

        current_start = datetime.strptime(meta_data["time_range"]["start"], "%Y/%m/%d %H:%M:%S").timestamp()
        sub_start = datetime.strptime(sub_meta_data["time_range"]["start"], "%Y/%m/%d %H:%M:%S").timestamp()
        current_end = datetime.strptime(meta_data["time_range"]["end"], "%Y/%m/%d %H:%M:%S").timestamp()
        sub_end = datetime.strptime(sub_meta_data["time_range"]["end"], "%Y/%m/%d %H:%M:%S").timestamp()

        meta_data["time_range"]["start"] = datetime.fromtimestamp(min(current_start, sub_start)).strftime(
            "%Y/%m/%d %H:%M:%S")
        meta_data["time_range"]["end"] = datetime.fromtimestamp(max(current_end, sub_end)).strftime("%Y/%m/%d %H:%M:%S")

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

    return meta_data


def generate_meta_data_for_file(file_path):
    meta_data = {}
    meta_data["mode"] = "File"
    meta_data["category"] = []
    meta_data["format"] = []
    meta_data["label"] = []
    meta_data["time_range"] = {"start": "2030/01/01 00:00:00", "end": "1970/01/01 00:00:00"}
    meta_data["spatial_range"] = {"northeast": {"lat": 0, "lng": -180}, "southwest": {"lat": 90, "lng": 0}}

    suffix = file_path.split("/")[-1].split(".")[1]

    if suffix == ".py":
        meta_data["format"].append("Python")
    elif suffix == "tif" \
            or suffix == "tiff" \
            or suffix == "png" \
            or suffix == "jpg" \
            or suffix == "jpeg": \
            meta_data["format"].append("Image")
    elif suffix == ".shp":
        meta_data["format"].append("Shape")
    elif suffix == ".m" or suffix == ".mlx":
        meta_data["format"].append("Matlab")
    elif suffix == ".r":
        meta_data["format"].append("R")
    elif suffix == "csv":
        meta_data["format"].append("CSV")
    elif suffix == "xlsx" or suffix == "xls":
        meta_data["format"].append("Spreadsheet")
    else:
        meta_data["format"].append("Other")

    if suffix == "tif" or suffix == "tiff":
        meta_data["spatial_range"] = read_tif_meta(file_path)

    meta_data_file_name = "_".join(file_path.split("/")[1:]) + ".json"

    with open(os.path.join(settings.CORE_DIR, 'data', meta_data_file_name), "w") as meta_data_file:
        json.dump(meta_data, meta_data_file)

    return meta_data


def read_tif_meta(file_path):
    # Open the GeoTIFF file
    with rasterio.open(file_path) as src:
        # Get the image's CRS (Coordinate Reference System)
        crs = CRS.from_epsg(4326)
        if src.crs != crs:
            return {"northeast": {"lat": 0, "lng": -180}, "southwest": {"lat": 90, "lng": 0}}

        # Get the image's transform (mapping from pixel coordinates to world coordinates)
        transform = src.transform

        # Get the image's width and height in pixels
        width = src.width
        height = src.height

        # Get the longitude and latitude coordinates of the southeast and northwest corners of the image
        nw_lng, nw_lat = transform * (0, 0)
        se_lng, se_lat = transform * (width, height)
    return {"northeast": {"lat": nw_lat, "lng": nw_lng}, "southwest": {"lat": se_lat, "lng": se_lng}}
