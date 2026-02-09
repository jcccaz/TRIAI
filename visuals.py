#  VISUALIZATION PROTOCOL
#  ----------------------
#  1. IF task == "chart" OR "technical" OR "blueprint":
#     -> generate code/spec (JSON/Matplotlib)
#     -> validate data
#     -> render static chart
#     -> OR return ERROR (NO IMAGE FALLBACK ALLOWED)
#
#  2. IF task == "creative illustration" OR "realistic":
#     -> image model allowed (DALL-E 3)

import os
import requests
import uuid
import base64
import json
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


def sanitize_mermaid_code(code):
    """
    Regex-based sanitizer to fix common Mermaid syntax errors in node labels.
    - Finds content inside [...] and (...)
    - Removes nested parentheses, colons, and special chars from the label text.
    """
    import re
    
    def clean_label(match):
        open_b = match.group(1)
        content = match.group(2)
        close_b = match.group(3)
        # Aggressive cleaning inside the label
        clean_content = content.replace('(', '').replace(')', '').replace(':', ' - ').replace('$', '').replace('%', 'pct')
        return f"{open_b}{clean_content}{close_b}"

    # Regex for [Label] and (Label) 
    code = re.sub(r'(\[)(.*?)(\])', clean_label, code)
    return code

def generate_mermaid_viz(concept, profile='data-viz'):
    """Generates precise Mermaid.js XYChart code using Gemini."""
    import logging
    logger = logging.getLogger(__name__)
    
    # DYNAMIC PROMPT SELECTION
    if profile == 'knowledge-graph':
        prompt = f"""
        You are a Knowledge Architect. Convert the concept below into a generic Mermaid.js 'graph TD' (Flowchart).
        
        INPUT CONCEPT:
        {concept[:3000]}
        
        INSTRUCTIONS:
        1. Identify key entities and their relationships.
        2. Use `graph TD` direction.
        3. Use standard shapes: `[Box]`, `((Circle))`, `{{`, `}}`, `([Rounded])`.
        4. Keep labels short and punchy.
        5. DO NOT use special characters in node IDs.
        
        STRICT SYNTAX RULES:
        - START with `graph TD`
        - Example: `A[Client] -->|Request| B(Server)`
        - **CRITICAL:** Visual labels must NOT contain parentheses `()` inside the brackets `[]`.
        - BAD: `A[Value (Q1)]` -> GOOD: `A[Value Q1]`
        - BAD: `B[$100: Total]` -> GOOD: `B[100 USD Total]`
        - Node IDs (A, B, C) must be simple alphanumeric strings (e.g., `Node1`, `Node2`).
        - Return ONLY the code. No markdown ticks.
        
        GENERATE NOW:
        """
    else:
        # Default: Data-Viz (xychart-beta)
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
        STRICT SYNTAX RULES:
        - START with `xychart-beta`
        - Define title: `title "Financial Projection"`
        - Define x-axis: `x-axis [ "Jan", "Feb", ... ]` (Arrays must be strings)
        - Define y-axis: `y-axis "Revenue (USD)" 0 --> 15000` (Set range automatically based on data)
        - Define data: `bar [100, 200, ...]` or `line [100, 200, ...]` based on context.
        - **Data Arrays:** Must NOT contain '$', ',', or text. Use raw numbers: `[1000, 5000]`.
        - **X-Axis Labels:** Must NOT contain '$', '(', ')', '|', ':', or '%'. Keep them simple e.g. "Q1 2026".
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
            
        response = google_client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt
        )
        
        raw_text = response.text.replace('```mermaid', '').replace('```', '').strip()
        
        # Validation: content must start with xychart-beta or graph
        if not raw_text.startswith('xychart-beta') and not raw_text.startswith('graph'):
             logger.warning(f"Invalid Mermaid returned: {raw_text[:50]}...")
             return None
             
        # SANITIZATION STEP
        clean_text = sanitize_mermaid_code(raw_text)
        
        logger.info(f"Generated clean Mermaid syntax ({len(clean_text)} chars).")
        return clean_text

    except Exception as e:
        logger.error(f"Mermaid generation error: {e}")
        return None

