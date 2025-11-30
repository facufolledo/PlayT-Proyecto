# Sistema de Zonas para Torneos - Implementado ✅

## Resumen

Sistema completo para generar y gestionar zonas en torneos de pádel, con distribución automática de parejas y cálculo de tablas de posiciones.

## Archivos Creados

### Backend
- ✅ `src/services/torneo_zona_service.py` - Servicio de gestión de zonas
- ✅ `src/controllers/torneo_controller.py` - Endpoints agregados
- ✅ `test_torneo_zonas.py` - Tests de funcionalidad

## Funcionalidades Implementadas

### 1. Generación Automática de Zonas

**Endpoint:** `POST /torneos/{torneo_id}/generar-zonas`

**Parámetros:**
- `num_zonas` (opcional): Número de zonas a crear
- `balancear_por_rating` (default: true): Distribuir parejas por rating

**Características:**
- Calcula automáticamente el número óptimo de zonas si no se especifica
- Distribuye parejas balanceando por rating promedio (método serpiente)
- Valida que haya al menos 4 parejas confirmadas
- Valida que haya mínimo 2 parejas por zona
- Elimina zonas anteriores si existen
- Cambia estado del torneo a "armando_zonas"

**Algoritmo de Distribución Balanceada:**
```
1. Calcular rating promedio de cada pareja
2. Ordenar parejas por rating descendente
3. Distribuir en serpiente:
   - Zona A: Pareja 1 (mejor)
   - Zona B: Pareja 2
   - Zona B: Pareja 3
   - Zona A: Pareja 4
   - Zona A: Pareja 5
   - Zona B: Pareja 6
   - etc.
```

**Número Óptimo de Zonas:**
- 4-8 parejas → 2 zonas
- 9-16 parejas → 4 zonas
- 17-24 parejas → 6 zonas
- 25+ parejas → 8 zonas

### 2. Listar Zonas

**Endpoint:** `GET /torneos/{torneo_id}/zonas`

**Respuesta:**
```json
[
  {
    "id": 1,
    "nombre": "Zona A",
    "numero": 1,
    "parejas": [
      {
        "id": 1,
        "nombre_pareja": "Los Cracks",
        "jugador1_id": 2,
        "jugador2_id": 3,
        "estado": "confirmada"
      }
    ]
  }
]
```

### 3. Tabla de Posiciones

**Endpoint:** `GET /torneos/{torneo_id}/zonas/{zona_id}/tabla`

**Calcula:**
- Partidos jugados/ganados/perdidos
- Sets ganados/perdidos
- Games ganados/perdidos
- Puntos (3 por victoria)
- Diferencia de sets y games

**Ordenamiento:**
1. Puntos (descendente)
2. Diferencia de sets (descendente)
3. Diferencia de games (descendente)

**Respuesta:**
```json
{
  "zona_id": 1,
  "zona_nombre": "Zona A",
  "tabla": [
    {
      "posicion": 1,
      "pareja_id": 1,
      "nombre_pareja": "Los Cracks",
      "jugador1_id": 2,
      "jugador2_id": 3,
      "partidos_jugados": 3,
      "partidos_ganados": 3,
      "partidos_perdidos": 0,
      "sets_ganados": 6,
      "sets_perdidos": 0,
      "games_ganados": 36,
      "games_perdidos": 18,
      "puntos": 9
    }
  ]
}
```

### 4. Mover Pareja Entre Zonas

**Endpoint:** `POST /torneos/{torneo_id}/zonas/mover-pareja`

**Parámetros:**
- `pareja_id`: ID de la pareja a mover
- `zona_destino_id`: ID de la zona destino

**Validaciones:**
- Solo organizadores pueden mover parejas
- La zona destino debe pertenecer al mismo torneo
- Elimina la pareja de su zona actual
- La agrega a la zona destino

## Permisos

**Organizadores pueden:**
- Generar zonas
- Mover parejas entre zonas

**Todos pueden:**
- Ver zonas
- Ver tablas de posiciones

## Validaciones

### Al Generar Zonas
- ✅ Torneo debe existir
- ✅ Usuario debe ser organizador
- ✅ Torneo debe estar en estado "inscripcion"
- ✅ Mínimo 4 parejas confirmadas
- ✅ Mínimo 2 parejas por zona
- ✅ Número de zonas válido

### Al Mover Parejas
- ✅ Pareja debe existir
- ✅ Usuario debe ser organizador
- ✅ Zona destino debe existir
- ✅ Zona destino debe ser del mismo torneo

## Flujo de Uso

### 1. Crear Torneo
```bash
POST /torneos
{
  "nombre": "Torneo Verano 2024",
  "categoria": "5ta",
  "max_parejas": 16,
  ...
}
```

