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
import urllib.parse

class Playlist_Dler:
    def __init__(self, playlist_url, output_file, http_headers, max_workers, do_verify, resolution):
        self.playlist_url = playlist_url
        self.output_file = output_file
        self.http_headers = http_headers
        self.max_workers = max_workers
        self.do_verify = do_verify
        self.resolution = resolution

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

        if successful:
            general.print_message_ok("Playlist file download successful")
        else:
            general.print_message_nok("Playlist file download failed")

        return successful

    def download_media_playlist_file(self):
        if not self.download_playlist_file(self.playlist_file):
            return False

        variants = playlist.parse_master_playlist(self.playlist_file)
        if not variants:
            general.print_message_info("Media playlist detected")
            return True

        general.print_message_info("Master playlist detected - available resolutions:")
        for v in variants:
            res = v.get('RESOLUTION', 'unknown')
            uri = v.get('URI', '')
            general.print_message_info(f"  resolution={res}, uri={uri}")

        if not self.resolution:
            general.print_message_nok("No resolution selected. Re-run with --resolution WxH.")
            return False

        chosen = playlist.select_variant_by_resolution(variants, self.resolution)
        if not chosen:
            general.print_message_nok("Requested resolution does not match any available variant.")
            return False

        variant_uri = chosen.get('URI')
        variant_uri = urllib.parse.urljoin(self.playlist_url, variant_uri)
        general.print_message_info(f"Selected variant url: {variant_uri}")

        self.playlist_url = variant_uri
        self.playlist_file = weblinks.get_url_file(self.playlist_url)
        if not self.download_playlist_file(self.playlist_file):
            return False

        return True

    def download_media_files(self):
        media_files = []
        base_url = ""

        with open(self.playlist_file, 'r') as file:
            for line in file:
                line = line.strip()
                if line and not line.startswith('#'):
                    media_files.append(line)

        if not media_files:
            general.print_message_nok("No media files found in playlist")
            return False

        self.url_overlap = weblinks.Url_Overlap.calculate(self.playlist_url, media_files[0])
        match self.url_overlap:
            case weblinks.Url_Overlap.DIRS:
                general.print_message_ok("Calculated url overlap: DIRS")
                base_url = weblinks.get_url_base_dirs(self.playlist_url)
                for i in range(len(media_files)):
                    media_files[i] = weblinks.get_url_file_args(media_files[i])
            case weblinks.Url_Overlap.BASE:
                general.print_message_ok("Calculated url overlap: BASE")
                base_url = weblinks.get_url_base(self.playlist_url)
                for i in range(len(media_files)):
                    media_files[i] = weblinks.get_url_path_args(media_files[i])
            case weblinks.Url_Overlap.NONE:
                general.print_message_ok("Calculated url overlap: NONE")
                # nothing to do
            case _:
                general.print_message_nok("Calculated url overlap: Unknown")
                return False

        successful = self.download_files(base_url, media_files)

        if successful:
            general.print_message_ok("Media files download successful")
        else:
            general.print_message_nok("Media files download failed")

        return successful

    def download_files(self, base_url, rel_urls):
        successful = True
        lock = threading.Lock()
        self.urls_are_files = weblinks.url_is_file(rel_urls[0])

        def download_task(rel_url_wa):
            nonlocal successful

            file_url = ""
            if base_url == "":
                file_url = rel_url_wa
            else:
                file_url = f"{base_url}/{rel_url_wa}"

            file = ""
            if self.urls_are_files:
                file = weblinks.get_url_file(rel_url_wa)
            else: # folders
                file = f"{general.get_hashed_text(rel_url_wa)}.ts"

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
            executor.map(download_task, rel_urls)

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
                        match self.url_overlap:
                            case weblinks.Url_Overlap.DIRS:
                                line = f"{general.get_hashed_text(weblinks.get_url_file_args(line))}.ts"
                            case weblinks.Url_Overlap.BASE:
                                line = f"{general.get_hashed_text(weblinks.get_url_path_args(line))}.ts"
                            case weblinks.Url_Overlap.NONE:
                                line = f"{general.get_hashed_text(line)}.ts"

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
            for idx, row in enumerate(ary):
                part = f"{file_name}_part{idx}.ts"
                command = ["ffmpeg", "-i", row, "-c", "copy", part]
                subprocess.run(command, check = True)
                parts += f"{part}|"
            parts = f"concat:{parts}"
            parts = parts.rstrip('|')
            command = ["ffmpeg", "-i", parts, "-c", "copy", self.output_file]
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
    parser.add_argument('-nv', '--no-verify', dest = 'do_verify', action = 'store_false',
                        help = 'Disable TLS certificate verification',
                        required = False, default = True)
    parser.add_argument('-rt', '--resolution', type = str,
                        help = 'Select variant by resolution (WxH)',
                        required = False, default = "")
    args = parser.parse_args()

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
        args.playlist_url, args.output_file, parsed_headers, args.max_workers, args.do_verify, args.resolution)
    successful = pl_dler.download_playlist()

    if successful:
        general.print_message_ok("Playlist processing successful")
    else:
        general.print_message_nok("Playlist processing failed")

if __name__ == "__main__":
    main()
