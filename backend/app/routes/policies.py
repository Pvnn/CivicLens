from flask import Blueprint, request, jsonify, current_app
from app.models.policy import PolicyCard, UserComplaint, RTIRequest
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
import io
from urllib.parse import urlparse
from flask import send_file

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
        # Prefer entries created recently to avoid refetching on every load
        cached_policies = PolicyCard.query.filter(
            PolicyCard.created_at >= datetime.utcnow() - timedelta(days=1)
        ).order_by(PolicyCard.publication_date.desc()).all()

        if not cached_policies:
            # Fetch fresh
            fetcher = GovernmentPolicyFetcher()
            new_policies = fetcher.fetch_recent_policies(days_back)

            summarizer = PolicySummarizer()
            for policy_data in new_policies:
                existing_policy = PolicyCard.query.filter_by(
                    notification_number=policy_data['notification_number']
                ).first()
                if existing_policy:
                    continue

                summary_card = summarizer.generate_policy_card(
                    policy_data.get('original_text', ''),
                    policy_data['title']
                )
                if not summary_card:
                    continue

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

        policy_cards = [p.to_dict() for p in cached_policies]
        return jsonify({'success': True, 'count': len(policy_cards), 'policies': policy_cards})

    except Exception as e:
        logging.error(f"Error fetching policies: {e}")
        return jsonify({'success': False, 'error': 'Failed to fetch policy data'}), 500


