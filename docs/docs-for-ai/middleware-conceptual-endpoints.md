# Conceptual API Endpoints - MVP Version

## Overview

This document describes a minimal, filesystem-driven middleware API for processing nurse-patient session transcripts. The system operates through a single submission endpoint, with data flowing forward to the backend Context Enrichment Agent for clinical knowledge enrichment.

## Data Flow Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         FRONTEND / CLIENT                           │
│                   (Submits transcript JSON)                         │
└─────────────────────────────────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      MIDDLEWARE (Port 5000)                         │
│   POST /transcripts                                                  │
│   ┌─────────────────────────────────────────────────────────────┐   │
│   │ 1. Receive transcript from scenarios.json format            │   │
│   │ 2. Extract patient_id, nurse_id, session_date               │   │
│   │ 3. Generate session_id (UUID)                               │   │
│   │ 4. Save transcript to filesystem                            │   │
│   │ 5. TRANSFORM to backend request format                      │   │
│   │ 6. CALL Backend API (POST http://localhost:8000/api/v1/enrich)│  │
│   │ 7. RECEIVE enriched context with warnings                   │   │
│   │ 8. Save classification results to filesystem                │   │
│   └─────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
                                 │
                                 │ HTTP POST /api/v1/enrich
                                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│                   BACKEND AGENT (Port 8000)                         │
│   Context Enrichment Agent                                           │
│   ┌─────────────────────────────────────────────────────────────┐   │
│   │ • KnowledgeRetriever → SOPs, Policies, Guidelines           │   │
│   │ • LLMClient → Summarize patient context                    │   │
│   │ • WarningGenerator → Clinical alerts                       │   │
│   └─────────────────────────────────────────────────────────────┘   │
│                                 │                                   │
│                                 ▼                                   │
│   Returns: PatientSummary, RelevantSOPs, Policies, Guidelines,      │
│            Warnings (contraindications, drug interactions, etc.)     │
└─────────────────────────────────────────────────────────────────────┘
```

## Base URL

```
http://localhost:5000/api/v1
```

## Single Endpoint

### POST /transcripts

Submit a transcript for processing. This is the only endpoint.

**Headers:**
```
Content-Type: application/json
```

**Request Body (from Data/scenarios.json):**

```json
{
  "PatientID": "P001",
  "PatientName": "Maria Chen",
  "Room": "3E-12",
  "Age": 62,
  "Gender": "Female",
  "Transcript": "Maria Chen in 3E-12, 62 y/o with Stage IIIB non-small cell lung cancer (NSCLC), on chemoradiation. Currently on Enoxaparin (40 mg SQ daily). Most recent vitals at 02:50: T 38.5C, HR 78, RR 22, BP 167/79, SpO2 93%. Latest labs: Hgb 9.7g/dL (N), Troponin 0.11ng/mL (H). Pending: CT chest read; blood cultures still pending. Allergies: NKDA. Code status: Full Code. Tasks for next shift: Follow up CT chest result when available; Assess pain and give PRN opioid if >6/10; Confirm code status with patient/family. Risks to watch: Arrhythmia risk with hypoxia, Respiratory decompensation.",
  "RecordedBy": {
    "StaffID": "N04",
    "Name": "Nurse Sofia Martinez"
  },
  "IncomingRole": "Intern",
  "Timestamp": "02:50:00",
  "Date": "2026-01-30",
  "ShiftContext": "Floor->ICU",
  "ScenarioType": "best_case"
}
```

**What Happens:**

1. Extract `patient_id` from `PatientID` (e.g., P001)
2. Extract `nurse_id` from `RecordedBy.StaffID` (e.g., N04)
3. Extract `session_date` from `Date` (e.g., 2026-01-30)
4. Generate `session_id` as UUID (e.g., 550e8400-e29b-41d4-a716-446655440000)
5. Create directory: `server/data/transcripts/P001/2026-01-30/`
6. Save transcript file
7. **Transform to backend request format** and call backend API
8. Receive enriched context with clinical warnings
9. Save classification file with all enrichment data
10. Return submission confirmation

**Response (200 OK):**

```json
{
  "status": "success",
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "patient_id": "P001",
  "patient_name": "Maria Chen",
  "nurse_id": "N04",
  "session_date": "2026-01-30",
  "transcript_file": "/data/transcripts/P001/2026-01-30/550e8400-....json",
  "classification_file": "/data/transcripts/P001/2026-01-30/550e8400-...._classification.json",
  "warnings_count": 2,
  "sops_count": 1,
  "risk_level": "high"
}
```

**Response (400 Bad Request):**

```json
{
  "status": "error",
  "error_code": "MISSING_FIELD",
  "message": "Missing required field: PatientID"
}
```

---

## Backend Integration

### Middleware-to-Backend Call

The middleware transforms the incoming transcript JSON into a backend request:

**Middleware extracts from scenarios.json:**

```json
{
  "PatientID": "P001",
  "PatientName": "Maria Chen",
  "Transcript": "...",
  "RecordedBy": {"StaffID": "N04", "Name": "Nurse Sofia Martinez"},
  "Date": "2026-01-30"
}
```

**Transforms to backend request format (POST http://localhost:8000/api/v1/enrich):**

```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "patient": {
    "patient_id": "P001",
    "name": "Maria Chen",
    "age": 62,
    "gender": "Female",
    "primary_diagnosis": "Stage IIIB non-small cell lung cancer (NSCLC)",
    "active_problems": ["Hemoptysis", "Pleural effusion", "COPD", "Neutropenia", "Anticoagulation", "Hypoxia"],
    "allergies": ["NKDA"],
    "code_status": "Full Code",
    "current_medications": [
      {"name": "Enoxaparin", "dose": "40 mg SQ daily", "status": "active"}
    ],
    "recent_vitals": {"Temp_C": 38.5, "HR": 78, "RR": 22, "BP_sys": 167, "SpO2": 93}
  },
  "provider": {
    "staff_id": "N04",
    "name": "Nurse Sofia Martinez",
    "role": "RN"
  },
  "transcript": "Maria Chen in 3E-12, 62 y/o with Stage IIIB NSCLC..."
}
```

**Backend Response (Enriched Context):**

```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "enriched_at": "2026-01-30T10:32:00Z",
  "patient_summary": {
    "key_diagnoses": ["Stage IIIB NSCLC", "Hemoptysis", "Neutropenia", "Hypoxia"],
    "risk_factors": [
      "On anticoagulation with active hemoptysis",
      "Hypoxia - monitor respiratory status closely",
      "Neutropenic - high infection risk"
    ],
    "critical_values": [
      {
        "name": "Temperature",
        "value": 38.5,
        "unit": "°C",
        "flag": "H",
        "reference_range": "36.5-38.0°C"
      }
    ]
  },
  "relevant_sops": [
    {
      "sop_id": "SOP-AC-001",
      "title": "Anticoagulation Management with Active Bleeding",
      "relevance_reason": "Patient on Enoxaparin with hemoptysis",
      "key_steps": ["Hold anticoagulation", "Notify physician", "Monitor for bleeding"]
    }
  ],
  "applicable_policies": [],
  "treatment_guidelines": [],
  "warnings": [
    {
      "type": "contraindication",
      "severity": "high",
      "message": "Patient on anticoagulation with active hemoptysis - review need for anticoagulation",
      "evidence": "Active bleeding is a contraindication to anticoagulation",
      "action_required": "Consult physician about holding anticoagulation"
    },
    {
      "type": "clinical_alert",
      "severity": "critical",
      "message": "Temperature 38.5°C in neutropenic patient - requires immediate evaluation",
      "evidence": "Temperature above threshold",
      "action_required": "Blood cultures and broad-spectrum antibiotics within 60 minutes"
    }
  ],
  "metadata": {
    "processing_time_ms": 150,
    "sources_consulted": ["nsclc_sops", "hospital_policies"],
    "llm_calls": 1
  }
}
```

---

## Directory Structure

```
server/data/
└── transcripts/
    └── P001/
        └── 2026-01-30/
            ├── 550e8400-e29b-41d4-a716-446655440000.json          (original transcript)
            └── 550e8400-e29b-41d4-a716-446655440000_classification.json  (enriched output)
