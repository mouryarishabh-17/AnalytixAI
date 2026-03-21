@echo off
echo ========================================
echo    Starting Frontend Server
echo ========================================
echo.
echo Frontend will be available at:
echo   http://localhost:5500
echo.
echo Press Ctrl+C to stop the server
echo ========================================
echo.

cd frontend
python -m http.server 5500
