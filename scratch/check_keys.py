import os
from pathlib import Path
from dotenv import load_dotenv

def main():
    root_dir = Path(__file__).parent.parent
    load_dotenv(root_dir / ".env", override=True)
    
    keys = ["GEMINI_API_KEY", "OPENROUTER_API_KEY", "OPENAI_API_KEY", "ANTHROPIC_API_KEY"]
    for k in keys:
        val = os.getenv(k, "")
        print(f"{k}: {'PRESENT (len=' + str(len(val)) + ')' if val else 'MISSING'}")
        
    print("LLM_PROVIDER:", os.getenv("LLM_PROVIDER", "not set"))
    print("GEMINI_MODEL:", os.getenv("GEMINI_MODEL", "not set"))
    print("OPENROUTER_MODEL:", os.getenv("OPENROUTER_MODEL", "not set"))

if __name__ == "__main__":
    main()
