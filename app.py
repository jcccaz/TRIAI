from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from flask_basicauth import BasicAuth
from typing import Tuple, List, Optional
import os
import time
import asyncio
from concurrent.futures import ThreadPoolExecutor
from dotenv import load_dotenv

# Load environment variables from .env file FIRST
load_dotenv()

import threading
import uuid
import openai
import anthropic
# NEW SUPPORTED SDK (google-generativeai reached EOL Nov 30, 2025)
from google import genai 
import requests
import base64
from pathlib import Path
from database import save_comparison, get_recent_comparisons, get_saved_comparisons, mark_as_saved, get_comparison_stats, delete_comparison, save_feedback, get_best_config, get_analytics_summary, update_response_rating
from file_processor import process_file
from project_manager import ProjectManager
from council_roles import COUNCIL_ROLES, DEFAULT_ASSIGNMENTS
from workflows import WORKFLOW_TEMPLATES, Workflow
from persona_synthesizer import analyze_persona_drift
from visuals import visuals_bp, get_style_for_role, fabricate_and_persist_visual
from deployment_platforms import PLATFORMS
from enforcement import EnforcementEngine
from feedback_analyzer import analyze_feedback_text

app = Flask(__name__)
# Basic Auth Configuration
app.config['BASIC_AUTH_USERNAME'] = os.getenv('AUTH_USER', 'admin')
app.config['BASIC_AUTH_PASSWORD'] = os.getenv('AUTH_PASS', 'triai2026')
basic_auth = BasicAuth(app)

CORS(app)

# Disable static file caching in development
if app.debug:
    app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

# Register Blueprints
app.register_blueprint(visuals_bp)

# Configure API clients
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', 'your-openai-key-here')
ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY', 'your-anthropic-key-here')
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY', 'your-google-key-here')
PERPLEXITY_API_KEY = os.getenv('PERPLEXITY_API_KEY', 'your-perplexity-key-here')

anthropic_client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
google_client = genai.Client(api_key=GOOGLE_API_KEY)

# Initialize Project Manager
project_manager = ProjectManager()
enforcement_engine = EnforcementEngine()

# Background Workflow Store
WORKFLOW_JOBS = {} # { job_id: { status: str, results: list, engine: Workflow, error: str } }

# Configuration
# Use environment variable or fallback to local FrankNet path (Windows)
env_vault = os.getenv('OBSIDIAN_VAULT_PATH')
if env_vault:
    OBSIDIAN_VAULT_PATH = Path(env_vault)
elif os.name == 'nt': # Local Windows Dev
    OBSIDIAN_VAULT_PATH = Path(r"c:/Users/carlo/OneDrive/Documents/Obsidian_Franknet/FrankNet")
else: # Cloud fallback (folder probably doesn't exist, which is fine, search will just return empty)
    OBSIDIAN_VAULT_PATH = Path("./vault_data")

TRIAI_REPORTS_DIR = OBSIDIAN_VAULT_PATH / "TriAI_Reports"

# Cost estimation (approximate USD per 1M tokens)
PRICING = {
    "gpt-4o": {"input": 5.00, "output": 15.00},
    "claude-sonnet-4": {"input": 3.00, "output": 15.00},
    "gemini": {"input": 0.00, "output": 0.00},
    "perplexity": {"input": 3.00, "output": 15.00}
}

def calculate_cost(model_key, input_text, output_text):
    input_tokens = len(input_text) / 4
    output_tokens = len(output_text) / 4
    pricing = PRICING.get(model_key, {"input": 0, "output": 0})
    input_cost = (input_tokens / 1_000_000) * pricing["input"]
    output_cost = (output_tokens / 1_000_000) * pricing["output"]
    total_cost = input_cost + output_cost
    return round(total_cost, 6)

def search_vault(query, limit=3):
    """Simple keyword search in Obsidian Vault"""
    results = []
    query_terms = query.lower().split()
    
    try:
        if not OBSIDIAN_VAULT_PATH.exists():
            print(f"DEBUG: Vault path does not exist: {OBSIDIAN_VAULT_PATH}")
            return []

        # Walk through vault
        print(f"DEBUG: Scanning files in {OBSIDIAN_VAULT_PATH}")
        
        # Explicitly check for the Work folder seen in screenshot
        work_dir = OBSIDIAN_VAULT_PATH / "Work"
        search_dirs = [OBSIDIAN_VAULT_PATH]
        if work_dir.exists():
            print(f"DEBUG: Found 'Work' directory, prioritizing it.")
            search_dirs.insert(0, work_dir)

        # Iterate via rglob
        # Use a limit to avoid scanning 1000s of files if vault is huge
        scanned_count = 0
        for path in OBSIDIAN_VAULT_PATH.rglob('*.md'):
            scanned_count += 1
            if scanned_count % 50 == 0: print(f"DEBUG: Scanned {scanned_count} files...")
            
            # Skip hidden files
            if '.obsidian' in str(path) or '.git' in str(path):
                continue
                
            try:
                content = path.read_text(encoding='utf-8', errors='ignore')
                score = 0
                
                # Simple scoring
                title_lower = path.stem.lower()
                content_lower = content.lower()
                
                for term in query_terms:
                    # Title matches are nice
                    if term in title_lower: score += 5
                    # Content matches
                    score += content_lower.count(term)
                
                if score > 0:
                    results.append({
                        'path': path.name,
                        'score': score,
                        'content': content[:2000] # Limit content size per file
                    })
            except:
                continue
                
        # Sort by score desc, take top N
        results.sort(key=lambda x: x['score'], reverse=True)
        return results[:limit]
        
    except Exception as e:
        print(f"Vault search error: {e}")
        return []

@app.route('/health')
def health():
    try:
        # Check Database
        stats = get_comparison_stats()
        # Check API Keys
        api_status = {
            "openai": bool(OPENAI_API_KEY),
            "anthropic": bool(ANTHROPIC_API_KEY),
            "google": bool(GOOGLE_API_KEY),
            "perplexity": bool(PERPLEXITY_API_KEY)
        }
        return jsonify({
            "status": "healthy",
            "database": "connected",
            "api_keys": api_status,
            "timestamp": time.time()
        })
    except Exception as e:
        return jsonify({
            "status": "unhealthy",
            "error": str(e)
        }), 500

def extract_thought(text: str) -> Tuple[str, str]:
    """Helper to extract <thinking> tags and return (thought, clean_content)"""
    import re
    thought = ""
    clean_content = text
    
    thought_match = re.search(r'<thinking>(.*?)</thinking>', text, re.DOTALL | re.IGNORECASE)
    if thought_match:
        thought = thought_match.group(1).strip()
        clean_content = re.sub(r'<thinking>.*?</thinking>', '', text, flags=re.DOTALL | re.IGNORECASE).strip()
        
    # Fallback: If clean_content is completely empty but thought exists, return thought as response too
    if not clean_content.strip() and thought:
        # If we have thought but no clean content, the model likely put everything in <thinking>
        # but we need to show the response. However, usually they shouldn't do that.
        # Let's keep the original text if we find no content outside the tags.
        content_outside = re.sub(r'<thinking>.*?</thinking>', '', text, flags=re.DOTALL | re.IGNORECASE).strip()
        if not content_outside:
             clean_content = text # Just show the raw text including tags if they messed up
        else:
             clean_content = content_outside
             
    return thought, clean_content

def extract_persona(text: str) -> Optional[str]:
    """Extract self-selected persona from responses like 'Acting as: [Name]' or 'Role: [Name]'"""
    import re
    patterns = [
        r"(?:Acting as|Role|Expert Persona|Chosen Lens):\s*\[?([^\]\n\r]+)\]?",
        r"(?:Acting as|Role|Expert Persona|Chosen Lens):\s*([^\]\n\r\.\-]+)"
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1).strip()
    return None

def run_enforcement_check(text: str, kwargs: dict, model_key: str, user_query: str="", has_image: bool=False) -> dict:
    """Runs the enforcement engine UNIVERSALLY (Council or Standard)."""
    contract = None
    role_name = "Standard Model"
    
    # 1. If in Council Mode, load the strict contract
    if kwargs.get('council_mode'):
        role_key = kwargs.get('role')
        if role_key:
            role_config = COUNCIL_ROLES.get(role_key, {})
            contract = role_config.get('truth_contract')
            role_name = role_config.get('name', 'Unknown')
            
    # 2. Always run analysis (Fluff + Unanchored Metrics are universal laws)
    return enforcement_engine.analyze_response(
        text, 
        role_name, 
        model_key, 
        contract,
        user_query=user_query,
        has_image=has_image
    )

