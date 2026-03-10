import argparse
import ast

from playlist_dler.playlist_dler import Playlist_Dler
from utils import general

def main():
    parser = argparse.ArgumentParser()

    parser.add_argument('-pu', '--playlist-url', type=str, required=True)
    parser.add_argument('-of', '--output-file', type=str, required=True)
    parser.add_argument('-hh', '--http-headers', type=str, default="")
    parser.add_argument('-mw', '--max-workers', type=int, default=10)
    parser.add_argument('-rt', '--resolution', type=str, default="")

    parser.add_argument('-f', '--force', dest='do_forced', action='store_true', default=False)
    parser.add_argument('-nv', '--no-verify', dest='do_verify', action='store_false', default=True)
    parser.add_argument('-v', '--verbose', dest='be_verbose', action='store_true', default=False)

    args = parser.parse_args()

    headers = ast.literal_eval(args.http_headers) if args.http_headers else {}

    dler = Playlist_Dler(
        args.playlist_url,
        args.output_file,
        headers,
        args.max_workers,
        args.resolution,
        args.do_verify,
        args.be_verbose,
        args.do_forced
    )

    if dler.run():
        general.print_message_ok("Playlist processing successful")
    else:
        general.print_message_nok("Playlist processing failed")


if __name__ == "__main__":
    main()
