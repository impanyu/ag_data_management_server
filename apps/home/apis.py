from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import authentication, permissions
from django.contrib.auth.models import User
from rest_framework import serializers
import os
from rest_framework import status
from django.conf import settings
from django.http import HttpResponse
from .data import *
import json
from django.views.decorators.csrf import csrf_exempt
from .native_tools import *
from django.shortcuts import redirect
from django.template import loader
import urllib.parse
import time
from dotenv import load_dotenv

from google_auth_oauthlib.flow import Flow

class FileUploadSerializer(serializers.Serializer):
    # Define a file field in your serializer
    # You can specify additional arguments for FileField to further customize its behavior
    # For example, you can set `allow_empty_file=False` to prevent empty files from being uploaded
    # `max_length` could be used to specify the maximum length of the file name
    file = serializers.FileField(allow_empty_file=False, max_length=100)
    # Use a ListField with a child FileField to accept multiple files

    #files = serializers.ListField(
    #    child=serializers.FileField(allow_empty_file=False, max_length=100),
    #    allow_empty=False  # Prevent empty list
    #)
    target_path = serializers.CharField(max_length=200)  # Adjust max_length as needed

    def validate_file(self, value):
        # Implement custom validation logic if needed
        # For example, you could check the file's size, type, or name here
        # This example checks the file size and restricts it to 10MB

        # 10MB limit
        max_upload_size = 10 * 1024 * 1024

        #if value.size > max_upload_size:
        #    raise serializers.ValidationError("File size exceeds the allowed limit of 10MB.")
        #for uploaded_file in value:
        if value.size > max_upload_size:
            raise serializers.ValidationError("One or more files exceed the allowed limit of 10MB.")


        # If you want to restrict file types, you can do so by examining `value.content_type`
        # Example: Allow only text files and images
        #allowed_types = [
        #    'text/plain',
        #    'image/jpeg',
        #    'image/png',
            # Add other MIME types as needed
        #]
        #if value.content_type not in allowed_types:
        #    raise serializers.ValidationError("Unsupported file type.")

        return value


class API(APIView):
    """
    View to list all users in the system.

    * Requires token authentication.
    * Only admin users are able to access this view.
    """
    authentication_classes = [authentication.TokenAuthentication]
    #permission_classes = [permissions.IsAdminUser]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, format=None):
        """
        Return a list of all users.
        """
        usernames = [user.username for user in User.objects.all()]
        return Response(usernames)



