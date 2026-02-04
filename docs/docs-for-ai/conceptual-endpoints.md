# Conceptual API Endpoints - Filesystem-Driven Architecture

## Overview

This document describes the conceptual API endpoints for a filesystem-driven middleware system. All data is stored in the filesystem using structured JSON files, with naming conventions that include patient identifiers and session timestamps for easy organization and retrieval.

The system processes nurse-patient session transcripts, applies AI-based classification, and stores results using a predictable file structure. No database is required—all operations are performed directly on the filesystem.

## Base URL

All endpoints are relative to the server root. The base URL structure is:

```
http://localhost:5000/api/v1
```

## Storage Structure

### Directory Organization

```
server/
├── data/
│   ├── transcripts/
│   │   └── {patient_id}/
│   │       └── {YYYY-MM-DD}/
│   │           ├── {session_id}.json
│   │           └── {session_id}_classification.json
│   ├── nurse/
│   │   └── profile.json
│   └── patients/
│       └── {patient_id}/
│           └── profile.json
├── processed/
│   └── {patient_id}/
│       └── {YYYY-MM-DD}/
│           └── {session_id}_tags.json
```

### File Naming Convention

- **Transcript files**: `{patient_id}_{YYYY-MM-DD}_{session_id}.json`
- **Classification files**: `{patient_id}_{YYYY-MM-DD}_{session_id}_classification.json`
- **Tag files**: `{patient_id}_{YYYY-MM-DD}_{session_id}_tags.json`

### Example Structure

Given a session with:
- Patient ID: `P001`
- Session Date: `2026-01-30`
- Session ID: `550e8400-e29b-41d4-a716-446655440000`

The files would be:
```
server/data/transcripts/P001/2026-01-30/
├── 550e8400-e29b-41d4-a716-446655440000.json
├── 550e8400-e29b-41d4-a716-446655440000_classification.json
└── 550e8400-e29b-41d4-a716-446655440000_tags.json
```

## Endpoints

### Health Check

#### GET /health

Health check endpoint to verify the server is running.

**Response (200 OK):**
```json
{
  "status": "healthy",
  "service": "medxp-middleware",
  "version": "1.0.0"
}
```

---

### Transcript Processing

#### POST /transcripts/process

Submit a transcript for processing. The transcript is saved to the filesystem and queued for classification.

**Request Headers:**
```
Content-Type: application/json
```

