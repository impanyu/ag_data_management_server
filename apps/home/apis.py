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

class FileUploadSerializer(serializers.Serializer):
    # Define a file field in your serializer
    # You can specify additional arguments for FileField to further customize its behavior
    # For example, you can set `allow_empty_file=False` to prevent empty files from being uploaded
    # `max_length` could be used to specify the maximum length of the file name
    file = serializers.FileField(allow_empty_file=False, max_length=100)
    target_path = serializers.CharField(max_length=200)  # Adjust max_length as needed

    def validate_file(self, value):
        # Implement custom validation logic if needed
        # For example, you could check the file's size, type, or name here
        # This example checks the file size and restricts it to 10MB

        # 10MB limit
        max_upload_size = 10 * 1024 * 1024

        if value.size > max_upload_size:
            raise serializers.ValidationError("File size exceeds the allowed limit of 10MB.")

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

            # Sanitize and validate the target_path
            safe_path = os.path.normpath(target_path).lstrip('/')
            #if not is_valid_path(safe_path):
            #    return Response({"message": "Invalid upload path."}, status=status.HTTP_400_BAD_REQUEST)
            current_user = request.user.username


            full_path = os.path.join(settings.USER_DATA_DIR, current_user,"ag_data",safe_path, file.name)
            os.makedirs(os.path.dirname(full_path), exist_ok=True)

            with open(full_path, 'wb+') as destination:
                for chunk in file.chunks():
                    destination.write(chunk)

            return Response({"message": "File uploaded successfully!"}, status=status.HTTP_201_CREATED)
        
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