### 2. Inscribir Parejas
```bash
POST /torneos/1/inscribir
{
  "jugador1_id": 2,
  "jugador2_id": 3,
  "nombre_pareja": "Los Cracks"
}
```

### 3. Confirmar Parejas (Organizador)
```bash
PATCH /torneos/1/parejas/1/confirmar
```

### 4. Generar Zonas
```bash
POST /torneos/1/generar-zonas
{
  "num_zonas": 4,
  "balancear_por_rating": true
}
```

### 5. Ver Zonas
```bash
GET /torneos/1/zonas
```

### 6. Ver Tabla de Posiciones
```bash
GET /torneos/1/zonas/1/tabla
```

### 7. Mover Pareja (si es necesario)
```bash
POST /torneos/1/zonas/mover-pareja
{
  "pareja_id": 5,
  "zona_destino_id": 2
}
```

## Testing

### Ejecutar Test
```bash
cd backend
python test_torneo_zonas.py
```

### Casos de Prueba
1. ✅ Crear torneo
2. ✅ Inscribir 8 parejas
3. ✅ Confirmar parejas
4. ✅ Generar 2 zonas balanceadas
5. ✅ Listar zonas con parejas
6. ✅ Obtener tablas de posiciones
7. ✅ Mover pareja entre zonas

## Próximos Pasos

### Fase de Fixture (Siguiente)
- Generar partidos automáticamente
- Programar horarios
- Asignar canchas
- Sistema de slots de tiempo

### Fase de Resultados
- Cargar resultados de partidos
- Actualizar tablas automáticamente
- Validar sets y games
- Integrar con sistema de ELO

### Fase de Eliminación
- Determinar clasificados por zona
- Generar cuadro de eliminación
- Calcular byes
- Asignar seeds

## Ejemplos de Uso

### Generar Zonas Automáticamente
```python
from services.torneo_zona_service import TorneoZonaService

zonas = TorneoZonaService.generar_zonas_automaticas(
    db=db,
    torneo_id=1,
    user_id=1,
    num_zonas=None,  # Se calcula automáticamente
    balancear_por_rating=True
)
```

### Obtener Tabla de Posiciones
```python
tabla = TorneoZonaService.obtener_tabla_posiciones(db, zona_id=1)

for item in tabla['tabla']:
    print(f"{item['posicion']}. {item['nombre_pareja']} - {item['puntos']} pts")
```

### Mover Pareja
```python
TorneoZonaService.mover_pareja_entre_zonas(
    db=db,
    pareja_id=5,
    zona_destino_id=2,
    user_id=1
)
```

## Notas Técnicas

### Cálculo de Rating Promedio
```python
rating1 = jugador1.rating or 1200  # Default 1200 si no tiene rating
rating2 = jugador2.rating or 1200
rating_promedio = (rating1 + rating2) / 2
```

### Distribución Serpiente
```
Zona A: [1, 4, 5, 8]  (ratings: 1500, 1300, 1250, 1100)
Zona B: [2, 3, 6, 7]  (ratings: 1450, 1350, 1200, 1150)

Rating promedio Zona A: 1287.5
Rating promedio Zona B: 1287.5
```

### Ordenamiento de Tabla
```python
tabla.sort(key=lambda x: (
    -x['puntos'],                              # 1. Más puntos
    -(x['sets_ganados'] - x['sets_perdidos']), # 2. Mejor diferencia de sets
    -(x['games_ganados'] - x['games_perdidos']) # 3. Mejor diferencia de games
))
```

## Estado Actual

✅ **Completado:**
- Generación automática de zonas
- Distribución balanceada por rating
- Listado de zonas con parejas
- Tabla de posiciones con estadísticas
- Mover parejas entre zonas
- Validaciones y permisos
- Tests funcionales

🔲 **Pendiente:**
- Generación de fixture
- Programación de partidos
- Sistema de slots de tiempo
- Asignación de canchas

## Integración con Frontend

### Componentes Necesarios
- `ZonasView.tsx` - Vista de zonas
- `TablaZona.tsx` - Tabla de posiciones
- `ModalGenerarZonas.tsx` - Modal para generar zonas
- `ModalMoverPareja.tsx` - Modal para mover parejas

### Servicios
```typescript
// torneo.service.ts
async generarZonas(torneoId: number, numZonas?: number, balancear?: boolean)
async listarZonas(torneoId: number)
async obtenerTablaZona(torneoId: number, zonaId: number)
async moverPareja(torneoId: number, parejaId: number, zonaDestinoId: number)
```

---

**Implementado por:** Kiro AI
**Fecha:** 2024-11-29
**Estado:** ✅ Funcional y testeado
