@echo off
echo ================================================
echo   AnalytixAI Backend Setup Script
echo ================================================
echo.

cd backend

echo [1/4] Creating virtual environment...
python -m venv venv
if errorlevel 1 (
    echo ERROR: Failed to create virtual environment
    pause
    exit /b 1
)

echo.
echo [2/4] Activating virtual environment...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo ERROR: Failed to activate virtual environment
    pause
    exit /b 1
)

echo.
echo [3/4] Installing dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

echo.
echo [4/4] Checking environment file...
if not exist .env (
    echo WARNING: .env file not found!
    echo Please copy .env.template to .env and configure it.
    echo.
    pause
) else (
    echo .env file found!
)

echo.
echo ================================================
echo   Setup Complete!
echo ================================================
echo.
echo To start the backend server, run:
echo   cd backend
echo   venv\Scripts\activate
echo   uvicorn main:app --reload
echo.
pause
