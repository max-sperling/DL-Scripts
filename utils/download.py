import os
import requests
import urllib3

def download_file(url, file, headers = None, attempts = 3, timeout = (5, 30), verify = True):
    """
    Download a URL to a local file with retry and timeout control.

    Parameters
    ----------
    url : str
        The URL to download.
    file : str
        Path to the local file to write the response content to. If the file
        already exists the function returns immediately.
    headers : dict, optional
        HTTP headers to include with the request. Defaults to empty dict.
    attempts : int, optional
        Number of attempts to try the download before giving up. Defaults to 3.
    timeout : float or (float, float), optional
        Timeout to pass to :func:`requests.get` in seconds. Can be a single
        float (applies to both connect and read) or a ``(connect, read)``
        tuple. The default ``(5, 30)`` preserves the previous behavior
        (5s connect, 30s read). Passing ``None`` disables the timeout (not
        recommended).
    verify : bool, optional
        Whether to verify the server's TLS certificate. Defaults to True.

    Raises
    ------
    requests.exceptions.RequestException
        Any exception raised by :mod:`requests` that is not retried further.

    Notes
    -----
    The function will remove a partially-downloaded file if the final
    attempt fails.
    """
    if os.path.isfile(file):
        return

    if headers is None:
        headers = {}

    # If verify is False, suppress InsecureRequestWarning
    if verify is False:
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    while attempts > 0:
        try:
            response = requests.get(url, headers = headers, timeout = timeout, verify = verify)
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