**Request Body:**
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "patient_id": "P001",
  "patient_name": "Maria Chen",
  "nurse_id": "N04",
  "nurse_name": "Nurse Sofia Martinez",
  "transcript_text": "Maria Chen in 3E-12, 62 y/o with Stage IIIB non-small cell lung cancer...",
  "session_timestamp": "2026-01-30T02:50:00",
  "shift_context": "Floor->ICU",
  "room": "3E-12",
  "scenario_type": "best_case"
}
```

**Field Descriptions:**
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| session_id | string | Yes | Unique UUID for the session |
| patient_id | string | Yes | Patient identifier (e.g., P001) |
| patient_name | string | No | Patient full name |
| nurse_id | string | Yes | Nurse identifier (e.g., N04) |
| nurse_name | string | No | Nurse full name |
| transcript_text | string | Yes | Full transcript content |
| session_timestamp | string | No | ISO 8601 timestamp |
| shift_context | string | No | Context of shift change |
| room | string | No | Patient room number |
| scenario_type | string | No | Type of scenario (best_case, worst_case) |

**Response (202 Accepted):**
```json
{
  "status": "accepted",
  "message": "Transcript submitted for processing",
  "job_id": "task-12345",
  "transcript_id": "550e8400-e29b-41d4-a716-446655440000",
  "file_path": "/data/transcripts/P001/2026-01-30/550e8400-e29b-41d4-a716-446655440000.json",
  "estimated_processing_time_seconds": 30
}
```

**Response (400 Bad Request):**
```json
{
  "status": "error",
  "error_code": "VALIDATION_ERROR",
  "message": "Missing required field: transcript_text"
}
```

---

#### GET /transcripts/{patient_id}

List all transcripts for a specific patient.

**Path Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| patient_id | string | Patient identifier (e.g., P001) |

**Query Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| date | string | - | Filter by date (YYYY-MM-DD) |
| limit | integer | 20 | Maximum results to return |
| offset | integer | 0 | Pagination offset |

**Response (200 OK):**
```json
{
  "status": "success",
  "patient_id": "P001",
  "total_count": 5,
  "transcripts": [
    {
      "session_id": "550e8400-e29b-41d4-a716-446655440000",
      "session_timestamp": "2026-01-30T02:50:00",
      "nurse_id": "N04",
      "nurse_name": "Nurse Sofia Martinez",
      "file_path": "/data/transcripts/P001/2026-01-30/550e8400-e29b-41d4-a716-446655440000.json",
      "classification_exists": true,
      "tags_exists": true
    }
  ]
}
```

---

#### GET /transcripts/{patient_id}/{session_id}

Get a specific transcript by patient and session ID.

**Path Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| patient_id | string | Patient identifier |
| session_id | string | Session UUID |

**Response (200 OK):**
```json
{
  "status": "success",
  "transcript": {
    "session_id": "550e8400-e29b-41d4-a716-446655440000",
    "patient_id": "P001",
    "patient_name": "Maria Chen",
    "nurse_id": "N04",
    "nurse_name": "Nurse Sofia Martinez",
    "transcript_text": "Maria Chen in 3E-12, 62 y/o with Stage IIIB non-small cell lung cancer...",
    "session_timestamp": "2026-01-30T02:50:00",
    "shift_context": "Floor->ICU",
    "room": "3E-12",
    "scenario_type": "best_case",
    "created_at": "2026-01-30T10:15:00Z"
  }
}
```

**Response (404 Not Found):**
```json
{
  "status": "error",
  "error_code": "TRANSCRIPT_NOT_FOUND",
  "message": "Transcript P001/550e8400-e29b-41d4-a716-446655440000 not found"
}
```

---

#### GET /transcripts/{patient_id}/{session_id}/classification

Get classification results for a specific transcript.

**Path Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| patient_id | string | Patient identifier |
| session_id | string | Session UUID |

**Response (200 OK):**
```json
{
  "status": "success",
  "classification": {
    "session_id": "550e8400-e29b-41d4-a716-446655440000",
    "patient_id": "P001",
    "classification_timestamp": "2026-01-30T10:32:00Z",
    "tags": [
      "pain_assessment",
      "medication_review",
      "vital_signs"
    ],
    "categories": [
      {
        "name": "clinical_assessment",
        "confidence": 0.92
      },
      {
        "name": "care_coordination",
        "confidence": 0.78
      }
    ],
    "risk_level": "low",
    "sentiment": {
      "overall": "neutral",
      "confidence": 0.85
    },
    "topics": [
      {
        "name": "Medication Management",
        "confidence": 0.87,
        "key_phrases": ["prescription refill", "take with food"]
      }
    ],
    "entities": {
      "medications": [
        {
          "name": "Enoxaparin",
          "dosage": "40 mg SQ daily",
          "context": "anticoagulation"
        }
      ],
      "symptoms": [],
      "procedures": ["vital signs check"],
      "care_instructions": ["Follow up in 2 weeks"]
    }
  }
}
```

---

### Nurse Endpoints

#### GET /nurse/profile

Get the current nurse profile (single-user POC).

**Response (200 OK):**
```json
{
  "status": "success",
  "profile": {
    "nurse_id": "N04",
    "name": "Nurse Sofia Martinez",
    "email": "sofia.martinez@hospital.org",
    "employee_id": "EMP-001",
    "department": "Oncology",
    "shift_pattern": "Day Shift",
    "certifications": ["RN", "OCN"],
    "statistics": {
      "total_sessions_processed": 0,
      "average_risk_score": 0.0,
      "high_risk_sessions": 0
    }
  }
}
```

---

#### PUT /nurse/profile

Update the nurse profile.

**Request Body:**
```json
{
  "email": "new.email@hospital.org",
  "shift_pattern": "Night Shift",
  "settings": {
    "auto_process_transcripts": true,
    "notification_preferences": {
      "email": true,
      "risk_threshold": "medium"
    }
  }
}
```

**Response (200 OK):**
```json
{
  "status": "success",
  "message": "Profile updated successfully"
}
```

---

#### GET /nurse/statistics

Get processing statistics for the nurse.

**Response (200 OK):**
```json
{
  "status": "success",
  "statistics": {
    "nurse_id": "N04",
    "total_sessions_processed": 156,
    "today_sessions": 12,
    "average_risk_score": 0.23,
    "high_risk_sessions": 3,
    "risk_breakdown": {
      "low": 120,
      "medium": 28,
      "high": 6,
      "critical": 2
    },
    "top_tags": [
      {"tag": "pain_assessment", "count": 45},
      {"tag": "medication_review", "count": 38},
      {"tag": "vital_signs", "count": 32}
    ]
  }
}
```

---

### Patient Endpoints

#### GET /patients

List all patients.

**Response (200 OK):**
```json
{
  "status": "success",
  "total_count": 2,
  "patients": [
    {
      "patient_id": "P001",
      "name": "Maria Chen",
      "room": "3E-12",
      "total_sessions": 5,
      "last_session": "2026-01-30T18:40:00"
    },
    {
      "patient_id": "P002",
      "name": "James Walker",
      "room": "3E-15",
      "total_sessions": 3,
      "last_session": "2026-01-29T14:20:00"
    }
  ]
}
```

---

#### GET /patients/{patient_id}

Get a specific patient's profile and session history.

**Path Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| patient_id | string | Patient identifier |

**Response (200 OK):**
```json
{
  "status": "success",
  "patient": {
    "patient_id": "P001",
    "name": "Maria Chen",
    "room": "3E-12",
    "age": 62,
    "gender": "Female",
    "primary_diagnosis": "Stage IIIB non-small cell lung cancer (NSCLC)",
    "allergies": ["NKDA"],
    "code_status": "Full Code",
    "active_problems": [
      "Hemoptysis",
      "Pleural effusion",
      "COPD"
    ],
    "current_medications": [
      {
        "name": "Enoxaparin",
        "dose": "40 mg SQ daily",
        "status": "active"
      }
    ],
    "total_sessions": 5,
    "session_history": [
      {
        "session_id": "550e8400-e29b-41d4-a716-446655440000",
        "timestamp": "2026-01-30T02:50:00",
        "nurse_id": "N04",
        "risk_level": "low"
      }
    ]
  }
}
```

---

#### GET /patients/{patient_id}/sessions

Get all sessions for a specific patient.

**Path Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| patient_id | string | Patient identifier |

**Query Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| start_date | string | Filter from date (YYYY-MM-DD) |
| end_date | string | Filter to date (YYYY-MM-DD) |
| risk_level | string | Filter by risk level |

**Response (200 OK):**
```json
{
  "status": "success",
  "patient_id": "P001",
  "total_count": 5,
  "sessions": [
    {
      "session_id": "550e8400-e29b-41d4-a716-446655440000",
      "timestamp": "2026-01-30T02:50:00",
      "nurse_id": "N04",
      "risk_level": "low",
      "tags": ["pain_assessment", "medication_review", "vital_signs"],
      "transcript_exists": true,
      "classification_exists": true
    }
  ]
}
```

---

### Classification Endpoints

#### GET /classification/{patient_id}/{session_id}

Get classification data for a session.

**Path Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| patient_id | string | Patient identifier |
| session_id | string | Session UUID |

**Response (200 OK):**
```json
{
  "status": "success",
  "classification": {
    "session_id": "550e8400-e29b-41d4-a716-446655440000",
    "patient_id": "P001",
    "processed_at": "2026-01-30T10:32:00Z",
    "tags": ["pain_assessment", "medication_review", "vital_signs"],
    "categories": [
      {"name": "clinical_assessment", "confidence": 0.92},
      {"name": "care_coordination", "confidence": 0.78}
    ],
    "risk_level": "low",
    "sentiment": {
      "overall": "neutral",
      "confidence": 0.85
    }
  }
}
```

---

#### GET /classification/{patient_id}/{session_id}/tags

Get tags for a specific session.

**Path Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| patient_id | string | Patient identifier |
| session_id | string | Session UUID |

**Response (200 OK):**
```json
{
  "status": "success",
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "patient_id": "P001",
  "tags": [
    {
      "name": "pain_assessment",
      "confidence": 0.95,
      "extracted_from": "Assess pain and give PRN opioid if >6/10"
    },
    {
      "name": "medication_review",
      "confidence": 0.88,
      "extracted_from": "Currently on Enoxaparin (40 mg SQ daily)"
    },
    {
      "name": "vital_signs",
      "confidence": 0.82,
      "extracted_from": "T 38.5C, HR 78, RR 22, BP 167/79, SpO2 93%"
    }
  ]
}
```

---

#### GET /classification/search

Search classifications across sessions.

**Query Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| tag | string | Filter by tag name |
| risk_level | string | Filter by risk level |
| patient_id | string | Filter by patient |
| start_date | string | Filter from date |
| end_date | string | Filter to date |
| limit | integer | Max results (default 20) |
| offset | integer | Pagination offset |

**Response (200 OK):**
```json
{
  "status": "success",
  "total_count": 3,
  "results": [
    {
      "session_id": "550e8400-e29b-41d4-a716-446655440000",
      "patient_id": "P001",
      "patient_name": "Maria Chen",
      "timestamp": "2026-01-30T02:50:00",
      "tags": ["pain_assessment", "medication_review"],
      "risk_level": "low",
      "matched_tag": "medication_review",
      "match_confidence": 0.88
    }
  ]
}
```

---

### Analysis Endpoints

#### POST /analyze/compare

Compare a transcript classification with medical standards.

**Request Body:**
```json
{
  "patient_id": "P001",
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "compare_with": ["pain_management", "medication_safety"]
}
```

**Response (200 OK):**
```json
{
  "status": "success",
  "analysis": {
    "session_id": "550e8400-e29b-41d4-a716-446655440000",
    "patient_id": "P001",
    "standards_reviewed": 2,
    "compliance_score": 0.95,
    "findings": [
      {
        "standard": "pain_management",
        "category": "Pain Assessment",
        "description": "All patients should receive pain assessment using a standardized scale",
        "compliant": true,
        "evidence": "Nurse assessed pain using 1-10 scale"
      },
      {
        "standard": "medication_safety",
        "category": "Medication Reconciliation",
        "description": "Complete medication reconciliation within 24 hours",
        "compliant": true,
        "evidence": "Current medications documented: Enoxaparin 40mg daily"
      }
    ],
    "gaps_identified": 0,
    "recommendations": []
  }
}
```

---

#### GET /analyze/patient/{patient_id}/summary

Get analysis summary for a patient across all sessions.

**Path Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| patient_id | string | Patient identifier |

**Response (200 OK):**
```json
{
  "status": "success",
  "patient_id": "P001",
  "summary": {
    "total_sessions": 5,
    "risk_trend": "stable",
    "average_risk_score": 0.25,
    "top_concerns": [
      {
        "category": "Medication Management",
        "occurrences": 4,
        "trend": "stable"
      },
      {
        "category": "Pain Assessment",
        "occurrences": 3,
        "trend": "increasing"
      }
    ],
    "session_patterns": {
      "most_common_tags": ["medication_review", "vital_signs", "pain_assessment"],
      "average_session_duration_minutes": 25,
      "preferred_shift": "Night Shift"
    },
    "care_recommendations": [
      "Continue monitoring pain levels every 4 hours",
      "Review anticoagulation therapy effectiveness"
    ]
  }
}
```

---

### Search Endpoints

#### GET /search/transcripts

Search across all transcripts.

**Query Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| q | string | Search query |
| patient_id | string | Filter by patient |
| nurse_id | string | Filter by nurse |
| date | string | Filter by date |
| limit | integer | Max results |

**Response (200 OK):**
```json
{
  "status": "success",
  "total_count": 2,
  " {
      "sessionresults": [
   _id": "550e8400-e29b-41d4-a716-446655440000",
      "patient_id": "P001",
      "patient_name": "Maria Chen",
      "nurse_id": "N04",
      "nurse_name": "Nurse Sofia Martinez",
      "timestamp": "2026-01-30T02:50:00",
      "matched_text": "...pain assessment...vital signs check...",
      "score": 0.95
    }
  ]
}
```

---

#### GET /search/tags

Search for sessions by tags.

**Query Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| tag | string | Tag to search for |
| patient_id | string | Filter by patient |
| start_date | string | Filter from date |
| end_date | string | Filter to date |
| limit | integer | Max results |

**Response (200 OK):**
```json
{
  "status": "success",
  "tag": "medication_review",
  "total_count": 15,
  "sessions": [
    {
      "session_id": "550e8400-e29b-41d4-a716-446655440000",
      "patient_id": "P001",
      "patient_name": "Maria Chen",
      "timestamp": "2026-01-30T02:50:00",
      "nurse_id": "N04",
      "confidence": 0.88
    }
  ]
}
```

---

## File Operations

### File Storage Operations

#### POST /files/upload

Upload a transcript file directly.

**Request (Multipart Form):**
```
Content-Type: multipart/form-data

