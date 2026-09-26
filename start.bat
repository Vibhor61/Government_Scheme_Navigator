@echo off
echo ====================================================================
echo  Citizen Rights and Government Scheme Navigator
echo  MAIT CST Department - Minor Project Batch (2023-2027)
echo ====================================================================
echo.

where docker >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    echo [1] Docker is detected!
    echo Starting full multi-container stack (minor_postgres, minor_backend, minor_frontend)...
    echo.
    docker compose up --build
    goto end
)

echo Docker not running or not found. Starting local Python backend server...
python run_backend.py

:end
pause
