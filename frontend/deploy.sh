#!/bin/bash

# Script para hacer build y deploy del frontend de PlayR
# Ejecutar desde PlayRMain/frontend/

echo "🚀 Iniciando build y deploy de PlayR Frontend..."

# Verificar que estamos en el directorio correcto
if [ ! -f "package.json" ]; then
    echo "❌ Error: No se encontró package.json. Ejecuta este script desde PlayRMain/frontend/"
    exit 1
fi

# Limpiar build anterior
echo "🧹 Limpiando build anterior..."
rm -rf dist/

# Instalar dependencias (por si acaso)
echo "📦 Verificando dependencias..."
npm install

# Hacer build
echo "🔨 Haciendo build..."
npm run build

if [ $? -ne 0 ]; then
    echo "❌ Error en el build"
    exit 1
fi

echo "✅ Build completado exitosamente"

# Verificar que el build se creó
if [ ! -d "dist" ]; then
    echo "❌ Error: No se generó la carpeta dist/"
    exit 1
fi

echo "📁 Contenido de dist/:"
ls -la dist/

echo ""
echo "🎉 Frontend listo para deploy!"
echo ""
echo "📋 Próximos pasos:"
echo "1. Subir el contenido de dist/ a tu servidor web"
echo "2. Asegurar que el servidor sirva index.html para rutas SPA"
echo "3. Verificar que los archivos .htaccess estén en su lugar"
echo ""
echo "🔧 Para probar CORS:"
echo "   Visita: https://kioskito.click/PlayR/cors-debug"
echo ""
echo "📊 Archivos generados:"
find dist/ -type f -name "*.js" -o -name "*.css" -o -name "*.html" | head -10