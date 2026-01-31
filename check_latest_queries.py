import sqlite3
import json

def get_latest_queries():
    conn = sqlite3.connect('comparisons.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Get the last 5 questions
    cursor.execute("SELECT id, question, timestamp FROM comparisons ORDER BY id DESC LIMIT 5")
    rows = cursor.fetchall()
    
    for row in rows:
        print(f"ID: {row['id']}")
        print(f"Timestamp: {row['timestamp']}")
        print(f"Question: {row['question'][:100]}...")
        print("-" * 20)
        
        # Get responses for this question
        cursor.execute("SELECT ai_provider, model_name, self_selected_persona FROM responses WHERE comparison_id = ?", (row['id'],))
        responses = cursor.fetchall()
        for resp in responses:
            print(f"  {resp['ai_provider']} ({resp['model_name']}): {resp['self_selected_persona']}")
        print("\n")
    
    conn.close()

if __name__ == "__main__":
    get_latest_queries()
