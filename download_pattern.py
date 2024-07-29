import download_utils

import argparse
import re
import requests

def download_pattern(url, pattern):
    response = requests.get(url)
    response.raise_for_status()
    text = response.text

    items = search_items(text, pattern)
    items = download_utils.remove_duplicates(items)
    download_items(items)

def search_items(text, pattern):
    matches = re.findall(pattern, text)
    return matches

def download_items(items):
    for item in items:
        item_name = download_utils.get_without_webpath(item)

        if download_utils.download_file(item, item_name):
            download_utils.print_message(f"Download successful: {item}")
        else:
            download_utils.print_message(f"Download failed: {item}")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-u', '--url', type = str, required = True)
    parser.add_argument('-p', '--pattern', type = str, required = True)

    args = parser.parse_args()
    download_pattern(args.url, args.pattern)

if __name__ == "__main__":
    main()