```

---

## File Contents

### Transcript File (Input)

```json
{
  "version": "1.0",
  "input_data": {
    "PatientID": "P001",
    "PatientName": "Maria Chen",
    "Room": "3E-12",
    "Age": 62,
    "Gender": "Female",
    "Transcript": "...",
    "RecordedBy": {"StaffID": "N04", "Name": "Nurse Sofia Martinez"},
    "Timestamp": "02:50:00",
    "Date": "2026-01-30",
    "ShiftContext": "Floor->ICU",
    "ScenarioType": "best_case"
  },
  "metadata": {
    "session_id": "550e8400-e29b-41d4-a716-446655440000",
    "patient_id": "P001",
    "nurse_id": "N04",
    "session_date": "2026-01-30",
    "submitted_at": "2026-01-30T10:15:00Z"
  }
}
```

### Classification File (Enriched Output from Backend)

```json
{
  "version": "1.0",
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "patient_id": "P001",
  "patient_name": "Maria Chen",
  "nurse_id": "N04",
  "classification_timestamp": "2026-01-30T10:32:00Z",
  "backend_metadata": {
    "processing_time_ms": 150,
    "sources_consulted": ["nsclc_sops", "hospital_policies"],
    "llm_calls": 1
  },
  "patient_summary": {
    "key_diagnoses": ["Stage IIIB NSCLC", "Hemoptysis", "Neutropenia", "Hypoxia"],
    "risk_factors": [
      "On anticoagulation with active hemoptysis",
      "Hypoxia - monitor respiratory status closely",
      "Neutropenic - high infection risk"
    ],
    "critical_values": [
      {
        "name": "Temperature",
        "value": 38.5,
        "unit": "°C",
        "flag": "H",
        "reference_range": "36.5-38.0°C"
      }
    ]
  },
  "relevant_sops": [
    {
      "sop_id": "SOP-AC-001",
      "title": "Anticoagulation Management with Active Bleeding",
      "relevance_reason": "Patient on Enoxaparin with hemoptysis",
      "key_steps": ["Hold anticoagulation", "Notify physician", "Monitor for bleeding"],
      "priority": "high"
    }
  ],
  "warnings": [
    {
      "type": "contraindication",
      "severity": "high",
      "message": "Patient on anticoagulation with active hemoptysis - review need for anticoagulation",
      "evidence": "Active bleeding is a contraindication to anticoagulation",
      "action_required": "Consult physician about holding anticoagulation"
    },
    {
      "type": "clinical_alert",
      "severity": "critical",
      "message": "Temperature 38.5°C in neutropenic patient - requires immediate evaluation",
      "evidence": "Temperature above threshold",
      "action_required": "Blood cultures and broad-spectrum antibiotics within 60 minutes"
    }
  ]
}
```

---

## Warning Types Generated by Backend

| Type | Severity | Trigger Condition |
|------|----------|-------------------|
| **contraindication** | high | Anticoagulation + active bleeding (hemoptysis) |
| **clinical_alert** | critical | Neutropenia + fever (temp ≥38.0°C) |
| **clinical_alert** | high | Hypoxia (SpO2 < 92%) |
| **allergy** | high | Penicillin allergy + beta-lactam antibiotics |
| **documentation** | medium | Missing code status |
| **drug_interaction** | medium | Opioid + benzodiazepine combination |
| **protocol_trigger** | medium | High-priority SOP conditions met |

---

## Example Flow

```bash
# 1. Submit transcript to middleware
curl -X POST http://localhost:5000/api/v1/transcripts \
  -H "Content-Type: application/json" \
  -d @Data/scenarios.json

