# Session Changelog: Workflow Enforcement & Domain Expansion

## 🚀 Features & Enhancements

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
