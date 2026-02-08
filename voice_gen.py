import os
import requests
import uuid
from pathlib import Path

# Load env variables if not already loaded (app.py does it, but good for standalone testing)
from dotenv import load_dotenv
load_dotenv()

ELEVENLABS_API_KEY = os.getenv('ELEVENLABS_API_KEY')
ELEVENLABS_VOICE_ID = os.getenv('ELEVENLABS_VOICE_ID', '21m00Tcm4TlvDq8ikWAM') # Default to Rachel if missing

CHUNK_SIZE = 1024
SOUNDS_DIR = Path('static/sounds')

def ensure_sounds_dir():
    SOUNDS_DIR.mkdir(parents=True, exist_ok=True)

def generate_voice_alert(text, filename=None):
    """
    Generates speech from text using ElevenLabs API.
    Saves to static/sounds/[filename].mp3
    Returns the web-accessible path or None on error.
    """
    if not ELEVENLABS_API_KEY:
        print("❌ ElevenLabs API Key missing.")
        return None

    ensure_sounds_dir()
    
    if not filename:
        filename = f"alert_{uuid.uuid4().hex[:8]}.mp3"
        
    full_path = SOUNDS_DIR / filename
    
    # Check if static file already exists (cache)
    # Only cache specific filenames (like 'welcome.mp3'), not random UUIDs
    if filename and not filename.startswith('alert_') and full_path.exists():
        return f"/static/sounds/{filename}"

    url = f"https://api.elevenlabs.io/v1/text-to-speech/{ELEVENLABS_VOICE_ID}"
    
    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": ELEVENLABS_API_KEY
    }
    
    data = {
        "text": text,
        "model_id": "eleven_monolingual_v1",
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.75
        }
    }
    
    try:
        response = requests.post(url, json=data, headers=headers)
        
        if response.status_code != 200:
            print(f"ElevenLabs Error ({response.status_code}): {response.text}")
            return None
            
        with open(full_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
                if chunk:
                    f.write(chunk)
                    
        print(f"🔊 Generated voice alert: {filename}")
        return f"/static/sounds/{filename}"
        
    except Exception as e:
        print(f"Voice Gen Exception: {e}")
        return None
