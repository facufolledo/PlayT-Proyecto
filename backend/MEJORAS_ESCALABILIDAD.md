# Mejoras de Escalabilidad - PlayT Backend

## Resumen de cambios implementados para escalar a 1000+ usuarios

---

## 1. Pool de Conexiones DB (`src/database/config.py`)

```python
pool_size=5          # Conexiones permanentes
max_overflow=10      # Conexiones extra bajo demanda
pool_pre_ping=True   # Verifica conexión antes de usar (evita BrokenPipe)
pool_recycle=300     # Recicla cada 5 min (Neon/Railway cortan idle)
```

**Variables de entorno:**
- `DB_POOL_SIZE` - default: 5
- `DB_MAX_OVERFLOW` - default: 10

---

## 2. Sistema de Caché (`src/utils/cache.py`)

Caché en memoria thread-safe con TTL:
- Rankings: 60 segundos
- Top weekly: 2 minutos
- Invalidación automática al cambiar ratings

**Uso:**
```python
from src.utils.cache import cache, invalidate_ranking_cache

# Cachear manualmente
cache.set("key", value, ttl_seconds=60)
cached = cache.get("key")

# Invalidar después de cambios
invalidate_ranking_cache()
```

---

## 3. Sistema de Excepciones (`src/utils/exceptions.py`)

Excepciones tipadas que se convierten automáticamente a HTTP status codes:

| Excepción | HTTP Status |
|-----------|-------------|
| `BusinessError` | 400 |
| `ValidationError` | 400 |
| `AuthenticationError` | 401 |
| `AuthorizationError` | 403 |
| `NotFoundError` | 404 |
| `ConflictError` | 409 |

**Uso en services:**
```python
from src.utils.exceptions import NotFoundError, BusinessError

def mi_service(db, id):
    item = db.query(Model).filter(Model.id == id).first()
    if not item:
        raise NotFoundError("Item", id)
    
    if item.estado != "activo":
        raise BusinessError("El item no está activo")
```

---

## 4. Logging Centralizado (`src/utils/logger.py`)

```python
from src.utils.logger import get_logger, Loggers

# Por módulo
logger = get_logger("mi_modulo")
logger.info("Mensaje")

# Pre-configurados
Loggers.elo().info("Calculando Elo...")
Loggers.torneo().warning("Torneo sin parejas")
Loggers.anti_trampa().error("Límite excedido")
```

---

## 5. Índices de DB (`migrations_indices_performance.sql`)

Índices críticos para performance:
- `idx_usuarios_rating` - Rankings
- `idx_partidos_fecha` - Historial
- `idx_historial_hash1/2` - Anti-trampa
- `idx_inscripciones_torneo` - Torneos

**Ejecutar en Neon:**
```sql
-- Copiar contenido de migrations_indices_performance.sql
```

---

## 6. Controllers Divididos (`src/controllers/torneo/`)

El torneo_controller (2300+ líneas) se dividió en:
- `torneo_base_controller.py` - CRUD básico
- `torneo_inscripcion_controller.py` - Inscripciones y parejas
- `torneo_zona_controller.py` - Zonas y grupos
- `torneo_fixture_controller.py` - Fixture y programación
- `torneo_resultado_controller.py` - Resultados de partidos
- `torneo_playoff_controller.py` - Playoffs y bracket

---

## 7. Enums para Estados (`src/schemas/enums.py`)

```python
from src.schemas.enums import EstadoPartido, EstadoTorneo

# En lugar de strings
estado: str = "pendiente"

# Usar enums
estado: EstadoPartido = EstadoPartido.pendiente
```

---

## 8. Endpoints de Monitoreo (`src/controllers/health_controller.py`)

- `GET /health/` - Health check básico
- `GET /health/db` - Estado de DB + pool de conexiones
- `GET /health/cache` - Estado del caché
- `POST /health/cache/clear` - Limpiar caché
- `POST /health/cache/cleanup` - Limpiar expirados

---

## Checklist de Deploy

1. [ ] Ejecutar `migrations_indices_performance.sql` en Neon
2. [ ] Configurar variables en Railway:
   - `ENVIRONMENT=production`
   - `DB_POOL_SIZE=5`
   - `DB_MAX_OVERFLOW=10`
3. [ ] Verificar `/health/db` después del deploy
4. [ ] Monitorear logs en Railway

---

## Próximos pasos (cuando escales más)

- **Redis** para caché distribuido (múltiples instancias)
- **Redis/PubSub** para WebSockets (>100 conexiones simultáneas)
- **Transacciones explícitas** en services críticos
- **Rate limiting** por usuario
