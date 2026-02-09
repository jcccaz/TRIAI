"""
Database layer for TriAI Compare (SQLAlchemy Version)
Handles both SQLite (Local) and PostgreSQL (Railway/Production) transparently.
"""
import os
import json
from datetime import datetime
from typing import List, Dict, Optional, Any
from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, Float, ForeignKey, Text, func, select, desc
from sqlalchemy.orm import declarative_base, sessionmaker, relationship, scoped_session

# --- Configuration ---
# Use database URL from environment variable, or fallback to local SQLite
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///comparisons.db')

# Fix for Railway's postgres:// URLs (SQLAlchemy requires postgresql://)
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# Create Engine & Session
engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))
Base = declarative_base()

# --- Models ---

class Comparison(Base):
    __tablename__ = "comparisons"
    id = Column(Integer, primary_key=True, index=True)
    question = Column(Text, nullable=False)
    document_content = Column(Text, nullable=True)
    document_name = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    saved = Column(Boolean, default=False)
    tags = Column(Text, nullable=True)

    # Relationships
    responses = relationship("Response", back_populates="comparison", cascade="all, delete-orphan")
    feedback = relationship("QueryFeedback", back_populates="comparison", cascade="all, delete-orphan")

class Response(Base):
    __tablename__ = "responses"
    id = Column(Integer, primary_key=True, index=True)
    comparison_id = Column(Integer, ForeignKey("comparisons.id"))
    ai_provider = Column(String, nullable=False)
    model_name = Column(String, nullable=False)
    response_text = Column(Text, nullable=False)
    response_time = Column(Float, nullable=True)
    success = Column(Boolean, default=False)
    thought_text = Column(Text, nullable=True)
    self_selected_persona = Column(Text, nullable=True)
    individual_rating = Column(Integer, nullable=True) # Added for rating feature
    timestamp = Column(DateTime, default=datetime.utcnow)

    comparison = relationship("Comparison", back_populates="responses")
    evaluations = relationship("ResponseEvaluation", back_populates="response", cascade="all, delete-orphan")

class QueryFeedback(Base):
    __tablename__ = "query_feedback"
    id = Column(Integer, primary_key=True, index=True)
    comparison_id = Column(Integer, ForeignKey("comparisons.id"))
    user_id = Column(String, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Role Config
    gpt_role = Column(String, nullable=True)
    claude_role = Column(String, nullable=True)
    gemini_role = Column(String, nullable=True)
    perplexity_role = Column(String, nullable=True)
    
    rating = Column(Integer, nullable=True)
    
    # Flags
    too_generic = Column(Boolean, default=False)
    missing_details = Column(Boolean, default=False)
    wrong_roles = Column(Boolean, default=False)
    didnt_answer = Column(Boolean, default=False)
    hallucinated = Column(Boolean, default=False)
    visual_mismatch = Column(Boolean, default=False)
    mandate_fail = Column(Boolean, default=False)
    cushioning_present = Column(Boolean, default=False)
    
    feedback_text = Column(Text, nullable=True)
    query_text = Column(Text, nullable=True)
    query_category = Column(String, nullable=True)
    feedback_tags = Column(String, nullable=True)

    comparison = relationship("Comparison", back_populates="feedback")

class ResponseEvaluation(Base):
    __tablename__ = "response_evaluations"
    id = Column(Integer, primary_key=True, index=True)
    response_id = Column(Integer, ForeignKey("responses.id"))
    specificity = Column(Integer, nullable=True)
    depth = Column(Integer, nullable=True)
    actionability = Column(Integer, nullable=True)
    risk_honesty = Column(Integer, nullable=True)
    overall_quality = Column(Integer, nullable=True)
    eval_notes = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)

    response = relationship("Response", back_populates="evaluations")

class SystemEvent(Base):
    __tablename__ = "system_events"
    id = Column(Integer, primary_key=True, index=True)
    event_type = Column(String, nullable=False) # STARTUP, CRASH, WORKFLOW_FAIL, RECOVERY
    message = Column(Text, nullable=False)
    details = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)

# --- Core Functions ---

def log_system_event(event_type: str, message: str, details: str = None):
    """Persist a system-level event for the dashboard telemetry."""
    db = SessionLocal()
    try:
        event = SystemEvent(
            event_type=event_type,
            message=message,
            details=details
        )
        db.add(event)
        db.commit()
    except Exception as e:
        print(f"Failed to log system event: {e}")
    finally:
        db.close()

