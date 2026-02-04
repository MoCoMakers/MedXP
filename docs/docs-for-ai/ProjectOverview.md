# Medical Malpractice Reduction System - MVP

## Project Overview

Create an MVP system to reduce medical malpractice and shift-change issues in hospital nursing settings. The system monitors nurse-patient interactions through audio recording, AI-powered transcription, and agentic analysis against medical standards of care.

## Key Clinical Goals (Based on Clinical Input)

The following goals were identified as critical for reducing medical malpractice:

1. **Drug-Drug Interactions** - Detect and alert on potentially dangerous medication combinations
2. **Allergies** - Ensure allergy information is properly captured and no contraindicated medications are prescribed
3. **Compliance** - Verify adherence to care standards, protocols, and documentation requirements

## Problem Statement

Medical malpractice and shift-change communication gaps in hospital nursing settings lead to adverse patient outcomes, legal liability, and reduced care quality. This system provides:

- Real-time monitoring of nurse-patient interactions
- Automated compliance checking against medical standards of care
- Proactive risk identification and alerting (drug interactions, allergies, compliance gaps)
- Comprehensive audit trails for quality improvement
- Patient-centric timeline view for risk factor visualization

## System Architecture

```
+-----------------------------------------------------------------------------+
|                         Frontend Layer (React/Lovable)                       |
|  +----------------------+     +------------------------------------------+    |
|  |  Nurse Manager       |     |        Notifications Portal              |    |
|  |  - Nurse oversight   |     |  - Real-time alerts                      |    |
|  |  - Session review    |     |  - Risk assessments                      |    |
|  |  - Analytics dashboard|    |  - Action items                          |    |
|  +----------------------+     +------------------------------------------+    |
|                                                                             |
|  +----------------------+     +------------------------------------------+    |
|  |  Patient View        |     |        Timeline View                     |    |
|  |  - Patient profile   |     |  - Session timeline                     |    |
|  |  - Risk summary     |     |  - Risk factor highlights               |    |
|  |  - Medication list  |     |  - Compliance tracking                 |    |
|  |  - Allergy alerts   |     |  - Drug interaction markers            |    |
|  +----------------------+     +------------------------------------------+    |
+-----------------------------------------------------------------------------+
                                    |
                                    v
+-----------------------------------------------------------------------------+
|                      Middleware Layer (FastAPI)                               |
|  +---------------------------------------------------------------------+    |
|  |  RESTful API Endpoints:                                             |    |
|  |  - /api/transcripts        - Transcript submission/processing        |    |
|  |  - /api/patients/*        - Patient data management                |    |
|  |  - /api/sessions/*        - Session management                    |    |
|  |  - /api/analysis/*        - AI analysis results                   |    |
|  |  - /api/notifications/*   - Alert and notification management     |    |
|  |  - /api/drug-checks/*     - Drug interaction checking            |    |
|  |  - /api/compliance/*     - Compliance verification              |    |
|  +---------------------------------------------------------------------+    |
+-----------------------------------------------------------------------------+
                                    |
                                    v
+-----------------------------------------------------------------------------+
|                    Agentic Backend Layer (Python)                             |
|  +---------------+  +---------------+  +-------------------------------+      |
|  |  Transcription|  |  Classification|  |  Clinical Safety Agent        |      |
|  |  Service      |  |  Service      |  |  - Drug interaction check     |      |
|  |               |  |               |  |  - Allergy verification       |      |
|  |               |  |               |  |  - Compliance assessment     |      |
|  +---------------+  +---------------+  +-------------------------------+      |
|                                                                             |
|  +-------------------------------+  +-------------------------------+      |
|  |  Risk Assessment Agent        |  |  Warning Generator            |      |
|  |  - Session risk scoring      |  |  - Severity classification   |      |
|  |  - Trend analysis           |  |  - Alert generation          |      |
|  |  - Pattern detection        |  |  - Action recommendations    |      |
|  +-------------------------------+  +-------------------------------+      |
+-----------------------------------------------------------------------------+
                                    |
                                    v
+-----------------------------------------------------------------------------+
|                         Data Layer                                          |
|  +---------------+  +---------------+  +-------------------------------+      |
|  |  Filesystem   |  |  Drug Database|  |  Medical Standards DB         |      |
|  |  - Transcripts|  |  - Drug list  |  |  - Care protocols             |      |
|  |  - Sessions   |  |  - Interactions| |  - Guidelines                 |      |
|  |  - Classifications| - Contraindications| |  - Compliance rules         |      |
|  +---------------+  +---------------+  +-------------------------------+      |
+-----------------------------------------------------------------------------+
```

## Core Safety Checks

### Drug-Drug Interaction Detection

The system automatically checks for:

