@echo off
echo 🔧 Arreglando entorno virtual con Python 314...
echo.

REM Ruta de Python 314
set "PYTHON_EXE=C:\Users\Facundo\AppData\Local\Programs\Python\Python314\python.exe"

REM Verificar Python
if not exist "%PYTHON_EXE%" (
    echo ❌ Python 314 no encontrado
    pause
    exit /b 1
)

echo ✅ Python 314 encontrado

REM Ir al backend
cd backend

REM Eliminar entorno virtual viejo (creado con Python 313)
if exist "venv" (
    echo 🗑️ Eliminando entorno virtual viejo (Python 313)...
    rmdir /s /q venv
    echo ✅ Entorno virtual viejo eliminado
)

REM Crear nuevo entorno virtual con Python 314
echo 📦 Creando nuevo entorno virtual con Python 314...
"%PYTHON_EXE%" -m venv venv
if errorlevel 1 (
    echo ❌ Error creando entorno virtual
    pause
    exit /b 1
)

echo ✅ Nuevo entorno virtual creado con Python 314

REM Activar e instalar dependencias
echo 📦 Instalando dependencias...
call venv\Scripts\activate.bat
pip install -r requirements.txt
if errorlevel 1 (
    echo ❌ Error instalando dependencias
    pause
    exit /b 1
)

echo ✅ Dependencias instaladas correctamente

cd ..

echo.
echo ✅ Entorno virtual arreglado con Python 314
echo 💡 Ahora puedes usar start-dev-quick.bat
pause