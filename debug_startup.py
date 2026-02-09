
import sys
import os

print("Testing database initialization...")
try:
    # Append current directory to path so imports work
    sys.path.append(os.getcwd())
    
    # Try importing database module which triggers init_database()
    import database
    print("Database module imported successfully.")
    
    # Try calling a function to ensure session works
    stats = database.get_comparison_stats()
    print(f"Database stats Verified: {stats}")
    
except Exception as e:
    print(f"\n❌ FATAL ERROR during initialization: {e}")
    import traceback
    traceback.print_exc()
