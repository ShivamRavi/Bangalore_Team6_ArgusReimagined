# Argus Reimagined V2
---

**An Intelligent, Event-Driven Gamified LMS Backend**

Argus is a state-aware educational technology backend designed to treat student engagement as a real-time data stream. By combining an event-sourced architecture with a multi-modal AI Copilot, Argus delivers a deeply gamified, intensely competitive, and instantly responsive learning platform.

A modern educational platform built with a **FastAPI** backend, **Tailwind CSS** powered frontend, and a **local Elasticsearch** hybrid (BM25 + vector) search service.

---

##  Platform Features

###  Context-Aware AI "Omni-Tutor"

Argus doesn't just offer a generic chat bar; it understands exactly what the student is looking at in real-time.

* **Screen-State Injection:** When a student asks a question, the backend instantly injects their exact location (e.g., "PDF Page 12" or "Video timestamp 14:30") into the AI's prompt.
* **Pre-emptive Caching:** Uploading a large PDF or 2-hour lecture automatically creates a server-side Gemini Context Cache, dropping AI response times to sub-500ms without burning through token budgets.

### Zero-Exploit Gamified Economy

A dual-currency system built on a strict, bank-grade transactional ledger to prevent double-spending and race conditions.

* **Euros (Individual Progression):** Earned via active, verified engagement (e.g., +10 for passing a worksheet, +5 for completing a video with no focus interruptions).
* **House Points (Communal Pool):** A collective score driven by individual 10-day login streaks (+2 HP), rank promotions, and athletic events, fostering team-based competition.

###  Automated Planetary Rank System

Progression is gated by automated cognitive checks, ensuring students actually master the material before advancing.

* **The 3-Quiz Gate:** Unlocking a new "Planet" triggers an adaptive sequence (Hard -> Medium -> Easy). Passing grants currency; failing all three penalizes the user, creating real stakes.
* **The Andromeda Sync (Apex Rank):** The highest achievable rank is dynamically capped using the capacity formula $x = 3 \times s$ (where $x$ is the max allowed students and $s$ is the total number of sections). A weekly background worker automatically demotes inactive students and promotes rising stars.

### Deep-Dive Hybrid Media Search

Students can search across the entire curriculum and pinpoint exact moments in lectures.

* **Automated Transcription:** Video and audio uploads are instantly transcribed using Whisper-large-v3.
* **Semantic Intent:** Search queries perform Reciprocal Rank Fusion, blending exact keyword matching with semantic vector intent to return the precise video timestamp or document paragraph the student needs.

###  Real-Time Learner State Machine

Every action—from a failed quiz to pausing a podcast—emits a real-time event.

* **Active Tracking:** The system continuously updates the student's cognitive state and focus score, allowing the platform to dynamically adjust difficulty or trigger an AI intervention.

---

## 🏗️ Technical Architecture

The platform relies on a reactive, async-first stack to handle high concurrency.

| Component | Technology | Purpose |
| --- | --- | --- |
| **API Framework** | FastAPI (Python) | High-concurrency async endpoints and WebSocket state injection. |
| **Primary Database** | PostgreSQL (SQLAlchemy 2.0) | Strict ACID compliance with `SELECT ... FOR UPDATE` row-level locking. |
| **Event Bus & Cache** | Redis Streams | Pub/Sub event broadcasting, active session state, and leaderboard caching. |
| **Background Workers** | Celery | Async tasks for audio transcription, index flattening, and rank rebalancing. |
| **Search Engine** | Elasticsearch + Qdrant | Hybrid vector and keyword retrieval. |
| **AI Orchestration** | Groq & Gemini API | Tier 1 (Mistral) for instant tasks; Tier 2 (Gemini 1.5 Pro) for multimodal reasoning. |

---

## Getting Started

### Requirements
- Python 3.11+
- Docker (Optional, for Elasticsearch)

### Setup and Run

1. **Clone the repository**:
```bash
   git clone <repository-url>
   cd stitch_argusreimaginedv2_main
```

2. **Run the setup script** (Windows):
```bash
   setup_and_run.bat
```

   Or manually:
   ```bash
   python -m venv .venv
   .venv\Scripts\activate
   pip install -r requirements.txt
   python -c "import asyncio; from backend.app.seed import seed_houses_and_sections; from backend.app.database import get_db; async def run(): async with get_db() as db: await seed_houses_and_sections(db); asyncio.run(run())"
   docker compose up -d elasticsearch  # Optional, if Docker is available
   uvicorn backend.app.main:app --reload
   ```

3. **Access the application**:
   - API: http://localhost:8000/
   - Swagger UI: http://localhost:8000/docs
   - Frontend: http://localhost:8000/

## Configuration

Copy `.env.example` to `.env` and configure the variables:

```
# Database
DATABASE_URL=sqlite+aiosqlite:///./argus.db

# Security
SECRET_KEY=argus-secret-key-1234567890abcdefghijklmnopqrstuvwxyz
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Elasticsearch
ELASTICSEARCH_URL=http://localhost:9200

# Redis (optional)
REDIS_URL=redis://localhost:6379/0

# CORS
CORS_ORIGINS=["*"]
```

## Usage

1. **Register** a new account on the home page
2. **Login** with your credentials
3. **Complete activities** and earn euros
4. **Search** for learning content
5. **Track progress** on your dashboard

## Notes

- Without Docker, Elasticsearch won't be available and search features will return empty results
- Sample data is seeded automatically during first run