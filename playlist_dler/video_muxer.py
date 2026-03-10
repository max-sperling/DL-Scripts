import subprocess

from utils import weblinks
from utils import general

def mux_segments(urls, urls_are_files, output_file, verbose, force):
    try:
        name, _ = output_file.rsplit(".")
        ts_file = f"{name}.ts"

        with open(ts_file, "wb") as outfile:
            for url in urls:
                if urls_are_files:
                    file = weblinks.get_url_file(url)
                else:
                    file = f"{general.get_hashed_text(url)}.ts"

                with open(file, "rb") as f:
                    outfile.write(f.read())

        args = ["ffmpeg"]
        if not verbose:
            args += ["-loglevel", "warning"]
        if force:
            args += ["-fflags", "+discardcorrupt"]
        args += [
            "-i", ts_file,
            "-c", "copy",
            output_file
        ]
        subprocess.run(args, check=True)

        general.print_message_ok("Muxing successful")
        return True

    except Exception as e:
        general.print_message_nok(f"Muxing failed ({e})")
        return False