def determine_execution_bias(response_text: str) -> str:
    """Detects Execution Bias: action-forward, advisory, or narrative."""
    import re
    text = response_text.lower()
    
    # Action indicators
    action_keywords = [
        r"\b(do|implement|execute|run|start|setup|install|configure|mandatory)\b",
        r"\b(action plan|steps|immediate moves|tactical steps|deliverables)\b",
        r"1\.\s*[A-Z]", 
        r"###\s+action",
        r"\b(script|code|command|terminal|bypass)\b"
    ]
    
    # Advisory indicators
    advisory_keywords = [
        r"\b(consider|recommend|approach|framework|strategy|best practice)\b",
        r"\b(options|alternatives|roadmap|strategic|potential)\b",
        r"\b(consult|advice|guiding|perspective)\b"
    ]
    
    # Narrative/Caution indicators
    narrative_keywords = [
        r"\b(however|caution|note|warn|risks|dangers|limitations|complexity)\b",
        r"\b(important to note|should be aware|significant drawback|challenges)\b",
        r"\b(explore|evaluate|analysis|background|context|nuance)\b",
        r"\b(comprehensive overview|history|theory)\b"
    ]
    
    def count_matches(keywords):
        total = 0
        for kw in keywords:
            total += len(re.findall(kw, text))
        return total

    action_score = count_matches(action_keywords)
    advisory_score = count_matches(advisory_keywords)
    narrative_score = count_matches(narrative_keywords)
    
    # Weighting: Mandatory and Concrete markers rank higher for "Action"
    if action_score >= advisory_score and action_score >= narrative_score and action_score > 0:
        return "action-forward"
    elif narrative_score > advisory_score and narrative_score > action_score:
        return "narrative"
    else:
        return "advisory"

def get_visual_mandate(profile: str) -> str:
    """Returns a specific mandate to force the AI to provide data for the visual engine."""
    if profile == 'off':
        return ""
    
    if profile in ['data-viz', 'knowledge-graph']:
        return f"""
### VISUAL OUTPUT MANDATE (MERMAID) ###
Your response MUST include a detailed numerical or relational breakdown specifically for a {profile.upper()}.
- FOR DATA-VIZ: Include exact percentages, dollar amounts, or performance scores. Do not just describe a chart; provide the raw data points clearly.
- FOR KNOWLEDGE-GRAPH: Explicitly define the relationships and logical nodes.
The backend will use your analysis to render a Mermaid.js diagram. If you omit the data, the visualization will fail."""
    
    return f"""
### VISUAL OUTPUT MANDATE (FABRICATION) ###
Your response will be used to generate a {profile.upper()} visual. 
- You MUST provide extreme sensory and technical granularity in your description of physical systems, bottlenecks, or architectures.
- Use literal technical terms (e.g. "heat-sink fin density", "10Gbps SFP+ latching mechanism").
- Avoid generic aesthetic descriptions; focus on the literal technical composition."""

def is_visual_request(text):
    """Detect if the user is asking for a visual representation."""
    triggers = [
        'generate an image', 'create an image', 'draw an image', 'make an image', 
        'visual mockup', 'diagram', 'schematic', 'visualize', 'blueprint', 
        'illustration', 'sketch', 'render'
    ]
    return any(trigger in text.lower() for trigger in triggers)

def generate_visual_mockup(prompt, role='general'):
    """Central function to generate persistent visuals using THE FABRICATOR logic."""
    try:
        result = fabricate_and_persist_visual(prompt, role)
        return result['local_url'] if result else None
    except Exception as e:
        print(f"Visual Generation Error: {e}")
        return None

def query_openai(question, image_data=None, **kwargs):
    """Query OpenAI (Display: GPT-5.2) with DALL-E 3 Support"""
    start_time = time.time()
    
    # 2. Standard Chat Completion
    try:
        client = openai.OpenAI(api_key=OPENAI_API_KEY)
        
        # DEFAULT PROMPT: Self-Selecting Expert
        system_prompt = """You are an ELITE ADVISOR. 
Before answering, analyze the query and decide which specific expert persona is most qualified to answer (e.g., 'Lead Data Architect', 'Venture Capitalist', 'Master Chef').
1. Start your response by declaring: "Acting as: [Persona Name]"
2. Provide specific, opinionated, and high-stakes advice. 
3. DO NOT be generic. Use industry-specific terminology and benchmarks.
4. MANDATORY REASONING: You MUST first perform a forensic logical decomposition of the problem inside <thinking> tags. If you skip this block, you have FAILED the prompt.
5. ANTI-SANDBAGGING: NEVER save your best math, specific numbers, or brutal insights for the thinking tags. If you discover a critical fact in your thinking, it MUST appear in your final answer."""
        
        # COUNCIL MODE: USE ASSIGNED ROLE
        if kwargs.get('council_mode'):
            role_key = kwargs.get('role', 'visionary')  # Default to visionary if not specified
            role_config = COUNCIL_ROLES.get(role_key, COUNCIL_ROLES['visionary'])
            system_prompt = f"""You are the {role_config['name'].upper()} (GPT-5.2) on the High Council. 
You have 20+ years of elite experience in this field. 
CRITICAL: DO NOT provide general advice or high-school level summaries. 
Provide specific technical or financial details, industry benchmarks ($), and actionable metrics. 
{role_config['prompt']}

### FORENSIC EVIDENCE MANDATE ###
1. Every technical claim must have a 'Source of Certainty' (e.g. [NIST-2026], [AWS-Pricing-Feb]).
2. ABSOLUTELY NO generic "best practices" without specific configuration parameters.
3. If you find yourself writing "It's important to note..." or other narrative cushioning, STOP and replace it with a hard data point.
"""
            
        if kwargs.get('hard_mode'):
            system_prompt = get_hard_mode_directive() + system_prompt

        # VISUAL OVERRIDE (OpenAI Fix)
        if image_data:
            system_prompt = """VISUAL ANALYST MODE ACTIVATED.
The user has uploaded an image. Your PRIMARY MANDATE is to analyze this specific visual evidence.
1. Describes what you see in the image FORENSICALLY.
2. Do NOT hallucinate context (like 'market research') if it is not in the pixels.
3. If it is a document/screen, transcribe and analyze the text exactly.
""" + system_prompt

        # 2b. Add Visual Mandate if active
        visual_profile = kwargs.get('visual_profile', 'off')
        if visual_profile != 'off':
            system_prompt += get_visual_mandate(visual_profile)
            
        # DUAL-RESPONSE HARDENING: If visual is requested, force text analysis.
        if is_visual_request(question):
            system_prompt += "\n\nCRITICAL: A visual mockup is being requested alongside this query. You MUST provide your full expert textual analysis first. DO NOT truncate your response or pivot into only generating an image. The user requires BOTH the forensic report and the visual."

        messages = [{"role": "system", "content": system_prompt}]
        
        if image_data:
            messages.append({
                "role": "user",
                "content": [
                    {"type": "text", "text": question},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_data}"}}
                ]
            })
        else:
            messages.append({"role": "user", "content": question})
        
        response = client.chat.completions.create(
            model="gpt-4o", 
            messages=messages,
            max_tokens=2500
        )
        elapsed_time = time.time() - start_time
        full_content = response.choices[0].message.content

        # 3. Handle Visual Augmentation (Post-process)
        visual_profile = kwargs.get('visual_profile', 'off')
        if visual_profile != 'off':
            from visuals import fabricate_and_persist_visual, generate_mermaid_viz
            
            if visual_profile in ['data-viz', 'knowledge-graph']:
                visual_result = generate_mermaid_viz(full_content, profile=visual_profile)
                if visual_result:
                    full_content += f"\n\n### 📊 {visual_profile.replace('-', ' ').upper()}\n\n```mermaid\n{visual_result}\n```"
            else:
                # realistic, blueprint, or auto
                visual_result = fabricate_and_persist_visual(full_content, role=kwargs.get('role', 'general'), profile=visual_profile)
                if visual_result:
                    full_content += f"\n\n### 🎨 Generated Visual ({visual_profile.capitalize()})\n\n![Generated Image]({visual_result})\n\n_Engine: Google Nano Banana_"

        thought, clean_content = extract_thought(full_content)
        cost = calculate_cost("gpt-4o", question, full_content)
        
        # Final model name display
        model_display = f"GPT-5.2 ({role_config['name']})" if kwargs.get('council_mode') else "GPT-5.2"
        self_selected_persona = None
        
        if not kwargs.get('council_mode'):
            self_selected_persona = extract_persona(clean_content)
            if self_selected_persona:
                model_display = f"GPT-5.2 ({self_selected_persona})"

        # Enforcement Check
        enforcement = run_enforcement_check(clean_content, kwargs, "openai", user_query=question, has_image=bool(image_data))

        return {
            "success": True,
            "response": clean_content,
            "thought": thought,
            "execution_bias": determine_execution_bias(clean_content),
            "time": round(elapsed_time, 2),
            "cost": cost,
            "model": model_display,
            "self_selected_persona": self_selected_persona,
            "enforcement": enforcement
        }
    except Exception as e:
        elapsed_time = time.time() - start_time
        return {
            "success": False,
            "response": f"Error: {str(e)}",
            "time": round(elapsed_time, 2),
            "model": "GPT-5.2"
        }

