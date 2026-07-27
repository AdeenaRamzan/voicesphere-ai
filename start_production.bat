@echo off
echo Starting VoiceSphere AI Production Server on http://0.0.0.0:8000 ...
python -m uvicorn server:app --host 0.0.0.0 --port 8000
pause
