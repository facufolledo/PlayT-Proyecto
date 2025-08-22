# 05 - Dominio y Datos

## Alcance
MVP con auditoría básica: partidos dobles 2v2, reporte + confirmación, cálculo de rating estilo Elo ajustado (a nivel equipo) y ranking.  
Incluye logs simples de eventos e indicadores de abuso.

---

## Entidades

### 1) `users`
- `id` **PK** (bigint, autoincrement)  
- `email` (único, obligatorio)  
- `password_hash`  
- `created_at` (UTC)  
- **Ranking**:  
  - `rating` (int, default 1000)  
  - `matches_played` (int, default 0)

### 2) `user_profile` (1:1 con `users`)
- `user_id` **PK/FK** → `users.id`  
- `nombre`, `apellido`  
- `ciudad`, `pais`  
- `avatar_url` (opcional)  
- `updated_at`

### 3) `clubs`
- `id` **PK** (bigint, autoincrement)  
- `nombre` (obligatorio)  
- `ciudad`, `pais`

### 4) `matches` (partido, siempre 2v2 — no hay singles en pádel)
- `id` **PK** (bigint, autoincrement)  
- `club_id` **FK** → `clubs.id` (nullable si amistoso sin club)  
- `fecha` (UTC)  
- `estado` (`pendiente` | `reportado` | `confirmado` | `cancelado`)  
- `created_by` **FK** → `users.id`  
- `created_at` (UTC)

### 5) `match_players` (jugadores por equipo)
- `match_id` **FK** → `matches.id`  
- `user_id` **FK** → `users.id`  
- `equipo` (tinyint: 1 o 2)  
- **PK compuesta**: `(match_id, user_id)`  
- **Restricciones**:
  - `check(equipo in (1,2))`  
  - `unique(match_id, user_id)`  
  - Al confirmar: exactamente 2 jugadores en cada equipo (validación en app/tx)

### 6) `match_results`
- `match_id` **PK/FK** → `matches.id`  
- `reporter_id` **FK** → `users.id`  
- `sets_e1` (tinyint), `sets_e2` (tinyint)  
- `detalle_set` (JSON)  
  Ej: `[{"e1":6,"e2":4},{"e1":7,"e2":6}]`  
- `confirmado` (boolean)  
- `outcome` (`normal` | `wo_e1` | `wo_e2` | `ret_e1` | `ret_e2`)  
- `created_at` (UTC)

### 7) `rating_history`
- `id` **PK** (bigint, autoincrement)  
- `user_id` **FK** → `users.id`  
- `match_id` **FK** → `matches.id`  
- `rating_antes`, `rating_despues`, `delta` (int)  
- `created_at` (UTC)

### 8) `match_events` (auditoría básica)
- `id` **PK** (bigint, autoincrement)  
- `match_id` **FK** → `matches.id`  
- `actor_user_id` **FK** → `users.id`  
- `tipo` (`create` | `report` | `confirm` | `cancel` | `reject` | `edit`)  
- `meta` (JSON)  
- `created_at` (UTC)

### 9) `suspicious_flags` (anti-abuso)
- `id` **PK** (bigint, autoincrement)  
- `match_id` **FK** → `matches.id`  
- `reason` (texto corto, ej: `repetidos_48h`)  
- `created_at` (UTC)

---

## 🔗 Relaciones
- `users (1..1) — user_profile`  
- `users (1..*) — match_players — (*..1) matches`  
- `matches (1..1) — (0..1) match_results`  
- `users (1..*) — rating_history — (*..1) matches`  
- `matches (1..*) — match_events`  
- `matches (1..*) — suspicious_flags`

---

## ✅ Reglas de integridad
- `match_results.match_id` = **PK** → evita doble resultado.  
- `match_players`:  
  - `unique(match_id, user_id)`  
  - `check(equipo in (1,2))`  
- Al confirmar (en transacción):  
  - exactamente 2 jugadores en `equipo=1`  
  - exactamente 2 jugadores en `equipo=2`  
  - bloqueo de filas de `matches` + ratings de los 4 jugadores (`SELECT … FOR UPDATE`).

---

## Índices recomendados
- `matches(club_id, fecha)` → listados por club/fecha.  
- `rating_history(user_id, created_at desc)` → historial rápido.  
- `users(rating desc)` → ranking global.  
- `match_events(match_id, created_at)`.

---

## Zona horaria
Todo en **UTC**. La aplicación convierte a hora local de La Rioja para mostrar.

---

## Borrados
**Borrado duro** en MVP.  
(Opcional futuro: soft delete en `matches`/`results` si se requiere auditoría total).

---

## 🚨 Anti-abuso
Regla inicial: marcar como `repetidos_48h` si los mismos 4 jugadores se enfrentan ≥3 veces en 48h.  
Se registra en `suspicious_flags`, no bloquea.

---

## Nota sobre cálculo de rating
- Rating de equipo = promedio de sus 2 jugadores.  
- Expectativa `E` según diferencia de rating de equipos (fórmula tipo Elo).  
- Puntuación real `S` ajustada por:
  - **margen de games** (`detalle_set` → no es lo mismo 6-0 que 7-6).  
  - **nivel relativo** de rivales (perder contra alguien mucho mejor resta poco, perder contra tu mismo nivel resta más).  
- Factor de sets `f_sets` (2–0, 2–1, 0–2).  
- K dinámico (ajustado según experiencia: jugadores nuevos suben/bajan más rápido).  
- Fórmula base:  
-ΔR_team = K * (S − E) * f_sets
- El delta se reparte en partes iguales entre los 2 jugadores del equipo.  
- Se insertan 4 filas en `rating_history` (una por jugador).
