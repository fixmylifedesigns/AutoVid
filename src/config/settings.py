# src/config/settings.py

import os

# Base directories
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SRC_DIR = os.path.join(BASE_DIR, 'src')
RESOURCES_DIR = os.path.join(BASE_DIR, 'resources')

# Output and working directories
# OUTPUT_DIR = os.path.join(SRC_DIR, 'output')
# SCREENSHOTS_DIR = os.path.join(OUTPUT_DIR, 'screenshots')
TEMPLATE_DIR = os.path.join(SRC_DIR, 'template')

# File paths
CONFIG_FILE = os.path.join(RESOURCES_DIR, 'config.json')
NAMES_FILE = os.path.join(RESOURCES_DIR, 'names.json')
TRACKING_FILE = os.path.join(RESOURCES_DIR, 'tracking.json')

# Ensure necessary directories exist
# os.makedirs(OUTPUT_DIR, exist_ok=True)
# os.makedirs(SCREENSHOTS_DIR, exist_ok=True)
os.makedirs(TEMPLATE_DIR, exist_ok=True)

# Application settings
APP_NAME = "AutoVid"
APP_VERSION = "1.0.0"

# Video settings
DEFAULT_FPS = 24
MIN_YEAR = 1978
MAX_YEAR = 1986

# You can add more settings as needed