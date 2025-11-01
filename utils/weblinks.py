from urllib.parse import urljoin, urlparse, urlunparse
import os

def url_is_file(url):
    return not url.rstrip().endswith('/')

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

def join_url(url_1, url_2):
    return urljoin(url_1, url_2)
