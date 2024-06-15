import os
import requests
from django.core.management.base import BaseCommand
from yt_api.models import YouTubeChannel
from django.utils import timezone
import time

from .utils import *




class Command(BaseCommand):
    help = 'Update top YouTube channel list'

    def handle(self, *args, **kwargs):
        channel_ids = get_channel_ids()
        self.get_channel_updates(channel_ids)


    '''   
    def get_channel_ids(self):
        channels = []
        page_token = None

        while len(channels) < 500000:  # You can adjust the number as needed
            try:
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
            except requests.exceptions.RequestException as e:
                if response.status_code == 403 and 'quota' in response.text.lower():
                    print('Quota exceeded, waiting for quota reset...')
                    time.sleep(24 * 3600)  # Sleep for 24 hours
                else:
                    print(f'An error occurred: {e}')
                    break

        return channels
    '''
    def get_channel_updates(self, channel_ids):
        params = {
            'part': 'snippet,statistics',
            'id': ','.join(channel_ids),
            'key': API_KEY
        }
        while True:
            try:
                response = requests.get(CHANNEL_URL, params=params)
                response.raise_for_status()
                data = response.json().get('items', [])
                # Get the current timestamp once
                current_timestamp = timezone.now()
               
                for item in data:
                    YouTubeChannel.objects.update_or_create(
                        channel_id=item['id'],
                        defaults={
                            'title': item['snippet']['title'],
                            'description': item['snippet']['description'],
                            'subscribers': int(item['statistics']['subscriberCount']),
                            'icon_url': item['snippet']['thumbnails']['default']['url'],  # Fetch the icon URL
                            'last_updated': current_timestamp  # Add the same timestamp for all records
                            
                        }
                    )
            except requests.exceptions.RequestException as e:
                if response.status_code == 403 and 'quota' in response.text.lower():
                    print('Quota exceeded, waiting for quota reset...')
                    time.sleep(24 * 3600)  # Sleep for 24 hours
                else:
                    print(f'An error occurred: {e}')


