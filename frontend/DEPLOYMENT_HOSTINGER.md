# 🚀 Deployment Frontend en Hostinger

## Paso 1: Preparar el Build

### 1.1 Configurar Variables de Entorno
Crear/actualizar `frontend/.env.production`:

```env
# API URL (Actualizar con tu URL de Render)
VITE_API_URL=https://playr-api.onrender.com

# Firebase (Mismo que desarrollo)
VITE_FIREBASE_API_KEY=tu_api_key
VITE_FIREBASE_AUTH_DOMAIN=tu_proyecto.firebaseapp.com
VITE_FIREBASE_PROJECT_ID=tu_proyecto_id
VITE_FIREBASE_STORAGE_BUCKET=tu_proyecto.appspot.com
VITE_FIREBASE_MESSAGING_SENDER_ID=123456789
VITE_FIREBASE_APP_ID=1:123456789:web:abcdef
```

### 1.2 Build de Producción
```bash
cd frontend

# Instalar dependencias
npm install

# Build
npm run build

# Resultado: carpeta dist/
```

---

## Paso 2: Preparar Hostinger

### 2.1 Acceder a hPanel
1. Login en Hostinger
2. Ir a "Hosting" > Tu plan
3. Click en "Administrar"

### 2.2 Configurar Dominio
**Opción A - Dominio Principal:**
- El sitio estará en: `https://tudominio.com`

**Opción B - Subdominio:**
1. Dominios > Crear Subdominio
2. Nombre: `app` o `play`
3. Resultado: `https://app.tudominio.com`

---

## Paso 3: Subir Archivos

### Método 1: File Manager (Recomendado)

#### 3.1 Acceder a File Manager
1. hPanel > File Manager
2. Navegar a `public_html/` (o carpeta del dominio)

#### 3.2 Limpiar Carpeta
- Eliminar archivos existentes (index.html, etc.)
- Mantener `.htaccess` si existe

#### 3.3 Subir Build
1. Click "Upload Files"
2. Seleccionar TODO el contenido de `frontend/dist/`
3. Subir:
   - index.html
   - assets/
   - icons/
   - manifest.json
   - sw.js
   - logo playR.png
   - etc.

**⚠️ IMPORTANTE:** Subir el CONTENIDO de `dist/`, no la carpeta `dist/` misma.

---

### Método 2: FTP

#### 3.1 Obtener Credenciales FTP
1. hPanel > FTP Accounts
2. Crear cuenta o usar existente
3. Anotar:
   - Host: ftp.tudominio.com
   - Usuario: usuario@tudominio.com
   - Password: tu_password
   - Puerto: 21

#### 3.2 Conectar con FileZilla
```
Host: ftp.tudominio.com
Username: usuario@tudominio.com
Password: tu_password
Port: 21
```

#### 3.3 Subir Archivos
1. Local: Navegar a `frontend/dist/`
2. Remoto: Navegar a `public_html/`
3. Seleccionar TODO el contenido de `dist/`
4. Arrastrar a `public_html/`

---

### Método 3: Git (Avanzado)

#### 3.1 SSH Access
1. hPanel > Advanced > SSH Access
2. Habilitar SSH
3. Conectar:
```bash
ssh usuario@tudominio.com
```

#### 3.2 Clonar y Build
```bash
cd public_html
git clone https://github.com/tu-usuario/playr-frontend.git temp
cd temp/frontend
npm install
npm run build
mv dist/* ../
cd ../
rm -rf temp
```

---

## Paso 4: Configurar .htaccess

### 4.1 Crear/Editar .htaccess
En `public_html/.htaccess`:

```apache
# Habilitar RewriteEngine
RewriteEngine On

# Forzar HTTPS
RewriteCond %{HTTPS} off
RewriteRule ^(.*)$ https://%{HTTP_HOST}%{REQUEST_URI} [L,R=301]

# SPA Routing - Redirigir todo a index.html
RewriteCond %{REQUEST_FILENAME} !-f
RewriteCond %{REQUEST_FILENAME} !-d
RewriteRule ^(.*)$ /index.html [L]

# Comprimir archivos
<IfModule mod_deflate.c>
  AddOutputFilterByType DEFLATE text/html text/plain text/xml text/css text/javascript application/javascript application/json
</IfModule>

# Cache de assets
<IfModule mod_expires.c>
  ExpiresActive On
  ExpiresByType image/jpg "access plus 1 year"
  ExpiresByType image/jpeg "access plus 1 year"
  ExpiresByType image/gif "access plus 1 year"
  ExpiresByType image/png "access plus 1 year"
  ExpiresByType image/webp "access plus 1 year"
  ExpiresByType image/svg+xml "access plus 1 year"
  ExpiresByType text/css "access plus 1 month"
  ExpiresByType application/javascript "access plus 1 month"
  ExpiresByType application/pdf "access plus 1 month"
  ExpiresByType text/x-javascript "access plus 1 month"
  ExpiresByType image/x-icon "access plus 1 year"
  ExpiresByType application/x-shockwave-flash "access plus 1 month"
</IfModule>

# Headers de seguridad
<IfModule mod_headers.c>
  Header set X-Content-Type-Options "nosniff"
  Header set X-Frame-Options "SAMEORIGIN"
  Header set X-XSS-Protection "1; mode=block"
  Header set Referrer-Policy "strict-origin-when-cross-origin"
  
  # PWA Headers
  Header set Service-Worker-Allowed "/"
  
  # Cache control
  <FilesMatch "\.(ico|pdf|flv|jpg|jpeg|png|gif|webp|svg|js|css|swf|woff|woff2|ttf|eot)$">
    Header set Cache-Control "max-age=31536000, public"
  </FilesMatch>
  
  <FilesMatch "\.(html|htm)$">
    Header set Cache-Control "max-age=0, no-cache, no-store, must-revalidate"
  </FilesMatch>
</IfModule>

# Tipos MIME para PWA
AddType application/manifest+json .webmanifest
AddType application/x-web-app-manifest+json .webapp
AddType text/cache-manifest .appcache

# Service Worker
<Files "sw.js">
  Header set Service-Worker-Allowed "/"
  Header set Cache-Control "no-cache, no-store, must-revalidate"
</Files>
```

