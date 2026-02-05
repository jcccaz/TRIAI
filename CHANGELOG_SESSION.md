# Session Changelog: Enforcement Engine & Visual Injection

## 1. Enforcement Engine (Anti-Hallucination Protocol)
**Objective:** implement a strict "Truth Contract" system to penalize generic outputs and unanchored metrics.

### Backend Updates
- **`council_roles.py`**:
  - Added `truth_contract` dictionaries to 19 key roles.
  - Contracts define `allowed`, `forbidden`, `must_label`, and `auto_interrogate_on` triggers.
- **`enforcement.py`**:
  - Created `EnforcementEngine` class.
  - Implemented `analyze_response` to check for:
    - **Generic Verbs** ("leverage", "optimize", etc.).
    - **Unanchored Numbers** (metrics without source contexts).
    - **Contract Violations** (forbidden terms).
  - Calculates `credibility_score` (0-100).
- **`app.py`**:
  - Integrated `EnforcementEngine`.
  - Updated `query_openai`, `query_anthropic`, `query_google`, `query_perplexity` to run enforcement checks.
  - Returns `enforcement` object in API response.

### Frontend Updates
- **`static/css/enforcement.css`**:
  - Added styles for `.credibility-badge` (Green/Yellow/Red).
  - Added styles for `.enforcement-report` and violation flags.
- **`static/app.js`**:
  - Implemented `renderEnforcementReport` to visualize audits dynamically.
  - Displays "Truth Score" in the card header.
  - Shows "Protocol Variance Detected" report with specific violations.

## 2. Visual & Document Injection (The "Eyes")
**Objective:** Enable drag-and-drop and paste support for images/PDFs.

- **`static/app.js`**:
  - Added `document.addEventListener('paste', ...)` to capture clipboard files (screenshots).
  - existing Drop zone logic connects to `process_file` in backend.

## 3. History Viewer UI
**Objective:** View past comparisons.

- Verified existing Sidebar UI and `loadHistory` logic in `app.js`.
- Confirmed implementation meets the "Local Time Machine" requirement.

## Next Steps
- **Test Enforcement:** Run queries in Council Mode to see credibility scores.
- **Refine Contracts:** Adjust allowed/forbidden terms based on false positives.
- **Interrogation Flow:** Connect the "Auto-Interrogate" triggers to the actual interrogation API (currently button-only).
