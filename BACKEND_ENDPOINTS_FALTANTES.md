# 🔧 Endpoints Faltantes en el Backend

## 📋 RESUMEN EJECUTIVO

El frontend está implementado pero faltan estos endpoints críticos en el backend para que funcione completamente.

---

## 🚨 URGENTE - Editar Perfil

### Endpoint: `PUT /usuarios/perfil`

**Ubicación:** `backend/src/controllers/usuario_controller.py`

**Request Body:**
```json
{
  "nombre": "Juan",
  "apellido": "Pérez",
  "ciudad": "Buenos Aires",
  "pais": "Argentina",
  "posicion_preferida": "drive",  // "drive" | "reves"
  "mano_dominante": "derecha"     // "derecha" | "zurda"
}
```

**Response:**
```json
{
  "id_usuario": 1,
  "nombre_usuario": "juanperez",
  "email": "juan@email.com",
  "nombre": "Juan",
  "apellido": "Pérez",
  "ciudad": "Buenos Aires",
  "pais": "Argentina",
  "posicion_preferida": "drive",
  "mano_dominante": "derecha",
  "rating": 1200,
  "partidos_jugados": 15,
  "id_categoria": 3
}
```

**Código de Implementación:**

```python
class ActualizarPerfilRequest(BaseModel):
    nombre: Optional[str] = None
    apellido: Optional[str] = None
    ciudad: Optional[str] = None
    pais: Optional[str] = None
    posicion_preferida: Optional[str] = None  # 'drive' o 'reves'
    mano_dominante: Optional[str] = None      # 'derecha' o 'zurda'


@router.put("/perfil", response_model=UserResponse)
async def actualizar_perfil(
    datos: ActualizarPerfilRequest,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Actualizar información del perfil del usuario actual
    """
    try:
        # Buscar perfil del usuario
        perfil = db.query(PerfilUsuario).filter(
            PerfilUsuario.id_usuario == current_user.id_usuario
        ).first()
        
        if not perfil:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Perfil no encontrado"
            )
        
        # Actualizar solo los campos que vienen en el request
        if datos.nombre is not None:
            perfil.nombre = datos.nombre
        
        if datos.apellido is not None:
            perfil.apellido = datos.apellido
        
        if datos.ciudad is not None:
            perfil.ciudad = datos.ciudad
        
        if datos.pais is not None:
            perfil.pais = datos.pais
        
        if datos.posicion_preferida is not None:
            perfil.posicion_preferida = datos.posicion_preferida
        
        if datos.mano_dominante is not None:
            perfil.mano_habil = datos.mano_dominante
        
        db.commit()
        db.refresh(perfil)
        db.refresh(current_user)
        
        return UserResponse(
            id_usuario=current_user.id_usuario,
            nombre_usuario=current_user.nombre_usuario,
            email=current_user.email,
            nombre=perfil.nombre,
            apellido=perfil.apellido,
            sexo=current_user.sexo,
            ciudad=perfil.ciudad,
            pais=perfil.pais,
            rating=current_user.rating,
            partidos_jugados=current_user.partidos_jugados,
            id_categoria=current_user.id_categoria,
            posicion_preferida=perfil.posicion_preferida,
            mano_dominante=perfil.mano_habil
        )
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al actualizar perfil: {str(e)}"
        )
```

**Nota:** Verificar que el schema `UserResponse` incluya los campos `posicion_preferida` y `mano_dominante`. Si no los tiene, agregarlos como `Optional[str]`.

---

## 📊 IMPORTANTE - Mejorar Endpoint de Partidos

### Endpoint: `GET /partidos/usuario/{id_usuario}`

**Problema Actual:** El endpoint existe pero puede necesitar optimización.

**Verificar que retorne:**
```json
[
  {
    "id_partido": 123,
    "fecha": "2025-11-20T15:30:00",
    "estado": "finalizado",
    "tipo": "torneo",  // "torneo" | "amistoso"
    "jugadores": [
      {
        "id_usuario": 1,
        "nombre_usuario": "juanperez",
        "nombre": "Juan",
        "apellido": "Pérez",
        "equipo": 1,
        "rating": 1200
      },
      // ... más jugadores
    ],
    "resultado": {
      "sets_eq1": 2,
      "sets_eq2": 1,
      "detalle_sets": [
        {
          "set": 1,
          "juegos_eq1": 6,
          "juegos_eq2": 4,
          "tiebreak_eq1": null,
          "tiebreak_eq2": null
        },
        {
          "set": 2,
          "juegos_eq1": 6,
          "juegos_eq2": 7,
          "tiebreak_eq1": 5,
          "tiebreak_eq2": 7
        }
      ],
      "confirmado": true,
      "desenlace": "victoria_eq1"
    },
    "historial_rating": {
      "rating_antes": 1180,
      "delta": 20,
      "rating_despues": 1200
    }
  }
]
```

