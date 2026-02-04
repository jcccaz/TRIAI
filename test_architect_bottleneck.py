import os
import sys
from dotenv import load_dotenv

# Ensure we can import from current dir
sys.path.append(os.getcwd())
load_dotenv()

from visuals import fabricate_and_persist_visual

def test_specific_prompt():
    print("🚀 INITIALIZING FABRICATOR STRESS TEST...")
    
    concept = "Diagram of the failed server architecture showing the $1.5M bottleneck point"
    role = "architect"
    
    print(f"INPUT CONCEPT: {concept}")
    print(f"TARGET ROLE: {role}")
    print("-" * 30)
    
    result = fabricate_and_persist_visual(concept, role)
    
    if result:
        print("\n✅ FABRICATION SUCCESSFUL")
        print(f"REFINED PROMPT: {result['refined_prompt']}")
        print(f"LOCAL PERSISTENT PATH: {result['local_url']}")
        print(f"EXTERNAL SOURCE: {result['external_url']}")
        
        # Verify file exists
        local_file = os.path.join(os.getcwd(), result['local_url'].lstrip('/'))
        if os.path.exists(local_file):
            print(f"💾 VERIFIED: Image saved to disk ({os.path.getsize(local_file)} bytes)")
        else:
            print("❌ ERROR: Image file not found on disk!")
    else:
        print("\n❌ FABRICATION FAILED. Check logs for API issues.")

if __name__ == "__main__":
    test_specific_prompt()
