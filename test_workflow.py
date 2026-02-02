import asyncio
from concurrent.futures import ThreadPoolExecutor
# Mocking parts of app.py and workflows.py for testing
from workflows import Workflow, WORKFLOW_TEMPLATES

# Mock query functions
def mock_query(prompt, **kwargs):
    print(f"Mocking query for role: {kwargs.get('role')}")
    return {"success": True, "response": f"Response for {kwargs.get('role')}"}

async def test_run():
    template = WORKFLOW_TEMPLATES['business_strategy']
    engine = Workflow(name=template['name'], steps=template['steps'])
    
    query_funcs = {
        'openai': mock_query,
        'anthropic': mock_query,
        'google': mock_query,
        'perplexity': mock_query
    }
    
    try:
        print("Starting workflow execution...")
        results = await engine.execute("Test Goal", query_funcs, hard_mode=True)
        print("Execution finished successfully!")
        for res in results:
            print(f"Step {res['step']} ({res['role']}): {res['data']['success']}")
    except Exception as e:
        import traceback
        print(f"CRASH DETECTED:\n{traceback.format_exc()}")

if __name__ == "__main__":
    asyncio.run(test_run())
