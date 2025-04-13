import os
import requests

def download_file(url, file, headers = {}, attempts = 3):
    if os.path.isfile(file):
        return

    while attempts > 0:
        try:
            response = requests.get(url, headers = headers, timeout = (5, 30))
            response.raise_for_status()
            with open(file, 'wb') as f:
                f.write(response.content)
            return
        except Exception as e:
            attempts -= 1
            if attempts == 0:
                if os.path.isfile(file):
                    os.remove(file)
                raise
