import database
comp = database.get_recent_comparisons(1)[0]
for r in comp['responses']:
    print(f"Provider: {r['ai_provider']}")
    print(f"Text: {r['response_text'][:200]}")
    print("-" * 20)
