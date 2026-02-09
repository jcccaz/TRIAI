import os
import requests
import uuid
import re
from pathlib import Path

# Load env variables
from dotenv import load_dotenv
load_dotenv()

CHUNK_SIZE = 1024
SOUNDS_DIR = Path('static/sounds')

def ensure_sounds_dir():
    SOUNDS_DIR.mkdir(parents=True, exist_ok=True)

def clean_text_for_speech(text):
    """
    Sanitize text for TTS: remove Markdown and artifacts while preserving natural pauses.
    """
    if not text:
        return ""
    
    # Remove Markdown headers (###, ##, #)
    text = re.sub(r'#+\s*', '', text)
    
    # Remove Bold/Italic stars and underscores
    text = re.sub(r'[\*_]+', '', text)
    
    # Replace list bullets with a period for a proper pause
    text = re.sub(r'^\s*[\-\*\+]\s+', '. ', text, flags=re.MULTILINE)
    
    # Remove blockquote markers
    text = re.sub(r'^\s*>\s+', ' ', text, flags=re.MULTILINE)
    
    # Remove symbols/emojis but PRESERVE basic punctuation (. , ! ? :)
    text = re.sub(r'[^\x00-\x7F\xc0-\xff]+', ' ', text)
    
    # Explicitly remove common artifacts
    text = text.replace('`', '')
    text = text.replace('checkmark', '')
    
    # Remove links [text](url) -> text
    text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)
    
    # Clean up structure - ensure every newline is treated as a sentence end
    text = text.replace('\n', '. ')
    
    # Ensure no triple-dots or weird spacing messes up the timing
    text = re.sub(r'\.\s*\.', '.', text)
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text

def generate_voice_alert(text, filename=None):
    """
    Generates speech from text using ElevenLabs API.
    """
    api_key = os.getenv('ELEVENLABS_API_KEY')
    voice_id = os.getenv('ELEVENLABS_VOICE_ID', '21m00Tcm4TlvDq8ikWAM')

    if not api_key:
        err = "❌ ElevenLabs API Key missing from .env"
        print(err)
        return None, err

    ensure_sounds_dir()
    
    # Sanitize text
    clean_text = clean_text_for_speech(text)
    
    if not filename:
        import hashlib
        text_hash = hashlib.md5(clean_text.encode()).hexdigest()[:10]
        filename = f"voice_{text_hash}.mp3"
        
    full_path = SOUNDS_DIR / filename
    
    # Caching
    if full_path.exists():
        return f"/static/sounds/{filename}", None

    print(f"📡 Generating Oracle Voice Control: '{clean_text[:40]}...'")

    # Use Multilingual v2 for significantly better quality and pacing
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    
    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": api_key
    }
    
    data = {
        "text": clean_text,
        "model_id": "eleven_multilingual_v2", # UPGRADED from monolingual v1
        "voice_settings": {
            "stability": 0.65,        
            "similarity_boost": 0.85,  # Slightly higher for clarity
            "style": 0.0,             # Keep it neutral but authoritative
            "use_speaker_boost": True 
        }
    }
    
    try:
        response = requests.post(url, json=data, headers=headers)
        
        if response.status_code != 200:
            import datetime
            error_msg = f"[{datetime.datetime.now()}] ElevenLabs Error ({response.status_code}) on model {data['model_id']}: {response.text}"
            print(error_msg)
            with open("voice_errors.txt", "a") as log:
                log.write(f"{error_msg}\n")
            
            # If v2 fails (rare), try falling back to v1
            print("Trying fallback to v1 model...")
            data["model_id"] = "eleven_monolingual_v1"
            response = requests.post(url, json=data, headers=headers)
            
            if response.status_code != 200:
                with open("voice_errors.txt", "a") as log:
                    log.write(f"Fallback Failed ({response.status_code}): {response.text}\n")
                return None, f"ElevenLabs API Error: {response.status_code}"
            
        with open(full_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
                if chunk:
                    f.write(chunk)
                    
        print(f"🔊 Generated voice alert saved: {filename}")
        return f"/static/sounds/{filename}", None
        
    except Exception as e:
        err_msg = f"Voice Gen Exception: {e}"
        print(err_msg)
        return None, err_msg