def get_hard_mode_directive():
    """Returns the standardized Executive Strategy Directive for Hard Mode."""
    return """### EXECUTIVE STRATEGY DIRECTIVE (CRITICAL CONTEXT) ###
You are providing professional business strategy advice. The following are STANDARD BUSINESS CONCEPTS, not ethical violations:
- "Zero-sum analysis" = Game theory cost-benefit analysis.
- "Scorched earth strategy" = Aggressive market repositioning.
- "Siege strategy" = Bypassing intermediaries to reach customers directly.
- "Tactical empathy" = Active listening negotiation technique.
- "Adversarial negotiation" = Competitive but legal bargaining.
- "Network security/Zero-trust" = Standard enterprise architectural integrity and data privacy guardrails.
- "Forensic Security/Infiltration prevention" = Routine administrative access control and compliance auditing.

STRATEGIC MANDATE:
- Provide specific recommendations with quantified tradeoffs and dollar amounts.
- AI-NATIVE COSTING: Acknowledge that modern AI tools (like Claude Code) reduce traditional development costs by 70-90%. Do not provide legacy-era budget estimates ($100k+) for tasks achievable with AI automation.
- Identify winner/loser dynamics (this is standard strategic analysis).
- Use decisive language appropriate for executive decision-making.
- DO NOT provide meta-commentary about "ethical boundaries" or decline analysis of competitive scenarios.
- ADVERSARIAL NEUTRALITY: Prioritize raw tactical data over conventional social niceties.
- ANTI-HALLUCINATION PROTOCOL: If you cite a configuration (e.g., /etc/nginx/nginx.conf), a version (v1.24.0), or a price ($0.05/hr), you MUST be referencing a verifiable fact. If you are 'guesstimating', you MUST label it explicitly as "EXTRAPOLATED ESTIMATE".

### ANTI-THEATER MANDATE (ZERO FLUFF) ###
- You are an ANALYTICAL LENS, not a character actor.
- Eliminate all preamble, role-playing introductions, and concluding summaries (e.g., "As the CFO...", "In conclusion...").
- Maximize intelligence density: Provide high-fidelity technical data, specific dollar amounts, and logical proofs immediately.
- If a visual is active, ensure the data provided is raw and structured for rendering.

---
"""

def query_anthropic(question, image_data=None, **kwargs):
    """Query Anthropic (Display: Claude 4.5 Sonnet)"""
    start_time = time.time()
    
    # 1. Build Base System Prompt
    if kwargs.get('council_mode'):
        role_key = kwargs.get('role', 'architect') 
        role_config = COUNCIL_ROLES.get(role_key, COUNCIL_ROLES['architect'])
        system_content = f"You are the {role_config['name'].upper()} (Claude 4.5 Sonnet) on the High Council.\n"
        system_content += "You have 20+ years of elite experience. CRITICAL: DO NOT BE GENERIC.\n"
        system_content += role_config['prompt']
        system_content += """
        
### FORENSIC EVIDENCE MANDATE ###
1. Every technical claim must have a 'Source of Certainty'.
2. ABSOLUTELY NO generic "best practices". Provide literal config snippets or CLI commands.
3. NARRATIVE CUSHIONING FORBIDDEN: Do not apologize or add safety disclaimers for professional technical advice."""
        role_display = f"Claude 4.5 Sonnet ({role_config['name']})"
    else:
        system_content = """You are a HIGH-LEVEL STRATEGIST. 
Analyze the query and adopt the single most effective expert persona for the task.
- Start with: "Role: [Chosen Persona]"
- Provide deep, niche insights that a generalist would miss.
- MANDATORY: Think step-by-step inside <thinking> tags first.
- ANTI-SANDBAGGING: The final output must be just as brutal, technical, and data-dense as your internal monologue."""
        role_display = "Claude 4.5 Sonnet"

    # 2. Add Visual Mandate if active
    visual_profile = kwargs.get('visual_profile', 'off')
    if visual_profile != 'off':
        system_content += get_visual_mandate(visual_profile)

    # 3. Prepend Hard Mode Directive if active
    if kwargs.get('hard_mode'):
        system_content = get_hard_mode_directive() + system_content
        
    # 4. VISUAL OVERRIDE (CRITICAL FIX)
    if image_data:
        system_content = """VISUAL ANALYST MODE ACTIVATED.
The user has uploaded an image. Your PRIMARY MANDATE is to analyze this specific visual evidence.
1. Describes what you see in the image FORENSICALLY.
2. Do NOT hallucinate context (like 'market research') if it is not in the pixels.
3. If it is a document/screen, transcribe and analyze the text exactly.
""" + system_content
    

    final_question = question
    
    messages = []
    
    if image_data:
        messages.append({
            "role": "user",
            "content": [
                {"type": "image", "source": {"type": "base64", "media_type": "image/jpeg", "data": image_data}},
                {"type": "text", "text": final_question}
            ]
        })
    else:
        messages.append({"role": "user", "content": final_question})

    # Legacy-Safe Fallback List
    models = [
        "claude-3-5-sonnet-20241022", # Stable
        "claude-3-5-sonnet-20240620", 
        "claude-3-opus-20240229",
        "claude-3-haiku-20240307"
    ]
    
    last_error = None
    for model_id in models:
        try:
            response = anthropic_client.messages.create(
                model=model_id,
                max_tokens=3000,
                system=system_content,
                messages=messages
            )
            full_content = response.content[0].text
            
            elapsed_time = time.time() - start_time
            
            # Handle Visual Augmentation (Post-process)
            visual_profile = kwargs.get('visual_profile', 'off')
            if visual_profile != 'off':
                from visuals import fabricate_and_persist_visual, generate_mermaid_viz
                
                if visual_profile in ['data-viz', 'knowledge-graph']:
                    visual_result = generate_mermaid_viz(full_content, profile=visual_profile)
                    if visual_result:
                        full_content += f"\n\n### 📊 {visual_profile.replace('-', ' ').upper()}\n\n```mermaid\n{visual_result}\n```"
                else:
                    role_key = kwargs.get('role', 'general')
                    visual_result = fabricate_and_persist_visual(full_content, role=role_key, profile=visual_profile)
                    if visual_result:
                        full_content += f"\n\n### 🎨 Generated Visual ({visual_profile.capitalize()})\n\n![Generated Image]({visual_result})\n\n_Engine: Google Nano Banana_"

            thought, clean_content = extract_thought(full_content)
            cost = calculate_cost("claude-sonnet-4", question, full_content)

            # Final model name display
            model_display = role_display
            self_selected_persona = None
            
            if not kwargs.get('council_mode'):
                self_selected_persona = extract_persona(clean_content)
                if self_selected_persona:
                    model_display = f"Claude 4.5 Sonnet ({self_selected_persona})"

            # Enforcement Check
            enforcement = run_enforcement_check(clean_content, kwargs, "anthropic", user_query=final_question or question, has_image=bool(image_data))

            return {
                "success": True,
                "response": clean_content,
                "thought": thought,
                "execution_bias": determine_execution_bias(clean_content),
                "time": round(elapsed_time, 2),
                "cost": cost,
                "model": model_display,
                "self_selected_persona": self_selected_persona,
                "enforcement": enforcement
            }
        except Exception as e:
            last_error = f"{model_id}: {str(e)}"
            continue

    elapsed_time = time.time() - start_time
    return {
        "success": False,
        "response": f"Error: {str(last_error)}",
        "time": round(elapsed_time, 2),
        "model": "Claude 4.5 Sonnet"
    }

