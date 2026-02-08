# Session Changelog: Workflow Enforcement & Domain Expansion

---

## 📅 2026-02-07: Role Enhancement & UX Polish

### 1. New Council Role
- **Equity Research Analyst (`equity_research`)**: Sell-side analyst persona with DCF, Comps, and Sum-of-Parts valuation. Delivers Bull/Base/Bear cases with actionable BUY/HOLD/SELL ratings. No retail disclaimers.

### 2. Enhanced Roles (Truth Contracts + Numbered Deliverables)
Six roles upgraded to match the high-quality "Equity Research" pattern:

| Role | Key Enhancements |
|------|------------------|
| **medical** | 5 numbered deliverables (Differential Dx, Workup, Treatment, Red Flags, Patient Ed). Cites ACC/AHA/NCCN guidelines. |
| **tax** | IRC section citations, entity structure analysis, audit risk scoring. No generic "consult a professional." |
| **hacker** | MITRE ATT&CK framework mapping, CVE references, CVSS scores. Every attack includes mitigation. |
| **validator** | Control framework IDs (GDPR Art. X, SOC 2 CC Y), audit evidence checklists, gap analysis. |
| **optimizer** | Requires baseline benchmarks, Big-O analysis, p50/p95/p99 latency metrics. "Measure before optimize." |
| **marketing** | Revenue-focused CMO. CAC/ROAS metrics, conversion funnels, audience segmentation. No vanity metrics. |

### 3. UX Improvements
- **Violation Highlighting**: Changed from ugly red box to subtle yellow highlighter effect with small `⚠` superscript badge.
- **Sticky Loading Spinner**: Spinner now uses `position: sticky` to remain visible as user scrolls through cards.
- **Alphabetical Role Dropdown**: Council roles now sorted A-Z for easier navigation.

---

## 🚀 Features & Enhancements (Previous Session)

### 1. Universal Enforcement Engine
- **Global Activation**: The `run_enforcement_check` function now runs for *every* AI query, ensuring unanchored metrics and fluff are caught even in standard mode or workflows.
- **Workflow Visualization**: Workflow Result Cards now display the **Truth Score Badge** and a red **Violation List** directly in the UI.
- **Interrogation Linkage**: Fixed a critical bug where clicking a violation in a Workflow step didn't highlight the text. Added `data-ai` attributes to specific workflow steps to enable "Click-to-Find".

### 2. Workflow Engine Upgrades
- **New Domain Workflows**:
    - **Wall Street Consensus (`wall_street`)**: A high-frequency financial pipeline (Scout -> Market Maker -> Hedge Fund -> Liquidator).
    - **UI/UX Foundry (`ui_foundry`)**: A design-first pipeline (Psychologist -> Visual Architect -> CSS Artisan -> A11y Audit).
- **Refined Templates**:
    - Upgraded `software_dev` to use `ai_architect` and `offensive_security` roles.
    - Upgraded `marketing_campaign` to use `cmo` and `web_designer`.
- **UI UX**:
    - **Alphabetical Sorting**: Workflow dropdown now sorts options A-Z for easier navigation.
    - **Pause/Stop Button**: Implemented a "Kill Switch" (`pauseWorkflowBtn`) that immediately halts the polling loop and cancels the backend job.

### 3. New AI Personas
- **Hedge Fund Manager (`hedge_fund`)**: Contrarian, alpha-seeking, forbids "financial advisor" disclaimers.
- **Market Maker (`market_maker`)**: Neutral, liquidity-focused, analyzes market microstructure.

## 🐛 Bug Fixes
- **Workflow Polling**: Fixed the polling loop to respect the `stopWorkflow()` signal immediately.
- **Violation Highlight**: Ensured scroll-to-text works in dynamically generated workflow cards.
