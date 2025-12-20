# -*- coding: utf-8 -*-
"""
List available Gemini models
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
load_dotenv(config_path)
api_key = os.getenv("GEMINI_API_KEY")

print(f"[OK] API Key found: {api_key[:10]}...{api_key[-4:]}")
print("\n[INFO] Listing available models...")

from google import genai

client = genai.Client(api_key=api_key)

for model in client.models.list():
    print(f"  - {model.name}")
