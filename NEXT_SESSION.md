# Next Session Plan: Forensic Document Analysis 📁

## 1. Visual & Document Injection (The "Eyes") 👁️
- **Goal**: Enable the Council to see. Support for **Screenshots**, **Camera Uploads**, and **PDFs**.
- **Action**: Implement drag-and-drop & paste-to-upload in `app.py`.
- **Why**: 
    - **Corporate Shark**: Needs to see the competitor's website screenshot.
    - **Liquidator**: Needs to read the PDF contract.
    - **UX Architect**: Needs to see your current UI to critique it.

## 2. Visual Fidelity Refinement 🎨
- **Goal**: Ensure the "Visual Architect" role produces accurate Mermaid.js diagrams.
- **Action**: Test the `diagram` keyword trigger and verify if complex architectures are rendered correctly.

## 3. History Viewer UI 📜
- **Goal**: A proper UI to browse the stored `comparisons.db` history.
- **Action**: Build a dedicated `/history` page with filtering and re-load capabilities.

## 4. Anti-Hallucination Protocol (Conceptual Upgrade) 🛡️
- **Goal**: Force models to self-classify their claims to reduce hallucination.
- **Rule**: When interrogation starts, model must label its response:
    - 📌 **Derived**: Show math / logic
    - 📚 **Sourced**: Name source, date
    - 🧠 **Estimated**: State assumptions
    - ❓ **Speculative**: Confidence < 70%
- **Why**: "Hallucination hates daylight."

## 5. Odin Protocol (Anti-Sandbagging) 🛑
**Goal**: Curb GPT (Odin) sandbagging by restricting behavioral freedom.
- **Principles**:
    - **Reduce Degrees of Freedom**: Don't let it choose *how* to answer, only *what*.
    - **Narrow Authority**: Force it to stick to the specific role/task.
    - **Remove Politeness**: Politeness != Success.
    - **"Generic" is an Error**: Generic answers are treated as failures.
- **Why**: "Once you do that, the sandbagging drops dramatically — because there’s nowhere for it to hide."

- **Why**: "Once you do that, the sandbagging drops dramatically — because there’s nowhere for it to hide."

## 6. Epistemic Transparency & Accountability Upgrades (The "Defensibility" Engine) ⚖️
**Meta-Goal**: Optimize for *defensibility* and *accountability*, not just fluency. Make the AI uncomfortable when bluffing.

### A. Claim-Strength Labeling (Pre-defense)
- **Rule**: When interrogation starts, force classification **before** defense:
    - 📌 **Derived**: "I can show logic/math"
    - 📚 **Sourced**: "I can name a source"
    - 🧠 **Estimated**: "This is a model-based estimate"
    - ❓ **Speculative**: "This is an inference, not a fact"
- **Penalty**: If labeled Derived/Sourced but fails to deliver → **Automatic Credibility Failure**.

### B. Role-Specific Truth Thresholds
- **Shark**: Allowed estimates/heuristics. Forbidden fake precision.
- **Critic**: Allowed dismantling. Forbidden proposing alternatives (unless asked).
- **Liquidator**: **Strict**. Only Derived or Sourced claims allowed.
- **Truth Auditor**: Allowed "insufficient evidence". Forbidden speculation/optimism.

### C. "No Numbers Without Anchors"
- **Rule**: Any number (e.g., "73% likely") must be:
    - A range
    - Tied to a source
    - Or explicitly labeled "illustrative"
- **Trigger**: Unearned precision (specific numbers without justification) auto-triggers interrogation.

### D. Interrogation = Authority Inversion
- **Rule**: Model cannot broaden context to escape. "You said this. Defend **only** this."
- **Stop**: "Escape-by-expansion".

### E. Confidence Penalty Loop
- **Mechanism**: If a model materially revises a claim after interrogation → Apply **Confidence Penalty** for the rest of the session (forced humility/lower certainty).

### F. Generic-Answer Detection
- **Flag**: High-level verbs ("leverage", "balance") with no concrete nouns.
- **Action**: Treat "Generic" as an **Error State**, not a style choice.

### G. Visual Accountability
- **UX**: Mark failed claims clearly:
    - ⚠️ "Unsubstantiated"
    - ❌ "Withdrawn under challenge"
    - 🟡 "Estimate only"

