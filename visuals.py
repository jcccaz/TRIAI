import os
import requests
import uuid
import base64
from pathlib import Path
from flask import Blueprint, request, jsonify
from openai import OpenAI
from google import genai
from google.genai import types
from dotenv import load_dotenv

# Re-load for standalone resilience
load_dotenv()

# Client lazy-loaders
def get_openai_client():
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("WARNING: OPENAI_API_KEY not found in environment.")
    return OpenAI(api_key=api_key) if api_key else None

def get_google_genai():
    api_key = os.getenv("GOOGLE_API_KEY")
    if api_key:
        return genai.Client(api_key=api_key)
    return None

visuals_bp = Blueprint('visuals', __name__)

@visuals_bp.route('/api/generate-visual', methods=['POST'])
def generate_visual_route():
    data = request.json
    raw_concept = data.get('concept')
    model_role = data.get('role', 'general')
    profile = data.get('profile', 'realistic')
    
    if profile in ['data-viz', 'knowledge-graph']:
        result = generate_mermaid_viz(raw_concept, profile)
        if result:
            return jsonify({
                "status": "success",
                "type": "mermaid",
                "syntax": result
            })
        else:
            return jsonify({"status": "error", "message": "Failed to generate chart data"}), 400
    else:
        # Fallback to image generation
        result = fabricate_and_persist_visual(raw_concept, model_role, profile)
        if result:
            return jsonify({
                "status": "success",
                "type": "image",
                "image_url": result
            })
            
    return jsonify({"status": "error", "message": "Fabrication failed"}), 500

def generate_mermaid_viz(concept, profile='data-viz'):
    """Generates precise Mermaid.js XYChart code using Gemini."""
    import logging
    logger = logging.getLogger(__name__)
    
    # Switch to 'xychart-beta' which is cleaner for data than 'graph TD'
    prompt = f"""
    You are a Data Visualization Engine. Your job is to convert the user's data into valid Mermaid.js 'xychart-beta' syntax.
    
    INPUT DATA:
    {concept[:3000]}
    
    INSTRUCTIONS:
    1. Extract the main numerical series (e.g., Revenue over Time).
    2. Use 'xychart-beta' which supports bar and line charts.
    3. If multiple series exist (e.g., Revenue vs Cost), plot both if possible or prioritize Revenue.
    4. X-Axis should be time (Months/Years) or Categories.
    5. Y-Axis must be numerical.
    
    STRICT SYNTAX RULES:
    - START with `xychart-beta`
    - Define title: `title "Financial Projection"`
    - Define x-axis: `x-axis [ "Jan", "Feb", ... ]` (Arrays must be strings)
    - Define y-axis: `y-axis "Revenue ($)" 0 --> 15000` (Set range automatically based on data)
    - Define data: `bar [100, 200, ...]` or `line [100, 200, ...]` based on context.
    - DO NOT use special characters like '$' or ',' inside the data arrays. Keep them as raw numbers.
    - DO NOT add markdown ticks (```). Return ONLY the code.
    
    EXAMPLE OUTPUT:
    xychart-beta
        title "Quarterly Revenue"
        x-axis ["Q1", "Q2", "Q3", "Q4"]
        y-axis "Revenue (k)" 0 --> 100
        bar [50, 60, 85, 95]
        line [40, 50, 60, 70]
        
    GENERATE NOW:
    """
    
    try:
        google_client = get_google_genai()
        if not google_client:
            logger.error("Google Client missing for Mermaid gen.")
            return None
            
        model = google_client.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt)
        
        raw_text = response.text.replace('```mermaid', '').replace('```', '').strip()
        
        # Validation: content must start with xychart-beta or graph
        if not raw_text.startswith('xychart-beta') and not raw_text.startswith('graph'):
             logger.warning(f"Invalid Mermaid returned: {raw_text[:50]}...")
             # Fallback to simple graph if xychart fails? No, return error to avoid bombs
             return None
             
        logger.info(f"Generated strict Mermaid syntax ({len(raw_text)} chars).")
        return raw_text

    except Exception as e:
        logger.error(f"Mermaid generation error: {e}")
        return None

def fabricate_and_persist_visual(concept, role='general', profile='realistic'):
    """High-fidelity visual generation prioritizing DALL-E 3 (Stable)."""
    import logging
    logger = logging.getLogger(__name__)
    
    style = get_style_for_role(role, profile)
    fabricator_instruction = f"""
    You are THE FABRICATOR. Write a high-fidelity image generation prompt for DALL-E 3.
    
    INPUT CONCEPT: "{concept}"
    PROFILE: {profile}
    STYLE GUIDE: {style}
    
    CORE MANDATE: Visual impact and thematic consistency.
    OUTPUT: Return ONLY the raw prompt.
    """

    try:
        openai_client = get_openai_client()
        if not openai_client: 
            logger.error("OpenAI client not configured for fabrication.")
            return None
        
        logger.info(f"Refining prompt for {role} using profile {profile}...")
        refined_response = openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "system", "content": fabricator_instruction}]
        )
        final_prompt = refined_response.choices[0].message.content

        # 1. THE ENGINE: DALL-E 3 (Primary)
        try:
             logger.info(f"Executing fabrication with DALL-E 3...")
             
             response = openai_client.images.generate(
                model="dall-e-3",
                prompt=final_prompt[:4000],
                size="1024x1024",
                quality="standard",
                n=1,
             )
             
             image_url = response.data[0].url
             
             # Download and save locally to match persistence pattern
             img_data = requests.get(image_url).content
             save_dir = Path("static/img/fabricated")
             save_dir.mkdir(parents=True, exist_ok=True)
             filename = f"dalle_{uuid.uuid4().hex[:12]}.png"
             local_path = save_dir / filename
             local_path.write_bytes(img_data)
             
             logger.info(f"DALL-E 3 Fabrication SUCCESS: {filename}")
             return f"/static/img/fabricated/{filename}"
             
        except Exception as dalle_error:
            logger.error(f"DALL-E 3 failed: {dalle_error}")
            # Could fallback to Imagen here if fixed later
            return None

    except Exception as e:
        logger.error(f"Fabrication error: {e}")
        return None

def get_style_for_role(role, profile='realistic'):
    if profile == 'blueprint':
        return "White architectural blueprint, clean lines, technical schematic overlay, Da Vinci style engineering sketch, matte white background."
    
    styles = {
        "architect": "High-fidelity architectural render, clean industrial lines, minimal photography, 8k resolution.",
        "scout": "Satellite reconnaissance reconnaissance imagery, thermal overlay, military HUD interface aesthetic.",
        "liquidator": "Cinematic macro photography of a destroyed server room, high contrast corporate noir.",
        "researcher": "Technical documentation with forensic annotations, microfiche archive aesthetic.",
        "integrity": "Clean wireframe visualization, glowing nodal connections, technical audit dashboard.",
        "containment": "Industrial containment seals, hazardous environment photography, fog and concrete texture.",
        "deepagent": "LiDAR point-cloud visualization, predictive pathing lines, autonomous machine vision aesthetic.",
        "general": "High-fidelity professional photography, subject-aware environment, natural lighting."
    }
    return styles.get(role.lower(), styles["general"])
