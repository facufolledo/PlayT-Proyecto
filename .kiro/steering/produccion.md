# Consideraciones de Producción - Drive+

## Entorno de Producción

- **Frontend**: Hosteado en `drive-plus.com.ar` (Hostinger)
- **Backend**: Hosteado en Railway (`drive-plus-production.up.railway.app`)
- **Base de datos**: PostgreSQL en Railway

## CORS - Siempre incluir dominios de producción

Cuando se modifique `backend/main.py`, asegurar que CORS incluya:
```python
origins = [
    "http://localhost:3000",
    "http://localhost:5173",
    "https://drive-plus.com.ar",
    "https://www.drive-plus.com.ar"
]
```

## Autenticación Firebase

- El frontend usa tokens de Firebase (`firebase_token` en localStorage)
- El backend valida estos tokens con Firebase Admin SDK
- En producción, las credenciales de Firebase se pasan por variable de entorno `FIREBASE_CREDENTIALS_JSON`

## Checklist al crear nuevos endpoints

1. ✅ Verificar que el método HTTP sea correcto (POST, GET, PUT, DELETE)
2. ✅ Incluir `Depends(get_current_user)` si requiere autenticación
3. ✅ Probar en localhost Y en producción
4. ✅ Verificar que CORS permita el método usado
5. ✅ Manejar errores con mensajes claros

## Variables de Entorno en Producción

El backend en Railway necesita:
- `DATABASE_URL` - URL de PostgreSQL
- `FIREBASE_CREDENTIALS_JSON` - Credenciales de Firebase (JSON string)
- `CORS_ORIGINS` - Lista de orígenes permitidos
- `SECRET_KEY` - Clave secreta para JWT

## Testing antes de deploy

```bash
# Probar endpoint con cURL simulando producción
curl -X POST "https://drive-plus-production.up.railway.app/torneos/1/inscribir" \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"jugador1_id": 1, "jugador2_id": 2, "nombre_pareja": "Test"}'
```
