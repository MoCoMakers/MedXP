"""
MedXP Streamlit Frontend

A Streamlit-based interface for medical handoff transcription, validation, and patient timeline visualization.

Features:
- Audio file upload and recording
- Speech-to-text transcription using OpenAI Whisper
- Transcript validation via backend enrichment API
- Patient timeline with clinical warnings
- SBAR handoff card generation
"""

import os
import json
import uuid
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Optional

import streamlit as st
import httpx
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
BACKEND_URL = os.environ.get("BACKEND_URL", "http://127.0.0.1:8000")
MIDDLEWARE_URL = os.environ.get("MIDDLEWARE_URL", "http://127.0.0.1:5001")
TRANSCRIPT_API_URL = os.environ.get("TRANSCRIPT_API_URL", "http://127.0.0.1:8000")

# Page configuration
st.set_page_config(
    page_title="MedXP - Medical Handoff System",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",
)


# Sample patient data (inspired by frontend mockData.ts)
SAMPLE_PATIENTS = [
    {
        "id": "P001",
        "name": "Johnson, Mary",
        "room": "412A",
        "mrn": "MRN-78432",
        "age": 67,
        "gender": "F",
        "primary_diagnosis": "Community-acquired pneumonia",
        "active_problems": ["Pneumonia", "COPD", "Hypertension", "Type 2 Diabetes"],
        "allergies": ["Penicillin"],
        "code_status": "DNR/DNI",
        "recent_vitals": {
            "temp_c": 37.8,
            "bp_sys": 128,
            "bp_dia": 78,
            "hr": 92,
            "spo2": 94,
        },
        "recent_labs": [
            {"name": "WBC", "value": 14.2, "unit": "K/uL"},
            {"name": "Creatinine", "value": 1.1, "unit": "mg/dL"},
        ],
    },
    {
        "id": "P002",
        "name": "Chen, Robert",
        "room": "418B",
        "mrn": "MRN-91205",
        "age": 52,
        "gender": "M",
        "primary_diagnosis": "Post-CABG day 2",
        "active_problems": ["Coronary artery disease", "Hyperlipidemia"],
        "allergies": [],
        "code_status": "Full code",
        "recent_vitals": {
            "temp_c": 37.2,
            "bp_sys": 118,
            "bp_dia": 72,
            "hr": 78,
            "spo2": 98,
        },
        "recent_labs": [
            {"name": "Hemoglobin", "value": 9.8, "unit": "g/dL"},
            {"name": "Creatinine", "value": 0.9, "unit": "mg/dL"},
        ],
    },
    {
        "id": "P003",
        "name": "Williams, Sarah",
        "room": "421",
        "mrn": "MRN-65891",
        "age": 34,
        "gender": "F",
        "primary_diagnosis": "Post-laparoscopic appendectomy",
        "active_problems": ["Acute appendicitis"],
        "allergies": [],
        "code_status": "Full code",
        "recent_vitals": {
            "temp_c": 37.0,
            "bp_sys": 115,
            "bp_dia": 70,
            "hr": 72,
            "spo2": 99,
        },
        "recent_labs": [],
    },
]


def init_session_state():
    """Initialize Streamlit session state."""
    if "transcript" not in st.session_state:
        st.session_state.transcript = ""
    if "audio_file" not in st.session_state:
        st.session_state.audio_file = None
    if "transcript_saved" not in st.session_state:
        st.session_state.transcript_saved = False
    if "enrichment_result" not in st.session_state:
        st.session_state.enrichment_result = None
    if "selected_patient" not in st.session_state:
        st.session_state.selected_patient = None
    if "timeline_events" not in st.session_state:
        st.session_state.timeline_events = []


def transcribe_audio(audio_path: str) -> str:
    """
    Transcribe audio file using OpenAI Whisper API.

    Args:
        audio_path: Path to the audio file

    Returns:
        Transcribed text
    """
    try:
        with open(audio_path, "rb") as audio_file:
            files = {"audio": audio_file}
            data = {"language": "en"}
            response = httpx.post(
                f"{TRANSCRIPT_API_URL}/api/transcribe",
                files=files,
                data=data,
                timeout=120.0,
            )
            response.raise_for_status()
            result = response.json()
            return result.get("transcript", "")
    except Exception as e:
        st.error(f"Transcription error: {e}")
        return ""


