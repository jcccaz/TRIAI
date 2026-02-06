# Features Confirmed (Locked)

## 1. Council Mode & Roles
- **Dynamic Role Assignment:** User can assign 19+ specific expert personas (e.g., Liquidator, Architect, Critic) to any model.
- **System Prompts:** `council_roles.py` defines deep, forensic prompts for each role.
- **UI Integration:** Dropdowns for role selection + "Use Recommended" logic based on query analysis.

## 2. Enforcement Engine (Anti-Hallucination)
- **Truth Contracts:** Every role has an `allowed`/`forbidden` list of terms/concepts.
- **Universal Auditing:** Engine runs on ALL queries (Standard or Council Mode).
- **Credibility Scoring:** Automated regex-based scoring (0-100) penalizing "fluff" and "unanchored metrics".
- **Visual Auditing:** UI displays a "Truth Score" badge and a "Protocol Variance" report.
- **Deep-Link Violations:** Clicking a violation auto-scrolls to the specific text in the response.

## 2b. Interrogation Engine (Active Prosecution)
- **Surgical Inquiry:** User can "Interrogate" specific claims.
- **Outcome Classification:** Detects `DEFENDED`, `REVISED`, `WITHDRAWN`, or `FABRICATED`.
- **Penalty Logic:** Applies score penalties (-30 for fabrication) dynamically.
- **Consensus Defense:** "Re-Synthesize" button appears if credibility drops below 70%.

## 3. Visual & File Injection ("The Eyes")
- **Multi-Modal Input:** Drag-and-drop support for PDF, TXT, CSV, Code.
- **Paste-to-Upload:** Clipboard support for screenshots (Ctrl+V).
- **Visual Output:** Logic to generate charts (`visuals.py` -> Mermaid) or realistic images (OpenAI DALL-E/Google Imagen).

## 4. Operational Foundations
- **Project Management:** Save/Load functionality for `triai_projects`.
- **History:** "Local Time Machine" sidebar to revisit past queries.
- **Deployment:** Railway configuration (`Procfile`, `requirements.txt`) verified.