**Verificar:**
- ✅ Que incluya el campo `tipo` (torneo/amistoso)
- ✅ Que incluya `historial_rating` con el delta de rating
- ✅ Que ordene por fecha descendente (más recientes primero)
- ✅ Que no haya duplicados

---

## 🔔 FUTURO - Notificaciones Push (No Urgente)

### Sistema de Notificaciones

**Endpoints Necesarios:**

1. **POST /notificaciones/enviar**
   - Enviar notificación a un usuario específico
   - Casos de uso:
     - "Tu rival confirmó el resultado"
     - "Te invitaron a una sala"
     - "Empieza tu partido en 30 minutos"

2. **GET /notificaciones/mis-notificaciones**
   - Obtener notificaciones del usuario actual
   - Marcar como leídas

**Implementación Requerida:**
- Instalar `firebase-admin` en requirements.txt
- Crear servicio de notificaciones
- Integrar con eventos del sistema (confirmación de resultados, invitaciones, etc.)

**Nota:** Esto puede esperar. Primero completar el endpoint de editar perfil.

---

## 🔍 OPCIONAL - Búsqueda de Jugadores

### Endpoint: `GET /usuarios/buscar`

**Query Params:**
- `q`: string de búsqueda (nombre, apellido o username)
- `limit`: cantidad de resultados (default: 10)

**Response:**
```json
[
  {
    "id_usuario": 1,
    "nombre_usuario": "juanperez",
    "nombre": "Juan",
    "apellido": "Pérez",
    "rating": 1200,
    "ciudad": "Buenos Aires",
    "foto_perfil": null
  }
]
```

**Uso:** Para invitar jugadores a salas privadas.

---

## 📈 OPCIONAL - Estadísticas Avanzadas

### Endpoint: `GET /estadisticas/usuario/{id_usuario}/avanzadas`

**Response:**
```json
{
  "racha_actual": {
    "tipo": "victorias",  // "victorias" | "derrotas"
    "cantidad": 5
  },
  "mejor_racha": {
    "tipo": "victorias",
    "cantidad": 8
  },
  "mejor_rival": {
    "id_usuario": 2,
    "nombre": "Carlos López",
    "victorias_contra_el": 7,
    "derrotas_contra_el": 2
  },
  "peor_rival": {
    "id_usuario": 3,
    "nombre": "Diego Martínez",
    "victorias_contra_el": 1,
    "derrotas_contra_el": 6
  },
  "estadisticas_por_posicion": {
    "drive": {
      "partidos": 20,
      "victorias": 12,
      "winrate": 60
    },
    "reves": {
      "partidos": 10,
      "victorias": 7,
      "winrate": 70
    }
  }
}
```

---

## ✅ CHECKLIST DE IMPLEMENTACIÓN

### Prioridad ALTA (Hacer YA)
- [ ] Implementar `PUT /usuarios/perfil`
- [ ] Verificar que `UserResponse` incluya todos los campos necesarios
- [ ] Probar endpoint con Postman/Thunder Client
- [ ] Verificar que `GET /partidos/usuario/{id}` retorne el campo `tipo`

### Prioridad MEDIA (Próxima semana)
- [ ] Implementar `GET /usuarios/buscar`
- [ ] Mejorar endpoint de partidos si falta algo

### Prioridad BAJA (Futuro)
- [ ] Sistema de notificaciones push
- [ ] Estadísticas avanzadas

---

## 🧪 TESTING

### Probar Editar Perfil:

```bash
# 1. Login y obtener token
POST http://localhost:8000/auth/login
{
  "email": "test@test.com",
  "password": "password123"
}

# 2. Actualizar perfil
PUT http://localhost:8000/usuarios/perfil
Authorization: Bearer {token}
{
  "nombre": "Juan",
  "apellido": "Pérez",
  "ciudad": "Buenos Aires",
  "posicion_preferida": "drive",
  "mano_dominante": "derecha"
}

# 3. Verificar cambios
GET http://localhost:8000/usuarios/me
Authorization: Bearer {token}
```

---

## 📝 NOTAS ADICIONALES

1. **Foto de Perfil:** Por ahora deshabilitado. El frontend maneja fotos con Firebase Storage pero no las envía al backend.

2. **Validaciones:** Agregar validaciones para:
   - `posicion_preferida` solo acepta: "drive" o "reves"
   - `mano_dominante` solo acepta: "derecha" o "zurda"

3. **Compatibilidad:** El campo en la BD se llama `mano_habil` pero el frontend usa `mano_dominante`. Mapear correctamente.

4. **Response Schema:** Asegurarse que `UserResponse` en `schemas/auth.py` incluya todos los campos que el frontend espera.

---

## 🚀 DEPLOYMENT

Una vez implementado:
1. Hacer commit y push a Railway
2. Verificar que el endpoint funcione en producción
3. Avisar al frontend para probar

---

**Fecha:** 27/11/2025
**Prioridad:** 🔴 URGENTE - Editar Perfil
**Estimación:** 30-45 minutos de desarrollo