def init_database():
    """Create tables if they don't exist"""
    Base.metadata.create_all(bind=engine)
    print(f"✅ Database initialized ({engine.url.drivername})")

def get_db():
    return SessionLocal()

def save_comparison(question: str, responses: Dict, document_content: str = None, document_name: str = None) -> int:
    db = SessionLocal()
    try:
        # Create Comparison
        comp = Comparison(
            question=question,
            document_content=document_content,
            document_name=document_name,
            saved=False
        )
        db.add(comp)
        db.commit()
        db.refresh(comp)
        
        # Create Responses
        for ai_name, r_data in responses.items():
            resp = Response(
                comparison_id=comp.id,
                ai_provider=ai_name,
                model_name=r_data.get('model', 'Unknown'),
                response_text=r_data.get('response', ''),
                response_time=r_data.get('time', 0),
                success=r_data.get('success', False),
                thought_text=r_data.get('thought', ''),
                self_selected_persona=r_data.get('self_selected_persona', None)
            )
            db.add(resp)
        
        db.commit()
        return comp.id
    except Exception as e:
        db.rollback()
        print(f"Error saving comparison: {e}")
        return -1
    finally:
        db.close()

def mark_as_saved(comparison_id: int, tags: str = None):
    db = SessionLocal()
    try:
        comp = db.query(Comparison).filter(Comparison.id == comparison_id).first()
        if comp:
            comp.saved = True
            comp.tags = tags
            db.commit()
    finally:
        db.close()

def update_response_rating(comparison_id: int, ai_provider: str, rating: int) -> bool:
    db = SessionLocal()
    try:
        # Find response by comparison and provider
        # Note: SQLite likes case-insensitive via query, Postgres is strict. use func.lower()
        resp = db.query(Response).filter(
            Response.comparison_id == comparison_id, 
            func.lower(Response.ai_provider) == ai_provider.lower()
        ).first()
        
        if resp:
            resp.individual_rating = rating
            db.commit()
            return True
        return False
    except Exception as e:
        print(f"Error updating rating: {e}")
        return False
    finally:
        db.close()

def save_evaluation(response_id: int, specificity: int, depth: int, actionability: int, risk_honesty: int, overall_quality: int, notes: str = None) -> bool:
    db = SessionLocal()
    try:
        evaluation = ResponseEvaluation(
            response_id=response_id,
            specificity=specificity,
            depth=depth,
            actionability=actionability,
            risk_honesty=risk_honesty,
            overall_quality=overall_quality,
            eval_notes=notes
        )
        db.add(evaluation)
        db.commit()
        return True
    except Exception as e:
        print(f"Error saving evaluation: {e}")
        return False
    finally:
        db.close()

def save_feedback(data: Dict) -> bool:
    db = SessionLocal()
    try:
        feedback = QueryFeedback(
            comparison_id=data.get('comparison_id'),
            user_id=data.get('user_id'),
            gpt_role=data.get('gpt_role'),
            claude_role=data.get('claude_role'),
            gemini_role=data.get('gemini_role'),
            perplexity_role=data.get('perplexity_role'),
            rating=data.get('rating'),
            too_generic=data.get('too_generic', False),
            missing_details=data.get('missing_details', False),
            wrong_roles=data.get('wrong_roles', False),
            didnt_answer=data.get('didnt_answer', False),
            hallucinated=data.get('hallucinated', False),
            visual_mismatch=data.get('visual_mismatch', False),
            mandate_fail=data.get('mandate_fail', False),
            cushioning_present=data.get('cushioning_present', False),
            feedback_text=data.get('feedback_text'),
            query_text=data.get('query_text'),
            query_category=data.get('query_category'),
            feedback_tags=data.get('feedback_tags')
        )
        db.add(feedback)
        db.commit()
        return True
    except Exception as e:
        print(f"Error saving feedback: {e}")
        return False
    finally:
        db.close()

def get_best_config(category: str) -> Optional[Dict]:
    db = SessionLocal()
    try:
        # SQLAlchemy Group By + Avg
        result = db.query(
            QueryFeedback.gpt_role,
            QueryFeedback.claude_role,
            QueryFeedback.gemini_role,
            QueryFeedback.perplexity_role,
            func.avg(QueryFeedback.rating).label('avg_rating'),
            func.count(QueryFeedback.id).label('usage_count')
        ).filter(
            QueryFeedback.query_category == category,
            QueryFeedback.rating >= 3
        ).group_by(
            QueryFeedback.gpt_role,
            QueryFeedback.claude_role,
            QueryFeedback.gemini_role,
            QueryFeedback.perplexity_role
        ).order_by(
            desc('avg_rating'),
            desc('usage_count')
        ).limit(1).first()

        if result:
            return {
                "gpt_role": result.gpt_role,
                "claude_role": result.claude_role,
                "gemini_role": result.gemini_role,
                "perplexity_role": result.perplexity_role,
                "avg_rating": result.avg_rating,
                "usage_count": result.usage_count
            }
        return None
    finally:
        db.close()