def generate_matplotlib_chart(data_json, style='professional'):
    """Generates a static chart image using Matplotlib based on JSON data."""
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    import io
    import time
    import os
    
    # 1. Setup Style
    if style == 'blueprint':
        plt.style.use('dark_background')
        plt.rcParams.update({
            "lines.color": "white",
            "patch.edgecolor": "white",
            "text.color": "white",
            "axes.facecolor": "#001f3f",  # Navy Blue
            "axes.edgecolor": "white",
            "axes.labelcolor": "white",
            "xtick.color": "white",
            "ytick.color": "white",
            "grid.color": "white",
            "grid.alpha": 0.3,
            "figure.facecolor": "#001f3f", # Navy Blue
            "font.family": "monospace"
        })
    else:
        plt.style.use('bmh') # Clean professional style
        plt.rcParams.update({
            "font.family": "sans-serif",
            "figure.facecolor": "white",
            "axes.facecolor": "#f8f9fa"
        })

    # 2. Extract Data
    months = data_json.get('months', [])
    revenue = data_json.get('revenue', [])
    costs = data_json.get('costs', [])
    labels = data_json.get('labels', [])
    
    if not revenue and not costs:
        return None

    # 3. Plot
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Ensure lengths match
    min_len = min(len(months), len(revenue))
    x = months[:min_len]
    y1 = revenue[:min_len]
    
    # Plot Revenue (Green/White)
    color_rev = '#00ff41' if style == 'blueprint' else '#2ca02c'
    ax.plot(x, y1, marker='o', linestyle='-', linewidth=2, color=color_rev, label='Revenue')
    
    # Plot Costs (Red/Orange)
    if costs:
        min_len_c = min(len(months), len(costs))
        y2 = costs[:min_len_c]
        color_cost = '#ff4136' if style == 'blueprint' else '#d62728'
        ax.plot(x[:min_len_c], y2, marker='x', linestyle='--', linewidth=2, color=color_cost, label='Costs')
        
    # Labels & Title
    ax.set_title("Financial Projection", fontsize=14, fontweight='bold', pad=20)
    ax.set_xlabel("Time Period", fontsize=12)
    ax.set_ylabel("Value ($)", fontsize=12)
    ax.legend()
    ax.grid(True)
    
    # 4. Save
    os.makedirs('static/charts', exist_ok=True)
    chart_filename = f"chart_{style}_{int(time.time())}.png"
    chart_path = os.path.join('static', 'charts', chart_filename)
    plt.savefig(chart_path, dpi=150, bbox_inches='tight')
    plt.close()
    
    return f"/static/charts/{chart_filename}"


def clean_table_input(text):
    """
    Pre-processes text to make it easier for LLMs to extract numerical data.
    1. Removes Markdown table formatting lines (e.g. |---|---|)
    2. Removes common currency symbols ($, €, £)
    3. Removes thousands separators (,) to avoid confusion
    4. Replaces pipes (|) with spaces to declutter
    """
    cleaned_lines = []
    for line in text.split('\n'):
        # Skip markdown separator lines (e.g. |---| or +---+ or :---:)
        if set(line.strip()) <= {'|', '-', ' ', ':', '+'}:
            continue
        
        # Remove currency and formatting
        # We replace with empty string to turn "$10,000" into "10000"
        line = line.replace('$', '').replace('€', '').replace('£', '')
        line = line.replace(',', '') # aggressive comma removal for numbers
        line = line.replace('|', '    ') # Replace pipes with 4 spaces to maintain separation
        cleaned_lines.append(line)
        
    return "\n".join(cleaned_lines)

