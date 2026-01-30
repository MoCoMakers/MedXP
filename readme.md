# MedXP - Medical Experience Platform

MedXP is a proof-of-concept clinical handoff platform designed to reduce medical malpractice and shift-change issues in hospital nursing settings. The system features AI-powered audio recording, transcription, and agentic analysis against medical standards of care.

## Overview

MedXP streamlines clinical handoffs by recording audio notes and automatically transcribing them. The platform helps healthcare professionals create structured SBAR handoff documentation efficiently while monitoring interactions against patient data and medical standards.

## Features

- 🎤 **Audio Recording**: Record clinical handoffs directly in the browser
- 📝 **AI Transcription**: Automatic transcription using OpenAI Whisper API
- 📋 **SBAR Format**: Structured handoff documentation
- 👥 **Patient Management**: Select and manage patient handoffs
- 📊 **Shift Board**: Kanban and timeline views for shift management
- 🔔 **Notifications Portal**: Alerts for nurse managers when care gaps are detected
- 🎨 **Modern UI**: Built with React, Tailwind CSS, and Shadcn/ui

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
├── backend-api/               # FastAPI backend with audio transcription
│   ├── main.py               # FastAPI server with transcription endpoint
│   └── requirements.txt      # Python dependencies
├── middleware/                # Flask API layer (legacy)
│   ├── app/
│   │   ├── routes/           # API endpoints
│   │   ├── models/           # Database models
│   │   ├── services/         # Business logic
│   │   └── utils/            # Utilities
│   └── migrations/           # Database migrations
├── backend/                   # Agentic AI backend services
│   ├── agents/               # AI agents
│   └── services/             # AI services
├── audio/                     # Audio recordings storage
├── docker/                    # Docker configuration
├── Data/                      # Sample data files
│   ├── scenarios.json        # Transcript scenarios
│   └── patients_ehr.json     # Patient EHR data
└── LICENSE
```

## Technology Stack

### Frontend
- React 18 with TypeScript
- Vite for development
- Tailwind CSS
- Radix UI / Shadcn/ui
- React Router
- React Query
- Custom audio recording hook

### Backend API (Modern)
- FastAPI
- OpenAI Whisper API for transcription
- Uvicorn
- Python 3.11+

### Middleware (Legacy)
- Flask (Python)
- PostgreSQL
- Redis (caching and Celery broker)
- Celery for async processing

### Backend (Agentic)
- Python-based AI agents
- Local LLM integration (siloed instance)
- Medical standards database

## API Documentation

### FastAPI (Audio Transcription)
Once the backend-api is running, visit:
- Interactive API docs: http://localhost:8000/docs
- Alternative docs: http://localhost:8000/redoc

### Flask Middleware
The middleware API documentation is available at `/api/docs` when running the middleware server, or see the detailed documentation in `docs/docs-for-ai/middleware-plan.md`.

#### Key Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /api/transcribe | Transcribe audio using OpenAI Whisper |
| POST | /api/transcripts/process | Submit transcript for processing |
| GET | /api/transcripts/{id}/classification | Get classification results |
| GET | /api/notifications | List notifications |
| GET | /api/dashboard/stats | Get dashboard statistics |

## Environment Variables

### Backend API (.env)
```
OPENAI_API_KEY=your_openai_api_key_here
```

### Middleware (.env)
```
POSTGRES_PASSWORD=your_secure_password
FLASK_SECRET_KEY=your_flask_secret_key
MINIO_ROOT_USER=minioadmin
MINIO_ROOT_PASSWORD=your_minio_password
LLM_API_KEY=your_llm_api_key
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

