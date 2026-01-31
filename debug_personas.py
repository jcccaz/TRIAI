
import sqlite3
conn = sqlite3.connect('comparisons.db')
cursor = conn.cursor()
cursor.execute("SELECT ai_provider, model_name, SUBSTR(response_text, 1, 200) FROM responses ORDER BY timestamp DESC LIMIT 4")
results = cursor.fetchall()
for provider, model, intro in results:
    print(f"PROVIDER: {provider}")
    print(f"MODEL/PERSONA: {model}")
    print(f"INTRO: {intro}...")
    print("-" * 30)
conn.close()
