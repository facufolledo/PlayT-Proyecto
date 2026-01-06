# Script para hacer build y deploy del frontend de PlayR
# Ejecutar desde PlayRMain/frontend/

Write-Host "🚀 Iniciando build y deploy de PlayR Frontend..." -ForegroundColor Green

# Verificar que estamos en el directorio correcto
if (-not (Test-Path "package.json")) {
    Write-Host "❌ Error: No se encontró package.json. Ejecuta este script desde PlayRMain/frontend/" -ForegroundColor Red
    exit 1
}

# Limpiar build anterior
Write-Host "🧹 Limpiando build anterior..." -ForegroundColor Yellow
if (Test-Path "dist") {
    Remove-Item -Recurse -Force "dist"
}

# Instalar dependencias (por si acaso)
Write-Host "📦 Verificando dependencias..." -ForegroundColor Blue
npm install

# Hacer build
Write-Host "🔨 Haciendo build..." -ForegroundColor Blue
npm run build

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Error en el build" -ForegroundColor Red
    exit 1
}

Write-Host "✅ Build completado exitosamente" -ForegroundColor Green

# Verificar que el build se creó
if (-not (Test-Path "dist")) {
    Write-Host "❌ Error: No se generó la carpeta dist/" -ForegroundColor Red
    exit 1
}

Write-Host "📁 Contenido de dist/:" -ForegroundColor Cyan
Get-ChildItem "dist" | Format-Table Name, Length, LastWriteTime

Write-Host ""
Write-Host "🎉 Frontend listo para deploy!" -ForegroundColor Green
Write-Host ""
Write-Host "📋 Próximos pasos:" -ForegroundColor Yellow
Write-Host "1. Subir el contenido de dist/ a tu servidor web"
Write-Host "2. Asegurar que el servidor sirva index.html para rutas SPA"
Write-Host "3. Verificar que los archivos .htaccess estén en su lugar"
Write-Host ""
Write-Host "🔧 Para probar CORS:" -ForegroundColor Cyan
Write-Host "   Visita: https://kioskito.click/PlayR/cors-debug"
Write-Host ""
Write-Host "📊 Archivos generados:" -ForegroundColor Magenta
Get-ChildItem "dist" -Recurse -Include "*.js", "*.css", "*.html" | Select-Object -First 10 | Format-Table Name, Length