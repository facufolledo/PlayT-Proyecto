# Integración Frontend de Torneos - Resumen

## ✅ Cambios Realizados

### 1. Base de Datos
- ✅ Agregada columna `es_administrador` a tabla `usuarios`
- ✅ Script `marcar_administradores.py` para gestionar permisos

### 2. Frontend - Servicio
**Archivo:** `frontend/src/services/torneo.service.ts`
- ✅ Servicio completo para conectar con API de torneos
- ✅ Métodos para CRUD de torneos
- ✅ Métodos para gestión de inscripciones
- ✅ Validaciones de datos
- ✅ Tipos TypeScript para backend

### 3. Frontend - Context
**Archivo:** `frontend/src/context/TorneosContext.tsx`
- ✅ Context actualizado para usar API real
- ✅ Estado de torneos, parejas, loading y errores
- ✅ Funciones para cargar, crear, actualizar y eliminar torneos
- ✅ Funciones para gestión de inscripciones
- ✅ Permisos: `puedeCrearTorneos` y `esAdministrador`
- ✅ Adaptador de datos backend → frontend

### 4. Frontend - Tipos
**Archivo:** `frontend/src/utils/types.ts`
- ✅ Agregados tipos `TorneoBackend`, `ParejaInscripcion`, `Pareja`
- ✅ Agregados campos `puede_crear_torneos` y `es_administrador` a `Usuario`

### 5. Frontend - Componentes
**Archivo:** `frontend/src/components/ModalCrearTorneo.tsx`
- ✅ Actualizado para usar el servicio real
- ✅ Preparación de datos para backend
- ✅ Manejo de errores

**Archivo:** `frontend/src/pages/Torneos.tsx`
- ✅ Botón "Crear Torneo" solo visible para usuarios con permisos
- ✅ Mensajes adaptados según permisos del usuario

## 🎯 Funcionalidades Implementadas

### Para Administradores
- ✅ Crear torneos
- ✅ Editar torneos
- ✅ Eliminar torneos
- ✅ Cambiar estado de torneos
- ✅ Gestionar inscripciones (confirmar/rechazar)
- ✅ Ver estadísticas

### Para Organizadores de Torneos
- ✅ Crear torneos
- ✅ Gestionar sus propios torneos
- ✅ Gestionar inscripciones de sus torneos

### Para Usuarios Normales
- ✅ Ver torneos disponibles
- ✅ Inscribirse en torneos (próximamente)
- ✅ Ver detalles de torneos

## 📋 Próximos Pasos

### 1. Marcar Administradores
```bash
cd backend
python marcar_administradores.py
```
Este script te permitirá:
- Ver todos los usuarios
- Marcar usuarios específicos como administradores
- Los administradores automáticamente pueden crear torneos

### 2. Componentes Faltantes

#### a) Página de Detalle de Torneo
**Archivo:** `frontend/src/pages/TorneoDetalle.tsx`
- Mostrar información completa del torneo
- Lista de parejas inscritas
- Botón de inscripción (si está abierto)
- Gestión de inscripciones (si es organizador/admin)
- Bracket/Zonas (cuando esté en fase de juego)

#### b) Modal de Inscripción
**Archivo:** `frontend/src/components/ModalInscribirPareja.tsx`
- Formulario para inscribir pareja
- Selector de jugadores
- Campo de observaciones
- Validaciones

#### c) Componente de Lista de Parejas
**Archivo:** `frontend/src/components/ListaParejas.tsx`
- Mostrar parejas inscritas
- Botones de confirmar/rechazar (si es organizador)
- Estados visuales (inscripta, confirmada, baja)

#### d) Componente de Bracket
**Archivo:** `frontend/src/components/BracketTorneo.tsx`
- Visualización de zonas
- Visualización de fase eliminatoria
- Actualización de resultados

### 3. Endpoints del Backend a Usar