class FileUploadView(APIView):
    def post(self, request, *args, **kwargs):
        # Assuming the serializer handles file validation but not the target path
        serializer = FileUploadSerializer(data=request.data)
        
        if serializer.is_valid():
            file = serializer.validated_data['file']
            target_path = request.data.get('target_path')
            files = [file]
           

            
            if "relative_paths" not in request.data:
                relative_paths = []
            else:
                relative_paths = request.data.getlist('relative_paths')
            

            # Sanitize and validate the target_path
            safe_path = os.path.normpath(target_path).lstrip('/')
            #if not is_valid_path(safe_path):
            #    return Response({"message": "Invalid upload path."}, status=status.HTTP_400_BAD_REQUEST)
            current_user = request.user.username

            for file in files:
                if len(relative_paths) == 0:
                    relative_path = ""
                else:
                    relative_path = relative_paths[files.index(file)]
                safe_relative_path = os.path.normpath(relative_path).lstrip('/')

                full_path = os.path.join(settings.USER_DATA_DIR, current_user,"ag_data",safe_path, safe_relative_path, file.name)
                os.makedirs(os.path.dirname(full_path), exist_ok=True)

                with open(full_path, 'wb+') as destination:
                    for chunk in file.chunks():
                        destination.write(chunk)

            return Response({"message": f"File uploaded successfully as {full_path}"}, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
class FileDownloadView(APIView):

    def get(self, request, *args, **kwargs):
        target_path = request.query_params.get('target_path')
        #file_name = request.query_params.get('file_name')

        # Sanitize and validate the target_path
        safe_path = os.path.normpath(target_path).lstrip('/')
        current_user = request.user.username

        # Construct the full file path
        full_path = os.path.join(settings.USER_DATA_DIR, current_user, "ag_data", safe_path)

        # Validate path to prevent path traversal attacks
        # Ensure full_path is within the allowed directory
        if not os.path.commonprefix([full_path, os.path.join(settings.USER_DATA_DIR, current_user, "ag_data")]) == os.path.join(settings.USER_DATA_DIR, current_user, "ag_data"):
            return Response({"message": "Invalid file path."}, status=status.HTTP_400_BAD_REQUEST)

        if os.path.exists(full_path) and os.path.isfile(full_path):
            with open(full_path, 'rb') as file:
                file_name = os.path.basename(full_path)
                response = HttpResponse(file, content_type='application/octet-stream')
                response['Content-Disposition'] = f'attachment; filename="{file_name}"'
                return response
        else:
            return Response({"message": "File not found."}, status=status.HTTP_404_NOT_FOUND)
        
class FileUploadNewLineView(APIView):

    def get(self, request, *args, **kwargs):
        target_path = request.query_params.get('target_path')
        new_line = request.query_params.get('new_line')
        if new_line is None:
            new_line = ""
        else:
            new_line += "\n"

        #file_name = request.query_params.get('file_name')

        # Sanitize and validate the target_path
        safe_path = os.path.normpath(target_path).lstrip('/')
        current_user = request.user.username

        # Construct the full file path
        full_path = os.path.join(settings.USER_DATA_DIR, current_user, "ag_data", safe_path)

        # Validate path to prevent path traversal attacks
        # Ensure full_path is within the allowed directory
        if not os.path.commonprefix([full_path, os.path.join(settings.USER_DATA_DIR, current_user, "ag_data")]) == os.path.join(settings.USER_DATA_DIR, current_user, "ag_data"):
            return Response({"message": "Invalid file path."}, status=status.HTTP_400_BAD_REQUEST)

        if os.path.exists(full_path) and os.path.isfile(full_path):
            with open(full_path, 'a') as file:
                file.write(new_line)
                #file_name = os.path.basename(full_path)
                #response = HttpResponse(file, content_type='application/octet-stream')
                #response['Content-Disposition'] = f'attachment; filename="{file_name}"'
                return Response({"message": f"New line uploaded successfully to {full_path}"}, status=status.HTTP_201_CREATED)
        else:
            return Response({"message": "File not found."}, status=status.HTTP_404_NOT_FOUND)
        

class GetMetaDataView(APIView):

    def get(self, request, *args, **kwargs):
        target_path = request.query_params.get('target_path')
        #file_name = request.query_params.get('file_name')

        # Sanitize and validate the target_path
        safe_path = os.path.normpath(target_path).lstrip('/')
        current_user = request.user.username

        # Construct the full file path
        full_path = os.path.join(settings.USER_DATA_DIR, current_user, "ag_data", safe_path)
       
        meta_data = get_meta_data(full_path)
        response = json.dumps(meta_data)
        return HttpResponse(response)


class ListFilesView(APIView):

    def get(self, request, *args, **kwargs):
        target_path = request.query_params.get('target_path')
        #file_name = request.query_params.get('file_name')

        # Sanitize and validate the target_path
        safe_path = os.path.normpath(target_path).lstrip('/')
        current_user = request.user.username

        # Construct the full file path
        full_path = os.path.join(settings.USER_DATA_DIR, current_user, "ag_data", safe_path)
       
        meta_data = get_meta_data(full_path)
        items = []
        if  "subdirs" in meta_data:

            for sub_path in meta_data["subdirs"]:
                items.append(sub_path[5:])
            items = sorted(items, key=lambda item: item)
       
        response = json.dumps(items)
        return HttpResponse(response)
    
class CreateFolder(APIView):

    def get(self, request, *args, **kwargs):
        target_path = request.query_params.get('target_path')
        safe_path = os.path.normpath(target_path).lstrip('/')
        current_user = request.user.username

        # Construct the full file path
        full_path = os.path.join(settings.USER_DATA_DIR, current_user, "ag_data", safe_path)
       
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        
        response = json.dumps({"result":f"folder {full_path} created success"})
        return HttpResponse(response)



class RunToolView(APIView):
    def get(self, request, *args, **kwargs):

        
        if 'entry_point' not in request.query_params:
            return Response({"message": "No tools provided."}, status=status.HTTP_400_BAD_REQUEST)
        
        if 'arg_values'  not in request.query_params :
            arg_values = []
        else:
            arg_values = request.query_params.getlist('arg_values')


        entry_point = request.query_params.get('entry_point')
        
        #arg_values = request.query_params.getlist('arg_values')
        

        #request_data = json.loads(request.body)
        #entry_point = request_data["entry_point"]
        #arg_values = request_data["arg_values"]
        arg_types = {}
        exe_env = "default"
        current_user = request.user.username

        safe_entry_point = os.path.normpath(entry_point).lstrip('/')
        safe_entry_point = f"/{current_user}/ag_data/{safe_entry_point}"

        for arg in arg_values:
            if("/" in arg):
                safe_arg = os.path.normpath(arg).lstrip('/')
                safe_arg = f"/{current_user}/ag_data/{safe_arg}"
                arg_values[arg_values.index(arg)] = safe_arg
        print(safe_entry_point)
        print(arg_values)
        
        container_id = run_tool(safe_entry_point,arg_values, arg_types,current_user,exe_env)
     
        
        #print(container_id)

        # Sanitize and validate the target_path
        #safe_path = os.path.normpath(target_path).lstrip('/')
        

        # Construct the full file path
        #full_path = os.path.join(settings.USER_DATA_DIR, current_user, "ag_data", safe_path)
       
       
        response = json.dumps({"running_instance_id":container_id})
        
        return HttpResponse(response)
    

class CheckRunningInstance(APIView):

    def get(self, request, *args, **kwargs):
        container_id = request.query_params.get('running_instance_id')
        response = check_running_instance(container_id)
        response = json.dumps(response)
        return HttpResponse(response)


class GetRunningInstance(APIView):

    def get(self, request, *args, **kwargs):
        target_path = request.query_params.get('target_path')
        #file_name = request.query_params.get('file_name')

        # Sanitize and validate the target_path
        safe_path = os.path.normpath(target_path).lstrip('/')
        current_user = request.user.username

        # Construct the full file path
        #full_path = os.path.join(settings.USER_DATA_DIR, current_user, "ag_data", safe_path)
       
        #meta_data = get_meta_data(full_path)
        target_path = os.path.join(settings.USER_DATA_DIR, safe_path)
        containers = get_running_containers_by_path(current_user,target_path)
        results= {}
        for container in containers:
            response = check_running_instance(container)
            results[container]=response
            

        return HttpResponse(json.dumps(results))

    
class StopRunningInstance(APIView):

    def get(self, request, *args, **kwargs):
        container_id = request.query_params.get('running_instance_id')
        response = stop_container(container_id)
        
        response = json.dumps(response)
        return HttpResponse(response)
    

class Search(APIView):
    def get(self, request, *args, **kwargs):
        root_dir = request.query_params.get('root_dir',"")
        search_box = request.query_params.get('search_box',"")
        category = request.query_params.getlist('category',["All"])
        mode = request.query_params.getlist('mode',["All"])
        format = request.query_params.getlist('form',["Python"])
        label = request.query_params.getlist('label',["All"])
        realtime = request.query_params.getlist('realtime',["All"])
        time_range = request.query_params.getlist('time_range',["start","end"])
        spatial_range = request.query_params.getlist('spatial_range',["southwest","northeast"])

      
        root_dir = os.path.join(settings.USER_DATA_DIR, request.user.username, "ag_data",root_dir)

        result = search(root_dir, search_box, category, mode, format, label,  realtime, time_range, spatial_range)

        response = json.dumps(result)
        #response = json.dumps({"result":"success"})
        return HttpResponse(response)



class JD_authorization_code(APIView):

    def get(self, request, *args, **kwargs):
        target_path = request.query_params.get('file_path') #this is already abs path
        load_dotenv()
        #safe_path = os.path.normpath(target_path).lstrip('/')
        #current_user = request.user.username

        # Construct the full file path
        full_path = target_path#os.path.join(settings.USER_DATA_DIR, current_user, "ag_data", safe_path)
        request.session['JD_tokens'] = {full_path:""}
       
        #os.makedirs(os.path.dirname(full_path), exist_ok=True)
        authorization_link = get_JD_authorization_code(full_path)
        # redirect the user to the authorization link
        #response = json.dumps({"authorization_link":authorization_link})
        
        #response = json.dumps({"result":f"folder {full_path} connected to JD"})
        return redirect(authorization_link)


class JD_access_token(APIView):

    def get(self, request, *args, **kwargs):
        authorization_code = request.query_params.get('code')
        load_dotenv()

        token = get_JD_token(authorization_code)
        url = get_JD_organizations()
        if not url == None:
            return redirect(url)
        #response = json.dumps(token)
        else:
            # get file path from the session
            JD_tokens = request.session.get('JD_tokens')
            for path in JD_tokens:
                if JD_tokens[path] == "":
                    file_path = path
                    
               
                    populate_JD_dir(file_path,token)
            context = {
                "result": "success"
            }
            file_path = "/".join(file_path.split("/")[2:])
            #encode file_path as uri component

            file_path = urllib.parse.quote(file_path)

         
            
            html_template = loader.get_template('home/files.html')
            # append the file path as url parameter to the template
            return redirect(f"/files.html?current_path={file_path}")
            #return HttpResponse(f"dir is populated {file_path}")



class Realm5_Weather_Connect(APIView):
    def get(self, request, *args, **kwargs):
        current_path = request.query_params.get('file_path')
        device_id = "0x019004F8"
        occurred_after = "2024-1-1"
        API_KEY = "U7nEMFir1hMKTucbRsqeC2joTYGXpJy2"
        API_URL = "https://app.realmfive.com/api/v2/weather_stations/observations"

        #response = requests.get(f"{API_URL}/{device_id}&occurred_after={occurred_after}", headers={"X-API-KEY":API_KEY})
        #get today's date and interate from the occurred_after date to today's date
        #for each date, get the weather data and save it to the file
        start_date = datetime.strptime(occurred_after, "%Y-%m-%d")
        current_date = start_date
        end_date = datetime.now()
        #iterate from start_date to today's date and get the weather data
        while current_date <= end_date:
            date = current_date.strftime("%Y-%m-%d")
            response = requests.get(f"{API_URL}/{device_id}?occurred_after={date}&occurred_before={date}", headers={"X-API-KEY":API_KEY})
            data = response.json()
            file_path = f"/{current_path}/weather_data_{date}.json"
            with open(file_path, 'w') as file:
                json.dump(data, file)
            current_date += timedelta(days=1)

        current_path = "/".join(current_path.split("/")[2:])
        #encode file_path as uri component
        current_path = urllib.parse.quote(current_path)


        return redirect(f"files.html?current_path={current_path}")
    

class Google_drive_callback(APIView):

    def get(self, request, *args, **kwargs):
        SCOPES = ['https://www.googleapis.com/auth/drive']
        state = request.query_params.get('state')
        params = dict(x.split('=') for x in state.split('&'))
        username = params['username']

        
        flow = Flow.from_client_secrets_file(
            'tmp/google_drive_client_secret.json',
            scopes=SCOPES,
            redirect_uri='https://adma.hopto.org/api/google_drive_auth_callback/'
        )
        
        flow.fetch_token(authorization_response=request.build_absolute_uri())

        # Now, use the credentials to interact with Google Drive.
        creds = flow.credentials
        # Save the credentials as needed (e.g., store them in the session or database).
        # Save the credentials for the next run
        with open(f'tmp/google_drive_credential_{username}.json', 'w') as token:
            token.write(creds.to_json())

        response = json.dumps({"result":"google drive token acquired"})

        return HttpResponse(response)

