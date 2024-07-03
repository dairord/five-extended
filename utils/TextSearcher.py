from pathlib import Path
import re


base_dir = Path(__file__).parent.parent

def get_tif_list():

    with open(str(base_dir / "elevations" / "indexer.html"), 'r') as file:
        content = file.read()

    pattern = r'linkDescDir_([a-zA-Z0-9]+)'
    matches = re.findall(pattern, content)
    return matches
