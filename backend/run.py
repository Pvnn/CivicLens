from flask import Flask, jsonify
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup
import re

def create_app():
    app = Flask(__name__)
    CORS(app) # This enables CORS for all routes

    def scrape_youth_topics():
        # Using a placeholder URL for the hackathon
        url = 'https://www.example-youth-forum.com'
        headers = {'User-Agent': 'Mozilla/5.0'}
        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status() # Raise an exception for bad status codes
            
            topics = []
            soup = BeautifulSoup(response.content, 'html.parser')
            # Example logic to find and count topics (you will need to adapt this)
            for item in soup.find_all('div', class_='topic-tag'):
                topic = item.get_text(strip=True)
                if topic:
                    # For a simple demo, we can just create mock data
                    topics.append({"topic": topic, "value": 1})
            
            # Since we are using mock data, let's just return a static list for the demo
            return [
                {"text": "Climate", "value": 30},
                {"text": "Jobs", "value": 25},
                {"text": "Transport", "value": 20},
                {"text": "Education", "value": 18},
                {"text": "Mental Health", "value": 15},
            ]
        except requests.exceptions.RequestException as e:
            print(f"Error scraping youth topics: {e}")
            return []

    def scrape_politician_topics():
        # Using a placeholder URL for the hackathon
        url = 'https://www.example-news-site.com/politics'
        headers = {'User-Agent': 'Mozilla/5.0'}
        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            topics = {}
            text = response.get_text()
            keywords = ["economy", "defense", "jobs", "infrastructure"]
            for keyword in keywords:
                count = len(re.findall(f'\\b{keyword}\\b', text, re.IGNORECASE))
                topics[keyword] = count
                
            # Returning mock data for the demo
            return [
                {"text": "Economy", "value": 20},
                {"text": "Jobs", "value": 20},
                {"text": "Defense", "value": 20},
                {"text": "Infrastructure", "value": 20},
            ]
        except requests.exceptions.RequestException as e:
            print(f"Error scraping politician topics: {e}")
            return []

    @app.route('/api/missing-topics', methods=['GET'])
    def get_missing_topics():
        youth_topics = scrape_youth_topics()
        politician_topics = scrape_politician_topics()
        
        # Merge the two lists to get a combined set of all topics
        all_topics = {topic['text'] for topic in youth_topics} | {topic['text'] for topic in politician_topics}
        
        comparison = []
        for topic in all_topics:
            youth_value = next((item['value'] for item in youth_topics if item['text'] == topic), 0)
            politician_value = next((item['value'] for item in politician_topics if item['text'] == topic), 0)
            comparison.append({
                "topic": topic,
                "youth_mentions": youth_value,
                "politician_mentions": politician_value
            })

        return jsonify(comparison)

    return app

# The main entry point for the application
if __name__ == '__main__':
    app = create_app()
    app.run(port=5000, debug=True)