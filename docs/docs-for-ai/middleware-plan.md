# Middleware API Plan - Transcript Processing and Classification

## Executive Summary

This document outlines the middleware API architecture for handling transcript processing, AI-driven tagging and classification, and persistent storage of classification results. The system is designed to receive transcript data from frontend applications (as shown in `Data/scenarios.json`), process it through a local AI pipeline, and store structured classification results with proper tracking of nurses and patients.

This is a proof-of-concept (POC) implementation for a single-nurse, single-user system with synthetic data.

## Data Structure Reference

### Input: Transcript Data (from Data/scenarios.json)

The middleware receives transcript data in the following format:

```json
{
  "PatientID": "P001",
  "PatientName": "Maria Chen",
  "Room": "3E-12",
  "Age": 62,
  "Gender": "Female",
  "Transcript": "Full transcript text from the session...",
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

### Input: Patient EHR Data (from Data/patients_ehr.json)

The agentic system receives patient data for comparison:

```json
{
  "PatientID": "P001",
  "PatientName": "Maria Chen",
  "MRN": "MRN100200",
  "PrimaryDiagnosis": "Stage IIIB non-small cell lung cancer (NSCLC)",
  "Allergies": ["NKDA"],
  "CodeStatus": "Full Code",
  "ActiveProblems": ["Hemoptysis", "Pleural effusion", "COPD"],
  "Medications": [
    {
      "name": "Enoxaparin",
      "dose": "40 mg SQ daily",
      "status": "active"
    }
  ],
  "Vitals": [...]
}
```

## System Overview

### High-Level Data Flow

```
Frontend Application (React/Lovable)
        |
        v
+---------------------------------------------------+
|  Middleware API (Flask)                           |
|  - POST /api/transcripts/process                  |
|  - Validate incoming JSON                         |
|  - Queue processing job                           |
+---------------------------------------------------+
        |
        v
+---------------------------------------------------+
|  Transcript Processing Service                    |
|  - Parse transcript text                          |
|  - Chunking and preprocessing                     |
|  - Prepare payload for AI pipeline                |
+---------------------------------------------------+
        |
        v
+---------------------------------------------------+
|  Local AI Pipeline (Classification Service)       |
|  - Call local LLM/classification model            |
|  - Generate tags and classifications              |
|  - Extract entities and insights                  |
+---------------------------------------------------+
        |
        v
