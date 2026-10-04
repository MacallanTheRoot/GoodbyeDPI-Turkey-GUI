@echo off
setlocal
cd /d "%~dp0"
if not exist ".venv\Scripts\pythonw.exe" (
    echo [ERROR] Create .venv and install requirements.txt first.
    exit /b 1
)
start "" ".venv\Scripts\pythonw.exe" "src\main.py"
