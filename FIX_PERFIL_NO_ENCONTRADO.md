# Fix: Perfil No Encontrado en Rankings

## Problema
Cuando el usuario hace click en el nombre de un jugador en el ranking, aparece el error "Jugador no encontrado" o "Error al cargar el perfil del usuario".

## Causas Raíz

### 1. Usuarios sin nombre_usuario
Algunos usuarios en el ranking no tienen `nombre_usuario` definido (es `null` o vacío), lo que causa que la navegación a `/jugador/${nombre_usuario}` falle porque la URL queda mal formada como `/jugador/null` o `/jugador/`.

### 2. Usuarios sin perfil asociado (ERROR 500)
Algunos usuarios existen en la tabla `usuarios` pero NO tienen registro en la tabla `perfil_usuario`. El endpoint estaba haciendo `JOIN` (inner join) lo que causaba que la query no devolviera nada y fallara con error 500.

**Ejemplo**: Usuario `francoayet07` existe en `usuarios` pero no tiene perfil en `perfil_usuario`.

## Solución Implementada

### 1. Frontend - Rankings.tsx
**Archivo**: `frontend/src/pages/Rankings.tsx`

Agregado validación antes de navegar:
```typescript
onClick={() => {
  // Navegar por username si existe, sino por ID
  if (jugador.nombre_usuario && jugador.nombre_usuario.trim() !== '') {
    navigate(`/jugador/${jugador.nombre_usuario}`);
  } else if (jugador.id_usuario || jugador.id) {
    navigate(`/perfil/${jugador.id_usuario || jugador.id}`);
  }
}}
```

**Cambios**:
- ✅ Verifica que `nombre_usuario` exista y no esté vacío
- ✅ Si no existe, usa el ID como fallback: `/perfil/{id}`
- ✅ Muestra "sin-usuario" en lugar de `null` en la UI

### 2. Frontend - UserLink.tsx
**Archivo**: `frontend/src/components/UserLink.tsx`

Mejorada la lógica de navegación:
```typescript
if (nombreUsuario && nombreUsuario.trim() !== '' && nombreUsuario !== 'sin-usuario') {
  destino = `/jugador/${nombreUsuario}`;
} else if (tieneIdValido) {
  destino = `/perfil/${userIdNum}`;
}
```

**Cambios**:
- ✅ Valida que `nombreUsuario` sea válido (no vacío, no "sin-usuario")
- ✅ Fallback a navegación por ID si no hay username válido
- ✅ Previene navegación a URLs inválidas

### 3. Backend - usuario_controller.py (CRÍTICO)
**Archivo**: `backend/src/controllers/usuario_controller.py`

Cambiado `JOIN` a `OUTERJOIN` en todos los endpoints de perfil:

#### Endpoint: `/usuarios/perfil-publico/{username}`
```python
# ANTES (causaba error 500 si no había perfil)
).join(
    PerfilUsuario, Usuario.id_usuario == PerfilUsuario.id_usuario
)

# DESPUÉS (funciona incluso sin perfil)
).outerjoin(
    PerfilUsuario, Usuario.id_usuario == PerfilUsuario.id_usuario
)
```

#### Manejo de datos faltantes:
```python
# Manejar caso donde no hay perfil (nombre y apellido pueden ser None)
nombre = resultado.nombre or "Usuario"
apellido = resultado.apellido or ""
nombre_completo = f"{nombre} {apellido}".strip()

return {
    "nombre": nombre,
    "apellido": apellido,
    "nombre_completo": nombre_completo,
    "ciudad": resultado.ciudad or "",
    "pais": resultado.pais or "Argentina",
    # ... resto de campos con valores por defecto
}
```

**Endpoints arreglados**:
- ✅ `GET /usuarios/perfil-publico/{username}` - Perfil por username
- ✅ `GET /usuarios/{user_id}/perfil` - Perfil por ID  
- ✅ `GET /usuarios/buscar-publico` - Búsqueda de usuarios

## Rutas Soportadas

El sistema ahora soporta dos formas de acceder a perfiles:

1. **Por Username** (preferido): `/jugador/{username}`
   - Ejemplo: `/jugador/facufolledo`
   - Endpoint backend: `GET /usuarios/perfil-publico/{username}`

2. **Por ID** (fallback): `/perfil/{id}`
   - Ejemplo: `/perfil/123`
   - Endpoint backend: `GET /usuarios/{user_id}/perfil`

## Verificación

### Script de Verificación - Usuarios sin username
**Archivo**: `backend/verificar_usuarios_sin_username.py`

Identifica usuarios sin `nombre_usuario` válido.

**Uso**:
```bash
cd backend
python verificar_usuarios_sin_username.py
```

### Script de Debug - Usuario específico
**Archivo**: `backend/debug_perfil_francoayet07.py`

Debug completo de un usuario específico para identificar problemas.

**Uso**:
```bash
cd backend
python debug_perfil_francoayet07.py
```

### Testing Manual
1. Ir a `/rankings`
2. Hacer click en cualquier nombre de jugador
3. Verificar que se carga el perfil correctamente
4. Si el usuario no tiene username, debería navegar por ID
5. Si el usuario no tiene perfil, debería mostrar datos por defecto

## Endpoints Backend Verificados

✅ `GET /usuarios/perfil-publico/{username}` - Perfil por username (con OUTERJOIN)
✅ `GET /usuarios/{user_id}/perfil` - Perfil por ID (con OUTERJOIN)
✅ `GET /usuarios/buscar-publico` - Búsqueda (con OUTERJOIN)
✅ `GET /ranking/` - Lista de ranking con nombre_usuario incluido

## Próximos Pasos (Opcional)

### Si se encuentran usuarios sin nombre_usuario:

1. **Generar usernames automáticamente**:
   ```sql
   UPDATE usuarios 
   SET nombre_usuario = LOWER(CONCAT(
     SUBSTRING(email FROM 1 FOR POSITION('@' IN email) - 1),
     id_usuario
   ))
   WHERE nombre_usuario IS NULL OR nombre_usuario = '';
   ```

2. **Agregar constraint en la base de datos**:
   ```sql
   ALTER TABLE usuarios 
   ALTER COLUMN nombre_usuario SET NOT NULL;
   
   ALTER TABLE usuarios 
   ADD CONSTRAINT nombre_usuario_not_empty 
   CHECK (TRIM(nombre_usuario) != '');
   ```

### Si se encuentran usuarios sin perfil:

1. **Crear perfiles automáticamente**:
   ```sql
   INSERT INTO perfil_usuario (id_usuario, nombre, apellido, pais)
   SELECT 
     u.id_usuario,
     'Usuario',
     CAST(u.id_usuario AS VARCHAR),
     'Argentina'
   FROM usuarios u
   LEFT JOIN perfil_usuario p ON u.id_usuario = p.id_usuario
   WHERE p.id_usuario IS NULL;
   ```

2. **O hacer que perfil sea opcional** (ya implementado con OUTERJOIN)

## Estado
✅ **RESUELTO** - Los usuarios ahora pueden navegar a perfiles desde el ranking sin errores, incluso si:
- No tienen `nombre_usuario` definido
- No tienen perfil asociado en `perfil_usuario`

## Archivos Modificados
- `frontend/src/pages/Rankings.tsx`
- `frontend/src/components/UserLink.tsx`
- `backend/src/controllers/usuario_controller.py` (CRÍTICO - cambio de JOIN a OUTERJOIN)
- `backend/verificar_usuarios_sin_username.py` (nuevo)
- `backend/debug_perfil_francoayet07.py` (nuevo)
