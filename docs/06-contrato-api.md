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
{ "error": "RATE_LIMIT", "message": "Too many requests" }

1) Autenticación
POST /auth/register
Registra un usuario.
Body
{ "email": "a@a.com", "password": "******", "nombre": "Facundo", "apellido": "Folledo", "ciudad": "La Rioja", "pais": "AR" }
200
{ "id": 123, "email": "a@a.com" }
409
{ "error": "EMAIL_TAKEN", "message": "Email ya registrado." }
POST /auth/login
Devuelve token.
Body
{ "email": "a@a.com", "password": "******" }

200
{ "access_token": "<jwt>", "token_type": "Bearer", "expires_in": 7200 }

401
{ "error": "INVALID_CREDENTIALS", "message": "Email o contraseña incorrectos." }
GET /users/me
(requiere token)
200
{ "id": 123, "email": "a@a.com", "nombre": "Facundo", "apellido": "Folledo", "rating": 1000, "matches_played": 0 }

401
{ "error": "UNAUTHORIZED", "message": "Token faltante o inválido." }

2) Usuarios
GET /users/{id}
200
{ "id": 33, "nombre": "Juan", "apellido": "Pérez", "ciudad": "La Rioja", "pais": "AR", "rating": 1134, "matches_played": 22 }

404
{ "error": "NOT_FOUND", "message": "Usuario no existe." }
GET /users/{id}/history
Historial de rating.
Query: limit (default 50)
200
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
{
  "club_id": 5,
  "fecha": "2025-08-25T19:30:00Z",
  "team1": [12, 33],
  "team2": [54, 61]
}
201
{ "id": 101, "estado": "pendiente" }
400
{ "error": "INVALID_PLAYERS", "message": "Se requieren 2 jugadores por equipo, sin repetidos." }
GET /matches/{id}
200
{
 "id": 101,
  "club_id": 5,
  "fecha": "2025-08-25T19:30:00Z",
  "estado": "pendiente",
  "team1": [ { "id":12,"nombre":"A","rating":1010 }, { "id":33,"nombre":"B","rating":980 } ],
  "team2": [ { "id":54,"nombre":"C","rating":1005 }, { "id":61,"nombre":"D","rating":1003 } ]
}

404
{ "error": "NOT_FOUND", "message": "Partido no existe." }
GET /matches
Listado/paginado.
Query: state, club_id, from, to, page, page_size
200
{
  "page": 1, "page_size": 20, "total": 56,
  "items": [
    { "id": 101, "fecha": "2025-08-25T19:30:00Z", "estado": "pendiente", "club_id": 5 },
    { "id": 102, "fecha": "2025-08-24T21:00:00Z", "estado": "confirmado", "club_id": 3 }
  ]
}
PATCH /matches/{id}
Acciones: report, confirm, cancel.
Body ejemplo (reportar):
{
  "action": "report",
  "reporter_id": 12,
  "sets_e1": 2,
  "sets_e2": 1,
  "detalle_set": [ {"e1":6,"e2":4}, {"e1":3,"e2":6}, {"e1":7,"e2":5} ]
}

200
{ "id":101, "estado":"reportado" }

409
{ "error": "CONFLICT", "message": "El partido ya fue confirmado/cancelado." }
4) Ranking
GET /ranking
Query: club_id opcional, limit=100
200
{
  "items": [
    { "user_id": 12, "nombre":"A", "rating": 1250, "matches_played": 33 },
    { "user_id": 33, "nombre":"B", "rating": 1180, "matches_played": 41 }
  ]
}
5) Auditoría / Eventos
GET /matches/{id}/events
200
{
  "items": [
    { "id":1, "tipo":"create", "actor":12, "created_at":"2025-08-21T18:20:00Z" },
    { "id":2, "tipo":"report", "actor":33, "created_at":"2025-08-21T18:45:00Z" }
  ]
}

6) Flags anti-abuso
GET /matches/{id}/flags
200
{
  "items": [
    { "id":7, "reason":"repetidos_48h", "created_at":"2025-08-22T11:10:00Z" }
  ]
}
