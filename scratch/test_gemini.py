import os
from pathlib import Path
from dotenv import load_dotenv
from google import genai

def main():
    root_dir = Path(__file__).parent.parent
    load_dotenv(root_dir / ".env", override=True)
    
    api_key = os.getenv("GEMINI_API_KEY", "")
    print(f"API key loaded: {'YES' if api_key else 'NO'}")
    
    if not api_key:
        print("Error: GEMINI_API_KEY is not set in .env")
        return
        
    client = genai.Client(api_key=api_key)
    # Using the standard gemini model
    model = os.getenv("GEMINI_MODEL", "gemini-2.5-pro-preview-05-06")
    print(f"Using model: {model}")
    
    try:
        response = client.models.generate_content(
            model=model,
            contents="Say 'Hello World' in Portuguese.",
            config={
                "temperature": 0.7,
                "max_output_tokens": 100
            }
        )
        print("Response:", response.text.strip())
    except Exception as e:
        print("API call failed:", e)

if __name__ == "__main__":
    main()
