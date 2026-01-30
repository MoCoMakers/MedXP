from fastapi import FastAPI, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
import openai
import os
from pathlib import Path
from datetime import datetime
from typing import Optional

app = FastAPI(title="MedXP Transcription API")

# CORS middleware to allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# OpenAI API configuration
openai.api_key = ""

# Audio storage directory
AUDIO_STORAGE_DIR = Path(__file__).parent.parent / "audio"
AUDIO_STORAGE_DIR.mkdir(exist_ok=True)


@app.get("/")
async def root():
    return {"message": "MedXP Transcription API", "status": "running"}


@app.get("/health")
async def health():
    return {"status": "healthy"}


@app.post("/api/transcribe")
async def transcribe_audio(
    audio: UploadFile = File(...),
    patient_id: Optional[str] = Form(None),
    incoming_role: Optional[str] = Form(None),
    shift_context: Optional[str] = Form(None),
):
    """
    Save audio file and transcribe using OpenAI Whisper API
    """
    saved_file_path = None
    
    try:
        # Read the uploaded audio file
        audio_content = await audio.read()
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"handoff_{timestamp}.webm"
        saved_file_path = AUDIO_STORAGE_DIR / filename
        
        # Save the audio file
        with open(saved_file_path, 'wb') as f:
            f.write(audio_content)
        
        print(f"Audio saved to: {saved_file_path}")
        
        # Transcribe using OpenAI Whisper
        with open(saved_file_path, 'rb') as audio_file:
            transcript = openai.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                language="en"
            )
        
        transcript_text = transcript.text
        
        return {
            "success": True,
            "transcript": transcript_text,
            "audio_file": str(saved_file_path.name),
            "patient_id": patient_id,
            "incoming_role": incoming_role,
            "shift_context": shift_context,
        }

    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to transcribe audio",
            "audio_file": str(saved_file_path.name) if saved_file_path else None
        }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
