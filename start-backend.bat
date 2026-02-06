@echo off
cd /d C:\archive\backend
python -m uvicorn main:app --reload --port 8000
pause
