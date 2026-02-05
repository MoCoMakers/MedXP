# MedXP Middleware

Flask service that receives transcript data, forwards it to the backend enrichment pipeline, and passes the enriched context to the malpractice agent for risk analysis.

## Prerequisites

- Python 3.9+
- **Backend** running at `http://localhost:8000` (see `backend/README.md`)
- API key for malpractice analysis: `MINIMAX_API_KEY` or `OPENAI_API_KEY` in project root `.env`

## Build / Install

From the **project root** (`MedXP/`):

```bash
# Install middleware dependencies
pip install -r middleware/requirements.txt

# Install root dependencies (required for malpractice_agent)
pip install -r requirements.txt
```

## Launch

From the **project root**:

```bash
python middleware/app.py
```

Or from the middleware directory (with project root on `PYTHONPATH`):

```bash
cd middleware
pip install -r requirements.txt
cd ..
PYTHONPATH=. python middleware/app.py
```

The middleware listens on **http://localhost:5001**.

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Health check; reports backend and malpractice agent availability |
| POST | `/api/transcribe` | Transcribe audio (Gemini); multipart form: `audio`, `patient_id`, `incoming_role`, `shift_context` |
| POST | `/api/v1/transcripts` | Submit transcript; body: `{"PatientID": "...", "Transcript": "..."}` |

## Session Logs

Session activity (transcribe requests/results, transcripts requests/responses) is logged to `middleware/logs/session_YYYYMMDD.jsonl` for troubleshooting. See [middleware/logs/README.md](logs/README.md) for log format and usage.

## Input (HTTP API)

Input is sent via HTTP POST with a JSON body. Any HTTP client works (curl, Postman, fetch, etc.).

### Command-line only: curl demo

Input is **raw transcript** (natural speech / dictation), not preprocessed. Copy-paste one of these (no files, no editor). For longer or arbitrary text use `python middleware/post_transcript.py P001 -f transcript.txt` or `... P001 < transcript.txt`.

| Shell | One-liner |
|-------|-----------|
| **Bash / Git Bash** | `curl -X POST http://localhost:5001/api/v1/transcripts -H "Content-Type: application/json" -d '{"PatientID": "P001", "Transcript": "Rounding on Maria Chen, room 3E-12. She is 62 with stage 3B NSCLC on chemoradiation. Overnight fever 38.5, WBC 1.2, neutropenic. Sats 89% on 3L. Blood in sputum this morning, hold enoxaparin, cultures times two, broad spectrum. Pain 4 out of 10. Family aware."}'` |
| **Command Prompt (Windows)** | `curl.exe -X POST http://localhost:5001/api/v1/transcripts -H "Content-Type: application/json" -d "{\"PatientID\": \"P001\", \"Transcript\": \"Rounding on Maria Chen, room 3E-12. She is 62 with stage 3B NSCLC on chemoradiation. Overnight fever 38.5, WBC 1.2, neutropenic. Sats 89% on 3L. Blood in sputum this morning, hold enoxaparin, cultures times two, broad spectrum. Pain 4 out of 10. Family aware.\"}"` |
| **Any (Python)** | `python middleware/simulate.py` |

### simulate.py

`middleware/simulate.py` is a Python client that POSTs a sample transcript (from `Data/scenarios.json`) and prints the combined backend enrichment + malpractice analysis as structured JSON, including warnings grouped by severity and type. Run from project root (requires `requests`):

```bash
pip install requests
python middleware/simulate.py
```

## Configuration

- **Backend URL**: `http://127.0.0.1:8000` (edit `BACKEND_URL` in `app.py` if needed)
- **Template**: Uses `Data/sample_input/scn_1.json` for enrichment request structure
- **Environment**: Loads `.env` from project root (see project root `.env.example`). Requires `MINIMAX_API_KEY` or `OPENAI_API_KEY` for malpractice analysis; `GEMINI_API_KEY` for transcription (`POST /api/transcribe`). For the frontend to reach middleware for transcription, set `VITE_TRANSCRIBE_URL=http://localhost:5001` in `frontend/.env` (see `frontend/.env.example`).

## Testing

Run `python middleware/simulate.py` from project root (see [simulate.py](#simulatepy) above).