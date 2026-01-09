# Solución: Error "Method Not Allowed" al crear torneo

## Problema
Al intentar crear un torneo desde el frontend, aparece el error:
```
Method Not Allowed
```

## Diagnóstico paso a paso

### 1. Verificar que el servidor backend esté corriendo
```bash
cd backend
python main.py
```

### 2. Probar endpoints básicos
```bash
# Endpoint simple
curl http://localhost:8000/torneos/test-simple

# Listar torneos
curl http://localhost:8000/torneos

# Health check
curl http://localhost:8000/health
```

### 3. Probar creación con curl
```bash
# Sin autenticación (debería dar 401)
curl -X POST http://localhost:8000/torneos \
  -H "Content-Type: application/json" \
  -d '{"nombre":"Test","categoria":"5ta","fecha_inicio":"2026-01-15","fecha_fin":"2026-01-22"}'

# Con token (reemplazar TOKEN)
curl -X POST http://localhost:8000/torneos \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer TOKEN" \
  -d '{"nombre":"Test","categoria":"5ta","fecha_inicio":"2026-01-15","fecha_fin":"2026-01-22"}'
```

### 4. Usar script de diagnóstico
```bash
python test_crear_torneo.py
```

## Posibles causas y soluciones

### 1. Router no incluido en main.py
**Verificar:** `DrivePlus/backend/main.py`
```python
from src.controllers.torneo_controller import router as torneo_router
app.include_router(torneo_router)
```

### 2. Conflicto de rutas
**Problema:** Rutas que se solapan
```python
# ❌ Problemático
@router.get("/")
@router.get("")
@router.post("/")

# ✅ Correcto
@router.get("/")
@router.post("/")
```

### 3. Orden de rutas incorrecto
**Problema:** Rutas específicas después de genéricas
```python
# ❌ Problemático
@router.get("/{torneo_id}")  # Captura todo
@router.get("/test-simple")  # Nunca se alcanza

# ✅ Correcto
@router.get("/test-simple")  # Específica primero
@router.get("/{torneo_id}")  # Genérica después
```

### 4. Problema de CORS
**Verificar:** Headers CORS en respuesta OPTIONS
```bash
curl -X OPTIONS http://localhost:8000/torneos \
  -H "Origin: http://localhost:5174" \
  -H "Access-Control-Request-Method: POST" \
  -v
```

### 5. Middleware bloqueando
**Verificar:** Logs del servidor para ver qué middleware procesa la request

### 6. Problema de autenticación
**Verificar:** Token válido en localStorage
```javascript
console.log('Token:', localStorage.getItem('firebase_token'));
```

## Soluciones implementadas

### 1. Endpoints de debugging agregados
```python
@router.get("/test-auth")
def test_auth(current_user: Usuario = Depends(get_current_user)):
    return {"status": "ok", "user_id": current_user.id_usuario}

@router.post("/test-create")
def test_create(data: dict, current_user: Usuario = Depends(get_current_user)):
    return {"status": "ok", "data_received": data}
```

### 2. Logging mejorado en frontend
```typescript
async crearTorneo(data: TorneoCreate): Promise<Torneo> {
  console.log('🔍 Datos a enviar:', data);
  console.log('🔍 Headers:', this.getAuthHeaders());
  // ... resto del código
}
```

### 3. Validación previa en modal
```typescript
// 1. Probar autenticación
await torneoService.testAuth();

// 2. Probar envío de datos
await torneoService.testCreate(torneoData);

// 3. Crear torneo real
const nuevoTorneo = await crearTorneo(torneoData);
```

## Pasos para resolver

### Paso 1: Verificar servidor
1. Asegurar que el backend esté corriendo en puerto 8000
2. Verificar que no hay errores en los logs del servidor
3. Probar endpoint simple: `curl http://localhost:8000/torneos/test-simple`

### Paso 2: Verificar autenticación
1. Abrir DevTools → Console
2. Verificar que hay token: `localStorage.getItem('firebase_token')`
3. Probar endpoint con auth: `/torneos/test-auth`

### Paso 3: Verificar datos
1. Revisar logs en console del navegador
2. Verificar formato de fechas (YYYY-MM-DD)
3. Probar endpoint de prueba: `/torneos/test-create`

### Paso 4: Verificar CORS
1. Revisar headers de respuesta en Network tab
2. Verificar que OPTIONS request funciona
3. Verificar configuración CORS en main.py

### Paso 5: Verificar rutas
1. Revisar orden de rutas en `torneo_controller.py`
2. Verificar que no hay conflictos
3. Verificar que el router está incluido en `main.py`

## Comandos útiles para debugging

```bash
# Ver logs del servidor
cd backend && python main.py

# Probar endpoints
curl -X GET http://localhost:8000/torneos/test-simple
curl -X GET http://localhost:8000/torneos/test-auth -H "Authorization: Bearer TOKEN"

# Ver rutas disponibles
curl http://localhost:8000/docs

# Verificar CORS
curl -X OPTIONS http://localhost:8000/torneos -H "Origin: http://localhost:5174" -v
```

## Resultado esperado

Después de aplicar las soluciones:
1. ✅ `GET /torneos/test-simple` → 200 OK
2. ✅ `GET /torneos/test-auth` → 200 OK (con token válido)
3. ✅ `POST /torneos/test-create` → 200 OK (con datos válidos)
4. ✅ `POST /torneos` → 201 Created (torneo creado exitosamente)

Si alguno de estos pasos falla, el error estará en ese nivel específico.