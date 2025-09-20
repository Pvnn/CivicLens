#!/usr/bin/env python3
"""
Test script to check descriptive topic names from API
"""

import requests
import json

def test_api_topics():
    """Test the API endpoint for descriptive topic names"""
    print("🔍 Testing API for Descriptive Topic Names...")
    print("=" * 60)
    
    try:
        # Test the real gap analysis API
        response = requests.get('http://localhost:5000/api/real-gap-analysis')
        
        if response.status_code == 200:
            data = response.json()
            
            print(f"\n📊 API Response:")
            print(f"Success: {data['success']}")
            print(f"Data points: {data['metadata']['data_points']}")
            print(f"Reliability score: {data['metadata']['reliability_score']:.2f}")
            print(f"Methodology: {data['metadata']['methodology']}")
            
            print(f"\n🎯 Top 10 Topics with Descriptive Names:")
            for i, item in enumerate(data['data'][:10], 1):
                print(f"{i:2d}. {item['topic']:40s} | "
                      f"Gap: {item['gap_score']:6.1f} | "
                      f"Youth: {item['youth_mentions']:4.1f} | "
                      f"Political: {item['politician_mentions']:4.1f} | "
                      f"Reliability: {item['reliability']*100:4.0f}%")
            
            print(f"\n✅ API test completed successfully!")
            print(f"💡 Topics now have descriptive names instead of generic keywords!")
            
        else:
            print(f"❌ API Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error testing API: {e}")
        print("💡 Make sure the backend server is running on localhost:5000")

if __name__ == "__main__":
    test_api_topics()
