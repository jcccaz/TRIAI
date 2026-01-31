# TriAI Compare - System Architecture (Jan 2026)

This document provides a technical overview of the **TriAI Compare** (FrankNet) architecture for use in project context and coordination.

## 1. Core Stack
*   **Backend:** Python (Flask)
*   **Frontend:** Vanilla JS / CSS (Gold Noir / Digital Brutalist Aesthetic)
*   **Database:** SQLite (`comparisons.db`)
*   **API Management:** Parallel ThreadPool execution for multi-model queries.

## 2. File Architecture
```text
/tri_ai_compare
├── app.py                  # Main Entry Point & Orchestration Layer
├── database.py             # SQLite Layer (History, Personas, Feedback)
├── council_roles.py        # Master Role Definitions & Assigned Personas
├── project_manager.py      # handles context-saving per project folder
├── file_processor.py       # PDF/Image/Text extraction logic
├── persona_synthesizer.py  # NEW: Analyzes self-selected persona patterns
├── static/                 # CSS (Noir themes), JS (Dynamic state transitions)
│   ├── css/role_selectors.css
│   └── background_videos/  # Gold Noir video backgrounds
└── templates/
    └── index.html          # 2x2 Grid AI Workbench UI
```

## 3. The "Council Mode" Pipeline
The system processes queries through three distinct modes:

1.  **Standard Mode:** Direct query to 4 models with default system prompts.
2.  **Self-Selecting Expert Mode:** Models are instructed to choose their own elite persona based on the query. Persona is extracted via regex and stored in the DB.
3.  **Council Mode (Assigned):** User assigns specific roles (e.g., Architect, Critic) from `council_roles.py` to specific models.

## 4. Key Experimental Features
*   **Anti-Sandbagging Protocol:** Prompts specifically designed to prevent models from hiding high-value insights in internal `<thinking>` tags.
*   **Persona Evolution Layer:** A feedback loop where self-selected personas are tracked and synthesized to update the "Manual" role definitions.
*   **Obsidian Vault Context:** The app can optionally RAG-search a local Obsidian vault to inject personal project notes into the AI context.

## 5. Database Schema (Simplified)
*   **Comparisons Table:** `id, question, document_content, timestamp, saved, tags`
*   **Responses Table:** `id, comparison_id, ai_provider, model_name, response_text, response_time, success, thought_text, self_selected_persona`
*   **Feedback Table:** `id, comparison_id, rating, tool_generic, missing_details, feedback_text`

---
*Generated for: Claude Project Context*
