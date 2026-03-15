@echo off
REM ============================================================
REM  C-C-C-COOLASSAPP — Setup Script
REM  Run this once to set up the project on Windows
REM ============================================================

echo.
echo ============================================================
echo  C-C-C-COOLASSAPP
echo  Windows Setup Script
echo ============================================================
echo.

REM Check Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python not found. Please install Python 3.10+
    echo         https://www.python.org/downloads/
    pause
    exit /b 1
)

REM Create virtual environment
echo [1/4] Creating virtual environment...
if not exist "venv" (
    python -m venv venv
    echo       Virtual environment created.
) else (
    echo       Virtual environment already exists.
)

REM Activate and install dependencies
echo [2/4] Installing dependencies...
call venv\Scripts\activate.bat
pip install -r requirements.txt --quiet

REM Initialize database and create admin user
echo [3/4] Initializing database...
echo [4/4] Creating default admin user...
python setup_db.py

echo.
echo ============================================================
echo  Setup complete!
echo.
echo  To start the application:
echo    venv\Scripts\activate.bat
echo    python run.py
echo.
echo  Then open http://localhost:5000 in your browser
echo  Login: admin / admin
echo ============================================================
echo.
pause
