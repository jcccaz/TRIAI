
from database import SessionLocal, Comparison, Response
from sqlalchemy import desc
import datetime

db = SessionLocal()
try:
    print("Checking recent comparisons...")
    recent = db.query(Comparison).order_by(desc(Comparison.timestamp)).limit(3).all()
    for r in recent:
        print(f"ID: {r.id}, Time: {r.timestamp}, Question: {r.question[:50]}")
        for resp in r.responses:
            print(f"  - {resp.ai_provider}: Success={resp.success}")
except Exception as e:
    print(f"Error: {e}")
finally:
    db.close()
