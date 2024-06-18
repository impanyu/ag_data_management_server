from rest_framework import generics
from .models import *
from .serializers import *
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


from django import template
from django.template import loader
from datetime import datetime, timedelta
import numpy as np


@method_decorator(csrf_exempt, name='dispatch')
class YouTubeTopChineseChannelList(generics.ListAPIView):
    serializer_class = YouTubeChannelSerializer
    permission_classes = [AllowAny]  # Override global settings

    def get_queryset(self):
        #print("queryset",flush=True)
        # Retrieve channel IDs
        channel_ids = get_channel_ids()
        print(len(channel_ids),flush=True)
        if not channel_ids:
            return []
        
        channels_data = fetch_channel_data(channel_ids)
        #print(len(channels_data),flush=True)


        # Sort channels by subscribers and return top 50
        #sorted_channels = sorted(channels_data, key=lambda x: x['subscribers'], reverse=True)[:50]
        #current_timestamp = timezone.now()
        # Convert to YouTubeChannel instances for serialization
        queryset = [Channel(
            channel_id=channel['channel_id'],
            title=channel['title'],
            description=channel['description'],
            #subscribers=channel['subscribers'],
            icon_url=channel['icon_url'],
            join_date=channel['join_date'],
            location=channel['location']
            #last_updated=current_timestamp
        ) for channel in channels_data]
        #print(f"queryset:{len(queryset)}",flush=True)
        return queryset




@method_decorator(csrf_exempt, name='dispatch')
class YouTubeTopChineseChannelSubscribers(generics.ListAPIView):
    serializer_class = YouTubeChannelSubscribersSerializer
    permission_classes = [AllowAny]  # Override global settings

    def get_queryset(self):
        # Get the query parameter for date filtering
        #date = self.request.query_params.get('date')
        date_str = self.request.query_params.get('date')
        # Validate and parse the date parameter
        if not date_str:
            raise ValidationError("Date parameter is required.")
        try:
            date = datetime.strptime(date_str, '%Y-%m-%d-%H-%M-%S')
        except ValueError:
            raise ValidationError("Invalid date format. Expected YYYY-mm-DD-HH-MM-SS.")


        # Define the delta period
        delta = timedelta(days=90)
        start_date = date - delta
        end_date = date + delta

        # Base queryset
        queryset = ChannelSubscribers.objects.filter(last_updated__range=[start_date, end_date])

        return queryset

    def list(self, request, *args, **kwargs):
         # Get the date parameter
        date_str = request.query_params.get('date')
        try:
            date = datetime.strptime(date_str, '%Y-%m-%d-%H-%M-%S')
        except ValueError:
            #raise ValidationError("Invalid date format. Expected YYYY-MM-DD-HH-MM-SS.")
            return Response("Invalid date format. Expected YYYY-MM-DD-HH-MM-SS.")
        # Call the get_queryset method
        queryset = self.get_queryset()

        # Create a dictionary with channel_id as keys and list of subscribers as values
        channel_subscribers = {}
        for channel in queryset:
            if channel.channel_id not in channel_subscribers:
                channel_subscribers[channel.channel_id] = []
            channel_subscribers[channel.channel_id].append((channel.subscribers, channel.last_updated))

        '''
        # Calculate the estimated subscribers for each channel at the specified date
        estimated_subscribers = {}
        for channel_id, data in channel_subscribers.items():
            if len(data) == 1:
                # If there's only one data point, return that number
                estimated_subscribers[channel_id] = 0
            else:
                # Convert dates to numerical values (timestamps)
                dates = np.array([d[1].timestamp() for d in data])
                subscribers = np.array([d[0] for d in data])

                # Fit a linear regression model
                A = np.vstack([dates, np.ones(len(dates))]).T
                m, c = np.linalg.lstsq(A, subscribers, rcond=None)[0]

                # Calculate the estimated subscribers at the specified date
                target_date_timestamp = date.timestamp()
                estimated_subscribers[channel_id] = m * target_date_timestamp + c

        # Create the response data
        response_data = [{"channel_id": channel_id, "subscribers": est} for channel_id, est in estimated_subscribers.items()]
        sorted_channels = sorted(response_data, key=lambda x: x['subscribers'], reverse=True)[:50]

        '''
        sorted_channels = []
        return Response(sorted_channels)

    

class GetHello(APIView):

    def get(self, request, *args, **kwargs):

        response = "hello"
        return HttpResponse(response)

@csrf_exempt
def pages(request):
    context = {}
    # All resource paths end in .html.
    # Pick out the html file name from the url. And load that template.
    try:

        load_template = request.path.split('/')[-1]

        load_template = load_template.split('?')[0]


        if load_template == "yt_top_chinese_channels.html":

            html_template = loader.get_template('home/yt_top_chinese_channels.html')
            return HttpResponse(html_template.render(context, request))
    except template.TemplateDoesNotExist:

        html_template = loader.get_template('home/page-404.html')
        return HttpResponse(html_template.render(context, request))

    except:
        html_template = loader.get_template('home/page-500.html')
        return HttpResponse(html_template.render(context, request))