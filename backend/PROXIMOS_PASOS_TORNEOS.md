# Próximos Pasos - Implementación Sistema de Torneos

## Archivos Creados

✅ **Documentación**
- `SISTEMA_TORNEOS_CLASICO.md` - Descripción general del sistema
- `LOGICA_TORNEOS_DETALLADA.md` - Algoritmos y lógica de negocio detallada
- `crear_tablas_torneos.sql` - Script SQL para crear todas las tablas

✅ **Modelos y Schemas**
- `src/models/torneo_models.py` - Modelos SQLAlchemy completos
- `src/schemas/torneo_schemas.py` - Schemas Pydantic para validación

## Próximos Pasos para Implementación

### 1. Crear las Tablas en la Base de Datos

```bash
# Ejecutar el script SQL
python -c "
from src.database.connection import get_db_connection
conn = get_db_connection()
with open('crear_tablas_torneos.sql', 'r') as f:
    sql = f.read()
    conn.execute(sql)
"
```

O crear un script Python:

```python
# backend/crear_tablas_torneos.py
import mysql.connector
from dotenv import load_dotenv
import os

load_dotenv()

conn = mysql.connector.connect(
    host=os.getenv('DB_HOST'),
    user=os.getenv('DB_USER'),
    password=os.getenv('DB_PASSWORD'),
    database=os.getenv('DB_NAME')
)

with open('crear_tablas_torneos.sql', 'r') as f:
    sql = f.read()
    
cursor = conn.cursor()
for statement in sql.split(';'):
    if statement.strip():
        cursor.execute(statement)

conn.commit()
print("✅ Tablas de torneos creadas exitosamente")
```

### 2. Crear los Servicios

Necesitás crear estos archivos en `backend/src/services/`:

#### `torneo_service.py`
- Crear torneo
- Actualizar torneo
- Listar torneos
- Obtener torneo por ID
- Cambiar estado del torneo
- Validar permisos de organizador

#### `torneo_inscripcion_service.py`
- Inscribir pareja
- Confirmar pareja
- Dar de baja pareja
- Reemplazar jugador en pareja
- Validar inscripciones

#### `torneo_zona_service.py`
- Generar zonas automáticamente
- Asignar parejas a zonas
- Mover pareja entre zonas
- Obtener tabla de posiciones de zona
- Calcular clasificados

#### `torneo_fixture_service.py`
- Generar fixture de zonas
- Programar partidos automáticamente
- Validar disponibilidad de jugadores
- Asignar canchas y horarios
- Reprogramar partidos

#### `torneo_eliminacion_service.py`
- Generar cuadro de eliminación
- Calcular byes
- Asignar seeds
- Generar partidos de playoff

#### `torneo_resultado_service.py`
- Cargar resultado de partido
- Validar sets
- Actualizar tabla de posiciones
- Integrar con EloController
- Guardar historial de jugadores
- Determinar ganador de torneo

### 3. Crear el Controller

#### `backend/src/controllers/torneo_controller.py`

Endpoints necesarios:

**Gestión de Torneos**
- `POST /torneos` - Crear torneo (solo organizadores autorizados)
- `GET /torneos` - Listar torneos
- `GET /torneos/{id}` - Obtener torneo
- `PUT /torneos/{id}` - Actualizar torneo
- `DELETE /torneos/{id}` - Eliminar torneo

**Inscripciones**
- `POST /torneos/{id}/inscribir` - Inscribir pareja
- `GET /torneos/{id}/parejas` - Listar parejas inscritas
- `PUT /torneos/{id}/parejas/{pareja_id}` - Actualizar pareja
- `DELETE /torneos/{id}/parejas/{pareja_id}` - Dar de baja pareja
- `POST /torneos/{id}/parejas/{pareja_id}/reemplazar-jugador` - Reemplazar jugador

**Restricciones Horarias**
- `POST /torneos/{id}/bloqueos` - Agregar bloqueo horario
- `GET /torneos/{id}/bloqueos` - Listar bloqueos del jugador
- `DELETE /torneos/{id}/bloqueos/{bloqueo_id}` - Eliminar bloqueo

**Canchas y Slots**
- `POST /torneos/{id}/canchas` - Agregar cancha
- `GET /torneos/{id}/canchas` - Listar canchas
- `POST /torneos/{id}/slots` - Crear slots de horarios
- `GET /torneos/{id}/slots` - Listar slots disponibles

**Fase de Zonas**
- `POST /torneos/{id}/generar-zonas` - Generar zonas automáticamente
- `GET /torneos/{id}/zonas` - Listar zonas
- `GET /torneos/{id}/zonas/{zona_id}/tabla` - Tabla de posiciones de zona
- `POST /torneos/{id}/zonas/mover-pareja` - Mover pareja entre zonas

