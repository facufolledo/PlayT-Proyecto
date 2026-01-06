# 🚗⚡ REBRANDING COMPLETO: PlayT/PlayR → Drive+

## ✅ CAMBIOS COMPLETADOS

### 📱 **Frontend**
- ✅ `package.json` → Nombre cambiado a "drive-plus-padel"
- ✅ `index.html` → Título, meta tags y referencias actualizadas
- ✅ `vite.config.ts` → Base URL cambiada de `/PlayR/` a `/DriveP/`
- ✅ `App.tsx` → Basename actualizado para producción
- ✅ `Landing.tsx`, `Login.tsx`, `Register.tsx` → Logos actualizados
- ✅ `Navbar.tsx` → Logo y texto actualizados a "Drive+"
- ✅ `PWAInstallPrompt.tsx` → "Instalar Drive+"
- ✅ `CorsDebugPage.tsx` → "Diagnóstico CORS - Drive+"
- ✅ Service Workers → Cache names y URLs actualizadas
- ✅ Firebase messaging → Iconos actualizados

### 🔧 **Backend**
- ✅ `main.py` → API title, descripción y logs actualizados a "Drive+ API"
- ✅ URLs de producción → Cambiadas a Railway: `drive-plus-production.up.railway.app`
- ✅ Scripts de testing → URLs actualizadas
- ✅ Mensajes de consola → "Drive+ API" en lugar de "PlayR/PlayT"

### � **Mobilet App**
- ✅ Logger → Referencias cambiadas a "[Drive+]"
- ✅ Pantallas → "Bienvenido a Drive+", "Acerca de Drive+"

### 📋 **Configuración**
- ✅ `produccion.md` → URLs y referencias actualizadas a Railway
- ✅ Scripts de desarrollo → Actualizados con "Drive+"

## 🚨 PRÓXIMOS PASOS MANUALES CRÍTICOS

### 1. 🖼️ **Cambiar Assets (URGENTE)**
```bash
# En frontend/public/:
logo-playr.png → logo-drive-plus.png
```

### 2. 🗂️ **Renombrar Modelo Backend (IMPORTANTE)**
```bash
# En backend/src/models/:
playt_models.py → driveplus_models.py
```
Luego actualizar TODOS los imports en el backend:
```python
# Cambiar en todos los archivos .py:
from src.models.playt_models import → from src.models.driveplus_models import
```

### 3. 🌐 **Hostinger (Frontend)**
```bash
# Cambiar carpeta en Hostinger:
/public_html/PlayR/ → /public_html/DriveP/

# Actualizar .htaccess:
RewriteBase /DriveP/
ErrorDocument 404 /DriveP/index.html
```

### 4. 🚂 **Railway (Backend)**
- ✅ URL ya actualizada: `drive-plus-production.up.railway.app`
- Hacer deploy del código actualizado
- Verificar variables de entorno

### 5. 🔥 **Firebase**
- Actualizar configuración del proyecto si es necesario
- Verificar que las notificaciones funcionen con nuevos iconos

## 📋 CHECKLIST DE VERIFICACIÓN

### ✅ **Desarrollo Local**
- [ ] Ejecutar `start-dev.bat` y verificar que funcione
- [ ] Verificar que aparezca "Drive+" en el título del navegador
- [ ] Verificar logs de consola con "Drive+ API"
- [ ] Probar funcionalidades principales

### ✅ **Frontend en Producción**
- [ ] Hacer `npm run build`
- [ ] Subir carpeta `dist/` a `/public_html/DriveP/` en Hostinger
- [ ] Verificar que `https://kioskito.click/DriveP/` funcione
- [ ] Verificar que el título sea "Drive+"

### ✅ **Backend en Producción**
- [ ] Hacer deploy en Railway con código actualizado
- [ ] Verificar que `https://drive-plus-production.up.railway.app/health` responda
- [ ] Verificar que la respuesta diga "Drive+ API"

### ✅ **Integración**
- [ ] Verificar CORS entre frontend y backend
- [ ] Probar login y funcionalidades principales
- [ ] Verificar que no haya referencias a "PlayT/PlayR" en la UI

## 🎯 RESULTADO FINAL

Después de completar todos los pasos:

- ✅ **Nombre**: Drive+ (en lugar de PlayT/PlayR)
- ✅ **URL Frontend**: `https://kioskito.click/DriveP/`
- ✅ **URL Backend**: `https://drive-plus-production.up.railway.app`
- ✅ **Desarrollo**: Scripts actualizados con "Drive+"
- ✅ **Branding**: Consistente en toda la aplicación

---

**Estado**: 🟢 **CASI COMPLETO** - Solo faltan pasos manuales críticos
**Próximo paso**: Cambiar logo y renombrar modelo backend