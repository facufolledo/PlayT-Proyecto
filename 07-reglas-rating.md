# 🏅 Reglas de Rating (Dobles, estilo Playtomic)

## 1) Conceptos básicos

- **Rating (R):** valor numérico que representa nivel del jugador. Rango sugerido: 600–2400.  
  Inicial: 1000.  

- **Partidos jugados (N):** cantidad de partidos confirmados de cada jugador.  

- **Equipo rating (R_team):** promedio de los 2 jugadores que forman el equipo.  
  \[
  R_{team} = \frac{R_{j1} + R_{j2}}{2}
  \]

- **Resultado por games (S_games):**  
  \[
  S = \frac{gw}{gw + gl}
  \]
  donde `gw` = games ganados por el equipo, `gl` = games perdidos.  
  Ejemplo:  
  - 6–0 → S=1.0  
  - 6–4 → S=0.6  
  - 7–6 → S≈0.54  

- **Resultado por sets (factor extra):**  
  - Victoria 2–0 ⇒ `f_sets = 1.10`  
  - Victoria 2–1 ⇒ `f_sets = 1.00`  
  - Derrota 1–2 ⇒ `f_sets = 1.00`  
  - Derrota 0–2 ⇒ `f_sets = 0.95`  

---

## 2) Expectativa (E)

Logística tipo Elo:

\[
E = \frac{1}{1 + 10^{\frac{(R_{op} - R_{me})}{400}}}
\]

- Si sos favorito (R_me > R_op), **E** se acerca a 1.  
- Si sos no favorito (R_me < R_op), **E** se acerca a 0.

---

## 3) K dinámico

- **K_base** = 24.  
- **Partidos jugados (por jugador en el equipo):**  
  - N < 15 ⇒ 32  
  - 15 ≤ N < 60 ⇒ 24  
  - N ≥ 60 ⇒ 18  

  *(se toma el promedio de K de los 2 jugadores del equipo)*

- **Diferencia de nivel (Δ):**  
  - |Δ| > 300 ⇒ multiplicar K por 0.85  
  - |Δ| > 450 ⇒ multiplicar K por 0.75  

- **Clamp final:** 12 ≤ K ≤ 40.

---

## 4) Cambio de rating (ΔR equipo)

\[
\Delta R_{team} = K \cdot (S - E) \cdot f_{sets}
\]

- Si `S > E` ⇒ el equipo rinde **mejor de lo esperado** (sube).  
- Si `S < E` ⇒ rinde **peor de lo esperado** (baja).  

---

## 5) Reparto a jugadores

El ΔR del equipo se reparte **por igual** a ambos jugadores:  

\[
R'_{j1} = R_{j1} + \Delta R_{team}
\]  
\[
R'_{j2} = R_{j2} + \Delta R_{team}
\]

*(si querés, se puede afinar para compensar redondeos, pero lo normal es aplicar el mismo valor a los 2)*.

---

## 6) Caps y límites

- Ganador favorito ⇒ máx +22.  
- Ganador no favorito ⇒ máx +40.  
- Perdedor favorito ⇒ mín −40.  
- Perdedor no favorito ⇒ mín −18.  
- No permitir |ΔR| < 1 → siempre al menos ±1.

---

## 7) Ejemplos rápidos

1. **Favoritos ganan 6–0**  
   - E≈0.75, S=1.0 → ΔR≈+6 a +8 para cada jugador del equipo ganador.  
   - Rival: −6 a −8 cada uno.  

2. **Favoritos ganan 7–6**  
   - E≈0.75, S≈0.54 → ΔR≈−5 a −6 para el equipo “ganador favorito” (subieron menos de lo esperado).  
   - Rivales (no favoritos) pierden, pero rinden por encima de expectativa ⇒ ΔR≈+5 cada uno.  

3. **No favoritos ganan 6–4**  
   - E≈0.25, S=0.6 → ΔR≈+20 para cada jugador ganador.  
   - Favoritos pierden ⇒ −20 cada uno.  

---

## 8) Pseudocódigo

```python
def expected(r_me, r_op):
    return 1.0 / (1.0 + 10 ** ((r_op - r_me) / 400))

def k_dynamic(n_avg, dr):
    k = 24
    if n_avg < 15:
        k = 32
    elif n_avg >= 60:
        k = 18
    if abs(dr) > 450:
        k *= 0.75
    elif abs(dr) > 300:
        k *= 0.85
    return max(12, min(int(round(k)), 40))

def apply_rating(r_team_me, r_team_op, n_avg_me, n_avg_op, gw, gl, sets_me, sets_op):
    e = expected(r_team_me, r_team_op)
    s = gw / (gw + gl)
    f_sets = 1.0
    if sets_me == 2 and sets_op == 0:
        f_sets = 1.10
    elif sets_me == 0 and sets_op == 2:
        f_sets = 0.95

    k = k_dynamic((n_avg_me + n_avg_op)//2, r_team_op - r_team_me)
    delta_team = k * (s - e) * f_sets
    return round(delta_team)
