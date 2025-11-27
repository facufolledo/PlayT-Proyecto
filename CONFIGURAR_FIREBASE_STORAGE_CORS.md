# Configurar CORS en Firebase Storage

## Problema
Error al subir fotos de perfil: `Access to XMLHttpRequest has been blocked by CORS policy`

## Solución

### Opción 1: Usar Google Cloud Console (Recomendado)

1. Ve a [Google Cloud Console](https://console.cloud.google.com/)
2. Selecciona tu proyecto: `playr-3f394`
3. Ve a **Cloud Storage** → **Buckets**
4. Selecciona tu bucket: `playr-3f394.appspot.com`
5. Ve a la pestaña **Permissions**
6. Haz clic en **Add Principal**
7. Agrega: `allUsers`
8. Rol: `Storage Object Viewer`
9. Guarda

### Opción 2: Usar gsutil (Línea de comandos)

Si tienes Google Cloud SDK instalado:

```bash
# 1. Instalar Google Cloud SDK si no lo tienes
# https://cloud.google.com/sdk/docs/install

# 2. Autenticarte
gcloud auth login

# 3. Configurar CORS
gsutil cors set firebase-storage-cors.json gs://playr-3f394.appspot.com
```

### Opción 3: Cambiar reglas de Firebase Storage

1. Ve a [Firebase Console](https://console.firebase.google.com/)
2. Selecciona tu proyecto
3. Ve a **Storage** → **Rules**
4. Cambia las reglas a:

```
rules_version = '2';
service firebase.storage {
  match /b/{bucket}/o {
    match /profile-photos/{userId}_{timestamp} {
      // Permitir lectura a todos
      allow read: if true;
      
      // Permitir escritura solo al usuario autenticado
      allow write: if request.auth != null;
    }
    
    match /{allPaths=**} {
      allow read: if true;
      allow write: if request.auth != null;
    }
  }
}
```

### Opción 4: Solución temporal (Desarrollo)

Mientras configuras CORS, puedes usar una solución temporal:

1. Deshabilita temporalmente la subida de fotos
2. O usa URLs de imágenes externas (ej: Imgur, Cloudinary)

## Verificar que funciona

Después de configurar CORS, prueba subir una foto de perfil. Deberías ver en la consola:

```
✅ Foto subida exitosamente
✅ URL: https://firebasestorage.googleapis.com/...
```

## Notas

- El error de CORS es normal en desarrollo local
- En producción (con dominio propio), necesitarás agregar tu dominio a la lista de orígenes permitidos
- Las reglas de Storage son diferentes a las de Firestore

## Alternativa: Subir foto al backend

Si no quieres lidiar con Firebase Storage, puedes:

1. Subir la imagen como base64 al backend
2. El backend la guarda en un servicio de almacenamiento (AWS S3, Cloudinary, etc.)
3. Retorna la URL

Esto requiere más trabajo en el backend pero evita problemas de CORS.
