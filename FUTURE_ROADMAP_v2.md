# Future Roadmap

## 1. Local LLM Integration (LM Studio / Stealth Mode) 🕵️‍♂️
- **Concept:** Enable "Stealth Mode" where TriAI switches from cloud providers (OpenAI/Google) to a local LM Studio instance (`localhost:1234`).
- **Use Case:** Sensitive strategy, highly confidential IP, or uncensored "Red Team" analysis using models like Dolphin-Mixtral.
- **Tech:** Add `Local` provider to `app.py` pointed at generic OpenAI-compatible endpoint.

## 2. Advanced Analytics Dashboard 📊
- **Concept:** A dedicated `/analytics` route with deep insights into system performance and model behavior.
- **Metrics:**
    - **Cost Per Query:** Real-time API spend tracking.
    - **Model Win Rate:** Which provider (GPT/Claude/Gemini) is winning the "Pick Winner" votes?
    - **Persona Drift:** Sentiment analysis to verify if "Aggressive" roles are actually aggressive.
    - **Latency:** Response time trends.
- **Tech:** Chart.js frontend, SQLite aggregation queries backend.

## 3. Professional & Social Export Suite 📤
- **Concept:** Turn chat artifacts into shareable assets.
- **Formats:**
    - **CSV/Excel:** Download raw financial tables (already partially built).
    - **PDF Briefing:** Compile full chat history into a branded "Executive Report".
    - **Social Share:** Format chart + summary for LinkedIn/Twitter posts ("One-Click Insight").

## 4. "The Crypto Quant" Persona 🪙
- **Concept:** A specialized role for cryptocurrency analysis.
- **Capabilities:**
    - Whitepaper auditing (for red flags/tokenomics).
    - Liquidation price calculators.
    - Chain analysis (parsing wallet transaction descriptions).
- **Requirements:** Integration with CoinGecko or similar free API for real-time price awareness.

## 5. Persistent Database Migration (PostgreSQL) 🗄️
- **Concept:** Migrate from SQLite to Railway PostgreSQL to prevent data loss on deployment.
- **Priority:** High (before serious production use).
