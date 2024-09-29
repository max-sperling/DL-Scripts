# DL-Scripts

## Installation

### Install package

<pre>
$ pip install -e &lt;path/to/dl-scripts&gt;
</pre>

### Uninstall package

<pre>
$ pip uninstall dl-scripts
</pre>

## Execution

### Playlist-Downloader

<pre>
$ playlist_downloader -h
usage: playlist_downloader [-h] -pu PLAYLIST_URL -of OUTPUT_FILE [-hh HTTP_HEADERS] [-uo URL_OVERLAP]
                           [-pc PLST_CONTENT]

options:
  -h, --help            show this help message and exit
  -pu PLAYLIST_URL, --playlist-url PLAYLIST_URL
                        The url to the HLS playlist file
  -of OUTPUT_FILE, --output-file OUTPUT_FILE
                        The name of the output video file
  -hh HTTP_HEADERS, --http-headers HTTP_HEADERS
                        The headers provided to the server
  -uo URL_OVERLAP, --url-overlap URL_OVERLAP
                        The overlap between the PL and the files
  -pc PLST_CONTENT, --plst-content PLST_CONTENT
                        The item types in the playlist file
</pre>

### Pattern-Downloader

<pre>
$ pattern_downloader -h
usage: pattern_downloader [-h] -ru RESOURCE_URL -sp SEARCH_PATTERN

options:
  -h, --help            show this help message and exit
  -ru RESOURCE_URL, --resource-url RESOURCE_URL
  -sp SEARCH_PATTERN, --search-pattern SEARCH_PATTERN
</pre>
