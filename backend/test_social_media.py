#!/usr/bin/env python3
"""
Test script for social media scraping functionality
Run this to test the social media scraper without the full Flask app
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.social_media_scraper import social_media_scraper
import json
from datetime import datetime

def test_social_media_scraper():
    """Test the social media scraper functionality"""
    print("🔍 Testing Social Media Scraper...")
    print("=" * 50)
    
    # Test API status
    print("\n📊 API Status:")
    print(f"Reddit API: {'✅ Available' if social_media_scraper.reddit else '❌ Not configured'}")
    print(f"Twitter API: {'✅ Available' if social_media_scraper.twitter_api else '❌ Not configured'}")
    print(f"YouTube API: {'✅ Available' if social_media_scraper.youtube else '❌ Not configured'}")
    
    # Test sentiment analysis
    print("\n🧠 Testing Sentiment Analysis:")
    test_texts = [
        "I love this new education policy! It's amazing!",
        "This is terrible, the government doesn't care about students",
        "The weather is okay today, nothing special"
    ]
    
    for text in test_texts:
        sentiment = social_media_scraper.analyze_sentiment(text)
        print(f"Text: '{text}'")
        print(f"Sentiment: {sentiment['overall']} (confidence: {sentiment['confidence']:.2f})")
        print()
    
    # Test keyword extraction
    print("\n🔑 Testing Keyword Extraction:")
    test_content = "I'm a student studying computer science at university. I'm interested in technology, startups, and climate change. The government should focus more on education and mental health."
    keywords = social_media_scraper.extract_youth_keywords(test_content)
    print(f"Content: '{test_content}'")
    print(f"Youth Keywords: {keywords}")
    print()
    
    # Test comprehensive scraping (if APIs are available)
    print("\n🌐 Testing Comprehensive Scraping:")
    try:
        youth_data = social_media_scraper.get_comprehensive_youth_opinions()
        
        print(f"Total posts scraped: {len(youth_data.get('posts', []))}")
        print(f"Platforms: {list(set([post.get('platform') for post in youth_data.get('posts', [])]))}")
        
        if youth_data.get('trends'):
            trends = youth_data['trends']
            print(f"Sentiment distribution: {trends.get('sentiment_distribution', {})}")
            print(f"Top keywords: {trends.get('top_keywords', [])[:5]}")
        
        # Save sample data
        with open('sample_youth_data.json', 'w') as f:
            json.dump(youth_data, f, indent=2, default=str)
        print("📁 Sample data saved to 'sample_youth_data.json'")
        
    except Exception as e:
        print(f"❌ Scraping failed: {e}")
        print("💡 This is normal if API keys are not configured")
    
    print("\n✅ Test completed!")
    print("\n💡 To enable full functionality:")
    print("1. Set up API keys in your environment or .env file")
    print("2. See SOCIAL_MEDIA_SETUP.md for detailed instructions")

if __name__ == "__main__":
    test_social_media_scraper()
