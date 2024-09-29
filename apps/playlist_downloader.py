from utils import download
from utils import general

from enum import Enum
import argparse
import ast
import concurrent.futures
import hashlib
import os
import threading
import subprocess

class Playlist_Dler:
    class URL_Overlap(str, Enum): # ... between the playlist and the media files
        path   = 'path'   # Domain and path matches (default)
        domain = 'domain' # Only the domain matches

    class DL_Content(str, Enum): # ... of the items listed in the playlist file
        files   = 'files'   # They are files (default)
        folders = 'folders' # They are folders

    def __init__(self, http_headers, url_overlap, dl_content):
        self.http_headers = http_headers
        self.url_overlap = url_overlap
        self.dl_content = dl_content

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
        base_url = download.get_url_domain_dir(playlist_url)
        rel_url_list = [download.get_url_file_args(playlist_url)]

        successful = self.download_files(base_url, rel_url_list, self.DL_Content.files)

        if successful:
            general.print_message("Playlist file download successful")
        else:
            general.print_message("Playlist file download failed")

        return successful

    def download_media_files(self, playlist_url):
        base_url = ""
        rel_url_list = []

        match self.url_overlap:
            case self.URL_Overlap.path:
                base_url = download.get_url_domain_dir(playlist_url)
            case self.URL_Overlap.domain:
                base_url = download.get_url_domain(playlist_url)

        playlist_file = download.get_url_file(playlist_url)
        with open(playlist_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    match self.url_overlap:
                        case self.URL_Overlap.path:
                            line = download.get_url_file_args(playlist_url)
                    rel_url_list.append(line)

        successful = self.download_files(base_url, rel_url_list, self.dl_content)

        if successful:
            general.print_message("Media files download successful")
        else:
            general.print_message("Media files download failed")

        return successful

    def download_files(self, base_url, rel_url_list, dl_content):
        successful = True
        lock = threading.Lock()

        def download_file_task(rel_url_wa):
            nonlocal successful

            file_url = f"{base_url}/{rel_url_wa}"
            file_path = ""
            match dl_content:
                case self.DL_Content.files:
                    file = download.get_url_file(rel_url_wa)
                    file_path = os.path.join(os.getcwd(), file)
                case self.DL_Content.folders:
                    file_hashed = hashlib.md5(rel_url_wa.encode()).hexdigest()
                    file_path = os.path.join(os.getcwd(), f"{file_hashed}.ts")

            try:
                download.download_file(file_url, file_path, self.http_headers)
            except Exception as e:
                with lock:
                    general.print_message(f"Download failed: {file_url}, {e}")
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
                    url_wa = line
                    file = ""
                    match self.dl_content:
                        case self.DL_Content.files:
                            file = download.get_url_file(url_wa)
                        case self.DL_Content.folders:
                            file = f"{hashlib.md5(url_wa.encode()).hexdigest()}.ts"
                    concat += f"{file}|"

        concat = concat.rstrip('|')
        command = ["ffmpeg", "-i", concat, "-c", "copy", output_file]

        try:
            subprocess.run(command, check = True)
        except Exception as e:
            general.print_message(f"Media files concatenation failed ({e})")
            return False

        general.print_message("Media files concatenation successful")
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
                        required = False, default = Playlist_Dler.URL_Overlap.path)
    parser.add_argument('-pc', '--plst-content', type = Playlist_Dler.DL_Content,
                        help = 'The item types in the playlist file',
                        required = False, default = Playlist_Dler.DL_Content.files)
    args = parser.parse_args()

    pl_dler = Playlist_Dler(ast.literal_eval(args.http_headers),
                            args.url_overlap, args.plst_content)
    successful = pl_dler.download_playlist(args.playlist_url,
                                           args.output_file)

    if successful:
        general.print_message("Playlist processing successful")
    else:
        general.print_message("Playlist processing failed")

if __name__ == "__main__":
    main()
