from typing import List, Dict

def parse_master_playlist(playlist_file: str):
    """
    Simple parser for HLS master playlists.

    Returns a list of variants where each variant is a dict containing
    attributes from the #EXT-X-STREAM-INF line and a 'URI' key for the
    following playlist URI.
    """
    variants: List[Dict[str, str]] = []

    try:
        with open(playlist_file, "r", encoding="utf-8") as file:
            lines = [l.strip() for l in file]
    except Exception:
        return []

    i = 0
    while i < len(lines):
        line = lines[i]

        if not line.startswith("#EXT-X-STREAM-INF:"):
            i += 1
            continue

        attrs: Dict[str, str] = {}
        attrs.setdefault('RESOLUTION', 'unknown')
        attrs.setdefault('URI', 'unknown')

        # Extract attributes
        attrs_str = line.split(":", 1)[1] if ":" in line else ""
        for part in attrs_str.split(','):
            if '=' in part:
                k, v = part.split('=', 1)
                attrs[k.strip()] = v.strip().strip('"')

        # Extract matching URI
        uri = ""
        j = i + 1
        while j < len(lines):
            nxt = lines[j]
            if nxt and not nxt.startswith('#'):
                uri = nxt
                break
            j += 1
        if uri:
            attrs['URI'] = uri
        i = j

        variants.append(attrs)

    return variants

def select_variant_by_resolution(variants: List[Dict[str, str]], resolution: str):
    """
    Select variant by exact resolution only.

    Returns the first variant whose RESOLUTION exactly matches the requested
    resolution (case-insensitive). If no match is found, returns None.
    """
    if not variants or not resolution:
        return None

    target = resolution.strip().lower()

    for v in variants:
        if v.get('RESOLUTION', '').lower() == target:
            return v

    return None
