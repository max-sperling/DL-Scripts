import os
import requests

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
