# DL-Scripts

## Installation

### Install package

```
$ pip install -e <path/to/dl-scripts>
```

### Uninstall package

```
$ pip uninstall dl-scripts
```

## Execution

### Playlist-Downloader

```
$ playlist_downloader -h
usage: playlist_downloader [-h] -pu PLAYLIST_URL -of OUTPUT_FILE [-hh HTTP_HEADERS]

options:
  -h, --help            show this help message and exit
  -pu PLAYLIST_URL, --playlist-url PLAYLIST_URL
                        The url to the HLS playlist file
  -of OUTPUT_FILE, --output-file OUTPUT_FILE
                        The name of the output video file
  -hh HTTP_HEADERS, --http-headers HTTP_HEADERS
                        The headers provided to the server
```

### Pattern-Downloader

```
$ pattern_downloader -h
usage: pattern_downloader [-h] -ru RESOURCE_URL -sp SEARCH_PATTERN

options:
  -h, --help            show this help message and exit
  -ru RESOURCE_URL, --resource-url RESOURCE_URL
  -sp SEARCH_PATTERN, --search-pattern SEARCH_PATTERN
```

## Appendix

### URL components

```
URL: https://www.example.com/path/to/file.ts?key=12345
     |         Base         |     Path      |  Args  |
     |Scheme|     Host      | Dirs  | File  |  Args  |
```
