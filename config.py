#!/usr/bin/env python3
"""
Configuration file for Enhanced Hot Spot Detection System
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv('script/.env')

# API Configuration
TWOGIS_API_KEY = os.getenv('DGIS_API_KEY')  # 2GIS API key from .env
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')  # OpenAI API key from .env

# Hot Spot Detection Parameters
HOTSPOT_THRESHOLD = 0.7  # Threshold for considering a location as hot spot (0.0-1.0)
TILE_SIZE_METERS = 100   # Size of each tile in meters (100m x 100m)

# Grid Configuration
GRID_SIZE = 10  # 10x10 grid for Astana dataset
N_SENSORS = GRID_SIZE * GRID_SIZE

# Prediction Parameters
PREDICTION_STEPS = 12  # Number of prediction steps (12 * 5min = 60min)
TIME_INTERVAL_MINUTES = 5  # Time interval between predictions in minutes

# Astana City Coordinates (approximate center)
ASTANA_CENTER_LAT = 51.1694
ASTANA_CENTER_LON = 71.4491

# Grid Coverage (approximate)
GRID_LAT_RANGE = 0.1  # ±0.05 degrees latitude
GRID_LON_RANGE = 0.1  # ±0.05 degrees longitude

# API Timeout Settings
API_TIMEOUT = 30  # seconds

# Visualization Settings
HTML_TITLE = "Enhanced Hot Spot Detection - Astana City"
HTML_DESCRIPTION = "Real-time traffic analysis with organization and event data integration"

# File Output Settings
OUTPUT_DIR = "output"
CURRENT_HOTSPOTS_FILE = "current_hotspots.html"
PREDICTED_HOTSPOTS_FILE = "predicted_hotspots_30min.html"
CURRENT_TILES_FILE = "current_tile_heatmap.csv"
PREDICTED_TILES_FILE = "predicted_tile_heatmap_30min.csv"

# Debug Settings
DEBUG_MODE = False
VERBOSE_LOGGING = True
