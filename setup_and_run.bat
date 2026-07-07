@echo off

rem Remove any existing virtual environment to ensure a clean setup
if exist .venv rmdir /s /q .venv

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
pip install -r requirements.txt && pip install "pydantic_core==2.46.4"

if %ERRORLEVEL% neq 0 (
    echo Error installing dependencies
    exit /b 1
)

echo [3/5] Seeding database...
C:\Users\DELL\AppData\Local\Temp\kilo\venv\Scripts\python.exe seed_db.py

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