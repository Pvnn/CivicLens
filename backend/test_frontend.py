#!/usr/bin/env python3
"""
Test if frontend is running
"""

import requests
import time

def test_frontend():
    """Test if frontend is accessible"""
    print("🔍 Testing Frontend...")
    
    try:
        time.sleep(3)
        response = requests.get('http://localhost:3000')
        print(f"Frontend status: {response.status_code}")
        print("✅ Frontend is running!")
        return True
    except Exception as e:
        print(f"❌ Frontend not accessible: {e}")
        return False

if __name__ == "__main__":
    test_frontend()
