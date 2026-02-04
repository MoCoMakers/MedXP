import requests
import json

# Test the transcript endpoint with full pipeline
# Using transcript from Data/scenarios.json (P001, Scenarios[0])
response = requests.post(
    "http://localhost:5001/api/v1/transcripts",
    json={
        "PatientID": "P001",
        "Transcript": "Maria Chen in 3E-12, 62 y/o with Stage IIIB non-small cell lung cancer (NSCLC), on chemoradiation. Currently on Enoxaparin (40 mg SQ daily) and Enoxaparin (40 mg SQ daily). Most recent vitals at 02:50: T 38.5C, HR 78, RR 22, BP 167/79, SpO2 93%. Latest labs: Hgb 9.7g/dL (N), Troponin 0.11ng/mL (H). Pending: CT chest read; blood cultures still pending. Allergies: NKDA. Code status: Full Code. Tasks for next shift: Follow up CT chest result when available; Assess pain and give PRN opioid if >6/10; Confirm code status with patient/family. Risks to watch: Arrhythmia risk with hypoxia, Respiratory decompensation."
    }
)

print(f"Status: {response.status_code}")
result = response.json()

# Build structured output with all analysis results
structured_output = {
    "session_id": result.get("session_id"),
    "patient_id": result.get("patient_id"),
    "status": result.get("status"),
    "analysis": {
        "backend_enrichment": result.get("backend_enrichment", {}),
        "malpractice_analysis": result.get("malpractice_analysis", {})
    },
    "warnings_summary": {
        "total_count": len(result.get("backend_enrichment", {}).get("warnings", [])),
        "by_severity": {},
        "by_type": {}
    }
}

# Process warnings into structured summary
warnings = result.get("backend_enrichment", {}).get("warnings", [])
for w in warnings:
    # By severity
    severity = w.get("severity", "unknown")
    structured_output["warnings_summary"]["by_severity"][severity] = \
        structured_output["warnings_summary"]["by_severity"].get(severity, 0) + 1
    
    # By type
    warning_type = w.get("type", "unknown")
    if warning_type not in structured_output["warnings_summary"]["by_type"]:
        structured_output["warnings_summary"]["by_type"][warning_type] = []
    structured_output["warnings_summary"]["by_type"][warning_type].append({
        "message": w.get("message"),
        "severity": severity,
        "action_required": w.get("action_required"),
        "evidence": w.get("evidence")
    })

# Print structured output as JSON
print("\n" + "=" * 60)
print("STRUCTURED OUTPUT (JSON)")
print("=" * 60)
print(json.dumps(structured_output, indent=2))

# Also print detailed warnings
print("\n" + "=" * 60)
print("DETAILED WARNINGS")
print("=" * 60)
for w in warnings:
    print(f"\n[{w.get('severity').upper()}] {w.get('type')}")
    print(f"  Message: {w.get('message')}")
    print(f"  Evidence: {w.get('evidence')}")
    print(f"  Action: {w.get('action_required')}")