# MedXP Context Enrichment Agent

A Python-based agentic AI system that enriches medical session data with relevant clinical knowledge to support healthcare decision-making and reduce medical malpractice.

## Overview

The Context Enrichment Agent accepts patient data, provider information, and session transcripts, then retrieves relevant Standard Operating Procedures (SOPs), hospital policies, and treatment guidelines. It generates clinical warnings and risk assessments to help healthcare providers make informed decisions.

**Focus Area:** Non-Small Cell Lung Cancer (NSCLC)

## How It Works

```
┌─────────────────────────────────────────────────────────────────────┐
│                         INPUT                                        │
│  Patient Data + Provider Info + Session Transcript                   │
└─────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                  CONTEXT ENRICHMENT AGENT                            │
│                                                                      │
│  1. Extract key entities (diagnoses, medications, symptoms)          │
│  2. Query knowledge bases using keyword matching                     │
│  3. Generate patient summary with risk factors                       │
│  4. Check for warnings (drug interactions, critical values)          │
│  5. Assemble enriched output                                         │
└─────────────────────────────────────────────────────────────────────┘
                                │
            ┌───────────────────┼───────────────────┐
            ▼                   ▼                   ▼
    ┌──────────────┐   ┌──────────────┐   ┌──────────────┐
    │     SOPs     │   │   Policies   │   │  Guidelines  │
    │  (10 items)  │   │  (10 items)  │   │  (11 items)  │
    └──────────────┘   └──────────────┘   └──────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         OUTPUT                                       │
│  Enriched Context JSON (SOPs, Policies, Guidelines, Warnings)        │
└─────────────────────────────────────────────────────────────────────┘
```

## Project Structure

```
backend/
├── main.py                      # FastAPI application entry point
├── requirements.txt             # Python dependencies
├── test_enrichment.py           # Test script with sample data
├── .env.example                 # Environment variables template
│
├── agents/
│   └── context_enrichment.py    # Core enrichment agent logic
│
├── services/
│   ├── knowledge_retriever.py   # Keyword-based knowledge retrieval
│   └── llm_client.py            # MiniMax LLM API wrapper
│
├── models/
│   ├── request.py               # Input Pydantic schemas
│   └── response.py              # Output Pydantic schemas
│
├── config/
│   └── settings.py              # Application configuration
│
└── data/
    ├── sops/
    │   └── nsclc_sops.json      # Standard Operating Procedures
    ├── policies/
    │   └── hospital_policies.json   # Hospital policies
    └── medical_guidelines/
        └── nsclc_guidelines.json    # Treatment guidelines
```

## Requirements

- Python 3.9+
- Virtual environment (recommended)

### Dependencies

- `fastapi` - Web framework for the API
- `uvicorn` - ASGI server
- `pydantic` - Data validation
- `pydantic-settings` - Settings management
- `httpx` - Async HTTP client (for LLM API)
- `python-dotenv` - Environment variable loading

## Installation

1. **Clone the repository and navigate to backend:**
   ```bash
   cd MedXP/backend
   ```

2. **Create and activate virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment (optional):**
   ```bash
   cp .env.example .env
   # Edit .env with your MiniMax API credentials if available
   ```

## Running the Application

### Start the API Server

```bash
source venv/bin/activate
python main.py
```

The server will start at `http://localhost:8000`

- **API Documentation:** http://localhost:8000/docs
- **Health Check:** http://localhost:8000/health
- **Knowledge Stats:** http://localhost:8000/api/v1/knowledge/stats

### Run Tests

```bash
source venv/bin/activate
python test_enrichment.py
```

## API Reference

### POST /api/v1/enrich

Enrich a patient session with relevant medical knowledge.

#### Request Body

```json
{
  "session_id": "string",
  "timestamp": "2026-01-30T10:00:00",
  "patient": {
    "patient_id": "string (required)",
    "name": "string",
    "age": 62,
    "gender": "Female",
    "primary_diagnosis": "Stage IIIB NSCLC",
    "active_problems": ["Hemoptysis", "Neutropenia", "Hypoxia"],
    "allergies": ["Penicillin"],
    "code_status": "Full Code",
    "current_medications": [
      {"name": "Enoxaparin", "dose": "40 mg SQ daily", "status": "active"}
    ],
    "recent_vitals": {
      "Temp_C": 38.5,
      "HR": 92,
      "RR": 22,
      "BP_sys": 120,
      "BP_dia": 80,
      "SpO2": 87
    },
    "recent_labs": [
      {"name": "WBC", "value": 1.2, "unit": "K/uL", "flag": "L"}
    ]
  },
  "provider": {
    "staff_id": "string (required)",
    "name": "Nurse Name",
    "role": "RN"
  },
  "transcript": "Patient session transcript text..."
}
```

#### Response

