from database import get_recent_comparisons
import json

try:
    history = get_recent_comparisons(limit=5)
    print("Success. Type:", type(history))
    if isinstance(history, list):
        print("Count:", len(history))
        print(json.dumps([dict(h) for h in history], default=str, indent=2))
    else:
        print("Response:", history)
except Exception as e:
    print("Error:", str(e))
