from flask import Blueprint, request, jsonify, current_app
from app.models.policy import PolicyCard
from app.services.policy_fetcher import GovernmentPolicyFetcher
from app.services.policy_summarizer import PolicySummarizer
from app.services.policy_service import EnhancedPolicyService
from app.services.gemini_gap_analyzer import GeminiGapAnalyzer
from app.services.live_policy_fetcher import LiveGovernmentDataFetcher
from app import db
from datetime import datetime, timedelta
import logging
import os
import requests

try:
    from newspaper import Article
    NEWSPAPER_AVAILABLE = True
except Exception:
    NEWSPAPER_AVAILABLE = False

policies_bp = Blueprint('policies', __name__)

@policies_bp.route('/recent', methods=['GET'])
def get_recent_policies():
    """Get recent policy cards from this week"""
    try:
        days_back = request.args.get('days', 7, type=int)
        
        # Check if we have cached data
        cached_policies = PolicyCard.query.filter(
            PolicyCard.created_at >= datetime.utcnow() - timedelta(days=1)
        ).order_by(PolicyCard.publication_date.desc()).all()
        
        if not cached_policies:
            # Fetch new data
            fetcher = GovernmentPolicyFetcher()
            new_policies = fetcher.fetch_recent_policies(days_back)
            
            # Process and save
            summarizer = PolicySummarizer()
            for policy_data in new_policies:
                existing_policy = PolicyCard.query.filter_by(
                    notification_number=policy_data['notification_number']
                ).first()
                
                if not existing_policy:
                    # Generate AI summary
                    summary_card = summarizer.generate_policy_card(
                        policy_data.get('original_text', ''),
                        policy_data['title']
                    )
                    
                    if summary_card:
                        policy = PolicyCard(
                            title=policy_data['title'],
                            ministry=policy_data['ministry'],
                            notification_number=policy_data['notification_number'],
                            publication_date=policy_data['publication_date'],
                            effective_date=policy_data.get('effective_date'),
                            original_text=policy_data.get('original_text'),
                            summary_english=summary_card['summary_english'],
                            summary_nepali=summary_card['summary_nepali'],
                            what_changed=summary_card['what_changed'],
                            who_affected=summary_card['who_affected'],
                            what_to_do=summary_card['what_to_do'],
                            source_url=policy_data.get('source_url'),
                            gazette_type=policy_data.get('gazette_type', 'Ordinary'),
                            status=policy_data.get('status', 'New'),
                            missing_dates=policy_data.get('missing_dates', False),
                            missing_officer_info=policy_data.get('missing_officer_info', False),
                            missing_urls=policy_data.get('missing_urls', False)
                        )
                        db.session.add(policy)
            
            db.session.commit()
            cached_policies = PolicyCard.query.filter(
                PolicyCard.publication_date >= datetime.utcnow() - timedelta(days=days_back)
            ).order_by(PolicyCard.publication_date.desc()).all()
        
        # Format response
        policy_cards = [policy.to_dict() for policy in cached_policies]
        
        return jsonify({
            'success': True,
            'count': len(policy_cards),
            'policies': policy_cards
        })
        
    except Exception as e:
        logging.error(f"Error fetching policies: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to fetch policy data'
        }), 500

def scrape_policy_from_url(url: str) -> str:
    """Extract main article text from a policy URL using newspaper3k fallback to requests+BeautifulSoup."""
    try:
        if NEWSPAPER_AVAILABLE:
            art = Article(url)
            art.download()
            art.parse()
            text = (art.text or '').strip()
            if text:
                return text
    except Exception:
        pass
    # Fallback
    try:
        headers = {'User-Agent': os.getenv('SCRAPING_USER_AGENT', 'CivicLens-PolicyBot/1.0')}
        r = requests.get(url, timeout=20, headers=headers)
        if r.status_code != 200:
            return ''
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(r.text, 'lxml')
        # Extract paragraphs and join
        paras = [p.get_text(strip=True) for p in soup.find_all('p')]
        return '\n'.join(paras[:100])
    except Exception:
        return ''

