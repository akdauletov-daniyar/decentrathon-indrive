#!/usr/bin/env python3
"""
Enhanced Hot Spot Detection System - Main Runner
Demonstrates the complete pipeline with 2GIS API integration and event detection
"""

import os
import sys
import time
from datetime import datetime

# Add current directory to path for imports
sys.path.append('.')

from enhanced_hotspot_detection import HotSpotDetector
from config import TWOGIS_API_KEY, OPENAI_API_KEY

def print_banner():
    """Print system banner"""
    print("=" * 80)
    print("🔥 ENHANCED HOT SPOT DETECTION SYSTEM")
    print("   Spatio-Temporal Graph Convolutional Networks + Real-World Data")
    print("=" * 80)
    print(f"🕐 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

def check_dependencies():
    """Check if all required dependencies are available"""
    print("🔍 Checking dependencies...")
    
    required_modules = [
        'numpy', 'pandas', 'torch', 'sklearn', 'matplotlib', 'requests'
    ]
    
    missing_modules = []
    for module in required_modules:
        try:
            __import__(module)
            print(f"   ✅ {module}")
        except ImportError:
            missing_modules.append(module)
            print(f"   ❌ {module} - MISSING")
    
    if missing_modules:
        print(f"\n❌ Missing dependencies: {', '.join(missing_modules)}")
        print("   Install with: pip install -r requirements.txt")
        return False
    
    print("   ✅ All dependencies available")
    return True

def check_model_files():
    """Check if required model files exist"""
    print("\n🔍 Checking model files...")
    
    required_files = [
        'STGCN_astana.pt',
        'data/astana/vel.csv',
        'data/astana/adj.npz'
    ]
    
    missing_files = []
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"   ✅ {file_path}")
        else:
            missing_files.append(file_path)
            print(f"   ❌ {file_path} - MISSING")
    
    if missing_files:
        print(f"\n❌ Missing model files: {', '.join(missing_files)}")
        print("   Please ensure the STGCN model is trained and data files exist")
        return False
    
    print("   ✅ All model files available")
    return True

def check_api_keys():
    """Check API key configuration"""
    print("\n🔍 Checking API configuration...")
    
    if TWOGIS_API_KEY:
        print("   ✅ 2GIS API key configured")
    else:
        print("   ⚠️  2GIS API key not set - will use mock data")
    
    if OPENAI_API_KEY:
        print("   ✅ OpenAI API key configured")
    else:
        print("   ⚠️  OpenAI API key not set - will use mock data")
    
    if not TWOGIS_API_KEY and not OPENAI_API_KEY:
        print("   ℹ️  No API keys set - system will run with mock data")
        print("   Run 'python setup_api_keys.py' to configure API keys")
    
    return True

def run_detection_pipeline():
    """Run the complete detection pipeline"""
    print("\n🚀 Starting Enhanced Hot Spot Detection Pipeline")
    print("-" * 60)
    
    # Initialize detector
    detector = HotSpotDetector(dataset_name='astana', grid_size=10)
    
    # Set API keys from config
    detector.set_api_keys(
        twogis_key=TWOGIS_API_KEY,
        openai_key=OPENAI_API_KEY
    )
    
    # Run detection
    start_time = time.time()
    success = detector.run_enhanced_detection()
    end_time = time.time()
    
    if success:
        print(f"\n✅ Pipeline completed successfully in {end_time - start_time:.2f} seconds")
        return True
    else:
        print(f"\n❌ Pipeline failed after {end_time - start_time:.2f} seconds")
        return False

def display_results():
    """Display generated results"""
    print("\n📁 Generated Files:")
    print("-" * 40)
    
    files_to_check = [
        ('current_hotspots.html', 'Current hot spots visualization'),
        ('predicted_hotspots_30min.html', '30-minute predictions'),
        ('current_tile_heatmap.csv', 'Current tile heat levels'),
        ('predicted_tile_heatmap_30min.csv', 'Predicted tile heat levels')
    ]
    
    for filename, description in files_to_check:
        if os.path.exists(filename):
            size = os.path.getsize(filename) / 1024  # KB
            print(f"   ✅ {filename} ({size:.1f} KB) - {description}")
        else:
            print(f"   ❌ {filename} - NOT FOUND")
    
    print("\n🌐 Open the HTML files in your browser to view visualizations")
    print("📊 Use the CSV files for further analysis or integration")

def main():
    """Main function"""
    print_banner()
    
    # Pre-flight checks
    if not check_dependencies():
        return False
    
    if not check_model_files():
        return False
    
    check_api_keys()
    
    # Run detection pipeline
    if not run_detection_pipeline():
        return False
    
    # Display results
    display_results()
    
    print("\n" + "=" * 80)
    print("🎯 ENHANCED HOT SPOT DETECTION COMPLETE!")
    print("=" * 80)
    print(f"🕐 Finished at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Process interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
