# 🎯 PLAN DE ACCIÓN - Backend Sistema de Marcador de Pádel

## 📋 RESUMEN EJECUTIVO

**Objetivo**: Implementar el sistema completo de marcador de pádel con confirmaciones, cálculo de Elo y notificaciones.

**Tiempo estimado**: 6-8 horas de desarrollo

**Prioridad**: ALTA - El frontend ya está listo y esperando estos endpoints

---

## 🗂️ FASE 1: BASE DE DATOS (1-2 horas)

### 1.1 Ejecutar Migración SQL

**Archivo**: `backend/CAMBIOS_BASE_DATOS_DETALLADO.md`

```bash
# Conectar a la base de datos
mysql -u usuario -p nombre_bd

# Ejecutar el script de migración completo
source backend/migration_script.sql
```

**Verificar**:
```sql
DESCRIBE salas;
DESCRIBE confirmaciones;
DESCRIBE usuarios;
DESCRIBE historial_elo;
DESCRIBE participaciones_sala;
DESCRIBE notificaciones;
```

### 1.2 Actualizar Modelos SQLAlchemy

**Archivos a modificar**:

1. `backend/src/models/sala.py`
2. `backend/src/models/user.py`
3. `backend/src/models/confirmacion.py` (NUEVO)
4. `backend/src/models/historial_elo.py` (NUEVO)
5. `backend/src/models/notificacion.py` (NUEVO)

**Checklist**:
- [ ] Agregar campos nuevos a modelo Sala
- [ ] Agregar campos nuevos a modelo Usuario
- [ ] Crear modelo Confirmacion
- [ ] Crear modelo HistorialElo
- [ ] Crear modelo Notificacion
- [ ] Actualizar relationships entre modelos

---

## 🔧 FASE 2: SERVICIOS CORE (2-3 horas)

### 2.1 Servicio de Cálculo de Elo

**Archivo**: `backend/src/services/elo_service.py` (NUEVO)

```python
class EloService:
    def calcular_elo(self, elo_ganador, elo_perdedor, k=32):
        """Calcula nuevo Elo usando fórmula estándar"""
        pass
    
    def actualizar_elo_partido(self, sala_id):
        """Actualiza Elo de todos los jugadores de un partido"""
        pass
    
    def registrar_historial(self, usuario_id, sala_id, cambio):
        """Registra cambio en historial_elo"""
        pass
```

**Funcionalidades**:
- [ ] Implementar fórmula de Elo estándar
- [ ] Calcular Elo promedio de equipos
- [ ] Actualizar estadísticas de usuarios (rachas, máximos, mínimos)
- [ ] Registrar en historial_elo
- [ ] Manejar casos edge (empates, abandonos)

### 2.2 Servicio de Confirmaciones

**Archivo**: `backend/src/services/confirmacion_service.py` (NUEVO)

```python
class ConfirmacionService:
    def confirmar_resultado(self, sala_id, usuario_id):
        """Usuario confirma el resultado"""
        pass
    
    def reportar_resultado(self, sala_id, usuario_id, motivo):
        """Usuario reporta resultado incorrecto"""
        pass
    
    def verificar_confirmaciones(self, sala_id):
        """Verifica si todos confirmaron"""
        pass
    
    def procesar_confirmacion_completa(self, sala_id):
        """Cuando todos confirman, actualiza Elo"""
        pass
```

**Funcionalidades**:
- [ ] Registrar confirmaciones en tabla confirmaciones
- [ ] Actualizar participaciones_sala
- [ ] Verificar si todos los jugadores confirmaron
- [ ] Cambiar estado_confirmacion de sala
- [ ] Trigger automático de cálculo de Elo
- [ ] Crear notificaciones

### 2.3 Servicio de Notificaciones

**Archivo**: `backend/src/services/notificacion_service.py` (NUEVO)

```python
class NotificacionService:
    def crear_notificacion(self, usuario_id, tipo, titulo, mensaje, sala_id):
        """Crea una notificación"""
        pass
    
    def notificar_resultado_pendiente(self, sala_id):
        """Notifica a jugadores que hay resultado pendiente"""
        pass
    
    def notificar_elo_actualizado(self, usuario_id, cambio_elo):
        """Notifica cambio de Elo"""
        pass
```

