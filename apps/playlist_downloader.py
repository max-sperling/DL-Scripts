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
    def __init__(self, playlist_url, output_file, http_headers, max_workers, resolution, do_verify, be_verbose, do_forced):
        self.playlist_url = playlist_url
        self.output_file = output_file
        self.media_file_urls = []
        self.urls_are_files = True
        self.http_headers = http_headers
        self.max_workers = max_workers
        self.resolution = resolution
        self.do_verify = do_verify
        self.be_verbose = be_verbose
        self.do_forced = do_forced

    def download_playlist(self):
        self.playlist_file = weblinks.get_url_file(self.playlist_url)

        if not self.download_media_playlist_file():
            return False
        if not self.parse_media_files():
            return False
        if not self.download_media_files():
            return False
        if not self.concat_media_files():
            return False

        return True

    def download_media_playlist_file(self):
        if not self.download_playlist_file():
            return False

        variants = playlist.parse_master_playlist(self.playlist_file)
        if not variants:
            general.print_message_ok("Media playlist download successful")
            return True
        general.print_message_ok("Master playlist download successful")

        media_playlist_uri = self.get_media_playlist_uri(variants)
        if not media_playlist_uri:
            return False

        self.playlist_url = media_playlist_uri
        self.playlist_file = weblinks.get_url_file(self.playlist_url)
        if not self.download_playlist_file():
            return False

        general.print_message_ok("Media playlist download successful")
        return True

    def download_playlist_file(self):
        successful = True

        try:
            download.download_file(
                url = self.playlist_url, file = self.playlist_file, headers = self.http_headers, verify = self.do_verify)
        except Exception as e:
            general.print_message_nok(f"Download failed: {self.playlist_url}, {e}")
            successful = False

        return successful

    def get_media_playlist_uri(self, variants):
        if self.be_verbose:
            general.print_message_info("Available resolutions:")
            for v in variants:
                res = v.get('RESOLUTION', 'unknown')
                uri = v.get('URI', 'unknown')
                general.print_message_info(f"  resolution={res}, uri={uri}")

        if not self.resolution:
            general.print_message_nok("No resolution selected. Re-run with --resolution WxH.")
            return None

        selected_media_playlist = playlist.select_variant_by_resolution(variants, self.resolution)
        if not selected_media_playlist:
            general.print_message_nok("Requested resolution does not match any available variant.")
            return None

        media_playlist_uri = selected_media_playlist.get('URI')
        media_playlist_uri = weblinks.join_url(self.playlist_url, media_playlist_uri)

        if self.be_verbose:
            general.print_message_info(f"Selected media playlist: {media_playlist_uri}")

        return media_playlist_uri

    def parse_media_files(self):
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

        self.media_file_urls = media_files
        self.urls_are_files = weblinks.url_is_file(self.media_file_urls[0])

        return True

    def download_media_files(self):
        successful = True
        lock = threading.Lock()

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
            executor.map(download_task, self.media_file_urls)

        if successful:
            general.print_message_ok("Media files download successful")
        else:
            general.print_message_nok("Media files download failed")

        return successful

    def concat_media_files(self):
        try:
            output_file_name, _ = self.output_file.rsplit('.')

            if self.be_verbose:
                verbosity_args = []
            else:
                verbosity_args = ["-loglevel", "warning"]

            if self.do_forced:
                format_flags = ["-fflags", "+discardcorrupt"]
            else:
                format_flags = []

            with open(f"{output_file_name}.ts", "wb") as outfile:
                for media_file_url in self.media_file_urls:
                    if self.urls_are_files:
                        media_file = weblinks.get_url_file(media_file_url)
                    else: # folders
                        media_file = f"{general.get_hashed_text(media_file_url)}.ts"
                    with open(media_file, "rb") as infile:
                        outfile.write(infile.read())

            command = ["ffmpeg", *verbosity_args, *format_flags, "-i", f"{output_file_name}.ts", "-c", "copy", self.output_file]
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

    parser.add_argument('-f', '--force', dest = 'do_forced', action = 'store_true',
                        help = 'Forces the video concat even with gaps',
                        required = False, default = False)
    parser.add_argument('-nv', '--no-verify', dest = 'do_verify', action = 'store_false',
                        help = 'Disable TLS certificate verification',
                        required = False, default = True)
    parser.add_argument('-v', '--verbose', dest='be_verbose', action='store_true',
                        help = 'Prints all the details',
                        required = False, default = False)

    args = parser.parse_args()

    if args.http_headers:
        parsed_headers = ast.literal_eval(args.http_headers)
    else:
        parsed_headers = {}

    pl_dler = Playlist_Dler(
        args.playlist_url, args.output_file, parsed_headers, args.max_workers, args.resolution, args.do_verify, args.be_verbose, args.do_forced)
    successful = pl_dler.download_playlist()

    if successful:
        general.print_message_ok("Playlist processing successful")
    else:
        general.print_message_nok("Playlist processing failed")

if __name__ == "__main__":
    main()
