@echo off
echo ================================================
echo   Starting AnalytixAI Backend Server
echo ================================================
echo.

cd backend

if not exist venv (
    echo ERROR: Virtual environment not found!
    echo Please run setup.bat first.
    pause
    exit /b 1
)

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo.
echo Starting FastAPI server...
echo Server will be available at: http://127.0.0.1:8000
echo API Docs available at: http://127.0.0.1:8000/docs
echo.
echo Press Ctrl+C to stop the server
echo.

uvicorn main:app --reload --host 127.0.0.1 --port 8000
