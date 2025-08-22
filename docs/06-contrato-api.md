# 06 - Contrato de la API (v1)

Base URL: `/api/v1`

## Convenciones generales
- Formato: JSON.
- Autenticación: **Bearer Token (JWT)** en header `Authorization: Bearer <token>`.
- Escrituras idempotentes: enviar header `Idempotency-Key: <uuid>` en POST/PATCH que modifican estado.
- Concurrencia: el servidor usa **transacciones con bloqueos** (tipo `SELECT ... FOR UPDATE`) en confirmación de resultados y actualización de rating.
- Errores (formato simple):
  ```json
  { "error": "CODIGO", "message": "Descripción legible" }
Rate limits
/auth/login: 5 req/min por IP.

/matches/* (report/confirm): 20 req/min por usuario.

Respuesta si excede: 429 con

json
Copiar
Editar
{ "error": "RATE_LIMIT", "message": "Too many requests" }
1) Autenticación
POST /auth/register
Registra un usuario.

Body

json
Copiar
Editar
{ "email": "a@a.com", "password": "******", "nombre": "Facundo", "apellido": "Folledo", "ciudad": "La Rioja", "pais": "AR" }
200

json
Copiar
Editar
{ "id": 123, "email": "a@a.com" }
409

json
Copiar
Editar
{ "error": "EMAIL_TAKEN", "message": "Email ya registrado." }
POST /auth/login
Devuelve token.

Body

json
Copiar
Editar
{ "email": "a@a.com", "password": "******" }
200

json
Copiar
Editar
{ "access_token": "<jwt>", "token_type": "Bearer", "expires_in": 7200 }
401

json
Copiar
Editar
{ "error": "INVALID_CREDENTIALS", "message": "Email o contraseña incorrectos." }
GET /users/me
(requiere token)

200

json
Copiar
Editar
{ "id": 123, "email": "a@a.com", "nombre": "Facundo", "apellido": "Folledo", "rating": 1000, "matches_played": 0 }
401

json
Copiar
Editar
{ "error": "UNAUTHORIZED", "message": "Token faltante o inválido." }
2) Usuarios
GET /users/{id}
200

json
Copiar
Editar
{ "id": 33, "nombre": "Juan", "apellido": "Pérez", "ciudad": "La Rioja", "pais": "AR", "rating": 1134, "matches_played": 22 }
404

json
Copiar
Editar
{ "error": "NOT_FOUND", "message": "Usuario no existe." }
GET /users/{id}/history
Historial de rating.

Query: limit (default 50)

200

json
Copiar
Editar
{
  "user_id": 33,
  "history": [
    { "match_id": 101, "delta": +12, "before": 1122, "after": 1134, "created_at": "2025-08-21T18:33:20Z" },
    { "match_id": 99,  "delta": -6,  "before": 1128, "after": 1122, "created_at": "2025-08-19T19:02:11Z" }
  ]
}
3) Partidos (2v2)
POST /matches
Crea partido.

Body

json
Copiar
Editar
{
  "club_id": 5,
  "fecha": "2025-08-25T19:30:00Z",
  "team1": [12, 33],
  "team2": [54, 61]
}
201

json
Copiar
Editar
{ "id": 101, "estado": "pendiente" }
400

json
Copiar
Editar
{ "error": "INVALID_PLAYERS", "message": "Se requieren 2 jugadores por equipo, sin repetidos." }
GET /matches/{id}
200

json
Copiar
Editar
{
  "id": 101,
  "club_id": 5,
  "fecha": "2025-08-25T19:30:00Z",
  "estado": "pendiente",
  "team1": [ { "id":12,"nombre":"A","rating":1010 }, { "id":33,"nombre":"B","rating":980 } ],
  "team2": [ { "id":54,"nombre":"C","rating":1005 }, { "id":61,"nombre":"D","rating":1003 } ]
}
404

json
Copiar
Editar
{ "error": "NOT_FOUND", "message": "Partido no existe." }
GET /matches
Listado/paginado.

Query: state, club_id, from, to, page, page_size

200

json
Copiar
Editar
{
  "page": 1, "page_size": 20, "total": 56,
  "items": [
    { "id": 101, "fecha": "2025-08-25T19:30:00Z", "estado": "pendiente", "club_id": 5 },
    { "id": 102, "fecha": "2025-08-24T21:00:00Z", "estado": "confirmado", "club_id": 3 }
  ]
}
PATCH /matches/{id}
Acciones: report, confirm, cancel.

Headers

yaml
Copiar
Editar
Authorization: Bearer <token>
Idempotency-Key: <uuid>   # recomendado en report/confirm
Body ejemplo (reportar):

json
Copiar
Editar
{
  "action": "report",
  "reporter_id": 12,
  "sets_e1": 2,
  "sets_e2": 1,
  "detalle_set": [ {"e1":6,"e2":4}, {"e1":3,"e2":6}, {"e1":7,"e2":5} ]
}
200

json
Copiar
Editar
{ "id":101, "estado":"reportado" }
409

json
Copiar
Editar
{ "error": "CONFLICT", "message": "El partido ya fue confirmado/cancelado." }
Transparencia de cálculo (respuesta al confirmar)
Al confirmar un partido, la API devuelve además un detalle del cálculo con los parámetros del algoritmo y los deltas finales por jugador, para que el usuario entienda por qué subió/bajó X puntos.

Body ejemplo (confirmar):

json
Copiar
Editar
{ "action": "confirm" }
200

json
Copiar
Editar
{
  "id": 101,
  "estado": "confirmado",
  "rating_calc": {
    "team1": {
      "players": [12, 33],
      "avg_before": 1250,
      "E": 0.64,
      "S": 0.58,
      "K": 24,
      "f_sets": 1.10,
      "f_diff": 0.85,
      "delta_base_team": +10.9,
      "suavizador": {
        "case": "A_gana_favorito",   // A: favorito; B: sorpresa
        "g_factor": 0.90,
        "l_factor": 0.70
      },
      "caps": { "winner_cap": 22, "loser_cap": -18 },
      "rounding": "nearest_int_min1",
      "final_delta_per_player": +10
    },
    "team2": {
      "players": [54, 61],
      "avg_before": 1100,
      "E": 0.36,
      "S": 0.42,
      "K": 24,
      "f_sets": 1.10,
      "f_diff": 0.85,
      "delta_base_team": -10.9,
      "suavizador": {
        "case": "A_gana_favorito",
        "g_factor": 0.90,
        "l_factor": 0.70
      },
      "caps": { "winner_cap": 40, "loser_cap": -40 },
      "rounding": "nearest_int_min1",
      "final_delta_per_player": -8
    }
  },
  "players_delta": [
    { "user_id": 12, "before": 1260, "delta": +10, "after": 1270 },
    { "user_id": 33, "before": 1240, "delta": +10, "after": 1250 },
    { "user_id": 54, "before": 1110, "delta": -8,  "after": 1102 },
    { "user_id": 61, "before": 1090, "delta": -8,  "after": 1082 }
  ]
}
Notas

E: expectativa del equipo (según diferencia de ratings promedio).

S: score observado por games.

K: según experiencia.

f_sets: factor por sets (2–0, 2–1, 1–2, 0–2).

f_diff: ajuste por diferencia de niveles (|Δteam|).

delta_base_team: K * (S - E) * f_sets * f_diff (antes del suavizador).

suavizador:

Caso A (gana favorito) → ganador ×0.90, perdedor ×0.70.

Caso B (gana no favorito) → ganador ×1.10, perdedor ×1.10.

final_delta_per_player: valor final tras suavizador, caps y redondeo; se aplica igual a los 2 del equipo.

4) Ranking
GET /ranking
Query: club_id opcional, limit=100

200

json
Copiar
Editar
{
  "items": [
    { "user_id": 12, "nombre":"A", "rating": 1250, "matches_played": 33 },
    { "user_id": 33, "nombre":"B", "rating": 1180, "matches_played": 41 }
  ]
}
5) Auditoría / Eventos
GET /matches/{id}/events
200

json
Copiar
Editar
{
  "items": [
    { "id":1, "tipo":"create", "actor":12, "created_at":"2025-08-21T18:20:00Z" },
    { "id":2, "tipo":"report", "actor":33, "created_at":"2025-08-21T18:45:00Z" },
    {
      "id":3,
      "tipo":"rating_update",
      "actor":33,
      "created_at":"2025-08-21T18:46:10Z",
      "meta": {
        "team1": { "E":0.64, "S":0.58, "K":24, "f_sets":1.10, "f_diff":0.85, "delta_base":10.9, "suavizador":"A", "g_factor":0.90, "l_factor":0.70, "final_pp":10 },
        "team2": { "E":0.36, "S":0.42, "K":24, "f_sets":1.10, "f_diff":0.85, "delta_base":-10.9,"suavizador":"A", "g_factor":0.90, "l_factor":0.70, "final_pp":-8 }
      }
    }
  ]
}
6) Flags anti-abuso
GET /matches/{id}/flags
200

json
Copiar
Editar
{
  "items": [
    { "id":7, "reason":"repetidos_48h", "created_at":"2025-08-22T11:10:00Z" }
  ]
}
Notas finales
Cada endpoint devuelve solo lo necesario para la pantalla que lo consume.

Confirmación de partido incluye detalle del cálculo para transparencia (además queda registrado en match_events).

Autenticación basada en login + token, nunca reenviando la contraseña en cada request.

Respuestas claras: 200 OK, 4xx errores del cliente, 5xx fallos del servidor.