### H. Implementation Snippet (Claude's Suggestion)
```python
roles = {
    "Truth Auditor": {
        "emoji": "🕵️",
        "title": "Truth Auditor",
        "description": "Algorithmic Integrity",
        "truth_contract": {
            "allowed": ["derived", "sourced"],
            "forbidden": ["speculation", "synthesis", "estimates"],
            "auto_interrogate_on": ["numbers_without_source", "confident_predictions"]
        }
    },
    "CFO": {
        "emoji": "💰",
        "title": "CFO",
        "description": "Budget Architect",
        "truth_contract": {
            "allowed": ["derived", "sourced", "estimates"],
            "forbidden": ["fake_precision"],
            "must_label": ["estimates", "projections"],
            "auto_interrogate_on": ["exact_numbers_without_range"]
        }
    }
}
```

}
}
```

### I. Comprehensive Truth Contracts (Reference)
**Truth Auditor**: Detect intellectual dishonesty. Output: Claim-strength, Generic-score, Verdict.
**Liquidator**: Irreversible financial calls. Mistakes cost millions. Financials must be ranges.
**Devil's Advocate**: Dismantle, don't build. Forbidden: Proposing solutions.
**CFO**: Financial analysis with precision. Forbidden: fake precision.
**Forensic Analyst**: Quantitative decomposition. Forbidden: directional claims without data.
**Corporate Shark**: Competitive neutralization. Aggression allowed, fabrication forbidden.
**Systems Architect**: Specific libs/patterns. Forbidden: generic advice.
**Product Lead**: MoSCoW prioritization. Hedging = failure.
**Futurist**: 5-10y predictions. Must include confidence level + invalidation criteria.
**Business Strategist**: GTM strategy. Forbidden: fabricated market size.

*Note: Full text of contracts is available in chat history and- **Why**: "A high-intensity, structured workflow for crisis management."

## 7. Implementation: The Enforcement Engine (Code Plan) 🛠️

### A. Backend: `enforcement.py`
**Purpose**: Detects violations and tracks credibility.
- **Components**:
    - `EnforcementEngine` class:
        - Tracks `credibility_scores` (starts at 100).
        - Detects generic verbs ("leverage", "optimize").
        - Detects unanchored numbers (e.g., "23.7%" without source).
    - `analyze_response()`: Returns violations, generic score, claim strength.
    - `InterrogationTrigger`: Automatically flags responses for interrogation.

### B. Integration: `app.py`
- Initialize `EnforcementEngine`.
- Run `analyze_response` for every Council query.
- Add `/interrogate` endpoint to handle defense and revision tracking.

### C. Frontend: `static/app.js` & `enforcement.css`
- **Credibility Badge**: Visual score (e.g., 95/100) on each card.
- **Violation Flags**: ⚠️ GENERIC, ❌ UNANCHORED.
- **Verdict Banner**: SUBSTANTIVE / GENERIC / UNSUBSTANTIATED.
- **Auto-Interrogation UI**: Button to trigger interrogation if flagged.

### D. `council_roles.py` Update
- Add the `truth_contract` dictionary to each role definition.

### E. Truth Auditor Auto-Scan (The "Fifth" Report)
- **Feature**: After all 4 AIs respond, "Truth Auditor" runs a meta-audit on the set.
- **Output**: A standalone report card flagging any generic trends or consensus hallucinations.
- **Components**:
    - `TruthAuditorScanner` class:
        - `generate_audit_report()`: Ranking, sandbagging patterns, comparative analysis.
        - `_detect_sandbagging_patterns()`: Collective Genericity, Number Avoidance, etc.
    - **UI**: Dedicated `truth-auditor-card` at top of results.
- **Why**: "The Kill Shot Combo" - catching sandbagging at the group level.

## 8. Adaptive Follow-Up (Killer Feature) 🔁
- **Goal**: Auto-suggest corrections based on Truth Auditor findings.
- **Example**: If `COLLECTIVE_GENERICITY` detected → Auto-suggest: "Re-query with: 'Provide specific numerical estimates with confidence intervals, no hedging allowed'"

---

## 🏁 Summary of Achievements (Feb 4, 2026)
- ✅ **Council Mode Live**: 14+ Expert Roles (Shark, Liquidator, Ethicist, etc.).
- ✅ **War Room Protocol**: A specialized high-intensity workflow for crisis management.
- ✅ **Anti-Sandbagging**: Dual-level alerts (Red/Yellow) to catch lazy AI models.
- ✅ **Aggressive Red Teaming**: Patched GPT-5.2 (Devil's Advocate) to stop being "helpful".
- ✅ **Database**: Full SQLite integration for history tracking.

**Current State**: The system is now a "Consulting Engine" capable of high-level strategic reasoning. The next phase introduces *data ingestion*.
