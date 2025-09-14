#!/usr/bin/env python3
"""
API Connectivity Test Script
Tests 2GIS and ChatGPT API connections and functionality
"""

import os
import sys
import requests
import json
from datetime import datetime

# Add current directory to path
sys.path.append('.')

def test_2gis_api():
    """Test 2GIS API connectivity and functionality"""
    print("🌐 Testing 2GIS API...")
    
    try:
        from config import TWOGIS_API_KEY
        
        if not TWOGIS_API_KEY:
            print("   ❌ 2GIS API key not found in .env file")
            return False
        
        print(f"   ✅ API key loaded: {TWOGIS_API_KEY[:8]}...")
        
        # Test API with Astana coordinates
        url = "https://catalog.api.2gis.com/3.0/items"
        params = {
            'key': TWOGIS_API_KEY,
            'point': '71.4491,51.1694',  # Astana center
            'radius': 1000,  # 1km radius
            'type': 'branch',
            'fields': 'items.point,items.name,items.type,items.schedule,items.rubrics',
            'limit': 5  # Limit to 5 results for testing
        }
        
        print("   🔍 Making API request...")
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            items = data.get('result', {}).get('items', [])
            
            print(f"   ✅ API request successful!")
            print(f"   📊 Found {len(items)} organizations")
            
            if items:
                print("   📋 Sample organizations:")
                for i, item in enumerate(items[:3]):  # Show first 3
                    name = item.get('name', 'Unknown')
                    org_type = item.get('type', 'Unknown')
                    print(f"      {i+1}. {name} ({org_type})")
            
            return True
        else:
            print(f"   ❌ API request failed with status {response.status_code}")
            print(f"   📄 Response: {response.text[:200]}...")
            return False
            
    except requests.exceptions.Timeout:
        print("   ❌ API request timed out")
        return False
    except requests.exceptions.ConnectionError:
        print("   ❌ Connection error - check internet connection")
        return False
    except Exception as e:
        print(f"   ❌ Error testing 2GIS API: {e}")
        return False

def test_openai_api():
    """Test OpenAI ChatGPT API connectivity and functionality"""
    print("\n🤖 Testing OpenAI ChatGPT API...")
    
    try:
        from config import OPENAI_API_KEY
        
        if not OPENAI_API_KEY:
            print("   ❌ OpenAI API key not found in .env file")
            return False
        
        print(f"   ✅ API key loaded: {OPENAI_API_KEY[:8]}...")
        
        # Test API with a simple request
        headers = {
            'Authorization': f'Bearer {OPENAI_API_KEY}',
            'Content-Type': 'application/json'
        }
        
        data = {
            'model': 'gpt-3.5-turbo',
            'messages': [
                {
                    'role': 'user', 
                    'content': 'Test message: Are there any events happening in Astana, Kazakhstan today? Please respond briefly.'
                }
            ],
            'max_tokens': 100
        }
        
        print("   🔍 Making API request...")
        response = requests.post(
            'https://api.openai.com/v1/chat/completions',
            headers=headers,
            json=data,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            message = result['choices'][0]['message']['content']
            
            print("   ✅ API request successful!")
            print(f"   📄 Response: {message[:100]}...")
            return True
        else:
            print(f"   ❌ API request failed with status {response.status_code}")
            print(f"   📄 Response: {response.text[:200]}...")
            return False
            
    except requests.exceptions.Timeout:
        print("   ❌ API request timed out")
        return False
    except requests.exceptions.ConnectionError:
        print("   ❌ Connection error - check internet connection")
        return False
    except Exception as e:
        print(f"   ❌ Error testing OpenAI API: {e}")
        return False

def test_enhanced_system_with_apis():
    """Test the enhanced system with real API calls"""
    print("\n🚀 Testing Enhanced System with Real APIs...")
    
    try:
        from enhanced_hotspot_detection import HotSpotDetector
        
        # Initialize detector
        detector = HotSpotDetector(dataset_name='astana', grid_size=10)
        
        # Set API keys from config
        from config import TWOGIS_API_KEY, OPENAI_API_KEY
        detector.set_api_keys(twogis_key=TWOGIS_API_KEY, openai_key=OPENAI_API_KEY)
        
        # Create mock hot spot centers for testing
        mock_centers = [{
            'center_latitude': 51.1694,
            'center_longitude': 71.4491,
            'center_x': 5,
            'center_y': 5,
            'intensity': 0.8,
            'traffic_level': 35.5,
            'hotspot_count': 1
        }]
        
        print("   🔍 Testing 2GIS integration...")
        organizations = detector.query_2gis_organizations(mock_centers)
        
        if organizations and organizations[0]['organization_count'] > 0:
            print(f"   ✅ 2GIS integration working - found {organizations[0]['organization_count']} organizations")
        else:
            print("   ⚠️  2GIS integration returned no organizations")
        
        print("   🔍 Testing ChatGPT integration...")
        events = detector.query_events_with_chatgpt(mock_centers)
        
        if events and events[0]['has_events']:
            print("   ✅ ChatGPT integration working - found event information")
        else:
            print("   ⚠️  ChatGPT integration found no events")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Error testing enhanced system: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_environment_loading():
    """Test environment variable loading"""
    print("🔧 Testing Environment Variable Loading...")
    
    try:
        from config import TWOGIS_API_KEY, OPENAI_API_KEY
        
        print(f"   📋 2GIS API Key: {'✅ Loaded' if TWOGIS_API_KEY else '❌ Not loaded'}")
        print(f"   📋 OpenAI API Key: {'✅ Loaded' if OPENAI_API_KEY else '❌ Not loaded'}")
        
        if TWOGIS_API_KEY:
            print(f"      Key: {TWOGIS_API_KEY[:8]}...{TWOGIS_API_KEY[-4:]}")
        if OPENAI_API_KEY:
            print(f"      Key: {OPENAI_API_KEY[:8]}...{OPENAI_API_KEY[-4:]}")
        
        return bool(TWOGIS_API_KEY and OPENAI_API_KEY)
        
    except Exception as e:
        print(f"   ❌ Error loading environment variables: {e}")
        return False

def main():
    """Run all API tests"""
    print("🧪 API Connectivity Test Suite")
    print("=" * 60)
    print(f"🕐 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    tests = [
        ("Environment Loading", test_environment_loading),
        ("2GIS API", test_2gis_api),
        ("OpenAI API", test_openai_api),
        ("Enhanced System Integration", test_enhanced_system_with_apis)
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
        print("🎉 All API tests passed! The system is ready to use with real APIs.")
        print("\n🚀 Run 'python run_enhanced_detection.py' to start the full system")
    else:
        print("⚠️  Some API tests failed. Please check the errors above.")
        print("\n🔧 Common fixes:")
        print("   - Check internet connection")
        print("   - Verify API keys in script/.env file")
        print("   - Check API key validity and permissions")
        print("   - Ensure sufficient API credits/quota")
    
    return passed == total

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Test suite error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
