@echo off
echo 🚗⚡ REBRANDING COMPLETO: PlayT/PlayR → Drive+
echo.
echo ⚠️  Este script cambiará TODAS las referencias en TODO el proyecto
echo    Incluyendo: PlayT, PlayR, playt, playr, logo-playr, etc.
echo.
pause

echo 🔍 Iniciando rebranding masivo...
echo.

REM ============================================
REM FRONTEND - Archivos principales
REM ============================================
echo 🎨 Actualizando frontend...

REM package.json
if exist "frontend\package.json" (
    powershell -Command "(Get-Content 'frontend\package.json') -replace 'playr-padel-rankings', 'drive-plus-padel' | Set-Content 'frontend\package.json'"
    echo ✅ Frontend package.json
)

REM index.html
if exist "frontend\index.html" (
    powershell -Command "(Get-Content 'frontend\index.html') -replace 'PlayR', 'Drive+' | Set-Content 'frontend\index.html'"
    powershell -Command "(Get-Content 'frontend\index.html') -replace 'PlayT', 'Drive+' | Set-Content 'frontend\index.html'"
    powershell -Command "(Get-Content 'frontend\index.html') -replace 'logo-playr', 'logo-drive-plus' | Set-Content 'frontend\index.html'"
    echo ✅ Frontend index.html
)

REM vite.config.ts
if exist "frontend\vite.config.ts" (
    powershell -Command "(Get-Content 'frontend\vite.config.ts') -replace '/PlayR/', '/DriveP/' | Set-Content 'frontend\vite.config.ts'"
    powershell -Command "(Get-Content 'frontend\vite.config.ts') -replace '/PlayT/', '/DriveP/' | Set-Content 'frontend\vite.config.ts'"
    echo ✅ Frontend vite.config.ts
)

REM App.tsx
if exist "frontend\src\App.tsx" (
    powershell -Command "(Get-Content 'frontend\src\App.tsx') -replace '/PlayR', '/DriveP' | Set-Content 'frontend\src\App.tsx'"
    powershell -Command "(Get-Content 'frontend\src\App.tsx') -replace '/PlayT', '/DriveP' | Set-Content 'frontend\src\App.tsx'"
    echo ✅ Frontend App.tsx
)

REM ============================================
REM FRONTEND - Todos los archivos TypeScript/React
REM ============================================
echo 📝 Actualizando todos los archivos .ts y .tsx...

for /r "frontend\src" %%f in (*.ts *.tsx) do (
    if exist "%%f" (
        powershell -Command "(Get-Content '%%f') -replace 'PlayR', 'Drive+' | Set-Content '%%f'"
        powershell -Command "(Get-Content '%%f') -replace 'PlayT', 'Drive+' | Set-Content '%%f'"
        powershell -Command "(Get-Content '%%f') -replace 'playr', 'drive-plus' | Set-Content '%%f'"
        powershell -Command "(Get-Content '%%f') -replace 'playt', 'drive-plus' | Set-Content '%%f'"
        powershell -Command "(Get-Content '%%f') -replace 'logo-playr', 'logo-drive-plus' | Set-Content '%%f'"
        powershell -Command "(Get-Content '%%f') -replace 'Plataforma PlayR', 'Plataforma Drive+' | Set-Content '%%f'"
        powershell -Command "(Get-Content '%%f') -replace 'Bienvenido a PlayR', 'Bienvenido a Drive+' | Set-Content '%%f'"
        powershell -Command "(Get-Content '%%f') -replace 'Instalar PlayR', 'Instalar Drive+' | Set-Content '%%f'"
        powershell -Command "(Get-Content '%%f') -replace 'Acerca de PlayR', 'Acerca de Drive+' | Set-Content '%%f'"
        powershell -Command "(Get-Content '%%f') -replace 'Dashboard PlayR', 'Dashboard Drive+' | Set-Content '%%f'"
        powershell -Command "(Get-Content '%%f') -replace 'Diagnóstico CORS - PlayR', 'Diagnóstico CORS - Drive+' | Set-Content '%%f'"
    )
)

echo ✅ Archivos TypeScript/React actualizados

REM ============================================
REM MOBILE - Si existe
REM ============================================
if exist "mobile" (
    echo 📱 Actualizando aplicación móvil...
    for /r "mobile" %%f in (*.ts *.tsx *.js *.jsx) do (
        if exist "%%f" (
            powershell -Command "(Get-Content '%%f') -replace 'PlayR', 'Drive+' | Set-Content '%%f'"
            powershell -Command "(Get-Content '%%f') -replace 'PlayT', 'Drive+' | Set-Content '%%f'"
            powershell -Command "(Get-Content '%%f') -replace 'Bienvenido a PlayR', 'Bienvenido a Drive+' | Set-Content '%%f'"
            powershell -Command "(Get-Content '%%f') -replace 'Acerca de PlayR', 'Acerca de Drive+' | Set-Content '%%f'"
        )
    )
    echo ✅ Aplicación móvil actualizada
)

REM ============================================
REM BACKEND - Todos los archivos Python
REM ============================================
echo 🔧 Actualizando backend...

