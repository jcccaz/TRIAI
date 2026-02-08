# Session Changelog - 2026-02-07

## 1. Visualization Engine Overhaul 📊
- **Objective:** Fix "Chart generation failed" errors on complex financial data (Project Phoenix).
- **Fix:** Rewrote `visuals.py` extraction logic.
    - Added **Universal Key Detection** (scans JSON for any list of numbers).
    - Added **Regex Fallback** (scans raw text for numbers if JSON extraction fails).
    - Added **Clean Table Input** (strips `|`, `$`, formulas before LLM processing).
    - Fixed `app.js` to correctly send highlighted text in the payload.
- **Result:** Successfully charted the "Project Phoenix" liquidation table.

## 2. Infrastructure Hardening (PostgreSQL Migration) 🗄️
- **Objective:** Prevent data loss on Railway deployments.
- **Action:** Migrated `database.py` from raw SQLite to **SQLAlchemy ORM**.
- **Result:** 
    - **Local:** Auto-detects and uses `sqlite:///comparisons.db` (No change to workflow).
    - **Production (Railway):** Auto-detects `DATABASE_URL` and uses **PostgreSQL**.
    - Data is now persistent across redeploys.

## 3. Roadmap Expansion 🗺️
- Added `FUTURE_ROADMAP_v2.md` with:
    - **Stealth Mode:** Local LLM integration (LM Studio).
    - **Analytics Dashboard:** Cost/Win-rate tracking.
    - **Crypto Persona:** Specialized quantitative role.
    - **Professional Exports:** PDF/CSV/Social generation.

## Dependencies Added
- `psycopg2-binary` (Postgres driver)
- `SQLAlchemy` (ORM)
