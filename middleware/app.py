"""MedXP Middleware 2 - Flask Application

Simple Flask app for receiving transcript data, forwarding to backend enrichment,
and then passing the enriched context to the malpractice agent.
"""

import json
import uuid
import os
from datetime import datetime, timezone
from pathlib import Path

import httpx
from dotenv import load_dotenv
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app, origins=["http://localhost:8080", "http://localhost:5173"])

# Backend API configuration
BACKEND_URL = "http://127.0.0.1:8000"
ENRICH_ENDPOINT = f"{BACKEND_URL}/api/v1/enrich"

# Project root (parent of middleware/)
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
_MIDDLEWARE_DIR = Path(__file__).resolve().parent
_LOGS_DIR = _MIDDLEWARE_DIR / "logs"
TEMPLATE_PATH = _PROJECT_ROOT / "Data" / "sample_input" / "scn_1.json"


def _log_session_event(event: str, data: dict) -> None:
    """Append a session event as JSON line to middleware/logs/session_YYYYMMDD.jsonl."""
    try:
        _LOGS_DIR.mkdir(parents=True, exist_ok=True)
        today = datetime.now(timezone.utc).strftime("%Y%m%d")
        log_path = _LOGS_DIR / f"session_{today}.jsonl"
        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "event": event,
            **data,
        }
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except OSError as e:
        print(f"Log write failed: {e}")

# Initialize malpractice agent
load_dotenv(_PROJECT_ROOT / ".env")
api_key = os.environ.get("MINIMAX_API_KEY") or os.environ.get("OPENAI_API_KEY")

_malpractice_agent = None


def get_malpractice_agent():
    """Get or create the malpractice agent singleton."""
    global _malpractice_agent
    if _malpractice_agent is None and api_key:
        try:
            from malpractice_agent.agents.clinical_logic import MalpracticeAgentSystem
            _malpractice_agent = MalpracticeAgentSystem(
                api_key=api_key,
                base_url="https://api.minimax.io/v1",
                model="MiniMax-M2.1"
            )
            print("Malpractice agent initialized")
        except Exception as e:
            print(f"Failed to initialize malpractice agent: {e}")
            _malpractice_agent = False
    return _malpractice_agent if _malpractice_agent else None


def load_template():
    """Load the scn_1.json template."""
    with open(TEMPLATE_PATH, 'r') as f:
        return json.load(f)


def generate_enrich_request(patient_id: str, transcript: str) -> dict:
    """
    Generate an enrichment request by replacing transcript in the template.
    
    Args:
        patient_id: The patient ID from the POST request
        transcript: The transcript text from the POST request
        
    Returns:
        Dictionary with template data but replaced transcript
    """
    # Load the template
    template = load_template()
    
    # Generate new session_id and timestamp
    new_session_id = f"MW2-{datetime.now().strftime('%Y%m%d-%H%M')}-{uuid.uuid4().hex[:8]}"
    new_timestamp = datetime.now().isoformat()
    
    # Update template with new session info and transcript
    template["session_id"] = new_session_id
    template["timestamp"] = new_timestamp
    template["transcript"] = transcript
    
    return template


def call_malpractice_agent(transcript: str, session_id: str, patient_id: str, backend_response: dict) -> dict:
    """
    Call the malpractice agent with the transcript and enriched context.
    
    Args:
        transcript: The raw transcript text
        session_id: Session identifier
        patient_id: Patient identifier
        backend_response: Response from the enrichment backend
        
    Returns:
        Malpractice agent report as dict
    """
    agent = get_malpractice_agent()
    
    if not agent:
        return {
            "status": "unavailable",
            "message": "Malpractice agent not configured",
            "risk_level": "unknown",
            "compliance_score": None,
            "executive_summary": "Malpractice agent not available",
            "key_concerns": [],
            "recommended_action": "Manual review required"
        }
    
    try:
        # Build enriched context to pass to the agent
        enriched_context = {
            "session_id": session_id,
            "patient_id": patient_id,
            "backend_enrichment": {
                "patient_summary": backend_response.get("patient_summary", {}),
                "relevant_sops": backend_response.get("relevant_sops", []),
                "applicable_policies": backend_response.get("applicable_policies", []),
                "treatment_guidelines": backend_response.get("treatment_guidelines", []),
                "warnings": backend_response.get("warnings", []),
            }
        }
        
        # Run the malpractice analysis with enriched context
        report = agent.run_analysis(
            raw_transcript=transcript,
            output_dir=Path(__file__).resolve().parent / "output"
        )
        
        return {
            "status": "success",
            "risk_level": report.risk_level,
            "compliance_score": report.compliance_score,
            "executive_summary": report.executive_summary,
            "key_concerns": report.key_concerns,
            "recommended_action": report.recommended_action
        }
        
    except Exception as e:
        print(f"Malpractice agent error: {e}")
        return {
            "status": "error",
            "message": str(e),
            "risk_level": "unknown",
            "compliance_score": None,
            "executive_summary": f"Analysis failed: {str(e)}",
            "key_concerns": [],
            "recommended_action": "Manual review required"
        }


