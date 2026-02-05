# Enhancements Completed

## ✅ History & Database
- [x] Added History Sidebar (Slide-out panel)
- [x] Implemented Database Storage (`comparisons.db`)
- [x] Added "History" Toggle Button in Header
- [x] Automatic saving of Questions & Answers
- [x] Click-to-restore functionality for past queries

## ✅ Visual Overhaul (Gold Noir / Digital Brutalist)
- [x] **Color Palette Rebrand:**
    - Main: Deep Black & Charcoal
    - Accents: Signal Gold (#d4af37) & Taupe
    - Text: Stark White & Grey
- [x] **Dynamic Video Background System:**
    - Idle State: `backround_main.mp4` (15% Opacity)
    - Processing State: `processing_gold_final.mp4` (60% Opacity)
    - Logic: Seamless transitions
- [x] **Layout:** 2x2 Grid for 4 AI Comparison

## ✅ Council Mode & Roles
- [x] **Dynamic Role Assignment:** Assign expert personas (e.g., "Liquidator", "Systems Architect") to specific models.
- [x] **Corporate Shark Role:** Added "Corporate Shark" (Takeover Specialist) for aggressive strategic analysis.
- [x] **Normalized Role Names:** Polished titles (e.g., "The Liquidator" -> "Liquidator") for better prompts.
- [x] **Aggressive Devil's Advocate:** Patched the "Critic" role to forbid helpfulness and enforce red-teaming.

## ✅ Anti-Sandbagging
- [x] **Dual-Level Detection:**
    - 🚨 **Red (CRITICAL):** Generic/Refusal/Safety-heavy responses.
    - ⚠️ **Yellow (WARNING):** Thought Imbalance (Thinking > 1.6x Output).
- [x] **Visual Alerts:** Pulse animations for sandbagging badges.

## ✅ Bug Fixes
- [x] Fixed "messages name error" in Claude API integration.
- [x] Fixed Browser Caching issues for video files.
- [x] Fixed Git Merge Conflicts in documentation.

## ✅ Backend
- [x] Migrated to Google GenAI SDK (`google-genai`).
- [x] **Models Updated:**
    - GPT-5.2 (High-Reasoning)
    - Claude 4.5 Sonnet
    - Gemini 3.0 Pro/Flash
    - Perplexity Sonar Pro
