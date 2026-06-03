@echo off
title PDF to Excel - Backend Server (Port 8000)
color 0A

echo ================================================
echo   PDF to Excel Backend Server
echo   http://127.0.0.1:8000
echo ================================================
echo.

:: Kill anything on port 8000 first
echo Clearing port 8000...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8000 " ^| findstr "LISTENING"') do (
    taskkill /PID %%a /F >nul 2>&1
)
timeout /t 1 /nobreak >nul

:: Go to pdf_service folder
cd /d "d:\pdf to excal\pdf_service"

echo Starting backend...
echo.
.\venv\Scripts\python.exe main.py

echo.
echo [Server stopped. Press any key to exit.]
pause >nul
