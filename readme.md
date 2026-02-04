# MedXP - Medical Experience Platform

MedXP is a proof-of-concept clinical handoff platform designed to reduce medical malpractice and shift-change issues in hospital nursing settings. The system features AI-powered audio recording, transcription, and agentic analysis against medical standards of care.

The platform offers two frontend options:

**Frontend (React)** - A modern web application with in-browser audio recording, real-time waveform visualization, and a comprehensive shift board for managing patient handoffs.

**Frontend2 (Streamlit)** - A Python-based web interface providing audio upload, transcription, validation, and patient timeline visualization. This frontend connects to both the backend (for context enrichment) and middleware (for transcript validation and malpractice analysis).

Both frontends help healthcare professionals create structured SBAR handoff documentation efficiently while monitoring interactions against patient data and medical standards.

## Overview

MedXP streamlines clinical handoffs by recording audio notes and automatically transcribing them. The platform helps healthcare professionals create structured SBAR handoff documentation efficiently while monitoring interactions against patient data and medical standards.

## Features

### Frontend (React)
- 🎤 **Audio Recording**: Record clinical handoffs directly in the browser
- 📝 **AI Transcription**: Automatic transcription using OpenAI Whisper API
- 📋 **SBAR Format**: Structured handoff documentation
- 👥 **Patient Management**: Select and manage patient handoffs
- 📊 **Shift Board**: Kanban and timeline views for shift management
- 🔔 **Notifications Portal**: Alerts for nurse managers when care gaps are detected
- 🎨 **Modern UI**: Built with React, Tailwind CSS, and Shadcn/ui

### Frontend2 (Streamlit)
- 📁 **Audio Upload**: Upload audio files in multiple formats (WAV, MP3, M4A, WebM, OGG)
- 🎙️ **Transcription**: Speech-to-text conversion using OpenAI Whisper
- 💾 **Transcript Export**: Save transcripts as text files with timestamps
- ⚠️ **Clinical Validation**: Validate against medical SOPs, policies, and guidelines
- 📅 **Patient Timeline**: Visual timeline with warnings and events
- ⚖️ **Risk Assessment**: Malpractice risk and compliance scoring
- 📋 **SBAR Display**: Structured handoff card visualization

## Quick Start (Modern Audio Recording Setup)

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm run dev
```

The app will be available at http://localhost:8080/

For detailed frontend documentation, see [frontend/README.md](frontend/README.md)

### Backend API Setup

1. Navigate to the backend-api directory:
```bash
cd backend-api
```

2. Run the setup script:
```bash
./setup.sh
```

Or manually:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

3. Configure your OpenAI API credentials:
```bash
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
```

4. Start the backend server:
```bash
python main.py
```

The API will be available at http://localhost:8000/

For detailed backend documentation, see [backend-api/README.md](backend-api/README.md)

### Running Both Servers

You need to run both the frontend and backend servers:

**Terminal 1 - Frontend:**
```bash
cd frontend
npm run dev
```

**Terminal 2 - Backend:**
```bash
cd backend-api
source venv/bin/activate
python main.py
```

## Complete System Setup (Backend + Middleware + Streamlit Frontend)

This section describes the complete MedXP system with three interconnected services:

1. **backend** - FastAPI server providing context enrichment and medical knowledge retrieval
2. **middleware** - Flask API handling transcript validation and malpractice analysis
3. **frontend2** - Streamlit web interface for recording and viewing handoffs

### Architecture Overview

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  frontend2  │────▶│  middleware │────▶│   backend   │
│  (Streamlit)│     │   (Flask)   │     │  (FastAPI)  │
└─────────────┘     └─────────────┘     └─────────────┘
      │                   │                   │
      │  Submit audio/    │  Enrich context   │  Retrieve
      │  transcript       │  + risk analysis  │  SOPs/guidelines
      │                   │                   │
      │◀──────────────────│◀──────────────────│
      │  Timeline with    │  Warnings +       │
      │  warnings         │  risk assessment  │
```

### Service Endports

| Service | Port | Description |
|---------|------|-------------|
| frontend2 | 8501 | Streamlit web UI |
| middleware | 5001 | Transcript validation API |
| backend | 8000 | Context enrichment API |

### Starting All Services

**Terminal 1 - Backend (Context Enrichment):**
```bash
cd backend
# Create virtual environment if not exists
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Start the server
python main.py
```
The backend will be available at http://localhost:8000

**Terminal 2 - Middleware (Validation & Risk Analysis):**
```bash
cd middleware
# Create virtual environment if not exists
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Configure API key (for malpractice agent)
cp .env.example .env
# Edit .env and add your MINIMAX_API_KEY or OPENAI_API_KEY

# Start the server
python app.py
```
The middleware will be available at http://localhost:5001

**Terminal 3 - Frontend2 (Streamlit UI):**
```bash
cd frontend2
# Create virtual environment if not exists
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Start the Streamlit app
streamlit run app.py
```
The frontend will be available at http://localhost:8501

### Using the System

1. Open your browser to **http://localhost:8501**

2. **New Handoff Flow:**
   - Select a patient from the dropdown
   - Upload an audio file (WAV, MP3, M4A, WebM, OGG)
   - Click "Transcribe Audio" to convert speech to text
   - Review and edit the transcript if needed
   - Click "Save Transcript" to save as a text file
   - Click "Validate & Analyze" to run validation

3. **Validation Process:**
   - Middleware receives the transcript
   - Forwards to backend for context enrichment (SOPs, policies, guidelines)
   - Backend generates clinical warnings
   - Malpractice agent analyzes for risk/compliance issues
   - Results are returned to frontend

