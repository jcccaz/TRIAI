"""
Quick test to verify all three AI services work with current 2026 models
"""
import os
from dotenv import load_dotenv

load_dotenv()

print("="*70)
print("🤖 TriAI Compare - 2026 Model Verification Test")
print("="*70)

# Test OpenAI GPT-4o
print("\n1️⃣  Testing OpenAI GPT-4o...")
try:
    import openai
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key or api_key == 'your-openai-key-here':
        print("   ❌ API Key not configured")
    else:
        client = openai.OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": "Say 'Hello from GPT-4o!'"}],
            max_tokens=20
        )
        print(f"   ✅ GPT-4o WORKING!")
        print(f"   Response: {response.choices[0].message.content}")
except Exception as e:
    print(f"   ❌ Error: {str(e)[:100]}")

# Test Anthropic Claude Sonnet 4
print("\n2️⃣  Testing Anthropic Claude Sonnet 4...")
try:
    import anthropic
    api_key = os.getenv('ANTHROPIC_API_KEY')
    if not api_key or api_key == 'your-anthropic-key-here':
        print("   ❌ API Key not configured")
    else:
        client = anthropic.Anthropic(api_key=api_key)
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=20,
            messages=[{"role": "user", "content": "Say 'Hello from Claude Sonnet 4!'"}]
        )
        print(f"   ✅ Claude Sonnet 4 WORKING!")
        print(f"   Response: {response.content[0].text}")
except Exception as e:
    print(f"   ❌ Error: {str(e)[:100]}")

# Test Google Gemini 2.5
print("\n3️⃣  Testing Google Gemini 2.5/3.0...")
try:
    import google.generativeai as genai
    api_key = os.getenv('GOOGLE_API_KEY')
    if not api_key or api_key == 'your-google-key-here':
        print("   ❌ API Key not configured")
    else:
        genai.configure(api_key=api_key)
        
        # Try 2026 models in order
        models_to_try = ['gemini-2.5-pro', 'gemini-3-pro', 'gemini-2.5-flash']
        
        for model_name in models_to_try:
            try:
                model = genai.GenerativeModel(model_name)
                response = model.generate_content("Say 'Hello from Gemini!'")
                print(f"   ✅ {model_name.upper()} WORKING!")
                print(f"   Response: {response.text}")
                break
            except Exception as e:
                print(f"   ⚠️  {model_name} not available, trying next...")
                continue
        else:
            print(f"   ❌ None of the Gemini models worked")
            
except Exception as e:
    print(f"   ❌ Error: {str(e)[:100]}")

print("\n" + "="*70)
print("✨ Test Complete!")
print("="*70)
print("\nIf all three show ✅, your app is ready to use!")
print("Run: python app.py")
print("Then open: http://localhost:5000")
