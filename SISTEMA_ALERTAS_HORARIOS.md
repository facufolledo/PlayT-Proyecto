# Sistema de Alertas por Incompatibilidad Horaria

## Descripción

Sistema implementado para detectar y alertar cuando parejas no pueden ser programadas en el fixture debido a incompatibilidad en sus horarios disponibles.

## Cambios Realizados

### Backend

#### 1. `backend/src/services/torneo_fixture_global_service.py`

**Método `generar_fixture_completo()`:**
- Ahora retorna información sobre partidos no programados
- Campos agregados al resultado:
  - `partidos_no_programados`: Cantidad de partidos sin programar
  - `partidos_sin_programar`: Lista detallada con información de cada partido no programado

**Método `_asignar_horarios_y_canchas()`:**
- Cambio de tipo de retorno: de `List[Dict]` a `Dict`
- Ahora retorna:
  ```python
  {
    "partidos_programados": [...],
    "partidos_no_programados": [...]
  }
  ```
- Cuando un partido no puede programarse, se agrega a `partidos_no_programados` con:
  - `zona_id`, `zona_nombre`, `categoria_id`
  - `pareja1_id`, `pareja2_id`
  - `pareja1_nombre`, `pareja2_nombre`
  - `motivo`: "Sin horarios compatibles"
  - `disponibilidad_pareja1`: Lista de slots disponibles o "Sin restricciones"
  - `disponibilidad_pareja2`: Lista de slots disponibles o "Sin restricciones"

#### 2. `backend/src/controllers/torneo_controller.py`

**Endpoint `POST /torneos/{torneo_id}/generar-fixture`:**
- Ahora retorna información adicional:
  - `partidos_no_programados`: Cantidad
  - `partidos_sin_programar`: Detalles (si existen)
  - `warning`: Mensaje de advertencia (si hay partidos sin programar)

Ejemplo de respuesta:
```json
{
  "message": "Fixture generado exitosamente",
  "partidos_generados": 45,
  "partidos_no_programados": 3,
  "zonas_procesadas": 4,
  "canchas_utilizadas": 3,
  "slots_utilizados": 18,
  "partidos_sin_programar": [
    {
      "zona_nombre": "Zona A - 8va Masculino",
      "pareja1_nombre": "Facundo Folledo / Facundito Folledo",
      "pareja2_nombre": "Juan Pérez / Pedro García",
      "motivo": "Sin horarios compatibles",
      "disponibilidad_pareja1": [["jueves", "19:00"], ["jueves", "19:50"], ...],
      "disponibilidad_pareja2": "Sin restricciones"
    }
  ],
  "warning": "⚠️ 3 partidos no pudieron programarse por incompatibilidad horaria"
}
```

### Frontend

#### 3. `frontend/src/components/TorneoFixture.tsx`

**Estado agregado:**
```typescript
const [partidosNoProgramados, setPartidosNoProgramados] = useState<any[]>([]);
```

**Función `generarFixture()` actualizada:**
- Captura `partidos_sin_programar` de la respuesta del backend
- Guarda en estado para mostrar alerta

**Alerta visual agregada:**
- Se muestra cuando `partidosNoProgramados.length > 0`
- Diseño con fondo amarillo y borde amarillo (warning)
- Muestra:
  - Cantidad de partidos no programados
  - Lista de cada partido con:
    - Zona
    - Nombres de las parejas
    - Motivo
    - Disponibilidad horaria de cada pareja (primeros 3 slots)
  - Sugerencia para resolver el problema
- Botón para cerrar la alerta (X)

**Características de la alerta:**
- Animación de entrada (fade in + slide down)
- Responsive (se adapta a mobile)
- Información clara y concisa
- Colores consistentes con el sistema de diseño (yellow-500)

## Flujo de Uso

1. **Organizador genera fixture:**
   - Click en "Generar Fixture"
   - Backend procesa todas las zonas y parejas

2. **Backend detecta incompatibilidades:**
   - Para cada partido, verifica disponibilidad de ambas parejas
   - Si no hay horarios compatibles, NO programa el partido
   - Guarda información detallada del partido no programado

3. **Frontend muestra alerta:**
   - Si hay partidos sin programar, muestra alerta amarilla
   - Lista cada partido con detalles
   - Sugiere soluciones

4. **Organizador toma acción:**
   - Contacta a las parejas para ajustar horarios
   - O regenera zonas con sistema inteligente (agrupa por compatibilidad)

## Ventajas

✅ **Transparencia:** El organizador sabe exactamente qué partidos no se pudieron programar y por qué

✅ **Información detallada:** Muestra la disponibilidad de cada pareja para facilitar la resolución

✅ **Prevención de errores:** No se programan partidos en horarios incompatibles

✅ **Sugerencias útiles:** Guía al organizador sobre cómo resolver el problema

✅ **UX mejorada:** Alerta visual clara y fácil de entender

## Testing

Script de prueba creado: `backend/test_partidos_no_programados.py`

Ejecutar:
```bash
cd backend
python test_partidos_no_programados.py
```

## Relación con Sistema de Zonas Inteligente

Este sistema complementa el **Sistema de Generación de Zonas con Compatibilidad Horaria** (`TorneoZonaHorariosService`):

- **Zonas inteligentes:** Agrupa parejas con horarios compatibles en la misma zona
- **Alertas de fixture:** Detecta cuando aún así hay incompatibilidades

**Recomendación:** Usar ambos sistemas en conjunto:
1. Generar zonas con sistema inteligente (`POST /torneos/{id}/generar-zonas-inteligente`)
2. Generar fixture (`POST /torneos/{id}/generar-fixture`)
3. Si hay alertas, ajustar horarios y regenerar

## Próximas Mejoras Sugeridas

- [ ] Agregar botón "Contactar parejas" que envíe notificación automática
- [ ] Mostrar sugerencias de horarios alternativos
- [ ] Permitir programación manual de partidos no programados
- [ ] Estadísticas de compatibilidad horaria por zona
- [ ] Exportar reporte de incompatibilidades en PDF

## Notas Técnicas

- La disponibilidad horaria se almacena en `TorneoPareja.disponibilidad_horaria` (JSON)
- Formato: `{"franjas": [{"dias": ["jueves", "viernes"], "horaInicio": "19:00", "horaFin": "22:00"}]}`
- Set vacío = sin restricciones (disponible en cualquier horario del torneo)
- La zona horaria es Argentina (America/Argentina/Buenos_Aires, UTC-3)
