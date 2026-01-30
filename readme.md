# Medical XP (Medical Experience)

Medical XP is a proof-of-concept system designed to reduce medical malpractice and shift-change issues in hospital nursing settings. The system monitors nurse-patient interactions through audio recording, AI-powered transcription, and agentic analysis against medical standards of care.

## Features

- **Nurse Portal**: Oversight of nursing activities and session reviews
- **Audio Recording**: Capture and transcription of patient sessions
- **AI Classification**: Automated tagging and categorization of session content
- **Agentic Monitoring**: Real-time comparison of interactions against patient data and medical standards
- **Notifications Portal**: Alerts for nurse managers when care gaps are detected

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Python 3.11+
- Node.js 18+ (for frontend development)

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
   - Frontend: http://localhost:3000
   - API: http://localhost:5000
   - MinIO Console: http://localhost:9001

## Project Structure

```
MedXP/
├── docs/
│   └── docs-for-ai/           # Project documentation for AI context
├── frontend/                   # React/Lovable frontend application
├── middleware/                 # Flask API layer
│   ├── app/
│   │   ├── routes/            # API endpoints
│   │   ├── models/            # Database models
│   │   ├── services/          # Business logic
│   │   └── utils/             # Utilities
│   └── migrations/            # Database migrations
├── backend/                    # Agentic AI backend services
│   ├── agents/                # AI agents
│   └── services/              # AI services
├── docker/                     # Docker configuration
├── Data/                       # Sample data files
│   ├── scenarios.json         # Transcript scenarios
│   └── patients_ehr.json      # Patient EHR data
└── LICENSE
```

## Technology Stack

### Frontend
- React with TypeScript
- Material-UI
- Zustand for state management
- Vite for development

### Middleware
- Flask (Python)
- PostgreSQL
- Redis (caching and Celery broker)
- Celery for async processing

### Backend (Agentic)
- Python-based AI agents
- Local LLM integration (siloed instance)
- Medical standards database

## API Documentation

The API documentation is available at `/api/docs` when running the middleware server, or see the detailed documentation in `docs/docs-for-ai/middleware-plan.md`.

### Key Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /api/transcripts/process | Submit transcript for processing |
| GET | /api/transcripts/{id}/classification | Get classification results |
| GET | /api/notifications | List notifications |
| GET | /api/dashboard/stats | Get dashboard statistics |

## Data

Sample data files are located in the `Data/` directory:
- `scenarios.json`: Sample nurse-patient session transcripts
- `patients_ehr.json`: Sample patient electronic health records

## Configuration

All configuration is managed through environment variables. Copy `.env.example` to `.env` and customize as needed for your environment.

## License

Copyright (c) 2026. All rights reserved. No use without permission.

See the LICENSE file for more details.
