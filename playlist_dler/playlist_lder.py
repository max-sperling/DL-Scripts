from utils import download
from utils import general
from utils import playlist
from utils import weblinks

def load_playlist(url, headers, resolution, verify):
    playlist_file = weblinks.get_url_file(url)
    try:
        download.download_file(url = url, file = playlist_file, headers = headers, verify = verify)
    except Exception as e:
        general.print_message_nok(f"Download failed: {url}, {e}")
        return None

    variants = playlist.parse_master_playlist(playlist_file)
    if variants:
        selected = playlist.select_variant_by_resolution(
            variants,
            resolution
        )

        if not selected:
            general.print_message_nok("Resolution not found")
            return None

        url = weblinks.join_url(url, selected["URI"])
        playlist_file = weblinks.get_url_file(url)
        try:
            download.download_file(url = url, file = playlist_file, headers = headers, verify = verify)
        except Exception as e:
            general.print_message_nok(f"Download failed: {url}, {e}")
            return None

    segments = []

    with open(playlist_file) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                segments.append(
                    weblinks.join_url(url, line)
                )

    if not segments:
        general.print_message_nok("No segments found")
        return None

    return segments
