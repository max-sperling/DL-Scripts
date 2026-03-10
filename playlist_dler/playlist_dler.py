from playlist_dler.playlist_lder import load_playlist
from playlist_dler.segment_dler import download_segments
from playlist_dler.video_muxer import mux_segments
from utils import weblinks

class Playlist_Dler:
    def __init__(self, playlist_url, output_file, headers,
                 workers, resolution, verify, verbose, force):
        self.playlist_url = playlist_url
        self.output_file = output_file
        self.headers = headers
        self.workers = workers
        self.resolution = resolution
        self.verify = verify
        self.verbose = verbose
        self.force = force

    def run(self):
        segments = load_playlist(
            self.playlist_url,
            self.headers,
            self.resolution,
            self.verify
        )

        if not segments:
            return False

        urls_are_files = weblinks.url_is_file(segments[0])

        if not download_segments(
            segments,
            urls_are_files,
            self.headers,
            self.workers,
            self.verify):
            return False

        return mux_segments(
            segments,
            urls_are_files,
            self.output_file,
            self.verbose,
            self.force
        )
