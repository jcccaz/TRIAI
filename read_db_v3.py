import sqlite3
import json

def get_latest(limit=3):
    conn = sqlite3.connect('comparisons.db')
    cursor = conn.cursor()
    
    # Get the latest N comparisons
    cursor.execute("SELECT id, question, timestamp FROM comparisons ORDER BY id DESC LIMIT ?", (limit,))
    rows = cursor.fetchall()
    
    for row in rows:
        comp_id, question, ts = row
        print(f"=== ID: {comp_id} | Timestamp: {ts} ===")
        print(f"Question: {question}")
        
        # Get the responses for this comparison
        cursor.execute("SELECT ai_provider, response_text, self_selected_persona FROM responses WHERE comparison_id = ?", (comp_id,))
        responses = cursor.fetchall()
        
        for model, response, persona in responses:
            print(f"\n--- {model.upper()} | Persona: {persona} ---")
            print(f"{response[:800]}...")
        print("\n" + "="*50 + "\n")
        
    conn.close()

if __name__ == "__main__":
    get_latest()