**Funcionalidades**:
- [ ] CRUD de notificaciones
- [ ] Marcar como leída
- [ ] Obtener notificaciones no leídas
- [ ] Enviar notificaciones push (opcional)

---

## 🌐 FASE 3: ENDPOINTS API (2-3 horas)

### 3.1 Endpoints de Resultados

**Archivo**: `backend/src/routes/resultados.py` (NUEVO)

```python
# POST /api/salas/{sala_id}/resultado
# Cargar resultado del partido
{
  "formato": "best_of_3",
  "sets": [...],
  "supertiebreak": {...},
  "ganador": "equipoA"
}

# GET /api/salas/{sala_id}/resultado
# Obtener resultado de un partido

# PUT /api/salas/{sala_id}/resultado
# Actualizar resultado (solo creador, antes de confirmaciones)
```

**Checklist**:
- [ ] Validar formato de resultado
- [ ] Validar que usuario sea participante
- [ ] Guardar en sala.resultado_padel
- [ ] Cambiar estado_confirmacion a 'pendiente_confirmacion'
- [ ] Notificar a otros jugadores
- [ ] Manejar errores y validaciones

### 3.2 Endpoints de Confirmaciones

**Archivo**: `backend/src/routes/confirmaciones.py` (NUEVO)

```python
# POST /api/salas/{sala_id}/confirmar
# Confirmar resultado

# POST /api/salas/{sala_id}/reportar
# Reportar resultado incorrecto
{
  "motivo": "El resultado no es correcto..."
}

# GET /api/confirmaciones/pendientes
# Obtener confirmaciones pendientes del usuario

# GET /api/salas/{sala_id}/confirmaciones
# Ver quién confirmó/reportó
```

**Checklist**:
- [ ] Validar que usuario sea participante
- [ ] Validar que haya resultado cargado
- [ ] Registrar confirmación/reporte
- [ ] Verificar si todos confirmaron
- [ ] Trigger de cálculo de Elo si todos confirmaron
- [ ] Manejar estado 'disputado' si hay reportes

### 3.3 Endpoints de Estadísticas

**Archivo**: `backend/src/routes/estadisticas.py` (NUEVO)

```python
# GET /api/usuarios/{usuario_id}/estadisticas
# Estadísticas completas del usuario
{
  "elo_rating": 1350,
  "elo_maximo": 1400,
  "elo_minimo": 1200,
  "partidos_jugados": 25,
  "partidos_ganados": 15,
  "partidos_perdidos": 10,
  "win_rate": 60.0,
  "racha_victorias": 3,
  "racha_maxima": 5,
  "ultimo_partido": "2024-11-20T10:00:00"
}

# GET /api/usuarios/{usuario_id}/historial-elo
# Historial de cambios de Elo
[
  {
    "fecha": "2024-11-20T10:00:00",
    "elo_anterior": 1300,
    "elo_nuevo": 1350,
    "cambio": +50,
    "resultado": "victoria",
    "sala": {...}
  }
]

# GET /api/rankings
# Ranking global por Elo
# GET /api/rankings/categoria/{categoria}
# Ranking por categoría
```

**Checklist**:
- [ ] Calcular estadísticas en tiempo real
- [ ] Cachear rankings (opcional)
- [ ] Paginación para historial
- [ ] Filtros por temporada
- [ ] Ordenamiento por diferentes criterios

### 3.4 Endpoints de Notificaciones

**Archivo**: `backend/src/routes/notificaciones.py` (NUEVO)

```python
# GET /api/notificaciones
# Obtener notificaciones del usuario

# GET /api/notificaciones/no-leidas
# Obtener solo no leídas

# PUT /api/notificaciones/{id}/leer
# Marcar como leída

# PUT /api/notificaciones/leer-todas
# Marcar todas como leídas
```

**Checklist**:
- [ ] Filtrar por usuario autenticado
- [ ] Ordenar por fecha descendente
- [ ] Incluir datos de sala relacionada
- [ ] Paginación

---

## 🔌 FASE 4: WEBSOCKETS (1 hora)

### 4.1 Eventos WebSocket

**Archivo**: `backend/src/websocket/events.py`

```python
# Eventos a emitir:
- "resultado_cargado" -> Cuando se carga un resultado
- "resultado_confirmado" -> Cuando alguien confirma
- "resultado_reportado" -> Cuando alguien reporta
- "elo_actualizado" -> Cuando se actualiza el Elo
- "confirmacion_completa" -> Cuando todos confirmaron
```

