# Argus Reimagined V2

![Python 3.11](https://img.shields.io/badge/python-3.11-blue)
---

**An Intelligent, Event-Driven Gamified LMS Backend**

Argus is a state-aware educational technology backend designed to treat student engagement as a real-time data stream. By combining an event-sourced architecture with a multi-modal AI Copilot, Argus delivers a deeply gamified, intensely competitive, and instantly responsive learning platform.

A modern educational platform built with a **FastAPI** backend, **Tailwind CSS** powered frontend, and a **local Elasticsearch** hybrid (BM25 + vector) search service.

## Table of Contents
- [Platform Features](#platform-features)
- [Technical Architecture](#technical-architecture)
- [Getting Started](#getting-started)
  - [Requirements](#requirements)
  - [Setup and Run](#setup-and-run)
  - [Enabling Search](#enabling-search)
- [Configuration](#configuration)
- [Usage](#usage)
- [Notes](#notes)
- [Running Tests](#running-tests)
- [Contributing](#contributing)

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

* **Active Tracking:** =
---

## 🏗️ Technical Architecture

The platform relies on a reactive, async-first stack to handle high concurrency.

| Component | Technology | Purpose |
| --- | --- | --- |
| **API Framework** | FastAPI (Python) | High-concurrency async endpoints and WebSocket state injection. |
| **Primary Database** | SQLite (SQLAlchemy async) | Simple file‑based DB used by default; can be swapped for PostgreSQL via `DATABASE_URL`. |
| **Event Bus & Cache** | Redis Streams | Pub/Sub event broadcasting, active session state, and leaderboard caching. |
| **Background Workers** | Celery | Async tasks for audio transcription, index flattening, and rank rebalancing. |
| **Search Engine** | Elasticsearch + Qdrant | Hybrid vector and keyword retrieval. |
| **AI Orchestration** | Groq & Gemini API | Tier 1 (Mistral) for instant tasks; Tier 2 (Gemini 1.5 Pro) for multimodal reasoning. |

---

## Getting Started

### Requirements
- Python 3.11+
- Docker (Optional, for Elasticsearch)
- PostgreSQL (Optional, via Docker)

### Setup and Run

1. **Clone the repository**:
```bash
   git clone <repository-url>
   cd stitch_argusreimaginedv2_main
```

2. **Run the setup script** (Windows):
```bash
  
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

## Contributing

Contributions are welcome! Fork the repository, create a feature branch, and open a pull request. Please ensure any new code follows the existing style guidelines and includes appropriate tests.

## Enabling Search

To enable hybrid search functionality:

- Ensure Elasticsearch is running (`docker compose up -d elasticsearch`).
- Uncomment the search router import and inclusion in `backend/app/api/v1/router.py`.

3. **Access the application**:
   - API: http://localhost:8000/
   - Swagger UI: http://localhost:8000/docs
    - Frontend: http://localhost:8000/

## Search Implementation Details

- The **search endpoint** (`GET /api/v1/search`) now:
  1. Guarantees the `argus_knowledge` index exists by calling `init_index`.
  2. Executes a **BM25‑only** query via a direct `httpx` request to Elasticsearch, avoiding compatibility‑header issues.
  3. Returns each hit’s `_source` together with its `_id`.

- **Embedding handling** in `index_document`:
  * Generates an embedding with `sentence‑transformers`.
  * If the resulting vector is all zeros (e.g., empty content), the `text_vector` field is omitted to avoid Elasticsearch’s *zero‑magnitude* error with `cosine` similarity.
  * Otherwise, the vector is stored alongside the document.

- The original hybrid BM25 + k‑NN logic remains in the codebase for future activation but is disabled for stability.

- When Elasticsearch is unavailable, the endpoint gracefully returns an empty `results` array instead of raising an exception, providing graceful degradation.


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

## Running Tests

- Quick integration test (makes a health check, registers a user, logs in, and fetches the profile):
  ```bash
  python test_api.py
  ```
- If a pytest suite exists, run the full test suite:
  ```bash
  pytest
  ```
