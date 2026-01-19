# ✅ Checklist de Limpieza Pre-Lanzamiento

## 🎯 Objetivo
Limpiar todos los datos de prueba y dejar la aplicación lista para producción sin romper funcionalidad.

---

## 📋 PASO 1: Backup de Seguridad

### ⚠️ CRÍTICO: Hacer backup ANTES de limpiar

```bash
# En Railway (Producción)
# 1. Ir a tu proyecto en Railway
# 2. Click en PostgreSQL
# 3. Click en "Backups" 
# 4. Click en "Create Backup"
# O usar pg_dump si tienes acceso directo
```

**¿Por qué?** Por si algo sale mal, puedes restaurar.

---

## 📋 PASO 2: Ejecutar Script de Limpieza

### Opción A: Limpiar Base de Datos de Producción (Railway)

```bash
cd backend

# Asegúrate de tener el .env.production configurado
python limpiar_datos_prelanzamiento.py
```

**El script te pedirá 3 confirmaciones para evitar accidentes.**

### ¿Qué borra el script?

- ❌ **Usuarios**: Todos los usuarios de prueba
- ❌ **Salas**: Todas las salas creadas
- ❌ **Partidos**: Todos los partidos jugados
- ❌ **Torneos**: Todos los torneos (incluido el Weekend)
- ❌ **Parejas**: Todas las inscripciones
- ❌ **Zonas**: Todas las zonas de torneos
- ❌ **Historial ELO**: Todo el historial de cambios
- ❌ **Confirmaciones**: Todas las confirmaciones de parejas
- ❌ **Enfrentamientos**: Todo el historial de enfrentamientos

### ✅ ¿Qué NO borra?

- ✅ **Estructura de tablas**: Todas las tablas siguen existiendo
- ✅ **Categorías del sistema**: Las 6 categorías (7ma, 6ta, 5ta, etc.)
- ✅ **Migraciones**: El historial de migraciones
- ✅ **Configuraciones**: Variables de entorno, CORS, etc.

---

## 📋 PASO 3: Verificar que Todo Funciona

### 3.1 Verificar Backend

```bash
# Probar que el backend arranca sin errores
cd backend
python -m uvicorn main:app --reload
```

**Verificar en el navegador:**
- ✅ `http://localhost:8000/health` → Debe responder OK
- ✅ `http://localhost:8000/docs` → Swagger debe cargar

### 3.2 Verificar Frontend

```bash
cd frontend
npm run dev
```

**Verificar en el navegador:**
- ✅ La app carga sin errores
- ✅ Puedes registrarte (crear nuevo usuario)
- ✅ Puedes iniciar sesión
- ✅ Las categorías aparecen correctamente

### 3.3 Probar Flujos Críticos

1. **Registro de Usuario**
   - ✅ Crear cuenta nueva
   - ✅ Completar perfil
   - ✅ Ver que el rating inicial es 1500

2. **Crear Sala**
   - ✅ Crear una sala de prueba
   - ✅ Unirse con código
   - ✅ Asignar equipos
   - ✅ Iniciar partido

3. **Crear Torneo**
   - ✅ Crear torneo de prueba
   - ✅ Agregar categorías
   - ✅ Inscribir pareja
   - ✅ Generar fixture

---

## 📋 PASO 4: Limpiar Archivos de Prueba (Opcional)

### Archivos que puedes borrar (NO afectan funcionalidad):

```bash
# Scripts de prueba y debug
backend/test_*.py
backend/debug_*.py
backend/crear_torneo_*.py (excepto los que uses)
backend/verificar_*.py

# Documentación de desarrollo
backend/*_COMPLETO.md
backend/*_IMPLEMENTADO.md
backend/SOLUCION_*.md
backend/FIX_*.py
```

**⚠️ NO BORRES:**
- `backend/main.py`
- `backend/requirements.txt`
- `backend/src/` (toda la carpeta)
- `backend/migrations_*.sql`
- `backend/.env.production`

---

## 📋 PASO 5: Configurar Torneo Real

### Crear el Torneo de Lanzamiento

```bash
# Editar y ejecutar
python backend/crear_torneo_lanzamiento.py
```

O crear manualmente desde el frontend:
1. Login como admin
2. Ir a "Torneos" → "Crear Torneo"
3. Configurar fechas reales
4. Agregar categorías necesarias
5. Configurar horarios disponibles
6. Agregar canchas

---

## 📋 PASO 6: Verificaciones Finales

### 6.1 Variables de Entorno en Railway

Verificar que estén configuradas:
- ✅ `DATABASE_URL`
- ✅ `FIREBASE_CREDENTIALS_JSON`
- ✅ `CORS_ORIGINS` (incluye drive-plus.com.ar)
- ✅ `SECRET_KEY`

### 6.2 CORS en Producción

Verificar en `backend/main.py`:
```python
origins = [
    "http://localhost:3000",
    "http://localhost:5173",
    "https://drive-plus.com.ar",
    "https://www.drive-plus.com.ar"
]
```

### 6.3 Firebase Storage

- ✅ CORS configurado para fotos de perfil
- ✅ Reglas de seguridad activas

### 6.4 Frontend en Hostinger

- ✅ Build actualizado (`npm run build`)
- ✅ Archivos subidos a `public_html/PlayR/`
- ✅ `.htaccess` configurado para SPA

---

## 📋 PASO 7: Monitoreo Post-Lanzamiento

### Primeras 24 horas

- 📊 Monitorear logs en Railway
- 📊 Verificar que los usuarios pueden registrarse
- 📊 Verificar que las salas funcionan
- 📊 Verificar que los torneos funcionan
- 📊 Revisar errores en Sentry (si está configurado)

### Métricas a observar

- 👥 Número de registros
- 🎮 Salas creadas
- 🏆 Inscripciones a torneos
- ⚠️ Errores 500
- 🐛 Bugs reportados

---

## 🚨 Plan de Contingencia

### Si algo sale mal:

1. **Restaurar backup de Railway**
   - Ir a Railway → PostgreSQL → Backups
   - Seleccionar backup pre-limpieza
   - Click en "Restore"

2. **Rollback de código**
   ```bash
   git log  # Ver commits
   git revert <commit-hash>  # Revertir cambio específico
   ```

3. **Contacto de emergencia**
   - Tener acceso a Railway
   - Tener acceso a Hostinger
   - Tener acceso a Firebase Console

---

## ✅ Checklist Final

Antes de anunciar el lanzamiento:

- [ ] Backup de base de datos creado
- [ ] Script de limpieza ejecutado exitosamente
- [ ] Backend funciona sin errores
- [ ] Frontend funciona sin errores
- [ ] Registro de usuarios funciona
- [ ] Creación de salas funciona
- [ ] Creación de torneos funciona
- [ ] CORS configurado correctamente
- [ ] Variables de entorno verificadas
- [ ] Torneo real creado (si aplica)
- [ ] Monitoreo configurado
- [ ] Plan de contingencia listo

---

## 🎉 ¡Listo para Lanzar!

Una vez completado todo:
1. Hacer anuncio oficial
2. Compartir link: https://drive-plus.com.ar
3. Monitorear primeras horas
4. Estar disponible para soporte

**¡Éxito con el lanzamiento! 🚀**
