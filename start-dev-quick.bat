@echo off
echo 🚀 Inicio rápido PlayT (Python 314)...
echo.

REM Crear .env.local si no existe
if not exist "frontend\.env.local" (
    echo VITE_API_URL=http://localhost:8000 > frontend\.env.local
    echo VITE_WS_URL=ws://localhost:8000 >> frontend\.env.local
)

echo 📍 URLs de desarrollo:
echo   Frontend: http://localhost:5173
echo   Backend:  http://localhost:8000
echo   API Docs: http://localhost:8000/docs
echo.

REM Obtener directorio actual
set "PROJECT_DIR=%CD%"

REM Iniciar backend con entorno virtual
start "PlayT Backend" cmd /k "cd /d "%PROJECT_DIR%\backend" && venv\Scripts\activate.bat && python main.py"

REM Esperar un poco
timeout /t 2 /nobreak > nul

REM Iniciar frontend
start "PlayT Frontend" cmd /k "cd /d "%PROJECT_DIR%\frontend" && npm run dev"

echo ✅ Servidores iniciados
pause > nul