def validate_transcript(patient_id: str, transcript: str) -> dict:
    """
    Submit transcript for validation and enrichment.

    Args:
        patient_id: Patient identifier
        transcript: The transcript text

    Returns:
        Enrichment response from backend
    """
    try:
        response = httpx.post(
            f"{MIDDLEWARE_URL}/api/v1/transcripts",
            json={"PatientID": patient_id, "Transcript": transcript},
            timeout=120.0,
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Validation error: {e}")
        return {"status": "error", "message": str(e)}


def save_transcript_to_file(transcript: str, patient_id: str) -> str:
    """
    Save transcript to a text file.

    Args:
        transcript: The transcript text
        patient_id: Patient identifier

    Returns:
        Path to the saved file
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"transcript_{patient_id}_{timestamp}.txt"
    output_dir = Path(__file__).parent / "transcripts"
    output_dir.mkdir(exist_ok=True)
    filepath = output_dir / filename

    with open(filepath, "w") as f:
        f.write(f"Patient ID: {patient_id}\n")
        f.write(f"Timestamp: {datetime.now().isoformat()}\n")
        f.write("-" * 50 + "\n\n")
        f.write(transcript)

    return str(filepath)


def render_patient_selector() -> dict:
    """Render patient selection component."""
    st.subheader("👤 Select Patient")

    patient_options = [f"{p['name']} - Room {p['room']} ({p['mrn']})" for p in SAMPLE_PATIENTS]
    patient_options.insert(0, "-- Select a patient --")

    selected_option = st.selectbox("Patient", patient_options, key="patient_select")

    if selected_option and selected_option != "-- Select a patient --":
        index = patient_options.index(selected_option) - 1
        return SAMPLE_PATIENTS[index]

    return None


def render_recording_section() -> Optional[str]:
    """Render audio recording/upload section."""
    st.subheader("🎤 Audio Input")

    tab1, tab2 = st.tabs(["📁 Upload File", "🎙️ Record"])

    with tab1:
        uploaded_file = st.file_uploader(
            "Upload audio file",
            type=["wav", "mp3", "m4a", "webm", "ogg"],
            help="Supported formats: WAV, MP3, M4A, WebM, OGG",
        )
        if uploaded_file:
            # Save to temp file
            with tempfile.NamedTemporaryFile(
                delete=False, suffix=f".{uploaded_file.name.split('.')[-1]}"
            ) as tmp:
                tmp.write(uploaded_file.getvalue())
                return tmp.name

    with tab2:
        st.info("🎙️ Recording not available in browser. Please upload a file or use a microphone app.")
        st.markdown("""
        **Tip:** Use an external recording app and upload the file.
        - Voice Memos (iOS)
        - Voice Recorder (Android)
        - Audacity (Desktop)
        """)

    return None


def render_transcript_editor(transcript: str) -> str:
    """Render transcript editing section."""
    st.subheader("📝 Transcript")

    if transcript:
        edited_transcript = st.text_area(
            "Edit transcript if needed:",
            value=transcript,
            height=200,
            help="Review and edit the transcribed text",
        )
        return edited_transcript
    else:
        st.info("No transcript available. Upload an audio file to begin.")
        return ""


def render_sbar_card(situation: str, background: str, assessment: str, recommendation: str):
    """Render SBAR card display."""
    st.subheader("📋 SBAR Handoff Card")

    sbar_sections = [
        ("S - Situation", situation, "info"),
        ("B - Background", background, "primary"),
        ("A - Assessment", assessment, "warning"),
        ("R - Recommendation", recommendation, "success"),
    ]

    for label, content, color in sbar_sections:
        st.markdown(f"**{label}**")
        st.info(content) if color == "info" else st.warning(content) if color == "warning" else st.success(content)
        st.markdown("")


def render_warnings(warnings: list):
    """Render clinical warnings section."""
    if warnings:
        st.subheader("⚠️ Clinical Warnings")

        for i, warning in enumerate(warnings):
            severity = warning.get("severity", "medium")
            severity_emoji = {"critical": "🔴", "high": "🟠", "medium": "🟡", "low": "🟢"}

            with st.expander(f"{severity_emoji.get(severity, '⚠️')} {warning.get('message', 'Warning')}", expanded=True):
                st.markdown(f"**Type:** {warning.get('type', 'N/A')}")
                st.markdown(f"**Severity:** {severity.upper()}")
                st.markdown(f"**Evidence:** {warning.get('evidence', 'N/A')}")
                st.markdown(f"**Action Required:** {warning.get('action_required', 'N/A')}")


def render_timeline(events: list):
    """Render patient timeline with warnings and events."""
    st.subheader("📅 Patient Timeline")

    if not events:
        st.info("No timeline events yet. Submit a transcript to generate timeline events.")
        return

    # Sort events by timestamp (most recent first)
    sorted_events = sorted(events, key=lambda x: x.get("timestamp", ""), reverse=True)

    for event in sorted_events:
        event_type = event.get("type", "info")
        event_icons = {
            "warning": "⚠️",
            "transcript": "📝",
            "medication": "💊",
            "vital": "🩺",
            "lab": "🔬",
            "procedure": "🏥",
        }

        icon = event_icons.get(event_type, "📌")
        timestamp = event.get("timestamp", "Unknown time")
        description = event.get("description", "No description")

        with st.container():
            col1, col2 = st.columns([1, 10])
            with col1:
                st.markdown(f"### {icon}")
            with col2:
                st.markdown(f"**{timestamp}**")
                st.markdown(description)

        if event != sorted_events[-1]:
            st.markdown("---")


def render_enrichment_results(result: dict):
    """Render full enrichment results."""
    if not result or result.get("status") != "success":
        st.error("No valid enrichment results to display.")
        return

    st.divider()

    # Backend enrichment section
    backend_enrichment = result.get("backend_enrichment", {})
    warnings = backend_enrichment.get("warnings", [])

    # Render warnings
    render_warnings(warnings)

    # Render patient summary
    patient_summary = backend_enrichment.get("patient_summary", {})
    if patient_summary:
        st.subheader("📊 Patient Summary")
        key_diagnoses = patient_summary.get("key_diagnoses", [])
        risk_factors = patient_summary.get("risk_factors", [])

        if key_diagnoses:
            st.markdown("**Key Diagnoses:**")
            for dx in key_diagnoses:
                st.markdown(f"- {dx}")

        if risk_factors:
            st.markdown("**Risk Factors:**")
            for rf in risk_factors:
                st.markdown(f"- {rf}")

    # Render relevant SOPs
    relevant_sops = backend_enrichment.get("relevant_sops", [])
    if relevant_sops:
        st.subheader("📚 Relevant SOPs")
        for sop in relevant_sops:
            with st.expander(f"SOP: {sop.get('title', 'Unknown')}"):
                st.markdown(f"**ID:** {sop.get('sop_id', 'N/A')}")
                st.markdown(f"**Priority:** {sop.get('priority', 'N/A')}")
                st.markdown(f"**Relevance:** {sop.get('relevance_reason', 'N/A')}")

    # Render malpractice analysis
    malpractice = result.get("malpractice_analysis", {})
    if malpractice and malpractice.get("status") == "success":
        st.subheader("⚖️ Risk Assessment")
        risk_level = malpractice.get("risk_level", "unknown")
        compliance_score = malpractice.get("compliance_score")

        col1, col2 = st.columns(2)
        with col1:
            st.metric("Risk Level", risk_level.upper())
        with col2:
            if compliance_score:
                st.metric("Compliance Score", f"{compliance_score:.1%}")

        st.markdown("**Executive Summary:**")
        st.markdown(malpractice.get("executive_summary", "No summary available"))

        key_concerns = malpractice.get("key_concerns", [])
        if key_concerns:
            st.markdown("**Key Concerns:**")
            for concern in key_concerns:
                st.markdown(f"- {concern}")

        st.markdown("**Recommended Action:**")
        st.info(malpractice.get("recommended_action", "No recommendation"))


def main():
    """Main application entry point."""
    init_session_state()

    # Sidebar
    with st.sidebar:
        st.title("🏥 MedXP")
        st.caption("Medical Handoff System")

        st.markdown("---")

        # Navigation
        page = st.radio(
            "Navigate",
            ["📝 New Handoff", "📅 Timeline", "👥 Patients"],
        )

        st.markdown("---")

        # Settings
        st.subheader("Settings")
        backend_url = st.text_input("Backend URL", value=BACKEND_URL, key="backend_url")
        middleware_url = st.text_input("Middleware URL", value=MIDDLEWARE_URL, key="middleware_url")

        st.markdown("---")

        st.caption("v1.0.0 | MedXP Streamlit Frontend")

    # Main content based on navigation
    if page == "📝 New Handoff":
        render_new_handoff_page()
    elif page == "📅 Timeline":
        render_timeline_page()
    elif page == "👥 Patients":
        render_patients_page()


def render_new_handoff_page():
    """Render the new handoff recording page."""
    st.title("📝 Record Handoff")
    st.markdown("Upload or record a handoff transcript for validation and analysis.")

    # Patient selection
    selected_patient = render_patient_selector()
    if selected_patient:
        st.session_state.selected_patient = selected_patient

    # Audio input
    audio_path = render_recording_section()

    # Transcription
    if audio_path and st.button("🎙️ Transcribe Audio", type="primary"):
        with st.spinner("Transcribing audio..."):
            transcript = transcribe_audio(audio_path)
            if transcript:
                st.session_state.transcript = transcript
                st.success("Transcription complete!")

    # Transcript editing
    edited_transcript = render_transcript_editor(st.session_state.transcript)
    if edited_transcript != st.session_state.transcript:
        st.session_state.transcript = edited_transcript

    # Save transcript
    if st.session_state.transcript and st.button("💾 Save Transcript"):
        if selected_patient:
            filepath = save_transcript_to_file(
                st.session_state.transcript, selected_patient["id"]
            )
            st.session_state.transcript_saved = True
            st.success(f"Transcript saved to: {filepath}")
        else:
            st.error("Please select a patient first.")

    # Validate and analyze
    if st.session_state.transcript and st.button("✅ Validate & Analyze"):
        if selected_patient:
            with st.spinner("Validating transcript and generating analysis..."):
                result = validate_transcript(
                    selected_patient["id"], st.session_state.transcript
                )
                st.session_state.enrichment_result = result

                # Add to timeline
                st.session_state.timeline_events.append({
                    "type": "transcript",
                    "timestamp": datetime.now().isoformat(),
                    "description": f"Handoff recorded for {selected_patient['name']}",
                })

                if result.get("status") == "success":
                    st.success("Validation complete!")

                    # Add warnings to timeline
                    warnings = result.get("backend_enrichment", {}).get("warnings", [])
                    for warning in warnings:
                        st.session_state.timeline_events.append({
                            "type": "warning",
                            "timestamp": datetime.now().isoformat(),
                            "description": f"Warning: {warning.get('message', 'Clinical alert')}",
                        })
                else:
                    st.error(f"Validation failed: {result.get('message', 'Unknown error')}")
        else:
            st.error("Please select a patient first.")

    # Display results
    if st.session_state.enrichment_result:
        render_enrichment_results(st.session_state.enrichment_result)


def render_timeline_page():
    """Render the patient timeline page."""
    st.title("📅 Patient Timeline")
    st.markdown("View all handoffs and clinical events for tracked patients.")

    # Show timeline events
    render_timeline(st.session_state.timeline_events)

    # Show recent events from sample data
    st.divider()
    st.subheader("📌 Sample Events")

    sample_events = [
        {
            "type": "medication",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "description": "Levaquin 750mg IV administered",
        },
        {
            "type": "vital",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "description": "Vitals: T 37.8°C, BP 128/78, HR 92, SpO2 94%",
        },
        {
            "type": "lab",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "description": "Labs: WBC 14.2, Creatinine 1.1",
        },
    ]

    render_timeline(sample_events)


def render_patients_page():
    """Render the patients overview page."""
    st.title("👥 Patient Overview")
    st.markdown("View and manage patient information.")

    for patient in SAMPLE_PATIENTS:
        with st.expander(f"{patient['name']} - Room {patient['room']}", expanded=True):
            col1, col2 = st.columns(2)

            with col1:
                st.markdown(f"**MRN:** {patient['mrn']}")
                st.markdown(f"**Age/Gender:** {patient['age']}/{patient['gender']}")
                st.markdown(f"**Primary Diagnosis:** {patient['primary_diagnosis']}")
                st.markdown(f"**Code Status:** {patient['code_status']}")

            with col2:
                st.markdown("**Active Problems:**")
                for problem in patient["active_problems"]:
                    st.markdown(f"- {problem}")

                st.markdown("**Allergies:**")
                if patient["allergies"]:
                    for allergy in patient["allergies"]:
                        st.markdown(f"- {allergy}")
                else:
                    st.markdown("_No known allergies_")

            # Vitals
            vitals = patient.get("recent_vitals", {})
            if vitals:
                st.markdown("**Recent Vitals:**")
                st.json(vitals)

            # Labs
            labs = patient.get("recent_labs", [])
            if labs:
                st.markdown("**Recent Labs:**")
                for lab in labs:
                    st.markdown(f"- {lab['name']}: {lab['value']} {lab['unit']}")


if __name__ == "__main__":
    main()
