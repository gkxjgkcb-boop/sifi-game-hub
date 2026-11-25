@echo off
setlocal
cd /d "%~dp0"
set PY=py -3.11
%PY% --version >nul 2>&1 || set PY=py -3
%PY% --version >nul 2>&1 || (echo Python 3.10+ for Windows 64-bit not found. Install from python.org & exit /b 1)
%PY% -m pip install --upgrade pip || exit /b 1
%PY% -m pip install -r requirements-dev.txt || exit /b 1
%PY% -m pytest -q || exit /b 1
%PY% -m PyInstaller --noconfirm --clean --windowed --name "SIFO GAME HUB" --collect-all customtkinter --hidden-import psutil run_app.py || exit /b 1
if not exist "dist\SIFO GAME HUB\SIFO GAME HUB.exe" (echo Build failed: EXE not found & exit /b 1)
echo Build complete: dist\SIFO GAME HUB\SIFO GAME HUB.exe
endlocal