| Interaction Type | Severity | Example |
|-----------------|----------|---------|
| Major Interaction | Critical | Warfarin + Aspirin (bleeding risk) |
| Moderate Interaction | High | ACE Inhibitor + Potassium (hyperkalemia) |
| Minor Interaction | Medium | Multiple CNS depressants |
| Duplicate Therapy | Medium | Two opioids prescribed |

### Allergy Verification

| Check Type | Description |
|------------|-------------|
| Direct Allergy | Patient allergy to medication class |
| Cross-Reactivity | Related drug class reactions |
| Ingredient Match | Inactive ingredient conflicts |
| Pseudoallergy | Documented adverse reactions |

### Compliance Monitoring

| Compliance Area | Check |
|----------------|-------|
| Documentation | Complete session notes |
| Protocol Adherence | Standard of care followed |
| Medication Reconciliation | Accurate medication list |
| Allergy Documentation | Allergy information recorded |
| Code Status | Code status confirmed |

## Patient View with Timeline

### Timeline Features

```
Patient Timeline View
+------------------------------------------------------------------------------+
|  Maria Chen (P001)                                                           |
|  62 y/o Female | Stage IIIB NSCLC | Room 3E-12                            |
+------------------------------------------------------------------------------+
|                                                                              |
|  Risk Overview                                                               |
|  [HIGH RISK] 2 Active Alerts                                                |
|  - Drug Interaction (Enoxaparin + Aspirin)                                   |
|  - Allergies (Penicillin documented)                                         |
|                                                                              |
+------------------------------------------------------------------------------+
|  Timeline                                                                   |
|                                                                              |
|  Jan 30                                                                    |
|  |-- 14:40 --|  Session with Nurse Priya Nair                             |
|  |            [RISK: Low] [Compliance: 95%]                              |
|  |            Tags: medication_review, vital_signs                         |
|  |                                                                   |
|  |-- 11:00 --|  Session with Nurse Sofia Martinez                       |
|  |            [WARNING: Drug Interaction Detected]                      |
|  |            [RISK: High] [Compliance: 78%]                          |
|  |            Tags: medication_review, risk_assessment                  |
|  |            Alerts: 2 (1 Critical, 1 High)                          |
|  |                                                                   |
|  |-- 03:00 --|  Session with Nurse Priya Nair                         |
|  |            [RISK: Medium] [Compliance: 88%]                        |
|  |            Tags: pain_assessment, medication_review                 |
|  |                                                                   |
|  |-- 02:50 --|  Session with Nurse Sofia Martinez                   |
|  |            [RISK: Low] [Compliance: 92%]                          |
|  |            Tags: clinical_assessment                                |
|  |                                                                   |
+------------------------------------------------------------------------------+
|  Risk Factors Summary                                                       |
|                                                                              |
|  [CRITICAL] Bleeding Risk - On anticoagulation with active symptoms         |
|  [HIGH]    Infection Risk - Neutropenic status                             |
|  [HIGH]    Respiratory Risk - Hypoxia documented                           |
|  [MEDIUM]  Pain Management - Regular PRN opioids prescribed                |
|                                                                              |
+------------------------------------------------------------------------------+
```

### Risk Factor Highlighting

| Risk Type | Color | Icon | Description |
|-----------|-------|------|-------------|
| Critical | Red | ! | Immediate action required |
| High | Orange | WARNING | Close monitoring needed |
| Medium | Yellow | INFO | Document and monitor |
| Low | Green | CHECK | Standard care |

## Technology Stack

### Frontend
- **Framework**: React (built with Lovable)
- **State Management**: React Context / Zustand
- **UI Library**: Material-UI or Tailwind CSS
- **Real-time**: WebSocket for notifications
- **Visualization**: Recharts for timeline and risk charts

### Middleware
- **Framework**: FastAPI (Python)
- **API Style**: RESTful
- **HTTP Client**: httpx for backend calls
- **Documentation**: OpenAPI auto-generated

### Backend (Agentic)
- **Language**: Python
- **AI/LLM**: Siloed instance (to be configured)
- **Framework**: Custom agent framework
- **Task Processing**: Asynchronous with httpx

### Storage
- **Primary**: Filesystem (JSON files)
- **Data Source**: Data/scenarios.json format
- **Patient Data**: Data/patients_ehr.json format

## Folder Structure

```
MedXP/
├── docs/
│   └── docs-for-ai/
│       ├── ProjectOverview.md              # This document
│       ├── middleware-conceptual-endpoints.md
│       └── middleware-plan.md
├── middleware/                            # FastAPI middleware
│   ├── app/
│   │   ├── main.py                       # FastAPI application
│   │   ├── config.py                     # Configuration
│   │   ├── models/
│   │   │   └── __init__.py              # Pydantic models
│   │   ├── services/
│   │   │   └── backend_client.py         # Backend API client
│   │   └── utils/
│   │       ├── transform.py              # Data transformation
│   │       └── storage.py               # Filesystem storage
│   └── tests/
├── backend/                              # Agentic backend services
│   ├── agents/
│   │   └── context_enrichment.py        # Clinical safety agent
│   ├── services/
│   │   ├── llm_client.py               # LLM integration
│   │   └── knowledge_retriever.py       # Knowledge base
│   └── data/
│       ├── sops/                        # Standard operating procedures
│       ├── policies/                    # Hospital policies
│       └── medical_guidelines/          # Treatment guidelines
├── Data/
│   ├── scenarios.json                  # Session transcripts
│   └── patients_ehr.json              # Patient EHR data
└── docker/
    └── docker-compose.yml
```

