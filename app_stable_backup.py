from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import os
import time
import asyncio
from concurrent.futures import ThreadPoolExecutor
from dotenv import load_dotenv
import openai
import anthropic
# LEGACY SDK as requested for stability
import google.generativeai as genai 
import requests
import base64
from database import save_comparison, get_recent_comparisons, get_saved_comparisons, mark_as_saved, get_comparison_stats
from file_processor import process_file

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

def extract_thought(text):
    """Extract content within <thinking> tags"""
    import re
    match = re.search(r'<thinking>(.*?)</thinking>', text, re.DOTALL)
    if match:
        thought = match.group(1).strip()
        clean_text = re.sub(r'<thinking>.*?</thinking>', '', text, flags=re.DOTALL).strip()
        return thought, clean_text
    return None, text

def query_openai(question, image_data=None):
    """Query OpenAI (Display: GPT-5.2)"""
    start_time = time.time()
    try:
        client = openai.OpenAI(api_key=OPENAI_API_KEY)
        system_prompt = "You are a helpful assistant. You MUST first think step-by-step about the user's request inside <thinking> tags, and then provide your final answer."
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
            max_tokens=1000
        )
        elapsed_time = time.time() - start_time
        full_content = response.choices[0].message.content
        thought, clean_content = extract_thought(full_content)
        cost = calculate_cost("gpt-4o", question, full_content)
        
        return {
            "success": True,
            "response": clean_content,
            "thought": thought,
            "time": round(elapsed_time, 2),
            "cost": cost,
            "model": "GPT-5.2" 
        }
    except Exception as e:
        elapsed_time = time.time() - start_time
        return {
            "success": False,
            "response": f"Error: {str(e)}",
            "time": round(elapsed_time, 2),
            "model": "GPT-5.2"
        }

def query_anthropic(question, image_data=None):
    """Query Anthropic (Display: Claude 4.5 Sonnet)"""
    start_time = time.time()
    system_content = "Think step-by-step inside <thinking> tags before answering."
    
    messages = []
    if image_data:
        messages.append({
            "role": "user",
            "content": [
                {"type": "image", "source": {"type": "base64", "media_type": "image/jpeg", "data": image_data}},
                {"type": "text", "text": question}
            ]
        })
    else:
        messages.append({"role": "user", "content": question})

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
                max_tokens=1000,
                system=system_content,
                messages=messages
            )
            full_content = response.content[0].text
            elapsed_time = time.time() - start_time
            thought, clean_content = extract_thought(full_content)
            cost = calculate_cost("claude-sonnet-4", question, full_content)
            
            return {
                "success": True,
                "response": clean_content,
                "thought": thought,
                "time": round(elapsed_time, 2),
                "cost": cost,
                "model": "Claude 4.5 Sonnet" 
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

def query_google(question, image_data=None):
    """Query Gemini using Legacy SDK (Display: Gemini 3.0)"""
    start_time = time.time()
    prompt_with_reasoning = f"Current User Question: {question}\n\nKey Instruction: First explain your reasoning step-by-step inside <thinking>...</thinking> tags, then provide the final answer."
    
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
            thought, clean_content = extract_thought(full_content)
            
            return {
                "success": True,
                "response": clean_content,
                "thought": thought,
                "time": round(elapsed_time, 2),
                "cost": 0,
                "model": "Gemini 3.0 Pro" # Display name
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

def query_perplexity(question, image_data=None):
    """Query Perplexity (Display: Perplexity Pro)"""
    if image_data:
        question += "\n[Note: The user uploaded an image that you cannot see. Do your best to answer based on the text description.]"
        
    start_time = time.time()
    url = "https://api.perplexity.ai/chat/completions"
    headers = {"Authorization": f"Bearer {PERPLEXITY_API_KEY}", "Content-Type": "application/json"}
    system_prompt = "You are a helpful AI. Please think step-by-step inside <thinking> tags before answering."
    
    models_to_try = ["sonar-pro", "sonar", "llama-3.1-sonar-small-128k-online"]
    
    for model_name in models_to_try:
        try:
            data = {
                "model": model_name,
                "messages": [{"role": "system", "content": system_prompt}, {"role": "user", "content": question}]
            }
            response = requests.post(url, json=data, headers=headers, timeout=30)
            response.raise_for_status()
            result = response.json()
            full_content = result['choices'][0]['message']['content']
            elapsed_time = time.time() - start_time
            thought, clean_content = extract_thought(full_content)
            cost = calculate_cost("perplexity", question, full_content)
            
            return {
                "success": True,
                "response": clean_content,
                "thought": thought,
                "time": round(elapsed_time, 2),
                "cost": cost,
                "model": "Perplexity Pro"
            }
        except:
            continue
            
    elapsed_time = time.time() - start_time
    return {
        "success": False,
        "response": "Error: Could not find working Perplexity model",
        "time": round(elapsed_time, 2),
        "model": "Perplexity Pro"
    }

@app.route('/')
def index():
    return render_template('index.html')

def generate_consensus(question, results):
    """Generate consensus using GPT-4o"""
    try:
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
            max_tokens=300
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
    else:
        question = request.form.get('question', '')
        file = request.files.get('file')
        if file:
            file_type, context, visual = process_file(file)
            if file_type == 'error': return jsonify({"error": context}), 400
            if file_type == 'text': question += f"\n\n{context}"
            if file_type == 'image': 
                image_data = visual
                question += f"\n\n{context}"

    if not question: return jsonify({"error": "No question"}), 400
    
    with ThreadPoolExecutor(max_workers=4) as executor:
        f1 = executor.submit(query_openai, question, image_data)
        f2 = executor.submit(query_anthropic, question, image_data)
        f3 = executor.submit(query_google, question, image_data)
        f4 = executor.submit(query_perplexity, question, image_data)
        
        r1, r2, r3, r4 = f1.result(), f2.result(), f3.result(), f4.result()
    
    # Check citations
    import re
    def has_cite(txt): return bool(re.search(r'\[\d+\]|http', txt))
    r1['has_citations'] = has_cite(r1['response'])
    r2['has_citations'] = has_cite(r2['response'])
    r3['has_citations'] = has_cite(r3['response'])
    r4['has_citations'] = has_cite(r4['response'])

    results_map = {"openai": r1, "anthropic": r2, "google": r3, "perplexity": r4}
    consensus = generate_consensus(question, results_map)
    
    try:
        cid = save_comparison(question, results_map)
    except:
        cid = None

    return jsonify({
        "results": results_map,
        "consensus": consensus,
        "comparison_id": cid
    })

# Routes for history/stats etc
@app.route('/api/history', methods=['GET'])
def get_history(): return jsonify(get_recent_comparisons(request.args.get('limit', 50, type=int)))

@app.route('/api/saved', methods=['GET'])
def get_saved(): return jsonify(get_saved_comparisons())

@app.route('/api/save/<int:comparison_id>', methods=['POST'])
def save_bookmark(comparison_id):
    mark_as_saved(comparison_id, (request.json or {}).get('tags', ''))
    return jsonify({"success": True})

@app.route('/api/stats', methods=['GET'])
def get_stats(): return jsonify(get_comparison_stats())

if __name__ == '__main__':
    app.run(debug=True, port=5000)
