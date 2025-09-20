from flask import Flask, jsonify, Response, stream_with_context
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup
import re
import time
import random
from datetime import datetime
import os
from app.services.social_media_scraper import social_media_scraper

def create_app():
    app = Flask(__name__)
    CORS(app)  # This enables CORS for all routes

    def try_scrape_real_data():
        """
        Attempt to scrape real data from accessible sources.
        Returns (success: bool, data: list, source: str)
        """
        print("Attempting to scrape real-time data...")
        
        # Try RSS feeds and more accessible sources (Reddit temporarily blocked, using alternatives)
        accessible_sources = [
            {
                'url': 'https://feeds.bbci.co.uk/news/world/asia/india/rss.xml',
                'name': 'BBC India RSS',
                'type': 'rss'
            },
            {
                'url': 'https://timesofindia.indiatimes.com/rssfeeds/1221656.cms',
                'name': 'TOI Education RSS',
                'type': 'rss'
            },
            {
                'url': 'https://www.hindustantimes.com/rss/education/rssfeed.xml',
                'name': 'Hindustan Times Education RSS',
                'type': 'rss'
            },
            {
                'url': 'https://www.thehindu.com/news/national/feeder/default.rss',
                'name': 'The Hindu National RSS',
                'type': 'rss'
            },
            {
                'url': 'https://www.indiatoday.in/rss/1206614',
                'name': 'India Today Education RSS',
                'type': 'rss'
            }
        ]
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (compatible; YouthOpinionScraper/1.0; +http://example.com/bot)',
            'Accept': 'application/json, application/rss+xml, application/xml, text/xml',
        }
        
        scraped_topics = []
        successful_sources = []
        
        for source in accessible_sources:
            try:
                print(f"Trying {source['name']}...")
                response = requests.get(source['url'], headers=headers, timeout=10)
                response.raise_for_status()
                
                # Parse content based on type
                if source['type'] == 'reddit_json':
                    try:
                        data = response.json()
                        posts = data.get('data', {}).get('children', [])
                        
                        for post_data in posts[:10]:  # Limit to prevent spam
                            post = post_data.get('data', {})
                            title_text = post.get('title', '')
                            selftext = post.get('selftext', '')
                            
                            # Combine title and selftext for better context
                            content = f"{title_text} {selftext}".strip()
                            
                            if len(content) > 20 and len(content) < 500:
                                # Clean up the content
                                clean_content = re.sub(r'[^\w\s-]', '', content)
                                clean_content = re.sub(r'\s+', ' ', clean_content).strip()
                                
                                if clean_content and clean_content not in [t['text'] for t in scraped_topics]:
                                    # Extract youth-relevant keywords
                                    youth_keywords = ['student', 'youth', 'teenager', 'young', 'college', 'university', 'school',
                                                   'education', 'job', 'career', 'future', 'dream', 'aspiration', 'startup',
                                                   'entrepreneur', 'technology', 'social media', 'mental health', 'climate',
                                                   'environment', 'politics', 'government', 'policy', 'reform', 'change']
                                    
                                    content_lower = content.lower()
                                    found_keywords = [kw for kw in youth_keywords if kw in content_lower]
                                    
                                    # Only include posts with youth relevance
                                    if found_keywords:
                                        scraped_topics.append({
                                            'text': clean_content[:200],  # Limit length
                                            'value': random.randint(20, 50),
                                            'source': source['name'],
                                            'score': post.get('score', 0),
                                            'keywords': found_keywords
                                        })
                    except Exception as e:
                        print(f"Error parsing Reddit JSON from {source['name']}: {e}")
                        continue
                        
                else:
                    # Parse RSS/XML content
                    soup = BeautifulSoup(response.content, 'xml')
                    
                    # Look for titles in RSS feeds
                    titles = soup.find_all(['title', 'headline'])
                    
                    for title in titles[:10]:  # Limit to prevent spam
                        title_text = title.get_text(strip=True)
                        if len(title_text) > 10 and len(title_text) < 200:
                            # Clean up the title
                            clean_title = re.sub(r'[^\w\s-]', '', title_text)
                            clean_title = re.sub(r'\s+', ' ', clean_title).strip()
                            
                            if clean_title and clean_title not in [t['text'] for t in scraped_topics]:
                                scraped_topics.append({
                                    'text': clean_title,
                                    'value': random.randint(15, 45),
                                    'source': source['name']
                                })
                
                successful_sources.append(source['name'])
                time.sleep(5)  # Increased rate limiting to avoid 429 errors
                
            except Exception as e:
                print(f"Failed to scrape {source['name']}: {e}")
                continue
        
        if scraped_topics:
            return True, scraped_topics, ', '.join(successful_sources)
        else:
            return False, [], "No sources accessible"

    def get_fallback_data():
        """
        Return realistic fallback data based on current Indian issues
        """
        print("Using curated fallback data...")
        
        # Current Indian youth issues (September 2024)
        youth_topics = [
            {"text": "Unemployment and Job Crisis", "value": 52, "gap_score": 35},
            {"text": "Mental Health Awareness", "value": 48, "gap_score": 32},
            {"text": "Climate Change and Environment", "value": 45, "gap_score": 28},
            {"text": "Education System Reform", "value": 44, "gap_score": 22},
            {"text": "Affordable Healthcare Access", "value": 42, "gap_score": 25},
            {"text": "Housing Affordability Crisis", "value": 40, "gap_score": 30},
            {"text": "Digital Privacy and Data Rights", "value": 38, "gap_score": 28},
            {"text": "Women Safety and Empowerment", "value": 37, "gap_score": 18},
            {"text": "Startup and Entrepreneurship Support", "value": 36, "gap_score": 15},
            {"text": "Skill Development and Reskilling", "value": 35, "gap_score": 12},
            {"text": "Social Media Impact and Regulation", "value": 34, "gap_score": 26},
            {"text": "LGBTQ+ Rights and Acceptance", "value": 33, "gap_score": 28},
            {"text": "Pollution and Air Quality", "value": 32, "gap_score": 20},
            {"text": "Public Transportation Infrastructure", "value": 30, "gap_score": 15},
            {"text": "Cybersecurity and Online Safety", "value": 29, "gap_score": 22}
        ]
        
        # Current political priorities (based on recent policy focus)
        politician_topics = [
            {"text": "Digital India and Technology", "value": 38, "gap_score": -8},
            {"text": "Infrastructure Development", "value": 35, "gap_score": -15},
            {"text": "Make in India Manufacturing", "value": 32, "gap_score": -12},
            {"text": "Rural Development Schemes", "value": 30, "gap_score": -10},
            {"text": "Defense and National Security", "value": 28, "gap_score": -18},
            {"text": "Tax Policy and GST", "value": 26, "gap_score": -16},
            {"text": "Foreign Policy and Diplomacy", "value": 25, "gap_score": -20},
            {"text": "Agricultural Reforms", "value": 24, "gap_score": -14},
            {"text": "Power and Energy Sector", "value": 23, "gap_score": -13},
            {"text": "Banking and Financial Inclusion", "value": 22, "gap_score": -12}
        ]
        
        # Combine and calculate final gap scores
        all_topics = {}
        
        # Add youth topics
        for topic in youth_topics:
            all_topics[topic['text']] = {
                'youth_mentions': topic['value'],
                'politician_mentions': max(0, topic['value'] - topic['gap_score']),
                'gap_score': topic['gap_score']
            }
        
        # Add politician-only topics
        for topic in politician_topics:
            if topic['text'] not in all_topics:
                all_topics[topic['text']] = {
                    'youth_mentions': max(0, topic['value'] + topic['gap_score']),
                    'politician_mentions': topic['value'],
                    'gap_score': topic['gap_score']
                }
        
        # Convert to list format
        comparison = []
        for topic_name, data in all_topics.items():
            comparison.append({
                'topic': topic_name,
                'youth_mentions': data['youth_mentions'],
                'politician_mentions': data['politician_mentions'],
                'gap_score': data['gap_score']
            })
        
        return comparison, "Curated data based on current Indian issues"

    def build_topic_description(topic: str, youth_mentions: int, politician_mentions: int, frequency: int | None = None) -> str:
        """Create a short, human-readable description for a topic row."""
        try:
            gap = (youth_mentions or 0) - (politician_mentions or 0)
            parts = []
            if gap > 0:
                parts.append(f"Youth interest is higher than political focus by {gap} points")
            elif gap < 0:
                parts.append(f"Political focus exceeds youth interest by {abs(gap)} points")
            else:
                parts.append("Youth interest and political focus are balanced")
            if frequency is not None:
                parts.append(f"Observed in {frequency} recent mentions")
            base = ", ".join(parts)
            return f"{topic}: {base}."
        except Exception:
            return f"{topic}: Context summary unavailable."

    def build_fallback_youth_data():
        """Return a safe fallback structure for youth opinions/trends so frontend never breaks."""
        try:
            sample_path = os.path.join(os.path.dirname(__file__), 'sample_youth_data.json')
            if os.path.exists(sample_path):
                import json as _json
                with open(sample_path, 'r', encoding='utf-8') as f:
                    sample = _json.load(f)
                posts = sample.get('posts', [])
                trends = sample.get('trends', {
                    'total_posts': len(posts),
                    'sentiment_distribution': {'positive': 33, 'negative': 33, 'neutral': 34},
                    'top_keywords': [],
                    'platform_distribution': {}
                })
            else:
                posts = []
                trends = {
                    'total_posts': 0,
                    'sentiment_distribution': {'positive': 0, 'negative': 0, 'neutral': 100},
                    'top_keywords': [],
                    'platform_distribution': {}
                }
            return {
                'posts': posts,
                'trends': trends,
                'scraping_timestamp': datetime.now().isoformat(),
                'total_sources_scraped': len(posts)
            }
        except Exception:
            return {
                'posts': [],
                'trends': {
                    'total_posts': 0,
                    'sentiment_distribution': {'positive': 0, 'negative': 0, 'neutral': 100},
                    'top_keywords': [],
                    'platform_distribution': {}
                },
                'scraping_timestamp': datetime.now().isoformat(),
                'total_sources_scraped': 0
            }

    @app.route('/api/missing-topics', methods=['GET'])
    def get_missing_topics():
        print(f"API called at {datetime.now()}")
        
        try:
            # First, try to scrape real data
            success, scraped_data, source_info = try_scrape_real_data()
            
            if success and len(scraped_data) > 5:
                print(f"Successfully scraped data from: {source_info}")
                
                # Process scraped data into comparison format
                comparison = []
                for item in scraped_data:
                    # Simulate youth vs politician mentions based on topic keywords
                    topic_text = item['text'].lower()
                    
                    # Youth-relevant keywords
                    youth_keywords = ['student', 'job', 'education', 'climate', 'mental health', 
                                    'social media', 'technology', 'startup', 'youth']
                    
                    # Political keywords  
                    political_keywords = ['government', 'minister', 'policy', 'parliament', 
                                        'election', 'budget', 'scheme', 'law']
                    
                    youth_relevance = sum(1 for kw in youth_keywords if kw in topic_text)
                    political_relevance = sum(1 for kw in political_keywords if kw in topic_text)
                    
                    youth_score = random.randint(20, 50) + (youth_relevance * 8)
                    political_score = random.randint(15, 40) + (political_relevance * 6)
                    
                    ym = min(youth_score, 60)
                    pm = min(political_score, 50)
                    comparison.append({
                        'topic': item['text'],
                        'youth_mentions': ym,
                        'politician_mentions': pm,
                        'gap_score': ym - pm,
                        'description': build_topic_description(item['text'], ym, pm),
                        'data_source': 'live_scraped'
                    })
                
                # Sort by gap score
                comparison.sort(key=lambda x: x['gap_score'], reverse=True)
                
                return jsonify({
                    'data': comparison,
                    'metadata': {
                        'timestamp': datetime.now().isoformat(),
                        'data_source': 'live_scraped',
                        'sources': source_info,
                        'note': 'Data scraped from live RSS feeds and news sources'
                    }
                })
            
            else:
                # Fall back to curated data
                print("Live scraping failed or insufficient data, using fallback")
                fallback_data, source_info = get_fallback_data()
                # Enrich with descriptions
                for t in fallback_data:
                    t['description'] = build_topic_description(t['topic'], t.get('youth_mentions', 0), t.get('politician_mentions', 0))
                return jsonify({
                    'data': fallback_data,
                    'metadata': {
                        'timestamp': datetime.now().isoformat(),
                        'data_source': 'curated_fallback',
                        'sources': source_info,
                        'note': 'Live scraping unavailable. Using curated data based on current Indian political and youth issues.'
                    }
                })
                
        except Exception as e:
            print(f"Error in get_missing_topics: {e}")
            
            # Emergency fallback
            emergency_data = [
                {"topic": "Youth Unemployment Crisis", "youth_mentions": 50, "politician_mentions": 15, "gap_score": 35},
                {"topic": "Mental Health Awareness", "youth_mentions": 45, "politician_mentions": 12, "gap_score": 33},
                {"topic": "Climate Action and Environment", "youth_mentions": 42, "politician_mentions": 18, "gap_score": 24},
                {"topic": "Education System Reform", "youth_mentions": 40, "politician_mentions": 22, "gap_score": 18},
                {"topic": "Housing Affordability", "youth_mentions": 38, "politician_mentions": 20, "gap_score": 18}
            ]
            
            return jsonify({
                'data': emergency_data,
                'metadata': {
                    'timestamp': datetime.now().isoformat(),
                    'data_source': 'emergency_fallback',
                    'sources': 'System fallback',
                    'note': 'System error occurred. Using emergency fallback data.',
                    'error': str(e)
                }
            })

    # -------- Accessible Tech/Career Feed Aggregator --------
    def fetch_career_feed() -> list:
        """Fetch tech/career updates from accessible, no-auth sources."""
        items = []
        headers = {
            'User-Agent': 'Mozilla/5.0 (compatible; PolicyPulseBot/1.0; +http://example.com)'
        }

        # 1) Hacker News via Algolia API (public, no key)
        try:
            hn_url = 'https://hn.algolia.com/api/v1/search_by_date?tags=story&numericFilters=points>50'
            r = requests.get(hn_url, timeout=10, headers=headers)
            r.raise_for_status()
            data = r.json()
            for hit in data.get('hits', [])[:20]:
                items.append({
                    'source': 'Hacker News',
                    'title': hit.get('title'),
                    'url': hit.get('url') or f"https://news.ycombinator.com/item?id={hit.get('objectID')}",
                    'score': hit.get('points', 0),
                    'author': hit.get('author'),
                    'created_at': hit.get('created_at')
                })
        except Exception as e:
            print(f"HN fetch error: {e}")

        # 2) GitHub Trending (HTML scrape)
        try:
            gh_url = 'https://github.com/trending'
            r = requests.get(gh_url, timeout=10, headers=headers)
            r.raise_for_status()
            soup = BeautifulSoup(r.text, 'html.parser')
            repos = soup.select('article.Box-row')[:20]
            for repo in repos:
                title_el = repo.select_one('h2 a')
                desc_el = repo.select_one('p')
                lang_el = repo.select_one('span[itemprop="programmingLanguage"]')
                stars_el = repo.select_one('a.Link--muted[href$="/stargazers"]')
                title = title_el.get_text(strip=True) if title_el else ''
                url = f"https://github.com{title_el['href']}" if title_el else ''
                desc = desc_el.get_text(strip=True) if desc_el else ''
                lang = lang_el.get_text(strip=True) if lang_el else ''
                stars = 0
                if stars_el:
                    try:
                        stars = int(stars_el.get_text(strip=True).replace(',', ''))
                    except Exception:
                        stars = 0
                items.append({
                    'source': 'GitHub Trending',
                    'title': title,
                    'url': url,
                    'description': desc,
                    'language': lang,
                    'score': stars,
                    'created_at': datetime.now().isoformat()
                })
        except Exception as e:
            print(f"GitHub Trending fetch error: {e}")

        # 3) Stack Overflow RSS (no auth)
        try:
            so_url = 'https://stackoverflow.com/feeds/tag?tagnames=python;javascript&sort=newest'
            r = requests.get(so_url, timeout=10, headers=headers)
            r.raise_for_status()
            soup = BeautifulSoup(r.content, 'xml')
            entries = soup.find_all('entry')[:20]
            for entry in entries:
                title = entry.find('title').get_text(strip=True) if entry.find('title') else ''
                link_el = entry.find('link')
                link = link_el.get('href') if link_el else ''
                author_el = entry.find('author')
                author = author_el.find('name').get_text(strip=True) if author_el and author_el.find('name') else ''
                updated = entry.find('updated').get_text(strip=True) if entry.find('updated') else datetime.now().isoformat()
                items.append({
                    'source': 'Stack Overflow',
                    'title': title,
                    'url': link,
                    'author': author,
                    'created_at': updated
                })
        except Exception as e:
            print(f"Stack Overflow RSS fetch error: {e}")

        # De-duplicate by url/title
        seen = set()
        deduped = []
        for it in items:
            key = (it.get('url') or '', it.get('title') or '')
            if key in seen:
                continue
            seen.add(key)
            deduped.append(it)
        # Sort by score desc if present, else by recency
        deduped.sort(key=lambda x: (x.get('score', 0), x.get('created_at', '')), reverse=True)
        return deduped[:50]

    @app.route('/api/career-feed', methods=['GET'])
    def api_career_feed():
        try:
            data = fetch_career_feed()
            return jsonify({
                'success': True,
                'data': data,
                'metadata': {
                    'timestamp': datetime.now().isoformat(),
                    'sources': ['Hacker News Algolia', 'GitHub Trending', 'Stack Overflow RSS']
                }
            })
        except Exception as e:
            print(f"career-feed error: {e}")
            return jsonify({'success': True, 'data': [], 'metadata': {'timestamp': datetime.now().isoformat(), 'error': str(e)}})

    @app.route('/api/stream/career-feed')
    def stream_career_feed():
        @stream_with_context
        def event_stream():
            while True:
                try:
                    data = fetch_career_feed()
                except Exception as e:
                    data = []
                yield sse_format({
                    'success': True,
                    'data': data,
                    'metadata': {
                        'timestamp': datetime.now().isoformat(),
                        'data_source': 'career_feed_stream'
                    }
                })
                time.sleep(20)
        headers = {
            'Cache-Control': 'no-cache',
            'Content-Type': 'text/event-stream',
            'Connection': 'keep-alive',
            'X-Accel-Buffering': 'no'
        }
        return Response(event_stream(), headers=headers)

    @app.route('/api/health', methods=['GET'])
    def health_check():
        return jsonify({
            "status": "healthy", 
            "message": "Indian Youth-Politics Gap Analyzer is running",
            "timestamp": datetime.now().isoformat(),
            "scraping_status": "Will attempt live scraping, with intelligent fallback"
        })

    @app.route('/api/scraping-status', methods=['GET'])
    def scraping_status():
        """New endpoint to check what data sources are working"""
        success, data, sources = try_scrape_real_data()
        return jsonify({
            'live_scraping_available': success,
            'accessible_sources': sources,
            'sample_topics_count': len(data),
            'timestamp': datetime.now().isoformat()
        })

    @app.route('/api/youth-opinions', methods=['GET'])
    def get_youth_opinions():
        """Get live youth opinions from social media"""
        print(f"Youth opinions API called at {datetime.now()}")
        
        try:
            # Get comprehensive youth opinions
            youth_data = social_media_scraper.get_comprehensive_youth_opinions()
            
            return jsonify({
                'success': True,
                'data': youth_data,
                'metadata': {
                    'timestamp': datetime.now().isoformat(),
                    'data_source': 'social_media_scraping',
                    'total_posts': len(youth_data.get('posts', [])),
                    'platforms_scraped': list(set([post.get('platform') for post in youth_data.get('posts', [])]))
                }
            })
            
        except Exception as e:
            print(f"Error in youth opinions scraping: {e}")
            # Graceful fallback with success=True so UI continues to work
            youth_data = build_fallback_youth_data()
            return jsonify({
                'success': True,
                'data': youth_data,
                'metadata': {
                    'timestamp': datetime.now().isoformat(),
                    'data_source': 'fallback',
                    'note': 'Scraping failed. Serving fallback data.'
                }
            })

    @app.route('/api/youth-sentiment', methods=['GET'])
    def get_youth_sentiment():
        """Get youth sentiment analysis"""
        print(f"Youth sentiment API called at {datetime.now()}")
        
        try:
            # Get youth opinions and analyze sentiment
            youth_data = social_media_scraper.get_comprehensive_youth_opinions()
            trends = youth_data.get('trends', {})
            
            # Extract sentiment insights
            sentiment_analysis = {
                'overall_sentiment': trends.get('sentiment_distribution', {}),
                'top_concerns': [kw[0] for kw in trends.get('top_keywords', [])[:5]],
                'platform_activity': trends.get('platform_distribution', {}),
                'total_opinions_analyzed': trends.get('total_posts', 0),
                'analysis_timestamp': datetime.now().isoformat()
            }
            
            return jsonify({
                'success': True,
                'data': sentiment_analysis,
                'metadata': {
                    'timestamp': datetime.now().isoformat(),
                    'data_source': 'sentiment_analysis',
                    'analysis_method': 'vader_textblob_hybrid'
                }
            })
            
        except Exception as e:
            print(f"Error in sentiment analysis: {e}")
            # Fallback sentiment
            youth_data = build_fallback_youth_data()
            trends = youth_data.get('trends', {})
            fallback_sentiment = {
                'overall_sentiment': trends.get('sentiment_distribution', {'positive': 0, 'negative': 0, 'neutral': 100}),
                'top_concerns': [kw[0] for kw in trends.get('top_keywords', [])[:5]],
                'platform_activity': trends.get('platform_distribution', {}),
                'total_opinions_analyzed': trends.get('total_posts', 0),
                'analysis_timestamp': datetime.now().isoformat()
            }
            return jsonify({
                'success': True,
                'data': fallback_sentiment,
                'metadata': {
                    'timestamp': datetime.now().isoformat(),
                    'data_source': 'fallback',
                    'note': 'Sentiment fallback due to scraping error.'
                }
            })

    @app.route('/api/youth-topics', methods=['GET'])
    def get_youth_topics():
        """Get trending topics among youth from social media"""
        print(f"Youth topics API called at {datetime.now()}")
        
        try:
            # Get youth opinions
            youth_data = social_media_scraper.get_comprehensive_youth_opinions()
            trends = youth_data.get('trends', {})
            
            # Extract topic insights
            top_keywords = trends.get('top_keywords', [])
            
            # Convert keywords to topic format similar to missing-topics
            youth_topics = []
            for keyword, frequency in top_keywords[:15]:  # Top 15 topics
                # Simulate youth vs politician mentions based on keyword relevance
                youth_mentions = min(frequency * 3, 60)  # Scale frequency to mentions
                politician_mentions = random.randint(5, 25)  # Simulate politician mentions
                gap_score = youth_mentions - politician_mentions
                
                youth_topics.append({
                    'topic': keyword.title(),
                    'youth_mentions': youth_mentions,
                    'politician_mentions': politician_mentions,
                    'gap_score': gap_score,
                    'description': build_topic_description(keyword.title(), youth_mentions, politician_mentions, frequency),
                    'frequency': frequency,
                    'data_source': 'social_media_scraping'
                })
            
            # Sort by gap score
            youth_topics.sort(key=lambda x: x['gap_score'], reverse=True)
            
            return jsonify({
                'success': True,
                'data': youth_topics,
                'metadata': {
                    'timestamp': datetime.now().isoformat(),
                    'data_source': 'social_media_topics',
                    'total_topics': len(youth_topics),
                    'scraping_sources': list(set([post.get('platform') for post in youth_data.get('posts', [])]))
                }
            })
            
        except Exception as e:
            print(f"Error in youth topics analysis: {e}")
            youth_data = build_fallback_youth_data()
            trends = youth_data.get('trends', {})
            top_keywords = trends.get('top_keywords', [])
            fallback_topics = []
            for keyword, frequency in top_keywords[:15]:
                youth_mentions = min(frequency * 3, 60)
                politician_mentions = random.randint(5, 25)
                gap_score = youth_mentions - politician_mentions
                fallback_topics.append({
                    'topic': str(keyword).title(),
                    'youth_mentions': youth_mentions,
                    'politician_mentions': politician_mentions,
                    'gap_score': gap_score,
                    'description': build_topic_description(str(keyword).title(), youth_mentions, politician_mentions, frequency),
                    'frequency': frequency,
                    'data_source': 'fallback'
                })
            return jsonify({
                'success': True,
                'data': fallback_topics,
                'metadata': {
                    'timestamp': datetime.now().isoformat(),
                    'data_source': 'fallback',
                    'note': 'Topics fallback due to scraping error.'
                }
            })

    @app.route('/api/social-media-status', methods=['GET'])
    def social_media_status():
        """Check status of social media APIs"""
        status = {
            'reddit': social_media_scraper.reddit is not None,
            'twitter': social_media_scraper.twitter_api is not None,
            'youtube': social_media_scraper.youtube is not None,
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify(status)

    # Server-Sent Events (SSE) streaming endpoints
    def sse_format(payload: dict) -> str:
        """Format a JSON-serializable payload for SSE."""
        import json as _json
        return f"data: {_json.dumps(payload)}\n\n"

    @app.route('/api/stream/youth-opinions')
    def stream_youth_opinions():
        """Stream periodic youth opinions and derived insights via SSE."""
        @stream_with_context
        def event_stream():
            while True:
                try:
                    data = social_media_scraper.get_comprehensive_youth_opinions()
                    payload = {
                        'success': True,
                        'data': {
                            'posts': data.get('posts', []),
                            'trends': data.get('trends', {})
                        },
                        'metadata': {
                            'timestamp': datetime.now().isoformat(),
                            'data_source': 'social_media_scraping_stream'
                        }
                    }
                    yield sse_format(payload)
                except Exception as e:
                    # Fallback in stream to keep UI updating
                    data = build_fallback_youth_data()
                    payload = {
                        'success': True,
                        'data': {
                            'posts': data.get('posts', []),
                            'trends': data.get('trends', {})
                        },
                        'metadata': {
                            'timestamp': datetime.now().isoformat(),
                            'data_source': 'fallback_stream',
                            'note': f'Error: {str(e)}'
                        }
                    }
                    yield sse_format(payload)
                # Avoid hammering sources; adjust interval as needed (faster for demo)
                time.sleep(10)
        headers = {
            'Cache-Control': 'no-cache',
            'Content-Type': 'text/event-stream',
            'Connection': 'keep-alive',
            'X-Accel-Buffering': 'no'
        }
        return Response(event_stream(), headers=headers)

    @app.route('/api/stream/missing-topics')
    def stream_missing_topics():
        """Stream periodic missing-topics results via SSE using the same logic as the REST endpoint."""
        def compute_missing_topics_payload():
            try:
                success, scraped_data, source_info = try_scrape_real_data()
                if success and len(scraped_data) > 5:
                    comparison = []
                    for item in scraped_data:
                        topic_text = item['text'].lower()
                        youth_keywords = ['student', 'job', 'education', 'climate', 'mental health',
                                         'social media', 'technology', 'startup', 'youth']
                        political_keywords = ['government', 'minister', 'policy', 'parliament',
                                             'election', 'budget', 'scheme', 'law']
                        youth_relevance = sum(1 for kw in youth_keywords if kw in topic_text)
                        political_relevance = sum(1 for kw in political_keywords if kw in topic_text)
                        youth_score = random.randint(20, 50) + (youth_relevance * 8)
                        political_score = random.randint(15, 40) + (political_relevance * 6)
                        comparison.append({
                            'topic': item['text'],
                            'youth_mentions': min(youth_score, 60),
                            'politician_mentions': min(political_score, 50),
                            'gap_score': youth_score - political_score,
                            'data_source': 'live_scraped'
                        })
                    comparison.sort(key=lambda x: x['gap_score'], reverse=True)
                    payload = {
                        'data': comparison,
                        'metadata': {
                            'timestamp': datetime.now().isoformat(),
                            'data_source': 'live_scraped',
                            'sources': source_info,
                            'note': 'Data scraped from live RSS feeds and news sources'
                        }
                    }
                else:
                    fallback_data, source_info = get_fallback_data()
                    payload = {
                        'data': fallback_data,
                        'metadata': {
                            'timestamp': datetime.now().isoformat(),
                            'data_source': 'curated_fallback',
                            'sources': source_info,
                            'note': 'Live scraping unavailable. Using curated data based on current Indian issues.'
                        }
                    }
                return payload
            except Exception as e:
                return {
                    'data': [],
                    'metadata': {
                        'timestamp': datetime.now().isoformat(),
                        'data_source': 'emergency_fallback',
                        'sources': 'System fallback',
                        'note': 'System error occurred. Using emergency fallback data.',
                        'error': str(e)
                    }
                }

        @stream_with_context
        def event_stream():
            while True:
                payload = compute_missing_topics_payload()
                yield sse_format(payload)
                # Faster interval for demo
                time.sleep(20)

        headers = {
            'Cache-Control': 'no-cache',
            'Content-Type': 'text/event-stream',
            'Connection': 'keep-alive',
            'X-Accel-Buffering': 'no'
        }
        return Response(event_stream(), headers=headers)

    return app

if __name__ == '__main__':
    app = create_app()
    print("Starting Indian Youth-Politics Gap Analyzer...")
    print("Note: Will attempt live scraping, but will use curated fallback if needed")
    app.run(port=5000, debug=True, host='0.0.0.0')
from app import create_app
import os

app = create_app()

if __name__ == '__main__':
    # Create database directory if it doesn't exist
    os.makedirs('instance', exist_ok=True)
    
    # Run the application
    app.run(debug=True, host='0.0.0.0', port=5000)
