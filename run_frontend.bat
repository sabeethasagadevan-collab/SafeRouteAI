@echo off
cd /d "%~dp0"
if exist ".venv\Scripts\python.exe" (
  ".venv\Scripts\python.exe" -m http.server 5500 --directory frontend
) else (
  python -m http.server 5500 --directory frontend
)
