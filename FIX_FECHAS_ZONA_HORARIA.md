# Fix: Problema de Zona Horaria en Fechas de Torneos

## Problema Identificado

Las fechas de los torneos se mostraban con **un día de diferencia** en el frontend:
- **Backend devolvía**: 2026-01-23 al 2026-01-25 (Viernes a Domingo) ✅
- **Frontend mostraba**: 22 al 24 de enero (Jueves a Sábado) ❌

### Causa Raíz

JavaScript interpreta `new Date("2026-01-23")` como **UTC medianoche**. Al convertirlo a hora local en Argentina (UTC-3), retrocede 3 horas, resultando en el día anterior:
- `new Date("2026-01-23")` → `2026-01-22 21:00:00 GMT-0300`

## Solución Implementada

### 1. Función Helper Global

Creado `frontend/src/utils/dateUtils.ts` con utilidades para parsear fechas correctamente:

```typescript
export function parseFechaSinZonaHoraria(fechaISO: string): Date {
  const [year, month, day] = fechaISO.split('-').map(Number);
  return new Date(year, month - 1, day); // Usa hora local
}
```

### 2. Componentes Actualizados

Se agregó la función helper y se actualizó el formateo de fechas en:

#### Frontend - Componentes de Torneos:
- ✅ `frontend/src/components/TorneoCard.tsx` - Cards de torneos en lista
- ✅ `frontend/src/pages/TorneoDetalle.tsx` - Detalle del torneo
- ✅ `frontend/src/components/ModalInscripcionTorneo.tsx` - Modal de inscripción
- ✅ `frontend/src/pages/MisTorneos.tsx` - Mis torneos
- ✅ `frontend/src/components/SelectorDisponibilidad.tsx` - Selector de días disponibles

#### Cambio Típico:
```typescript
// ❌ ANTES (con bug)
{new Date(torneo.fechaInicio).toLocaleDateString('es-ES', { ... })}

// ✅ DESPUÉS (arreglado)
{parseFechaSinZonaHoraria(torneo.fechaInicio).toLocaleDateString('es-ES', { ... })}
```

### 3. Prevención de Cache

Agregado en `frontend/src/services/torneo.service.ts`:

```typescript
// Headers anti-cache
axios.defaults.headers.common['Cache-Control'] = 'no-cache, no-store, must-revalidate';
axios.defaults.headers.common['Pragma'] = 'no-cache';
axios.defaults.headers.common['Expires'] = '0';

// Timestamp en URL para evitar cache
async obtenerTorneo(torneoId: number): Promise<Torneo> {
  const response = await axios.get(`${API_URL}/torneos/${torneoId}?_t=${Date.now()}`);
  return response.data;
}
```

## Verificación

### Backend (Correcto desde el inicio)
```bash
# Local y Producción devuelven lo mismo:
curl http://localhost:8000/torneos/24
curl https://drive-plus-production.up.railway.app/torneos/24

# Respuesta:
{
  "fecha_inicio": "2026-01-23",
  "fecha_fin": "2026-01-25",
  "horarios_disponibles": {
    "viernes": {"inicio": "15:00", "fin": "23:59"},
    "sabado": {"inicio": "09:00", "fin": "23:59"},
    "domingo": {"inicio": "09:00", "fin": "23:59"}
  }
}
```

### Frontend (Ahora Correcto)
- ✅ Fechas: **23-25 de enero 2026**
- ✅ Días disponibles: **Viernes, Sábado, Domingo**
- ✅ Horarios: Vie 15:00-23:59, Sáb/Dom 09:00-23:59

## Instrucciones para el Usuario

Si aún ves fechas incorrectas después del fix:

1. **Cierra completamente el navegador** (no solo la pestaña)
2. **Abre DevTools** (F12) → Network → Marca "Disable cache"
3. **Recarga con Ctrl + Shift + R**
4. O ejecuta en consola:
   ```javascript
   localStorage.clear();
   sessionStorage.clear();
   location.reload(true);
   ```

## Archivos Modificados

### Nuevos:
- `frontend/src/utils/dateUtils.ts` - Utilidades de fechas
- `backend/test_torneo_24_api.py` - Test de endpoint
- `backend/test_torneo_24_produccion.py` - Test producción vs local
- `frontend/test-dias-disponibles.html` - Test de cálculo de días

### Modificados:
- `frontend/src/services/torneo.service.ts` - Anti-cache
- `frontend/src/components/TorneoCard.tsx` - Fix fechas
- `frontend/src/pages/TorneoDetalle.tsx` - Fix fechas
- `frontend/src/components/ModalInscripcionTorneo.tsx` - Fix fechas
- `frontend/src/pages/MisTorneos.tsx` - Fix fechas
- `frontend/src/components/SelectorDisponibilidad.tsx` - Fix cálculo de días

## Impacto

- ✅ **Torneo Weekend (ID 24)** ahora muestra fechas correctas
- ✅ **Todos los torneos** mostrarán fechas correctas
- ✅ **Selector de disponibilidad** muestra días correctos
- ✅ **Sin más problemas de zona horaria** en fechas ISO

## Notas Técnicas

Este es un problema común en aplicaciones web que manejan fechas sin hora. La mejor práctica es:
- **Backend**: Siempre devolver fechas en formato ISO (YYYY-MM-DD)
- **Frontend**: Parsear manualmente para evitar conversiones de zona horaria
- **Nunca** usar `new Date(string)` con fechas ISO sin hora

## Testing

```bash
# Verificar backend
cd backend
python test_torneo_24_produccion.py

# Verificar frontend
# Abrir en navegador: frontend/test-dias-disponibles.html
```
