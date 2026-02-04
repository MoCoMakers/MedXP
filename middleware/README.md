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
| POST | `/api/v1/transcripts` | Submit transcript; body: `{"PatientID": "...", "Transcript": "..."}` |

## Input (HTTP API)

Input is sent via HTTP POST with a JSON body. Any HTTP client works (curl, Postman, fetch, etc.).

### Example: curl

```bash
curl -X POST http://localhost:5001/api/v1/transcripts \
  -H "Content-Type: application/json" \
  -d '{"PatientID": "P001", "Transcript": "Maria Chen in 3E-12, 62 y/o with Stage IIIB NSCLC. Currently on Enoxaparin 40 mg SQ daily. Vitals: T 38.5C, HR 78, BP 167/79. Allergies: NKDA. Code status: Full Code."}'
```

### simulate.py

`middleware/simulate.py` is a Python client that POSTs a sample transcript (from `Data/scenarios.json`) and prints the combined backend enrichment + malpractice analysis as structured JSON, including warnings grouped by severity and type. Run from project root (requires `requests`):

```bash
pip install requests
python middleware/simulate.py
```

## Configuration

- **Backend URL**: `http://127.0.0.1:8000` (edit `BACKEND_URL` in `app.py` if needed)
- **Template**: Uses `Data/sample_input/scn_1.json` for enrichment request structure
- **Environment**: Loads `.env` from project root; requires `MINIMAX_API_KEY` or `OPENAI_API_KEY` for malpractice analysis

## Testing

Run `python middleware/simulate.py` from project root (see [simulate.py](#simulatepy) above).