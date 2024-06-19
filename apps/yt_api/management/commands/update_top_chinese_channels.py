import os
import requests
from django.core.management.base import BaseCommand
from apps.yt_api.models import *
from django.utils import timezone
import time
from datetime import datetime, timedelta

from apps.yt_api.utils import *
import random



class Command(BaseCommand):
    help = 'Update top YouTube channel list and subs'

    def add_arguments(self, parser):
        # Add custom command line arguments here
        parser.add_argument(
            '--initialize',
            action='store_true',
            help='Run the initial update',
        )

    def handle(self, *args, **kwargs):
        channel_ids = get_channel_ids()
        print(f"in task: {len(channel_ids)}",flush=True)
        initialize = kwargs.get('initialize', False)
        if initialize:
            self.get_channel_updates_initial(channel_ids)
        else:
            #self.get_channel_updates_initial(channel_ids)
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
        channels = fetch_channel_data(channel_ids)
        print(f"in get_channel_updates",flush=True)
        current_timestamp = timezone.now()
        for channel in channels:
             Channel.objects.update_or_create(
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
    
             ChannelSubscribers.objects.create(
                channel_id=channel['channel_id'],
                subscribers=channel['subscribers'],
                video_count=channel['video_count'],
                view_count=channel['view_count'],
                last_updated=current_timestamp  # Add the same timestamp for all records
            )
             
    def get_channel_updates_initial(self, channel_ids):
        channels = fetch_channel_data(channel_ids)
        channel_subs = get_channel_subs_initial()
        print(f"in get_channel_updates_initial",flush=True)
        #initial_timestamp = datetime(2024, 4, 8, 0, 0)  # 2024-04-08 00:00:00
        current_timestamp = timezone.now()
        for i,channel in enumerate(channels):
             #index = channel_ids.index(channel['channel_id'])
             channel_id = channel['channel_id']
             Channel.objects.update_or_create(
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
            
             # Generate a random timedelta
             random_days = random.randint(0, 3)  # Random number of days between 0 and 30
             random_hours = random.randint(0, 23)  # Random number of hours between 0 and 23
             random_minutes = random.randint(0, 59)  # Random number of minutes between 0 and 59

             # Create the timedelta
             random_timedelta = timedelta(days=random_days, hours=random_hours, minutes=random_minutes)
             last_updated = datetime.strptime(channel_subs[channel_id]["initial_date"],"%Y-%m-%d")

             # Add the timedelta to the last_updated date
             #last_updated += random_timedelta
             #estimated_subs = int(channel_subs[channel_id]["subscribers"] * 10000)
             #estimated_subs -= random.randint(0, 1000)  # Subtract a random number between 0 and 2000

             ChannelSubscribers.objects.create(
                channel_id=channel['channel_id'],
                subscribers=int(estimated_subs),
                video_count=channel['video_count'],
                view_count=channel['view_count'],
                last_updated= last_updated # Add the same timestamp for all records
            )
             
             if channel['subscribers'] > 1000000:
                estimated_subs = channel['subscribers'] + random.randint(0, 8000)
             else:
                estimated_subs = channel['subscribers'] + random.randint(0, 800)  

             ChannelSubscribers.objects.create(
                channel_id=channel['channel_id'],
                subscribers=estimated_subs,
                video_count=channel['video_count'],
                view_count=channel['view_count'],
                last_updated=current_timestamp  # Add the same timestamp for all records
            )
             
