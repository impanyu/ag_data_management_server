import os
import requests
from django.core.management.base import BaseCommand
from api.models import YouTubeChannel
from django.utils import timezone

API_KEY = 'AIzaSyBbX7lUkM_AO4bD5wT-_znOLqvyQU8ezfA'
SEARCH_URL = 'https://www.googleapis.com/youtube/v3/search'
CHANNEL_URL = 'https://www.googleapis.com/youtube/v3/channels'

class Command(BaseCommand):
    help = 'Update top YouTube channel list'

    def handle(self, *args, **kwargs):
        channels = self.fetch_all_channels()
        self.get_top_channels(channels)

    def fetch_all_channels(self):
        channels = []
        page_token = None

        while len(channels) < 100000:  # You can adjust the number as needed
            params = {
                'part': 'snippet',
                'type': 'channel',
                'q': '',
                'maxResults': 50,
                'relevanceLanguage': 'zh',
                'key': API_KEY,
                'pageToken': page_token
            }
            response = requests.get(SEARCH_URL, params=params)
            response.raise_for_status()
            data = response.json()

            channels.extend(data.get('items', []))
            page_token = data.get('nextPageToken')

            if not page_token:
                break

        return channels

    def get_top_channels(self, channels):
        channel_data_list = []

        # Fetch channel data for each channel and collect it in a list
        for item in channels:
            channel_id = item['id']['channelId']
            channel_data = self.fetch_channel_data(channel_id)
            if channel_data:
                channel_data_list.append(channel_data)

        # Sort the channels by subscribers in descending order
        sorted_channels = sorted(channel_data_list, key=lambda x: x['subscribers'], reverse=True)

        # Select the top 100 channels
        top_100_channels = sorted_channels[:100]

        # Get the current timestamp once
        #current_timestamp = timezone.now()

        # Update or create records in the database for the top 100 channels
        for channel_data in top_100_channels:
            YouTubeChannel.objects.update_or_create(
                channel_id=channel_data['channel_id'],
                defaults={
                    'title': channel_data['title'],
                    'description': channel_data['description']
                    #'subscribers': channel_data['subscribers']
                    #'last_updated': current_timestamp  # Add the same timestamp for all records
                    
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
            'title': data['snippet']['title'],
            'description': data['snippet']['description'],
            'subscribers': int(data['statistics']['subscriberCount'])
        }
