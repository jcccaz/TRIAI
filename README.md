# 🎯 TriAI Compare
### Forensic AI Response Analysis & Comparison Framework

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

**TriAI Compare** is a professional AI response analysis tool that goes beyond simple chat interfaces. It provides **forensic-level analysis** of how different AI models (GPT-4o, Claude 4.5, Gemini 2.5, Perplexity) respond to the same prompt, with unique features like **Council Mode**, **Hard Mode execution**, and **Execution Bias detection**.

While tools like Abacus.ai and ChatGPT exist, TriAI Compare is built for **researchers, developers, and power users** who need deep comparative analysis, not just chat responses.

---

## 🚀 What Makes This Different?

### 1. **Council Mode** 🏛️
Assign specific **expert roles** to each AI model. We now support **30+ specialized personas** including:
- **War Room**: Liquidator, Crisis Manager, Truth Auditor
- **Business**: CFO, General Counsel, Sales Engineer
- **Tech**: Fabric Architect, HAL Lead, Hacker
- **Science**: Physicist, Evolutionary Biologist, Cognitive Architect

👉 **[See the Full Roles Reference](ROLES_REFERENCE.md)** for all 30+ available personas.

### 2. **Hard Mode Execution** ⚡
Anti-sandbagging protocols that force AI models to:
- Provide specific numbers, not vague estimates
- Skip safety theater and narrative cushioning
- Deliver actionable insights, not generic advice
- Use forensic reasoning with `<thinking>` tags

### 3. **Execution Bias Detection** 🔍
Automatically classifies responses as:
- **Action-Forward**: Direct, executable steps
- **Advisory**: Strategic recommendations
- **Narrative**: Contextual analysis

### 4. **Universal Enforcement Engine** 👮
The system now universally enforces truthfulness across all queries (Standard, Council, or Workflow modes):
- **Truth Score Badge**: Every response gets a credibility score (0-100).
- **Violation Auditing**: Detected "Fluff", "Unanchored Metrics", or "Generic Platitudes" are flagged in real-time.
- **Interrogation Engine**: Click any flagged violation to instantly interrogate the AI about that specific claim.

### 5. **Workflow Engine** ⚡
Run complex, multi-step agentic pipelines that force models to collaborate:
- **Wall Street Consensus**: Scout (News) -> Market Maker (Liquidity) -> Hedge Fund (Alpha) -> Liquidator (Risk).
- **UI/UX Foundry**: Psychologist (Intent) -> Visual Architect (Vibe) -> UI Artisan (Code) -> Critic (A11y).
- **Crisis Response**: Immediate Triage -> Fact Check -> PR Strategy -> Recovery Plan.

### 6. **Mission Control Dashboard** 🎛️
Real-time telemetry and operational awareness:
- **Live KPI Cards**: Monitor prompts, costs, and system uptime.
- **Dynamic Usage Grid**: Heatmap of "Persona × Model" utilization to identify best-performing AI roles.
- **Voice Alerts**: "System Nominal" audio cues via ElevenLabs integration.
- **Visual Fabrication Engine**: Generate charts/graphs directly from data.

### 7. **Multi-Modal Support** 📎
- Upload PDFs, images, text files
- AI analyzes document content
- Image-based queries supported

### 8. **Persistent History** 💾
- SQLite/PostgreSQL storage
- Search past queries
- Export results
### 9. **Forensic Analysis** 🧠
- Extract hidden `<thinking>` tags to see AI reasoning
- Track response depth vs. thought process length
- **Execution Bias Detection**: Action-Forward vs. Advisory vs. Narrative

---

## ⚙️ Installation

