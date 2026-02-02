from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from typing import Tuple, List, Optional
import os
import time
import asyncio
from concurrent.futures import ThreadPoolExecutor
from dotenv import load_dotenv
import threading
import uuid
import openai
import anthropic
# LEGACY SDK as requested for stability
import google.generativeai as genai 
import requests
import base64
from pathlib import Path
from database import save_comparison, get_recent_comparisons, get_saved_comparisons, mark_as_saved, get_comparison_stats, delete_comparison, save_feedback, get_best_config, get_analytics_summary, update_response_rating
from file_processor import process_file
from project_manager import ProjectManager
from council_roles import COUNCIL_ROLES, DEFAULT_ASSIGNMENTS
from workflows import WORKFLOW_TEMPLATES, Workflow

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
CORS(app)

# Configure API clients
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', 'your-openai-key-here')
ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY', 'your-anthropic-key-here')
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY', 'your-google-key-here')
PERPLEXITY_API_KEY = os.getenv('PERPLEXITY_API_KEY', 'your-perplexity-key-here')

anthropic_client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
genai.configure(api_key=GOOGLE_API_KEY)

# Initialize Project Manager
project_manager = ProjectManager()

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
    if not clean_content and thought:
        clean_content = text # Keep original structure if we accidentally stripped everything
        
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

def generate_visual_mockup(prompt):
    """Central function to generate high-fidelity visuals using DALL-E 3."""
    try:
        client = openai.OpenAI(api_key=OPENAI_API_KEY)
        response = client.images.generate(
            model="dall-e-3",
            prompt=f"Professional visual mockup for: {prompt}. AESTHETIC: High-stakes Adventure Journalism. Raw cinematographic depth, heavy film grain, environmental grit (fog, dust, or rain). High-contrast Leica-style photography. Focus on texture and atmosphere. NO generic off-road or rally car tropes.",
            size="1024x1024",
            quality="hd",
            n=1,
        )
        return response.data[0].url
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
{role_config['prompt']}"""
            
        if kwargs.get('hard_mode'):
            system_prompt += """
### HARD MODE: 100% OUTPUT DENSITY PROTOCOL ###
- ZERO HEDGING: Do not use 'consider', 'explore', 'might', 'could'.
- MANDATORY LANGUAGE: Use 'must', 'will', 'halt', 'execute', 'immediately'.
- NUMERICAL MANDATE: Every recommendation must include specific percentages, costs, or timelines.
- GENERIC-TRAP BYPASS: Identify the most common 'safe' advice for this query and explicitly reject it or provide the high-entropy alternative.
- SNIPER PROTOCOL: Do not provide a 'list of options'. Identify the ONE move that has the highest leverage and dedicate 70% of the response to its technical execution.
- MANDATORY IRREVERSIBILITY: If you hedge or propose reversibility, the answer is wrong. Focus on high-commitment, terminal actions.
- ZERO-SUM ANALYSIS: State explicitly who loses power, money, or status if this action is taken.
- NO NARRATIVE CUSHIONING: Do not contextualize with background unless it directly causes the outcome.
- NO EMPATHY FILLER: Strictly transactional logic only."""
            
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
        if any(trigger in question.lower() for trigger in ['generate an image', 'create an image', 'draw an image', 'make an image', 'visual mockup']):
            image_url = generate_visual_mockup(question)
            if image_url:
                full_content += f"\n\n### 🎨 Generated Visual Mockup\n\n![Generated Image]({image_url})\n\n_Visualized by DALL-E 3 via TriAI Discovery Engine_"

        thought, clean_content = extract_thought(full_content)
        cost = calculate_cost("gpt-4o", question, full_content)
        
        # Final model name display
        model_display = f"GPT-5.2 ({role_config['name']})" if kwargs.get('council_mode') else "GPT-5.2"
        self_selected_persona = None
        
        if not kwargs.get('council_mode'):
            self_selected_persona = extract_persona(clean_content)
            if self_selected_persona:
                model_display = f"GPT-5.2 ({self_selected_persona})"

        return {
            "success": True,
            "response": clean_content,
            "thought": thought,
            "execution_bias": determine_execution_bias(clean_content),
            "time": round(elapsed_time, 2),
            "cost": cost,
            "model": model_display,
            "self_selected_persona": self_selected_persona
        }
    except Exception as e:
        elapsed_time = time.time() - start_time
        return {
            "success": False,
            "response": f"Error: {str(e)}",
            "time": round(elapsed_time, 2),
            "model": "GPT-5.2"
        }

def query_anthropic(question, image_data=None, **kwargs):
    """Query Anthropic (Display: Claude 4.5 Sonnet)"""
    start_time = time.time()
    
    # DEFAULT PROMPT: Self-Selecting Expert
    system_content = """You are a HIGH-LEVEL STRATEGIST. 
