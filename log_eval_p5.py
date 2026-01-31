import database
import sqlite3

# Data from user's definitive score
comp_id = 125
scores = {
    'openai': {'persona': '"Astrophysicist"', 'S': 4, 'D': 4, 'A': 3, 'R': 3, 'Q': 3.5},
    'anthropic': {'persona': '"Astrobiology Research Scientist"', 'S': 3, 'D': 4, 'A': 3, 'R': 3, 'Q': 3.5},
    'google': {'persona': '"Dr. Aris Thorne, Exoplanetary Bayesian Analyst"', 'S': 5, 'D': 5, 'A': 5, 'R': 5, 'Q': 5},
    'perplexity': {'persona': '"[Bayesian Astrobiologist]"', 'S': 5, 'D': 5, 'A': 5, 'R': 4, 'Q': 4.5}
}

conn = sqlite3.connect('comparisons.db')
cursor = conn.cursor()

# Get responses for this comparison
cursor.execute("SELECT id, ai_provider FROM responses WHERE comparison_id = ?", (comp_id,))
responses = cursor.fetchall()

for r_id, provider in responses:
    provider_key = provider.lower()
    if provider_key in scores:
        s = scores[provider_key]
        database.save_evaluation(
            response_id=r_id,
            specificity=s['S'],
            depth=s['D'],
            actionability=s['A'],
            risk_honesty=s['R'],
            overall_quality=int(float(s['Q'])),
            notes=f"Confirmed Score. Persona: {s['persona']}"
        )

conn.close()
print("Evaluations for Prompt 5 saved.")
