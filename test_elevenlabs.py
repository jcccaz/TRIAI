import os
import requests
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

api_key = os.getenv('ELEVENLABS_API_KEY')
voice_id = os.getenv('ELEVENLABS_VOICE_ID')

print(f"API Key: {api_key[:5]}...{api_key[-5:] if api_key else 'None'}")
print(f"Voice ID: {voice_id}")

url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
headers = {
    "Accept": "audio/mpeg",
    "Content-Type": "application/json",
    "xi-api-key": api_key
}
data = {
    "text": "System test. Cassandra is active.",
    "model_id": "eleven_monolingual_v1"
}

try:
    response = requests.post(url, json=data, headers=headers)
    print(f"Status Code: {response.status_code}")
    if response.status_code != 200:
        print(f"Error: {response.text}")
    else:
        print("Success!")
except Exception as e:
    print(f"Exception: {e}")
