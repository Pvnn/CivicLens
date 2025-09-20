from flask import Flask, jsonify
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup
import re
import time

def create_app():
    app = Flask(__name__)
    CORS(app) # This enables CORS for all routes

    def scrape_youth_topics():
        print("Scraping youth topics from Pew Research Center...")
        url = 'https://www.pewresearch.org/topics/'
        headers = {'User-Agent': 'Mozilla/5.0'}
        topics = []
        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            # Scrapes popular youth-related topics from Pew Research Center
            for item in soup.select('ul.is-style-no-bullets li a'):
                topic_text = item.get_text(strip=True)
                if topic_text and "youth" in topic_text.lower():
                    # Assign a hardcoded value for demo purposes
                    topics.append({"text": topic_text, "value": 25})
            print(f"Found {len(topics)} youth topics.")
        except requests.exceptions.RequestException as e:
            print(f"Error scraping youth topics: {e}")
        return topics

    def scrape_politician_topics():
        print("Scraping politician topics from Bloomberg Government...")
        url = 'https://about.bgov.com/insights/public-affairs-strategies/top-10-public-policy-issues/'
        headers = {'User-Agent': 'Mozilla/5.0'}
        topics = []
        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            for h3 in soup.find_all('h3', text=re.compile('Key areas of policy action')):
                ul_tag = h3.find_next_sibling('ul')
                if ul_tag:
                    for li in ul_tag.find_all('li'):
                        topic_text = li.get_text(strip=True).replace('`', '')
                        if topic_text:
                            topics.append({"text": topic_text, "value": 20})
            print(f"Found {len(topics)} politician topics.")
        except requests.exceptions.RequestException as e:
            print(f"Error scraping politician topics: {e}")
        return topics

    @app.route('/api/missing-topics', methods=['GET'])
    def get_missing_topics():
        youth_topics = scrape_youth_topics()
        politician_topics = scrape_politician_topics()
        
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

if __name__ == '__main__':
    app = create_app()
    app.run(port=5000, debug=True)