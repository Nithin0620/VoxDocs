@echo off
REM VoxDocs Backend - Setup Script (Windows)
REM This script sets up the development environment

echo.
echo 🚀 VoxDocs Backend Setup
echo ========================
echo.

REM Check Python version
echo ✓ Checking Python version...
python --version

REM Create virtual environment
if not exist "venv" (
    echo ✓ Creating virtual environment...
    python -m venv venv
) else (
    echo ✓ Virtual environment already exists
)

REM Activate virtual environment
echo ✓ Activating virtual environment...
call venv\Scripts\activate.bat

REM Upgrade pip
echo ✓ Upgrading pip...
python -m pip install --upgrade pip

REM Install dependencies
echo ✓ Installing dependencies...
pip install -r requirements.txt

REM Setup environment file
if not exist ".env" (
    echo ✓ Creating .env file from example...
    copy .env.example .env
    echo.
    echo ⚠️  IMPORTANT: Edit .env file with your API keys:
    echo    - OPENAI_API_KEY=your_key_here
    echo    - ELEVENLABS_API_KEY=your_key_here
) else (
    echo ✓ .env file already exists
)

REM Create necessary directories
echo ✓ Creating directories...
if not exist uploads mkdir uploads
if not exist vectors mkdir vectors
if not exist logs mkdir logs

echo.
echo ✅ Setup complete!
echo.
echo Next steps:
echo 1. Edit .env file with your API keys
echo 2. Run: venv\Scripts\activate.bat
echo 3. Run: python -m uvicorn app.main:app --reload
echo.
echo API Documentation: http://localhost:8000/docs
