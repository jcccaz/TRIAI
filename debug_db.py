import os
import sys
from sqlalchemy import create_engine, text

DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///comparisons.db')
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

print(f"Testing connection to: {DATABASE_URL}")
try:
    engine = create_engine(DATABASE_URL)
    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1"))
        print(f"Connection Successful: {result.fetchone()}")
        
        # Check tables
        from sqlalchemy import inspect
        inspector = inspect(engine)
        print(f"Tables: {inspector.get_table_names()}")
        
except Exception as e:
    print(f"Connection Failed: {e}")
    sys.exit(1)
