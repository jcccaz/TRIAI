<<<<<<< HEAD
# 🚀 TriAI Compare - Quick Start Guide

## What You Have

A beautiful web app that sends ONE question to THREE AI services:
- **OpenAI** (GPT-4)
- **Anthropic** (Claude 3.5 Sonnet)  
- **Google** (Gemini Pro)

All responses appear **side-by-side** with timing data!

---

## ⚡ Quick Start (3 Steps)

### Step 1: Get API Keys

You need three API keys (most offer free tiers):

1. **OpenAI**: https://platform.openai.com/api-keys
   - Sign up → Create new secret key → Copy it

2. **Anthropic**: https://console.anthropic.com/
   - Sign up → API Keys → Create key → Copy it

3. **Google AI Studio**: https://makersuite.google.com/app/apikey
   - Sign in → Get API key → Create API key → Copy it

### Step 2: Configure Keys

Create a file called `.env` in the `tri_ai_compare` folder:

```bash
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxx
ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxx
GOOGLE_API_KEY=xxxxxxxxxxxxx
```

💡 **Tip**: Copy `.env.example` and rename it to `.env`, then paste your keys

### Step 3: Run the App

```bash
cd tri_ai_compare
python test_setup.py    # Verify keys are configured
python app.py           # Start the server
```

Then open: **http://localhost:5000**

---

## 🎯 How to Use

1. **Enter your question** in the text box
2. **Click "Ask All AIs"** (or press Ctrl/Cmd + Enter)
3. **Watch** as all three AIs respond in parallel
4. **Compare** responses, check response times
5. **Copy** any response with the copy button

---

## 🎨 Features

✨ **Parallel queries** - All three AIs respond simultaneously  
⏱️ **Response timing** - See which AI is fastest  
📋 **One-click copy** - Copy any response to clipboard  
🎨 **Premium UI** - Beautiful dark theme with gradients  
⌨️ **Keyboard shortcuts** - Ctrl/Cmd + Enter to submit  

---

## 💰 Cost Considerations

- All three services have **free tiers** with monthly credits
- Typical question costs: **$0.01 - $0.05** total (across all 3)
- Monitor your usage in each provider's dashboard

---

## 🔧 Troubleshooting

### "API Key Error"
- Make sure `.env` file exists (not `.env.example`)
- Check that keys are pasted correctly (no extra spaces)
- Run `python test_setup.py` to verify

### "Module not found"
```bash
pip install -r requirements.txt
```

### Port already in use
Edit `app.py` and change port 5000 to something else like 5001

---

## 🚀 Example Questions to Try

- "Explain quantum computing in simple terms"
- "Write a haiku about artificial intelligence"
- "What are the key differences between Python and JavaScript?"
- "How would you explain blockchain to a 10-year-old?"
- "What's the most efficient way to learn a new programming language?"

---

## 📂 Project Structure

```
tri_ai_compare/
├── app.py              # Flask backend
├── test_setup.py       # API key verification
├── requirements.txt    # Dependencies
├── .env               # Your API keys (create this!)
├── templates/
│   └── index.html     # UI
└── static/
    ├── style.css      # Styles
    └── app.js         # Frontend logic
```

---

## 🎓 Next Steps

Once you have it running, you could:
- Add more AI models (Mistral, Cohere, etc.)
- Save favorite comparisons
- Add streaming responses
- Export results to PDF
- Track token usage and costs

---

**Ready to compare AI perspectives? Let's go! 🚀**
=======
# 🚀 TriAI Compare - Quick Start Guide

## What You Have

A beautiful web app that sends ONE question to THREE AI services:
- **OpenAI** (GPT-4)
- **Anthropic** (Claude 3.5 Sonnet)  
- **Google** (Gemini Pro)

All responses appear **side-by-side** with timing data!

---

## ⚡ Quick Start (3 Steps)

### Step 1: Get API Keys

You need three API keys (most offer free tiers):

1. **OpenAI**: https://platform.openai.com/api-keys
   - Sign up → Create new secret key → Copy it

2. **Anthropic**: https://console.anthropic.com/
   - Sign up → API Keys → Create key → Copy it

3. **Google AI Studio**: https://makersuite.google.com/app/apikey
   - Sign in → Get API key → Create API key → Copy it

### Step 2: Configure Keys

Create a file called `.env` in the `tri_ai_compare` folder:

```bash
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxx
ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxx
GOOGLE_API_KEY=xxxxxxxxxxxxx
```

💡 **Tip**: Copy `.env.example` and rename it to `.env`, then paste your keys

### Step 3: Run the App

```bash
cd tri_ai_compare
python test_setup.py    # Verify keys are configured
python app.py           # Start the server
```

Then open: **http://localhost:5000**

---

## 🎯 How to Use

1. **Enter your question** in the text box
2. **Click "Ask All AIs"** (or press Ctrl/Cmd + Enter)
3. **Watch** as all three AIs respond in parallel
4. **Compare** responses, check response times
5. **Copy** any response with the copy button

---

## 🎨 Features

✨ **Parallel queries** - All three AIs respond simultaneously  
⏱️ **Response timing** - See which AI is fastest  
📋 **One-click copy** - Copy any response to clipboard  
🎨 **Premium UI** - Beautiful dark theme with gradients  
⌨️ **Keyboard shortcuts** - Ctrl/Cmd + Enter to submit  

---

## 💰 Cost Considerations

- All three services have **free tiers** with monthly credits
- Typical question costs: **$0.01 - $0.05** total (across all 3)
- Monitor your usage in each provider's dashboard

---

## 🔧 Troubleshooting

### "API Key Error"
- Make sure `.env` file exists (not `.env.example`)
- Check that keys are pasted correctly (no extra spaces)
- Run `python test_setup.py` to verify

### "Module not found"
```bash
pip install -r requirements.txt
```

### Port already in use
Edit `app.py` and change port 5000 to something else like 5001

---

## 🚀 Example Questions to Try

- "Explain quantum computing in simple terms"
- "Write a haiku about artificial intelligence"
- "What are the key differences between Python and JavaScript?"
- "How would you explain blockchain to a 10-year-old?"
- "What's the most efficient way to learn a new programming language?"

---

## 📂 Project Structure

```
tri_ai_compare/
├── app.py              # Flask backend
├── test_setup.py       # API key verification
├── requirements.txt    # Dependencies
├── .env               # Your API keys (create this!)
├── templates/
│   └── index.html     # UI
└── static/
    ├── style.css      # Styles
    └── app.js         # Frontend logic
```

---

## 🎓 Next Steps

Once you have it running, you could:
- Add more AI models (Mistral, Cohere, etc.)
- Save favorite comparisons
- Add streaming responses
- Export results to PDF
- Track token usage and costs

---

**Ready to compare AI perspectives? Let's go! 🚀**
>>>>>>> 6added3 (Initial commit: TriApp multi-AI comparison tool with GPT-5.2, Claude 4.5 Sonnet, Gemini 3.0, and Perplexity Pro support)
