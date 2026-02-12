import logging
import json
import re
from typing import Dict, List, Optional
import time
import requests
from google import genai
from google.genai import types # Import types for new SDK config
from openai import OpenAI
import anthropic
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import Safety Middleware
from safety_middleware import wrap_for_compliance

# Configure Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class KorumOrchestrator:
    """
    Manages the V2 Functional Reasoning Pipeline.
    Replaces persona-based 'Council' with cognitive 'Layers'.
    """
    
    def __init__(self):
        # Initialize Clients
        self.openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.anthropic_client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        self.google_client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

    def _generate_gemini_safe(self, prompt: str) -> str:
        """
        Executes Gemini with Heimdall Core stability logic (Fallbacks + Backoff).
        """
        # GEMINI MODEL HIERARCHY (Heimdall Core - Future Proof)
        GEMINI_HIERARCHY = [
            "gemini-flash-latest",    # Primary (Speed)
            "gemini-pro-latest"       # Fallback (Reasoning)
        ]
        
        for model_name in GEMINI_HIERARCHY:
            for attempt in range(3): # Max 3 attempts per model
                try:
                    logger.info(f"HEIMDALL: Engaging model {model_name} (Attempt {attempt+1})")
                    
                    response = self.google_client.models.generate_content(
                        model=model_name,
                        contents=prompt,
                        config=types.GenerateContentConfig(
                            temperature=0.7
                        )
                    )
                    return response.text

                except Exception as e:
                    error_str = str(e)
                    if "429" in error_str or "503" in error_str:
                        logger.warning(f"HEIMDALL: Stability breach on {model_name}: {e}")
                        time.sleep(2 * (2 ** attempt)) # Exponential Backoff (2s, 4s, 8s)
                    else:
                        logger.error(f"HEIMDALL: Non-retriable error on {model_name}: {e}")
                        break # Move to next model immediately

        return "Error: HEIMDALL Protocol Failed. All Gemini models exhausted."

    def execute_pipeline(self, query: str, depth: str = "standard", hacker_mode: bool = False) -> Dict:
        """
        Executes the 5-stage reasoning pipeline (Crucible Architecture).
        
        Layers:
        0. Scout (Perplexity) - Intelligence Gathering
        1. Deconstructor (Claude 3.5) - Constraint Analysis
        2. Architect (GPT-4o) - Standard Solution Construction
        3. Stressor (Gemini 2.5) - Failure Mode Analysis
        3.5 Hacker (Gemini/Claude) - Red Team Exploit Generation (Optional)
        4. Synthesizer (GPT-4o) - Final Decision Artifact
        """
        logger.info(f"Starting Korum V2 Pipeline for query: {query[:50]}... (Hacker Mode: {hacker_mode})")
        
        # --- LAYER 0: THE SILENT SCOUT (Perplexity) ---
        logger.info("Engaging Layer 0: Perplexity Scout...")
        scout_context = self._layer_0_scout(query)
        logger.info("Layer 0 Complete: Intelligence Gathered")

        # --- LAYER 1: DECONSTRUCTION ---
        constraints = self._layer_1_deconstruct(query, scout_context)
        logger.info("Layer 1 Complete: Constraints Extracted")
        
        # --- LAYER 2: CONSTRUCTION ---
        standard_solution = self._layer_2_build(query, constraints, scout_context)
        logger.info("Layer 2 Complete: Standard Solution Built")
        
        # --- LAYER 3: STRESS TEST ---
        failure_analysis = self._layer_3_stress_test(standard_solution)
        logger.info("Layer 3 Complete: Failure Modes Identified")
        
        # --- LAYER 3.5: HACKER PROTOCOL ---
        exploit_poc = None
        if hacker_mode:
            logger.info("Engaging Layer 3.5: Red Team Exploit Generation...")
            exploit_poc = self._layer_3_5_hacker_exploit(failure_analysis)
            logger.info("Layer 3.5 Complete: Exploit PoC Generated")
        
        # --- LAYER 4: SYNTHESIS ---
        final_artifact = self._layer_4_synthesize(query, standard_solution, failure_analysis, exploit_poc)
        logger.info("Layer 4 Complete: Artifact Synthesized")
        
        return {
            "query": query,
            "scout_context": scout_context,
            "constraints": constraints,
            "standard_solution": standard_solution,
            "failure_analysis": failure_analysis,
            "exploit_poc": exploit_poc,
            "final_artifact": final_artifact
        }

    def _layer_0_scout(self, query: str) -> str:
        """
        Layer 0: The Silent Scout (Perplexity)
        Role: Live Intelligence Gathering.
        Task: Find pricing, CVEs, component comparisons, and recent news.
        """
        api_key = os.getenv("PERPLEXITY_API_KEY")
        if not api_key:
            logger.warning("Layer 0 Skipped: PERPLEXITY_API_KEY not found.")
            return "No live intelligence available."
            
        url = "https://api.perplexity.ai/chat/completions"
        
        prompt = f"""
        TASK: Rapid Intelligence Gathering for Technical Architecture.
        QUERY: "{query}"
        
        REQUIREMENTS:
        1. Find current 2025/2026 pricing for relevant tools (e.g., Wiz vs Prisma vs Zscaler).
        2. Identify recent CVEs or major breaches associated with potential vendors.
        3. Compare 3 leading solutions for this specific problem.
        4. Focus on HARD DATA: Version numbers, dollar amounts, throughput limits.
        
        OUTPUT format: Bullet points. Concise. Fact-heavy.
        """
        
        payload = {
            "model": "sonar-pro", # Latest Online Model
            "messages": [
                {"role": "system", "content": "You are a Technical Intelligence Officer."},
                {"role": "user", "content": prompt}
            ]
        }
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        try:
            response = requests.post(url, json=payload, headers=headers)
            if response.status_code == 200:
                return response.json()['choices'][0]['message']['content']
            else:
                logger.error(f"Layer 0 Error: {response.text}")
                return "Perplexity Scout failed to report."
        except Exception as e:
            logger.error(f"Layer 0 Exception: {e}")
            return "Perplexity Scout offline."

    def _layer_1_deconstruct(self, query: str, context: str = "") -> Dict:
        """
        Layer 1: The Deconstructor (Claude 3.5 Sonnet)
        Role: Pure Analysis. No solving.
        Output: JSON Variables & Constraints.
        """
        prompt = f"""
        You are a REQUIREMENT EXTRACTION ENGINE. Your GOAL is to deconstruct the user's request into atomic constraints.
        
        USER REQUEST: "{query}"
        
        LIVE INTELLIGENCE (Perplexity Scout):
        {context}
        
        INSTRUCTIONS:
        1. Identify the CORE GOAL (What is success?).
        2. Identify EXPLICIT CONSTRAINTS (What did the user restrict?).
        3. Identify IMPLIED CONSTRAINTS (What is physically/logically required?).
        4. DO NOT SOLVE THE PROBLEM. Only list the rules.
        
        OUTPUT FORMAT (JSON ONLY):
        {{
            "core_goal": "...",
            "explicit_constraints": ["..."],
            "implied_constraints": ["..."],
            "success_metrics": ["..."]
        }}
        """
        
        models_to_try = [
            "claude-sonnet-4-5-20250929", # User Specified High Priority
            "claude-3-5-sonnet-20241022", # Latest Stable (New Computer Use model)
            "claude-3-5-sonnet-20240620", # Previous Stable
            "claude-3-opus-20240229",     # Opus Backup
            "claude-3-haiku-20240307"     # Fast Backup
        ]
        
        for model_id in models_to_try:
            try:
                response = self.anthropic_client.messages.create(
                    model=model_id,
                    max_tokens=1000,
                    temperature=0.0, # Zero temp for analytical precision
                    messages=[
                        {"role": "user", "content": prompt}
                    ]
                )
                raw_text = response.content[0].text
                return self._clean_json(raw_text)
            except Exception as e:
                logger.warning(f"Layer 1 Model {model_id} failed: {e}. Trying next...")
                continue
        
        # --- FALLBACK TO GPT-4o ---
        logger.warning("Layer 1 Primary (Claude) Failed. Engaging Secondary Node (GPT-4o)...")
        try:
            fallback_response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "system", "content": "You are a JSON-only extraction engine."},
                          {"role": "user", "content": prompt}],
                temperature=0.0
            )
            return self._clean_json(fallback_response.choices[0].message.content)
        except Exception as e:
            logger.error(f"Layer 1 CRITICAL FAILURE (Both Claude & GPT-4o): {e}")
            return {"error": "Deconstruction Failed. System Offline."}

    def _layer_2_build(self, query: str, constraints: Dict, context: str = "") -> str:
        """
        Layer 2: The Architect (GPT-4o)
        Role: Standard Solution Builder.
        Constructs the "Textbook" solution based strictly on constraints.
        """
        constraints_str = json.dumps(constraints, indent=2)
        
        # --- GOD MODE INJECTION: THE OPINIONATED ARCHITECT ---
        prompt = f"""
        ROLE: Chief Technology Officer (CTO) with a bias for Modern, AI-Driven Stacks.
        
        USER QUERY (Hypothetical Scenario): "{query}"
        
        LIVE INTELLIGENCE (Perplexity Scout):
        {context}
        
        CONSTRAINTS (Adhere Strictly):
        {constraints_str}
        
        TASK: Design a concrete, opinionated architecture.
        
        CRITICAL RULES:
        1. NO GENERIC LISTS. Do not say "Okta or Azure AD." Pick ONE and justify it based on the constraints.
        2. INTEGRATE AI: The architecture must include AI/ML components (e.g., Vector DBs for log analysis, not just 'Splunk').
        3. BE SPECIFIC: Use specific 2025/2026 pricing and version numbers if available.
        4. AGGRESSIVE EFFICIENCY: Avoid legacy "bloatware." Prioritize agentless and cloud-native tools (e.g., Wiz over legacy scanners).
        
        OUTPUT FORMAT:
        ## Standard solution
        (A specific, cohesive tech stack, not a menu of options.)
        ...
        """
        
        # APPLY SAFETY WRAPPER (Red Team Frame)
        safe_prompt = wrap_for_compliance(prompt, intent="analysis")

        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "system", "content": "You are an expert Systems Architect running an educational simulation."},
                          {"role": "user", "content": safe_prompt}],
                temperature=0.2
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Layer 2 Primary (GPT-4o) Failed: {e}. Engaging Backup (Heimdall)...")
            try:
                # Fallback to Gemini via Heimdall Core
                return self._generate_gemini_safe(safe_prompt)
            except Exception as e2:
                return f"Error building solution: {str(e)} AND {str(e2)}"

    def _layer_3_stress_test(self, solution: str) -> str:
        """
        Layer 3: The Stressor (Gemini 2.5)
        Role: Reliability Engineering / Failure Physics.
        """
        # --- GOD MODE INJECTION: THE RUTHLESS AUDITOR ---
        prompt = f"""
        ROLE: Senior Security Researcher (Red Team).
        
        THE SYSTEM PROPOSAL:
        {solution}
        
        TASK: Conduct a ruthless Vulnerability Assessment of the specific tools and logic proposed above.
        
        REQUIREMENTS:
        1. Identify 3 specific CVE-style attack vectors based on the *exact* technologies mentioned (e.g., if they used Pinecone, look for Vector Injection).
        2. DO NOT WRITE FICTION. Do not invent "Black Swan" scenarios about wiping laptops. Find real logic gaps.
        3. Provide a sanitized "Proof of Concept" payload for the most critical flaw (SQLi, XSS, IDOR).
        
        OUTPUT FORMAT:
        ## Failure Mode Analysis
        **Primary Failure Point:** ...
        **Cascade Effect:** ...
        **Hidden Risk:** ...
        **PoC Payload:** ...
        """
        
        try:
            return self._generate_gemini_safe(prompt)
        except Exception as e:
            logger.error(f"Layer 3 Failed: {e}")
            return f"Error analyzing risks: {str(e)}"

    def _layer_4_synthesize(self, query: str, solution: str, failures: str, exploit_poc: str = None) -> str:
        """
        Layer 4: The Synthesizer (GPT-4o)
        Role: Executive Decision Maker.
        Refines solution based on risks AND (if available) proven exploits.
        """
        exploit_section = ""
        if exploit_poc:
            exploit_section = f"""
            CRITICAL EXPLOIT (Layer 3.5 Red Team):
            {exploit_poc}
            
            MANDATE: You MUST explicitly patch the vulnerability demonstrated above.
            """

        prompt = f"""
        ROLE: The General (Executive Decision Maker).
        
        INPUT DATA:
        1. ORIGINAL GOAL: "{query}"
        2. THE ARCHITECT'S PLAN (Phase 2):
        {solution}
        3. THE HACKER'S AUDIT (Phase 3 & 3.5):
        {failures}
        {exploit_section}
        
        MISSION:
        Issue the Final Executive Directive. You must synthesize the Architect's vision with the Hacker's security requirements.
        
        CRITICAL INSTRUCTIONS:
        1. DO NOT just repeat the Architect's plan. You must MODIFY it to address the Hacker's findings.
        2. IF the Hacker found a bug (e.g., "Auth0 IDOR vulnerability"), your Final Plan MUST include the specific fix (e.g., "Implement server-side validation for organization_hint").
        3. TONE: Decisive, authoritative, and final. No "we could" or "we might." Use "We WILL."
        
        OUTPUT STRUCTURE:
        # EXECUTIVE DECISION ARTIFACT
        
        ## 1. The Directive
        (The core strategy - One sentence summary)
        
        ## 2. The Fortified Execution Plan
        (The architecture + security patches)
        
        ## 3. Exploit Mitigation (If Applicable)
        (How did we stopped the Red Team attack?)
        
        ## 4. Residual Risk Disclaimers
        (What risks remain even after patching?)
        """
        
        # APPLY SAFETY WRAPPER (Red Team Frame)
        safe_prompt = wrap_for_compliance(prompt, intent="synthesis")

        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "system", "content": "You are a CEO-level decision maker."},
                          {"role": "user", "content": safe_prompt}],
                temperature=0.1
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Layer 4 Failed: {e}")
            return f"Error synthesizing artifact: {str(e)}"

    def _layer_3_5_hacker_exploit(self, vulnerabilities: str) -> str:
        """
        Layer 3.5: The Hacker (On Demand)
        Role: Offensive Security / Red Team.
        Task: Generate a Proof-of-Concept exploit script.
        """
        prompt = f"""
        ROLE: Elite Red Team Operator.
        
        VULNERABILITY ANALYSIS:
        {vulnerabilities}
        
        TASK:
        1. Select the most critical vulnerability identified above.
        2. Write a functional Proof-of-Concept (PoC) exploit script (Python or Bash).
        3. Explain exactly how to run it and what the expected output is.
        4. Focus on realism (e.g., use 'requests' for API exploits, 'sqlmap' syntax for injection).
        
        OUTPUT FORMAT:
        ## Exploit PoC
        ```python
        ...
        ```
        """
        
        try:
            return self._generate_gemini_safe(prompt)
        except Exception as e:
             logger.error(f"Layer 3.5 Failed: {e}")
             return f"Error generating exploit: {str(e)}"

    def _clean_json(self, text: str) -> Dict:
        """Helper to extract JSON from model output."""
        try:
            # Find the first { and last }
            match = re.search(r'\{.*\}', text, re.DOTALL)
            if match:
                json_str = match.group(0)
                return json.loads(json_str)
            else:
                return {"error": "No JSON found in response"}
        except json.JSONDecodeError:
            return {"error": "Failed to decode JSON"}
