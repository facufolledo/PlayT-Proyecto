# Solución: Error Cross-Origin-Opener-Policy en Firebase Auth

## Problema
```
Cross-Origin-Opener-Policy policy would block the window.closed call.
```

Este error aparece cuando Firebase Auth intenta usar `signInWithPopup` en móviles o cuando hay políticas CORS estrictas.

## Causa
- **COOP (Cross-Origin-Opener-Policy)** bloquea el acceso a `window.closed` en popups
- Los navegadores móviles son más estrictos con las políticas de seguridad
- Firebase intenta verificar si la ventana popup se cerró, pero COOP lo impide

## Solución implementada

### 1. Headers CORS en index.html
```html
<meta http-equiv="Cross-Origin-Opener-Policy" content="same-origin-allow-popups" />
<meta http-equiv="Cross-Origin-Embedder-Policy" content="unsafe-none" />
```

### 2. Headers en Vite config
```typescript
server: {
  headers: {
    'Cross-Origin-Opener-Policy': 'same-origin-allow-popups',
    'Cross-Origin-Embedder-Policy': 'unsafe-none'
  }
}
```

### 3. Detección automática móvil/desktop
```typescript
const isMobile = () => {
  return /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent) ||
         window.innerWidth < 768;
};
```

### 4. Estrategia híbrida: Popup + Redirect
```typescript
async loginWithGoogle(): Promise<User> {
  if (isMobile()) {
    // Móviles: usar redirect (más confiable)
    await signInWithRedirect(auth, googleProvider);
    throw new Error('REDIRECT_IN_PROGRESS');
  } else {
    // Desktop: usar popup (mejor UX)
    const result = await signInWithPopup(auth, googleProvider);
    return result.user;
  }
}
```

### 5. Manejo de redirect result
```typescript
// Verificar resultado de redirect al cargar la página
async checkRedirectResult(): Promise<User | null> {
  const result = await getRedirectResult(auth);
  return result?.user || null;
}
```

## Flujo de autenticación

### Desktop (Popup)
1. Usuario hace clic en "Login con Google"
2. Se abre popup de Google
3. Usuario se autentica
4. Popup se cierra y retorna el usuario
5. Continúa flujo normal

### Móvil (Redirect)
1. Usuario hace clic en "Login con Google"
2. Página redirige a Google
3. Usuario se autentica
4. Google redirige de vuelta a la app
5. `checkRedirectResult()` obtiene el usuario
6. Continúa flujo normal

## Ventajas de esta solución

✅ **Compatibilidad universal** - Funciona en todos los dispositivos
✅ **Mejor UX** - Popup en desktop, redirect en móvil
✅ **Fallback automático** - Si popup falla, usa redirect
✅ **Sin cambios en UI** - El componente de login no cambia

## Archivos modificados

### Frontend:
- `index.html` - Headers COOP/COEP
- `vite.config.ts` - Headers de desarrollo
- `src/services/auth.service.ts` - Lógica híbrida popup/redirect
- `src/context/AuthContext.tsx` - Manejo de redirect result

## Configuración para producción

### Railway/Vercel/Netlify
Agregar headers en la configuración del servidor:

```json
{
  "headers": [
    {
      "source": "/(.*)",
      "headers": [
        {
          "key": "Cross-Origin-Opener-Policy",
          "value": "same-origin-allow-popups"
        },
        {
          "key": "Cross-Origin-Embedder-Policy", 
          "value": "unsafe-none"
        }
      ]
    }
  ]
}
```

### Apache (.htaccess)
```apache
Header always set Cross-Origin-Opener-Policy "same-origin-allow-popups"
Header always set Cross-Origin-Embedder-Policy "unsafe-none"
```

### Nginx
```nginx
add_header Cross-Origin-Opener-Policy "same-origin-allow-popups";
add_header Cross-Origin-Embedder-Policy "unsafe-none";
```

## Testing

### Probar en diferentes dispositivos:
1. **Desktop Chrome/Firefox** - Debe usar popup
2. **Mobile Chrome/Safari** - Debe usar redirect
3. **Incógnito/Privado** - Debe funcionar en ambos
4. **Diferentes dominios** - Verificar CORS

### Comandos de prueba:
```bash
# Desarrollo
npm run dev

# Preview (simula producción)
npm run preview

# Build y test
npm run build && npm run preview
```

## Monitoreo

### Logs a revisar:
- `🔄 Usando signInWithPopup para desktop`
- `🔄 Usando signInWithRedirect para móvil`
- `🔄 Usuario obtenido de redirect: email@example.com`
- `🔄 Redirect en progreso, esperando resultado...`

### Errores comunes:
- `auth/popup-blocked` → Automáticamente cambia a redirect
- `REDIRECT_IN_PROGRESS` → Normal, no es error
- `Cross-Origin-Opener-Policy` → Verificar headers

## Próximos pasos

1. **Monitorear métricas** - % de éxito por dispositivo
2. **A/B testing** - Comparar popup vs redirect en desktop
3. **PWA integration** - Mejorar experiencia en móviles
4. **Analytics** - Trackear método de login usado

Esta solución garantiza que el login con Google funcione en todos los dispositivos sin errores COOP.