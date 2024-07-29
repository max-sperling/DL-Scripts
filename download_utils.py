import datetime
import os
import requests
import urllib

def download_file(url, filename, retries = 3):
    if os.path.isfile(filename):
        return True

    while retries > 0:
        try:
            response = requests.get(url, timeout = 10)
            response.raise_for_status()
            with open(filename, 'wb') as f:
                f.write(response.content)
            return True
        except Exception as e:
            retries -= 1

    return False

def get_without_webargs(link):
    return link.split('?')[0]

def get_without_webpath(link):
    return link.split('/')[-1]

def print_message(message):
    print(f"{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")} {message}")

def remove_duplicates(items):
    unique_items = []

    for item in items:
        if item not in unique_items:
            unique_items.append(item)

    return unique_items
