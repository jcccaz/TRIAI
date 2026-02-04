import os
import requests
import uuid
import base64
from pathlib import Path
from flask import Blueprint, request, jsonify
from openai import OpenAI
from google import genai
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
        result = fabricate_and_persist_visual(raw_concept, model_role, profile)
        if result:
            return jsonify({
                "status": "success",
                "type": "image",
                "image_url": result
            })
            
    return jsonify({"status": "error", "message": "Fabrication failed"}), 500

def generate_mermaid_viz(concept, profile='data-viz'):
    """Generates Mermaid.js syntax for charts/graphs using Gemini."""
    import logging
    logger = logging.getLogger(__name__)
    
    gen = get_google_genai()
    if not gen: 
        logger.error("Google GenAI not configured.")
        return None
    
    # Truncate concept to avoid context bloat if it's too long
    concept_digest = concept[:4000] if len(concept) > 4000 else concept
    
    instruction = f"""
    You are THE DATA ARCHITECT. Your mission is to extract numerical or relational data from the provided CONCEPT and convert it into high-fidelity Mermaid.js syntax.
    
    PROFILE: {profile}
    - If 'data-viz': Use 'pie', 'lineChart', or 'barChart' (Mermaid v10+ syntax). Focus on numerical comparisons.
    - If 'knowledge-graph': Use 'graph TD' or 'flowchart LR'. Focus on logical dependencies and structural flows.
    
    CONCEPT: "{concept_digest}"
    
    STRICT RULES:
    1. Return ONLY the raw Mermaid syntax. NO markdown code blocks, NO "mermaid" prefix.
    2. Zero external text. Only syntax.
    3. Ensure labels are concise and technical.
    4. If no clear data exists to visualize, return "NULL".
    5. If 'data-viz', ensure the chart title reflects the core numerical comparison.
    """
    
    try:
        client = gen
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=instruction
        )
        clean_syntax = response.text.replace('```mermaid', '').replace('```', '').strip()
        
        if clean_syntax.upper() == "NULL" or len(clean_syntax) < 10:
            logger.warning(f"Mermaid generation for {profile} returned NULL or insufficient data.")
            return None
            
        logger.info(f"Successfully generated Mermaid syntax for {profile} ({len(clean_syntax)} chars).")
        return clean_syntax
    except Exception as e:
        logger.error(f"Mermaid generation error: {e}")
        return None

def fabricate_and_persist_visual(concept, role='general', profile='realistic'):
    """High-fidelity visual generation using Google Nano Banana (Imagen 3)."""
    import logging
    logger = logging.getLogger(__name__)
    
    # 1. THE FABRICATOR: Refine the prompt (Using GPT for high-quality prompt engineering)
    style = get_style_for_role(role, profile)
    fabricator_instruction = f"""
    You are THE FABRICATOR. Write a high-fidelity image generation prompt for Imagen 3 (Nano Banana).
    
    INPUT CONCEPT: "{concept}"
    PROFILE: {profile}
    
    CORE MANDATE: 100% TECHNICAL ACCURACY.
    - The image must be a literal translation of the technical data provided.
    ...
    
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

        # 2. THE ENGINE: Google Nano Banana (Imagen 3)
        logger.info(f"Executing fabrication with prompt: {final_prompt[:100]}...")
        
        response = openai_client.images.generate(
            model="dall-e-3",
            prompt=final_prompt,
            size="1024x1024",
            quality="hd",
            n=1
        )
        external_url = response.data[0].url
        
        # 3. PERSISTENCE
        save_dir = Path("static/img/fabricated")
        save_dir.mkdir(parents=True, exist_ok=True)
        filename = f"nano_{uuid.uuid4().hex[:12]}.png"
        local_path = save_dir / filename
        
        img_data = requests.get(external_url).content
        local_path.write_bytes(img_data)
        
        logger.info(f"Successfully fabricated and persisted image: {filename}")
        return f"/static/img/fabricated/{filename}"

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
