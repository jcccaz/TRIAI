import sqlite3
import json

def export_last_two():
    try:
        conn = sqlite3.connect('comparisons.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT id, question, timestamp FROM comparisons ORDER BY id DESC LIMIT 2")
        rows = cursor.fetchall()
        
        with open('last_two_prompts.txt', 'w', encoding='utf-8') as f:
            for row in rows:
                f.write(f"ID: {row['id']}\n")
                f.write(f"Timestamp: {row['timestamp']}\n")
                f.write(f"Question: {row['question']}\n")
                f.write("-" * 20 + "\n")
                
                cursor.execute("SELECT ai_provider, model_name, self_selected_persona, response, thought FROM responses WHERE comparison_id = ?", (row['id'],))
                responses = cursor.fetchall()
                for resp in responses:
                    f.write(f"AI: {resp['ai_provider']} ({resp['model_name']})\n")
                    f.write(f"Persona: {resp['self_selected_persona']}\n")
                    f.write(f"Thought: {resp['thought'][:500]}...\n")
                    f.write(f"Response: {resp['response'][:500]}...\n")
                    f.write("\n")
                f.write("=" * 40 + "\n\n")
        print("Exported to last_two_prompts.txt")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    export_last_two()
