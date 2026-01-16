# 🚨 URGENTE: Actualizar CORS en Railway

## Problema Actual
El frontend en `https://drive-plus.com.ar` no puede conectarse al backend porque Railway todavía tiene configurado el dominio antiguo `kioskito.click`.

## Solución: Actualizar Variable de Entorno en Railway

### Pasos:

1. **Ir a Railway Dashboard:**
   - Abrir: https://railway.app
   - Seleccionar el proyecto del backend

2. **Ir a Variables:**
   - Click en el servicio del backend
   - Click en la pestaña "Variables"

3. **Actualizar CORS_ORIGINS:**
   - Buscar la variable `CORS_ORIGINS`
   - Cambiar el valor a:
   ```json
   ["http://localhost:3000", "http://localhost:5173", "https://drive-plus.com.ar", "https://www.drive-plus.com.ar"]
   ```

4. **Guardar y Redesplegar:**
   - Click en "Save"
   - Railway automáticamente redesplegar el backend
   - Esperar 1-2 minutos a que termine el deploy

## Verificar que Funciona

Después del deploy, abrir la consola del navegador en `https://drive-plus.com.ar` y verificar que ya no aparezcan errores de CORS.

## Nota Importante

El código del backend YA está actualizado con el nuevo dominio. Solo falta actualizar la variable de entorno en Railway para que tome efecto en producción.
