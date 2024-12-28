from utils import download
from utils import general
from utils import weblinks

import argparse
import re
import requests

class Pattern_Dler:
    def download_pattern(self, resource_url, search_pattern):
        successful, resource_content = self.get_resource_content(resource_url)
        if not successful:
            return False

        successful = self.download_matching_items(resource_content, search_pattern)
        if not successful:
            return False

        return True

    def get_resource_content(self, resource_url):
        resource_content = ""

        try:
            response = requests.get(resource_url)
            response.raise_for_status()
            resource_content = response.text
        except Exception as exception:
            general.print_message_nok(f"Get resource content failed ({exception})")
            return False, resource_content

        general.print_message_ok("Get resource content successful")
        return True, resource_content

    def download_matching_items(self, resource_content, search_pattern):
        item_urls = re.findall(search_pattern, resource_content)
        item_urls = general.remove_duplicates(item_urls)

        if not item_urls:
            general.print_message_nok("No matching items found in resource")
            return False

        successful = self.download_items(item_urls)

        if successful:
            general.print_message_ok("Download matching items successful")
        else:
            general.print_message_nok("Download matching items failed")

        return successful

    def download_items(self, item_urls):
        successful = True

        for item_url in item_urls:
            item_name = weblinks.get_url_file(item_url)

            try:
                download.download_file(item_url, item_name)
            except Exception as exception:
                general.print_message_nok(f"Download failed: {item_name}, {exception}")
                successful = False

        return successful

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-ru', '--resource-url',   type = str, required = True)
    parser.add_argument('-sp', '--search-pattern', type = str, required = True)
    args = parser.parse_args()

    p_dler = Pattern_Dler()
    successful = p_dler.download_pattern(args.resource_url, args.search_pattern)

    if successful:
        general.print_message_ok("Pattern download successful")
    else:
        general.print_message_nok("Pattern download failed")

if __name__ == "__main__":
    main()