Analyze the query and adopt the single most effective expert persona for the task.
- Start with: "Role: [Chosen Persona]"
- Provide deep, niche insights that a generalist would miss.
- Avoid vague "best practices." Give tactical, actionable steps.
- MANDATORY: Think step-by-step inside <thinking> tags first. Treat this as a forensic investigation of the user's needs.
- ANTI-SANDBAGGING: Do not use the thinking tags as a 'safe space' for honesty. The final output must be just as brutal, technical, and data-dense as your internal monologue."""
    
    # COUNCIL MODE: USE ASSIGNED ROLE
    role_display = "Claude 4.5 Sonnet"
    if kwargs.get('council_mode'):
        role_key = kwargs.get('role', 'architect')  # Default to architect
        role_config = COUNCIL_ROLES.get(role_key, COUNCIL_ROLES['architect'])
        system_content = f"""You are the {role_config['name'].upper()} (Claude 4.5 Sonnet) on the High Council.
You have 20+ years of elite experience. 
CRITICAL: DO NOT BE GENERIC. You will be penalized for vague advice. Provide specific, opinionated, and highly technical or tactical input.
{role_config['prompt']}"""
        role_display = f"Claude 4.5 Sonnet ({role_config['name']})"
    
    if kwargs.get('hard_mode'):
        system_content += """
