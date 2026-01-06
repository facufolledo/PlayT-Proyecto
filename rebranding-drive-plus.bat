@echo off
echo 🚗⚡ REBRANDING A DRIVE+ ⚡🚗
echo.
echo ⚠️  IMPORTANTE: Este script cambiará TODOS los archivos
echo    Asegúrate de tener un backup o commit en git
echo.
pause

echo 🔍 Iniciando rebranding completo...
echo.

REM Crear directorio de backup
if not exist "backup-playt" (
    mkdir backup-playt
    echo 📦 Directorio de backup creado
)

echo 📝 Cambiando archivos principales...

REM ============================================
REM FRONTEND - Package.json
REM ============================================
echo 🔧 Actualizando package.json del frontend...
cd frontend
if exist package.json (
    powershell -Command "(Get-Content package.json) -replace '\"name\": \".*\"', '\"name\": \"drive-plus\"' | Set-Content package.json"
    powershell -Command "(Get-Content package.json) -replace '\"PlayT\"', '\"Drive+\"' | Set-Content package.json"
    powershell -Command "(Get-Content package.json) -replace '\"PlayR\"', '\"Drive+\"' | Set-Content package.json"
    powershell -Command "(Get-Content package.json) -replace '\"playt\"', '\"drive-plus\"' | Set-Content package.json"
    powershell -Command "(Get-Content package.json) -replace '\"playr\"', '\"drive-plus\"' | Set-Content package.json"
    echo ✅ package.json actualizado
)
cd ..

REM ============================================
REM FRONTEND - Index.html
REM ============================================
echo 🔧 Actualizando index.html...
cd frontend
if exist index.html (
    powershell -Command "(Get-Content index.html) -replace 'PlayT', 'Drive+' | Set-Content index.html"
    powershell -Command "(Get-Content index.html) -replace 'PlayR', 'Drive+' | Set-Content index.html"
    powershell -Command "(Get-Content index.html) -replace 'playt', 'drive-plus' | Set-Content index.html"
    powershell -Command "(Get-Content index.html) -replace 'playr', 'drive-plus' | Set-Content index.html"
    echo ✅ index.html actualizado
)
cd ..

REM ============================================
REM FRONTEND - Vite config
REM ============================================
echo 🔧 Actualizando vite.config.ts...
cd frontend
if exist vite.config.ts (
    powershell -Command "(Get-Content vite.config.ts) -replace '/PlayR/', '/DriveP/' | Set-Content vite.config.ts"
    powershell -Command "(Get-Content vite.config.ts) -replace '/PlayT/', '/DriveP/' | Set-Content vite.config.ts"
    echo ✅ vite.config.ts actualizado
)
cd ..

REM ============================================
REM FRONTEND - App.tsx
REM ============================================
echo 🔧 Actualizando App.tsx...
cd frontend\src
if exist App.tsx (
    powershell -Command "(Get-Content App.tsx) -replace 'PlayR', 'Drive+' | Set-Content App.tsx"
    powershell -Command "(Get-Content App.tsx) -replace 'PlayT', 'Drive+' | Set-Content App.tsx"
    powershell -Command "(Get-Content App.tsx) -replace '/PlayR', '/DriveP' | Set-Content App.tsx"
    powershell -Command "(Get-Content App.tsx) -replace '/PlayT', '/DriveP' | Set-Content App.tsx"
    echo ✅ App.tsx actualizado
)
cd ..\..

REM ============================================
REM BACKEND - Main.py
REM ============================================
echo 🔧 Actualizando main.py del backend...
cd backend
if exist main.py (
    powershell -Command "(Get-Content main.py) -replace 'PlayT', 'Drive+' | Set-Content main.py"
    powershell -Command "(Get-Content main.py) -replace 'PlayR', 'Drive+' | Set-Content main.py"
    powershell -Command "(Get-Content main.py) -replace 'playt', 'drive-plus' | Set-Content main.py"
    powershell -Command "(Get-Content main.py) -replace 'playr', 'drive-plus' | Set-Content main.py"
    powershell -Command "(Get-Content main.py) -replace 'Sistema de pádel', 'Sistema de pádel Drive+' | Set-Content main.py"
    echo ✅ main.py actualizado
)
cd ..

