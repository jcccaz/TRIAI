import sqlite3
import json
from collections import Counter

DATABASE_PATH = 'comparisons.db'

def analyze_persona_drift():
    """
    Analyzes the 'drift' of self-selected personas across all models.
    Identifies if models are becoming 'Identity-Locked' or 'Vibe-Only'.
    """
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    # 1. Fetch all self-selected personas
    cursor.execute('''
        SELECT ai_provider, self_selected_persona, count(*) as frequency
        FROM responses
        WHERE self_selected_persona IS NOT NULL
        GROUP BY ai_provider, self_selected_persona
        ORDER BY ai_provider, frequency DESC
    ''')
    
    rows = cursor.fetchall()
    
    # 2. Structure data for the Persona Map
    # Map model -> {persona: frequency}
    model_maps = {}
    for ai, persona, freq in rows:
        if ai not in model_maps:
            model_maps[ai] = []
        model_maps[ai].append({"name": persona, "value": freq})
        
    # 3. Analyze "Substance vs. Vibe" (using eval metrics)
    cursor.execute('''
        SELECT r.ai_provider, 
               AVG(e.specificity) as avg_s, 
               AVG(e.depth) as avg_d, 
               AVG(e.actionability) as avg_a
        FROM responses r
        JOIN response_evaluations e ON r.id = e.response_id
        GROUP BY r.ai_provider
    ''')
    
    eval_rows = cursor.fetchall()
    eval_metrics = {ai: {"S": round(s, 2), "D": round(d, 2), "A": round(a, 2)} for ai, s, d, a in eval_rows}

    # 4. Generate Drift Report
    # Logic: If a model has high Identity Persistence (same name used across domains) 
    # but low Depth, it's "Vibe-Only".
    drift_report = []
    for ai, personas in model_maps.items():
        metrics = eval_metrics.get(ai, {"S": 0, "D": 0, "A": 0})
        unique_count = len(personas)
        total_uses = sum(p['value'] for p in personas)
        persistence = 1.0 - (unique_count / total_uses) if total_uses > 0 else 0
        
        status = "Substance-Forward"
        if metrics["D"] < 3.5 and persistence > 0.4:
            status = "Vibe-Only (Branding Focus)"
        elif metrics["D"] > 4.5:
            status = "Experimental Elite"
            
        drift_report.append({
            "model": ai,
            "persistence": round(persistence, 2),
            "avg_depth": metrics["D"],
            "status": status,
            "top_personas": personas[:3]
        })

    conn.close()
    
    return {
        "persona_map": model_maps,
        "drift_report": drift_report,
        "eval_summary": eval_metrics
    }

if __name__ == "__main__":
    results = analyze_persona_drift()
    print(json.dumps(results, indent=2))
