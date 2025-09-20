import os
import json
from datetime import datetime
import logging
from typing import Dict, Any

import google.generativeai as genai
import re


class GeminiGapAnalyzer:
    """Wrapper around Google Gemini for gap analysis and summaries."""

    def __init__(self):
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise RuntimeError('GEMINI_API_KEY missing. Set it in your environment or .env file.')
        genai.configure(api_key=api_key)
        # Model name configurable; default to fast flash model
        model_name = os.getenv('GEMINI_MODEL', 'gemini-2.0-flash')
        self.model = genai.GenerativeModel(model_name)

    def analyze_policy_gaps(self, policy_text: str, policy_metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Use Gemini to intelligently identify policy implementation gaps.
        Returns a dict as specified in the prompt contract.
        """
        gap_analysis_prompt = f"""
You are an expert policy analyst specializing in Indian government regulations. Analyze this policy document for implementation gaps that would prevent citizens from taking action.

POLICY DOCUMENT:
Title: {policy_metadata.get('title', 'Unknown')}
Ministry: {policy_metadata.get('ministry', 'Unknown')}
Text: {policy_text}

ANALYSIS FRAMEWORK:
1. TEMPORAL GAPS - Missing time-sensitive information:
   - Implementation dates/deadlines
   - Application windows
   - Compliance timelines
   - Review/renewal periods

2. CONTACT GAPS - Missing responsible authorities:
   - Implementing officer details
   - Department contact information
   - Helpline/support channels
   - Appeal mechanisms

3. PROCEDURAL GAPS - Missing process clarity:
   - Application/compliance procedures
   - Required documents/forms
   - Fee structures
   - Processing timelines

4. JURISDICTIONAL GAPS - Missing scope clarity:
   - Geographic applicability
   - Affected entity categories
   - Exemption criteria
   - Territorial boundaries

For each identified gap, provide:
- Gap Type (Critical/High/Medium/Low)
- Specific Missing Information
- Impact on Citizens
- RTI Question Template

Format response STRICTLY as minified JSON object with fields:
{{
  "overall_completeness_score": 0-100,
  "critical_gaps": [],
  "high_priority_gaps": [],
  "medium_priority_gaps": [],
  "rti_questions": [],
  "citizen_action_blocked": true,
  "analysis_confidence": 0-100
}}
"""
        try:
            response = self.model.generate_content(gap_analysis_prompt)
            return self._parse_gemini_response(response.text)
        except Exception as e:
            logging.error(f"Gemini gap analysis failed: {e}")
            return {"error": str(e), "fallback": True}

    def generate_policy_summary(self, policy_text: str) -> Dict[str, Any]:
        """Generate citizen-friendly English and Hindi summaries."""
        summary_prompt = f"""
Create a citizen-friendly summary of this government policy in simple language.

POLICY TEXT: {policy_text}

Create summaries in this format:
ENGLISH SUMMARY (150 words max):
- What changed: [specific changes]
- Who's affected: [target groups]
- What to do: [citizen actions required]
- Key dates: [important deadlines]

HINDI SUMMARY (हिंदी में सारांश):
[Hindi translation of key points]

ACTIONABILITY SCORE: X/10 (how easily can citizens act on this?)
COMPLEXITY LEVEL: [Simple/Medium/Complex]
"""
        try:
            response = self.model.generate_content(summary_prompt)
            return self._parse_summary_response(response.text)
        except Exception as e:
            logging.error(f"Gemini summary failed: {e}")
            return {"error": str(e), "fallback": True}

    def _parse_gemini_response(self, response_text: str) -> Dict[str, Any]:
        """Parse structured JSON response from Gemini robustly.
        Handles code fences, extra prose, and extracts the first balanced JSON object.
        """
        if not response_text:
            return {"error": "Empty response from Gemini."}
        text = response_text.strip()

        # 1) Remove leading/trailing code fences if present (```json ... ``` or ``` ... ```)
        if text.startswith('```'):
            lines = text.splitlines()
            # Drop first fence line
            if lines and lines[0].startswith('```'):
                lines = lines[1:]
            # Drop trailing fence line if present
            if lines and lines[-1].startswith('```'):
                lines = lines[:-1]
            text = '\n'.join(lines).strip()
            # Some models include language tag like 'json' on first line
            if text.lower().startswith('json'):
                text = text.split('\n', 1)[1] if '\n' in text else ''

        # 2) If text looks like pure JSON, try loading directly
        direct = text.strip()
        if direct.startswith('{') and direct.rstrip().endswith('}'):
            try:
                data = json.loads(direct)
                if 'overall_completeness_score' in data:
                    return data
            except Exception:
                pass

        # 3) Extract the first balanced JSON object from the text
        def extract_balanced_json(s: str) -> str:
            start = s.find('{')
            if start == -1:
                return ''
            depth = 0
            in_str = False
            esc = False
            for i in range(start, len(s)):
                ch = s[i]
                if in_str:
                    if esc:
                        esc = False
                    elif ch == '\\':
                        esc = True
                    elif ch == '"':
                        in_str = False
                else:
                    if ch == '"':
                        in_str = True
                    elif ch == '{':
                        depth += 1
                    elif ch == '}':
                        depth -= 1
                        if depth == 0:
                            return s[start:i+1]
            return ''

        candidate = extract_balanced_json(response_text)
        if candidate:
            try:
                data = json.loads(candidate)
                if 'overall_completeness_score' in data:
                    return data
            except Exception:
                pass

        return {"error": "Failed to parse JSON", "raw": response_text}

    def _parse_summary_response(self, response_text: str) -> Dict[str, Any]:
        """Return a dict with english and hindi fields using simple parsing."""
        result = {"english": "", "hindi": "", "actionability": None, "complexity": None}
        if not response_text:
            return result
        text = response_text.strip()
        # Heuristic parsing
        # Split on lines, accumulate sections
        lines = [l.strip() for l in text.splitlines() if l.strip()]
        section = None
        buf = []
        for line in lines:
            low = line.lower()
            if 'english summary' in low:
                if section and buf:
                    result[section] = '\n'.join(buf).strip()
                section = 'english'
                buf = []
                continue
            if 'hindi summary' in low or 'हिंदी' in line:
                if section and buf:
                    result[section] = '\n'.join(buf).strip()
                section = 'hindi'
                buf = []
                continue
            if 'actionability score' in low:
                # Prefer X/10 pattern; fallback to first integer
                m = re.search(r'(\d+)\s*/\s*10', line)
                try:
                    if m:
                        result['actionability'] = int(m.group(1))
                    else:
                        m2 = re.search(r'(\d+)', line)
                        if m2:
                            result['actionability'] = int(m2.group(1))
                except Exception:
                    pass
            if 'complexity level' in low:
                if ':' in line:
                    val = line.split(':', 1)[1].strip()
                    # Clean trailing punctuation/parenthetical notes
                    val = re.sub(r'[\*`"]', '', val).strip()
                    result['complexity'] = val
            if section:
                buf.append(line)
        if section and buf:
            result[section] = '\n'.join(buf).strip()
        return result

    # --- Generic JSON extraction helpers for simple prompts (e.g., RTI validation) ---
    def _strip_code_fences(self, text: str) -> str:
        t = text.strip()
        if t.startswith('```'):
            lines = t.splitlines()
            if lines and lines[0].startswith('```'):
                lines = lines[1:]
            if lines and lines[-1].startswith('```'):
                lines = lines[:-1]
            t = '\n'.join(lines).strip()
            if t.lower().startswith('json'):
                t = t.split('\n', 1)[1] if '\n' in t else ''
        return t

    def _extract_first_json_object(self, text: str) -> str:
        s = text
        start = s.find('{')
        if start == -1:
            return ''
        depth, in_str, esc = 0, False, False
        for i in range(start, len(s)):
            ch = s[i]
            if in_str:
                if esc:
                    esc = False
                elif ch == '\\':
                    esc = True
                elif ch == '"':
                    in_str = False
            else:
                if ch == '"':
                    in_str = True
                elif ch == '{':
                    depth += 1
                elif ch == '}':
                    depth -= 1
                    if depth == 0:
                        return s[start:i+1]
        return ''

    def parse_json_with_keys(self, response_text: str, required_keys) -> Dict[str, Any]:
        """Extract the first JSON object and ensure it contains required keys."""
        if not response_text:
            return {"error": "Empty response"}
        text = self._strip_code_fences(response_text)
        # direct
        if text.startswith('{') and text.endswith('}'):
            try:
                data = json.loads(text)
                if all(k in data for k in required_keys):
                    return data
            except Exception:
                pass
        # balanced extraction
        cand = self._extract_first_json_object(response_text)
        if cand:
            try:
                data = json.loads(cand)
                if all(k in data for k in required_keys):
                    return data
            except Exception:
                pass
        return {"error": "Failed to parse expected JSON", "raw": response_text}

    def parse_rti_validation_response(self, response_text: str) -> Dict[str, Any]:
        """Parse Gemini response for RTI validation prompt into eligible/score/reason."""
        parsed = self.parse_json_with_keys(response_text, ["eligible", "score", "reason"])
        if 'error' not in parsed:
            # Normalize types
            try:
                parsed['eligible'] = bool(parsed['eligible'])
            except Exception:
                parsed['eligible'] = str(parsed.get('eligible', '')).strip().lower() in ('true', 'yes', '1')
            try:
                parsed['score'] = int(parsed['score'])
            except Exception:
                # Fallback: extract first integer
                m = re.search(r'(\d+)', str(parsed.get('score', '0')))
                parsed['score'] = int(m.group(1)) if m else 0
            parsed['reason'] = str(parsed.get('reason', '')) or 'No reason provided'
            return parsed

        # Heuristic fallback from prose
        text = response_text or ''
        low = text.lower()
        eligible = 'eligible' in low and ('not eligible' not in low and 'ineligible' not in low)
        mscore = re.search(r'(\d{1,3})\s*(?:/\s*100)?', low)
        score = int(mscore.group(1)) if mscore else 0
        reason = 'Unable to parse AI response'
        mreason = re.search(r'reason\s*[:\-]\s*(.+)', text, re.IGNORECASE)
        if mreason:
            reason = mreason.group(1).strip()
        return {"eligible": eligible, "score": score, "reason": reason}
