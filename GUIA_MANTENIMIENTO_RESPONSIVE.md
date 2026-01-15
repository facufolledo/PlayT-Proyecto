# 📘 Guía de Mantenimiento - Responsive Design

## 🎯 Objetivo

Esta guía te ayudará a mantener la optimización responsive al agregar nuevos componentes o features a Drive+.

---

## ✅ Checklist para Nuevos Componentes

Antes de considerar un componente "terminado", verifica:

### 1. Layout Responsive
- [ ] Grid adaptativo (1/2/3 columnas según breakpoint)
- [ ] Flex direction cambia en móvil si es necesario
- [ ] Padding responsive (p-2 móvil, p-4 desktop)
- [ ] Margins adaptativos
- [ ] Max-width para contenido muy ancho

### 2. Tipografía
- [ ] Tamaños de fuente escalables (text-xs/text-base)
- [ ] Line height adecuado para lectura
- [ ] Truncate en textos largos con `truncate`
- [ ] Contraste suficiente (WCAG AA mínimo)
- [ ] Font weight apropiado (bold para destacar)

### 3. Elementos Interactivos
- [ ] Botones mínimo 44x44px en móvil
- [ ] Áreas táctiles amplias
- [ ] Estados hover/active/focus visibles
- [ ] Feedback visual en interacciones
- [ ] Disabled state claro

### 4. Imágenes y Media
- [ ] Responsive images con max-w-full
- [ ] Lazy loading implementado
- [ ] Fallbacks para errores
- [ ] Alt text descriptivo
- [ ] Aspect ratio preservado

### 5. Tablas
- [ ] Scroll horizontal en móvil
- [ ] Columnas prioritarias visibles
- [ ] Columnas secundarias ocultas (hidden md:table-cell)
- [ ] Header sticky opcional
- [ ] Paginación si hay muchos datos

### 6. Modales
- [ ] Max height 90vh
- [ ] Scroll interno si es necesario
- [ ] Padding responsive
- [ ] Botones grandes en móvil
- [ ] Cierre fácil (X, backdrop, ESC)

### 7. Formularios
- [ ] Inputs grandes en móvil (min 44px height)
- [ ] Labels visibles y descriptivos
- [ ] Errores claros y visibles
- [ ] Validación en tiempo real
- [ ] Submit button destacado

### 8. Performance
- [ ] Lazy loading si es pesado
- [ ] Memoización si re-renderiza mucho
- [ ] Debounce en búsquedas
- [ ] Skeleton loader mientras carga
- [ ] Animaciones condicionales (useReducedMotion)

---

## 🎨 Patrones de Código

### Pattern 1: Grid Responsive Básico
```tsx
<div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
  {items.map(item => (
    <Card key={item.id}>{item.content}</Card>
  ))}
</div>
```

### Pattern 2: Texto Escalable
```tsx
<h1 className="text-2xl md:text-4xl font-bold">
  Título Principal
</h1>
<p className="text-xs md:text-base text-textSecondary">
  Descripción secundaria
</p>
```

### Pattern 3: Padding Responsive
```tsx
<div className="p-3 md:p-6">
  <div className="space-y-2 md:space-y-4">
    {/* Contenido */}
  </div>
</div>
```

### Pattern 4: Iconos Adaptativos
```tsx
<Icon 
  size={14} 
  className="md:w-6 md:h-6" 
/>
```

### Pattern 5: Dual Layout (Móvil/Desktop)
```tsx
{/* Vista Móvil */}
<div className="block md:hidden">
  <MobileLayout />
</div>

{/* Vista Desktop */}
<div className="hidden md:block">
  <DesktopLayout />
</div>
```

### Pattern 6: Scroll Horizontal en Filtros
```tsx
<div className="overflow-x-auto -mx-4 px-4 md:mx-0 md:px-0 pb-2">
  <div className="flex gap-2 min-w-max">
    {filters.map(filter => (
      <Button key={filter.id} size="sm">
        {filter.label}
      </Button>
    ))}
  </div>
</div>
```

