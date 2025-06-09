from datetime import datetime
import hashlib
import platform

def get_hashed_text(text):
    return hashlib.md5(text.encode()).hexdigest()

def print_message_ok(message):
    line = f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} {message}"
    print('\033[32m' + line + '\033[0m')

def print_message_nok(message):
    line = f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} {message}"
    print('\033[31m' + line + '\033[0m')

def print_message_warn(message):
    line = f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} {message}"
    print('\033[33m' + line + '\033[0m')

def get_cmd_content_limit():
    cmd_line_limit = 20000
    meta_content = 500

    if platform.system() == "Windows":
        cmd_line_limit = 32767
    elif platform.system() in ("Linux", "Darwin"):
        import os
        cmd_line_limit = os.sysconf("SC_ARG_MAX")
    else:
        print_message_warn("Unknown platform. Using default command line limit.")

    return cmd_line_limit - meta_content

def remove_duplicates(items):
    unique_items = []

    for item in items:
        if item not in unique_items:
            unique_items.append(item)

    return unique_items
