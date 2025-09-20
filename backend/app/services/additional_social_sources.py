"""
Additional accessible social media sources for youth opinion scraping
These sources don't require API keys and are more accessible
"""

import requests
from bs4 import BeautifulSoup
from datetime import datetime
import time
import logging

logger = logging.getLogger(__name__)

class AdditionalSocialSources:
    """Additional social media sources that are accessible without API keys"""
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (compatible; YouthOpinionScraper/1.0; +http://example.com/bot)',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        }
    
    def scrape_quora_topics(self):
        """Scrape Quora topics related to Indian youth"""
        try:
            # Quora topics that are accessible
            topics = [
                'https://www.quora.com/topic/Indian-Youth',
                'https://www.quora.com/topic/Indian-Students',
                'https://www.quora.com/topic/Indian-Education',
                'https://www.quora.com/topic/Indian-Technology'
            ]
            
            posts = []
            for topic_url in topics:
                try:
                    response = requests.get(topic_url, headers=self.headers, timeout=10)
                    response.raise_for_status()
                    
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    # Find question elements
                    questions = soup.find_all('div', class_='q-text')[:3]  # Limit to 3 per topic
                    
                    for question in questions:
                        question_text = question.get_text(strip=True)
                        if len(question_text) > 20:
                            posts.append({
                                'platform': 'quora',
                                'content': question_text,
                                'title': question_text[:100],
                                'url': topic_url,
                                'source': 'Quora Topics',
                                'created_at': datetime.now()
                            })
                    
                    time.sleep(3)  # Rate limiting
                    
                except Exception as e:
                    logger.error(f"Error scraping Quora topic {topic_url}: {e}")
                    continue
            
            return posts
            
        except Exception as e:
            logger.error(f"Error in Quora scraping: {e}")
            return []
    
    def scrape_medium_articles(self):
        """Scrape Medium articles related to Indian youth topics"""
        try:
            # Medium tags that are accessible
            tags = [
                'https://medium.com/tag/india',
                'https://medium.com/tag/indian-youth',
                'https://medium.com/tag/indian-education',
                'https://medium.com/tag/indian-technology'
            ]
            
            posts = []
            for tag_url in tags:
                try:
                    response = requests.get(tag_url, headers=self.headers, timeout=10)
                    response.raise_for_status()
                    
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    # Find article elements
                    articles = soup.find_all('article')[:3]  # Limit to 3 per tag
                    
                    for article in articles:
                        title_elem = article.find('h2')
                        excerpt_elem = article.find('p')
                        
                        if title_elem:
                            title = title_elem.get_text(strip=True)
                            excerpt = excerpt_elem.get_text(strip=True) if excerpt_elem else ''
                            content = f"{title} {excerpt}".strip()
                            
                            if len(content) > 20:
                                posts.append({
                                    'platform': 'medium',
                                    'content': content,
                                    'title': title,
                                    'url': tag_url,
                                    'source': 'Medium Articles',
                                    'created_at': datetime.now()
                                })
                    
                    time.sleep(3)  # Rate limiting
                    
                except Exception as e:
                    logger.error(f"Error scraping Medium tag {tag_url}: {e}")
                    continue
            
            return posts
            
        except Exception as e:
            logger.error(f"Error in Medium scraping: {e}")
            return []
    
    def scrape_dev_to_articles(self):
        """Scrape Dev.to articles related to Indian developers"""
        try:
            # Dev.to tags
            tags = [
                'https://dev.to/t/india',
                'https://dev.to/t/indian-developers',
                'https://dev.to/t/indian-tech'
            ]
            
            posts = []
            for tag_url in tags:
                try:
                    response = requests.get(tag_url, headers=self.headers, timeout=10)
                    response.raise_for_status()
                    
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    # Find article elements
                    articles = soup.find_all('article')[:3]  # Limit to 3 per tag
                    
                    for article in articles:
                        title_elem = article.find('h2')
                        excerpt_elem = article.find('p')
                        
                        if title_elem:
                            title = title_elem.get_text(strip=True)
                            excerpt = excerpt_elem.get_text(strip=True) if excerpt_elem else ''
                            content = f"{title} {excerpt}".strip()
                            
                            if len(content) > 20:
                                posts.append({
                                    'platform': 'devto',
                                    'content': content,
                                    'title': title,
                                    'url': tag_url,
                                    'source': 'Dev.to Articles',
                                    'created_at': datetime.now()
                                })
                    
                    time.sleep(3)  # Rate limiting
                    
                except Exception as e:
                    logger.error(f"Error scraping Dev.to tag {tag_url}: {e}")
                    continue
            
            return posts
            
        except Exception as e:
            logger.error(f"Error in Dev.to scraping: {e}")
            return []
    
    def scrape_hackernews(self):
        """Scrape Hacker News for India-related posts"""
        try:
            # Hacker News search for India
            search_url = 'https://hn.algolia.com/api/v1/search?query=india&tags=story'
            
            response = requests.get(search_url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            hits = data.get('hits', [])[:10]  # Limit to 10 posts
            
            posts = []
            for hit in hits:
                title = hit.get('title', '')
                story_text = hit.get('story_text', '')
                content = f"{title} {story_text}".strip()
                
                if len(content) > 20:
                    posts.append({
                        'platform': 'hackernews',
                        'content': content,
                        'title': title,
                        'url': hit.get('url', ''),
                        'source': 'Hacker News',
                        'created_at': datetime.fromtimestamp(hit.get('created_at_i', 0)),
                        'points': hit.get('points', 0)
                    })
            
            return posts
            
        except Exception as e:
            logger.error(f"Error in Hacker News scraping: {e}")
            return []
    
    def scrape_all_additional_sources(self):
        """Scrape all additional social media sources"""
        all_posts = []
        
        # Scrape different platforms
        try:
            quora_posts = self.scrape_quora_topics()
            all_posts.extend(quora_posts)
            logger.info(f"Scraped {len(quora_posts)} Quora posts")
        except Exception as e:
            logger.error(f"Quora scraping failed: {e}")
        
        try:
            medium_posts = self.scrape_medium_articles()
            all_posts.extend(medium_posts)
            logger.info(f"Scraped {len(medium_posts)} Medium posts")
        except Exception as e:
            logger.error(f"Medium scraping failed: {e}")
        
        try:
            devto_posts = self.scrape_dev_to_articles()
            all_posts.extend(devto_posts)
            logger.info(f"Scraped {len(devto_posts)} Dev.to posts")
        except Exception as e:
            logger.error(f"Dev.to scraping failed: {e}")
        
        try:
            hn_posts = self.scrape_hackernews()
            all_posts.extend(hn_posts)
            logger.info(f"Scraped {len(hn_posts)} Hacker News posts")
        except Exception as e:
            logger.error(f"Hacker News scraping failed: {e}")
        
        return all_posts

# Global instance
additional_social_sources = AdditionalSocialSources()
