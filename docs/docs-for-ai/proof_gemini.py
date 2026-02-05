#!/usr/bin/env python3
"""Proof that GEMINI_API_KEY from .env works with the Gemini 3 API.

Usage: python proof_gemini.py
Requires: .env with GEMINI_API_KEY, pip install google-genai python-dotenv
Ref: https://ai.google.dev/gemini-api/docs/gemini-3
"""

from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent / ".env")

from google import genai
from google.genai import types

client = genai.Client()

try:
    response = client.models.generate_content(
        model="gemini-3-flash-preview",
        contents="Explain how AI works in a few words",
        config=types.GenerateContentConfig(
            thinking_config=types.ThinkingConfig(thinking_level="high")
        ),
    )
    print(response.text)
    print("\nOK: GEMINI_API_KEY works.")
except Exception as e:
    err = str(e)
    if "429" in err or "RESOURCE_EXHAUSTED" in err or "quota" in err.lower():
        print("OK: GEMINI_API_KEY is valid (API responded). Quota exceeded.")
        print("  See https://ai.google.dev/gemini-api/docs/rate-limits")
    elif "401" in err or "API_KEY" in err or "unauthorized" in err.lower():
        print("FAIL: GEMINI_API_KEY invalid or missing. Add it to .env")
    else:
        raise