# Middleware internally:
# - Saves transcript to /data/transcripts/P001/2026-01-30/{session_id}.json
# - Calls http://localhost:8000/api/v1/enrich with transformed request
# - Receives enriched context with warnings
# - Saves to /data/transcripts/P001/2026-01-30/{session_id}_classification.json

# Response
{
  "status": "success",
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "warnings_count": 2,
  "risk_level": "high"
}
```

---

## Implementation Summary

| Aspect | Description |
|--------|-------------|
| Endpoints | 1 (POST /transcripts) |
| Storage | Filesystem only (no database) |
| Backend Integration | HTTP call to http://localhost:8000/api/v1/enrich |
| File Format | JSON |
| Structure | patient_id/date/session_id.json |
| Output Files | transcript (input), classification (enriched output) |

---

## File Naming Rules

| Component | Format | Example |
|-----------|--------|---------|
| Patient | P + 3 digits | P001, P002 |
| Date | YYYY-MM-DD | 2026-01-30 |
| Session ID | UUID | 550e8400-e29b-41d4-a716-446655440000 |
| Transcript File | {patient}_{date}_{session_id}.json | P001_2026-01-30_550e8400-....json |
| Classification File | {patient}_{date}_{session_id}_classification.json | P001_2026-01-30_550e8400-...._classification.json |
