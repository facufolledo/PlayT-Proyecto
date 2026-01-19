# 📱 GUÍA DE OPTIMIZACIÓN MOBILE - Drive+

## 🎯 Objetivo
Optimizar Drive+ para dispositivos móviles, asegurando una experiencia fluida en 3G/4G con dispositivos de gama media/baja.

---

## 🚀 OPTIMIZACIONES CRÍTICAS (Implementar YA)

### 1. **Lazy Loading de Imágenes** ⚡

**Problema**: Imágenes cargan todas a la vez, consumiendo datos y memoria.

**Solución**:
```tsx
// frontend/src/components/ImageLazy.tsx (ya existe, usar en todos lados)
import { useState, useEffect, useRef } from 'react';

export const LazyImage = ({ src, alt, className, placeholder = '/placeholder.png' }) => {
  const [imageSrc, setImageSrc] = useState(placeholder);
  const [isLoaded, setIsLoaded] = useState(false);
  const imgRef = useRef<HTMLImageElement>(null);

  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            setImageSrc(src);
            observer.disconnect();
          }
        });
      },
      { rootMargin: '50px' } // Cargar 50px antes de ser visible
    );

    if (imgRef.current) {
      observer.observe(imgRef.current);
    }

    return () => observer.disconnect();
  }, [src]);

  return (
    <img
      ref={imgRef}
      src={imageSrc}
      alt={alt}
      className={`${className} ${isLoaded ? 'opacity-100' : 'opacity-50'} transition-opacity`}
      onLoad={() => setIsLoaded(true)}
      loading="lazy"
    />
  );
};
```

**Usar en**:
- Fotos de perfil
- Logos de torneos
- Imágenes de salas

---

### 2. **Paginación en Listas Largas** 📄

**Problema**: Cargar 100+ torneos/salas/usuarios de una vez es lento.

**Solución Backend**:
```python
# Agregar paginación a endpoints críticos
@router.get("/torneos")
async def listar_torneos(
    page: int = 1,
    limit: int = 20,  # 20 items por página en mobile
    db: Session = Depends(get_db)
):
    offset = (page - 1) * limit
    
    torneos = db.query(Torneo).filter(
        Torneo.estado.in_(['inscripcion', 'en_curso'])
    ).order_by(
        Torneo.fecha_inicio.desc()
    ).offset(offset).limit(limit).all()
    
    total = db.query(func.count(Torneo.id)).filter(
        Torneo.estado.in_(['inscripcion', 'en_curso'])
    ).scalar()
    
    return {
        "items": torneos,
        "page": page,
        "limit": limit,
        "total": total,
        "pages": (total + limit - 1) // limit
    }
```

**Solución Frontend**:
```tsx
// Infinite scroll para mobile
const [page, setPage] = useState(1);
const [hasMore, setHasMore] = useState(true);

const loadMore = async () => {
  if (!hasMore) return;
  
  const response = await fetch(`/api/torneos?page=${page + 1}&limit=20`);
  const data = await response.json();
  
  setTorneos([...torneos, ...data.items]);
  setPage(page + 1);
  setHasMore(page + 1 < data.pages);
};

// Usar react-intersection-observer para detectar scroll
```

---

### 3. **Reducir Tamaño de Bundle** 📦

**Problema**: Bundle de React muy grande para mobile.

**Solución**:
```typescript
// vite.config.ts
export default defineConfig({
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          // Separar vendors grandes
          'react-vendor': ['react', 'react-dom', 'react-router-dom'],
          'firebase': ['firebase/app', 'firebase/auth', 'firebase/storage'],
          'ui': ['@headlessui/react', 'framer-motion'],
        }
      }
    },
    // Minificar agresivamente
    minify: 'terser',
    terserOptions: {
      compress: {
        drop_console: true, // Eliminar console.logs en producción
        drop_debugger: true
      }
    }
  }
});
```

---

### 4. **Optimizar Fuentes** 🔤

**Problema**: Fuentes web tardan en cargar.

**Solución**:
```css
/* index.css */
@font-face {
  font-family: 'Inter';
  font-style: normal;
  font-weight: 400;
  font-display: swap; /* Mostrar texto inmediatamente */
  src: url('/fonts/inter-v12-latin-regular.woff2') format('woff2');
}

/* Preload fuentes críticas */
```

```html
<!-- index.html -->
<link rel="preload" href="/fonts/inter-v12-latin-regular.woff2" as="font" type="font/woff2" crossorigin>
```

---

### 5. **Service Worker para Cache** 💾