def scrape_policy_from_url(url: str) -> str:
    """Extract main article text from a policy URL using newspaper3k, fallback to requests+BeautifulSoup."""
    try:
        if NEWSPAPER_AVAILABLE:
            art = Article(url)
            art.download(); art.parse()
            text = (art.text or '').strip()
            if text:
                return text
    except Exception:
        pass
    try:
        headers = {'User-Agent': os.getenv('SCRAPING_USER_AGENT', 'CivicLens-PolicyBot/1.0')}
        r = requests.get(url, timeout=20, headers=headers)
        if r.status_code != 200:
            return ''
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(r.text, 'lxml')
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
        summarizer = PolicySummarizer()
        new_count = 0
        for policy_data in policies:
            existing_policy = PolicyCard.query.filter_by(
                notification_number=policy_data['notification_number']
            ).first()
            if existing_policy:
                continue
            summary_card = summarizer.generate_policy_card(
                policy_data.get('original_text', ''),
                policy_data['title']
            )
            if not summary_card:
                continue
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
        return jsonify({'success': True, 'message': f'Refreshed {new_count} new policies', 'new_policies': new_count, 'total_checked': len(policies)})
    except Exception as e:
        logging.error(f"Error refreshing policies: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


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
        return jsonify({'success': True, 'live_analysis': True, 'timestamp': datetime.utcnow().isoformat(), 'gaps_analysis': gaps, 'citizen_summary': summary, 'data_source': 'REAL_TIME_GEMINI'})
    except Exception as e:
        logging.error(f"Live analysis error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@policies_bp.route('/refresh-all', methods=['POST'])
def refresh_all_policies():
    """Trigger complete refresh of all policy data using live scraping + Gemini."""
    try:
        service = EnhancedPolicyService()
        policies = service.process_weekly_policies(days_back=7)
        return jsonify({'success': True, 'policies_processed': len(policies), 'analysis_method': 'Live scraping + Gemini AI', 'last_update': datetime.utcnow().isoformat()})
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
        return jsonify({'success': True, 'gemini_api': 'CONFIGURED' if os.getenv('GEMINI_API_KEY') else 'MISSING_KEY', 'data_sources': verification, 'live_scraping': 'ENABLED', 'ai_analysis': 'GEMINI_POWERED'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@policies_bp.route('/<int:policy_id>', methods=['GET'])
def get_policy_details(policy_id):
    """Get detailed information for a specific policy"""
    try:
        policy = PolicyCard.query.get_or_404(policy_id)
        return jsonify({'success': True, 'policy': policy.to_dict()})
    except Exception:
        return jsonify({'success': False, 'error': 'Policy not found'}), 404


@policies_bp.route('/<int:policy_id>/gaps', methods=['GET'])
def get_policy_gaps(policy_id):
    """Get operational gaps for RTI generation"""
    try:
        policy = PolicyCard.query.get_or_404(policy_id)
        gaps = []
        if policy.missing_dates:
            gaps.append({'type': 'missing_dates', 'description': 'Implementation timeline not specified', 'rti_question': f'What is the specific implementation timeline for {policy.title}?'})
        if policy.missing_officer_info:
            gaps.append({'type': 'missing_officer_info', 'description': 'Responsible officer contact not provided', 'rti_question': f'Who is the responsible officer for implementing {policy.title} and what are their contact details?'})
        if policy.missing_urls:
            gaps.append({'type': 'missing_urls', 'description': 'Detailed guidelines or forms not linked', 'rti_question': f'Where can citizens access detailed implementation guidelines and required forms for {policy.title}?'})
        return jsonify({'success': True, 'policy_id': policy_id, 'title': policy.title, 'gaps': gaps, 'gap_count': len(gaps)})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@policies_bp.route('/search', methods=['GET'])
def search_policies():
    """Search policies by title, ministry, or content"""
    try:
        query = request.args.get('q', '').strip()
        ministry = request.args.get('ministry', '').strip()
        if not query and not ministry:
            return jsonify({'success': False, 'error': 'Search query or ministry filter required'}), 400
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
        return jsonify({'success': True, 'count': len(policies), 'policies': [p.to_dict() for p in policies]})
    except Exception as e:
        logging.error(f"Error searching policies: {e}")
        return jsonify({'success': False, 'error': 'Search failed'}), 500


@policies_bp.route('/ministries', methods=['GET'])
def get_ministries():
    """Get list of all ministries with policy counts"""
    try:
        ministries = db.session.query(
            PolicyCard.ministry,
            db.func.count(PolicyCard.id).label('count')
        ).group_by(PolicyCard.ministry).all()
        ministry_list = [{'name': ministry, 'policy_count': count} for ministry, count in ministries]
        return jsonify({'success': True, 'ministries': ministry_list})
    except Exception:
        return jsonify({'success': False, 'error': 'Failed to fetch ministries'}), 500


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
        return jsonify({'success': True, 'stats': {
            'total_policies': total_policies,
            'recent_policies': recent_policies,
            'policies_with_gaps': policies_with_gaps,
            'ministry_count': ministry_count,
            'gap_percentage': round((policies_with_gaps / total_policies * 100), 2) if total_policies > 0 else 0
        }})
    except Exception:
        return jsonify({'success': False, 'error': 'Failed to fetch statistics'}), 500

# --- RTI Blueprint and Endpoints ---
rti_bp = Blueprint('rti', __name__)

ALLOWED_DOMAINS = [d.strip() for d in os.getenv('ALLOWED_DOMAINS', '.gov.in,.nic.in,pib.gov.in,prsindia.org').split(',') if d.strip()]
RTI_CHARACTER_LIMIT = int(os.getenv('RTI_CHARACTER_LIMIT', '3000'))

def _is_allowed_government_url(url: str) -> bool:
    try:
        u = urlparse(url)
        host = (u.hostname or '').lower()
        return host and any(host.endswith(dom) for dom in ALLOWED_DOMAINS)
    except Exception:
        return False

@rti_bp.route('/submit-complaint', methods=['POST'])
def rti_submit_complaint():
    data = request.get_json(force=True, silent=True) or {}
    url = data.get('url', '').strip()
    complaint = data.get('complaint', '').strip()
    if not url or not complaint:
        return jsonify({'success': False, 'error': 'url and complaint are required'}), 400

    is_gov = _is_allowed_government_url(url)
    uc = UserComplaint(url=url, complaint_text=complaint, is_valid_government_url=is_gov,
                       validation_status='pending', validation_reason=None)
    db.session.add(uc)
    db.session.commit()
    return jsonify({'success': True, 'id': uc.id, 'is_valid_government_url': is_gov})

@rti_bp.route('/validate/<int:cid>', methods=['GET'])
def rti_validate(cid: int):
    uc = UserComplaint.query.get_or_404(cid)
    # Basic rule checks
    if not uc.is_valid_government_url:
        uc.validation_status = 'invalid'
        uc.validation_reason = 'URL is not a recognized government domain.'
        db.session.commit()
        return jsonify({'success': True, 'eligible': False, 'reason': uc.validation_reason})

    if len(uc.complaint_text) > RTI_CHARACTER_LIMIT:
        uc.validation_status = 'invalid'
        uc.validation_reason = f'Complaint exceeds character limit of {RTI_CHARACTER_LIMIT}.'
        db.session.commit()
        return jsonify({'success': True, 'eligible': False, 'reason': uc.validation_reason})

    # Gemini-based eligibility analysis
    try:
        from app.services.gemini_gap_analyzer import GeminiGapAnalyzer
        analyzer = GeminiGapAnalyzer()
        prompt = f"""
You are an RTI compliance checker. Determine if the user's complaint qualifies for an RTI (information request) under RTI Act, 2005.
URL: {uc.url}
COMPLAINT: {uc.complaint_text}
Criteria:
- Ask for information, not action/opinion.
- Is specific and answerable.
- Not seeking explanations/justifications; prefers records/documents/dates/procedures/contacts.
Respond with ONLY JSON (no markdown, no code fences), exactly in this schema: {{"eligible": true|false, "score": 0-100, "reason": "..."}}
"""
        res = analyzer.model.generate_content(prompt)
        
        raw = getattr(res, 'text', '')
        parsed = analyzer.parse_rti_validation_response(raw)
        eligible = bool(parsed.get('eligible', False))
        score = int(parsed.get('score', 0))
        reason = parsed.get('reason', 'AI validation did not provide a reason')
        uc.validation_status = 'valid' if eligible else 'invalid'
        uc.validation_reason = f'{reason} (score={score})'
        db.session.commit()
        return jsonify({'success': True, 'eligible': eligible, 'score': score, 'reason': uc.validation_reason})
    except Exception as e:
        logging.error(f'RTI validation AI error: {e}')
        uc.validation_status = 'valid'  # Fallback to allow generation for testing
        uc.validation_reason = 'AI validation failed; allowing for testing.'
        db.session.commit()
        return jsonify({'success': True, 'eligible': True, 'reason': uc.validation_reason, 'ai_error': str(e)})

@rti_bp.route('/generate/<int:cid>', methods=['POST'])
def rti_generate(cid: int):
    uc = UserComplaint.query.get_or_404(cid)
    if uc.validation_status not in ('valid', 'pending'):
        return jsonify({'success': False, 'error': 'Complaint not eligible. Run validation first.'}), 400

    try:
        from app.services.gemini_gap_analyzer import GeminiGapAnalyzer
        analyzer = GeminiGapAnalyzer()
        prompt = f"""
Draft a formal RTI (Right to Information) request under the RTI Act, 2005 for the complaint below.
URL: {uc.url}
COMPLAINT: {uc.complaint_text}
Requirements:
- Ask for specific information, not actions or opinions.
- Include references to RTI Act sections (e.g., Sec 2(f), Sec 6(1)).
- Be within {RTI_CHARACTER_LIMIT} characters.
- Provide bullet points of the exact information requested (dates, documents, procedures, contact details).
Return plain text only.
"""
        res = analyzer.model.generate_content(prompt)
        rti_text = (getattr(res, 'text', '') or '').strip()
        if not rti_text:
            raise ValueError('Empty RTI text from AI')

        # Basic compliance score heuristic
        score = 50
        low = rti_text.lower()
        if 'rti act' in low or 'right to information' in low:
            score += 15
        if 'section 6(1)' in low or 'sec 6(1)' in low:
            score += 10
        if len(rti_text) <= RTI_CHARACTER_LIMIT:
            score += 15
        if any(k in low for k in ['provide', 'furnish', 'copies of', 'certified copy']):
            score += 10
        score = min(score, 100)

        existing = RTIRequest.query.filter_by(complaint_id=uc.id).first()
        if existing:
            existing.rti_text = rti_text
            existing.compliance_score = score
            db.session.commit()
            rr = existing
        else:
            rr = RTIRequest(complaint_id=uc.id, rti_text=rti_text, compliance_score=score)
            db.session.add(rr)
            db.session.commit()

        return jsonify({'success': True, 'rti_id': rr.id, 'compliance_score': rr.compliance_score, 'rti_text': rr.rti_text})
    except Exception as e:
        logging.error(f'RTI generation error: {e}')
        return jsonify({'success': False, 'error': str(e)}), 500

@rti_bp.route('/download/<int:rid>', methods=['GET'])
def rti_download(rid: int):
    rr = RTIRequest.query.get_or_404(rid)
    # Generate PDF if not exists
    pdf_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'generated_pdfs')
    os.makedirs(pdf_dir, exist_ok=True)
    if not rr.pdf_path or not os.path.exists(rr.pdf_path):
        try:
            from reportlab.lib.pagesizes import A4
            from reportlab.pdfgen import canvas
            pdf_path = os.path.join(pdf_dir, f'rti_{rid}.pdf')
            c = canvas.Canvas(pdf_path, pagesize=A4)
            width, height = A4
            textobject = c.beginText(40, height - 40)
            textobject.setFont("Helvetica", 11)
            for line in rr.rti_text.splitlines():
                # naive wrap
                while len(line) > 110:
                    textobject.textLine(line[:110])
                    line = line[110:]
                textobject.textLine(line)
            c.drawText(textobject)
            c.showPage(); c.save()
            rr.pdf_path = pdf_path
            db.session.commit()
        except Exception as e:
            logging.error(f'PDF generation failed: {e}')
            return jsonify({'success': False, 'error': 'PDF generation failed'}), 500
    return send_file(rr.pdf_path, as_attachment=True, download_name=f'RTI_{rid}.pdf')
