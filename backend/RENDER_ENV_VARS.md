# 🔐 Variables de Entorno para Render

## Copiar estas variables en Render Dashboard

Ve a: **Environment** → **Add Environment Variable**

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
["http://localhost:5173","http://localhost:5174","https://tudominio.com","https://www.tudominio.com"]
```

**IMPORTANTE:** Actualiza con tu dominio real de Hostinger cuando lo tengas.

---

## ⚙️ Configuración del Servidor

```
HOST
0.0.0.0
```

```
PORT
10000
```

```
DEBUG
False
```

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
Drive+ API
```

```
APP_VERSION
1.0.0
```

---

## 🚀 Pasos para Configurar

### 1. En Render Dashboard:
- Ve a tu servicio → **Environment**
- Click **Add Environment Variable**
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
Cuando tengas tu dominio de Hostinger, actualiza:
```
CORS_ORIGINS=["https://tudominio.com","https://www.tudominio.com","http://localhost:5173"]
```

---

## ✅ Checklist

- [ ] DATABASE_URL configurada
- [ ] SECRET_KEY generada y configurada
- [ ] FIREBASE_CREDENTIALS_JSON o FIREBASE_CREDENTIALS_PATH configurada
- [ ] CORS_ORIGINS actualizada con tu dominio
- [ ] Todas las demás variables copiadas
- [ ] Deploy exitoso en Render
- [ ] Health check funcionando: `https://tu-app.onrender.com/health`
- [ ] API Docs accesibles: `https://tu-app.onrender.com/docs`

---

## 🔍 Verificar Configuración

Después del deploy, verifica:

```bash
# Health check
curl https://tu-app.onrender.com/health

# Debería responder:
# {"status":"healthy","service":"PlayT API","database":"connected"}
```

---

## ⚠️ Notas Importantes

1. **SECRET_KEY**: NUNCA uses la misma que en desarrollo
2. **Firebase**: Asegúrate de que el JSON esté en UNA SOLA LÍNEA
3. **CORS**: Incluye TODOS los dominios desde donde accederás (frontend)
4. **DATABASE_URL**: Verifica que Neon permita conexiones desde cualquier IP (0.0.0.0/0)
5. **Free Tier**: El servicio se dormirá después de 15 min de inactividad

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

---

**¡Listo para producción!** 🚀
