import sqlite3

DATABASE_PATH = 'comparisons.db'

# Pricing per 1M tokens (USD)
PRICING = {
    "openai": {"input": 5.00, "output": 15.00},
    "anthropic": {"input": 3.00, "output": 15.00},
    "google": {"input": 0.00, "output": 0.00},
    "perplexity": {"input": 3.00, "output": 15.00}
}

def calculate_total_cost():
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    # Get all comparisons and their responses
    cursor.execute('''
        SELECT c.question, r.ai_provider, r.response_text 
        FROM comparisons c
        JOIN responses r ON c.id = r.comparison_id
        WHERE r.success = 1
    ''')
    
    total_cost = 0.0
    provider_costs = {provider: 0.0 for provider in PRICING.keys()}
    
    for question, provider, response in cursor.fetchall():
        p_key = provider.lower()
        if p_key not in PRICING:
            continue
            
        pricing = PRICING[p_key]
        
        # Approximate tokens (4 chars per token)
        input_tokens = len(question) / 4
        output_tokens = len(response) / 4
        
        input_cost = (input_tokens / 1_000_000) * pricing["input"]
        output_cost = (output_tokens / 1_000_000) * pricing["output"]
        
        cost = input_cost + output_cost
        provider_costs[p_key] += cost
        total_cost += cost
        
    conn.close()
    
    print("--- API SPENDING REPORT ---")
    for provider, cost in provider_costs.items():
        print(f"{provider.capitalize()}: ${cost:.4f}")
    print("---------------------------")
    print(f"TOTAL SPENT: ${total_cost:.4f}")

if __name__ == "__main__":
    calculate_total_cost()
