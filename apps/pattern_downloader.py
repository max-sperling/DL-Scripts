from utils import download
from utils import general

import argparse
import re
import requests

def download_pattern(url, pattern):
    response = requests.get(url)
    response.raise_for_status()
    text = response.text

    items = search_items(text, pattern)
    items = general.remove_duplicates(items)
    download_items(items)

def search_items(text, pattern):
    matches = re.findall(pattern, text)
    return matches

def download_items(items):
    for item in items:
        item_name = download.get_resource_without_webargs(item)

        if download.download_file(item, item_name):
            general.print_message(f"Download successful: {item}")
        else:
            general.print_message(f"Download failed: {item}")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-u', '--url', type = str, required = True)
    parser.add_argument('-p', '--pattern', type = str, required = True)

    args = parser.parse_args()
    download_pattern(args.url, args.pattern)

if __name__ == "__main__":
    main()
