@echo off

echo ==============================
echo Argus LMS Setup and Run Script
echo ==============================

echo [1/5] Creating virtual environment...
python -m venv .venv

if %ERRORLEVEL% neq 0 (
    echo Error creating virtual environment
    exit /b 1
)

echo [2/5] Activating virtual environment and installing dependencies...
call .venv\Scripts\activate.bat
pip install -r requirements.txt

if %ERRORLEVEL% neq 0 (
    echo Error installing dependencies
    exit /b 1
)

echo [3/5] Seeding database...
python -c "import asyncio; from backend.app.seed import seed_houses_and_sections; from backend.app.database import get_db; async def run(): async with get_db() as db: await seed_houses_and_sections(db); asyncio.run(run())"

if %ERRORLEVEL% neq 0 (
    echo Error seeding database
    exit /b 1
)

echo [4/5] Starting Elasticsearch container (if Docker is available)...
docker compose up -d elasticsearch 2>nul || echo Docker not available, Elasticsearch will not run

if %ERRORLEVEL% equ 0 (
    echo Waiting for Elasticsearch to initialize...
    timeout /t 30
) else (
    echo Elasticsearch will not be available - search features will not work
)

echo [5/5] Starting FastAPI server...
uvicorn backend.app.main:app --reload