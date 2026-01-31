"""
Persona Synthesizer for TriAI Compare
Analyzes captured self-selected personas to suggest improvements for permanent Council Roles.
"""
import sqlite3
import json
from collections import Counter
from typing import List, Dict
from council_roles import COUNCIL_ROLES

DATABASE_PATH = 'comparisons.db'

def get_all_self_selected_personas() -> List[str]:
    """Fetch all self-selected personas from the database"""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        cursor.execute("SELECT self_selected_persona FROM responses WHERE self_selected_persona IS NOT NULL")
        personas = [row[0] for row in cursor.fetchall()]
        
        conn.close()
        return personas
    except Exception as e:
        print(f"Error fetching personas: {e}")
        return []

def analyze_personas():
    """Perform a frequency analysis of self-selected personas"""
    personas = get_all_self_selected_personas()
    if not personas:
        print("No self-selected personas found in database yet.")
        return

    counter = Counter(personas)
    print("\n" + "="*40)
    print("      PERSONA FREQUENCY ANALYSIS")
    print("="*40)
    
    for persona, count in counter.most_common():
        print(f"[{count}x] {persona}")
    
    print("="*40 + "\n")

if __name__ == "__main__":
    analyze_personas()
