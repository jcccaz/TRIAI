<<<<<<< HEAD
"""
Quick test script to verify API keys are configured correctly
Run this before starting the main app
"""
import os
from dotenv import load_dotenv

load_dotenv()

print("=" * 50)
print("TriAI Compare - API Key Configuration Check")
print("=" * 50)

# Check OpenAI
openai_key = os.getenv('OPENAI_API_KEY', '')
if openai_key and openai_key != 'your-openai-key-here':
    print("✓ OpenAI API Key: Configured")
else:
    print("✗ OpenAI API Key: NOT configured")

# Check Anthropic
anthropic_key = os.getenv('ANTHROPIC_API_KEY', '')
if anthropic_key and anthropic_key != 'your-anthropic-key-here':
    print("✓ Anthropic API Key: Configured")
else:
    print("✗ Anthropic API Key: NOT configured")

# Check Google
google_key = os.getenv('GOOGLE_API_KEY', '')
if google_key and google_key != 'your-google-key-here':
    print("✓ Google API Key: Configured")
else:
    print("✗ Google API Key: NOT configured")

print("=" * 50)
print("\nIf any keys are missing:")
print("1. Copy .env.example to .env")
print("2. Fill in your actual API keys")
print("3. Run this test again")
print("\nOnce all keys are configured, run: python app.py")
=======
"""
Quick test script to verify API keys are configured correctly
Run this before starting the main app
"""
import os
from dotenv import load_dotenv

load_dotenv()

print("=" * 50)
print("TriAI Compare - API Key Configuration Check")
print("=" * 50)

# Check OpenAI
openai_key = os.getenv('OPENAI_API_KEY', '')
if openai_key and openai_key != 'your-openai-key-here':
    print("✓ OpenAI API Key: Configured")
else:
    print("✗ OpenAI API Key: NOT configured")

# Check Anthropic
anthropic_key = os.getenv('ANTHROPIC_API_KEY', '')
if anthropic_key and anthropic_key != 'your-anthropic-key-here':
    print("✓ Anthropic API Key: Configured")
else:
    print("✗ Anthropic API Key: NOT configured")

# Check Google
google_key = os.getenv('GOOGLE_API_KEY', '')
if google_key and google_key != 'your-google-key-here':
    print("✓ Google API Key: Configured")
else:
    print("✗ Google API Key: NOT configured")

print("=" * 50)
print("\nIf any keys are missing:")
print("1. Copy .env.example to .env")
print("2. Fill in your actual API keys")
print("3. Run this test again")
print("\nOnce all keys are configured, run: python app.py")
>>>>>>> 6added3 (Initial commit: TriApp multi-AI comparison tool with GPT-5.2, Claude 4.5 Sonnet, Gemini 3.0, and Perplexity Pro support)
