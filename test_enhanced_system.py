#!/usr/bin/env python3
"""
Test script for Enhanced Hot Spot Detection System
Verifies that all components work correctly
"""

import os
import sys
import numpy as np
import pandas as pd

# Add current directory to path
sys.path.append('.')

def test_imports():
    """Test that all required modules can be imported"""
    print("🔍 Testing imports...")
    
    try:
        from enhanced_hotspot_detection import HotSpotDetector
        print("   ✅ HotSpotDetector imported successfully")
    except ImportError as e:
        print(f"   ❌ Failed to import HotSpotDetector: {e}")
        return False
    
    try:
        import torch
        print("   ✅ PyTorch imported successfully")
    except ImportError as e:
        print(f"   ❌ Failed to import PyTorch: {e}")
        return False
    
    try:
        import requests
        print("   ✅ Requests imported successfully")
    except ImportError as e:
        print(f"   ❌ Failed to import Requests: {e}")
        return False
    
    return True

def test_data_files():
    """Test that required data files exist"""
    print("\n🔍 Testing data files...")
    
    required_files = [
        'data/astana/vel.csv',
        'data/astana/adj.npz'
    ]
    
    all_exist = True
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"   ✅ {file_path} exists")
        else:
            print(f"   ❌ {file_path} missing")
            all_exist = False
    
    return all_exist

def test_model_file():
    """Test that the trained model exists"""
    print("\n🔍 Testing model file...")
    
    model_file = 'STGCN_astana.pt'
    if os.path.exists(model_file):
        print(f"   ✅ {model_file} exists")
        return True
    else:
        print(f"   ❌ {model_file} missing")
        print("   Run 'python main.py --dataset astana' to train the model")
        return False

def test_hotspot_detector():
    """Test HotSpotDetector initialization"""
    print("\n🔍 Testing HotSpotDetector...")
    
    try:
        from enhanced_hotspot_detection import HotSpotDetector
        
        detector = HotSpotDetector(dataset_name='astana', grid_size=10)
        print("   ✅ HotSpotDetector initialized successfully")
        
        # Test API key setting
        detector.set_api_keys(twogis_key="test_key", openai_key="test_key")
        print("   ✅ API keys set successfully")
        
        return True
    except Exception as e:
        print(f"   ❌ HotSpotDetector test failed: {e}")
        return False

def test_mock_data_generation():
    """Test mock data generation functions"""
    print("\n🔍 Testing mock data generation...")
    
    try:
        from enhanced_hotspot_detection import HotSpotDetector
        
        detector = HotSpotDetector(dataset_name='astana', grid_size=10)
        
        # Test hot spot detection with mock data
        mock_traffic = np.random.rand(100) * 50 + 20  # Random traffic data
        hotspots = detector.detect_current_hotspots(mock_traffic)
        print(f"   ✅ Hot spot detection: found {len(hotspots)} hotspots")
        
        # Test hot spot center calculation
        if hotspots:
            centers = detector.calculate_hotspot_centers(hotspots)
            print(f"   ✅ Hot spot centers: calculated {len(centers)} centers")
        
        # Test mock organization data
        if hotspots:
            centers = detector.calculate_hotspot_centers(hotspots)
            orgs = detector._generate_mock_organization_data(centers)
            print(f"   ✅ Mock organizations: generated {len(orgs)} location groups")
        
        # Test mock event data
        if hotspots:
            centers = detector.calculate_hotspot_centers(hotspots)
            events = detector._generate_mock_event_data(centers)
            print(f"   ✅ Mock events: generated {len(events)} event groups")
        
        return True
    except Exception as e:
        print(f"   ❌ Mock data generation test failed: {e}")
        return False

def test_tile_generation():
    """Test tile-based heat map generation"""
    print("\n🔍 Testing tile generation...")
    
    try:
        from enhanced_hotspot_detection import HotSpotDetector
        
        detector = HotSpotDetector(dataset_name='astana', grid_size=10)
        
        # Generate mock predictions
        mock_predictions = np.random.rand(12, 100) * 50 + 20
        
        # Test tile generation
        tiles = detector.generate_tile_heatmap(mock_predictions, timestep=0)
        print(f"   ✅ Tile generation: created {len(tiles)} tiles")
        
        # Verify tile structure
        if tiles:
            tile = tiles[0]
            required_keys = ['tile_id', 'grid_x', 'grid_y', 'lat_min', 'lat_max', 
                           'lon_min', 'lon_max', 'center_lat', 'center_lon', 
                           'heat_level', 'normalized_heat']
            
            missing_keys = [key for key in required_keys if key not in tile]
            if missing_keys:
                print(f"   ❌ Missing tile keys: {missing_keys}")
                return False
            else:
                print("   ✅ Tile structure is correct")
        
        return True
    except Exception as e:
        print(f"   ❌ Tile generation test failed: {e}")
        return False

