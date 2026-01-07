@echo off
set "VENV_PYTHON=.\venv\Scripts\python.exe"

if not exist "%VENV_PYTHON%" (
    echo [ERROR] Virtual Environment not found! 
    echo Please ensure you have created the 'venv' folder.
    pause
    exit /b 1
)

echo Using Virtual Environment Python: %VENV_PYTHON%

echo Installing Dependencies into venv...
"%VENV_PYTHON%" -m pip install --upgrade pip
"%VENV_PYTHON%" -m pip install -r requirements.txt
"%VENV_PYTHON%" -m pip install pyinstaller

echo Cleaning up previous builds...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist *.spec del *.spec

echo Building Executable...
"%VENV_PYTHON%" -m PyInstaller --noconsole --onefile ^
    --name "GoodbyeDPI-Turkey" ^
    --collect-all customtkinter ^
    --hidden-import PIL ^
    --hidden-import pystray ^
    --add-data "bin;bin" ^
    src/main.py

echo Build Complete!
echo Check the 'dist' folder for your executable.
pause
