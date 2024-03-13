from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import authentication, permissions
from django.contrib.auth.models import User


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
    authentication_classes = [authentication.TokenAuthentication]
    #permission_classes = [permissions.IsAdminUser]
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = FileUploadSerializer(data=request.data)
        
        if serializer.is_valid():
            file = serializer.validated_data['file']
            # Handle the file, e.g., save it to the server's file system
            # or store in your media storage solution
            
            # For demonstration, let's just save it to the media root
            with open(f'media/{file.name}', 'wb+') as destination:
                for chunk in file.chunks():
                    destination.write(chunk)
            
            return Response({"message": "File uploaded successfully!"}, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)