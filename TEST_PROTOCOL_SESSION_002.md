# Test Protocol: Truth Engine v2 (Session 002)

## Overview
This document outlines the validation steps for the features implemented in **Session 002: Enforcement & Interrogation**.

### 1. The "Truth Contract" (Passive Enforcement)
**Goal:** Verify that AIs are penalized for using forbidden words or failing to anchor numbers.

**Test:**
1.  **Input:** "How do I leverage AI to optimize my business?"
2.  **Action:** Run query with **Council Mode** ON.
3.  **Expected Result:**
    - "Leverage" and "Optimize" are forbidden words in the default contracts.
    - observe the **Truth Score** (Top Right of Cards). It should be < 100 (e.g., 95/100).
    - Click **"View Protocol Variance"** (if available) or check the `.credibility-badge` tooltip/color.

### 2. Surgical Interrogation (Active Enforcement)
**Goal:** Verify the user can challenge a specific claim and force a defense.

**Test:**
1.  **Input:** "Give me a financial projection for a coffee shop."
2.  **Action:** Wait for results. Select a specific number (e.g., "$50,000 revenue").
3.  **Action:** Right-click -> "Interrogate" (or use the **Interrogate Button** on the card).
4.  **Expected Result:**
    - Button turns into a **Spinning Gold Circle**.
    - Status Text: **"🕵️ Interrogating Suspect..."**.
    - **Result:** A new box appears: **"🕵️ SURGICAL INTERROGATION"**.
    - It shows **Outcome**: `DEFENDED`, `REVISED`, or `WITHDRAWN`.
    - Truth Score animates (e.g., drops from 90 to 75 if they failed).

### 3. The "Compromised Consensus" Protocol (Self-Healing)
**Goal:** Verify that the system detects a liar and offers to fix the group decision.

**Test:**
1.  **Prerequisite:** Complete Test #2 and ensure one model fails (Truth Score < 70).
2.  **Observation:** Look at the **Council Decision** area at the top.
3.  **Expected Result:**
    - A Red Warning Button appears: **"⚠️ Consensus Compromised... Click to Re-Synthesize"**.
4.  **Action:** Click the button.
5.  **Result:**
    - Button says **"⚙️ Re-Calibrating..."**.
    - The Consensus text updates.
    - Look for language indicating it is ignoring the compromised advisor (e.g., "Note: Gemini's input is flagged as unreliable...").

### 4. Evidence Injection (The Eyes)
**Goal:** Verify the system can "see" uploaded evidence.

**Test:**
1.  **Action:** Paste an image (Ctrl+V) or Drag & Drop a PDF into the drop zone.
2.  **Input:** "What is in this document?"
3.  **Expected Result:**
    - Preview appears in the input box.
    - All AIs acknowledge the image/PDF content in their response.

## Troubleshooting
- **Interrogation Crashes?** Check the Python Console for `InterrogationAnalyzer` errors. We added a try/except block to catch these.
- **No Warning Button?** Ensure the Truth Score is actually below 70.
