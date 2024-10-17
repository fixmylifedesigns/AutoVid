# src/core/utils.py

import json
import re
from config.settings import NAMES_FILE, TRACKING_FILE

def sanitize_filename(name):
    """Sanitize the filename by removing unsafe characters and replacing spaces"""
    return re.sub(r'[\/:*?"<>|]', '', name).replace(' ', '_')

def parse_filename(filename):
    """Parse filename to extract song name, artist, and year"""
    pattern = r"(.+)_(.+)_(\d{4})\.mp3"
    match = re.match(pattern, filename)
    return match.groups() if match else (None, None, None)

def load_names(names_file=NAMES_FILE):
    """Load names from the names.json file"""
    try:
        with open(names_file, 'r') as f:
            names_data = json.load(f)
        return names_data['first_names'], names_data['last_names']
    except FileNotFoundError:
        print(f"Names file '{names_file}' not found.")
        return [], []

def load_tracking(tracking_file=TRACKING_FILE):
    """Load the tracking data from file"""
    try:
        with open(tracking_file, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_tracking(tracking_data, tracking_file=TRACKING_FILE):
    """Save the tracking data to file"""
    with open(tracking_file, 'w', encoding='utf-8') as f:
        json.dump(tracking_data, f, ensure_ascii=False, indent=4)