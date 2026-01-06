@echo off
echo 🚀 Iniciando PlayT con Python 314...
echo.

REM Ruta exacta de tu Python 314
set "PYTHON_EXE=C:\Users\Facundo\AppData\Local\Programs\Python\Python314\python.exe"

REM Verificar que Python existe
echo 🔍 Verificando Python en: %PYTHON_EXE%
if not exist "%PYTHON_EXE%" (
    echo ❌ ERROR: Python no encontrado en la ruta especificada
    echo 💡 Verifica que la ruta sea correcta
    pause
    exit /b 1
)

echo ✅ Python 314 encontrado correctamente
echo.

REM Verificar directorios
if not exist "backend" (
    echo ❌ Error: Carpeta 'backend' no encontrada
    pause
    exit /b 1
)

if not exist "frontend" (
    echo ❌ Error: Carpeta 'frontend' no encontrada  
    pause
    exit /b 1
)

echo ✅ Directorios del proyecto encontrados
echo.

REM Crear .env.local para desarrollo
if not exist "frontend\.env.local" (
    echo 📝 Creando configuración de desarrollo...
    echo VITE_API_URL=http://localhost:8000 > "frontend\.env.local"
    echo VITE_WS_URL=ws://localhost:8000 >> "frontend\.env.local"
    echo ✅ Archivo .env.local creado
) else (
    echo ✅ Configuración de desarrollo ya existe
)

echo.
echo 🐍 Configurando Backend Python...
cd backend

REM Crear entorno virtual con la ruta específica
if not exist "venv" (
    echo 📦 Creando entorno virtual con Python 314...
    "%PYTHON_EXE%" -m venv venv
    if errorlevel 1 (
        echo ❌ Error al crear entorno virtual
        pause
        exit /b 1
    )
    echo ✅ Entorno virtual creado exitosamente
) else (
    echo ✅ Entorno virtual existe, verificando compatibilidad...
    REM Verificar si el entorno virtual es compatible con Python 314
    call "venv\Scripts\activate.bat" 2>nul
    if errorlevel 1 (
        echo ⚠️ Entorno virtual incompatible, recreando con Python 314...
        rmdir /s /q venv
        "%PYTHON_EXE%" -m venv venv
        if errorlevel 1 (
            echo ❌ Error al recrear entorno virtual
            pause
            exit /b 1
        )
        echo ✅ Entorno virtual recreado con Python 314
    )
)

REM Activar entorno virtual e instalar dependencias
echo 📦 Activando entorno virtual e instalando dependencias...
call "venv\Scripts\activate.bat"
if errorlevel 1 (
    echo ❌ Error al activar entorno virtual
    pause
    exit /b 1
)

pip install -r requirements.txt
if errorlevel 1 (
    echo ❌ Error al instalar dependencias de Python
    pause
    exit /b 1
)

echo ✅ Dependencias de Python instaladas
cd ..

echo.
echo ⚛️ Configurando Frontend Node.js...
cd frontend

if not exist "node_modules" (
    echo 📦 Instalando dependencias de Node.js...
    npm install
    if errorlevel 1 (
        echo ❌ Error al instalar dependencias de Node.js
        pause
        exit /b 1
    )
    echo ✅ Dependencias de Node.js instaladas
) else (
    echo ✅ Dependencias de Node.js ya instaladas
)

cd ..

echo.
echo 🚀 Iniciando servidores de desarrollo...
echo.
echo 📍 URLs disponibles:
echo   🌐 Frontend: http://localhost:5173
echo   🔧 Backend:  http://localhost:8000  
echo   📚 API Docs: http://localhost:8000/docs
echo.

REM Obtener directorio actual completo
set "PROJECT_DIR=%CD%"

REM Iniciar backend
echo 🐍 Iniciando servidor backend...
start "PlayT Backend" cmd /k "cd /d "%PROJECT_DIR%\backend" && call venv\Scripts\activate.bat && python main.py"

REM Esperar 3 segundos
timeout /t 3 /nobreak > nul

REM Iniciar frontend  
echo ⚛️ Iniciando servidor frontend...
start "PlayT Frontend" cmd /k "cd /d "%PROJECT_DIR%\frontend" && npm run dev"

echo.
echo ✅ Ambos servidores iniciados en ventanas separadas
echo 💡 Presiona cualquier tecla para cerrar esta ventana
pause > nul