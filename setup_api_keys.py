#!/usr/bin/env python3
"""
API Key Setup Script for Enhanced Hot Spot Detection System
"""

import os
import getpass

def setup_api_keys():
    """Interactive setup for API keys"""
    print("🔑 API Key Setup for Enhanced Hot Spot Detection System")
    print("=" * 60)
    
    print("\nThis script will help you set up API keys for external services.")
    print("You can skip any API key by pressing Enter.")
    
    # 2GIS API Key
    print("\n1. 2GIS API Key")
    print("   Get your API key from: https://2gis.ru/api")
    print("   This is used to query nearby organizations and businesses.")
    
    twogis_key = getpass.getpass("   Enter 2GIS API key (or press Enter to skip): ").strip()
    if not twogis_key:
        twogis_key = None
        print("   ⚠️  2GIS API key not set - will use mock data")
    else:
        print("   ✅ 2GIS API key saved")
    
    # OpenAI API Key
    print("\n2. OpenAI API Key")
    print("   Get your API key from: https://platform.openai.com/api-keys")
    print("   This is used to query for event information using ChatGPT.")
    
    openai_key = getpass.getpass("   Enter OpenAI API key (or press Enter to skip): ").strip()
    if not openai_key:
        openai_key = None
        print("   ⚠️  OpenAI API key not set - will use mock data")
    else:
        print("   ✅ OpenAI API key saved")
    
    # Save to config file
    config_content = f'''#!/usr/bin/env python3
"""
Configuration file for Enhanced Hot Spot Detection System
"""

# API Configuration
TWOGIS_API_KEY = {repr(twogis_key)}
OPENAI_API_KEY = {repr(openai_key)}

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
'''
    
    with open('config.py', 'w') as f:
        f.write(config_content)
    
    print(f"\n✅ Configuration saved to config.py")
    
    # Summary
    print("\n" + "=" * 60)
    print("📋 SETUP SUMMARY")
    print("=" * 60)
    print(f"2GIS API Key: {'✅ Set' if twogis_key else '❌ Not set (will use mock data)'}")
    print(f"OpenAI API Key: {'✅ Set' if openai_key else '❌ Not set (will use mock data)'}")
    
    if not twogis_key and not openai_key:
        print("\n⚠️  No API keys set - the system will run with mock data")
        print("   This is fine for testing, but for real-world data:")
        print("   1. Get a 2GIS API key for organization data")
        print("   2. Get an OpenAI API key for event information")
        print("   3. Run this script again to set them up")
    
    print("\n🚀 You can now run the enhanced hot spot detection system!")
    print("   python enhanced_hotspot_detection.py")

if __name__ == "__main__":
    setup_api_keys()
