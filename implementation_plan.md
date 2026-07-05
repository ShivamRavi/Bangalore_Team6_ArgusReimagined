# Phase 1: Core Scaffolding, Auth & Frontend Sync — Argus LMS Backend

## Context & Frontend Analysis

The existing frontend is a collection of **static HTML/Tailwind mockups** (not a React/Vue app with service files). These define the visual contract and data shapes the backend must serve. Key findings from the analysis:

### Frontend Data Contract (Inferred from UI Mockups)

| Screen | Key Data Points |
|---|---|
| **Login** ([code.html](file:///d:/stitch_argusreimaginedv2_main/stitch_argusreimaginedv2_main/argus_login_glassmorphic_immersion/code.html)) | Role tabs: `Student / Staff / Parent`. Fields: `identifier` (enrollment/phone/user ID), `password`. OTP login support. |
| **Leaderboard** ([code.html](file:///d:/stitch_argusreimaginedv2_main/stitch_argusreimaginedv2_main/leaderboard_newton_ai_chat_integration/code.html)) | **Two tabs**: "My Grade" (individual Euro leaderboard) and "House Leads" (House Points). Header shows: current planet (Mercury League), `2,450 Euros`. Houses: Poseidon (Blue), Mercury (Red), Apollo (Yellow), Zeus (Green). Planet ranks: Mercury→Venus→Earth→Mars→Jupiter→Saturn→Uranus→Neptune→Andromeda(Cosmic) with thresholds 0, 500, 1000, 1500, 2000, 2500, 3000, 3500, 4500+. |
| **Dashboard** ([code.html](file:///d:/stitch_argusreimaginedv2_main/stitch_argusreimaginedv2_main/argus_dashboard_sticky_nav_extended_quiz_center_1/code.html)) | User profile (name, grade, section). Newton AI chat drawer with "Answer & Earn: 10 Euros". Courses, quizzes, discussions. |
| **Search** ([code.html](file:///d:/stitch_argusreimaginedv2_main/stitch_argusreimaginedv2_main/argus_search_updated_branding_and_top_bar_style_1/code.html)) | Search results with timestamps (02:15, 08:45, 15:30), AI Digest flashcards, worksheets, courses, individual lessons with `+50 XP` / `+80 XP` potential. |
| **Podcast** ([code.html](file:///d:/stitch_argusreimaginedv2_main/stitch_argusreimaginedv2_main/argus_podcast_newton_ai_integration/code.html)) | Audio waveform, live transcript, Newton AI integration per resource. |
| **Design System** ([design.md](file:///d:/stitch_argusreimaginedv2_main/stitch_argusreimaginedv2_main/design.md), [DESIGN.md](file:///d:/stitch_argusreimaginedv2_main/stitch_argusreimaginedv2_main/argus_celestial/DESIGN.md)) | Argus Celestial theme. Colors: deep indigos/purples. Gamified colors: `exp-gold`, `streak-flame`, `mars-red`. |

> [!IMPORTANT]
> Since the frontend is static HTML mockups (no JS framework, no API service files, no fetch/axios calls), I will **define the REST API contract** to serve the data shapes visible in the UI, and design Pydantic schemas that can power these screens.

---

## Phase 1 Scope

Phase 1 establishes the foundational project scaffolding:

1. **Project structure** with proper Python packaging
2. **FastAPI application** with CORS, exception handlers, structured JSON logging
3. **Async SQLAlchemy 2.0 models** for all 4 tables (Houses, Sections, Users, Transactions)
4. **Alembic migration** setup with initial migration
5. **JWT Auth** (OAuth2 Password Bearer) with login, register, refresh, and `/me` endpoints
6. **Configuration** via Pydantic Settings (env-based)
7. **Auth integration tests** using pytest-asyncio + httpx

---

## Proposed Changes

### Project Root Directory

The backend will be created at:
```
d:\stitch_argusreimaginedv2_main\stitch_argusreimaginedv2_main\backend\
```

### Directory Structure

```
backend/
├── alembic/                    # Alembic migrations
│   ├── versions/               # Migration scripts
│   ├── env.py
│   └── script.py.mako
├── alembic.ini
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI app factory, CORS, exception handlers
│   ├── config.py               # Pydantic Settings (env-based config)
│   ├── database.py             # Async engine, sessionmaker, Base
│   ├── models/
│   │   ├── __init__.py
│   │   ├── house.py            # House model
│   │   ├── section.py          # Section model
│   │   ├── user.py             # User model (UUID PK, planet, streak, euros)
│   │   └── transaction.py      # Transaction model (audit trail)
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── auth.py             # Login, Register, Token schemas
│   │   └── user.py             # UserResponse, UserProfile schemas
│   ├── api/
│   │   ├── __init__.py
│   │   └── v1/
│   │       ├── __init__.py
│   │       ├── router.py       # v1 API router aggregator
│   │       └── auth.py         # POST /login, POST /register, POST /refresh, GET /me
│   ├── core/
│   │   ├── __init__.py
│   │   ├── security.py         # JWT creation, verification, password hashing
│   │   └── dependencies.py     # get_db, get_current_user dependencies
│   └── middleware/
│       ├── __init__.py
│       └── logging.py          # Structured JSON request/response logger
├── tests/
│   ├── __init__.py
│   ├── conftest.py             # Fixtures: async test DB, client, auth helpers
│   ├── test_auth.py            # Auth integration tests
│   └── test_models.py          # Model creation & constraint tests
├── requirements.txt
├── .env.example
└── pyproject.toml
```

---

### Core Infrastructure

#### [NEW] [config.py](file:///d:/stitch_argusreimaginedv2_main/stitch_argusreimaginedv2_main/backend/app/config.py)
- Pydantic `BaseSettings` with:
  - `DATABASE_URL` (async pg: `postgresql+asyncpg://...`)
  - `REDIS_URL`
  - `SECRET_KEY`, `ALGORITHM` (HS256), `ACCESS_TOKEN_EXPIRE_MINUTES` (30), `REFRESH_TOKEN_EXPIRE_DAYS` (7)
  - `CORS_ORIGINS` (list)
  - `GROQ_API_KEY`, `GEMINI_API_KEY` (optional, for later phases)
  - `ELASTICSEARCH_URL` (optional)

#### [NEW] [database.py](file:///d:/stitch_argusreimaginedv2_main/stitch_argusreimaginedv2_main/backend/app/database.py)
- `create_async_engine` with pool configuration
- `async_sessionmaker` with `expire_on_commit=False`
- `Base = declarative_base()` for model inheritance
- `get_db()` async generator dependency

#### [NEW] [main.py](file:///d:/stitch_argusreimaginedv2_main/stitch_argusreimaginedv2_main/backend/app/main.py)
- FastAPI app with metadata (title, version, description)
- CORS middleware with configurable origins
- Global exception handlers:
  - `RequestValidationError` → 422 with structured error body
  - `HTTPException` → pass-through
  - Generic `Exception` → 500 with structured error + logging
- Include `/api/v1` router
- Startup/shutdown lifespan events for DB engine lifecycle

---

### SQLAlchemy Models (4 Tables)

#### [NEW] [house.py](file:///d:/stitch_argusreimaginedv2_main/stitch_argusreimaginedv2_main/backend/app/models/house.py)
```python
class House(Base):
    __tablename__ = "houses"
    id: int           # PK, autoincrement
    name: str         # Unique, NOT NULL
    total_points: int # Indexed, default=0
```
Seeded houses: Poseidon (Blue), Mercury (Red), Apollo (Yellow), Zeus (Green) — matching the leaderboard UI.

#### [NEW] [section.py](file:///d:/stitch_argusreimaginedv2_main/stitch_argusreimaginedv2_main/backend/app/models/section.py)
```python
class Section(Base):
    __tablename__ = "sections"
    id: int           # PK, autoincrement
    name: str         # e.g. "Grade 12-A"
    student_count: int # default=0
```

#### [NEW] [user.py](file:///d:/stitch_argusreimaginedv2_main/stitch_argusreimaginedv2_main/backend/app/models/user.py)
```python
class User(Base):
    __tablename__ = "users"
    id: UUID          # PK, server_default=gen_random_uuid()
    username: str     # Unique, NOT NULL, Indexed
    hashed_password: str
    role: str         # Enum: 'student', 'staff', 'parent' (from login tabs)
    house_id: int     # FK → houses.id, nullable for staff/parent
    section_id: int   # FK → sections.id, nullable for staff/parent
    euros_balance: int    # Indexed (for leaderboard sorting), default=0
    lifetime_euros: int   # default=0
    current_planet: str   # default='Mercury' (PlanetEnum)
    current_streak: int   # default=0
    last_active_at: datetime  # Indexed, server_default=now()
    created_at: datetime
    updated_at: datetime
```

#### [NEW] [transaction.py](file:///d:/stitch_argusreimaginedv2_main/stitch_argusreimaginedv2_main/backend/app/models/transaction.py)
```python
class CurrencyType(str, Enum):
    EUROS = "euros"
    HOUSE_POINTS = "house_points"

class Transaction(Base):
    __tablename__ = "transactions"
    id: UUID          # PK
    user_id: UUID     # FK → users.id, Indexed
    currency_type: CurrencyType  # Enum
    amount: int
    reason: str
    created_at: datetime  # Indexed
```

#### Planet Progression Thresholds (Constants)
From the Rank Info modal in the leaderboard UI:
```python
PLANET_THRESHOLDS = {
    "Mercury": 0,
    "Venus": 500,
    "Earth": 1000,
    "Mars": 1500,
    "Jupiter": 2000,
    "Saturn": 2500,
    "Uranus": 3000,
    "Neptune": 3500,
    "Andromeda": 4500,
}
```

---

### Authentication System

#### [NEW] [security.py](file:///d:/stitch_argusreimaginedv2_main/stitch_argusreimaginedv2_main/backend/app/core/security.py)
- `hash_password(password: str) -> str` via `passlib[bcrypt]`
- `verify_password(plain: str, hashed: str) -> bool`
- `create_access_token(data: dict, expires_delta: timedelta) -> str`
- `create_refresh_token(data: dict) -> str`
- `decode_token(token: str) -> dict` with expiry validation

#### [NEW] [auth.py (schemas)](file:///d:/stitch_argusreimaginedv2_main/stitch_argusreimaginedv2_main/backend/app/schemas/auth.py)
```python
class RegisterRequest:
    username: str       # Maps to "Enrollment Number / Phone Number / User ID"
    password: str
    role: Literal["student", "staff", "parent"]
    house_id: int | None     # Required for students
    section_id: int | None   # Required for students

class LoginRequest:
    username: str
    password: str

class TokenResponse:
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class RefreshRequest:
    refresh_token: str
```

#### [NEW] [auth.py (routes)](file:///d:/stitch_argusreimaginedv2_main/stitch_argusreimaginedv2_main/backend/app/api/v1/auth.py)
| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/v1/auth/register` | Create user, hash password, return tokens |
| `POST` | `/api/v1/auth/login` | Validate credentials, return access + refresh tokens |
| `POST` | `/api/v1/auth/refresh` | Validate refresh token, issue new access token |
| `GET` | `/api/v1/auth/me` | Return current user profile (protected) |

#### [NEW] [user.py (schemas)](file:///d:/stitch_argusreimaginedv2_main/stitch_argusreimaginedv2_main/backend/app/schemas/user.py)
Response shape matches the header bar UI:
```python
class UserResponse:
    id: UUID
    username: str
    role: str
    house_name: str | None
    section_name: str | None
    euros_balance: int          # "2,450 Euros" in top bar
    lifetime_euros: int
    current_planet: str         # "Mercury League" in top bar
    current_streak: int
    last_active_at: datetime
    created_at: datetime
```

---

### Alembic Migrations

#### [NEW] Alembic configuration
- `alembic.ini` configured with async PostgreSQL URL
- `env.py` with async migration support
- Initial migration creating all 4 tables with proper:
  - Indexes on `users.euros_balance`, `users.last_active_at`, `users.username`
  - Indexes on `transactions.user_id`, `transactions.created_at`
  - Indexes on `houses.total_points`
  - Foreign key constraints with `ON DELETE` rules
  - Check constraints (e.g., `euros_balance >= 0`)

---

### Middleware & Logging

#### [NEW] [logging.py](file:///d:/stitch_argusreimaginedv2_main/stitch_argusreimaginedv2_main/backend/app/middleware/logging.py)
- Structured JSON logging via `structlog` or Python stdlib
- Request/response logging middleware:
  - Method, path, status code, duration_ms
  - Request ID correlation
  - Excludes sensitive fields (passwords, tokens)

---

### Testing

#### [NEW] [conftest.py](file:///d:/stitch_argusreimaginedv2_main/stitch_argusreimaginedv2_main/backend/tests/conftest.py)
- Async SQLite test database (in-memory) for fast test execution
- `async_client` fixture using `httpx.AsyncClient` with `ASGITransport`
- `test_db` fixture that creates/drops all tables per test session
- Helper fixtures for creating test users and getting auth tokens

#### [NEW] [test_auth.py](file:///d:/stitch_argusreimaginedv2_main/stitch_argusreimaginedv2_main/backend/tests/test_auth.py)
Tests:
1. ✅ Register a new student with valid data → 201 + tokens returned
2. ✅ Register with duplicate username → 409 Conflict
3. ✅ Register student without house_id → 422 Validation Error
4. ✅ Login with correct credentials → 200 + tokens
5. ✅ Login with wrong password → 401 Unauthorized
6. ✅ Login with non-existent user → 401 Unauthorized
7. ✅ Access `/me` with valid token → 200 + user profile
8. ✅ Access `/me` without token → 401
9. ✅ Access `/me` with expired token → 401
10. ✅ Refresh token flow → new access token
11. ✅ Refresh with invalid token → 401

#### [NEW] [test_models.py](file:///d:/stitch_argusreimaginedv2_main/stitch_argusreimaginedv2_main/backend/tests/test_models.py)
Tests:
1. ✅ Create House with unique name
2. ✅ Create User with FK to House and Section
3. ✅ Create Transaction linked to User
4. ✅ Unique constraint on username
5. ✅ Default values for euros_balance, current_planet

---

## Open Questions

> [!IMPORTANT]
> **1. Database Choice for Testing:** The spec mentions Testcontainers for ephemeral Postgres. For Phase 1, I'll use **async SQLite in-memory** for fast, zero-dependency tests. I'll upgrade to Testcontainers in Phase 2 when we test `FOR UPDATE` row locking (which requires real Postgres). Is this acceptable?

> [!IMPORTANT]
> **2. Role-Based Access Control:** The login UI shows Student/Staff/Parent tabs. Should Staff and Parent have different API permissions (e.g., Staff can view all students' data, Parents can view only their child's data)? Or is role just a user attribute for now?

> [!IMPORTANT]
> **3. Seed Data:** Should Phase 1 include a seed script to populate the 4 Houses (Poseidon, Mercury, Apollo, Zeus) and sample Sections (Grade 12-A, Grade 12-B, etc.) visible in the UI? I plan to include this as part of the initial migration.

> [!IMPORTANT]
> **4. OTP Login:** The login UI has "Login Using OTP" button. Should I stub this endpoint now (return 501 Not Implemented) or defer to a later phase?

---

## Verification Plan

### Automated Tests
```bash
cd backend
pip install -r requirements.txt
pytest tests/ -v --asyncio-mode=auto
```

### Manual Verification
- Run `alembic upgrade head` against a local PostgreSQL and verify all tables are created
- Hit `/api/v1/auth/register` and `/api/v1/auth/login` with curl/httpx
- Verify JWT tokens decode correctly and `/me` returns the expected user shape
- Confirm CORS headers are present in responses
- Verify structured JSON logs appear in stdout
