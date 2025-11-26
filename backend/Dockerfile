# Usar imagen oficial de Python
FROM python:3.11-slim

# Establecer directorio de trabajo
WORKDIR /app

# Copiar requirements
COPY requirements.txt .

# Instalar dependencias
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copiar el código de la aplicación
COPY . .

# Exponer el puerto (Railway asigna dinámicamente)
EXPOSE $PORT

# Comando para ejecutar la aplicación
# Crear credenciales de Firebase al inicio si existen
CMD sh -c "if [ -n \"$FIREBASE_CREDENTIALS_JSON\" ]; then echo \"$FIREBASE_CREDENTIALS_JSON\" > /app/firebase-credentials.json; fi && uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}"
