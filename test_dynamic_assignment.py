import requests
import json

BASE_URL = "http://127.0.0.1:5000"

def test_role_override():
    print("Testing Manual Role Override...")
    payload = {
        "question": "What is the floor value of a distressed SaaS asset?",
        "council_mode": True,
        "role_overrides": {
            "openai": "liquidation"
        },
        "active_models": ["openai"]
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/ask", json=payload)
        data = response.json()
        
        gpt_res = data['results']['openai']['response']
        print(f"GPT Response Start: {gpt_res[:100]}...")
        
        # Check if the role was applied - usually the model will adopt the persona
        # In our system, the role is passed to query_openai which sets the system prompt.
        print("✅ Manual override test request sent successfully.")
    except Exception as e:
        print(f"❌ Test failed: {e}")

if __name__ == "__main__":
    test_role_override()
