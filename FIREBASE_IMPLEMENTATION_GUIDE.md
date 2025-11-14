# 🔥 GUÍA DE IMPLEMENTACIÓN FIREBASE AUTH

## 📋 RESUMEN

Esta guía explica cómo implementar Firebase Authentication con Google Sign-In y el flujo de completar perfil en PlayR.

---

## 🎯 FLUJO COMPLETO

```
1. Usuario hace click en "Iniciar con Google"
   ↓
2. Firebase Auth → Login con Google
   ↓
3. ¿Perfil completo en BD?
   ├─ SÍ → Ir a /dashboard
   └─ NO → Ir a /completar-perfil
          ↓
       4. Usuario completa datos faltantes
          ↓
       5. Guardar en backend → Ir a /dashboard
```

---

## 📦 PASO 1: INSTALAR DEPENDENCIAS

```bash
cd frontend
npm install firebase
```

---

## 🔧 PASO 2: CONFIGURAR FIREBASE CONSOLE

1. Ir a [Firebase Console](https://console.firebase.google.com/)
2. Crear nuevo proyecto o usar existente
3. Activar **Authentication** → **Sign-in method** → **Google**
4. Copiar las credenciales del proyecto

---

## 🔑 PASO 3: CONFIGURAR VARIABLES DE ENTORNO

Crear archivo `frontend/.env`:

```env
# API Backend
VITE_API_URL=http://localhost:8000/api

# Firebase Configuration
VITE_FIREBASE_API_KEY=AIzaSyXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
VITE_FIREBASE_AUTH_DOMAIN=tu-proyecto.firebaseapp.com
VITE_FIREBASE_PROJECT_ID=tu-proyecto-id
VITE_FIREBASE_STORAGE_BUCKET=tu-proyecto.appspot.com
VITE_FIREBASE_MESSAGING_SENDER_ID=123456789012
VITE_FIREBASE_APP_ID=1:123456789012:web:xxxxxxxxxxxxx
```

---

## 📁 ARCHIVOS CREADOS

### ✅ Ya Creados:

1. **`frontend/src/config/firebase.ts`** - Configuración de Firebase
2. **`frontend/src/services/auth.service.ts`** - Servicio de autenticación
3. **`frontend/src/pages/CompletarPerfil.tsx`** - Página para completar datos
4. **`frontend/.env.example`** - Template de variables

---

## 🔨 PASO 4: MODIFICAR ARCHIVOS EXISTENTES

### A. Actualizar `frontend/src/pages/Login.tsx`

Agregar botón de Google después del formulario:

```tsx
// Importar al inicio
import { authService } from '../services/auth.service';

// Agregar función para login con Google
const handleGoogleLogin = async () => {
  try {
    await authService.loginWithGoogle();
    
    // Verificar si el perfil está completo
    const perfilCompleto = await authService.checkProfileComplete();
    
    if (perfilCompleto) {
      navigate('/dashboard');
    } else {
      navigate('/completar-perfil');
    }
  } catch (err: any) {
    setError(err.message || 'Error al iniciar sesión con Google');
  }
};

// Agregar botón DESPUÉS del formulario y ANTES de los links
<div className="mt-6">
  <div className="relative">
    <div className="absolute inset-0 flex items-center">
      <div className="w-full border-t border-cardBorder"></div>
    </div>
    <div className="relative flex justify-center text-sm">
      <span className="px-2 bg-cardBg text-textSecondary">O continuar con</span>
    </div>
  </div>

  <Button
    type="button"
    variant="secondary"
    className="w-full mt-4 flex items-center justify-center gap-2"
    onClick={handleGoogleLogin}
  >
    <svg className="w-5 h-5" viewBox="0 0 24 24">
      <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
      <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
      <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
      <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
    </svg>
    Continuar con Google
  </Button>
</div>
```

### B. Actualizar `frontend/src/pages/Register.tsx`

Similar al Login, agregar el mismo botón de Google.

### C. Actualizar `frontend/src/App.tsx`

Agregar la ruta de completar perfil:

```tsx
// Importar
import CompletarPerfil from './pages/CompletarPerfil';

// Agregar ruta DESPUÉS de /register
<Route path="/completar-perfil" element={<CompletarPerfil />} />
```

### D. Actualizar `frontend/src/context/AuthContext.tsx`

Integrar con Firebase:

```tsx
// Importar al inicio
import { auth } from '../config/firebase';
import { onAuthStateChanged } from 'firebase/auth';
import { authService } from '../services/auth.service';

// En el useEffect inicial, escuchar cambios de Firebase
useEffect(() => {
  const unsubscribe = onAuthStateChanged(auth, async (firebaseUser) => {
    if (firebaseUser) {
      // Usuario logueado con Firebase
      // Verificar si tiene perfil completo en tu BD
      const perfilCompleto = await authService.checkProfileComplete();
      
      if (perfilCompleto) {
        // Cargar datos del usuario desde tu backend
        const token = await firebaseUser.getIdToken();
        const response = await fetch(`${import.meta.env.VITE_API_URL}/usuarios/me`, {
          headers: { 'Authorization': `Bearer ${token}` }
        });
        const userData = await response.json();
        setUsuario(userData);
      }
    } else {
      setUsuario(null);
    }
    setIsLoading(false);
  });

  return () => unsubscribe();
}, []);

// Actualizar función login
const login = async (email: string, password: string) => {
  setIsLoading(true);
  try {
    await authService.loginWithEmail(email, password);
  } catch (error) {
    throw error;
  } finally {
    setIsLoading(false);
  }
};

// Actualizar función logout
const logout = async () => {
  await authService.logout();
  setUsuario(null);
};
```

---

## 🗄️ PASO 5: ESTRUCTURA DE BASE DE DATOS

### Tabla `jugadores`:

```sql
CREATE TABLE jugadores (
  id SERIAL PRIMARY KEY,
  uid_firebase VARCHAR(255) UNIQUE NOT NULL,
  email VARCHAR(255) UNIQUE NOT NULL,
  nombre VARCHAR(100) NOT NULL,
  apellido VARCHAR(100) NOT NULL,
  dni VARCHAR(20) UNIQUE NOT NULL,
  fecha_nacimiento DATE NOT NULL,
  genero VARCHAR(20) NOT NULL CHECK (genero IN ('masculino', 'femenino')),
  categoria_inicial VARCHAR(20) NOT NULL,
  mano_habil VARCHAR(20) CHECK (mano_habil IN ('derecha', 'zurda')),
  posicion_preferida VARCHAR(20) CHECK (posicion_preferida IN ('drive', 'reves', 'indiferente')),
  telefono VARCHAR(50),
  ciudad VARCHAR(100),
  foto_url TEXT,
  rating INT DEFAULT 1000,
  rol VARCHAR(20) DEFAULT 'jugador' CHECK (rol IN ('jugador', 'admin')),
  fecha_registro TIMESTAMP DEFAULT NOW(),
  activo BOOLEAN DEFAULT TRUE
);
```

---

## 🔐 PASO 6: BACKEND - ENDPOINTS NECESARIOS

### A. Middleware de Autenticación (FastAPI)

```python
# backend/middleware/auth.py
import firebase_admin
from firebase_admin import credentials, auth
from fastapi import Depends, HTTPException, Header

# Inicializar Firebase Admin
cred = credentials.Certificate("firebase_key.json")
firebase_admin.initialize_app(cred)

async def verify_firebase_token(authorization: str = Header(...)):
    try:
        scheme, token = authorization.split()
        if scheme.lower() != 'bearer':
            raise HTTPException(status_code=401, detail="Invalid authentication scheme")
        
        decoded_token = auth.verify_id_token(token)
        return decoded_token
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid token")
```

### B. Endpoint: Completar Perfil

```python
# backend/routers/usuarios.py
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from datetime import date

router = APIRouter()

class PerfilCompleto(BaseModel):
    nombre: str
    apellido: str
    dni: str
    fecha_nacimiento: date
    genero: str
    categoria_inicial: str
    mano_habil: str | None = None
    posicion_preferida: str | None = None
    telefono: str | None = None
    ciudad: str | None = None

@router.post("/completar-perfil")
async def completar_perfil(
    datos: PerfilCompleto,
    user = Depends(verify_firebase_token)
):
    uid = user["uid"]
    email = user["email"]
    foto = user.get("picture", "")
    
    # Insertar en base de datos
    query = """
    INSERT INTO jugadores (
        uid_firebase, email, nombre, apellido, dni,
        fecha_nacimiento, genero, categoria_inicial,
        mano_habil, posicion_preferida, telefono, ciudad, foto_url
    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    ON CONFLICT (uid_firebase) DO UPDATE SET
        nombre = EXCLUDED.nombre,
        apellido = EXCLUDED.apellido,
        dni = EXCLUDED.dni,
        fecha_nacimiento = EXCLUDED.fecha_nacimiento,
        genero = EXCLUDED.genero,
        categoria_inicial = EXCLUDED.categoria_inicial,
        mano_habil = EXCLUDED.mano_habil,
        posicion_preferida = EXCLUDED.posicion_preferida,
        telefono = EXCLUDED.telefono,
        ciudad = EXCLUDED.ciudad
    """
    
    db.execute(query, (
        uid, email, datos.nombre, datos.apellido, datos.dni,
        datos.fecha_nacimiento, datos.genero, datos.categoria_inicial,
        datos.mano_habil, datos.posicion_preferida,
        datos.telefono, datos.ciudad, foto
    ))
    
    return {"status": "ok", "message": "Perfil completado"}
```

### C. Endpoint: Obtener Usuario Actual

```python
@router.get("/me")
async def get_current_user(user = Depends(verify_firebase_token)):
    uid = user["uid"]
    
    query = "SELECT * FROM jugadores WHERE uid_firebase = %s"
    result = db.fetchone(query, (uid,))
    
    if not result:
        return {"categoria_inicial": None}  # Perfil incompleto
    
    return {
        "id": result["id"],
        "nombre": result["nombre"],
        "apellido": result["apellido"],
        "email": result["email"],
        "categoria_inicial": result["categoria_inicial"],
        "genero": result["genero"],
        "rating": result["rating"],
        "rol": result["rol"],
        # ... otros campos
    }
```

---

## ✅ CHECKLIST DE IMPLEMENTACIÓN

### Frontend:
- [ ] Instalar Firebase (`npm install firebase`)
- [ ] Configurar variables de entorno (`.env`)
- [ ] Agregar botón de Google en Login
- [ ] Agregar botón de Google en Register
- [ ] Agregar ruta `/completar-perfil` en App.tsx
- [ ] Integrar Firebase en AuthContext
- [ ] Probar flujo completo

### Backend:
- [ ] Instalar Firebase Admin SDK (`pip install firebase-admin`)
- [ ] Descargar credenciales de Firebase Console
- [ ] Crear middleware de autenticación
- [ ] Crear endpoint `/completar-perfil`
- [ ] Crear endpoint `/me`
- [ ] Crear tabla `jugadores` en PostgreSQL
- [ ] Probar endpoints con Postman

---

## 🧪 TESTING

### Probar Login con Google:
1. Click en "Continuar con Google"
2. Seleccionar cuenta de Google
3. Debe redirigir a `/completar-perfil`
4. Completar formulario
5. Debe redirigir a `/dashboard`

### Probar Login Subsecuente:
1. Cerrar sesión
2. Login con Google nuevamente
3. Debe ir directo a `/dashboard` (sin pedir datos)

---

## 📝 NOTAS IMPORTANTES

1. **Seguridad**: Nunca commitear el archivo `.env` ni las credenciales de Firebase
2. **Token**: El token de Firebase expira cada 1 hora, renovarlo automáticamente
3. **Validación**: Validar todos los datos en backend antes de guardar
4. **DNI**: Debe ser único en la base de datos
5. **Categoría**: Usar para calcular rating inicial (ver documentación ELO)

---

## 🎯 DATOS REQUERIDOS

### Obligatorios:
- ✅ Nombre
- ✅ Apellido
- ✅ DNI
- ✅ Fecha de Nacimiento
- ✅ Género (masculino/femenino)
- ✅ Categoría Inicial (8va-Libre)

### Opcionales:
- Mano Hábil (derecha/zurda)
- Posición Preferida (drive/revés/indiferente)
- Teléfono
- Ciudad

---

## 🚀 PRÓXIMOS PASOS

Una vez implementado Firebase Auth:
1. Implementar refresh de tokens
2. Agregar recuperación de contraseña
3. Agregar verificación de email
4. Implementar roles y permisos
5. Agregar foto de perfil con Firebase Storage

---

**¡El frontend está listo para Firebase! Solo falta configurar las credenciales y el backend.** 🎉
