# Modelo de Datos (ERD textual)

## Entidades
- **users**
  - id, nombre, apellido, telefono, email, ciudad, pais, rating, matches_played
- **clubs**
  - id, nombre, ciudad, pais
- **matches**
  - id, club_id, modalidad, fecha, estado, created_by
- **match_players**
  - match_id, user_id, equipo (1/2)
- **match_results**
  - match_id, reporter_id, sets_equipo1, sets_equipo2, detalle_set (json), confirmado_por_rival
- **rating_history**
  - id, user_id, match_id, rating_antes, rating_despues, delta, created_at

## Relaciones
- users (1..*) — (participa) — match_players — (*..1) matches
- matches (1..*) — rating_history — (*..1) users
- matches (1..1) — (tiene) — (0..1) match_results
