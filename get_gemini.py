import sqlite3

def get_gemini_persona(comp_id):
    conn = sqlite3.connect('comparisons.db')
    cursor = conn.cursor()
    cursor.execute("SELECT self_selected_persona FROM responses WHERE comparison_id = ? AND ai_provider = 'google'", (comp_id,))
    row = cursor.fetchone()
    if row:
        print(f"GEMINI PERSONA: {row[0]}")
    conn.close()

if __name__ == "__main__":
    get_gemini_persona(126)
