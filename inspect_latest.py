import sqlite3
import json

def get_latest_data():
    try:
        conn = sqlite3.connect('comparisons.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Get latest 2 comparisons
        cursor.execute("SELECT id, question, timestamp FROM comparisons ORDER BY id DESC LIMIT 2")
        comparisons = cursor.fetchall()
        
        print(f"--- LATEST QUERIES ---")
        for comp in comparisons:
            print(f"ID: {comp['id']} | [{comp['timestamp']}]")
            print(f"Q: {comp['question']}")
            
            # Fetch responses
            cursor.execute("SELECT ai_provider, model_name, self_selected_persona, response, thought FROM responses WHERE comparison_id = ?", (comp['id'],))
            responses = cursor.fetchall()
            for resp in responses:
                print(f"  > {resp['ai_provider']} ({resp['model_name']})")
                print(f"    Persona: {resp['self_selected_persona']}")
                # print(f"    Thought snippet: {resp['thought'][:100] if resp['thought'] else 'N/A'}...")
            print("-" * 50)
            
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    get_latest_data()
