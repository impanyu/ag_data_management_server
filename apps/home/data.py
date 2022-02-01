# -*- encoding: utf-8 -*-
from django.conf import settings
from django.core.files.storage import FileSystemStorage
import os
from pandas import DataFrame, read_csv
import json
import pandas as pd 
import numpy as np

def retrieve_sub_domains(domain_path,session):
    if domain_path=="/spidercam":
        domains=["1373"]
        for i in [1374,1375,1376]:
            if str(i) in session:
                domains.append(str(i))

        #domains=[str(i) for i in [1373,1374,1375,1376]]
        #domains.insert(0,"spidercam")
        return domains
    elif domain_path=="/soilwater":
        domains=["0.15m","0.45m","0.75m"]
        return domains
    else: 
        return [] 

def retrieve_layers(domain_path):
    if domain_path=="/spidercam/1373":
    
        return ["RGB","NIR","Infrared_Soil","Infrared_Vege"]#,"PixelArray_Soil", "PixelArray_Vege","TemperatureMatrix_Soil","TemperatureMatrix_Vege"]
    elif domain_path=="/soilwater/0.15m":
        return ["water_content"]
    else:
        return []


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
    elif subdomain_path=="/spidercam/1376":
        return ["20210521182709"]

    else:
        return ["all"]



def retrieve_sub_domain_data(subdomain_path,layer,time):

    subdomain_dir = subdomain_path.split('/')


    subdomain=subdomain_dir[1]

    for i in range(2,len(subdomain_dir)):

        subdomain = subdomain+"_"+subdomain_dir[i]
    #print(settings.MEDIA_ROOT)

    if(subdomain_dir[1]=="spidercam"):
        return settings.STATIC_URL+"data_cache/"+subdomain+"_"+layer+"_"+time+".png"

    elif(subdomain_dir[1]=="soilwater"):

        fs_cache = FileSystemStorage(location=os.path.join(settings.CORE_DIR, 'data')+"/data_cache")
        fs_data = FileSystemStorage(location=os.path.join(settings.CORE_DIR, 'data')+"/users/impanyu")

        output_file_name = subdomain+"_"+time+"_"+layer+".json"
        output_time_file_name = "soilwater_time.json";

        if(not fs_cache.exists(output_file_name)):
            

            raw_file_path = os.path.join(settings.CORE_DIR,'data/users/impanyu/soilwater.xlsx')


            df=pd.read_excel(raw_file_path,converters={'z6-13171':str})
            print("ok")
            




            df['z6-13171'].replace('', np.nan, inplace=True)
            #df = df[df['VAERS ID']!=np.nan]
            df.dropna(subset=['z6-13171'], inplace=True)


            soilwaters=df[subdomain_dir[2]][2:df.shape[0]].tolist()
            times=df['z6-13171'][2:df.shape[0]].tolist()



            

            with fs_cache.open(output_file_name,"w") as output_file:
                json.dump(soilwaters,output_file)

            
            with fs_cache.open(output_time_file_name,"w") as output_time_file:
                json.dump(times,output_time_file)

        else:
            with fs_cache.open(output_file_name,"r") as output_file:
                soilwaters=json.load(output_file)

            
            with fs_cache.open(output_time_file_name,"r") as output_time_file:
                times=json.load(output_time_file)



                    
        return json.dumps({"soilwaters": soilwaters,"times":times})






