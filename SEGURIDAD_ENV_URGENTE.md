# 🚨 ACCIÓN URGENTE: Credenciales Expuestas

## Problema
El archivo `.env` con credenciales de Firebase fue subido al repositorio público de GitHub.

## Acciones Tomadas
1. ✅ Creado `.gitignore` para prevenir futuros commits de archivos sensibles
2. ✅ Eliminado `.env` del tracking de Git
3. ✅ Creados archivos `.env.example` como plantillas

## 🔴 ACCIONES REQUERIDAS INMEDIATAMENTE

### 1. Rotar Credenciales de Firebase
Las credenciales actuales están comprometidas. Debes:

1. **Ir a Firebase Console**: https://console.firebase.google.com
2. **Seleccionar tu proyecto**: playr-3f394
3. **Project Settings > Service Accounts**
4. **Generar nueva clave privada**
5. **Actualizar en Railway** la variable `FIREBASE_CREDENTIALS_JSON`

### 2. Regenerar API Key de Firebase
1. **Firebase Console > Project Settings > General**
2. **Web API Key** - considera regenerarla si es posible
3. **Actualizar en tu `.env` local** (no subir a Git)

### 3. Verificar Reglas de Seguridad
1. **Firebase Console > Firestore Database > Rules**
2. **Firebase Console > Storage > Rules**
3. Asegurar que las reglas no permitan acceso público sin autenticación

### 4. Monitorear Uso
1. **Firebase Console > Usage**
2. Revisar si hay actividad sospechosa
3. Configurar alertas de uso

## Archivos que NO deben estar en Git
- `.env`
- `.env.local`
- `.env.production`
- `backend/.env`
- `backend/.env.railway`
- Cualquier archivo con credenciales

## Archivos que SÍ pueden estar en Git
- `.env.example` (plantilla sin valores reales)
- `.gitignore`

## Próximos Pasos
1. Hacer commit de estos cambios
2. Push al repositorio
3. Rotar credenciales de Firebase
4. Actualizar variables en Railway
5. Crear nuevo `.env` local con las nuevas credenciales (NO subirlo a Git)
