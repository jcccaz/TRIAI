import os
import argparse
from dotenv import load_dotenv

# Load env from .env file to get API key
load_dotenv()

try:
    from google import genai
    from google.genai import types
except ImportError:
    print("Error: 'google-genai' SDK not installed. Run 'pip install google-genai'")
    exit(1)

def main():
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("ERROR: GOOGLE_API_KEY not found in environment.")
        return

    print(f"--- TESTING GEMINI CONNECTION (Key: ...{api_key[-4:]}) ---")
    
    try:
        client = genai.Client(api_key=api_key)
        
        # 1. LIST MODELS
        print("\n[1] Listing Available Models:")
        available_models = []
        for m in client.models.list():
            print(f" - {m.name}")
            available_models.append(m.name)
        
        # 2. TEST GENERATION (2.5 Flash - current stable)
        target_model = "gemini-2.5-flash"
        print(f"\n[2] Attempting Generation with '{target_model}'...")

        try:
            response = client.models.generate_content(
                model=target_model,
                contents="System Check. Reply with 'OK'."
            )
            print(f"SUCCESS: {response.text}")
        except Exception as e:
            print(f"FAILED on {target_model}: {e}")

            # 3. IF FAILED, TRY FALLBACK (2.0 Flash)
            fallback_model = "gemini-2.0-flash"
            print(f"\n[3] Attempting Fallback with '{fallback_model}'...")
            try:
                response = client.models.generate_content(
                    model=fallback_model,
                    contents="System Check (Fallback)."
                )
                print(f"FALLBACK SUCCESS: {response.text}")
            except Exception as e2:
                print(f"FALLBACK FAILED: {e2}")

    except Exception as e:
        print(f"\nFATAL CLIENT ERROR: {e}")

if __name__ == "__main__":
    main()
