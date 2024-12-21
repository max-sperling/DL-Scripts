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
    class URL_Overlap(str, Enum): # ... between the playlist and the media files
        dirs = 'dirs' # Base and dirs match (default)
        base = 'base' # Only the base matches
        none = 'none' # Nothing matches

    def __init__(self, http_headers, url_overlap):
        self.http_headers = http_headers
        self.url_overlap = url_overlap

    def download_playlist(self, playlist_url, output_file):
        playlist_file = download.get_url_file(playlist_url)

        if not self.download_playlist_file(playlist_url):
            return False
        if not self.download_media_files(playlist_url):
            return False
        if not self.concat_media_files(playlist_file, output_file):
            return False

        return True

    def download_playlist_file(self, playlist_url):
        playlist_file = download.get_url_file(playlist_url)

        successful = True 
        try:
            download.download_file(playlist_url, playlist_file, self.http_headers)
        except Exception as e:
            general.print_message_nok(f"Download failed: {playlist_url}, {e}")
            successful = False

        if successful:
            general.print_message_ok("Playlist file download successful")
        else:
            general.print_message_nok("Playlist file download failed")

        return successful

    def download_media_files(self, playlist_url):
        base_url = ""
        rel_url_list = []

        match self.url_overlap:
            case self.URL_Overlap.dirs:
                base_url = download.get_url_base_dirs(playlist_url)
            case self.URL_Overlap.base:
                base_url = download.get_url_base(playlist_url)
            # case self.URL_Overlap.none:
                # nothing to do

        playlist_file = download.get_url_file(playlist_url)
        with open(playlist_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    match self.url_overlap:
                        case self.URL_Overlap.dirs:
                            line = download.get_url_file_args(line)
                        case self.URL_Overlap.base:
                            line = download.get_url_path_args(line)
                        # case self.URL_Overlap.none:
                            # nothing to do
                    rel_url_list.append(line)

        successful = self.download_files(base_url, rel_url_list)

        if successful:
            general.print_message_ok("Media files download successful")
        else:
            general.print_message_nok("Media files download failed")

        return successful

    def download_files(self, base_url, rel_url_list):
        successful = True
        lock = threading.Lock()

        def download_file_task(rel_url_wa):
            nonlocal successful

            file_url = ""
            match self.url_overlap:
                case self.URL_Overlap.dirs:
                    file_url = f"{base_url}/{rel_url_wa}"
                case self.URL_Overlap.base:
                    file_url = f"{base_url}/{rel_url_wa}"
                case self.URL_Overlap.none:
                    file_url = rel_url_wa

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
            executor.map(download_file_task, rel_url_list)

        return successful

    def concat_media_files(self, playlist_file, output_file):
        concat = "concat:"

        with open(playlist_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    line = download.get_url_file(line)
                    concat += f"{line}|"

        concat = concat.rstrip('|')
        command = ["ffmpeg", "-i", concat, "-c", "copy", output_file]

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
    parser.add_argument('-uo', '--url-overlap', type = Playlist_Dler.URL_Overlap,
                        help = 'The overlap between the PL and the files',
                        required = False, default = Playlist_Dler.URL_Overlap.dirs)
    args = parser.parse_args()

    if args.http_headers:
        parsed_headers = ast.literal_eval(args.http_headers)
    else:
        parsed_headers = {}

    pl_dler = Playlist_Dler(parsed_headers, args.url_overlap)
    successful = pl_dler.download_playlist(args.playlist_url, args.output_file)

    if successful:
        general.print_message_ok("Playlist processing successful")
    else:
        general.print_message_nok("Playlist processing failed")

if __name__ == "__main__":
    main()
