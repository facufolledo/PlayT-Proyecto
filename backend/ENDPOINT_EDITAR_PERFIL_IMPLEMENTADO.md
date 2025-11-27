# ✅ Endpoint Editar Perfil - IMPLEMENTADO

## Resumen

Se implementó exitosamente el endpoint `PUT /usuarios/perfil` para permitir a los usuarios actualizar su información de perfil.

---

## 📍 Endpoint Implementado

### `PUT /usuarios/perfil`

**Ubicación:** `backend/src/controllers/usuario_controller.py`

**Autenticación:** Requiere Bearer Token

**Request Body:**
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

**Todos los campos son opcionales** - solo se actualizan los que se envían.

**Response:**
```json
{
  "id_usuario": 1,
  "nombre_usuario": "juanperez",
  "email": "juan@email.com",
  "nombre": "Juan",
  "apellido": "Pérez",
  "sexo": "M",
  "ciudad": "Buenos Aires",
  "pais": "Argentina",
  "rating": 1200,
  "partidos_jugados": 15,
  "id_categoria": 3,
  "posicion_preferida": "drive",
  "mano_dominante": "derecha"
}
```

---

## 🔧 Cambios Realizados

### 1. Schema `ActualizarPerfilRequest` (usuario_controller.py)
```python
class ActualizarPerfilRequest(BaseModel):
    nombre: Optional[str] = None
    apellido: Optional[str] = None
    ciudad: Optional[str] = None
    pais: Optional[str] = None
    posicion_preferida: Optional[str] = None  # 'drive' o 'reves'
    mano_dominante: Optional[str] = None  # 'derecha' o 'zurda'
```

### 2. Endpoint `actualizar_perfil` (usuario_controller.py)
- Valida que el perfil exista
- Actualiza solo los campos enviados
- Valida valores permitidos:
  - `posicion_preferida`: 'drive', 'reves', 'indiferente'
  - `mano_dominante`: 'derecha', 'zurda'
- Mapea `mano_dominante` (frontend) → `mano_habil` (BD)
- Retorna el perfil actualizado

### 3. Schema `UserResponse` (schemas/auth.py)
Agregados campos:
```python
posicion_preferida: Optional[str] = None
mano_dominante: Optional[str] = None
```

### 4. Actualizado `GET /usuarios/me`
Ahora retorna también `posicion_preferida` y `mano_dominante`

### 5. Actualizado `POST /completar-perfil`
Ahora retorna también `posicion_preferida` y `mano_dominante`

---

## ✅ Validaciones Implementadas

1. **Perfil existe:** Retorna 404 si no encuentra el perfil
2. **Posición preferida:** Solo acepta 'drive', 'reves', 'indiferente'
3. **Mano dominante:** Solo acepta 'derecha', 'zurda'
4. **Actualización parcial:** Permite actualizar solo algunos campos
5. **Mapeo de campos:** `mano_dominante` (API) ↔ `mano_habil` (BD)

---

## 🧪 Cómo Probar

### Opción 1: Script de prueba automatizado
```bash
cd backend
python test_actualizar_perfil.py
```

### Opción 2: Manualmente con Thunder Client / Postman

**1. Login:**
```
POST http://localhost:8000/auth/login
Content-Type: application/json

{
  "email": "test@test.com",
  "password": "password123"
}
```

**2. Actualizar perfil:**
```
PUT http://localhost:8000/usuarios/perfil
Authorization: Bearer {tu_token}
Content-Type: application/json

{
  "nombre": "Juan",
  "ciudad": "Buenos Aires",
  "posicion_preferida": "drive",
  "mano_dominante": "derecha"
}
```

**3. Verificar cambios:**
```
GET http://localhost:8000/usuarios/me
Authorization: Bearer {tu_token}
```

---

## 📝 Notas Importantes

1. **Mapeo de campos:** El frontend envía `mano_dominante` pero en la BD se guarda como `mano_habil`
2. **Actualización parcial:** No es necesario enviar todos los campos, solo los que se quieren actualizar
3. **Compatibilidad:** El endpoint es compatible con el frontend existente
4. **Validaciones:** Los valores inválidos retornan 400 Bad Request con mensaje descriptivo

---

## 🚀 Próximos Pasos

1. ✅ Endpoint implementado
2. ⏳ Probar con el frontend
3. ⏳ Hacer commit y push
4. ⏳ Desplegar a producción (Railway/Render)

---

**Fecha:** 27/11/2025
**Estado:** ✅ COMPLETADO
**Tiempo de implementación:** ~15 minutos
