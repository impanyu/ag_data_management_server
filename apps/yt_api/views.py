from rest_framework import generics
from .models import *
from .serializers import YouTubeChannelSerializer
from django.utils.timezone import now, timedelta
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import OuterRef, Subquery, F
import requests
from django.utils import timezone
from .management.commands.update_top_chinese_channels import fetch_channel_data
from django.utils.dateparse import parse_date
from rest_framework.exceptions import ValidationError

from .utils import *
from rest_framework.permissions import AllowAny
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from rest_framework.views import APIView
from rest_framework.response import Response
from django.http import HttpResponse

@method_decorator(csrf_exempt, name='dispatch')
class YouTubeTopChineseChannelListRealTime(generics.ListAPIView):
    serializer_class = YouTubeChannelSerializer
    permission_classes = [AllowAny]  # Override global settings

    def get_queryset(self):
        print("queryset",flush=True)
        # Retrieve channel IDs
        channel_ids = get_channel_ids()
       
        if not channel_ids:
            return []
        
        channels_data = fetch_channel_data(channel_ids)


        # Sort channels by subscribers and return top 100
        sorted_channels = sorted(channels_data, key=lambda x: x['subscribers'], reverse=True)
        current_timestamp = timezone.now()
        # Convert to YouTubeChannel instances for serialization
        queryset = [YouTubeChannel(
            channel_id=channel['channel_id'],
            title=channel['title'],
            description=channel['description'],
            subscribers=channel['subscribers'],
            icon_url=channel['icon_url'],
            last_updated=current_timestamp
        ) for channel in sorted_channels]

        return queryset


@method_decorator(csrf_exempt, name='dispatch')
class YouTubeTopChineseChannelListHistoric(generics.ListAPIView):
    serializer_class = YouTubeChannelSerializer
    permission_classes = [AllowAny]  # Override global settings
    def get_queryset(self):
        # Get query parameters for date filtering
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')

        # Parse the date strings into date objects
        if start_date:
            start_date = parse_date(start_date)
        if end_date:
            end_date = parse_date(end_date)

        # Validate date range
        if start_date and end_date and start_date > end_date:
            raise ValidationError("Start date cannot be after end date.")

        # Base queryset
        queryset = YouTubeChannel.objects.all()

        # Apply date filtering if both dates are provided
        if start_date and end_date:
            queryset = queryset.filter(last_updated__range=[start_date, end_date])
        elif start_date:
            queryset = queryset.filter(last_updated__gte=start_date)
        elif end_date:
            queryset = queryset.filter(last_updated__lte=end_date)


        return queryset
    

class GetHello(APIView):

    def get(self, request, *args, **kwargs):

        response = "hello"
        return HttpResponse(response)
