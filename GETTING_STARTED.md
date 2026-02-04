# Getting Started with Audio Recording & Transcription

## Quick Start (All Services)

Use the project launcher for the fastest setup:

```bash
# 1. Copy .env.example to .env at project root and set MINIMAX_API_KEY or OPENAI_API_KEY

# 2. Start all services (creates .venv and runs npm install if needed)
python start_all.py
```

This starts Backend (8000), Middleware (5001), and Frontend (8080). Press Ctrl+C to stop all.

**Preflight:** `.env` must exist—script errors and quits if missing. `.venv` and `frontend/node_modules` are created/installed automatically if missing.

**Fresh install:** Run `python clean_deps.py`, then `python start_all.py` to reinstall.

### Environment Files (.env)

Project root `.env` is used by both middleware and malpractice_agent (including when run standalone). Set `MINIMAX_API_KEY` or `OPENAI_API_KEY`. Copy `.env.example` to `.env`.

Backend uses `backend/.env` for its own config (see `backend/.env.example`).

## What Was Implemented

### Frontend
✅ Audio recording hook (`use-audio-recorder.ts`)
- Captures audio from user's microphone
- Uses browser MediaRecorder API
- Tracks recording duration
- Returns audio as Blob for upload

✅ Updated RecordHandoff page
- Integrated audio recording functionality
- Sends recorded audio to backend API
- Displays transcription results
- Error handling with toast notifications

✅ API service layer (`lib/api.ts`)
- Clean API interface for backend communication
- Type-safe request/response handling

### Backend
✅ FastAPI server (`backend/main.py`)
- `/api/transcribe` endpoint for audio transcription
- Uses OpenAI Whisper API
- Handles file uploads
- CORS configured for frontend

✅ Setup automation
- `setup.sh` script for easy installation
- Requirements file with all dependencies
- Environment configuration

## How to Use

### Step 1: Set Up the Backend

```bash
cd backend-api
./setup.sh
```

Edit `backend-api/.env` and add your Minimax API credentials:
```
MINIMAX_API_KEY=your-api-key-here
MINIMAX_GROUP_ID=your-group-id-here
```

Start the backend:
```bash
source venv/bin/activate
python main.py
```

### Step 2: Frontend is Already Running

Your frontend should already be running at http://localhost:8080/

If not:
```bash
cd frontend
npm run dev
```

### Step 3: Test the Recording

1. Open http://localhost:8080/ in your browser
2. Select a patient from the dropdown
3. **Hold down** the record button to start recording
4. Speak your handoff notes
5. **Release** the button to stop
6. The audio will automatically be sent to the backend
7. Wait a few seconds for the transcription to appear

## Features

- 🎤 **Real-time Recording**: Press and hold to record
- ⏱️ **Duration Timer**: See recording length
- 🌊 **Waveform Animation**: Visual feMinimax Speech-to-Textecording
- 🤖 **AI Transcription**: Powered by OpenAI Whisper
- 📱 **Responsive**: Works on desktop and mobile
- ⚡ **Fast**: Near real-time transcription

## Troubleshooting

### "Recording Error" - Microphone Permission
- Click "Allow" when browser asks for microphone access
- Check browser settings if permission was denied

### "Transcription Failed"
- Make sure backend is running on port 8000
- Verify Minimax API credentials are set in `backend-api/.env`
- Check backend terminal for error messages

### "Failed to fetch"
- Backend server might not be running
- Check that CORS is properly configured
- Verify the API URL in console

## API Endpoint Details

**POST** `/api/transcribe`

Request:
- `audio` (file): Audio recording
- `patient_id` (optional): Selected patient
- `incoming_role` (optional): RN, Intern, Resident, or Attending
- `shift_context` (optional): Handoff context

Response:
```json
{
  "success": true,
  "transcript": "Patient is a 45-year-old male presenting with...",
  "patient_id": "12345",
  "incoming_role": "RN",
  "shift_context": "ED → Floor"
}
```

## Next Steps

Potential enhancements:
- [ ] Save transcriptions to database
- [ ] Generate SBAR format from transcript
- [ ] Support multiple audio formats
- [ ] Add audio playback functionality
- [ ] Implement offline recording with sync
- [ ] Add speaker diarization
- [ ] Custom medical vocabulary training

## Cost Considerations

Minimax API pricing varies by usage. Check https://www.minimaxi.com/ for current pricing.

For production, consider:
- Implementing usage limits
- Adding user authentication
- Monitoring API costs
- Caching common transcriptions
