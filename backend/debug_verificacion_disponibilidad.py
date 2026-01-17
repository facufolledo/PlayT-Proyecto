"""
Debug de la verificación de disponibilidad
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from src.database.config import get_db
from src.services.torneo_fixture_global_service import TorneoFixtureGlobalService
from src.models.torneo_models import TorneoPareja
from datetime import datetime
import json

def debug_verificacion():
    db = next(get_db())
    
    print("🔍 DEBUG VERIFICACIÓN DE DISPONIBILIDAD")
    print("="*60)
    
    # Tomar una pareja específica que está teniendo problemas
    pareja_id = 140  # 7ma_m1j1_1768608276 & 7ma_m1j2_1768608276
    
    pareja = db.query(TorneoPareja).filter(TorneoPareja.id == pareja_id).first()
    if not pareja:
        print("❌ Pareja no encontrada")
        return
    
    print(f"🎾 Pareja {pareja_id}")
    print(f"   Disponibilidad RAW: {json.dumps(pareja.disponibilidad_horaria, indent=2)}")
    
    # Procesar disponibilidad usando el método del servicio
    partidos_mock = [{'pareja1_id': pareja_id, 'pareja2_id': pareja_id}]
    disponibilidad = TorneoFixtureGlobalService._obtener_disponibilidad_parejas(
        db, partidos_mock, None
    )
    
    disp_procesada = disponibilidad[pareja_id]
    print(f"   Disponibilidad procesada: {disp_procesada}")
    
    # Probar verificación con diferentes horarios
    test_cases = [
        ('viernes', '17:30'),  # Debería fallar (fuera de rango)
        ('sabado', '09:00'),   # Debería pasar
        ('sabado', '12:00'),   # Debería pasar
        ('sabado', '23:00'),   # Debería pasar
        ('sabado', '01:50'),   # Debería fallar (fuera de rango)
        ('domingo', '10:00'),  # Debería pasar
        ('lunes', '15:00'),    # Debería pasar (día sin restricción)
    ]
    
    print(f"\n📋 PRUEBAS DE VERIFICACIÓN:")
    for dia, hora in test_cases:
        hora_mins = int(hora.split(':')[0]) * 60 + int(hora.split(':')[1])
        
        resultado = TorneoFixtureGlobalService._verificar_disponibilidad_pareja(
            dia, hora_mins, disp_procesada
        )
        
        status = "✅" if resultado else "❌"
        print(f"   {status} {dia} {hora} -> {resultado}")
    
    db.close()

if __name__ == "__main__":
    debug_verificacion()