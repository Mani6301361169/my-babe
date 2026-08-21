@echo off
REM J.A.R.V.I.S Web - Quick Start Script (Windows)

echo.
echo ===============================================
echo   J.A.R.V.I.S Web - Voice-Activated AI Assistant
echo ===============================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://www.python.org/
    pause
    exit /b 1
)

REM Check if virtual environment exists
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo ERROR: Failed to create virtual environment
        pause
        exit /b 1
    )
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install/upgrade dependencies
echo Installing dependencies...
pip install --upgrade pip >nul 2>&1
pip install -q -r requirements-web.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    echo Run: pip install -r requirements-web.txt
    pause
    exit /b 1
)

REM Check if .env exists, if not copy from .env.example
if not exist ".env" (
    echo Creating .env file from template...
    copy .env.example .env
    echo.
    echo WARNING: Please edit .env with your API keys!
    echo - OPENAI_API_KEY: Get from https://platform.openai.com/account/api-keys
    echo.
)

REM Display startup info
echo.
echo ===============================================
echo   Starting J.A.R.V.I.S Web...
echo ===============================================
echo.
echo   Web UI:    http://localhost:5000
echo   API Base:  http://localhost:5000/api
echo   Health:    http://localhost:5000/health
echo.
echo   Press Ctrl+C to stop the server
echo.

REM Run the Flask app
python app.py

pause
