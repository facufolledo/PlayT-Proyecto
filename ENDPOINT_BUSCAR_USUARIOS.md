# 🔍 Endpoint Necesario: Buscar Usuarios

## Endpoint Faltante

El modal de inscripción de torneos necesita un endpoint para buscar usuarios por nombre.

### Especificación del Endpoint:

```python
# Ruta: GET /usuarios/buscar
# Descripción: Buscar usuarios por nombre o apellido

@router.get("/usuarios/buscar")
async def buscar_usuarios(
    q: str = Query(..., min_length=2, description="Término de búsqueda"),
    limit: int = Query(5, ge=1, le=20, description="Límite de resultados"),
    db: Session = Depends(get_db)
):
    """
    Buscar usuarios por nombre o apellido.
    
    - **q**: Término de búsqueda (mínimo 2 caracteres)
    - **limit**: Número máximo de resultados (default: 5, max: 20)
    
    Returns:
        Lista de usuarios que coinciden con la búsqueda
    """
    # Buscar en nombre o apellido (case insensitive)
    usuarios = db.query(Usuario).filter(
        or_(
            Usuario.nombre.ilike(f"%{q}%"),
            Usuario.apellido.ilike(f"%{q}%")
        )
    ).limit(limit).all()
    
    # Retornar solo datos necesarios
    return [
        {
            "id_usuario": u.id_usuario,
            "nombre": u.nombre,
            "apellido": u.apellido,
            "email": u.email,
            "rating": u.rating or 1200,
            "categoria": u.categoria
        }
        for u in usuarios
    ]
```

## Ejemplo de Uso desde Frontend:

```typescript
// GET /usuarios/buscar?q=fac&limit=5

// Response:
[
  {
    "id_usuario": 123,
    "nombre": "Facundo",
    "apellido": "Folledo",
    "email": "facu@example.com",
    "rating": 1500,
    "categoria": "A"
  },
  {
    "id_usuario": 456,
    "nombre": "Facundo",
    "apellido": "García",
    "email": "facug@example.com",
    "rating": 1300,
    "categoria": "B"
  }
]
```

## Ubicación en el Backend:

```
backend/
├── src/
│   ├── controllers/
│   │   └── usuario_controller.py  ← Agregar aquí
│   └── routes/
│       └── usuarios.py  ← O aquí si tienes rutas separadas
```

## Imports Necesarios:

```python
from sqlalchemy.orm import Session
from sqlalchemy import or_
from fastapi import APIRouter, Depends, Query
from ..database import get_db
from ..models.playt_models import Usuario
```

## Características:

✅ **Búsqueda case-insensitive**: Encuentra "Facundo" con "fac", "FAC", "Fac"  
✅ **Busca en nombre Y apellido**: Más flexible  
✅ **Límite de resultados**: Evita sobrecarga  
✅ **Mínimo 2 caracteres**: Evita búsquedas muy amplias  
✅ **Solo datos necesarios**: No expone información sensible  

## Testing:

```bash
# Probar el endpoint
curl "http://localhost:8000/usuarios/buscar?q=fac&limit=5"

# Con autenticación si es necesario
curl -H "Authorization: Bearer TOKEN" \
     "http://localhost:8000/usuarios/buscar?q=fac&limit=5"
```

## Opcional: Agregar Autenticación

Si quieres que solo usuarios autenticados puedan buscar:

```python
from ..dependencies import get_current_user

@router.get("/usuarios/buscar")
async def buscar_usuarios(
    q: str = Query(..., min_length=2),
    limit: int = Query(5, ge=1, le=20),
    current_user: Usuario = Depends(get_current_user),  # ← Agregar esto
    db: Session = Depends(get_db)
):
    # ... resto del código
```

## Mejoras Opcionales:

### 1. Búsqueda más inteligente (fuzzy search):
```python
# Buscar por palabras separadas
terminos = q.split()
filtros = []
for termino in terminos:
    filtros.append(
        or_(
            Usuario.nombre.ilike(f"%{termino}%"),
            Usuario.apellido.ilike(f"%{termino}%")
        )
    )
usuarios = db.query(Usuario).filter(and_(*filtros)).limit(limit).all()
```

### 2. Ordenar por relevancia:
```python
# Ordenar por coincidencia exacta primero
usuarios = db.query(Usuario).filter(
    or_(
        Usuario.nombre.ilike(f"%{q}%"),
        Usuario.apellido.ilike(f"%{q}%")
    )
).order_by(
    # Coincidencia exacta primero
    case(
        (Usuario.nombre.ilike(q), 1),
        (Usuario.apellido.ilike(q), 1),
        else_=2
    ),
    Usuario.nombre
).limit(limit).all()
```

### 3. Excluir usuarios ya inscritos:
```python
@router.get("/usuarios/buscar")
async def buscar_usuarios(
    q: str = Query(..., min_length=2),
    limit: int = Query(5, ge=1, le=20),
    torneo_id: Optional[int] = Query(None),  # ← Nuevo parámetro
    db: Session = Depends(get_db)
):
    query = db.query(Usuario).filter(
        or_(
            Usuario.nombre.ilike(f"%{q}%"),
            Usuario.apellido.ilike(f"%{q}%")
        )
    )
    
    # Si se proporciona torneo_id, excluir usuarios ya inscritos
    if torneo_id:
        usuarios_inscritos = db.query(Pareja.jugador1_id, Pareja.jugador2_id).filter(
            Pareja.torneo_id == torneo_id
        ).all()
        
        ids_inscritos = set()
        for p in usuarios_inscritos:
            ids_inscritos.add(p.jugador1_id)
            ids_inscritos.add(p.jugador2_id)
        
        if ids_inscritos:
            query = query.filter(~Usuario.id_usuario.in_(ids_inscritos))
    
    usuarios = query.limit(limit).all()
    
    return [
        {
            "id_usuario": u.id_usuario,
            "nombre": u.nombre,
            "apellido": u.apellido,
            "email": u.email,
            "rating": u.rating or 1200,
            "categoria": u.categoria
        }
        for u in usuarios
    ]
```

---

**Prioridad**: 🔴 Alta - Necesario para inscripciones de torneos  
**Complejidad**: 🟢 Baja - Endpoint simple  
**Tiempo estimado**: 15-30 minutos