### Pattern 7: Tabla Responsive
```tsx
{/* Desktop */}
<div className="hidden md:block overflow-x-auto">
  <table className="w-full">
    {/* Tabla completa */}
  </table>
</div>

{/* Móvil */}
<div className="md:hidden space-y-2">
  {items.map(item => (
    <Card key={item.id}>
      {/* Card compacta con info prioritaria */}
    </Card>
  ))}
</div>
```

### Pattern 8: Modal Responsive
```tsx
<div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50 p-4">
  <motion.div
    initial={{ opacity: 0, scale: 0.95 }}
    animate={{ opacity: 1, scale: 1 }}
    className="bg-cardBg rounded-2xl w-full max-w-lg max-h-[90vh] overflow-y-auto"
  >
    <div className="p-4 md:p-6">
      {/* Contenido */}
    </div>
  </motion.div>
</div>
```

### Pattern 9: Glow Effects Solo Desktop
```tsx
<div className="group relative">
  {/* Glow effect - solo desktop */}
  <div className="hidden md:block absolute -inset-[1px] bg-gradient-to-br from-primary to-secondary opacity-0 group-hover:opacity-100 transition-opacity duration-200 rounded-xl -z-10 blur-sm" />
  
  {/* Contenido */}
  <div className="relative z-10">
    {/* ... */}
  </div>
</div>
```

### Pattern 10: Animaciones Condicionales
```tsx
import { useReducedMotion } from 'framer-motion';

function Component() {
  const shouldReduceMotion = useReducedMotion();
  
  return (
    <motion.div
      initial={shouldReduceMotion ? false : { opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={shouldReduceMotion ? { duration: 0 } : { duration: 0.3 }}
    >
      {/* Contenido */}
    </motion.div>
  );
}
```

---

## 🚫 Anti-Patrones (Evitar)

### ❌ 1. Tamaños Fijos
```tsx
// MAL
<div className="w-[300px] h-[200px]">

// BIEN
<div className="w-full max-w-md h-auto">
```

### ❌ 2. Texto Muy Pequeño
```tsx
// MAL
<p className="text-[8px]">

// BIEN
<p className="text-xs md:text-sm">
```

### ❌ 3. Botones Pequeños en Móvil
```tsx
// MAL
<button className="px-2 py-1 text-xs">

// BIEN
<button className="px-4 py-3 text-sm md:text-base min-h-[44px]">
```

### ❌ 4. Tablas Sin Scroll
```tsx
// MAL
<table className="w-full">

// BIEN
<div className="overflow-x-auto">
  <table className="w-full min-w-[600px]">
```

### ❌ 5. Modales Sin Max Height
```tsx
// MAL
<div className="bg-white rounded-lg p-6">

// BIEN
<div className="bg-white rounded-lg p-6 max-h-[90vh] overflow-y-auto">
```

### ❌ 6. Animaciones Pesadas Siempre
```tsx
// MAL
<motion.div
  animate={{ rotate: 360 }}
  transition={{ duration: 2, repeat: Infinity }}
>

// BIEN
const shouldReduceMotion = useReducedMotion();

<motion.div
  animate={shouldReduceMotion ? {} : { rotate: 360 }}
  transition={shouldReduceMotion ? {} : { duration: 2, repeat: Infinity }}
>
```

### ❌ 7. Grid Sin Responsive
```tsx
// MAL
<div className="grid grid-cols-3 gap-4">

// BIEN
<div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
```

### ❌ 8. Padding Fijo
```tsx
// MAL
<div className="p-6">

// BIEN
<div className="p-3 md:p-6">
```

---

## 🔍 Testing Checklist

Antes de dar por terminado un componente, prueba en:

### Dispositivos Móviles
- [ ] iPhone SE (375px) - El más pequeño común
- [ ] iPhone 12/13 (390px) - Estándar actual
- [ ] iPhone 14 Pro Max (430px) - Grande
- [ ] Android estándar (360px-414px)

### Tablets
- [ ] iPad Mini (768px)
- [ ] iPad (810px)
- [ ] iPad Pro (1024px)

### Desktop
- [ ] Laptop (1366px)
- [ ] Desktop (1920px)
- [ ] 4K (2560px+)

