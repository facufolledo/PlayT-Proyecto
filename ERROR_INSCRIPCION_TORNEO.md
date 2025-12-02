# 🐛 Error: Inscripción de Torneo

## 🔴 Problema Reportado

Al intentar inscribirse a un torneo, aparecen dos errores:
1. **"Method Not Allowed"** (405)
2. **"Token inválido"** (401)

## 📸 Evidencia

```
Error mostrado: "Token inválido"
Detalle en consola: {"detail":"Method Not Allowed"}
```

## 🔍 Análisis

### Frontend (Correcto)

El frontend está enviando la petición correctamente:

```typescript
// Endpoint: POST /torneos/{torneoId}/inscribir
await axios.post(
  `${API_URL}/torneos/${torneoId}/inscribir`,
  {
    jugador1_id: usuario.id_usuario,
    jugador2_id: parseInt(formData.jugador2_id),
    nombre_pareja: nombrePareja
  },
  {
    headers: {
      Authorization: `Bearer ${token}`
    }
  }
);
```

**Token:**
- Se obtiene de `localStorage.getItem('firebase_token')`
- Se envía en header: `Authorization: Bearer {token}`

### Backend (Revisar)

Posibles causas del error:

#### 1. Método HTTP Incorrecto
```python
# ❌ Si está así (GET en lugar de POST):
@router.get("/torneos/{torneo_id}/inscribir")

# ✅ Debe ser:
@router.post("/torneos/{torneo_id}/inscribir")
```

#### 2. Ruta Incorrecta
```python
# ❌ Si la ruta es diferente:
@router.post("/torneos/{torneo_id}/inscripcion")  # Diferente

# ✅ Debe ser exactamente:
@router.post("/torneos/{torneo_id}/inscribir")
```

#### 3. Validación de Token
```python
# Verificar que el endpoint tenga la dependencia de autenticación:
@router.post("/torneos/{torneo_id}/inscribir")
async def inscribir_pareja(
    torneo_id: int,
    data: ParejaInscripcion,
    current_user: Usuario = Depends(get_current_user),  # ← Importante
    db: Session = Depends(get_db)
):
    # ...
```

#### 4. Verificación del Token Firebase
```python
# Asegurarse de que el middleware de autenticación esté validando correctamente:
from firebase_admin import auth as firebase_auth

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        # Verificar token de Firebase
        decoded_token = firebase_auth.verify_id_token(token)
        uid = decoded_token['uid']
        email = decoded_token.get('email')
        
        # Buscar usuario en BD
        usuario = db.query(Usuario).filter(Usuario.firebase_uid == uid).first()
        if not usuario:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        
        return usuario
    except Exception as e:
        raise HTTPException(status_code=401, detail="Token inválido")
```

---

## 🔧 Solución Recomendada

### Paso 1: Verificar el Endpoint

```python
# backend/src/controllers/torneo_controller.py o routes/torneos.py

@router.post("/torneos/{torneo_id}/inscribir")
async def inscribir_pareja(
    torneo_id: int,
    data: ParejaInscripcion,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Inscribir una pareja en un torneo.
    
    - **torneo_id**: ID del torneo
    - **jugador1_id**: ID del primer jugador (debe ser el usuario actual)
    - **jugador2_id**: ID del segundo jugador
    - **nombre_pareja**: Nombre de la pareja
    """
    try:
        # Validar que jugador1 sea el usuario actual
        if data.jugador1_id != current_user.id_usuario:
            raise HTTPException(
                status_code=403, 
                detail="Solo puedes inscribirte a ti mismo"
            )
        
        # Validar que el torneo existe
        torneo = db.query(Torneo).filter(Torneo.id == torneo_id).first()
        if not torneo:
            raise HTTPException(status_code=404, detail="Torneo no encontrado")
        
        # Validar que el torneo está en inscripción
        if torneo.estado != 'inscripcion':
            raise HTTPException(
                status_code=400, 
                detail="El torneo no está en fase de inscripción"
            )
        
        # Validar que jugador2 existe
        jugador2 = db.query(Usuario).filter(Usuario.id_usuario == data.jugador2_id).first()
        if not jugador2:
            raise HTTPException(status_code=404, detail="Compañero no encontrado")
        
        # Validar que no estén ya inscritos
        pareja_existente = db.query(Pareja).filter(
            Pareja.torneo_id == torneo_id,
            or_(
                and_(Pareja.jugador1_id == data.jugador1_id, Pareja.jugador2_id == data.jugador2_id),
                and_(Pareja.jugador1_id == data.jugador2_id, Pareja.jugador2_id == data.jugador1_id)
            )
        ).first()
        
        if pareja_existente:
            raise HTTPException(status_code=400, detail="Esta pareja ya está inscrita")
        
        # Crear pareja
        nueva_pareja = Pareja(
            torneo_id=torneo_id,
            jugador1_id=data.jugador1_id,
            jugador2_id=data.jugador2_id,
            nombre_pareja=data.nombre_pareja,
            estado='inscripta'
        )
        
        db.add(nueva_pareja)
        db.commit()
        db.refresh(nueva_pareja)
        
        return nueva_pareja
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
```

