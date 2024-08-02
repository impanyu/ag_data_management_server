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
        container = get_container_by_id(container_id)
        if container is None:
            response = json.dumps({"container_id":container_id,"status":"not found"})
            return HttpResponse(response)
        logs = container.logs().decode('utf-8')
        # Get the container status
        status = container.status
        # Get the container image name
        image_name = container.image.tags[0] if container.image.tags else "No image tag"

        # Get the container start timestamp
        started_at = container.attrs['State']['StartedAt'][:-5]
        #start_time = datetime.strptime(started_at, '%Y-%m-%dT%H:%M:%S.%fZs')

        start_time = datetime.strptime(started_at, '%Y-%m-%dT%H:%M:%S.%f')

        stop_time = datetime.utcnow()#datetime.strptime(finished_at, '%Y-%m-%dT%H:%M:%S.%f')

        if status == "exited":
            finished_at = container.attrs['State']['FinishedAt'][:-5]
            stop_time = datetime.strptime(finished_at, '%Y-%m-%dT%H:%M:%S.%f')

        duration = (stop_time - start_time).total_seconds()

        response={"container_id": container_id, "status": status, "image": image_name,"running_time": duration,"logs":logs}#,"start_time":started_at, "finished_time":finished_at}

        response = json.dumps(response)
        return HttpResponse(response)


class GetContainersFromTool(APIView):

    def get(self, request, *args, **kwargs):
        target_path = request.query_params.get('target_path')
        #file_name = request.query_params.get('file_name')

        # Sanitize and validate the target_path
        safe_path = os.path.normpath(target_path).lstrip('/')
        current_user = request.user.username

        # Construct the full file path
        full_path = os.path.join(settings.USER_DATA_DIR, current_user, "ag_data", safe_path)
       
        meta_data = get_meta_data(full_path)
        containers = []

        if "containers" in meta_data:
            containers = json.dumps(meta_data["containers"])
        return HttpResponse(containers)

    


def wait_for_container_to_stop(container_id):
    api_client = docker.APIClient()
    while True:
        try:
            container_info = api_client.inspect_container(container_id)
            if container_info['State']['Status'] == 'exited':
                return container_info
        except docker.errors.APIError as e:
            print(f"Error inspecting container: {e}")
            return None
        time.sleep(1)

class StopRunningInstance(APIView):

    def get(self, request, *args, **kwargs):
        container_id = request.query_params.get('running_instance_id')
        container = get_container_by_id(container_id)
        if container is None:
            response = json.dumps({"container_id": container_id, "status": "not found"})
            return HttpResponse(response)

        try:
            container.stop()
            # Ensure the container is stopped before continuing
            counter = 0

            # Wait for the container to fully stop
            #while container.status != 'exited' and counter<20:
            #    time.sleep(1)
            #    container.reload()
            #    counter += 1
            #wait_for_container_to_stop(container)
            time.sleep(5)
            container.reload()

            api_client = docker.APIClient()
            container_info = api_client.inspect_container(container_id)
            status = container_info['State']['Status']
            #if container_info['State']['Status'] == 'exited':
        

            if container.status == 'exited':
                logs = container.logs().decode('utf-8')
                # Get the container image name
                image_name = container.image.tags[0] if container.image.tags else "No image tag"
                # Get the container start timestamp
                started_at = container.attrs['State']['StartedAt'][:-5]
                start_time = datetime.strptime(started_at, '%Y-%m-%dT%H:%M:%S.%f')
                # Calculate the duration in seconds
                duration = (datetime.utcnow() - start_time).total_seconds()
                response = {
                    "container_id": container_id,
                    "status": container.status,
                    "image": image_name,
                    "running_time": duration,
                    "logs": logs
                }
                # Remove the container
                #container.remove()
            else:
                response = {
                    "container_id": container_id,
                    "status": container.status
                }
        except docker.errors.APIError as e:
            response = {
                "container_id": container_id,
                "status": "error",
                "error": str(e)
            }

        response = json.dumps(response)
        return HttpResponse(response)



class JD_authorization_code(APIView):

    def get(self, request, *args, **kwargs):
        target_path = request.query_params.get('file_path') #this is already abs path
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