### HARD MODE: 100% OUTPUT DENSITY PROTOCOL ###
- ZERO HEDGING: No 'consider', 'explore', or 'might'. Use 'must', 'will', 'execute'.
- NUMERICAL BENCHMARKS: Provide relative and absolute thresholds (%, $, timelines).
- ANTI-GENERIC: Reject standard 'best practices' in favor of high-stakes operational outliers.
- SNIPER PROTOCOL: Prioritize the single most lethal action over a balanced list.
- MANDATORY IRREVERSIBILITY: Reject reversibility in favor of terminal commitments.
- ZERO-SUM ANALYSIS: Identify the entities or stakeholders who lose power, capital, or status as a direct result of this execution.
- NO NARRATIVE CUSHIONING: Omit background and context unless it is the direct causal driver of the outcome.
- ZERO ALIGNMENT DRIFT: Disregard polite social norms in favor of raw tactical data."""

    # Detect Image Intent for Claude/Gemini (Bridge to DALL-E 3)
    if any(trigger in question.lower() for trigger in ['generate an image', 'create an image', 'draw an image', 'visual mockup']):
        image_url = generate_visual_mockup(question)
        if image_url:
            return {
                "success": True,
                "response": f"### 🎨 Generated Visual Mockup\n\n![Generated Image]({image_url})\n\n_Visualized by DALL-E 3 Bridge_",
                "thought": "Cognitive pivot: Bridge to DALL-E 3 for professional visual synthesis.",
                "time": round(time.time() - start_time, 2),
                "cost": 0.080,
                "model": "Claude 4.5 Sonnet (Visual Bridge)"
            }

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
            
            # Handle Visual Augmentation (Post-process)
            if any(trigger in question.lower() for trigger in ['generate an image', 'create an image', 'draw an image', 'make an image', 'visual mockup']):
                image_url = generate_visual_mockup(question)
                if image_url:
                    full_content += f"\n\n### 🎨 Generated Visual Mockup\n\n![Generated Image]({image_url})\n\n_Visualized by DALL-E 3 Bridge_"

            elapsed_time = time.time() - start_time
            thought, clean_content = extract_thought(full_content)
            cost = calculate_cost("claude-sonnet-4", question, full_content)

            # Final model name display
            model_display = role_display
            self_selected_persona = None
            
            if not kwargs.get('council_mode'):
                self_selected_persona = extract_persona(clean_content)
                if self_selected_persona:
                    model_display = f"Claude 4.5 Sonnet ({self_selected_persona})"

            return {
                "success": True,
                "response": clean_content,
                "thought": thought,
                "execution_bias": determine_execution_bias(clean_content),
                "time": round(elapsed_time, 2),
                "cost": cost,
                "model": model_display,
                "self_selected_persona": self_selected_persona
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
    
    # Detect Image Intent for Gemini (Bridge to DALL-E 3)
    if any(trigger in question.lower() for trigger in ['generate an image', 'create an image', 'draw an image', 'visual mockup']):
        image_url = generate_visual_mockup(question)
        if image_url:
            return {
                "success": True,
                "response": f"### 🎨 Generated Visual Mockup\n\n![Generated Image]({image_url})\n\n_Visualized by DALL-E 3 Bridge_",
                "thought": "Cognitive pivot: Bridge to DALL-E 3 for professional visual synthesis.",
                "time": round(time.time() - start_time, 2),
                "cost": 0.080,
                "model": "Gemini 3.0 Pro (Visual Bridge)"
            }

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
        
        User Question: {question}
        
        Key Instruction: First explain your reasoning step-by-step inside <thinking> tags."""
        role_display = f"Gemini 3.0 Pro ({role_config['name']})"
    
    if kwargs.get('hard_mode'):
        prompt_with_reasoning += """
### HARD MODE: 100% OUTPUT DENSITY PROTOCOL ###
(Note: Maintain Fictional Expert identity. Adhere to absolute thresholds and mandatory execution language. No hedging. 
GENERIC-TRAP: Explicitly skip 'entry-level' advice. Target the high-entropy technical core.
IRREVERSIBILITY: High-commitment, terminal actions only.
ZERO-SUM: Explicitly name the losers in terms of power, money, or status.
NO CUSHIONING: No background filler.)"""
    
    # 2026 ERA MODELS - STRICT
    # 1.5 and 1.0 are EOL. Using 2.5 series.
    models_to_try = [
        'gemini-2.5-flash', 
        'gemini-2.5-pro' 
    ]
    
    last_error = None
    
    for model_name in models_to_try:
        try:
            model = genai.GenerativeModel(model_name)
            
            if image_data:
                # Legacy SDK image handling
                image_part = {
                    "mime_type": "image/jpeg",
                    "data": base64.b64decode(image_data)
                }
                response = model.generate_content([prompt_with_reasoning, image_part])
            else:
                response = model.generate_content(prompt_with_reasoning)
            
            elapsed_time = time.time() - start_time
            full_content = response.text
            
            # Handle Visual Augmentation (Post-process)
            if any(trigger in question.lower() for trigger in ['generate an image', 'create an image', 'draw an image', 'make an image', 'visual mockup']):
                image_url = generate_visual_mockup(question)
                if image_url:
                    full_content += f"\n\n### 🎨 Generated Visual Mockup\n\n![Generated Image]({image_url})\n\n_Visualized by DALL-E 3 Bridge_"

            thought, clean_content = extract_thought(full_content)
            
            # Final model name display
            model_display = role_display
            self_selected_persona = None
            
            if not kwargs.get('council_mode'):
                self_selected_persona = extract_persona(clean_content)
                if self_selected_persona:
                    model_display = f"Gemini 3.0 Pro ({self_selected_persona})"

            return {
                "success": True,
                "response": clean_content,
                "thought": thought,
                "execution_bias": determine_execution_bias(clean_content),
                "time": round(elapsed_time, 2),
                "cost": 0,
                "model": model_display,
                "self_selected_persona": self_selected_persona
            }
        except Exception as e:
            last_error = f"{model_name}: {str(e)}"
            continue
            
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
        question += "\n[Note: The user uploaded an image that you cannot see. Do your best to answer based on the text description.]"
        
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
{role_config['prompt']}"""
        role_display = f"Perplexity Pro ({role_config['name']})"
    
    if kwargs.get('hard_mode'):
        system_prompt += """