def get_total_spending() -> Dict:
    pricing_config = {
        "openai": {"input": 5.00, "output": 15.00},
        "anthropic": {"input": 3.00, "output": 15.00},
        "google": {"input": 0.00, "output": 0.00},
        "perplexity": {"input": 3.00, "output": 15.00}
    }
    
    db = SessionLocal()
    try:
        # Join Comparison + Response
        responses = db.query(Comparison.question, Response.ai_provider, Response.response_text)\
            .join(Response, Comparison.id == Response.comparison_id)\
            .filter(Response.success == True)\
            .all()
            
        breakdown = {p: 0.0 for p in pricing_config.keys()}
        total = 0.0
        
        for q, provider, text in responses:
            p_key = provider.lower()
            if p_key in pricing_config:
                p = pricing_config[p_key]
                cost = (len(q or "") / 4 / 1_000_000 * p["input"]) + \
                       (len(text or "") / 4 / 1_000_000 * p["output"])
                breakdown[p_key] += cost
                total += cost
                
        return {
            "total": round(total, 4),
            "breakdown": {p: round(c, 4) for p, c in breakdown.items()}
        }
    finally:
        db.close()

def get_analytics_summary() -> Dict:
    db = SessionLocal()
    try:
        total_queries = db.query(Comparison).count()
        total_feedback = db.query(QueryFeedback).count()
        avg_satisfaction = db.query(func.avg(QueryFeedback.rating)).scalar() or 0
        
        spending_data = get_total_spending()
        
        # Top Configs
        top_combos_query = db.query(
            QueryFeedback.query_category,
            QueryFeedback.gpt_role,
            QueryFeedback.claude_role,
            QueryFeedback.gemini_role,
            QueryFeedback.perplexity_role,
            func.avg(QueryFeedback.rating).label('avg_rating'),
            func.count(QueryFeedback.id).label('count')
        ).filter(
            QueryFeedback.rating >= 3
        ).group_by(
            QueryFeedback.query_category,
            QueryFeedback.gpt_role,
            QueryFeedback.claude_role,
            QueryFeedback.gemini_role,
            QueryFeedback.perplexity_role
        ).order_by(
            desc('avg_rating'),
            desc('count')
        ).limit(5).all()

        top_combos = [
            {
                "category": r.query_category, 
                "roles": {"gpt": r.gpt_role, "claude": r.claude_role, "gemini": r.gemini_role, "perplexity": r.perplexity_role},
                "rating": round(r.avg_rating, 1),
                "count": r.count
            } for r in top_combos_query
        ]

        return {
            "total_queries": total_queries,
            "total_feedback": total_feedback,
            "avg_satisfaction": round(avg_satisfaction, 1),
            "total_spent": spending_data["total"],
            "spending_breakdown": spending_data["breakdown"],
            "top_combinations": top_combos
        }
    finally:
        db.close()

def get_recent_comparisons(limit: int = 50) -> List[Dict]:
    db = SessionLocal()
    try:
        comps = db.query(Comparison).order_by(desc(Comparison.timestamp)).limit(limit).all()
        results = []
        for c in comps:
            c_dict = {
                "id": c.id, "question": c.question, 
                "document_content": c.document_content, "document_name": c.document_name,
                "timestamp": c.timestamp.isoformat() if c.timestamp else None,
                "saved": c.saved, "tags": c.tags,
                "responses": []
            }
            # Fetch responses manually or rely on relationship (lazy load)
            # Relationship is easier but we need to convert to dict
            for r in c.responses:
                r_dict = {
                    "id": r.id, "ai_provider": r.ai_provider, "model_name": r.model_name,
                    "response_text": r.response_text, "response_time": r.response_time,
                    "success": r.success, "thought_text": r.thought_text,
                    "self_selected_persona": r.self_selected_persona,
                    "individual_rating": r.individual_rating
                }
                c_dict['responses'].append(r_dict)
            results.append(c_dict)
        return results
    finally:
        db.close()

