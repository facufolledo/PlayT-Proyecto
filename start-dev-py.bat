@echo off
echo 🚀 Iniciando entorno de desarrollo PlayT (Python 314)...
echo.

REM Definir ruta específica de Python 314
set "PYTHON_EXE=C:\Users\Facundo\AppData\Local\Programs\Python\Python314\python.exe"

REM Verificar que Python existe
if not exist "%PYTHON_EXE%" (
    echo ❌ Error: Python 314 no encontrado en %PYTHON_EXE%
    pause
    exit /b 1
)

echo ✅ Python 314 encontrado

REM Verificar directorios
if not exist "backend" (
    echo ❌ Error: No se encuentra la carpeta 'backend'
    pause
    exit /b 1
)

if not exist "frontend" (
    echo ❌ Error: No se encuentra la carpeta 'frontend'
    pause
    exit /b 1
)

echo ✅ Directorios encontrados
echo.

REM Crear .env.local
if not exist "frontend\.env.local" (
    echo 📝 Creando archivo .env.local...
    echo VITE_API_URL=http://localhost:8000 > frontend\.env.local
    echo VITE_WS_URL=ws://localhost:8000 >> frontend\.env.local
    echo ✅ Archivo .env.local creado
)

echo 🐍 Configurando backend...
cd backend

REM Crear entorno virtual usando Python 314
if not exist "venv" (
    echo 📦 Creando entorno virtual con Python 314...
    "%PYTHON_EXE%" -m venv venv
    if errorlevel 1 (
        echo ❌ Error creando entorno virtual
        pause
        exit /b 1
    )
    echo ✅ Entorno virtual creado
)

REM Activar e instalar dependencias
echo 📦 Instalando dependencias...
call venv\Scripts\activate.bat
pip install -r requirements.txt
if errorlevel 1 (
    echo ❌ Error instalando dependencias
    pause
    exit /b 1
)

cd ..

echo ⚛️ Configurando frontend...
cd frontend
if not exist "node_modules" (
    echo 📦 Instalando dependencias del frontend...
    npm install
    if errorlevel 1 (
        echo ❌ Error instalando dependencias del frontend
        pause
        exit /b 1
    )
)
cd ..

echo.
echo 🚀 Iniciando servidores...
echo   Frontend: http://localhost:5173
echo   Backend:  http://localhost:8000
echo.

REM Obtener directorio actual
set "PROJECT_DIR=%CD%"

REM Iniciar servidores
start "PlayT Backend" cmd /k "cd /d "%PROJECT_DIR%\backend" && venv\Scripts\activate.bat && python main.py"
timeout /t 2 /nobreak > nul
start "PlayT Frontend" cmd /k "cd /d "%PROJECT_DIR%\frontend" && npm run dev"

echo ✅ Servidores iniciados
pause > nul