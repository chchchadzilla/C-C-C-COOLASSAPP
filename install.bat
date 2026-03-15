@echo off
REM ============================================================================
REM  C-C-C-COOLASSAPP — One-Click Windows Installer
REM  
REM  Carefully-Crafted-Claude-Code Original Orchestration Layer
REM  And Super Serious Appropriately Positioned Project
REM
REM  Just double-click this file. It does everything.
REM ============================================================================

setlocal enabledelayedexpansion

echo.
echo  ============================================================================
echo   🧊 C-C-C-COOLASSAPP — One-Click Installer
echo  ============================================================================
echo.

REM ── Step 0: Check we're in the right folder ──────────────────────────────────
if not exist "app.py" (
    echo  [ERROR] app.py not found in the current directory.
    echo          Make sure you run this from the C-C-C-COOLASSAPP project folder.
    echo.
    echo  Current directory: %CD%
    echo.
    pause
    exit /b 1
)

if not exist "requirements.txt" (
    echo  [ERROR] requirements.txt not found.
    echo          This doesn't look like the right project folder.
    echo.
    pause
    exit /b 1
)

echo  [OK] Project files found.
echo.

REM ── Step 1: Check Python ─────────────────────────────────────────────────────
echo  [1/6] Checking Python installation...

python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo  [ERROR] Python is NOT installed, or not on your PATH.
    echo.
    echo  ┌─────────────────────────────────────────────────────────────┐
    echo  │  HOW TO FIX THIS:                                          │
    echo  │                                                             │
    echo  │  1. Go to https://www.python.org/downloads/                 │
    echo  │  2. Download Python 3.10 or newer                           │
    echo  │  3. Run the installer                                       │
    echo  │  4. *** CHECK THE BOX: "Add Python to PATH" ***             │
    echo  │     (This is the most common mistake. Don't skip it.)       │
    echo  │  5. Restart your computer                                   │
    echo  │  6. Double-click this file again                            │
    echo  └─────────────────────────────────────────────────────────────┘
    echo.
    pause
    exit /b 1
)

REM Check Python version is 3.10+
for /f "tokens=2 delims= " %%v in ('python --version 2^>^&1') do set PYVER=%%v
for /f "tokens=1,2 delims=." %%a in ("%PYVER%") do (
    set PYMAJOR=%%a
    set PYMINOR=%%b
)

if %PYMAJOR% LSS 3 (
    echo  [ERROR] Python %PYVER% is too old. You need Python 3.10 or newer.
    echo          Download it from https://www.python.org/downloads/
    pause
    exit /b 1
)

if %PYMAJOR%==3 if %PYMINOR% LSS 10 (
    echo  [ERROR] Python %PYVER% is too old. You need Python 3.10 or newer.
    echo          Download it from https://www.python.org/downloads/
    pause
    exit /b 1
)

echo        Python %PYVER% ✓
echo.

REM ── Step 2: Create virtual environment ───────────────────────────────────────
echo  [2/6] Creating virtual environment...

if exist "venv\Scripts\python.exe" (
    echo        Virtual environment already exists ✓
) else (
    python -m venv venv
    if %errorlevel% neq 0 (
        echo  [ERROR] Failed to create virtual environment.
        echo          Try running: python -m venv venv
        pause
        exit /b 1
    )
    echo        Created venv/ ✓
)
echo.

REM ── Step 3: Install dependencies ────────────────────────────────────────────
echo  [3/6] Installing dependencies (this may take a minute)...

venv\Scripts\pip.exe install -r requirements.txt --quiet
if %errorlevel% neq 0 (
    echo.
    echo  [ERROR] Failed to install dependencies.
    echo          Try running manually:
    echo            venv\Scripts\activate
    echo            pip install -r requirements.txt
    pause
    exit /b 1
)

echo        All dependencies installed ✓
echo.

REM ── Step 4: Create .env file ────────────────────────────────────────────────
echo  [4/6] Setting up configuration...

if exist ".env" (
    echo        .env already exists, keeping your settings ✓
) else (
    if exist ".env.example" (
        copy .env.example .env >nul
        echo        Copied .env.example to .env ✓
        echo        TIP: Edit .env to set a real SECRET_KEY for production
    ) else (
        echo SECRET_KEY=dev-key-change-me-in-production> .env
        echo DATABASE_URL=sqlite:///orchestration.db>> .env
        echo FLASK_ENV=development>> .env
        echo FLASK_DEBUG=1>> .env
        echo        Created default .env ✓
    )
)
echo.

REM ── Step 5: Initialize database ─────────────────────────────────────────────
echo  [5/6] Initializing database...

venv\Scripts\python.exe setup_db.py
if %errorlevel% neq 0 (
    echo.
    echo  [ERROR] Database initialization failed.
    echo          Try running manually:
    echo            venv\Scripts\python.exe setup_db.py
    pause
    exit /b 1
)

echo        Database ready ✓
echo.

REM ── Step 6: Launch ──────────────────────────────────────────────────────────
echo  [6/6] Starting server...
echo.
echo  ============================================================================
echo   🧊 C-C-C-COOLASSAPP is starting!
echo  ============================================================================
echo.
echo   URL:       http://127.0.0.1:5000
echo   Login:     http://127.0.0.1:5000/login
echo.
echo   Default credentials:
echo     Username: admin
echo     Password: admin
echo     (You'll be asked to change the password on first login)
echo.
echo   Press Ctrl+C to stop the server.
echo  ============================================================================
echo.

REM Open browser
start "" http://127.0.0.1:5000/login

REM Start the server (this blocks)
venv\Scripts\python.exe run_server.py

pause