+---------------------------------------------------+
|  Result Storage                                   |
|  - Save classification JSON to server folder      |
|  - Update database with references                |
|  - Trigger downstream analysis                    |
+---------------------------------------------------+
```

## API Endpoint Design

### Primary Endpoint

```
POST /api/transcripts/process
Content-Type: application/json
```

This endpoint receives transcript data from the frontend for processing.

### Request Structure

```json
{
  "session_id": "uuid-string",
  "patient_id": "P001",
  "patient_name": "Maria Chen",
  "transcript_text": "Full transcript content from the session",
  "nurse_id": "N04",
  "nurse_name": "Nurse Sofia Martinez",
  "session_timestamp": "2026-01-30T02:50:00",
  "shift_context": "Floor->ICU",
  "room": "3E-12",
  "scenario_type": "best_case"
}
```

### Response Structure

#### Immediate Response (202 Accepted)

```json
{
  "status": "accepted",
  "message": "Transcript submitted for processing",
  "job_id": "uuid-string",
  "estimated_processing_time_seconds": 120,
  "_links": {
    "status": "/api/jobs/{job_id}/status",
    "result": "/api/transcripts/{session_id}/classification"
  }
}
```

#### Error Response (400/422/500)

```json
{
  "status": "error",
  "error_code": "VALIDATION_ERROR",
  "message": "Invalid request data",
  "details": [
    {
      "field": "transcript_text",
      "message": "Transcript text cannot be empty"
    }
  ]
}
```

### Supporting Endpoints

#### Get Job Status

```
GET /api/jobs/{job_id}/status
```

Response:

```json
{
  "job_id": "uuid-string",
  "status": "processing|completed|failed",
  "progress_percent": 45,
  "current_stage": "classifying_content",
  "started_at": "2026-01-30T10:31:00Z",
  "estimated_completion": "2026-01-30T10:33:00Z"
}
```

#### Get Classification Result

```
GET /api/transcripts/{session_id}/classification
```

Response:

```json
{
  "session_id": "uuid-string",
  "patient_id": "P001",
  "patient_name": "Maria Chen",
  "nurse_id": "N04",
  "nurse_name": "Nurse Sofia Martinez",
  "classification": {
    "tags": ["pain_assessment", "medication_review", "vital_signs"],
    "categories": ["clinical_assessment", "care_coordination"],
    "risk_level": "low",
    "sentiment": "neutral",
    "topics": [
      {
        "name": "Medication Management",
        "confidence": 0.87,
        "key_phrases": ["prescription refill", "dosage adjustment"]
      }
    ]
  },
  "entities": {
    "medications": [],
    "symptoms": ["chest pain", "shortness of breath"],
    "procedures": ["vital_signs_check"],
    "time_expressions": ["every 4 hours", "since yesterday"]
  },
  "processing_metadata": {
    "model_version": "1.2.0",
    "processing_time_ms": 4523,
    "confidence_threshold": 0.7
  },
  "session_timestamp": "2026-01-30T02:50:00"
}
```

#### Get All Transcripts

```
GET /api/transcripts
```

Query Parameters:
- `patient_id`: Filter by patient ID
- `nurse_id`: Filter by nurse ID
- `page`: Page number (default: 1)
- `limit`: Items per page (default: 20)

## Data Models

### Transcript Record

```python
class TranscriptRecord(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    session_id: UUID
    patient_id: str  # e.g., "P001"
    patient_name: str
    nurse_id: str  # e.g., "N04"
    nurse_name: str
    transcript_text: str
    session_timestamp: datetime
    shift_context: str
    room: str
    scenario_type: str
    status: TranscriptStatus = TranscriptStatus.PENDING
    created_at: datetime = Field(default_factory=datetime.utcnow)
    processed_at: Optional[datetime] = None
```

### Classification Result

```python
class ClassificationResult(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    transcript_id: UUID
    session_id: UUID
    patient_id: str
    nurse_id: str
    tags: List[str]
    categories: List[str]
    risk_level: RiskLevel
    sentiment: Sentiment
    topics: List[TopicClassification]
    entities: EntityExtraction
    metadata: ProcessingMetadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
```

### Topic Classification

```python
class TopicClassification(BaseModel):
    name: str
    confidence: float
    key_phrases: List[str]
    relevant_segments: List[TextSegment] = []
```

### Entity Extraction

```python
class EntityExtraction(BaseModel):
    medications: List[MedicationMention]
    symptoms: List[SymptomMention]
    procedures: List[str]
    time_expressions: List[TimeExpression]
    personnel_mentions: List[str] = []
    care_instructions: List[str] = []
```

## File Storage Structure

### Server Folder Organization

For this POC, files are named using patient_id and session date for easy identification:

```
server/
├── data/
│   ├── transcripts/
│   │   └── {patient_id}_{session_date}/
│   │       └── {session_id}.json
│   ├── classifications/
│   │   └── {patient_id}_{session_date}/
│   │       └── {session_id}_classification.json
├── nurse/
│   └── profile.json
└── patients/
    └── {patient_id}/
        └── profile.json
```

### Naming Convention

- **Transcript files**: `{patient_id}_{YYYY-MM-DD}_{session_id}.json`
  - Example: `P001_2026-01-30_550e8400-e29b-41d4-a716-446655440000.json`

- **Classification files**: `{patient_id}_{YYYY-MM-DD}_{session_id}_classification.json`
  - Example: `P001_2026-01-30_550e8400-e29b-41d4-a716-446655440000_classification.json`

### Transcript JSON File Structure

```json
{
  "version": "1.0",
  "file_info": {
    "patient_id": "P001",
    "patient_name": "Maria Chen",
    "session_id": "550e8400-e29b-41d4-a716-446655440000",
    "session_timestamp": "2026-01-30T02:50:00",
    "room": "3E-12",
    "shift_context": "Floor->ICU",
    "scenario_type": "best_case"
  },
  "recording_info": {
    "nurse_id": "N04",
    "nurse_name": "Nurse Sofia Martinez",
    "recorded_at": "2026-01-30T02:50:00Z",
    "created_at": "2026-01-30T10:15:00Z"
  },
  "transcript": {
    "text": "Full transcript content from the session...",
    "word_count": 150,
    "language": "en"
  }
}
```

### Classification JSON File Structure

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
    "id": "uuid-classification-id",
    "tags": [
      "pain_assessment",
      "medication_review",
      "vital_signs",
      "patient_education"
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
    "risk_factors": [],
    "sentiment": {
      "overall": "neutral",
      "confidence": 0.85,
      "breakdown": {
        "positive": 0.15,
        "neutral": 0.70,
        "negative": 0.15
      }
    },
    "topics": [
      {
        "name": "Medication Management",
        "confidence": 0.87,
        "key_phrases": [
          "prescription refill",
          "take with food",
          "avoid alcohol"
        ],
        "relevant_segments": [
          {
            "start_char": 450,
            "end_char": 890,
            "text": "..."
          }
        ]
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
      "symptoms": [
        {
          "term": "fever",
          "severity": "38.5C",
          "context": "elevated temperature"
        }
      ],
      "procedures": [
        "vital signs check",
        "wound assessment"
      ],
      "time_expressions": [
        {
          "expression": "q4h",
          "parsed_duration": "PT4H",
          "context": "medication frequency"
        }
      ],
      "care_instructions": [
        "Follow up in 2 weeks",
        "Return if symptoms worsen"
      ]
    },
    "care_gaps": [],
    "recommendations": [],
    "metadata": {
      "model_version": "1.2.0",
      "processing_time_ms": 4523,
      "confidence_threshold": 0.7,
      "pipeline_version": "2026.01.30"
    }
  }
}
```

## Nurse Data (POC - Single User)

### Nurse Profile Structure

For this proof-of-concept, a single synthetic nurse profile is used:

```json
{
  "nurse_id": "N04",
  "profile": {
    "name": "Nurse Sofia Martinez",
    "email": "sofia.martinez@hospital.org",
    "employee_id": "EMP-001",
    "department": "Oncology",
    "shift_pattern": "Day Shift",
    "hire_date": "2020-03-15",
    "certifications": ["RN", "OCN"]
  },
  "statistics": {
    "total_sessions_processed": 0,
    "average_risk_score": 0.0,
    "high_risk_sessions": 0,
    "tags_frequencies": {}
  },
  "settings": {
    "auto_process_transcripts": true,
    "notification_preferences": {
      "email": true,
      "in_app": true,
      "risk_threshold": "medium"
    }
  }
}
```

### Nurse Index File

Location: `server/data/nurse/profile.json`

```json
{
  "nurse_id": "N04",
  "name": "Nurse Sofia Martinez",
  "total_sessions": 0,
  "updated_at": "2026-01-30T10:32:00Z",
  "recent_sessions": []
}
```

## Patient Data Tracking

### Patient Profile Structure

For each patient referenced in transcripts, a profile is maintained:

```json
{
  "patient_id": "P001",
  "profile": {
    "name": "Maria Chen",
    "mrn": "MRN100200",
    "room": "3E-12",
    "age": 62,
    "gender": "Female"
  },
  "medical_context": {
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
        "dose": "40 mg SQ daily"
      }
    ]
  },
  "session_history": []
}
```

### Patient Session Index

Location: `server/data/patients/{patient_id}/sessions/index.json`

```json
{
  "patient_id": "P001",
  "patient_name": "Maria Chen",
  "total_sessions": 0,
  "updated_at": "2026-01-30T10:32:00Z",
  "sessions": []
}
```

## Session Timestamp Support

Each classification is linked to a specific session with timestamp metadata:

```json
{
  "session_context": {
    "session_id": "uuid-session-id",
    "session_timestamp": "2026-01-30T02:50:00",
    "recording_timestamp": "2026-01-30T02:50:00",
    "shift_context": "Floor->ICU",
    "room": "3E-12",
    "scenario_type": "best_case"
  },
  "nurse_context": {
    "nurse_id": "N04",
    "nurse_name": "Nurse Sofia Martinez"
  },
  "patient_context": {
    "patient_id": "P001",
    "patient_name": "Maria Chen"
  },
  "processing_context": {
    "processing_timestamp": "2026-01-30T10:32:00Z",
    "processing_duration_ms": 4523
  }
}
```

## Processing Pipeline

### Pipeline Architecture

```
+------------------+     +-------------------+     +------------------+
|  Input Validator | --> | Preprocessor      | --> | Text Chunking    |
+------------------+     +-------------------+     +------------------+
                                                        |
                                                        v
+------------------+     +-------------------+     +------------------+
|  Result Persister|<-- | Post-processor    | <-- | Classification   |
+------------------+     +-------------------+     | Engine           |
        |                                               |
        v                                               v
+------------------+                      +----------------------+
|  Index Updater   |                      | Local AI Model       |
+------------------+                      | (Siloed LLM)         |
                                          +----------------------+
```

### Pipeline Stages

1. **Input Validation**
   - Validate JSON structure
   - Verify required fields
   - Check for empty transcript
   - Sanitize text content

2. **Preprocessing**
   - Normalize whitespace
   - Handle special characters
   - Detect language
   - Identify speaker segments
   - Extract potential entities

3. **Text Chunking**
   - Split long transcripts into manageable chunks
   - Maintain context across chunks
   - Overlap segments for continuity
   - Preserve paragraph boundaries

4. **Classification Engine**
   - Call local LLM model
   - Extract tags and categories
   - Identify risk factors
   - Generate sentiment analysis
   - Extract named entities

5. **Post-processing**
   - Aggregate chunk-level results
   - Deduplicate tags
   - Normalize entity formats
   - Calculate confidence scores
   - Generate summary

6. **Result Persistence**
   - Save transcript JSON to file
   - Save classification JSON to file
   - Generate filenames with patient_id and date
   - Update index files

7. **Index Updates**
   - Update patient session history
   - Update nurse statistics
   - Update global search index

### API Integration Points

#### Calling the Local AI Pipeline

```python
async def call_classification_pipeline(transcript_text: str, context: Dict) -> ClassificationResult:
    """
    Calls the local AI pipeline for transcript classification.

    Args:
        transcript_text: The raw transcript text
        context: Additional context (nurse_id, patient_id, etc.)

    Returns:
        ClassificationResult with tags, categories, and entities
    """
    # Prepare payload
    payload = {
        "text": transcript_text,
        "context": context,
        "config": {
            "max_tokens": 4096,
            "temperature": 0.1,
            "tags": [
                "pain_assessment",
                "medication_review",
                "vital_signs",
                "patient_education",
                "care_coordination",
                "symptom_inquiry",
                "treatment_plan",
                "follow_up_instructions"
            ],
            "categories": [
                "clinical_assessment",
                "care_planning",
                "patient_education",
                "care_coordination",
                "administrative"
            ]
        }
    }

    # Call local LLM service
    response = await asyncio.to_thread(
        subprocess.run,
        [
            "python", "backend/services/classify_transcript.py",
            "--input", json.dumps(payload),
            "--model", config.LLM_MODEL_PATH
        ],
        capture_output=True,
        text=True,
        timeout=300
    )

    if response.returncode != 0:
        raise PipelineError(f"Classification failed: {response.stderr}")

    return ClassificationResult(**json.loads(response.stdout))
```

## Database Schema

### Transcripts Table

```sql
CREATE TABLE transcripts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID NOT NULL,
    patient_id VARCHAR(50) NOT NULL,
    patient_name VARCHAR(255) NOT NULL,
    nurse_id VARCHAR(50) NOT NULL,
    nurse_name VARCHAR(255) NOT NULL,
    transcript_text TEXT NOT NULL,
    session_timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    shift_context VARCHAR(100),
    room VARCHAR(50),
    scenario_type VARCHAR(50),
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    processed_at TIMESTAMP WITH TIME ZONE,
    processing_duration_ms INTEGER
);

CREATE INDEX idx_transcripts_patient_id ON transcripts(patient_id);
CREATE INDEX idx_transcripts_nurse_id ON transcripts(nurse_id);
CREATE INDEX idx_transcripts_session_timestamp ON transcripts(session_timestamp);
CREATE INDEX idx_transcripts_status ON transcripts(status);
```

### Classifications Table

```sql
CREATE TABLE classifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    transcript_id UUID NOT NULL UNIQUE,
    session_id UUID NOT NULL,
    patient_id VARCHAR(50) NOT NULL,
    nurse_id VARCHAR(50) NOT NULL,
    tags JSONB NOT NULL DEFAULT '[]',
    categories JSONB NOT NULL DEFAULT '[]',
    risk_level VARCHAR(20) NOT NULL DEFAULT 'unknown',
    sentiment JSONB NOT NULL,
    topics JSONB NOT NULL DEFAULT '[]',
    entities JSONB NOT NULL DEFAULT '{}',
    metadata JSONB NOT NULL DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    CONSTRAINT fk_transcript FOREIGN KEY (transcript_id) REFERENCES transcripts(id)
);

CREATE INDEX idx_classifications_risk_level ON classifications(risk_level);
CREATE INDEX idx_classifications_tags ON classifications USING GIN(tags);
CREATE INDEX idx_classifications_patient_id ON classifications(patient_id);
CREATE INDEX idx_classifications_nurse_id ON classifications(nurse_id);
```

### Nurse Table (POC - Single Row)

```sql
CREATE TABLE nurse_profile (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    nurse_id VARCHAR(50) NOT NULL UNIQUE,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255),
    employee_id VARCHAR(100),
    department VARCHAR(100),
    shift_pattern VARCHAR(50),
    hire_date DATE,
    certifications JSONB DEFAULT '[]',
    statistics JSONB DEFAULT '{}',
    settings JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### Patients Table

```sql
CREATE TABLE patient_profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    patient_id VARCHAR(50) NOT NULL UNIQUE,
    name VARCHAR(255) NOT NULL,
    mrn VARCHAR(100),
    room VARCHAR(50),
    age INTEGER,
    gender VARCHAR(20),
    primary_diagnosis TEXT,
    allergies JSONB DEFAULT '[]',
    code_status VARCHAR(50),
    active_problems JSONB DEFAULT '[]',
    current_medications JSONB DEFAULT '[]',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_patients_patient_id ON patient_profiles(patient_id);
```

## Error Handling

### Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| VALIDATION_ERROR | 400 | Invalid request data |
| TRANSCRIPT_EMPTY | 400 | Transcript text is empty |
| SESSION_NOT_FOUND | 404 | Session not found |
| PATIENT_NOT_FOUND | 404 | Patient not found |
| PROCESSING_ERROR | 500 | Internal processing error |
| MODEL_ERROR | 500 | AI model inference error |
| TIMEOUT_ERROR | 504 | Processing timeout |

### Error Response Format

```json
{
  "status": "error",
  "error_code": "PROCESSING_ERROR",
  "message": "Failed to process transcript",
  "details": {
    "reason": "Model inference timeout",
    "retry_after": 60
  },
  "request_id": "uuid-request-id"
}
```

## Scalability Considerations

### Async Processing Model

For the POC, processing can be synchronous or asynchronous. For production scaling:

1. **Message Queue Integration**
   - Use Redis with Celery or RQ
   - Submit job to queue on POST
   - Return job_id immediately
   - Worker processes in background

2. **Horizontal Scaling**
   - Stateless API servers
   - Shared Redis for job queue
   - Distributed file storage (MinIO/S3)

### Caching Strategy

- Cache recent classifications by session_id
- Use Redis with TTL-based expiration
- Invalidate on new classifications

## Security Considerations

### Authentication

For this POC, authentication can be simplified:
- No multi-user authentication needed
- Single nurse profile with hardcoded access

### Data Protection

- Encrypt sensitive fields at rest
- Audit log for all access
- Data retention policies

## Implementation Roadmap

### Phase 1: Core API (Week 1)
- Implement POST /api/transcripts/process endpoint
- Create basic validation and error handling
- Set up file storage structure
- Implement synchronous classification call

### Phase 2: Storage and Indexing (Week 2)
- Create database tables
- Implement file persistence with naming convention
- Build patient session indexing
- Add supporting endpoints

### Phase 3: Async Processing (Week 3)
- Integrate message queue
- Implement background processing
- Add job status tracking
- Build notification system

### Phase 4: Optimization (Week 4)
- Add caching layer
- Performance tuning
- Load testing

## Appendix A: Example Classification Output

### Complete Classification JSON

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
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "tags": [
      "pain_assessment",
      "medication_review",
      "vital_signs",
      "patient_education",
      "follow_up_instructions"
    ],
    "categories": [
      {
        "name": "clinical_assessment",
        "confidence": 0.92
      },
      {
        "name": "patient_education",
        "confidence": 0.85
      },
      {
        "name": "care_planning",
        "confidence": 0.78
      }
    ],
    "risk_level": "low",
    "risk_factors": [],
    "sentiment": {
      "overall": "neutral",
      "confidence": 0.85,
      "breakdown": {
        "positive": 0.15,
        "neutral": 0.70,
        "negative": 0.15
      }
    },
    "topics": [
      {
        "name": "Medication Management",
        "confidence": 0.87,
        "key_phrases": [
          "prescription refill",
          "take with food",
          "avoid alcohol"
        ],
        "relevant_segments": [
          {
            "start_char": 450,
            "end_char": 890,
            "text": "Nurse: Good morning. How have you been feeling since we last met? Patient: I've been okay, but I need a refill on my Enoxaparin. Nurse: Of course. Are you taking it as prescribed? Patient: Yes, once daily in the morning. Nurse: Great. Remember to take it with food and avoid alcohol."
          }
        ]
      },
      {
        "name": "Pain Assessment",
        "confidence": 0.82,
        "key_phrases": [
          "pain level",
          "on a scale of 1 to 10"
        ],
        "relevant_segments": [
          {
            "start_char": 120,
            "end_char": 300,
            "text": "Nurse: On a scale of 1 to 10, how would you rate your pain today? Patient: I'd say about a 3. Nurse: When did it start? Patient: It started yesterday evening."
          }
        ]
      }
    ],
    "entities": {
      "medications": [
        {
          "name": "Enoxaparin",
          "dosage": "40 mg SQ daily",
          "context": "anticoagulation",
          "instruction": "take with food",
          "precaution": "avoid alcohol"
        }
      ],
      "symptoms": [
        {
          "term": "pain",
          "severity": "3/10",
          "duration": "since yesterday",
          "location": null,
          "context": "mild discomfort"
        }
      ],
      "procedures": [
        "vital signs check",
        "pain assessment"
      ],
      "time_expressions": [
        {
          "expression": "once daily",
          "parsed_duration": "P1D",
          "context": "medication frequency"
        },
        {
          "expression": "yesterday evening",
          "parsed_timestamp": "2025-01-29T18:00:00Z",
          "context": "symptom onset"
        },
        {
          "expression": "in 2 weeks",
          "parsed_duration": "P14D",
          "context": "follow-up timeframe"
        }
      ],
      "care_instructions": [
        "Take Enoxaparin with food",
        "Avoid alcohol while taking this medication",
        "Return if pain increases to 5 or higher",
        "Follow up in 2 weeks"
      ]
    },
    "care_gaps": [],
    "recommendations": [
      {
        "type": "follow_up",
        "priority": "normal",
        "description": "Schedule follow-up in 2 weeks to assess condition",
        "reason": "Routine monitoring"
      }
    ],
    "metadata": {
      "model_version": "1.2.0",
      "model_name": "medxp-classifier-v1",
      "processing_time_ms": 4523,
      "confidence_threshold": 0.7,
      "pipeline_version": "2026.01.30",
      "text_length_chars": 2500,
      "chunks_processed": 3
    }
  }
}
```

## Appendix B: API Quick Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /api/transcripts/process | Submit transcript for processing |
| GET | /api/transcripts/{session_id} | Get transcript details |
| GET | /api/transcripts/{session_id}/classification | Get classification result |
| GET | /api/transcripts/{session_id}/status | Get processing status |
| GET | /api/transcripts | List all transcripts |
| GET | /api/jobs/{job_id}/status | Get job processing status |
| GET | /api/health | Health check endpoint |

## Appendix C: Configuration

### Environment Variables

```bash
# Server Configuration
SERVER_HOST=0.0.0.0
SERVER_PORT=5000
DEBUG=false

# Database Configuration
DATABASE_URL=postgresql://user:pass@localhost:5432/medxp

# Redis Configuration
REDIS_URL=redis://localhost:6379/0

# MinIO/S3 Configuration
MINIO_URL=http://localhost:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin_secret
MINIO_BUCKET=medxp-classifications

# AI Pipeline Configuration
LLM_MODEL_PATH=/models/medxp-classifier
LLM_MAX_TOKENS=4096
LLM_TEMPERATURE=0.1

# Processing Configuration
MAX_TRANSCRIPT_LENGTH=100000
CHUNK_SIZE=4000
CHUNK_OVERLAP=200
PROCESSING_TIMEOUT=300

# POC Settings
SINGLE_NURSE_MODE=true
SYNTHETIC_DATA=true
```
