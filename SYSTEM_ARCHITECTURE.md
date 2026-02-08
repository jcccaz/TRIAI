# 🦅 TriAI System Architecture (v7.0)

## Overview
TriAI is a **Multi-Model Intelligence Council** that orchestrates specialized AI personas ("Roles") to solve complex problems. It uses a "War Room" architecture where different AI models (GPT, Claude, Gemini, Perplexity) are assigned distinct psychological and functional lenses to prevent groupthink and hallucinations.

---

## 1. The Core Loop
The system operates on a Request-Response-Audit cycle:

```mermaid
graph TD
    User[User Query] -->|1. Router| App[Main App Logic]
    App -->|2. Parallel Request| Council[Council of AI Experts]
    
    subgraph "The Council"
        GPT[GPT-5.2 (Logic)]
        Claude[Claude 3.7 (Nuance)]
        Gemini[Gemini 1.5 (Data)]
        Perplexity[Perplexity (Search)]
    end
    
    Council -->|3. Raw Output| Enforcement[Enforcement Engine]
    Enforcement -->|4. Audit| TruthContract{Violations?}
    TruthContract -->|Yes| Penalty[Score Deduction / Interrogation]
    TruthContract -->|No| Visualization[Viz Engine]
    
    Visualization -->|5. Render| UI[Frontend Card]
```

---

## 2. Key Modules

### A. The Truth Engine (Enforcement)
*   **File:** `enforcement.py`
*   **Purpose:** Prevents AI "sandbagging" and "drift."
*   **Mechanism:**
    *   **Truth Contracts:** Each role (e.g., `Liquidator`) has a strict definition of what is allowed/forbidden (defined in `council_roles.py`).
    *   **Interrogation:** If a claim violates the contract (e.g., "market will grow" without a number), the system triggers an **Auto-Interrogation** where the AI must "Defend or Withdraw" the claim.
    *   **Scoring:** Responses are graded (0-100). Scores < 70 trigger a forced "Consensus Re-Synthesis".

### B. War Room v7.0: The Hardware/Software Split
To handle complex engineering tasks without "refusals" or generic advice, the architecture splits responsibilities:
*   **Fabric Architect (Claude):** Defines the *Invariants* and *Axioms*. (e.g., "The network must never block port 443"). Pure logic, no implementation.
*   **HAL Lead (Gemini/GPT):** Defines the *Hardware Abstraction Layer*. (e.g., "Map Invariant A to Cisco ASR9000 config"). Pure implementation, no philosophy.
This separation preventing "contamination" of high-level reasoning with low-level implementation details until the final synthesis.

### C. Visualization Engine
*   **File:** `visuals.py`
*   **Purpose:** Converts text data into visual artifacts.
*   **Modes:**
    1.  **Mermaid.js:** For flowcharts, sequence diagrams, and gantt charts.
    2.  **Matplotlib:** For hard financial data (bar charts, line graphs) generated from CSV data tables.
    3.  **Image Gen (Imagen 3):** For conceptual or artistic renderings of the solution.

---

## 3. Data Flow & Persistence

### Session Management
*   **Storage:** `comparisons.db` (SQLite)
*   **Context:** `project_manager.py` maintains valid reference to the active project.
*   **Logs:** All prompts and responses are logged to `triai_projects/` as JSON for replayability.

### Frontend
*   **Stack:** Vanilla JS + CSS (No build step required).
*   **Design:** Glassmorphism UI with "Enforcement" highlights (Red/Green text for violations/validations).

---

## 4. Directory Structure
```
/tri_ai_compare
│
├── app.py                 # Main Flask Application
├── council_roles.py       # Role Definitions & Prompts
├── enforcement.py         # Truth Engine Logic
├── visuals.py             # Image & Chart Generation
├── workflows.py           # Pre-defined Logic Chains (War Room)
├── database.py            # SQLite Interface
├── project_manager.py     # File I/O for Projects
│
├── static/
│   ├── css/               # enforcement.css, interrogation.css
│   └── app.js             # Frontend Logic
│
└── templates/
    └── index.html         # Main UI
```
