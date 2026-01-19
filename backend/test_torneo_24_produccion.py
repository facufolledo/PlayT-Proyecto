import requests
import json

# Test en producción
url_prod = "https://drive-plus-production.up.railway.app/torneos/24"
url_local = "http://localhost:8000/torneos/24"

print("=" * 60)
print("VERIFICANDO TORNEO 24 EN PRODUCCIÓN Y LOCAL")
print("=" * 60)

# Test en producción
print("\n🌐 PRODUCCIÓN (Railway):")
print(f"URL: {url_prod}")
try:
    response = requests.get(url_prod, headers={
        'Cache-Control': 'no-cache',
        'Pragma': 'no-cache'
    })
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Nombre: {data.get('nombre')}")
        print(f"✅ Fecha Inicio: {data.get('fecha_inicio')}")
        print(f"✅ Fecha Fin: {data.get('fecha_fin')}")
        print(f"✅ Horarios: {json.dumps(data.get('horarios_disponibles'), indent=2, ensure_ascii=False)}")
    else:
        print(f"❌ Error: {response.text}")
except Exception as e:
    print(f"❌ Error de conexión: {e}")

# Test en local
print("\n💻 LOCAL:")
print(f"URL: {url_local}")
try:
    response = requests.get(url_local, headers={
        'Cache-Control': 'no-cache',
        'Pragma': 'no-cache'
    })
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Nombre: {data.get('nombre')}")
        print(f"✅ Fecha Inicio: {data.get('fecha_inicio')}")
        print(f"✅ Fecha Fin: {data.get('fecha_fin')}")
        print(f"✅ Horarios: {json.dumps(data.get('horarios_disponibles'), indent=2, ensure_ascii=False)}")
    else:
        print(f"❌ Error: {response.text}")
except Exception as e:
    print(f"❌ Error de conexión: {e}")

print("\n" + "=" * 60)
print("CONCLUSIÓN:")
print("Si ambos muestran 2026-01-23 a 2026-01-25, el backend está OK")
print("Si el frontend muestra 22-24, es un problema de cache del navegador")
print("=" * 60)
