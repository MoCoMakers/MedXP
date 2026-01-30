# MedXP Backend API

FastAPI backend service for audio transcription using Minimax Speech-to-Text API.

## Prerequisites

- Python 3.8 or higher
- Minimax API key and Group ID
- FFmpeg (for audio format conversion)

### Install FFmpeg

**macOS:**
```bash
brew install ffmpeg
```

**Ubuntu/Debian:**
```bash
sudo apt-get install ffmpeg
```

**Windows:**
Download from https://ffmpeg.org/download.html

## Setup

1. **Create a virtual environment:**

```bash
cd backend-api
python3 -m venv venv
```

2. **Activate the virtual environment:**

On macOS/Linux:
```bash
source venv/bin/activate
```

On Windows:
```bash
venv\Scripts\activate
```

3. **Install dependencies:**

```bash
pip install -r requirements.txt
```

4. **Set up environment variables:**

Create a `.env` file in the backend-api directory:

```bash
cp .env.example .env
```

Edit `.env` and add your Minimax API credentials:
```
MINIMAX_API_KEY=your-actual-api-key-here
MINIMAX_GROUP_ID=your-group-id-here
```

## Running the Server

Start the development server:

```bash
python main.py
```

Or using uvicorn directly:

```bash
uvicorn main:app --reload --port 8000
```

The API will be available at:
- API: http://localhost:8000
- Interactive API docs: http://localhost:8000/docs
- Alternative docs: http://localhost:8000/redoc

## API Endpoints

### POST /api/transcribe
Minimax Speech-to-Text API
Transcribe audio files to text using OpenAI Whisper.

**Request:**
- Method: `POST`
- Content-Type: `multipart/form-data`
- Body:
  - `audio` (file): Audio file (webm, mp3, wav, etc.)
  - `patient_id` (optional): Patient identifier
  - `incoming_role` (optional): Healthcare role (RN, Intern, Resident, Attending)
  - `shift_context` (optional): Shift transition context

**Response:**
```json
{
  "success": true,
  "transcript": "Patient is a 45-year-old male...",
  "patient_id": "12345",
  "incoming_role": "RN",
  "shift_context": "ED → Floor"
}
```

### GET /health

Health check endpoint.

**Response:**
```json
{
  "status": "healthy"
}
```

## Tech Stack

- **FastAPI** - Modern web framework for building APIs
- **Uvicorn** - ASGI server
- **Minimax Speech-to-Text** - Audio transcription
- **Python Multipart** - File upload handling

## Development

### Testing the API

You can test the transcription endpoint using curl:

```bash
curl -X POST "http://localhost:8000/api/transcribe" \
  -F "audio=@/path/to/audio/file.webm" \
  -F "patient_id=12345" \
  -F "incoming_role=RN" \
  -F "shift_context=ED → Floor"
```

Or visit http://localhost:8000/docs to use the interactive API documentation.

### CORS Configuration

The backend is configured to accept requests from:
- http://localhost:8080 (Vite default)
- http://localhost:5173 (Alternative Vite port)

To add more origins, edit the `allow_origins` list in `main.py`.

## Troubleshooting

### Minimax API Key Issues

If you get authentication errors:
1. Verify your API key and Group ID are correct in `.env`
2. Make sure you have access to Minimax API
3. Check that the `.env` file is in the backend-api directory
4. Get your credentials from: https://www.minimaxi.com/

### Audio File Format Issues
Minimax supports multiple formats including:
- webm
- mp3
- wav
- m4a
- flac

If transcription fails, try converting your audio to a supported format.

### Port Already in Use

If port 8000 is already in use, you can change it:

```bash
uvicorn main:app --reload --port 8001
```

Then update the frontend API URL accordingly.
