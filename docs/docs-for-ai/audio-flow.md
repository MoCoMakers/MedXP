# Audio Flow Documentation

## Overview

This document describes the audio-to-transcript flow in MedXP: how recorded handoff audio flows from the frontend through the middleware to produce transcripts, and how transcripts are optionally forwarded for enrichment and malpractice analysis.

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         FRONTEND (Port 8080)                                │
│   RecordHandoff page                                                        │
│   ┌─────────────────────────────────────────────────────────────────────┐  │
│   │ use-audio-recorder (MediaRecorder)                                   │  │
│   │ • Record → Stop → Full blob (audio/webm or audio/mp4)                │  │
│   │ • No chunking; one-shot recording                                    │  │
│   └─────────────────────────────────────────────────────────────────────┘  │
│   transcriptionApi.transcribe({ audio, patientId, incomingRole, shiftContext })│
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    │ POST multipart/form-data
                                    │ VITE_TRANSCRIBE_URL/api/transcribe
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                      MIDDLEWARE (Port 5001)                                 │
│   POST /api/transcribe                                                      │
│   ┌─────────────────────────────────────────────────────────────────────┐  │
│   │ 1. Receive audio blob (required), patient_id, incoming_role,        │  │
│   │    shift_context                                                     │  │
│   │ 2. Call Gemini API (google-genai) for transcription                 │  │
│   │ 3. Return { success, transcript, audio_file }                        │  │
│   └─────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
│   POST /api/v1/transcripts (separate flow; JSON only)                       │
│   ┌─────────────────────────────────────────────────────────────────────┐  │
│   │ 1. Receive { PatientID, Transcript }                                │  │
│   │ 2. Generate enrich request from scn_1.json template                  │  │
│   │ 3. Forward to Backend POST /api/v1/enrich                            │  │
│   │ 4. Call malpractice agent with enriched context                      │  │
│   │ 5. Return combined response                                          │  │
│   └─────────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    │ (transcripts only; enrich flow)
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                    BACKEND (Port 8000)                                      │
│   POST /api/v1/enrich                                                       │
│   • Context Enrichment Agent                                                │
│   • Returns patient_summary, relevant_sops, policies, guidelines, warnings  │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Endpoints

### POST /api/transcribe (Audio → Transcript)

**Purpose:** One-shot transcription of recorded handoff audio via Gemini.

**Request:**
- Content-Type: `multipart/form-data`
- Fields:
  - `audio` (required): Audio blob (WebM or MP4 from MediaRecorder)
  - `patient_id` (optional)
  - `incoming_role` (optional)
  - `shift_context` (optional)

**Response:**
```json
{
  "success": true,
  "transcript": "Transcribed text...",
  "audio_file": "handoff_20260130_123456.webm"
}
```

**Configuration:**
- `GEMINI_API_KEY` in project root `.env` (used by middleware)
- `VITE_TRANSCRIBE_URL=http://localhost:5001` in `frontend/.env` (used by Vite). See `frontend/.env.example`. Restart frontend dev server after changing.

### POST /api/v1/transcripts (Transcript → Enrichment + Malpractice)

**Purpose:** Submit an existing transcript for backend enrichment and malpractice analysis. Does not accept audio.

**Request:**
- Content-Type: `application/json`
- Body:
```json
{
  "PatientID": "P001",
  "Transcript": "Full session transcript text"
}
```

**Response:**
```json
{
  "status": "success",
  "session_id": "MW2-20260130-1234-abc12345",
  "patient_id": "P001",
  "backend_enrichment": {
    "patient_summary": {...},
    "relevant_sops": [...],
    "applicable_policies": [...],
    "treatment_guidelines": [...],
    "warnings": [...]
  },
  "malpractice_analysis": {
    "risk_level": "medium",
    "compliance_score": 0.85,
    "executive_summary": "...",
    "key_concerns": [...],
    "recommended_action": "..."
  }
}
```

**Flow:**
1. Middleware loads `Data/sample_input/scn_1.json` template
2. Replaces `transcript` with request transcript; generates new `session_id`, `timestamp`
3. POSTs to Backend `http://127.0.0.1:8000/api/v1/enrich`
4. Passes enriched result to malpractice agent
5. Returns combined response

## Current PoC Scope

- **One-shot only:** No streaming or chunked transcription
- **No automatic feed-forward:** After `/api/transcribe`, the frontend displays the transcript. It does not automatically call `/api/v1/transcripts`
- **Separate flows:** Transcribe and transcripts are independent; linking them is a future phase

## Troubleshooting

Session activity logs are written to `middleware/logs/` for debugging. See [middleware/logs/README.md](../../middleware/logs/README.md) for log format and usage.
