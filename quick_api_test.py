#!/usr/bin/env python3
"""
Quick API Test - Simple test to verify API connectivity
"""

import os
import sys

def test_imports():
    """Test basic imports"""
    try:
        import requests
        print("✅ Requests module available")
        return True
    except ImportError:
        print("❌ Requests module not available")
        return False

def test_env_loading():
    """Test environment variable loading"""
    try:
        from dotenv import load_dotenv
        load_dotenv('script/.env')
        
        twogis_key = os.getenv('DGIS_API_KEY')
        openai_key = os.getenv('OPENAI_API_KEY')
        
        print(f"2GIS API Key: {'✅ Found' if twogis_key else '❌ Not found'}")
        print(f"OpenAI API Key: {'✅ Found' if openai_key else '❌ Not found'}")
        
        if twogis_key:
            print(f"   Key: {twogis_key[:8]}...{twogis_key[-4:]}")
        if openai_key:
            print(f"   Key: {openai_key[:8]}...{openai_key[-4:]}")
        
        return bool(twogis_key and openai_key)
    except Exception as e:
        print(f"❌ Error loading environment: {e}")
        return False

def test_2gis_simple():
    """Simple 2GIS API test"""
    try:
        import requests
        from dotenv import load_dotenv
        
        load_dotenv('script/.env')
        api_key = os.getenv('DGIS_API_KEY')
        
        if not api_key:
            print("❌ No 2GIS API key found")
            return False
        
        url = "https://catalog.api.2gis.com/3.0/items"
        params = {
            'key': api_key,
            'point': '71.4491,51.1694',  # Astana
            'radius': 1000,
            'limit': 1
        }
        
        print("🔍 Testing 2GIS API...")
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            print("✅ 2GIS API is working!")
            return True
        else:
            print(f"❌ 2GIS API error: {response.status_code}")
            print(f"Response: {response.text[:100]}...")
            return False
            
    except Exception as e:
        print(f"❌ 2GIS API test failed: {e}")
        return False

def test_openai_simple():
    """Simple OpenAI API test"""
    try:
        import requests
        from dotenv import load_dotenv
        
        load_dotenv('script/.env')
        api_key = os.getenv('OPENAI_API_KEY')
        
        if not api_key:
            print("❌ No OpenAI API key found")
            return False
        
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
        
        data = {
            'model': 'gpt-3.5-turbo',
            'messages': [{'role': 'user', 'content': 'Hello, this is a test.'}],
            'max_tokens': 10
        }
        
        print("🔍 Testing OpenAI API...")
        response = requests.post(
            'https://api.openai.com/v1/chat/completions',
            headers=headers,
            json=data,
            timeout=15
        )
        
        if response.status_code == 200:
            print("✅ OpenAI API is working!")
            return True
        else:
            print(f"❌ OpenAI API error: {response.status_code}")
            print(f"Response: {response.text[:100]}...")
            return False
            
    except Exception as e:
        print(f"❌ OpenAI API test failed: {e}")
        return False

def main():
    print("🧪 Quick API Test")
    print("=" * 40)
    
    tests = [
        ("Import Test", test_imports),
        ("Environment Loading", test_env_loading),
        ("2GIS API", test_2gis_simple),
        ("OpenAI API", test_openai_simple)
    ]
    
    passed = 0
    for name, test_func in tests:
        print(f"\n📋 {name}:")
        if test_func():
            passed += 1
        print()
    
    print("=" * 40)
    print(f"Results: {passed}/{len(tests)} tests passed")
    
    if passed == len(tests):
        print("🎉 All APIs are working correctly!")
    else:
        print("⚠️ Some APIs may have issues. Check the errors above.")

if __name__ == "__main__":
    main()
