# 👤 ENDPOINTS PARA PERFILES PÚBLICOS

## 📋 ENDPOINTS NECESARIOS PARA FACU

### **1. Perfil Público por Username**
```python
@router.get("/usuarios/perfil-publico/{username}")
async def get_perfil_publico(username: str):
    """
    Obtener perfil público de un jugador por su username
    
    QUERY SQL:
    SELECT 
        id_usuario,
        nombre,
        apellido,
        nombre_usuario,
        rating,
        posicion_preferida,
        mano_dominante,
        ciudad,
        pais,
        fecha_registro,
        foto_perfil,
        activo
    FROM usuarios 
    WHERE nombre_usuario = %s AND activo = true
    """
    user = await get_user_by_username(username)
    if not user:
        raise HTTPException(404, "Jugador no encontrado")
    
    return {
        "id_usuario": user.id_usuario,
        "nombre": user.nombre,
        "apellido": user.apellido,
        "nombre_usuario": user.nombre_usuario,
        "rating": user.rating or 1200,
        "posicion_preferida": user.posicion_preferida,
        "mano_dominante": user.mano_dominante,
        "ciudad": user.ciudad,
        "pais": user.pais,
        "fecha_registro": user.fecha_registro,
        "foto_perfil": user.foto_perfil,
        "activo": user.activo
        # NO incluir: email, telefono, fecha_nacimiento (datos privados)
    }
```

### **2. Estadísticas Avanzadas de Jugador**
```python
@router.get("/usuarios/{user_id}/estadisticas")
async def get_estadisticas_jugador(user_id: int):
    """
    Estadísticas detalladas del jugador
    
    QUERIES SQL NECESARIAS:
    """
    
    # 1. Estadísticas básicas
    stats_query = """
    SELECT 
        COUNT(*) as partidos_jugados,
        SUM(CASE WHEN ganador = true THEN 1 ELSE 0 END) as partidos_ganados,
        COUNT(*) - SUM(CASE WHEN ganador = true THEN 1 ELSE 0 END) as partidos_perdidos
    FROM historial_ratings hr
    JOIN partidos p ON hr.id_partido = p.id
    WHERE hr.id_usuario = %s
    """
    
    # 2. Rating histórico
    rating_query = """
    SELECT 
        MAX(nuevo_rating) as mejor_rating,
        MIN(nuevo_rating) as peor_rating,
        SUM(rating_change) as cambio_rating_total
    FROM historial_ratings 
    WHERE id_usuario = %s
    """
    
    # 3. Estadísticas por tipo (torneo vs amistoso)
    tipo_query = """
    SELECT 
        p.tipo,
        COUNT(*) as total,
        SUM(CASE WHEN hr.rating_change > 0 THEN 1 ELSE 0 END) as victorias
    FROM historial_ratings hr
    JOIN partidos p ON hr.id_partido = p.id
    WHERE hr.id_usuario = %s
    GROUP BY p.tipo
    """
    
    # 4. Sets y games (si hay detalle_sets)
    sets_query = """
    SELECT 
        SUM(CASE WHEN equipo = 1 THEN sets_eq1 ELSE sets_eq2 END) as sets_ganados,
        SUM(CASE WHEN equipo = 1 THEN sets_eq2 ELSE sets_eq1 END) as sets_perdidos
    FROM partidos p
    JOIN jugadores_partidos jp ON p.id = jp.id_partido
    WHERE jp.id_usuario = %s AND p.resultado IS NOT NULL
    """
    
    return {
        "partidos_jugados": 45,
        "partidos_ganados": 28,
        "partidos_perdidos": 17,
        "porcentaje_victorias": 62.2,
        "mejor_rating": 1420,
        "peor_rating": 1180,
        "rating_actual": 1350,
        "cambio_rating_total": +150,
        "winrate_torneos": 65,
        "winrate_amistosos": 60,
        "sets_ganados": 85,
        "sets_perdidos": 52,
        "games_ganados": 520,
        "games_perdidos": 380,
        "racha_actual": {
            "tipo": "victorias",
            "cantidad": 3
        },
        "mejor_racha": 8,
        "torneos_participados": 8,
        "torneos_ganados": 1,
        "finales_jugadas": 3
    }
```

