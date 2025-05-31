from datetime import datetime
import hashlib

def hash_text(text):
    return hashlib.md5(text.encode()).hexdigest()

def print_message_ok(message):
    line = f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} {message}"
    print('\033[32m' + line + '\033[0m')

def print_message_nok(message):
    line = f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} {message}"
    print('\033[31m' + line + '\033[0m')

def remove_duplicates(items):
    unique_items = []

    for item in items:
        if item not in unique_items:
            unique_items.append(item)

    return unique_items
