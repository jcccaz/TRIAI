# TriApp Gold Noir Edition - Configuration Lock
**Date:** 2026-01-27
**Status:** STABLE - LOCKED

## 🎨 Aesthetic Profile: "Gold Noir" / "Digital Brutalist"
- **Primary Background:** #050505 (True Black)
- **Secondary Background:** #0f0f11 (Charcoal)
- **Primary Accent:** #d4af37 (Signal Gold)
- **Secondary Accent:** #8b8580 (Taupe/Bronze)
- **Text:** #f0f0f0 (Stark White)

## 🎥 Video Configuration
The application uses a dual-video system for dynamic interaction:

### 1. Idle / Ambient Layer
- **File:** `static/videos/backround_main.mp4`
- **Description:** "Gen 4" Static Camera, Gold Noir ambiance.
- **Behavior:** Autoplays on loop, 15% Opacity.
- **Trigger:** Default state, returns after processing.

### 2. Processing / Action Layer
- **File:** `static/videos/processing_gold_final.mp4`
- **Description:** High-speed "Gold Data Tunnel".
- **Behavior:** 60% Opacity, high energy.
- **Trigger:** JavaScript event on "Ask All AIs" button.

## 💾 Critical Files
- **`templates/index.html`**: Contains the HTML structure for the 2-layer video container.
- **`static/css/history_video.css`**: Controls video layering, z-index, and transition opacity.
- **`static/style.css`**: Contains the full CSS Variable definitions for the Gold Noir palette.
- **`static/app.js`**: Contains logic for switching video classes (`.active`) during API calls.