@policies_bp.route('/refresh', methods=['POST'])
def refresh_policies():
    """Manually refresh policy data"""
    try:
        fetcher = GovernmentPolicyFetcher()
        policies = fetcher.fetch_recent_policies(days_back=7)
        
        # Process new policies
        summarizer = PolicySummarizer()
        new_count = 0
        
        for policy_data in policies:
            existing_policy = PolicyCard.query.filter_by(
                notification_number=policy_data['notification_number']
            ).first()
            
            if not existing_policy:
                summary_card = summarizer.generate_policy_card(
                    policy_data.get('original_text', ''),
                    policy_data['title']
                )
                
                if summary_card:
                    policy = PolicyCard(
                        title=policy_data['title'],
                        ministry=policy_data['ministry'],
                        notification_number=policy_data['notification_number'],
                        publication_date=policy_data['publication_date'],
                        effective_date=policy_data.get('effective_date'),
                        original_text=policy_data.get('original_text'),
                        summary_english=summary_card['summary_english'],
                        summary_nepali=summary_card['summary_nepali'],
                        what_changed=summary_card['what_changed'],
                        who_affected=summary_card['who_affected'],
                        what_to_do=summary_card['what_to_do'],
                        source_url=policy_data.get('source_url'),
                        gazette_type=policy_data.get('gazette_type', 'Ordinary'),
                        status=policy_data.get('status', 'New'),
                        missing_dates=policy_data.get('missing_dates', False),
                        missing_officer_info=policy_data.get('missing_officer_info', False),
                        missing_urls=policy_data.get('missing_urls', False)
                    )
                    db.session.add(policy)
                    new_count += 1
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Refreshed {new_count} new policies',
            'new_policies': new_count,
            'total_checked': len(policies)
        })
        
    except Exception as e:
        logging.error(f"Error refreshing policies: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@policies_bp.route('/analyze-live', methods=['POST'])
def analyze_live_policy():
    """Real-time policy analysis using Gemini."""
    try:
        data = request.get_json(force=True, silent=True) or {}
        policy_text = data.get('policy_text')
        policy_url = data.get('source_url')
        metadata = data.get('metadata', {})

        if policy_url and not policy_text:
            policy_text = scrape_policy_from_url(policy_url)

        if not policy_text:
            return jsonify({'success': False, 'error': 'No policy text provided'}), 400

        analyzer = GeminiGapAnalyzer()
        gaps = analyzer.analyze_policy_gaps(policy_text, metadata)
        summary = analyzer.generate_policy_summary(policy_text)

        return jsonify({
            'success': True,
            'live_analysis': True,
            'timestamp': datetime.utcnow().isoformat(),
            'gaps_analysis': gaps,
            'citizen_summary': summary,
            'data_source': 'REAL_TIME_GEMINI'
        })
    except Exception as e:
        logging.error(f"Live analysis error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@policies_bp.route('/refresh-all', methods=['POST'])
def refresh_all_policies():
    """Trigger complete refresh of all policy data using live scraping + Gemini."""
    try:
        service = EnhancedPolicyService()
        policies = service.process_weekly_policies(days_back=7)
        return jsonify({
            'success': True,
            'policies_processed': len(policies),
            'analysis_method': 'Live scraping + Gemini AI',
            'last_update': datetime.utcnow().isoformat()
        })
    except Exception as e:
        logging.error(f"Refresh-all error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@policies_bp.route('/verify-data-sources', methods=['GET'])
def verify_data_sources():
    """Show which data sources are working and Gemini configuration status."""
    try:
        fetcher = LiveGovernmentDataFetcher()
        verification = {}
        for source_name, url in fetcher.sources.items():
            try:
                resp = requests.get(url, timeout=10)
                verification[source_name] = {
                    'status': 'WORKING' if resp.status_code == 200 else 'ERROR',
                    'last_checked': datetime.utcnow().isoformat(),
                    'response_time': resp.elapsed.total_seconds(),
                    'status_code': resp.status_code
                }
            except Exception:
                verification[source_name] = {'status': 'FAILED'}

        return jsonify({
            'success': True,
            'gemini_api': 'CONFIGURED' if os.getenv('GEMINI_API_KEY') else 'MISSING_KEY',
            'data_sources': verification,
            'live_scraping': 'ENABLED',
            'ai_analysis': 'GEMINI_POWERED'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@policies_bp.route('/<int:policy_id>', methods=['GET'])
def get_policy_details(policy_id):
    """Get detailed information for a specific policy"""
    try:
        policy = PolicyCard.query.get_or_404(policy_id)
        return jsonify({
            'success': True,
            'policy': policy.to_dict()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Policy not found'
        }), 404

@policies_bp.route('/<int:policy_id>/gaps', methods=['GET'])
def get_policy_gaps(policy_id):
    """Get operational gaps for RTI generation"""
    try:
        policy = PolicyCard.query.get_or_404(policy_id)
        
        gaps = []
        if policy.missing_dates:
            gaps.append({
                'type': 'missing_dates',
                'description': 'Implementation timeline not specified',
                'rti_question': f'What is the specific implementation timeline for {policy.title}?'
            })
        
        if policy.missing_officer_info:
            gaps.append({
                'type': 'missing_officer_info',
                'description': 'Responsible officer contact not provided',
                'rti_question': f'Who is the responsible officer for implementing {policy.title} and what are their contact details?'
            })
        
        if policy.missing_urls:
            gaps.append({
                'type': 'missing_urls',
                'description': 'Detailed guidelines or forms not linked',
                'rti_question': f'Where can citizens access detailed implementation guidelines and required forms for {policy.title}?'
            })
        
        return jsonify({
            'success': True,
            'policy_id': policy_id,
            'title': policy.title,
            'gaps': gaps,
            'gap_count': len(gaps)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@policies_bp.route('/search', methods=['GET'])
def search_policies():
    """Search policies by title, ministry, or content"""
    try:
        query = request.args.get('q', '').strip()
        ministry = request.args.get('ministry', '').strip()
        
        if not query and not ministry:
            return jsonify({
                'success': False,
                'error': 'Search query or ministry filter required'
            }), 400
        
        # Build search query
        search_query = PolicyCard.query
        
        if query:
            search_query = search_query.filter(
                db.or_(
                    PolicyCard.title.contains(query),
                    PolicyCard.summary_english.contains(query),
                    PolicyCard.what_changed.contains(query),
                    PolicyCard.who_affected.contains(query)
                )
            )
        
        if ministry:
            search_query = search_query.filter(PolicyCard.ministry.contains(ministry))
        
        policies = search_query.order_by(PolicyCard.publication_date.desc()).limit(20).all()
        
        return jsonify({
            'success': True,
            'count': len(policies),
            'policies': [policy.to_dict() for policy in policies]
        })
        
    except Exception as e:
        logging.error(f"Error searching policies: {e}")
        return jsonify({
            'success': False,
            'error': 'Search failed'
        }), 500

@policies_bp.route('/ministries', methods=['GET'])
def get_ministries():
    """Get list of all ministries with policy counts"""
    try:
        ministries = db.session.query(
            PolicyCard.ministry,
            db.func.count(PolicyCard.id).label('count')
        ).group_by(PolicyCard.ministry).all()
        
        ministry_list = [
            {'name': ministry, 'policy_count': count}
            for ministry, count in ministries
        ]
        
        return jsonify({
            'success': True,
            'ministries': ministry_list
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to fetch ministries'
        }), 500

@policies_bp.route('/stats', methods=['GET'])
def get_policy_stats():
    """Get policy statistics"""
    try:
        total_policies = PolicyCard.query.count()
        recent_policies = PolicyCard.query.filter(
            PolicyCard.publication_date >= datetime.utcnow() - timedelta(days=7)
        ).count()
        
        policies_with_gaps = PolicyCard.query.filter(
            db.or_(
                PolicyCard.missing_dates == True,
                PolicyCard.missing_officer_info == True,
                PolicyCard.missing_urls == True
            )
        ).count()
        
        ministry_count = db.session.query(PolicyCard.ministry).distinct().count()
        
        return jsonify({
            'success': True,
            'stats': {
                'total_policies': total_policies,
                'recent_policies': recent_policies,
                'policies_with_gaps': policies_with_gaps,
                'ministry_count': ministry_count,
                'gap_percentage': round((policies_with_gaps / total_policies * 100), 2) if total_policies > 0 else 0
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to fetch statistics'
        }), 500
