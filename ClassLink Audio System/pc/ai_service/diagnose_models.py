import os
from google import genai
from dotenv import load_dotenv
from pathlib import Path

# Load config.env
config_path = Path(__file__).parent / "config.env"
if config_path.exists():
    load_dotenv(config_path)

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("❌ ERROR: GEMINI_API_KEY not found in config.env")
else:
    print(f"🔍 Testing API Key: {api_key[:10]}...")
    try:
        client = genai.Client(api_key=api_key)
        print("✅ Client initialized. Listing models...")
        
        models = client.models.list()
        found_flash = False
        print("\n--- AVAILABLE MODELS ---")
        for m in models:
            # Print whatever attributes are available safely
            name = getattr(m, 'name', 'Unknown')
            methods = getattr(m, 'supported_methods', 'Unknown')
            print(f"- {name} (Methods: {methods})")
            if "gemini-1.5-flash" in name:
                found_flash = True
        
        if not found_flash:
            print("\n⚠️ WARNING: 'gemini-1.5-flash' NOT FOUND in the list above!")
        else:
            print("\n✅ 'gemini-1.5-flash' is available!")
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