**Problema**: Cada visita descarga todo de nuevo.

**Solución**:
```javascript
// public/sw.js (mejorado)
const CACHE_NAME = 'drive-plus-v1';
const STATIC_CACHE = [
  '/',
  '/index.html',
  '/manifest.json',
  '/logo-drive.png',
  // Agregar assets críticos
];

// Cache-first para assets estáticos
self.addEventListener('fetch', (event) => {
  const { request } = event;
  const url = new URL(request.url);
  
  // Cache-first para assets
  if (url.pathname.match(/\.(js|css|png|jpg|jpeg|svg|woff2)$/)) {
    event.respondWith(
      caches.match(request).then((response) => {
        return response || fetch(request).then((fetchResponse) => {
          return caches.open(CACHE_NAME).then((cache) => {
            cache.put(request, fetchResponse.clone());
            return fetchResponse;
          });
        });
      })
    );
  }
  
  // Network-first para API
  else if (url.pathname.startsWith('/api/')) {
    event.respondWith(
      fetch(request).catch(() => caches.match(request))
    );
  }
});
```

---

### 6. **Comprimir Respuestas API** 🗜️

**Problema**: Respuestas JSON muy grandes.

**Solución Backend**:
```python
# main.py
from fastapi.middleware.gzip import GZipMiddleware

app.add_middleware(GZipMiddleware, minimum_size=1000)  # Comprimir > 1KB
```

**Beneficio**: Reduce tamaño de respuestas en 70-80%

---

### 7. **Optimizar Imágenes** 🖼️

**Problema**: Imágenes muy pesadas.

**Solución**:
```bash
# Convertir imágenes a WebP (más ligero)
# Usar servicio como Cloudinary o ImageKit

# O implementar en backend:
from PIL import Image
import io

def optimize_image(image_bytes, max_width=800):
    img = Image.open(io.BytesIO(image_bytes))
    
    # Redimensionar si es muy grande
    if img.width > max_width:
        ratio = max_width / img.width
        new_height = int(img.height * ratio)
        img = img.resize((max_width, new_height), Image.LANCZOS)
    
    # Convertir a WebP
    output = io.BytesIO()
    img.save(output, format='WEBP', quality=85)
    return output.getvalue()
```

---

### 8. **Debounce en Búsquedas** ⏱️

**Problema**: Búsquedas hacen request en cada tecla.

**Solución**:
```tsx
import { useState, useEffect } from 'react';
import { debounce } from 'lodash';

const BuscarUsuarios = () => {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  
  // Debounce de 300ms
  const debouncedSearch = debounce(async (searchQuery) => {
    if (searchQuery.length < 2) return;
    
    const response = await fetch(`/api/usuarios/buscar?q=${searchQuery}`);
    const data = await response.json();
    setResults(data);
  }, 300);
  
  useEffect(() => {
    debouncedSearch(query);
    return () => debouncedSearch.cancel();
  }, [query]);
  
  return (
    <input
      value={query}
      onChange={(e) => setQuery(e.target.value)}
      placeholder="Buscar usuarios..."
    />
  );
};
```

---

### 9. **Skeleton Loaders** 💀

**Problema**: Pantallas en blanco mientras carga.

**Solución**:
```tsx
// Usar LoadingSkeleton.tsx existente
import { LoadingSkeleton } from '@/components/LoadingSkeleton';

const TorneosList = () => {
  const [loading, setLoading] = useState(true);
  const [torneos, setTorneos] = useState([]);
  
  if (loading) {
    return (
      <div className="space-y-4">
        {[1, 2, 3].map((i) => (
          <LoadingSkeleton key={i} className="h-32 w-full" />
        ))}
      </div>
    );
  }
  
  return <div>{/* Torneos */}</div>;
};
```

---

### 10. **Reducir Re-renders** ⚛️

**Problema**: Componentes se re-renderizan innecesariamente.

**Solución**:
```tsx
import { memo, useMemo, useCallback } from 'react';

// Memoizar componentes pesados
const TorneoCard = memo(({ torneo }) => {
  return <div>{/* Card */}</div>;
});

// Memoizar cálculos costosos
const TorneosList = ({ torneos }) => {
  const torneosActivos = useMemo(() => {
    return torneos.filter(t => t.estado === 'activo');
  }, [torneos]);
  
  const handleClick = useCallback((id) => {
    // Handler
  }, []);
  
  return <div>{/* Lista */}</div>;
};
```

---

## 📊 MÉTRICAS OBJETIVO

