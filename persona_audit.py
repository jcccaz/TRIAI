
import sqlite3
import os

conn = sqlite3.connect('comparisons.db')
cursor = conn.cursor()
cursor.execute("SELECT ai_provider, model_name, response_text FROM responses ORDER BY id DESC LIMIT 4")
rows = cursor.fetchall()

with open('persona_audit.txt', 'w', encoding='utf-8') as f:
    for provider, model, response in rows:
        f.write(f"PROVIDER: {provider}\n")
        f.write(f"MODEL_NAME: {model}\n")
        f.write(f"INTRO: {response[:400]}\n")
        f.write("-" * 50 + "\n")

conn.close()
print("PERSONA AUDIT COMPLETE")
