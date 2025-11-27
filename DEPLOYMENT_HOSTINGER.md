# 🚀 Deployment PlayR - Producción

## ✅ CAMBIOS APLICADOS

### 1. Error COOP Corregido ✅
- Agregado `prompt: 'select_account'` al Google Provider en Firebase
- Eliminados warnings de Cross-Origin-Opener-Policy

### 2. Datos Hardcodeados Eliminados ✅
- Removida categoría "7ma" hardcodeada
- Removida info de posición hardcodeada
- Card de categoría reemplazada por estadísticas reales (victorias/derrotas/winrate)
- Año dinámico en "Miembro desde"

### 3. Código Limpio ✅
- Removidos imports no utilizados
- Optimizado para producción

---

## 📦 DEPLOYMENT EN HOSTINGER

### Paso 1: Build

```bash
cd frontend
npm install
npm run build
```

Esto genera `frontend/dist/` con los archivos listos.

### Paso 2: Subir Archivos

**File Manager de Hostinger:**

1. Accede a tu panel de Hostinger
2. Abre **File Manager**
3. Navega a `public_html/PlayR/`
4. **ELIMINA** todo el contenido anterior
5. **SUBE** todo el contenido de `frontend/dist/`
   - Selecciona todos los archivos dentro de dist/
   - Arrástralos o usa "Upload"

**Estructura final en Hostinger:**
```
public_html/
└── PlayR/
    ├── index.html
    ├── assets/
    │   ├── index-[hash].js
    │   ├── index-[hash].css
    │   └── ...
    └── .htaccess
```

### Paso 3: Configurar .htaccess

Crear archivo `.htaccess` en `public_html/PlayR/`:

```apache
<IfModule mod_rewrite.c>
  RewriteEngine On
  RewriteBase /PlayR/
  RewriteRule ^index\.html$ - [L]
  RewriteCond %{REQUEST_FILENAME} !-f
  RewriteCond %{REQUEST_FILENAME} !-d
  RewriteRule . /PlayR/index.html [L]
</IfModule>

# Compresión
<IfModule mod_deflate.c>
  AddOutputFilterByType DEFLATE text/html text/plain text/xml text/css text/javascript application/javascript application/json
</IfModule>

# Cache
<IfModule mod_expires.c>
  ExpiresActive On
  ExpiresByType image/* "access plus 1 year"
  ExpiresByType text/css "access plus 1 month"
  ExpiresByType application/javascript "access plus 1 month"
</IfModule>
```

### Paso 4: Verificar

1. Accede a https://kioskito.click/PlayR
2. Verifica que cargue
3. Prueba login/registro
4. Verifica conexión con backend Railway

---

## 🔧 CONFIGURACIÓN ACTUAL

### Frontend (Hostinger)
- **URL**: https://kioskito.click/PlayR
- **Base Path**: `/PlayR/` (configurado en vite.config.ts)

### Backend (Railway)
- **API URL**: https://playr-proyecto-production.up.railway.app
- **WebSocket**: wss://playr-proyecto-production.up.railway.app

### Firebase
- **Auth Domain**: playr-3f394.firebaseapp.com
- **Storage**: playr-3f394.firebasestorage.app

---

## 🚨 CHECKLIST PRE-DEPLOYMENT

- [x] Build exitoso sin errores
- [x] Variables de entorno configuradas
- [x] Error COOP corregido
- [x] Datos hardcodeados eliminados
- [x] Base path configurado para /PlayR/
- [ ] Archivos subidos a Hostinger
- [ ] .htaccess configurado
- [ ] Verificado en producción

---

## 🔄 ACTUALIZAR DEPLOYMENT

Cada vez que hagas cambios:

```bash
# 1. Build
cd frontend
npm run build

# 2. Subir a Hostinger
# - Eliminar contenido de public_html/PlayR/
# - Subir nuevo contenido de frontend/dist/
```

---

## 🐛 TROUBLESHOOTING

### Error 404 en rutas
- Verificar que .htaccess esté presente
- Verificar RewriteBase en .htaccess

### No carga assets
- Verificar que base: '/PlayR/' esté en vite.config.ts
- Verificar que los archivos estén en la carpeta correcta

### Error de CORS
- Verificar que kioskito.click esté en CORS_ORIGINS del backend
- Backend debe incluir: "https://kioskito.click"

### Firebase no funciona
- Verificar variables VITE_FIREBASE_* en .env
- Verificar que el build incluya las variables

---

**Fecha:** 27/11/2025
**Estado:** ✅ Listo para deployment
