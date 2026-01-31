# Persona Research & Evolution Protocol
**Date:** January 30, 2026
**Subject:** Analyzing AI Identity Drift and Self-Selection Patterns

## 🎯 Research Objectives
This protocol defines how we utilize the captured persona data to evolve the TriAI High Council.

### 1. Research Value Questions
We are tracking data to answer four foundational questions:
*   **"Do different AIs have natural persona preferences?"**
    *   *Hypothesis:* Gemini leans toward character-driven identities; Perplexity anchors in objective research roles.
*   **"Does query type affect persona choice?"**
    *   *Variable:* Technical queries vs. Creative/Historical queries.
*   **"Is self-selection consistent or random?"**
    *   *Test:* Does Gemini's "character mode" remain consistent across similar domains?
*   **"Where do AIs agree on the optimal persona?"**
    *   *Measurement:* Consensus in persona selection (e.g., all 4 choosing "Researcher") signals a high-certainty domain.

## 🛠️ Implementation Phases

### Phase 1: Discovery (Current - First 50 Queries)
*   **Action:** Allow AIs to self-select freely without manual role assignment.
*   **Monitoring:** Periodic execution of `persona_synthesizer.py`.
*   **Observation:** Watch for "Emergent Experts" not currently in our `council_roles.py`.

### Phase 2: Pattern Analysis (50-100 Queries)
*   **Action:** Categorize most common personas into "Elite Clusters."
*   **Mapping:** Associate specific query domains (Finance, IT, History) with AI-specific persona preferences.
*   **Metric:** Measure "Persona Success Rate" (which roles yield the highest-rated answers).

### Phase 3: Council Optimization (100+ Queries)
*   **Action:** Formalize the "New High Council" based on data, not assumptions.
*   **Hybridization:** Blend assigned roles (for structural stability) with self-selection (for specialized depth).
*   **Auto-Config:** Use historical data to auto-recommend the best persona configuration based on the user's initial prompt keywords.

---
*Note: This document serves as the living roadmap for the Persona Evolution project.*
