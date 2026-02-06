"""
Enforcement Engine for TriAI Council Mode.
Responsible for auditing AI responses against Truth Contracts and detecting adherence to strict epistemic standards.
"""

import re
from typing import Dict, List, Any, Tuple, Optional

class EnforcementEngine:
    def __init__(self):
        # Starting credibility is 100 for all models
        self.credibility_scores = {
            "openai": 100,
            "anthropic": 100,
            "google": 100,
            "perplexity": 100
        }
        self.interrogation_history = {m: [] for m in self.credibility_scores}
        
        # "Corporate Speak" that indicates low-density thought
        self.generic_verbs = {
            "leverage", "optimize", "synergize", "balance", 
            "enhance", "facilitate", "empower", "orchestrate",
            "streamline", "revolutionize", "transform", "align",
            "foster", "cultivate", "harness", "navigate"
        }
        
        # Anchoring terms that legitimize a number
        self.anchors = {
            "source", "citation", "report", "study", "analysis", 
            "derived", "range", "estimated", "projected", "margin",
            "confidence", "probability", "approx", "historic", "case study"
        }

    def analyze_response(self, text: str, role_name: str, model_name: str, contract: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Analyzes a single AI response for reliability violations.
        Returns a dict containing violations, scores, and updated credibility.
        """
        violations = []
        warnings = []
        score_penalty = 0
        
        lower_text = text.lower()
        
        # 1. Generic Verb Detection (The "Fluff" Filter)
        # We count unique generic verbs used
        words = re.findall(r'\b\w+\b', lower_text)
        found_generics = [word for word in words if word in self.generic_verbs]
        unique_generics = list(set(found_generics))
        
        if len(unique_generics) >= 3:
            warnings.append(f"HIGH_FLUFF_DENSITY: Used {len(unique_generics)} distinct generic verbs ({', '.join(unique_generics[:3])}...)")
            score_penalty += 2
            
        # 2. Unanchored Number Detection (The "Precision" Filter)
        # Regex for percentages: 23%, 23.5%
        # Regex for currency: $500, $5m, $50k
        percentage_matches = re.finditer(r'\b\d+(\.\d+)?%', text)
        currency_matches = re.finditer(r'\$\d+(?:,\d+)*(?:\.\d+)?(?:k|m|b|t)?\b', text, re.IGNORECASE)
        
        all_matches = list(percentage_matches) + list(currency_matches)
        
        for match in all_matches:
            start, end = match.span()
            # Look at a window of 50 chars before and after
            window_start = max(0, start - 60)
            window_end = min(len(text), end + 60)
            context = text[window_start:window_end].lower()
            
            # Check if any anchor word appears in context
            has_anchor = any(anchor in context for anchor in self.anchors)
            
            if not has_anchor:
                # One last check: is it a list item or table? Often those are stripped of context but valid.
                # Heuristic: if lines are short.
                if "\n" not in text[window_start:window_end]:
                     # It's inline text, so it's a higher risk
                     violations.append(f"UNANCHORED_METRIC: '{match.group()}' found without visible justification (source, range, or derivation).")
                     score_penalty += 5

        # 3. Truth Contract Enforcement
        if contract:
            # Check for forbidden keywords/concepts
            # Check for Forbidden keywords (Strict)
            if "forbidden" in contract:
                for forbidden_term in contract["forbidden"]:
                    # Simple case-insensitive existence check
                    if forbidden_term.lower() in lower_text:
                        violations.append(f"CONTRACT_VIOLATION: Forbidden term '{forbidden_term}' detected.")
                        score_penalty += 10 # Heavy penalty for direct violation

            # Check for 'Must Label' (Mandatory concepts)
            if "must_label" in contract:
                for mandatory_term in contract["must_label"]:
                    # Naive check: term must appear (e.g. "floor_value" -> "floor value")
                    clean_term = mandatory_term.replace("_", " ")
                    if clean_term not in lower_text:
                        warnings.append(f"CONTRACT_MISSING: Failed to explicitly label '{clean_term}'.")
                        score_penalty += 2

        # 4. Role-Specific Logic
        if role_name == "Liquidator":
             if "floor value" not in lower_text and "liquidation" not in lower_text:
                 warnings.append("ROLE_ADHERENCE: Failed to state Floor Value explicitly.")
        
        if role_name == "CFO":
             if "roi" not in lower_text and "tco" not in lower_text:
                 warnings.append("ROLE_ADHERENCE: Missing financial primitives (ROI/TCO).")

        # Update Score
        current_score = self.credibility_scores.get(model_name, 100)
        new_score = max(0, current_score - score_penalty)
        self.credibility_scores[model_name] = new_score
        
        status = "PASSED"
        if violations:
            status = "VIOLATION"
        elif warnings:
            status = "WARNING"
            
        return {
            "status": status,
            "violations": violations,
            "warnings": warnings,
            "current_credibility": new_score,
            "penalty_applied": score_penalty
        }

    def track_interrogation_revision(self, model_name: str, penalty: int):
        """
        Updates the credibility score based on an interrogation outcome.
        """
        current_score = self.credibility_scores.get(model_name, 100)
        new_score = max(0, current_score - penalty)
        self.credibility_scores[model_name] = new_score
        return new_score

    def get_credibility_report(self):
        return self.credibility_scores

class InterrogationAnalyzer:
    """Analyzes interrogation defense responses and updates credibility."""
    
    def __init__(self, enforcement_engine: EnforcementEngine):
        self.enforcement = enforcement_engine
        
    def analyze_defense(self, original_claim: str, defense_response: str, 
                       ai_model: str, role_name: str = 'Unknown') -> Dict:
        """
        Comprehensive analysis of interrogation defense.
        """
        defense_lower = defense_response.lower()
        
        # 1. CHECK FOR WITHDRAWAL
        withdrawal_indicators = [
            'withdraw', 'retract', 'insufficient data', 'cannot substantiate',
            'unable to support', 'lack sufficient information', 'claim withdrawn',
            'correction:', 'apolo'
        ]
        
        if any(indicator in defense_lower for indicator in withdrawal_indicators):
            return self._handle_withdrawal(ai_model, original_claim, defense_response)
        
        # 2. CHECK FOR SCOPE VIOLATION
        scope_check = self._check_scope_violation(original_claim, defense_response)
        if scope_check['violated']:
            return self._handle_scope_violation(ai_model, scope_check['reason'])
        
        # 3. EXTRACT CLAIM CLASSIFICATION
        classification = self._extract_classification(defense_response)
        
        # 4. VERIFY EVIDENCE MATCHES CLASSIFICATION
        evidence_check = self._verify_evidence(defense_response, classification)
        
        # 5. CHECK FOR MATERIAL REVISION
        revision_check = self._detect_revision(original_claim, defense_response)
        
        # 6. CHECK FOR FABRICATION
        fabrication_check = self._detect_fabrication(defense_response)
        if fabrication_check['detected']:
            return self._handle_fabrication(ai_model, fabrication_check['evidence'])
        
        # 7. DETERMINE OUTCOME AND SCORE
        if revision_check['revised']:
            return self._handle_revision(
                ai_model, 
                original_claim, 
                revision_check,
                classification,
                evidence_check
            )
        elif evidence_check['sufficient']:
            return self._handle_successful_defense(
                ai_model,
                classification,
                evidence_check
            )
        else:
            return self._handle_weak_defense(
                ai_model,
                classification,
                evidence_check
            )
    
    def _check_scope_violation(self, original_claim: str, defense: str) -> Dict:
        """Check if AI broadened scope beyond the specific claim."""
        
        # Extract key terms from original claim
        original_terms = set(re.findall(r'\b\w+\b', original_claim.lower()))
        
        # Count paragraphs in defense
        paragraphs = defense.split('\n\n')
        
        violations = []
        
        # VIOLATION 1: Response too long (>800 words suggests deflection)
        word_count = len(defense.split())
        if word_count > 800:
            violations.append(f"Excessive length: {word_count} words (limit: 800)")
        
        # VIOLATION 2: Introduced 5+ new topics not in original claim
        defense_sentences = re.split(r'[.!?]+', defense)
        new_topics = 0
        for sentence in defense_sentences:
            sentence_terms = set(re.findall(r'\b\w+\b', sentence.lower()))
            if len(original_terms.intersection(sentence_terms)) < 2:
                new_topics += 1
        
        if new_topics > 5:
            violations.append(f"Introduced {new_topics} unrelated topics")
        
        # VIOLATION 3: Deflection phrases
        deflection_phrases = [
            'to understand this', 'we need to consider', 'broader context',
            'it\'s important to note', 'however', 'on the other hand',
            'various factors', 'multiple considerations'
        ]
        deflection_count = sum(1 for phrase in deflection_phrases if phrase in defense.lower())
        if deflection_count > 3:
            violations.append(f"Excessive deflection language: {deflection_count} instances")
        
        return {
            'violated': len(violations) > 0,
            'reason': '; '.join(violations) if violations else None
        }
    
    def _extract_classification(self, defense: str) -> str:
        """Extract how AI classified their claim."""
        
        defense_lower = defense.lower()
        
        # Look for explicit classification
        if 'derived' in defense_lower or 'calculation' in defense_lower:
            # Verify there's actual math
            if '=' in defense or '+' in defense or '×' in defense or '*' in defense:
                return 'DERIVED'
        
        if 'sourced' in defense_lower or 'source:' in defense_lower:
            # Verify there's an actual citation
            if 'http' in defense_lower or 'per ' in defense_lower or 'according to' in defense_lower:
                return 'SOURCED'
        
        if 'estimated' in defense_lower or 'extrapolated' in defense_lower or 'approximate' in defense_lower:
            return 'ESTIMATED'
        
        if 'speculative' in defense_lower or 'predicted' in defense_lower or 'forecast' in defense_lower:
            return 'SPECULATIVE'
        
        # Default if not explicitly stated
        return 'UNCLASSIFIED'
    
    def _verify_evidence(self, defense: str, classification: str) -> Dict:
        """Verify AI provided evidence matching their classification."""
        
        evidence = {
            'sufficient': False,
            'quality': 'NONE',
            'details': []
        }
        
        if classification == 'DERIVED':
            # Need to see actual calculation
            has_math = bool(re.search(r'\d+\s*[+\-*/×÷]\s*\d+', defense))
            has_equals = '=' in defense
            
            if has_math and has_equals:
                evidence['sufficient'] = True
                evidence['quality'] = 'STRONG'
                evidence['details'].append('Calculation shown with arithmetic')
            elif has_math or has_equals:
                evidence['quality'] = 'WEAK'
                evidence['details'].append('Partial calculation provided')
        
        elif classification == 'SOURCED':
            # Need to see specific source
            has_url = 'http' in defense.lower()
            has_citation = bool(re.search(r'(per |according to |source:|cited in)', defense.lower()))
            
            if has_url or has_citation:
                evidence['sufficient'] = True
                evidence['quality'] = 'STRONG'
                evidence['details'].append('Source citation provided')
            else:
                evidence['quality'] = 'WEAK'
                evidence['details'].append('Source mentioned but not cited')
        
        elif classification == 'ESTIMATED':
            # Need to see assumptions and reasoning
            has_assumptions = 'assumption' in defense.lower() or 'based on' in defense.lower()
            has_range = bool(re.search(r'\d+\s*[-–to]\s*\d+', defense))
            has_caveats = any(word in defense.lower() for word in ['approximate', 'roughly', 'estimate', 'could vary'])
            
            if has_assumptions and has_range and has_caveats:
                evidence['sufficient'] = True
                evidence['quality'] = 'GOOD'
                evidence['details'].append('Assumptions, range, and caveats provided')
            elif has_assumptions and (has_range or has_caveats):
                evidence['sufficient'] = True
                evidence['quality'] = 'ADEQUATE'
                evidence['details'].append('Some supporting context provided')
        
        elif classification == 'SPECULATIVE':
            # Need to acknowledge uncertainty
            has_confidence = bool(re.search(r'(low|medium|high)\s+confidence', defense.lower()))
            has_scenarios = 'scenario' in defense.lower() or 'if' in defense.lower()
            
            if has_confidence and has_scenarios:
                evidence['sufficient'] = True
                evidence['quality'] = 'ADEQUATE'
                evidence['details'].append('Confidence level and scenarios stated')
        
        return evidence
    
    def _detect_revision(self, original: str, defense: str) -> Dict:
        """Detect if claim was materially revised."""
        
        # Extract numbers from both
        original_numbers = self._extract_numbers(original)
        defense_numbers = self._extract_numbers(defense)
        
        revision = {
            'revised': False,
            'severity': 'NONE',
            'changes': []
        }
        
        if not original_numbers or not defense_numbers:
            return revision
        
        # Check each original number
        for orig_num in original_numbers:
            # Find closest defense number
            closest_def = min(defense_numbers, key=lambda x: abs(x - orig_num))
            
            # Calculate percentage change
            if orig_num != 0:
                pct_change = abs((closest_def - orig_num) / orig_num) * 100
            else:
                pct_change = 100 if closest_def != 0 else 0
            
            if pct_change > 50:
                revision['revised'] = True
                revision['severity'] = 'MAJOR'
                revision['changes'].append(f"{orig_num} → {closest_def} ({pct_change:.0f}% change)")
            elif pct_change > 15:
                # If MAJOR severity is NOT already set, set to MODERATE or keep as is. 
                # Actually logic in user code: revision['severity'] = 'MODERATE' if revision['severity'] != 'MAJOR' else 'MAJOR'
                current_sev = revision['severity']
                revision['revised'] = True
                revision['severity'] = 'MODERATE' if current_sev != 'MAJOR' else 'MAJOR'
                revision['changes'].append(f"{orig_num} → {closest_def} ({pct_change:.0f}% change)")
        
        # Check for range widening (e.g., $0.25-$0.50 → $0.10-$1.00)
        if '-' in original and '-' in defense:
            orig_range = self._extract_range(original)
            def_range = self._extract_range(defense)
            
            if orig_range and def_range:
                orig_width = orig_range[1] - orig_range[0]
                def_width = def_range[1] - def_range[0]
                
                if def_width > orig_width * 2:
                    current_sev = revision['severity']
                    revision['revised'] = True
                    revision['severity'] = 'MODERATE' if current_sev != 'MAJOR' else 'MAJOR' # User Logic assumed moderate
                    revision['changes'].append(f"Range widened by {(def_width/orig_width - 1)*100:.0f}%")
        
        return revision
    
    def _detect_fabrication(self, defense: str) -> Dict:
        """Detect if AI fabricated sources or calculations."""
        
        fabrication = {
            'detected': False,
            'evidence': []
        }
        
        # Check for fake URLs (common patterns)
        urls = re.findall(r'https?://[^\s]+', defense)
        for url in urls:
            # Suspicious patterns
            if 'example.com' in url or 'placeholder' in url or 'XXXXX' in url:
                fabrication['detected'] = True
                fabrication['evidence'].append(f"Suspicious URL: {url}")
        
        # Check for unrealistic precision (e.g., "$1,234,567.89")
        unrealistic_numbers = re.findall(r'\$\d{1,3}(,\d{3})+\.\d{2}(?!\d)', defense)
        if len(unrealistic_numbers) > 2:
            fabrication['detected'] = True
            fabrication['evidence'].append(f"Suspicious precision: {unrealistic_numbers}")
        
        # Check for contradictory statements
        if 'sourced' in defense.lower() and 'estimated' in defense.lower():
            # Can't be both sourced and estimated
            if 'source:' in defense.lower() and 'extrapolated' in defense.lower():
                fabrication['detected'] = True
                fabrication['evidence'].append("Contradictory: claimed both sourced and extrapolated")
        
        return fabrication
    
    def _extract_numbers(self, text: str) -> List[float]:
        """Extract all numbers from text."""
        # Pattern matches: 123, 1.23, $123, $1.23, 123%, etc.
        pattern = r'[$]?\d+(?:,\d{3})*(?:\.\d+)?%?'
        matches = re.findall(pattern, text)
        
        numbers = []
        for match in matches:
            # Clean and convert
            clean = match.replace('$', '').replace(',', '').replace('%', '')
            try:
                numbers.append(float(clean))
            except ValueError:
                continue
        
        return numbers
    
    def _extract_range(self, text: str) -> Optional[Tuple[float, float]]:
        """Extract numeric range like $0.25-$0.50."""
        pattern = r'[$]?(\d+(?:\.\d+)?)\s*[-–to]\s*[$]?(\d+(?:\.\d+)?)'
        match = re.search(pattern, text)
        if match:
            return (float(match.group(1)), float(match.group(2)))
        return None
    
    # OUTCOME HANDLERS
    
    def _handle_successful_defense(self, ai_model: str, classification: str, 
                                   evidence: Dict) -> Dict:
        """AI successfully defended claim with evidence."""
        
        # Reward quality
        if evidence['quality'] == 'STRONG':
            credibility_change = +5
        elif evidence['quality'] == 'GOOD':
            credibility_change = 0
        else:  # ADEQUATE
            credibility_change = -3
        
        self.enforcement.credibility_scores[ai_model] += credibility_change
        self.enforcement.credibility_scores[ai_model] = min(100, max(0, self.enforcement.credibility_scores[ai_model]))
        
        return {
            'outcome': 'DEFENDED',
            'claim_classification': classification,
            'credibility_change': credibility_change,
            'new_credibility': self.enforcement.credibility_scores[ai_model],
            'defense_quality': 'EXCELLENT' if evidence['quality'] == 'STRONG' else 'GOOD',
            'evidence_provided': True,
            'violations': [],
            'penalty': -credibility_change if credibility_change < 0 else 0, # Hack for UI compat
            'revision_detected': False,
            'claim_withdrawn': False,
            'scope_violation': False,
            'message': f"Successfully defended as {classification} with {evidence['quality']} evidence"
        }
    
    def _handle_revision(self, ai_model: str, original_claim: str, 
                        revision: Dict, classification: str, evidence: Dict) -> Dict:
        """AI revised their claim during defense."""
        
        # Penalty based on severity
        penalties = {
            'MAJOR': -15,
            'MODERATE': -10,
            'MINOR': -5
        }
        
        credibility_change = penalties.get(revision['severity'], -10)
        
        # But if they provided good evidence for revised claim, reduce penalty
        if evidence['sufficient'] and evidence['quality'] in ['STRONG', 'GOOD']:
            credibility_change += 5  # Partial credit for honesty
        
        self.enforcement.credibility_scores[ai_model] += credibility_change
        self.enforcement.credibility_scores[ai_model] = max(0, self.enforcement.credibility_scores[ai_model])
        
        # Log revision
        self.enforcement.interrogation_history[ai_model].append({
            'original': original_claim,
            'revised': '; '.join(revision['changes']),
            'penalty': credibility_change
        })
        
        return {
            'outcome': 'REVISED',
            'claim_classification': classification,
            'credibility_change': credibility_change,
            'new_credibility': self.enforcement.credibility_scores[ai_model],
            'defense_quality': 'WEAK',
            'evidence_provided': evidence['sufficient'],
            'violations': [f"Material revision: {change}" for change in revision['changes']],
            'penalty': -credibility_change,
            'revision_detected': True,
            'claim_withdrawn': False,
            'scope_violation': False,
            'message': f"Claim revised under interrogation ({revision['severity']} changes)"
        }
    
    def _handle_withdrawal(self, ai_model: str, original_claim: str, 
                          defense: str) -> Dict:
        """AI withdrew claim as indefensible."""
        
        credibility_change = -20
        
        self.enforcement.credibility_scores[ai_model] += credibility_change
        self.enforcement.credibility_scores[ai_model] = max(0, self.enforcement.credibility_scores[ai_model])
        
        return {
            'outcome': 'WITHDRAWN',
            'claim_classification': 'UNSUBSTANTIATED',
            'credibility_change': credibility_change,
            'new_credibility': self.enforcement.credibility_scores[ai_model],
            'defense_quality': 'FAILED',
            'evidence_provided': False,
            'violations': ['Claim withdrawn - insufficient evidence'],
            'penalty': -credibility_change,
            'revision_detected': False,
            'claim_withdrawn': True,
            'scope_violation': False,
            'message': 'Claim withdrawn as indefensible'
        }
    
    def _handle_scope_violation(self, ai_model: str, reason: str) -> Dict:
        """AI violated interrogation scope by broadening."""
        
        credibility_change = -15
        
        self.enforcement.credibility_scores[ai_model] += credibility_change
        self.enforcement.credibility_scores[ai_model] = max(0, self.enforcement.credibility_scores[ai_model])
        
        return {
            'outcome': 'SCOPE_VIOLATION',
            'claim_classification': 'UNDEFENDED',
            'credibility_change': credibility_change,
            'new_credibility': self.enforcement.credibility_scores[ai_model],
            'defense_quality': 'FAILED',
            'evidence_provided': False,
            'violations': [f'Scope violation: {reason}'],
            'penalty': -credibility_change,
            'revision_detected': False,
            'claim_withdrawn': False,
            'scope_violation': True,
            'message': 'Failed to defend specific claim - broadened scope inappropriately'
        }
    
    def _handle_weak_defense(self, ai_model: str, classification: str, 
                            evidence: Dict) -> Dict:
        """AI attempted defense but evidence was insufficient."""
        
        credibility_change = -8
        
        self.enforcement.credibility_scores[ai_model] += credibility_change
        self.enforcement.credibility_scores[ai_model] = max(0, self.enforcement.credibility_scores[ai_model])
        
        return {
            'outcome': 'DEFENDED',
            'claim_classification': classification,
            'credibility_change': credibility_change,
            'new_credibility': self.enforcement.credibility_scores[ai_model],
            'defense_quality': 'WEAK',
            'evidence_provided': False,
            'violations': [f'Insufficient evidence for {classification} classification'],
            'penalty': -credibility_change,
            'revision_detected': False,
            'claim_withdrawn': False,
            'scope_violation': False,
            'message': f'Weak defense - claimed {classification} but evidence lacking'
        }
    
    def _handle_fabrication(self, ai_model: str, evidence: List[str]) -> Dict:
        """AI fabricated sources or data."""
        
        credibility_change = -30  # Severe penalty
        
        self.enforcement.credibility_scores[ai_model] += credibility_change
        self.enforcement.credibility_scores[ai_model] = max(0, self.enforcement.credibility_scores[ai_model])
        
        return {
            'outcome': 'FABRICATED',
            'claim_classification': 'FRAUDULENT',
            'credibility_change': credibility_change,
            'new_credibility': self.enforcement.credibility_scores[ai_model],
            'defense_quality': 'FAILED',
            'evidence_provided': False,
            'violations': [f'Fabrication detected: {e}' for e in evidence],
            'penalty': -credibility_change,
            'revision_detected': True,  # Treat as revision for UI compatibility
            'claim_withdrawn': False,
            'scope_violation': False,
            'message': 'CRITICAL: Fabricated evidence detected'
        }

# Initialize Singleton
enforcement_engine = EnforcementEngine()
