# Resumen: Sistema de Torneos - Sesión Actual

## ✅ Lo que implementamos HOY

### Backend Completo

#### 1. Base de Datos
- ✅ 12 tablas de torneos creadas en PostgreSQL
- ✅ Tabla `partidos` extendida para soportar torneos
- ✅ Tabla `partido_sets` para guardar sets
- ✅ Columnas en `usuarios`:
  - `puede_crear_torneos` (BOOLEAN) - Para organizadores de torneos
  - `es_administrador` (BOOLEAN) - Para administradores del sistema (vos y tu amigo)

#### 2. Servicios Implementados
- ✅ `torneo_service.py` - CRUD básico de torneos
- ✅ `torneo_inscripcion_service.py` - Sistema de inscripciones

#### 3. Endpoints REST (15+ endpoints)

**Gestión de Torneos:**
- `POST /torneos` - Crear torneo (solo organizadores autorizados)
- `GET /torneos` - Listar torneos (público)
- `GET /torneos/{id}` - Obtener torneo (público)
- `PUT /torneos/{id}` - Actualizar torneo (solo organizadores del torneo)
- `DELETE /torneos/{id}` - Eliminar torneo (solo owner)
- `PATCH /torneos/{id}/estado` - Cambiar estado
- `GET /torneos/{id}/estadisticas` - Estadísticas del torneo

**Organizadores:**
- `POST /torneos/{id}/organizadores` - Agregar organizador
- `DELETE /torneos/{id}/organizadores/{id}` - Remover organizador
- `GET /torneos/{id}/organizadores` - Listar organizadores

**Inscripciones:**
- `POST /torneos/{id}/inscribir` - Inscribir pareja
- `GET /torneos/{id}/parejas` - Listar parejas
- `PATCH /torneos/{id}/parejas/{id}/confirmar` - Confirmar pareja (organizador)
- `DELETE /torneos/{id}/parejas/{id}/rechazar` - Rechazar pareja (organizador)
- `PATCH /torneos/{id}/parejas/{id}/baja` - Dar de baja pareja
- `PATCH /torneos/{id}/parejas/{id}/reemplazar-jugador` - Reemplazar jugador
- `PUT /torneos/{id}/parejas/{id}` - Actualizar pareja

#### 4. Tests Funcionando
- ✅ `test_torneo_basico.py` - CRUD de torneos
- ✅ `test_torneo_inscripciones.py` - Inscripciones

## 🎯 Roles y Permisos

### Administrador (`es_administrador = true`)
- Acceso total a todo el sistema
- Puede autorizar organizadores de torneos
- Puede gestionar cualquier torneo
- Solo vos y tu amigo

### Organizador de Torneos (`puede_crear_torneos = true`)
- Puede crear torneos
- Puede gestionar sus propios torneos
- Puede confirmar/rechazar inscripciones
- Puede cargar resultados
- Puede editar fixture

### Usuario Normal
- Puede inscribirse en torneos
- Puede ver torneos públicos
- Puede dar de baja su propia pareja
- Puede jugar partidos

## 📋 Frontend a Implementar

### Páginas Necesarias

#### 1. `/torneos` - Listado de Torneos
**Para todos los usuarios:**
- Card de cada torneo con:
  - Nombre, categoría, fechas
  - Estado (inscripción, en curso, finalizado)
  - Cantidad de parejas inscritas
  - Botón "Ver detalles"
  - Botón "Inscribirse" (si está en inscripción)

**Para organizadores:**
- Botón "Crear Torneo" (solo si `puede_crear_torneos = true`)

**Para administradores:**
- Botón "Panel Admin" (solo si `es_administrador = true`)

#### 2. `/torneos/crear` - Crear Torneo
**Solo organizadores autorizados**
- Formulario:
  - Nombre del torneo
  - Descripción
  - Categoría
  - Fecha inicio / fin
  - Lugar
  - Reglas (JSON opcional)

#### 3. `/torneos/{id}` - Vista del Torneo
**Para todos:**
- Información del torneo
- Lista de parejas inscritas
- Fixture (cuando esté generado)
- Resultados

**Para jugadores:**
- Botón "Inscribirse" (si está en inscripción)
- Botón "Dar de baja mi pareja" (si está inscrito)

**Para organizadores del torneo:**
- Botón "Gestionar" → va a panel de admin

#### 4. `/torneos/{id}/inscribir` - Inscribir Pareja
**Para usuarios logueados:**
- Selector de compañero
- Campo de observaciones
- Botón "Inscribirse"

#### 5. `/torneos/{id}/admin` - Panel de Administración
**Solo organizadores del torneo:**

**Tabs:**
- **Inscripciones:**
  - Lista de parejas inscritas/confirmadas
  - Botones: Confirmar, Rechazar, Reemplazar jugador
  
- **Zonas:** (próximo paso)
  - Botón "Generar Zonas"
  - Vista de zonas generadas
  - Tabla de posiciones por zona
  
- **Fixture:** (próximo paso)
  - Definir canchas
  - Definir horarios
  - Programar partidos
  
- **Resultados:** (próximo paso)
  - Cargar resultados de partidos
  - Ver historial

- **Configuración:**
  - Editar datos del torneo
  - Agregar/remover organizadores
  - Cambiar estado

#### 6. `/admin/torneos` - Panel de Administración Global
**Solo administradores (`es_administrador = true`):**
- Gestionar organizadores autorizados
- Ver todos los torneos
- Estadísticas globales

### Componentes a Crear

