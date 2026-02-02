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
            thought_text TEXT,
            self_selected_persona TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (comparison_id) REFERENCES comparisons(id)
        )
    ''')
    
    # Migration: Add self_selected_persona if it doesn't exist
    try:
        cursor.execute("ALTER TABLE responses ADD COLUMN self_selected_persona TEXT")
    except sqlite3.OperationalError:
        # Column already exists
        pass

    # Feedback table (User-provided schema)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS query_feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            comparison_id INTEGER,  -- Links to 'comparisons' table id
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            user_id TEXT,  
            
            -- Role configuration used
            gpt_role TEXT,
            claude_role TEXT,
            gemini_role TEXT,
            perplexity_role TEXT,
            
            -- Satisfaction rating
            rating INTEGER,  -- 1-4 scale
            
            -- Problem indicators
            too_generic BOOLEAN,
            missing_details BOOLEAN,
            wrong_roles BOOLEAN,
            didnt_answer BOOLEAN,
            
            -- Optional text feedback
            feedback_text TEXT,
            
            -- Query metadata
            query_text TEXT,
            query_category TEXT,
            
            FOREIGN KEY (comparison_id) REFERENCES comparisons(id)
        )
    ''')

    # Response Evaluations table (for the 10-prompt experiment)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS response_evaluations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            response_id INTEGER,
            specificity INTEGER,
            depth INTEGER,
            actionability INTEGER,
            risk_honesty INTEGER,
            overall_quality INTEGER,
            eval_notes TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (response_id) REFERENCES responses(id)
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
            INSERT INTO responses (comparison_id, ai_provider, model_name, response_text, response_time, success, thought_text, self_selected_persona)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            comparison_id,
            ai_name,
            response_data.get('model', 'Unknown'),
            response_data.get('response', ''),
            response_data.get('time', 0),
            response_data.get('success', False),
            response_data.get('thought', ''),
            response_data.get('self_selected_persona', None)
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

def update_response_rating(comparison_id: int, ai_provider: str, rating: int) -> bool:
    """Update the rating for a specific AI response within a comparison"""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE responses 
            SET individual_rating = ? 
            WHERE comparison_id = ? AND LOWER(ai_provider) = LOWER(?)
        ''', (rating, comparison_id, ai_provider))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error updating response rating: {e}")
        return False

def save_evaluation(response_id: int, specificity: int, depth: int, actionability: int, risk_honesty: int, overall_quality: int, notes: str = None) -> bool:
    """Save granular evaluation metrics for a specific response"""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO response_evaluations (
                response_id, specificity, depth, actionability, risk_honesty, overall_quality, eval_notes
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (response_id, specificity, depth, actionability, risk_honesty, overall_quality, notes))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error saving evaluation: {e}")
        return False

def save_feedback(data: Dict) -> bool:
    """Save user feedback for a comparison"""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO query_feedback (
                comparison_id, user_id, 
                gpt_role, claude_role, gemini_role, perplexity_role,
                rating, too_generic, missing_details, wrong_roles, didnt_answer,
                feedback_text, query_text, query_category
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            data.get('comparison_id'),
            data.get('user_id'),
            data.get('gpt_role'),
            data.get('claude_role'),
            data.get('gemini_role'),
            data.get('perplexity_role'),
            data.get('rating'),
            data.get('too_generic', False),
            data.get('missing_details', False),
            data.get('wrong_roles', False),
            data.get('didnt_answer', False),
            data.get('feedback_text'),
            data.get('query_text'),
            data.get('query_category')
        ))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error saving feedback: {e}")
        return False

def get_best_config(category: str) -> Optional[Dict]:
    """Get the highest rated role configuration for a category"""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT gpt_role, claude_role, gemini_role, perplexity_role, 
               AVG(rating) as avg_rating, COUNT(*) as usage_count
        FROM query_feedback
        WHERE query_category = ? AND rating >= 3
        GROUP BY gpt_role, claude_role, gemini_role, perplexity_role
        ORDER BY avg_rating DESC, usage_count DESC
        LIMIT 1
    """, (category,))
    
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def get_total_spending() -> Dict:
    """Calculate total spending and breakdown by provider."""
    pricing_config = {
        "openai": {"input": 5.00, "output": 15.00},
        "anthropic": {"input": 3.00, "output": 15.00},
        "google": {"input": 0.00, "output": 0.00},
        "perplexity": {"input": 3.00, "output": 15.00}
    }
    
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT c.question, r.ai_provider, r.response_text 
        FROM comparisons c
        JOIN responses r ON c.id = r.comparison_id
        WHERE r.success = 1
    ''')
    
    breakdown = {p: 0.0 for p in pricing_config.keys()}
    total = 0.0
    
    for question, provider, response in cursor.fetchall():
        p_key = provider.lower()
        if p_key in pricing_config:
            p = pricing_config[p_key]
            cost = (len(question or "") / 4 / 1_000_000 * p["input"]) + \
                   (len(response or "") / 4 / 1_000_000 * p["output"])
            breakdown[p_key] += cost
            total += cost
            
    conn.close()
    return {
        "total": round(total, 4),
        "breakdown": {p: round(c, 4) for p, c in breakdown.items()}
    }

def get_analytics_summary() -> Dict:
    """Get summarized analytics for the dashboard"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    # Total Queries
    cursor.execute("SELECT COUNT(*) FROM comparisons")
    total_queries = cursor.fetchone()[0]
    
    # Total Feedback
    cursor.execute("SELECT COUNT(*) FROM query_feedback")
    total_feedback = cursor.fetchone()[0]
    
    # Average Satisfaction
    cursor.execute("SELECT AVG(rating) FROM query_feedback")
    avg_satisfaction = cursor.fetchone()[0] or 0
    
    spending_data = get_total_spending()
    
    # Top combinations by category
    cursor.execute("""
        SELECT query_category, gpt_role, claude_role, gemini_role, perplexity_role, 
               AVG(rating) as avg_rating, COUNT(*) as count
        FROM query_feedback
        WHERE rating >= 3
        GROUP BY query_category, gpt_role, claude_role, gemini_role, perplexity_role
        ORDER BY avg_rating DESC, count DESC
        LIMIT 5
    """)
    top_combos = [
        {
            "category": r[0], 
            "roles": {"gpt": r[1], "claude": r[2], "gemini": r[3], "perplexity": r[4]},
            "rating": round(r[5], 1),
            "count": r[6]
        } for r in cursor.fetchall()
    ]
    
    conn.close()
    return {
        "total_queries": total_queries,
        "total_feedback": total_feedback,
        "avg_satisfaction": round(avg_satisfaction, 1),
        "total_spent": spending_data["total"],
        "spending_breakdown": spending_data["breakdown"],
        "top_combinations": top_combos
    }

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

def delete_comparison(comparison_id: int):
    """Delete a comparison and its responses"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    # Delete responses first (foreign key)
    cursor.execute('DELETE FROM responses WHERE comparison_id = ?', (comparison_id,))
    
    # Delete comparison
    cursor.execute('DELETE FROM comparisons WHERE id = ?', (comparison_id,))
    
    conn.commit()
    conn.close()

# Initialize database on import
init_database()
