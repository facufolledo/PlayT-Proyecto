# 🎨 Componentes del Sistema de Salas

## Estructura de Componentes

```
frontend/src/components/
├── ModalCrearSala.tsx          ✅ Actualizado
├── ModalUnirseSala.tsx         ✅ Nuevo
├── SalaEspera.tsx              ✅ Actualizado
├── AsignarEquipos.tsx          ✅ Actualizado
├── MarcadorInteractivo.tsx     ✅ Existente
├── ModalReportarResultado.tsx  ✅ Nuevo
├── ModalConfirmarResultado.tsx ✅ Actualizado
└── SalaCard.tsx                ✅ Actualizado
```

## 1. ModalCrearSala

### Props
```typescript
interface ModalCrearSalaProps {
  isOpen: boolean;
  onClose: () => void;
  onSalaCreada?: (salaId: string, codigo: string) => void;
}
```

### Funcionalidad
- Formulario con 3 campos: nombre, fecha, hora
- Genera código de invitación automático (6 caracteres)
- Muestra pantalla de confirmación con código
- Botones para compartir: Copiar, WhatsApp, Link

### Estados
1. **Formulario**: Ingreso de datos
2. **Confirmación**: Código generado y opciones de compartir

---

## 2. ModalUnirseSala

### Props
```typescript
interface ModalUnirseSalaProps {
  isOpen: boolean;
  onClose: () => void;
  onUnido?: (salaId: string) => void;
}
```

### Funcionalidad
- Input para código de 6 caracteres
- Validación en tiempo real
- Mensajes de error específicos:
  - Código inválido
  - Sala llena
  - Ya estás en la sala
  - Sala no disponible

### Validaciones
- Longitud exacta de 6 caracteres
- Solo letras y números
- Conversión automática a mayúsculas

---

## 3. SalaEspera

### Props
```typescript
interface SalaEsperaProps {
  sala: Sala;
  onAsignarEquipos: () => void;
  onIniciarPartido: () => void;
  onSalir: () => void;
}
```

### Secciones

#### Header
- Nombre de la sala
- Fecha y hora del partido
- Código de invitación (grande y destacado)
- Botones de compartir

#### Lista de Jugadores
- Avatar generado con inicial
- Nombre del jugador
- Rating
- Indicador de creador (👑)
- Slots vacíos con placeholder

#### Acciones
- **Todos**: Salir de la sala
- **Solo Creador**:
  - Asignar Equipos (cuando hay 4 jugadores)
  - Iniciar Partido (cuando equipos asignados)

### Estados Visuales
- Contador de jugadores (X/4)
- Indicador de actualización en tiempo real
- Alertas cuando falta completar jugadores

---

## 4. AsignarEquipos

### Props
```typescript
interface AsignarEquiposProps {
  isOpen: boolean;
  onClose: () => void;
  sala: Sala;
  onGuardar: (equipo1: string[], equipo2: string[]) => void;
}
```

### Funcionalidad
- Drag & drop de jugadores entre equipos
- Click para seleccionar y asignar
- Asignación automática balanceada
- Cálculo de rating promedio por equipo
- Indicador de balance (diferencia ≤100 puntos)

### Validaciones
- 2 jugadores por equipo obligatorio
- No puede haber equipos vacíos
- Todos los jugadores deben estar asignados

### Visual
- Equipo 1: Color azul/primary
- Equipo 2: Color rosa/secondary
- Indicador de balance con colores

---

## 5. MarcadorInteractivo

### Props
```typescript
interface MarcadorInteractivoProps {
  isOpen: boolean;
  onClose: () => void;
  sala: Sala | null;
}
```

### Funcionalidad
- Marcador en tiempo real
- Botones +/- para cada equipo
- Botón de reiniciar
- Botón de finalizar (solo creador)
- Animaciones en cambios de puntos

### Visual
- Diseño estilo eSports
- Números grandes y legibles
- Efectos de glow
- Animaciones suaves

---

## 6. ModalReportarResultado

### Props
```typescript
interface ModalReportarResultadoProps {
  isOpen: boolean;
  onClose: () => void;
  sala: Sala | null;
}
```

