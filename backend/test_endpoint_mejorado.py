"""
Script para probar el endpoint mejorado de historial de partidos
"""
import requests
import json

API_URL = "http://localhost:8000"

# Probar sin autenticación (para ver estructura)
print("🔍 Probando endpoint de historial de partidos...")
print(f"URL: {API_URL}/partidos/usuario/14?limit=50")

response = requests.get(f"{API_URL}/partidos/usuario/14?limit=50")

print(f"\nStatus Code: {response.status_code}")

if response.status_code == 200:
    partidos = response.json()
    print(f"✅ Partidos obtenidos: {len(partidos)}")
    
    if len(partidos) > 0:
        print("\n📋 Primer partido:")
        primer_partido = partidos[0]
        print(json.dumps(primer_partido, indent=2, default=str))
        
        # Verificar campos importantes
        print("\n✅ Verificación de campos:")
        print(f"  - Tiene tipo: {'tipo' in primer_partido}")
        print(f"  - Tipo: {primer_partido.get('tipo', 'N/A')}")
        print(f"  - Tiene resultado: {primer_partido.get('resultado') is not None}")
        
        if primer_partido.get('resultado'):
            resultado = primer_partido['resultado']
            print(f"  - Sets: {resultado.get('sets_eq1')}-{resultado.get('sets_eq2')}")
            print(f"  - Detalle sets: {len(resultado.get('detalle_sets', []))} sets")
            
            if resultado.get('detalle_sets'):
                print(f"  - Formato detalle_sets correcto: {all('juegos_eq1' in s and 'juegos_eq2' in s for s in resultado['detalle_sets'])}")
                print(f"  - Primer set: {resultado['detalle_sets'][0]}")
        
        if primer_partido.get('historial_rating'):
            historial = primer_partido['historial_rating']
            print(f"  - Rating antes: {historial.get('rating_antes')}")
            print(f"  - Delta: {historial.get('delta'):+d}")
            print(f"  - Rating después: {historial.get('rating_despues')}")
    else:
        print("⚠️  No hay partidos confirmados con resultado")
else:
    print(f"❌ Error: {response.status_code}")
    print(response.text)
