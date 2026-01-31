import sqlite3
import json

def get_latest():
    conn = sqlite3.connect('comparisons.db')
    cursor = conn.cursor()
    
    # Get the latest comparison
    cursor.execute("SELECT id, question FROM comparisons ORDER BY id DESC LIMIT 1")
    row = cursor.fetchone()
    if row:
        comp_id, question = row
        print(f"ID: {comp_id}")
        print(f"Question: {question}")
        
        # Get the responses for this comparison
        cursor.execute("SELECT ai_provider, response_text, thought_text, self_selected_persona FROM responses WHERE comparison_id = ?", (comp_id,))
        responses = cursor.fetchall()
        
        print("\n--- RESPONSES ---")
        for model, response, thought, persona in responses:
            print(f"Model: {model.upper()}")
            print(f"Persona: {persona}")
            print(f"Response Snippet: {response[:500]}...\n")
    else:
        print("No comparisons found.")
    conn.close()

if __name__ == "__main__":
    get_latest()
