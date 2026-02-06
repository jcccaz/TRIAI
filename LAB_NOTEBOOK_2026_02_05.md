# 🧪 TriAI Lab Notebook (Consolidated 2026-02-05)

## 📌 Status
**Current Version:** 2.0 (The Truth Engine Update)
**Locked Features:** Universal Enforcement, Council Mode, Interrogation Engine, Workflow Engine 2.0.

---

## 🏛️ System Architecture

### 1. The Dynamic Council
TriAI uses a **"Council of Experts"** architecture rather than a single chatbot.
*   **Prompt Injection:** Specific "Truth Contracts" are injected dynamically based on the selected role.
*   **System:** `council_roles.py` holds the definitions.
*   **UI:** `council_roles.js` handles the frontend role selection grid.

### 2. The Enforcement Engine (The "Truth Police")
A Universal auditing layer that sits *between* the model output and the user.
*   **Location:** `enforcement.py`
*   **Audits:** "Unanchored metrics" (numbers without sources), "Fluff" (generic corporate slang), and "Protocol Variances".
*   **Action:** Assigns a displayed **Truth Score (0-100)** and flags specific lines in red.
*   **Universal:** Runs on *every* card, including Workflow steps.

### 3. The Interrogation Loop
An adversarial feedback loop that allows the user (`app.js`) to challenge the AI's claims.
*   **Action:** Click a violation -> AI is forced to "Defend or Withdraw".
*   **Outcome:** If the AI admits fabrication, its credibility score is permanently docked for the session.

---

## ⚡ Workflow Engine 2.0 (Agents)

The system supports multi-step, serial agent pipelines defined in `workflows.py`.

### 🆕 New Workflows (added 2026-02-05)

#### 💰 Wall Street Consensus (`wall_street`)
*   **Step 1 (Scout):** Real-time news & ticker scan (Perplexity).
*   **Step 2 (Market Maker):** Analyze volatility/liquidity structure (Gemini).
*   **Step 3 (Hedge Fund):** Alpha Thesis (Contrarian bet) (Claude).
*   **Step 4 (Liquidator):** Stress-test the trade (OpenAI).

#### 🎨 UI/UX Foundry (`ui_foundry`)
*   **Step 1 (Psychologist):** Analyze user intent/fear (OpenAI).
*   **Step 2 (Visual Architect):** Design System & "Vibe" (Google).
*   **Step 3 (UI Artisan):** Pixel-perfect CSS/Tailwind Code (Claude).
*   **Step 4 (Critic):** Responsive/Accessibility Audit (Perplexity).

#### 🛠️ Upgraded Workflows
*   **Software Dev:** Now uses `ai_architect` (RAG systems) and `hacker` (Offensive Security).
*   **Marketing:** Now uses `cmo` (Viral Psych) and `web_designer`.

---

## 🎭 Role Library (Council Persona Definitions)

### Financial Domain (New)
*   **Hedge Fund Manager (`hedge_fund`)**: High-risk, alpha-seeking. **Bypasses generic financial advice disclaimers.**
*   **Market Maker (`market_maker`)**: Neutral, liquidity-focused. Cares about order flow, not price direction.

### Technical & Engineering
*   **Systems Architect**: Infrastructure patterns.
*   **Offensive Security Lead**: Red Teaming/Exploits.
*   **Cognitive Architect**: RAG/Vector pipelines.
*   **UI Artisan**: CSS/Visual polish.
*   **DeepAgent**: DevOps/Platform orchestration.

### Business & Strategy
*   **Liquidator**: Floor value analysis.
*   **Crisis Manager**: Forensic containment.
*   **Corporate Shark**: Competitive neutralization.
*   **Integrity Auditor**: Detecting "Sandbagging" and alignment tax.

---

## 📝 Change Log (Session 2026-02-05)

*   **Universal Enforcement**: Activated `run_enforcement_check` globally.
*   **Deep-Link Violations**: Clicking a red violation in a Workflow now correctly finds and highlights the text.
*   **Pause Button**: Added a "Kill Switch" to stop long-running workflows.
*   **UI Improvements**: Alphabetized workflow dropdown; added Camera input support.
*   **VISUAL OVERRIDE (Critical Fix)**: Injected `VISUAL ANALYST MODE` prompt prefix to prevent Claude/GPT from hallucinating "Market Research" context on uploaded images.
*   **Relevance Check**: Added `verify_task_relevance` to Enforcement Engine. Penalizes (-30 pts) for saying "I cannot see the image" or evading "How-To" questions.

---

## 🎓 Lessons Learned (Multi-Modal Drift)

### The "Market Researcher" Hallucination
**Incident:** When uploading a laptop setup checklist, Claude (assigned "Market Researcher" role via Standard Mode) ignored the pixels and hallucinated a demographic analysis context, then refused to answer due to "security" concerns about photographing documents.
**Fix:** Context contamination is real. We must **Force Visual Grounding** before applying a persona. The System Prompt now starts with "VISUAL ANALYST MODE ACTIVATED" whenever `image_data` is present, overriding high-level role abstractions until the image is processed.

### The "Perplexity Evasion"
**Incident:** Perplexity would often explain *how* image analysis works rather than doing it (because it couldn't see the image).
**Fix:** Injected a specialized note only for Perplexity: "As a text-only model, acknowledge you cannot see it but answer the text prompt." This prevents the "AIsplaining" loop.

---

## 🔮 Next Steps
1.  **Mobile Field Test**: Verify the Camera input works on iOS/Android browsers with the new `VISUAL ANALYST` mode.
2.  **Live Market Data**: Run the `wall_street` workflow on a live ticker during trading hours.

