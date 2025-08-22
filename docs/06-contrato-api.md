# Contrato API (MVP)

## Autenticación
- `POST /auth/register`
- `POST /auth/login` → retorna JWT

## Usuarios
- `GET /users/{id}` → datos y rating
- `GET /users/{id}/history` → rating_history

## Clubs
- `POST /clubs`
- `GET /clubs/{id}`

## Matches
- `POST /matches`  
  Body: { club_id, modalidad, fecha, players[] }
- `GET /matches/{id}`
- `POST /matches/{id}/report`  
  Body: { sets_equipo1, sets_equipo2, detalle_set }
- `POST /matches/{id}/confirm`  
  Body: { confirm: true/false }

## Rankings
- `GET /ranking?club_id=&ciudad=&limit=50`

## Concurrencia
- `select ... for update` en confirmación.
- `match_results.match_id` = PK (evita duplicado).
