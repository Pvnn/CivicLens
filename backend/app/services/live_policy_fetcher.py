import os
import time
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any

import requests
from bs4 import BeautifulSoup

try:
    # Optional: for dynamic sites; only used if available
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options as ChromeOptions
    from selenium.webdriver.common.by import By
    SELENIUM_AVAILABLE = True
except Exception:
    SELENIUM_AVAILABLE = False

USER_AGENT = os.getenv('SCRAPING_USER_AGENT', 'CivicLens-PolicyBot/1.0')
RATE_LIMIT_DELAY = float(os.getenv('RATE_LIMIT_DELAY', '1'))

class LiveGovernmentDataFetcher:
    def __init__(self):
        self.sources = {
            'pib_releases': 'https://pib.gov.in/PressReleasePage.aspx',
            'rbi_notifications': 'https://www.rbi.org.in/Scripts/BS_PressReleaseDisplay.aspx',
            'sebi_updates': 'https://www.sebi.gov.in/sebiweb/other/OtherAction.do?doRecent=yes',
            'ministry_health': 'https://www.mohfw.gov.in/media/disease-alerts',
            'finance_ministry': 'https://finmin.nic.in/press_room/press_release'
        }
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': USER_AGENT})

    def fetch_weekly_updates(self, days_back: int = 7) -> List[Dict[str, Any]]:
        """Scrape multiple official sources for recent updates within days_back.
        Returns a list of dicts: {title, ministry, content, source_url, metadata}
        """
        results: List[Dict[str, Any]] = []
        try:
            results.extend(self.scrape_pib_releases(days_back))
        except Exception as e:
            logging.warning(f"PIB scrape failed: {e}")
        time.sleep(RATE_LIMIT_DELAY)
        
        try:
            results.extend(self.scrape_sebi_updates(days_back))
        except Exception as e:
            logging.warning(f"SEBI scrape failed: {e}")
        time.sleep(RATE_LIMIT_DELAY)

        # Add more sources as needed (RBI, Health, Finance). Keep minimal for initial version.
        return results

    def _within_days(self, date_obj: datetime, days_back: int) -> bool:
        return date_obj >= (datetime.now() - timedelta(days=days_back))

    def scrape_pib_releases(self, days_back: int = 7) -> List[Dict[str, Any]]:
        """Scrape Press Information Bureau for recent releases.
        Extract: title, date, ministry (if present), brief content, source_url
        """
        url = self.sources['pib_releases']
        r = self.session.get(url, timeout=20)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, 'lxml')

        items: List[Dict[str, Any]] = []
        # Heuristic selectors; PIB markup changes, so we keep it resilient
        for a in soup.select('a'):
            title = (a.get_text() or '').strip()
            href = a.get('href')
            if not title or not href:
                continue
            if 'PressRelease' not in href and 'PressRelese' not in href:
                continue
            source_url = href if href.startswith('http') else f"https://pib.gov.in/{href.lstrip('/')}"
            # Fetch detail page briefly to extract date and content snippet
            try:
                detail = self.session.get(source_url, timeout=20)
                if detail.status_code != 200:
                    continue
                dsoup = BeautifulSoup(detail.text, 'lxml')
                # Try common date pattern element
                date_text = ''
                date_el = dsoup.find(string=lambda s: s and ('Posted On:' in s or 'PIB' in s))
                if isinstance(date_el, str):
                    date_text = date_el
                # Simple fallback: now
                pub_date = datetime.now()
                # Convert rough date; real parsing could be added
                # Ministry detection heuristic
                ministry = 'Government of India'
                min_el = dsoup.find(string=lambda s: s and 'Ministry' in s)
                if isinstance(min_el, str):
                    ministry = min_el.strip().split(':')[-1].strip() or ministry
                # Content snippet
                para = dsoup.find('p')
                content = (para.get_text().strip() if para else '')
                if not content:
                    content = title
                if self._within_days(pub_date, days_back):
                    items.append({
                        'title': title,
                        'ministry': ministry,
                        'content': content,
                        'source_url': source_url,
                        'metadata': {
                            'publication_date': pub_date.isoformat(),
                            'source': 'PIB',
                        }
                    })
            except Exception:
                continue
        return items[:15]  # limit for performance

    def scrape_sebi_updates(self, days_back: int = 7) -> List[Dict[str, Any]]:
        """Scrape SEBI recent updates page for titles and links."""
        url = self.sources['sebi_updates']
        r = self.session.get(url, timeout=20)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, 'lxml')
        items: List[Dict[str, Any]] = []
        for a in soup.select('a'):
            title = (a.get_text() or '').strip()
            href = a.get('href')
            if not title or not href:
                continue
            if not href.startswith('http'):
                href = f"https://www.sebi.gov.in{href}"
            # Basic filter for relevant items
            if any(k in title.lower() for k in ['regulation', 'circular', 'guideline', 'amendment']):
                items.append({
                    'title': title,
                    'ministry': 'Securities and Exchange Board of India',
                    'content': title,
                    'source_url': href,
                    'metadata': {
                        'publication_date': datetime.now().isoformat(),
                        'source': 'SEBI'
                    }
                })
        return items[:15]
