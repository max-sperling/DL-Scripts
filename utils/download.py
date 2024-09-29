from utils import general

from urllib.parse import urlparse, urlunparse
import os
import requests

def download_file(url, file, headers = {}, attempts = 3):
    if os.path.isfile(file):
        return

    while attempts > 0:
        try:
            response = requests.get(url, headers = headers, timeout = 10)
            response.raise_for_status()
            with open(file, 'wb') as f:
                f.write(response.content)
            return
        except Exception as e:
            attempts -= 1
            if attempts == 0:
                raise

def get_url_domain(url):
    parsed_url = urlparse(url)
    return urlunparse((parsed_url.scheme, parsed_url.netloc, '', '', '', ''))

def get_url_domain_dir(url):
    parsed_url = urlparse(url)
    dir_name = os.path.dirname(parsed_url.path)
    return urlunparse((parsed_url.scheme, parsed_url.netloc, dir_name, '', '', ''))

def get_url_file(url):
    parsed_url = urlparse(url)
    base_name = os.path.basename(parsed_url.path)
    return urlunparse(('', '', base_name, '', '', ''))

def get_url_file_args(url):
    parsed_url = urlparse(url)
    base_name = os.path.basename(parsed_url.path)
    return urlunparse(('', '', base_name, '', parsed_url.query, ''))
