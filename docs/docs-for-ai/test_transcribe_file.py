#!/usr/bin/env python3
"""One-off test: transcribe Data/TranscriptTest.mp3 using Gemini 3.

Usage: python docs/docs-for-ai/test_transcribe_file.py
Requires: .env with GEMINI_API_KEY, Data/TranscriptTest.mp3
"""

import os
from pathlib import Path

from dotenv import load_dotenv

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
load_dotenv(_PROJECT_ROOT / ".env")

AUDIO_PATH = _PROJECT_ROOT / "Data" / "TranscriptTest.mp3"


def main():
    if not AUDIO_PATH.exists():
        print(f"FAIL: {AUDIO_PATH} not found")
        return 1

    key = os.environ.get("GEMINI_API_KEY")
    if not key:
        print("FAIL: GEMINI_API_KEY not set in .env")
        return 1

    audio_bytes = AUDIO_PATH.read_bytes()
    print(f"Loaded {len(audio_bytes)} bytes from {AUDIO_PATH.name}")

    from google import genai
    from google.genai import types

    client = genai.Client(api_key=key)
    response = client.models.generate_content(
        model="gemini-3-flash-preview",
        contents=[
            "Transcribe this medical handoff audio verbatim.",
            types.Part.from_bytes(data=audio_bytes, mime_type="audio/mp3"),
        ],
    )

    transcript = response.text or ""
    print("\n--- Transcript ---")
    print(transcript)
    print("\n--- OK ---")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