REM ============================================
REM SCRIPTS DE DESARROLLO
REM ============================================
echo 🔧 Actualizando scripts de desarrollo...
for %%f in (start-dev*.bat fix-venv.bat) do (
    if exist %%f (
        powershell -Command "(Get-Content %%f) -replace 'PlayT', 'Drive+' | Set-Content %%f"
        powershell -Command "(Get-Content %%f) -replace 'PlayR', 'Drive+' | Set-Content %%f"
        echo ✅ %%f actualizado
    )
)

REM ============================================
REM DOCUMENTACIÓN
REM ============================================
echo 🔧 Actualizando documentación...
if exist README.md (
    powershell -Command "(Get-Content README.md) -replace 'PlayT', 'Drive+' | Set-Content README.md"
    powershell -Command "(Get-Content README.md) -replace 'PlayR', 'Drive+' | Set-Content README.md"
    powershell -Command "(Get-Content README.md) -replace 'playt', 'drive-plus' | Set-Content README.md"
    powershell -Command "(Get-Content README.md) -replace 'playr', 'drive-plus' | Set-Content README.md"
    echo ✅ README.md actualizado
)

REM Actualizar archivos .md en la raíz
for %%f in (*.md) do (
    if exist %%f (
        powershell -Command "(Get-Content %%f) -replace 'PlayT', 'Drive+' | Set-Content %%f"
        powershell -Command "(Get-Content %%f) -replace 'PlayR', 'Drive+' | Set-Content %%f"
        powershell -Command "(Get-Content %%f) -replace 'playt', 'drive-plus' | Set-Content %%f"
        powershell -Command "(Get-Content %%f) -replace 'playr', 'drive-plus' | Set-Content %%f"
    )
)

REM ============================================
REM ARCHIVOS DE CONFIGURACIÓN
REM ============================================
echo 🔧 Actualizando archivos de configuración...

REM .htaccess
cd frontend
if exist .htaccess (
    powershell -Command "(Get-Content .htaccess) -replace 'PlayR', 'DriveP' | Set-Content .htaccess"
    powershell -Command "(Get-Content .htaccess) -replace 'PlayT', 'DriveP' | Set-Content .htaccess"
    echo ✅ .htaccess actualizado
)
cd ..

REM Steering files
if exist .kiro\steering\produccion.md (
    powershell -Command "(Get-Content .kiro\steering\produccion.md) -replace 'PlayT', 'Drive+' | Set-Content .kiro\steering\produccion.md"
    powershell -Command "(Get-Content .kiro\steering\produccion.md) -replace 'PlayR', 'Drive+' | Set-Content .kiro\steering\produccion.md"
    powershell -Command "(Get-Content .kiro\steering\produccion.md) -replace 'playt-backend', 'driveplus-backend' | Set-Content .kiro\steering\produccion.md"
    powershell -Command "(Get-Content .kiro\steering\produccion.md) -replace 'playr-backend', 'driveplus-backend' | Set-Content .kiro\steering\produccion.md"
    echo ✅ produccion.md actualizado
)

echo.
echo 🎨 REBRANDING COMPLETADO
echo.
echo 📋 RESUMEN DE CAMBIOS:
echo   ✅ PlayT → Drive+
echo   ✅ PlayR → Drive+
echo   ✅ playt → drive-plus  
echo   ✅ playr → drive-plus
echo   ✅ URLs /PlayR/ → /DriveP/
echo   ✅ URLs /PlayT/ → /DriveP/
echo   ✅ Frontend package.json
echo   ✅ Backend main.py
echo   ✅ Scripts de desarrollo
echo   ✅ Documentación
echo   ✅ Archivos de configuración
echo.
echo 🚨 PRÓXIMOS PASOS MANUALES:
echo   1. 🌐 Cambiar URL en Hostinger: /PlayR/ → /DriveP/
echo   2. 🔧 Redeploy backend en Render con nuevo nombre
echo   3. 🔥 Actualizar Firebase project name
echo   4. 📱 Cambiar logos y favicons
echo   5. 🎨 Actualizar colores/branding si es necesario
echo.
echo 💡 Revisa los archivos y haz commit cuando estés conforme
pause