for /r "backend" %%f in (*.py) do (
    if exist "%%f" (
        powershell -Command "(Get-Content '%%f') -replace 'PlayR', 'Drive+' | Set-Content '%%f'"
        powershell -Command "(Get-Content '%%f') -replace 'PlayT', 'Drive+' | Set-Content '%%f'"
        powershell -Command "(Get-Content '%%f') -replace 'playr', 'drive-plus' | Set-Content '%%f'"
        powershell -Command "(Get-Content '%%f') -replace 'playt', 'drive-plus' | Set-Content '%%f'"
    )
)

echo ✅ Archivos Python actualizados

REM ============================================
REM DOCUMENTACIÓN - Todos los archivos .md
REM ============================================
echo 📚 Actualizando documentación...

for /r . %%f in (*.md) do (
    if exist "%%f" (
        powershell -Command "(Get-Content '%%f') -replace 'PlayR', 'Drive+' | Set-Content '%%f'"
        powershell -Command "(Get-Content '%%f') -replace 'PlayT', 'Drive+' | Set-Content '%%f'"
        powershell -Command "(Get-Content '%%f') -replace 'playr', 'drive-plus' | Set-Content '%%f'"
        powershell -Command "(Get-Content '%%f') -replace 'playt', 'drive-plus' | Set-Content '%%f'"
        powershell -Command "(Get-Content '%%f') -replace 'playr-padel-rankings', 'drive-plus-padel' | Set-Content '%%f'"
        powershell -Command "(Get-Content '%%f') -replace 'playt-backend', 'driveplus-backend' | Set-Content '%%f'"
        powershell -Command "(Get-Content '%%f') -replace 'playr-backend', 'driveplus-backend' | Set-Content '%%f'"
    )
)

echo ✅ Documentación actualizada

REM ============================================
REM ARCHIVOS DE CONFIGURACIÓN
REM ============================================
echo ⚙️ Actualizando configuraciones...

REM .htaccess
if exist "frontend\.htaccess" (
    powershell -Command "(Get-Content 'frontend\.htaccess') -replace 'PlayR', 'DriveP' | Set-Content 'frontend\.htaccess'"
    powershell -Command "(Get-Content 'frontend\.htaccess') -replace 'PlayT', 'DriveP' | Set-Content 'frontend\.htaccess'"
    echo ✅ .htaccess actualizado
)

REM package.json del backend
if exist "backend\package.json" (
    powershell -Command "(Get-Content 'backend\package.json') -replace 'PlayR', 'Drive+' | Set-Content 'backend\package.json'"
    powershell -Command "(Get-Content 'backend\package.json') -replace 'PlayT', 'Drive+' | Set-Content 'backend\package.json'"
    echo ✅ Backend package.json actualizado
)

REM ============================================
REM SCRIPTS DE DESARROLLO
REM ============================================
echo 🛠️ Actualizando scripts...

for %%f in (start-dev*.bat fix-venv.bat) do (
    if exist %%f (
        powershell -Command "(Get-Content %%f) -replace 'PlayR', 'Drive+' | Set-Content %%f"
        powershell -Command "(Get-Content %%f) -replace 'PlayT', 'Drive+' | Set-Content %%f"
    )
)

echo ✅ Scripts de desarrollo actualizados

REM ============================================
REM ARCHIVOS JSON Y CONFIGURACIÓN
REM ============================================
echo 📄 Actualizando archivos JSON...

REM manifest.json si existe
if exist "frontend\public\manifest.json" (
    powershell -Command "(Get-Content 'frontend\public\manifest.json') -replace 'PlayR', 'Drive+' | Set-Content 'frontend\public\manifest.json'"
    powershell -Command "(Get-Content 'frontend\public\manifest.json') -replace 'PlayT', 'Drive+' | Set-Content 'frontend\public\manifest.json'"
    echo ✅ manifest.json actualizado
)

echo.
echo 🎉 REBRANDING COMPLETO FINALIZADO
echo.
echo 📋 CAMBIOS REALIZADOS:
echo   ✅ PlayR → Drive+ (en todo el código)
echo   ✅ PlayT → Drive+ (en todo el código)
echo   ✅ playr → drive-plus (nombres técnicos)
echo   ✅ playt → drive-plus (nombres técnicos)
echo   ✅ logo-playr → logo-drive-plus (assets)
echo   ✅ URLs /PlayR/ → /DriveP/
echo   ✅ URLs /PlayT/ → /DriveP/
echo   ✅ Mensajes de usuario actualizados
echo   ✅ Documentación completa
echo   ✅ Scripts de desarrollo
echo   ✅ Configuraciones
echo.
echo 🚨 PRÓXIMOS PASOS MANUALES:
echo   1. 🖼️ Cambiar logo: logo-playr.png → logo-drive-plus.png
echo   2. 🌐 Actualizar Hostinger: /PlayR/ → /DriveP/
echo   3. 🔧 Redeploy backend en Render
echo   4. 🔥 Actualizar Firebase project
echo   5. 📱 Cambiar iconos y assets
echo.
pause