### Funcionalidades
- [ ] Navegación funciona
- [ ] Botones son clickeables
- [ ] Formularios son usables
- [ ] Texto es legible
- [ ] Imágenes cargan
- [ ] Animaciones son suaves
- [ ] No hay scroll horizontal no deseado
- [ ] Modales se cierran correctamente

---

## 🛠️ Herramientas de Desarrollo

### Chrome DevTools
1. Abrir DevTools (F12)
2. Toggle device toolbar (Ctrl+Shift+M)
3. Probar diferentes dispositivos
4. Usar responsive mode para tamaños custom

### Firefox DevTools
1. Abrir DevTools (F12)
2. Responsive Design Mode (Ctrl+Shift+M)
3. Probar diferentes dispositivos
4. Simular touch events

### Extensiones Útiles
- **Responsive Viewer** - Ver múltiples tamaños a la vez
- **Lighthouse** - Auditoría de performance y accesibilidad
- **axe DevTools** - Testing de accesibilidad

---

## 📊 Métricas a Monitorear

### Performance
- **First Contentful Paint (FCP)**: < 1.8s
- **Largest Contentful Paint (LCP)**: < 2.5s
- **Time to Interactive (TTI)**: < 3.8s
- **Cumulative Layout Shift (CLS)**: < 0.1

### Accesibilidad
- **Contraste**: Mínimo 4.5:1 para texto normal
- **Touch Targets**: Mínimo 44x44px
- **Keyboard Navigation**: Todos los elementos accesibles
- **Screen Reader**: Contenido comprensible

### UX
- **Bounce Rate**: < 40%
- **Time on Page**: > 2 minutos
- **Conversion Rate**: Según objetivos
- **User Satisfaction**: > 4/5

---

## 🎓 Recursos Adicionales

### Documentación
- [Tailwind CSS Responsive Design](https://tailwindcss.com/docs/responsive-design)
- [Framer Motion](https://www.framer.com/motion/)
- [React Hooks](https://react.dev/reference/react)

### Guías
- [Web.dev - Responsive Design](https://web.dev/responsive-web-design-basics/)
- [MDN - Responsive Design](https://developer.mozilla.org/en-US/docs/Learn/CSS/CSS_layout/Responsive_Design)
- [WCAG Guidelines](https://www.w3.org/WAI/WCAG21/quickref/)

### Herramientas
- [Responsive Breakpoints Generator](https://www.responsivebreakpoints.com/)
- [Can I Use](https://caniuse.com/)
- [Lighthouse](https://developers.google.com/web/tools/lighthouse)

---

## 🔄 Proceso de Review

### Antes de Merge
1. ✅ Código revisado por otro dev
2. ✅ Testing en al menos 3 dispositivos diferentes
3. ✅ Lighthouse score > 90
4. ✅ No hay errores de consola
5. ✅ Accesibilidad verificada
6. ✅ Performance aceptable

### Después de Deploy
1. 📊 Monitorear métricas de performance
2. 🐛 Revisar reportes de bugs
3. 💬 Recopilar feedback de usuarios
4. 🔄 Iterar sobre mejoras

---

## 💡 Tips Finales

### 1. Mobile First
Siempre diseña primero para móvil, luego escala a desktop.

### 2. Test Early, Test Often
No esperes a terminar todo para probar en móvil.

### 3. Use Real Devices
Los emuladores son útiles, pero nada reemplaza dispositivos reales.

### 4. Performance Matters
Un sitio lento es un sitio que nadie usa.

### 5. Accessibility is Not Optional
Diseña para todos desde el principio.

### 6. Consistency is Key
Mantén patrones consistentes en toda la app.

### 7. Document Everything
El código se olvida, la documentación permanece.

### 8. Iterate and Improve
El diseño responsive es un proceso continuo.

---

## 📞 Soporte

Si tienes dudas sobre cómo implementar algo responsive:

1. Revisa esta guía
2. Busca ejemplos en componentes existentes
3. Consulta la documentación de Tailwind
4. Pregunta al equipo

---

**Última actualización:** 15 de Enero, 2026  
**Versión:** 1.0  
**Mantenedor:** Equipo Drive+