### **3. Búsqueda Pública de Usuarios**
```python
@router.get("/usuarios/buscar-publico")
async def buscar_usuarios_publico(
    q: str = Query(..., min_length=2),
    limit: int = Query(20, ge=1, le=50)
):
    """
    Búsqueda pública de usuarios (sin autenticación requerida)
    
    QUERY SQL:
    """
    query = """
    SELECT 
        id_usuario,
        nombre,
        apellido,
        nombre_usuario,
        rating,
        ciudad,
        pais,
        foto_perfil
    FROM usuarios 
    WHERE 
        (nombre ILIKE %s OR apellido ILIKE %s OR nombre_usuario ILIKE %s)
        AND activo = true
    ORDER BY 
        -- Priorizar matches exactos
        CASE 
            WHEN nombre_usuario ILIKE %s THEN 1
            WHEN nombre ILIKE %s OR apellido ILIKE %s THEN 2
            ELSE 3
        END,
        -- Luego por rating
        rating DESC NULLS LAST
    LIMIT %s
    """
    
    search_term = f"%{q}%"
    exact_term = f"{q}%"
    
    params = [
        search_term, search_term, search_term,  # Para búsqueda ILIKE
        exact_term, exact_term, exact_term,     # Para priorización
        limit
    ]
    
    # results = await database.fetch_all(query, params)
    return results
```

### **4. Historial de Partidos (Ya existe, pero verificar)**
```python
# Este endpoint YA EXISTE en /partidos/usuario/{user_id}
# Solo verificar que funcione sin autenticación para perfiles públicos
# O crear una versión pública:

@router.get("/usuarios/{user_id}/historial-publico")
async def get_historial_publico(user_id: int, limit: int = 50):
    """
    Historial público de partidos (sin datos sensibles)
    """
    # Usar la misma query que /partidos/usuario/{user_id}
    # pero sin requerir autenticación
    pass
```

---

## 🗄️ MODIFICACIONES A LA BASE DE DATOS

### **Índices Adicionales (Opcional - para performance)**
```sql
-- Índice para búsqueda por username
CREATE INDEX IF NOT EXISTS idx_usuarios_nombre_usuario 
ON usuarios(nombre_usuario) WHERE activo = true;

-- Índice para búsqueda por nombre/apellido
CREATE INDEX IF NOT EXISTS idx_usuarios_nombre_apellido 
ON usuarios(nombre, apellido) WHERE activo = true;

-- Índice compuesto para búsquedas
CREATE INDEX IF NOT EXISTS idx_usuarios_busqueda 
ON usuarios(nombre, apellido, nombre_usuario, rating) WHERE activo = true;
```

---

## 🔧 CONFIGURACIÓN DE CORS

### **Agregar a main.py:**
```python
# Si los perfiles públicos van a ser accesibles sin login,
# asegurar que CORS permita requests públicos

origins = [
    "http://localhost:3000",
    "http://localhost:5173",
    "https://kioskito.click",
    "https://www.kioskito.click"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,  # Mantener para endpoints autenticados
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## 📝 FUNCIONES HELPER NECESARIAS

### **1. Función para obtener usuario por username**
```python
async def get_user_by_username(username: str):
    """Obtener usuario por nombre de usuario"""
    query = """
    SELECT * FROM usuarios 
    WHERE nombre_usuario = %s AND activo = true
    """
    return await database.fetch_one(query, [username])
```

### **2. Función para calcular racha actual**
```python
def calcular_racha_actual(partidos_ordenados, user_id):
    """Calcular racha actual de victorias/derrotas"""
    racha = 0
    tipo_racha = None
    
    for partido in partidos_ordenados:
        # Determinar si fue victoria o derrota
        es_victoria = partido.rating_change > 0
        
        if racha == 0:
            tipo_racha = 'victorias' if es_victoria else 'derrotas'
            racha = 1
        elif (tipo_racha == 'victorias' and es_victoria) or (tipo_racha == 'derrotas' and not es_victoria):
            racha += 1
        else:
            break
    
    return {"tipo": tipo_racha, "cantidad": racha}
```

---

## 🚀 PRIORIDAD DE IMPLEMENTACIÓN

### **CRÍTICO (Implementar YA):**
1. ✅ `GET /usuarios/perfil-publico/{username}` - Perfil básico
2. ✅ `GET /usuarios/buscar-publico` - Búsqueda pública

### **IMPORTANTE (Esta semana):**
3. ✅ `GET /usuarios/{id}/estadisticas` - Estadísticas avanzadas
4. ✅ Verificar que `/partidos/usuario/{id}` funcione públicamente

### **OPCIONAL (Mejoras futuras):**
5. ⚡ Índices de performance
6. ⚡ Caché en endpoints (5 min TTL)
7. ⚡ Rate limiting específico para búsquedas

---

## 🧪 TESTING

### **URLs para probar:**
```bash
# Perfil público
GET /usuarios/perfil-publico/juanp

# Búsqueda
GET /usuarios/buscar-publico?q=juan&limit=10

# Estadísticas
GET /usuarios/123/estadisticas

# Historial
GET /partidos/usuario/123?limit=20
```

### **Casos de prueba:**
- ✅ Usuario existente y activo
- ❌ Usuario no encontrado
- ❌ Usuario inactivo
- ✅ Búsqueda con resultados
- ✅ Búsqueda sin resultados
- ✅ Búsqueda con caracteres especiales

---

**¡Con estos endpoints, el frontend de perfiles públicos funcionará perfectamente!** 🚀