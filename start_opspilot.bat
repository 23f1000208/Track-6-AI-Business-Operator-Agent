@echo off
title OpsPilot AI - Autonomous Operations Agent
echo ============================================================
echo           OpsPilot AI - Launching System
echo    Google ADK + Python Core + Swytchcode (Track 6)
echo ============================================================
echo.
echo Starting FastAPI Backend and Serving Web UI...
echo Open your browser to: http://localhost:8000
echo.

start "" http://localhost:8000
python -m uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8000

pause
