# Argus Gamified Learning Management System

A learning management system with gamified progress tracking, leaderboards, and rewards.

## Features

- **Authentication** with JWT tokens
- **Gamified activities** with euro rewards
- **User profiles** with houses and sections
- **Hybrid search** across learning content
- **Progress tracking** with streaks and planets

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