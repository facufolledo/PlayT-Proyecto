# 🔑 Usuario de Prueba - PlayR

## Credenciales para Login

```
📧 Email: demo@playr.com
👤 Username: demo
🔒 Contraseña: demo123
```

## Cómo usar

### Opción 1: Desde el Frontend (Recomendado)

1. **Asegúrate de que el backend esté corriendo:**
   ```bash
   cd backend
   python main.py
   ```

2. **Inicia el frontend:**
   ```bash
   cd frontend
   npm run dev
   ```

3. **Ve a la página de login:**
   - Abre `http://localhost:5173/login`

4. **Inicia sesión con:**
   - **Email**: `demo@playr.com`
   - **Contraseña**: `demo123`

5. **O también puedes usar:**
   - **Username**: `demo`
   - **Contraseña**: `demo123`

### Opción 2: Desde la API (Swagger)

1. **Ve a la documentación de la API:**
   - Abre `http://localhost:8000/docs`

2. **Encuentra el endpoint `/auth/login`**

3. **Haz clic en "Try it out"**

4. **Ingresa:**
   - `username`: `demo@playr.com` o `demo`
   - `password`: `demo123`

5. **Haz clic en "Execute"**

6. **Copia el `access_token` que recibes**

7. **Úsalo en otros endpoints:**
   - Haz clic en el botón "Authorize" (arriba a la derecha)
   - Ingresa: `Bearer <tu-access-token>`

## Datos del Usuario

- **Nombre completo**: Demo Usuario
- **Email**: demo@playr.com
- **Username**: demo
- **Rating inicial**: 1099
- **Categoría**: 7ma
- **Sexo**: Masculino
- **Ciudad**: Buenos Aires
- **País**: Argentina

## ⚠️ Nota sobre Firebase

Este usuario funciona con el sistema de autenticación tradicional (email/password) del backend. 

**NO necesitas Firebase** para usar este usuario. Funciona ahora mismo.

Cuando tu compañero te dé acceso a Firebase, podrás:
- Usar "Continuar con Google"
- Crear nuevos usuarios con Google Auth
- Este usuario seguirá funcionando también

## 🔄 Crear Otro Usuario de Prueba

Si quieres crear más usuarios, puedes:

1. **Desde la API:**
   - Usar el endpoint `POST /auth/register`
   - Completa todos los campos requeridos

2. **Ejecutar el script nuevamente:**
   ```bash
   cd backend
   python create_test_user.py
   ```
   (Nota: solo creará uno con email `demo@playr.com`, si ya existe no lo duplicará)

3. **Modificar el script:**
   - Edita `backend/create_test_user.py`
   - Cambia el email, nombre, etc.
   - Ejecuta nuevamente

## ✅ Verificar que Todo Funciona

1. Backend corriendo en `http://localhost:8000`
2. Frontend corriendo en `http://localhost:5173`
3. Ve a `http://localhost:5173/login`
4. Ingresa las credenciales de arriba
5. Deberías entrar al dashboard

## 🐛 Solución de Problemas

### "Usuario no encontrado"
- Verifica que el backend esté corriendo
- Verifica que el script se ejecutó correctamente
- Prueba acceder directamente a la API en `/docs`

### "Credenciales inválidas"
- Verifica que estés usando el email/username correcto
- Verifica que la contraseña sea `demo123`
- Verifica que no haya espacios extra

### "No se puede conectar al backend"
- Verifica que el backend esté corriendo
- Verifica que el puerto sea 8000
- Verifica la URL en `.env` del frontend: `VITE_API_URL=http://localhost:8000`

---

**¡Listo para usar! 🎾**