#### Torneos
- `GET /torneos` - Listar torneos ✅
- `GET /torneos/{id}` - Obtener torneo ✅
- `POST /torneos` - Crear torneo ✅
- `PUT /torneos/{id}` - Actualizar torneo ✅
- `DELETE /torneos/{id}` - Eliminar torneo ✅
- `PATCH /torneos/{id}/estado` - Cambiar estado ✅
- `GET /torneos/{id}/estadisticas` - Estadísticas ✅

#### Inscripciones
- `POST /torneos/{id}/inscribir` - Inscribir pareja ✅
- `GET /torneos/{id}/parejas` - Listar parejas ✅
- `PATCH /torneos/{id}/parejas/{pareja_id}/confirmar` - Confirmar ✅
- `DELETE /torneos/{id}/parejas/{pareja_id}/rechazar` - Rechazar ✅
- `PATCH /torneos/{id}/parejas/{pareja_id}/baja` - Dar de baja ✅

#### Zonas y Partidos
- `POST /torneos/{id}/armar-zonas` - Armar zonas
- `GET /torneos/{id}/zonas` - Ver zonas
- `POST /torneos/{id}/iniciar-fase-grupos` - Iniciar fase de grupos
- `POST /torneos/{id}/iniciar-fase-eliminacion` - Iniciar eliminación
- `GET /torneos/{id}/partidos` - Listar partidos del torneo

## 🔐 Sistema de Permisos

### Niveles de Acceso
1. **Administrador** (`es_administrador = true`)
   - Acceso total a todos los torneos
   - Puede marcar otros usuarios como organizadores
   - Puede eliminar cualquier torneo

2. **Organizador** (`puede_crear_torneos = true`)
   - Puede crear torneos
   - Puede gestionar sus propios torneos
   - Puede gestionar inscripciones de sus torneos

3. **Usuario Normal**
   - Puede ver torneos
   - Puede inscribirse en torneos
   - Puede ver sus inscripciones

### Verificación en Frontend
```typescript
const { puedeCrearTorneos, esAdministrador } = useTorneos();

// Mostrar botón crear solo si tiene permisos
{(puedeCrearTorneos || esAdministrador) && (
  <Button onClick={crearTorneo}>Crear Torneo</Button>
)}
```

## 🧪 Testing

### Probar Creación de Torneo
1. Marcar tu usuario como administrador
2. Ir a `/torneos`
3. Click en "Nuevo Torneo"
4. Llenar formulario
5. Verificar que aparece en la lista

### Probar Permisos
1. Crear usuario sin permisos
2. Verificar que NO ve botón "Crear Torneo"
3. Marcar como organizador
4. Verificar que SÍ ve botón "Crear Torneo"

## 📝 Notas Importantes

1. **Adaptación de Estados**
   - Backend: `INSCRIPCION`, `ARMANDO_ZONAS`, `FASE_GRUPOS`, etc.
   - Frontend: `programado`, `activo`, `finalizado`
   - El context hace la conversión automáticamente

2. **IDs**
   - Backend usa `number`
   - Frontend usa `string` (por compatibilidad con código existente)
   - El servicio hace la conversión

3. **Fechas**
   - Backend espera formato `YYYY-MM-DD`
   - Frontend usa `<input type="date">` que ya devuelve ese formato

4. **Validaciones**
   - Validaciones básicas en frontend (UX)
   - Validaciones completas en backend (seguridad)

## 🚀 Cómo Continuar

1. **Marcar administradores:**
   ```bash
   cd backend
   python marcar_administradores.py
   ```

2. **Probar creación de torneo:**
   - Iniciar frontend
   - Login con usuario administrador
   - Ir a Torneos
   - Crear torneo de prueba

3. **Implementar página de detalle:**
   - Crear `TorneoDetalle.tsx`
   - Mostrar información completa
   - Agregar botón de inscripción

4. **Implementar inscripciones:**
   - Crear modal de inscripción
   - Conectar con endpoint
   - Mostrar lista de parejas

5. **Implementar gestión de zonas:**
   - Botón "Armar Zonas" (solo organizador)
   - Visualización de zonas
   - Inicio de fase de grupos

¿Por dónde querés seguir? 🎾