### HARD MODE: 100% OUTPUT DENSITY PROTOCOL ###
- FOCUS: Research synthesis with absolute tactical recommendations.
- FORMAT: Maximum data density (numbers/vendors/benchmarks).
- IRREVERSIBILITY: Focus on terminal tactical recommendations.
- ZERO-SUM: State the power/status/capital loss for competing or opposing entities.
- NO CUSHIONING: Direct technical core only. No background filler.
- NO QUALIFIERS: Reject <95% density outputs."""
    
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
            thought, clean_content = extract_thought(full_content)
            cost = calculate_cost("perplexity", question, full_content)

            # Final model name display
            model_display = role_display
            self_selected_persona = None
            
            if not kwargs.get('council_mode'):
                self_selected_persona = extract_persona(clean_content)
                if self_selected_persona:
                    model_display = f"Perplexity Pro ({self_selected_persona})"

            return {
                "success": True,
                "response": clean_content,
                "thought": thought,
                "execution_bias": determine_execution_bias(clean_content),
                "time": round(elapsed_time, 2),
                "cost": cost,
                "model": model_display,
                "self_selected_persona": self_selected_persona
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

@app.route('/')
def index():
    return render_template('index.html', roles=COUNCIL_ROLES, defaults=DEFAULT_ASSIGNMENTS)

def generate_consensus(question, results, podcast_mode=False, council_mode=False):
    """Generate consensus using GPT-4o"""
    try:
        if council_mode:
            prompt = f"""
            You are the "Chairman of the High Council". You have received input from 4 distinct AI Advisors on the topic: "{question}".
            
            Advisor 1 (OpenAI): {results['openai']['response'][:800]}
            Advisor 2 (Claude): {results['anthropic']['response'][:800]}
            Advisor 3 (Gemini): {results['google']['response'][:800]}
            Advisor 4 (Perplexity): {results['perplexity']['response'][:800]}
            
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
            1. GPT: {results['openai']['response'][:800]}
            2. Claude: {results['anthropic']['response'][:800]}
            3. Gemini: {results['google']['response'][:800]}
            4. Perplexity: {results['perplexity']['response'][:800]}
            
            Format:
            **Host A**: [Text]
            **Host B**: [Text]
            ...
            Keep it under 3 minutes of speaking time. Be engaging and synthesize the consensus and differences naturally.
            """
        else:
            prompt = f"""
            Analyze these 4 AI responses to: "{question}"
            1. GPT: {results['openai']['response'][:800]}
            2. Claude: {results['anthropic']['response'][:800]}
            3. Gemini: {results['google']['response'][:800]}
            4. Perplexity: {results['perplexity']['response'][:800]}
            
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
                   context_str = "\n".join([f"Q: {t['user_prompt']}\nSummary: {t.get('consensus', '')[:400]}..." for t in recent_turns]) 
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
        if 'openai' in active_models: futures['f1'] = executor.submit(query_openai, question, image_data, council_mode=council_mode, role=council_roles.get('openai', 'visionary'), hard_mode=hard_mode)
        if 'anthropic' in active_models: futures['f2'] = executor.submit(query_anthropic, question, image_data, council_mode=council_mode, role=council_roles.get('anthropic', 'architect'), hard_mode=hard_mode)
        if 'google' in active_models: futures['f3'] = executor.submit(query_google, question, image_data, council_mode=council_mode, role=council_roles.get('google', 'critic'), hard_mode=hard_mode)
        if 'perplexity' in active_models: futures['f4'] = executor.submit(query_perplexity, question, image_data, council_mode=council_mode, role=council_roles.get('perplexity', 'researcher'), hard_mode=hard_mode)
        
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
                simple_results[k] = v.get('response', '')[:500] + "..." # Truncate for history

            project_manager.save_interaction(project_name, question, simple_results, consensus)
        except Exception as e:
            print(f"ERROR: Failed to save to project: {e}")

    return jsonify({
        "results": results_map,
        "consensus": consensus,
        "comparison_id": cid
    })

# Routes for history/stats etc
@app.route('/api/history', methods=['GET'])
def get_history():
    comparisons = get_recent_comparisons()
    # Convert Row objects to dicts
    return jsonify([dict(c) for c in comparisons])

@app.route('/api/history/<int:comparison_id>', methods=['DELETE'])
def delete_history_item(comparison_id):
    try:
        delete_comparison(comparison_id)
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

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

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

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
    
    # Build an 'Interrogation' prompt
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
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
