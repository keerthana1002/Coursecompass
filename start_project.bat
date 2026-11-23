@echo off
title CourseCompass Launcher
start "CourseCompass Backend" cmd /k "cd /d %~dp0backend && .\venv\Scripts\uvicorn.exe app.main:app --reload"
start "CourseCompass Frontend" cmd /k "cd /d %~dp0frontend && npm start"
timeout /t 5 /nobreak >nul
start http://localhost:3000
start http://127.0.0.1:8000/docs
