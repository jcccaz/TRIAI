import sqlite3
import sys

# Ensure output is UTF-8
if sys.platform == "win32":
    import codecs
    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())

def get_query_summary(comp_id):
    conn = sqlite3.connect('comparisons.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("SELECT question FROM comparisons WHERE id = ?", (comp_id,))
    comp = cursor.fetchone()
    if comp:
        print(f"QUESTION: {comp['question']}")
    
    cursor.execute("SELECT ai_provider, model_name, self_selected_persona FROM responses WHERE comparison_id = ?", (comp_id,))
    responses = cursor.fetchall()
    for resp in responses:
        print(f"PROVIDER: {resp['ai_provider']}")
        print(f"PERSONA: {resp['self_selected_persona']}")
        print("---")
    
    conn.close()

if __name__ == "__main__":
    get_query_summary(126)
