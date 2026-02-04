def get_response_by_comparison_and_provider(comparison_id: int, provider: str):
    """Get a specific AI response by comparison ID and provider name."""
    import sqlite3
    DATABASE_PATH = 'comparisons.db'
    
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT * FROM responses 
        WHERE comparison_id = ? AND ai_provider = ?
    ''', (comparison_id, provider))
    
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return dict(row)
    return None
