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
usage: playlist_downloader [-h] -pu PLAYLIST_URL -of OUTPUT_FILE [-hh HTTP_HEADERS] [-mw MAX_WORKERS] [-rt RESOLUTION]
                           [-f] [-nv] [-v]

options:
  -h, --help            show this help message and exit
  -pu, --playlist-url PLAYLIST_URL
                        The url to the HLS playlist file
  -of, --output-file OUTPUT_FILE
                        The name of the output video file
  -hh, --http-headers HTTP_HEADERS
                        The headers provided to the server
  -mw, --max-workers MAX_WORKERS
                        The maximum number of download workers
  -rt, --resolution RESOLUTION
                        Select variant by resolution (WxH)
  -f, --force           Forces the video concat even with gaps
  -nv, --no-verify      Disable TLS certificate verification
  -v, --verbose         Prints all the details
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

## Testing

```
<path/to/dl-scripts>$ python -m unittest -v
```

## Appendix

### URL components

```
URL: https://www.example.com/path/to/file.ts?key=12345
     |         Base         |     Path      |  Args  |
     |Scheme|     Host      | Dirs  | File  |  Args  |
```
