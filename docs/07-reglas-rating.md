# 07 - Reglas de Rating (dobles) · Preset A + Suavizador no cero-sum

## Objetivo
Elo adaptado a pádel (siempre 2v2) con:
- **Categoría inicial declarada** por el jugador (8va… Libre) → se asigna rating base.
- Ajuste por **diferencia de nivel** (expectativa).
- Ajuste por **margen de games** y **sets**.
- **Suavizador no cero-sum**: en resultados “esperables”, el perdedor pierde **menos** de lo que gana el ganador; en **sorpresas**, el movimiento es mayor y compensa parte del suavizado.

---

## Categorías y rating inicial
El jugador elige su categoría al registrarse:

| Categoría | Descripción breve                                       | Rating inicial |
|-----------|----------------------------------------------------------|----------------|
| 8va       | Principiante / princ. avanzado                           | 800            |
| 7ma       | Golpes más sólidos, primeros smashes                     | 950            |
| 6ta       | Mejor dominio y estrategia básica                         | 1100           |
| 5ta       | Buenos jugadores, constancia                              | 1250           |
| 4ta       | Muy buenos, técnica + estrategia                          | 1400           |
| Libre     | Élite local (top provincia)                               | 1600           |

> La **categoría actual** se recalcula en función del rating (cortes sugeridos: 8va <900; 7ma 900–1049; 6ta 1050–1199; 5ta 1200–1349; 4ta 1350–1499; Libre ≥1500).

---

## Parámetros base (igual que Preset A)
- **K por experiencia (por jugador)**  
  `<15: 32`, `15–59: 24`, `≥60: 18`
- **Ajuste por diferencia de rating entre equipos (|Δteam|)**  
  `>300 ⇒ ×0.85`, `>450 ⇒ ×0.75`
- **Expectativa `E`** (Elo divisor 400):  
  \[
  E = \frac{1}{1 + 10^{\frac{(R_{op} - R_{me})}{400}}}
  \]
- **Resultado real `S`** por **games totales**:  
  \[
  S = \frac{gw}{gw + gl}
  \]
- **Factor de sets `f_sets`**: 2–0 ⇒ ×1.10; 0–2 ⇒ ×0.95; 2–1/1–2 ⇒ ×1.00
- **WO/Abandono**: ±4 (sin margen)

---

## Δ base del equipo (antes del suavizador)
\[
\Delta R_{team}^{base} = K \cdot (S - E) \cdot f_{sets} \cdot f_{diff}
\]
- Si `Δbase > 0` ganó el **equipo A** (el que estamos evaluando).
- El valor por **jugador** es el del equipo, aplicado igual a los 2.

> Hasta acá, el sistema es **cero-sum** entre equipos (lo que gana uno, lo pierde el otro).

---

## Suavizador no cero-sum
Queremos que **en resultados esperables** (gana el favorito) el perdedor **pierda menos**.  
Y que **en sorpresas** (gana el no favorito) la magnitud sea **más grande** para compensar.

Definimos multiplicadores según el caso (sobre el **módulo** de `Δbase`):

- **Caso A – Gana el favorito**  
  - **Ganador (favorito):** `g_factor = 0.90`  
  - **Perdedor (no favorito):** `l_factor = 0.70`  _(pierde menos)_

- **Caso B – Gana el no favorito (sorpresa)**  
  - **Ganador (no favorito):** `g_factor = 1.10`  
  - **Perdedor (favorito):** `l_factor = 1.10`

Aplicación por equipo:
if Δbase > 0 para A:
if A era favorito:
gain_A = + |Δbase| * 0.90
loss_B = - |Δbase| * 0.70
else: # A no favorito (sorpresa)
gain_A = + |Δbase| * 1.10
loss_B = - |Δbase| * 1.10


> Nota: esto **no es cero-sum** por diseño. En promedio, los resultados esperables (más frecuentes) generan ligera **inflación**, y las sorpresas generan **deflación** que compensa parte del efecto. Si con uso real viéramos deriva, ajustamos estos factores (0.88/0.68 vs 1.12/1.12, por ejemplo) o aplicamos una **normalización trimestral** del promedio.

---

## Caps y mínimos (por jugador)
- Ganador **favorito**: **+22** máx.  
- Ganador **no favorito**: **+40** máx.  
- Perdedor **favorito**: **−40** mín.  
- Perdedor **no favorito**: **−18** mín.  
- Redondeo a entero; |Δ|<1 ⇒ forzar ±1 según signo; si ganaste y da negativo ⇒ **+1**.

---

## Distribución en dobles
El valor resultante del **equipo** se aplica **igual** a ambos jugadores del equipo.

---

## Ejemplos numéricos

> Para simplificar, suponemos K y factores ya aplicados en `Δbase`.

### 1) Favorito (5ta 1250 avg) vence a no favorito (6ta 1100 avg) por 6–2, 6–3
- `Δbase = +12` para 5ta (ganador).  
- **Suavizador (Caso A):**  
  - Ganador (favorito): `+12 * 0.90 = +10.8` → **+11** c/u  
  - Perdedor (no favorito): `-12 * 0.70 = -8.4` → **-8** c/u  
- Resultado final: **+11 / −8** por jugador.

### 2) Sorpresa: 6ta (1100) vence a 5ta (1250) por 6–4, 3–6, 6–4
- `Δbase = +18` para 6ta (ganador no favorito).  
- **Suavizador (Caso B):**  
  - Ganador (no favorito): `+18 * 1.10 = +19.8` → **+20** c/u  
  - Perdedor (favorito): `-18 * 1.10 = -19.8` → **-20** c/u  
- Resultado final: **+20 / −20** por jugador (caps podrían aplicar).

### 3) Entre pares (6ta vs 6ta) gana 7–6, 7–6
- `Δbase = +5` para el ganador. No hay favorito claro → tratar como “favorito leve”, usar **Caso A** suave.  
  - Ganador: `+5 * 0.90 = +4.5` → **+5** c/u  
  - Perdedor: `-5 * 0.70 = -3.5` → **-4** c/u

---

## Auditoría/transparencia
En cada confirmación de partido:
- Guardar en `rating_history` por jugador: `before`, `delta`, `after`, `match_id`, `created_at`.
- En `match_events.meta` registrar: `{ E, S, K, f_sets, f_diff, Δbase, suavizador: "Caso A|B", g_factor, l_factor }`.

---

## Resumen
- Se parte de un Elo adaptado (E y S por **games**, `f_sets`, `K` dinámico).  
- Se aplica un **suavizador no cero-sum** para ser más “humano” con derrotas esperables y más “enfático” con sorpresas.  
- Los jugadores arrancan en su **categoría real** y el sistema ajusta con el juego.