---

## Paso 5: Configurar SSL

### 5.1 SSL Gratuito (Let's Encrypt)
1. hPanel > SSL
2. Seleccionar dominio
3. Click "Install SSL"
4. Esperar 5-10 minutos

### 5.2 Verificar SSL
```bash
# Debe mostrar certificado válido
curl -I https://tudominio.com
```

---

## Paso 6: Optimizaciones

### 6.1 Comprimir Assets
```bash
# Antes de subir, comprimir imágenes
npm install -g imagemin-cli
imagemin dist/assets/*.{jpg,png} --out-dir=dist/assets/
```

### 6.2 Habilitar Gzip
Ya configurado en `.htaccess` con `mod_deflate`

### 6.3 CDN (Opcional)
Hostinger incluye Cloudflare CDN:
1. hPanel > Performance > CDN
2. Activar Cloudflare
3. Configurar DNS

---

## Paso 7: Configurar DNS

### 7.1 Si usas dominio externo
Apuntar a Hostinger:
```
A Record:
@ -> IP de Hostinger (ej: 123.45.67.89)
www -> IP de Hostinger

CNAME:
www -> tudominio.com
```

### 7.2 Verificar DNS
```bash
nslookup tudominio.com
dig tudominio.com
```

---

## Paso 8: Testing

### 8.1 Verificar Sitio
```
✅ https://tudominio.com carga
✅ Rutas funcionan (ej: /dashboard)
✅ API conecta con Render
✅ Login con Google funciona
✅ PWA instalable
✅ Service Worker activo
```

### 8.2 Lighthouse Audit
1. Chrome DevTools > Lighthouse
2. Run audit
3. Verificar scores:
   - Performance: >90
   - PWA: 100
   - SEO: >90

### 8.3 Test en Móviles
- Android: Instalar PWA
- iOS: Agregar a inicio
- Verificar offline mode

---

## Paso 9: Actualizaciones

### 9.1 Proceso de Update
```bash
# 1. Hacer cambios en código
cd frontend

# 2. Build nuevo
npm run build

# 3. Subir a Hostinger
# Via File Manager o FTP
# Reemplazar archivos en public_html/

# 4. Limpiar cache
# Hostinger > Performance > Clear Cache
```

### 9.2 Cache Busting
Vite automáticamente agrega hashes a archivos:
```
assets/index-abc123.js
assets/index-def456.css
```

---

## Paso 10: Monitoreo

### 10.1 Analytics
Agregar Google Analytics en `index.html`:
```html
<!-- Google Analytics -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-XXXXXXXXXX"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'G-XXXXXXXXXX');
</script>
```

### 10.2 Error Tracking
Considerar Sentry para errores en producción.

---

## 🔧 Troubleshooting

### Error 404 en rutas
- Verificar `.htaccess` existe
- Verificar RewriteEngine On
- Verificar mod_rewrite habilitado

### Assets no cargan
- Verificar rutas en `index.html`
- Verificar permisos de archivos (644)
- Verificar permisos de carpetas (755)

### Service Worker no funciona
- Verificar HTTPS activo
- Verificar `sw.js` en raíz
- Limpiar cache del navegador

### API no conecta
- Verificar VITE_API_URL correcto
- Verificar CORS en backend
- Verificar SSL en ambos lados

---

## 📊 Checklist Final

- [ ] Build de producción creado
- [ ] Variables de entorno configuradas
- [ ] Archivos subidos a Hostinger
- [ ] .htaccess configurado
- [ ] SSL instalado y activo
- [ ] DNS configurado
- [ ] Rutas SPA funcionando
- [ ] API conectando con Render
- [ ] PWA instalable
- [ ] Service Worker activo
- [ ] Lighthouse score >90
- [ ] Tested en móviles

---

## 🎯 URLs Finales

```
Frontend: https://tudominio.com
API: https://playr-api.onrender.com
Docs: https://playr-api.onrender.com/docs
```

---

## 💰 Costos Hostinger

### Premium Web Hosting
- ~$2.99/mes (promo)
- 100 GB SSD
- 100 websites
- SSL gratis
- CDN gratis
- Email incluido

### Business Web Hosting
- ~$3.99/mes (promo)
- 200 GB SSD
- Backups diarios
- CDN premium

---

**¡Frontend listo en Hostinger!** 🎉
