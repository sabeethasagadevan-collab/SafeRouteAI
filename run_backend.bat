@echo off
cd /d "%~dp0backend"
if exist "%~dp0.venv\Scripts\python.exe" (
  "%~dp0.venv\Scripts\python.exe" -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
) else (
  echo Create .venv and install backend requirements first. See README.md.
  pause
)
