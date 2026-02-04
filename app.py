"""MedXP Middleware 2 - Flask Application

Simple Flask app for receiving transcript data, forwarding to backend enrichment,
and then passing the enriched context to the malpractice agent.
"""

import json
import uuid
import os
from datetime import datetime
from pathlib import Path

import httpx
from dotenv import load_dotenv
from flask import Flask, request, jsonify

app = Flask(__name__)

# Backend API configuration
BACKEND_URL = "http://127.0.0.1:8000"
ENRICH_ENDPOINT = f"{BACKEND_URL}/api/v1/enrich"

# Load scn_1.json as template
TEMPLATE_PATH = "c:/Users/enact/Projects/MedXP/Data/sample_input/scn_1.json"

# Initialize malpractice agent
load_dotenv(Path(__file__).resolve().parent.parent / ".env")
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
        return jsonify({
            "status": "error",
            "error_code": "BACKEND_UNAVAILABLE",
            "message": f"Failed to connect to backend: {str(e)}"
        }), 503
    except Exception as e:
        print(f"Unexpected error: {e}")
        return jsonify({
            "status": "error",
            "error_code": "INTERNAL_ERROR",
            "message": str(e)
        }), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
