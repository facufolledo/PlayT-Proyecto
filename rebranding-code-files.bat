@echo off
echo 🔧 REBRANDING ARCHIVOS DE CÓDIGO - DRIVE+
echo.

echo 📝 Actualizando archivos de código específicos...

REM ============================================
REM FRONTEND - Componentes principales
REM ============================================
echo 🎨 Actualizando componentes del frontend...

REM Layout.tsx
if exist "frontend\src\components\Layout.tsx" (
    powershell -Command "(Get-Content 'frontend\src\components\Layout.tsx') -replace 'PlayT', 'Drive+' | Set-Content 'frontend\src\components\Layout.tsx'"
    powershell -Command "(Get-Content 'frontend\src\components\Layout.tsx') -replace 'PlayR', 'Drive+' | Set-Content 'frontend\src\components\Layout.tsx'"
    echo ✅ Layout.tsx actualizado
)

REM Sidebar.tsx
if exist "frontend\src\components\Sidebar.tsx" (
    powershell -Command "(Get-Content 'frontend\src\components\Sidebar.tsx') -replace 'PlayT', 'Drive+' | Set-Content 'frontend\src\components\Sidebar.tsx'"
    powershell -Command "(Get-Content 'frontend\src\components\Sidebar.tsx') -replace 'PlayR', 'Drive+' | Set-Content 'frontend\src\components\Sidebar.tsx'"
    echo ✅ Sidebar.tsx actualizado
)

REM Landing.tsx
if exist "frontend\src\pages\Landing.tsx" (
    powershell -Command "(Get-Content 'frontend\src\pages\Landing.tsx') -replace 'PlayT', 'Drive+' | Set-Content 'frontend\src\pages\Landing.tsx'"
    powershell -Command "(Get-Content 'frontend\src\pages\Landing.tsx') -replace 'PlayR', 'Drive+' | Set-Content 'frontend\src\pages\Landing.tsx'"
    powershell -Command "(Get-Content 'frontend\src\pages\Landing.tsx') -replace 'playt', 'drive-plus' | Set-Content 'frontend\src\pages\Landing.tsx'"
    powershell -Command "(Get-Content 'frontend\src\pages\Landing.tsx') -replace 'playr', 'drive-plus' | Set-Content 'frontend\src\pages\Landing.tsx'"
    echo ✅ Landing.tsx actualizado
)

REM ============================================
REM BACKEND - Controladores y servicios
REM ============================================
echo 🔧 Actualizando backend...

REM Buscar y actualizar todos los archivos Python
for /r "backend" %%f in (*.py) do (
    if exist "%%f" (
        powershell -Command "(Get-Content '%%f') -replace 'PlayT', 'Drive+' | Set-Content '%%f'"
        powershell -Command "(Get-Content '%%f') -replace 'PlayR', 'Drive+' | Set-Content '%%f'"
        powershell -Command "(Get-Content '%%f') -replace 'playt', 'drive-plus' | Set-Content '%%f'"
        powershell -Command "(Get-Content '%%f') -replace 'playr', 'drive-plus' | Set-Content '%%f'"
    )
)

echo ✅ Archivos Python actualizados

REM ============================================
REM LOGS Y MENSAJES DE CONSOLA
REM ============================================
echo 📊 Actualizando logs y mensajes...

REM Actualizar mensajes en archivos TypeScript
for /r "frontend\src" %%f in (*.ts *.tsx) do (
    if exist "%%f" (
        powershell -Command "(Get-Content '%%f') -replace 'PlayT', 'Drive+' | Set-Content '%%f'"
        powershell -Command "(Get-Content '%%f') -replace 'PlayR', 'Drive+' | Set-Content '%%f'"
        powershell -Command "(Get-Content '%%f') -replace 'playt', 'drive-plus' | Set-Content '%%f'"
        powershell -Command "(Get-Content '%%f') -replace 'playr', 'drive-plus' | Set-Content '%%f'"
    )
)

echo ✅ Archivos TypeScript actualizados

REM ============================================
REM ARCHIVOS DE CONFIGURACIÓN ESPECÍFICOS
REM ============================================
echo ⚙️ Actualizando configuraciones específicas...

REM package.json del backend si existe
if exist "backend\package.json" (
    powershell -Command "(Get-Content 'backend\package.json') -replace 'PlayT', 'Drive+' | Set-Content 'backend\package.json'"
    powershell -Command "(Get-Content 'backend\package.json') -replace 'PlayR', 'Drive+' | Set-Content 'backend\package.json'"
    powershell -Command "(Get-Content 'backend\package.json') -replace 'playt', 'drive-plus' | Set-Content 'backend\package.json'"
    powershell -Command "(Get-Content 'backend\package.json') -replace 'playr', 'drive-plus' | Set-Content 'backend\package.json'"
    echo ✅ Backend package.json actualizado
)

REM requirements.txt comments
if exist "backend\requirements.txt" (
    powershell -Command "(Get-Content 'backend\requirements.txt') -replace 'PlayT', 'Drive+' | Set-Content 'backend\requirements.txt'"
    powershell -Command "(Get-Content 'backend\requirements.txt') -replace 'PlayR', 'Drive+' | Set-Content 'backend\requirements.txt'"
    echo ✅ requirements.txt actualizado
)

REM ============================================
REM ARCHIVOS DE DOCUMENTACIÓN ESPECÍFICOS
REM ============================================
echo 📚 Actualizando documentación específica...

REM Actualizar todos los archivos .md en backend
for /r "backend" %%f in (*.md) do (
    if exist "%%f" (
        powershell -Command "(Get-Content '%%f') -replace 'PlayT', 'Drive+' | Set-Content '%%f'"
        powershell -Command "(Get-Content '%%f') -replace 'PlayR', 'Drive+' | Set-Content '%%f'"
        powershell -Command "(Get-Content '%%f') -replace 'playt', 'drive-plus' | Set-Content '%%f'"
        powershell -Command "(Get-Content '%%f') -replace 'playr', 'drive-plus' | Set-Content '%%f'"
    )
)

echo ✅ Documentación del backend actualizada

echo.
echo 🎉 REBRANDING DE CÓDIGO COMPLETADO
echo.
echo 📋 ARCHIVOS ACTUALIZADOS:
echo   ✅ Todos los componentes React (.tsx)
echo   ✅ Todos los servicios TypeScript (.ts)
echo   ✅ Todos los controladores Python (.py)
echo   ✅ Archivos de configuración
echo   ✅ Documentación técnica
echo   ✅ Logs y mensajes de consola
echo.
pause