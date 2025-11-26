# 🚂 Deploy en Railway - PlayR

## 📋 Configuración Actualizada

### Frontend
- **Dominio**: https://kioskito.click/PlayR
- **Backend API**: https://playr-proyecto-production.up.railway.app

### Backend
- **Plataforma**: Railway
- **URL**: https://playr-proyecto-production.up.railway.app
- **Base de Datos**: Neon PostgreSQL

---

## 🎯 Paso 1: Configurar Backend en Railway

### 1.1 Crear Proyecto en Railway

1. Ve a https://railway.app/
2. Haz clic en "New Project"
3. Selecciona "Deploy from GitHub repo"
4. Conecta tu repositorio
5. Selecciona la carpeta `backend`

### 1.2 Variables de Entorno

Agrega estas variables en Railway Dashboard:

```env
# Base de datos
DATABASE_URL=postgresql+pg8000://neondb_owner:npg_i2uqcNEZbk4M@ep-dawn-frost-ac67h4ke-pooler.sa-east-1.aws.neon.tech/neondb
DATABASE_URL_ASYNC=postgresql+asyncpg://neondb_owner:npg_i2uqcNEZbk4M@ep-dawn-frost-ac67h4ke-pooler.sa-east-1.aws.neon.tech/neondb

# Seguridad
SECRET_KEY=playt_super_secret_key_2025_cambiar_en_produccion
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Servidor
HOST=0.0.0.0
PORT=8000
DEBUG=False

# Elo
INITIAL_ELO_RATING=1200
K_FACTOR=32
MIN_K_FACTOR=16
MAX_K_FACTOR=48

# App
APP_NAME=PlayT API
APP_VERSION=1.0.0

# CORS (IMPORTANTE: Incluir tu dominio)
CORS_ORIGINS=["https://kioskito.click", "https://www.kioskito.click"]

# Firebase
FIREBASE_CREDENTIALS_PATH=./firebase-credentials.json
```

### 1.3 Configurar Build

Railway detectará automáticamente que es Python. Si no:

**Build Command**: 
```bash
pip install -r requirements.txt
```

**Start Command**:
```bash
uvicorn main:app --host 0.0.0.0 --port $PORT
```

### 1.4 Dominio Personalizado (Opcional)

Si quieres usar un subdominio:
1. Ve a Settings → Domains
2. Agrega: `api.kioskito.click`
3. Configura DNS en Hostinger

---

## 🎨 Paso 2: Compilar Frontend

### 2.1 Verificar .env

Asegúrate de que `frontend/.env` tenga:

```env
VITE_API_URL=https://playr-proyecto-production.up.railway.app
VITE_WS_URL=wss://playr-proyecto-production.up.railway.app

VITE_FIREBASE_API_KEY=AIzaSyArwo4G6QDwM6XCWi5Vv98XEo2kcnd1kCg
VITE_FIREBASE_AUTH_DOMAIN=playr-3f394.firebaseapp.com
VITE_FIREBASE_PROJECT_ID=playr-3f394
VITE_FIREBASE_STORAGE_BUCKET=playr-3f394.firebasestorage.app
VITE_FIREBASE_MESSAGING_SENDER_ID=135735478278
VITE_FIREBASE_APP_ID=1:135735478278:web:7461afc12bf20c95951b87
```

### 2.2 Compilar

```powershell
cd frontend
npm install
npm run build
```

---

## 📤 Paso 3: Subir a Hostinger

### 3.1 Archivos a Subir

Sube TODO el contenido de `frontend/dist/` a:
```
public_html/PlayR/
```

### 3.2 Verificar .htaccess

Asegúrate de que `public_html/PlayR/.htaccess` tenga:

```apache
<IfModule mod_rewrite.c>
  RewriteEngine On
  RewriteBase /PlayR/
  RewriteRule ^index\.html$ - [L]
  RewriteCond %{REQUEST_FILENAME} !-f
  RewriteCond %{REQUEST_FILENAME} !-d
  RewriteRule . /PlayR/index.html [L]
</IfModule>

# Habilitar CORS
<IfModule mod_headers.c>
  Header set Access-Control-Allow-Origin "*"
  Header set Access-Control-Allow-Methods "GET, POST, PUT, DELETE, OPTIONS"
  Header set Access-Control-Allow-Headers "Content-Type, Authorization"
  
  # Configurar COOP para permitir popups de Firebase
  Header always set Cross-Origin-Opener-Policy "same-origin-allow-popups"
  Header always set Cross-Origin-Embedder-Policy "unsafe-none"
  
  # Permitir iframes de Firebase
  Header always set X-Frame-Options "ALLOW-FROM https://playr-3f394.firebaseapp.com"
</IfModule>

# Comprimir archivos
<IfModule mod_deflate.c>
  AddOutputFilterByType DEFLATE text/html text/plain text/xml text/css text/javascript application/javascript application/json
</IfModule>

# Cache para assets
<IfModule mod_expires.c>
  ExpiresActive On
  ExpiresByType image/jpg "access plus 1 year"
  ExpiresByType image/jpeg "access plus 1 year"
  ExpiresByType image/gif "access plus 1 year"
  ExpiresByType image/png "access plus 1 year"
  ExpiresByType image/svg+xml "access plus 1 year"
  ExpiresByType text/css "access plus 1 month"
  ExpiresByType application/javascript "access plus 1 month"
</IfModule>
```

