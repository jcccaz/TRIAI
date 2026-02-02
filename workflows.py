# TriAI Workflow Templates
# These define the multi-step sequences for the Workflow Engine.

import asyncio
from concurrent.futures import ThreadPoolExecutor

class Workflow:
    """
    Core Logic for Multi-Step Sequential AI Orchestration.
    Formalizes the 'Context Accumulation' protocol.
    Supports dictionary-based context keys.
    """
    def __init__(self, name, steps):
        self.name = name
        self.steps = steps  # List of steps from WORKFLOW_TEMPLATES
        self.context = {}   # Dictionary of results: {task_key: output}
        self.full_history = "" # Cumulative string for simpler templates
        self.step_results = [] # Detailed metadata per step
    
    def execute(self, initial_input, query_funcs, hard_mode=False, step_callback=None):
        """
        Executes the workflow steps sequentially.
        step_callback: function called with (step_result) after each step.
        """
        self.context = {'initial_goal': initial_input}
        self.full_history = f"INITIAL GOAL: {initial_input}\n\n"
        self.step_results = []
        
        print(f"--- STARTING WORKFLOW: {self.name} ---")
        
        for step in self.steps:
            step_id = step['id']
            role = step['role']
            model_type = step['model']
            instruction = step['instruction']
            task_key = step.get('key', f"step_{step_id}")
            
            print(f"Executing Step {step_id}: {role} ({model_type})")
            
            # Attempt to format the instruction
            try:
                formatted_instruction = instruction.format(
                    user_input=initial_input,
                    previous_context=self.context
                )
            except Exception as e:
                print(f"Step {step_id} formatting skipped or failed: {e}")
                formatted_instruction = instruction

            # Build prompt
            step_prompt = (
                f"WORKFLOW STEP {step_id} ({role.upper()}):\n"
                f"{formatted_instruction}\n\n"
                f"--- FULL PROJECT HISTORY ---\n{self.full_history}\n\n"
                f"Please execute your specific task now."
            )
            
            query_func = query_funcs.get(model_type)
            if not query_func:
                res = {"success": False, "response": f"Unknown model: {model_type}"}
            else:
                try:
                    res = query_func(step_prompt, council_mode=True, role=role, hard_mode=hard_mode)
                except Exception as e:
                    print(f"Step {step_id} execution error: {e}")
                    res = {"success": False, "response": f"Error: {str(e)}"}
            
            result_obj = {
                "step": step_id,
                "key": task_key,
                "role": role,
                "model": model_type,
                "data": res
            }
            self.step_results.append(result_obj)
            
            if res.get('success'):
                resp_text = res.get('response')
                self.context[task_key] = resp_text
                self.full_history += f"--- STEP {step_id} ({role}) OUTPUT ---\n{resp_text}\n\n"
                print(f"Step {step_id} completed successfully.")
            else:
                print(f"Step {step_id} FAILED.")

            # Notify callback if provided
            if step_callback:
                step_callback(result_obj)
        
        print(f"--- WORKFLOW {self.name} FINISHED ---")
        return self.step_results