### Paso 2: Verificar el Modelo

```python
# backend/src/models/playt_models.py

class ParejaInscripcion(BaseModel):
    jugador1_id: int
    jugador2_id: int
    nombre_pareja: str
    
    class Config:
        from_attributes = True
```

### Paso 3: Verificar CORS

```python
# backend/main.py

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
        "https://kioskito.click",
        "https://www.kioskito.click"
    ],
    allow_credentials=True,
    allow_methods=["*"],  # ← Importante: permite POST
    allow_headers=["*"],
)
```

---

## 🧪 Testing

### Probar con cURL:

```bash
# Obtener token de Firebase desde el navegador (localStorage.getItem('firebase_token'))
TOKEN="tu_token_aqui"

# Probar endpoint
curl -X POST "http://localhost:8000/torneos/1/inscribir" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "jugador1_id": 1,
    "jugador2_id": 2,
    "nombre_pareja": "Test / Pareja"
  }'
```

### Respuesta Esperada:

```json
{
  "id": 1,
  "torneo_id": 1,
  "jugador1_id": 1,
  "jugador2_id": 2,
  "nombre_pareja": "Test / Pareja",
  "estado": "inscripta"
}
```

---

## 📋 Checklist de Verificación

- [ ] Endpoint usa método POST (no GET)
- [ ] Ruta es exactamente `/torneos/{torneo_id}/inscribir`
- [ ] Tiene dependencia `Depends(get_current_user)`
- [ ] Valida token de Firebase correctamente
- [ ] CORS permite método POST
- [ ] Modelo `ParejaInscripcion` está definido
- [ ] Tabla `parejas` existe en la BD
- [ ] Usuario tiene permisos para inscribirse

---

## 🔍 Debug en Backend

Agregar logs para debug:

```python
@router.post("/torneos/{torneo_id}/inscribir")
async def inscribir_pareja(
    torneo_id: int,
    data: ParejaInscripcion,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    print(f"🔍 Inscripción recibida:")
    print(f"  - Torneo ID: {torneo_id}")
    print(f"  - Usuario actual: {current_user.email}")
    print(f"  - Jugador 1: {data.jugador1_id}")
    print(f"  - Jugador 2: {data.jugador2_id}")
    print(f"  - Nombre pareja: {data.nombre_pareja}")
    
    # ... resto del código
```

---

## 💡 Mejoras en Frontend (Ya Implementadas)

```typescript
// Mejor manejo de errores
catch (err: any) {
  console.error('Error al inscribir:', err);
  const errorMsg = err.response?.data?.detail || err.response?.data?.message || err.message;
  
  if (err.response?.status === 401) {
    setError('Tu sesión ha expirado. Por favor, vuelve a iniciar sesión.');
  } else if (err.response?.status === 405) {
    setError('Método no permitido. El endpoint puede estar mal configurado.');
  } else {
    setError(errorMsg);
  }
}
```

---

**Prioridad**: 🔴 Alta - Bloquea inscripciones  
**Complejidad**: 🟡 Media - Requiere revisar backend  
**Tiempo estimado**: 30-60 minutos
