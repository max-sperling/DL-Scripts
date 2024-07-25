import datetime
import os
import requests
import urllib

def download_file(url, filename):
    if not os.path.isfile(filename):
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        with open(filename, 'wb') as f:
            f.write(response.content)

def get_without_webargs(link):
    return link.split('?')[0]

def get_without_webpath(link):
    return link.split('/')[-1]

def call_until_successful(max_iterations, func, *args):
    for _ in range(max_iterations):
        if func(*args):
            return True
    return False

def print_message(message):
    print(f"{datetime.datetime.now()} {message}")

def remove_duplicates(items):
    unique_items = []
    for item in items:
        if item not in unique_items:
            unique_items.append(item)
    return unique_items
