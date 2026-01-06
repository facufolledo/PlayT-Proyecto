@echo off
echo 🚗⚡ Iniciando entorno de desarrollo Drive+...
echo.

REM Definir ruta de Python 314
set "PYTHON_PATH=C:\Users\Facundo\AppData\Local\Programs\Python\Python314\python.exe"
set "PIP_PATH=C:\Users\Facundo\AppData\Local\Programs\Python\Python314\Scripts\pip.exe"

REM Verificar que Python existe
if not exist "%PYTHON_PATH%" (
    echo ❌ Error: Python no encontrado en %PYTHON_PATH%
    echo 💡 Verifica la ruta de Python
    pause
    exit /b 1
)

echo ✅ Python encontrado: %PYTHON_PATH%

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
) else (
    echo ✅ Archivo .env.local ya existe
)

echo.
echo 🐍 Configurando backend...
cd backend

REM Crear entorno virtual usando ruta específica de Python 314
if not exist "venv" (
    echo 📦 Creando entorno virtual con Python 314...
    "%PYTHON_PATH%" -m venv venv
    if errorlevel 1 (
        echo ❌ Error creando entorno virtual
        pause
        exit /b 1
    )
    echo ✅ Entorno virtual creado
) else (
    echo ✅ Entorno virtual ya existe
)

REM Activar entorno virtual e instalar dependencias
echo 📦 Instalando dependencias del backend...
call venv\Scripts\activate.bat
pip install -r requirements.txt
if errorlevel 1 (
    echo ❌ Error instalando dependencias del backend
    pause
    exit /b 1
)
echo ✅ Dependencias del backend instaladas

cd ..

echo ⚛️ Configurando frontend...
cd frontend

REM Instalar dependencias de Node.js
if not exist "node_modules" (
    echo 📦 Instalando dependencias del frontend...
    npm install
    if errorlevel 1 (
        echo ❌ Error instalando dependencias del frontend
        pause
        exit /b 1
    )
    echo ✅ Dependencias del frontend instaladas
) else (
    echo ✅ Dependencias del frontend ya instaladas
)

cd ..

echo.
echo 🚀 Iniciando servidores...
echo.
echo 📍 URLs de desarrollo:
echo   Frontend: http://localhost:5173
echo   Backend:  http://localhost:8000
echo   API Docs: http://localhost:8000/docs
echo.

REM Obtener directorio actual
set "PROJECT_DIR=%CD%"

REM Iniciar backend con entorno virtual
echo 🐍 Iniciando backend con entorno virtual...
start "Drive+ Backend" cmd /k "cd /d "%PROJECT_DIR%\backend" && venv\Scripts\activate.bat && python main.py"

REM Esperar un poco para que el backend inicie
timeout /t 3 /nobreak > nul

REM Iniciar frontend
echo ⚛️ Iniciando frontend...
start "Drive+ Frontend" cmd /k "cd /d "%PROJECT_DIR%\frontend" && npm run dev"

echo.
echo ✅ Servidores iniciados en ventanas separadas
echo 💡 Presiona cualquier tecla para cerrar esta ventana
pause > nul