4. **View Results:**
   - Clinical warnings are displayed with severity levels
   - SBAR handoff card is shown
   - Patient timeline is updated with warnings
   - Risk assessment shows compliance score

### Frontend2 Features

- **📝 Record Handoff**: Upload audio files for transcription
- **📅 Patient Timeline**: Visual timeline of events and warnings
- **👥 Patient Overview**: View patient information and vitals

### API Endpoints Used

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/transcribe` | Transcribe audio (backend-api) |
| POST | `/api/v1/transcripts` | Validate transcript (middleware) |
| GET | `/health` | Health check (all services) |

## Docker Setup (Alternative)

### Prerequisites

- Docker and Docker Compose
- Python 3.11+
- Node.js 18+

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd MedXP
   ```

2. **Set up environment variables**
   
   Copy the example environment file and fill in the required values:
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` and configure the following settings:
   ```env
   # Database
   POSTGRES_PASSWORD=your_secure_password
   
   # Flask
   FLASK_SECRET_KEY=your_flask_secret_key
   
   # MinIO
   MINIO_ROOT_USER=minioadmin
   MINIO_ROOT_PASSWORD=your_minio_password
   
   # AI/LLM
   LLM_API_KEY=your_llm_api_key
   ```

3. **Start the development environment**
   ```bash
   cd docker
   ./setup.sh
   ```

   Or manually with Docker Compose:
   ```bash
   docker-compose up -d
   ```

4. **Access the application**
   - Frontend: http://localhost:3000 (Docker) or http://localhost:8080 (Dev)
   - API: http://localhost:5000 (Flask) or http://localhost:8000 (FastAPI)
   - MinIO Console: http://localhost:9001

## Project Structure

```
MedXP/
├── docs/
│   └── docs-for-ai/           # Project documentation for AI context
├── frontend/                   # React + TypeScript + Vite frontend
│   └── src/
│       ├── components/        # UI components
│       ├── hooks/             # Custom React hooks (audio recording)
│       ├── pages/             # Page components
│       └── lib/               # Utilities and API clients
├── frontend2/                  # Streamlit Python frontend
│   ├── app.py                # Main Streamlit application
│   └── requirements.txt      # Python dependencies
├── backend-api/               # FastAPI backend with audio transcription
│   ├── main.py               # FastAPI server with transcription endpoint
│   └── requirements.txt      # Python dependencies
├── middleware/                # Flask API layer for transcript validation
│   ├── app.py               # Flask application
│   └── requirements.txt      # Python dependencies
├── backend/                   # Agentic AI backend services
│   ├── agents/               # AI agents (context enrichment, malpractice)
│   └── services/             # AI services
├── audio/                     # Audio recordings storage
├── docker/                    # Docker configuration
├── Data/                      # Sample data files
│   ├── scenarios.json        # Transcript scenarios
│   └── patients_ehr.json     # Patient EHR data
└── LICENSE
```

## Technology Stack

### Frontend (React)
- React 18 with TypeScript
- Vite for development
- Tailwind CSS
- Radix UI / Shadcn/ui
- React Router
- React Query
- Custom audio recording hook

### Frontend2 (Streamlit)
- Streamlit for rapid Python UI development
- httpx for HTTP client requests
- Python 3.11+

### Backend API (Modern - backend-api)
- FastAPI
- OpenAI Whisper API for transcription
- Uvicorn
- Python 3.11+

### Middleware (Validation Layer)
- Flask (Python)
- httpx for backend communication
- Malpractice agent integration

### Backend (Agentic - backend)
- Python-based AI agents
- Context enrichment with medical knowledge
- Medical standards database (SOPs, policies, guidelines)

## API Documentation

### FastAPI (Audio Transcription - backend-api)
Once the backend-api is running, visit:
- Interactive API docs: http://localhost:8000/docs
- Alternative docs: http://localhost:8000/redoc

### Flask Middleware (Validation & Risk Analysis)
The middleware API handles transcript validation and forwards to the backend for enrichment.

#### Key Endpoints

| Method | Endpoint | Service | Description |
|--------|----------|---------|-------------|
| POST | `/api/transcribe` | backend-api | Transcribe audio using OpenAI Whisper |
| POST | `/api/v1/transcripts` | middleware | Validate transcript with backend enrichment |
| POST | `/api/v1/enrich` | backend | Context enrichment with medical knowledge |
| GET | `/health` | all | Health check endpoint |

### Transcript Validation Flow

When submitting a transcript via `/api/v1/transcripts`:

1. Middleware receives `PatientID` and `Transcript`
2. Generates enrichment request using `scn_1.json` template
3. Forwards to backend at `/api/v1/enrich`
4. Backend retrieves relevant SOPs, policies, and guidelines
5. Backend generates clinical warnings
6. Malpractice agent analyzes for risk/compliance
7. Combined response returned to frontend

## Environment Variables

### Frontend2 (.env - optional)
```
BACKEND_URL=http://127.0.0.1:8000
MIDDLEWARE_URL=http://127.0.0.1:5001
TRANSCRIPT_API_URL=http://127.0.0.1:8000
```

### Backend API (backend-api/.env)
```
OPENAI_API_KEY=your_openai_api_key_here
```

### Middleware (.env)
```
MINIMAX_API_KEY=your_minimax_api_key_here
# or
OPENAI_API_KEY=your_openai_api_key_here
```

## Data

Sample data files are located in the `Data/` directory:
- `scenarios.json`: Sample nurse-patient session transcripts
- `patients_ehr.json`: Sample patient electronic health records

## Configuration

All configuration is managed through environment variables. Copy `.env.example` to `.env` and customize as needed for your environment.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

Copyright (c) 2026. All rights reserved. No use without permission.

See the LICENSE file for details.

## Support

For issues and questions, please open an issue on GitHub.

