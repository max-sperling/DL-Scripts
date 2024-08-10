from datetime import datetime

def print_message(message):
    print(f"{datetime.now().strftime("%Y-%m-%d %H:%M:%S")} {message}")

def remove_duplicates(items):
    unique_items = []

    for item in items:
        if item not in unique_items:
            unique_items.append(item)

    return unique_items
