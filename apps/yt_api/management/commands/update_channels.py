import os
import requests
from django.core.management.base import BaseCommand
from api.models import *
from django.utils import timezone

API_KEY = 'AIzaSyBbX7lUkM_AO4bD5wT-_znOLqvyQU8ezfA'
SEARCH_URL = 'https://www.googleapis.com/youtube/v3/search'
CHANNEL_URL = 'https://www.googleapis.com/youtube/v3/channels'

class Command(BaseCommand):
    help = 'Update YouTube channel data'

    def handle(self, *args, **kwargs):
        channels = self.fetch_all_channels()
        if len(channels)< 100:
            return
        self.get_top_channels(channels)

    def fetch_all_channels(self):
        channels = []
        total_channels = YouTubeChannel.objects.count()
         # If there are less than 100 channels, return an empty list
        if total_channels < 100:
            return []

        
        # Get the latest timestamp from the YouTubeChannel table
        latest_timestamp = YouTubeChannel.objects.latest('last_updated').last_updated
        
        # Fetch channels with the latest timestamp
        channels_with_latest_timestamp = YouTubeChannel.objects.filter(last_updated=latest_timestamp)

        # Collect channel data
        for channel in channels_with_latest_timestamp:
            channels.append({
                'channel_id': channel.channel_id,
                'title': channel.title,
                'description': channel.description
            })

        return channels

    def get_top_channels(self, channels):
        channel_data_list = []

        # Fetch channel data for each channel and collect it in a list
        for item in channels:
            channel_id = item['channel_id']
            channel_data = self.fetch_channel_data(channel_id)
            if channel_data:
                channel_data_list.append(channel_data)

        # Sort the channels by subscribers in descending order
        sorted_channels = sorted(channel_data_list, key=lambda x: x['subscribers'], reverse=True)

        # Select the top 100 channels
        top_100_channels = sorted_channels[:100]

        # Get the current timestamp once
        current_timestamp = timezone.now()

        # Update or create records in the database for the top 100 channels
        for channel_data in top_100_channels:
            YouTubeChannelSubscribers.objects.update_or_create(
                channel=channel_data['channel_id'],
                defaults={
                    'subscribers': channel_data['subscribers'],
                    'last_updated': current_timestamp  # Add the same timestamp for all records
                    
                }
            )

    def fetch_channel_data(self, channel_id):
        params = {
            'part': 'snippet,statistics',
            'id': channel_id,
            'key': API_KEY
        }
        response = requests.get(CHANNEL_URL, params=params)
        response.raise_for_status()
        data = response.json().get('items', [])[0]
        return {
            #'title': data['snippet']['title'],
            #'description': data['snippet']['description'],
            'subscribers': int(data['statistics']['subscriberCount'])
        }
