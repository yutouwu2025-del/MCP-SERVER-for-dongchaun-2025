@echo off
export LANG=zh_CN.GB18030
chcp 65001 >nul
cls

echo ========================================
echo     Rainfall MCP Server - auto start
echo ========================================
echo ****************************************
echo          Author:wuy@imde.ac.cn
echo          Created:2025/09/15
echo          Purpose:auto start
echo ****************************************
echo.
echo Starting both Web Server and MCP Server...
echo.

echo [1/4] Checking Python environment...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python not found in PATH
    echo Please install Python and add it to PATH
    pause
    exit /b 1
)
echo Python environment OK

echo.
echo [2/4] Starting MCP Server...
start "MCP Server" /MIN python start_server.py

echo.
echo [3/4] Waiting for MCP Server initialization...
timeout /t 2 /nobreak >nul

echo.
echo [4/4] Starting Web Server...
start "Web Server" /MIN python web_server.py

echo.
echo Waiting for services to fully start...
timeout /t 3 /nobreak >nul

echo.
echo ========================================
echo Services Started Successfully!
echo ========================================
echo.
echo Web Interface: http://localhost:8081
echo MCP Server: Running in background
echo.
echo Services running in separate windows:
echo - MCP Server (minimized)
echo - Web Server (minimized)
echo.
echo Opening web browser...
start http://localhost:8081

echo.
echo ========================================
echo Service Management
echo ========================================
echo.
echo To stop all services, you can:
echo 1. Close this window and the service windows
echo 2. Run: taskkill /F /IM python.exe
echo 3. Use Ctrl+C in each service window
echo.
echo Press any key to stop all services...
pause >nul

echo.
echo Stopping all services...
taskkill /F /IM python.exe >nul 2>&1

echo.
echo All services stopped.
echo Thank you for using DongChuan Rainfall MCP Server!