**Partidos**
- `GET /torneos/{id}/partidos` - Listar todos los partidos
- `GET /torneos/{id}/partidos/{partido_id}` - Obtener partido
- `POST /torneos/{id}/partidos/{partido_id}/resultado` - Cargar resultado
- `PUT /torneos/{id}/partidos/{partido_id}/reprogramar` - Reprogramar partido
- `POST /torneos/{id}/partidos/{partido_id}/wo` - Marcar W.O.

**Fase de Eliminación**
- `POST /torneos/{id}/generar-cuadro` - Generar cuadro de eliminación
- `GET /torneos/{id}/cuadro` - Obtener cuadro completo
- `GET /torneos/{id}/clasificados` - Listar clasificados

**Estadísticas**
- `GET /torneos/{id}/estadisticas` - Estadísticas generales del torneo
- `GET /torneos/{id}/historial-cambios` - Historial de cambios

### 4. Integración con Sistema Existente

#### Modificar `elo_controller.py`
Agregar soporte para tipo de partido "torneo":

```python
def process_match(match_data):
    # ... código existente ...
    
    # Si es partido de torneo, guardar referencia
    if match_data.get('tipo_partido') == 'torneo':
        torneo_id = match_data.get('torneo_id')
        # Guardar en historial con referencia al torneo
```

#### Modificar `usuario_controller.py`
Agregar endpoint para ver torneos del jugador:

```python
@router.get("/usuarios/{user_id}/torneos")
def obtener_torneos_jugador(user_id: int):
    # Listar torneos donde el jugador participó
    pass
```

### 5. Testing

Crear tests para cada componente:

- `test_torneo_service.py` - Tests de servicios
- `test_torneo_controller.py` - Tests de endpoints
- `test_torneo_zonas.py` - Tests de generación de zonas
- `test_torneo_fixture.py` - Tests de programación
- `test_torneo_eliminacion.py` - Tests de cuadros finales
- `test_torneo_elo_integration.py` - Tests de integración con ELO

### 6. Frontend (Después del Backend)

Páginas necesarias:

- `/torneos` - Listado de torneos
- `/torneos/crear` - Crear torneo (solo organizadores)
- `/torneos/{id}` - Vista del torneo
- `/torneos/{id}/inscribir` - Inscripción de pareja
- `/torneos/{id}/zonas` - Vista de zonas y tablas
- `/torneos/{id}/fixture` - Fixture completo
- `/torneos/{id}/cuadro` - Cuadro de eliminación
- `/torneos/{id}/admin` - Panel de administración (solo organizadores)

## Orden Recomendado de Implementación

1. ✅ Crear tablas en BD
2. ✅ Implementar `torneo_service.py` (CRUD básico)
3. ✅ Implementar `torneo_controller.py` (endpoints básicos)
4. ✅ Implementar `torneo_inscripcion_service.py`
5. ✅ Implementar endpoints de inscripción
6. ✅ Implementar `torneo_zona_service.py`
7. ✅ Implementar `torneo_fixture_service.py`
8. ✅ Implementar `torneo_resultado_service.py` + integración ELO
9. ✅ Implementar `torneo_eliminacion_service.py`
10. ✅ Testing completo
11. ✅ Frontend básico
12. ✅ Frontend avanzado (admin panel)

## Consideraciones Importantes

### Permisos
- Solo organizadores autorizados pueden crear torneos
- Solo organizadores del torneo pueden:
  - Confirmar/rechazar parejas
  - Generar zonas
  - Cargar resultados
  - Editar fixture
  - Mover parejas

### Validaciones Críticas
- No permitir cambios en zonas si ya hay partidos jugados
- No permitir cargar resultado si el partido no está programado
- Validar que los sets sean válidos según reglas de pádel
- Validar que los jugadores no estén en múltiples parejas del mismo torneo

### Performance
- Cachear tabla de posiciones
- Índices en todas las foreign keys
- Paginación en listados de torneos y partidos

### Notificaciones (Futuro)
- Notificar a jugadores cuando se programa su partido
- Notificar cuando se carga un resultado
- Notificar cuando clasifican a fase final
- Notificar cambios de horario

## ¿Querés que empiece a implementar algún servicio específico?

Puedo empezar por:
1. `torneo_service.py` - CRUD básico de torneos
2. `torneo_inscripcion_service.py` - Sistema de inscripciones
3. `torneo_zona_service.py` - Generación de zonas
4. O el que prefieras

Decime por cuál arrancamos y te lo armo completo con tests incluidos.
