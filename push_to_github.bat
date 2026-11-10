@echo off
setlocal
cd /d "%~dp0"
chcp 65001 >nul 2>&1
title Push Code lên GitHub (bot_discord)

echo =====================================================================
echo       🚀 ĐẨY CODE LÊN GITHUB: truong2903/bot_discord
echo =====================================================================
echo.
echo [1/3] Kiểm tra Git Remote...
git remote -v
echo.
echo [2/3] Đang đẩy code lên nhánh main...
echo (Nếu có cửa sổ GitHub hiện lên, bạn chỉ cần bấm xác thực đăng nhập)
echo.
git push -u origin main

if %errorlevel% equ 0 (
    echo.
    echo =====================================================================
    echo   🎉 THÀNH CÔNG! Code đã được đẩy lên https://github.com/truong2903/bot_discord
    echo =====================================================================
) else (
    echo.
    echo =====================================================================
    echo   ❌ LƯU Ý QUAN TRỌNG:
    echo   Nếu báo "Repository not found", hãy chắc chắn bạn đã vào
    echo   https://github.com/new và bấm "Create repository" với tên: bot_discord
    echo =====================================================================
)

echo.
pause
