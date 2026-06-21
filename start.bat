@echo off
title Cadmus Station v0.001
cd /d "%~dp0"
echo.
echo   CADMUS STATION v0.001
echo   =====================
echo.
echo   Starting server...
echo   Open http://localhost:5000 in your browser
echo   Press Ctrl+C to stop
echo.
python server.py
pause
