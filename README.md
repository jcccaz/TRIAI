<<<<<<< HEAD
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
=======
# TriAI Compare - Multi-AI Response Comparison Tool

A sleek web application that sends your question to three major AI services (OpenAI, Anthropic, Google) simultaneously and displays their responses side-by-side for easy comparison.

## Features

✨ **Three AI Services in One**: Query GPT-4, Claude 3.5 Sonnet, and Gemini Pro simultaneously  
⚡ **Parallel Processing**: Get all responses at the same time  
⏱️ **Response Time Tracking**: See how fast each AI responds  
📋 **Copy to Clipboard**: Easily copy any response  
🎨 **Premium Dark UI**: Beautiful, modern interface with smooth animations  
⌨️ **Keyboard Shortcuts**: Press Ctrl/Cmd + Enter to submit

## Setup Instructions

### 1. Install Dependencies

```bash
cd tri_ai_compare
pip install -r requirements.txt
```

### 2. Configure API Keys

You'll need API keys from three services:

- **OpenAI**: Get from https://platform.openai.com/api-keys
- **Anthropic**: Get from https://console.anthropic.com/
- **Google AI**: Get from https://makersuite.google.com/app/apikey

#### Option A: Environment Variables (Recommended)

Create a `.env` file in the `tri_ai_compare` directory:

```env
OPENAI_API_KEY=your-openai-key-here
ANTHROPIC_API_KEY=your-anthropic-key-here
GOOGLE_API_KEY=your-google-key-here
```

#### Option B: Direct in Code

Edit `app.py` and replace the placeholder values:

```python
OPENAI_API_KEY = 'your-openai-key-here'
ANTHROPIC_API_KEY = 'your-anthropic-key-here'
GOOGLE_API_KEY = 'your-google-key-here'
```

### 3. Run the Application

```bash
python app.py
```

The app will start at `http://localhost:5000`

## Usage

1. Open your browser to `http://localhost:5000`
2. Enter your question in the text area
3. Click "Ask All AIs" or press Ctrl/Cmd + Enter
4. Watch as all three AIs respond in parallel
5. Compare responses, check response times, and copy text as needed

## Tech Stack

- **Backend**: Python Flask
- **Frontend**: Vanilla JavaScript, HTML, CSS
- **AI APIs**: OpenAI, Anthropic, Google Generative AI
- **Design**: Premium dark theme with gradient accents

## Project Structure

```
tri_ai_compare/
├── app.py                 # Flask backend
├── requirements.txt       # Python dependencies
├── templates/
│   └── index.html        # Main HTML template
└── static/
    ├── style.css         # Styles
    └── app.js            # Frontend JavaScript
```

## Notes

- API calls may incur costs depending on your usage and plan
- Ensure you have sufficient API credits/quota for all three services
- Response times vary based on network conditions and API availability
- The app uses parallel execution for faster results

## Future Enhancements

- [ ] Add more AI models (Mistral, Cohere, etc.)
- [ ] Save comparison history
- [ ] Export comparisons as PDF/Markdown
- [ ] Add streaming responses
- [ ] Token usage tracking
- [ ] Custom model selection

---

Built with ❤️ for comparing AI perspectives
>>>>>>> 6added3 (Initial commit: TriApp multi-AI comparison tool with GPT-5.2, Claude 4.5 Sonnet, Gemini 3.0, and Perplexity Pro support)
