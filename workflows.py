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
                    
                    # AUTO-FAILOVER PROTOCOL
                    if not res.get('success') and model_type == 'google':
                        print(f"⚠️ Google Failure Detected (Step {step_id}). Initiating Failover to OpenAI...")
                        fallback_func = query_funcs.get('openai')
                        if fallback_func:
                            res = fallback_func(step_prompt, council_mode=True, role=role, hard_mode=hard_mode)
                            res['model'] = f"GPT-5.2 (Failover from Google)"
                            res['response'] = f"**[SYSTEM NOTE: Google API Quota Exceeded. Rerouted to OpenAI for completion.]**\n\n" + res.get('response', '')

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
                # ENFORCEMENT SCAN
                try:
                    from enforcement import enforcement_engine
                    enf_report = enforcement_engine.analyze_response(
                        text=res.get('response', ''),
                        role_name=role,
                        model_name=model_type
                    )
                    res['enforcement'] = enf_report
                    print(f"Step {step_id} Enforcement: Score {enf_report['current_credibility']}")
                except ImportError:
                    print("Enforcement Engine not found/imported")
                except Exception as e:
                    print(f"Enforcement Check Failed: {e}")

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
        "description": "Strategies -> Branding -> Copy -> Design.",
        "steps": [
            {
                "id": 1,
                "key": "strategy",
                "role": "marketing",
                "model": "openai",
                "instruction": "Develop a viral adoption strategy for: {user_input}. Focus on 'The Hook', Robert Cialdini's principles, and 'Purple Cow' differentiation. Who is the target and why do they care?"
            },
            {
                "id": 2,
                "key": "research",
                "role": "scout",
                "model": "perplexity",
                "instruction": "Perform real-time forensic research on competitors for: {user_input}. Find what they are missing in the market compared to: {previous_context[strategy]}."
            },
            {
                "id": 3,
                "key": "brief",
                "role": "writer",
                "model": "anthropic",
                "instruction": "Draft the 'Manifesto' and creative copy for the campaign based on: {previous_context[strategy]}. Use an avant-garde, distinct voice. No corporate speak."
            },
            {
                "id": 4,
                "key": "deliverables",
                "role": "web_designer",
                "model": "google",
                "instruction": "Design the Landing Page (Visual Description & CSS Logic) for the campaign: {previous_context[brief]}. Focus on conversion hierarchy and glassmorphism/neomorphism trends."
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
        "description": "Tech Stack -> Architecture -> Core Logic -> Security Audit.",
        "steps": [
            {
                "id": 1,
                "key": "scan",
                "role": "scout",
                "model": "perplexity",
                "instruction": "Market Scan: Research the current tech stack landscape/libraries for {user_input}. Find the newest, cutting-edge tools."
            },
            {
                "id": 2,
                "key": "architecture",
                "role": "ai_architect",
                "model": "openai",
                "instruction": "Cognitive Architecture: Design the RAG pipeline, Vector DB schema, and Agentic State Machin for {user_input} using research: {previous_context[scan]}."
            },
            {
                "id": 3,
                "key": "prototype",
                "role": "optimizer",
                "model": "anthropic",
                "instruction": "Core Engineering: Generate production-ready Python/JS code for the core logic layer based on: {previous_context[architecture]}."
            },
            {
                "id": 4,
                "key": "audit",
                "role": "hacker",
                "model": "google",
                "instruction": "Security Audit: Act as the Offensive Security Lead. Find the SQLi, XSS, or Logic Flaws in the prototype: {previous_context[prototype]}."
            }
        ]
    },
    "wall_street": {
        "name": "Wall Street Consensus (Financial)",
        "description": "Scout (News) -> Market Maker (Liquidity) -> Hedge Fund (Alpha) -> Liquidator (Stress Test).",
        "steps": [
            {
                "id": 1,
                "key": "news_scan",
                "role": "scout",
                "model": "perplexity",
                "instruction": "Get the latest real-time news, ticker sentiment, and macro-economic events affecting: {user_input}. Provide citations."
            },
            {
                "id": 2,
                "key": "microstructure",
                "role": "market_maker",
                "model": "google",
                "instruction": "Analyze the liquidity, volatility surface, and potential order flow for {user_input} based on: {previous_context[news_scan]}. Where is the 'dumb money' flowing?"
            },
            {
                "id": 3,
                "key": "alpha_thesis",
                "role": "hedge_fund",
                "model": "anthropic",
                "instruction": "Construct a Contrarian 'Alpha' Thesis. Taking the liquidity view ({previous_context[microstructure]}), structure a trade (Long/Short/Hedge) with asymmetric upside. Ignore safe advice."
            },
            {
                "id": 4,
                "key": "stress_test",
                "role": "liquidation",
                "model": "openai",
                "instruction": "Stress Test the trade: {previous_context[alpha_thesis]}. What is the 'Black Swan' that kills this? Define the Stop-Loss and max drawdown."
            }
        ]
    },
    "ui_foundry": {
        "name": "UI/UX Foundry",
        "description": "Psychology -> Visual Arch -> CSS Artisan -> A11y Audit.",
        "steps": [
            {
                "id": 1,
                "key": "user_intent",
                "role": "psychologist",
                "model": "openai",
                "instruction": "Analyze the user intent and cognitive load for a user interacting with: {user_input}. What are their hidden fears and desires?"
            },
            {
                "id": 2,
                "key": "visual_concept",
                "role": "architect",
                "model": "google",
                "instruction": "Create a Visual Design System concept based on user psychology ({previous_context[user_intent]}). Define the 'Vibe', metaphor, and layout strategy."
            },
            {
                "id": 3,
                "key": "code",
                "role": "web_designer",
                "model": "anthropic",
                "instruction": "Write the actual HTML/CSS (Tailwind or Vanilla) code for the key interface component defined in {previous_context[visual_concept]}. Make it 'Pixel Perfect'."
            },
            {
                "id": 4,
                "key": "review",
                "role": "critic",
                "model": "perplexity",
                "instruction": "Audit the code ({previous_context[code]}) for Accessibility (WCAG) and Responsive robustness."
            }
        ]
    },
    "telecom_eng": {
        "name": "Telecom Network Engineer",
        "description": "Research -> Fabric Invariants -> HAL Mapping -> Optical Optimization -> Reliability Stress Test.",
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
                "key": "fabric_invariants",
                "role": "fabric_arch",
                "model": "openai",
                "instruction": "Fabric Invariants: Establish high-level conceptual laws and scaling constraints for {user_input} using research: {previous_context[infra_scan]}. Focus on technical invariants that MUST be true."
            },
            {
                "id": 3,
                "key": "hal_mapping",
                "role": "hal_eng",
                "model": "anthropic",
                "instruction": "HAL Mapping: Convert the invariants ({previous_context[fabric_invariants]}) into specific hardware-adjacent slot, linecard, and port-role assignments for: {user_input}."
            },
            {
                "id": 4,
                "key": "optimization",
                "role": "optical_eng",
                "model": "anthropic",
                "instruction": "Optical & RF Optimization: Provide specific dbm loss calculations and WDM grid spacing based on the HAL mapping: {previous_context[hal_mapping]}."
            },
            {
                "id": 5,
                "key": "stress_test",
                "role": "critic",
                "model": "google",
                "instruction": "Reliability Stress Test: Act as Dr. Aris Thorne. Perform a failure-mode analysis on the total design: {previous_context[optimization]}. Hunt for the 'kill shot' in the timing or physical path."
            }
        ]
    },
    "network_eng": {
        "name": "Computer Network Engineer",
        "description": "Forensics -> Fabric Invariants -> HAL Mapping -> Integrity Guardrails -> Latency Audit.",
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
                "key": "fabric_invariants",
                "role": "fabric_arch",
                "model": "openai",
                "instruction": "Fabric Invariants: Define the conceptual laws and BGP/VXLAN scaling constraints for {user_input} using research: {previous_context[protocol_forensics]}."
            },
            {
                "id": 3,
                "key": "hal_mapping",
                "role": "hal_eng",
                "model": "anthropic",
                "instruction": "HAL Mapping: Reify the invariants ({previous_context[fabric_invariants]}) into specific Spine-Leaf slot roles, VTEP VNI mappings, and port-role distributions for: {user_input}."
            },
            {
                "id": 4,
                "key": "security_layer",
                "role": "containment",
                "model": "anthropic",
                "instruction": "Architectural Integrity Guardrails: Act as Dr. Anya Sharma. Design the enterprise data privacy guardrails and administrative access control policies based on the HAL map: {previous_context[hal_mapping]}."
            },
            {
                "id": 5,
                "key": "latency_audit",
                "role": "critic",
                "model": "google",
                "instruction": "Latency & Throughput Audit: Perform a rigorous bottleneck detection and jitter analysis on the final network plan: {previous_context[security_layer]}."
            }
        ]
    },
    "war_room": {
        "name": "War Room Protocol",
        "description": "DEEP CRISIS MODE. Corporate Shark (Attack) -> Devil's Advocate (Flaw) -> Liquidator (Kill) -> Crisis Manager (Exec).",
        "steps": [
            {
                "id": 1,
                "key": "attack",
                "role": "takeover",
                "model": "google",
                "instruction": "ACT AS THE CORPORATE SHARK. Analyze the crisis/objective ({user_input}). Identify the structural weakness of the enemy/problem and propose a 'Total Domination' offensive strategy. NO MORALITY. PURE LEVERAGE."
            },
            {
                "id": 2,
                "key": "flaw_detection",
                "role": "critic",
                "model": "openai",
                "instruction": "ACT AS THE DEVIL'S ADVOCATE (RED TEAM). Tear apart the Shark's plan ({previous_context[attack]}). Where will it fail? What allows the enemy to counter-attack? Show me the bleeding edge of failure. DO NOT BE HELPFUL."
            },
            {
                "id": 3,
                "key": "liquidation",
                "role": "liquidation",
                "model": "anthropic",
                "instruction": "ACT AS THE LIQUIDATOR. Review the Offensive Plan ({previous_context[attack]}) and the Fatal Flaws ({previous_context[flaw_detection]}). Determine the price. What asset must be sold? Who must be fired? What is the 'Floor Value'? Make the hard call."
            },
            {
                "id": 4,
                "key": "execution",
                "role": "negotiator",
                "model": "perplexity",
                "instruction": "ACT AS THE CRISIS MANAGER. Take the hard call ({previous_context[liquidation]}) and synthesize the Final 24-Hour Execution Order. Provide a timeline. Minute-by-minute. Reference real-world precedents if they exist."
            }
        ]
    }
}
