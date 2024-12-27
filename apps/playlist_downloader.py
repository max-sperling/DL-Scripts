from utils import download
from utils import general

from enum import Enum
import argparse
import ast
import concurrent.futures
import os
import threading
import subprocess

class Playlist_Dler:
    def __init__(self, playlist_url, output_file, http_headers):
        self.playlist_url = playlist_url
        self.output_file = output_file
        self.http_headers = http_headers

    def download_playlist(self):
        playlist_file = download.get_url_file(self.playlist_url)

        if not self.download_playlist_file(playlist_file):
            return False
        if not self.download_media_files(playlist_file):
            return False
        if not self.concat_media_files(playlist_file):
            return False

        return True

    def download_playlist_file(self, playlist_file):
        successful = True

        try:
            download.download_file(self.playlist_url, playlist_file, self.http_headers)
        except Exception as e:
            general.print_message_nok(f"Download failed: {self.playlist_url}, {e}")
            successful = False

        if successful:
            general.print_message_ok("Playlist file download successful")
        else:
            general.print_message_nok("Playlist file download failed")

        return successful

    def download_media_files(self, playlist_file):
        media_files = []
        base_url = ""
        rel_urls = []

        with open(playlist_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    media_files.append(line)

        url_overlap = download.find_url_overlap(self.playlist_url, media_files[0])
        match url_overlap:
            case download.URL_Overlap.DIRS:
                general.print_message_ok("Calculated url overlap: DIRS")
                base_url = download.get_url_base_dirs(self.playlist_url)
                for media_file in media_files:
                    rel_urls.append(download.get_url_file_args(media_file))
            case download.URL_Overlap.BASE:
                general.print_message_ok("Calculated url overlap: BASE")
                base_url = download.get_url_base(self.playlist_url)
                for media_file in media_files:
                    rel_urls.append(download.get_url_path_args(media_file))
            case download.URL_Overlap.NONE:
                general.print_message_ok("Calculated url overlap: NONE")
                # base_url = ""
                for media_file in media_files:
                    rel_urls.append(media_file)

        successful = self.download_files(base_url, rel_urls)

        if successful:
            general.print_message_ok("Media files download successful")
        else:
            general.print_message_nok("Media files download failed")

        return successful

    def download_files(self, base_url, rel_urls):
        successful = True
        lock = threading.Lock()

        def download_task(rel_url_wa):
            nonlocal successful

            file_url = ""
            if base_url == "":
                file_url = rel_url_wa
            else:
                file_url = f"{base_url}/{rel_url_wa}"

            file = download.get_url_file(rel_url_wa)
            file_path = os.path.join(os.getcwd(), file)

            try:
                download.download_file(file_url, file_path, self.http_headers)
            except Exception as e:
                with lock:
                    general.print_message_nok("Download failed\n"
                        f"File-URL: {file_url},\n"
                        f"File-Path: {file_path},\n"
                        f"Exception: {e}\n")
                    successful = False

        with concurrent.futures.ThreadPoolExecutor(max_workers = 5) as executor:
            executor.map(download_task, rel_urls)

        return successful

    def concat_media_files(self, playlist_file):
        concat = "concat:"

        with open(playlist_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    line = download.get_url_file(line)
                    concat += f"{line}|"

        concat = concat.rstrip('|')
        command = ["ffmpeg", "-i", concat, "-c", "copy", self.output_file]

        try:
            subprocess.run(command, check = True)
        except Exception as e:
            general.print_message_nok(f"Media files concatenation failed ({e})")
            return False

        general.print_message_ok("Media files concatenation successful")
        return True

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-pu', '--playlist-url', type = str,
                        help = 'The url to the HLS playlist file',
                        required = True)
    parser.add_argument('-of', '--output-file', type = str,
                        help = 'The name of the output video file',
                        required = True)
    parser.add_argument('-hh', '--http-headers', type = str,
                        help = 'The headers provided to the server',
                        required = False, default = "")
    args = parser.parse_args()

    if args.http_headers:
        parsed_headers = ast.literal_eval(args.http_headers)
    else:
        parsed_headers = {}

    pl_dler = Playlist_Dler(args.playlist_url, args.output_file, parsed_headers)
    successful = pl_dler.download_playlist()

    if successful:
        general.print_message_ok("Playlist processing successful")
    else:
        general.print_message_nok("Playlist processing failed")

if __name__ == "__main__":
    main()