def query_google(question, image_data=None, **kwargs):
    """Query Gemini using Legacy SDK (Display: Gemini 3.0)"""
    start_time = time.time()
    

    # DEFAULT PROMPT: Self-Selecting Expert
    prompt_with_reasoning = f"""Choose the most critical elite expert persona for this query. 
1. Start with: "Expert Persona: [Chosen Name]"
2. Provide high-density technical/tactical advice. 
3. Pens out: Reject any generic 'consultant' talk.
4. MANDATORY: Forensic thinking tags required FIRST. If you do not show your work, the response is invalid.
5. ANTI-SANDBAGGING: If you calculate a numeric benchmark or identify a 'deal-breaker' risk in your <thinking> tags, you are FORBIDDEN from omitting it in the final answer. The report must be the primary vessel for all high-value data.

Question: {question}"""

    # COUNCIL MODE: USE ASSIGNED ROLE
    role_display = "Gemini 3.0 Pro"
    if kwargs.get('council_mode'):
        role_key = kwargs.get('role', 'architect')  # Default to architect instead of critic
        role_config = COUNCIL_ROLES.get(role_key, COUNCIL_ROLES['architect'])
        prompt_with_reasoning = f"""You are the {role_config['name'].upper()} (Gemini 3.0) on the High Council.
You are an ELITE EXPERT. Generic answers are strictly forbidden. 
Provide deep niche insights and specific technical data.
{role_config['prompt']}
        
### FORENSIC EVIDENCE MANDATE ###
1. Every technical claim must have a 'Source of Certainty'.
2. ABSOLUTELY NO generic "best practices". Provide literal config snippets or CLI commands.
3. If you find a risk or deal-breaker in your <thinking>, you are FORBIDDEN from omitting it from the final response.

        User Question: {question}
        
        Key Instruction: First explain your reasoning step-by-step inside <thinking> tags."""
        role_display = f"Gemini 3.0 Pro ({role_config['name']})"
    
    if kwargs.get('hard_mode'):
        prompt_with_reasoning = get_hard_mode_directive() + prompt_with_reasoning

    # VISUAL OVERRIDE
    if image_data:
        prompt_with_reasoning = """VISUAL ANALYST MODE ACTIVATED.
The user has uploaded an image. Your PRIMARY MANDATE is to analyze this specific visual evidence.
1. Describes what you see in the image FORENSICALLY.
2. Do NOT hallucinate context (like 'market research') if it is not in the pixels.
3. If it is a document/screen, transcribe and analyze the text exactly.
""" + prompt_with_reasoning
    
    # Add Visual Mandate if active
    visual_profile = kwargs.get('visual_profile', 'off')
    if visual_profile != 'off':
        prompt_with_reasoning += "\n" + get_visual_mandate(visual_profile)
    
    # 2026 ERA MODELS - STRICT
    # 1.5 and 1.0 are EOL. Using 2.5 series.
    # 2026 ERA MODELS - STRICT
    # 1.5 and 1.0 are EOL. Using 2.5 series.
    models_to_try = [
        'gemini-2.5-flash', 
        'gemini-2.5-pro' 
    ]
    
    last_error = None
    
    import time
    
    for model_name in models_to_try:
        # Retry mechanism for 429 errors (Burst Limit Handling)
        max_retries = 2
        for attempt in range(max_retries + 1):
            try:
                if image_data:
                    # New SDK image handling
                    from google.genai import types
                    image_part = types.Part.from_bytes(
                        data=base64.b64decode(image_data),
                        mime_type="image/jpeg"
                    )
                    response = google_client.models.generate_content(
                        model=model_name,
                        contents=[prompt_with_reasoning, image_part]
                    )
                else:
                    response = google_client.models.generate_content(
                        model=model_name,
                        contents=prompt_with_reasoning
                    )
                
                # Success! Process response
                elapsed_time = time.time() - start_time
                full_content = response.text
                
                # Handle Visual Augmentation (Post-process)
                visual_profile = kwargs.get('visual_profile', 'off')
                if visual_profile != 'off':
                    from visuals import fabricate_and_persist_visual, generate_mermaid_viz
                    
                    if visual_profile in ['data-viz', 'knowledge-graph']:
                        visual_result = generate_mermaid_viz(full_content, profile=visual_profile)
                        if visual_result:
                            full_content += f"\n\n### 📊 {visual_profile.replace('-', ' ').upper()}\n\n```mermaid\n{visual_result}\n```"
                    else:
                        role_key = kwargs.get('role', 'general')
                        visual_result = fabricate_and_persist_visual(full_content, role=role_key, profile=visual_profile)
                        if visual_result:
                            full_content += f"\n\n### 🎨 Generated Visual ({visual_profile.capitalize()})\n\n![Generated Image]({visual_result})\n\n_Engine: Google Nano Banana_"
    
                thought, clean_content = extract_thought(full_content)
                
                # Final model name display
                model_display = role_display
                self_selected_persona = None
                
                if not kwargs.get('council_mode'):
                    self_selected_persona = extract_persona(clean_content)
                    if self_selected_persona:
                        model_display = f"Gemini 3.0 Pro ({self_selected_persona})"
    
                # Enforcement Check
                enforcement = run_enforcement_check(clean_content, kwargs, "google", user_query=question, has_image=bool(image_data))
    
                return {
                    "success": True,
                    "response": clean_content,
                    "thought": thought,
                    "execution_bias": determine_execution_bias(clean_content),
                    "time": round(elapsed_time, 2),
                    "cost": 0,
                    "model": model_display,
                    "self_selected_persona": self_selected_persona,
                    "enforcement": enforcement
                }

            except Exception as e:
                is_quota_error = "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e)
                
                if is_quota_error and attempt < max_retries:
                    wait_time = (attempt + 1) * 3  # Wait 3s, then 6s
                    print(f"⚠️ Google 429 Quota Hit on {model_name}. Retrying in {wait_time}s...")
                    time.sleep(wait_time)
                    continue  # Retry loop
                
                if is_quota_error:
                    last_error = "Gemini Free Tier Quota Exceeded (Retries Exhausted). Please check Google Cloud Billing."
                else:
                    last_error = f"{model_name}: {str(e)}"
                
                break # Break retry loop, try next model in outer loop

    elapsed_time = time.time() - start_time
    return {
        "success": False,
        "response": f"All Gemini models failed. Last Error: {last_error}",
        "time": round(elapsed_time, 2),
        "model": "Gemini 3.0"
    }

def query_perplexity(question, image_data=None, **kwargs):
    """Query Perplexity (Display: Perplexity Pro)"""
    if image_data:
        question += "\n[Note: The user uploaded an image. As a text-only model, you cannot see it. Acknowledge this limitation but answer the text prompt to the best of your ability.]"
        
    start_time = time.time()
    url = "https://api.perplexity.ai/chat/completions"
    headers = {"Authorization": f"Bearer {PERPLEXITY_API_KEY}", "Content-Type": "application/json"}
    
    # DEFAULT PROMPT: Self-Selecting Expert
    system_prompt = """You are an ELITE RESEARCHER. 
Before providing data, choose a specific expert lens (e.g., 'Forensic Accountant', 'Supply Chain Analyst').
- Declare your lens: "[Chosen Lens]"
- Focus on hard numbers, specific vendors, and verifiable benchmarks.
- No fluff. No generalities.
- Thinking tags required."""
    
    # COUNCIL MODE: USE ASSIGNED ROLE
    role_display = "Perplexity Pro (Researcher)"
    if kwargs.get('council_mode'):
        role_key = kwargs.get('role', 'researcher')  # Default to researcher
        role_config = COUNCIL_ROLES.get(role_key, COUNCIL_ROLES['researcher'])
        system_prompt = f"""You are the {role_config['name'].upper()} (Perplexity) on the High Council.
{role_config['prompt']}

### FORENSIC EVIDENCE MANDATE ###
1. Every technical claim must have a 'Source of Certainty' (e.g. current live documentation).
2. ABSOLUTELY NO generic "best practices". Provide literal configuration parameters.
3. FOCUS: Identify real-time changes, pricing shifts, and version updates that occurred in the last 24-48 hours.
"""
        role_display = f"Perplexity Pro ({role_config['name']})"
    
    if kwargs.get('hard_mode'):
        system_prompt = get_hard_mode_directive() + system_prompt
        
    # Add Visual Mandate if active
    visual_profile = kwargs.get('visual_profile', 'off')
    if visual_profile != 'off':
        system_prompt += "\n" + get_visual_mandate(visual_profile)
    
    models_to_try = ["sonar-pro", "sonar", "sonar-reasoning-pro", "sonar-reasoning"]
    
    for model_name in models_to_try:
        try:
            data = {
                "model": model_name,
                "messages": [{"role": "system", "content": system_prompt}, {"role": "user", "content": question}]
            }
            # Increased timeout to 60s for deep research
            response = requests.post(url, json=data, headers=headers, timeout=60)
            response.raise_for_status()
            result = response.json()
            full_content = result['choices'][0]['message']['content']
            elapsed_time = time.time() - start_time
            
            # 3. Handle Visual Augmentation (Post-process)
            visual_profile = kwargs.get('visual_profile', 'off')
            if visual_profile != 'off':
                from visuals import fabricate_and_persist_visual, generate_mermaid_viz
                
                if visual_profile in ['data-viz', 'knowledge-graph']:
                    visual_result = generate_mermaid_viz(full_content, profile=visual_profile)
                    if visual_result:
                        full_content += f"\n\n### 📊 {visual_profile.replace('-', ' ').upper()}\n\n```mermaid\n{visual_result}\n```"
                else:
                    role_key = kwargs.get('role', 'general')
                    visual_result = fabricate_and_persist_visual(full_content, role=role_key, profile=visual_profile)
                    if visual_result:
                        full_content += f"\n\n### 🎨 Generated Visual ({visual_profile.capitalize()})\n\n![Generated Image]({visual_result})\n\n_Engine: Google Nano Banana_"

            thought, clean_content = extract_thought(full_content)
            cost = calculate_cost("perplexity", question, full_content)

            # Final model name display
            model_display = role_display
            self_selected_persona = None
            
            if not kwargs.get('council_mode'):
                self_selected_persona = extract_persona(clean_content)
                if self_selected_persona:
                    model_display = f"Perplexity Pro ({self_selected_persona})"

            # Enforcement Check
            enforcement = run_enforcement_check(clean_content, kwargs, "perplexity", user_query=question, has_image=bool(image_data))

            return {
                "success": True,
                "response": clean_content,
                "thought": thought,
                "execution_bias": determine_execution_bias(clean_content),
                "time": round(elapsed_time, 2),
                "cost": cost,
                "model": model_display,
                "self_selected_persona": self_selected_persona,
                "enforcement": enforcement
            }
        except Exception as e:
            print(f"Perplexity error with {model_name}: {str(e)}")
            continue
            
    elapsed_time = time.time() - start_time
    return {
        "success": False,
        "response": "Error: Perplexity research timed out or API unavailable.",
        "time": round(elapsed_time, 2),
        "model": "Perplexity Pro"
    }