@app.route("/api/transcribe", methods=["POST"])
def transcribe_audio():
    """
    Transcribe audio via Gemini API (one-shot PoC).

    Accepts multipart form: audio (required), patient_id, incoming_role, shift_context.
    Returns TranscribeResponse shape: { success, transcript, audio_file?, message?, error? }.
    """
    if "audio" not in request.files:
        return jsonify({
            "success": False,
            "error": "Missing audio file",
            "message": "audio is required"
        }), 400

    file = request.files["audio"]
    if file.filename == "" or not file.readable():
        return jsonify({
            "success": False,
            "error": "Invalid audio file",
            "message": "audio file is empty or unreadable"
        }), 400

    audio_bytes = file.read()
    mime_type = file.content_type or "audio/webm"
    if mime_type == "application/octet-stream":
        mime_type = "audio/webm"

    patient_id = request.form.get("patient_id") or ""
    incoming_role = request.form.get("incoming_role") or ""
    shift_context = request.form.get("shift_context") or ""

    _log_session_event("transcribe_request", {
        "patient_id": patient_id,
        "incoming_role": incoming_role,
        "shift_context": shift_context,
        "audio_size_bytes": len(audio_bytes),
        "mime_type": mime_type,
    })

    gemini_key = os.environ.get("GEMINI_API_KEY")
    if not gemini_key:
        _log_session_event("transcribe_result", {
            "success": False,
            "transcript_preview": None,
            "transcript_length": None,
            "error": "GEMINI_API_KEY not configured",
        })
        return jsonify({
            "success": False,
            "error": "GEMINI_API_KEY not configured",
            "message": "Transcription service not configured"
        }), 503

    try:
        from google import genai
        from google.genai import types

        client = genai.Client(api_key=gemini_key)
        response = client.models.generate_content(
            model="gemini-3-flash-preview",
            contents=[
                "Transcribe this medical handoff audio verbatim.",
                types.Part.from_bytes(data=audio_bytes, mime_type=mime_type),
            ],
        )

        transcript_text = response.text or ""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        audio_filename = f"handoff_{timestamp}.webm"

        _log_session_event("transcribe_result", {
            "success": True,
            "transcript_preview": (transcript_text[:200] + "...") if len(transcript_text) > 200 else transcript_text,
            "transcript_length": len(transcript_text),
            "error": None,
        })

        return jsonify({
            "success": True,
            "transcript": transcript_text,
            "audio_file": audio_filename,
        }), 200

    except Exception as e:
        print(f"Transcription error: {e}")
        _log_session_event("transcribe_result", {
            "success": False,
            "transcript_preview": None,
            "transcript_length": None,
            "error": str(e),
        })
        # Detect Google API 5xx/429 - surface user-friendly alert
        err_str = str(e)
        if "429" in err_str or "RESOURCE_EXHAUSTED" in err_str or "quota" in err_str.lower():
            msg = "Transcription service quota exceeded. Please try again in a moment."
            return jsonify({"success": False, "error": err_str, "message": msg}), 503
        if "503" in err_str or "UNAVAILABLE" in err_str or "overloaded" in err_str.lower():
            msg = "Transcription service temporarily unavailable (Google API overloaded). Please try again shortly."
            return jsonify({"success": False, "error": err_str, "message": msg}), 503
        if "500" in err_str or "INTERNAL" in err_str:
            msg = "Transcription service error. Please try again."
            return jsonify({"success": False, "error": err_str, "message": msg}), 503
        return jsonify({
            "success": False,
            "error": err_str,
            "message": "Failed to transcribe audio",
        }), 500


