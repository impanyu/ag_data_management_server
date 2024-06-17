import os
import requests
from django.core.management.base import BaseCommand
from apps.yt_api.models import *
from django.utils import timezone
import time
from datetime import datetime

from apps.yt_api.utils import *




class Command(BaseCommand):
    help = 'Update top YouTube channel list and subs'

    def handle(self, *args, **kwargs):
        channel_ids = get_channel_ids()
        print(f"in task: {len(channel_ids)}",flush=True)
        self.get_channel_updates_initial(channel_ids)
        #self.get_channel_updates(channel_ids)

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
        channels = fetch_channel_data(channel_ids)
        print(f"in get_channel_updates",flush=True)
        current_timestamp = timezone.now()
        for channel in channels:
             YouTubeChannel.objects.update_or_create(
                channel_id=channel['channel_id'],
                defaults={
                    'title': channel['title'],
                    'description': channel['description'],
                    #'subscribers': int(channel['subscribers']),
                    'icon_url': channel['icon_url'],  # Fetch the icon URL
                    #'last_updated': current_timestamp  # Add the same timestamp for all records
                    'join_date': channel["join_date"],
                    'location': channel["location"]
                })
    
             YouTubeChannelSubscribers.objects.update_or_create(
                channel_id=channel['channel_id'],
                defaults={
                    #'title': channel['title'],
                    #'description': channel['description'],
                    'subscribers': int(channel['subscribers']),
                    #'icon_url': channel['icon_url']  # Fetch the icon URL
                    'last_updated': current_timestamp  # Add the same timestamp for all records
                   
                })
             
    def get_channel_updates_initial(self, channel_ids):
        channels = fetch_channel_data(channel_ids)
        channel_subs = get_channel_subs_initial()
        print(f"in get_channel_updates_initial",flush=True)
        initial_timestamp = datetime(2024, 4, 8, 0, 0)  # 2024-04-08 00:00:00
        for i,channel in enumerate(channels):
             YouTubeChannel.objects.update_or_create(
                channel_id=channel['channel_id'],
                defaults={
                    'title': channel['title'],
                    'description': channel['description'],
                    #'subscribers': int(channel['subscribers']),
                    'icon_url': channel['icon_url'],  # Fetch the icon URL
                    #'last_updated': current_timestamp  # Add the same timestamp for all records
                    'join_date': channel["join_date"],
                    'location': channel["location"]
                })
    
             YouTubeChannelSubscribers.objects.update_or_create(
                channel_id=channel['channel_id'],
                defaults={
                    #'title': channel['title'],
                    #'description': channel['description'],
                    'subscribers': int(channel_subs[i]*10000),
                    #'icon_url': channel['icon_url']  # Fetch the icon URL
                    'last_updated': initial_timestamp  # Add the same timestamp for all records
                    
                })