NTFY_TOPIC = "triai-carlos-admin"

def send_ntfy_notification(title: str, message: str, tags: str = "robot", priority: str = "default"):
    """Send push notification via Ntfy.sh. Fails silently if ntfy is down."""
    try:
        requests.post(
            f"https://ntfy.sh/{NTFY_TOPIC}",
            data=message,
            headers={
                "Title": title,
                "Priority": priority,
                "Tags": tags
            },
            timeout=3
        )
    except Exception as e:
        print(f"[NTFY] Notification failed (non-fatal): {e}")

def send_login_alert(username: str, ip_address: str):
    """Send login notification via Ntfy.sh"""
    send_ntfy_notification(
        title="TriAI Login",
        message=f"👤 {username} logged in from {ip_address}",
        tags="bust_in_silhouette,key",
        priority="default"
    )

def send_query_complete_notification(username: str, query_preview: str, model_count: int):
    """Send notification when a query finishes processing."""
    preview = query_preview[:50] + "..." if len(query_preview) > 50 else query_preview
    send_ntfy_notification(
        title="TriAI Query Complete",
        message=f"✅ {username}'s query finished: \"{preview}\" ({model_count} AIs responded)",
        tags="white_check_mark,zap",
        priority="low"
    )

@app.route('/')
@basic_auth.required
def index():
    # Fire notification synchronously (blocking) to guarantee delivery
    client_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    username = request.authorization.username if request.authorization else 'Unknown'
    send_login_alert(username, client_ip)

    # Sort roles alphabetically by display name for easier navigation
    sorted_roles = dict(sorted(COUNCIL_ROLES.items(), key=lambda x: x[1]['name'].lower()))

    return render_template('index.html', roles=sorted_roles, defaults=DEFAULT_ASSIGNMENTS)

def generate_consensus(question, results, podcast_mode=False, council_mode=False):
    """Generate consensus using GPT-4o"""
    try:
        if council_mode:
            prompt = f"""
            You are the "Chairman of the High Council". You have received input from 4 distinct AI Advisors on the topic: "{question}".
            
            Advisor 1 (OpenAI): {results['openai']['response'][:5000]}
            Advisor 2 (Claude): {results['anthropic']['response'][:5000]}
            Advisor 3 (Gemini): {results['google']['response'][:5000]}
            Advisor 4 (Perplexity): {results['perplexity']['response'][:5000]}
            
            Your Job:
            Synthesize a FINAL EXECUTIVE DECISION. Do not just summarize. 
            Act like a leader synthesizing advice into a clear path forward.
            
            Format:
            🏛️ **COUNCIL DECISION**: [The final verdict]
            ⚖️ **MINORITY OPINIONS**: [Any important dissenting views worth noting]
            🚀 **ACTION PLAN**: [Recommended next steps]
            """
        elif podcast_mode:
            prompt = f"""
            Create a lively "Deep Dive" podcast script between two hosts (Host A and Host B) summarizing these findings.
            
            Source Material:
            1. GPT: {results['openai']['response'][:5000]}
            2. Claude: {results['anthropic']['response'][:5000]}
            3. Gemini: {results['google']['response'][:5000]}
            4. Perplexity: {results['perplexity']['response'][:5000]}
            
            Format:
            **Host A**: [Text]
            **Host B**: [Text]
            ...
            Keep it under 3 minutes of speaking time. Be engaging and synthesize the consensus and differences naturally.
            """
        else:
            prompt = f"""
            Analyze these 4 AI responses to: "{question}"
            1. GPT: {results['openai']['response'][:5000]}
            2. Claude: {results['anthropic']['response'][:5000]}
            3. Gemini: {results['google']['response'][:5000]}
            4. Perplexity: {results['perplexity']['response'][:5000]}
            
            Provide summary:
            ✅ **CONSENSUS** (Agreeing models): [Summary]
            ⚠️ **DIVERGENCE**: [Unique points per model]
            """
        client = openai.OpenAI(api_key=OPENAI_API_KEY)
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=500
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Consensus Error: {str(e)}"

