# Generación de Iconos PWA para PlayR

## Opción 1: Usar herramienta online (Recomendado)

1. Ve a: https://www.pwabuilder.com/imageGenerator
2. Sube tu logo (`/public/logo playR.png`)
3. Descarga el paquete de iconos
4. Extrae los archivos en `/public/icons/`

## Opción 2: Usar PWA Asset Generator (CLI)

```bash
# Instalar globalmente
npm install -g pwa-asset-generator

# Generar iconos desde la carpeta frontend
cd frontend
pwa-asset-generator public/logo\ playR.png public/icons --icon-only --favicon --type png
```

## Opción 3: Crear manualmente con ImageMagick

```bash
# Instalar ImageMagick
# Windows: https://imagemagick.org/script/download.php
# Mac: brew install imagemagick
# Linux: sudo apt-get install imagemagick

# Generar iconos (desde carpeta frontend)
cd frontend/public

# Crear carpeta icons
mkdir icons

# Generar cada tamaño
magick "logo playR.png" -resize 72x72 icons/icon-72x72.png
magick "logo playR.png" -resize 96x96 icons/icon-96x96.png
magick "logo playR.png" -resize 128x128 icons/icon-128x128.png
magick "logo playR.png" -resize 144x144 icons/icon-144x144.png
magick "logo playR.png" -resize 152x152 icons/icon-152x152.png
magick "logo playR.png" -resize 192x192 icons/icon-192x192.png
magick "logo playR.png" -resize 384x384 icons/icon-384x384.png
magick "logo playR.png" -resize 512x512 icons/icon-512x512.png
```

## Tamaños requeridos:

- 72x72 - Android Chrome
- 96x96 - Android Chrome
- 128x128 - Android Chrome
- 144x144 - Windows
- 152x152 - iOS Safari
- 192x192 - Android Chrome (mínimo)
- 384x384 - Android Chrome
- 512x512 - Android Chrome (recomendado)

## Verificación:

Después de generar los iconos, verifica que existan:
- `/public/icons/icon-72x72.png`
- `/public/icons/icon-96x96.png`
- `/public/icons/icon-128x128.png`
- `/public/icons/icon-144x144.png`
- `/public/icons/icon-152x152.png`
- `/public/icons/icon-192x192.png`
- `/public/icons/icon-384x384.png`
- `/public/icons/icon-512x512.png`

## Nota:
Por ahora, puedes usar el logo existente como fallback hasta generar los iconos específicos.
