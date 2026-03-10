import concurrent.futures
import threading
import os

from utils import download
from utils import weblinks
from utils import general

def download_segments(urls, urls_are_files, headers, workers, verify):
    success = True
    lock = threading.Lock()

    def worker(url):
        nonlocal success

        if urls_are_files:
            file = weblinks.get_url_file(url)
        else:
            file = f"{general.get_hashed_text(url)}.ts"

        path = os.path.join(os.getcwd(), file)
        try:
            download.download_file(url = url, file = path, headers = headers, verify = verify)
        except Exception as e:
            with lock:
                general.print_message_nok("Download failed\n"
                                          f"File-URL: {url},\n"
                                          f"File-Path: {path},\n"
                                          f"Exception: {e}\n")
                success = False

    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as pool:
        pool.map(worker, urls)

    return success
