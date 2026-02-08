# Lab Notebook: Visualization Engine Overhaul
**Date:** 2026-02-07
**Objective:** Replace "hallucinating" AI image generation (DALL-E/Imagen) with accurate, programmatic plotting (Matplotlib) for data visualization.

## Key Changes
1.  **Matplotlib Integration (`visuals.py`):**
    - Implemented `generate_matplotlib_chart(data, style)`.
    - Styles: 'professional' (White/Clean) and 'blueprint' (Navy/Monospace).
    - Logic: Extracts JSON data from text using GPT-4o, then plots vectors.

2.  **Routing Updates (`app.py`):**
    - Redirected `data-viz`, `chart`, and `blueprint` profiles to the Matplotlib engine.
    - **Removed** Mermaid.js path for now (consolidated to Python backend).

3.  **Fallback Policy:**
    - **Strict Mode Enabled:** If data extraction fails, the system returns an error (`None`) instead of falling back to DALL-E.
    - **DALL-E Demoted:** Only used for explicit 'art' or 'realistic' profiles, never for data.

## Current Status
- **Charts:** reliable, accurate, static PNGs.
- **Blueprints:** reliable, schematic-style, static PNGs.
- **Tables:** Extraction prompts upgraded to 4000 char context window.

## Next Steps
- Refine JSON extraction for non-standard Markdown tables.
- Consider adding Plotly/Chart.js for interactivity if needed.
- Re-evaluate Image Gen for purely artistic requests.

---

## Session 2: Council Role Enhancement & UX Polish

### Council Roles Upgraded
Added **Equity Research Analyst** role with full truth_contract and 5 numbered deliverables. Enhanced 6 existing roles to match this pattern:

| Role | Enhancement Summary |
|------|---------------------|
| `equity_research` | NEW - DCF, Comps, Bull/Base/Bear with BUY/HOLD/SELL |
| `medical` | Differential Dx, Workup, Treatment Protocol, Red Flags, Patient Ed |
| `tax` | IRC citations, entity analysis, audit risk scoring |
| `hacker` | MITRE ATT&CK mapping, CVE refs, attack + mitigation pairs |
| `validator` | Control framework IDs, audit evidence, gap analysis |
| `optimizer` | Baseline benchmarks, Big-O, p50/p95/p99 metrics |
| `marketing` | CAC/ROAS, conversion funnels, revenue attribution |

### UX Fixes
1. **Violation Highlight**: Red box → subtle yellow highlighter + `⚠` superscript
2. **Sticky Spinner**: `position: sticky` keeps loading indicator visible during scroll
3. **Role Dropdown**: Alphabetically sorted (40+ roles)

### Pattern Discovered
The key to high-quality AI output is **numbered deliverables** + **constraints that remove hedging**:
```
- Deliverables:
  1. Specific item with methodology
  2. Another item with framework reference
  ...
- CONSTRAINT: You are [professional role]. No [hedging language]. Provide [actionable output].
```