## Implementation Phases (3-Month MVP)

### Phase 1: Foundation (Weeks 1-3)
- Set up Docker development environment
- Initialize FastAPI middleware
- Create filesystem storage utilities
- Implement transcript submission endpoint
- Connect to backend Context Enrichment Agent

### Phase 2: Core Features (Weeks 4-7)
- Build Patient View with Timeline
- Implement drug interaction checking
- Add allergy verification system
- Create compliance monitoring
- Develop risk factor visualization

### Phase 3: Agentic Intelligence (Weeks 8-10)
- Enhance Clinical Safety Agent
- Build comprehensive warning system
- Implement risk trend analysis
- Create patient risk summaries

### Phase 4: Notifications and Integration (Weeks 11-12)
- Build Notifications Portal
- Add real-time alert system
- Final testing and documentation

## Core API Endpoints

### Transcript Processing
- `POST /api/transcripts` - Submit transcript for processing
- `GET /api/transcripts/{patient_id}` - List patient transcripts

### Patient Data
- `GET /api/patients/{patient_id}` - Get patient profile
- `GET /api/patients/{patient_id}/timeline` - Get patient session timeline
- `GET /api/patients/{patient_id}/risk-factors` - Get patient risk factors

### Drug Safety
- `GET /api/drug-checks/interactions` - Check drug interactions
- `GET /api/drug-checks/allergies` - Verify allergy safety

### Compliance
- `GET /api/compliance/{session_id}` - Get compliance assessment
- `GET /api/compliance/patient/{patient_id}` - Get patient compliance summary

### Analysis
- `GET /api/analysis/{session_id}` - Get analysis results
- `GET /api/analysis/{session_id}/warnings` - Get session warnings
- `GET /api/analysis/{session_id}/risks` - Get risk details

## Data Format Reference

### Input: Transcript Data (from Data/scenarios.json)

```json
{
  "PatientID": "P001",
  "PatientName": "Maria Chen",
  "Room": "3E-12",
  "Age": 62,
  "Gender": "Female",
  "Transcript": "Maria Chen in 3E-12, 62 y/o with Stage IIIB NSCLC...",
  "RecordedBy": {
    "StaffID": "N04",
    "Name": "Nurse Sofia Martinez"
  },
  "Timestamp": "02:50:00",
  "Date": "2026-01-30"
}
```

### Input: Patient EHR Data (from Data/patients_ehr.json)

```json
{
  "PatientID": "P001",
  "PatientName": "Maria Chen",
  "MRN": "MRN100200",
  "PrimaryDiagnosis": "Stage IIIB NSCLC",
  "Allergies": ["NKDA"],
  "ActiveProblems": ["Hemoptysis", "Neutropenia", "Hypoxia"],
  "Medications": [
    {"name": "Enoxaparin", "dose": "40 mg SQ daily", "status": "active"}
  ]
}
```

## Warning Types Generated

| Type | Severity | Trigger Example |
|------|----------|----------------|
| **Drug-Drug Interaction** | Critical/High | Anticoagulation + bleeding symptoms |
| **Allergy Alert** | High | Penicillin allergy + beta-lactam prescribed |
| **Compliance Gap** | Medium | Missing code status documentation |
| **Protocol Trigger** | Medium | SOP conditions met |
| **Critical Value** | Critical | Temperature > 38.0C in neutropenic patient |
| **Contraindication** | High | Medication contraindicated for condition |

## HIPAA Compliance Considerations

### Data Security
- All data encrypted at rest and in transit
- PHI fields protected
- Secure key management via environment variables

### Audit and Compliance
- Complete audit trail for all data access
- Data retention policies
- Export capabilities for compliance reporting

### Patient Privacy
- Consent tracking
- Data minimization principles
- Secure data handling

## Deliverables at End of 3 Months

1. FastAPI middleware with transcript processing
2. Patient View with interactive timeline
3. Drug interaction checking system
4. Allergy verification system
5. Compliance monitoring
6. Real-time alert system
7. Risk factor visualization
8. Connection to backend Clinical Safety Agent

## Success Metrics

### Safety Metrics
- Drug interactions detected and prevented
- Allergy documentation completeness
- Compliance rate across sessions
- Alert response rate

### Technical Metrics
- API response time: < 500ms
- Drug check accuracy
- False positive rate in alerts
