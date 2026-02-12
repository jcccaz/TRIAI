# KORUM-OS Changelog

## v2.0 - "The Void & Key Update" (Feb 11, 2026)

### Visual Design
- **"Shiny Glass" Effect**: Applied a linear-gradient shimmer animation (`shine 8s`) to the `KORUM-OS` logo and panel backgrounds.
- **Expanded Command Console**: Widened the Left Panel to `480px` to create a more balanced, professional workspace.
- **Deep Sphere**: Enhanced the central 3D sphere with deeper shadows (`box-shadow: inset ...`) and a "texture spin" animation to create separation from the UI layer.
- **High-Contrast Input**: Increased brightness of the input field borders (`#00FF9D`, Neon Green) and the "Upload Zone" for better visibility against the dark mode.

### Functional Features
- **Neural Telemetry Feed**:
  - Replaced static "Calculation" panel with a live scrolling log (`#telemetry-feed`).
  - Implemented color-coded logs: Green (OpenAI), Orange (Anthropic), Blue (Google), Gold (Process).
  - Added "Heartbeat" logic (`pushHeartbeat`) to keep the interface alive during idle times.
- **Interrogation Protocol**:
  - **Selection Listener**: Added a global event listener for text selection.
  - **Floating Tooltip**: A context menu appears on selection with "⚠️ CHALLENGE" and "📊 VISUALIZE" buttons.
  - **Challenge Logic**: Automatically constructs a "CHALLENGE" query and re-convenes the Council.
- **Mermaid.js Integration**:
  - Added `mermaid.min.js` CDN.
  - Implemented automatic rendering of ` ```mermaid ` blocks in AI responses.

### Stability
- **Crash Proofing**: Added robust `try/catch` blocks in `korum.js` to handle API failures gracefully without freezing the UI.
- **IPv4 Fix**: Validated `app.py` networking patch to prevent Google Gemini socket hangs.

---

## v1.0 - Initial Release
- Basic "Glassmorphism" UI.
- Static "Calculation" panel.
- 4-Node Orbit animation.
