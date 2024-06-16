import json
import requests
import time

CHANNEL_IDS_FILE = '/data/yt/channel_ids.json'
API_KEY = 'AIzaSyBbX7lUkM_AO4bD5wT-_znOLqvyQU8ezfA'
SEARCH_URL = 'https://www.googleapis.com/youtube/v3/search'
CHANNEL_URL = 'https://www.googleapis.com/youtube/v3/channels'


def get_channel_ids():
        try:
            with open(CHANNEL_IDS_FILE, 'r') as file:
                data = json.load(file)
                # Assuming the JSON structure is a list of channel IDs
                return data if isinstance(data, list) else []
        except FileNotFoundError:
            print(f"The file {CHANNEL_IDS_FILE} was not found.")
            return []
        except json.JSONDecodeError:
            print("Error decoding the JSON file.")
            return []
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return []
        


def fetch_channel_data(channel_ids):
    if len(channel_ids) > 50:
        raise ValueError("The length of channel_ids should not exceed 50.")

    params = {
        'part': 'snippet,statistics',
        'id': ','.join(channel_ids),
        'key': API_KEY,
        'maxResults': 50
    }

    channels = []
    page_token = None

    while True:
        try:
            if page_token:
                params['pageToken'] = page_token

            response = requests.get(CHANNEL_URL, params=params)
            response.raise_for_status()
            data = response.json()

            items = data.get('items', [])
            for item in items:
                channels.append({
                    'channel_id': item['id'],
                    'title': item['snippet']['title'],
                    'description': item['snippet']['description'],
                    'subscribers': int(item['statistics']['subscriberCount']),
                    'icon_url': item['snippet']['thumbnails']['default']['url']  # Fetch the icon URL
                })

            page_token = data.get('nextPageToken')
            if not page_token:
                break

        except requests.exceptions.RequestException as e:
            if response.status_code == 403 and 'quota' in response.text.lower():
                print('Quota exceeded, waiting for quota reset...')
                time.sleep(24 * 3600)  # Sleep for 24 hours
            else:
                print(f'An error occurred: {e}')
                return []

    return channels