### Funcionalidad
- Formulario para 3 sets
- Inputs numéricos (0-7)
- Validación de puntos por set:
  - Mínimo 6 games para ganar
  - No empates
  - Reglas de tie-break
- Cálculo automático de ganador
- Resumen visual

### Validaciones
```typescript
// Ejemplos válidos
6-0, 6-1, 6-2, 6-3, 6-4  // Victoria clara
7-5, 7-6                  // Victoria ajustada
```

### Visual
- Inputs grandes y claros
- Resumen con sets ganados
- Indicador de ganador
- Reglas de validación visibles

---

## 7. ModalConfirmarResultado

### Props
```typescript
interface ModalConfirmarResultadoProps {
  isOpen: boolean;
  onClose: () => void;
  sala: Sala | null;
}
```

### Funcionalidad
- Muestra resultado final
- Detalle por sets
- Estado de confirmación por equipo
- Botón confirmar / disputar
- Formulario de disputa con motivo

### Estados
1. **Pendiente**: Esperando confirmación
2. **Confirmado**: Ya confirmaste
3. **Disputa**: Formulario de motivo

### Visual
- Resultado destacado
- Sets en grid
- Indicadores de confirmación (✓)
- Formulario de disputa expandible

---

## 8. SalaCard

### Props
```typescript
interface SalaCardProps {
  sala: Sala;
  onOpenMarcador: (sala: Sala) => void;
}
```

### Funcionalidad
- Vista compacta de sala
- Diferentes vistas según estado:
  - **Esperando**: Lista de jugadores + código
  - **Activa/Programada/Finalizada**: Marcador

### Estados Visuales
- **Esperando**: Morado/Rosa
- **Activa**: Rosa/Secondary
- **Programada**: Azul/Primary
- **Finalizada**: Amarillo/Accent

### Acciones
- Ver/Iniciar según estado
- Eliminar sala

---

## 🎨 Estilos Comunes

### Colores
```typescript
primary: Azul (#3B82F6)
secondary: Rosa (#EC4899)
accent: Amarillo (#F59E0B)
purple: Morado (#A855F7) // Nuevo para "esperando"
```

### Animaciones
- Framer Motion para todas las transiciones
- Efectos de hover con scale
- Glow effects en bordes
- Animaciones de entrada/salida

### Responsive
- Mobile first
- Grid adaptativo
- Botones apilados en móvil
- Modales con scroll

---

## 📱 Flujo de Uso

```
1. Usuario hace click en "Nueva Sala"
   ↓
2. ModalCrearSala se abre
   ↓
3. Ingresa nombre, fecha, hora
   ↓
4. Sistema genera código
   ↓
5. Pantalla de confirmación con opciones de compartir
   ↓
6. Usuario comparte código
   ↓
7. Otros usuarios hacen click en "Unirse a Sala"
   ↓
8. ModalUnirseSala se abre
   ↓
9. Ingresan código de 6 caracteres
   ↓
10. Sistema valida y une a la sala
    ↓
11. SalaEspera muestra jugadores en tiempo real
    ↓
12. Cuando hay 4 jugadores, creador asigna equipos
    ↓
13. AsignarEquipos permite organizar equipos
    ↓
14. Creador inicia partido
    ↓
15. MarcadorInteractivo para jugar
    ↓
16. Creador reporta resultado
    ↓
17. ModalReportarResultado con sets
    ↓
18. Todos confirman resultado
    ↓
19. ModalConfirmarResultado
    ↓
20. Partido finalizado ✅
```

---

## 🔧 Integración con Contexto

### SalasContext
```typescript
// Funciones utilizadas
addSala()              // ModalCrearSala
unirseASala()          // ModalUnirseSala
asignarEquipos()       // AsignarEquipos
updateMarcador()       // MarcadorInteractivo
finalizarPartido()     // ModalReportarResultado
confirmarResultado()   // ModalConfirmarResultado
disputarResultado()    // ModalConfirmarResultado
```

### AuthContext
```typescript
// Datos utilizados
usuario.id
usuario.nombre
usuario.rating (opcional)
```

---

**Documentación actualizada**: 18/11/2025
