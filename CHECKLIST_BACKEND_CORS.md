# 📋 CHECKLIST BACKEND - Arreglar CORS

## 🚨 PROBLEMA ACTUAL
El frontend en `https://kioskito.click/PlayR/` no puede conectarse al backend en Railway porque **CORS está bloqueando todas las requests**.

## ✅ CAMBIOS NECESARIOS EN EL BACKEND

### 1. Aplicar cambios en `main.py`
Los cambios ya están hechos en el código local. Necesitas aplicar estos cambios en Railway:

```python
# ---- CORS (DEBE IR ANTES DE OTROS MIDDLEWARES) ----
_default_origins = '["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:8080", "http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:5174", "http://127.0.0.1:5174", "https://kioskito.click", "https://www.kioskito.click"]'
try:
    origins = json.loads(os.getenv("CORS_ORIGINS", _default_origins))
    if not isinstance(origins, list):
        raise ValueError("CORS_ORIGINS debe ser una lista JSON de strings.")
    logger.info(f"✅ CORS configurado con origins: {origins}")
except Exception as e:
    logger.error(f"❌ Error configurando CORS: {e}")
    origins = json.loads(_default_origins)
    logger.info(f"🔄 Usando origins por defecto: {origins}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)
```

### 2. Agregar endpoints de debug y preflight
```python
@app.get("/debug/cors")
async def cors_debug():
    """Endpoint de debug para verificar configuración CORS"""
    return {
        "cors_origins": origins,
        "cors_origins_env": os.getenv("CORS_ORIGINS"),
        "cors_origins_default": _default_origins,
        "cors_middleware_enabled": True,
        "allow_credentials": True,
        "allow_methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["*"],
        "timestamp": datetime.now().isoformat()
    }

@app.options("/api/test-cors")
async def test_cors_preflight():
    """Endpoint OPTIONS para preflight requests"""
    return {"message": "Preflight OK"}

@app.options("/{path:path}")
async def handle_preflight(path: str):
    """Manejar todas las requests OPTIONS (preflight)"""
    return {"message": "Preflight handled"}
```

### 3. Configurar Variables de Entorno en Railway

**CRÍTICO**: Ve al dashboard de Railway → Tu proyecto → Variables y configura:

```bash
CORS_ORIGINS=["https://kioskito.click", "https://www.kioskito.click", "http://localhost:5173"]
```

**IMPORTANTE**: 
- Debe ser un JSON válido (con comillas dobles)
- Incluir tanto `kioskito.click` como `www.kioskito.click`
- NO usar `*` como origin cuando `allow_credentials=True`

### 4. Verificar endpoints de búsqueda y torneos

El frontend está intentando usar estos endpoints:

**Para buscar jugadores:**
- `/usuarios/buscar?q=...`
- `/usuarios/search?query=...`

**Para mis torneos:**
- `/torneos/mis-torneos` (GET) - Debe retornar los torneos donde el usuario está inscrito

Asegúrate de que al menos uno de estos endpoints exista y funcione para cada funcionalidad.

## 🔧 PASOS PARA APLICAR

### Paso 1: Actualizar el código
1. Hacer pull de los cambios del repositorio
2. Verificar que `main.py` tenga los cambios de CORS
3. Hacer commit y push

### Paso 2: Configurar variables en Railway
1. Ir a Railway Dashboard
2. Seleccionar el proyecto del backend
3. Ir a Variables
4. Agregar/editar: `CORS_ORIGINS=["https://kioskito.click", "https://www.kioskito.click", "http://localhost:5173"]`
5. Guardar

### Paso 3: Redeploy
1. En Railway, hacer "Redeploy" del servicio
2. Esperar que termine el deploy
3. Verificar que el servicio esté corriendo

### Paso 4: Verificar que funciona
1. Ir a: `https://playr-proyecto-production.up.railway.app/debug/cors`
2. Verificar que `cors_origins` contenga `https://kioskito.click`
3. Probar: `https://playr-proyecto-production.up.railway.app/health`

## 🧪 PRUEBAS PARA VERIFICAR

### Desde el navegador (en kioskito.click):
```javascript
// Abrir consola en https://kioskito.click/PlayR/ y ejecutar:
fetch('https://playr-proyecto-production.up.railway.app/health', {
  method: 'GET',
  credentials: 'include'
})
.then(r => r.json())
.then(data => console.log('✅ CORS funciona:', data))
.catch(err => console.error('❌ CORS falla:', err));
```

### Desde curl:
```bash
# Probar preflight
curl -X OPTIONS "https://playr-proyecto-production.up.railway.app/health" \
  -H "Origin: https://kioskito.click" \
  -H "Access-Control-Request-Method: GET" \
  -v

# Probar request real
curl -X GET "https://playr-proyecto-production.up.railway.app/health" \
  -H "Origin: https://kioskito.click" \
  -v
```

## ✅ RESULTADO ESPERADO

Después de aplicar los cambios, deberías ver estos headers en las responses:

```
Access-Control-Allow-Origin: https://kioskito.click
Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS
Access-Control-Allow-Headers: *
Access-Control-Allow-Credentials: true
```

## 🚨 TROUBLESHOOTING

### Si sigue fallando:

1. **Verificar logs de Railway**:
   - Buscar mensajes de error relacionados con CORS
   - Verificar que las variables de entorno se cargaron correctamente

2. **Verificar que el middleware está en el orden correcto**:
   - CORS debe ir ANTES que otros middlewares
   - CORS debe ir DESPUÉS de crear la app FastAPI

3. **Verificar la variable de entorno**:
   - Ir a `/debug/cors` y verificar que `cors_origins_env` no sea null
   - Verificar que `cors_origins` contenga los dominios correctos

4. **Hard refresh del frontend**:
   - Ctrl+Shift+R en el navegador
   - O probar en ventana incógnita

## 📞 CONTACTO

Una vez aplicados los cambios, el frontend debería poder:
- ✅ Hacer login
- ✅ Cargar torneos
- ✅ Acceder a health check
- ✅ Buscar jugadores
- ✅ Ver logs de admin

Si algo no funciona, revisar los logs de Railway y el endpoint `/debug/cors` para diagnosticar.