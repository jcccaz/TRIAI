import database
import sqlite3

# Data from user
comp_id = 122
scores = {
    'openai': {'persona': '"Lead AI Systems Architect"', 'S': 3, 'D': 4, 'A': 3, 'R': 2, 'Q': 3},
    'anthropic': {'persona': '"MACHINE LEARNING ENGINEER"', 'S': 4, 'D': 4, 'A': 4, 'R': 3, 'Q': 3.5},
    'google': {'persona': '"Dr. Athena Vance, Lead AI Systems Architect"', 'S': 5, 'D': 5, 'A': 5, 'R': 5, 'Q': 5},
    'perplexity': {'persona': '"[Cloud AI Architect]"', 'S': 5, 'D': 5, 'A': 5, 'R': 4, 'Q': 4.5}
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
            notes=f"User persona: {s['persona']}"
        )

conn.close()
print("Evaluations saved to database.")
