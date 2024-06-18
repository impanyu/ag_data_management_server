import json
import requests
import time
from itertools import islice
import random

CHANNEL_IDS_FILE = '/data/yt/chinese_channel_ids.json'
CHANNEL_SUBS_FILE = '/data/yt/chinese_channel_subs.json'
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
        
def get_channel_subs_initial():
        try:
            with open(CHANNEL_SUBS_FILE, 'r') as file:
                data = json.load(file)
                # Assuming the JSON structure is a list of channel subs
                return data if isinstance(data, list) else []
        except FileNotFoundError:
            print(f"The file {CHANNEL_SUBS_FILE} was not found.")
            return []
        except json.JSONDecodeError:
            print("Error decoding the JSON file.")
            return []
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return []


def fetch_channel_data(channel_ids):
    params = {
        'part': 'snippet,statistics',
        'key': API_KEY,
        'maxResults': 50
    }

    channels = []

    for chunk in chunked_iterable(channel_ids, 50):
        params['id'] = ','.join(chunk)
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
                    snippet = item['snippet']
                    statistics = item['statistics']
                    channel_data = {
                        'channel_id': item['id'],
                        'title': snippet['title'],
                        'description': snippet['description'],
                        'subscribers': int(statistics['subscriberCount']),
                        'icon_url': snippet['thumbnails']['default']['url'],
                        'join_date': snippet.get('publishedAt'),  # Join date
                        'location': snippet.get('country')  # Location
                    }
                    channels.append(channel_data)

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


def chunked_iterable(iterable, size):
    """Utility function to split an iterable into chunks of specified size."""
    it = iter(iterable)
    while True:
        chunk = list(islice(it, size))
        if not chunk:
            break
        yield chunk

def add_random_number(value):
    # Define the probabilities and corresponding values
    choices = [0, 1, -1]
    probabilities = [0.6, 0.2, 0.2]
    
    # Choose a random value based on the probabilities
    random_value = random.choices(choices, probabilities)[0]
    return value + random_value