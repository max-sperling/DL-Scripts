from utils import download
from utils import general

import argparse
import ast
import concurrent.futures
import hashlib
import os
import threading
import subprocess
from enum import Enum

HEADERS = {}

class DL_Content(str, Enum): # DL content in the playlist file
    files   = 'files'   # Contains files (default)
    folders = 'folders' # Contains folder
CONTENT = DL_Content.files

class URL_Overlap(str, Enum): # URL overlap between playlist and media files
    path   = 'path'   # Domain and path matches (default)
    domain = 'domain' # Only the domain matches
OVERLAP = URL_Overlap.path

def download_playlist(playlist_url, output_file):
    playlist_file = download.get_url_file(playlist_url)

    if not download_playlist_file(playlist_url):
        return False
    if not download_media_files(playlist_url):
        return False
    if not concat_media_files(playlist_file, output_file):
        return False

    return True

def download_playlist_file(playlist_url):
    base_url = download.get_url_domain_dir(playlist_url)
    rel_url_list = [download.get_url_file_args(playlist_url)]

    successful = download_files(base_url, rel_url_list, DL_Content.files)

    if successful:
        general.print_message("Playlist file download successful")
    else:
        general.print_message("Playlist file download failed")

    return successful

def download_media_files(playlist_url):
    base_url = ""
    rel_url_list = []

    match OVERLAP:
        case URL_Overlap.path:
            base_url = download.get_url_domain_dir(playlist_url)
        case URL_Overlap.domain:
            base_url = download.get_url_domain(playlist_url)

    playlist_file = download.get_url_file(playlist_url)
    with open(playlist_file, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                match OVERLAP:
                    case URL_Overlap.path:
                        line = download.get_url_file_args(playlist_url)
                rel_url_list.append(line)

    successful = download_files(base_url, rel_url_list, CONTENT)

    if successful:
        general.print_message("Media files download successful")
    else:
        general.print_message("Media files download failed")

    return successful

def download_files(base_url, rel_url_list, dl_content):
    successful = True
    lock = threading.Lock()

    def download_file_task(rel_url_wa):
        nonlocal successful

        file_url = f"{base_url}/{rel_url_wa}"
        file_path = ""
        match dl_content:
            case DL_Content.files:
                file = download.get_url_file(rel_url_wa)
                file_path = os.path.join(os.getcwd(), file)
            case DL_Content.folders:
                file_hashed = hashlib.md5(rel_url_wa.encode()).hexdigest()
                file_path = os.path.join(os.getcwd(), f"{file_hashed}.ts")

        try:
            download.download_file(file_url, file_path, HEADERS)
        except Exception as e:
            with lock:
                general.print_message(f"Download failed: {file_url}, {e}")
                successful = False

    with concurrent.futures.ThreadPoolExecutor(max_workers = 5) as executor:
        executor.map(download_file_task, rel_url_list)

    return successful

def concat_media_files(playlist_file, output_file):
    concat = "concat:"

    with open(playlist_file, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                url_wa = line
                file = ""
                match CONTENT:
                    case DL_Content.files:
                        file = download.get_url_file(url_wa)
                    case DL_Content.folders:
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
    parser.add_argument('-P', '--playlist-url', type = str,         required = True)
    parser.add_argument('-O', '--output-file',  type = str,         required = True)
    parser.add_argument('-H', '--http-headers', type = str,         required = False)
    parser.add_argument('-C', '--plst-content', type = DL_Content,  required = False)
    parser.add_argument('-U', '--url-overlap',  type = URL_Overlap, required = False)
    args = parser.parse_args()

    if args.http_headers is not None:
        global HEADERS
        HEADERS = ast.literal_eval(args.http_headers)

    if args.plst_content is not None:
        global CONTENT
        CONTENT = args.plst_content

    if args.url_overlap is not None:
        global OVERLAP
        OVERLAP = args.url_overlap

    successful = download_playlist(args.playlist_url, args.output_file)

    if successful:
        general.print_message("Playlist processing successful")
    else:
        general.print_message("Playlist processing failed")

if __name__ == "__main__":
    main()
