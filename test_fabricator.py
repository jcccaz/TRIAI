import os
import sys
from dotenv import load_dotenv

# Add current directory to path
sys.path.append(os.getcwd())

load_dotenv()

def test_fabricator_logic():
    print("Testing Fabricator Logic...")
    try:
        from app import generate_visual_mockup
        
        test_prompt = "A high-security data center under a cyber attack"
        test_role = "liquidator"
        
        print(f"Generating visual for: {test_prompt} with role: {test_role}")
        # Note: This will actually call the OpenAI API if keys are present
        # If you don't want to spend credits, we can just check the imports and logic
        
        # Checking imports
        from visuals import get_style_for_role
        style = get_style_for_role(test_role)
        print(f"Mapped style for {test_role}: {style}")
        
        print("Logic check passed (Imports and Role Mapping ok).")
        
    except Exception as e:
        print(f"Test failed: {e}")

if __name__ == "__main__":
    test_fabricator_logic()
