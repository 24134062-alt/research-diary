# -*- coding: utf-8 -*-
"""
Quick test for AI Teaching Assistant - using gemini-2.5-flash
"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Fix Windows console encoding
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Load API key from config.env
config_path = Path(__file__).parent / "config.env"
if config_path.exists():
    load_dotenv(config_path)
    print(f"[OK] Loaded config from: {config_path}")
else:
    print(f"[ERROR] Config file not found: {config_path}")
    exit(1)

# Check API key
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("[ERROR] GEMINI_API_KEY not found in config.env")
    exit(1)
print(f"[OK] API Key found: {api_key[:10]}...{api_key[-4:]}")

# Test Gemini API with new package
print("\n[TEST] Testing Gemini API with gemini-2.5-flash model...")
from google import genai

try:
    # Create client with API key
    client = genai.Client(api_key=api_key)
    
    # Use gemini-2.5-flash (different rate limit pool)
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents="Xin chao, ban la ai? Tra loi ngan gon bang tieng Viet."
    )
    print(f"\n[OK] Gemini response:\n{response.text}")
    
    print("\n" + "="*50)
    print("AI SERVICE READY!")
    print("="*50)
    
except Exception as e:
    print(f"[ERROR] {e}")
    exit(1)
