# 🚨 ENDPOINT URGENTE - Editar Perfil

## Lo que necesito YA

### `PUT /usuarios/perfil`

**Archivo:** `backend/src/controllers/usuario_controller.py`

**Recibe:**
```json
{
  "nombre": "Juan",
  "apellido": "Pérez", 
  "ciudad": "Buenos Aires",
  "pais": "Argentina",
  "posicion_preferida": "drive",
  "mano_dominante": "derecha"
}
```

**Devuelve:** El mismo formato que `GET /usuarios/me`

---

## Código para copiar y pegar

```python
# Agregar este schema arriba con los otros
class ActualizarPerfilRequest(BaseModel):
    nombre: Optional[str] = None
    apellido: Optional[str] = None
    ciudad: Optional[str] = None
    pais: Optional[str] = None
    posicion_preferida: Optional[str] = None  # 'drive' o 'reves'
    mano_dominante: Optional[str] = None      # 'derecha' o 'zurda'


# Agregar este endpoint después de get_usuario_actual
@router.put("/perfil", response_model=UserResponse)
async def actualizar_perfil(
    datos: ActualizarPerfilRequest,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Actualizar información del perfil del usuario actual"""
    try:
        perfil = db.query(PerfilUsuario).filter(
            PerfilUsuario.id_usuario == current_user.id_usuario
        ).first()
        
        if not perfil:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Perfil no encontrado"
            )
        
        # Actualizar solo los campos que vienen
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
            id_categoria=current_user.id_categoria
        )
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al actualizar perfil: {str(e)}"
        )
```

---

## ⚠️ IMPORTANTE

1. **Mapeo de campos:** En la BD el campo se llama `mano_habil` pero el frontend envía `mano_dominante`
2. **Validar:** Solo aceptar "drive"/"reves" para posición y "derecha"/"zurda" para mano
3. **Probar:** Después de implementar, probar con Postman antes de pushear

---

## 🧪 Para probar

```bash
PUT http://localhost:8000/usuarios/perfil
Authorization: Bearer {tu_token}

{
  "nombre": "Test",
  "ciudad": "Buenos Aires",
  "posicion_preferida": "drive"
}
```

---

## ✅ Checklist

- [ ] Copiar el código
- [ ] Agregar imports si faltan (Optional de typing)
- [ ] Probar localmente
- [ ] Push a Railway
- [ ] Avisar que está listo

---

**Tiempo estimado:** 20-30 minutos
**Prioridad:** 🔴 URGENTE
