#!/usr/bin/env python3
"""
Test script to check if rate limiting fixes work
"""

import requests
import time
import json

def test_reddit_access():
    """Test Reddit JSON access with proper rate limiting"""
    print("🔍 Testing Reddit Access with Rate Limiting...")
    print("=" * 50)
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (compatible; YouthOpinionScraper/1.0; +http://example.com/bot)',
        'Accept': 'application/json',
    }
    
    # Test a few Reddit subreddits with proper delays
    subreddits = [
        'https://www.reddit.com/r/india/hot.json',
        'https://www.reddit.com/r/IndianTeenagers/hot.json',
        'https://www.reddit.com/r/IndianStudents/hot.json'
    ]
    
    successful_scrapes = 0
    
    for i, url in enumerate(subreddits):
        try:
            print(f"\n📡 Testing {url}...")
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                posts = data.get('data', {}).get('children', [])
                print(f"✅ Success! Found {len(posts)} posts")
                
                # Show sample post
                if posts:
                    sample_post = posts[0].get('data', {})
                    title = sample_post.get('title', 'No title')
                    print(f"   Sample: {title[:100]}...")
                
                successful_scrapes += 1
            else:
                print(f"❌ HTTP {response.status_code}: {response.reason}")
                
        except Exception as e:
            print(f"❌ Error: {e}")
        
        # Rate limiting delay
        if i < len(subreddits) - 1:  # Don't sleep after the last request
            print("⏳ Waiting 5 seconds to respect rate limits...")
            time.sleep(5)
    
    print(f"\n📊 Results: {successful_scrapes}/{len(subreddits)} subreddits scraped successfully")
    
    if successful_scrapes > 0:
        print("✅ Rate limiting is working! Reddit access is functional.")
    else:
        print("❌ All requests failed. May need to wait longer or check network.")

if __name__ == "__main__":
    test_reddit_access()
