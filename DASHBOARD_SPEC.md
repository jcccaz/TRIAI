# 🧠 TriAI Control Dashboard (Mission Control v1)

## Philosophy
**Think mission control, not admin panel.**
This dashboard is a research instrument and a career artifact. It demonstrates deep understanding of multi-agent cognitive architectures.

---

## 1️⃣ Dashboard Layout (Structure First)

### 🟦 Top Bar (Thin, Restrained)
*   **Left:** TriAI Logo
*   **Environment Toggle:**
    *   LOCAL :5000
    *   RAILWAY (Active)
    *   AWS
*   **Status Dot:**
    *   🟢 All systems nominal
    *   🟠 Cost drift
    *   🔴 Intervention required
*   **Right:**
    *   🔮 Cassandra Icon (Glow when active)
    *   🔊 Voice Toggle (Off by default)
    *   ⚙️ Settings

### 🟪 Left Rail (Icon-Only, Tooltip on Hover)
*   🧠 Profiles (Cognitive Posture)
*   🎭 Personas (Model Usage)
*   💸 Cost (Burn Logic)
*   🧬 Combos (Interaction Intelligence)
*   ☁️ Infra (Server Status)
*   🔮 Oracle Log (Cassandra)

---

## 2️⃣ Core Panels (The "Meat")

### 🧠 Panel 1: Profile Intelligence (Top Left)
**Title:** Cognitive Posture Distribution
**Visual:** Horizontal weighted bars (NOT pie charts). Colors tied to personas.
**Example metrics:**
*   Strategist: 42%
*   Architect: 28%
*   Defender: 18%
*   Auditor: 7%
*   Wildcard: 5%
**Metadata:**
*   Dominant posture (rolling 24h)
*   Drift velocity (↑ ↓ →)
*   Cassandra note (1 line max)

### 🎭 Panel 2: Persona + Model Usage (Top Right)
**Visual:** Data Grid
**Columns:** Persona | Model | Calls | Avg Tokens | Avg Cost
**Example:**
*   Strategist | GPT | 214 | 1,220 | $0.034
*   Architect | Claude | 168 | 2,010 | $0.041
**Hover Interactions:**
*   Show common failure modes
*   Show hallucination flags
*   Show interrogation rate

### 💸 Panel 3: Cost Reality (Center, Wide)
**Title:** Burn vs Value
**Left Side:**
*   Cost per prompt (rolling avg)
*   Cost per persona
*   Cost per combo
**Right Side:**
*   Hard thresholds
*   Cassandra triggers
*   "Silent burn" detection
**Visual Style:** Thin line graphs, dark background. No bright colors unless danger.

### 🧬 Panel 4: Combo Intelligence
**Visual:** Matrix View
**Columns:** Combo | Frequency | Outcome Score | Cost | Risk
**Example:**
*   GPT + Claude | High | ⭐⭐⭐⭐ | $$ | Low
**Drilldown:** Click a row to see disagreements and Cassandra verdicts.

### ☁️ Panel 5: Infra / AWS / Railway
**Split View:**
*   **Railway:** Service status, make/deploy time, CPU/Mem, Cost estimate.
*   **AWS:** EC2 status, Idle detection, Monthly burn.
**Cassandra Flag:** "Why is this on?" (Idle cost detection).

### 🔮 Panel 6: Cassandra Log (Bottom)
**Visual:** Scrollable, timestamped, immutable log.
**Philosophy:** She records judgment, not discussion.
**Examples:**
*   "I warned you at 14:32."
*   "Persona imbalance detected."
*   "No intervention required."
**Interaction:** Click to replay voice (Phase 2).

---

## 3️⃣ Tech Stack
*   **Frontend:** React + Vite, Tailwind (custom muted palette), Framer Motion (subtle).
*   **Backend:** Existing TriAI Flask/FastAPI.
*   **New Endpoints:** `/telemetry`, `/oracle/verdicts`.
*   **Data:** PostgreSQL (Railway). Tables: `prompts`, `personas`, `costs`, `combos`, `oracle_events`.
*   **Voice (Phase 2):** ElevenLabs / Artlist.

---

## 4️⃣ Build Order
### Phase 1 (Initial Build)
*   [ ] Dashboard Shell (Layout & Navigation)
*   [ ] Panel 3: Cost Reality (Cost per prompt)
*   [ ] Panel 2: Persona Usage
*   [ ] Panel 4: Combo Frequency
*   [ ] Panel 6: Static Cassandra Text Log

### Phase 2 (Intelligence)
*   [ ] Voice Alerts
*   [ ] Cognitive Drift Detection
*   [ ] AWS Idle Cost Logic
