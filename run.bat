@echo off
setlocal
cd /d "%~dp0"
chcp 65001 >nul 2>&1
set PYTHONUTF8=1
set PYTHONIOENCODING=utf-8
title Discord HypeSquad Selector Bot Pro

echo =====================================================================
echo       🌟 DISCORD HYPESQUAD SELECTOR BOT PRO (EMBED + BUTTONS)
echo =====================================================================
echo.

python --version >nul 2>&1
if %errorlevel% neq 0 (
    py --version >nul 2>&1
    if %errorlevel% equ 0 (
        echo [INFO] Đang kiểm tra thư viện...
        py -m pip install -r requirements.txt >nul 2>&1
        echo [INFO] Khởi chạy Bot...
        py main.py
        if %errorlevel% neq 0 pause
        exit /b
    )
    echo [ERROR] Python chua duoc cai dat hoac chua them vao PATH.
    echo Vui long cai dat Python tu https://www.python.org/downloads/
    pause
    exit /b
)

echo [INFO] Đang kiểm tra và cài đặt thư viện cần thiết...
python -m pip install -r requirements.txt >nul 2>&1
echo [INFO] Khởi chạy Bot...
python main.py
if %errorlevel% neq 0 (
    pause
)
