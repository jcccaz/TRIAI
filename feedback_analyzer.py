from google import genai
import os
import json
from typing import List, Dict

# Reuse the key from environment
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
client = genai.Client(api_key=GOOGLE_API_KEY)

def analyze_feedback_text(feedback_text: str, rating: int) -> Dict[str, any]:
    """
    Uses Gemini Flash to analyze free-text feedback and extract structured signals.
    Returns: { "tags": ["TAG_1", "TAG_2"], "sentiment": "positive"|"negative"|"mixed" }
    """
    if not feedback_text or len(feedback_text.strip()) < 5:
        return {"tags": [], "sentiment": "neutral"}

    prompt = f"""
    Analyze the following user feedback for an AI system. The user gave a rating of {rating}/4.
    
    Feedback: "{feedback_text}"
    
    Your task is to classify this feedback into structured tags for a recommendation system.
    
    Valid Tags:
    - POSITIVE_LOGIC: User praised the reasoning/logic.
    - NEGATIVE_LOGIC: User found the logic flawed.
    - POSITIVE_ACCURACY: User verified the facts as correct.
    - NEGATIVE_ACCURACY: User found factual errors or hallucinations.
    - POSITIVE_STYLE: User liked the tone/format.
    - NEGATIVE_STYLE: User disliked the tone/format (e.g. too generic, too preachy).
    - HALLUCINATION: Specific mention of invented facts/numbers.
    - GOOD_DEPTH: User appreciated the detail.
    - TOO_SHALLOW: User found it superficial.
    
    Return ONLY a valid JSON object with this format:
    {{
        "tags": ["TAG1", "TAG2"],
        "sentiment": "positive" | "negative" | "mixed"
    }}
    """
    
    try:
        response = client.models.generate_content(
            model='gemini-2.0-flash', 
            contents=prompt,
            config={'response_mime_type': 'application/json'}
        )
        
        return json.loads(response.text)
    except Exception as e:
        print(f"Feedback Analysis Error: {e}")
        return {"tags": [], "sentiment": "neutral"}