**Checklist**:
- [ ] Emitir eventos en tiempo real
- [ ] Broadcast a sala específica
- [ ] Notificar a usuarios específicos
- [ ] Manejar desconexiones

---

## 🧪 FASE 5: TESTING (1 hora)

### 5.1 Tests Unitarios

**Archivos**:
- `backend/tests/test_elo_service.py`
- `backend/tests/test_confirmacion_service.py`

```python
def test_calcular_elo_victoria():
    """Test cálculo de Elo en victoria"""
    pass

def test_confirmacion_completa():
    """Test cuando todos confirman"""
    pass

def test_reporte_resultado():
    """Test cuando alguien reporta"""
    pass
```

### 5.2 Tests de Integración

```python
def test_flujo_completo_resultado():
    """Test flujo: cargar -> confirmar -> Elo actualizado"""
    pass
```

### 5.3 Tests Manuales con Postman/Thunder Client

**Crear colección con**:
- [ ] Cargar resultado
- [ ] Confirmar resultado (4 usuarios)
- [ ] Verificar Elo actualizado
- [ ] Obtener estadísticas
- [ ] Obtener historial
- [ ] Reportar resultado

---

## 📦 ESTRUCTURA DE ARCHIVOS FINAL

```
backend/
├── src/
│   ├── models/
│   │   ├── sala.py (ACTUALIZAR)
│   │   ├── user.py (ACTUALIZAR)
│   │   ├── confirmacion.py (NUEVO)
│   │   ├── historial_elo.py (NUEVO)
│   │   └── notificacion.py (NUEVO)
│   │
│   ├── services/
│   │   ├── elo_service.py (NUEVO)
│   │   ├── confirmacion_service.py (NUEVO)
│   │   └── notificacion_service.py (NUEVO)
│   │
│   ├── routes/
│   │   ├── resultados.py (NUEVO)
│   │   ├── confirmaciones.py (NUEVO)
│   │   ├── estadisticas.py (NUEVO)
│   │   └── notificaciones.py (NUEVO)
│   │
│   ├── websocket/
│   │   └── events.py (ACTUALIZAR)
│   │
│   └── utils/
│       └── validators.py (NUEVO - validaciones de pádel)
│
├── tests/
│   ├── test_elo_service.py (NUEVO)
│   ├── test_confirmacion_service.py (NUEVO)
│   └── test_resultados_api.py (NUEVO)
│
├── migrations/
│   └── 001_sistema_marcador.sql (NUEVO)
│
└── CAMBIOS_BASE_DATOS_DETALLADO.md (YA EXISTE)
```

---

## 🎯 CHECKLIST GENERAL

### Base de Datos
- [ ] Ejecutar migración SQL
- [ ] Verificar todas las tablas creadas
- [ ] Poblar datos de prueba
- [ ] Verificar índices y constraints

### Modelos
- [ ] Actualizar modelo Sala
- [ ] Actualizar modelo Usuario
- [ ] Crear modelo Confirmacion
- [ ] Crear modelo HistorialElo
- [ ] Crear modelo Notificacion
- [ ] Actualizar relationships

### Servicios
- [ ] Implementar EloService
- [ ] Implementar ConfirmacionService
- [ ] Implementar NotificacionService
- [ ] Tests unitarios de servicios

### API Endpoints
- [ ] POST /api/salas/{id}/resultado
- [ ] GET /api/salas/{id}/resultado
- [ ] POST /api/salas/{id}/confirmar
- [ ] POST /api/salas/{id}/reportar
- [ ] GET /api/confirmaciones/pendientes
- [ ] GET /api/usuarios/{id}/estadisticas
- [ ] GET /api/usuarios/{id}/historial-elo
- [ ] GET /api/rankings
- [ ] GET /api/notificaciones
- [ ] PUT /api/notificaciones/{id}/leer

### WebSockets
- [ ] Evento resultado_cargado
- [ ] Evento resultado_confirmado
- [ ] Evento resultado_reportado
- [ ] Evento elo_actualizado
- [ ] Evento confirmacion_completa

