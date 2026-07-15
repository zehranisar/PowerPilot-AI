@echo off
echo Starting Backend and Frontend...
echo.
echo Starting Backend in new window...
start "Backend Server" cmd /k "cd /d D:\Electricity_forcasting && call venv\Scripts\activate && python run_server.py"
timeout /t 3 /nobreak >nul
echo.
echo Starting Frontend in new window...
start "Frontend Server" cmd /k "cd /d D:\Electricity_forcasting\frontend && npm run dev"
echo.
echo Both servers are starting in separate windows.
echo Backend: http://localhost:8000
echo Frontend: http://localhost:3000
pause