file: (JSON transcript file)
patient_id: P001
session_timestamp: 2026-01-30T02:50:00
```

**Response (201 Created):**
```json
{
  "status": "success",
  "file_path": "/data/transcripts/P001/2026-01-30/550e8400-e29b-41d4-a716-446655440000.json",
  "message": "File uploaded successfully"
}
```

---

#### GET /files/download/{patient_id}/{session_id}

Download a transcript file.

**Path Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| patient_id | string | Patient identifier |
| session_id | string | Session UUID |

**Response (200):**
Returns the raw JSON file for download.

---

#### GET /files/list/{patient_id}/{date}

List all files for a patient on a specific date.

**Path Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| patient_id | string | Patient identifier |
| date | string | Date (YYYY-MM-DD) |

**Response (200 OK):**
```json
{
  "status": "success",
  "patient_id": "P001",
  "date": "2026-01-30",
  "files": [
    {
      "filename": "550e8400-e29b-41d4-a716-446655440000.json",
      "type": "transcript",
      "size_bytes": 2048,
      "created_at": "2026-01-30T10:15:00Z"
    },
    {
      "filename": "550e8400-e29b-41d4-a716-446655440000_classification.json",
      "type": "classification",
      "size_bytes": 1024,
      "created_at": "2026-01-30T10:32:00Z"
    }
  ]
}
```

---

## Batch Operations

#### POST /batch/process

Process multiple transcripts in batch.

**Request Body:**
```json
{
  "transcripts": [
    {
      "session_id": "uuid-1",
      "patient_id": "P001",
      "nurse_id": "N04",
      "transcript_text": "..."
    },
    {
      "session_id": "uuid-2",
      "patient_id": "P002",
      "nurse_id": "N04",
      "transcript_text": "..."
    }
  ],
  "options": {
    "parallel": true,
    "notify_on_complete": true
  }
}
```

**Response (202 Accepted):**
```json
{
  "status": "accepted",
  "batch_id": "batch-12345",
  "total_count": 2,
  "completed_count": 0,
  "pending_count": 2,
  "status_url": "/batch/status/batch-12345"
}
```

---

#### GET /batch/status/{batch_id}

Get batch processing status.

**Path Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| batch_id | string | Batch job identifier |

**Response (200 OK):**
```json
{
  "status": "success",
  "batch_id": "batch-12345",
  "status": "processing",
  "progress": 50,
  "completed": 1,
  "failed": 0,
  "pending": 1,
  "results": [
    {
      "session_id": "uuid-1",
      "status": "completed",
      "classification_exists": true
    }
  ]
}
```

---

## Error Responses

All error responses follow this format:

```json
{
  "status": "error",
  "error_code": "ERROR_CODE",
  "message": "Human-readable error message",
  "details": {
    "field": "field_name",
    "reason": "specific reason"
  }
}
```

### Common Error Codes

| Error Code | HTTP Status | Description |
|------------|-------------|-------------|
| VALIDATION_ERROR | 400 | Invalid request data |
| TRANSCRIPT_NOT_FOUND | 404 | Transcript not found |
| PATIENT_NOT_FOUND | 404 | Patient not found |
| FILE_NOT_FOUND | 404 | File not found |
| FILE_READ_ERROR | 500 | Error reading file |
| FILE_WRITE_ERROR | 500 | Error writing file |
| PROCESSING_ERROR | 500 | Processing failed |
| BATCH_NOT_FOUND | 404 | Batch job not found |

---

## Data Flow Examples

### Example 1: Processing a Transcript

```
1. POST /transcripts/process
   - Request contains transcript from scenarios.json
   - Middleware creates: data/transcripts/P001/2026-01-30/{session_id}.json

