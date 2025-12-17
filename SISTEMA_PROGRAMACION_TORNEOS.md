# ✅ Sistema de Programación de Torneos - Implementado

## 🎯 Objetivo

Permitir a los organizadores gestionar canchas, horarios y programar partidos automáticamente considerando la disponibilidad de los jugadores.

---

## 📡 Endpoints Integrados

### Canchas
```typescript
// Listar canchas
GET /torneos/{id}/canchas

// Crear cancha
POST /torneos/{id}/canchas
Body: { nombre: string, activa?: boolean }

// Actualizar cancha
PUT /torneos/{id}/canchas/{cancha_id}
Body: { nombre?: string, activa?: boolean }

// Eliminar cancha
DELETE /torneos/{id}/canchas/{cancha_id}
```

### Slots de Horarios
```typescript
// Listar slots
GET /torneos/{id}/slots?cancha_id=1&fecha=2024-12-02

// Crear slot
POST /torneos/{id}/slots
Body: {
  cancha_id: number,
  fecha_hora_inicio: string,
  fecha_hora_fin: string
}

// Eliminar slot
DELETE /torneos/{id}/slots/{slot_id}
```

### Programación Automática
```typescript
// Programar partidos automáticamente
POST /torneos/{id}/programar-automatico
Body: {
  fecha_inicio?: string,
  fecha_fin?: string,
  duracion_partido_minutos?: number
}

// Obtener programación
GET /torneos/{id}/programacion
```

### Bloqueos Horarios
```typescript
// Listar bloqueos de un jugador
GET /torneos/{id}/jugadores/{jugador_id}/bloqueos

// Crear bloqueo
POST /torneos/{id}/jugadores/{jugador_id}/bloqueos
Body: {
  fecha: string,
  hora_desde: string,
  hora_hasta: string,
  motivo?: string
}

// Eliminar bloqueo
DELETE /torneos/{id}/jugadores/{jugador_id}/bloqueos/{bloqueo_id}
```

---

## 🎨 Componente Frontend

### TorneoProgramacion.tsx

**Ubicación:** `frontend/src/components/TorneoProgramacion.tsx`

**Funcionalidades:**

#### 1. Gestión de Canchas
- ✅ Listar canchas con estado (activa/inactiva)
- ✅ Crear nuevas canchas con modal
- ✅ Eliminar canchas con confirmación
- ✅ Indicador visual de estado (punto verde/gris)

#### 2. Programación Automática
- ✅ Selección de rango de fechas
- ✅ Configuración de duración de partidos
- ✅ Botón para programar automáticamente
- ✅ Considera disponibilidad horaria de jugadores
- ✅ Asigna canchas y horarios óptimos

#### 3. Visualización de Horarios
- ✅ Slots agrupados por fecha
- ✅ Indicador de ocupado/libre
- ✅ Muestra cancha y horario
- ✅ Responsive mobile

#### 4. Permisos
- ✅ Solo organizadores pueden crear/eliminar
- ✅ Todos pueden ver la programación

---

## 🔄 Integración en TorneoDetalle

### Nueva Tab "Programación"

```typescript
// Agregada entre "Fixture" y "Playoffs"
<button onClick={() => setTab('programacion')}>
  <Calendar size={16} />
  Programación
</button>
```

**Orden de Tabs:**
1. Información
2. Parejas
3. Zonas
4. Fixture
5. **Programación** ← NUEVO
6. Playoffs

---

## 📱 Diseño Responsive

### Mobile (< 768px)
- Grid de 1 columna para canchas
- Inputs de fecha apilados verticalmente
- Botones full-width
- Scroll horizontal en tabs
- Textos más pequeños (text-xs md:text-sm)

### Tablet (768px - 1024px)
- Grid de 2 columnas para canchas
- Inputs de fecha en fila
- Botones con ancho automático

### Desktop (> 1024px)
- Grid de 3 columnas para canchas
- Layout completo en fila
- Espaciado amplio

---

## 🎯 Flujo de Uso

### Para Organizadores:

1. **Configurar Canchas**
   ```
   Ir a tab "Programación" → Click "Nueva Cancha" → Ingresar nombre → Crear
   ```

2. **Programar Automáticamente**
   ```
   Seleccionar fecha inicio → Seleccionar fecha fin → 
   Configurar duración → Click "Programar Automáticamente"
   ```

3. **Resultado**
   ```
   Sistema asigna partidos a canchas y horarios considerando:
   - Disponibilidad de jugadores
   - Bloqueos horarios
   - Distribución equitativa
   - Compatibilidad horaria
   ```

