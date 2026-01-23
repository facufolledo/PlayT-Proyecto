"""
Test del endpoint de parejas para verificar disponibilidad_horaria
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import requests
import json

API_URL = "http://localhost:8000"
TORNEO_ID = 25

def test_endpoint():
    try:
        url = f"{API_URL}/torneos/{TORNEO_ID}/parejas"
        print(f"Consultando: {url}\n")
        
        response = requests.get(url)
        
        if response.status_code != 200:
            print(f"Error {response.status_code}: {response.text}")
            return
        
        data = response.json()
        parejas = data if isinstance(data, list) else data.get('parejas', [])
        
        print(f"Total parejas: {len(parejas)}\n")
        
        if len(parejas) == 0:
            print("No hay parejas en el torneo")
            return
        
        # Mostrar primera pareja como ejemplo
        primera_pareja = parejas[0]
        print("Ejemplo de pareja (primera):")
        print(json.dumps(primera_pareja, indent=2, ensure_ascii=False))
        
        # Verificar si tienen disponibilidad
        print("\n" + "="*80)
        print("VERIFICACION DE DISPONIBILIDAD_HORARIA:")
        print("="*80 + "\n")
        
        con_disponibilidad = 0
        
        for pareja in parejas:
            if pareja.get('disponibilidad_horaria'):
                con_disponibilidad += 1
        
        print(f"Parejas con disponibilidad_horaria: {con_disponibilidad}/{len(parejas)}")
        
        # Mostrar un ejemplo con disponibilidad
        for pareja in parejas:
            if pareja.get('disponibilidad_horaria'):
                print(f"\nEjemplo con disponibilidad:")
                print(f"Pareja ID: {pareja.get('id')}")
                print(f"Jugadores: {pareja.get('jugador1', {}).get('nombre', 'N/A')} / {pareja.get('jugador2', {}).get('nombre', 'N/A')}")
                print(f"Disponibilidad: {json.dumps(pareja['disponibilidad_horaria'], ensure_ascii=False)}")
                break
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_endpoint()