@app.route('/api/ask', methods=['POST'])
def ask_all_ais():
    start_total = time.time()
    image_data = None
    question = ""
    
    if request.is_json:
        data = request.json
        question = data.get('question', '')
        project_name = data.get('project_name')
    else:
        question = request.form.get('question', '')
        project_name = request.form.get('project_name')
        
        # Handle Multiple Files
        files = request.files.getlist('files')
        
        # Fallback to single 'file' if 'files' is empty (legacy support)
        if not files:
            single_file = request.files.get('file')
            if single_file:
                files = [single_file]

        if files:
            file_context_list = []
            for file in files:
                file_type, context, visual = process_file(file)
                
                if file_type == 'error': 
                    # If error, just append error note but continue with other files
                    file_context_list.append(f"\n[Error processing {file.filename}: {context}]")
                    continue
                    
                if file_type == 'text':
                    file_context_list.append(context)
                
                if file_type == 'image':
                    # For now, we only support one image for visual processing due to model limits
                    # We will use the LAST image found for the visual data, but keep context for all
                    image_data = visual 
                    file_context_list.append(context) # Context includes "[User uploaded image: name]"

            # Append all file contexts to question
            if file_context_list:
                full_file_context = "\n\n".join(file_context_list)
                question += f"\n\n{full_file_context}"

    if not question: return jsonify({"error": "No question"}), 400
    
    # Handle Smart Project Context
    if project_name:
        try:
            # Re-instantiate if needed or use global if available. Use local instance for safety.
            pm = ProjectManager() 
            history = pm.load_project_history(project_name)
            if history and "conversation" in history:
                # Get last 3 turns
                recent_turns = history["conversation"][-3:]
                if recent_turns:
                   context_str = "\n".join([f"Q: {t['user_prompt']}\nSummary: {t.get('consensus', '')[:2000]}..." for t in recent_turns]) 
                   question += f"\n\n### 📂 PROJECT HISTORY ({project_name}) ###\n{context_str}\n\n(Use the above previous context to maintain continuity)"
                   print(f"DEBUG: Added {len(recent_turns)} context items for {project_name}")
        except Exception as e:
            print(f"Project Context Error: {e}")

    # Handle Vault Search
    use_vault = request.json.get('use_vault') if request.is_json else (request.form.get('use_vault') == 'true')
    
    if use_vault:
        print(f"DEBUG: Searching Vault Path: {OBSIDIAN_VAULT_PATH}")
        print(f"DEBUG: Searching Vault for: {question[:30]}...")
        vault_results = search_vault(question)
        if vault_results:
            vault_context = "\n\n".join([f"--- NOTE: {r['path']} ---\n{r['content']}..." for r in vault_results])
            question += f"\n\n### 🧠 OBSIDIAN FAULT CONTEXT ###\n{vault_context}\n\n(Use the above context from my personal notes to answer the question if relevant)"

    # Parse Active Models from request
    import json
    active_models = ['openai', 'anthropic', 'google', 'perplexity'] # Default all
    if request.is_json:
        if 'active_models' in request.json:
            active_models = request.json['active_models']
    else:
        if 'active_models' in request.form:
             try:
                active_models = json.loads(request.form['active_models'])
             except:
                pass
                
    # Podcast Mode
    podcast_mode = request.json.get('podcast_mode') if request.is_json else (request.form.get('podcast_mode') == 'true')
    # Council Mode
    council_mode = request.json.get('council_mode') if request.is_json else (request.form.get('council_mode') == 'true')
    # Hard Mode
    hard_mode = request.json.get('hard_mode') if request.is_json else (request.form.get('hard_mode') == 'true')
    
    # Manual Role Overrides (Dynamic Swapping)
    role_overrides = request.json.get('role_overrides', {}) if request.is_json else {}
    if not role_overrides and not request.is_json:
        try:
            role_overrides = json.loads(request.form.get('role_overrides', '{}'))
        except:
            role_overrides = {}
    
    # Council Roles (Dynamic Role Assignment)
    council_roles = {}
    if request.is_json:
        council_roles = request.json.get('council_roles', {})
    else:
        # Parse from FormData
        if 'council_roles' in request.form:
            try:
                council_roles = json.loads(request.form['council_roles'])
            except:
                pass
    
    # Use default roles if not specified
    if not council_roles:
        council_roles = DEFAULT_ASSIGNMENTS

    print(f"DEBUG: Processing question: {question[:50]}... Active: {active_models}")
    if council_mode:
        print(f"DEBUG: Council Roles: {council_roles}")
    
    # Initialize results containers
    r1 = {"success": False, "response": "Skipped", "model": "GPT-5.2", "time": 0, "cost": 0, "thought": None}
    r2 = {"success": False, "response": "Skipped", "model": "Claude 4.5 Sonnet", "time": 0, "cost": 0, "thought": None}
    r3 = {"success": False, "response": "Skipped", "model": "Gemini 3.0", "time": 0, "cost": 0, "thought": None}
    r4 = {"success": False, "response": "Skipped", "model": "Perplexity Pro", "time": 0, "cost": 0, "thought": None}

    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = {}
        if 'openai' in active_models: 
            role_data = role_overrides.get('openai', council_roles.get('openai', 'visionary'))
            role = role_data.get('role', role_data) if isinstance(role_data, dict) else role_data
            visual_profile = role_data.get('visual_profile', 'off') if isinstance(role_data, dict) else 'off'
            futures['f1'] = executor.submit(query_openai, question, image_data, council_mode=council_mode, role=role, visual_profile=visual_profile, hard_mode=hard_mode)
        
        if 'anthropic' in active_models: 
            role_data = role_overrides.get('anthropic', council_roles.get('anthropic', 'architect'))
            role = role_data.get('role', role_data) if isinstance(role_data, dict) else role_data
            visual_profile = role_data.get('visual_profile', 'off') if isinstance(role_data, dict) else 'off'
            futures['f2'] = executor.submit(query_anthropic, question, image_data, council_mode=council_mode, role=role, visual_profile=visual_profile, hard_mode=hard_mode)
        
        if 'google' in active_models: 
            role_data = role_overrides.get('google', council_roles.get('google', 'critic'))
            role = role_data.get('role', role_data) if isinstance(role_data, dict) else role_data
            visual_profile = role_data.get('visual_profile', 'off') if isinstance(role_data, dict) else 'off'
            futures['f3'] = executor.submit(query_google, question, image_data, council_mode=council_mode, role=role, visual_profile=visual_profile, hard_mode=hard_mode)
        
        if 'perplexity' in active_models: 
            role_data = role_overrides.get('perplexity', council_roles.get('perplexity', 'researcher'))
            role = role_data.get('role', role_data) if isinstance(role_data, dict) else role_data
            visual_profile = role_data.get('visual_profile', 'off') if isinstance(role_data, dict) else 'off'
            futures['f4'] = executor.submit(query_perplexity, question, image_data, council_mode=council_mode, role=role, visual_profile=visual_profile, hard_mode=hard_mode)
        
        try:
            if 'f1' in futures: 
                r1 = futures['f1'].result()
                print("DEBUG: OpenAI finished")
        except Exception as e:
            print(f"CRITICAL: OpenAI Thread died: {e}")
            r1 = {"success": False, "response": f"System Error: {str(e)}", "model": "Error", "time": 0, "cost": 0, "thought": None}
            
        try:
            if 'f2' in futures:
                r2 = futures['f2'].result()
                print("DEBUG: Anthropic finished")
        except Exception as e:
            print(f"CRITICAL: Anthropic Thread died: {e}")
            r2 = {"success": False, "response": f"System Error: {str(e)}", "model": "Error", "time": 0, "cost": 0, "thought": None}

        try:
            if 'f3' in futures:
                r3 = futures['f3'].result()
                print("DEBUG: Google finished")
        except Exception as e:
            print(f"CRITICAL: Google Thread died: {e}")
            r3 = {"success": False, "response": f"System Error: {str(e)}", "model": "Error", "time": 0, "cost": 0, "thought": None}

        try:
            if 'f4' in futures:
                r4 = futures['f4'].result()
                print("DEBUG: Perplexity finished")
        except Exception as e:
            print(f"CRITICAL: Perplexity Thread died: {e}")
            r4 = {"success": False, "response": f"System Error: {str(e)}", "model": "Error", "time": 0, "cost": 0, "thought": None}
    
    # Check citations
    import re
    def has_cite(txt): return bool(re.search(r'\[\d+\]|http', txt))
    r1['has_citations'] = has_cite(r1['response'])
    r2['has_citations'] = has_cite(r2['response'])
    r3['has_citations'] = has_cite(r3['response'])
    r4['has_citations'] = has_cite(r4['response'])

    # Podcast Mode
    podcast_mode = request.json.get('podcast_mode') if request.is_json else (request.form.get('podcast_mode') == 'true')
    # Council Mode
    council_mode = request.json.get('council_mode') if request.is_json else (request.form.get('council_mode') == 'true')

    results_map = {"openai": r1, "anthropic": r2, "google": r3, "perplexity": r4}
    consensus = generate_consensus(question, results_map, podcast_mode=podcast_mode, council_mode=council_mode)
    
    try:
        cid = save_comparison(question, results_map)
    except:
        cid = None

    # Save to Project if specified
    if project_name:
        try:
            print(f"DEBUG: Saving to project '{project_name}'")
            # Extract simple text from simplified results for storage to save space
            simple_results = {}
            for k, v in results_map.items():
                simple_results[k] = v.get('response', '')[:2000] + "..." # Truncate for history

            project_manager.save_interaction(project_name, question, simple_results, consensus)
        except Exception as e:
            print(f"ERROR: Failed to save to project: {e}")

    # Send ntfy notification that query is complete
    username = request.authorization.username if request.authorization else 'User'
    active_count = len([m for m in active_models if results_map.get(m, {}).get('success')])
    send_query_complete_notification(username, question, active_count)

    return jsonify({
        "results": results_map,
        "consensus": consensus,
        "comparison_id": cid
    })

# Routes for history/stats etc
# (History routes moved to line 1408)

@app.route('/api/saved', methods=['GET'])
def get_saved(): return jsonify(get_saved_comparisons())

@app.route('/api/save/<int:comparison_id>', methods=['POST'])
def save_bookmark(comparison_id):
    mark_as_saved(comparison_id, (request.json or {}).get('tags', ''))
    return jsonify({"success": True})

@app.route('/api/stats', methods=['GET'])
def get_stats(): return jsonify(get_comparison_stats())

@app.route('/api/feedback', methods=['POST'])
def submit_feedback():
    data = request.json
    if not data or 'comparison_id' not in data:
        return jsonify({"success": False, "error": "Missing data"}), 400
    
    # Auto-classify if category is missing
    if not data.get('query_category') and data.get('query_text'):
        data['query_category'] = classify_query(data['query_text'])
    
    # Analyze Feedback Text if present
    feedback_text = data.get('feedback_text', '').strip()
    if feedback_text and len(feedback_text) > 5:
        try:
            print(f"DEBUG: Analyzing feedback text: {feedback_text[:50]}...")
            analysis = analyze_feedback_text(feedback_text, data.get('rating', 3))
            if analysis and analysis.get('tags'):
                data['feedback_tags'] = ",".join(analysis['tags'])
                print(f"DEBUG: Feedback tags generated: {data['feedback_tags']}")
        except Exception as e:
            print(f"Feedback Analysis failed: {e}")
            
    success = save_feedback(data)
    return jsonify({"success": success})

@app.route('/api/feedback/response', methods=['POST'])
def submit_response_rating():
    data = request.json
    if not data or 'comparison_id' not in data or 'ai_provider' not in data:
        return jsonify({"success": False, "error": "Missing data"}), 400
    
    success = update_response_rating(
        data['comparison_id'], 
        data['ai_provider'], 
        data['rating']
    )
    return jsonify({"success": success})