---

## ✅ Paso 4: Verificar Despliegue

### 4.1 Backend

Prueba el backend:

```bash
# Health check
curl https://playr-proyecto-production.up.railway.app/health

# Debe responder:
# {"status":"healthy","service":"PlayT API","database":"connected"}
```

### 4.2 Frontend

1. Ve a: https://kioskito.click/PlayR
2. Abre DevTools (F12) → Console
3. Verifica que no haya errores
4. Prueba el login con Google

### 4.3 Conexión Frontend-Backend

En la consola del navegador deberías ver:

```
✅ 🔥 Firebase user: tu@email.com
✅ 🔑 Firebase token obtenido
✅ ✅ Usuario backend encontrado: tu@email.com
```

---

## 🔧 Troubleshooting

### Error: CORS

**Síntoma**: Error de CORS en consola

**Solución**:
1. Ve a Railway Dashboard
2. Variables de entorno
3. Verifica que `CORS_ORIGINS` incluya `https://kioskito.click`
4. Reinicia el servicio

### Error: 502 Bad Gateway

**Síntoma**: Backend no responde

**Solución**:
1. Ve a Railway Dashboard → Logs
2. Busca errores en los logs
3. Verifica que `DATABASE_URL` sea correcta
4. Verifica que el puerto sea `$PORT`

### Error: Cannot GET /PlayR

**Síntoma**: 404 en rutas de React

**Solución**:
1. Verifica que `.htaccess` esté en `public_html/PlayR/`
2. Verifica que `RewriteBase` sea `/PlayR/`
3. Limpia caché del navegador

### Backend Lento

**Síntoma**: Respuestas lentas del backend

**Solución**:
1. Railway puede dormir en plan gratuito
2. Considera upgrade a plan Hobby ($5/mes)
3. O usa Railway's "Keep Alive" feature

---

## 📊 Comparación: Render vs Railway

| Característica | Render | Railway |
|---------------|--------|---------|
| **Precio Free** | $0 | $0 (con $5 crédito) |
| **Sleep** | Sí (15 min inactividad) | No (con crédito) |
| **Build Time** | ~5 min | ~2 min |
| **Deploy** | Automático (Git push) | Automático (Git push) |
| **Logs** | Sí | Sí (mejores) |
| **Dominio** | Incluido | Incluido |
| **Base de Datos** | Separada (Neon) | Separada (Neon) |

---

## 🚀 Ventajas de Railway

### 1. Más Rápido
- Builds más rápidos
- Deploys instantáneos
- Mejor performance

### 2. Mejor DX
- UI más intuitiva
- Logs en tiempo real
- Métricas detalladas

### 3. No Duerme
- Con crédito gratuito, no duerme
- Respuestas más rápidas
- Mejor experiencia de usuario

---

## 💰 Costos

### Plan Free
- $5 de crédito mensual
- ~500 horas de ejecución
- Suficiente para desarrollo

### Plan Hobby ($5/mes)
- $5 de crédito + $5 adicionales
- Sin límite de horas
- Recomendado para producción

---

## 📝 Checklist de Despliegue

### Backend
- [ ] Proyecto creado en Railway
- [ ] Variables de entorno configuradas
- [ ] Build command configurado
- [ ] Start command configurado
- [ ] Health check funciona
- [ ] CORS configurado correctamente

### Frontend
- [ ] .env actualizado con URL de Railway
- [ ] npm run build ejecutado
- [ ] Archivos subidos a Hostinger
- [ ] .htaccess en su lugar
- [ ] Login funciona
- [ ] API responde correctamente

### Firebase
- [ ] kioskito.click en dominios autorizados
- [ ] Popup de Google funciona
- [ ] Tokens se renuevan correctamente

---

## 🎉 Resultado Final

- ✅ Backend en Railway (rápido y confiable)
- ✅ Frontend en Hostinger (kioskito.click/PlayR)
- ✅ Base de datos en Neon (PostgreSQL)
- ✅ Firebase para autenticación
- ✅ Todo conectado y funcionando

---

## 📌 URLs Importantes

- **Frontend**: https://kioskito.click/PlayR
- **Backend**: https://playr-proyecto-production.up.railway.app
- **API Docs**: https://playr-proyecto-production.up.railway.app/docs
- **Health**: https://playr-proyecto-production.up.railway.app/health
- **Railway Dashboard**: https://railway.app/dashboard
- **Firebase Console**: https://console.firebase.google.com/

---

## 🔄 Actualizar Despliegue

### Backend
```bash
# Railway detecta cambios automáticamente
git add .
git commit -m "Update backend"
git push origin main
```

### Frontend
```powershell
cd frontend
npm run build
# Subir dist/ a Hostinger
```
