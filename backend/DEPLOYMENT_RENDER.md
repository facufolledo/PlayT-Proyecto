# 🚀 Deployment Backend en Render

## Paso 1: Preparar el Repositorio

### 1.1 Subir a GitHub
```bash
# Si aún no tienes repo
git init
git add .
git commit -m "Preparar para deployment"
git branch -M main
git remote add origin https://github.com/tu-usuario/playr-backend.git
git push -u origin main
```

---

## Paso 2: Configurar Render

### 2.1 Crear Cuenta
1. Ir a https://render.com
2. Sign up con GitHub
3. Autorizar acceso a repositorios

### 2.2 Crear Web Service
1. Dashboard > "New +" > "Web Service"
2. Conectar repositorio de GitHub
3. Seleccionar el repo de PlayR

### 2.3 Configuración del Service
```
Name: playr-api
Region: Oregon (o el más cercano)
Branch: main
Root Directory: backend (si está en subcarpeta)
Runtime: Python 3
Build Command: pip install -r requirements.txt
Start Command: uvicorn src.main:app --host 0.0.0.0 --port $PORT
Plan: Free
```

---

## Paso 3: Variables de Entorno

### 3.1 En Render Dashboard
Ir a: Environment > Add Environment Variable

```env
# Base de Datos (Neon)
DATABASE_URL=postgresql+pg8000://neondb_owner:TU_PASSWORD@ep-dawn-frost-ac67h4ke-pooler.sa-east-1.aws.neon.tech/neondb

# Seguridad
SECRET_KEY=tu_secret_key_super_segura_cambiar_esto
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Firebase
FIREBASE_CREDENTIALS_PATH=./secrets/firebase-credentials.json

# CORS (Actualizar con tu dominio de Hostinger)
CORS_ORIGINS=["https://tudominio.com","https://www.tudominio.com"]

# Configuración
HOST=0.0.0.0
PORT=10000
DEBUG=False

# ELO
INITIAL_ELO_RATING=1200
K_FACTOR=32
MIN_K_FACTOR=16
MAX_K_FACTOR=48

# App Info
APP_NAME=PlayT API
APP_VERSION=1.0.0
```

### 3.2 Firebase Credentials
**Opción 1 - Variable de Entorno (Recomendado):**
```bash
# Convertir firebase-credentials.json a string
cat secrets/firebase-credentials.json | jq -c

# Agregar como variable:
FIREBASE_CREDENTIALS_JSON={"type":"service_account",...}
```

Luego actualizar el código para leer de variable:
```python
import json
import os

firebase_creds = os.getenv('FIREBASE_CREDENTIALS_JSON')
if firebase_creds:
    cred = credentials.Certificate(json.loads(firebase_creds))
```

**Opción 2 - Archivo en Repo (Menos seguro):**
- Subir `secrets/firebase-credentials.json` al repo
- Asegurar que `.gitignore` NO lo ignore para deployment

---

## Paso 4: Deploy

### 4.1 Primer Deploy
1. Click "Create Web Service"
2. Render automáticamente:
   - Clona el repo
   - Instala dependencias
   - Ejecuta el comando de inicio
   - Asigna URL: `https://playr-api.onrender.com`

### 4.2 Verificar Deploy
```bash
# Health check
curl https://playr-api.onrender.com/health

# API Docs
# Abrir: https://playr-api.onrender.com/docs
```

---

## Paso 5: Configurar Base de Datos

### 5.1 Ejecutar Migraciones
**Opción 1 - Desde local:**
```bash
# Actualizar .env con URL de producción
DATABASE_URL=postgresql+pg8000://...

# Ejecutar migraciones
python run_migrations.py
```

**Opción 2 - Shell de Render:**
1. Dashboard > Shell
2. Ejecutar:
```bash
python run_migrations.py
```

---

## Paso 6: Configurar WebSockets

### 6.1 Verificar Soporte
Render soporta WebSockets automáticamente en el plan Free.

### 6.2 URL de WebSocket
```
wss://playr-api.onrender.com/ws/salas/{sala_id}
```

---

## Paso 7: Monitoreo

### 7.1 Logs
- Dashboard > Logs
- Ver logs en tiempo real
- Filtrar por errores

### 7.2 Métricas
- Dashboard > Metrics
- CPU, Memory, Request count
- Response times

### 7.3 Health Checks
Render hace ping cada 5 minutos a `/health`

---

## Paso 8: Auto-Deploy

### 8.1 Configurar
Por defecto, Render hace auto-deploy en cada push a `main`

### 8.2 Desactivar (opcional)
Settings > Build & Deploy > Auto-Deploy: Off

---

## Paso 9: Custom Domain (Opcional)

### 9.1 Agregar Dominio
1. Settings > Custom Domains
2. Add Custom Domain: `api.tudominio.com`
3. Agregar CNAME en tu DNS:
```
CNAME api.tudominio.com -> playr-api.onrender.com
```

---

## Paso 10: Actualizar Frontend

### 10.1 Variable de Entorno
En Hostinger, actualizar:
```env
VITE_API_URL=https://playr-api.onrender.com
```

### 10.2 Rebuild Frontend
```bash
cd frontend
npm run build
# Subir dist/ a Hostinger
```

---

## 🔧 Troubleshooting

### Error: Module not found
```bash
# Verificar requirements.txt
pip freeze > requirements.txt
git add requirements.txt
git commit -m "Update requirements"
git push
```

### Error: Database connection
- Verificar DATABASE_URL en variables de entorno
- Verificar que Neon DB esté activo
- Verificar IP whitelist en Neon (permitir todas: 0.0.0.0/0)

### Error: Firebase credentials
- Verificar FIREBASE_CREDENTIALS_JSON o archivo
- Verificar permisos del service account

### Service se duerme (Free tier)
- Render duerme servicios inactivos después de 15 min
- Primera request tarda ~30s en despertar
- Solución: Upgrade a plan Starter ($7/mes) o usar cron job

---

## 💰 Costos

### Free Tier
- ✅ 750 horas/mes
- ✅ 512 MB RAM
- ✅ Shared CPU
- ⚠️ Se duerme después de 15 min inactivo
- ⚠️ 100 GB bandwidth/mes

### Starter ($7/mes)
- ✅ Always on
- ✅ 512 MB RAM
- ✅ Shared CPU
- ✅ 100 GB bandwidth/mes

### Standard ($25/mes)
- ✅ 2 GB RAM
- ✅ 1 CPU
- ✅ 400 GB bandwidth/mes

---

## 📊 Checklist Final

- [ ] Repo en GitHub
- [ ] Service creado en Render
- [ ] Variables de entorno configuradas
- [ ] Firebase credentials configuradas
- [ ] Migraciones ejecutadas
- [ ] Health check funcionando
- [ ] API Docs accesibles
- [ ] WebSockets funcionando
- [ ] CORS configurado con dominio de Hostinger
- [ ] Frontend actualizado con nueva API URL

---

## 🎯 URL Final

```
API: https://playr-api.onrender.com
Docs: https://playr-api.onrender.com/docs
Health: https://playr-api.onrender.com/health
WebSocket: wss://playr-api.onrender.com/ws/salas/{id}
```

---

**¡Backend listo para producción!** 🚀
