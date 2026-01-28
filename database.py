"""
Database layer for TriAI Compare
Stores all comparisons and responses for history/review
"""
import sqlite3
from datetime import datetime
from typing import List, Dict, Optional
import json

DATABASE_PATH = 'comparisons.db'

def init_database():
    """Initialize the database with required tables"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    # Comparisons table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS comparisons (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question TEXT NOT NULL,
            document_content TEXT,
            document_name TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            saved BOOLEAN DEFAULT 0,
            tags TEXT
        )
    ''')
    
    # Responses table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS responses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            comparison_id INTEGER,
            ai_provider TEXT NOT NULL,
            model_name TEXT NOT NULL,
            response_text TEXT NOT NULL,
            response_time REAL,
            success BOOLEAN,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (comparison_id) REFERENCES comparisons(id)
        )
    ''')
    
    conn.commit()
    conn.close()
    print("✅ Database initialized successfully!")

def save_comparison(question: str, responses: Dict, document_content: str = None, document_name: str = None) -> int:
    """
    Save a comparison and its responses
    Returns the comparison ID
    """
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    # Insert comparison
    cursor.execute('''
        INSERT INTO comparisons (question, document_content, document_name, saved)
        VALUES (?, ?, ?, 0)
    ''', (question, document_content, document_name))
    
    comparison_id = cursor.lastrowid
    
    # Insert responses
    for ai_name, response_data in responses.items():
        cursor.execute('''
            INSERT INTO responses (comparison_id, ai_provider, model_name, response_text, response_time, success)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            comparison_id,
            ai_name,
            response_data.get('model', 'Unknown'),
            response_data.get('response', ''),
            response_data.get('time', 0),
            response_data.get('success', False)
        ))
    
    conn.commit()
    conn.close()
    
    return comparison_id

def mark_as_saved(comparison_id: int, tags: str = None):
    """Mark a comparison as saved with optional tags"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        UPDATE comparisons 
        SET saved = 1, tags = ?
        WHERE id = ?
    ''', (tags, comparison_id))
    
    conn.commit()
    conn.close()

def get_recent_comparisons(limit: int = 50) -> List[Dict]:
    """Get recent comparisons with their responses"""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT * FROM comparisons 
        ORDER BY timestamp DESC 
        LIMIT ?
    ''', (limit,))
    
    comparisons = []
    for row in cursor.fetchall():
        comparison = dict(row)
        comparison_id = comparison['id']
        
        # Get responses for this comparison
        cursor.execute('''
            SELECT * FROM responses 
            WHERE comparison_id = ?
            ORDER BY ai_provider
        ''', (comparison_id,))
        
        comparison['responses'] = [dict(r) for r in cursor.fetchall()]
        comparisons.append(comparison)
    
    conn.close()
    return comparisons

def get_saved_comparisons() -> List[Dict]:
    """Get only saved/bookmarked comparisons"""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT * FROM comparisons 
        WHERE saved = 1
        ORDER BY timestamp DESC
    ''')
    
    comparisons = []
    for row in cursor.fetchall():
        comparison = dict(row)
        comparison_id = comparison['id']
        
        # Get responses
        cursor.execute('''
            SELECT * FROM responses 
            WHERE comparison_id = ?
            ORDER BY ai_provider
        ''', (comparison_id,))
        
        comparison['responses'] = [dict(r) for r in cursor.fetchall()]
        comparisons.append(comparison)
    
    conn.close()
    return comparisons

def search_comparisons(query: str) -> List[Dict]:
    """Search comparisons by question text"""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT * FROM comparisons 
        WHERE question LIKE ?
        ORDER BY timestamp DESC
        LIMIT 50
    ''', (f'%{query}%',))
    
    comparisons = []
    for row in cursor.fetchall():
        comparison = dict(row)
        comparison_id = comparison['id']
        
        cursor.execute('''
            SELECT * FROM responses 
            WHERE comparison_id = ?
            ORDER BY ai_provider
        ''', (comparison_id,))
        
        comparison['responses'] = [dict(r) for r in cursor.fetchall()]
        comparisons.append(comparison)
    
    conn.close()
    return comparisons

def get_comparison_stats() -> Dict:
    """Get statistics about stored comparisons"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    cursor.execute('SELECT COUNT(*) FROM comparisons')
    total_comparisons = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM comparisons WHERE saved = 1')
    saved_comparisons = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM responses')
    total_responses = cursor.fetchone()[0]
    
    conn.close()
    
    return {
        'total_comparisons': total_comparisons,
        'saved_comparisons': saved_comparisons,
        'total_responses': total_responses
    }

# Initialize database on import
init_database()
