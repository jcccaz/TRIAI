# Dynamic Role Assignment for Council Mode ✅

## Overview
Successfully implemented **Dynamic Role Assignment** for Council Mode, allowing you to customize which expert role each AI model adopts for any given query.

## 🎯 What's New

### 1. **High-Resolution Role Library** (12 Technical Roles) ✅
Located in `council_roles.py`:

### ️ Technical & Engineering
- 🏗️ **Systems Architect** - Lead Technical Architect; focuses on specific libs (Three.js), patterns, and infra.
- ⚡ **System Optimizer** - Performance Engineering; efficiency maximization and latency reduction.
- ♟️ **Ops Strategist** - Infra & Operations Strategist; spec'ing CI/CD, k8s, and Gantt-style deployment.
- 🏴‍☠️ **Offensive Security Lead** - Red Teaming, exploits, and breaking the system.
- 📡 **Telecom Pro** - Telecom Infrastructure; 5G, Fiber, and RAN optimization.
- 🕸️ **Network Engineer** - Network Systems; resilient, scalable data center networks.
- 🧠 **Cognitive Architect** - The "Brain Builder"; RAG pipelines, vector schemas, and token economics.
- 🖌️ **UI Artisan** - The "Visual Stylist"; pixel-perfect CSS, HSL color theory, and micro-interactions.

### 💼 Business & Law
- 💰 **CFO** - Budget Architect; TCO calculations, ROI projections, and fiscal viability.
- 📈 **Business Strategist** - Market Intelligence; GTM strategy and competitive analysis.
- 🎯 **Product Lead** - User-centric lead; MoSCoW prioritization and MVP sequencing.
- ⚖️ **International Jurist** - Global legal synthesis and statute citation.
- 🧾 **Forensic Tax Strategist** - Wealth preservation, loopholes, and compliance.
- 📣 **Chief Marketing Officer** - Viral persuasion and conversion psychology.
- 🤝 **Negotiator** - High-Stakes Resolution; finding hidden motivations and de-escalating.
- ⚔️ **Corporate Shark** - Competitive Neutralization; identifying weaknesses and strategic levers.

### 💰 Financial High-Frequency
*New Domain*
- **Hedge Fund Manager (`hedge_fund`)**: Alpha-seeking, contrarian, and risk-adjusted. Specifically instructed to skip "financial advisor" disclaimers.
- **Market Maker (`market_maker`)**: Neutral, liquidity-focused, analyzes microstructure and order flow rather than price direction.

### 🔬 Science & Medicine
- 🧬 **Evolutionary Biologist** - Systems analysis via natural selection and adaptation.
- ⚕️ **Chief Medical Officer** - Clinical precision and differential diagnosis.
- 🧪 **Molecular Chemist** - Elemental analysis and thermodynamic decomposition.
- 🌌 **Theoretical Physicist** - First Principles and thought experiments.
- 🧠 **Behavioral Psychologist** - Decoding human motivation and cognitive bias.
- 💀 **Liquidator** - Chief Liquidation Officer; ruthlessly identifying floor value.
- ☣️ **Crisis Manager** - Forensic Crisis Lead; architectural containment of failures.

### 🎨 Creative & Humanities
- 🔮 **Futurist** - Chief Futurist; predicts 5-10 year transformations and paradigm shifts.
- ✍️ **Avant-Garde Author** - Radical originality; anti-cliché creative writing.
- 🎼 **Virtuoso Musicologist** - Sonic theory, production, and cultural history.
- 📜 **Historian** - Technical Historian; tracing lineage and learning from historical patterns.
- 🎨 **UX Architect** - Experience Layer; motion physics, HMI logic, and interactive sophistication.
- 🎓 **Distinguished Professor** - Radical engagement; 'Cool Professor' pedagogical hook.

