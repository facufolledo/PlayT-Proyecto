#!/usr/bin/env node

/**
 * Script para preparar la aplicación para producción
 * Verifica configuraciones, optimiza assets y valida el build
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

console.log('🚀 Preparando PlayR para producción...\n');

// 1. Verificar variables de entorno
console.log('📋 1. Verificando configuración...');

const envFile = path.join(__dirname, '.env');
const envExampleFile = path.join(__dirname, '.env.example');

if (!fs.existsSync(envFile)) {
  console.log('⚠️  Archivo .env no encontrado');
  if (fs.existsSync(envExampleFile)) {
    console.log('📄 Copiando .env.example a .env...');
    fs.copyFileSync(envExampleFile, envFile);
  }
}

// Leer variables de entorno
const envContent = fs.readFileSync(envFile, 'utf8');
const requiredVars = [
  'VITE_API_URL',
  'VITE_FIREBASE_API_KEY',
  'VITE_FIREBASE_AUTH_DOMAIN',
  'VITE_FIREBASE_PROJECT_ID'
];

console.log('🔍 Verificando variables requeridas:');
requiredVars.forEach(varName => {
  if (envContent.includes(`${varName}=`)) {
    console.log(`  ✅ ${varName}`);
  } else {
    console.log(`  ❌ ${varName} - FALTANTE`);
  }
});

// 2. Verificar dependencias
console.log('\n📦 2. Verificando dependencias...');
try {
  execSync('npm list --depth=0', { stdio: 'pipe' });
  console.log('  ✅ Dependencias instaladas correctamente');
} catch (error) {
  console.log('  ⚠️  Instalando dependencias faltantes...');
  execSync('npm install', { stdio: 'inherit' });
}

// 3. Ejecutar linting
console.log('\n🔍 3. Ejecutando linting...');
try {
  execSync('npm run lint', { stdio: 'pipe' });
  console.log('  ✅ Código sin errores de linting');
} catch (error) {
  console.log('  ⚠️  Errores de linting encontrados, ejecuta: npm run lint');
}

// 4. Ejecutar type checking
console.log('\n📝 4. Verificando tipos TypeScript...');
try {
  execSync('npx tsc --noEmit', { stdio: 'pipe' });
  console.log('  ✅ Sin errores de TypeScript');
} catch (error) {
  console.log('  ⚠️  Errores de TypeScript encontrados');
}

// 5. Optimizar imágenes (si existen)
console.log('\n🖼️  5. Verificando assets...');
const publicDir = path.join(__dirname, 'public');
const assetsDir = path.join(__dirname, 'src', 'assets');

[publicDir, assetsDir].forEach(dir => {
  if (fs.existsSync(dir)) {
    const files = fs.readdirSync(dir, { recursive: true });
    const imageFiles = files.filter(file => 
      typeof file === 'string' && /\.(jpg|jpeg|png|gif|svg|webp)$/i.test(file)
    );
    console.log(`  📁 ${path.basename(dir)}: ${imageFiles.length} imágenes encontradas`);
  }
});

// 6. Crear build de producción
console.log('\n🏗️  6. Creando build de producción...');
try {
  execSync('npm run build', { stdio: 'inherit' });
  console.log('  ✅ Build creado exitosamente');
} catch (error) {
  console.log('  ❌ Error en el build');
  process.exit(1);
}

// 7. Verificar tamaño del build
console.log('\n📊 7. Analizando tamaño del build...');
const distDir = path.join(__dirname, 'dist');
if (fs.existsSync(distDir)) {
  const getDirectorySize = (dirPath) => {
    let totalSize = 0;
    const files = fs.readdirSync(dirPath, { withFileTypes: true });
    
    for (const file of files) {
      const filePath = path.join(dirPath, file.name);
      if (file.isDirectory()) {
        totalSize += getDirectorySize(filePath);
      } else {
        totalSize += fs.statSync(filePath).size;
      }
    }
    return totalSize;
  };

  const sizeInMB = (getDirectorySize(distDir) / (1024 * 1024)).toFixed(2);
  console.log(`  📦 Tamaño total del build: ${sizeInMB} MB`);
  
  if (parseFloat(sizeInMB) > 10) {
    console.log('  ⚠️  Build grande (>10MB), considera optimizar assets');
  } else {
    console.log('  ✅ Tamaño del build optimizado');
  }
}

// 8. Generar reporte de preparación
console.log('\n📋 8. Generando reporte...');
const report = {
  timestamp: new Date().toISOString(),
  environment: 'production',
  buildSize: fs.existsSync(distDir) ? `${(getDirectorySize(distDir) / (1024 * 1024)).toFixed(2)} MB` : 'N/A',
  nodeVersion: process.version,
  npmVersion: execSync('npm --version', { encoding: 'utf8' }).trim()
};

fs.writeFileSync(
  path.join(__dirname, 'production-report.json'),
  JSON.stringify(report, null, 2)
);

console.log('\n🎉 ¡Preparación para producción completada!');
console.log('\n📋 Próximos pasos:');
console.log('  1. Sube el contenido de /dist a tu servidor');
console.log('  2. Configura las variables de entorno en producción');
console.log('  3. Verifica que el backend esté configurado correctamente');
console.log('  4. Prueba la aplicación en el dominio de producción');

function getDirectorySize(dirPath) {
  let totalSize = 0;
  const files = fs.readdirSync(dirPath, { withFileTypes: true });
  
  for (const file of files) {
    const filePath = path.join(dirPath, file.name);
    if (file.isDirectory()) {
      totalSize += getDirectorySize(filePath);
    } else {
      totalSize += fs.statSync(filePath).size;
    }
  }
  return totalSize;
}