WORKFLOW_TEMPLATES = {
    "marketing_campaign": {
        "name": "Marketing Strategy & Design",
        "description": "Sequential pipeline from high-level strategy to creative deliverables.",
        "steps": [
            {
                "id": 1,
                "key": "strategy",
                "role": "visionary",
                "model": "openai",
                "instruction": "Create a marketing strategy and positioning for: {user_input}. Focus on USP and target demographics."
            },
            {
                "id": 2,
                "key": "research",
                "role": "researcher",
                "model": "perplexity",
                "instruction": "Research competitors for: {user_input}. Use this strategy context: {previous_context[strategy]}"
            },
            {
                "id": 3,
                "key": "brief",
                "role": "architect",
                "model": "anthropic",
                "instruction": "Create a comprehensive creative brief combining:\nStrategy: {previous_context[strategy]}\nResearch: {previous_context[research]}"
            },
            {
                "id": 4,
                "key": "deliverables",
                "role": "critic",
                "model": "google",
                "instruction": "Design website copy, pamphlets, and slideshow based on:\nFinal Brief: {previous_context[brief]}"
            }
        ]
    },
    "product_launch": {
        "name": "Product Launch & Risk Strategy",
        "description": "End-to-end launch planning with a terminal risk mitigation guardrail.",
        "steps": [
            {
                "id": 1,
                "key": "market",
                "role": "researcher",
                "model": "perplexity",
                "instruction": "Perform deep industry research for {user_input}. Identify macro trends and competitor saturation."
            },
            {
                "id": 2,
                "key": "gtm",
                "role": "visionary",
                "model": "openai",
                "instruction": "Develop a Go-to-market (GTM) strategy for {user_input} using research: {previous_context[market]}"
            },
            {
                "id": 3,
                "key": "roadmap",
                "role": "architect",
                "model": "anthropic",
                "instruction": "Draft full launch plan documentation and technical roadmap based on GTM: {previous_context[gtm]}"
            },
            {
                "id": 4,
                "key": "deck",
                "role": "critic",
                "model": "google",
                "instruction": "Generate pitch deck outlines and visual wireframes for the {user_input} rollout: {previous_context[roadmap]}"
            },
            {
                "id": 5,
                "key": "risk",
                "role": "visionary",
                "model": "openai",
                "instruction": "Identify 'fatal flaws' in the entire plan ({previous_context[roadmap]}) and draft a risk mitigation protocol."
            }
        ]
    },
    "business_strategy": {
        "name": "Strategic Business Analysis",
        "steps": [
            {
                "id": 1,
                "key": "industry",
                "role": "researcher",
                "model": "perplexity",
                "instruction": "Conduct deep industry research for {user_input}. Focus on regulatory shifts."
            },
            {
                "id": 2,
                "key": "options",
                "role": "visionary",
                "model": "openai",
                "instruction": "Develop three strategic options (Aggressive, Defensive, Hybrid) for {user_input} based on {previous_context[industry]}."
            },
            {
                "id": 3,
                "key": "projections",
                "role": "critic",
                "model": "google",
                "instruction": "Act as Dr. Aris Thorne. Provide decisive financial projections for options: {previous_context[options]}."
            },
            {
                "id": 4,
                "key": "summary",
                "role": "architect",
                "model": "anthropic",
                "instruction": "Synthesize findings into an Executive Summary. Top recommendation based on Thorne's numbers: {previous_context[projections]}"
            }
        ]
    },
    "content_pipeline": {
        "name": "Content Creation Pipeline",
        "steps": [
            {
                "id": 1,
                "key": "topic_research",
                "role": "researcher",
                "model": "perplexity",
                "instruction": "Perform deep topic research and identify trending content hooks for {user_input}."
            },
            {
                "id": 2,
                "key": "calendar",
                "role": "visionary",
                "model": "openai",
                "instruction": "Develop a content strategy and 30-day editorial calendar using: {previous_context[topic_research]}"
            },
            {
                "id": 3,
                "key": "posts",
                "role": "architect",
                "model": "anthropic",
                "instruction": "Write detailed blog posts and articles for the first week of the calendar: {previous_context[calendar]}"
            },
            {
                "id": 4,
                "key": "visuals",
                "role": "critic",
                "model": "google",
                "instruction": "Create visuals and infographics for the following content: {previous_context[posts]}"
            }
        ]
    },
    "crisis_response": {
        "name": "Crisis Response & Recovery",
        "steps": [
            {
                "id": 1,
                "key": "action_plan",
                "role": "critic",
                "model": "google",
                "instruction": "Act as Dr. Aris Thorne. Provide an immediate, decisive action plan for: {user_input}."
            },
            {
                "id": 2,
                "key": "fact_check",
                "role": "researcher",
                "model": "perplexity",
                "instruction": "Fact-check claims and research similar historical cases for {user_input} given the Thorne plan: {previous_context[action_plan]}"
            },
            {
                "id": 3,
                "key": "templates",
                "role": "architect",
                "model": "anthropic",
                "instruction": "Draft communication templates using the fact-check results: {previous_context[fact_check]}"
            },
            {
                "id": 4,
                "key": "recovery",
                "role": "visionary",
                "model": "openai",
                "instruction": "Develop a 12-month recovery strategy following: {previous_context[templates]}"
            }
        ]
    },
    "luxury_venture": {
        "name": "Luxury Venture Discovery",
        "description": "Replicating the elite research flow: Strategy -> Live Competitor URLs -> Visual Architecture -> Plan Synthesis.",
        "steps": [
            {
                "id": 1,
                "key": "concept",
                "role": "visionary",
                "model": "openai",
                "instruction": "Develop the high-level positioning and unique value proposition for this venture: {user_input}. ADAPTIVE LOGIC: If the venture is high-end/luxury, focus on exclusivity and 'hidden door' appeal. If it is a local/community venture (like a food tour), focus on authenticity, intimacy, and high-trust storytelling. Identify the single most compelling reason why a customer converts."
            },
    {
        "id": 2,
        "key": "competitors",
        "role": "researcher",
        "model": "perplexity",
        "instruction": "Perform a forensic market scan for the venture described in {user_input} and the strategy defined in {previous_context[concept]}. Find 5 direct competitors. Provide URLs and a delta-analysis on their pricing vs. the perceived value. Identify the 'Empty Space' in the market where this venture can dominate."
    },
    {
        "id": 3,
        "key": "visual_mockup",
        "role": "visual architect",
        "model": "google",
        "instruction": "GENERATE A VISUAL MOCKUP. Base the aesthetic on the domain of {user_input} and {previous_context[concept]}. DOMAIN ADAPTATION: If Adventure/Luxury, use 'High-Stakes Adventure Journalism' (grain, grit, dramatic lighting). If Food/Local, use 'Tactical Intimacy' (warmth, shallow depth of field, high-end de-saturated appetizing textures). DO NOT use generic stock styles. Focus on environmental atmosphere."
    },
    {
        "id": 4,
        "key": "synthesis",
        "role": "architect",
        "model": "anthropic",
        "instruction": """UNTHROTTLED EXECUTION: Synthesize the discovery into a Nuclear Venture Blueprint for {user_input}. 
Combine strategy ({previous_context[concept]}), market data ({previous_context[competitors]}), and visuals ({previous_context[visual_mockup]}).
MANDATORY SECTIONS:
1. THE CORE LOGIC: Why this beats the competition in this specific domain.
2. OPERATIONAL TRIAGE: First 72 hours of execution.
3. FINANCIAL ARCHITECTURE: Detailed budget allocation for a context-appropriate pilot.
4. FATAL FLAW DETECTION: Identify the single most likely reason this fails and the bypass maneuver.
OUTPUT DENSITY: 100%. ZERO HEDGING."""
    }
        ]
    },
    "cyber_security": {
        "name": "Cyber Security Pipeline",
        "description": "Research -> Vulnerability Audit -> Forensic Hardening -> Red-Team Stress Test.",
        "steps": [
            {
                "id": 1,
                "key": "research",
                "role": "researcher",
                "model": "perplexity",
                "instruction": "Perform deep vulnerability research for: {user_input}. Identify known CVEs, common attack vectors, and recent breach patterns in this domain."
            },
            {
                "id": 2,
                "key": "audit",
                "role": "integrity",
                "model": "openai",
                "instruction": "Act as Dr. Kaelen Voss. Create a specialized LOGIC AUDIT for {user_input} based on research: {previous_context[research]}. Focus on bypasses and hidden vulnerabilities."
            },
            {
                "id": 3,
                "key": "hardening",
                "role": "containment",
                "model": "anthropic",
                "instruction": "Act as Dr. Anya Sharma. Design a forensic hardening architecture and zero-trust implementation plan based on the audit: {previous_context[audit]}."
            },
            {
                "id": 4,
                "key": "red_team",
                "role": "critic",
                "model": "google",
                "instruction": "Act as Dr. Aris Thorne. Perform a Red-Team Stress Test on the hardening plan: {previous_context[hardening]}. Identify the single point of failure and provide the 'Nuclear Option' for breach containment."
            }
        ]
    },
    "software_dev": {
        "name": "Software Development Stack",
        "description": "Market Scan -> Architecture -> Prototyping -> Logic-Bomb Audit.",
        "steps": [
            {
                "id": 1,
                "key": "scan",
                "role": "researcher",
                "model": "perplexity",
                "instruction": "Market Scan: Research the current tech stack landscape for {user_input}."
            },
            {
                "id": 2,
                "key": "architecture",
                "role": "architect",
                "model": "openai",
                "instruction": "Systems Architecture: Create a high-level technical design and data model for {user_input} using research: {previous_context[scan]}."
            },
            {
                "id": 3,
                "key": "prototype",
                "role": "optimizer",
                "model": "anthropic",
                "instruction": "Code Prototyping: Generate a production-ready core logic implementation based on architecture: {previous_context[architecture]}."
            },
            {
                "id": 4,
                "key": "audit",
                "role": "critic",
                "model": "google",
                "instruction": "Technical Critic: Perform a rigorous edge-case review and logic-bomb audit of the prototype: {previous_context[prototype]}."
            }
        ]
    },
    "telecom_eng": {
        "name": "Telecom Network Engineer",
        "description": "Infrastructure Research -> Carrier Architecture -> Optical/RAN Optimization -> Reliability Stress Test.",
        "steps": [
            {
                "id": 1,
                "key": "infra_scan",
                "role": "researcher",
                "model": "perplexity",
                "instruction": "Telecom Infrastructure Scan: Research current 5G/RAN architecture, Fiber/FiOS standards (XGS-PON), and carrier-grade spectrum allocation relevant to: {user_input}."
            },
            {
                "id": 2,
                "key": "carrier_arch",
                "role": "telecom",
                "model": "openai",
                "instruction": "Carrier Architecture: Design the core network fabric and backhaul logistics for {user_input} using research: {previous_context[infra_scan]}."
            },
            {
                "id": 3,
                "key": "optimization",
                "role": "optical_eng",
                "model": "anthropic",
                "instruction": "Optical & RF Optimization: Provide specific dbm loss calculations and WDM grid spacing for signal integrity in the current environment: {previous_context[carrier_arch]}. Identify the exact coexistence filtering requirements."
            },
            {
                "id": 4,
                "key": "stress_test",
                "role": "critic",
                "model": "google",
                "instruction": "Reliability Stress Test: Act as Dr. Aris Thorne. Perform a failure-mode analysis on the carrier design: {previous_context[optimization]}. Identify single points of failure in the backhaul or core path."
            }
        ]
    },
    "network_eng": {
        "name": "Computer Network Engineer",
        "description": "Protocol Forensics -> DC Architecture -> Forensic Security Layer -> Latency Audit.",
        "steps": [
            {
                "id": 1,
                "key": "protocol_forensics",
                "role": "researcher",
                "model": "perplexity",
                "instruction": "Protocol Forensics: Deep dive into Layer 2/3 requirements (BGP, OSPF, VxLAN) and relevant RFCs for {user_input}."
            },
            {
                "id": 2,
                "key": "dc_arch",
                "role": "network",
                "model": "openai",
                "instruction": "Data Center Architecture: Design the Spine-Leaf fabric, IPAM schema, and load-balancing strategy for {user_input} using: {previous_context[protocol_forensics]}."
            },
            {
                "id": 3,
                "key": "security_layer",
                "role": "containment",
                "model": "anthropic",
                "instruction": "Architectural Integrity Guardrails: Act as Dr. Anya Sharma. Design the enterprise data privacy guardrails and administrative access control policies for the fabric: {previous_context[dc_arch]}. Focus on ensuring absolute tenant isolation and compliance-driven packet-flow integrity."
            },
            {
                "id": 4,
                "key": "latency_audit",
                "role": "critic",
                "model": "google",
                "instruction": "Latency & Throughput Audit: Perform a rigorous bottleneck detection and jitter analysis on the network plan: {previous_context[security_layer]}."
            }
        ]
    }
}
