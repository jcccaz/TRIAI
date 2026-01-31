import sqlite3

def get_query_details(comp_id):
    conn = sqlite3.connect('comparisons.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM comparisons WHERE id = ?", (comp_id,))
    comp = cursor.fetchone()
    if not comp:
        print("Comparison not found")
        return

    print(f"--- COMPARISON {comp_id} ---")
    print(f"Question: {comp['question']}")
    print("-" * 50)
    
    cursor.execute("SELECT * FROM responses WHERE comparison_id = ?", (comp_id,))
    responses = cursor.fetchall()
    for resp in responses:
        print(f"### PROVIDER: {resp['ai_provider']} ###")
        print(f"Model: {resp['model_name']}")
        print(f"Persona: {resp['self_selected_persona']}")
        print(f"Thought: {resp['thought_text'][:500] if resp['thought_text'] else 'None'}...")
        print(f"Response: {resp['response_text'][:1000]}...")
        print("-" * 30)
    
    conn.close()

if __name__ == "__main__":
    get_query_details(126)
