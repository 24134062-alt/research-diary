import os
from google import genai
from pathlib import Path
from dotenv import load_dotenv

# Load config
config_path = Path("ClassLink Audio System/pc/ai_service/config.env")
load_dotenv(config_path)
api_key = os.getenv("GEMINI_API_KEY")

print(f"Testing Gemini 2.5 API with Key: {api_key[:10]}...")

try:
    client = genai.Client(api_key=api_key, http_options={'api_version': 'v1'})
    
    # Use the EXACT name found in list_models earlier
    model_id = "gemini-2.5-flash-native-audio-latest"
    
    print(f"Sending prompt to {model_id}...")
    response = client.models.generate_content(
        model=model_id,
        contents="2+3 bằng mấy? Trả lời cực ngắn."
    )
    
    print("-" * 30)
    print(f"AI RESPONSE: {response.text}")
    print("-" * 30)
    print("✅ KẾT QUẢ: API HOẠT ĐỘNG HOÀN HẢO!")

except Exception as e:
    print(f"❌ LỖI: {e}")
