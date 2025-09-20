"""
Advanced Gap Analysis System for Youth vs Political Focus
This module analyzes real data to determine the gap between youth and political priorities
"""

import re
import requests
import time
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from typing import Dict, List, Any, Tuple
from collections import Counter
import logging

logger = logging.getLogger(__name__)

class GapAnalyzer:
    """
    Analyzes the gap between youth and political focus using real data sources
    """
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (compatible; GapAnalyzer/1.0; +http://example.com/bot)',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        }
        
        # Youth-relevant keywords with weights and context mapping
        self.youth_keywords = {
            # Education Issues
            'education': 10, 'student': 10, 'university': 8, 'college': 8, 'school': 6,
            'tuition fees': 9, 'student loan': 9, 'education loan': 9, 'college debt': 8,
            'exam pressure': 8, 'board exams': 7, 'entrance exam': 7, 'competitive exams': 7,
            'online classes': 7, 'digital learning': 6, 'remote education': 6,
            'campus placement': 8, 'job placement': 7, 'career guidance': 7,
            
            # Employment & Career Issues
            'job': 9, 'career': 9, 'employment': 8, 'unemployment': 9, 'hiring': 7,
            'job market': 8, 'job search': 8, 'resume': 6, 'interview': 6,
            'salary': 7, 'low salary': 8, 'wage': 6, 'income': 6,
            'work life balance': 8, 'overtime': 6, 'workplace stress': 7,
            'internship': 7, 'fresher': 7, 'entry level': 6, 'experience required': 7,
            
            # Entrepreneurship & Startups
            'startup': 8, 'entrepreneur': 8, 'business': 6, 'innovation': 7,
            'funding': 7, 'investor': 6, 'venture capital': 6, 'angel investor': 6,
            'business plan': 6, 'market research': 6, 'customer acquisition': 6,
            
            # Technology & Digital Issues
            'technology': 7, 'tech': 7, 'digital': 6, 'internet': 5, 'mobile': 5,
            'app development': 7, 'coding': 7, 'programming': 7, 'software': 6,
            'artificial intelligence': 7, 'AI': 7, 'machine learning': 6,
            'cybersecurity': 6, 'data privacy': 7, 'online safety': 6,
            'digital divide': 7, 'internet access': 6, 'broadband': 5,
            
            # Mental Health & Wellbeing
            'mental health': 9, 'depression': 8, 'anxiety': 8, 'therapy': 7,
            'stress': 7, 'burnout': 7, 'suicide': 8, 'self harm': 8,
            'counseling': 7, 'psychologist': 6, 'psychiatrist': 6,
            'meditation': 5, 'mindfulness': 5, 'wellness': 6,
            
            # Climate & Environment
            'climate change': 8, 'environment': 7, 'pollution': 7, 'sustainability': 6,
            'global warming': 7, 'carbon footprint': 6, 'renewable energy': 6,
            'air quality': 7, 'water pollution': 6, 'waste management': 6,
            'green energy': 6, 'solar power': 5, 'electric vehicle': 6,
            
            # Social Media & Digital Life
            'social media': 6, 'instagram': 5, 'tiktok': 5, 'youtube': 5,
            'facebook': 5, 'twitter': 5, 'linkedin': 5, 'snapchat': 4,
            'online harassment': 7, 'cyberbullying': 7, 'fake news': 6,
            'digital addiction': 7, 'screen time': 6, 'social media detox': 6,
            
            # Housing & Living Costs
            'housing': 7, 'rent': 6, 'home': 6, 'affordable': 7,
            'rental crisis': 8, 'housing shortage': 7, 'real estate': 6,
            'mortgage': 6, 'property prices': 6, 'landlord': 5,
            'shared accommodation': 6, 'PG': 6, 'hostel': 6,
            
            # Transportation & Infrastructure
            'transportation': 6, 'public transport': 6, 'metro': 5, 'bus': 4,
            'traffic': 6, 'commute': 6, 'fuel prices': 6, 'petrol': 5, 'diesel': 5,
            'ride sharing': 5, 'uber': 5, 'ola': 5, 'auto rickshaw': 4,
            
            # Healthcare & Medical
            'healthcare': 7, 'medical': 6, 'hospital': 5, 'doctor': 5,
            'health insurance': 7, 'medical bills': 7, 'pharmacy': 5,
            'mental healthcare': 8, 'therapy cost': 7, 'medication': 6,
            
            # Politics & Governance
            'politics': 5, 'government': 5, 'policy': 6, 'reform': 6,
            'election': 6, 'voting': 6, 'democracy': 6, 'corruption': 7,
            'transparency': 6, 'accountability': 6, 'governance': 6,
            
            # Rights & Social Issues
            'rights': 6, 'freedom': 6, 'equality': 7, 'justice': 6,
            'discrimination': 7, 'racism': 7, 'sexism': 7, 'caste': 7,
            'LGBTQ': 7, 'gender equality': 7, 'women rights': 7,
            'freedom of speech': 7, 'censorship': 6, 'privacy rights': 7,
            
            # Future & Aspirations
            'future': 8, 'dream': 7, 'aspiration': 7, 'goal': 6,
            'career goals': 8, 'life goals': 7, 'ambition': 7,
            'success': 6, 'achievement': 6, 'motivation': 6,
            
            # Skills & Development
            'skill': 7, 'training': 6, 'development': 6, 'learning': 6,
            'skill development': 8, 'upskilling': 7, 'reskilling': 7,
            'certification': 6, 'course': 6, 'workshop': 5,
            'soft skills': 6, 'communication skills': 6, 'leadership': 6
        }
        
        # Political keywords with weights and context mapping
        self.political_keywords = {
            # Government & Administration
            'government': 10, 'minister': 9, 'parliament': 8, 'assembly': 7,
            'prime minister': 10, 'chief minister': 9, 'bureaucracy': 7,
            'civil service': 7, 'IAS': 7, 'IPS': 6, 'IRS': 6,
            'governance': 8, 'administration': 7, 'public administration': 7,
            
            # Policy & Programs
            'policy': 9, 'scheme': 8, 'program': 7, 'initiative': 7,
            'government scheme': 9, 'welfare scheme': 8, 'subsidy': 7,
            'beneficiary': 6, 'targeted': 6, 'implementation': 7,
            'monitoring': 6, 'evaluation': 6, 'impact assessment': 6,
            
            # Economic & Financial
            'budget': 8, 'finance': 7, 'economy': 8, 'gdp': 7,
            'union budget': 9, 'state budget': 8, 'fiscal policy': 8,
            'monetary policy': 7, 'RBI': 7, 'reserve bank': 7,
            'economic growth': 8, 'inflation': 7, 'unemployment rate': 7,
            'tax collection': 7, 'revenue': 6, 'expenditure': 6,
            
            # Elections & Democracy
            'election': 9, 'vote': 8, 'campaign': 7, 'candidate': 7,
            'voting': 8, 'electoral': 7, 'constituency': 6, 'MP': 7, 'MLA': 6,
            'political party': 8, 'opposition': 7, 'coalition': 6,
            'democracy': 8, 'constitution': 8, 'fundamental rights': 7,
            
            # Legislation & Law
            'law': 8, 'act': 7, 'bill': 7, 'legislation': 8,
            'parliamentary': 8, 'legislative': 7, 'amendment': 7,
            'supreme court': 8, 'high court': 7, 'judiciary': 7,
            'legal framework': 7, 'constitutional': 7, 'statutory': 6,
            
            # Infrastructure & Development
            'infrastructure': 7, 'development': 7, 'project': 6,
            'smart city': 7, 'digital india': 7, 'make in india': 7,
            'highway': 6, 'railway': 6, 'metro': 6, 'airport': 6,
            'urban development': 7, 'rural development': 7,
            'housing for all': 7, 'swachh bharat': 6,
            
            # Defense & Security
            'defense': 6, 'security': 7, 'military': 6,
            'national security': 8, 'border security': 7, 'terrorism': 7,
            'army': 6, 'navy': 6, 'air force': 6, 'paramilitary': 6,
            'intelligence': 6, 'cyber security': 6, 'internal security': 7,
            
            # Foreign Policy & Diplomacy
            'foreign policy': 7, 'diplomacy': 6, 'international': 6,
            'bilateral': 6, 'multilateral': 6, 'trade agreement': 6,
            'embassy': 5, 'consulate': 5, 'visa': 5, 'immigration': 6,
            'UN': 6, 'WTO': 5, 'SAARC': 5, 'BRICS': 5,
            
            # Agriculture & Rural
            'agriculture': 6, 'farmer': 6, 'rural': 6,
            'farmers protest': 8, 'agricultural policy': 7, 'crop insurance': 6,
            'minimum support price': 7, 'MSP': 7, 'mandi': 6,
            'rural employment': 7, 'MNREGA': 7, 'panchayat': 6,
            
            # Energy & Environment
            'energy': 6, 'power': 6, 'electricity': 5,
            'renewable energy': 6, 'solar power': 5, 'wind energy': 5,
            'coal': 5, 'petroleum': 5, 'natural gas': 5,
            'environmental policy': 6, 'climate policy': 6, 'green energy': 5,
            
            # Taxation & Revenue
            'tax': 7, 'gst': 6, 'revenue': 6, 'fiscal': 6,
            'income tax': 7, 'corporate tax': 6, 'property tax': 5,
            'tax evasion': 6, 'black money': 6, 'demonetization': 7,
            'tax reform': 7, 'simplification': 6,
            
            # Social Issues & Welfare
            'welfare': 6, 'social': 6, 'public': 6,
            'social security': 7, 'pension': 6, 'healthcare policy': 7,
            'education policy': 7, 'skill development': 6, 'employment generation': 7,
            'women empowerment': 7, 'child welfare': 6, 'senior citizens': 6,
            
            # Governance & Accountability
            'corruption': 6, 'transparency': 6, 'accountability': 6,
            'RTI': 6, 'right to information': 6, 'whistleblower': 5,
            'audit': 5, 'CAG': 5, 'vigilance': 5, 'ethics': 5,
            'good governance': 7, 'e-governance': 6, 'digital governance': 6
        }
    
    def analyze_youth_mentions(self, content: str) -> Tuple[int, List[str]]:
        """Analyze youth relevance of content"""
        content_lower = content.lower()
        total_score = 0
        found_keywords = []
        
        for keyword, weight in self.youth_keywords.items():
            if keyword in content_lower:
                count = content_lower.count(keyword)
                score = count * weight
                total_score += score
                found_keywords.append(keyword)
        
        return total_score, found_keywords
    
    def analyze_political_mentions(self, content: str) -> Tuple[int, List[str]]:
        """Analyze political relevance of content"""
        content_lower = content.lower()
        total_score = 0
        found_keywords = []
        
        for keyword, weight in self.political_keywords.items():
            if keyword in content_lower:
                count = content_lower.count(keyword)
                score = count * weight
                total_score += score
                found_keywords.append(keyword)
        
        return total_score, found_keywords
    
    def scrape_youth_sources(self) -> List[Dict[str, Any]]:
        """Scrape youth-focused sources"""
        youth_sources = [
            {
                'url': 'https://www.reddit.com/r/IndianTeenagers/hot.json',
                'name': 'Reddit Indian Teenagers',
                'type': 'reddit'
            },
            {
                'url': 'https://www.reddit.com/r/IndianStudents/hot.json',
                'name': 'Reddit Indian Students',
                'type': 'reddit'
            },
            {
                'url': 'https://www.reddit.com/r/developersIndia/hot.json',
                'name': 'Reddit Developers India',
                'type': 'reddit'
            },
            {
                'url': 'https://feeds.bbci.co.uk/news/world/asia/india/rss.xml',
                'name': 'BBC India RSS',
                'type': 'rss'
            }
        ]
        
        youth_data = []
        
        for source in youth_sources:
            try:
                response = requests.get(source['url'], headers=self.headers, timeout=10)
                response.raise_for_status()
                
                if source['type'] == 'reddit':
                    data = response.json()
                    posts = data.get('data', {}).get('children', [])
                    
                    for post_data in posts[:10]:
                        post = post_data.get('data', {})
                        title = post.get('title', '')
                        selftext = post.get('selftext', '')
                        content = f"{title} {selftext}".strip()
                        
                        if content:
                            youth_score, youth_keywords = self.analyze_youth_mentions(content)
                            political_score, political_keywords = self.analyze_political_mentions(content)
                            
                            youth_data.append({
                                'content': content,
                                'source': source['name'],
                                'youth_score': youth_score,
                                'political_score': political_score,
                                'youth_keywords': youth_keywords,
                                'political_keywords': political_keywords,
                                'platform': 'reddit'
                            })
                
                elif source['type'] == 'rss':
                    soup = BeautifulSoup(response.content, 'xml')
                    items = soup.find_all('item')
                    
                    for item in items[:10]:
                        title = item.find('title')
                        description = item.find('description')
                        
                        if title:
                            title_text = title.get_text(strip=True)
                            desc_text = description.get_text(strip=True) if description else ''
                            content = f"{title_text} {desc_text}".strip()
                            
                            if content:
                                youth_score, youth_keywords = self.analyze_youth_mentions(content)
                                political_score, political_keywords = self.analyze_political_mentions(content)
                                
                                youth_data.append({
                                    'content': content,
                                    'source': source['name'],
                                    'youth_score': youth_score,
                                    'political_score': political_score,
                                    'youth_keywords': youth_keywords,
                                    'political_keywords': political_keywords,
                                    'platform': 'news'
                                })
                
                time.sleep(2)  # Rate limiting
                
            except Exception as e:
                logger.error(f"Error scraping youth source {source['name']}: {e}")
                continue
        
        return youth_data
    
    def scrape_political_sources(self) -> List[Dict[str, Any]]:
        """Scrape political-focused sources"""
        political_sources = [
            {
                'url': 'https://timesofindia.indiatimes.com/rssfeeds/1221656.cms',
                'name': 'TOI Education RSS',
                'type': 'rss'
            },
            {
                'url': 'https://www.thehindu.com/news/national/feeder/default.rss',
                'name': 'The Hindu National RSS',
                'type': 'rss'
            },
            {
                'url': 'https://www.hindustantimes.com/rss/education/rssfeed.xml',
                'name': 'Hindustan Times Education RSS',
                'type': 'rss'
            }
        ]
        
        political_data = []
        
        for source in political_sources:
            try:
                response = requests.get(source['url'], headers=self.headers, timeout=10)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.content, 'xml')
                items = soup.find_all('item')
                
                for item in items[:10]:
                    title = item.find('title')
                    description = item.find('description')
                    
                    if title:
                        title_text = title.get_text(strip=True)
                        desc_text = description.get_text(strip=True) if description else ''
                        content = f"{title_text} {desc_text}".strip()
                        
                        if content:
                            youth_score, youth_keywords = self.analyze_youth_mentions(content)
                            political_score, political_keywords = self.analyze_political_mentions(content)
                            
                            political_data.append({
                                'content': content,
                                'source': source['name'],
                                'youth_score': youth_score,
                                'political_score': political_score,
                                'youth_keywords': youth_keywords,
                                'political_keywords': political_keywords,
                                'platform': 'news'
                            })
                
                time.sleep(2)  # Rate limiting
                
            except Exception as e:
                logger.error(f"Error scraping political source {source['name']}: {e}")
                continue
        
        return political_data
    
    def create_descriptive_topic_name(self, topic: str) -> str:
        """Create more descriptive topic names by mapping keywords to meaningful issues"""
        topic_mapping = {
            # Education Issues
            'education': 'Education System & Access',
            'student': 'Student Life & Challenges',
            'university': 'Higher Education Issues',
            'college': 'College Education Problems',
            'tuition fees': 'Tuition Fee Crisis',
            'student loan': 'Student Loan Burden',
            'education loan': 'Education Loan Crisis',
            'college debt': 'College Debt Crisis',
            'exam pressure': 'Exam Pressure & Stress',
            'board exams': 'Board Exam System',
            'entrance exam': 'Entrance Exam Competition',
            'competitive exams': 'Competitive Exam Pressure',
            'online classes': 'Online Learning Challenges',
            'digital learning': 'Digital Education Gap',
            'campus placement': 'Campus Placement Issues',
            'job placement': 'Job Placement Problems',
            
            # Employment Issues
            'job': 'Job Market Crisis',
            'career': 'Career Development Challenges',
            'employment': 'Employment Opportunities',
            'unemployment': 'Youth Unemployment Crisis',
            'job market': 'Job Market Conditions',
            'job search': 'Job Search Difficulties',
            'salary': 'Salary & Compensation Issues',
            'low salary': 'Low Salary Problem',
            'work life balance': 'Work-Life Balance',
            'workplace stress': 'Workplace Stress & Burnout',
            'internship': 'Internship Opportunities',
            'fresher': 'Fresher Job Challenges',
            'entry level': 'Entry-Level Job Crisis',
            'experience required': 'Experience Requirement Problem',
            
            # Mental Health
            'mental health': 'Mental Health Crisis',
            'depression': 'Depression & Mental Illness',
            'anxiety': 'Anxiety & Stress Disorders',
            'therapy': 'Mental Health Therapy Access',
            'stress': 'Stress & Pressure',
            'burnout': 'Burnout & Exhaustion',
            'suicide': 'Suicide Prevention',
            'self harm': 'Self-Harm & Mental Health',
            'counseling': 'Mental Health Counseling',
            'mental healthcare': 'Mental Healthcare Access',
            'therapy cost': 'Mental Health Treatment Cost',
            
            # Technology & Digital
            'technology': 'Technology Access & Skills',
            'tech': 'Tech Industry Opportunities',
            'digital': 'Digital Divide & Access',
            'app development': 'App Development Opportunities',
            'coding': 'Coding & Programming Skills',
            'programming': 'Programming Education',
            'artificial intelligence': 'AI & Machine Learning',
            'AI': 'Artificial Intelligence Impact',
            'cybersecurity': 'Cybersecurity & Online Safety',
            'data privacy': 'Data Privacy & Protection',
            'online safety': 'Online Safety & Security',
            'digital divide': 'Digital Divide & Inequality',
            'internet access': 'Internet Access & Connectivity',
            
            # Climate & Environment
            'climate change': 'Climate Change & Environment',
            'environment': 'Environmental Protection',
            'pollution': 'Pollution & Air Quality',
            'global warming': 'Global Warming Concerns',
            'air quality': 'Air Quality & Pollution',
            'water pollution': 'Water Pollution Crisis',
            'renewable energy': 'Renewable Energy Transition',
            'green energy': 'Green Energy & Sustainability',
            
            # Social Media & Digital Life
            'social media': 'Social Media Impact',
            'instagram': 'Instagram & Social Media',
            'tiktok': 'TikTok & Short Videos',
            'youtube': 'YouTube & Content Creation',
            'online harassment': 'Online Harassment & Bullying',
            'cyberbullying': 'Cyberbullying & Online Safety',
            'fake news': 'Fake News & Misinformation',
            'digital addiction': 'Digital Addiction & Screen Time',
            'screen time': 'Screen Time & Digital Wellness',
            
            # Housing & Living Costs
            'housing': 'Housing Affordability Crisis',
            'rent': 'Rental Housing Crisis',
            'rental crisis': 'Rental Housing Crisis',
            'housing shortage': 'Housing Shortage Problem',
            'real estate': 'Real Estate & Property',
            'property prices': 'Property Price Inflation',
            'shared accommodation': 'Shared Housing & PG',
            'PG': 'PG & Hostel Accommodation',
            'hostel': 'Hostel & Student Housing',
            
            # Transportation
            'transportation': 'Public Transportation',
            'public transport': 'Public Transport System',
            'metro': 'Metro & Urban Transport',
            'traffic': 'Traffic & Commute Issues',
            'commute': 'Daily Commute Problems',
            'fuel prices': 'Fuel Price Inflation',
            'petrol': 'Petrol & Diesel Prices',
            'ride sharing': 'Ride-Sharing & Mobility',
            
            # Healthcare
            'healthcare': 'Healthcare Access & Quality',
            'medical': 'Medical Care & Treatment',
            'health insurance': 'Health Insurance Coverage',
            'medical bills': 'Medical Bills & Healthcare Cost',
            'pharmacy': 'Pharmacy & Medicine Access',
            
            # Skills & Development
            'skill': 'Skill Development & Training',
            'skill development': 'Skill Development Programs',
            'upskilling': 'Upskilling & Career Growth',
            'reskilling': 'Reskilling & Career Change',
            'certification': 'Professional Certification',
            'course': 'Online Courses & Learning',
            'soft skills': 'Soft Skills Development',
            'communication skills': 'Communication Skills',
            'leadership': 'Leadership Development',
            
            # Future & Aspirations
            'future': 'Future Planning & Aspirations',
            'dream': 'Dreams & Life Goals',
            'aspiration': 'Career Aspirations',
            'career goals': 'Career Goals & Planning',
            'life goals': 'Life Goals & Ambitions',
            'success': 'Success & Achievement',
            'motivation': 'Motivation & Inspiration',
            
            # Rights & Social Issues
            'rights': 'Human Rights & Freedoms',
            'freedom': 'Freedom & Liberty',
            'equality': 'Equality & Social Justice',
            'justice': 'Justice & Fairness',
            'discrimination': 'Discrimination & Bias',
            'racism': 'Racism & Prejudice',
            'sexism': 'Sexism & Gender Bias',
            'caste': 'Caste Discrimination',
            'LGBTQ': 'LGBTQ+ Rights & Acceptance',
            'gender equality': 'Gender Equality & Women Rights',
            'women rights': 'Women Rights & Empowerment',
            'freedom of speech': 'Freedom of Speech & Expression',
            'censorship': 'Censorship & Free Speech',
            'privacy rights': 'Privacy Rights & Data Protection'
        }
        
        return topic_mapping.get(topic, topic.title())
    
    def calculate_topic_gaps(self, youth_data: List[Dict], political_data: List[Dict]) -> Dict[str, Any]:
        """Calculate the gap between youth and political focus on different topics"""
        
        # Extract all topics from both datasets
        all_topics = set()
        
        # From youth data
        for item in youth_data:
            all_topics.update(item['youth_keywords'])
            all_topics.update(item['political_keywords'])
        
        # From political data
        for item in political_data:
            all_topics.update(item['youth_keywords'])
            all_topics.update(item['political_keywords'])
        
        # Calculate gap scores for each topic
        topic_gaps = {}
        
        for topic in all_topics:
            # Calculate youth focus on this topic
            youth_focus = 0
            youth_count = 0
            
            for item in youth_data:
                if topic in item['youth_keywords']:
                    youth_focus += item['youth_score']
                    youth_count += 1
            
            # Calculate political focus on this topic
            political_focus = 0
            political_count = 0
            
            for item in political_data:
                if topic in item['political_keywords']:
                    political_focus += item['political_score']
                    political_count += 1
            
            # Normalize scores
            youth_avg = youth_focus / max(youth_count, 1)
            political_avg = political_focus / max(political_count, 1)
            
            # Calculate gap
            gap_score = youth_avg - political_avg
            
            # Create descriptive topic name
            descriptive_name = self.create_descriptive_topic_name(topic)
            
            topic_gaps[topic] = {
                'topic_name': descriptive_name,
                'original_keyword': topic,
                'youth_focus': youth_avg,
                'political_focus': political_avg,
                'gap_score': gap_score,
                'youth_mentions': youth_count,
                'political_mentions': political_count,
                'reliability': min(youth_count + political_count, 10) / 10  # Reliability based on data points
            }
        
        return topic_gaps
    
    def generate_gap_analysis(self) -> Dict[str, Any]:
        """Generate comprehensive gap analysis"""
        logger.info("Starting gap analysis...")
        
        # Scrape data from both youth and political sources
        youth_data = self.scrape_youth_sources()
        political_data = self.scrape_political_sources()
        
        logger.info(f"Scraped {len(youth_data)} youth items and {len(political_data)} political items")
        
        # Calculate topic gaps
        topic_gaps = self.calculate_topic_gaps(youth_data, political_data)
        
        # Sort topics by gap score
        sorted_topics = sorted(topic_gaps.items(), key=lambda x: x[1]['gap_score'], reverse=True)
        
        # Calculate overall statistics
        total_youth_score = sum(item['youth_score'] for item in youth_data)
        total_political_score = sum(item['political_score'] for item in political_data)
        
        # Generate analysis
        analysis = {
            'timestamp': datetime.now().isoformat(),
            'data_sources': {
                'youth_sources': len(youth_data),
                'political_sources': len(political_data),
                'total_items': len(youth_data) + len(political_data)
            },
            'overall_scores': {
                'total_youth_score': total_youth_score,
                'total_political_score': total_political_score,
                'overall_gap': total_youth_score - total_political_score
            },
            'topic_gaps': dict(sorted_topics),
            'top_gaps': sorted_topics[:10],  # Top 10 gaps
            'reliability_notes': {
                'data_points': len(youth_data) + len(political_data),
                'reliability_score': min(len(youth_data) + len(political_data), 50) / 50,
                'methodology': 'Real-time analysis of youth vs political content using keyword scoring'
            }
        }
        
        return analysis

# Global instance
gap_analyzer = GapAnalyzer()
