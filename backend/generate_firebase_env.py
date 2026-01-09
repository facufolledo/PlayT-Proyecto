#!/usr/bin/env python3
"""
Script para generar la variable de entorno FIREBASE_CREDENTIALS_JSON
"""
import json

# Leer el archivo firebase-credentials.json
with open('firebase-credentials.json', 'r') as f:
    credentials = json.load(f)

# Convertir a string JSON compacto
credentials_json = json.dumps(credentials, separators=(',', ':'))

print("=== VARIABLE DE ENTORNO PARA RAILWAY ===")
print("Nombre: FIREBASE_CREDENTIALS_JSON")
print("Valor:")
print(credentials_json)
print("\n=== INSTRUCCIONES ===")
print("1. Copia el valor de arriba")
print("2. Ve a Railway Dashboard")
print("3. Variables → FIREBASE_CREDENTIALS_JSON")
print("4. Pega el valor y guarda")
print("5. Railway hará redeploy automáticamente")