```typescript
// Componentes de Torneo
- TorneoCard.tsx          // Card para listado
- TorneoDetalle.tsx       // Vista detallada
- FormCrearTorneo.tsx     // Formulario crear/editar
- FormInscribir.tsx       // Formulario inscripción
- ListaParejas.tsx        // Lista de parejas inscritas
- ParejaCard.tsx          // Card de pareja

// Componentes de Admin
- PanelAdminTorneo.tsx    // Panel principal
- TabInscripciones.tsx    // Tab de inscripciones
- TabZonas.tsx            // Tab de zonas (próximo)
- TabFixture.tsx          // Tab de fixture (próximo)
- TabResultados.tsx       // Tab de resultados (próximo)

// Componentes Compartidos
- EstadoBadge.tsx         // Badge de estado del torneo
- CategoriaBadge.tsx      // Badge de categoría
```

### Servicios a Crear

```typescript
// frontend/src/services/torneo.service.ts
export const torneoService = {
  // Torneos
  listarTorneos: (filtros?) => Promise<Torneo[]>
  obtenerTorneo: (id) => Promise<Torneo>
  crearTorneo: (data) => Promise<Torneo>
  actualizarTorneo: (id, data) => Promise<Torneo>
  eliminarTorneo: (id) => Promise<void>
  
  // Inscripciones
  inscribirPareja: (torneoId, data) => Promise<Pareja>
  listarParejas: (torneoId) => Promise<Pareja[]>
  confirmarPareja: (torneoId, parejaId) => Promise<Pareja>
  rechazarPareja: (torneoId, parejaId) => Promise<void>
  darBajaPareja: (torneoId, parejaId, motivo) => Promise<Pareja>
  reemplazarJugador: (torneoId, parejaId, data) => Promise<Pareja>
  
  // Estadísticas
  obtenerEstadisticas: (torneoId) => Promise<Estadisticas>
}
```

### Context a Crear

```typescript
// frontend/src/context/TorneosContext.tsx
interface TorneosContextType {
  torneos: Torneo[]
  torneoActual: Torneo | null
  loading: boolean
  error: string | null
  
  // Acciones
  cargarTorneos: () => Promise<void>
  cargarTorneo: (id: number) => Promise<void>
  crearTorneo: (data: TorneoCreate) => Promise<Torneo>
  inscribirPareja: (torneoId: number, data: ParejaInscripcion) => Promise<void>
  
  // Permisos
  puedeCrearTorneos: boolean
  esAdministrador: boolean
  esOrganizadorDe: (torneoId: number) => boolean
}
```

### Rutas a Agregar en App.tsx

```typescript
// Rutas públicas
<Route path="/torneos" element={<Torneos />} />
<Route path="/torneos/:id" element={<TorneoDetalle />} />

// Rutas protegidas (requieren login)
<Route path="/torneos/:id/inscribir" element={<ProtectedRoute><InscribirPareja /></ProtectedRoute>} />

// Rutas de organizador (requieren puede_crear_torneos)
<Route path="/torneos/crear" element={<OrganizadorRoute><CrearTorneo /></OrganizadorRoute>} />
<Route path="/torneos/:id/admin" element={<OrganizadorRoute><AdminTorneo /></OrganizadorRoute>} />

// Rutas de administrador (requieren es_administrador)
<Route path="/admin/torneos" element={<AdminRoute><AdminGlobal /></AdminRoute>} />
```

## 🔄 Flujo de Usuario

### Jugador Normal
1. Ve listado de torneos en `/torneos`
2. Click en un torneo → `/torneos/{id}`
3. Click "Inscribirse" → `/torneos/{id}/inscribir`
4. Selecciona compañero y se inscribe
5. Espera confirmación del organizador
6. Ve fixture cuando se genere
7. Juega sus partidos

### Organizador de Torneo
1. Click "Crear Torneo" → `/torneos/crear`
2. Llena formulario y crea torneo
3. Comparte link del torneo
4. Jugadores se inscriben
5. Va a `/torneos/{id}/admin`
6. Confirma/rechaza parejas
7. Cuando tiene suficientes, genera zonas
8. Programa partidos
9. Carga resultados
10. Genera cuadro final
11. Declara campeón

### Administrador
1. Puede hacer todo lo anterior
2. Además accede a `/admin/torneos`
3. Autoriza nuevos organizadores
4. Gestiona todos los torneos
5. Ve estadísticas globales

## 📊 Estados del Torneo

```typescript
enum EstadoTorneo {
  INSCRIPCION = 'inscripcion',        // Abierto a inscripciones
  ARMANDO_ZONAS = 'armando_zonas',    // Organizador armando zonas
  FASE_GRUPOS = 'fase_grupos',        // Jugando fase de grupos
  FASE_ELIMINACION = 'fase_eliminacion', // Jugando eliminación
  FINALIZADO = 'finalizado'           // Torneo terminado
}
```

## 🎨 Diseño Sugerido

### Colores por Estado
- Inscripción: Verde (#10b981)
- En curso: Azul (#3b82f6)
- Finalizado: Gris (#6b7280)

### Iconos
- Torneo: 🏆
- Inscripción: ✍️
- Parejas: 👥
- Fixture: 📅
- Resultados: 📊
- Admin: ⚙️

## 🚀 Próximos Pasos Backend (después del frontend)

1. **Generación de Zonas** - Algoritmo para dividir parejas
2. **Programación de Partidos** - Fixture automático con restricciones
3. **Resultados** - Integración con ELO
4. **Fase de Eliminación** - Cuadros finales con byes

## 📝 Notas Importantes

- Los administradores (`es_administrador`) tienen acceso a TODO
- Los organizadores (`puede_crear_torneos`) solo a sus torneos
- Las inscripciones están abiertas hasta que el organizador cierre
- Los jugadores pueden darse de baja hasta que empiece el torneo
- El historial de cambios registra TODO para auditoría
