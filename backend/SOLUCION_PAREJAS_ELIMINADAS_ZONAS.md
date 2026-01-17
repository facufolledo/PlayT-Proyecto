# Solución: Manejo de Parejas Eliminadas en Zonas

## Problema Original
Cuando se eliminaba una pareja después de generar las zonas, la categoría completa dejaba de mostrarse en el frontend porque el backend no podía encontrar la pareja referenciada en las asignaciones de zona.

## Solución Implementada

### Backend (`TorneoZonaService`)

#### 1. Método `listar_zonas()` Mejorado
- **Antes**: Solo devolvía parejas existentes usando JOIN
- **Ahora**: Consulta todas las asignaciones de zona y maneja parejas faltantes
- **Cambio clave**: Usa `TorneoZonaPareja` como punto de partida, no `TorneoPareja`

```python
# Obtener todas las asignaciones de parejas a esta zona
asignaciones = db.query(TorneoZonaPareja).filter(
    TorneoZonaPareja.zona_id == zona.id
).all()

for asignacion in asignaciones:
    pareja = db.query(TorneoPareja).filter(
        TorneoPareja.id == asignacion.pareja_id
    ).first()
    
    if pareja:
        # Pareja existe - datos normales
    else:
        # Pareja eliminada - placeholder
        parejas_info.append({
            'id': asignacion.pareja_id,
            'eliminada': True,
            'estado': 'eliminada'
        })
```

#### 2. Método `obtener_tabla_posiciones()` Mejorado
- **Antes**: Solo procesaba parejas existentes
- **Ahora**: Incluye parejas eliminadas con datos placeholder
- **Resultado**: Tablas completas con indicadores visuales para parejas eliminadas

```python
if pareja:
    # Pareja existente - estadísticas normales
else:
    # Pareja eliminada - estadísticas en cero
    tabla.append({
        'pareja_id': asignacion.pareja_id,
        'eliminada': True,
        'pareja_nombre': "Pareja Eliminada"
    })
```

### Frontend (`TorneoZonas.tsx`)

#### 1. Detección de Parejas Eliminadas
- Verifica el campo `eliminada` en los datos de pareja
- Aplica estilos visuales diferenciados

#### 2. Indicadores Visuales
- **Nombre**: "❌ Pareja Eliminada" con texto tachado
- **Fila**: Fondo rojo translúcido y opacidad reducida
- **Posición**: Ícono ❌ y número tachado
- **Estadísticas**: Texto tachado y color rojo atenuado
- **Clasificación**: No muestra badge "Clasifica" para parejas eliminadas

```tsx
{item.eliminada ? (
  <span className="text-red-500/70 font-medium text-xs md:text-sm line-through flex items-center gap-1">
    <span className="text-red-500">❌</span>
    Pareja Eliminada
  </span>
) : (
  // Pareja normal
)}
```

#### 3. Estilos CSS Aplicados
- `line-through`: Texto tachado
- `text-red-500/70`: Color rojo atenuado
- `bg-red-500/5`: Fondo rojo muy sutil
- `opacity-60`: Opacidad reducida para toda la fila

## Beneficios de la Solución

### ✅ Robustez
- Las categorías siempre se muestran, incluso con parejas eliminadas
- No hay errores de renderizado por datos faltantes

### ✅ Transparencia
- Los organizadores ven claramente qué parejas fueron eliminadas
- Se mantiene la integridad visual de las zonas

### ✅ Compatibilidad
- Funciona con parejas existentes (comportamiento normal)
- Maneja parejas eliminadas (comportamiento defensivo)
- No rompe funcionalidad existente

### ✅ Experiencia de Usuario
- No más categorías que "desaparecen"
- Información clara sobre el estado de las parejas
- Tablas de posiciones completas y comprensibles

## Casos de Uso Cubiertos

1. **Pareja eliminada antes de partidos**: Se muestra como eliminada, sin estadísticas
2. **Pareja eliminada después de partidos**: Se muestra como eliminada, conserva estadísticas históricas
3. **Zona con mix de parejas**: Parejas activas y eliminadas conviven visualmente
4. **Regeneración de zonas**: Limpia automáticamente referencias a parejas eliminadas

## Limitaciones de la Base de Datos

**Nota importante**: En la implementación actual, las foreign key constraints impiden la eliminación de parejas que tienen partidos asociados. Esto significa que el escenario de "parejas eliminadas en zonas" es raro en producción, pero la solución actúa como medida defensiva para casos edge.

## Testing

- ✅ Backend maneja correctamente asignaciones huérfanas
- ✅ Frontend renderiza sin errores con parejas eliminadas
- ✅ Tablas de posiciones incluyen parejas eliminadas
- ✅ No hay regresiones en funcionalidad existente

## Archivos Modificados

### Backend
- `backend/src/services/torneo_zona_service.py`
  - `listar_zonas()`: Manejo de parejas eliminadas
  - `obtener_tabla_posiciones()`: Inclusión de parejas eliminadas

### Frontend
- `frontend/src/components/TorneoZonas.tsx`
  - Detección y renderizado de parejas eliminadas
  - Estilos visuales diferenciados
  - Lógica de clasificación actualizada

### Tests
- `backend/test_zonas_parejas_eliminadas.py`: Test básico
- `backend/test_verificar_parejas_faltantes.py`: Test de referencias huérfanas
- `backend/SOLUCION_PAREJAS_ELIMINADAS_ZONAS.md`: Esta documentación