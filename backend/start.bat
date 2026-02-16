@echo off
echo ========================================
echo RAG Knowledge Base - Backend Server
echo ========================================
echo.

cd /d "%~dp0"
echo [1/3] Activating virtual environment...
call venv\Scripts\activate.bat

echo [2/3] Starting FastAPI server...
echo.
echo Server will be available at:
echo   - API: http://localhost:8000
echo   - Docs: http://localhost:8000/docs
echo.
echo Press Ctrl+C to stop the server.
echo.

uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

pause
