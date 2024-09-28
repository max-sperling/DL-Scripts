from utils import download
from utils import general

import argparse
import re
import requests

def download_pattern(resource_url, search_pattern):
    successful, resource_content = get_resource_content(resource_url)
    if not successful:
        return False

    successful = download_matching_items(resource_content, search_pattern)
    if not successful:
        return False

    return True

def get_resource_content(resource_url):
    resource_content = ""

    try:
        response = requests.get(resource_url)
        response.raise_for_status()
        resource_content = response.text
    except Exception as e:
        general.print_message(f"Get resource content failed ({e})")
        return False, resource_content

    general.print_message("Get resource content successful")
    return True, resource_content

def download_matching_items(resource_content, search_pattern):
    item_urls = re.findall(search_pattern, resource_content)
    item_urls = general.remove_duplicates(item_urls)

    successful = download_items(item_urls)

    if successful:
        general.print_message("Download matching items successful")
    else:
        general.print_message("Download matching items failed")

    return successful

def download_items(item_urls):
    successful = True

    for item_url in item_urls:
        item_name = download.get_url_file(item_url)

        try:
            download.download_file(item_url, item_name)
        except Exception as e:
            general.print_message(f"Download failed: {item_name}, {e}")
            successful = False

    return successful

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-U', '--resource-url',   type = str, required = True)
    parser.add_argument('-P', '--search-pattern', type = str, required = True)

    args = parser.parse_args()
    successful = download_pattern(args.resource_url, args.search_pattern)

    if successful:
        general.print_message("Pattern download successful")
    else:
        general.print_message("Pattern download failed")

if __name__ == "__main__":
    main()
