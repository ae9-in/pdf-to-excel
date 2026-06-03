@echo off
title PDF to Excel - Frontend (Port 3000)
color 0B

echo ================================================
echo   PDF to Excel Frontend
echo   http://localhost:3000
echo ================================================
echo.

cd /d "d:\pdf to excal"

echo Starting frontend...
echo.
npm run dev

echo.
echo [Frontend stopped. Press any key to exit.]
pause >nul
