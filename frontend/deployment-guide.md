# 🚀 Guía de Deployment - Drive+ Frontend

## 📋 Pre-requisitos

1. **Node.js** >= 18.0.0
2. **npm** >= 9.0.0
3. **Cuenta en Hostinger/Vercel** (para frontend)
4. **Backend desplegado** en Render

## 🔧 Preparación

### 1. Configurar variables de entorno

Copia `.env.production` a `.env` y actualiza:

```bash
cp .env.production .env
```

Edita `.env` con tus valores reales:
- `VITE_API_URL`: URL del backend en Render
- `VITE_FIREBASE_*`: Credenciales de Firebase
- Otros valores según tu configuración

### 2. Ejecutar preparación automática

```bash
npm run prepare-prod
```

Este comando:
- ✅ Verifica configuración
- ✅ Instala dependencias
- ✅ Ejecuta linting
- ✅ Verifica tipos TypeScript
- ✅ Crea build optimizado
- ✅ Genera reporte

## 🌐 Deployment en Hostinger

### Opción A: Panel de Control

1. **Accede al Panel de Hostinger**
2. **Ve a "Administrador de Archivos"**
3. **Navega a `public_html/`**
4. **Sube el contenido de `/dist`**

### Opción B: FTP/SFTP

```bash
# Usando rsync (recomendado)
rsync -avz --delete dist/ usuario@servidor:/public_html/

# O usando scp
scp -r dist/* usuario@servidor:/public_html/
```

### 3. Configurar .htaccess (Hostinger)

Crea `/public_html/.htaccess`:

```apache
# Habilitar compresión
<IfModule mod_deflate.c>
    AddOutputFilterByType DEFLATE text/plain
    AddOutputFilterByType DEFLATE text/html
    AddOutputFilterByType DEFLATE text/xml
    AddOutputFilterByType DEFLATE text/css
    AddOutputFilterByType DEFLATE application/xml
    AddOutputFilterByType DEFLATE application/xhtml+xml
    AddOutputFilterByType DEFLATE application/rss+xml
    AddOutputFilterByType DEFLATE application/javascript
    AddOutputFilterByType DEFLATE application/x-javascript
</IfModule>

# Cache de archivos estáticos
<IfModule mod_expires.c>
    ExpiresActive on
    ExpiresByType text/css "access plus 1 year"
    ExpiresByType application/javascript "access plus 1 year"
    ExpiresByType image/png "access plus 1 year"
    ExpiresByType image/jpg "access plus 1 year"
    ExpiresByType image/jpeg "access plus 1 year"
    ExpiresByType image/gif "access plus 1 year"
    ExpiresByType image/svg+xml "access plus 1 year"
</IfModule>

# Rewrite para SPA (React Router)
<IfModule mod_rewrite.c>
    RewriteEngine On
    RewriteBase /
    RewriteRule ^index\.html$ - [L]
    RewriteCond %{REQUEST_FILENAME} !-f
    RewriteCond %{REQUEST_FILENAME} !-d
    RewriteRule . /index.html [L]
</IfModule>

# Seguridad
<IfModule mod_headers.c>
    Header always set X-Frame-Options DENY
    Header always set X-Content-Type-Options nosniff
    Header always set Referrer-Policy "strict-origin-when-cross-origin"
    Header always set Permissions-Policy "geolocation=(), microphone=(), camera=()"
</IfModule>
```

## 🌐 Deployment en Vercel (Alternativa)

### 1. Instalar Vercel CLI

```bash
npm i -g vercel
```

### 2. Deploy

```bash
# Primera vez
vercel

# Deployments posteriores
vercel --prod
```

### 3. Configurar variables de entorno en Vercel

```bash
vercel env add VITE_API_URL
vercel env add VITE_FIREBASE_API_KEY
# ... otras variables
```

## 🔍 Verificación Post-Deployment

### 1. Checklist básico

- [ ] ✅ Sitio carga correctamente
- [ ] ✅ Login/registro funciona
- [ ] ✅ API se conecta al backend
- [ ] ✅ Rutas funcionan (no 404)
- [ ] ✅ Assets se cargan (imágenes, CSS, JS)

### 2. Pruebas de rendimiento

```bash
# Lighthouse (Chrome DevTools)
# PageSpeed Insights: https://pagespeed.web.dev/
# GTmetrix: https://gtmetrix.com/
```

### 3. Monitoreo

- **Errores**: Consola del navegador
- **Red**: Network tab en DevTools
- **Performance**: Lighthouse score
- **Uptime**: Pingdom/UptimeRobot

## 🐛 Troubleshooting

### Error: "Failed to fetch"
- ✅ Verifica `VITE_API_URL` en `.env`
- ✅ Confirma que el backend esté funcionando
- ✅ Revisa CORS en el backend

### Error: 404 en rutas
- ✅ Verifica configuración de `.htaccess`
- ✅ Confirma que el servidor soporte SPA

### Error: Firebase
- ✅ Verifica credenciales de Firebase
- ✅ Confirma dominios autorizados en Firebase Console

### Performance lenta
- ✅ Habilita compresión gzip
- ✅ Optimiza imágenes
- ✅ Usa CDN si es posible

## 📊 Métricas objetivo

- **First Contentful Paint**: < 2s
- **Largest Contentful Paint**: < 3s
- **Cumulative Layout Shift**: < 0.1
- **Time to Interactive**: < 4s
- **Lighthouse Score**: > 90

## 🔄 CI/CD (Opcional)

### GitHub Actions para auto-deploy

Crea `.github/workflows/deploy.yml`:

```yaml
name: Deploy to Production

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Setup Node.js
      uses: actions/setup-node@v3
      with:
        node-version: '18'
        cache: 'npm'
    
    - name: Install dependencies
      run: npm ci
    
    - name: Build
      run: npm run build:prod
      env:
        VITE_API_URL: ${{ secrets.VITE_API_URL }}
        VITE_FIREBASE_API_KEY: ${{ secrets.VITE_FIREBASE_API_KEY }}
    
    - name: Deploy to Vercel
      uses: amondnet/vercel-action@v20
      with:
        vercel-token: ${{ secrets.VERCEL_TOKEN }}
        vercel-org-id: ${{ secrets.ORG_ID }}
        vercel-project-id: ${{ secrets.PROJECT_ID }}
        vercel-args: '--prod'
```

## 📞 Soporte

Si encuentras problemas:

1. **Revisa los logs** del navegador y servidor
2. **Consulta la documentación** de Hostinger/Vercel
3. **Verifica la configuración** del backend
4. **Prueba en local** primero

---

¡Listo para producción! 🎉