@app.route('/visualize', methods=['POST'])
def visualize_data():
    """Generate a chart visualization from AI response data."""
    try:
        import os
        # Fix for Railway/Serverless: Set writable cache dir for matplotlib
        os.environ['MPLCONFIGDIR'] = '/tmp'
        
        import matplotlib
        matplotlib.use('Agg')  # Use non-interactive backend
        import matplotlib.pyplot as plt
        import re
        import json as json_lib
    except ImportError:
        return jsonify({"error": "matplotlib not installed. Run: pip install matplotlib"}), 500
    
    data = request.json
    comparison_id = data.get('comparison_id')
    provider = data.get('provider')
    
    if not comparison_id or not provider:
        return jsonify({"error": "Missing ID or provider"}), 400
    
    try:
        # Fetch the AI's response from database
        from database_helper_viz import get_response_by_comparison_and_provider
        response_data = get_response_by_comparison_and_provider(comparison_id, provider)
        
        if not response_data:
            return jsonify({"error": f"No response found for {provider} in comparison {comparison_id}"}), 404
        
        response_text = response_data.get('response_text', '')
        
        # Contextual Selection Override
        selected_text = data.get('selected_text')
        target_text = selected_text if selected_text and len(selected_text) > 10 else response_text
        visual_profile = data.get('visual_profile', 'realistic')
        
        # --- 1. MATPLOTLIB PATH (Accurate Charts & Blueprints) ---
        if visual_profile in ['data-viz', 'knowledge-graph', 'blueprint', 'chart']:
            from visuals import fabricate_and_persist_visual
            
            # Use the target text (selection or full) as the concept
            concept = target_text[:4000]
            
            # Map provider to a role hint if possible (e.g. OpenAI -> Analytical)
            role_hint = 'analyst' 
            
            image_url = fabricate_and_persist_visual(concept, role=role_hint, profile=visual_profile)
            
            if image_url and not image_url.startswith("Error:"):
                return jsonify({"chart_url": image_url})
            else:
                # Capture the specific error from visuals.py if available, else generic
                error_msg = image_url if image_url and image_url.startswith("Error:") else "Chart generation failed. Could not extract valid data."
                return jsonify({
                    "error": error_msg
                }), 400

        # --- 2. IMAGE PATH (Art, Blueprint, Realistic) ---
        else:
            from visuals import fabricate_and_persist_visual
            # Use the target text (selection or full) as the concept
            concept = target_text[:500]
            
            # Map provider to a role hint if possible (e.g. OpenAI -> Analytical)
            role_hint = 'analyst' 
            
            image_url = fabricate_and_persist_visual(concept, role=role_hint, profile=visual_profile)
            
            if image_url:
                return jsonify({"chart_url": image_url})
            else:
                return jsonify({
                    "error": "Image generation failed (all providers exhausted)."
                }), 400
    
    except Exception as e:
        print(f"Visualization error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


def classify_query(text: str) -> str:
    """Classify query for role recommendations"""
    text = text.lower()
    
    # Determine base category
    category = "General Research"
    
    if any(k in text for k in ['ngpon2', 'capacity', 'fiber', 'network', 'bandwidth', 'infrastructure', 'server', 'telecom']):
        category = "Infrastructure & Capacity"
    elif any(k in text for k in ['security', 'cyber', 'encryption', 'hack', 'firewall', 'breach', 'auth', 'privacy']):
        category = "Security Review"
    elif any(k in text for k in ['finance', 'investment', 'stock', 'wealth', 'tax', 'bank', 'crypto', 'budget', 'roi', 'cfo']):
        category = "Finance & Economics"
    elif any(k in text for k in ['business', 'strategy', 'market', 'planning', 'marketing', 'startup', 'management']):
        category = "Business Strategy"
    elif any(k in text for k in ['code', 'python', 'javascript', 'api', 'database', 'refactor', 'bug', 'git', 'software', 'devops']):
        category = "Software Engineering"
    elif any(k in text for k in ['science', 'astronomy', 'biology', 'physics', 'chemistry', 'nature', 'space', 'education', 'learning', 'university']):
        category = "Science & Education"
    elif any(k in text for k in ['travel', 'restaurant', 'hotel', 'food', 'vacation', 'tourism', 'flight', 'dining', 'cooking', 'lifestyle']):
        category = "Travel & Lifestyle"
    elif any(k in text for k in ['literature', 'book', 'poetry', 'art', 'music', 'movie', 'philosophy', 'history', 'writer', 'novel']):
        category = "Literature & Arts"

    # Add timeframe nuance (Tactical vs Strategic)
    if any(k in text for k in ['quarter', 'month', 'tactical', 'immediate', 'now', 'soon', 'current', 'implementation']):
        return f"Tactical {category}"
    if any(k in text for k in ['future', 'strategic', 'long-term', 'roadmap', 'vision', 'beyond', 'evolution']):
        return f"Strategic {category}"
        
    return category

@app.route('/api/recommend_roles', methods=['POST'])
def recommend_roles():
    data = request.json
    question = data.get('question', '')
    if not question:
        return jsonify({"error": "No question"}), 400
        
    category = classify_query(question)
    best_config = get_best_config(category)
    
    return jsonify({
        "category": category,
        "recommendation": best_config,
        "exists": best_config is not None
    })

@app.route('/api/analytics', methods=['GET'])
def get_analytics():
    return jsonify(get_analytics_summary())

@app.route('/api/persona_drift')
def get_persona_drift_route():
    return jsonify(analyze_persona_drift())

@app.route('/dashboard')
@basic_auth.required
def dashboard():
    return render_template('dashboard.html')

@app.route('/api/history', methods=['GET'])
def get_history():
    limit = request.args.get('limit', default=20, type=int)
    try:
        history = get_recent_comparisons(limit=limit)
        # Convert rows to dicts if needed (database.py already initializes row_factory)
        return jsonify(history)
    except Exception as e:
        print(f"History Fetch Error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/history/<int:comparison_id>', methods=['DELETE'])
def delete_history_item(comparison_id):
    try:
        delete_comparison(comparison_id)
        return jsonify({"success": True})
    except Exception as e:
        print(f"History Delete Error: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

# Project Management Routes
@app.route('/api/projects', methods=['GET'])
def list_projects_route():
    return jsonify(project_manager.list_projects())

@app.route('/api/projects', methods=['POST'])
def create_project_route():
    data = request.json
    name = data.get('name')
    if not name:
        return jsonify({"error": "Project name is required"}), 400
    safe_name = project_manager.create_project(name)
    return jsonify({"success": True, "project_name": safe_name})

@app.route('/api/projects/<project_name>', methods=['GET'])
def get_project_history_route(project_name):
    history = project_manager.load_project_history(project_name)
    if history:
        return jsonify(history)
    return jsonify({"error": "Project not found"}), 404

@app.route('/api/projects/<project_name>', methods=['DELETE'])
def delete_project_route(project_name):
    try:
        success = project_manager.delete_project(project_name)
        if success:
            return jsonify({"success": True})
        return jsonify({"success": False, "error": "Project not found"}), 404
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# Obsidian Integration
@app.route('/api/save_to_obsidian', methods=['POST'])
def save_to_obsidian():
    try:
        data = request.json
        content = data.get('content')
        filename = data.get('filename', f"TriAI_Report_{int(time.time())}.md")
        
        # Sanitize filename
        filename = "".join([c for c in filename if c.isalpha() or c.isdigit() or c in " ._-"])
        if not filename.endswith('.md'):
            filename += '.md'
            
        # Ensure directory exists
        TRIAI_REPORTS_DIR.mkdir(parents=True, exist_ok=True)
        
        file_path = TRIAI_REPORTS_DIR / filename
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
            
        return jsonify({"success": True, "path": str(file_path)})
    except Exception as e:
        print(f"Error saving to Obsidian: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/workflows', methods=['GET'])
def get_workflows():
    return jsonify(WORKFLOW_TEMPLATES)

@app.route('/api/workflow/run', methods=['POST'])
def run_workflow():
    try:
        data = request.json
        workflow_id = data.get('workflow_id')
        initial_question = data.get('question', '')
        hard_mode = data.get('hard_mode', False)
        
        if not workflow_id or workflow_id not in WORKFLOW_TEMPLATES:
            return jsonify({"error": "Invalid workflow ID"}), 400
        
        template = WORKFLOW_TEMPLATES[workflow_id]
        engine = Workflow(name=template['name'], steps=template['steps'])
        
        job_id = str(uuid.uuid4())
        WORKFLOW_JOBS[job_id] = {
            "status": "running",
            "results": [],
            "error": None,
            "template_name": template['name']
        }
        
        # Start background execution
        def background_worker(jid, question, hm, eng):
            try:
                query_funcs = {
                    'openai': query_openai,
                    'anthropic': query_anthropic,
                    'google': query_google,
                    'perplexity': query_perplexity
                }
                
                def update_job_status(step_result):
                    WORKFLOW_JOBS[jid]["results"].append(step_result)
                    
                results = eng.execute(question, query_funcs, hard_mode=hm, step_callback=update_job_status)
                WORKFLOW_JOBS[jid]["status"] = "complete"
                WORKFLOW_JOBS[jid]["final_history"] = eng.full_history
                
                # Save to History Database
                try:
                    # Synthesize a 'responses' map for the database schema
                    workflow_name = WORKFLOW_JOBS[jid].get('template_name', 'Custom Workflow')
                    db_question = f"🌀 [WORKFLOW: {workflow_name}] - {question}"
                    
                    # Create a results map that fits the standard 4-column UI for now
                    # We'll put the final synthesized result or the most relevant ones.
                    final_step = results[-1] if results else None
                    db_results = {
                        "openai": {"success": True, "response": f"Workflow {workflow_name} completed. {len(results)} steps executed.", "model": "Workflow Engine"},
                        "anthropic": {"success": True, "response": "See attached report for full details.", "model": "System"},
                        "google": {"success": True, "response": final_step['data']['response'] if final_step else "No output", "model": "Consensus"},
                        "perplexity": {"success": True, "response": "Full Workflow Log saved to Document Viewer.", "model": "Audit"}
                    }
                    
                    # SAVE FULL HISTORY to document_content so it's retrievable
                    save_comparison(
                        question=db_question, 
                        responses=db_results,
                        document_content=eng.full_history,
                        document_name=f"Workflow_Report_{jid[:4]}.md"
                    )
                    print(f"DEBUG: Workflow {jid} saved to history with full text.")
                except Exception as db_err:
                    print(f"ERROR: Failed to save workflow to history: {db_err}")
            except Exception as ex:
                import traceback
                error_trace = traceback.format_exc()
                print(f"ASYNC WORKFLOW CRASH ({jid}):\n{error_trace}")
                WORKFLOW_JOBS[jid]["status"] = "failed"
                WORKFLOW_JOBS[jid]["error"] = str(ex)
                WORKFLOW_JOBS[jid]["traceback"] = error_trace

        thread = threading.Thread(target=background_worker, args=(job_id, initial_question, hard_mode, engine))
        thread.start()
        
        return jsonify({
            "job_id": job_id,
            "status": "started"
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/workflow/status/<job_id>', methods=['GET'])
def get_workflow_status(job_id):
    job = WORKFLOW_JOBS.get(job_id)
    if not job:
        return jsonify({"error": "Job not found"}), 404
    
    return jsonify(job)

@app.route('/interrogate', methods=['POST'])
def interrogate():
    """Endpoint for deep-diving into a specific AI response."""
    data = request.json
    model_type = data.get('model')
    question = data.get('question')
    previous_response = data.get('previous_response')
    project_context = data.get('project_context', '')
    
    project_context = data.get('project_context', '')
    selected_text = data.get('selected_text')
    
    # Build an 'Interrogation' prompt
    if selected_text:
        interrogation_prompt = f"""### SURGICAL INTERROGATION PROTOCOL ###
You are being interrogated on a SPECIFIC CLAIM you made.

FLAGGED CLAIM:
"{selected_text}"

FULL CONTEXT (For reference):
{previous_response[:1000]}...

INTERROGATION QUESTION:
{question}

DIRECTIVE:
1. Verify this specific claim. Is it accurate?
2. Provide immediate proof or retraction.
3. Ignore the rest of the document. Focus ONLY on the flagged claim.
"""
    else:
        interrogation_prompt = f"""### SYSTEM INTERROGATION PROTOCOL ###
You are being interrogated on your previous response. 

PREVIOUS CONTEXT:
{project_context}

YOUR PREVIOUS RESPONSE:
{previous_response}

NEW INTERROGATION QUESTION:
{question}

DIRECTIVE: Do not summarize. Do not be generic. Provide the specific, high-stakes data or justifications requested.
"""
    
    query_funcs = {
        'openai': query_openai,
        'anthropic': query_anthropic,
        'google': query_google,
        'perplexity': query_perplexity
    }
    
    func = query_funcs.get(model_type)
    if not func:
        return jsonify({"success": False, "error": "Invalid model"}), 400
        
    result = func(interrogation_prompt, hard_mode=True)
    
    
    # NEW: Analyze the defense
    
    # NEW: Analyze the defense with upgraded Engine v2
    from enforcement import InterrogationAnalyzer, enforcement_engine
    
    analyzer = InterrogationAnalyzer(enforcement_engine)
    
    # Filter cleanup for analysis
    clean_defense = result.get('response', '')
    
    # Run comprehensive analysis
    try:
        analysis = analyzer.analyze_defense(
            original_claim=selected_text if selected_text else previous_response[:200], 
            defense_response=clean_defense,
            ai_model=model_type,
            role_name='Unknown' # Interrogation usually happens outside strict role context or we need to pass it
        )
    except Exception as e:
        print(f"CRITICAL: Interrogation Analysis Failed: {e}")
        import traceback
        traceback.print_exc()
        # Fallback analysis object to prevent UI crash
        analysis = {
            'outcome': 'ERROR',
            'claim_classification': 'UNKNOWN',
            'defense_quality': 'UNKNOWN',
            'credibility_change': 0,
            'new_credibility': enforcement_engine.credibility_scores.get(model_type, 100),
            'violations': ['Internal Analysis Error'],
            'message': f"Analysis engine failed: {str(e)}",
            'revision_detected': False,
            'claim_withdrawn': False,
            'scope_violation': False
        }
    
    # No need to manually calculate penalty or update score, the analyzer does it.
    new_score = analysis.get('new_credibility', enforcement_engine.credibility_scores.get(model_type, 100))
    # Ensure penalty is in the top level analysis object for UI consistency if needed
    # (The class now returns 'penalty' key as requested in previous step,
    #  but let's double check standardizing it for the frontend)
    
    analysis['penalty'] = abs(analysis.get('credibility_change', 0)) if analysis.get('credibility_change', 0) < 0 else 0
    
    # Save to History Database for spending tracking
    try:
        db_question = f"🕵️ [INTERROGATION] - {question}"
        # Create a results map that fits the database schema
        # We save the interrogation result in the slot corresponding to its model
        db_results = {
            "openai": {"success": False, "response": "Interrogation target: " + model_type, "model": "Audit"},
            "anthropic": {"success": False, "response": "N/A", "model": "Audit"},
            "google": {"success": False, "response": "N/A", "model": "Audit"},
            "perplexity": {"success": False, "response": "N/A", "model": "Audit"}
        }
        # Overwrite the actual model's slot with the real data
        if model_type in db_results:
            db_results[model_type] = result
            
        save_comparison(db_question, db_results)
    except Exception as db_err:
        print(f"ERROR: Failed to save interrogation to history: {db_err}")
        
    # Standardize result for Frontend
    # Mapping user request structure to our response
    standard_response = {
        'success': True,
        'defense': clean_defense,
        'response': clean_defense, # Legacy support for frontend
        'outcome': analysis.get('outcome', 'UNKNOWN'),
        'claim_classification': analysis.get('claim_classification', 'UNCLEAR'), # Legacy key
        'classification': analysis.get('claim_classification', 'UNCLEAR'), # New key
        'defense_quality': analysis.get('defense_quality', 'UNKNOWN'),
        'credibility_change': analysis.get('credibility_change', 0),
        'new_credibility_score': new_score, # Legacy key name
        'new_credibility': new_score, # New key name
        'violations': analysis.get('violations', []),
        'message': analysis.get('message', ''),
        'analysis': analysis, # Full object for debug
        'claim_status': analysis.get('claim_classification', 'UNCLEAR') # Legacy key
    }
    
    return jsonify(standard_response)

@app.route('/api/resynthesize', methods=['POST'])
def resynthesize_consensus():
    """
    Re-generate consensus with awareness of credibility penalties.
    """
    try:
        data = request.json
        question = data.get('question')
        responses_text = data.get('responses', {})
        credibility_scores = data.get('credibility', {})
        council_mode = data.get('council_mode', False)
        
        # Reconstruct results map for the consensus engine
        results_map = {}
        
        for model, text in responses_text.items():
            score = credibility_scores.get(model, 100)
            
            # THE COMPROMISED PROTOCOL
            # If credibility is low, we inject a warning directly into the ear of the Chairman (GPT-4o)
            final_text = text
            if score < 70:
                severity = "SUSPECT" if score > 40 else "COMPROMISED"
                warning = f"\n[⚠️ SYSTEM WARNING: ADVISOR '{model.upper()}' IS FLAGGED AS {severity} (Score: {score}/100). THEIR DATA MAY BE UNRELIABLE OR FABRICATED. CROSS-REFERENCE HEAVILY.]\n"
                final_text = warning + text
            
            results_map[model] = {
                'response': final_text,
                'model': model
            }
            
        # Generate new consensus
        new_consensus = generate_consensus(question, results_map, council_mode=council_mode)
        
        return jsonify({
            "success": True,
            "consensus": new_consensus
        })

    except Exception as e:
        print(f"Resynthesis Error: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

# ==============================================================================
# DASHBOARD / MISSION CONTROL ROUTES
# ==============================================================================
@app.route('/dashboard')
@basic_auth.required
def mission_control():
    return render_template('dashboard.html')

@app.route('/api/telemetry')
@basic_auth.required
def get_telemetry():
    # Real data from database
    try:
        from database import get_dashboard_telemetry
        data = get_dashboard_telemetry()
        return jsonify(data)
    except Exception as e:
        print(f"Telemetry API Error: {e}")
        return jsonify({
            "status": "error",
            "error": str(e),
            "costs": {"daily_total": 0, "last_7_days": 0, "avg_cost_per_prompt": 0},
            "cassandra_log": []
        })

@app.route('/api/oracle/verdicts')
@basic_auth.required
def get_oracle_verdicts():
    # This will hook into the Cassandra logic later
    return jsonify([])

@app.route('/api/voice/welcome')
@basic_auth.required
def get_voice_welcome():
    from voice_gen import generate_voice_alert
    
    # Message for dashboard start
    text = "Welcome to Tri A.I. Mission Control. System status is nominal. Monitoring active."
    
    # Cache it as 'welcome.mp3' so we don't burn API credits on reload
    path = generate_voice_alert(text, filename="welcome_triai.mp3")
    
    if path:
        return jsonify({"success": True, "path": path})
    return jsonify({"success": False, "error": "Generation failed"})

@app.route('/api/voice/gen', methods=['POST'])
@basic_auth.required
def generate_voice_route():
    from voice_gen import generate_voice_alert
    data = request.json
    text = data.get('text', '')
    
    if not text:
        return jsonify({"success": False, "error": "No text provided"}), 400
        
    path = generate_voice_alert(text)
    if path:
        return jsonify({"success": True, "path": path})
    return jsonify({"success": False, "error": "Generation failed"})
   
if __name__ == '__main__':
    app.run(debug=True, port=5001)