```json
{
  "session_id": "string",
  "enriched_at": "2026-01-30T10:00:05",
  "patient_summary": {
    "key_diagnoses": ["Stage IIIB NSCLC", "Neutropenia"],
    "risk_factors": ["Neutropenic - high infection risk", "On anticoagulation"],
    "critical_values": [
      {"name": "SpO2", "value": 87.0, "unit": "%", "flag": "L"}
    ]
  },
  "relevant_sops": [
    {
      "sop_id": "SOP-NF-001",
      "title": "Neutropenic Fever Management",
      "relevance_reason": "diagnosis:neutropenia",
      "key_steps": ["Obtain blood cultures", "Start antibiotics within 60 min"],
      "priority": "high"
    }
  ],
  "applicable_policies": [
    {
      "policy_id": "POL-NP-001",
      "title": "Neutropenic Precautions",
      "requirement": "Patients with ANC < 500 require neutropenic precautions"
    }
  ],
  "treatment_guidelines": [
    {
      "guideline_id": "GL-NSCLC-007",
      "source": "ASCO/NCCN Guidelines",
      "title": "Neutropenia Management in Chemotherapy",
      "recommendation": "G-CSF prophylaxis when febrile neutropenia risk >= 20%"
    }
  ],
  "warnings": [
    {
      "type": "clinical_alert",
      "severity": "critical",
      "message": "Neutropenic fever - requires immediate evaluation",
      "evidence": "Temperature 38.5°C in neutropenic patient",
      "action_required": "Blood cultures and antibiotics within 60 minutes"
    }
  ],
  "metadata": {
    "processing_time_ms": 5,
    "sources_consulted": ["nsclc_sops", "hospital_policies", "nsclc_guidelines"],
    "llm_calls": 1
  }
}
```

## Warning Types Generated

| Type | Severity | Trigger |
|------|----------|---------|
| `contraindication` | high | Anticoagulation + active bleeding |
| `clinical_alert` | critical | Neutropenic fever (temp ≥38°C + neutropenia) |
| `clinical_alert` | high | Hypoxia (SpO2 < 92%) |
| `allergy` | high | Penicillin allergy + beta-lactam prescribed |
| `drug_interaction` | medium | Opioid + benzodiazepine combination |
| `documentation` | medium | Missing or unknown code status |
| `protocol_trigger` | medium | High-priority SOP matched |

## Knowledge Bases

### SOPs (10 items)
- Neutropenic Fever Management
- Anticoagulation with Active Bleeding
- Oxygen Therapy for Hypoxia
- Pain Management in Cancer
- Chemotherapy Administration Safety
- Pleural Effusion Management
- Immunotherapy Adverse Events
- Delirium Prevention
- Shift Handoff (SBAR)
- AKI Prevention

### Hospital Policies (10 items)
- Code Status Documentation
- Medication Reconciliation
- Critical Lab Value Notification
- Fall Prevention Protocol
- Neutropenic Precautions
- Patient Identification
- Pain Assessment
- Discharge Planning
- Isolation Precautions
- Rapid Response Activation

### Treatment Guidelines (11 items)
- NSCLC Stage-Based Treatment
- Molecular Testing in NSCLC
- Immunotherapy in NSCLC
- EGFR-Mutant NSCLC Treatment
- CINV Prevention
- VTE in Cancer
- Neutropenia Management
- Malignant Pleural Effusion
- Brain Metastases
- Cancer Pain Management
- Common Drug Interactions

## Configuration

Environment variables (set in `.env`):

| Variable | Description | Default |
|----------|-------------|---------|
| `MINIMAX_API_KEY` | MiniMax LLM API key | None (uses mock) |
| `MINIMAX_GROUP_ID` | MiniMax group ID | None |
| `DEBUG` | Enable debug mode | true |

**Note:** The system works without an LLM API key by using intelligent mock responses based on patient data patterns.

## Example Usage

### cURL

```bash
curl -X POST http://localhost:8000/api/v1/enrich \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "S001",
    "patient": {
      "patient_id": "P001",
      "name": "Maria Chen",
      "age": 62,
      "primary_diagnosis": "Stage IIIB NSCLC",
      "active_problems": ["Hemoptysis", "Neutropenia", "Hypoxia"],
      "current_medications": [{"name": "Enoxaparin", "dose": "40 mg SQ daily"}],
      "recent_vitals": {"Temp_C": 38.5, "SpO2": 87}
    },
    "provider": {"staff_id": "N03", "role": "RN"},
    "transcript": "Maria Chen, 62 y/o with NSCLC on chemoradiation..."
  }'
```

### Python

```python
import httpx

response = httpx.post(
    "http://localhost:8000/api/v1/enrich",
    json={
        "session_id": "S001",
        "patient": {
            "patient_id": "P001",
            "primary_diagnosis": "Stage IIIB NSCLC",
            "active_problems": ["Neutropenia"],
        },
        "provider": {"staff_id": "N03"},
        "transcript": "Patient transcript...",
    },
)
result = response.json()
print(f"Warnings: {len(result['warnings'])}")
```

## Integration with Larger System

This Context Enrichment Agent is designed to be part of a larger medical malpractice reduction system:

1. **Audio Recording Service** → Records nurse-patient interactions
2. **Transcription Service** → Converts audio to text
3. **Context Enrichment Agent** (this component) → Enriches with medical knowledge
4. **Analysis Agent** → Analyzes enriched context for compliance issues
5. **Notification Service** → Alerts managers to potential problems

The enriched output JSON from this agent serves as input to downstream analysis agents.

## License

Part of the MedXP project. See repository root for license information.
