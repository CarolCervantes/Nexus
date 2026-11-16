@echo off
echo ===================================================
echo Deteniendo servicios locales de NEXUS...
echo ===================================================

REM Detener uvicorn (FastAPI en puerto 8000)
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8000 ^| findstr LISTENING') do (
    echo Cerrando proceso FastAPI (PID: %%a)...
    taskkill /F /PID %%a >nul 2>&1
)

echo.
echo NEXUS ha sido detenido correctamente.
timeout /t 3
