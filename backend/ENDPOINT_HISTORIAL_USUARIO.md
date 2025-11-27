# Endpoint de Historial de Usuario

## Endpoint Implementado

### GET `/partidos/usuario/{usuario_id}`

Obtiene el historial completo de partidos de un usuario específico.

#### Parámetros

- `usuario_id` (path): ID del usuario
- `limit` (query, opcional): Número máximo de partidos a devolver (default: 20, max: 100)

#### Headers Requeridos

```
Authorization: Bearer {token}
```

#### Respuesta Exitosa (200)

```json
[
  {
    "id_partido": 123,
    "fecha": "2025-11-26T10:00:00",
    "estado": "finalizado",
    "id_creador": 14,
    "creado_en": "2025-11-26T09:00:00",
    "id_club": 1,
    "jugadores": [
      {
        "id_usuario": 14,
        "nombre_usuario": "facundo",
        "nombre": "Facundo",
        "apellido": "Folledo",
        "equipo": 1,
        "rating": 1293
      },
      {
        "id_usuario": 15,
        "nombre_usuario": "facundo2",
        "nombre": "Facundo",
        "apellido": "Dos",
        "equipo": 1,
        "rating": 978
      },
      {
        "id_usuario": 5,
        "nombre_usuario": "6ta_1",
        "nombre": "Jugador",
        "apellido": "6ta 1",
        "equipo": 2,
        "rating": 1104
      },
      {
        "id_usuario": 6,
        "nombre_usuario": "6ta_2",
        "nombre": "Jugador",
        "apellido": "6ta 2",
        "equipo": 2,
        "rating": 1104
      }
    ],
    "resultado": {
      "id_partido": 123,
      "id_reportador": 14,
      "sets_eq1": 2,
      "sets_eq2": 1,
      "detalle_sets": [
        {
          "set": 1,
          "juegos_eq1": 6,
          "juegos_eq2": 4
        },
        {
          "set": 2,
          "juegos_eq1": 4,
          "juegos_eq2": 6
        },
        {
          "set": 3,
          "juegos_eq1": 6,
          "juegos_eq2": 3
        }
      ],
      "confirmado": true,
      "desenlace": "normal",
      "creado_en": "2025-11-26T12:00:00"
    },
    "club": {
      "id_club": 1,
      "nombre": "Club Ejemplo",
      "ciudad": "Buenos Aires",
      "pais": "AR"
    },
    "creador": {
      "id_usuario": 14,
      "nombre_usuario": "facundo"
    },
    "historial_rating": {
      "rating_antes": 1280,
      "delta": 13,
      "rating_despues": 1293
    }
  }
]
```

#### Campos Importantes

- **jugadores**: Lista completa de los 4 jugadores del partido con su información
- **resultado**: Información del resultado del partido incluyendo:
  - `sets_eq1` y `sets_eq2`: Sets ganados por cada equipo
  - `detalle_sets`: Array con el detalle de cada set (juegos ganados)
  - `confirmado`: Si el resultado fue confirmado por todos
  - `desenlace`: Tipo de desenlace (normal, wo, lesion, etc.)
- **historial_rating**: Cambio de rating del usuario específico en ese partido
  - `rating_antes`: Rating antes del partido
  - `delta`: Cambio de rating (+/-)
  - `rating_despues`: Rating después del partido

## Uso en Frontend

El componente `MiPerfil.tsx` consume este endpoint para mostrar:

1. **Estadísticas generales**:
   - Total de partidos
   - Victorias/Derrotas
   - Winrate

2. **Historial de partidos**:
   - Lista de todos los partidos jugados
   - Resultado de cada partido (sets ganados)
   - Detalle expandible de cada set
   - Cambios de rating (+/- puntos)
   - Fecha relativa ("hace X días")

3. **Información de equipos**:
   - Nombres de compañeros y rivales
   - Equipos claramente identificados

## Implementación

El endpoint está implementado en:
- **Controller**: `backend/src/controllers/partido_controller.py`
- **Función**: `partidos_usuario()`
- **Modelos**: `backend/src/models/playt_models.py`
- **Schemas**: `backend/src/schemas/partido.py`

## Notas

- El endpoint devuelve los partidos ordenados por fecha descendente (más recientes primero)
- Solo devuelve partidos donde el usuario participó como jugador
- El `historial_rating` es específico para el usuario que hace la consulta
- Si un partido no tiene resultado, los campos `resultado` y `historial_rating` serán `null`
