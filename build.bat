@echo off
setlocal
cd /d "%~dp0"
set "VENV_PYTHON=.venv\Scripts\python.exe"
if not exist "%VENV_PYTHON%" (
    echo [ERROR] Create .venv and install requirements.txt first.
    exit /b 1
)
"%VENV_PYTHON%" -c "import PyInstaller, PySide6.QtWidgets"
if errorlevel 1 exit /b 1
"%VENV_PYTHON%" -m PyInstaller --noconfirm --clean packaging\windows\goodbyedpi-turkey.spec
if errorlevel 1 exit /b 1
echo Build complete: dist\GoodbyeDPI-Turkey.exe
