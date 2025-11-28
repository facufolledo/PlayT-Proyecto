# Script para iniciar el backend en Windows
# Ejecutar con: .\start_backend.ps1

Write-Host "🚀 Iniciando PlayT Backend..." -ForegroundColor Green
Write-Host "📍 Host: 127.0.0.1:8000" -ForegroundColor Cyan

# Activar entorno virtual si no está activado
if (-not $env:VIRTUAL_ENV) {
    Write-Host "⚙️  Activando entorno virtual..." -ForegroundColor Yellow
    .\venv\Scripts\Activate.ps1
}

# Iniciar servidor
uvicorn main:app --reload --host 127.0.0.1 --port 8000