### Para Jugadores:

1. **Ver Programación**
   ```
   Ir a tab "Programación" → Ver horarios asignados
   ```

2. **Bloquear Horarios** (Próximamente)
   ```
   Indicar horarios no disponibles para evitar conflictos
   ```

---

## 🔧 Servicios Agregados

### torneo.service.ts

**Nuevos Métodos:**

```typescript
// Canchas
listarCanchas(torneoId)
crearCancha(torneoId, data)
actualizarCancha(torneoId, canchaId, data)
eliminarCancha(torneoId, canchaId)

// Slots
listarSlots(torneoId, params?)
crearSlot(torneoId, data)
eliminarSlot(torneoId, slotId)

// Programación
programarPartidosAutomaticamente(torneoId, params?)
obtenerProgramacion(torneoId)

// Bloqueos
listarBloqueosJugador(torneoId, jugadorId)
crearBloqueoJugador(torneoId, jugadorId, data)
eliminarBloqueoJugador(torneoId, jugadorId, bloqueoId)
```

---

## 🎨 Características Visuales

### Canchas
```
┌─────────────────────────┐
│ 🟢 Cancha 1        🗑️  │
│ 🟢 Cancha 2        🗑️  │
│ ⚫ Cancha 3        🗑️  │
└─────────────────────────┘
```

### Programación Automática
```
┌─────────────────────────────────────┐
│ Fecha Inicio: [2024-12-02]         │
│ Fecha Fin:    [2024-12-10]         │
│ Duración:     [90] minutos         │
│                                     │
│ [Programar Automáticamente]        │
└─────────────────────────────────────┘
```

### Horarios
```
📅 Lunes 2 de Diciembre
┌─────────────────────────────────────┐
│ 🕐 09:00 - 10:30  Cancha 1  [Ocupado]│
│ 🕐 10:45 - 12:15  Cancha 1  [Libre]  │
│ 🕐 09:00 - 10:30  Cancha 2  [Ocupado]│
└─────────────────────────────────────┘
```

---

## 🐛 Manejo de Errores

```typescript
// Error al crear cancha sin nombre
"El nombre de la cancha es requerido"

// Error al programar sin fechas
"Debes seleccionar las fechas de inicio y fin"

// Error del backend
"Error al crear cancha" (muestra detail del backend)
```

---

## 🧪 Testing

### Probar Creación de Canchas:
1. Ir a torneo como organizador
2. Tab "Programación"
3. Click "Nueva Cancha"
4. Ingresar nombre
5. Verificar que aparece en la lista

### Probar Programación Automática:
1. Crear al menos 1 cancha
2. Seleccionar fechas
3. Click "Programar Automáticamente"
4. Verificar que aparecen horarios

### Probar Responsive:
1. Abrir en mobile
2. Verificar que todo se ve bien
3. Probar scroll horizontal en tabs
4. Verificar botones táctiles

---

## 📋 Checklist Backend (Para Facu)

- [ ] Endpoint GET `/torneos/{id}/canchas` existe
- [ ] Endpoint POST `/torneos/{id}/canchas` existe
- [ ] Endpoint PUT `/torneos/{id}/canchas/{cancha_id}` existe
- [ ] Endpoint DELETE `/torneos/{id}/canchas/{cancha_id}` existe
- [ ] Endpoint GET `/torneos/{id}/slots` existe
- [ ] Endpoint POST `/torneos/{id}/slots` existe
- [ ] Endpoint DELETE `/torneos/{id}/slots/{slot_id}` existe
- [ ] Endpoint POST `/torneos/{id}/programar-automatico` existe
- [ ] Endpoint GET `/torneos/{id}/programacion` existe
- [ ] Algoritmo de programación automática funciona
- [ ] Considera bloqueos horarios de jugadores
- [ ] CORS permite todos los métodos

---

## 🚀 Próximos Pasos

1. **Bloqueos Horarios UI**
   - Interfaz para que jugadores bloqueen horarios
   - Calendario visual de disponibilidad

2. **Notificaciones**
   - Avisar a jugadores cuando se programa su partido
   - Recordatorios antes del partido

3. **Reprogramación**
   - Permitir cambiar horarios de partidos
   - Validar disponibilidad al reprogramar

4. **Estadísticas**
   - Uso de canchas
   - Horarios más populares
   - Conflictos de horarios

---

**Estado**: ✅ Frontend Completo - ⏳ Esperando endpoints backend  
**Prioridad**: 🔴 Alta - Necesario para gestión de torneos  
**Complejidad**: 🟡 Media - Requiere coordinación con backend