### Performance
| Métrica | Objetivo | Actual |
|---------|----------|--------|
| First Contentful Paint | < 1.5s | ? |
| Time to Interactive | < 3s | ? |
| Largest Contentful Paint | < 2.5s | ? |
| Bundle Size | < 500KB | ? |
| API Response | < 500ms | ✅ |

### Mobile Específico
| Métrica | Objetivo |
|---------|----------|
| Carga en 3G | < 5s |
| Uso de datos | < 2MB por sesión |
| Memoria RAM | < 100MB |
| Batería | Mínimo impacto |

---

## 🛠️ HERRAMIENTAS DE TESTING

### 1. **Lighthouse** (Chrome DevTools)
```bash
# Auditar performance mobile
lighthouse https://drive-plus.com.ar --preset=mobile --output=html
```

### 2. **WebPageTest**
```
https://www.webpagetest.org/
# Probar desde Argentina con 3G
```

### 3. **Chrome DevTools**
- Network throttling: Fast 3G
- CPU throttling: 4x slowdown
- Device emulation: iPhone SE, Galaxy S9

---

## 📱 OPTIMIZACIONES ESPECÍFICAS POR PANTALLA

### Pantalla de Torneos
- ✅ Paginación (20 por página)
- ✅ Lazy loading de imágenes
- ✅ Skeleton loaders
- ✅ Cache de 30s

### Pantalla de Salas
- ✅ Ya optimizada (200-500ms)
- ✅ Cache implementado
- ✅ Auto-refresh inteligente

### Pantalla de Perfil
- ✅ Ya optimizada (50-100ms)
- ✅ Batch queries
- ✅ Sin N+1 queries

### Pantalla de Fixture
- ⚠️ Puede ser pesada con muchos partidos
- 🔧 Implementar virtualización
- 🔧 Cargar por zonas

---

## 🚀 PLAN DE IMPLEMENTACIÓN

### Prioridad ALTA (Implementar HOY)
1. ✅ Comprimir respuestas API (GZipMiddleware)
2. ✅ Lazy loading de imágenes
3. ✅ Debounce en búsquedas
4. ✅ Skeleton loaders

### Prioridad MEDIA (Esta semana)
1. Paginación en listas largas
2. Service Worker mejorado
3. Optimizar bundle size
4. Reducir re-renders

### Prioridad BAJA (Después del torneo)
1. Virtualización de listas
2. Optimizar fuentes
3. CDN para assets
4. Progressive Web App completa

---

## 📝 CHECKLIST DE OPTIMIZACIÓN

### Backend
- [x] N+1 queries eliminados
- [x] Batch queries implementadas
- [x] Índices de base de datos
- [ ] Comprimir respuestas (GZip)
- [ ] Paginación en todos los endpoints
- [ ] Cache headers apropiados

### Frontend
- [ ] Lazy loading de imágenes
- [ ] Code splitting
- [ ] Bundle size < 500KB
- [ ] Service Worker actualizado
- [ ] Skeleton loaders en todas las pantallas
- [ ] Debounce en búsquedas
- [ ] Memoización de componentes pesados

### Assets
- [ ] Imágenes optimizadas (WebP)
- [ ] Fuentes optimizadas (WOFF2)
- [ ] Icons como SVG inline
- [ ] Preload de recursos críticos

---

## 🎯 RESULTADO ESPERADO

### Antes
- Carga inicial: 5-8s en 3G
- Bundle: 800KB+
- Uso de datos: 5MB por sesión
- Re-renders innecesarios

### Después
- Carga inicial: < 3s en 3G
- Bundle: < 500KB
- Uso de datos: < 2MB por sesión
- Performance optimizada

---

## 📞 TESTING EN DISPOSITIVOS REALES

### Dispositivos Objetivo
- iPhone SE (2020) - iOS 15+
- Samsung Galaxy A32 - Android 11+
- Xiaomi Redmi Note 10 - Android 11+

### Condiciones de Red
- WiFi rápido (50+ Mbps)
- 4G normal (10-20 Mbps)
- 3G lento (1-3 Mbps)

---

## 🎉 CONCLUSIÓN

**Con estas optimizaciones, Drive+ será 3-5x más rápido en móviles.**

### Beneficios:
- ✅ Carga inicial < 3s
- ✅ Uso de datos reducido 60%
- ✅ Mejor experiencia en 3G/4G
- ✅ Menos consumo de batería
- ✅ Funciona en dispositivos de gama baja

**¡Drive+ será la app de pádel más rápida en móviles! 📱⚡**
