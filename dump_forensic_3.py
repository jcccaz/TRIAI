import sqlite3
import json
import os

def dump_forensics():
    try:
        db_path = r'c:\Users\carlo\OneDrive\Documents\Obsidian_Franknet\FrankNet\FrankNet\tri_ai_compare\comparisons.db'
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Get latest 2 comparisons
        cursor.execute("SELECT id, question, timestamp FROM comparisons ORDER BY id DESC LIMIT 2")
        comparisons = cursor.fetchall()
        
        output = []
        output.append("=== STRESS TEST 3 FORENSIC AUDIT ===")
        
        for comp in comparisons:
            output.append(f"\nID: {comp['id']} | Timestamp: {comp['timestamp']}")
            output.append(f"QUESTION: {comp['question']}")
            
            # Fetch responses
            cursor.execute("SELECT ai_provider, model_name, self_selected_persona, response_text, thought_text FROM responses WHERE comparison_id = ?", (comp['id'],))
            responses = cursor.fetchall()
            
            for resp in responses:
                output.append(f"\n--- PROVIDER: {resp['ai_provider'].upper()} ({resp['model_name']}) ---")
                output.append(f"PERSONA: {resp['self_selected_persona']}")
                output.append("THOUGHTS:")
                output.append(resp['thought_text'][:2000] if resp['thought_text'] else "NONE")
                output.append("\nRESPONSE:")
                output.append(resp['response_text'])
                output.append("-" * 30)
            output.append("\n" + "="*80)
            
        with open('forensic_stress_test_3.txt', 'w', encoding='utf-8') as f:
            f.write("\n".join(output))
        print("Forensic dump complete: forensic_stress_test_3.txt")
        
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    dump_forensics()
