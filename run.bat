@echo off
setlocal
cd /d "%~dp0"
title Discord Multi-Function Bot

echo =====================================================================
echo       DISCORD BOT PRO (EMBED + BUTTONS)
echo =====================================================================
echo.

python --version >nul 2>&1
if %errorlevel% neq 0 (
    py --version >nul 2>&1
    if %errorlevel% equ 0 (
        echo [INFO] Kiem tra thu vien...
        py -m pip install -r requirements.txt >nul 2>&1
        echo [INFO] Khoi chay Bot...
        py main.py
        if %errorlevel% neq 0 pause
        exit /b
    )
    echo [ERROR] Python chua duoc cai dat hoac chua them vao PATH.
    echo Vui long cai dat Python tu https://www.python.org/downloads/
    pause
    exit /b
)

echo [INFO] Kiem tra va cai dat thu vien can thiet...
python -m pip install -r requirements.txt >nul 2>&1
echo [INFO] Khoi chay Bot...
python main.py
if %errorlevel% neq 0 (
    pause
)
