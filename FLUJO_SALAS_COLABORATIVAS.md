# 🎾 Sistema de Salas Colaborativas - PlayR

## 🎯 Concepto

Sistema de salas donde un jugador crea una sala, comparte un código de invitación, otros se unen, juegan y confirman resultados.

---

## 📋 Flujo Completo

### 1️⃣ Crear Sala
**Quién**: Cualquier jugador  
**Qué hace**:
- Crea una sala con nombre y fecha
- Sistema genera código de invitación único (ej: `ABC123`)
- Creador se une automáticamente como primer jugador

**Endpoint**: `POST /salas/`
```json
{
  "nombre": "Partido del Viernes",
  "fecha": "2024-11-22T18:00:00",
  "max_jugadores": 4
}
```

**Respuesta**:
```json
{
  "id_sala": "123",
  "codigo_invitacion": "ABC123",
  "jugadores_actuales": 1,
  "estado": "esperando"
}
```

---

### 2️⃣ Compartir Invitación
**Quién**: Creador  
**Qué hace**:
- Comparte el código `ABC123` por WhatsApp, email, etc.
- O comparte link directo: `https://playr.com/sala/ABC123`

---

### 3️⃣ Unirse a la Sala
**Quién**: Otros jugadores (hasta 3 más)  
**Qué hace**:
- Ingresa el código de invitación
- Se une a la sala
- Ve quiénes están en la sala

**Endpoint**: `POST /salas/unirse`
```json
{
  "codigo_invitacion": "ABC123"
}
```

---

### 4️⃣ Asignar Equipos
**Quién**: Solo el creador  
**Cuándo**: Cuando haya 4 jugadores  
**Qué hace**:
- Asigna 2 jugadores al Equipo 1
- Asigna 2 jugadores al Equipo 2

**Endpoint**: `POST /salas/{sala_id}/asignar-equipos`
```json
{
  "1": 1,  // Jugador 1 → Equipo 1
  "2": 1,  // Jugador 2 → Equipo 1
  "3": 2,  // Jugador 3 → Equipo 2
  "4": 2   // Jugador 4 → Equipo 2
}
```

---

### 5️⃣ Iniciar Partido
**Quién**: Solo el creador  
**Cuándo**: Cuando haya 4 jugadores con equipos asignados  
**Qué hace**:
- Crea el partido oficial en la BD
- Cambia estado de sala a "en_juego"
- Habilita el marcador

**Endpoint**: `POST /salas/{sala_id}/iniciar`

---

### 6️⃣ Jugar (Marcador en Tiempo Real)
**Quién**: Todos los jugadores  
**Qué hace**:
- Ven el marcador en tiempo real
- Cualquiera puede actualizar puntos (opcional: solo creador)
- Sistema detecta automáticamente cuando termina

---

### 7️⃣ Reportar Resultado
**Quién**: Creador  
**Cuándo**: Al finalizar el partido  
**Qué hace**:
- Ingresa resultado final (sets y games)
- Estado cambia a "reportado"

**Endpoint**: `POST /partidos/{partido_id}/resultado`
```json
{
  "sets_eq1": 2,
  "sets_eq2": 1,
  "detalle_sets": [
    {"games_a": 6, "games_b": 4},
    {"games_a": 4, "games_b": 6},
    {"games_a": 6, "games_b": 3}
  ]
}
```

---

### 8️⃣ Confirmar Resultado
**Quién**: Jugadores del equipo rival  
**Qué hace**:
- Revisan el resultado reportado
- Confirman o disputan
- Cuando ambos equipos confirman → Calcular Elo

**Endpoint**: `POST /partidos/{partido_id}/confirmar`

---

### 9️⃣ Calcular Elo
**Quién**: Sistema automático  
**Cuándo**: Cuando ambos equipos confirman  
**Qué hace**:
- Calcula nuevos ratings con algoritmo Elo avanzado
- Actualiza ratings de los 4 jugadores
- Actualiza rankings
- Estado cambia a "finalizada"

**Endpoint**: `POST /partidos/{partido_id}/calcular-elo`

---

## 🗄️ Estructura de Base de Datos

