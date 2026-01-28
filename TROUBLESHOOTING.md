# 🛠️ Troubleshooting Guide

## Common API Errors and Solutions

### 1. OpenAI - "Quota Exceeded" Error (429)

**Error Message:**
```
Error: Error code: 429 - You exceeded your current quota, please check your plan and billing details
```

**Why This Happens:**
- You haven't added credits to your OpenAI account yet
- Your free trial credits have run out
- You've hit your usage limit

**How to Fix:**
1. Go to https://platform.openai.com/account/billing
2. Click "Add payment method"
3. Add at least $5-10 in credits
4. Wait a few minutes for it to activate
5. Refresh the TriAI Compare page and try again

**Alternative:** If you don't want to add credits yet, the app will still work with the other two AIs (Anthropic and Google)!

---

### 2. Anthropic - Model Not Found Error (404)

**Error Message:**
```
Error: 404 - model: claude-3-5-sonnet-latest not found
```

**Fixed!** ✅ I've updated the code to use `claude-3-5-sonnet-20241022` which should work.

---

### 3. Google - Model Not Found Error (404)

**Error Message:**
```
Error: 404 models/gemini-1.5-flash is not found
```

**Fixed!** ✅ I've updated the code to use `gemini-1.5-pro` which should work.

---

## Testing Your Setup

Run this command to verify your API keys are configured:

```bash
python test_setup.py
```

It will show you which API keys are detected.

---

## About API Costs

### Free Tiers & Pricing:

**OpenAI (GPT-3.5 Turbo)**
- ❌ No free tier anymore
- 💰 ~$0.0005 per question (very cheap)
- Need to add credits first

**Anthropic (Claude 3.5 Sonnet)**
- ✅ Free tier: $5 credits for new users
- 💰 ~$0.003 per question after free tier
- Most expensive but very high quality

**Google (Gemini 1.5 Pro)**
- ✅ Free tier: 1500 requests/day
- 💰 Free for most personal use
- Best value!

### Cost per Query (All 3 AIs):
- **GPT-3.5 + Claude + Gemini**: ~$0.0035 per question
- **Just Claude + Gemini** (no OpenAI): ~$0.003 per question or FREE on Gemini tier

---

## Current Model Configuration

The app is currently set to use:

1. **OpenAI**: `gpt-3.5-turbo` (fast, cheap, needs credits)
2. **Anthropic**: `claude-3-5-sonnet-20241022` (highest quality)
3. **Google**: `gemini-1.5-pro` (free tier available)

---

## What to Do Right Now

### Option A: Use All Three AIs
1. Add $5-10 credits to OpenAI: https://platform.openai.com/account/billing
2. Wait 2-3 minutes
3. Refresh the page and try again
4. All three should work! 🎉

### Option B: Use Just Claude + Gemini
1. The app will still show errors for OpenAI
2. **But Claude and Gemini should work!** ✅
3. You can compare two AI perspectives while you set up OpenAI

### Option C: Check What Works Now
1. **Refresh the page**: http://localhost:5000
2. Ask a question
3. See which AIs respond successfully!

---

## Need Help?

If you're still seeing errors:
1. Check the exact error message
2. Verify your API key is correct in the `.env` file
3. Make sure there are no extra spaces or quotes around the key
4. Try regenerating the API key from the provider's dashboard

---

**Tip:** Google Gemini has the most generous free tier, so it's the easiest to test with!