### Prerequisites
- Python 3.8+
- API Keys for:
  - [OpenAI](https://platform.openai.com/)
  - [Anthropic](https://console.anthropic.com/)
  - [Google AI](https://makersuite.google.com/app/apikey)
  - [ElephantLabs](https://elevenlabs.io/) (Optional - for Voice Alerts)
  - [Perplexity](https://www.perplexity.ai/settings/api) (Optional)

### Quick Start

```bash
# 1. Clone the repository
git clone https://github.com/YOUR_USERNAME/triai-compare.git
cd triai-compare

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Create .env file
# Create a .env file in the project root with your API keys:
```

**`.env` file content:**
```env
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GOOGLE_API_KEY=AIza...
PERPLEXITY_API_KEY=pplx-...
```

```bash
# 5. Run the app
python app.py
```

Open your browser to `http://localhost:5000`

---

## 🎮 Usage

### Basic Comparison
1. Enter your question in the text box
2. Click "Compare Responses"
3. Get side-by-side responses from all 4 AI models

### Council Mode
1. Enable "Council Mode" toggle
2. Assign roles to each AI (Architect, Strategist, Researcher, etc.)
3. AI models respond from their assigned expert perspective

### Hard Mode
1. Enable "Hard Mode" toggle
2. AI models bypass safety theater and provide direct, actionable advice
3. Responses include mandatory `<thinking>` reasoning tags

### Visual Generation
1. Select a visual profile (Data Viz, Knowledge Graph, Blueprint, etc.)
2. AI responses automatically include generated visuals

---

## 🏗️ Architecture

For a deep dive into the v7.0 Architecture (including the **War Room Split** and **Truth Engine** logic), please see **[SYSTEM_ARCHITECTURE.md](SYSTEM_ARCHITECTURE.md)**.

```
triai-compare/
├── app.py                  # Main Flask application
├── database.py             # SQLite database manager
├── council_roles.py        # Council Mode role definitions
├── visuals.py              # Visual generation engine
├── workflows.py            # Domain-adaptive workflows
├── file_processor.py       # Multi-modal file handling
├── templates/
│   └── index.html          # Frontend UI
├── static/
│   ├── app.js              # Frontend logic
│   ├── css/                # Styles
│   └── img/fabricated/     # Generated visuals
└── requirements.txt        # Python dependencies
```

---

## 🧪 Testing

```bash
# Test all API connections
python test_apis.py

# Should output:
# ✅ GPT-4o WORKING!
# ✅ Claude Sonnet 4 WORKING!
# ✅ Gemini 2.5 WORKING!
# ✅ Perplexity Pro WORKING!
```

---

## 🔧 Configuration

### Council Roles Customization

Edit `council_roles.py` to add your own expert roles:

```python
COUNCIL_ROLES = {
    "your_custom_role": {
        "name": "Custom Expert",
        "prompt": "Your custom system prompt here",
        "emoji": "🎯"
    }
}
```

---

## 📊 Use Cases

### For Researchers
- Compare how different AI models interpret academic questions
- Analyze response bias and model alignment
- Export data for research papers

### For Developers
- Test AI model performance on technical queries
- Evaluate which model is best for specific tasks
- Benchmark response quality

### For Business Analysts
- Get multi-perspective strategic advice (Council Mode)
- Evaluate AI models for business use cases
- Cost-compare AI services

### For Writers & Content Creators
- See different creative approaches from each model
- Compare writing styles and tone
- Generate visual content ideas

---

## 🤝 Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

**Areas we'd love help with:**
- New Council Mode roles (Legal Expert, Medical Advisor, etc.)
- Additional visual generation profiles
- UI/UX improvements
- Documentation and tutorials
- Bug reports and feature requests

---

## 📜 License

MIT License - See [LICENSE](LICENSE) for details.

This means you can:
- ✅ Use commercially
- ✅ Modify and distribute
- ✅ Use privately
- ✅ Patent use

---

## 🙏 Acknowledgments

- **OpenAI** for GPT-4o API
- **Anthropic** for Claude 4.5 Sonnet API
- **Google** for Gemini 2.5 API
- **Perplexity** for Sonar Pro API

---

## 🗺️ Roadmap

- [ ] Add support for Mistral AI
- [ ] Team collaboration features
- [ ] API rate limiting and queue management
- [ ] Advanced analytics dashboard
- [ ] Chrome extension for one-click comparisons
- [ ] Export to Markdown, PDF, CSV
- [ ] Self-hosted deployment guides (Docker, Railway, Vercel)

---

## ⭐ Star This Repo

If you find this useful, please star the repo! It helps others discover the project.

---

**Built with ❤️ by Carlo | Powered by AI, Analyzed by Humans**