### Tabla: `salas`
```sql
- id_sala (PK)
- nombre
- codigo_invitacion (UNIQUE)
- fecha
- estado (esperando, en_juego, finalizada)
- id_creador (FK → usuarios)
- max_jugadores (default: 4)
- id_partido (FK → partidos, nullable)
- creado_en
```

### Tabla: `sala_jugadores`
```sql
- id_sala (PK, FK → salas)
- id_usuario (PK, FK → usuarios)
- equipo (1 o 2, nullable)
- orden (1-4)
- unido_en
```

---

## 🎨 UI/UX

### Página "Crear Sala"
```
┌─────────────────────────────────────┐
│  Nueva Sala                         │
├─────────────────────────────────────┤
│  Nombre: [Partido del Viernes    ] │
│  Fecha:  [2024-11-22]               │
│  Hora:   [18:00]                    │
│                                     │
│  [Crear Sala]                       │
└─────────────────────────────────────┘
```

### Página "Sala de Espera"
```
┌─────────────────────────────────────┐
│  Partido del Viernes                │
│  Código: ABC123  [Copiar] [Compartir]│
├─────────────────────────────────────┤
│  Jugadores (2/4):                   │
│  ✅ Juan Pérez (Creador)            │
│  ✅ María García                    │
│  ⏳ Esperando...                    │
│  ⏳ Esperando...                    │
│                                     │
│  [Asignar Equipos] [Iniciar]       │
└─────────────────────────────────────┘
```

### Página "Asignar Equipos"
```
┌─────────────────────────────────────┐
│  Equipo 1          Equipo 2         │
├──────────────────┬──────────────────┤
│  Juan Pérez      │  María García    │
│  Carlos López    │  Ana Martínez    │
│                  │                  │
│  [Guardar Equipos]                  │
└─────────────────────────────────────┘
```

### Página "Partido en Juego"
```
┌─────────────────────────────────────┐
│  Equipo 1    2  -  1    Equipo 2    │
│  Juan/Carlos         María/Ana      │
├─────────────────────────────────────┤
│  Set 1:  6 - 4                      │
│  Set 2:  4 - 6                      │
│  Set 3:  6 - 3  ← En juego          │
│                                     │
│  [Finalizar Partido]                │
└─────────────────────────────────────┘
```

---

## 🔗 Endpoints Completos

### Salas
- `POST /salas/` - Crear sala
- `GET /salas/` - Listar mis salas
- `GET /salas/{sala_id}` - Ver sala específica
- `POST /salas/unirse` - Unirse con código
- `POST /salas/{sala_id}/asignar-equipos` - Asignar equipos
- `POST /salas/{sala_id}/iniciar` - Iniciar partido

### Partidos (ya existentes)
- `POST /partidos/{partido_id}/resultado` - Reportar resultado
- `POST /partidos/{partido_id}/confirmar` - Confirmar resultado
- `POST /partidos/{partido_id}/calcular-elo` - Calcular Elo

---

## 🚀 Migración

Para crear las tablas en la base de datos:

```bash
# Conectar a PostgreSQL
psql -h ep-dawn-frost-ac67h4ke-pooler.sa-east-1.aws.neon.tech \
     -U neondb_owner \
     -d neondb

# Ejecutar migración
\i backend/migrations_salas.sql
```

O ejecutar el contenido del archivo `migrations_salas.sql` en tu cliente SQL.

---

## ✅ Ventajas de este Sistema

1. **Flexible**: No necesitas saber quiénes jugarán al crear la sala
2. **Colaborativo**: Todos participan en el proceso
3. **Transparente**: Todos ven el resultado y deben confirmar
4. **Justo**: Sistema Elo solo se aplica cuando todos confirman
5. **Social**: Fácil compartir e invitar amigos

---

## 📱 Próximas Mejoras

- [ ] Notificaciones push cuando alguien se une
- [ ] Chat en la sala
- [ ] Historial de salas
- [ ] Estadísticas por sala
- [ ] Compartir resultado en redes sociales
- [ ] Fotos del partido
- [ ] Ubicación del club/cancha

---

**Última actualización**: Noviembre 2024  
**Versión**: 1.0.0
