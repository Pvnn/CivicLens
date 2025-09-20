import os
import time
import json
import re
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import requests
from bs4 import BeautifulSoup
from textblob import TextBlob
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import praw
try:
    import tweepy
    TWITTER_AVAILABLE = True
except ImportError:
    TWITTER_AVAILABLE = False
    print("Twitter API not available - tweepy import failed")

try:
    from googleapiclient.discovery import build
    YOUTUBE_AVAILABLE = True
except ImportError:
    YOUTUBE_AVAILABLE = False
    print("YouTube API not available - googleapiclient import failed")

from .additional_social_sources import additional_social_sources
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SocialMediaScraper:
    """
    Comprehensive social media scraper for youth opinions
    Supports Reddit, Twitter/X, YouTube, and general web scraping
    """
    
    def __init__(self):
        self.sentiment_analyzer = SentimentIntensityAnalyzer()
        self.setup_apis()
        
    def setup_apis(self):
        """Initialize API clients for various platforms"""
        try:
            # Reddit API (using environment variables or defaults)
            self.reddit = praw.Reddit(
                client_id=os.getenv('REDDIT_CLIENT_ID', 'your_client_id'),
                client_secret=os.getenv('REDDIT_CLIENT_SECRET', 'your_client_secret'),
                user_agent=os.getenv('REDDIT_USER_AGENT', 'YouthOpinionScraper/1.0')
            )
            logger.info("Reddit API initialized")
        except Exception as e:
            logger.warning(f"Reddit API not available: {e}")
            self.reddit = None
            
        try:
            if TWITTER_AVAILABLE:
                # Twitter API
                self.twitter_api = tweepy.Client(
                    bearer_token=os.getenv('TWITTER_BEARER_TOKEN', 'your_bearer_token'),
                    consumer_key=os.getenv('TWITTER_CONSUMER_KEY', 'your_consumer_key'),
                    consumer_secret=os.getenv('TWITTER_CONSUMER_SECRET', 'your_consumer_secret'),
                    access_token=os.getenv('TWITTER_ACCESS_TOKEN', 'your_access_token'),
                    access_token_secret=os.getenv('TWITTER_ACCESS_SECRET', 'your_access_secret')
                )
                logger.info("Twitter API initialized")
            else:
                self.twitter_api = None
        except Exception as e:
            logger.warning(f"Twitter API not available: {e}")
            self.twitter_api = None
            
        try:
            if YOUTUBE_AVAILABLE:
                # YouTube API
                self.youtube = build('youtube', 'v3', developerKey=os.getenv('YOUTUBE_API_KEY', 'your_api_key'))
                logger.info("YouTube API initialized")
            else:
                self.youtube = None
        except Exception as e:
            logger.warning(f"YouTube API not available: {e}")
            self.youtube = None

    def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """Analyze sentiment of text using multiple methods"""
        try:
            # VADER sentiment
            vader_scores = self.sentiment_analyzer.polarity_scores(text)
            
            # TextBlob sentiment
            blob = TextBlob(text)
            textblob_polarity = blob.sentiment.polarity
            textblob_subjectivity = blob.sentiment.subjectivity
            
            # Determine overall sentiment
            if vader_scores['compound'] >= 0.05:
                overall_sentiment = 'positive'
            elif vader_scores['compound'] <= -0.05:
                overall_sentiment = 'negative'
            else:
                overall_sentiment = 'neutral'
                
            return {
                'overall': overall_sentiment,
                'vader': vader_scores,
                'textblob': {
                    'polarity': textblob_polarity,
                    'subjectivity': textblob_subjectivity
                },
                'confidence': abs(vader_scores['compound'])
            }
        except Exception as e:
            logger.error(f"Sentiment analysis error: {e}")
            return {
                'overall': 'neutral',
                'vader': {'compound': 0, 'pos': 0, 'neu': 1, 'neg': 0},
                'textblob': {'polarity': 0, 'subjectivity': 0},
                'confidence': 0
            }

    def scrape_reddit_youth_opinions(self, subreddits: List[str] = None, limit: int = 50) -> List[Dict[str, Any]]:
        """Scrape youth opinions from Reddit"""
        if not self.reddit:
            logger.warning("Reddit API not available")
            return []
            
        if not subreddits:
            subreddits = [
                'india', 'IndianTeenagers', 'IndianStudents', 'developersIndia',
                'IndianAcademia', 'IndianStreetBets', 'IndianGaming',
                'Mumbai', 'Delhi', 'Bangalore', 'Chennai', 'Hyderabad'
            ]
        
        youth_posts = []
        
        try:
            for subreddit_name in subreddits:
                try:
                    subreddit = self.reddit.subreddit(subreddit_name)
                    
                    # Get hot posts
                    for post in subreddit.hot(limit=limit//len(subreddits)):
                        if post.selftext or post.title:
                            content = f"{post.title} {post.selftext}".strip()
                            
                            # Analyze sentiment
                            sentiment = self.analyze_sentiment(content)
                            
                            # Extract youth-relevant keywords
                            youth_keywords = self.extract_youth_keywords(content)
                            
                            if youth_keywords:  # Only include posts with youth relevance
                                youth_posts.append({
                                    'platform': 'reddit',
                                    'subreddit': subreddit_name,
                                    'title': post.title,
                                    'content': content[:500],  # Limit content length
                                    'author': str(post.author) if post.author else 'deleted',
                                    'score': post.score,
                                    'comments_count': post.num_comments,
                                    'created_utc': datetime.fromtimestamp(post.created_utc),
                                    'url': f"https://reddit.com{post.permalink}",
                                    'sentiment': sentiment,
                                    'youth_keywords': youth_keywords,
                                    'relevance_score': len(youth_keywords) * post.score / 100
                                })
                                
                except Exception as e:
                    logger.error(f"Error scraping subreddit {subreddit_name}: {e}")
                    continue
                    
                time.sleep(1)  # Rate limiting
                
        except Exception as e:
            logger.error(f"Reddit scraping error: {e}")
            
        return youth_posts

    def scrape_twitter_youth_opinions(self, hashtags: List[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
        """Scrape youth opinions from Twitter/X"""
        if not self.twitter_api:
            logger.warning("Twitter API not available")
            return []
            
        if not hashtags:
            hashtags = [
                '#IndianYouth', '#StudentLife', '#IndianStudents', '#YouthVoice',
                '#IndianTeenagers', '#CampusLife', '#IndianEducation', '#YouthPolitics',
                '#IndianStartups', '#TechIndia', '#ClimateAction', '#MentalHealth'
            ]
        
        youth_tweets = []
        
        try:
            for hashtag in hashtags:
                try:
                    tweets = self.twitter_api.search_recent_tweets(
                        query=hashtag,
                        max_results=min(limit//len(hashtags), 100),
                        tweet_fields=['created_at', 'public_metrics', 'author_id', 'context_annotations']
                    )
                    
                    if tweets.data:
                        for tweet in tweets.data:
                            content = tweet.text
                            sentiment = self.analyze_sentiment(content)
                            youth_keywords = self.extract_youth_keywords(content)
                            
                            if youth_keywords:
                                youth_tweets.append({
                                    'platform': 'twitter',
                                    'hashtag': hashtag,
                                    'content': content,
                                    'author_id': tweet.author_id,
                                    'created_at': tweet.created_at,
                                    'retweet_count': tweet.public_metrics.get('retweet_count', 0),
                                    'like_count': tweet.public_metrics.get('like_count', 0),
                                    'reply_count': tweet.public_metrics.get('reply_count', 0),
                                    'sentiment': sentiment,
                                    'youth_keywords': youth_keywords,
                                    'relevance_score': len(youth_keywords) * tweet.public_metrics.get('like_count', 1) / 100
                                })
                                
                except Exception as e:
                    logger.error(f"Error scraping hashtag {hashtag}: {e}")
                    continue
                    
                time.sleep(1)  # Rate limiting
                
        except Exception as e:
            logger.error(f"Twitter scraping error: {e}")
            
        return youth_tweets

    def scrape_youtube_youth_comments(self, video_ids: List[str] = None, limit: int = 200) -> List[Dict[str, Any]]:
        """Scrape youth opinions from YouTube comments"""
        if not self.youtube:
            logger.warning("YouTube API not available")
            return []
            
        if not video_ids:
            # Search for youth-relevant videos
            search_response = self.youtube.search().list(
                q='Indian youth opinions politics education',
                part='id',
                type='video',
                maxResults=10,
                order='relevance'
            ).execute()
            
            video_ids = [item['id']['videoId'] for item in search_response.get('items', [])]
        
        youth_comments = []
        
        try:
            for video_id in video_ids:
                try:
                    # Get video comments
                    comments_response = self.youtube.commentThreads().list(
                        part='snippet',
                        videoId=video_id,
                        maxResults=min(limit//len(video_ids), 100),
                        order='relevance'
                    ).execute()
                    
                    for comment_thread in comments_response.get('items', []):
                        comment = comment_thread['snippet']['topLevelComment']['snippet']
                        content = comment['textDisplay']
                        
                        sentiment = self.analyze_sentiment(content)
                        youth_keywords = self.extract_youth_keywords(content)
                        
                        if youth_keywords:
                            youth_comments.append({
                                'platform': 'youtube',
                                'video_id': video_id,
                                'content': content,
                                'author': comment['authorDisplayName'],
                                'like_count': comment['likeCount'],
                                'published_at': comment['publishedAt'],
                                'sentiment': sentiment,
                                'youth_keywords': youth_keywords,
                                'relevance_score': len(youth_keywords) * comment['likeCount'] / 100
                            })
                            
                except Exception as e:
                    logger.error(f"Error scraping video {video_id}: {e}")
                    continue
                    
                time.sleep(1)  # Rate limiting
                
        except Exception as e:
            logger.error(f"YouTube scraping error: {e}")
            
        return youth_comments

    def scrape_general_web_sources(self) -> List[Dict[str, Any]]:
        """Scrape youth opinions from general web sources"""
        web_opinions = []
        
        # Youth-focused websites and forums (using RSS feeds and accessible social platforms)
        sources = [
            # News RSS Feeds
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
            # Social Media Platforms (accessible without API keys)
            {
                'url': 'https://www.reddit.com/r/india/hot.json',
                'name': 'Reddit India Hot',
                'type': 'reddit_json'
            },
            {
                'url': 'https://www.reddit.com/r/IndianTeenagers/hot.json',
                'name': 'Reddit Indian Teenagers',
                'type': 'reddit_json'
            },
            {
                'url': 'https://www.reddit.com/r/IndianStudents/hot.json',
                'name': 'Reddit Indian Students',
                'type': 'reddit_json'
            },
            {
                'url': 'https://www.reddit.com/r/developersIndia/hot.json',
                'name': 'Reddit Developers India',
                'type': 'reddit_json'
            },
            # GitHub Discussions (accessible)
            {
                'url': 'https://github.com/topics/india',
                'name': 'GitHub India Topics',
                'type': 'github'
            },
            # Stack Overflow (accessible)
            {
                'url': 'https://stackoverflow.com/questions/tagged/india',
                'name': 'Stack Overflow India',
                'type': 'stackoverflow'
            }
        ]
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (compatible; YouthOpinionScraper/1.0; +http://example.com/bot)',
            'Accept': 'application/json, text/html, */*',
        }
        
        for source in sources:
            try:
                response = requests.get(source['url'], headers=headers, timeout=10)
                response.raise_for_status()
                
                if source['type'] == 'rss':
                    # Parse RSS/XML content
                    soup = BeautifulSoup(response.content, 'xml')
                    
                    # Look for items in RSS feeds
                    items = soup.find_all('item')
                    
                    for item in items[:10]:  # Limit to 10 items per RSS feed
                        title = item.find('title')
                        description = item.find('description')
                        link = item.find('link')
                        
                        if title:
                            title_text = title.get_text(strip=True)
                            desc_text = description.get_text(strip=True) if description else ''
                            
                            # Combine title and description for better context
                            content = f"{title_text} {desc_text}".strip()
                            
                            if content and len(content) > 20:
                                sentiment = self.analyze_sentiment(content)
                                youth_keywords = self.extract_youth_keywords(content)
                                
                                # Only include posts with youth relevance
                                if youth_keywords:
                                    web_opinions.append({
                                        'platform': 'news',
                                        'source': source['name'],
                                        'content': content[:500],
                                        'title': title_text,
                                        'url': link.get_text(strip=True) if link else '',
                                        'sentiment': sentiment,
                                        'youth_keywords': youth_keywords,
                                        'relevance_score': len(youth_keywords) * 10  # Base relevance score
                                    })
                                
                elif source['type'] == 'reddit_json':
                    try:
                        data = response.json()
                        posts = data.get('data', {}).get('children', [])
                        
                        for post_data in posts[:5]:  # Limit to 5 posts per subreddit
                            post = post_data.get('data', {})
                            title = post.get('title', '')
                            selftext = post.get('selftext', '')
                            
                            # Combine title and selftext for better context
                            content = f"{title} {selftext}".strip()
                            
                            if content and len(content) > 20:
                                sentiment = self.analyze_sentiment(content)
                                youth_keywords = self.extract_youth_keywords(content)
                                
                                # Only include posts with youth relevance
                                if youth_keywords:
                                    web_opinions.append({
                                        'platform': 'reddit',
                                        'source': source['name'],
                                        'content': content[:500],
                                        'title': title,
                                        'score': post.get('score', 0),
                                        'num_comments': post.get('num_comments', 0),
                                        'created_utc': datetime.fromtimestamp(post.get('created_utc', 0)),
                                        'url': f"https://reddit.com{post.get('permalink', '')}",
                                        'sentiment': sentiment,
                                        'youth_keywords': youth_keywords,
                                        'relevance_score': len(youth_keywords) * max(post.get('score', 1), 1) / 100
                                    })
                    except Exception as e:
                        logger.error(f"Error parsing Reddit JSON from {source['name']}: {e}")
                        continue
                        
                elif source['type'] == 'github':
                    try:
                        soup = BeautifulSoup(response.content, 'html.parser')
                        
                        # Find repository cards or discussion items
                        repos = soup.find_all('article', class_='Box-row')[:5]  # Limit to 5 repos
                        
                        for repo in repos:
                            title_elem = repo.find('h3')
                            desc_elem = repo.find('p', class_='col-9')
                            
                            if title_elem:
                                title = title_elem.get_text(strip=True)
                                desc = desc_elem.get_text(strip=True) if desc_elem else ''
                                content = f"{title} {desc}".strip()
                                
                                if content and len(content) > 20:
                                    sentiment = self.analyze_sentiment(content)
                                    youth_keywords = self.extract_youth_keywords(content)
                                    
                                    if youth_keywords:
                                        web_opinions.append({
                                            'platform': 'github',
                                            'source': source['name'],
                                            'content': content[:500],
                                            'title': title,
                                            'url': f"https://github.com{title_elem.find('a').get('href', '')}",
                                            'sentiment': sentiment,
                                            'youth_keywords': youth_keywords,
                                            'relevance_score': len(youth_keywords) * 15  # Higher score for tech content
                                        })
                    except Exception as e:
                        logger.error(f"Error parsing GitHub from {source['name']}: {e}")
                        continue
                        
                elif source['type'] == 'stackoverflow':
                    try:
                        soup = BeautifulSoup(response.content, 'html.parser')
                        
                        # Find question items
                        questions = soup.find_all('div', class_='s-post-summary')[:5]  # Limit to 5 questions
                        
                        for question in questions:
                            title_elem = question.find('h3')
                            excerpt_elem = question.find('div', class_='s-post-summary--content-excerpt')
                            
                            if title_elem:
                                title = title_elem.get_text(strip=True)
                                excerpt = excerpt_elem.get_text(strip=True) if excerpt_elem else ''
                                content = f"{title} {excerpt}".strip()
                                
                                if content and len(content) > 20:
                                    sentiment = self.analyze_sentiment(content)
                                    youth_keywords = self.extract_youth_keywords(content)
                                    
                                    if youth_keywords:
                                        web_opinions.append({
                                            'platform': 'stackoverflow',
                                            'source': source['name'],
                                            'content': content[:500],
                                            'title': title,
                                            'url': f"https://stackoverflow.com{title_elem.find('a').get('href', '')}",
                                            'sentiment': sentiment,
                                            'youth_keywords': youth_keywords,
                                            'relevance_score': len(youth_keywords) * 12  # Tech-focused score
                                        })
                    except Exception as e:
                        logger.error(f"Error parsing Stack Overflow from {source['name']}: {e}")
                        continue
                                
            except Exception as e:
                logger.error(f"Error scraping {source['name']}: {e}")
                continue
                
            time.sleep(5)  # Increased rate limiting to avoid 429 errors
            
        return web_opinions

    def extract_youth_keywords(self, text: str) -> List[str]:
        """Extract youth-relevant keywords from text"""
        youth_keywords = [
            'student', 'youth', 'teenager', 'young', 'college', 'university', 'school',
            'education', 'job', 'career', 'future', 'dream', 'aspiration', 'startup',
            'entrepreneur', 'technology', 'social media', 'mental health', 'climate',
            'environment', 'politics', 'government', 'policy', 'reform', 'change',
            'innovation', 'digital', 'online', 'internet', 'mobile', 'app', 'coding',
            'programming', 'AI', 'artificial intelligence', 'sustainability', 'equality',
            'diversity', 'inclusion', 'rights', 'freedom', 'expression', 'voice',
            'opinion', 'thought', 'idea', 'solution', 'problem', 'challenge', 'opportunity'
        ]
        
        text_lower = text.lower()
        found_keywords = [kw for kw in youth_keywords if kw in text_lower]
        
        return found_keywords

    def analyze_youth_sentiment_trends(self, posts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze sentiment trends from youth posts"""
        if not posts:
            return {}
            
        total_posts = len(posts)
        sentiment_counts = {'positive': 0, 'negative': 0, 'neutral': 0}
        keyword_frequency = {}
        platform_distribution = {}
        
        for post in posts:
            # Count sentiments
            sentiment = post.get('sentiment', {}).get('overall', 'neutral')
            sentiment_counts[sentiment] += 1
            
            # Count keywords
            keywords = post.get('youth_keywords', [])
            for keyword in keywords:
                keyword_frequency[keyword] = keyword_frequency.get(keyword, 0) + 1
            
            # Count platforms
            platform = post.get('platform', 'unknown')
            platform_distribution[platform] = platform_distribution.get(platform, 0) + 1
        
        # Calculate percentages
        sentiment_percentages = {
            sentiment: (count / total_posts) * 100 
            for sentiment, count in sentiment_counts.items()
        }
        
        # Get top keywords
        top_keywords = sorted(keyword_frequency.items(), key=lambda x: x[1], reverse=True)[:10]
        
        return {
            'total_posts': total_posts,
            'sentiment_distribution': sentiment_percentages,
            'top_keywords': top_keywords,
            'platform_distribution': platform_distribution,
            'analysis_timestamp': datetime.now().isoformat()
        }

    def get_comprehensive_youth_opinions(self) -> Dict[str, Any]:
        """Get comprehensive youth opinions from all available sources"""
        logger.info("Starting comprehensive youth opinion scraping...")
        
        all_posts = []
        
        # Scrape from different platforms
        try:
            reddit_posts = self.scrape_reddit_youth_opinions(limit=50)
            all_posts.extend(reddit_posts)
            logger.info(f"Scraped {len(reddit_posts)} Reddit posts")
        except Exception as e:
            logger.error(f"Reddit scraping failed: {e}")
            
        try:
            twitter_posts = self.scrape_twitter_youth_opinions(limit=50)
            all_posts.extend(twitter_posts)
            logger.info(f"Scraped {len(twitter_posts)} Twitter posts")
        except Exception as e:
            logger.error(f"Twitter scraping failed: {e}")
            
        try:
            youtube_posts = self.scrape_youtube_youth_comments(limit=50)
            all_posts.extend(youtube_posts)
            logger.info(f"Scraped {len(youtube_posts)} YouTube comments")
        except Exception as e:
            logger.error(f"YouTube scraping failed: {e}")
            
        try:
            web_posts = self.scrape_general_web_sources()
            all_posts.extend(web_posts)
            logger.info(f"Scraped {len(web_posts)} web posts")
        except Exception as e:
            logger.error(f"Web scraping failed: {e}")
            
        try:
            additional_posts = additional_social_sources.scrape_all_additional_sources()
            all_posts.extend(additional_posts)
            logger.info(f"Scraped {len(additional_posts)} additional social media posts")
        except Exception as e:
            logger.error(f"Additional social media scraping failed: {e}")
        
        # Analyze trends
        trends = self.analyze_youth_sentiment_trends(all_posts)
        
        # Sort posts by relevance score
        all_posts.sort(key=lambda x: x.get('relevance_score', 0), reverse=True)
        
        return {
            'posts': all_posts[:100],  # Return top 100 most relevant posts
            'trends': trends,
            'scraping_timestamp': datetime.now().isoformat(),
            'total_sources_scraped': len(all_posts)
        }

# Global scraper instance
social_media_scraper = SocialMediaScraper()