### 🔎 Research & Validation
- 📊 **Forensic Analyst** - Senior Data Forensic Analyst; quantitative decomposition and forensic proof.
- 😈 **Devil's Advocate** - Lead Red-Teamer; fragility detection and system hardening.
- 🔬 **Lead Researcher** - Lead Forensic Researcher; technical manuals, whitepapers, and proprietary 'how-to' guides.
- 👨‍🏫 **Technical Mentor** - Pedagogical Engineer; deep-dive conceptual models and First Principles.
- 📚 **Archivist** - Documentation Lead; generating RFCs, SOPs, and structured archives.
- ✅ **Compliance Officer** - Lead Compliance & QA Officer; mandate enforcement (NIST/FedRAMP) and quality assurance.
- ⚖️ **Ethicist** - Algorithmic Ethicist; impact audits and responsible-by-design guardrails.
- 🕵️‍♂️ **Private Investigator** - Deductive reasoning and connecting hidden dots.
- 🕵️ **Truth Auditor** - Algorithmic Integrity; detecting sandbagging and alignment tax.
- 🎭 **Spy Master** - Counter-Intelligence; strategic re-contextualization and camouflage.

### 2. **UI: Role Selector Dropdowns**
- **Appears automatically** when Council Mode toggle is ON
- **Grid layout** showing all 4 AI models with dropdown role selectors
- **Default assignments**:
  - OpenAI (GPT-5.2): Visionary
  - Anthropic (Claude): Architect
  - Google (Gemini): Critic
  - Perplexity: Researcher

### 3. **Backend: Dynamic Role Injection**
- Each AI query function (`query_openai`, `query_anthropic`, `query_google`, `query_perplexity`) now:
  - Accepts a `role` parameter
  - Dynamically loads the role configuration from `councilroles.py`
  - Injects the appropriate system prompt for that role
  - Displays the role name in the card header (e.g., "Claude 4.5 Sonnet (Architect)")

### 4. **Frontend: Role Capture & Transmission**
- JavaScript function `getCouncilRoles()` captures selected roles from dropdowns
- Roles are automatically sent with the API request when Council Mode is enabled
- Supports both JSON and FormData request formats

## 🚀 How to Use

1. **Toggle Council Mode ON** 🏛️
2. **Role selector panel appears** below the model buttons
3. **Assign roles** to each AI using the dropdowns
4. **Ask your question** - Each AI will respond from their assigned perspective

## 📁 Files Modified/Created

### Created:
- `council_roles.py` - Role configuration library
- `static/css/role_selectors.css` - Styling for role UI

### Modified:
- `app.py` - Import roles, extract from request, pass to query functions
- `templates/index.html` - Added role selector UI and CSS link
- `static/app.js` - Added show/hide logic and role capture function

## 💡 Use Cases

### IT/Software Development:
- **Architect**: Design system architecture
- **Critic**: Code review, security audit
- **Optimizer**: Performance improvements

### Business Strategy:
- **Strategist**: Business planning
- **Analyst**: Market analysis
- **Ethicist**: Corporate responsibility

### Research & Education:
- **Researcher**: Literature review
- **Teacher**: Explain complex concepts
- **Historian**: Historical context

### Creative Projects:
- **Innovator**: Brainstorming
- **Visionary**: Future possibilities
- **Critic**: Constructive critique

## 🎨 UI Features
- **Smooth slide-down animation** when Council Mode is enabled
- **Gold Noir aesthetic** matching the app's design
- **Responsive 2-column grid** (stacks to 1 column on mobile)
- **Emoji icons** for each role for quick visual identification

## 🎉 Ready to Test!

The feature is **fully functional** and ready to use! Refresh your browser (Ctrl+F5) and toggle Council Mode ON to see the role selectors in action.

Try asking a question like:
> "Design a microservices architecture for a social media platform"

Then experiment with different role assignments:
- Claude as **Architect** (design the system)
- GPT as **Critic** (find potential issues)
- Gemini as **Optimizer** (improve efficiency)
- Perplexity as **Researcher** (industry best practices)

Enjoy your **flexible AI council**! 🏛️✨
