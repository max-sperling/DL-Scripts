from utils import download
from utils import general

import argparse
import concurrent.futures
import os
import threading
import subprocess

def download_playlist(playlist_link, output_file):
    storage_link = download.get_link_without_resource(playlist_link)
    playlist_file_wa = download.get_resource_with_webargs(playlist_link)
    playlist_file = download.get_resource_without_webargs(playlist_link)

    if not download_playlist_file(storage_link, playlist_file_wa):
        return False
    if not download_media_files(storage_link, playlist_file):
        return False
    if not concat_media_files(playlist_file, output_file):
        return False

    return True

def download_playlist_file(storage_link, playlist_file_wa):
    file_list = [playlist_file_wa]

    successful = download_files(storage_link, file_list)

    if successful:
        general.print_message("Playlist file download successful")
    else:
        general.print_message("Playlist file download failed")

    return successful

def download_media_files(storage_link, playlist_file):
    file_list = []

    with open(playlist_file, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                file_list.append(line)

    successful = download_files(storage_link, file_list)

    if successful:
        general.print_message("Media files download successful")
    else:
        general.print_message("Media files download failed")

    return successful

def download_files(storage_link, url_list):
    successful = True
    lock = threading.Lock()

    def download_file_task(url_wa):
        nonlocal successful

        file_wa = download.get_resource_with_webargs(url_wa)
        file = download.get_resource_without_webargs(url_wa)
        file_link = f"{storage_link}/{file_wa}"
        local_path = os.path.join(os.getcwd(), file)

        if not download.download_file(file_link, local_path):
            with lock:
                successful = False

    with concurrent.futures.ThreadPoolExecutor(max_workers = 5) as executor:
        executor.map(download_file_task, url_list)

    return successful

def concat_media_files(playlist_file, output_file):
    concat = "concat:"

    with open(playlist_file, 'r') as f:
        for line in f:
            line = line.strip()
            if not line.startswith('#'):
                url_wa = line
                file = download.get_resource_without_webargs(url_wa)
                concat += f"{file}|"

    concat = concat.rstrip('|')
    command = ["ffmpeg", "-i", concat, "-c", "copy", output_file]

    try:
        subprocess.run(command, check=True)
    except Exception as e:
        general.print_message(f"Media files concatenation failed ({e})")
        return False

    general.print_message("Media files concatenation successful")
    return True

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--playlist-link', type = str, required = True)
    parser.add_argument('-o', '--output-file', type = str, required = True)

    args = parser.parse_args()
    successful = download_playlist(args.playlist_link, args.output_file)

    if successful:
        general.print_message("Playlist processing successful")
    else:
        general.print_message("Playlist processing failed")

if __name__ == "__main__":
    main()
