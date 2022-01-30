# -*- encoding: utf-8 -*-
from django.conf import settings

import os

def retrieve_sub_domains(subdomain_path,session):
    if subdomain_path=="/spidercam":
        domains=["1373"]
        for i in [1374,1375,1376]:
            if str(i) in session:
                domains.append(str(i))

        #domains=[str(i) for i in [1373,1374,1375,1376]]
        #domains.insert(0,"spidercam")
        return domains

def retrieve_layers(subdomain_path):
    
    return ["RGB","NIR","Infrared_Soil","Infrared_Vege"]#,"PixelArray_Soil", "PixelArray_Vege","TemperatureMatrix_Soil","TemperatureMatrix_Vege"]


def retrieve_times(subdomain_path,session):
    
    #print(session["1375"])
    if subdomain_path=="/spidercam/1373":
        return ["20210521182617"]

    elif subdomain_path=="/spidercam/1374":
        result=[]
        if  "20210521175836" in session["1374"]:
            result.append("20210521175836")
        if "20210521182634" in session["1374"]:
            result.append("20210521182634")    

        return result

    elif subdomain_path=="/spidercam/1375":
        print(session["1375"])
        result=[]

        if "20210521182651" in session["1375"]:
            result.append("20210521182651")

        if "20210521175855" in session["1375"]:   
            result.append("20210521175855")
        print(session["1375"])
        

        return result
    else:
        return ["20210521182709"]


def retrieve_sub_domain_data(subdomain_path,layer,time):

    subdomain_dir = subdomain_path.split('/')

    subdomain=subdomain_dir[1]

    for i in range(2,len(subdomain_dir)):

        subdomain = subdomain+"_"+subdomain_dir[i]
    #print(settings.MEDIA_ROOT) 
    return settings.STATIC_URL+"data_cache/"+subdomain+"_"+layer+"_"+time+".png"