def get_saved_comparisons() -> List[Dict]:
    db = SessionLocal()
    try:
        comps = db.query(Comparison).filter(Comparison.saved == True).order_by(desc(Comparison.timestamp)).all()
        results = []
        for c in comps:
            c_dict = {
                "id": c.id, "question": c.question, 
                "timestamp": c.timestamp.isoformat() if c.timestamp else None,
                "saved": c.saved, "tags": c.tags,
                "responses": []
            }
            for r in c.responses:
                r_dict = {
                    "ai_provider": r.ai_provider, "model_name": r.model_name,
                    "response_text": r.response_text, "success": r.success,
                    "self_selected_persona": r.self_selected_persona
                }
                c_dict['responses'].append(r_dict)
            results.append(c_dict)
        return results
    finally:
        db.close()

def search_comparisons(query: str) -> List[Dict]:
    db = SessionLocal()
    try:
        comps = db.query(Comparison).filter(Comparison.question.ilike(f'%{query}%')).order_by(desc(Comparison.timestamp)).limit(50).all()
        results = []
        for c in comps:
            c_dict = {
                "id": c.id, "question": c.question, 
                "timestamp": c.timestamp.isoformat() if c.timestamp else None,
                "responses": []
            }
            for r in c.responses:
                r_dict = {
                    "ai_provider": r.ai_provider,
                    "response_text": r.response_text,
                    "self_selected_persona": r.self_selected_persona
                }
                c_dict['responses'].append(r_dict)
            results.append(c_dict)
        return results
    finally:
        db.close()

def get_comparison_stats() -> Dict:
    db = SessionLocal()
    try:
        total = db.query(Comparison).count()
        saved = db.query(Comparison).filter(Comparison.saved == True).count()
        responses = db.query(Response).count()
        return {
            'total_comparisons': total,
            'saved_comparisons': saved,
            'total_responses': responses
        }
    finally:
        db.close()

def delete_comparison(comparison_id: int):
    db = SessionLocal()
    try:
        comp = db.query(Comparison).filter(Comparison.id == comparison_id).first()
        if comp:
            db.delete(comp)
            db.commit()
    finally:
        db.close()

