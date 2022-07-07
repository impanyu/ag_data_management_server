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


def add_to_new_domain(domain_name, start_date, end_date, southwest, northeast, file_path):
    domain_data_path = os.path.join(settings.CORE_DIR, 'data', 'domain_data.json')
    if not os.path.exists(domain_data_path):
        with open(domain_data_path, 'w') as domain_data_file:
            domain_data = {domain_name:[]}
            domain_data[domain_name].append({"bounding_box": [southwest,northeast],"date_range":[start_date,end_date],"file_path":file_path})
            json.dump(domain_data, domain_data_file)

    else:
        with open(domain_data_path, 'r') as domain_data_file:
            domain_data = json.load(domain_data_file)
        if(domain_name not in domain_data):
            domain_data[domain_name] = []
        domain_data[domain_name].append({"bounding_box": [southwest, northeast], "date_range": [start_date, end_date], "file_path": file_path})

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
