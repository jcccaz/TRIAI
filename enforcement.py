"""
Enforcement Engine for TriAI Council Mode.
Responsible for auditing AI responses against Truth Contracts and detecting adherence to strict epistemic standards.
"""

import re
from typing import Dict, List, Any

class EnforcementEngine:
    def __init__(self):
        # Starting credibility is 100 for all models
        self.credibility_scores = {
            "openai": 100,
            "anthropic": 100,
            "google": 100,
            "perplexity": 100
        }
        
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
            if "forbidden" in contract:
                for forbidden_item in contract["forbidden"]:
                    # Basic keyword check - this can be refined with embeddings later
                    # checking if the forbidden concept (as a word) exists
                    # This is naive; "no hedging" is hard to grep. 
                    # But "do not use 'hope'" is easy.
                    # We will implement specific 'concept detectors' later.
                    pass

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

    def get_credibility_report(self):
        return self.credibility_scores
