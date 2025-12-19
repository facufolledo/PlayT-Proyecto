# 🔐 Variables de Entorno para Railway

## Copiar estas variables en Railway Dashboard

Ve a: **Variables** → **New Variable**

---

## 📊 Base de Datos (Neon)

```
DATABASE_URL
postgresql+pg8000://neondb_owner:npg_i2uqcNEZbk4M@ep-dawn-frost-ac67h4ke-pooler.sa-east-1.aws.neon.tech/neondb
```

---

## 🔒 Seguridad JWT

```
SECRET_KEY
tu_secret_key_super_segura_cambiar_esto_por_algo_aleatorio_largo
```

```
ALGORITHM
HS256
```

```
ACCESS_TOKEN_EXPIRE_MINUTES
30
```

---

## 🔥 Firebase

**Opción 1 - JSON completo (Recomendado):**

```
FIREBASE_CREDENTIALS_JSON
```

Valor: Copia TODO el contenido de `backend/firebase-credentials.json` en UNA SOLA LÍNEA (sin saltos de línea)

**Opción 2 - Ruta al archivo:**

```
FIREBASE_CREDENTIALS_PATH
./firebase-credentials.json
```

(Requiere subir el archivo al repo)

---

## 🌐 CORS

```
CORS_ORIGINS
["http://localhost:5173","http://localhost:5174","https://kioskito.click","https://www.kioskito.click"]
```

---

## ⚙️ Configuración del Servidor

```
HOST
0.0.0.0
```

```
PORT
8000
```

```
DEBUG
False
```

```
ENVIRONMENT
production
```

---

## 🗄️ Pool de Conexiones DB (IMPORTANTE para escalar)

```
DB_POOL_SIZE
5
```

```
DB_MAX_OVERFLOW
10
```

**Nota:** En Railway Hobby ($5/mes), estos valores son suficientes. Si escalás a un plan Pro o DB dedicada, podés subir a `DB_POOL_SIZE=10` y `DB_MAX_OVERFLOW=20`.

---

## 🎮 Configuración ELO

```
INITIAL_ELO_RATING
1000
```

```
K_FACTOR
32
```

```
MIN_K_FACTOR
16
```

```
MAX_K_FACTOR
48
```

---

## 📱 Información de la App

```
APP_NAME
PlayT API
```

```
APP_VERSION
1.0.0
```

---

## 🚀 Pasos para Configurar

### 1. En Railway Dashboard:
- Ve a tu servicio → **Variables**
- Click **New Variable**
- Copia cada variable de arriba

### 2. Firebase Credentials:
**Método recomendado (JSON):**
```bash
# En tu terminal local:
cat backend/firebase-credentials.json | jq -c
```
Copia el resultado (una sola línea) y pégalo en `FIREBASE_CREDENTIALS_JSON`

### 3. Generar SECRET_KEY seguro:
```bash
# En Python:
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 4. Actualizar CORS:
```
CORS_ORIGINS=["https://kioskito.click","https://www.kioskito.click","http://localhost:5173"]
```

---

## ✅ Checklist

- [ ] DATABASE_URL configurada
- [ ] SECRET_KEY generada y configurada
- [ ] FIREBASE_CREDENTIALS_JSON o FIREBASE_CREDENTIALS_PATH configurada
- [ ] CORS_ORIGINS actualizada con tu dominio (kioskito.click)
- [ ] ENVIRONMENT=production
- [ ] DB_POOL_SIZE y DB_MAX_OVERFLOW configurados
- [ ] Todas las demás variables copiadas
- [ ] Deploy exitoso en Railway
- [ ] Health check funcionando: `https://tu-app.up.railway.app/health`
- [ ] Pool status: `https://tu-app.up.railway.app/health/db`
- [ ] API Docs accesibles: `https://tu-app.up.railway.app/docs`

---

## 🔍 Verificar Configuración

Después del deploy, verifica:

```bash
# Health check
curl https://tu-app.up.railway.app/health

# Debería responder:
# {"status":"healthy","service":"PlayT API","database":"connected"}

# Ver estado del pool de conexiones
curl https://tu-app.up.railway.app/health/db

# Ver estado del caché
curl https://tu-app.up.railway.app/health/cache
```

---

## ⚠️ Notas Importantes

1. **SECRET_KEY**: NUNCA uses la misma que en desarrollo
2. **Firebase**: Asegúrate de que el JSON esté en UNA SOLA LÍNEA
3. **CORS**: Incluye TODOS los dominios desde donde accederás (frontend)
4. **DATABASE_URL**: Verifica que Neon permita conexiones desde cualquier IP (0.0.0.0/0)
5. **Railway Hobby ($5/mes)**: El servicio NO se duerme, está siempre activo

---

## 🐛 Troubleshooting

### Error: "Database connection failed"
- Verifica DATABASE_URL
- Verifica que Neon DB esté activo
- En Neon Dashboard → Settings → IP Allow → Permitir 0.0.0.0/0

### Error: "Firebase credentials invalid"
- Verifica que FIREBASE_CREDENTIALS_JSON esté en una sola línea
- Verifica que el JSON sea válido
- Prueba con FIREBASE_CREDENTIALS_PATH si el JSON no funciona

### Error: "CORS policy"
- Agrega el dominio de tu frontend a CORS_ORIGINS
- Incluye http:// o https:// según corresponda
- Incluye www y sin www si es necesario

### Error: "BrokenPipeError" o "network error"
- Verifica que DB_POOL_SIZE y DB_MAX_OVERFLOW estén configurados
- El pool_pre_ping=True debería manejar esto automáticamente
- Revisa `/health/db` para ver estado del pool

---

**¡Listo para producción en Railway!** 🚀
