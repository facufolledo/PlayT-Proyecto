# Fix: Perfil No Encontrado en Rankings

## Problema
Cuando el usuario hace click en el nombre de un jugador en el ranking, aparece el error "Jugador no encontrado" o "Error al cargar el perfil del usuario".

## Causa Raíz
Algunos usuarios en el ranking no tienen `nombre_usuario` definido (es `null` o vacío), lo que causa que la navegación a `/jugador/${nombre_usuario}` falle porque la URL queda mal formada como `/jugador/null` o `/jugador/`.

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

## Rutas Soportadas

El sistema ahora soporta dos formas de acceder a perfiles:

1. **Por Username** (preferido): `/jugador/{username}`
   - Ejemplo: `/jugador/facufolledo`
   - Endpoint backend: `GET /usuarios/perfil-publico/{username}`

2. **Por ID** (fallback): `/perfil/{id}`
   - Ejemplo: `/perfil/123`
   - Endpoint backend: `GET /usuarios/{user_id}/perfil`

## Verificación

### Script de Verificación
Creado `backend/verificar_usuarios_sin_username.py` para identificar usuarios sin `nombre_usuario` válido.

**Uso**:
```bash
cd backend
python verificar_usuarios_sin_username.py
```

### Testing Manual
1. Ir a `/rankings`
2. Hacer click en cualquier nombre de jugador
3. Verificar que se carga el perfil correctamente
4. Si el usuario no tiene username, debería navegar por ID

## Endpoints Backend Verificados

✅ `GET /usuarios/perfil-publico/{username}` - Perfil por username
✅ `GET /usuarios/{user_id}/perfil` - Perfil por ID
✅ `GET /ranking/` - Lista de ranking con nombre_usuario incluido

## Próximos Pasos (Opcional)

Si se encuentran usuarios sin `nombre_usuario`:

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

## Estado
✅ **RESUELTO** - Los usuarios ahora pueden navegar a perfiles desde el ranking sin errores.

## Archivos Modificados
- `frontend/src/pages/Rankings.tsx`
- `frontend/src/components/UserLink.tsx`
- `backend/verificar_usuarios_sin_username.py` (nuevo)