def get_dashboard_telemetry() -> Dict:
    """
    Real-time telemetry for the Mission Control dashboard.
    Counts prompts, costs, top personas, and anomalies.
    """
    from datetime import timedelta
    
    pricing = {
        "openai": {"input": 5.00, "output": 15.00},
        "anthropic": {"input": 3.00, "output": 15.00},
        "google": {"input": 0.00, "output": 0.00},
        "perplexity": {"input": 3.00, "output": 15.00}
    }

    db = SessionLocal()
    try:
        now = datetime.utcnow()
        past_24h = now - timedelta(hours=24)
        past_7d = now - timedelta(days=7)
        
        # 1. Prompt Counts (Comparisons created)
        total_prompts_24h = db.query(Comparison).filter(Comparison.timestamp >= past_24h).count()
        total_prompts_7d = db.query(Comparison).filter(Comparison.timestamp >= past_7d).count()
        
        # 2. Daily Cost
        # Uses Comparison.question joined with Response
        responses_24h = db.query(Comparison.question, Response.ai_provider, Response.response_text)\
             .join(Response, Comparison.id == Response.comparison_id)\
             .filter(Comparison.timestamp >= past_24h)\
             .all()
        
        cost_24h = 0.0
        for q, provider, text in responses_24h:
             pk = provider.lower() if provider else 'unknown'
             if pk in pricing:
                 c = pricing[pk]
                 # Rough token estimate: 1 char ~= 0.25 tokens
                 cost = (len(q or "") * 0.25 / 1_000_000 * c["input"]) + \
                        (len(text or "") * 0.25 / 1_000_000 * c["output"])
                 cost_24h += cost

        # 3. 7-Day Cost
        responses_7d_q = db.query(Comparison.question, Response.ai_provider, Response.response_text)\
             .join(Response, Comparison.id == Response.comparison_id)\
             .filter(Comparison.timestamp >= past_7d)\
             .all()
        
        cost_7d = 0.0
        prompts_processed = 0
        for q, provider, text in responses_7d_q:
             prompts_processed += 1
             pk = provider.lower() if provider else 'unknown'
             if pk in pricing:
                 c = pricing[pk]
                 cost = (len(q or "") * 0.25 / 1_000_000 * c["input"]) + \
                        (len(text or "") * 0.25 / 1_000_000 * c["output"])
                 cost_7d += cost
                 
        avg_cost = (cost_7d / prompts_processed) if prompts_processed > 0 else 0.0

        # 4. Top Used Schema (Persona)
        top_persona_q = db.query(Response.self_selected_persona, func.count(Response.id).label('count'))\
            .filter(Response.self_selected_persona.isnot(None))\
            .group_by(Response.self_selected_persona)\
            .order_by(desc('count'))\
            .limit(1).first()
            
        most_used_persona = top_persona_q.self_selected_persona if top_persona_q else "General"

        # 4a. Persona x Provider Density Matrix
        # Groups counts by (Persona, Provider)
        density_q = db.query(
            Response.self_selected_persona, 
            Response.ai_provider, 
            func.count(Response.id).label('count')
        ).filter(
            Response.self_selected_persona.isnot(None)
        ).group_by(
            Response.self_selected_persona, 
            Response.ai_provider
        ).all()
        
        # Transform into structured dict: { "Architect": {"openai": 45, "anthropic": 12}, ... }
        persona_matrix = {}
        for persona, provider, count in density_q:
            if not persona: continue
            if persona not in persona_matrix:
                persona_matrix[persona] = {"openai": 0, "anthropic": 0, "google": 0, "perplexity": 0}
            
            p_key = provider.lower() if provider else 'unknown'
            # Map common names to keys
            if 'openai' in p_key or 'gpt' in p_key: p_key = 'openai'
            elif 'anthropic' in p_key or 'claude' in p_key: p_key = 'anthropic'
            elif 'google' in p_key or 'gemini' in p_key: p_key = 'google'
            elif 'perplexity' in p_key: p_key = 'perplexity'
            
            if p_key in persona_matrix[persona]:
                persona_matrix[persona][p_key] += count

        # 5. Anomalies Log (Combine Feedback + System Events)
        anomaly_log = []
        
        # 5a. Get Feedback Anomalies
        anomalies_q = db.query(QueryFeedback.timestamp, QueryFeedback.feedback_text)\
            .filter((QueryFeedback.hallucinated == True) | (QueryFeedback.mandate_fail == True))\
            .order_by(desc(QueryFeedback.timestamp))\
            .limit(5).all()
        for a in anomalies_q:
            anomaly_log.append({
                "time": a.timestamp.strftime("%I:%M %p"),
                "type": "HALLUCINATION",
                "message": f"Flagged: {a.feedback_text[:50] if a.feedback_text else 'Feedback provided'}",
                "ts": a.timestamp
            })
            
        # 5b. Get System Events (Crashes, Startup)
        system_events = db.query(SystemEvent).order_by(desc(SystemEvent.timestamp)).limit(5).all()
        for se in system_events:
            anomaly_log.append({
                "time": se.timestamp.strftime("%I:%M %p"),
                "type": se.event_type,
                "message": se.message[:60],
                "details": se.details,
                "ts": se.timestamp
            })
            
        # 5c. Get Recent Missions
        recent_missions = []
        missions_q = db.query(Comparison.timestamp, Comparison.question)\
            .order_by(desc(Comparison.timestamp)).limit(5).all()
        for m in missions_q:
            recent_missions.append({
                "time": m.timestamp.strftime("%I:%M %p"),
                "question": m.question[:80] + "..." if len(m.question) > 80 else m.question
            })
            
        # Sort combined log by timestamp descending
        anomaly_log.sort(key=lambda x: x['ts'], reverse=True)
        # Clean up the internal timestamp
        for item in anomaly_log: del item['ts']
        
        if not anomaly_log:
            anomaly_log.append({
                "time": now.strftime("%I:%M %p"),
                "type": "SYS_EVENT",
                "message": "System nominal. No events detected."
            })

        return {
            "status": "nominal",
            "posture": {
                "strategist": 35, "architect": 40, "defender": 15, "other": 10
            },
            "costs": {
                "daily_total": round(cost_24h, 3),
                "last_7_days": round(cost_7d, 2), 
                "avg_cost_per_prompt": round(avg_cost, 4),
                "prompts_24h": total_prompts_24h
            },
            "most_used_persona": most_used_persona,
            "persona_density": persona_matrix,
            "cassandra_log": anomaly_log,
            "recent_missions": recent_missions,
            "infra": {
                "railway_uptime": "99.9%",
                "postgres_rows": f"{db.query(Response).count()}",
                "aws_status": "Stopped"
            }
        }
    except Exception as e:
        print(f"Telemetry Error: {e}")
        return { "status": "error", "error": str(e) }
    finally:
        db.close()

# Auto-init on import
import sys
try:
    init_database()
except Exception as e:
    print(f"🔥 CRITICAL: Database initialization failed: {e}")
    sys.exit(1)
