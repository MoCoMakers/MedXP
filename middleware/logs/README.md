# Middleware Session Logs

Session activity logs are written here for troubleshooting. Log files are created daily and contain structured JSON lines (one JSON object per line).

## Log Files

| Pattern | Description |
|---------|-------------|
| `session_YYYYMMDD.jsonl` | Daily session log (JSON Lines format) |

Log files are ignored by git (see `.gitignore`). The `logs/` directory is kept for documentation.

## Log Events

### transcribe_request

Logged when `POST /api/transcribe` receives an audio upload.

```json
{
  "timestamp": "2026-01-30T12:34:56.789Z",
  "event": "transcribe_request",
  "patient_id": "P001",
  "incoming_role": "RN",
  "shift_context": "ED → Floor",
  "audio_size_bytes": 45678,
  "mime_type": "audio/webm"
}
```

### transcribe_result

Logged after transcription completes (success or failure).

```json
{
  "timestamp": "2026-01-30T12:35:02.123Z",
  "event": "transcribe_result",
  "success": true,
  "transcript_preview": "Rounding on Maria Chen, room 3E-12...",
  "transcript_length": 420,
  "error": null
}
```

On failure:
```json
{
  "timestamp": "2026-01-30T12:35:02.123Z",
  "event": "transcribe_result",
  "success": false,
  "transcript_preview": null,
  "error": "GEMINI_API_KEY not configured"
}
```

### transcripts_request

Logged when `POST /api/v1/transcripts` receives a transcript submission.

```json
{
  "timestamp": "2026-01-30T12:36:00.000Z",
  "event": "transcripts_request",
  "patient_id": "P001",
  "transcript_length": 420,
  "transcript_preview": "Rounding on Maria Chen..."
}
```

### transcripts_response

Logged after `/api/v1/transcripts` completes (enrichment + malpractice analysis).

```json
{
  "timestamp": "2026-01-30T12:36:15.000Z",
  "event": "transcripts_response",
  "session_id": "MW2-20260130-1236-abc12345",
  "patient_id": "P001",
  "status": "success",
  "backend_enrichment_summary": {
    "warnings_count": 3
  },
  "malpractice_analysis": {
    "risk_level": "medium",
    "compliance_score": 0.85
  }
}
```

## Usage

View latest log file:
```bash
tail -f middleware/logs/session_20260130.jsonl
```

Search for failed transcriptions:
```bash
grep '"success": false' middleware/logs/session_*.jsonl
```

Parse with jq:
```bash
cat middleware/logs/session_20260130.jsonl | jq -s '.'
```
