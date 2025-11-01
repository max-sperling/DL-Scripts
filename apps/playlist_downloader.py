from utils import download
from utils import general
from utils import playlist
from utils import weblinks

import argparse
import ast
import concurrent.futures
import os
import threading
import subprocess

class Playlist_Dler:
    def __init__(self, playlist_url, output_file, http_headers, max_workers, resolution, do_verify, be_verbose):
        self.playlist_url = playlist_url
        self.output_file = output_file
        self.http_headers = http_headers
        self.max_workers = max_workers
        self.resolution = resolution
        self.do_verify = do_verify
        self.be_verbose = be_verbose

    def download_playlist(self):
        self.playlist_file = weblinks.get_url_file(self.playlist_url)

        if not self.download_media_playlist_file():
            return False
        if not self.download_media_files():
            return False
        if not self.concat_media_files():
            return False

        return True

    def download_playlist_file(self, playlist_file):
        successful = True

        try:
            download.download_file(
                url = self.playlist_url, file = playlist_file, headers = self.http_headers, verify = self.do_verify)
        except Exception as e:
            general.print_message_nok(f"Download failed: {self.playlist_url}, {e}")
            successful = False

        return successful

    def download_media_playlist_file(self):
        if not self.download_playlist_file(self.playlist_file):
            return False

        variants = playlist.parse_master_playlist(self.playlist_file)
        if not variants:
            general.print_message_ok("Media playlist download successful")
            return True

        general.print_message_ok("Master playlist download successful")

        if self.be_verbose:
            general.print_message_info("Available resolutions:")
            for v in variants:
                res = v.get('RESOLUTION', 'unknown')
                uri = v.get('URI', 'unknown')
                general.print_message_info(f"  resolution={res}, uri={uri}")

        if not self.resolution:
            general.print_message_nok("No resolution selected. Re-run with --resolution WxH.")
            return False

        chosen = playlist.select_variant_by_resolution(variants, self.resolution)
        if not chosen:
            general.print_message_nok("Requested resolution does not match any available variant.")
            return False

        variant_uri = chosen.get('URI')
        variant_uri = weblinks.join_url(self.playlist_url, variant_uri)

        if self.be_verbose:
            general.print_message_info(f"Selected media playlist: {variant_uri}")

        self.playlist_url = variant_uri
        self.playlist_file = weblinks.get_url_file(self.playlist_url)
        if not self.download_playlist_file(self.playlist_file):
            return False

        general.print_message_ok("Media playlist download successful")
        return True

    def download_media_files(self):
        media_files = []

        with open(self.playlist_file, 'r') as file:
            for line in file:
                line = line.strip()
                if line and not line.startswith('#'):
                    media_files.append(line)

        if not media_files:
            general.print_message_nok("No media files found in playlist")
            return False

        for i in range(len(media_files)):
            media_files[i] = weblinks.join_url(self.playlist_url, media_files[i])

        successful = self.download_files(media_files)
        if successful:
            general.print_message_ok("Media files download successful")
        else:
            general.print_message_nok("Media files download failed")

        return successful

    def download_files(self, file_urls):
        successful = True
        lock = threading.Lock()
        self.urls_are_files = weblinks.url_is_file(file_urls[0])

        def download_task(file_url):
            nonlocal successful

            if self.urls_are_files:
                file = weblinks.get_url_file(file_url)
            else: # folders
                file = f"{general.get_hashed_text(file_url)}.ts"

            file_path = os.path.join(os.getcwd(), file)

            try:
                download.download_file(
                    url = file_url, file = file_path, headers = self.http_headers, verify = self.do_verify)
            except Exception as exception:
                with lock:
                    general.print_message_nok("Download failed\n"
                        f"File-URL: {file_url},\n"
                        f"File-Path: {file_path},\n"
                        f"Exception: {exception}\n")
                    successful = False

        with concurrent.futures.ThreadPoolExecutor(max_workers = self.max_workers) as executor:
            executor.map(download_task, file_urls)

        return successful

    def concat_media_files(self):
        ary = []

        with open(self.playlist_file, 'r') as file:
            max_len, _ = general.get_cmd_content_limit()
            row = ""
            for line in file:
                line = line.strip()
                if line and not line.startswith('#'):
                    if self.urls_are_files:
                        line = weblinks.get_url_file(line)
                    else: # folders
                        file_url = weblinks.join_url(self.playlist_url, line)
                        line = f"{general.get_hashed_text(file_url)}.ts"

                    if len(row) <= max_len:
                        row += f"{line}|"
                    else:
                        row = f"concat:{row}"
                        row = row.rstrip('|')
                        ary.append(row)
                        row = ""
            if row:
                row = f"concat:{row}"
                row = row.rstrip('|')
                ary.append(row)

        try:
            file_name, _ = self.output_file.rsplit('.')
            parts = ""

            if self.be_verbose:
                verbosity_args = []
            else:
                verbosity_args = ["-loglevel", "warning"]

            for idx, row in enumerate(ary):
                part = f"{file_name}_part{idx}.ts"
                command = ["ffmpeg", *verbosity_args, "-i", row, "-c", "copy", part]
                subprocess.run(command, check = True)
                parts += f"{part}|"
            parts = f"concat:{parts}"
            parts = parts.rstrip('|')
            command = ["ffmpeg", *verbosity_args, "-i", parts, "-c", "copy", self.output_file]
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
    parser.add_argument('-mw', '--max-workers', type = int,
                        help = 'The maximum number of download workers',
                        required = False, default = 10)
    parser.add_argument('-rt', '--resolution', type = str,
                        help = 'Select variant by resolution (WxH)',
                        required = False, default = "")

    parser.add_argument('-nv', '--no-verify', dest = 'do_verify', action = 'store_false',
                        help = 'Disable TLS certificate verification',
                        required = False, default = True)
    parser.add_argument('-v', '--verbose', dest='be_verbose', action='store_true',
                        help = 'Print provided arguments', required = False, default = False)

    args = parser.parse_args()

    if args.be_verbose:
        general.print_message_info("Provided arguments:")
        general.print_message_info(f"  playlist_url: {args.playlist_url}")
        general.print_message_info(f"  output_file: {args.output_file}")
        general.print_message_info(f"  http_headers : {args.http_headers}")
        general.print_message_info(f"  max_workers: {args.max_workers}")
        general.print_message_info(f"  do_verify : {args.do_verify}")
        general.print_message_info(f"  resolution : {args.resolution}")

    if args.http_headers:
        parsed_headers = ast.literal_eval(args.http_headers)
    else:
        parsed_headers = {}

    pl_dler = Playlist_Dler(
        args.playlist_url, args.output_file, parsed_headers, args.max_workers, args.resolution, args.do_verify, args.be_verbose)
    successful = pl_dler.download_playlist()

    if successful:
        general.print_message_ok("Playlist processing successful")
    else:
        general.print_message_nok("Playlist processing failed")

if __name__ == "__main__":
    main()
