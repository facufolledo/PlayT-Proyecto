"""
Test del endpoint de partidos para verificar disponibilidad_horaria
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
        url = f"{API_URL}/torneos/{TORNEO_ID}/partidos"
        print(f"Consultando: {url}\n")
        
        response = requests.get(url)
        
        if response.status_code != 200:
            print(f"Error {response.status_code}: {response.text}")
            return
        
        data = response.json()
        partidos = data.get('partidos', [])
        
        print(f"Total partidos: {len(partidos)}\n")
        
        if len(partidos) == 0:
            print("No hay partidos en el torneo")
            return
        
        # Mostrar primer partido como ejemplo
        primer_partido = partidos[0]
        print("Ejemplo de partido (primero):")
        print(json.dumps(primer_partido, indent=2, ensure_ascii=False))
        
        # Verificar si tienen disponibilidad
        print("\n" + "="*80)
        print("VERIFICACION DE DISPONIBILIDAD_HORARIA:")
        print("="*80 + "\n")
        
        con_disp_p1 = 0
        con_disp_p2 = 0
        
        for partido in partidos:
            if partido.get('pareja1_disponibilidad'):
                con_disp_p1 += 1
            if partido.get('pareja2_disponibilidad'):
                con_disp_p2 += 1
        
        print(f"Partidos con pareja1_disponibilidad: {con_disp_p1}/{len(partidos)}")
        print(f"Partidos con pareja2_disponibilidad: {con_disp_p2}/{len(partidos)}")
        
        # Mostrar un ejemplo con disponibilidad
        for partido in partidos:
            if partido.get('pareja1_disponibilidad'):
                print(f"\nEjemplo con disponibilidad:")
                print(f"Partido ID: {partido['id_partido']}")
                print(f"Pareja 1: {partido['pareja1_nombre']}")
                print(f"Disponibilidad: {json.dumps(partido['pareja1_disponibilidad'], ensure_ascii=False)}")
                break
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_endpoint()
