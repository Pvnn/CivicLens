#!/usr/bin/env python3
"""
Test script to check if social media data is updating properly
"""

import requests
import json
from datetime import datetime

def test_social_media_updates():
    """Test all social media endpoints"""
    print("🔍 Testing Social Media Data Updates...")
    print("=" * 50)
    
    base_url = 'http://localhost:5000'
    
    try:
        # Test health endpoint
        print("\n1. Health Check:")
        response = requests.get(f'{base_url}/api/health')
        print(f"   Status: {response.status_code}")
        
        # Test social media status
        print("\n2. Social Media Status:")
        response = requests.get(f'{base_url}/api/social-media-status')
        if response.status_code == 200:
            status = response.json()
            print(f"   Reddit: {status.get('reddit', False)}")
            print(f"   Twitter: {status.get('twitter', False)}")
            print(f"   YouTube: {status.get('youtube', False)}")
            print(f"   Timestamp: {status.get('timestamp', 'N/A')}")
        
        # Test youth opinions
        print("\n3. Youth Opinions:")
        response = requests.get(f'{base_url}/api/youth-opinions')
        if response.status_code == 200:
            data = response.json()
            posts = data.get('data', {}).get('posts', [])
            print(f"   Total posts: {len(posts)}")
            if posts:
                print(f"   Sample post: {posts[0].get('content', 'No content')[:100]}...")
                print(f"   Platform: {posts[0].get('platform', 'Unknown')}")
                print(f"   Sentiment: {posts[0].get('sentiment', {}).get('overall', 'Unknown')}")
        
        # Test youth sentiment
        print("\n4. Youth Sentiment:")
        response = requests.get(f'{base_url}/api/youth-sentiment')
        if response.status_code == 200:
            data = response.json()
            sentiment = data.get('data', {})
            print(f"   Overall sentiment: {sentiment.get('overall_sentiment', 'Unknown')}")
            print(f"   Positive: {sentiment.get('positive_percentage', 0):.1f}%")
            print(f"   Negative: {sentiment.get('negative_percentage', 0):.1f}%")
            print(f"   Neutral: {sentiment.get('neutral_percentage', 0):.1f}%")
        
        # Test youth topics
        print("\n5. Youth Topics:")
        response = requests.get(f'{base_url}/api/youth-topics')
        if response.status_code == 200:
            data = response.json()
            topics = data.get('data', {}).get('topics', [])
            print(f"   Total topics: {len(topics)}")
            if topics:
                print(f"   Top 3 topics:")
                for i, topic in enumerate(topics[:3], 1):
                    print(f"     {i}. {topic.get('text', 'Unknown')} (Score: {topic.get('value', 0)})")
        
        # Test real gap analysis
        print("\n6. Real Gap Analysis:")
        response = requests.get(f'{base_url}/api/real-gap-analysis')
        if response.status_code == 200:
            data = response.json()
            print(f"   Success: {data.get('success', False)}")
            print(f"   Data points: {data.get('metadata', {}).get('data_points', 0)}")
            print(f"   Reliability: {data.get('metadata', {}).get('reliability_score', 0):.2f}")
            
            gap_data = data.get('data', [])
            print(f"   Total topics: {len(gap_data)}")
            if gap_data:
                print(f"   Top 3 gaps:")
                for i, item in enumerate(gap_data[:3], 1):
                    print(f"     {i}. {item.get('topic', 'Unknown')} (Gap: {item.get('gap_score', 0)})")
        
        print(f"\n✅ All tests completed at {datetime.now().strftime('%H:%M:%S')}")
        print("💡 Social media data is updating properly!")
        
    except Exception as e:
        print(f"❌ Error testing social media updates: {e}")
        print("💡 Make sure the backend server is running on localhost:5000")

if __name__ == "__main__":
    test_social_media_updates()
