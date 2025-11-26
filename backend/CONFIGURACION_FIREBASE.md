# 🔥 Configuración de Firebase Admin SDK en el Backend

## Paso 1: Instalar Firebase Admin SDK

```bash
cd backend
pip install firebase-admin
```

O si usas requirements.txt:
```bash
pip install -r requirements.txt
```

## Paso 2: Obtener Credenciales de Firebase

Necesitas descargar el archivo de credenciales de servicio de Firebase:

1. Ve a [Firebase Console](https://console.firebase.google.com/)
2. Selecciona tu proyecto
3. Ve a ⚙️ **Configuración del proyecto** → **Cuentas de servicio**
4. Haz clic en **"Generar nueva clave privada"**
5. Se descargará un archivo JSON con las credenciales
6. **IMPORTANTE**: Guarda este archivo de forma segura, nunca lo subas a Git

## Paso 3: Configurar Variables de Entorno

Tienes dos opciones:

### Opción A: Usar archivo de credenciales (Recomendado)

1. Coloca el archivo JSON descargado en una carpeta segura (por ejemplo, `backend/secrets/`)
2. Agrega al archivo `.env` del backend:

```env
FIREBASE_CREDENTIALS_PATH=/ruta/completa/al/archivo/firebase-credentials.json
```

Ejemplo:
```env
FIREBASE_CREDENTIALS_PATH=D:/Users/Facundo/Desktop/Proyecto/backend/secrets/firebase-credentials.json
```

### Opción B: Usar JSON como variable de entorno

1. Abre el archivo JSON descargado
2. Convierte todo el contenido en una sola línea
3. Agrega al archivo `.env` del backend:

```env
FIREBASE_CREDENTIALS_JSON='{"type":"service_account","project_id":"...","private_key_id":"...",...}'
```

## Paso 4: Agregar al .gitignore

Asegúrate de que el archivo `.gitignore` del backend incluya:

```
# Firebase credentials
firebase-credentials.json
secrets/
*.json
```

## Paso 5: Verificar Configuración

El backend intentará inicializar Firebase Admin SDK automáticamente cuando se use por primera vez.

Si todo está bien configurado, verás en los logs:
```
✅ Firebase Admin inicializado con archivo de credenciales
```

Si hay problemas:
```
⚠️  Firebase Admin no inicializado. Configura FIREBASE_CREDENTIALS_PATH o FIREBASE_CREDENTIALS_JSON
```

## Uso en el Backend

El backend ahora soporta ambos sistemas de autenticación:

1. **JWT tradicional**: Para login con email/password
2. **Firebase tokens**: Para autenticación con Google

### Endpoints disponibles:

- `POST /auth/login` - Login tradicional con email/password
- `POST /auth/register` - Registro tradicional
- `POST /auth/firebase-auth` - Verificar token de Firebase
- `GET /auth/me` - Obtener usuario actual (soporta ambos tipos de tokens)
- `GET /auth/categorias` - Obtener categorías disponibles

### Flujo de autenticación con Firebase:

1. Usuario se autentica con Google en el frontend
2. Frontend obtiene token de Firebase
3. Frontend envía token a `/auth/firebase-auth` para verificar usuario
4. O directamente usa el token en el header `Authorization: Bearer <firebase_token>`
5. El backend valida automáticamente el token y retorna el usuario

## Estructura del Token

Los tokens de Firebase contienen:
- `uid`: ID único del usuario en Firebase
- `email`: Email del usuario
- `name`: Nombre del usuario (si está disponible)

El backend busca usuarios por email, por lo que el email en Firebase debe coincidir con el email registrado en la base de datos.

## Notas de Seguridad

1. **NUNCA** subas el archivo de credenciales a Git
2. **NUNCA** compartas el archivo de credenciales públicamente
3. Usa variables de entorno para las rutas de los archivos
4. En producción, usa un sistema de gestión de secretos (AWS Secrets Manager, Azure Key Vault, etc.)

## Testing

Puedes probar el endpoint de Firebase con:

```bash
curl -X POST "http://localhost:8000/auth/firebase-auth" \
  -H "Content-Type: application/json" \
  -d '{"firebase_token": "tu-token-de-firebase-aqui"}'
```

O usar el token directamente en otros endpoints:

```bash
curl -X GET "http://localhost:8000/auth/me" \
  -H "Authorization: Bearer tu-token-de-firebase-aqui"
```

