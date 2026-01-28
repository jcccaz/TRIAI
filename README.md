# TriAI Compare - Multi-AI Response Comparison Tool

A sleek web application that sends your question to three major AI services (OpenAI, Anthropic, Google) simultaneously and displays their responses side-by-side for easy comparison.

## Features

✨ **Four AI Services**: Query GPT-4o, Claude 3.5 Sonnet, Gemini 3.0, and Perplexity Pro simultaneously  
⚡ **Parallel Processing**: Get all responses at the same time  
🎙️ **Podcast Mode**: Listen to AIs debate your question in a generated podcast format  
🧠 **Vault Context**: Securely search your local Obsidian notes for context  
📊 **Mermaid Diagrams**: Automatically render architecture charts and flows  
📂 **Project Memory**: Remembers your recent project interactions  
⏱️ **Response Time & Cost**: Track speed and estimated cost per query  
🎨 **Premium 'Gold Noir' UI**: Digital Brutalism aesthetic  

## Setup Instructions

### 1. Install Dependencies

```bash
cd tri_ai_compare
pip install -r requirements.txt
```

### 2. Configure API Keys

Create a `.env` file:

```env
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GOOGLE_API_KEY=...
PERPLEXITY_API_KEY=pplx-...
```

### 3. Run the Application

```bash
python app.py
```

Visit `http://localhost:5000`

## Structure

```
tri_ai_compare/
├── app.py                 # Flask backend (API + Logic)
├── database.py            # SQLite History
├── project_manager.py     # Session Memory
├── templates/index.html   # Main Interface
├── static/
│   ├── style.css         # Gold Noir CSS
│   └── app.js            # Frontend Logic
└── Procfile               # Deployment Config
```

## Roadmap

- [x] Add Perplexity AI
- [x] Podcast Audio Mode
- [x] Obsidian Integration
- [x] Diagram Generation (Mermaid)
- [ ] User Auth / Monetization
- [ ] Cloud Deployment
- [ ] Mobile App Wrapper

---

Built for the **FrankNet** Workstation.