### Testing
- [ ] Tests unitarios de servicios
- [ ] Tests de endpoints
- [ ] Tests de integración
- [ ] Tests manuales con Postman

### Documentación
- [ ] Documentar endpoints en Swagger/OpenAPI
- [ ] Actualizar README con nuevos endpoints
- [ ] Documentar estructura de datos JSON

---

## 🚀 ORDEN DE IMPLEMENTACIÓN RECOMENDADO

### DÍA 1 (4 horas)
1. ✅ Ejecutar migración de BD (30 min)
2. ✅ Actualizar modelos SQLAlchemy (1 hora)
3. ✅ Implementar EloService (1.5 horas)
4. ✅ Implementar ConfirmacionService (1 hora)

### DÍA 2 (4 horas)
5. ✅ Crear endpoints de resultados (1 hora)
6. ✅ Crear endpoints de confirmaciones (1 hora)
7. ✅ Crear endpoints de estadísticas (1 hora)
8. ✅ Implementar WebSockets (1 hora)

### DÍA 3 (2 horas)
9. ✅ Testing completo (1 hora)
10. ✅ Documentación y ajustes finales (1 hora)

---

## 📝 NOTAS IMPORTANTES

### Validaciones Críticas
- Verificar que usuario sea participante antes de confirmar
- Validar formato de resultado de pádel
- Evitar confirmaciones duplicadas
- Manejar casos edge (abandonos, empates técnicos)

### Performance
- Cachear rankings si hay muchos usuarios
- Índices en campos de búsqueda frecuente
- Paginación en historial y notificaciones

### Seguridad
- Autenticación en todos los endpoints
- Validar permisos (solo participantes pueden confirmar)
- Sanitizar inputs (especialmente motivo de reporte)

### Casos Edge
- ¿Qué pasa si alguien reporta después de que otros confirmaron?
- ¿Cómo manejar abandonos?
- ¿Qué hacer con partidos muy antiguos sin confirmar?

---

## 🔗 RECURSOS

### Documentos de Referencia
- `backend/CAMBIOS_BASE_DATOS_DETALLADO.md` - Estructura completa de BD
- `frontend/PLAN_INTEGRACION_BACKEND.md` - Contrato de API con frontend
- `frontend/src/services/sala.service.ts` - Cómo el frontend consume la API

### Fórmula de Elo
```
E_a = 1 / (1 + 10^((R_b - R_a) / 400))
R_a_nuevo = R_a + K * (S_a - E_a)

Donde:
- R_a = Elo actual del jugador A
- R_b = Elo del oponente
- K = Factor K (32 para jugadores normales)
- S_a = Resultado (1 = victoria, 0 = derrota)
- E_a = Resultado esperado
```

### Estructura JSON de Resultado
```json
{
  "formato": "best_of_3",
  "sets": [
    {
      "gamesEquipoA": 6,
      "gamesEquipoB": 4,
      "ganador": "equipoA",
      "completado": true
    }
  ],
  "supertiebreak": {
    "puntosEquipoA": 10,
    "puntosEquipoB": 8,
    "ganador": "equipoA",
    "completado": true
  },
  "ganador": "equipoA",
  "completado": true
}
```

---

## ✅ CRITERIOS DE ACEPTACIÓN

El sistema está completo cuando:

1. ✅ Se puede cargar un resultado de partido
2. ✅ Los 4 jugadores reciben notificación
3. ✅ Cada jugador puede confirmar o reportar
4. ✅ Cuando todos confirman, el Elo se actualiza automáticamente
5. ✅ Se registra en historial_elo
6. ✅ Se actualizan estadísticas (rachas, máximos, etc.)
7. ✅ Los rankings reflejan los cambios
8. ✅ Las notificaciones funcionan en tiempo real
9. ✅ El frontend puede consumir todos los endpoints
10. ✅ Los tests pasan correctamente

---

## 🆘 SOPORTE

Si tienes dudas durante la implementación:

1. Revisa `CAMBIOS_BASE_DATOS_DETALLADO.md` para estructura de BD
2. Revisa `frontend/PLAN_INTEGRACION_BACKEND.md` para contrato de API
3. Consulta el código del frontend en `frontend/src/services/sala.service.ts`
4. Revisa los componentes de confirmación en `frontend/src/pages/Confirmaciones.tsx`

**¡Éxito con la implementación! 🚀**