def test_html_generation():
    """Test HTML visualization generation"""
    print("\n🔍 Testing HTML generation...")
    
    try:
        from enhanced_hotspot_detection import HotSpotDetector
        
        detector = HotSpotDetector(dataset_name='astana', grid_size=10)
        
        # Create mock data
        mock_hotspots = [{
            'grid_x': 5, 'grid_y': 5, 'latitude': 51.1694, 'longitude': 71.4491,
            'intensity': 0.8, 'traffic_level': 35.5
        }]
        
        mock_orgs = [{
            'hotspot_center': mock_hotspots[0],
            'organizations': [{
                'name': 'Test Restaurant', 'type': 'restaurant',
                'closing_time': 22, 'latitude': 51.1694, 'longitude': 71.4491
            }],
            'organization_count': 1
        }]
        
        mock_events = [{
            'hotspot_center': mock_hotspots[0],
            'event_info': 'Test Event: Concert at 8 PM',
            'has_events': True
        }]
        
        # Test HTML generation
        html_file = detector.create_html_visualization(
            mock_hotspots, mock_hotspots, mock_orgs, mock_events, 'test_output.html'
        )
        
        if os.path.exists(html_file):
            print(f"   ✅ HTML file generated: {html_file}")
            # Clean up test file
            os.remove(html_file)
            print("   ✅ Test HTML file cleaned up")
            return True
        else:
            print("   ❌ HTML file not created")
            return False
            
    except Exception as e:
        print(f"   ❌ HTML generation test failed: {e}")
        return False

def test_csv_generation():
    """Test CSV file generation"""
    print("\n🔍 Testing CSV generation...")
    
    try:
        from enhanced_hotspot_detection import HotSpotDetector
        
        detector = HotSpotDetector(dataset_name='astana', grid_size=10)
        
        # Create mock tiles
        mock_tiles = []
        for i in range(10):
            for j in range(10):
                mock_tiles.append({
                    'tile_id': f"{i:02d}_{j:02d}",
                    'grid_x': i, 'grid_y': j,
                    'lat_min': 51.1194 + i * 0.01,
                    'lat_max': 51.1294 + i * 0.01,
                    'lon_min': 71.3991 + j * 0.01,
                    'lon_max': 71.4091 + j * 0.01,
                    'center_lat': 51.1244 + i * 0.01,
                    'center_lon': 71.4041 + j * 0.01,
                    'heat_level': np.random.rand() * 50 + 20,
                    'normalized_heat': np.random.rand()
                })
        
        # Test CSV generation
        csv_file = detector.save_tile_csv(mock_tiles, 'test_tiles.csv')
        
        if os.path.exists(csv_file):
            print(f"   ✅ CSV file generated: {csv_file}")
            # Verify CSV content
            df = pd.read_csv(csv_file)
            if len(df) == 100:  # 10x10 grid
                print("   ✅ CSV content is correct")
                # Clean up test file
                os.remove(csv_file)
                print("   ✅ Test CSV file cleaned up")
                return True
            else:
                print(f"   ❌ CSV has wrong number of rows: {len(df)}")
                return False
        else:
            print("   ❌ CSV file not created")
            return False
            
    except Exception as e:
        print(f"   ❌ CSV generation test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Enhanced Hot Spot Detection System - Test Suite")
    print("=" * 60)
    
    tests = [
        ("Import Tests", test_imports),
        ("Data Files", test_data_files),
        ("Model File", test_model_file),
        ("HotSpotDetector", test_hotspot_detector),
        ("Mock Data Generation", test_mock_data_generation),
        ("Tile Generation", test_tile_generation),
        ("HTML Generation", test_html_generation),
        ("CSV Generation", test_csv_generation)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 Running {test_name}...")
        try:
            if test_func():
                print(f"   ✅ {test_name} PASSED")
                passed += 1
            else:
                print(f"   ❌ {test_name} FAILED")
        except Exception as e:
            print(f"   ❌ {test_name} ERROR: {e}")
    
    print("\n" + "=" * 60)
    print(f"📊 TEST RESULTS: {passed}/{total} tests passed")
    print("=" * 60)
    
    if passed == total:
        print("🎉 All tests passed! The system is ready to use.")
        print("\n🚀 Run 'python run_enhanced_detection.py' to start the system")
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
        print("\n🔧 Common fixes:")
        print("   - Install dependencies: pip install -r requirements.txt")
        print("   - Train the model: python main.py --dataset astana")
        print("   - Check data files in data/astana/ directory")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
