import sqlite3
import json

def get_latest():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    # Get the latest comparison
    cursor.execute("SELECT id, question, results_json FROM comparisons ORDER BY id DESC LIMIT 1")
    row = cursor.fetchone()
    if row:
        comp_id, question, results_json = row
        results = json.loads(results_json)
        print(f"ID: {comp_id}")
        print(f"Question: {question}")
        print("\n--- RESULTS ---")
        for model, data in results.items():
            print(f"Model: {model.upper()}")
            print(f"Bias: {data.get('execution_bias')}")
            print(f"Response Snippet: {data.get('response', '')[:500]}...\n")
    else:
        print("No comparisons found.")
    conn.close()

if __name__ == "__main__":
    get_latest()