2. Background processing
   - AI classification applied
   - Tags extracted
   - Results saved to: data/transcripts/P001/2026-01-30/{session_id}_classification.json
   - Tags saved to: data/transcripts/P001/2026-01-30/{session_id}_tags.json

3. GET /transcripts/P001/{session_id}/classification
   - Returns classification results
```

### Example 2: Retrieving Patient Data

```
1. GET /patients/P001
   - Reads: server/data/patients/P001/profile.json
   - Scans: server/data/transcripts/P001/*/ for session history
   - Returns combined patient profile and session list
```

### Example 3: Searching by Tag

```
1. GET /search/tags?tag=medication_review
   - Scans: server/data/transcripts/*/*/*_tags.json
   - Filters for "medication_review" tag
   - Returns matching sessions with confidence scores
```

---

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| DATA_DIR | Base data directory | ./server/data |
| TRANSCRIPTS_DIR | Transcripts subdirectory | transcripts |
| NURSE_DIR | Nurse data directory | nurse |
| PATIENTS_DIR | Patients data directory | patients |
| LOG_LEVEL | Logging level | INFO |

---

## Rate Limiting

Currently, no rate limiting is implemented. For production use, add rate limiting headers:

```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 99
X-RateLimit-Reset: 3600
```

---

## Versioning

API versioning is not currently implemented. All endpoints use `/api/v1/` prefix for future compatibility.

---

## Appendix A: Sample Transcript Format

Input format (from Data/scenarios.json):

```json
{
  "PatientID": "P001",
  "PatientName": "Maria Chen",
  "Room": "3E-12",
  "Age": 62,
  "Gender": "Female",
  "Transcript": "Maria Chen in 3E-12, 62 y/o with Stage IIIB non-small cell lung cancer...",
  "RecordedBy": {
    "StaffID": "N04",
    "Name": "Nurse Sofia Martinez"
  },
  "Timestamp": "02:50:00",
  "Date": "2026-01-30",
  "ShiftContext": "Floor->ICU",
  "ScenarioType": "best_case"
}
```

---

## Appendix B: Sample Classification Output

```json
{
  "version": "1.0",
  "file_info": {
    "patient_id": "P001",
    "patient_name": "Maria Chen",
    "session_id": "550e8400-e29b-41d4-a716-446655440000",
    "session_timestamp": "2026-01-30T02:50:00",
    "classification_timestamp": "2026-01-30T10:32:00Z"
  },
  "classification": {
    "tags": ["pain_assessment", "medication_review", "vital_signs"],
    "risk_level": "low",
    "sentiment": {"overall": "neutral", "confidence": 0.85},
    "topics": [
      {
        "name": "Medication Management",
        "confidence": 0.87,
        "key_phrases": ["prescription refill", "take with food"]
      }
    ]
  }
}
```