def fabricate_and_persist_visual(concept, role='general', profile='realistic'):
    """High-fidelity visual generation prioritizing Matplotlib over DALL-E."""
    import logging
    logger = logging.getLogger(__name__)

    # --- 1. MATPLOTLIB PATH (Accurate Data) ---
    if profile in ['data-viz', 'blueprint', 'chart']:
        # Step 0: Clean the Input (Council Recommendation)
        cleaned_concept = clean_table_input(concept[:4000])
        logger.info(f"Cleaned Input for Chart: {cleaned_concept[:100]}...")

        # Universal Data Extraction Prompt
        extraction_prompt = f"""
        You are a Data Extraction Analyst. Your job is to convert the raw text below into a clean JSON object for a Matplotlib chart.

        INPUT TEXT:
        {cleaned_concept}

        INSTRUCTIONS:
        1. Look for any data table, bulleted list, or numbers in the text.
        2. Extract time-series labels (Months, Quarters) into a "months" array.
        3. Extract the primary numerical values into a "revenue" array.
        4. Clean the numbers: Remove '$', ',', '%', 'USD'. Convert "10k" to 10000.
        
        REQUIRED JSON STRUCTURE:
        {{
            "months": ["Q1", "Q2", "Q3", "Q4"],
            "revenue": [150, 200, 180, 220],
            "costs": [100, 120, 110, 130],
            "title": "Quarterly Performance",
            "ylabel": "Revenue ($)"
        }}

        - If no valid numerical data can be found, return an empty JSON object {{}}.
        """
        try:
             # Use generic LLM to extract JSON
            openai_client = get_openai_client()
            if openai_client:
                json_resp = openai_client.chat.completions.create(
                    model="gpt-4o",
                    messages=[{"role": "user", "content": extraction_prompt}],
                    response_format={"type": "json_object"}
                )
                # Clean up markdown code blocks if present (common LLM failure mode)
                content = json_resp.choices[0].message.content
                if '```' in content:
                    content = content.replace('```json', '').replace('```', '').strip()
                
                logger.info(f"Matplotlib Extraction Raw: {content[:100]}...")
                
                try:
                    data_json = json.loads(content)
                except json.JSONDecodeError as je:
                    logger.error(f"JSON Decode Error in Matplotlib extraction: {je} | Content: {content}")
                    return None

                # Fallback Keys (If LLM disregards instructions)
                if 'revenue' not in data_json:
                    # UNIVERSAL KEY DETECTION: Scan ALL keys for a list of numbers
                    found_series = False
                    for key, val in data_json.items():
                        if isinstance(val, list) and len(val) > 0:
                            # Check if first element is number-ish
                            first_item = val[0]
                            if isinstance(first_item, (int, float)) or (isinstance(first_item, str) and first_item.replace('.','',1).isdigit()):
                                data_json['revenue'] = val
                                logger.info(f"Universal Detection Found Series in key: '{key}'")
                                found_series = True
                                break
                    
                    if not found_series:
                        logger.warning(f"Universal Detection Failed. Keys: {list(data_json.keys())}")

                # Fallback for X-Axis (If 'months'/labels missing)
                if 'months' not in data_json:
                    for key in ['labels', 'categories', 'names', 'x', 'time', 'period', 'quarter']:
                        if key in data_json:
                            data_json['months'] = data_json[key]
                            break
                            
                # Final Hail Mary: If we have data but no labels, make them up.
                if data_json.get('revenue') and not data_json.get('months'):
                    count = len(data_json['revenue'])
                    data_json['months'] = [f"Item {i+1}" for i in range(count)]

                # Check validity
                # Check validity
                if not data_json.get('revenue'):
                     logger.warning(f"LLM Extraction Failed. Attempting Regex Fallback on: {cleaned_concept[:100]}...")
                     
                     # REGEX FALLBACK: Find all numbers in the text
                     import re
                     # Match numbers like 10, 10.5, 1,000, $500 (cleaned input already removed $)
                     # We look for digits, optional commas, optional decimals
                     raw_nums = re.findall(r'[-+]?\d[\d,]*\.?\d+', cleaned_concept)
                     
                     clean_nums = []
                     for n in raw_nums:
                         try:
                             # Remove commas and convert
                             val = float(n.replace(',', ''))
                             clean_nums.append(val)
                         except ValueError:
                             continue
                             
                     if len(clean_nums) >= 2:
                         logger.info(f"Regex Fallback SUCCESS. Found {len(clean_nums)} numbers: {clean_nums[:5]}...")
                         data_json['revenue'] = clean_nums
                         data_json['months'] = [f"Pt {i+1}" for i in range(len(clean_nums))]
                         data_json['title'] = "Auto-Extracted Data"
                     else:
                         logger.warning(f"FINAL FAIL: No valid data series found even with regex. Raw JSON: {json.dumps(data_json)}")
                         return "Error: Could not extract any numbers (LLM & Regex failed)." # Return error string

                # Normalize data for the plotter
                if 'months' not in data_json and 'labels' in data_json:
                    # Create dummy numeric x-axis if missing
                    data_json['months'] = list(range(len(data_json['labels'])))
                elif 'labels' not in data_json and 'months' in data_json:
                    # Create string labels from months if needed
                    data_json['labels'] = [str(m) for m in data_json['months']]

                # Generate Chart
                style = 'blueprint' if profile == 'blueprint' else 'professional'
                chart_url = generate_matplotlib_chart(data_json, style=style)
                if chart_url:
                    return chart_url
                else:
                    return "Error: Matplotlib chart generation returned None."
        except Exception as e:
            logger.error(f"Matplotlib generation failed: {e}")
            import traceback
            traceback.print_exc()
            return f"Error: Exception in extraction pipeline: {str(e)}"
    
    # --- 2. DALL-E 3 PATH (Art Only) ---
    # Only proceed to DALL-E if the profile is explicitly 'realistic' or 'art'
    if profile in ['data-viz', 'blueprint', 'chart']:
        return None
    # ... (Existing DALL-E Logic) ...
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

        # Execute DALL-E 3
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
             
             # Download and save locally
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