@app.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint."""
    # Check backend health
    backend_healthy = False
    try:
        resp = httpx.get(f"{BACKEND_URL}/health", timeout=5.0)
        backend_healthy = resp.status_code == 200
    except:
        pass
    
    # Check malpractice agent
    malpractice_available = get_malpractice_agent() is not None
    
    return jsonify({
        "status": "healthy" if backend_healthy else "degraded",
        "service": "MedXP Middleware 2",
        "version": "1.0.0",
        "backend_connected": backend_healthy,
        "malpractice_agent_available": malpractice_available
    })


@app.route("/api/v1/transcripts", methods=["POST"])
def submit_transcript():
    """
    Submit a transcript for backend enrichment and malpractice analysis.
    
    Receives PatientID and Transcript, replaces the transcript in scn_1.json template,
    forwards it to the backend enrichment API, then passes the enriched result to
    the malpractice agent for compliance/risk analysis.
    
    Expected JSON body:
    {
        "PatientID": "P001",
        "Transcript": "Full session transcript text"
    }
    
    Returns:
        Combined response with backend enrichment and malpractice analysis
    """
    # Validate request content type
    if not request.is_json:
        return jsonify({
            "status": "error",
            "error_code": "INVALID_CONTENT_TYPE",
            "message": "Content-Type must be application/json"
        }), 400
    
    data = request.get_json()
    
    # Validate required fields
    if "PatientID" not in data:
        return jsonify({
            "status": "error",
            "error_code": "MISSING_PATIENT_ID",
            "message": "PatientID is required"
        }), 400
    
    if "Transcript" not in data:
        return jsonify({
            "status": "error",
            "error_code": "MISSING_TRANSCRIPT",
            "message": "Transcript is required"
        }), 400
    
    patient_id = data["PatientID"]
    transcript = data["Transcript"]

    preview = (transcript[:200] + "...") if len(transcript) > 200 else transcript
    _log_session_event("transcripts_request", {
        "patient_id": patient_id,
        "transcript_length": len(transcript),
        "transcript_preview": preview,
    })

    # Log receipt
    print(f"Received transcript for patient: {patient_id}")
    print(f"Transcript length: {len(transcript)} characters")
    
    # Generate enrichment request from template
    enrich_request = generate_enrich_request(patient_id, transcript)
    session_id = enrich_request["session_id"]
    
    print(f"Forwarding to backend: {ENRICH_ENDPOINT}")
    print(f"Session ID: {session_id}")
    
    try:
        # Step 1: Forward to backend enrichment API
        response = httpx.post(
            ENRICH_ENDPOINT,
            json=enrich_request,
            timeout=120.0
        )
        
        if response.status_code != 200:
            _log_session_event("transcripts_response", {
                "session_id": session_id,
                "patient_id": patient_id,
                "status": "error",
                "error_code": "BACKEND_ERROR",
                "message": f"Backend returned status {response.status_code}",
            })
            return jsonify({
                "status": "error",
                "error_code": "BACKEND_ERROR",
                "message": f"Backend returned status {response.status_code}",
                "details": response.text
            }), 502

        backend_response = response.json()
        
        print(f"Backend enrichment complete. Warnings: {len(backend_response.get('warnings', []))}")
        
        # Step 2: Call malpractice agent with enriched context
        print("Calling malpractice agent with enriched context...")
        malpractice_report = call_malpractice_agent(
            transcript=transcript,
            session_id=session_id,
            patient_id=patient_id,
            backend_response=backend_response
        )
        
        print(f"Malpractice analysis complete. Risk level: {malpractice_report.get('risk_level', 'unknown')}")

        _log_session_event("transcripts_response", {
            "session_id": session_id,
            "patient_id": patient_id,
            "status": "success",
            "backend_enrichment_summary": {
                "warnings_count": len(backend_response.get("warnings", [])),
            },
            "malpractice_analysis": {
                "risk_level": malpractice_report.get("risk_level"),
                "compliance_score": malpractice_report.get("compliance_score"),
            },
        })

        # Return combined response
        return jsonify({
            "status": "success",
            "message": "Transcript enriched and analyzed successfully",
            "session_id": session_id,
            "patient_id": patient_id,
            "backend_enrichment": {
                "patient_summary": backend_response.get("patient_summary", {}),
                "relevant_sops": backend_response.get("relevant_sops", []),
                "applicable_policies": backend_response.get("applicable_policies", []),
                "treatment_guidelines": backend_response.get("treatment_guidelines", []),
                "warnings": backend_response.get("warnings", []),
                "metadata": backend_response.get("metadata", {})
            },
            "malpractice_analysis": malpractice_report
        }), 200
        
    except httpx.RequestError as e:
        print(f"Backend request failed: {e}")
        _log_session_event("transcripts_response", {
            "session_id": session_id,
            "patient_id": patient_id,
            "status": "error",
            "error_code": "BACKEND_UNAVAILABLE",
            "message": str(e),
        })
        return jsonify({
            "status": "error",
            "error_code": "BACKEND_UNAVAILABLE",
            "message": f"Failed to connect to backend: {str(e)}"
        }), 503
    except Exception as e:
        print(f"Unexpected error: {e}")
        resp_log = {"patient_id": patient_id, "status": "error", "error_code": "INTERNAL_ERROR", "message": str(e)}
        try:
            resp_log["session_id"] = session_id
        except NameError:
            pass
        _log_session_event("transcripts_response", resp_log)
        return jsonify({
            "status": "error",
            "error_code": "INTERNAL_ERROR",
            "message": str(e)
        }), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
