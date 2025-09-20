import re
import logging
from datetime import datetime

class PolicySummarizer:
    def __init__(self):
        # For hackathon speed, using rule-based approach instead of heavy ML models
        self.change_keywords = ['amend', 'replace', 'effective', 'new', 'revised', 'update', 'modify']
        self.party_keywords = {
            'taxpayers': ['taxpayer', 'tax', 'income', 'gst', 'revenue'],
            'businesses': ['company', 'business', 'enterprise', 'corporate', 'msme'],
            'citizens': ['citizen', 'public', 'individual', 'person'],
            'students': ['student', 'education', 'school', 'university'],
            'farmers': ['farmer', 'agriculture', 'crop', 'rural'],
            'banks': ['bank', 'financial', 'rbi', 'sebi', 'finance']
        }
        
    def generate_policy_card(self, policy_text, title):
        """Generate structured policy card with bilingual summaries"""
        try:
            # Extract key information using NLP
            analysis = self._analyze_policy_text(policy_text, title)
            
            # Generate English summary
            english_summary = self._create_english_summary(policy_text, analysis, title)
            
            # Generate Nepali translation (simplified for hackathon)
            nepali_summary = self._translate_to_nepali(english_summary)
            
            # Structure the response
            policy_card = {
                'summary_english': english_summary,
                'summary_nepali': nepali_summary,
                'what_changed': analysis['what_changed'],
                'who_affected': analysis['who_affected'],
                'what_to_do': analysis['what_to_do']
            }
            
            return policy_card
            
        except Exception as e:
            logging.error(f"Error in policy summarization: {e}")
            return {
                'summary_english': f"Policy update: {title}",
                'summary_nepali': f"नीति अपडेट: {title}",
                'what_changed': "Policy changes not clearly specified",
                'who_affected': "General public",
                'what_to_do': "Follow new regulations and compliance requirements"
            }
    
    def _analyze_policy_text(self, text, title):
        """Extract structured information from policy text"""
        analysis = {
            'what_changed': self._extract_changes(text, title),
            'who_affected': self._extract_affected_parties(text, title),
            'what_to_do': self._extract_actions(text, title)
        }
        return analysis
    
    def _extract_changes(self, text, title):
        """Extract what has changed in the policy"""
        changes = []
        
        # Look for change indicators in text
        for keyword in self.change_keywords:
            pattern = rf'{keyword}[^.]*'
            matches = re.findall(pattern, text, re.IGNORECASE)
            changes.extend(matches[:2])  # Limit to 2 matches per keyword
        
        # If no specific changes found, infer from title
        if not changes:
            if 'GST' in title:
                changes.append("GST rates and exemptions have been updated")
            elif 'Income Tax' in title or 'Income-Tax' in title:
                changes.append("Income tax provisions and procedures have been modified")
            elif 'SEBI' in title:
                changes.append("Securities regulations and compliance requirements updated")
            elif 'Education' in title:
                changes.append("Educational policies and implementation guidelines revised")
            elif 'Land' in title:
                changes.append("Land records and property documentation procedures updated")
            else:
                changes.append("Policy provisions have been updated")
        
        return '. '.join(changes[:3]) if changes else "Policy changes not clearly specified"
    
    def _extract_affected_parties(self, text, title):
        """Extract who is affected by the policy"""
        affected = set()
        
        # Check text for party keywords
        text_lower = text.lower()
        title_lower = title.lower()
        combined_text = f"{text_lower} {title_lower}"
        
        for party, keywords in self.party_keywords.items():
            if any(keyword in combined_text for keyword in keywords):
                affected.add(party)
        
        # Infer from title if nothing found
        if not affected:
            if any(word in title_lower for word in ['gst', 'tax', 'income']):
                affected.add('taxpayers')
            elif any(word in title_lower for word in ['sebi', 'securities', 'listing']):
                affected.add('businesses')
            elif any(word in title_lower for word in ['education', 'student']):
                affected.add('students')
            elif any(word in title_lower for word in ['land', 'property']):
                affected.add('citizens')
            else:
                affected.add('citizens')
        
        return ', '.join(affected) if affected else "General public"
    
    def _extract_actions(self, text, title):
        """Extract required actions"""
        actions = []
        
        # Look for action patterns
        action_patterns = [
            r'shall[^.]*',
            r'must[^.]*',
            r'required to[^.]*',
            r'need to[^.]*',
            r'should[^.]*'
        ]
        
        for pattern in action_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            actions.extend(matches[:2])
        
        # Default actions based on policy type
        if not actions:
            if 'GST' in title:
                actions.append("Update GST compliance procedures")
                actions.append("Review exemption eligibility for applicable items")
            elif 'Income Tax' in title:
                actions.append("Prepare for new tax filing procedures")
                actions.append("Update accounting systems for new provisions")
            elif 'SEBI' in title:
                actions.append("Review and update compliance frameworks")
                actions.append("Ensure adherence to new disclosure requirements")
            elif 'Education' in title:
                actions.append("Implement new curriculum guidelines")
                actions.append("Train staff on updated procedures")
            else:
                actions.append("Review policy changes and ensure compliance")
                actions.append("Update internal procedures as required")
        
        return '. '.join(actions[:3]) if actions else "Follow new regulations and compliance requirements"
    
    def _create_english_summary(self, text, analysis, title):
        """Create a concise English summary"""
        summary_parts = []
        
        # Add title context
        if 'GST' in title:
            summary_parts.append("GST notification updates tax exemptions and rates.")
        elif 'Income Tax' in title:
            summary_parts.append("Income Tax Act introduces new provisions and procedures.")
        elif 'SEBI' in title:
            summary_parts.append("SEBI regulations update compliance requirements for listed entities.")
        elif 'Education' in title:
            summary_parts.append("Education policy implements new curriculum and assessment frameworks.")
        elif 'Land' in title:
            summary_parts.append("Land records modernization introduces digital verification systems.")
        else:
            summary_parts.append(f"Policy update: {title[:100]}...")
        
        # Add key changes
        if analysis['what_changed'] != "Policy changes not clearly specified":
            summary_parts.append(f"Key changes: {analysis['what_changed'][:150]}...")
        
        # Add affected parties
        summary_parts.append(f"Affects: {analysis['who_affected']}")
        
        return ' '.join(summary_parts)[:300] + "..." if len(' '.join(summary_parts)) > 300 else ' '.join(summary_parts)
    
    def _translate_to_nepali(self, text):
        """Translate to Nepali (simplified mapping for hackathon)"""
        # Basic word mapping for common policy terms
        translations = {
            'GST': 'जीएसटी',
            'tax': 'कर',
            'Income Tax': 'आयकर',
            'policy': 'नीति',
            'notification': 'सूचना',
            'update': 'अपडेट',
            'changes': 'परिवर्तन',
            'citizens': 'नागरिक',
            'taxpayers': 'करदाता',
            'businesses': 'व्यवसाय',
            'students': 'विद्यार्थी',
            'education': 'शिक्षा',
            'compliance': 'अनुपालना',
            'requirements': 'आवश्यकताहरू',
            'effective': 'प्रभावकारी',
            'implementation': 'कार्यान्वयन'
        }
        
        nepali_text = text
        for english, nepali in translations.items():
            nepali_text = nepali_text.replace(english, nepali)
        
        # If no translations found, provide generic Nepali message
        if nepali_text == text:
            return f"नीति अपडेट: {text[:50]}... (पूर्ण नेपाली अनुवाद उपलब्ध छैन)"
        
        return nepali_text
    
    def identify_gaps(self, policy_data):
        """Identify missing information gaps for RTI generation"""
        gaps = []
        
        if policy_data.get('missing_dates', True):
            gaps.append({
                'type': 'missing_dates',
                'description': 'Implementation timeline not specified',
                'rti_question': f'What is the specific implementation timeline for {policy_data.get("title", "this policy")}?'
            })
        
        if policy_data.get('missing_officer_info', True):
            gaps.append({
                'type': 'missing_officer_info',
                'description': 'Responsible officer contact not provided',
                'rti_question': f'Who is the responsible officer for implementing {policy_data.get("title", "this policy")} and what are their contact details?'
            })
        
        if policy_data.get('missing_urls', True):
            gaps.append({
                'type': 'missing_urls',
                'description': 'Detailed guidelines or forms not linked',
                'rti_question': f'Where can citizens access detailed implementation guidelines and required forms for {policy_data.get("title", "this policy")}?'
            })
        
        return gaps
