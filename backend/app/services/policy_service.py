from typing import List
from datetime import datetime
import logging

from app.services.live_policy_fetcher import LiveGovernmentDataFetcher
from app.services.gemini_gap_analyzer import GeminiGapAnalyzer
from app.models.policy import PolicyCard
from app import db

class EnhancedPolicyService:
    def __init__(self):
        self.fetcher = LiveGovernmentDataFetcher()
        self.gap_analyzer = GeminiGapAnalyzer()

    def process_weekly_policies(self, days_back: int = 7) -> List[PolicyCard]:
        """Complete pipeline: Fetch → Analyze → Store (synchronous for simplicity)."""
        raw_policies = self.fetcher.fetch_weekly_updates(days_back)
        processed: List[PolicyCard] = []

        for raw in raw_policies:
            try:
                title = raw.get('title')
                ministry = raw.get('ministry', 'Government of India')
                content = raw.get('content') or title
                source_url = raw.get('source_url')

                # Gemini gap analysis and summary
                gap_analysis = self.gap_analyzer.analyze_policy_gaps(
                    content,
                    {"title": title, "ministry": ministry}
                )
                summary = self.gap_analyzer.generate_policy_summary(content)

                # Map Gemini outputs into existing schema (no schema changes)
                summary_en = summary.get('english') or f"Policy update: {title}"
                summary_hi = summary.get('hindi') or "हिंदी सारांश उपलब्ध नहीं"

                # Approximate missing flags from gap analysis if available
                def _flag_contains(gtype: str) -> bool:
                    if not isinstance(gap_analysis, dict):
                        return False
                    all_lists = []
                    for k in ['critical_gaps', 'high_priority_gaps', 'medium_priority_gaps']:
                        lst = gap_analysis.get(k)
                        if isinstance(lst, list):
                            all_lists.extend(lst)
                    joined = str(all_lists).lower()
                    return gtype in joined

                missing_dates = _flag_contains('temporal')
                missing_officer = _flag_contains('contact')
                missing_urls = False  # We have a source URL for scraped items

                # Check duplicate by notification_number (not available) or title+source
                exists = PolicyCard.query.filter(
                    PolicyCard.title == title,
                    PolicyCard.source_url == source_url
                ).first()
                if exists:
                    continue

                policy = PolicyCard(
                    title=title,
                    ministry=ministry,
                    notification_number=None,
                    publication_date=datetime.fromisoformat(raw['metadata']['publication_date']) if raw.get('metadata', {}).get('publication_date') else datetime.utcnow(),
                    original_text=content,
                    summary_english=summary_en,
                    summary_nepali=summary_hi,  # storing Hindi in Nepali field as placeholder
                    what_changed=None,
                    who_affected=None,
                    what_to_do=None,
                    source_url=source_url,
                    gazette_type='Ordinary',
                    status='New',
                    missing_dates=missing_dates,
                    missing_officer_info=missing_officer,
                    missing_urls=missing_urls
                )
                db.session.add(policy)
                processed.append(policy)
            except Exception as e:
                logging.error(f"Failed to process policy '{raw.get('title','')}' : {e}")
                continue

        db.session.commit()
        return processed
