# Argus

> **An Intelligent, Event-Driven Gamified LMS Backend**

Argus is a state-aware educational technology backend designed to treat student engagement as a real-time data stream. By combining an event-sourced architecture with a multi-modal AI Copilot, Argus delivers a deeply gamified, intensely competitive, and instantly responsive learning platform.

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

### Prerequisites

* Python 3.12+
* PostgreSQL 16+
* Redis 7+
* Elasticsearch & Qdrant instances

### 1. Environment Configuration

Create a `.env` file in the root directory.

| Variable | Description |
| --- | --- |
| `DATABASE_URL` | Async Postgres connection string (`postgresql+asyncpg://...`) |
| `REDIS_URL` | Redis instance for Streams and Caching |
| `GROQ_API_KEY` | API key for Tier 1 inference and Whisper transcription |
| `GEMINI_API_KEY` | API key for Tier 2 multimodal reasoning and Context Caching |

### 2. Installation & Setup

Install dependencies, run database migrations, and start the development server.

```bash
# Clone the repository and navigate to the directory
git clone https://github.com/your-org/argus-backend.git
cd argus-backend

# Install dependencies using Poetry or pip
pip install -r requirements.txt

# Run Alembic migrations to build the schema (Users, Houses, Sections)
alembic upgrade head

# Start the FastAPI application with Uvicorn
uvicorn app.main:app --reload --workers 4

```

### 3. Background Services

You will need to run the Celery worker and beat scheduler in separate terminal windows to handle transcriptions and the weekly Andromeda rank rebalancing.

```bash
# Start the Celery Worker
celery -A app.core.celery_app worker --loglevel=info

# Start the Celery Beat Scheduler
celery -A app.core.celery_app beat --loglevel=info

```
