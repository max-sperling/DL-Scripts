from utils import general

from enum import Enum
from urllib.parse import urlparse, urlunparse
import os
import requests

def get_url_base(url):
    parsed_url = urlparse(url)
    return urlunparse((parsed_url.scheme, parsed_url.netloc, '', '', '', ''))

def get_url_base_dirs(url):
    parsed_url = urlparse(url)
    dirs = os.path.dirname(parsed_url.path)
    return urlunparse((parsed_url.scheme, parsed_url.netloc, dirs, '', '', ''))

def get_url_file(url):
    parsed_url = urlparse(url)
    file = os.path.basename(parsed_url.path)
    return urlunparse(('', '', file, '', '', ''))

def get_url_file_args(url):
    parsed_url = urlparse(url)
    file = os.path.basename(parsed_url.path)
    return urlunparse(('', '', file, '', parsed_url.query, ''))

def get_url_path_args(url):
    parsed_url = urlparse(url)
    return urlunparse(('', '', parsed_url.path, '', parsed_url.query, ''))

class URL_Overlap(Enum):
    DIRS = 1  # Base and dirs match
    BASE = 2  # Only the base matches
    NONE = 3  # Nothing matches

def find_url_overlap(url1, url2):
    parsed_url1 = urlparse(url1)
    parsed_url2 = urlparse(url2)

    if ((parsed_url1.scheme == parsed_url2.scheme or parsed_url1.scheme == "" or parsed_url2.scheme == "") and
        (parsed_url1.netloc == parsed_url2.netloc or parsed_url1.netloc == "" or parsed_url2.netloc == "")):
        url1_dirs = os.path.dirname(parsed_url1.path)
        url2_dirs = os.path.dirname(parsed_url2.path)
        if (url1_dirs == url2_dirs or url1_dirs == "" or url2_dirs == ""):
            return URL_Overlap.DIRS
        else:
           return URL_Overlap.BASE
    else:
        return URL_Overlap.NONE

def download_file(url, file, headers = {}, attempts = 3):
    if os.path.isfile(file):
        return

    while attempts > 0:
        try:
            response = requests.get(url, headers = headers, timeout = (5, 30))
            response.raise_for_status()
            with open(file, 'wb') as f:
                f.write(response.content)
            return
        except Exception as e:
            attempts -= 1
            if attempts == 0:
                raise
